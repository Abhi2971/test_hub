"""
Exam model for ExamSaaS platform.
"""
import logging
from datetime import datetime
from mongoengine import (
    Document, StringField, IntField, FloatField, BooleanField,
    DateTimeField, EmbeddedDocument, EmbeddedDocumentField, ListField, ReferenceField
)

logger = logging.getLogger(__name__)


class Schedule(EmbeddedDocument):
    start_at = DateTimeField()
    end_at = DateTimeField()
    grace_minutes = IntField(default=5)


class Security(EmbeddedDocument):
    camera_required = BooleanField(default=False)
    tab_switch_limit = IntField(default=3)
    fullscreen_required = BooleanField(default=False)
    copy_paste_disabled = BooleanField(default=False)
    shuffle_questions = BooleanField(default=False)
    shuffle_options = BooleanField(default=False)
    passcode_hash = StringField(null=True)
    magic_link_token = StringField(null=True)


class Exam(Document):
    meta = {
        'collection': 'exams',
        'indexes': [
            {'fields': ['institute', 'status']},
            {'fields': ['created_by']},
            {'fields': ['exam_type', 'status']},
        ],
        'ordering': ['-created_at'],
    }
    
    EXAM_TYPE_CHOICES = (('institute', 'Institute'), ('public', 'Public'))
    STATUS_CHOICES = (('draft', 'Draft'), ('pending_approval', 'Pending Approval'), ('published', 'Published'), ('active', 'Active'), ('closed', 'Closed'), ('archived', 'Archived'))
    RESULT_MODE_CHOICES = (('instant', 'Instant'), ('delayed', 'Delayed'))
    ACCESS_MODE_CHOICES = (('magic_link', 'Magic Link'), ('passcode', 'Passcode'), ('open', 'Open'))
    
    title = StringField(required=True, max_length=255)
    description = StringField()
    subject = StringField(max_length=100)
    topic = StringField(max_length=100)
    institute = ReferenceField('Institute', null=True)
    created_by = ReferenceField('User', required=True)
    exam_type = StringField(choices=EXAM_TYPE_CHOICES, default='institute')
    status = StringField(choices=STATUS_CHOICES, default='draft')
    total_marks = IntField(default=0)
    passing_percentage = FloatField(default=40.0)
    duration_minutes = IntField(default=60)
    schedule = EmbeddedDocumentField(Schedule, default=Schedule)
    security = EmbeddedDocumentField(Security, default=Security)
    result_mode = StringField(choices=RESULT_MODE_CHOICES, default='instant')
    access_mode = StringField(choices=ACCESS_MODE_CHOICES, default='open')
    price = IntField(default=0)
    allowed_attempts = IntField(default=1)
    certificate_enabled = BooleanField(default=False)
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
            'topic': self.topic,
            'institute_id': str(self.institute.id) if self.institute else None,
            'created_by_id': str(self.created_by.id) if self.created_by else None,
            'exam_type': self.exam_type,
            'status': self.status,
            'total_marks': self.total_marks,
            'passing_percentage': self.passing_percentage,
            'duration_minutes': self.duration_minutes,
            'result_mode': self.result_mode,
            'access_mode': self.access_mode,
            'price': self.price,
            'allowed_attempts': self.allowed_attempts,
            'certificate_enabled': self.certificate_enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


logger.info("Exam model loaded")
