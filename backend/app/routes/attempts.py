"""
Attempt routes for ExamSaaS platform.
Blueprint: /api/v1/attempts
"""
import logging
from flask import Blueprint, request, g

from app.response import success_response, error_response
from app.schemas.exam_schemas import (
    start_exam_schema,
    save_answers_schema,
    log_violation_schema,
    force_submit_schema,
)
from app.services.attempt_service import (
    start_attempt,
    get_attempt,
    save_answers,
    submit_attempt,
    log_violation,
    force_submit_attempt,
    get_attempt_questions,
    list_attempts,
    AttemptServiceError,
    AttemptNotFoundError,
)
from app.utils.decorators import require_auth, audit_log

logger = logging.getLogger(__name__)

attempts_bp = Blueprint("attempts", __name__, url_prefix="/attempts")


def _handle_service_error(error: AttemptServiceError):
    """Handle attempt service errors."""
    return error_response(error.message, error.status_code)


def _validate_schema(schema, data):
    """Validate request data against schema."""
    try:
        return schema.load(data), None
    except Exception as e:
        errors = e.messages if hasattr(e, "messages") else str(e)
        return None, errors


@attempts_bp.route("/start/<exam_id>", methods=["POST"])
@require_auth
def start(exam_id: str):
    """Start an exam attempt."""
    data = request.get_json() or {}
    
    validated, errors = _validate_schema(start_exam_schema, data)
    if errors:
        return error_response("Validation error", 422, errors)
    
    try:
        attempt = start_attempt(
            exam_id=exam_id,
            student_id=g.current_user_id,
            passcode=validated.get("passcode"),
            ip_address=request.remote_addr,
            user_agent=str(request.headers.get("User-Agent", ""))[:500],
        )
        
        return success_response(attempt, "Exam started successfully", status=201)
    
    except AttemptServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Start attempt failed: {e}")
        return error_response("Failed to start exam", 500)


@attempts_bp.route("/<attempt_id>", methods=["GET"])
@require_auth
def get(attempt_id: str):
    """Get attempt by ID."""
    try:
        attempt = get_attempt(attempt_id, g.current_user_id)
        return success_response(attempt)
    except AttemptNotFoundError as e:
        return _handle_service_error(e)
    except AttemptServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Get attempt failed: {e}")
        return error_response("Failed to get attempt", 500)


@attempts_bp.route("/<attempt_id>/questions", methods=["GET"])
@require_auth
def get_questions(attempt_id: str):
    """Get questions for an active attempt."""
    try:
        questions = get_attempt_questions(attempt_id, g.current_user_id)
        return success_response({"questions": questions})
    except AttemptNotFoundError as e:
        return _handle_service_error(e)
    except AttemptServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Get attempt questions failed: {e}")
        return error_response("Failed to get questions", 500)


@attempts_bp.route("/<attempt_id>/answers", methods=["PUT"])
@require_auth
def save(attempt_id: str):
    """Save answers for an attempt."""
    data = request.get_json()
    if not data:
        return error_response("Request body is required", 400)
    
    validated, errors = _validate_schema(save_answers_schema, data)
    if errors:
        return error_response("Validation error", 422, errors)
    
    try:
        result = save_answers(
            attempt_id=attempt_id,
            student_id=g.current_user_id,
            answers=validated["answers"],
        )
        
        return success_response(result, "Answers saved successfully")
    
    except AttemptServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Save answers failed: {e}")
        return error_response("Failed to save answers", 500)


@attempts_bp.route("/<attempt_id>/submit", methods=["POST"])
@require_auth
def submit(attempt_id: str):
    """Submit an exam attempt."""
    try:
        result = submit_attempt(attempt_id, g.current_user_id)
        return success_response(result, "Exam submitted successfully")
    except AttemptServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Submit attempt failed: {e}")
        return error_response("Failed to submit exam", 500)


@attempts_bp.route("/<attempt_id>/violation", methods=["POST"])
@require_auth
def log_viol(attempt_id: str):
    """Log a violation during exam."""
    data = request.get_json()
    if not data:
        return error_response("Request body is required", 400)
    
    validated, errors = _validate_schema(log_violation_schema, data)
    if errors:
        return error_response("Validation error", 422, errors)
    
    try:
        result = log_violation(
            attempt_id=attempt_id,
            student_id=g.current_user_id,
            violation_type=validated["violation_type"],
            screenshot_url=validated.get("screenshot_url"),
        )
        
        if result.get("force_submit"):
            return success_response(result, "Maximum violations exceeded. Exam auto-submitted.")
        
        return success_response(result, "Violation logged")
    
    except AttemptServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Log violation failed: {e}")
        return error_response("Failed to log violation", 500)


@attempts_bp.route("/<attempt_id>/force-submit", methods=["POST"])
@require_auth
@audit_log(action="force_submit_attempt", target_type="ExamAttempt")
def force_submit(attempt_id: str):
    """Force submit an attempt (admin action)."""
    data = request.get_json() or {}
    
    validated, errors = _validate_schema(force_submit_schema, data)
    if errors:
        return error_response("Validation error", 422, errors)
    
    try:
        result = force_submit_attempt(
            attempt_id=attempt_id,
            admin_id=g.current_user_id,
            reason=validated.get("reason", "Admin forced submission"),
        )
        
        return success_response(result, "Attempt force submitted")
    
    except AttemptServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Force submit failed: {e}")
        return error_response("Failed to force submit", 500)


@attempts_bp.route("", methods=["GET"])
@require_auth
def list():
    """List attempts with pagination."""
    exam_id = request.args.get("exam_id")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    status = request.args.get("status")
    
    try:
        result = list_attempts(
            user_id=g.current_user_id,
            exam_id=exam_id,
            page=page,
            per_page=per_page,
            status=status,
        )
        
        return success_response(result)
    except AttemptServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"List attempts failed: {e}")
        return error_response("Failed to list attempts", 500)
