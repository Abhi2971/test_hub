"""
Certificate service for ExamSaaS platform.
Pure Python - zero Flask imports, zero HTTP concepts.
"""
import logging
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List

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
            logger.warning("Redis not available for certificate service")
            return None
    return REDIS_CLIENT


def _get_config(key: str, default: Any = None) -> Any:
    """Get configuration value."""
    try:
        from flask import current_app
        return current_app.config.get(key, default)
    except RuntimeError:
        return default


def _queue_certificate_email(student_email: str, student_name: str, exam_title: str, certificate_url: str, certificate_id: str) -> bool:
    """Queue certificate email via Celery."""
    try:
        from app.tasks.email_tasks import EmailTask
        task = EmailTask()
        task.send_certificate_email_task.delay(
            student_email=student_email,
            student_name=student_name,
            exam_title=exam_title,
            certificate_url=certificate_url,
            certificate_id=certificate_id,
        )
        return True
    except Exception as e:
        logger.error(f"Failed to queue certificate email: {e}")
        return False


class CertificateServiceError(Exception):
    """Base exception for certificate service errors."""
    def __init__(self, message: str, code: str, status_code: int = 400):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class CertificateNotFoundError(CertificateServiceError):
    """Certificate not found."""
    def __init__(self):
        super().__init__("Certificate not found", "CERTIFICATE_NOT_FOUND", 404)


class AccessDeniedError(CertificateServiceError):
    """Access denied to certificate."""
    def __init__(self):
        super().__init__("Access denied to this certificate", "ACCESS_DENIED", 403)


class CertificateRevokedError(CertificateServiceError):
    """Certificate has been revoked."""
    def __init__(self, reason: str = None):
        message = "Certificate has been revoked"
        if reason:
            message += f": {reason}"
        super().__init__(message, "CERTIFICATE_REVOKED", 410)


def _generate_certificate_code() -> str:
    """Generate unique certificate code."""
    uuid_part = uuid.uuid4().hex[:8].upper()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    return f"CRT-{timestamp}-{uuid_part}"


def _get_signed_cloudinary_url(public_id: str, expires_in: int = 3600) -> tuple:
    """
    Get signed Cloudinary URL.
    
    Args:
        public_id: Cloudinary public ID
        expires_in: Seconds until expiration
    
    Returns:
        Tuple of (url, expires_at)
    """
    try:
        from app.services.cloudinary_service import get_signed_url as cloudinary_signed_url
        
        url = cloudinary_signed_url(public_id, expires_in)
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        
        return url, expires_at
    except Exception as e:
        logger.error(f"Failed to get signed URL: {e}")
        cloud_name = _get_config("CLOUDINARY_CLOUD_NAME", "demo")
        fallback_url = f"https://res.cloudinary.com/{cloud_name}/raw/upload/{public_id}"
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        return fallback_url, expires_at


def get_student_certificates(student_id: str) -> list:
    """
    Get all certificates for a student.
    
    Args:
        student_id: Student user ID
    
    Returns:
        List of certificate dictionaries
    """
    from app.models import Certificate, User
    
    user = User.objects(id=student_id).first()
    if not user:
        return []
    
    certificates = Certificate.objects(student=user).order_by("-created_at")
    
    result = []
    for cert in certificates:
        cert_dict = cert.to_dict()
        cert_dict["is_revoked"] = cert.is_revoked
        cert_dict["revoked_reason"] = cert.revoked_reason
        result.append(cert_dict)
    
    return result


def get_certificate_download_url(certificate_id: str, user_id: str) -> dict:
    """
    Get signed download URL for a certificate.
    
    Args:
        certificate_id: Certificate ID
        user_id: User ID requesting the download
    
    Returns:
        Dict with download_url and expires_at
    
    Raises:
        CertificateNotFoundError: If certificate not found
        AccessDeniedError: If user doesn't own the certificate
    """
    from app.models import Certificate
    
    certificate = Certificate.objects(id=certificate_id).first()
    if not certificate:
        raise CertificateNotFoundError()
    
    if str(certificate.student.id) != user_id:
        raise AccessDeniedError()
    
    if certificate.is_revoked:
        raise CertificateRevokedError(certificate.revoked_reason)
    
    if not certificate.cloudinary_public_id:
        raise CertificateServiceError(
            "Certificate file not available",
            "CERTIFICATE_FILE_MISSING",
            404
        )
    
    download_url, expires_at = _get_signed_cloudinary_url(
        certificate.cloudinary_public_id,
        expires_in=3600
    )
    
    return {
        "download_url": download_url,
        "expires_at": expires_at.isoformat(),
    }


def verify_certificate(code: str) -> dict:
    """
    Verify a certificate by its public code.
    This is a public endpoint for external verification.
    
    Args:
        code: Certificate code
    
    Returns:
        Certificate details dictionary
    
    Raises:
        CertificateNotFoundError: If certificate not found
    """
    from app.models import Certificate
    
    certificate = Certificate.objects(certificate_code=code).first()
    if not certificate:
        raise CertificateNotFoundError()
    
    result = {
        "student_name": certificate.student_name,
        "exam_name": certificate.exam_name,
        "institute_name": certificate.institute_name,
        "score": certificate.score,
        "grade": certificate.grade,
        "issued_at": certificate.issued_at.isoformat() if certificate.issued_at else None,
        "is_revoked": certificate.is_revoked,
    }
    
    if certificate.is_revoked and certificate.revoked_reason:
        result["revoked_reason"] = certificate.revoked_reason
    
    return result


def revoke_certificate(certificate_id: str, reason: str, revoked_by: str) -> dict:
    """
    Revoke a certificate.
    
    Args:
        certificate_id: Certificate ID
        reason: Reason for revocation
        revoked_by: User ID revoking the certificate
    
    Returns:
        Updated certificate dictionary
    
    Raises:
        CertificateNotFoundError: If certificate not found
    """
    from app.models import Certificate, User, AuditLog
    
    if not reason or not reason.strip():
        raise CertificateServiceError("Revocation reason is required", "REASON_REQUIRED", 400)
    
    certificate = Certificate.objects(id=certificate_id).first()
    if not certificate:
        raise CertificateNotFoundError()
    
    if certificate.is_revoked:
        raise CertificateServiceError("Certificate already revoked", "ALREADY_REVOKED", 400)
    
    certificate.is_revoked = True
    certificate.revoked_reason = reason.strip()
    certificate.save()
    
    actor = User.objects(id=revoked_by).first()
    if actor:
        institute_id = None
        if certificate.institute:
            institute_id = certificate.institute.id
        
        audit_log = AuditLog(
            actor=actor,
            actor_role=actor.role,
            action="revoke_certificate",
            target_type="Certificate",
            target_id=str(certificate.id),
            institute=certificate.institute,
            metadata={
                "certificate_code": certificate.certificate_code,
                "reason": reason,
                "student_id": str(certificate.student.id),
            }
        )
        audit_log.save()
    
    logger.info(f"Certificate {certificate.certificate_code} revoked by {revoked_by}: {reason}")
    
    _queue_certificate_email(
        student_email=certificate.student.email if certificate.student else "",
        student_name=certificate.student_name or "Student",
        exam_title=certificate.exam_name or "Exam",
        certificate_url="",
        certificate_id=str(certificate.id),
    )
    
    cert_dict = certificate.to_dict()
    cert_dict["is_revoked"] = certificate.is_revoked
    cert_dict["revoked_reason"] = certificate.revoked_reason
    
    return cert_dict


def create_certificate(
    student_id: str,
    exam_id: str,
    result_id: str,
    institute_id: str,
    student_name: str,
    exam_name: str,
    institute_name: str,
    score: float,
    grade: str,
    cloudinary_url: str = None,
    cloudinary_public_id: str = None
) -> dict:
    """
    Create a new certificate (internal function).
    
    Args:
        student_id: Student user ID
        exam_id: Exam ID
        result_id: Result ID
        institute_id: Institute ID
        student_name: Student name
        exam_name: Exam name
        institute_name: Institute name
        score: Exam score
        grade: Exam grade
        cloudinary_url: Cloudinary URL (optional)
        cloudinary_public_id: Cloudinary public ID (optional)
    
    Returns:
        Created certificate dictionary
    """
    from app.models import Certificate, User, Exam, Result, Institute
    
    student = User.objects(id=student_id).first()
    if not student:
        raise CertificateServiceError("Student not found", "STUDENT_NOT_FOUND", 404)
    
    exam = Exam.objects(id=exam_id).first()
    if not exam:
        raise CertificateServiceError("Exam not found", "EXAM_NOT_FOUND", 404)
    
    result = Result.objects(id=result_id).first()
    if not result:
        raise CertificateServiceError("Result not found", "RESULT_NOT_FOUND", 404)
    
    institute = None
    if institute_id:
        institute = Institute.objects(id=institute_id).first()
    
    existing_cert = Certificate.objects(result=result).first()
    if existing_cert:
        raise CertificateServiceError(
            "Certificate already exists for this result",
            "CERTIFICATE_EXISTS",
            409
        )
    
    certificate_code = _generate_certificate_code()
    
    while Certificate.objects(certificate_code=certificate_code).first():
        certificate_code = _generate_certificate_code()
    
    certificate = Certificate(
        student=student,
        exam=exam,
        result=result,
        institute=institute,
        certificate_code=certificate_code,
        cloudinary_url=cloudinary_url,
        cloudinary_public_id=cloudinary_public_id,
        student_name=student_name,
        exam_name=exam_name,
        institute_name=institute_name,
        score=score,
        grade=grade,
        issued_at=datetime.now(timezone.utc),
    )
    certificate.save()
    
    logger.info(f"Certificate created: {certificate_code} for student {student_id}")
    
    return certificate.to_dict()


def list_certificates(institute_id: str = None, filters: dict = None, page: int = 1, limit: int = 20) -> dict:
    """
    List certificates with filtering and pagination.
    
    Args:
        institute_id: Institute ID (optional)
        filters: Dict with optional keys: student_id, exam_id, is_revoked
        page: Page number (1-based)
        limit: Items per page
    
    Returns:
        Dict with certificates list and pagination info
    """
    from app.models import Certificate
    
    query = {}
    
    if institute_id:
        from app.models import Institute
        institute = Institute.objects(id=institute_id).first()
        if institute:
            query["institute"] = institute
    
    if filters:
        if filters.get("student_id"):
            from app.models import User
            student = User.objects(id=filters["student_id"]).first()
            if student:
                query["student"] = student
        
        if filters.get("exam_id"):
            from app.models import Exam
            exam = Exam.objects(id=filters["exam_id"]).first()
            if exam:
                query["exam"] = exam
        
        if filters.get("is_revoked") is not None:
            query["is_revoked"] = filters["is_revoked"]
    
    offset = (page - 1) * limit
    
    certificates = Certificate.objects(**query).order_by("-created_at").skip(offset).limit(limit)
    total = Certificate.objects(**query).count()
    
    cert_list = []
    for cert in certificates:
        cert_dict = cert.to_dict()
        cert_dict["is_revoked"] = cert.is_revoked
        cert_dict["revoked_reason"] = cert.revoked_reason
        cert_list.append(cert_dict)
    
    return {
        "certificates": cert_list,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit,
        }
    }


def get_certificate_by_id(certificate_id: str, user_id: str = None, user_role: str = None) -> dict:
    """
    Get a certificate by ID.
    
    Args:
        certificate_id: Certificate ID
        user_id: User ID requesting (optional, for access check)
        user_role: User role (optional, for access check)
    
    Returns:
        Certificate dictionary
    
    Raises:
        CertificateNotFoundError: If certificate not found
        AccessDeniedError: If user doesn't have access
    """
    from app.models import Certificate
    
    certificate = Certificate.objects(id=certificate_id).first()
    if not certificate:
        raise CertificateNotFoundError()
    
    if user_id and user_role:
        is_agent = user_role in ["support_agent", "admin_college", "admin_public", "super_admin"]
        is_owner = str(certificate.student.id) == user_id
        
        if not is_agent and not is_owner:
            if certificate.institute:
                from app.models import User
                user = User.objects(id=user_id).first()
                if not user or not user.institute or str(user.institute.id) != str(certificate.institute.id):
                    raise AccessDeniedError()
    
    cert_dict = certificate.to_dict()
    cert_dict["is_revoked"] = certificate.is_revoked
    cert_dict["revoked_reason"] = certificate.revoked_reason
    
    return cert_dict