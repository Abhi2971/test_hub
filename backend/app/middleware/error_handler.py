"""
Error handler middleware for ExamSaaS platform.
Global exception handling with JSON responses.
"""
import logging
import traceback
from typing import Optional, Callable

from flask import Flask, jsonify, request, Response
from marshmallow import ValidationError as MarshmallowValidationError

from app.exceptions import (
    ExamSaaSException,
    RateLimitError,
)

logger = logging.getLogger(__name__)


class ErrorHandler:
    """
    Global error handler for Flask application.
    
    Registers handlers for:
      - 400: Bad Request
      - 401: Unauthorized
      - 403: Forbidden
      - 404: Not Found
      - 405: Method Not Allowed
      - 409: Conflict
      - 422: Unprocessable Entity
      - 429: Too Many Requests
      - 500: Internal Server Error
    
    Custom exception classes are also handled automatically.
    """
    
    def __init__(self, app: Optional[Flask] = None):
        self.app = app
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask) -> None:
        """Initialize error handlers with Flask app."""
        self.app = app
        
        self._register_handlers()
        
        app.logger.info("ErrorHandler middleware initialized")
    
    def _register_handlers(self) -> None:
        """Register all error handlers."""
        
        @self.app.errorhandler(ExamSaaSException)
        def handle_examsaas_exception(error: ExamSaaSException) -> tuple:
            """Handle custom ExamSaaS exceptions."""
            response = {
                "success": False,
                "message": error.message,
                "errors": error.errors,
            }
            
            if isinstance(error, RateLimitError):
                response_headers = {
                    'Retry-After': str(error.errors.get('retry_after', 60)),
                    'X-RateLimit-Limit': str(error.errors.get('limit', 0)),
                    'X-RateLimit-Remaining': '0',
                }
                return jsonify(response), error.status_code, response_headers
            
            return jsonify(response), error.status_code
        
        @self.app.errorhandler(400)
        def handle_bad_request(error) -> tuple:
            """Handle 400 Bad Request."""
            return jsonify({
                "success": False,
                "message": "Bad request",
                "errors": {"error": str(error.description) if hasattr(error, 'description') else "Invalid request"},
            }), 400
        
        @self.app.errorhandler(401)
        def handle_unauthorized(error) -> tuple:
            """Handle 401 Unauthorized."""
            return jsonify({
                "success": False,
                "message": "Authentication required",
                "errors": None,
            }), 401
        
        @self.app.errorhandler(403)
        def handle_forbidden(error) -> tuple:
            """Handle 403 Forbidden."""
            return jsonify({
                "success": False,
                "message": "Access denied",
                "errors": None,
            }), 403
        
        @self.app.errorhandler(404)
        def handle_not_found(error) -> tuple:
            """Handle 404 Not Found."""
            return jsonify({
                "success": False,
                "message": "Resource not found",
                "errors": None,
            }), 404
        
        @self.app.errorhandler(405)
        def handle_method_not_allowed(error) -> tuple:
            """Handle 405 Method Not Allowed."""
            return jsonify({
                "success": False,
                "message": "Method not allowed",
                "errors": {"allowed_methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS"},
            }), 405
        
        @self.app.errorhandler(409)
        def handle_conflict(error) -> tuple:
            """Handle 409 Conflict."""
            return jsonify({
                "success": False,
                "message": "Resource conflict",
                "errors": None,
            }), 409
        
        @self.app.errorhandler(422)
        def handle_unprocessable_entity(error) -> tuple:
            """Handle 422 Unprocessable Entity."""
            errors = {}
            
            if hasattr(error, 'description') and isinstance(error.description, dict):
                errors = error.description
            elif hasattr(error, 'data') and isinstance(error.data, dict):
                errors = error.data
            
            return jsonify({
                "success": False,
                "message": "Validation failed",
                "errors": errors,
            }), 422
        
        @self.app.errorhandler(429)
        def handle_too_many_requests(error) -> tuple:
            """Handle 429 Too Many Requests."""
            retry_after = 60
            
            if hasattr(error, 'description'):
                retry_after = int(error.description) if error.description.isdigit() else 60
            
            return jsonify({
                "success": False,
                "message": f"Too many requests. Please try again in {retry_after} seconds.",
                "errors": {"retry_after": retry_after},
            }), 429, {'Retry-After': str(retry_after)}
        
        @self.app.errorhandler(500)
        def handle_internal_server_error(error) -> tuple:
            """Handle 500 Internal Server Error - log full traceback, return generic message."""
            logger.exception(f"Internal server error: {error}")
            
            return jsonify({
                "success": False,
                "message": "An internal error occurred. Please contact support.",
                "errors": None,
            }), 500
        
        @self.app.errorhandler(MarshmallowValidationError)
        def handle_marshmallow_validation_error(error: MarshmallowValidationError) -> tuple:
            """Handle Marshmallow validation errors."""
            return jsonify({
                "success": False,
                "message": "Validation failed",
                "errors": error.messages,
            }), 422
        
        @self.app.errorhandler(Exception)
        def handle_generic_exception(error: Exception) -> tuple:
            """Handle all other exceptions - log full traceback, return generic message."""
            if isinstance(error, ExamSaaSException):
                return handle_examsaas_exception(error)
            
            logger.exception(f"Unhandled exception: {error}")
            
            return jsonify({
                "success": False,
                "message": "An unexpected error occurred. Please contact support.",
                "errors": None,
            }), 500


def format_validation_errors(errors: dict) -> dict:
    """
    Format Marshmallow validation errors into API response format.
    
    Args:
        errors: Dictionary of field -> error messages
    
    Returns:
        Formatted errors dictionary
    """
    formatted = {}
    
    def flatten_errors(e, prefix=''):
        if isinstance(e, dict):
            for key, value in e.items():
                new_prefix = f"{prefix}.{key}" if prefix else key
                flatten_errors(value, new_prefix)
        elif isinstance(e, list):
            for item in e:
                flatten_errors(item, prefix)
        else:
            formatted[prefix] = str(e)
    
    flatten_errors(errors)
    return formatted


error_handler = ErrorHandler()
