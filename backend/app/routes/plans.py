"""
Plan routes for ExamSaaS platform.
Blueprint: /api/v1/plans

GET endpoints are PUBLIC (anyone can view plans).
POST/PATCH/DELETE require super_admin role.
"""
import logging
from flask import Blueprint, request, jsonify, g

from app.response import success_response, error_response
from app.utils.decorators import require_roles

plans_bp = Blueprint("plans", __name__)
logger = logging.getLogger(__name__)


@plans_bp.route("", methods=["GET"])
def list_plans():
    """
    List all active plans (PUBLIC).

    Query params:
        page: int (default 1)
        limit: int (default 20)
        is_for: str (student | institute)
        is_active: bool

    Returns:
        Paginated list of plans
    """
    from marshmallow import ValidationError as MarshmallowValidationError
    from app.models import Plan
    from app.schemas.plan_schemas import PlanListSchema

    try:
        schema = PlanListSchema()
        params = schema.load(request.args.to_dict())
    except MarshmallowValidationError as e:
        return error_response("Validation error", status=422, errors=e.messages)

    query = {}
    if params.get("is_for") and params["is_for"] != "all":
        query["is_for"] = params["is_for"]
    if params.get("is_active") is not None:
        query["is_active"] = params["is_active"]
    elif params.get("is_for") == "all":
        pass
    else:
        query["is_active"] = True

    page = params["page"]
    limit = params["limit"]

    total = Plan.objects(**query).count()
    plans = Plan.objects(**query).order_by("price").skip((page - 1) * limit).limit(limit)

    return success_response(
        data={
            "items": [p.to_dict() for p in plans],
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit if total > 0 else 0,
        }
    )


@plans_bp.route("/<plan_id>", methods=["GET"])
def get_plan(plan_id):
    """Get a specific plan by ID (PUBLIC)."""
    from app.models import Plan
    from bson import ObjectId
    from bson.errors import InvalidId

    try:
        oid = ObjectId(plan_id)
    except InvalidId:
        return error_response("Invalid plan ID", status=400)

    plan = Plan.objects(id=oid).first()
    if not plan:
        return error_response("Plan not found", status=404)

    return success_response(data=plan.to_dict())


@plans_bp.route("", methods=["POST"])
@require_roles("super_admin")
def create_plan():
    """
    Create a new subscription plan.

    Request body:
        name, slug, price, duration_days, max_students, max_teachers,
        exam_limit, ai_usage_limit, feature_flags, is_for
    """
    from marshmallow import ValidationError as MarshmallowValidationError
    from app.models import Plan, FeatureFlags
    from app.schemas.plan_schemas import PlanCreateSchema
    import re

    try:
        schema = PlanCreateSchema()
        data = schema.load(request.get_json() or {})
    except MarshmallowValidationError as e:
        return error_response("Validation error", status=422, errors=e.messages)

    slug = data.get("slug") or re.sub(r'[^a-z0-9]+', '-', data["name"].lower()).strip('-')
    counter = 1
    base_slug = slug
    while Plan.objects(slug=slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1

    flags_data = data.get("feature_flags", {})
    feature_flags = FeatureFlags(**flags_data)

    plan = Plan(
        name=data["name"],
        slug=slug,
        price=data["price"],
        duration_days=data["duration_days"],
        max_students=data.get("max_students", 0),
        max_teachers=data.get("max_teachers", 0),
        exam_limit=data.get("exam_limit", 0),
        ai_usage_limit=data.get("ai_usage_limit", 0),
        feature_flags=feature_flags,
        is_for=data["is_for"],
        is_active=True,
        created_by=g.current_user_id,
    )
    plan.save()

    logger.info(f"Plan created: {plan.name} (id={plan.id}) by user {g.current_user_id}")

    return success_response(data=plan.to_dict(), status=201)


@plans_bp.route("/<plan_id>", methods=["PATCH"])
@require_roles("super_admin")
def update_plan(plan_id):
    """Update a plan."""
    from marshmallow import ValidationError as MarshmallowValidationError
    from app.models import Plan, FeatureFlags
    from app.schemas.plan_schemas import PlanUpdateSchema
    from bson import ObjectId
    from bson.errors import InvalidId

    try:
        oid = ObjectId(plan_id)
    except InvalidId:
        return error_response("Invalid plan ID", status=400)

    plan = Plan.objects(id=oid).first()
    if not plan:
        return error_response("Plan not found", status=404)

    try:
        schema = PlanUpdateSchema()
        data = schema.load(request.get_json() or {})
    except MarshmallowValidationError as e:
        return error_response("Validation error", status=422, errors=e.messages)

    for field, value in data.items():
        if field == "feature_flags":
            flags = FeatureFlags(**value)
            plan.feature_flags = flags
        else:
            setattr(plan, field, value)

    plan.save()

    logger.info(f"Plan updated: {plan.name} (id={plan.id}) by user {g.current_user_id}")

    return success_response(data=plan.to_dict())


@plans_bp.route("/<plan_id>", methods=["DELETE"])
@require_roles("super_admin")
def delete_plan(plan_id):
    """
    Soft-delete a plan (sets is_active=False).
    """
    from app.models import Plan
    from bson import ObjectId
    from bson.errors import InvalidId

    try:
        oid = ObjectId(plan_id)
    except InvalidId:
        return error_response("Invalid plan ID", status=400)

    plan = Plan.objects(id=oid).first()
    if not plan:
        return error_response("Plan not found", status=404)

    plan.is_active = False
    plan.save()

    logger.info(f"Plan soft-deleted: {plan.name} (id={plan.id}) by user {g.current_user_id}")

    return success_response(data={"id": str(plan.id), "deleted": True})
