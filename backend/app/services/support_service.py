"""
Support service for ExamSaaS platform.
Pure Python - zero Flask imports, zero HTTP concepts.
"""
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

REDIS_CLIENT = None


def _get_redis():
    """Get Redis client from extensions."""
    global REDIS_CLIENT
    if REDIS_CLIENT is None:
        try:
            from app.extensions import get_redis
            REDIS_CLIENT = get_redis()
        except RuntimeError:
            logger.warning("Redis not available for support service")
            return None
    return REDIS_CLIENT


def _get_config(key: str, default: Any = None) -> Any:
    """Get configuration value."""
    try:
        from flask import current_app
        return current_app.config.get(key, default)
    except RuntimeError:
        return default


class SupportServiceError(Exception):
    """Base exception for support service errors."""
    def __init__(self, message: str, code: str, status_code: int = 400):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class TicketNotFoundError(SupportServiceError):
    """Ticket not found."""
    def __init__(self):
        super().__init__("Ticket not found", "TICKET_NOT_FOUND", 404)


class AccessDeniedError(SupportServiceError):
    """Access denied to ticket."""
    def __init__(self):
        super().__init__("Access denied to this ticket", "ACCESS_DENIED", 403)


class InvalidStatusTransitionError(SupportServiceError):
    """Invalid status transition."""
    def __init__(self, message: str = "Invalid status transition"):
        super().__init__(message, "INVALID_STATUS_TRANSITION", 400)


def _generate_ticket_number() -> str:
    """Generate ticket number: TKT-YYYYMMDD-NNNN"""
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y%m%d")
    
    redis = _get_redis()
    
    if redis:
        try:
            counter_key = f"ticket_counter:{date_str}"
            counter = redis.incr(counter_key)
            
            if counter == 1:
                redis.expire(counter_key, 25 * 3600)
            
            ticket_num = f"TKT-{date_str}-{counter:04d}"
            return ticket_num
        except Exception as e:
            logger.error(f"Redis ticket counter failed: {e}")
    
    fallback_num = uuid.uuid4().hex[:8].upper()
    return f"TKT-{date_str}-{fallback_num}"


def create_ticket(data: dict, user_id: str, institute_id: str) -> dict:
    """
    Create a new support ticket.
    
    Args:
        data: Ticket data with keys: category, priority, subject, description
        user_id: User ID creating the ticket
        institute_id: Institute ID
    
    Returns:
        Created ticket dictionary
    
    Raises:
        SupportServiceError: If creation fails
    """
    from app.models import User, SupportTicket, Institute
    
    user = User.objects(id=user_id).first()
    if not user:
        raise SupportServiceError("User not found", "USER_NOT_FOUND", 404)
    
    institute = None
    if institute_id:
        institute = Institute.objects(id=institute_id).first()
    
    category = data.get("category", "other")
    priority = data.get("priority", "medium")
    subject = data.get("subject", "")
    description = data.get("description", "")
    
    if not subject:
        raise SupportServiceError("Subject is required", "SUBJECT_REQUIRED", 400)
    
    valid_categories = ["technical", "billing", "exam", "account", "other"]
    valid_priorities = ["low", "medium", "high", "critical"]
    
    if category not in valid_categories:
        category = "other"
    if priority not in valid_priorities:
        priority = "medium"
    
    ticket_number = _generate_ticket_number()
    
    ticket = SupportTicket(
        ticket_number=ticket_number,
        user=user,
        institute=institute,
        category=category,
        priority=priority,
        subject=subject,
        description=description,
        status="open",
    )
    ticket.save()
    
    logger.info(f"Ticket created: {ticket_number} by user {user_id}")
    
    return ticket.to_dict()


def get_ticket(ticket_id: str, user_id: str, user_role: str) -> dict:
    """
    Get a ticket by ID with access control.
    
    Args:
        ticket_id: Ticket ID
        user_id: Current user ID
        user_role: Current user role
    
    Returns:
        Ticket dictionary
    
    Raises:
        TicketNotFoundError: If ticket not found
        AccessDeniedError: If user doesn't have access
    """
    from app.models import SupportTicket
    
    ticket = SupportTicket.objects(id=ticket_id).first()
    if not ticket:
        raise TicketNotFoundError()
    
    is_agent = user_role in ["support_agent", "admin_college", "admin_public", "super_admin"]
    is_owner = str(ticket.user.id) == user_id
    
    if not is_agent and not is_owner:
        raise AccessDeniedError()
    
    return ticket.to_dict()


def list_tickets(
    user_id: str,
    user_role: str,
    filters: dict,
    page: int,
    limit: int
) -> dict:
    """
    List tickets with filtering and pagination.
    
    Args:
        user_id: Current user ID
        user_role: Current user role
        filters: Dict with optional keys: status, priority, category, assigned_to, assigned_to_me
        page: Page number (1-based)
        limit: Items per page
    
    Returns:
        Dict with tickets list and pagination info
    """
    from app.models import SupportTicket, User
    
    is_agent = user_role in ["support_agent", "admin_college", "admin_public", "super_admin"]
    
    query = {}
    
    if not is_agent:
        query["user"] = user_id
    else:
        if filters.get("assigned_to_me"):
            query["assigned_to"] = user_id
        
        if filters.get("assigned_to"):
            assigned_user = User.objects(id=filters["assigned_to"]).first()
            if assigned_user:
                query["assigned_to"] = assigned_user
    
    if filters.get("status"):
        query["status"] = filters["status"]
    
    if filters.get("priority"):
        query["priority"] = filters["priority"]
    
    if filters.get("category"):
        query["category"] = filters["category"]
    
    offset = (page - 1) * limit
    
    tickets = SupportTicket.objects(**query).order_by("-created_at").skip(offset).limit(limit)
    total = SupportTicket.objects(**query).count()
    
    ticket_list = [ticket.to_dict() for ticket in tickets]
    
    return {
        "tickets": ticket_list,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit,
        }
    }


def update_ticket(ticket_id: str, data: dict, updated_by: str) -> dict:
    """
    Update ticket status or priority.
    
    Args:
        ticket_id: Ticket ID
        data: Dict with optional keys: status, priority
        updated_by: User ID making the update
    
    Returns:
        Updated ticket dictionary
    
    Raises:
        TicketNotFoundError: If ticket not found
    """
    from app.models import SupportTicket
    
    ticket = SupportTicket.objects(id=ticket_id).first()
    if not ticket:
        raise TicketNotFoundError()
    
    if data.get("status"):
        new_status = data["status"]
        valid_statuses = ["open", "assigned", "in_progress", "resolved", "closed"]
        
        if new_status not in valid_statuses:
            raise SupportServiceError(f"Invalid status: {new_status}", "INVALID_STATUS", 400)
        
        if new_status == "resolved" and not ticket.resolved_at:
            ticket.resolved_at = datetime.now(timezone.utc)
        elif new_status == "closed" and not ticket.closed_at:
            ticket.closed_at = datetime.now(timezone.utc)
        
        ticket.status = new_status
    
    if data.get("priority"):
        new_priority = data["priority"]
        valid_priorities = ["low", "medium", "high", "critical"]
        
        if new_priority not in valid_priorities:
            raise SupportServiceError(f"Invalid priority: {new_priority}", "INVALID_PRIORITY", 400)
        
        ticket.priority = new_priority
    
    ticket.save()
    
    logger.info(f"Ticket {ticket.ticket_number} updated by {updated_by}")
    
    return ticket.to_dict()


def assign_ticket(ticket_id: str, agent_id: str, assigned_by: str) -> dict:
    """
    Assign ticket to a support agent.
    
    Args:
        ticket_id: Ticket ID
        agent_id: Agent user ID to assign to
        assigned_by: User ID making the assignment
    
    Returns:
        Updated ticket dictionary
    
    Raises:
        TicketNotFoundError: If ticket not found
    """
    from app.models import SupportTicket, User
    
    ticket = SupportTicket.objects(id=ticket_id).first()
    if not ticket:
        raise TicketNotFoundError()
    
    agent = User.objects(id=agent_id).first()
    if not agent:
        raise SupportServiceError("Agent not found", "AGENT_NOT_FOUND", 404)
    
    ticket.assigned_to = agent
    
    if ticket.status == "open":
        ticket.status = "assigned"
    
    ticket.save()
    
    logger.info(f"Ticket {ticket.ticket_number} assigned to agent {agent_id} by {assigned_by}")
    
    return ticket.to_dict()


def close_ticket(ticket_id: str, closed_by: str) -> dict:
    """
    Close a ticket.
    
    Args:
        ticket_id: Ticket ID
        closed_by: User ID closing the ticket
    
    Returns:
        Closed ticket dictionary
    
    Raises:
        TicketNotFoundError: If ticket not found
    """
    from app.models import SupportTicket
    
    ticket = SupportTicket.objects(id=ticket_id).first()
    if not ticket:
        raise TicketNotFoundError()
    
    ticket.status = "closed"
    ticket.closed_at = datetime.now(timezone.utc)
    
    if not ticket.resolved_at:
        ticket.resolved_at = ticket.closed_at
    
    ticket.save()
    
    logger.info(f"Ticket {ticket.ticket_number} closed by {closed_by}")
    
    return ticket.to_dict()


def add_message(ticket_id: str, data: dict, user_id: str) -> dict:
    """
    Add a message to a ticket.
    
    Args:
        ticket_id: Ticket ID
        data: Dict with keys: message, is_internal_note (optional)
        user_id: User ID adding the message
    
    Returns:
        Created message dictionary
    
    Raises:
        TicketNotFoundError: If ticket not found
    """
    from app.models import SupportTicket, TicketMessage, User
    
    ticket = SupportTicket.objects(id=ticket_id).first()
    if not ticket:
        raise TicketNotFoundError()
    
    user = User.objects(id=user_id).first()
    if not user:
        raise SupportServiceError("User not found", "USER_NOT_FOUND", 404)
    
    message_text = data.get("message", "")
    if not message_text:
        raise SupportServiceError("Message is required", "MESSAGE_REQUIRED", 400)
    
    is_internal_note = data.get("is_internal_note", False)
    
    user_role = user.role
    is_agent = user_role in ["support_agent", "admin_college", "admin_public", "super_admin"]
    
    if is_internal_note and not is_agent:
        raise SupportServiceError("Only agents can add internal notes", "ACCESS_DENIED", 403)
    
    message = TicketMessage(
        ticket=ticket,
        sender=user,
        sender_role=user_role,
        message=message_text,
        is_internal_note=is_internal_note,
    )
    message.save()
    
    if ticket.status == "open":
        ticket.status = "in_progress"
        ticket.save()
    
    logger.info(f"Message added to ticket {ticket.ticket_number} by user {user_id}")
    
    return message.to_dict()


def list_messages(ticket_id: str, user_id: str, user_role: str) -> list:
    """
    Get all messages for a ticket.
    
    Args:
        ticket_id: Ticket ID
        user_id: Current user ID
        user_role: Current user role
    
    Returns:
        List of message dictionaries
    
    Raises:
        TicketNotFoundError: If ticket not found
    """
    from app.models import SupportTicket, TicketMessage
    
    ticket = SupportTicket.objects(id=ticket_id).first()
    if not ticket:
        raise TicketNotFoundError()
    
    is_agent = user_role in ["support_agent", "admin_college", "admin_public", "super_admin"]
    
    messages = TicketMessage.objects(ticket=ticket).order_by("created_at")
    
    if not is_agent:
        messages = messages.filter(is_internal_note=False)
    
    return [msg.to_dict() for msg in messages]


def get_stats(user_role: str) -> dict:
    """
    Get support dashboard statistics.
    
    Args:
        user_role: Current user role
    
    Returns:
        Dictionary with statistics
    
    Raises:
        SupportServiceError: If user role cannot access stats
    """
    from app.models import SupportTicket, User
    
    is_agent = user_role in ["support_agent", "admin_college", "admin_public", "super_admin"]
    
    if not is_agent:
        raise SupportServiceError("Access denied to support stats", "ACCESS_DENIED", 403)
    
    query = {}
    if user_role == "support_agent":
        query["assigned_to"] = user_role
    
    total_tickets = SupportTicket.objects.count()
    
    open_tickets = SupportTicket.objects(status__in=["open", "assigned"]).count()
    
    in_progress_tickets = SupportTicket.objects(status="in_progress").count()
    
    resolved_tickets = SupportTicket.objects(status="resolved").count()
    
    closed_tickets = SupportTicket.objects(status="closed").count()
    
    critical_tickets = SupportTicket.objects(priority="critical", status__in=["open", "assigned"]).count()
    
    high_priority = SupportTicket.objects(priority="high", status__in=["open", "assigned"]).count()
    
    medium_priority = SupportTicket.objects(priority="medium", status__in=["open", "assigned"]).count()
    
    low_priority = SupportTicket.objects(priority="low", status__in=["open", "assigned"]).count()
    
    category_breakdown = {}
    for cat in ["technical", "billing", "exam", "account", "other"]:
        count = SupportTicket.objects(category=cat).count()
        category_breakdown[cat] = count
    
    return {
        "total": total_tickets,
        "open": open_tickets,
        "in_progress": in_progress_tickets,
        "resolved": resolved_tickets,
        "closed": closed_tickets,
        "critical": critical_tickets,
        "by_priority": {
            "critical": critical_tickets,
            "high": high_priority,
            "medium": medium_priority,
            "low": low_priority,
        },
        "by_category": category_breakdown,
    }