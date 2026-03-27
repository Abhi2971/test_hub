"""
Superadmin service for ExamSaaS platform.
Pure Python - zero Flask imports, zero HTTP concepts.
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class SuperadminServiceError(Exception):
    """Base exception for superadmin service errors."""
    def __init__(self, message: str, code: str = "SUPERADMIN_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


def _mask_email(email: str) -> str:
    """
    Mask email for PII protection.
    Shows first 3 characters + ***@domain.com
    """
    if not email or '@' not in email:
        return "***@***.***"
    
    local_part, domain = email.rsplit('@', 1)
    masked_local = local_part[:3] + "***" if len(local_part) > 3 else "***"
    return f"{masked_local}@{domain}"


def _mask_phone(phone: str) -> str:
    """Mask phone number for PII protection."""
    if not phone or len(phone) < 4:
        return "***"
    return phone[:2] + "****" + phone[-2:]


def get_platform_analytics() -> Dict[str, Any]:
    """
    Super admin platform-wide stats
    
    Returns:
        Dict with mau, total_revenue, active_institutes, daily_exams_30d, plan_distribution
    """
    from app.models import User, ExamAttempt, Payment, Institute, Subscription, Plan, Exam
    from bson import ObjectId
    
    try:
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        # Total Users
        total_students = User.objects(role__in=['student_registered', 'student_assigned']).count()
        total_teachers = User.objects(role='teacher').count()
        total_institutes = Institute.objects().count()
        
        # MAU - Users with exam attempts in last 30 days
        mau = ExamAttempt.objects(created_at__gte=thirty_days_ago).distinct('student')
        mau = len([m for m in mau if m])
        
        # Total Revenue
        total_revenue = Payment.objects(status='completed').sum('amount') or 0
        if total_revenue == 0:
            total_revenue = Payment.objects(status='captured').sum('amount') or 0
        
        # Active Institutes (with activity in last 30 days)
        active_institute_ids = set()
        for attempt in ExamAttempt.objects(created_at__gte=thirty_days_ago):
            try:
                if attempt.exam and attempt.exam.institute:
                    active_institute_ids.add(attempt.exam.institute.id)
            except:
                pass
        
        active_institutes = len(active_institute_ids)
        if active_institutes == 0:
            active_institutes = Institute.objects(is_active=True).count()
        
        # Total Exams
        total_exams = Exam.objects().count()
        
        # Daily exam attempts for last 30 days
        daily_exams_30d = []
        for i in range(30):
            day = datetime.utcnow() - timedelta(days=29 - i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            count = ExamAttempt.objects(
                created_at__gte=day_start,
                created_at__lte=day_end
            ).count()
            
            daily_exams_30d.append({
                "date": day_start.strftime("%Y-%m-%d"),
                "count": count
            })
        
        # Plan distribution
        subscriptions = Subscription.objects()
        plan_counts = {}
        for sub in subscriptions:
            if sub.plan:
                plan_name = sub.plan.name
                plan_counts[plan_name] = plan_counts.get(plan_name, 0) + 1
        
        plan_distribution = [
            {"plan_name": name, "count": count}
            for name, count in plan_counts.items()
        ]
        plan_distribution.sort(key=lambda x: x["count"], reverse=True)
        
        # Subscriptions stats
        total_subscriptions = Subscription.objects().count()
        active_subscriptions = Subscription.objects(status='active').count()
        
        return {
            "mau": mau,
            "total_revenue": total_revenue,
            "active_institutes": active_institutes,
            "total_institutes": total_institutes,
            "total_students": total_students,
            "total_teachers": total_teachers,
            "total_exams": total_exams,
            "total_subscriptions": total_subscriptions,
            "active_subscriptions": active_subscriptions,
            "daily_exams_30d": daily_exams_30d,
            "plan_distribution": plan_distribution
        }
    except Exception as e:
        logger.error(f"Error in get_platform_analytics: {e}")
        return {
            "mau": 0,
            "total_revenue": 0,
            "active_institutes": 0,
            "total_institutes": 0,
            "total_students": 0,
            "total_teachers": 0,
            "total_exams": 0,
            "total_subscriptions": 0,
            "active_subscriptions": 0,
            "daily_exams_30d": [],
            "plan_distribution": []
        }


def get_audit_logs(filters: Dict[str, Any], page: int, limit: int) -> Dict[str, Any]:
    """
    Paginated audit logs with filters
    
    Args:
        filters: Dict with action, actor_id, institute_id, date_from, date_to
        page: Page number (1-based)
        limit: Items per page
    
    Returns:
        Dict with items (list), total, page, limit
    """
    from app.models import AuditLog, User
    
    query = {}
    
    if filters.get("action"):
        query["action"] = filters["action"]
    
    if filters.get("actor_id"):
        try:
            actor = User.objects.get(id=filters["actor_id"])
            query["actor"] = actor
        except User.DoesNotExist:
            return {"items": [], "total": 0, "page": page, "limit": limit}
    
    if filters.get("institute_id"):
        from app.models import Institute
        try:
            institute = Institute.objects.get(id=filters["institute_id"])
            query["institute"] = institute
        except Institute.DoesNotExist:
            return {"items": [], "total": 0, "page": page, "limit": limit}
    
    if filters.get("date_from") or filters.get("start_date"):
        date_from = filters.get("date_from") or filters.get("start_date")
        date_from = datetime.fromisoformat(date_from)
        query["created_at__gte"] = date_from
    
    if filters.get("date_to") or filters.get("end_date"):
        date_to = filters.get("date_to") or filters.get("end_date")
        date_to = datetime.fromisoformat(date_to)
        query["created_at__lte"] = date_to
    
    total = AuditLog.objects(**query).count()
    
    skip = (page - 1) * limit
    logs = AuditLog.objects(**query).order_by('-created_at').skip(skip).limit(limit)
    
    items = []
    for log in logs:
        actor_email = None
        if log.actor:
            actor_email = log.actor.email
        
        masked_email = _mask_email(actor_email) if actor_email else None
        
        items.append({
            "id": str(log.id),
            "actor_id": str(log.actor.id) if log.actor else None,
            "actor_email": masked_email,
            "actor_role": log.actor_role,
            "action": log.action,
            "target_type": log.target_type,
            "target_id": log.target_id,
            "institute_id": str(log.institute.id) if log.institute else None,
            "ip_address": log.ip_address,
            "metadata": log.metadata,
            "created_at": log.created_at.isoformat() if log.created_at else None
        })
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit
    }


def get_institute_stats(institute_id: str) -> Dict[str, Any]:
    """
    Per-institute stats for superadmin
    
    Args:
        institute_id: The institute ID
    
    Returns:
        Dict with comprehensive stats for the institute
    """
    from app.models import Institute, User, Exam, ExamAttempt, Result, Subscription, Payment
    from app.services.analytics_service import (
        get_overview_analytics,
        get_student_analytics,
        get_revenue_analytics
    )
    
    try:
        institute = Institute.objects.get(id=institute_id)
    except Institute.DoesNotExist:
        raise SuperadminServiceError("Institute not found", "INSTITUTE_NOT_FOUND")
    
    overview = get_overview_analytics(institute_id, "", "super_admin")
    
    student_stats = get_student_analytics(institute_id)
    
    revenue_stats = get_revenue_analytics(institute_id)
    
    exams = Exam.objects(institute=institute)
    exam_count = exams.count()
    published_exams = exams.filter(status='published').count()
    draft_exams = exams.filter(status='draft').count()
    active_exams = exams.filter(status='active').count()
    closed_exams = exams.filter(status='closed').count()
    
    exam_ids = [e.id for e in exams]
    
    total_attempts = 0
    in_progress_attempts = 0
    submitted_attempts = 0
    if exam_ids:
        total_attempts = ExamAttempt.objects(exam__in=exam_ids).count()
        in_progress_attempts = ExamAttempt.objects(exam__in=exam_ids, status='in_progress').count()
        submitted_attempts = ExamAttempt.objects(
            exam__in=exam_ids,
            status__in=['submitted', 'auto_submitted', 'force_submitted']
        ).count()
    
    results = Result.objects(exam__in=exam_ids) if exam_ids else []
    results_list = list(results)
    total_results = len(results_list)
    passed_results = len([r for r in results_list if r.passed])
    failed_results = total_results - passed_results
    
    avg_score = 0.0
    if results_list:
        total_percentage = sum(r.percentage for r in results_list)
        avg_score = round(total_percentage / len(results_list), 2)
    
    teachers = User.objects(institute=institute, role='teacher')
    teachers_count = teachers.count()
    
    students = User.objects(
        institute=institute,
        role__in=['student_registered', 'student_assigned']
    )
    students_count = students.count()
    
    subscription = institute.subscription
    subscription_data = None
    if subscription:
        plan = subscription.plan
        subscription_data = {
            "plan_name": plan.name if plan else "Unknown",
            "plan_slug": plan.slug if plan else None,
            "status": subscription.status,
            "start_date": subscription.start_date.isoformat() if subscription.start_date else None,
            "end_date": subscription.end_date.isoformat() if subscription.end_date else None,
            "is_active": subscription.is_active
        }
    
    institute_users = User.objects(institute=institute)
    user_ids = [u.id for u in institute_users]
    
    institute_payments = Payment.objects(
        user__in=user_ids,
        status='captured'
    )
    total_payments = institute_payments.sum('amount') or 0
    payment_count = institute_payments.count()
    
    recent_activity = []
    recent_attempts = ExamAttempt.objects(exam__in=exam_ids).order_by('-created_at').limit(10)
    for attempt in recent_attempts:
        student = attempt.student
        exam = attempt.exam
        recent_activity.append({
            "type": "attempt",
            "exam_title": exam.title if exam else "Unknown",
            "student_name": student.full_name if student else "Unknown",
            "status": attempt.status,
            "created_at": attempt.created_at.isoformat() if attempt.created_at else None
        })
    
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    daily_activity = []
    for i in range(7):
        day = datetime.utcnow() - timedelta(days=6 - i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        attempts_count = 0
        if exam_ids:
            attempts_count = ExamAttempt.objects(
                exam__in=exam_ids,
                created_at__gte=day_start,
                created_at__lte=day_end
            ).count()
        
        daily_activity.append({
            "date": day_start.strftime("%Y-%m-%d"),
            "attempts": attempts_count
        })
    
    return {
        "institute": {
            "id": str(institute.id),
            "name": institute.name,
            "slug": institute.slug,
            "city": institute.city,
            "state": institute.state,
            "country": institute.country,
            "is_active": institute.is_active,
            "is_suspended": institute.is_suspended,
            "created_at": institute.created_at.isoformat() if institute.created_at else None
        },
        "overview": overview,
        "students": student_stats,
        "revenue": revenue_stats,
        "exams": {
            "total": exam_count,
            "published": published_exams,
            "draft": draft_exams,
            "active": active_exams,
            "closed": closed_exams
        },
        "attempts": {
            "total": total_attempts,
            "in_progress": in_progress_attempts,
            "submitted": submitted_attempts
        },
        "results": {
            "total": total_results,
            "passed": passed_results,
            "failed": failed_results,
            "avg_score": avg_score
        },
        "users": {
            "teachers": teachers_count,
            "students": students_count
        },
        "subscription": subscription_data,
        "payments": {
            "total_amount": total_payments,
            "count": payment_count
        },
        "daily_activity_7d": daily_activity,
        "recent_activity": recent_activity
    }


def get_subscriptions(filters: Dict[str, Any], page: int, limit: int) -> Dict[str, Any]:
    """
    Paginated subscriptions with filters
    
    Args:
        filters: Dict with status, entity_type (institute/student), plan_id
        page: Page number (1-based)
        limit: Items per page
    
    Returns:
        Dict with items (list), total, page, limit
    """
    from app.models import Subscription, Institute, User, Plan
    
    query = {}
    
    if filters.get("status"):
        query["status"] = filters["status"]
    
    if filters.get("entity_type") == "institute":
        query["institute__ne"] = None
        query["student"] = None
    elif filters.get("entity_type") == "student":
        query["student__ne"] = None
    
    if filters.get("plan_id"):
        from bson import ObjectId
        try:
            query["plan"] = ObjectId(filters["plan_id"])
        except:
            pass
    
    total = Subscription.objects(**query).count()
    
    skip = (page - 1) * limit
    subs = Subscription.objects(**query).order_by('-created_at').skip(skip).limit(limit)
    
    items = []
    for sub in subs:
        plan_name = None
        plan_price = None
        if sub.plan:
            plan_name = sub.plan.name
            plan_price = sub.plan.price
        
        institute_name = None
        institute_id = None
        if sub.institute:
            institute_id = str(sub.institute.id)
            institute_name = getattr(sub.institute, 'name', None) or getattr(sub.institute, 'institute_name', None)
        
        student_email = None
        student_id = None
        if sub.student:
            student_id = str(sub.student.id)
            student_email = sub.student.email
        
        items.append({
            "id": str(sub.id),
            "entity_type": "institute" if sub.institute else "student",
            "institute_id": institute_id,
            "institute_name": institute_name,
            "student_id": student_id,
            "student_email": student_email,
            "plan_id": str(sub.plan.id) if sub.plan else None,
            "plan_name": plan_name,
            "plan_price": plan_price,
            "status": sub.status,
            "starts_at": sub.starts_at.isoformat() if sub.starts_at else None,
            "expires_at": sub.expires_at.isoformat() if sub.expires_at else None,
            "grace_until": sub.grace_until.isoformat() if sub.grace_until else None,
            "ai_usage_this_month": sub.ai_usage_this_month,
            "auto_renew": sub.auto_renew,
            "created_at": sub.created_at.isoformat() if sub.created_at else None,
        })
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit
    }


def get_exams(filters: Dict[str, Any], page: int, limit: int) -> Dict[str, Any]:
    """
    Paginated exams with filters
    
    Args:
        filters: Dict with status, exam_type, search
        page: Page number (1-based)
        limit: Items per page
    
    Returns:
        Dict with items (list), total, page, limit
    """
    from app.models import Exam, Institute, User, ExamAttempt
    from bson import ObjectId
    
    query = {}
    
    if filters.get("status"):
        query["status"] = filters["status"]
    
    if filters.get("exam_type"):
        query["exam_type"] = filters["exam_type"]
    
    if filters.get("search"):
        query["title__icontains"] = filters["search"]
    
    if filters.get("institute_id"):
        from bson import ObjectId
        try:
            query["institute"] = ObjectId(filters["institute_id"])
        except:
            pass
    
    total = Exam.objects(**query).count()
    
    skip = (page - 1) * limit
    exams = Exam.objects(**query).order_by('-created_at').skip(skip).limit(limit)
    
    items = []
    for exam in exams:
        # Get counts
        question_count = len(exam.questions) if hasattr(exam, 'questions') and exam.questions else 0
        attempts_count = ExamAttempt.objects(exam=exam).count()
        
        institute_name = None
        institute_id = None
        if exam.institute:
            institute_id = str(exam.institute.id)
            institute_name = getattr(exam.institute, 'name', None)
        
        creator_name = None
        creator_id = None
        if exam.created_by:
            creator_id = str(exam.created_by.id)
            creator_name = getattr(exam.created_by, 'full_name', None) or getattr(exam.created_by, 'email', None)
        
        items.append({
            "id": str(exam.id),
            "title": exam.title,
            "description": exam.description,
            "subject": exam.subject,
            "topic": exam.topic,
            "exam_type": exam.exam_type,
            "status": exam.status,
            "total_marks": exam.total_marks,
            "passing_percentage": exam.passing_percentage,
            "duration_minutes": exam.duration_minutes,
            "price": exam.price,
            "question_count": question_count,
            "attempts_count": attempts_count,
            "institute_id": institute_id,
            "institute_name": institute_name,
            "creator_id": creator_id,
            "creator_name": creator_name,
            "created_at": exam.created_at.isoformat() if exam.created_at else None,
        })
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit
    }
