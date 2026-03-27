"""
Institute model for ExamSaaS platform.
"""
import logging
from datetime import datetime
from mongoengine import (
    Document, StringField, BooleanField, ReferenceField,
    DateTimeField, EmbeddedDocumentField, CASCADE
)

logger = logging.getLogger(__name__)


class Institute(Document):
    """
    Institute/Organization document for multi-tenant SaaS.
    """
    meta = {
        'collection': 'institutes',
        'indexes': [
            {'fields': ['slug'], 'unique': True},
            {'fields': ['is_active']},
        ],
        'ordering': ['-created_at'],
    }
    
    ADMIN_TYPE_CHOICES = (
        ('platform_admin', 'Platform Admin'),
        ('institute_admin', 'Institute Admin'),
    )
    
    name = StringField(required=True, max_length=255)
    slug = StringField(required=True, unique=True)
    logo_url = StringField()
    address = StringField(max_length=500)
    city = StringField(max_length=100)
    state = StringField(max_length=100)
    country = StringField(max_length=100, default='India')
    admin_type = StringField(choices=ADMIN_TYPE_CHOICES, default='institute_admin')
    is_active = BooleanField(default=True)
    is_suspended = BooleanField(default=False)
    subscription = ReferenceField('Subscription', null=True)
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
            'logo_url': self.logo_url,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'admin_type': self.admin_type,
            'is_active': self.is_active,
            'is_suspended': self.is_suspended,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


logger.info("Institute model loaded")
