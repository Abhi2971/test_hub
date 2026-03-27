"""
Institute service for ExamSaaS platform.
Pure Python - zero Flask imports, zero HTTP concepts.
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List
from bson import ObjectId

import jwt
import bcrypt

from app.utils.security import (
    hash_password,
    sanitize_input,
    generate_jti,
)
from app.utils.email_helper import send_welcome_email

logger = logging.getLogger(__name__)

REDIS_CLIENT = None


def _get_redis():
    """Get Redis client from extensions."""
    global REDIS_CLIENT
    if REDIS_CLIENT is None:
        try:
            from app.extensions import get_redis
            REDIS_CLIENT = get_redis()
        except RuntimeError:
            logger.warning("Redis not available for institute service")
            return None
    return REDIS_CLIENT


def _get_config(key: str, default: Any = None) -> Any:
    """Get configuration value."""
    try:
        from flask import current_app
        return current_app.config.get(key, default)
    except RuntimeError:
        return default


def _create_audit_log(
    actor_id: str,
    actor_role: str,
    action: str,
    institute_id: Optional[str] = None,
    target_type: Optional[str] = None,
    target_id: Optional[str] = None,
    metadata: Optional[Dict] = None
) -> None:
    """Create audit log entry."""
    try:
        from app.models import AuditLog, User, Institute
        
        actor = None
        if actor_id:
            actor = User.objects(id=actor_id).first()
        
        institute_obj = None
        if institute_id:
            institute_obj = Institute.objects(id=institute_id).first()
        
        audit_log = AuditLog(
            actor=actor,
            actor_role=actor_role,
            action=action,
            target_type=target_type,
            target_id=target_id,
            institute=institute_obj,
            metadata=metadata or {}
        )
        audit_log.save()
        logger.info(f"Audit log created: {action}")
    except Exception as e:
        logger.error(f"Failed to create audit log: {e}")


IMPERSONATION_TOKEN_EXPIRY = 30 * 60


class InstituteServiceError(Exception):
    """Base exception for institute service errors."""
    def __init__(self, message: str, code: str, status_code: int = 400):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class InstituteNotFoundError(InstituteServiceError):
    """Institute not found."""
    def __init__(self):
        super().__init__("Institute not found", "INSTITUTE_NOT_FOUND", 404)


class InstituteAlreadyExistsError(InstituteServiceError):
    """Institute already exists."""
    def __init__(self):
        super().__init__("Institute with this slug already exists", "INSTITUTE_ALREADY_EXISTS", 409)


class InstituteSuspendedError(InstituteServiceError):
    """Institute is suspended."""
    def __init__(self):
        super().__init__("Institute has been suspended", "INSTITUTE_SUSPENDED", 423)


class InvalidInstituteDataError(InstituteServiceError):
    """Invalid institute data."""
    def __init__(self, message: str):
        super().__init__(message, "INVALID_INSTITUTE_DATA", 400)


def create_institute_with_admin(data: dict) -> dict:
    """
    ATOMIC: Create Institute + admin User + Wallet + Subscription.
    Rollback all if any step fails.
    
    Args:
        data = { name, slug, city, state, country, admin: { email, password, first_name, last_name } }
    
    Returns:
        dict with institute and admin details
    
    Raises:
        InstituteAlreadyExistsError: If slug already exists
        InvalidInstituteDataError: If required data is missing
    """
    if not data.get('slug'):
        raise InvalidInstituteDataError("Slug is required")
    
    slug = sanitize_input(data['slug']).lower().strip()
    name = sanitize_input(data.get('name', ''))
    
    if not name:
        raise InvalidInstituteDataError("Institute name is required")
    
    admin_data = data.get('admin', {})
    if not admin_data.get('email'):
        raise InvalidInstituteDataError("Admin email is required")
    if not admin_data.get('password'):
        raise InvalidInstituteDataError("Admin password is required")
    if not admin_data.get('first_name'):
        raise InvalidInstituteDataError("Admin first name is required")
    
    from app.models import Institute, User, Wallet, Subscription, Plan
    
    existing_institute = Institute.objects(slug=slug).first()
    if existing_institute:
        raise InstituteAlreadyExistsError()
    
    existing_user = User.objects(email=admin_data['email'].lower().strip()).first()
    if existing_user:
        raise InstituteAlreadyExistsError()
    
    created_objects = []
    
    try:
        institute = Institute(
            name=name,
            slug=slug,
            city=sanitize_input(data.get('city', '')) if data.get('city') else None,
            state=sanitize_input(data.get('state', '')) if data.get('state') else None,
            country=sanitize_input(data.get('country', 'India')) if data.get('country') else 'India',
            is_active=True,
            is_suspended=False,
        )
        institute.save()
        created_objects.append(('institute', institute))
        logger.info(f"Institute created: {institute.id}")
        
        password_hash = hash_password(admin_data['password'], cost=12)
        
        admin_user = User(
            email=admin_data['email'].lower().strip(),
            password_hash=password_hash,
            first_name=sanitize_input(admin_data['first_name']),
            last_name=sanitize_input(admin_data['last_name']) if admin_data.get('last_name') else None,
            role='admin_college',
            institute=institute,
            is_active=True,
            is_email_verified=False,
            auth_provider='local'
        )
        admin_user.save()
        created_objects.append(('user', admin_user))
        logger.info(f"Admin user created: {admin_user.id}")
        
        wallet = Wallet(user=admin_user.id, balance=0)
        wallet.save()
        created_objects.append(('wallet', wallet))
        
        admin_user.wallet = wallet
        admin_user.save()
        
        free_plan = Plan.objects(slug='free', is_for='institute', is_active=True).first()
        if not free_plan:
            free_plan = Plan(
                name='Free',
                slug='free',
                price=0,
                duration_days=30,
                max_students=100,
                max_teachers=5,
                exam_limit=10,
                ai_usage_limit=0,
                is_for='institute',
                is_active=True
            )
            free_plan.save()
            created_objects.append(('plan', free_plan))
        
        now = datetime.utcnow()
        subscription = Subscription(
            institute=institute,
            plan=free_plan,
            status='active',
            starts_at=now,
            expires_at=now + timedelta(days=30)
        )
        subscription.save()
        created_objects.append(('subscription', subscription))
        
        institute.subscription = subscription
        institute.save()
        
        try:
            send_welcome_email(admin_user.email, admin_user.first_name)
            logger.info(f"Welcome email sent to {admin_user.email}")
        except Exception as e:
            logger.warning(f"Failed to send welcome email: {e}")
        
        logger.info(f"Institute with admin created successfully: {institute.id}")
        
        return {
            'institute': {
                'id': str(institute.id),
                'name': institute.name,
                'slug': institute.slug,
                'city': institute.city,
                'state': institute.state,
                'country': institute.country,
                'is_suspended': institute.is_suspended,
                'created_at': institute.created_at.isoformat() if institute.created_at else None,
            },
            'admin': {
                'id': str(admin_user.id),
                'email': admin_user.email,
                'first_name': admin_user.first_name,
                'last_name': admin_user.last_name,
                'role': admin_user.role,
                'is_active': admin_user.is_active,
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to create institute: {e}")
        
        for obj_type, obj in reversed(created_objects):
            try:
                if obj_type == 'institute':
                    for user_obj in User.objects(institute=obj):
                        if user_obj.wallet:
                            user_obj.wallet.delete()
                        user_obj.delete()
                    for sub in Subscription.objects(institute=obj):
                        sub.delete()
                    obj.delete()
                elif obj_type == 'user':
                    if obj.wallet:
                        obj.wallet.delete()
                    obj.delete()
                elif obj_type == 'wallet':
                    obj.delete()
                elif obj_type == 'subscription':
                    obj.delete()
                elif obj_type == 'plan':
                    obj.delete()
                logger.info(f"Rolled back {obj_type}")
            except Exception as rollback_error:
                logger.error(f"Failed to rollback {obj_type}: {rollback_error}")
        
        raise InstituteServiceError(f"Failed to create institute: {str(e)}", "CREATE_FAILED", 500)


def list_institutes(filters: dict, page: int, limit: int) -> dict:
    """
    Paginated list with filters: city, state, plan, is_suspended, search(name)
    
    Args:
        filters: Dictionary with filter parameters
        page: Page number (1-indexed)
        limit: Items per page
    
    Returns:
        Dictionary with items, total, page, limit, total_pages
    """
    from app.models import Institute, Subscription, Plan
    
    query = Institute.objects
    
    if filters.get('city'):
        query = query(city__iexact=filters['city'])
    
    if filters.get('state'):
        query = query(state__iexact=filters['state'])
    
    if filters.get('is_suspended') is not None:
        is_suspended = filters['is_suspended'] in [True, 'true', 'True', '1', 1]
        query = query(is_suspended=is_suspended)
    
    if filters.get('plan'):
        plan = Plan.objects(slug=filters['plan'], is_active=True).first()
        if plan:
            from app.models import Subscription
            subs = Subscription.objects(plan=plan).only('id')
            sub_ids = [s.id for s in subs]
            if sub_ids:
                query = query(subscription__in=sub_ids)
    
    if filters.get('search'):
        search_term = sanitize_input(filters['search'])
        query = query(name__icontains=search_term)
    
    total = query.count()
    
    skip = (page - 1) * limit
    institutes = query.order_by('-created_at').skip(skip).limit(limit)
    
    items = []
    for inst in institutes:
        item = {
            'id': str(inst.id),
            'name': inst.name,
            'slug': inst.slug,
            'logo_url': inst.logo_url,
            'city': inst.city,
            'state': inst.state,
            'country': inst.country,
            'is_suspended': inst.is_suspended,
            'is_active': inst.is_active,
            'created_at': inst.created_at.isoformat() if inst.created_at else None,
        }
        
        if inst.subscription:
            sub = inst.subscription
            if sub and sub.plan:
                item['plan'] = sub.plan.name
        
        items.append(item)
    
    total_pages = (total + limit - 1) // limit if limit > 0 else 0
    
    return {
        'items': items,
        'total': total,
        'page': page,
        'limit': limit,
        'total_pages': total_pages
    }


def get_institute(institute_id: str) -> dict:
    """
    Get institute by ID.
    
    Args:
        institute_id: Institute ID
    
    Returns:
        Institute dictionary
    
    Raises:
        InstituteNotFoundError: If institute not found
    """
    from app.models import Institute, Subscription
    
    institute = Institute.objects(id=institute_id).first()
    if not institute:
        raise InstituteNotFoundError()
    
    result = {
        'id': str(institute.id),
        'name': institute.name,
        'slug': institute.slug,
        'logo_url': institute.logo_url,
        'address': institute.address,
        'city': institute.city,
        'state': institute.state,
        'country': institute.country,
        'admin_type': institute.admin_type,
        'is_active': institute.is_active,
        'is_suspended': institute.is_suspended,
        'created_at': institute.created_at.isoformat() if institute.created_at else None,
        'updated_at': institute.updated_at.isoformat() if institute.updated_at else None,
    }
    
    if institute.subscription:
        sub = institute.subscription
        if sub:
            result['subscription'] = {
                'id': str(sub.id),
                'status': sub.status,
                'plan': sub.plan.name if sub.plan else None,
                'expires_at': sub.expires_at.isoformat() if sub.expires_at else None,
            }
    
    return result


def update_institute(institute_id: str, data: dict) -> dict:
    """
    Update institute fields.
    
    Args:
        institute_id: Institute ID
        data: Dictionary with fields to update
    
    Returns:
        Updated institute dictionary
    
    Raises:
        InstituteNotFoundError: If institute not found
    """
    from app.models import Institute
    
    institute = Institute.objects(id=institute_id).first()
    if not institute:
        raise InstituteNotFoundError()
    
    if 'name' in data:
        name = sanitize_input(data['name'])
        if name:
            institute.name = name
    
    if 'logo_url' in data:
        institute.logo_url = data['logo_url']
    
    if 'address' in data:
        institute.address = sanitize_input(data['address']) if data['address'] else None
    
    if 'city' in data:
        institute.city = sanitize_input(data['city']) if data['city'] else None
    
    if 'state' in data:
        institute.state = sanitize_input(data['state']) if data['state'] else None
    
    if 'country' in data:
        institute.country = sanitize_input(data['country']) if data['country'] else None
    
    if 'admin_type' in data:
        if data['admin_type'] in ['platform_admin', 'institute_admin']:
            institute.admin_type = data['admin_type']
    
    institute.save()
    
    logger.info(f"Institute updated: {institute_id}")
    
    return get_institute(institute_id)


def suspend_institute(institute_id: str, admin_id: str, reason: Optional[str] = None) -> dict:
    """
    Set is_suspended=True, log audit, suspend all users in institute.
    
    Args:
        institute_id: Institute ID
        admin_id: Admin user ID performing the action
        reason: Optional reason for suspension
    
    Returns:
        Updated institute dictionary
    
    Raises:
        InstituteNotFoundError: If institute not found
    """
    from app.models import Institute, User
    
    institute = Institute.objects(id=institute_id).first()
    if not institute:
        raise InstituteNotFoundError()
    
    institute.is_suspended = True
    institute.save()
    
    suspended_count = 0
    users = User.objects(institute=institute)
    for user in users:
        user.is_active = False
        user.save()
        suspended_count += 1
    
    _create_audit_log(
        actor_id=admin_id,
        actor_role='super_admin',
        action='suspend_institute',
        institute_id=institute_id,
        target_type='institute',
        target_id=institute_id,
        metadata={
            'suspended_users_count': suspended_count,
            'reason': reason
        }
    )
    
    logger.info(f"Institute suspended: {institute_id}, {suspended_count} users suspended")
    
    return get_institute(institute_id)


def restore_institute(institute_id: str, admin_id: str) -> dict:
    """
    Set is_suspended=False, restore all users.
    
    Args:
        institute_id: Institute ID
        admin_id: Admin user ID performing the action
    
    Returns:
        Updated institute dictionary
    
    Raises:
        InstituteNotFoundError: If institute not found
    """
    from app.models import Institute, User
    
    institute = Institute.objects(id=institute_id).first()
    if not institute:
        raise InstituteNotFoundError()
    
    institute.is_suspended = False
    institute.save()
    
    restored_count = 0
    users = User.objects(institute=institute)
    for user in users:
        user.is_active = True
        user.save()
        restored_count += 1
    
    _create_audit_log(
        actor_id=admin_id,
        actor_role='super_admin',
        action='restore_institute',
        institute_id=institute_id,
        target_type='institute',
        target_id=institute_id,
        metadata={
            'restored_users_count': restored_count
        }
    )
    
    logger.info(f"Institute restored: {institute_id}, {restored_count} users restored")
    
    return get_institute(institute_id)


def generate_impersonation_token(institute_id: str, super_admin_id: str) -> dict:
    """
    Generate short-lived JWT for institute admin.
    
    Args:
        institute_id: Institute ID
        super_admin_id: Super admin ID performing impersonation
    
    Returns:
        Dictionary with token and expiry
    
    Raises:
        InstituteNotFoundError: If institute not found
    """
    from app.models import Institute, User
    
    institute = Institute.objects(id=institute_id).first()
    if not institute:
        raise InstituteNotFoundError()
    
    admin_user = User.objects(institute=institute, role='admin_college').first()
    if not admin_user:
        raise InstituteNotFoundError()
    
    jwt_secret = _get_config("JWT_SECRET_KEY", "dev-jwt-secret-change-in-production")
    now = datetime.now(timezone.utc)
    expiry = now + timedelta(seconds=IMPERSONATION_TOKEN_EXPIRY)
    
    jti = generate_jti()
    
    payload = {
        "sub": str(admin_user.id),
        "user_id": str(admin_user.id),
        "role": admin_user.role,
        "institute_id": str(institute.id),
        "impersonated_by": super_admin_id,
        "jti": jti,
        "type": "impersonation",
        "iat": now,
        "exp": expiry,
    }
    
    token = jwt.encode(payload, jwt_secret, algorithm="HS256")
    
    _create_audit_log(
        actor_id=super_admin_id,
        actor_role='super_admin',
        action='impersonate_admin',
        institute_id=institute_id,
        target_type='user',
        target_id=str(admin_user.id),
        metadata={
            'institute_id': institute_id,
            'target_user_id': str(admin_user.id)
        }
    )
    
    logger.info(f"Impersonation token generated for institute {institute_id}, admin {admin_user.id}")
    
    return {
        'token': token,
        'expires_in': IMPERSONATION_TOKEN_EXPIRY
    }


def get_institute_analytics(institute_id: str) -> dict:
    """
    Get institute-level analytics.
    
    Args:
        institute_id: Institute ID
    
    Returns:
        Dictionary with analytics data
    
    Raises:
        InstituteNotFoundError: If institute not found
    """
    from app.models import Institute, User, Exam, ExamAttempt, WalletTransaction
    
    institute = Institute.objects(id=institute_id).first()
    if not institute:
        raise InstituteNotFoundError()
    
    student_count = User.objects(
        institute=institute,
        role__in=['student_registered', 'student_assigned']
    ).count()
    
    exam_count = Exam.objects(
        institute=institute,
        status='published'
    ).count()
    
    attempt_count = ExamAttempt.objects(
        exam__in=Exam.objects(institute=institute).only('id')
    ).count()
    
    institute_users = User.objects(institute=institute).only('id')
    user_ids = [u.id for u in institute_users]
    
    wallet_ids = []
    for user in User.objects(id__in=user_ids).only('wallet'):
        if user.wallet:
            wallet_ids.append(user.wallet.id)
    
    total_revenue = 0
    if wallet_ids:
        revenue_transactions = WalletTransaction.objects(
            wallet__in=wallet_ids,
            type='credit'
        ).aggregate([
            {'$group': {'_id': None, 'total': {'$sum': '$amount'}}}
        ])
        result = list(revenue_transactions)
        if result:
            total_revenue = result[0].get('total', 0)
    
    logger.info(f"Analytics retrieved for institute {institute_id}")
    
    return {
        'student_count': student_count,
        'exam_count': exam_count,
        'attempt_count': attempt_count,
        'total_revenue': total_revenue
    }


def delete_institute(institute_id: str) -> dict:
    """
    Soft delete - just set is_suspended=True.
    
    Args:
        institute_id: Institute ID
    
    Returns:
        Dictionary with success status
    
    Raises:
        InstituteNotFoundError: If institute not found
    """
    from app.models import Institute
    
    institute = Institute.objects(id=institute_id).first()
    if not institute:
        raise InstituteNotFoundError()
    
    institute.is_suspended = True
    institute.is_active = False
    institute.save()
    
    logger.info(f"Institute soft deleted: {institute_id}")
    
    return {
        'success': True,
        'message': 'Institute has been deleted',
        'institute_id': institute_id
    }