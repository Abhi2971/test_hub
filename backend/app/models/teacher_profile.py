"""
TeacherProfile model for ExamSaaS platform.
"""
import logging
from mongoengine import Document, StringField, IntField, ReferenceField

logger = logging.getLogger(__name__)


class TeacherProfile(Document):
    """
    Extended profile for teacher users.
    """
    meta = {
        'collection': 'teacher_profiles',
        'indexes': [],
    }
    
    user = ReferenceField('User', required=True, unique=True)
    teacher_code = StringField(required=True, max_length=50)
    department = StringField(max_length=100)
    designation = StringField(max_length=100)
    exams_created = IntField(default=0)
    students_managed = IntField(default=0)
    
    def __str__(self):
        return f"TeacherProfile({self.teacher_code})"
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': str(self.user.id) if self.user else None,
            'teacher_code': self.teacher_code,
            'department': self.department,
            'designation': self.designation,
            'exams_created': self.exams_created,
            'students_managed': self.students_managed,
        }


logger.info("TeacherProfile model loaded")
