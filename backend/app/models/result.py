"""
Result model for ExamSaaS platform.
"""
import logging
from datetime import datetime
from mongoengine import (
    Document, StringField, IntField, FloatField, BooleanField,
    DateTimeField, EmbeddedDocument, EmbeddedDocumentField, ListField, ReferenceField
)

logger = logging.getLogger(__name__)


class PerQuestionAnalysis(EmbeddedDocument):
    question_id = StringField(required=True)
    correct = BooleanField()
    time_spent_seconds = IntField()
    topic = StringField()


class TopicPerformance(EmbeddedDocument):
    topic = StringField()
    correct = IntField()
    total = IntField()
    percentage = FloatField()


class Result(Document):
    meta = {
        'collection': 'results',
        'indexes': [
            {'fields': ['student', 'exam']},
            {'fields': ['institute']},
            {'fields': ['attempt'], 'unique': True},
        ],
        'ordering': ['-created_at'],
    }
    
    exam = ReferenceField('Exam', required=True)
    student = ReferenceField('User', required=True)
    attempt = ReferenceField('ExamAttempt', required=True, unique=True)
    institute = ReferenceField('Institute', null=True)
    score = FloatField(default=0.0)
    total_marks = IntField(default=0)
    percentage = FloatField(default=0.0)
    passed = BooleanField(default=False)
    grade = StringField()
    correct_count = IntField(default=0)
    wrong_count = IntField(default=0)
    unattempted_count = IntField(default=0)
    per_question_analysis = ListField(EmbeddedDocumentField(PerQuestionAnalysis), default=list)
    topic_performance = ListField(EmbeddedDocumentField(TopicPerformance), default=list)
    rank = IntField()
    is_published = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.utcnow)
    
    def __str__(self):
        return f"Result({self.id}) - {self.percentage}%"
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'exam_id': str(self.exam.id) if self.exam else None,
            'student_id': str(self.student.id) if self.student else None,
            'attempt_id': str(self.attempt.id) if self.attempt else None,
            'score': self.score,
            'total_marks': self.total_marks,
            'percentage': self.percentage,
            'passed': self.passed,
            'grade': self.grade,
            'correct_count': self.correct_count,
            'wrong_count': self.wrong_count,
            'unattempted_count': self.unattempted_count,
            'rank': self.rank,
            'is_published': self.is_published,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


logger.info("Result model loaded")
