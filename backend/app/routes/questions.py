"""
Question routes for ExamSaaS platform.
Blueprint: /api/v1/questions
"""
import logging
from flask import Blueprint, request, g

from app.response import success_response, error_response
from app.schemas.question_schemas import (
    create_question_schema,
    update_question_schema,
    bulk_create_question_schema,
    question_list_schema,
    review_question_schema,
)
from app.services.question_service import (
    create_question,
    get_question,
    update_question,
    delete_question,
    list_questions,
    bulk_create_questions,
    review_question,
    QuestionServiceError,
    QuestionNotFoundError,
)
from app.utils.decorators import require_auth

logger = logging.getLogger(__name__)

questions_bp = Blueprint("questions", __name__, url_prefix="/questions")


def _handle_service_error(error: QuestionServiceError):
    """Handle question service errors."""
    return error_response(error.message, error.status_code)


def _validate_schema(schema, data):
    """Validate request data against schema."""
    try:
        return schema.load(data), None
    except Exception as e:
        errors = e.messages if hasattr(e, "messages") else str(e)
        return None, errors


@questions_bp.route("", methods=["POST"])
@require_auth
def create():
    """Create a new question."""
    data = request.get_json()
    if not data:
        return error_response("Request body is required", 400)
    
    validated, errors = _validate_schema(create_question_schema, data)
    if errors:
        return error_response("Validation error", 422, errors)
    
    try:
        institute_id = getattr(g, "current_institute_id", None)
        
        question = create_question(
            creator_id=g.current_user_id,
            institute_id=institute_id,
            text=validated["text"],
            question_type=validated["question_type"],
            options=validated["options"],
            correct_option_id=validated["correct_option_id"],
            explanation=validated.get("explanation"),
            subject=validated.get("subject"),
            topic=validated.get("topic"),
            difficulty=validated.get("difficulty", "medium"),
            marks=validated.get("marks", 1),
            source=validated.get("source", "manual"),
        )
        
        return success_response(question, "Question created successfully", status=201)
    
    except QuestionServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Create question failed: {e}")
        return error_response("Failed to create question", 500)


@questions_bp.route("/<question_id>", methods=["GET"])
@require_auth
def get(question_id: str):
    """Get question by ID."""
    try:
        question = get_question(question_id, g.current_user_id)
        return success_response(question)
    except QuestionNotFoundError as e:
        return _handle_service_error(e)
    except QuestionServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Get question failed: {e}")
        return error_response("Failed to get question", 500)


@questions_bp.route("/<question_id>", methods=["PATCH"])
@require_auth
def update(question_id: str):
    """Update a question."""
    data = request.get_json()
    if not data:
        return error_response("Request body is required", 400)
    
    validated, errors = _validate_schema(update_question_schema, data)
    if errors:
        return error_response("Validation error", 422, errors)
    
    try:
        question = update_question(
            question_id=question_id,
            user_id=g.current_user_id,
            text=validated.get("text"),
            question_type=validated.get("question_type"),
            options=validated.get("options"),
            correct_option_id=validated.get("correct_option_id"),
            explanation=validated.get("explanation"),
            subject=validated.get("subject"),
            topic=validated.get("topic"),
            difficulty=validated.get("difficulty"),
            marks=validated.get("marks"),
        )
        
        return success_response(question, "Question updated successfully")
    
    except QuestionServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Update question failed: {e}")
        return error_response("Failed to update question", 500)


@questions_bp.route("/<question_id>", methods=["DELETE"])
@require_auth
def delete(question_id: str):
    """Delete a question."""
    try:
        delete_question(question_id, g.current_user_id)
        return success_response(None, "Question deleted successfully")
    except QuestionServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Delete question failed: {e}")
        return error_response("Failed to delete question", 500)


@questions_bp.route("", methods=["GET"])
@require_auth
def list():
    """List questions with pagination."""
    args = request.args.to_dict()
    
    for key in ["is_approved", "is_reviewed"]:
        if key in args:
            args[key] = args[key].lower() == "true"
    
    validated, errors = _validate_schema(question_list_schema, args)
    if errors:
        return error_response("Validation error", 422, errors)
    
    try:
        result = list_questions(
            user_id=g.current_user_id,
            page=validated.get("page", 1),
            per_page=validated.get("per_page", 20),
            institute_id=validated.get("institute_id"),
            subject=validated.get("subject"),
            topic=validated.get("topic"),
            difficulty=validated.get("difficulty"),
            is_approved=validated.get("is_approved"),
            is_reviewed=validated.get("is_reviewed"),
            search=validated.get("search"),
            question_type=validated.get("question_type"),
        )
        
        return success_response(result)
    except QuestionServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"List questions failed: {e}")
        return error_response("Failed to list questions", 500)


@questions_bp.route("/bulk", methods=["POST"])
@require_auth
def bulk_create():
    """Create multiple questions at once."""
    data = request.get_json()
    if not data:
        return error_response("Request body is required", 400)
    
    validated, errors = _validate_schema(bulk_create_question_schema, data)
    if errors:
        return error_response("Validation error", 422, errors)
    
    try:
        institute_id = getattr(g, "current_institute_id", None)
        
        result = bulk_create_questions(
            creator_id=g.current_user_id,
            institute_id=institute_id,
            questions_data=validated["questions"],
        )
        
        return success_response(result, f"Created {result['created']} questions")
    except QuestionServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Bulk create questions failed: {e}")
        return error_response("Failed to create questions", 500)


@questions_bp.route("/<question_id>/review", methods=["POST"])
@require_auth
def review(question_id: str):
    """Review/approve a question."""
    data = request.get_json()
    if not data:
        return error_response("Request body is required", 400)
    
    validated, errors = _validate_schema(review_question_schema, data)
    if errors:
        return error_response("Validation error", 422, errors)
    
    try:
        question = review_question(
            question_id=question_id,
            reviewer_id=g.current_user_id,
            action=validated["action"],
        )
        
        return success_response(question, f"Question {validated['action']}d successfully")
    except QuestionServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Review question failed: {e}")
        return error_response("Failed to review question", 500)
