"""
Analytics routes for ExamSaaS platform.
Blueprint: /api/v1/admin
"""
import logging
from flask import Blueprint, request, g

from app.response import success_response, error_response
from app.utils.decorators import require_roles
from app.services.analytics_service import (
    get_overview_analytics,
    get_exam_analytics,
    get_student_analytics,
    get_revenue_analytics,
    AnalyticsServiceError,
)

logger = logging.getLogger(__name__)

analytics_bp = Blueprint("analytics", __name__, url_prefix="/admin")


def _handle_service_error(error: AnalyticsServiceError):
    """Handle analytics service errors."""
    return error_response(error.message, error.status_code)


@analytics_bp.route("/analytics/overview", methods=["GET"])
@require_roles("admin_college", "teacher")
def overview():
    """
    Get overview analytics for the institute.
    
    Returns:
        200: { total_exams, total_students, total_attempts, avg_pass_rate }
    """
    try:
        institute_id = getattr(g, "current_institute_id", None)
        
        if not institute_id:
            return error_response("Institute context required", 400)
        
        data = get_overview_analytics(
            institute_id=institute_id,
            user_id=g.current_user_id,
            user_role=g.current_role,
        )
        
        return success_response(data)
    
    except AnalyticsServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Get overview analytics failed: {e}")
        return error_response("Failed to get analytics", 500)


@analytics_bp.route("/analytics/exams", methods=["GET"])
@require_roles("admin_college", "teacher")
def exam_analytics():
    """
    Get per-exam analytics, grouped by month.
    
    Query params:
        - start_date: Start date (YYYY-MM-DD)
        - end_date: End date (YYYY-MM-DD)
        - page: Page number (default: 1)
        - per_page: Items per page (default: 20)
    
    Returns:
        200: Per-exam stats with monthly grouping
    """
    args = request.args.to_dict()
    
    try:
        institute_id = getattr(g, "current_institute_id", None)
        
        if not institute_id:
            return error_response("Institute context required", 400)
        
        page = int(args.get("page", 1))
        per_page = int(args.get("per_page", 20))
        
        data = get_exam_analytics(
            institute_id=institute_id,
            user_id=g.current_user_id,
            user_role=g.current_role,
            start_date=args.get("start_date"),
            end_date=args.get("end_date"),
            page=page,
            per_page=per_page,
        )
        
        return success_response(data)
    
    except AnalyticsServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Get exam analytics failed: {e}")
        return error_response("Failed to get exam analytics", 500)


@analytics_bp.route("/analytics/students", methods=["GET"])
@require_roles("admin_college", "teacher")
def student_analytics():
    """
    Get student analytics - growth trend and active students.
    
    Query params:
        - start_date: Start date (YYYY-MM-DD)
        - end_date: End date (YYYY-MM-DD)
        - period: daily, weekly, monthly (default: daily)
    
    Returns:
        200: Student growth trend and active count
    """
    args = request.args.to_dict()
    
    try:
        institute_id = getattr(g, "current_institute_id", None)
        
        if not institute_id:
            return error_response("Institute context required", 400)
        
        data = get_student_analytics(
            institute_id=institute_id,
            user_id=g.current_user_id,
            user_role=g.current_role,
            start_date=args.get("start_date"),
            end_date=args.get("end_date"),
            period=args.get("period", "daily"),
        )
        
        return success_response(data)
    
    except AnalyticsServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Get student analytics failed: {e}")
        return error_response("Failed to get student analytics", 500)


@analytics_bp.route("/analytics/revenue", methods=["GET"])
@require_roles("admin_college")
def revenue_analytics():
    """
    Get revenue analytics - wallet transactions and subscription costs.
    
    Query params:
        - start_date: Start date (YYYY-MM-DD)
        - end_date: End date (YYYY-MM-DD)
        - page: Page number (default: 1)
        - per_page: Items per page (default: 20)
    
    Returns:
        200: Revenue data with transactions
    """
    args = request.args.to_dict()
    
    try:
        institute_id = getattr(g, "current_institute_id", None)
        
        if not institute_id:
            return error_response("Institute context required", 400)
        
        page = int(args.get("page", 1))
        per_page = int(args.get("per_page", 20))
        
        data = get_revenue_analytics(
            institute_id=institute_id,
            user_id=g.current_user_id,
            user_role=g.current_role,
            start_date=args.get("start_date"),
            end_date=args.get("end_date"),
            page=page,
            per_page=per_page,
        )
        
        return success_response(data)
    
    except AnalyticsServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Get revenue analytics failed: {e}")
        return error_response("Failed to get revenue analytics", 500)