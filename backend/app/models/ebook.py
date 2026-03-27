"""
Ebook model for ExamSaaS platform.
"""
import logging
from datetime import datetime
from mongoengine import (
    Document, StringField, IntField, BooleanField,
    DateTimeField, ReferenceField
)

logger = logging.getLogger(__name__)


class Ebook(Document):
    meta = {
        'collection': 'ebooks',
        'indexes': [
            {'fields': ['institute', 'is_active']},
            {'fields': ['access_level', 'subject']},
        ],
        'ordering': ['-created_at'],
    }
    
    ACCESS_LEVEL_CHOICES = (('free', 'Free'), ('subscription', 'Subscription'), ('purchase', 'Purchase'))
    
    title = StringField(required=True, max_length=255)
    description = StringField()
    subject = StringField(max_length=100)
    topics = StringField()
    cloudinary_url = StringField()
    cloudinary_public_id = StringField()
    thumbnail_url = StringField()
    file_size_bytes = IntField()
    page_count = IntField()
    access_level = StringField(choices=ACCESS_LEVEL_CHOICES, default='subscription')
    price = IntField(default=0)
    institute = ReferenceField('Institute', null=True)
    uploaded_by = ReferenceField('User', required=True)
    download_count = IntField(default=0)
    view_count = IntField(default=0)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'title': self.title,
            'description': self.description,
            'subject': self.subject,
            'topics': self.topics,
            'cloudinary_url': self.cloudinary_url,
            'thumbnail_url': self.thumbnail_url,
            'page_count': self.page_count,
            'access_level': self.access_level,
            'price': self.price,
            'institute_id': str(self.institute.id) if self.institute else None,
            'download_count': self.download_count,
            'view_count': self.view_count,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


logger.info("Ebook model loaded")
