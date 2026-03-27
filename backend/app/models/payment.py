"""
Payment model for ExamSaaS platform.
"""
import logging
from datetime import datetime
from mongoengine import (
    Document, StringField, IntField, DictField,
    DateTimeField, ReferenceField
)

logger = logging.getLogger(__name__)


class Payment(Document):
    meta = {
        'collection': 'payments',
        'indexes': [
            {'fields': ['razorpay_order_id']},
            {'fields': ['razorpay_payment_id'], 'unique': True, 'sparse': True},
        ],
        'ordering': ['-created_at'],
    }
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('captured', 'Captured'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    
    PURPOSE_CHOICES = (
        ('wallet_topup', 'Wallet Top-up'),
        ('subscription', 'Subscription'),
        ('exam_purchase', 'Exam Purchase'),
    )
    
    user = ReferenceField('User', required=True)
    institute = ReferenceField('Institute', null=True)
    razorpay_order_id = StringField(required=True)
    razorpay_payment_id = StringField(unique=True, null=True)
    razorpay_signature = StringField(null=True)
    amount = IntField(required=True, min_value=0)
    currency = StringField(default='INR', max_length=3)
    status = StringField(choices=STATUS_CHOICES, default='pending')
    purpose = StringField(choices=PURPOSE_CHOICES, required=True)
    metadata = DictField()
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Payment({self.razorpay_order_id}) - {self.status}"
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': str(self.user.id) if self.user else None,
            'institute_id': str(self.institute.id) if self.institute else None,
            'razorpay_order_id': self.razorpay_order_id,
            'razorpay_payment_id': self.razorpay_payment_id,
            'amount': self.amount,
            'currency': self.currency,
            'status': self.status,
            'purpose': self.purpose,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


logger.info("Payment model loaded")
