"""
Superadmin analytics routes for ExamSaaS platform.
Blueprint: /api/v1/superadmin
"""
import logging
from flask import Blueprint, request, g

from app.response import success_response, error_response
from app.utils.decorators import require_roles
from app.services.superadmin_service import (
    get_platform_analytics,
    get_audit_logs,
    get_subscriptions,
    get_exams,
    SuperadminServiceError,
)

logger = logging.getLogger(__name__)

superadmin_bp = Blueprint("superadmin", __name__, url_prefix="/superadmin")


def _handle_service_error(error: SuperadminServiceError):
    """Handle superadmin service errors."""
    return error_response(error.message, error.status_code)


@superadmin_bp.route("/analytics/platform", methods=["GET"])
@require_roles("super_admin")
def platform_analytics():
    """
    Get platform-wide analytics for super admin.
    
    Returns:
        200: {
            mau: Monthly active users,
            total_revenue: Total revenue,
            active_institutes: Active institute count,
            daily_exams: 30-day chart data,
            institute_distribution: institutes by plan
        }
    """
    try:
        data = get_platform_analytics()
        
        return success_response(data)
    
    except SuperadminServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Get platform analytics failed: {e}")
        return error_response("Failed to get platform analytics", 500)


@superadmin_bp.route("/audit-logs", methods=["GET"])
@require_roles("super_admin")
def audit_logs():
    """
    Get paginated audit logs with filters.
    
    Query params:
        - page: Page number (default: 1)
        - per_page: Items per page (default: 50)
        - action: Filter by action type
        - actor_id: Filter by user ID
        - institute_id: Filter by institute ID
        - start_date: Filter by date range start (YYYY-MM-DD)
        - end_date: Filter by date range end (YYYY-MM-DD)
    
    Returns:
        200: Paginated audit logs
    """
    args = request.args.to_dict()
    
    try:
        page = int(args.get("page", 1))
        limit = int(args.get("limit", args.get("per_page", 50)))
        
        filters = {}
        if args.get("action"):
            filters["action"] = args["action"]
        if args.get("actor_id"):
            filters["actor_id"] = args["actor_id"]
        if args.get("institute_id"):
            filters["institute_id"] = args["institute_id"]
        if args.get("start_date"):
            filters["start_date"] = args["start_date"]
        if args.get("end_date"):
            filters["end_date"] = args["end_date"]
        
        result = get_audit_logs(
            page=page,
            limit=limit,
            filters=filters,
        )
        
        return success_response(result)
    
    except SuperadminServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Get audit logs failed: {e}")
        return error_response("Failed to get audit logs", 500)


@superadmin_bp.route("/subscriptions", methods=["GET"])
@require_roles("super_admin")
def subscriptions():
    """
    Get paginated subscriptions with filters.
    
    Query params:
        - page: Page number (default: 1)
        - limit: Items per page (default: 20)
        - status: Filter by status (active, expired, etc.)
        - entity_type: Filter by type (institute, student)
        - plan_id: Filter by plan ID
    
    Returns:
        200: Paginated subscriptions
    """
    args = request.args.to_dict()
    
    try:
        page = int(args.get("page", 1))
        limit = int(args.get("limit", 20))
        
        filters = {}
        if args.get("status"):
            filters["status"] = args["status"]
        if args.get("entity_type"):
            filters["entity_type"] = args["entity_type"]
        if args.get("plan_id"):
            filters["plan_id"] = args["plan_id"]
        
        result = get_subscriptions(
            page=page,
            limit=limit,
            filters=filters,
        )
        
        return success_response(result)
    
    except SuperadminServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Get subscriptions failed: {e}")
        return error_response("Failed to get subscriptions", None, 500)


@superadmin_bp.route("/exams", methods=["GET"])
@require_roles("super_admin")
def exams():
    """
    Get paginated exams with filters.
    
    Query params:
        - page: Page number (default: 1)
        - limit: Items per page (default: 20)
        - status: Filter by status (draft, published, active, closed)
        - exam_type: Filter by type (institute, public)
        - search: Search in title
        - institute_id: Filter by institute ID
    
    Returns:
        200: Paginated exams
    """
    args = request.args.to_dict()
    
    try:
        page = int(args.get("page", 1))
        limit = int(args.get("limit", 20))
        
        filters = {}
        if args.get("status"):
            filters["status"] = args["status"]
        if args.get("exam_type"):
            filters["exam_type"] = args["exam_type"]
        if args.get("search"):
            filters["search"] = args["search"]
        if args.get("institute_id"):
            filters["institute_id"] = args["institute_id"]
        
        result = get_exams(
            page=page,
            limit=limit,
            filters=filters,
        )
        
        return success_response(result)
    
    except SuperadminServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Get exams failed: {e}")
        return error_response("Failed to get exams", None, 500)