"""
SupportTicket model for ExamSaaS platform.
"""
import logging
from datetime import datetime
from mongoengine import (
    Document, StringField, DateTimeField, EmbeddedDocument, EmbeddedDocumentField, ListField, ReferenceField
)

logger = logging.getLogger(__name__)


class TicketAttachment(EmbeddedDocument):
    url = StringField(required=True)
    filename = StringField(required=True)


class SupportTicket(Document):
    meta = {
        'collection': 'support_tickets',
        'indexes': [
            {'fields': ['status', '-priority']},
            {'fields': ['institute']},
            {'fields': ['user']},
        ],
        'ordering': ['-created_at'],
    }
    
    CATEGORY_CHOICES = (('technical', 'Technical'), ('billing', 'Billing'), ('exam', 'Exam'), ('account', 'Account'), ('other', 'Other'))
    PRIORITY_CHOICES = (('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical'))
    STATUS_CHOICES = (('open', 'Open'), ('assigned', 'Assigned'), ('in_progress', 'In Progress'), ('resolved', 'Resolved'), ('closed', 'Closed'))
    
    ticket_number = StringField(required=True, unique=True)
    user = ReferenceField('User', required=True)
    institute = ReferenceField('Institute', null=True)
    category = StringField(choices=CATEGORY_CHOICES, required=True)
    priority = StringField(choices=PRIORITY_CHOICES, default='medium')
    status = StringField(choices=STATUS_CHOICES, default='open')
    subject = StringField(required=True, max_length=255)
    description = StringField()
    assigned_to = ReferenceField('User', null=True)
    attachments = ListField(EmbeddedDocumentField(TicketAttachment), default=list)
    resolved_at = DateTimeField()
    closed_at = DateTimeField()
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Ticket({self.ticket_number}) - {self.subject}"
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'ticket_number': self.ticket_number,
            'user_id': str(self.user.id) if self.user else None,
            'institute_id': str(self.institute.id) if self.institute else None,
            'category': self.category,
            'priority': self.priority,
            'status': self.status,
            'subject': self.subject,
            'description': self.description,
            'assigned_to_id': str(self.assigned_to.id) if self.assigned_to else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'closed_at': self.closed_at.isoformat() if self.closed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


logger.info("SupportTicket model loaded")
