"""
Institute routes for ExamSaaS platform.
Blueprint: /api/v1/institutes
"""
import logging
from datetime import datetime
from flask import Blueprint, request, g

from app.response import success_response, error_response
from app.utils.decorators import require_roles, audit_log
from app.services.institute_service import (
    create_institute_with_admin,
    get_institute,
    update_institute,
    suspend_institute,
    restore_institute,
    list_institutes,
    generate_impersonation_token,
    get_institute_analytics,
    InstituteServiceError,
    InstituteNotFoundError,
)

logger = logging.getLogger(__name__)

institutes_bp = Blueprint("institutes", __name__, url_prefix="/institutes")


def _handle_service_error(error: InstituteServiceError):
    """Handle institute service errors."""
    return error_response(error.message, error.status_code)


def _validate_schema(schema, data):
    """Validate request data against schema."""
    try:
        return schema.load(data), None
    except Exception as e:
        errors = e.messages if hasattr(e, "messages") else str(e)
        return None, errors


@institutes_bp.route("/create-with-admin", methods=["POST"])
@require_roles("super_admin")
@audit_log(action="create_institute", target_type="Institute")
def create_with_admin():
    """
    Create institute with admin user.
    
    Input:
        - name: Institute name
        - slug: URL-friendly slug
        - city: City name
        - state: State name
        - country: Country name
        - admin: { email, password, first_name, last_name }
    
    Returns:
        201: Institute and admin user data
    """
    data = request.get_json()
    
    if not data:
        return error_response("Request body is required", 400)
    
    required_fields = ["name", "slug", "admin"]
    for field in required_fields:
        if field not in data:
            return error_response(f"Missing required field: {field}", 400)
    
    admin_data = data.get("admin", {})
    admin_required = ["email", "password", "first_name", "last_name"]
    for field in admin_required:
        if field not in admin_data:
            return error_response(f"Missing required admin field: {field}", 400)
    
    try:
        result = create_institute_with_admin({
            "name": data["name"],
            "slug": data["slug"],
            "city": data.get("city"),
            "state": data.get("state"),
            "country": data.get("country", "India"),
            "admin": {
                "email": admin_data["email"],
                "password": admin_data["password"],
                "first_name": admin_data["first_name"],
                "last_name": admin_data.get("last_name", ""),
            },
            "creator_id": g.current_user_id,
        })
        
        return success_response(result, "Institute created successfully", status=201)
    
    except InstituteServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Create institute failed: {e}")
        return error_response("Failed to create institute", 500)


@institutes_bp.route("", methods=["GET"])
@require_roles("super_admin")
def list_institutions():
    """
    List institutes with pagination and filters.
    
    Query params:
        - page: Page number (default: 1)
        - per_page: Items per page (default: 20)
        - city: Filter by city
        - state: Filter by state
        - plan: Filter by plan type
        - is_suspended: Filter by suspension status
        - search: Search by name or slug
    
    Returns:
        200: Paginated list of institutes
    """
    args = request.args.to_dict()
    
    try:
        page = int(args.get("page", 1))
        per_page = int(args.get("per_page", 20))
        
        filters = {}
        if args.get("city"):
            filters["city"] = args["city"]
        if args.get("state"):
            filters["state"] = args["state"]
        if args.get("plan") and args["plan"].strip():
            filters["plan"] = args["plan"].strip()
        if args.get("is_suspended"):
            filters["is_suspended"] = args["is_suspended"].lower() == "true"
        if args.get("search") and args["search"].strip():
            filters["search"] = args["search"].strip()
        
        result = list_institutes(
            filters=filters,
            page=page,
            limit=per_page,
        )
        
        return success_response(result)
    
    except InstituteServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"List institutes failed: {e}")
        return error_response("Failed to list institutes", 500)


@institutes_bp.route("/<institute_id>", methods=["GET"])
@require_roles("super_admin")
def get(institute_id: str):
    """
    Get institute by ID.
    
    Returns:
        200: Institute details
        404: Institute not found
    """
    try:
        institute = get_institute(institute_id)
        return success_response(institute)
    
    except InstituteNotFoundError as e:
        return _handle_service_error(e)
    except InstituteServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Get institute failed: {e}")
        return error_response("Failed to get institute", 500)


@institutes_bp.route("/<institute_id>", methods=["PATCH"])
@require_roles("super_admin")
def update(institute_id: str):
    """
    Update institute details.
    
    Input:
        - name: New institute name
        - city: New city
        - state: New state
        - country: New country
        - plan: Subscription plan
        - is_active: Active status
    
    Returns:
        200: Updated institute
    """
    data = request.get_json()
    
    if not data:
        return error_response("Request body is required", 400)
    
    try:
        institute = update_institute(
            institute_id=institute_id,
            name=data.get("name"),
            city=data.get("city"),
            state=data.get("state"),
            country=data.get("country"),
            plan=data.get("plan"),
            is_active=data.get("is_active"),
        )
        
        return success_response(institute, "Institute updated successfully")
    
    except InstituteNotFoundError as e:
        return _handle_service_error(e)
    except InstituteServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Update institute failed: {e}")
        return error_response("Failed to update institute", 500)


@institutes_bp.route("/<institute_id>/suspend", methods=["POST"])
@require_roles("super_admin")
@audit_log(action="suspend_institute", target_type="Institute")
def suspend(institute_id: str):
    """
    Suspend an institute.
    
    Returns:
        200: Institute suspended successfully
    """
    try:
        institute = suspend_institute(
            institute_id=institute_id,
            suspended_by=g.current_user_id,
        )
        
        return success_response(institute, "Institute suspended successfully")
    
    except InstituteNotFoundError as e:
        return _handle_service_error(e)
    except InstituteServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Suspend institute failed: {e}")
        return error_response("Failed to suspend institute", 500)


@institutes_bp.route("/<institute_id>/restore", methods=["POST"])
@require_roles("super_admin")
@audit_log(action="restore_institute", target_type="Institute")
def restore(institute_id: str):
    """
    Restore a suspended institute.
    
    Returns:
        200: Institute restored successfully
    """
    try:
        institute = restore_institute(
            institute_id=institute_id,
            restored_by=g.current_user_id,
        )
        
        return success_response(institute, "Institute restored successfully")
    
    except InstituteNotFoundError as e:
        return _handle_service_error(e)
    except InstituteServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Restore institute failed: {e}")
        return error_response("Failed to restore institute", 500)


@institutes_bp.route("/<institute_id>/impersonate", methods=["POST"])
@require_roles("super_admin")
@audit_log(action="impersonate_institute", target_type="Institute")
def impersonate(institute_id: str):
    """
    Generate impersonation token for institute admin.
    
    Returns:
        200: { token, expires_in }
    """
    try:
        result = generate_impersonation_token(
            institute_id=institute_id,
            super_admin_id=g.current_user_id,
        )
        
        return success_response(result, "Impersonation token generated")
    
    except InstituteNotFoundError as e:
        return _handle_service_error(e)
    except InstituteServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Impersonate failed: {e}")
        return error_response("Failed to generate impersonation token", 500)


@institutes_bp.route("/<institute_id>/analytics", methods=["GET"])
@require_roles("super_admin", "admin_college")
def analytics(institute_id: str):
    """
    Get institute analytics.
    
    Returns:
        200: { student_count, exam_count, attempts, revenue }
    """
    try:
        analytics_data = get_institute_analytics(
            institute_id=institute_id,
            user_id=g.current_user_id,
        )
        
        return success_response(analytics_data)
    
    except InstituteNotFoundError as e:
        return _handle_service_error(e)
    except InstituteServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Get institute analytics failed: {e}")
        return error_response("Failed to get analytics", 500)