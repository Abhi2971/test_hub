"""
Ebook service for ExamSaaS platform.
Pure Python - zero Flask imports, zero HTTP concepts.
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class EbookServiceError(Exception):
    """Base exception for ebook service errors."""
    def __init__(self, message: str, code: str, status_code: int = 400):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class EbookNotFoundError(EbookServiceError):
    """Ebook not found."""
    def __init__(self):
        super().__init__("Ebook not found", "EBOOK_NOT_FOUND", 404)


class EbookAccessDeniedError(EbookServiceError):
    """Access to ebook denied."""
    def __init__(self, message: str = "Access denied"):
        super().__init__(message, "EBOOK_ACCESS_DENIED", 403)


class EbookPurchaseRequiredError(EbookServiceError):
    """Ebook purchase required."""
    def __init__(self):
        super().__init__("Ebook purchase required", "EBOOK_PURCHASE_REQUIRED", 402)


class SubscriptionRequiredError(EbookServiceError):
    """Active subscription required."""
    def __init__(self):
        super().__init__("Active subscription required", "SUBSCRIPTION_REQUIRED", 402)


def _get_models():
    """Lazy-load models to avoid circular imports."""
    from app.models import Ebook, User, Institute, Subscription
    return Ebook, User, Institute, Subscription


def create_ebook(
    data: dict,
    uploaded_by: str,
    institute_id: Optional[str],
) -> dict:
    """
    Create Ebook record after Cloudinary upload.
    
    Args:
        data: Dictionary with cloudinary_url, cloudinary_public_id, title,
              description, subject, topics, access_level, price, 
              page_count, file_size_bytes, thumbnail_url
        uploaded_by: User ID who uploaded the ebook
        institute_id: Institute ID (optional)
    
    Returns:
        Created Ebook dict
    """
    Ebook, User, Institute, Subscription = _get_models()
    
    try:
        from bson import ObjectId
        user_oid = ObjectId(uploaded_by)
    except Exception as e:
        raise EbookServiceError(f"Invalid user ID: {e}", "INVALID_ID", 400)
    
    user = User.objects(id=user_oid).first()
    if not user:
        raise EbookServiceError("User not found", "USER_NOT_FOUND", 404)
    
    institute = None
    if institute_id:
        try:
            institute_oid = ObjectId(institute_id)
            institute = Institute.objects(id=institute_oid).first()
        except Exception:
            pass
    
    access_level = data.get("access_level", "subscription")
    if access_level not in ["free", "subscription", "purchase"]:
        access_level = "subscription"
    
    ebook = Ebook(
        title=data.get("title", "Untitled Ebook"),
        description=data.get("description"),
        subject=data.get("subject"),
        topics=data.get("topics"),
        cloudinary_url=data.get("cloudinary_url"),
        cloudinary_public_id=data.get("cloudinary_public_id"),
        thumbnail_url=data.get("thumbnail_url"),
        file_size_bytes=data.get("file_size_bytes", 0),
        page_count=data.get("page_count", 0),
        access_level=access_level,
        price=data.get("price", 0),
        institute=institute,
        uploaded_by=user,
        download_count=0,
        view_count=0,
        is_active=True,
    )
    ebook.save()
    
    logger.info(f"Ebook created: {ebook.id} by user {uploaded_by}")
    
    return {
        "id": str(ebook.id),
        "title": ebook.title,
        "description": ebook.description,
        "subject": ebook.subject,
        "topics": ebook.topics,
        "cloudinary_url": ebook.cloudinary_url,
        "thumbnail_url": ebook.thumbnail_url,
        "page_count": ebook.page_count,
        "access_level": ebook.access_level,
        "price": ebook.price,
        "institute_id": str(ebook.institute.id) if ebook.institute else None,
        "uploaded_by_id": str(ebook.uploaded_by.id) if ebook.uploaded_by else None,
        "download_count": ebook.download_count,
        "view_count": ebook.view_count,
        "is_active": ebook.is_active,
        "created_at": ebook.created_at.isoformat() if ebook.created_at else None,
    }


def list_ebooks(
    filters: dict,
    page: int,
    limit: int,
) -> dict:
    """
    List ebooks with filters: access_level, subject, institute_id
    
    Args:
        filters: Dictionary of filter options
        page: Page number
        limit: Items per page
    
    Returns:
        Paginated ebook list
    """
    Ebook, User, Institute, Subscription = _get_models()
    
    query = {"is_active": True}
    
    access_level = filters.get("access_level")
    if access_level:
        query["access_level"] = access_level
    
    subject = filters.get("subject")
    if subject:
        query["subject"] = subject
    
    institute_id = filters.get("institute_id")
    if institute_id:
        try:
            from bson import ObjectId
            institute_oid = ObjectId(institute_id)
            query["institute"] = institute_oid
        except Exception:
            pass
    
    total = Ebook.objects(**query).count()
    
    skip = (page - 1) * limit
    ebooks = Ebook.objects(**query).order_by("-created_at").skip(skip).limit(limit)
    
    items = []
    for ebook in ebooks:
        items.append({
            "id": str(ebook.id),
            "title": ebook.title,
            "description": ebook.description,
            "subject": ebook.subject,
            "topics": ebook.topics,
            "thumbnail_url": ebook.thumbnail_url,
            "page_count": ebook.page_count,
            "access_level": ebook.access_level,
            "price": ebook.price,
            "institute_id": str(ebook.institute.id) if ebook.institute else None,
            "view_count": ebook.view_count,
            "created_at": ebook.created_at.isoformat() if ebook.created_at else None,
        })
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
    }


def get_ebook_detail(
    ebook_id: str,
    user_id: str,
) -> dict:
    """
    Get ebook. Increment view_count.
    
    Args:
        ebook_id: Ebook ID
        user_id: Requesting user ID
    
    Returns:
        Ebook detail dict
    """
    Ebook, User, Institute, Subscription = _get_models()
    
    try:
        from bson import ObjectId
        ebook_oid = ObjectId(ebook_id)
    except Exception:
        raise EbookServiceError("Invalid ebook ID", "INVALID_ID", 400)
    
    ebook = Ebook.objects(id=ebook_oid, is_active=True).first()
    if not ebook:
        raise EbookNotFoundError()
    
    user = User.objects(id=user_id).first()
    if not user:
        raise EbookServiceError("User not found", "USER_NOT_FOUND", 404)
    
    ebook.view_count = (ebook.view_count or 0) + 1
    ebook.save()
    
    return {
        "id": str(ebook.id),
        "title": ebook.title,
        "description": ebook.description,
        "subject": ebook.subject,
        "topics": ebook.topics,
        "cloudinary_url": ebook.cloudinary_url,
        "thumbnail_url": ebook.thumbnail_url,
        "page_count": ebook.page_count,
        "access_level": ebook.access_level,
        "price": ebook.price,
        "institute_id": str(ebook.institute.id) if ebook.institute else None,
        "uploaded_by_id": str(ebook.uploaded_by.id) if ebook.uploaded_by else None,
        "download_count": ebook.download_count,
        "view_count": ebook.view_count,
        "is_active": ebook.is_active,
        "created_at": ebook.created_at.isoformat() if ebook.created_at else None,
    }


def _check_subscription_access(user) -> bool:
    """Check if user has active subscription."""
    from app.models import Subscription
    
    if not user:
        return False
    
    now = datetime.now(timezone.utc)
    
    if user.role in ["super_admin", "admin_public", "admin_college", "teacher"]:
        return True
    
    if user.institute and user.institute.subscription:
        sub = user.institute.subscription
        if sub.status == "active" and sub.expires_at > now:
            return True
    
    student_sub = Subscription.objects(student=user, status="active", expires_at__gt=now).first()
    if student_sub:
        return True
    
    return False


def _check_purchase_access(user_id: str, ebook_id: str) -> bool:
    """Check if user has purchased the ebook."""
    from app.models import WalletTransaction
    
    try:
        from bson import ObjectId
        user_oid = ObjectId(user_id)
        ebook_oid = ObjectId(ebook_id)
    except Exception:
        return False
    
    transaction = WalletTransaction.objects(
        user=user_oid,
        purpose="ebook_purchase",
        reference_id=str(ebook_oid),
    ).first()
    
    return transaction is not None


def get_ebook_read_url(
    ebook_id: str,
    user_id: str,
) -> dict:
    """
    Get signed Cloudinary URL for ebook. Check access rights.
    
    Args:
        ebook_id: Ebook ID
        user_id: Requesting user ID
    
    Returns:
        Dict with signed URL and expiration
    """
    Ebook, User, Institute, Subscription = _get_models()
    
    try:
        from bson import ObjectId
        ebook_oid = ObjectId(ebook_id)
    except Exception:
        raise EbookServiceError("Invalid ebook ID", "INVALID_ID", 400)
    
    ebook = Ebook.objects(id=ebook_oid, is_active=True).first()
    if not ebook:
        raise EbookNotFoundError()
    
    user = User.objects(id=user_id).first()
    if not user:
        raise EbookServiceError("User not found", "USER_NOT_FOUND", 404)
    
    has_access = False
    
    if ebook.access_level == "free":
        has_access = True
    elif ebook.access_level == "subscription":
        has_access = _check_subscription_access(user)
        if not has_access:
            raise SubscriptionRequiredError()
    elif ebook.access_level == "purchase":
        has_access = _check_purchase_access(user_id, ebook_id)
        if not has_access:
            raise EbookPurchaseRequiredError()
    
    if not has_access:
        raise EbookAccessDeniedError("You do not have access to this ebook")
    
    expires_in = 3600
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
    
    try:
        from app.services import cloudinary_service
        signed_url = cloudinary_service.get_signed_url(
            ebook.cloudinary_public_id,
            expires_in=expires_in,
        )
    except Exception as e:
        logger.warning(f"Failed to generate signed URL: {e}")
        signed_url = ebook.cloudinary_url
    
    ebook.download_count = (ebook.download_count or 0) + 1
    ebook.save()
    
    logger.info(f"Generated read URL for ebook {ebook_id} for user {user_id}")
    
    return {
        "url": signed_url,
        "expires_at": expires_at.isoformat(),
    }


def delete_ebook(
    ebook_id: str,
    user_id: str,
) -> dict:
    """
    Soft delete ebook.
    
    Args:
        ebook_id: Ebook ID
        user_id: Requesting user ID
    
    Returns:
        Deletion result
    """
    Ebook, User, Institute, Subscription = _get_models()
    
    try:
        from bson import ObjectId
        ebook_oid = ObjectId(ebook_id)
        user_oid = ObjectId(user_id)
    except Exception:
        raise EbookServiceError("Invalid ID", "INVALID_ID", 400)
    
    user = User.objects(id=user_oid).first()
    if not user:
        raise EbookServiceError("User not found", "USER_NOT_FOUND", 404)
    
    ebook = Ebook.objects(id=ebook_oid).first()
    if not ebook:
        raise EbookNotFoundError()
    
    can_delete = False
    if user.role in ["super_admin", "admin_public"]:
        can_delete = True
    elif user.role == "admin_college" and user.institute:
        if ebook.institute and str(ebook.institute.id) == str(user.institute.id):
            can_delete = True
    elif user.role == "teacher" and ebook.uploaded_by:
        if str(ebook.uploaded_by.id) == str(user.id):
            can_delete = True
    
    if not can_delete:
        raise EbookAccessDeniedError("You cannot delete this ebook")
    
    ebook.is_active = False
    ebook.save()
    
    logger.info(f"Ebook deleted: {ebook_id} by user {user_id}")
    
    return {
        "deleted": True,
        "ebook_id": ebook_id,
    }


def update_ebook(
    ebook_id: str,
    data: dict,
    user_id: str,
) -> dict:
    """
    Update ebook fields.
    
    Args:
        ebook_id: Ebook ID
        data: Dictionary of fields to update
        user_id: Requesting user ID
    
    Returns:
        Updated ebook dict
    """
    Ebook, User, Institute, Subscription = _get_models()
    
    try:
        from bson import ObjectId
        ebook_oid = ObjectId(ebook_id)
        user_oid = ObjectId(user_id)
    except Exception:
        raise EbookServiceError("Invalid ID", "INVALID_ID", 400)
    
    user = User.objects(id=user_oid).first()
    if not user:
        raise EbookServiceError("User not found", "USER_NOT_FOUND", 404)
    
    ebook = Ebook.objects(id=ebook_oid).first()
    if not ebook:
        raise EbookNotFoundError()
    
    can_edit = False
    if user.role in ["super_admin", "admin_public"]:
        can_edit = True
    elif user.role == "admin_college" and user.institute:
        if ebook.institute and str(ebook.institute.id) == str(user.institute.id):
            can_edit = True
    elif user.role == "teacher" and ebook.uploaded_by:
        if str(ebook.uploaded_by.id) == str(user.id):
            can_edit = True
    
    if not can_edit:
        raise EbookAccessDeniedError("You cannot edit this ebook")
    
    updatable_fields = [
        "title", "description", "subject", "topics",
        "access_level", "price", "thumbnail_url",
    ]
    
    for field in updatable_fields:
        if field in data and data[field] is not None:
            setattr(ebook, field, data[field])
    
    ebook.save()
    
    logger.info(f"Ebook updated: {ebook_id} by user {user_id}")
    
    return {
        "id": str(ebook.id),
        "title": ebook.title,
        "description": ebook.description,
        "subject": ebook.subject,
        "topics": ebook.topics,
        "access_level": ebook.access_level,
        "price": ebook.price,
        "thumbnail_url": ebook.thumbnail_url,
        "updated_at": ebook.updated_at.isoformat() if ebook.updated_at else None,
    }
