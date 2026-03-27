"""
Support routes for ExamSaaS platform.
Blueprint: /api/v1/support
"""
import logging
from datetime import datetime
from flask import Blueprint, request, g

from app.response import success_response, error_response
from app.utils.decorators import require_auth, require_roles
from app.services.support_service import (
    create_ticket,
    get_ticket,
    list_tickets,
    update_ticket,
    assign_ticket,
    close_ticket,
    add_message,
    list_messages,
    SupportServiceError,
    TicketNotFoundError,
)

logger = logging.getLogger(__name__)

support_bp = Blueprint("support", __name__, url_prefix="/support")


def _handle_service_error(error: SupportServiceError):
    """Handle support service errors."""
    return error_response(error.message, error.status_code)


def _validate_schema(schema, data):
    """Validate request data against schema."""
    try:
        return schema.load(data), None
    except Exception as e:
        errors = e.messages if hasattr(e, "messages") else str(e)
        return None, errors


@support_bp.route("/tickets", methods=["POST"])
@require_auth
def create_ticket_route():
    """
    Create a new support ticket.
    
    Input:
        - subject: Ticket subject
        - description: Detailed description
        - category: Issue category (technical, billing, exam, other)
        - priority: low, medium, high
        - related_exam_id: Optional related exam ID
    
    Returns:
        201: Created ticket with ticket_number
    """
    data = request.get_json()
    
    if not data:
        return error_response("Request body is required", 400)
    
    required_fields = ["subject", "description", "category"]
    for field in required_fields:
        if field not in data:
            return error_response(f"Missing required field: {field}", 400)
    
    valid_categories = ["technical", "billing", "exam", "account", "other"]
    if data["category"] not in valid_categories:
        return error_response(f"Invalid category. Must be one of: {valid_categories}", 400)
    
    valid_priorities = ["low", "medium", "high", "urgent"]
    priority = data.get("priority", "medium")
    if priority not in valid_priorities:
        priority = "medium"
    
    try:
        ticket = create_ticket(
            user_id=g.current_user_id,
            subject=data["subject"],
            description=data["description"],
            category=data["category"],
            priority=priority,
            related_exam_id=data.get("related_exam_id"),
        )
        
        return success_response(ticket, "Ticket created successfully", status=201)
    
    except SupportServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Create ticket failed: {e}")
        return error_response("Failed to create ticket", 500)


@support_bp.route("/tickets", methods=["GET"])
@require_auth
def list_tickets_route():
    """
    List support tickets.
    
    For support agents: Returns all tickets with filters.
    For students: Returns only their own tickets.
    
    Query params:
        - page: Page number (default: 1)
        - per_page: Items per page (default: 20)
        - status: Filter by status (open, in_progress, resolved, closed)
        - priority: Filter by priority
        - category: Filter by category
    
    Returns:
        200: Paginated list of tickets
    """
    args = request.args.to_dict()
    
    try:
        page = int(args.get("page", 1))
        per_page = int(args.get("per_page", 20))
        
        filters = {}
        if args.get("status"):
            filters["status"] = args["status"]
        if args.get("priority"):
            filters["priority"] = args["priority"]
        if args.get("category"):
            filters["category"] = args["category"]
        
        is_agent = g.current_role in ["support_agent", "super_admin"]
        
        result = list_tickets(
            user_id=g.current_user_id,
            user_role=g.current_role,
            filters=filters,
            page=page,
            limit=per_page,
        )
        
        return success_response(result)
    
    except SupportServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"List tickets failed: {e}")
        return error_response("Failed to list tickets", 500)


@support_bp.route("/tickets/<ticket_id>", methods=["GET"])
@require_auth
def get_ticket_route(ticket_id: str):
    """
    Get ticket details by ID.
    
    Returns:
        200: Ticket details
    """
    try:
        ticket = get_ticket(
            ticket_id=ticket_id,
            user_id=g.current_user_id,
            user_role=g.current_role,
        )
        
        return success_response(ticket)
    
    except TicketNotFoundError as e:
        return _handle_service_error(e)
    except SupportServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Get ticket failed: {e}")
        return error_response("Failed to get ticket", 500)


@support_bp.route("/tickets/<ticket_id>", methods=["PATCH"])
@require_roles("support_agent", "super_admin")
def update_ticket_route(ticket_id: str):
    """
    Update ticket status or priority.
    
    Input:
        - status: New status (open, in_progress, resolved, closed)
        - priority: New priority (low, medium, high, urgent)
    
    Returns:
        200: Updated ticket
    """
    data = request.get_json()
    
    if not data:
        return error_response("Request body is required", 400)
    
    valid_statuses = ["open", "in_progress", "resolved", "closed"]
    valid_priorities = ["low", "medium", "high", "urgent"]
    
    update_data = {}
    if "status" in data:
        if data["status"] not in valid_statuses:
            return error_response(f"Invalid status. Must be one of: {valid_statuses}", 400)
        update_data["status"] = data["status"]
    
    if "priority" in data:
        if data["priority"] not in valid_priorities:
            return error_response(f"Invalid priority. Must be one of: {valid_priorities}", 400)
        update_data["priority"] = data["priority"]
    
    if not update_data:
        return error_response("No valid fields to update", 400)
    
    try:
        ticket = update_ticket(
            ticket_id=ticket_id,
            updated_by=g.current_user_id,
            **update_data,
        )
        
        return success_response(ticket, "Ticket updated successfully")
    
    except TicketNotFoundError as e:
        return _handle_service_error(e)
    except SupportServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Update ticket failed: {e}")
        return error_response("Failed to update ticket", 500)


@support_bp.route("/tickets/<ticket_id>/assign", methods=["POST"])
@require_roles("support_agent", "super_admin")
def assign_ticket_route(ticket_id: str):
    """
    Assign ticket to a support agent.
    
    Input:
        - agent_id: ID of the support agent to assign
    
    Returns:
        200: Updated ticket
    """
    data = request.get_json()
    
    if not data or "agent_id" not in data:
        return error_response("agent_id is required", 400)
    
    try:
        ticket = assign_ticket(
            ticket_id=ticket_id,
            agent_id=data["agent_id"],
            assigned_by=g.current_user_id,
        )
        
        return success_response(ticket, "Ticket assigned successfully")
    
    except TicketNotFoundError as e:
        return _handle_service_error(e)
    except SupportServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Assign ticket failed: {e}")
        return error_response("Failed to assign ticket", 500)


@support_bp.route("/tickets/<ticket_id>/close", methods=["POST"])
@require_roles("support_agent", "super_admin")
def close_ticket_route(ticket_id: str):
    """
    Close a support ticket.
    
    Input:
        - resolution: Resolution notes (optional)
    
    Returns:
        200: Closed ticket
    """
    data = request.get_json() or {}
    
    try:
        ticket = close_ticket(
            ticket_id=ticket_id,
            closed_by=g.current_user_id,
            resolution=data.get("resolution"),
        )
        
        return success_response(ticket, "Ticket closed successfully")
    
    except TicketNotFoundError as e:
        return _handle_service_error(e)
    except SupportServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Close ticket failed: {e}")
        return error_response("Failed to close ticket", 500)


@support_bp.route("/tickets/<ticket_id>/messages", methods=["POST"])
@require_auth
def add_message_route(ticket_id: str):
    """
    Add a message to a ticket.
    
    Input:
        - message: Message text
        - is_internal_note: Whether this is an internal note (default: false)
    
    Returns:
        201: Created message
    """
    data = request.get_json()
    
    if not data or "message" not in data:
        return error_response("message is required", 400)
    
    is_internal = data.get("is_internal_note", False)
    if is_internal and g.current_role not in ["support_agent", "super_admin"]:
        return error_response("Only support agents can add internal notes", 403)
    
    try:
        message = add_message(
            ticket_id=ticket_id,
            user_id=g.current_user_id,
            user_role=g.current_role,
            message=data["message"],
            is_internal_note=is_internal,
        )
        
        return success_response(message, "Message added successfully", status=201)
    
    except TicketNotFoundError as e:
        return _handle_service_error(e)
    except SupportServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Add message failed: {e}")
        return error_response("Failed to add message", 500)


@support_bp.route("/tickets/<ticket_id>/messages", methods=["GET"])
@require_auth
def list_messages_route(ticket_id: str):
    """
    List messages for a ticket.
    
    For non-agents: Returns only non-internal messages.
    For agents: Returns all messages including internal notes.
    
    Returns:
        200: List of messages
    """
    try:
        is_agent = g.current_role in ["support_agent", "super_admin"]
        
        messages = list_messages(
            ticket_id=ticket_id,
            user_id=g.current_user_id,
            user_role=g.current_role,
            include_internal=is_agent,
        )
        
        return success_response({"messages": messages})
    
    except TicketNotFoundError as e:
        return _handle_service_error(e)
    except SupportServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"List messages failed: {e}")
        return error_response("Failed to list messages", 500)