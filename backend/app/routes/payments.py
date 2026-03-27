"""
Payment routes for ExamSaaS platform.
Blueprint: /api/v1/payments
"""
import logging
from flask import Blueprint, request, jsonify, g

from app.response import success_response, error_response
from app.utils.decorators import require_roles
from app.schemas.payment_schemas import (
    CreateOrderSchema,
    VerifyPaymentSchema,
    PaymentListSchema,
)

payments_bp = Blueprint("payments", __name__)
logger = logging.getLogger(__name__)


@payments_bp.route("/create-order", methods=["POST"])
@require_roles("student_registered", "admin_college")
def create_order():
    """
    Create a Razorpay order.

    Request body:
        amount: int (in rupees, will be converted to paise)
        purpose: str (wallet_topup | subscription | exam_purchase)
        reference_id: str (optional)

    Returns:
        order_id, amount, currency, key_id
    """
    from marshmallow import ValidationError as MarshmallowValidationError
    from app.services.payment_service import (
        create_razorpay_order,
        PaymentServiceError,
    )

    try:
        schema = CreateOrderSchema()
        data = schema.load(request.get_json() or {})
    except MarshmallowValidationError as e:
        return error_response("Validation error", status=422, errors=e.messages)

    amount_rupees = data.get("amount", 0)
    amount_paise = amount_rupees * 100

    try:
        result = create_razorpay_order(
            user_id=str(request.user.id),
            amount_paise=amount_paise,
            purpose=data["purpose"],
            reference_id=data.get("reference_id"),
        )
        return success_response(data=result)
    except PaymentServiceError as e:
        return error_response(str(e), status=400)


@payments_bp.route("/verify", methods=["POST"])
@require_roles("student_registered", "admin_college")
def verify_payment():
    """
    Verify Razorpay payment signature and process.

    Request body:
        razorpay_order_id: str
        razorpay_payment_id: str
        razorpay_signature: str

    Returns:
        Payment status and action result
    """
    from marshmallow import ValidationError as MarshmallowValidationError
    from app.services.payment_service import (
        verify_and_process_payment,
        PaymentServiceError,
    )

    try:
        schema = VerifyPaymentSchema()
        data = schema.load(request.get_json() or {})
    except MarshmallowValidationError as e:
        return error_response("Validation error", status=422, errors=e.messages)

    try:
        result = verify_and_process_payment(
            razorpay_order_id=data["razorpay_order_id"],
            razorpay_payment_id=data["razorpay_payment_id"],
            razorpay_signature=data["razorpay_signature"],
            user_id=str(request.user.id),
        )
        return success_response(data=result)
    except PaymentServiceError as e:
        return error_response(str(e), status=400)


@payments_bp.route("/webhook", methods=["POST"])
def webhook():
    """
    Handle Razorpay webhook.
    NO JWT AUTH — signature verified with HMAC.
    Always returns HTTP 200 to prevent Razorpay retries.
    """
    from app.services.payment_service import handle_webhook

    payload = request.get_data()
    signature = request.headers.get("X-Razorpay-Signature", "")

    logger.info(f"Webhook received, signature present: {bool(signature)}")

    result = handle_webhook(payload, signature)

    return jsonify({"status": result.get("status", "received")}), 200


@payments_bp.route("", methods=["GET"])
@require_roles("student_registered", "admin_college", "super_admin")
def list_payments():
    """
    List payments for the current user (student) or institute (admin).

    Query params:
        page: int (default 1)
        limit: int (default 20)
        status: str (optional)
        purpose: str (optional)

    Returns:
        Paginated list of payments
    """
    from marshmallow import ValidationError as MarshmallowValidationError
    from app.models import Payment, User
    from bson import ObjectId

    try:
        schema = PaymentListSchema()
        params = schema.load(request.args.to_dict())
    except MarshmallowValidationError as e:
        return error_response("Validation error", status=422, errors=e.messages)

    user_id = g.current_user_id
    user_role = g.current_role
    institute_id = g.current_institute_id
    page = params["page"]
    limit = params["limit"]

    query = {}
    if params.get("status"):
        query["status"] = params["status"]
    if params.get("purpose"):
        query["purpose"] = params["purpose"]

    if user_role in ["student_registered", "student_assigned"]:
        query["user"] = user_id
    elif institute_id:
        query["institute"] = ObjectId(institute_id)
    else:
        pass

    total = Payment.objects(**query).count()
    payments = Payment.objects(**query).order_by("-created_at").skip((page - 1) * limit).limit(limit)

    return success_response(
        data={
            "items": [p.to_dict() for p in payments],
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit if total > 0 else 0,
        }
    )


@payments_bp.route("/<payment_id>", methods=["GET"])
@require_roles("student_registered", "admin_college", "super_admin")
def get_payment(payment_id):
    """Get a specific payment by ID."""
    from app.models import Payment
    from bson import ObjectId
    from bson.errors import InvalidId

    try:
        oid = ObjectId(payment_id)
    except InvalidId:
        return error_response("Invalid payment ID", status=400)

    payment = Payment.objects(id=oid).first()
    if not payment:
        return error_response("Payment not found", status=404)

    user_role = g.current_role
    institute_id = g.current_institute_id
    user_id = g.current_user_id
    if user_role in ["student_registered", "student_assigned"]:
        if str(payment.user.id) != str(user_id):
            return error_response("Access denied", status=403)
    elif institute_id:
        if payment.institute and str(payment.institute.id) != str(institute_id):
            return error_response("Access denied", status=403)

    return success_response(data=payment.to_dict())
