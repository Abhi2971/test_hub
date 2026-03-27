"""
AuditLog model for ExamSaaS platform.
"""
import logging
from datetime import datetime
from mongoengine import (
    Document, StringField, DictField,
    DateTimeField, ReferenceField
)

logger = logging.getLogger(__name__)


class AuditLog(Document):
    meta = {
        'collection': 'audit_logs',
        'indexes': [
            {'fields': ['actor', '-created_at']},
            {'fields': ['institute', '-created_at']},
            {'fields': ['action']},
        ],
        'ordering': ['-created_at'],
    }
    
    actor = ReferenceField('User', null=True)
    actor_role = StringField()
    action = StringField(required=True)
    target_type = StringField()
    target_id = StringField()
    institute = ReferenceField('Institute', null=True)
    ip_address = StringField()
    user_agent = StringField()
    metadata = DictField()
    created_at = DateTimeField(default=datetime.utcnow)
    
    def __str__(self):
        return f"AuditLog({self.action}) by {self.actor_role}"
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'actor_id': str(self.actor.id) if self.actor else None,
            'actor_role': self.actor_role,
            'action': self.action,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'institute_id': str(self.institute.id) if self.institute else None,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


logger.info("AuditLog model loaded")
