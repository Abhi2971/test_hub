"""
Subscription model for ExamSaaS platform.
"""
import logging
from datetime import datetime, timedelta
from mongoengine import (
    Document, StringField, IntField, BooleanField,
    DateTimeField, ReferenceField
)

logger = logging.getLogger(__name__)


class Subscription(Document):
    """
    Subscription document linking institutes/students to plans.
    """
    meta = {
        'collection': 'subscriptions',
        'indexes': [
            {'fields': ['institute', 'status']},
            {'fields': ['student', 'status']},
        ],
        'ordering': ['-created_at'],
    }
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('grace', 'Grace Period'),
        ('cancelled', 'Cancelled'),
    )
    
    institute = ReferenceField('Institute', null=True)
    student = ReferenceField('User', null=True)
    plan = ReferenceField('Plan', required=True)
    status = StringField(choices=STATUS_CHOICES, default='active')
    starts_at = DateTimeField(required=True)
    expires_at = DateTimeField(required=True)
    grace_until = DateTimeField()
    ai_usage_this_month = IntField(default=0)
    payment = ReferenceField('Payment', null=True)
    auto_renew = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        if self.expires_at and not self.grace_until:
            self.grace_until = self.expires_at + timedelta(days=7)
        return super().save(*args, **kwargs)
    
    @property
    def is_expired(self) -> bool:
        """Check if subscription is expired."""
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_in_grace(self) -> bool:
        """Check if subscription is in grace period."""
        if not self.is_expired:
            return False
        return datetime.utcnow() <= self.grace_until
    
    def __str__(self):
        return f"Subscription({self.id}) - {self.status}"
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'institute_id': str(self.institute.id) if self.institute else None,
            'student_id': str(self.student.id) if self.student else None,
            'plan_id': str(self.plan.id) if self.plan else None,
            'status': self.status,
            'starts_at': self.starts_at.isoformat() if self.starts_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'grace_until': self.grace_until.isoformat() if self.grace_until else None,
            'ai_usage_this_month': self.ai_usage_this_month,
            'auto_renew': self.auto_renew,
            'is_expired': self.is_expired,
            'is_in_grace': self.is_in_grace,
        }


logger.info("Subscription model loaded")
