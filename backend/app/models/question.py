"""
Question model for ExamSaaS platform.
"""
import logging
from datetime import datetime
from mongoengine import (
    Document, StringField, IntField, BooleanField,
    DateTimeField, EmbeddedDocument, EmbeddedDocumentField, ListField, ReferenceField
)

logger = logging.getLogger(__name__)


class QuestionOption(EmbeddedDocument):
    option_id = StringField(required=True)
    text = StringField(required=True)


class Question(Document):
    meta = {
        'collection': 'questions',
        'indexes': [
            {'fields': ['institute', 'topic']},
            {'fields': ['created_by']},
            {'fields': ['source', 'is_reviewed']},
            {'fields': ['exam']},
        ],
        'ordering': ['-created_at'],
    }
    
    QUESTION_TYPE_CHOICES = (('mcq', 'Multiple Choice'), ('true_false', 'True/False'))
    DIFFICULTY_CHOICES = (('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard'))
    SOURCE_CHOICES = (('manual', 'Manual'), ('pdf', 'PDF Import'), ('ai_generated', 'AI Generated'))
    
    text = StringField(required=True)
    question_type = StringField(choices=QUESTION_TYPE_CHOICES, required=True)
    options = ListField(EmbeddedDocumentField(QuestionOption), default=list)
    correct_option_id = StringField()
    explanation = StringField()
    subject = StringField(max_length=100)
    topic = StringField(max_length=100)
    difficulty = StringField(choices=DIFFICULTY_CHOICES, default='medium')
    marks = IntField(default=1, min_value=1)
    source = StringField(choices=SOURCE_CHOICES, default='manual')
    pdf_upload = ReferenceField('PDFUpload', null=True)
    institute = ReferenceField('Institute', null=True)
    exam = ReferenceField('Exam', null=True)
    created_by = ReferenceField('User', required=True)
    is_reviewed = BooleanField(default=False)
    is_approved = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Question({self.id}) - {self.text[:50]}"
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'text': self.text,
            'question_type': self.question_type,
            'options': [{'option_id': opt.option_id, 'text': opt.text} for opt in self.options],
            'correct_option_id': self.correct_option_id,
            'explanation': self.explanation,
            'subject': self.subject,
            'topic': self.topic,
            'difficulty': self.difficulty,
            'marks': self.marks,
            'source': self.source,
            'is_reviewed': self.is_reviewed,
            'is_approved': self.is_approved,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


logger.info("Question model loaded")
