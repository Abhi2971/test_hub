"""
Response helpers for consistent API responses.
"""
import logging
from typing import Any, Optional
from flask import jsonify, Response

logger = logging.getLogger(__name__)


def success_response(
    data: Any = None,
    message: str = "Success",
    status: int = 200,
    meta: Optional[dict] = None
) -> Response:
    """
    Create a standardized success response.
    
    Args:
        data: Response payload (dict, list, or None)
        message: Human-readable success message
        status: HTTP status code
        meta: Pagination metadata (optional)
    
    Returns:
        Flask Response with JSON body
    """
    response = {
        "success": True,
        "message": message,
        "data": data,
        "errors": None
    }
    
    if meta is not None:
        response["meta"] = meta
    
    logger.info(f"Success response: {message} (status={status})")
    return jsonify(response), status


def error_response(
    message: str = "Error",
    errors: Optional[dict] = None,
    status: int = 400
) -> Response:
    """
    Create a standardized error response.
    
    Args:
        message: Human-readable error message
        errors: Field-specific errors dict (e.g., {"email": "Invalid format"})
        status: HTTP status code
    
    Returns:
        Flask Response with JSON body
    """
    response = {
        "success": False,
        "message": message,
        "data": None,
        "errors": errors
    }
    
    logger.warning(f"Error response: {message} (status={status}, errors={errors})")
    return jsonify(response), status


def paginated_response(
    data: list,
    page: int,
    total: int,
    per_page: int,
    message: str = "Success"
) -> Response:
    """
    Create a standardized paginated response.
    
    Args:
        data: List of items for current page
        page: Current page number
        total: Total number of items
        per_page: Items per page
        message: Human-readable message
    
    Returns:
        Flask Response with JSON body including meta
    """
    meta = {
        "page": page,
        "total": total,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page if per_page > 0 else 0
    }
    
    logger.info(f"Paginated response: page {page}/{meta['total_pages']} ({total} total items)")
    return success_response(data=data, message=message, meta=meta)


def created_response(
    data: Any = None,
    message: str = "Resource created successfully"
) -> Response:
    """
    Create a standardized 201 Created response.
    
    Args:
        data: Created resource data
        message: Human-readable message
    
    Returns:
        Flask Response with 201 status
    """
    return success_response(data=data, message=message, status=201)


def no_content_response() -> Response:
    """
    Create a standardized 204 No Content response.
    
    Returns:
        Flask Response with 204 status
    """
    logger.info("No content response (204)")
    return "", 204
