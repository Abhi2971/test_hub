"""
AIRecommendation model for ExamSaaS platform.
"""
import logging
from datetime import datetime
from mongoengine import (
    Document, StringField, ListField, ReferenceField, DateTimeField
)

logger = logging.getLogger(__name__)


class AIRecommendation(Document):
    meta = {
        'collection': 'ai_recommendations',
        'indexes': [
            {'fields': ['student']},
            {'fields': ['result'], 'unique': True},
        ],
        'ordering': ['-created_at'],
    }
    
    DIFFICULTY_CHOICES = (('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard'))
    PROCESSING_STATUS_CHOICES = (('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed'))
    
    student = ReferenceField('User', required=True)
    result = ReferenceField('Result', required=True, unique=True)
    exam = ReferenceField('Exam', required=True)
    weak_topics = ListField(StringField(), default=list)
    recommendations = ListField(StringField(), default=list)
    learning_path = ListField(StringField(), default=list)
    next_difficulty = StringField(choices=DIFFICULTY_CHOICES)
    suggested_ebook_ids = ListField(ReferenceField('Ebook'), default=list)
    suggested_exam_ids = ListField(ReferenceField('Exam'), default=list)
    processing_status = StringField(choices=PROCESSING_STATUS_CHOICES, default='pending')
    error_message = StringField()
    created_at = DateTimeField(default=datetime.utcnow)
    
    def __str__(self):
        return f"AIRecommendation({self.id}) - {self.processing_status}"
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'student_id': str(self.student.id) if self.student else None,
            'result_id': str(self.result.id) if self.result else None,
            'exam_id': str(self.exam.id) if self.exam else None,
            'weak_topics': self.weak_topics,
            'recommendations': self.recommendations,
            'learning_path': self.learning_path,
            'next_difficulty': self.next_difficulty,
            'processing_status': self.processing_status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


logger.info("AIRecommendation model loaded")
