"""
AI routes for ExamSaaS platform.
Blueprint: /api/v1/ai
"""
import logging
from flask import Blueprint, request, g

from app.response import success_response, error_response
from app.utils.decorators import require_auth, require_roles
from app.services.ai_service import (
    generate_questions,
    get_task_status,
    analyze_exam,
    get_recommendations,
    AIServiceError,
)

logger = logging.getLogger(__name__)

ai_bp = Blueprint("ai", __name__, url_prefix="/ai")


def _handle_service_error(error: AIServiceError):
    """Handle AI service errors."""
    return error_response(error.message, error.status_code)


def _validate_schema(schema, data):
    """Validate request data against schema."""
    try:
        return schema.load(data), None
    except Exception as e:
        errors = e.messages if hasattr(e, "messages") else str(e)
        return None, errors


@ai_bp.route("/generate-questions", methods=["POST"])
@require_roles("admin_public", "admin_college", "teacher")
def generate_questions_route():
    """
    Generate questions using AI.
    
    Input:
        - topic: Topic for questions
        - difficulty: easy, medium, hard (default: medium)
        - count: Number of questions (default: 5, max: 20)
        - subject: Subject (optional)
    
    Returns:
        202: { task_id, status: "queued" }
    """
    data = request.get_json()
    
    if not data:
        return error_response("Request body is required", 400)
    
    if "topic" not in data:
        return error_response("topic is required", 400)
    
    topic = data["topic"]
    difficulty = data.get("difficulty", "medium")
    count = min(int(data.get("count", 5)), 20)
    subject = data.get("subject")
    
    valid_difficulties = ["easy", "medium", "hard"]
    if difficulty not in valid_difficulties:
        return error_response(f"Invalid difficulty. Must be one of: {valid_difficulties}", 400)
    
    try:
        institute_id = getattr(g, "current_institute_id", None)
        
        result = generate_questions(
            creator_id=g.current_user_id,
            institute_id=institute_id,
            topic=topic,
            difficulty=difficulty,
            count=count,
            subject=subject,
        )
        
        return success_response(result, "Question generation started", status=202)
    
    except AIServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Generate questions failed: {e}")
        return error_response("Failed to start question generation", 500)


@ai_bp.route("/generate-questions/<task_id>/status", methods=["GET"])
@require_auth
def get_generation_status(task_id: str):
    """
    Check question generation task status from Redis.
    
    Returns:
        200: { status, result or error }
    """
    try:
        result = get_task_status(task_id=task_id)
        
        return success_response(result)
    
    except AIServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Get task status failed: {e}")
        return error_response("Failed to get task status", 500)


@ai_bp.route("/analyze-exam/<exam_id>", methods=["POST"])
@require_roles("admin_public", "admin_college", "teacher")
def analyze_exam_route(exam_id: str):
    """
    Analyze exam quality using AI.
    
    Input:
        - analysis_type: quality, improvements, suggestions (default: quality)
    
    Returns:
        202: { task_id, status: "queued" }
    """
    data = request.get_json() or {}
    
    analysis_type = data.get("analysis_type", "quality")
    valid_types = ["quality", "improvements", "suggestions"]
    if analysis_type not in valid_types:
        analysis_type = "quality"
    
    try:
        result = analyze_exam(
            exam_id=exam_id,
            user_id=g.current_user_id,
            analysis_type=analysis_type,
        )
        
        return success_response(result, "Exam analysis started", status=202)
    
    except AIServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Analyze exam failed: {e}")
        return error_response("Failed to start exam analysis", 500)


@ai_bp.route("/recommendations/<result_id>", methods=["GET"])
@require_auth
def recommendations(result_id: str):
    """
    Get AI recommendations for a result.
    Polls until analysis is complete.
    
    Query params:
        - wait: seconds to wait for completion (default: 30, max: 60)
    
    Returns:
        200: { recommendations, status }
    """
    args = request.args.to_dict()
    
    wait_time = min(int(args.get("wait", 30)), 60)
    
    try:
        result = get_recommendations(
            result_id=result_id,
            user_id=g.current_user_id,
            wait_time=wait_time,
        )
        
        return success_response(result)
    
    except AIServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Get recommendations failed: {e}")
        return error_response("Failed to get recommendations", 500)