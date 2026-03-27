"""
Request logger middleware for ExamSaaS platform.
Structured JSON logging for all HTTP requests/responses.
"""
import logging
import uuid
import time
import json
from datetime import datetime, timezone
from typing import Optional, Callable
from functools import wraps

from flask import Flask, request, g, Response

logger = logging.getLogger(__name__)


class RequestLogger:
    """
    Middleware for structured JSON request/response logging.
    
    Logs are output as JSON with the following structure:
    {
      "timestamp": "ISO8601",
      "level": "INFO",
      "module": "request_logger",
      "method": "POST",
      "path": "/api/v1/auth/login",
      "ip": "1.2.3.4",
      "user_agent": "...",
      "user_id": "...",          // from JWT if available
      "status_code": 200,
      "response_time_ms": 45,
      "request_id": "uuid4"      // attached to response header
    }
    """
    
    def __init__(self, app: Optional[Flask] = None):
        self.app = app
        self._excluded_paths = {
            '/health',
            '/favicon.ico',
            '/static/',
        }
        self._sensitive_paths = {
            '/api/v1/auth/login',
            '/api/v1/auth/register',
            '/api/v1/auth/forgot-password',
            '/api/v1/auth/reset-password',
        }
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask) -> None:
        """
        Initialize the middleware with Flask app.
        
        Args:
            app: Flask application instance
        """
        self.app = app
        
        @app.before_request
        def before_request():
            """Record request start time and generate request ID."""
            g.request_start_time = time.perf_counter()
            g.request_id = str(uuid.uuid4())
            g.request_logged = False
            
            if self._should_log_request():
                self._log_request_start()
        
        @app.after_request
        def after_request(response: Response) -> Response:
            """Log request completion and attach request ID header."""
            if hasattr(g, 'request_id'):
                response.headers['X-Request-ID'] = g.request_id
            
            if self._should_log_request() and not getattr(g, 'request_logged', False):
                self._log_request_complete(response)
            
            return response
        
        app.logger.info("RequestLogger middleware initialized")
    
    def _should_log_request(self) -> bool:
        """Check if the current request should be logged."""
        if request.path.startswith('/static/'):
            return False
        
        for excluded in self._excluded_paths:
            if request.path.startswith(excluded):
                return False
        
        return True
    
    def _get_user_id_from_token(self) -> Optional[str]:
        """Extract user_id from JWT token in Authorization header."""
        try:
            auth_header = request.headers.get('Authorization', '')
            
            if not auth_header.startswith('Bearer '):
                return None
            
            token = auth_header[7:]
            
            import jwt
            from flask import current_app
            
            jwt_secret = current_app.config.get('JWT_SECRET_KEY', 'dev-jwt-secret')
            
            payload = jwt.decode(
                token,
                jwt_secret,
                algorithms=['HS256'],
                options={'verify_exp': False}
            )
            
            return payload.get('user_id')
        
        except Exception:
            return None
    
    def _log_request_start(self) -> None:
        """Log the start of a request (without body)."""
        log_data = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'level': 'INFO',
            'module': 'request_logger',
            'event': 'request_start',
            'method': request.method,
            'path': request.path,
            'ip': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', '')[:200],
            'user_id': self._get_user_id_from_token(),
            'request_id': getattr(g, 'request_id', None),
        }
        
        logger.info(json.dumps(log_data))
    
    def _log_request_complete(self, response: Response) -> None:
        """Log the completion of a request."""
        try:
            start_time = getattr(g, 'request_start_time', None)
            
            if start_time:
                response_time_ms = (time.perf_counter() - start_time) * 1000
            else:
                response_time_ms = 0
            
            level = 'INFO'
            if response.status_code >= 500:
                level = 'ERROR'
            elif response.status_code >= 400:
                level = 'WARNING'
            
            log_data = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'level': level,
                'module': 'request_logger',
                'event': 'request_complete',
                'method': request.method,
                'path': request.path,
                'ip': request.remote_addr,
                'user_agent': request.headers.get('User-Agent', '')[:200],
                'user_id': getattr(g, 'current_user_id', self._get_user_id_from_token()),
                'status_code': response.status_code,
                'response_time_ms': round(response_time_ms, 2),
                'request_id': getattr(g, 'request_id', None),
                'content_length': response.content_length,
            }
            
            log_func = getattr(logger, level.lower())
            log_func(json.dumps(log_data))
            
            g.request_logged = True
        
        except Exception as e:
            logger.error(f"Failed to log request: {e}")


def get_request_id() -> Optional[str]:
    """Get the current request ID from Flask g object."""
    return getattr(g, 'request_id', None)


def log_audit_event(
    action: str,
    target_type: Optional[str] = None,
    target_id: Optional[str] = None,
    metadata: Optional[dict] = None
) -> None:
    """
    Log an audit event with structured data.
    
    Args:
        action: The action being performed
        target_type: Type of resource being acted upon
        target_id: ID of the resource
        metadata: Additional metadata
    """
    try:
        log_data = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'level': 'INFO',
            'module': 'audit',
            'event': action,
            'user_id': getattr(g, 'current_user_id', None),
            'user_role': getattr(g, 'current_role', None),
            'institute_id': str(getattr(g, 'current_institute_id', None) or ''),
            'target_type': target_type,
            'target_id': target_id,
            'ip': request.remote_addr if request else None,
            'request_id': getattr(g, 'request_id', None),
            'metadata': metadata or {},
        }
        
        logger.info(json.dumps(log_data))
    
    except Exception as e:
        logger.error(f"Failed to log audit event: {e}")


request_logger = RequestLogger()
