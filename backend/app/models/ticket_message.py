"""
TicketMessage model for ExamSaaS platform.
"""
import logging
from datetime import datetime
from mongoengine import (
    Document, StringField, BooleanField,
    DateTimeField, EmbeddedDocument, EmbeddedDocumentField, ListField, ReferenceField
)

logger = logging.getLogger(__name__)


class MessageAttachment(EmbeddedDocument):
    url = StringField(required=True)
    filename = StringField(required=True)


class TicketMessage(Document):
    meta = {
        'collection': 'ticket_messages',
        'indexes': [
            {'fields': ['ticket', 'created_at']},
        ],
        'ordering': ['created_at'],
    }
    
    ticket = ReferenceField('SupportTicket', required=True)
    sender = ReferenceField('User', required=True)
    sender_role = StringField()
    message = StringField(required=True)
    is_internal_note = BooleanField(default=False)
    attachments = ListField(EmbeddedDocumentField(MessageAttachment), default=list)
    created_at = DateTimeField(default=datetime.utcnow)
    
    def __str__(self):
        return f"Message({self.id}) on Ticket({self.ticket.id if self.ticket else 'N/A'})"
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'ticket_id': str(self.ticket.id) if self.ticket else None,
            'sender_id': str(self.sender.id) if self.sender else None,
            'sender_role': self.sender_role,
            'message': self.message,
            'is_internal_note': self.is_internal_note,
            'attachments': [{'url': att.url, 'filename': att.filename} for att in self.attachments],
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


logger.info("TicketMessage model loaded")
