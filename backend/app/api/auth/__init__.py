"""
Authentication routes for ExamSaaS platform.
"""
import logging
import re
from datetime import datetime
from flask import Blueprint, request, current_app
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    get_jwt_identity, get_jwt
)

from app.models import User, Wallet, AuditLog
from app.extensions import sanitize_input
from app.response import success_response, error_response
from app.auth_helpers import (
    generate_tokens, decode_token, generate_verification_token,
    generate_password_reset_token, get_token_expiry
)
from app.constants import AuditAction

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password(password: str) -> Tuple[bool, str]:
    """Validate password strength."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    return True, ""


def create_audit_log(user: User, action: str, details: dict = None):
    """Create audit log entry."""
    try:
        AuditLog(
            user=user.id,
            action=action,
            details=details or {},
            ip_address=request.remote_addr,
            user_agent=request.headers.get("User-Agent", "")[:500],
        ).save()
    except Exception as e:
        logger.warning(f"Failed to create audit log: {e}")


def send_verification_email(user: User, token: str):
    """Send email verification email via Celery task."""
    try:
        from app.tasks.email_tasks import send_email_task
        verify_url = f"{current_app.config['APP_URL']}/auth/verify-email/{token}"
        send_email_task.delay(
            to_email=user.email,
            subject="Verify your ExamSaaS account",
            template="verify_email",
            context={
                "user": user,
                "verify_url": verify_url,
                "first_name": user.first_name,
            }
        )
    except Exception as e:
        logger.warning(f"Failed to queue verification email: {e}")


def send_password_reset_email(user: User, token: str):
    """Send password reset email via Celery task."""
    try:
        from app.tasks.email_tasks import send_email_task
        reset_url = f"{current_app.config['APP_URL']}/auth/reset-password/{token}"
        send_email_task.delay(
            to_email=user.email,
            subject="Reset your ExamSaaS password",
            template="password_reset",
            context={
                "user": user,
                "reset_url": reset_url,
                "first_name": user.first_name,
            }
        )
    except Exception as e:
        logger.warning(f"Failed to queue password reset email: {e}")


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Register a new user account.
    
    Request body:
        - email: User's email address
        - password: User's password (min 8 chars, upper, lower, number)
        - first_name: User's first name
        - last_name: User's last name (optional)
        - institute_id: Institute ID for assigned students (optional)
    
    Returns:
        User data with tokens on success
    """
    data = request.get_json()
    
    if not data:
        return error_response("Request body is required", 400)
    
    email = sanitize_input(data.get("email", "")).lower().strip()
    password = data.get("password", "")
    first_name = sanitize_input(data.get("first_name", "")).strip()
    last_name = sanitize_input(data.get("last_name", "")).strip()
    institute_id = data.get("institute_id")
    
    if not email or not password or not first_name:
        return error_response("Email, password, and first name are required", 400)
    
    if not validate_email(email):
        return error_response("Invalid email format", 400)
    
    valid, msg = validate_password(password)
    if not valid:
        return error_response(msg, 400)
    
    if User.objects(email=email).first():
        return error_response("An account with this email already exists", 409)
    
    role = "student_registered"
    
    try:
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role,
            is_email_verified=False,
            auth_provider="local",
        )
        user.set_password(password)
        user.save()
        
        wallet = Wallet(user=user.id, balance=0)
        wallet.save()
        user.wallet = wallet
        user.save()
        
        token = generate_verification_token(str(user.id))
        send_verification_email(user, token)
        
        jwt_config = current_app.config
        tokens = generate_tokens(
            user_id=str(user.id),
            role=role,
            jwt_secret=jwt_config["JWT_SECRET_KEY"],
            access_expires=jwt_config.get("JWT_ACCESS_TOKEN_EXPIRES", 3600),
            refresh_expires=jwt_config.get("JWT_REFRESH_TOKEN_EXPIRES", 2592000),
        )
        
        create_audit_log(user, AuditAction.CREATE.value, {"method": "register"})
        
        logger.info(f"New user registered: {email}")
        
        return success_response({
            "user": user.to_dict(),
            **tokens,
        }, "Registration successful. Please check your email to verify your account.", 201)
    
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        return error_response("Registration failed. Please try again.", 500)


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Authenticate user and return tokens.
    
    Request body:
        - email: User's email address
        - password: User's password
    
    Returns:
        User data with access and refresh tokens
    """
    data = request.get_json()
    
    if not data:
        return error_response("Request body is required", 400)
    
    email = data.get("email", "").lower().strip()
    password = data.get("password", "")
    
    if not email or not password:
        return error_response("Email and password are required", 400)
    
    user = User.objects(email=email).first()
    
    if not user:
        return error_response("Invalid email or password", 401)
    
    if not user.is_active:
        return error_response("Your account has been deactivated. Contact support.", 403)
    
    if not user.check_password(password):
        return error_response("Invalid email or password", 401)
    
    user.last_login_at = datetime.utcnow()
    user.save()
    
    jwt_config = current_app.config
    tokens = generate_tokens(
        user_id=str(user.id),
        role=user.role,
        jwt_secret=jwt_config["JWT_SECRET_KEY"],
        access_expires=jwt_config.get("JWT_ACCESS_TOKEN_EXPIRES", 3600),
        refresh_expires=jwt_config.get("JWT_REFRESH_TOKEN_EXPIRES", 2592000),
    )
    
    create_audit_log(user, AuditAction.LOGIN.value)
    
    logger.info(f"User logged in: {email}")
    
    return success_response({
        "user": user.to_dict(include_sensitive=True),
        **tokens,
    }, "Login successful")


@auth_bp.route("/refresh", methods=["POST"])
def refresh():
    """
    Refresh access token using refresh token.
    
    Request body:
        - refresh_token: Valid refresh token
    
    Returns:
        New access and refresh tokens
    """
    data = request.get_json()
    refresh_token = data.get("refresh_token") if data else None
    
    if not refresh_token:
        return error_response("Refresh token is required", 400)
    
    jwt_config = current_app.config
    payload, error = decode_token(refresh_token, jwt_config["JWT_SECRET_KEY"])
    
    if error:
        return error_response(error, 401)
    
    if payload.get("type") != "refresh":
        return error_response("Invalid token type", 401)
    
    user = User.objects(id=payload["sub"]).first()
    
    if not user or not user.is_active:
        return error_response("User not found or inactive", 401)
    
    tokens = generate_tokens(
        user_id=str(user.id),
        role=user.role,
        jwt_secret=jwt_config["JWT_SECRET_KEY"],
        access_expires=jwt_config.get("JWT_ACCESS_TOKEN_EXPIRES", 3600),
        refresh_expires=jwt_config.get("JWT_REFRESH_TOKEN_EXPIRES", 2592000),
    )
    
    logger.info(f"Token refreshed for user: {user.email}")
    
    return success_response(tokens, "Token refreshed successfully")


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """
    Logout user (client should discard tokens).
    
    Returns:
        Success message
    """
    identity = get_jwt_identity()
    
    if identity:
        user = User.objects(id=identity).first()
        if user:
            create_audit_log(user, AuditAction.LOGOUT.value)
            logger.info(f"User logged out: {user.email}")
    
    return success_response(None, "Logged out successfully")


@auth_bp.route("/verify-email/<token>", methods=["POST"])
def verify_email(token: str):
    """
    Verify user email with token.
    
    Args:
        token: Email verification token
    
    Returns:
        Success message
    """
    users = User.objects(is_email_verified=False)
    
    for user in users:
        expected_token = generate_verification_token(str(user.id))
        if expected_token == token or _tokens_match(token, str(user.id)):
            user.is_email_verified = True
            user.save()
            create_audit_log(user, "verify_email")
            logger.info(f"Email verified for user: {user.email}")
            return success_response(None, "Email verified successfully")
    
    return error_response("Invalid or expired verification token", 400)


def _tokens_match(input_token: str, user_id: str, max_age_days: int = 7) -> bool:
    """Check if token matches user (simplified check)."""
    import hashlib
    import time
    
    for i in range(max_age_days * 24 * 60):
        timestamp = time.time() - (i * 60)
        data = f"{user_id}:{datetime.fromtimestamp(timestamp).isoformat()}:"
        data = hashlib.sha256(data.encode()).hexdigest()[:64]
        if data == input_token[:64]:
            return True
    return False


@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    """
    Send password reset email.
    
    Request body:
        - email: User's email address
    
    Returns:
        Success message
    """
    data = request.get_json()
    email = data.get("email", "").lower().strip() if data else ""
    
    if not email:
        return error_response("Email is required", 400)
    
    user = User.objects(email=email).first()
    
    if user and user.auth_provider == "local":
        token = generate_password_reset_token(str(user.id), user.email)
        send_password_reset_email(user, token)
        create_audit_log(user, "password_reset_requested")
        logger.info(f"Password reset requested for: {email}")
    
    return success_response(
        None, 
        "If an account exists with this email, you will receive password reset instructions."
    )


@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    """
    Reset password with token.
    
    Request body:
        - token: Password reset token
        - user_id: User ID
        - email: User email
        - new_password: New password
    
    Returns:
        Success message
    """
    data = request.get_json()
    
    if not data:
        return error_response("Request body is required", 400)
    
    token = data.get("token", "")
    user_id = data.get("user_id", "")
    email = data.get("email", "").lower().strip()
    new_password = data.get("new_password", "")
    
    if not all([token, user_id, email, new_password]):
        return error_response("Token, user_id, email, and new_password are required", 400)
    
    valid, msg = validate_password(new_password)
    if not valid:
        return error_response(msg, 400)
    
    user = User.objects(id=user_id, email=email).first()
    
    if not user:
        return error_response("Invalid reset request", 400)
    
    if user.check_password(new_password):
        return error_response("New password must be different from current password", 400)
    
    user.set_password(new_password)
    user.save()
    
    create_audit_log(user, "password_reset")
    logger.info(f"Password reset for user: {email}")
    
    return success_response(None, "Password reset successfully. Please login with your new password.")


@auth_bp.route("/me", methods=["GET"])
def get_current_user():
    """
    Get current authenticated user.
    
    Returns:
        Current user data
    """
    identity = get_jwt_identity()
    
    if not identity:
        return error_response("Unauthorized", 401)
    
    user = User.objects(id=identity).first()
    
    if not user or not user.is_active:
        return error_response("User not found or inactive", 401)
    
    return success_response(user.to_dict(include_sensitive=True))


@auth_bp.route("/change-password", methods=["POST"])
def change_password():
    """
    Change password for authenticated user.
    
    Request body:
        - current_password: Current password
        - new_password: New password
    
    Returns:
        Success message
    """
    identity = get_jwt_identity()
    
    if not identity:
        return error_response("Unauthorized", 401)
    
    user = User.objects(id=identity).first()
    
    if not user:
        return error_response("User not found", 401)
    
    if user.auth_provider != "local":
        return error_response("Password change not available for OAuth accounts", 400)
    
    data = request.get_json()
    
    if not data:
        return error_response("Request body is required", 400)
    
    current_password = data.get("current_password", "")
    new_password = data.get("new_password", "")
    
    if not user.check_password(current_password):
        return error_response("Current password is incorrect", 400)
    
    valid, msg = validate_password(new_password)
    if not valid:
        return error_response(msg, 400)
    
    user.set_password(new_password)
    user.save()
    
    create_audit_log(user, "password_changed")
    logger.info(f"Password changed for user: {user.email}")
    
    return success_response(None, "Password changed successfully")


from typing import Tuple

__all__ = ["auth_bp"]
