"""
Wallet routes for ExamSaaS platform.
Blueprint: /api/v1/wallet
"""
import logging
from flask import Blueprint, request

from app.response import success_response, error_response
from app.utils.decorators import require_roles
from app.schemas.payment_schemas import WalletTopupSchema

wallet_bp = Blueprint("wallet", __name__)
logger = logging.getLogger(__name__)


@wallet_bp.route("", methods=["GET"])
@require_roles("student_registered", "admin_college")
def get_wallet():
    """
    Get current user's wallet balance.

    Returns:
        balance_paise, balance_rupees, currency, totals
    """
    from app.services.wallet_service import (
        get_wallet_balance,
        WalletServiceError,
    )

    user_id = str(request.user.id)

    try:
        balance = get_wallet_balance(user_id)
        return success_response(data=balance)
    except WalletServiceError as e:
        return error_response(str(e), status=400)


@wallet_bp.route("/transactions", methods=["GET"])
@require_roles("student_registered", "admin_college")
def list_transactions():
    """
    Get paginated wallet transactions, newest first.

    Query params:
        page: int (default 1)
        per_page: int (default 20, max 50)

    Returns:
        items, total, page, limit, total_pages
    """
    from marshmallow import ValidationError as MarshmallowValidationError
    from app.schemas.wallet_schemas import TransactionListSchema
    from app.services.wallet_service import (
        get_transactions,
        WalletServiceError,
    )

    try:
        schema = TransactionListSchema()
        params = schema.load(request.args.to_dict())
    except MarshmallowValidationError as e:
        return error_response("Validation error", status=422, errors=e.messages)

    user_id = str(request.user.id)

    try:
        result = get_transactions(
            user_id=user_id,
            page=params["page"],
            per_page=params["per_page"],
        )
        return success_response(data=result)
    except WalletServiceError as e:
        return error_response(str(e), status=400)


@wallet_bp.route("/topup", methods=["POST"])
@require_roles("student_registered")
def wallet_topup():
    """
    Initiate wallet top-up via Razorpay.

    Request body:
        amount_rupees: int (minimum ₹50, maximum ₹50,000)
        OR amount_rupees in [50, 100, 200, 500, 1000, 2000] for preset amounts

    Returns:
        order_id, amount, currency, key_id, payment_id
    """
    from marshmallow import ValidationError as MarshmallowValidationError
    from app.services.payment_service import (
        create_razorpay_order,
        PaymentServiceError,
    )

    try:
        schema = WalletTopupSchema()
        data = schema.load(request.get_json() or {})
    except MarshmallowValidationError as e:
        return error_response("Validation error", status=422, errors=e.messages)

    amount_rupees = data["amount_rupees"]
    amount_paise = amount_rupees

    user_id = str(request.user.id)

    try:
        result = create_razorpay_order(
            user_id=user_id,
            amount_paise=amount_paise,
            purpose="wallet_topup",
            reference_id=None,
        )
        return success_response(data=result)
    except PaymentServiceError as e:
        return error_response(str(e), status=400)
