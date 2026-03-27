"""
Marshmallow schemas for payment operations.
"""
from marshmallow import Schema, fields, validate, validates_schema, ValidationError


class CreateOrderSchema(Schema):
    """Schema for creating a Razorpay order."""
    amount = fields.Integer(required=True, strict=True)
    purpose = fields.String(
        required=True,
        validate=validate.OneOf(["wallet_topup", "subscription", "exam_purchase"])
    )
    reference_id = fields.String(load_default=None)


class VerifyPaymentSchema(Schema):
    """Schema for verifying a Razorpay payment."""
    razorpay_order_id = fields.String(required=True)
    razorpay_payment_id = fields.String(required=True)
    razorpay_signature = fields.String(required=True)


class PaymentListSchema(Schema):
    """Schema for listing payments."""
    page = fields.Integer(load_default=1, validate=validate.Range(min=1))
    limit = fields.Integer(load_default=20, validate=validate.Range(min=1, max=100))
    status = fields.String(
        load_default=None,
        validate=validate.OneOf(["pending", "captured", "failed", "refunded"])
    )
    purpose = fields.String(
        load_default=None,
        validate=validate.OneOf(["wallet_topup", "subscription", "exam_purchase"])
    )


class WalletTopupSchema(Schema):
    """Schema for wallet top-up request."""
    amount_rupees = fields.Integer(required=True, strict=True)

    @validates_schema
    def validate_amount(self, data, **kwargs):
        amount = data.get("amount_rupees", 0)
        if amount < 50:
            raise ValidationError("Minimum top-up amount is ₹50", field_name="amount_rupees")
        if amount > 50000:
            raise ValidationError("Maximum top-up amount is ₹50,000", field_name="amount_rupees")


class WalletTopupCustomSchema(Schema):
    """Schema for custom wallet top-up."""
    amount_rupees = fields.Integer(required=True, strict=True)

    @validates_schema
    def validate_amount(self, data, **kwargs):
        amount = data.get("amount_rupees", 0)
        if amount < 50:
            raise ValidationError("Minimum top-up is ₹50", field_name="amount_rupees")
        if amount > 50000:
            raise ValidationError("Maximum top-up is ₹50,000", field_name="amount_rupees")
