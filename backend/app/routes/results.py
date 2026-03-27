"""
Result routes for ExamSaaS platform.
Blueprint: /api/v1/results
"""
import logging
from flask import Blueprint, request, g

from app.response import success_response, error_response
from app.services.result_service import (
    calculate_result,
    compute_rank,
    publish_result,
    publish_all_results,
    get_result,
    get_student_result,
    list_results,
    get_exam_analytics,
    ResultServiceError,
    ResultNotFoundError,
)
from app.utils.decorators import require_auth

logger = logging.getLogger(__name__)

results_bp = Blueprint("results", __name__, url_prefix="/results")


def _handle_service_error(error: ResultServiceError):
    """Handle result service errors."""
    return error_response(error.message, error.status_code)


@results_bp.route("/<result_id>", methods=["GET"])
@require_auth
def get(result_id: str):
    """Get result by ID."""
    try:
        result = get_result(result_id, g.current_user_id)
        return success_response(result)
    except ResultNotFoundError as e:
        return _handle_service_error(e)
    except ResultServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Get result failed: {e}")
        return error_response("Failed to get result", 500)


@results_bp.route("/exam/<exam_id>/student/<student_id>", methods=["GET"])
@require_auth
def get_by_exam_student(exam_id: str, student_id: str):
    """Get student's result for an exam."""
    try:
        result = get_student_result(exam_id, student_id)
        return success_response(result)
    except ResultNotFoundError as e:
        return _handle_service_error(e)
    except ResultServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Get student result failed: {e}")
        return error_response("Failed to get result", 500)


@results_bp.route("/<result_id>/publish", methods=["POST"])
@require_auth
def publish_single(result_id: str):
    """Publish a result."""
    try:
        result = publish_result(result_id, g.current_user_id)
        return success_response(result, "Result published successfully")
    except ResultServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Publish result failed: {e}")
        return error_response("Failed to publish result", 500)


@results_bp.route("/exam/<exam_id>/publish-all", methods=["POST"])
@require_auth
def publish_all(exam_id: str):
    """Publish all results for an exam."""
    try:
        result = publish_all_results(exam_id, g.current_user_id)
        return success_response(result, f"Published {result['published_count']} results")
    except ResultServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Publish all results failed: {e}")
        return error_response("Failed to publish results", 500)


@results_bp.route("/exam/<exam_id>/ranks", methods=["GET"])
@require_auth
def ranks(exam_id: str):
    """Compute and get ranks for an exam."""
    try:
        ranked = compute_rank(exam_id)
        return success_response({"rankings": ranked})
    except ResultServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Compute ranks failed: {e}")
        return error_response("Failed to compute ranks", 500)


@results_bp.route("/exam/<exam_id>/analytics", methods=["GET"])
@require_auth
def analytics(exam_id: str):
    """Get analytics for an exam."""
    try:
        analytics_data = get_exam_analytics(exam_id, g.current_user_id)
        return success_response(analytics_data)
    except ResultServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Get analytics failed: {e}")
        return error_response("Failed to get analytics", 500)


@results_bp.route("", methods=["GET"])
@require_auth
def list():
    """List results with pagination."""
    exam_id = request.args.get("exam_id")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    include_unpublished = request.args.get("include_unpublished", "false").lower() == "true"
    
    try:
        result = list_results(
            user_id=g.current_user_id,
            exam_id=exam_id,
            page=page,
            per_page=per_page,
            include_unpublished=include_unpublished,
        )
        
        return success_response(result)
    except ResultServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"List results failed: {e}")
        return error_response("Failed to list results", 500)
