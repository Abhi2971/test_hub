"""
Decorator utilities for ExamSaaS platform.
Contains authentication, authorization, and audit decorators.
"""
import logging
from functools import wraps
from typing import List, Callable, Optional, Any

from flask import request, g, jsonify
import jwt

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
            return None
    return REDIS_CLIENT


def _blacklist_check(jti: str) -> bool:
    """
    Check if a token JTI is blacklisted.
    
    Args:
        jti: JWT ID to check
    
    Returns:
        True if blacklisted, False otherwise
    """
    redis = _get_redis()
    if redis is None:
        return False
    
    try:
        return redis.exists(f"blacklist:{jti}") > 0
    except Exception as e:
        logger.error(f"Redis error during blacklist check: {e}")
        return False


def _session_check(user_id: str, jti: str) -> bool:
    """
    Check if session is valid for user.
    
    Args:
        user_id: User ID
        jti: JWT ID to verify
    
    Returns:
        True if session valid, False otherwise
    """
    redis = _get_redis()
    if redis is None:
        return True
    
    try:
        stored_jti = redis.get(f"session:{user_id}")
        if stored_jti is None:
            return True
        return stored_jti == jti
    except Exception as e:
        logger.error(f"Redis error during session check: {e}")
        return True


def require_roles(*allowed_roles: str) -> Callable:
    """
    Decorator to require specific roles for access.
    
    Usage:
        @app.route("/admin-only")
        @require_roles("super_admin", "admin_public")
        def admin_only():
            return "Admin access granted"
    
    Args:
        *allowed_roles: Role names that are allowed access
    
    Returns:
        Decorated function
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args, **kwargs) -> Any:
            from app.response import error_response
            
            auth_header = request.headers.get("Authorization", "")
            
            if not auth_header.startswith("Bearer "):
                return error_response("Missing or invalid Authorization header", 401)
            
            token = auth_header[7:]
            
            try:
                jwt_secret = _get_jwt_secret()
                
                payload = jwt.decode(
                    token,
                    jwt_secret,
                    algorithms=["HS256"]
                )
            except jwt.ExpiredSignatureError:
                return error_response("Token has expired", 401)
            except jwt.InvalidTokenError as e:
                logger.warning(f"Invalid token: {e}")
                return error_response("Invalid token", 401)
            
            jti = payload.get("jti")
            user_id = payload.get("user_id")
            user_role = payload.get("role")
            
            if not all([jti, user_id, user_role]):
                return error_response("Invalid token payload", 401)
            
            if _blacklist_check(jti):
                return error_response("Token has been revoked", 401)
            
            if not _session_check(user_id, jti):
                return error_response("Session invalidated", 401)
            
            if user_role not in allowed_roles:
                logger.warning(
                    f"Access denied for user {user_id} with role {user_role}: "
                    f"required roles {allowed_roles}"
                )
                return error_response("Access denied. Insufficient permissions.", 403)
            
            g.current_user_id = user_id
            g.current_role = user_role
            g.current_institute_id = payload.get("institute_id")
            g.current_email = payload.get("email")
            g.current_jti = jti
            
            return f(*args, **kwargs)
        
        return decorated
    return decorator


def require_auth(f: Callable) -> Callable:
    """
    Decorator to require authentication (any valid token).
    
    Usage:
        @app.route("/protected")
        @require_auth
        def protected():
            user_id = g.current_user_id
            return f"Hello, {user_id}"
    
    Args:
        f: Function to decorate
    
    Returns:
        Decorated function
    """
    @wraps(f)
    def decorated(*args, **kwargs) -> Any:
        from app.response import error_response
        
        auth_header = request.headers.get("Authorization", "")
        
        if not auth_header.startswith("Bearer "):
            return error_response("Missing or invalid Authorization header", 401)
        
        token = auth_header[7:]
        
        try:
            jwt_secret = _get_jwt_secret()
            
            payload = jwt.decode(
                token,
                jwt_secret,
                algorithms=["HS256"]
            )
        except jwt.ExpiredSignatureError:
            return error_response("Token has expired", 401)
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return error_response("Invalid token", 401)
        
        jti = payload.get("jti")
        user_id = payload.get("user_id")
        
        if not all([jti, user_id]):
            return error_response("Invalid token payload", 401)
        
        if _blacklist_check(jti):
            return error_response("Token has been revoked", 401)
        
        if not _session_check(user_id, jti):
            return error_response("Session invalidated", 401)
        
        g.current_user_id = user_id
        g.current_role = payload.get("role")
        g.current_institute_id = payload.get("institute_id")
        g.current_email = payload.get("email")
        g.current_jti = jti
        
        return f(*args, **kwargs)
    
    return decorated


def require_verified_email(f: Callable) -> Callable:
    """
    Decorator to require email verification.
    Must be used after @require_auth.
    
    Usage:
        @app.route("/verified-only")
        @require_auth
        @require_verified_email
        def verified_only():
            return "Email verified"
    
    Args:
        f: Function to decorate
    
    Returns:
        Decorated function
    """
    @wraps(f)
    def decorated(*args, **kwargs) -> Any:
        from app.response import error_response
        
        if not hasattr(g, "current_user_id"):
            return error_response("Authentication required", 401)
        
        try:
            from app.models import User
            user = User.objects(id=g.current_user_id).first()
            
            if not user:
                return error_response("User not found", 404)
            
            if not user.is_email_verified:
                return error_response("Email verification required", 403)
            
        except Exception as e:
            logger.error(f"Error checking email verification: {e}")
            return error_response("Error verifying email status", 500)
        
        return f(*args, **kwargs)
    
    return decorated


def require_active_account(f: Callable) -> Callable:
    """
    Decorator to require an active user account.
    Must be used after @require_auth.
    
    Usage:
        @app.route("/active-only")
        @require_auth
        @require_active_account
        def active_only():
            return "Account is active"
    
    Args:
        f: Function to decorate
    
    Returns:
        Decorated function
    """
    @wraps(f)
    def decorated(*args, **kwargs) -> Any:
        from app.response import error_response
        
        if not hasattr(g, "current_user_id"):
            return error_response("Authentication required", 401)
        
        try:
            from app.models import User
            user = User.objects(id=g.current_user_id).first()
            
            if not user:
                return error_response("User not found", 404)
            
            if not user.is_active:
                return error_response("Account has been deactivated", 403)
            
        except Exception as e:
            logger.error(f"Error checking account status: {e}")
            return error_response("Error verifying account status", 500)
        
        return f(*args, **kwargs)
    
    return decorated


def rate_limit(max_requests: int, window_seconds: int) -> Callable:
    """
    Decorator to rate limit requests.
    
    Usage:
        @app.route("/limited")
        @rate_limit(max_requests=5, window_seconds=60)
        def limited():
            return "Limited endpoint"
    
    Args:
        max_requests: Maximum requests allowed in window
        window_seconds: Time window in seconds
    
    Returns:
        Decorated function
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args, **kwargs) -> Any:
            from app.response import error_response
            
            redis = _get_redis()
            
            if redis is None:
                logger.warning("Rate limiting skipped: Redis not available")
                return f(*args, **kwargs)
            
            client_ip = request.remote_addr
            key = f"ratelimit:{client_ip}:{request.endpoint}"
            
            try:
                current = redis.get(key)
                
                if current is None:
                    redis.setex(key, window_seconds, 1)
                elif int(current) >= max_requests:
                    return error_response(
                        "Rate limit exceeded. Please try again later.",
                        429,
                        {"retry_after": window_seconds}
                    )
                else:
                    redis.incr(key)
            
            except Exception as e:
                logger.error(f"Rate limiting error: {e}")
                return f(*args, **kwargs)
            
            return f(*args, **kwargs)
        
        return decorated
    return decorator


def _get_jwt_secret() -> str:
    """
    Get JWT secret from Flask config.
    
    Returns:
        JWT secret key
    """
    try:
        from flask import current_app
        return current_app.config.get("JWT_SECRET_KEY", "dev-jwt-secret-change-in-production")
    except RuntimeError:
        return "dev-jwt-secret-change-in-production"


def get_current_user_id() -> Optional[str]:
    """
    Get current user ID from Flask g object.
    
    Returns:
        User ID or None
    """
    return getattr(g, "current_user_id", None)


def get_current_role() -> Optional[str]:
    """
    Get current user role from Flask g object.
    
    Returns:
        Role or None
    """
    return getattr(g, "current_role", None)


def get_current_institute_id() -> Optional[str]:
    """
    Get current institute ID from Flask g object.
    
    Returns:
        Institute ID or None
    """
    return getattr(g, "current_institute_id", None)


def require_institute(f: Callable) -> Callable:
    """
    Decorator to require institute context.
    Must be used after @require_auth or @require_roles.
    
    Usage:
        @app.route("/institute-data")
        @require_roles("teacher")
        @require_institute
        def get_institute_data():
            institute = g.current_institute
            return jsonify({"name": institute.name})
    
    Args:
        f: Function to decorate
    
    Returns:
        Decorated function
    """
    @wraps(f)
    def decorated(*args, **kwargs) -> Any:
        from app.exceptions import NotFoundError
        
        if not hasattr(g, "current_institute"):
            raise NotFoundError("Institute context required")
        
        if g.current_institute is None:
            raise NotFoundError("Institute not found")
        
        return f(*args, **kwargs)
    
    return decorated


def require_permission(*actions: str) -> Callable:
    """
    Decorator to require specific permissions.
    Must be used after @require_auth or @require_roles.
    
    Usage:
        @app.route("/create-exam")
        @require_roles("teacher")
        @require_permission("exam:create")
        def create_exam():
            return "Exam created"
    
    Args:
        *actions: Permission actions required
    
    Returns:
        Decorated function
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args, **kwargs) -> Any:
            from app.exceptions import AuthorizationError
            from app.utils.rbac import has_permission
            
            role = getattr(g, "current_role", None)
            
            if not role:
                raise AuthorizationError("Authentication required")
            
            if not all(has_permission(role, action) for action in actions):
                raise AuthorizationError(
                    "Access denied. Insufficient permissions."
                )
            
            return f(*args, **kwargs)
        
        return decorated
    return decorator


def audit_log(action: str, target_type: str = None) -> Callable:
    """
    Decorator to create audit log for sensitive actions.
    
    Usage:
        @app.route("/force-submit")
        @require_roles("teacher")
        @audit_log(action="force_submit_attempt", target_type="ExamAttempt")
        def force_submit():
            return "Attempt force submitted"
    
    Args:
        action: Action being performed
        target_type: Type of resource being acted upon
    
    Returns:
        Decorated function
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args, **kwargs) -> Any:
            result = f(*args, **kwargs)
            
            try:
                _create_audit_log(
                    action=action,
                    target_type=target_type,
                    target_id=_extract_target_id_from_result(result),
                    kwargs=kwargs,
                    result=result,
                )
            except Exception as e:
                logger.error(f"Failed to create audit log: {e}")
            
            return result
        
        return decorated
    return decorator


def _extract_target_id_from_result(result: Any) -> Optional[str]:
    """Extract target ID from function result."""
    if result is None:
        return None
    
    if hasattr(result, 'id'):
        return str(result.id)
    
    if isinstance(result, dict):
        return result.get('id') or result.get('data', {}).get('id')
    
    if isinstance(result, tuple):
        first = result[0]
        if hasattr(first, 'id'):
            return str(first.id)
        if isinstance(first, dict):
            return first.get('id')
    
    return None


def _create_audit_log(
    action: str,
    target_type: Optional[str] = None,
    target_id: Optional[str] = None,
    kwargs: Optional[dict] = None,
    result: Any = None
) -> None:
    """
    Create an audit log entry asynchronously.
    
    Args:
        action: The action being performed
        target_type: Type of resource
        target_id: ID of the resource
        kwargs: Function kwargs
        result: Function result
    """
    try:
        from app.models import AuditLog
        from datetime import datetime, timezone
        
        user_id = getattr(g, "current_user_id", None)
        user_role = getattr(g, "current_role", None)
        institute_id = getattr(g, "current_institute_id", None)
        
        metadata = {
            "endpoint": request.endpoint if request else None,
            "method": request.method if request else None,
            "path": request.path if request else None,
        }
        
        if target_id is None and kwargs:
            target_id = kwargs.get("id") or kwargs.get("attempt_id") or kwargs.get("user_id")
        
        if result is not None:
            if hasattr(result, "id"):
                target_id = str(result.id)
            elif isinstance(result, dict) and "id" in result:
                target_id = result["id"]
        
        try:
            audit_log = AuditLog(
                user=user_id,
                action=action,
                target_type=target_type,
                target_id=target_id,
                institute=getattr(g, "current_institute", None),
                ip_address=request.remote_addr if request else None,
                user_agent=str(request.headers.get("User-Agent", ""))[:500] if request else "",
                details=metadata,
            )
            audit_log.save()
        except Exception as e:
            logger.error(f"Failed to save audit log to DB: {e}")
            _queue_audit_log(
                user_id=user_id,
                action=action,
                target_type=target_type,
                target_id=target_id,
                user_role=user_role,
                institute_id=institute_id,
                metadata=metadata,
            )
    
    except Exception as e:
        logger.error(f"Error creating audit log: {e}")


def _queue_audit_log(
    user_id: Optional[str],
    action: str,
    target_type: Optional[str],
    target_id: Optional[str],
    user_role: Optional[str],
    institute_id: Optional[str],
    metadata: dict
) -> None:
    """Queue audit log for async creation."""
    try:
        from app.tasks.email_tasks import send_email_task
        
        logger.info(
            f"AUDIT: user={user_id}, action={action}, "
            f"target_type={target_type}, target_id={target_id}"
        )
    except Exception:
        pass
