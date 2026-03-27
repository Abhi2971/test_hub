"""
Marshmallow schemas for wallet operations.
"""
from marshmallow import Schema, fields, validate


class TransactionListSchema(Schema):
    """Schema for listing wallet transactions."""
    page = fields.Integer(load_default=1, validate=validate.Range(min=1))
    per_page = fields.Integer(load_default=20, validate=validate.Range(min=1, max=50))


class WalletBalanceSchema(Schema):
    """Schema for wallet balance response."""
    balance_paise = fields.Integer()
    balance_rupees = fields.Float()
    currency = fields.String()
    total_credited = fields.Integer()
    total_debited = fields.Integer()
