"""
Exam routes for ExamSaaS platform.
Blueprint: /api/v1/exams
"""
import logging
from typing import Any, Dict, Optional, List
from flask import Blueprint, request, g

from app.response import success_response, error_response
from app.schemas.exam_schemas import (
    create_exam_schema,
    update_exam_schema,
    start_exam_schema,
    generate_magic_link_schema,
    assign_questions_schema,
    exam_list_schema,
    magic_link_verify_schema,
)
from app.services.exam_service import (
    create_exam,
    get_exam,
    update_exam,
    publish_exam,
    activate_exam,
    close_exam,
    delete_exam,
    list_exams,
    generate_magic_link,
    verify_magic_link,
    assign_questions_to_exam,
    get_exam_questions,
    get_exam_results,
    ExamServiceError,
    ExamNotFoundError,
    ExamAccessDeniedError,
)
from app.utils.decorators import require_auth

logger = logging.getLogger(__name__)

exams_bp = Blueprint("exams", __name__, url_prefix="/exams")


def _handle_service_error(error: ExamServiceError):
    """Handle exam service errors."""
    return error_response(error.message, None, error.status_code)


def _validate_schema(schema, data):
    """Validate request data against schema."""
    try:
        return schema.load(data), None
    except Exception as e:
        errors = e.messages if hasattr(e, "messages") else str(e)
        return None, errors


@exams_bp.route("", methods=["POST"])
@require_auth
def create():
    """Create a new exam."""
    data = request.get_json()
    if not data:
        return error_response("Request body is required", None, 400)

    validated, errors = _validate_schema(create_exam_schema, data)
    if errors:
        return error_response("Validation error", errors, 422)

    try:
        institute_id = getattr(g, "current_institute_id", None)

        exam = create_exam(
            creator_id=g.current_user_id,
            institute_id=institute_id,
            title=validated["title"],
            description=validated.get("description"),
            subject=validated.get("subject"),
            topic=validated.get("topic"),
            duration_minutes=validated.get("duration_minutes", 60),
            total_marks=validated.get("total_marks", 0),
            passing_percentage=validated.get("passing_percentage", 40.0),
            exam_type=validated.get("exam_type", "institute"),
            result_mode=validated.get("result_mode", "instant"),
            access_mode=validated.get("access_mode", "open"),
            price=validated.get("price", 0),
            allowed_attempts=validated.get("allowed_attempts", 1),
            certificate_enabled=validated.get("certificate_enabled", False),
            start_at=validated.get("schedule", {}).get("start_at") if validated.get("schedule") else None,
            end_at=validated.get("schedule", {}).get("end_at") if validated.get("schedule") else None,
            grace_minutes=validated.get("schedule", {}).get("grace_minutes", 5) if validated.get("schedule") else 5,
            camera_required=validated.get("security", {}).get("camera_required", False) if validated.get("security") else False,
            tab_switch_limit=validated.get("security", {}).get("tab_switch_limit", 3) if validated.get("security") else 3,
            fullscreen_required=validated.get("security", {}).get("fullscreen_required", False) if validated.get("security") else False,
            copy_paste_disabled=validated.get("security", {}).get("copy_paste_disabled", False) if validated.get("security") else False,
            shuffle_questions=validated.get("security", {}).get("shuffle_questions", False) if validated.get("security") else False,
            shuffle_options=validated.get("security", {}).get("shuffle_options", False) if validated.get("security") else False,
            passcode=validated.get("passcode"),
        )

        return success_response(exam, "Exam created successfully", status=201)

    except ExamServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Create exam failed: {e}")
        return error_response("Failed to create exam", None, 500)


@exams_bp.route("/<exam_id>", methods=["GET"])
@require_auth
def get(exam_id: str):
    """Get exam by ID."""
    try:
        exam = get_exam(exam_id, g.current_user_id)
        return success_response(exam)
    except ExamNotFoundError as e:
        return _handle_service_error(e)
    except ExamServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Get exam failed: {e}")
        return error_response("Failed to get exam", None, 500)


@exams_bp.route("/<exam_id>", methods=["PATCH"])
@require_auth
def update(exam_id: str):
    """Update an exam."""
    data = request.get_json()
    if not data:
        return error_response("Request body is required", None, 400)

    validated, errors = _validate_schema(update_exam_schema, data)
    if errors:
        return error_response("Validation error", errors, 422)

    try:
        exam = update_exam(
            exam_id=exam_id,
            user_id=g.current_user_id,
            title=validated.get("title"),
            description=validated.get("description"),
            subject=validated.get("subject"),
            topic=validated.get("topic"),
            duration_minutes=validated.get("duration_minutes"),
            total_marks=validated.get("total_marks"),
            passing_percentage=validated.get("passing_percentage"),
            result_mode=validated.get("result_mode"),
            access_mode=validated.get("access_mode"),
            price=validated.get("price"),
            allowed_attempts=validated.get("allowed_attempts"),
            certificate_enabled=validated.get("certificate_enabled"),
            schedule=validated.get("schedule"),
            security=validated.get("security"),
        )

        return success_response(exam, "Exam updated successfully")
    except ExamServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Update exam failed: {e}")
        return error_response("Failed to update exam", None, 500)


@exams_bp.route("/<exam_id>", methods=["DELETE"])
@require_auth
def delete(exam_id: str):
    """Delete an exam."""
    try:
        delete_exam(exam_id, g.current_user_id)
        return success_response(None, "Exam deleted successfully")
    except ExamServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Delete exam failed: {e}")
        return error_response("Failed to delete exam", None, 500)


@exams_bp.route("/<exam_id>/publish", methods=["POST"])
@require_auth
def publish(exam_id: str):
    """Publish an exam."""
    try:
        exam = publish_exam(exam_id, g.current_user_id)
        return success_response(exam, "Exam published successfully")
    except ExamServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Publish exam failed: {e}")
        return error_response("Failed to publish exam", None, 500)



@exams_bp.route("/<exam_id>/assign-questions", methods=["POST"])
@require_auth
def assign_questions(exam_id: str):
    """Assign questions to an exam."""
    data = request.get_json()
    if not data:
        return error_response("Request body is required", None, 400)

    validated, errors = _validate_schema(assign_questions_schema, data)
    if errors:
        return error_response("Validation error", errors, 422)

    try:
        result = assign_questions_to_exam(
            exam_id=exam_id,
            user_id=g.current_user_id,
            question_ids=validated["question_ids"],
            marks_per_question=validated.get("marks_per_question"),
        )

        return success_response(result, "Questions assigned successfully")
    except ExamServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Assign questions failed: {e}")
        return error_response("Failed to assign questions", None, 500)


@exams_bp.route("/<exam_id>/activate", methods=["POST"])
@require_auth
def activate(exam_id: str):
    """Activate an exam."""
    try:
        exam = activate_exam(exam_id, g.current_user_id)
        return success_response(exam, "Exam activated successfully")
    except ExamServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Activate exam failed: {e}")
        return error_response("Failed to activate exam", None, 500)


@exams_bp.route("/<exam_id>/close", methods=["POST"])
@require_auth
def close(exam_id: str):
    """Close an exam."""
    try:
        exam = close_exam(exam_id, g.current_user_id)
        return success_response(exam, "Exam closed successfully")
    except ExamServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Close exam failed: {e}")
        return error_response("Failed to close exam", None, 500)


@exams_bp.route("", methods=["GET"])
@require_auth
def list():
    """List exams with pagination."""
    args = request.args.to_dict()

    validated, errors = _validate_schema(exam_list_schema, args)
    if errors:
        return error_response("Validation error", errors, 422)

    try:
        result = list_exams(
            user_id=g.current_user_id,
            page=validated.get("page", 1),
            per_page=validated.get("per_page", 20),
            status=validated.get("status"),
            institute_id=validated.get("institute_id"),
            search=validated.get("search"),
            exam_type=validated.get("exam_type"),
        )

        return success_response(result)
    except ExamServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        import traceback
        logger.exception(f"List exams failed: {e}\n{traceback.format_exc()}")
        return error_response("Failed to list exams", None, 500)


@exams_bp.route("/<exam_id>/magic-links", methods=["POST"])
@require_auth
def create_magic_links(exam_id: str):
    """Generate magic links for exam access."""
    data = request.get_json() or {}

    validated, errors = _validate_schema(generate_magic_link_schema, data)
    if errors:
        return error_response("Validation error", errors, 422)

    try:
        links = generate_magic_link(
            exam_id=exam_id,
            creator_id=g.current_user_id,
            student_ids=validated.get("student_ids"),
            valid_hours=validated.get("valid_hours", 24),
        )

        return success_response({"links": links}, f"Generated {len(links)} magic links")
    except ExamServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Generate magic links failed: {e}")
        return error_response("Failed to generate magic links", None, 500)


@exams_bp.route("/magic-link/verify", methods=["POST"])
def verify_magic():
    """Verify magic link and get access."""
    data = request.get_json()
    if not data:
        return error_response("Request body is required", None, 400)

    validated, errors = _validate_schema(magic_link_verify_schema, data)
    if errors:
        return error_response("Validation error", errors, 422)

    try:
        result = verify_magic_link(validated["token"])
        return success_response(result, "Magic link verified")
    except ExamServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Verify magic link failed: {e}")
        return error_response("Failed to verify magic link", None, 500)


@exams_bp.route("/<exam_id>/questions", methods=["GET"])
@require_auth
def get_questions(exam_id: str):
    """Get exam questions for taking the exam."""
    access_token = request.args.get("access_token")

    try:
        questions = get_exam_questions(
            exam_id=exam_id,
            user_id=g.current_user_id,
            access_token=access_token,
        )

        return success_response({"questions": questions})
    except ExamServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Get exam questions failed: {e}")
        return error_response("Failed to get exam questions", None, 500)


@exams_bp.route("/<exam_id>/results", methods=["GET"])
@require_auth
def get_results(exam_id: str):
    """Get results and performance analytics for an exam."""
    data = request.args.to_dict()

    try:
        result = get_exam_results(
            exam_id=exam_id,
            user_id=g.current_user_id,
            user_role=g.current_role,
            filters=data,
        )

        return success_response(result)
    except ExamServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Get exam results failed: {e}")
        return error_response("Failed to get exam results", None, 500)