"""
Certificate routes for ExamSaaS platform.
Blueprint: /api/v1/certificates
"""
import logging
from flask import Blueprint, request, g

from app.response import success_response, error_response
from app.utils.decorators import require_auth, require_roles, audit_log
from app.services.certificate_service import (
    get_student_certificates,
    get_certificate_download_url,
    verify_certificate,
    revoke_certificate,
    CertificateServiceError,
    CertificateNotFoundError,
)

logger = logging.getLogger(__name__)

certificates_bp = Blueprint("certificates", __name__, url_prefix="/certificates")


def _handle_service_error(error: CertificateServiceError):
    """Handle certificate service errors."""
    return error_response(error.message, error.status_code)


@certificates_bp.route("", methods=["GET"])
@require_roles("student_registered", "student_assigned")
def list():
    """
    Get student's earned certificates.
    
    Returns:
        200: List of certificates earned by the student
    """
    try:
        certificates = get_student_certificates(
            student_id=g.current_user_id,
        )
        
        return success_response({"certificates": certificates})
    
    except CertificateServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"List certificates failed: {e}")
        return error_response("Failed to list certificates", 500)


@certificates_bp.route("/<certificate_id>/download", methods=["GET"])
@require_roles("student_registered", "student_assigned")
def download(certificate_id: str):
    """
    Get download URL for certificate.
    
    Returns:
        200: { download_url, expires_in }
    """
    try:
        result = get_certificate_download_url(
            certificate_id=certificate_id,
            user_id=g.current_user_id,
        )
        
        return success_response(result)
    
    except CertificateNotFoundError as e:
        return _handle_service_error(e)
    except CertificateServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Get certificate download URL failed: {e}")
        return error_response("Failed to get download URL", 500)


@certificates_bp.route("/verify/<code>", methods=["GET"])
def verify(code: str):
    """
    Verify a certificate by its unique code.
    
    This endpoint is public - no authentication required.
    
    Returns:
        200: { student_name, exam_name, institute_name, issued_at, score, grade, is_revoked }
    """
    try:
        result = verify_certificate(verification_code=code)
        
        return success_response(result)
    
    except CertificateNotFoundError as e:
        return _handle_service_error(e)
    except CertificateServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Verify certificate failed: {e}")
        return error_response("Failed to verify certificate", 500)


@certificates_bp.route("/<certificate_id>/revoke", methods=["POST"])
@require_roles("super_admin")
@audit_log(action="revoke_certificate", target_type="Certificate")
def revoke(certificate_id: str):
    """
    Revoke a certificate.
    
    Input:
        - revoke_reason: Reason for revocation (required)
    
    Returns:
        200: Revoked certificate
    """
    data = request.get_json()
    
    if not data or "revoke_reason" not in data:
        return error_response("revoke_reason is required", 400)
    
    try:
        certificate = revoke_certificate(
            certificate_id=certificate_id,
            revoked_by=g.current_user_id,
            revoke_reason=data["revoke_reason"],
        )
        
        return success_response(certificate, "Certificate revoked successfully")
    
    except CertificateNotFoundError as e:
        return _handle_service_error(e)
    except CertificateServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Revoke certificate failed: {e}")
        return error_response("Failed to revoke certificate", 500)