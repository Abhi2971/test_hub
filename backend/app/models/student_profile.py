"""
StudentProfile model for ExamSaaS platform.
"""
import logging
from mongoengine import Document, StringField, IntField, FloatField, ReferenceField

logger = logging.getLogger(__name__)


class StudentProfile(Document):
    """
    Extended profile for student users.
    """
    meta = {
        'collection': 'student_profiles',
        'indexes': [
            {'fields': ['user'], 'unique': True},
        ],
    }
    
    user = ReferenceField('User', required=True, unique=True)
    student_code = StringField(required=True, max_length=50)
    batch = StringField(max_length=50)
    section = StringField(max_length=20)
    year = IntField(min_value=1, max_value=10)
    teacher = ReferenceField('User', null=True)
    assigned_username = StringField(null=True)
    assigned_password_hash = StringField(null=True)
    free_exams_used = IntField(default=0)
    total_exams_taken = IntField(default=0)
    average_score = FloatField(default=0.0)
    
    def __str__(self):
        return f"StudentProfile({self.student_code})"
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': str(self.user.id) if self.user else None,
            'student_code': self.student_code,
            'batch': self.batch,
            'section': self.section,
            'year': self.year,
            'teacher_id': str(self.teacher.id) if self.teacher else None,
            'assigned_username': self.assigned_username,
            'free_exams_used': self.free_exams_used,
            'total_exams_taken': self.total_exams_taken,
            'average_score': self.average_score,
        }


logger.info("StudentProfile model loaded")
