"""
Plan model for ExamSaaS platform.
"""
import logging
from datetime import datetime
from mongoengine import (
    Document, StringField, IntField, BooleanField,
    DateTimeField, EmbeddedDocument, EmbeddedDocumentField, ReferenceField
)

logger = logging.getLogger(__name__)


class FeatureFlags(EmbeddedDocument):
    """Embedded document for plan feature flags."""
    ebook_access = BooleanField(default=False)
    ai_recommendations = BooleanField(default=False)
    pdf_exam_generation = BooleanField(default=False)
    certificate_generation = BooleanField(default=False)
    live_monitoring = BooleanField(default=False)
    excel_export = BooleanField(default=False)
    marketplace_access = BooleanField(default=False)


class Plan(Document):
    """
    Subscription plan document.
    """
    meta = {
        'collection': 'plans',
        'indexes': [
            {'fields': ['slug'], 'unique': True},
            {'fields': ['is_for', 'is_active']},
        ],
        'ordering': ['price'],
    }
    
    IS_FOR_CHOICES = (
        ('student', 'Student'),
        ('institute', 'Institute'),
    )
    
    name = StringField(required=True, max_length=100)
    slug = StringField(required=True, unique=True)
    price = IntField(required=True, min_value=0)
    currency = StringField(default='INR', max_length=3)
    duration_days = IntField(required=True, min_value=1)
    max_students = IntField(default=0)
    max_teachers = IntField(default=0)
    exam_limit = IntField(default=0)
    ai_usage_limit = IntField(default=0)
    feature_flags = EmbeddedDocumentField(FeatureFlags, default=FeatureFlags)
    is_for = StringField(choices=IS_FOR_CHOICES, required=True)
    is_active = BooleanField(default=True)
    created_by = ReferenceField('User', null=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'slug': self.slug,
            'price': self.price,
            'currency': self.currency,
            'duration_days': self.duration_days,
            'max_students': self.max_students,
            'max_teachers': self.max_teachers,
            'exam_limit': self.exam_limit,
            'ai_usage_limit': self.ai_usage_limit,
            'feature_flags': {
                'ebook_access': self.feature_flags.ebook_access,
                'ai_recommendations': self.feature_flags.ai_recommendations,
                'pdf_exam_generation': self.feature_flags.pdf_exam_generation,
                'certificate_generation': self.feature_flags.certificate_generation,
                'live_monitoring': self.feature_flags.live_monitoring,
                'excel_export': self.feature_flags.excel_export,
                'marketplace_access': self.feature_flags.marketplace_access,
            },
            'is_for': self.is_for,
            'is_active': self.is_active,
        }


logger.info("Plan model loaded")
