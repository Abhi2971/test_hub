"""
Certificate model for ExamSaaS platform.
"""
import logging
from datetime import datetime
from mongoengine import (
    Document, StringField, FloatField, BooleanField,
    DateTimeField, ReferenceField
)

logger = logging.getLogger(__name__)


class Certificate(Document):
    meta = {
        'collection': 'certificates',
        'indexes': [
            {'fields': ['certificate_code'], 'unique': True},
            {'fields': ['student']},
            {'fields': ['result'], 'unique': True},
        ],
        'ordering': ['-created_at'],
    }
    
    student = ReferenceField('User', required=True)
    exam = ReferenceField('Exam', required=True)
    result = ReferenceField('Result', required=True, unique=True)
    institute = ReferenceField('Institute', required=True)
    certificate_code = StringField(required=True, unique=True)
    cloudinary_url = StringField()
    cloudinary_public_id = StringField()
    student_name = StringField()
    exam_name = StringField()
    institute_name = StringField()
    score = FloatField()
    grade = StringField()
    issued_at = DateTimeField()
    is_revoked = BooleanField(default=False)
    revoked_reason = StringField()
    created_at = DateTimeField(default=datetime.utcnow)
    
    def __str__(self):
        return f"Certificate({self.certificate_code})"
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'certificate_code': self.certificate_code,
            'student_id': str(self.student.id) if self.student else None,
            'exam_id': str(self.exam.id) if self.exam else None,
            'result_id': str(self.result.id) if self.result else None,
            'student_name': self.student_name,
            'exam_name': self.exam_name,
            'score': self.score,
            'grade': self.grade,
            'issued_at': self.issued_at.isoformat() if self.issued_at else None,
            'is_revoked': self.is_revoked,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


logger.info("Certificate model loaded")
