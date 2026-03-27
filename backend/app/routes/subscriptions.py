"""
Subscription routes for ExamSaaS platform.
Blueprint: /api/v1/subscriptions
"""
import logging
from flask import Blueprint, request, g

from app.response import success_response, error_response
from app.utils.decorators import require_roles

subscriptions_bp = Blueprint("subscriptions", __name__)
logger = logging.getLogger(__name__)


@subscriptions_bp.route("/my", methods=["GET"])
@require_roles("admin_college", "admin_public")
def get_my_subscription():
    """
    Get the current institute's active subscription.

    Returns:
        Subscription details including plan info
    """
    user = request.user
    institute = getattr(user, "institute", None)

    if not institute:
        return error_response("No institute associated with your account", status=400)

    from app.services.subscription_service import get_active_subscription
    from app.models import Plan

    sub = get_active_subscription(str(institute.id), entity_type="institute")

    if not sub:
        return success_response(
            data={
                "status": "none",
                "message": "No active subscription found",
            }
        )

    plan = sub.plan
    result = sub.to_dict()
    if plan:
        result["plan"] = plan.to_dict()

    return success_response(data=result)


@subscriptions_bp.route("/student/my", methods=["GET"])
@require_roles("student_registered", "student_assigned")
def get_student_subscription():
    """
    Get the current student's active subscription.

    Returns:
        Subscription details including plan info
    """
    from app.services.subscription_service import get_active_subscription

    user_id = g.current_user_id
    sub = get_active_subscription(user_id, entity_type="student")

    if not sub:
        return success_response(
            data={
                "status": "none",
                "message": "No active subscription found",
            }
        )

    plan = sub.plan
    result = sub.to_dict()
    if plan:
        result["plan"] = plan.to_dict()

    return success_response(data=result)


@subscriptions_bp.route("/student/plans", methods=["GET"])
def list_student_plans():
    """
    List available plans for students (PUBLIC).

    Query params:
        page: int (default 1)
        limit: int (default 20)

    Returns:
        Paginated list of student plans
    """
    from app.models import Plan

    page = request.args.get("page", 1, type=int)
    limit = min(request.args.get("limit", 20, type=int), 100)

    query = {"is_for": "student", "is_active": True}

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


@subscriptions_bp.route("/student/subscribe", methods=["POST"])
@require_roles("student_registered", "student_assigned")
def student_subscribe_to_plan():
    """
    Student subscribes to a plan using wallet or razorpay.

    Request body:
        plan_id: str (Plan document ID)
        payment_method: str (razorpay | wallet)

    Returns:
        Payment order details or wallet debit confirmation
    """
    from app.services.subscription_service import get_active_subscription, activate_subscription
    from app.services.wallet_service import debit_wallet, get_wallet_balance, WalletServiceError
    from app.services.payment_service import create_razorpay_order, PaymentServiceError
    from app.models import Plan
    from bson import ObjectId
    from bson.errors import InvalidId

    user_id = g.current_user_id
    data = request.get_json() or {}
    plan_id = data.get("plan_id")
    payment_method = data.get("payment_method", "wallet")

    if not plan_id:
        return error_response("plan_id is required", status=400)

    try:
        plan_oid = ObjectId(plan_id)
    except InvalidId:
        return error_response("Invalid plan_id", status=400)

    plan = Plan.objects(id=plan_oid, is_for="student", is_active=True).first()
    if not plan:
        return error_response("Student plan not found", status=404)

    existing_sub = get_active_subscription(user_id, entity_type="student")
    if existing_sub:
        return error_response("You already have an active subscription", status=400)

    if payment_method == "wallet":
        try:
            debit_wallet(
                user_id=user_id,
                amount_paise=int(plan.price),
                purpose="subscription",
                source="system",
                reference_id=str(plan.id),
                description=f"Subscription to {plan.name} plan",
            )

            sub = activate_subscription(
                entity_id=user_id,
                plan_id=str(plan.id),
                payment_id=None,
                entity_type="student",
            )

            return success_response(
                data={
                    "action": "wallet",
                    "subscription_id": str(sub.id),
                    "subscription_active": True,
                    "wallet_debited": int(plan.price),
                    "balance": get_wallet_balance(user_id),
                }
            )
        except WalletServiceError as e:
            return error_response(str(e), status=422)

    else:
        try:
            result = create_razorpay_order(
                user_id=user_id,
                amount_paise=int(plan.price),
                purpose="subscription",
                reference_id=str(plan.id),
            )

            result["metadata"] = {
                "plan_id": str(plan.id),
                "entity_id": user_id,
                "entity_type": "student",
                "plan_name": plan.name,
            }

            return success_response(data=result)
        except PaymentServiceError as e:
            return error_response(str(e), status=400)


@subscriptions_bp.route("/subscribe", methods=["POST"])
@require_roles("admin_college", "admin_public")
def subscribe_to_plan():
    """
    Create a payment order for a plan subscription.

    Request body:
        plan_id: str (Plan document ID)
        payment_method: str (razorpay | wallet)

    Returns:
        Payment order details or wallet debit confirmation
    """
    from app.models import Institute
    from app.services.subscription_service import get_active_subscription
    from app.services.payment_service import create_razorpay_order, PaymentServiceError
    from bson import ObjectId
    from bson.errors import InvalidId

    user = request.user
    institute = getattr(user, "institute", None)

    if not institute:
        return error_response("No institute associated with your account", status=400)

    data = request.get_json() or {}
    plan_id = data.get("plan_id")
    payment_method = data.get("payment_method", "razorpay")

    if not plan_id:
        return error_response("plan_id is required", status=400)

    try:
        plan_oid = ObjectId(plan_id)
    except InvalidId:
        return error_response("Invalid plan_id", status=400)

    from app.models import Plan
    plan = Plan.objects(id=plan_oid).first()
    if not plan:
        return error_response("Plan not found", status=404)

    if not plan.is_active:
        return error_response("This plan is no longer available", status=400)

    if payment_method == "wallet":
        from app.services.wallet_service import (
            debit_wallet,
            get_wallet_balance,
            WalletServiceError,
        )

        try:
            debit_wallet(
                user_id=str(user.id),
                amount_paise=int(plan.price),
                purpose="subscription",
                source="system",
                reference_id=str(plan.id),
                description=f"Subscription to {plan.name} plan",
            )

            from app.services.subscription_service import activate_subscription
            sub = activate_subscription(
                entity_id=str(institute.id),
                plan_id=str(plan.id),
                payment_id=None,
                entity_type="institute",
            )

            return success_response(
                data={
                    "action": "wallet",
                    "subscription_id": str(sub.id),
                    "subscription_active": True,
                    "wallet_debited": int(plan.price),
                    "balance": get_wallet_balance(str(user.id)),
                }
            )
        except WalletServiceError as e:
            return error_response(str(e), status=422)

    else:
        try:
            result = create_razorpay_order(
                user_id=str(user.id),
                amount_paise=int(plan.price),
                purpose="subscription",
                reference_id=str(plan.id),
            )

            result["metadata"] = {
                "plan_id": str(plan.id),
                "entity_id": str(institute.id),
                "entity_type": "institute",
                "plan_name": plan.name,
            }

            return success_response(data=result)
        except PaymentServiceError as e:
            return error_response(str(e), status=400)


@subscriptions_bp.route("/cancel", methods=["POST"])
@require_roles("admin_college", "admin_public")
def cancel_subscription():
    """
    Cancel the current institute's subscription.
    """
    from app.services.subscription_service import cancel_subscription

    user = request.user
    institute = getattr(user, "institute", None)

    if not institute:
        return error_response("No institute associated with your account", status=400)

    cancel_subscription(str(institute.id), entity_type="institute")

    return success_response(data={"message": "Subscription cancelled successfully"})


@subscriptions_bp.route("/check-feature", methods=["GET"])
@require_roles("admin_college", "admin_public")
def check_feature():
    """
    Check if a feature is accessible under current subscription.

    Query params:
        feature: str (feature flag name)

    Returns:
        { allowed: bool, message?: str }
    """
    from app.services.subscription_service import check_feature_access
    from app.exceptions import SubscriptionRequiredError, FeatureNotAvailableError

    feature = request.args.get("feature")
    if not feature:
        return error_response("feature query parameter is required", status=400)

    user = request.user
    institute = getattr(user, "institute", None)

    if not institute:
        return error_response("No institute associated", status=400)

    try:
        check_feature_access(str(institute.id), feature)
        return success_response(data={"allowed": True})
    except SubscriptionRequiredError as e:
        return success_response(data={"allowed": False, "reason": "subscription_required", "message": e.message})
    except FeatureNotAvailableError as e:
        return success_response(data={"allowed": False, "reason": "feature_not_available", "message": e.message})
