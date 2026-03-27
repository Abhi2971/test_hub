"""
Wallet model for ExamSaaS platform.
"""
import logging
from datetime import datetime
from decimal import Decimal
from mongoengine import (
    Document, StringField, IntField,
    DateTimeField, ReferenceField
)
from bson.decimal128 import Decimal128

logger = logging.getLogger(__name__)


class Wallet(Document):
    """
    Wallet document for storing user balance.
    Balance uses Decimal128 for precision.
    """
    meta = {
        'collection': 'wallets',
        'indexes': [
            {'fields': ['user'], 'unique': True},
        ],
    }
    
    user = ReferenceField('User', required=True, unique=True)
    balance = IntField(default=0)
    currency = StringField(default='INR', max_length=3)
    total_credited = IntField(default=0)
    total_debited = IntField(default=0)
    version = IntField(default=0)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        if self.balance < 0:
            raise ValueError("Wallet balance cannot be negative")
        self.version += 1
        return super().save(*args, **kwargs)
    
    def credit(self, amount: int, purpose: str, reference_id: str = None):
        from app.models.wallet_transaction import WalletTransaction, TransactionType, TransactionSource, TransactionPurpose
        
        if amount <= 0:
            raise ValueError("Credit amount must be positive")
        
        self.balance += amount
        self.total_credited += amount
        self.save()
        
        transaction = WalletTransaction(
            wallet=self,
            user=self.user,
            type=TransactionType.CREDIT,
            amount=amount,
            balance_after=self.balance,
            purpose=TransactionPurpose.TOP_UP if purpose == 'top_up' else TransactionPurpose.ADMIN_CREDIT,
            source=TransactionSource.RAZORPAY,
            reference_id=reference_id or str(self.id),
            description=f"Credited {amount} paise for {purpose}"
        )
        transaction.save()
        return transaction
    
    def debit(self, amount: int, purpose: str, reference_id: str = None):
        from app.models.wallet_transaction import WalletTransaction, TransactionType, TransactionSource, TransactionPurpose
        
        if amount <= 0:
            raise ValueError("Debit amount must be positive")
        
        if self.balance < amount:
            raise ValueError("Insufficient balance")
        
        self.balance -= amount
        self.total_debited += amount
        self.save()
        
        transaction = WalletTransaction(
            wallet=self,
            user=self.user,
            type=TransactionType.DEBIT,
            amount=amount,
            balance_after=self.balance,
            purpose=TransactionPurpose.SUBSCRIPTION if purpose == 'subscription' else TransactionPurpose.EXAM_PURCHASE,
            source=TransactionSource.SYSTEM,
            reference_id=reference_id or str(self.id),
            description=f"Debited {amount} paise for {purpose}"
        )
        transaction.save()
        return transaction
    
    def __str__(self):
        return f"Wallet({self.id}) - Balance: {self.balance}"
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': str(self.user.id) if self.user else None,
            'balance': self.balance,
            'currency': self.currency,
            'total_credited': self.total_credited,
            'total_debited': self.total_debited,
            'version': self.version,
        }


logger.info("Wallet model loaded")
