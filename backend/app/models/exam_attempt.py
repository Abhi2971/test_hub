"""
ExamAttempt model for ExamSaaS platform.
"""
import logging
from datetime import datetime
from mongoengine import (
    Document, StringField, IntField, BooleanField,
    DateTimeField, EmbeddedDocument, EmbeddedDocumentField, ListField, ReferenceField
)

logger = logging.getLogger(__name__)


class Answer(EmbeddedDocument):
    question_id = StringField(required=True)
    selected_option_id = StringField()
    flagged = BooleanField(default=False)
    time_spent_seconds = IntField(default=0)


class Violation(EmbeddedDocument):
    TYPE_CHOICES = ('tab_switch', 'face_mismatch', 'fullscreen_exit', 'copy_paste')
    type = StringField(required=True, choices=[(t, t) for t in TYPE_CHOICES])
    occurred_at = DateTimeField()
    screenshot_url = StringField()


class ExamAttempt(Document):
    meta = {
        'collection': 'exam_attempts',
        'indexes': [
            {'fields': ['exam', 'student']},
            {'fields': ['status', '-created_at']},
            {'fields': ['student']},
        ],
        'ordering': ['-created_at'],
    }
    
    STATUS_CHOICES = (('in_progress', 'In Progress'), ('submitted', 'Submitted'), ('auto_submitted', 'Auto Submitted'), ('force_submitted', 'Force Submitted'))
    ACCESS_METHOD_CHOICES = (('magic_link', 'Magic Link'), ('passcode', 'Passcode'), ('direct', 'Direct'))
    
    exam = ReferenceField('Exam', required=True)
    student = ReferenceField('User', required=True)
    status = StringField(choices=STATUS_CHOICES, default='in_progress')
    started_at = DateTimeField()
    submitted_at = DateTimeField()
    answers = ListField(EmbeddedDocumentField(Answer), default=list)
    violations = ListField(EmbeddedDocumentField(Violation), default=list)
    tab_switch_count = IntField(default=0)
    face_check_count = IntField(default=0)
    face_mismatch_count = IntField(default=0)
    access_method = StringField(choices=ACCESS_METHOD_CHOICES, default='direct')
    ip_address = StringField()
    user_agent = StringField()
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return f"ExamAttempt({self.id}) - {self.status}"
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'exam_id': str(self.exam.id) if self.exam else None,
            'student_id': str(self.student.id) if self.student else None,
            'status': self.status,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'tab_switch_count': self.tab_switch_count,
            'face_mismatch_count': self.face_mismatch_count,
            'access_method': self.access_method,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


logger.info("ExamAttempt model loaded")
