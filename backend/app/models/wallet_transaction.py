"""
WalletTransaction model for ExamSaaS platform.
"""
import logging
from datetime import datetime
from mongoengine import (
    Document, StringField, IntField,
    DateTimeField, ReferenceField
)

logger = logging.getLogger(__name__)


class TransactionType:
    CREDIT = 'credit'
    DEBIT = 'debit'


class TransactionSource:
    RAZORPAY = 'razorpay'
    ADMIN = 'admin'
    SYSTEM = 'system'


class TransactionPurpose:
    SUBSCRIPTION = 'subscription'
    EXAM_PURCHASE = 'exam_purchase'
    REFUND = 'refund'
    TOP_UP = 'top_up'
    ADMIN_CREDIT = 'admin_credit'


class WalletTransaction(Document):
    meta = {
        'collection': 'wallet_transactions',
        'indexes': [
            {'fields': ['wallet', '-created_at']},
            {'fields': ['user']},
        ],
        'ordering': ['-created_at'],
    }
    
    wallet = ReferenceField('Wallet', required=True)
    user = ReferenceField('User', required=True)
    type = StringField(required=True, choices=[('credit', 'Credit'), ('debit', 'Debit')])
    amount = IntField(required=True, min_value=0)
    balance_after = IntField(required=True)
    purpose = StringField(required=True)
    source = StringField(required=True)
    reference_id = StringField()
    description = StringField()
    created_at = DateTimeField(default=datetime.utcnow)
    
    def __str__(self):
        return f"Transaction({self.type}) - {self.amount} paise"
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'wallet_id': str(self.wallet.id) if self.wallet else None,
            'user_id': str(self.user.id) if self.user else None,
            'type': self.type,
            'amount': self.amount,
            'balance_after': self.balance_after,
            'purpose': self.purpose,
            'source': self.source,
            'reference_id': self.reference_id,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


logger.info("WalletTransaction model loaded")
