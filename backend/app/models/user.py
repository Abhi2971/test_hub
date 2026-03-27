"""
User model for ExamSaaS platform.
"""
import logging
from datetime import datetime
from mongoengine import (
    Document, StringField, BooleanField, ReferenceField,
    DateTimeField, EmbeddedDocument, ListField, FloatField, EmbeddedDocumentField
)
import bcrypt

logger = logging.getLogger(__name__)


class FaceData(EmbeddedDocument):
    """Embedded document for face recognition data."""
    enrolled = BooleanField(default=False)
    descriptor = ListField(FloatField(), default=list)


class User(Document):
    """
    User document with authentication and profile data.
    """
    meta = {
        'collection': 'users',
        'indexes': [
            {'fields': ['email'], 'unique': True},
            {'fields': ['institute', 'role']},
            {'fields': ['google_id'], 'sparse': True},
        ],
        'ordering': ['-created_at'],
    }
    
    ROLE_CHOICES = (
        ('super_admin', 'Super Admin'),
        ('admin_public', 'Public Admin'),
        ('admin_college', 'College Admin'),
        ('teacher', 'Teacher'),
        ('student_registered', 'Registered Student'),
        ('student_assigned', 'Assigned Student'),
        ('support_agent', 'Support Agent'),
    )
    
    AUTH_PROVIDER_CHOICES = (
        ('local', 'Local'),
        ('google', 'Google'),
    )
    
    SUPPORT_SCOPE_CHOICES = (
        ('platform', 'Platform'),
        ('institute', 'Institute'),
    )
    
    email = StringField(required=True, unique=True)
    password_hash = StringField()
    first_name = StringField(required=True, max_length=100)
    last_name = StringField(max_length=100)
    role = StringField(choices=ROLE_CHOICES, required=True)
    institute = ReferenceField('Institute', null=True)
    is_active = BooleanField(default=True)
    is_email_verified = BooleanField(default=False)
    auth_provider = StringField(choices=AUTH_PROVIDER_CHOICES, default='local')
    google_id = StringField(null=True)
    avatar_url = StringField(null=True)
    phone = StringField(max_length=20, null=True)
    face_data = EmbeddedDocumentField(FaceData, default=FaceData)
    wallet = ReferenceField('Wallet', null=True)
    support_scope = StringField(choices=SUPPORT_SCOPE_CHOICES, null=True)
    last_login_at = DateTimeField(null=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
    
    def set_password(self, password: str) -> None:
        """Hash and set password."""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        """Verify password against hash."""
        if not self.password_hash:
            return False
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}".strip()
    
    def __str__(self):
        return f"{self.full_name} ({self.email})"
    
    def to_dict(self, include_sensitive: bool = False):
        data = {
            'id': str(self.id),
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'role': self.role,
            'is_active': self.is_active,
            'is_email_verified': self.is_email_verified,
            'avatar_url': self.avatar_url,
            'phone': self.phone,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if include_sensitive:
            data['last_login_at'] = self.last_login_at.isoformat() if self.last_login_at else None
        return data


logger.info("User model loaded")
