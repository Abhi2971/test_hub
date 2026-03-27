"""
User management routes for ExamSaaS platform.
Admin endpoints for user management.
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.response import success_response, error_response
from app.utils.decorators import require_roles

users_bp = Blueprint("users", __name__)


@users_bp.route("", methods=["GET"])
@jwt_required()
@require_roles("admin_college", "admin_public", "super_admin")
def list_users():
    """
    List users for the current institute.
    
    Query params:
        page: int (default 1)
        limit: int (default 20)
        role: str (optional filter)
        is_active: bool (optional filter)
    
    Returns:
        Paginated list of users
    """
    from app.models import User
    
    page = request.args.get("page", 1, type=int)
    limit = min(request.args.get("limit", 20, type=int), 100)
    role = request.args.get("role")
    is_active = request.args.get("is_active")
    
    query = {}
    if role:
        query["role"] = role
    if is_active is not None:
        query["is_active"] = is_active.lower() == "true"
    
    total = User.objects(**query).count()
    users = User.objects(**query).skip((page - 1) * limit).limit(limit)
    
    return success_response(
        data={
            "items": [u.to_dict() for u in users],
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit if total > 0 else 0,
        }
    )


@users_bp.route("/<user_id>", methods=["GET"])
@jwt_required()
@require_roles("admin_college", "admin_public", "super_admin")
def get_user(user_id):
    """Get a specific user by ID."""
    from app.models import User
    from bson import ObjectId
    from bson.errors import InvalidId
    
    try:
        oid = ObjectId(user_id)
    except InvalidId:
        return error_response("Invalid user ID", status=400)
    
    user = User.objects(id=oid).first()
    if not user:
        return error_response("User not found", status=404)
    
    return success_response(data=user.to_dict())


@users_bp.route("/<user_id>/toggle-active", methods=["PUT"])
@jwt_required()
@require_roles("admin_college", "admin_public", "super_admin")
def toggle_user_active(user_id):
    """Toggle user active status."""
    from app.models import User
    from bson import ObjectId
    from bson.errors import InvalidId
    
    try:
        oid = ObjectId(user_id)
    except InvalidId:
        return error_response("Invalid user ID", status=400)
    
    user = User.objects(id=oid).first()
    if not user:
        return error_response("User not found", status=404)
    
    data = request.get_json() or {}
    is_active = data.get("is_active", not user.is_active)
    user.is_active = is_active
    user.save()
    
    return success_response(data={"id": str(user.id), "is_active": user.is_active})


@users_bp.route("/students", methods=["GET"])
@jwt_required()
@require_roles("admin_college", "admin_public", "teacher", "super_admin")
def list_students():
    """
    List students for the current institute.
    
    Returns:
        List of students
    """
    from app.models import User
    
    students = User.objects(role__in=["student_registered", "student_assigned"], is_active=True)
    return success_response(data={"items": [s.to_dict() for s in students]})
