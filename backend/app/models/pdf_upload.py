"""
PDFUpload model for ExamSaaS platform.
"""
import logging
from datetime import datetime
from mongoengine import (
    Document, StringField, IntField, BooleanField,
    DateTimeField, ReferenceField
)

logger = logging.getLogger(__name__)


class PDFUpload(Document):
    meta = {
        'collection': 'pdf_uploads',
        'indexes': [
            {'fields': ['institute', 'processing_status']},
            {'fields': ['uploaded_by']},
        ],
        'ordering': ['-created_at'],
    }
    
    PROCESSING_STATUS_CHOICES = (
        ('uploaded', 'Uploaded'), ('extracting', 'Extracting'), ('chunking', 'Chunking'),
        ('generating', 'Generating'), ('reviewing', 'Reviewing'), ('completed', 'Completed'), ('failed', 'Failed'),
    )
    
    original_filename = StringField(required=True)
    cloudinary_url = StringField()
    cloudinary_public_id = StringField()
    file_size_bytes = IntField()
    page_count = IntField()
    institute = ReferenceField('Institute', required=True)
    uploaded_by = ReferenceField('User', required=True)
    processing_status = StringField(choices=PROCESSING_STATUS_CHOICES, default='uploaded')
    processing_error = StringField()
    text_extracted = BooleanField(default=False)
    total_chunks = IntField(default=0)
    chunks_processed = IntField(default=0)
    questions_generated = IntField(default=0)
    questions_approved = IntField(default=0)
    celery_task_id = StringField()
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return f"PDFUpload({self.id}) - {self.original_filename}"
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'original_filename': self.original_filename,
            'cloudinary_url': self.cloudinary_url,
            'file_size_bytes': self.file_size_bytes,
            'page_count': self.page_count,
            'institute_id': str(self.institute.id) if self.institute else None,
            'processing_status': self.processing_status,
            'processing_error': self.processing_error,
            'text_extracted': self.text_extracted,
            'questions_generated': self.questions_generated,
            'questions_approved': self.questions_approved,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


logger.info("PDFUpload model loaded")
