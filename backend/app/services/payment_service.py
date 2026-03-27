"""
Payment service for ExamSaaS platform.
Razorpay integration for payments, webhooks, and order management.
"""
import hashlib
import hmac
import json
import logging
import time
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def _get_config() -> Dict[str, Any]:
    """Get Razorpay configuration from Flask app."""
    try:
        from flask import current_app
        return {
            "razorpay_key_id": current_app.config.get("RAZORPAY_KEY_ID", ""),
            "razorpay_key_secret": current_app.config.get("RAZORPAY_KEY_SECRET", ""),
            "razorpay_webhook_secret": current_app.config.get("RAZORPAY_WEBHOOK_SECRET", ""),
        }
    except RuntimeError:
        return {
            "razorpay_key_id": "",
            "razorpay_key_secret": "",
            "razorpay_webhook_secret": "",
        }


def _get_razorpay_client():
    """Get configured Razorpay client."""
    import razorpay
    config = _get_config()
    if not config["razorpay_key_id"] or not config["razorpay_key_secret"]:
        raise RuntimeError("Razorpay not configured")
    return razorpay.Client(
        auth=(config["razorpay_key_id"], config["razorpay_key_secret"])
    )


ALLOWED_PURPOSES = {"wallet_topup", "subscription", "exam_purchase"}
MIN_AMOUNT_PAISE = 100


class PaymentServiceError(Exception):
    """Base exception for payment service errors."""
    pass


def create_razorpay_order(
    user_id: str,
    amount_paise: int,
    purpose: str,
    reference_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a Razorpay order and Payment record.

    Args:
        user_id: User document ID
        amount_paise: Amount in paise (must be >= 100)
        purpose: Payment purpose (wallet_topup | subscription | exam_purchase)
        reference_id: Optional reference (e.g. exam_id, plan_id)

    Returns:
        dict with order_id, amount, currency, key_id

    Raises:
        PaymentServiceError: If validation fails or Razorpay API error
    """
    if amount_paise < MIN_AMOUNT_PAISE:
        raise PaymentServiceError(
            f"Minimum amount is {MIN_AMOUNT_PAISE} paise (₹{MIN_AMOUNT_PAISE / 100:.2f})"
        )

    if purpose not in ALLOWED_PURPOSES:
        raise PaymentServiceError(f"Invalid purpose. Allowed: {ALLOWED_PURPOSES}")

    config = _get_config()
    if not config["razorpay_key_id"] or not config["razorpay_key_secret"]:
        raise PaymentServiceError("Razorpay is not configured on this server")

    from app.models import Payment, User
    from bson import ObjectId

    try:
        user_oid = ObjectId(user_id)
    except Exception:
        raise PaymentServiceError(f"Invalid user_id: {user_id}")

    user = User.objects(id=user_oid).first()
    if not user:
        raise PaymentServiceError("User not found")

    receipt = f"rcpt_{user_id[:8]}_{int(time.time())}"

    try:
        client = _get_razorpay_client()
        rz_order = client.order.create({
            "amount": amount_paise,
            "currency": "INR",
            "receipt": receipt,
            "notes": {
                "purpose": purpose,
                "user_id": str(user_id),
                "reference_id": str(reference_id) if reference_id else "",
            },
        })
    except Exception as e:
        logger.error(f"Razorpay order creation failed: {e}")
        raise PaymentServiceError(f"Payment order creation failed: {str(e)}")

    metadata = {"purpose": purpose}
    if reference_id:
        metadata["reference_id"] = str(reference_id)

    payment = Payment(
        user=user,
        razorpay_order_id=rz_order["id"],
        amount=amount_paise,
        currency="INR",
        status="pending",
        purpose=purpose,
        metadata=metadata,
    )
    payment.save()

    logger.info(
        f"Created Razorpay order {rz_order['id']} for user {user_id}: "
        f"{amount_paise} paise, purpose={purpose}"
    )

    return {
        "order_id": rz_order["id"],
        "amount": amount_paise,
        "currency": "INR",
        "key_id": config["razorpay_key_id"],
        "payment_id": str(payment.id),
    }


def verify_and_process_payment(
    razorpay_order_id: str,
    razorpay_payment_id: str,
    razorpay_signature: str,
    user_id: str,
) -> Dict[str, Any]:
    """
    Verify HMAC signature, update Payment, execute business action.

    Idempotent: if payment already captured, returns immediately.

    Args:
        razorpay_order_id: Razorpay order ID
        razorpay_payment_id: Razorpay payment ID
        razorpay_signature: HMAC signature from client
        user_id: User document ID (for validation)

    Returns:
        dict with business action result

    Raises:
        PaymentServiceError: If signature invalid or processing fails
    """
    config = _get_config()

    payload = f"{razorpay_order_id}|{razorpay_payment_id}"
    expected = hmac.new(
        config["razorpay_key_secret"].encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected, razorpay_signature):
        logger.warning(
            f"Payment signature mismatch for order {razorpay_order_id}, "
            f"payment {razorpay_payment_id}"
        )
        raise PaymentServiceError("Payment signature verification failed")

    from app.models import Payment
    from bson import ObjectId

    payment = Payment.objects(razorpay_order_id=razorpay_order_id).first()
    if not payment:
        raise PaymentServiceError("Payment record not found")

    if payment.status == "captured":
        logger.info(f"Payment {razorpay_payment_id} already captured, returning idempotently")
        return {
            "already_processed": True,
            "payment_id": str(payment.id),
            "status": "captured",
        }

    payment.razorpay_payment_id = razorpay_payment_id
    payment.razorpay_signature = razorpay_signature
    payment.status = "captured"
    payment.save()

    logger.info(
        f"Captured payment {razorpay_payment_id} for order {razorpay_order_id}, "
        f"purpose={payment.purpose}"
    )

    result = _execute_payment_action(payment)

    return {
        "already_processed": False,
        "payment_id": str(payment.id),
        "status": "captured",
        **result,
    }


def _execute_payment_action(payment: "Payment") -> Dict[str, Any]:
    """
    Execute business action based on payment purpose.

    Args:
        payment: Payment document

    Returns:
        dict with action result
    """
    from app.services.wallet_service import credit_wallet, get_wallet_balance
    from app.services.subscription_service import activate_subscription

    purpose = payment.purpose
    amount_paise = int(payment.amount)
    payment_id = str(payment.id)

    if purpose == "wallet_topup":
        user_id = str(payment.user.id)
        credit_wallet(
            user_id=user_id,
            amount_paise=amount_paise,
            purpose="top_up",
            source="razorpay",
            reference_id=payment_id,
            description=f"Wallet top-up via Razorpay payment {payment_id}",
        )
        balance = get_wallet_balance(user_id)
        logger.info(f"Wallet top-up complete for user {user_id}: +{amount_paise} paise")
        return {
            "action": "wallet_topup",
            "new_balance_paise": balance["balance_paise"],
            "new_balance_rupees": balance["balance_rupees"],
        }

    elif purpose == "subscription":
        metadata = payment.metadata or {}
        plan_id = metadata.get("plan_id")
        entity_id = metadata.get("entity_id")
        entity_type = metadata.get("entity_type", "institute")

        if not plan_id:
            raise PaymentServiceError("Plan ID not found in payment metadata")

        sub = activate_subscription(
            entity_id=entity_id,
            plan_id=plan_id,
            payment_id=payment_id,
            entity_type=entity_type,
        )
        logger.info(f"Subscription activated: {sub.id}")
        return {
            "action": "subscription",
            "subscription_id": str(sub.id),
            "subscription_active": True,
        }

    elif purpose == "exam_purchase":
        metadata = payment.metadata or {}
        exam_id = metadata.get("exam_id")
        user_id = str(payment.user.id)

        logger.info(f"Exam purchase payment captured: exam={exam_id}, user={user_id}")
        return {
            "action": "exam_purchase",
            "exam_id": exam_id,
            "access_granted": True,
        }

    else:
        logger.warning(f"Unknown payment purpose: {purpose}")
        return {"action": "unknown", "purpose": purpose}


def handle_webhook(payload: bytes, signature: str) -> Dict[str, Any]:
    """
    Process Razorpay webhook.
    ALWAYS returns HTTP 200 to Razorpay to prevent retries.
    All errors are logged internally.

    Args:
        payload: Raw webhook payload bytes
        signature: Razorpay webhook signature header value

    Returns:
        dict with processing result (for logging)
    """
    config = _get_config()

    try:
        expected = hmac.new(
            config["razorpay_webhook_secret"].encode(),
            payload,
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(expected, signature):
            logger.warning("Invalid webhook signature")
            return {"status": "rejected", "reason": "Invalid signature"}

        event = json.loads(payload.decode("utf-8"))
        event_type = event.get("event")
        payment_entity = event.get("payload", {}).get("payment", {}).get("entity", {})

        logger.info(f"Processing webhook event: {event_type}")

        if event_type == "payment.captured":
            return _handle_payment_captured(event, payment_entity)

        elif event_type == "payment.failed":
            return _handle_payment_failed(event, payment_entity)

        elif event_type == "refund.created":
            return _handle_refund_created(event, payment_entity)

        else:
            logger.info(f"Webhook event {event_type} received (no action)")
            return {"status": "received", "event": event_type}

    except Exception as exc:
        logger.exception(f"Webhook processing error: {exc}")
        return {"status": "error", "message": str(exc)}


def _handle_payment_captured(event: Dict, payment_entity: Dict) -> Dict[str, Any]:
    """Handle payment.captured webhook event."""
    from app.models import Payment
    from app.services.wallet_service import credit_wallet, get_wallet_balance

    razorpay_payment_id = payment_entity.get("id")
    razorpay_order_id = payment_entity.get("order_id")

    if not razorpay_payment_id:
        return {"status": "error", "reason": "No payment_id in entity"}

    payment = Payment.objects(razorpay_payment_id=razorpay_payment_id).first()
    if payment:
        if payment.status == "captured":
            return {"status": "skipped", "reason": "Already captured"}
        payment.status = "captured"
        payment.save()
        _execute_payment_action(payment)
        return {"status": "processed", "event": "payment.captured", "payment_id": str(payment.id)}

    payment = Payment.objects(razorpay_order_id=razorpay_order_id).first()
    if not payment:
        logger.warning(f"Payment not found for webhook: order={razorpay_order_id}, payment={razorpay_payment_id}")
        return {"status": "skipped", "reason": "Payment record not found"}

    payment.razorpay_payment_id = razorpay_payment_id
    payment.status = "captured"
    payment.save()

    try:
        _execute_payment_action(payment)
    except Exception as exc:
        logger.exception(f"Business action failed for captured payment {razorpay_payment_id}: {exc}")

    return {"status": "processed", "event": "payment.captured", "payment_id": str(payment.id)}


def _handle_payment_failed(event: Dict, payment_entity: Dict) -> Dict[str, Any]:
    """Handle payment.failed webhook event."""
    from app.models import Payment
    from app.tasks.email_tasks import send_payment_failed_email_task

    razorpay_payment_id = payment_entity.get("id")
    razorpay_order_id = payment_entity.get("order_id")

    payment = Payment.objects(
        razorpay_payment_id=razorpay_payment_id
    ).first() or Payment.objects(
        razorpay_order_id=razorpay_order_id
    ).first()

    if not payment:
        return {"status": "skipped", "reason": "Payment record not found"}

    payment.status = "failed"
    payment.save()

    try:
        send_payment_failed_email_task.delay(
            str(payment.user.id),
            payment.razorpay_order_id,
            str(payment.amount),
        )
    except Exception as exc:
        logger.warning(f"Failed to queue payment failure email: {exc}")

    return {"status": "processed", "event": "payment.failed", "payment_id": str(payment.id)}


def _handle_refund_created(event: Dict, payment_entity: Dict) -> Dict[str, Any]:
    """Handle refund.created webhook event."""
    from app.models import Payment
    from app.services.wallet_service import credit_wallet

    razorpay_payment_id = payment_entity.get("id")
    refund_amount = int(payment_entity.get("amount", 0))

    payment = Payment.objects(razorpay_payment_id=razorpay_payment_id).first()
    if not payment:
        return {"status": "skipped", "reason": "Payment not found"}

    payment.status = "refunded"
    payment.save()

    if refund_amount > 0 and payment.user:
        try:
            credit_wallet(
                user_id=str(payment.user.id),
                amount_paise=refund_amount,
                purpose="refund",
                source="razorpay",
                reference_id=str(payment.id),
                description=f"Refund for Razorpay payment {razorpay_payment_id}",
            )
            logger.info(f"Refund credited to wallet: {refund_amount} paise")
        except Exception as exc:
            logger.exception(f"Failed to credit refund to wallet: {exc}")

    return {
        "status": "processed",
        "event": "refund.created",
        "payment_id": str(payment.id),
        "refund_amount_paise": refund_amount,
    }
