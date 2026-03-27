"""
Authentication routes for ExamSaaS platform.
Blueprint: /api/v1/auth
"""
import logging
from flask import Blueprint, request, g

from app.response import success_response, error_response
from app.schemas.auth_schemas import (
    register_schema,
    login_schema,
    google_auth_schema,
    verify_email_schema,
    forgot_password_schema,
    reset_password_schema,
    magic_link_verify_schema,
    update_profile_schema,
    refresh_token_schema,
    resend_otp_schema,
)
from app.services.auth_service import (
    register_user,
    verify_email,
    authenticate_user,
    authenticate_google,
    refresh_access_token,
    logout_user,
    request_password_reset,
    reset_password_with_otp,
    get_user_profile,
    update_user_profile,
    verify_magic_link,
    resend_otp,
    AuthServiceError,
    EmailExistsError,
    InvalidCredentialsError,
    AccountSuspendedError,
    EmailNotVerifiedError,
    InvalidTokenError,
    InvalidOtpError,
    UserNotFoundError,
    GoogleAuthError,
    InstituteSuspendedError,
)
from app.utils.decorators import require_auth

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def _handle_auth_error(error: AuthServiceError):
    """Handle authentication service errors."""
    return error_response(error.message, error.status_code)


def _validate_schema(schema, data):
    """Validate request data against schema."""
    try:
        return schema.load(data), None
    except Exception as e:
        errors = e.messages if hasattr(e, "messages") else str(e)
        return None, errors


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Register a new user.
    
    Input:
        - email: Valid email address
        - password: Min 8 chars with uppercase, lowercase, digit, special char
        - first_name: 2-50 alphabetic characters
        - last_name: Optional, 2-50 alphabetic characters
    
    Returns:
        201: {"message": "OTP sent to {email}"}
        409: Email already exists
        422: Validation error
    """
    data = request.get_json()
    
    if not data:
        return error_response("Request body is required", 400)
    
    validated, errors = _validate_schema(register_schema, data)
    
    if errors:
        return error_response("Validation error", 422, errors)
    
    try:
        user_id, masked_email = register_user(
            email=validated["email"],
            password=validated["password"],
            first_name=validated["first_name"],
            last_name=validated.get("last_name"),
        )
        
        return success_response(
            {"user_id": user_id},
            f"OTP sent to {masked_email}",
            status=201
        )
    
    except EmailExistsError as e:
        return _handle_auth_error(e)
    except AuthServiceError as e:
        return _handle_auth_error(e)
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        return error_response("Registration failed", 500)


@auth_bp.route("/verify-email", methods=["POST"])
def verify_email_route():
    """
    Verify email with OTP.
    
    Input:
        - email: User's email address
        - otp: 6-digit OTP
    
    Returns:
        200: {"message": "Email verified successfully"}
        400: Invalid or expired OTP
        404: User not found
    """
    data = request.get_json()
    
    if not data:
        return error_response("Request body is required", 400)
    
    validated, errors = _validate_schema(verify_email_schema, data)
    
    if errors:
        return error_response("Validation error", 422, errors)
    
    try:
        verify_email(
            email=validated["email"],
            otp=validated["otp"],
        )
        
        return success_response(None, "Email verified successfully")
    
    except InvalidOtpError as e:
        return _handle_auth_error(e)
    except UserNotFoundError as e:
        return _handle_auth_error(e)
    except AuthServiceError as e:
        return _handle_auth_error(e)
    except Exception as e:
        logger.error(f"Email verification failed: {e}")
        return error_response("Verification failed", 500)


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Authenticate user and return tokens.
    
    Input:
        - email: User's email address
        - password: User's password
        - role_hint: Optional role hint
    
    Returns:
        200: Full login response with tokens and user info
        401: Invalid credentials
        403: Account suspended or email not verified
        423: Institute suspended
    """
    data = request.get_json()
    
    if not data:
        return error_response("Request body is required", 400)
    
    validated, errors = _validate_schema(login_schema, data)
    
    if errors:
        return error_response("Validation error", 422, errors)
    
    try:
        result = authenticate_user(
            email=validated["email"],
            password=validated["password"],
            role_hint=validated.get("role_hint"),
        )
        
        return success_response(result, "Login successful")
    
    except InvalidCredentialsError as e:
        return _handle_auth_error(e)
    except AccountSuspendedError as e:
        return _handle_auth_error(e)
    except EmailNotVerifiedError as e:
        return _handle_auth_error(e)
    except InstituteSuspendedError as e:
        return _handle_auth_error(e)
    except AuthServiceError as e:
        return _handle_auth_error(e)
    except Exception as e:
        logger.error(f"Login failed: {e}")
        return error_response("Login failed", 500)


@auth_bp.route("/google", methods=["POST"])
def google_auth():
    """
    Authenticate with Google OAuth.
    
    Input:
        - id_token: Google ID token
        - role_hint: Optional role hint
    
    Returns:
        200: Full login response with tokens and user info
        401: Invalid token or authentication failed
        403: Account suspended
    """
    data = request.get_json()
    
    if not data:
        return error_response("Request body is required", 400)
    
    validated, errors = _validate_schema(google_auth_schema, data)
    
    if errors:
        return error_response("Validation error", 422, errors)
    
    try:
        result = authenticate_google(
            id_token=validated["id_token"],
            role_hint=validated.get("role_hint"),
        )
        
        return success_response(result, "Login successful")
    
    except GoogleAuthError as e:
        return _handle_auth_error(e)
    except AccountSuspendedError as e:
        return _handle_auth_error(e)
    except InstituteSuspendedError as e:
        return _handle_auth_error(e)
    except AuthServiceError as e:
        return _handle_auth_error(e)
    except Exception as e:
        logger.error(f"Google auth failed: {e}")
        return error_response("Google authentication failed", 500)


@auth_bp.route("/refresh", methods=["POST"])
def refresh():
    """
    Refresh access token.
    
    Input:
        - refresh_token: Valid refresh token
    
    Returns:
        200: New access and refresh tokens
        401: Invalid or expired token
    """
    data = request.get_json()
    
    if not data:
        return error_response("Request body is required", 400)
    
    validated, errors = _validate_schema(refresh_token_schema, data)
    
    if errors:
        return error_response("Validation error", 422, errors)
    
    try:
        result = refresh_access_token(validated["refresh_token"])
        
        return success_response(result, "Token refreshed successfully")
    
    except InvalidTokenError as e:
        return _handle_auth_error(e)
    except AuthServiceError as e:
        return _handle_auth_error(e)
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        return error_response("Token refresh failed", 500)


@auth_bp.route("/logout", methods=["POST"])
@require_auth
def logout():
    """
    Logout user.
    
    Headers:
        - Authorization: Bearer {access_token}
    
    Returns:
        200: {"message": "Logged out successfully"}
    """
    try:
        auth_header = request.headers.get("Authorization", "")
        token = auth_header[7:] if auth_header.startswith("Bearer ") else ""
        logout_user(token)
        
        return success_response(None, "Logged out successfully")
    
    except Exception as e:
        logger.error(f"Logout failed: {e}")
        return success_response(None, "Logged out successfully")


@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    """
    Request password reset OTP.
    
    Input:
        - email: User's email address
    
    Returns:
        200: {"message": "If that email exists, an OTP has been sent"}
    """
    data = request.get_json()
    
    if not data:
        return error_response("Request body is required", 400)
    
    validated, errors = _validate_schema(forgot_password_schema, data)
    
    if errors:
        return error_response("Validation error", 422, errors)
    
    try:
        request_password_reset(validated["email"])
        
        return success_response(
            None,
            "If that email exists, an OTP has been sent"
        )
    
    except Exception as e:
        logger.error(f"Forgot password failed: {e}")
        return success_response(
            None,
            "If that email exists, an OTP has been sent"
        )


@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    """
    Reset password with OTP.
    
    Input:
        - email: User's email address
        - otp: 6-digit OTP
        - new_password: New password meeting strength requirements
    
    Returns:
        200: {"message": "Password reset successfully"}
        400: Invalid or expired OTP
        404: User not found
    """
    data = request.get_json()
    
    if not data:
        return error_response("Request body is required", 400)
    
    validated, errors = _validate_schema(reset_password_schema, data)
    
    if errors:
        return error_response("Validation error", 422, errors)
    
    try:
        reset_password_with_otp(
            email=validated["email"],
            otp=validated["otp"],
            new_password=validated["new_password"],
        )
        
        return success_response(None, "Password reset successfully")
    
    except InvalidOtpError as e:
        return _handle_auth_error(e)
    except UserNotFoundError as e:
        return _handle_auth_error(e)
    except AuthServiceError as e:
        return _handle_auth_error(e)
    except Exception as e:
        logger.error(f"Password reset failed: {e}")
        return error_response("Password reset failed", 500)


@auth_bp.route("/me", methods=["GET"])
@require_auth
def get_me():
    """
    Get current user profile.
    
    Headers:
        - Authorization: Bearer {access_token}
    
    Returns:
        200: Full user profile with institute details
        401: Unauthorized
        404: User not found
    """
    try:
        profile = get_user_profile(g.current_user_id)
        
        return success_response(profile)
    
    except UserNotFoundError as e:
        return _handle_auth_error(e)
    except AuthServiceError as e:
        return _handle_auth_error(e)
    except Exception as e:
        logger.error(f"Get profile failed: {e}")
        return error_response("Failed to get profile", 500)


@auth_bp.route("/me", methods=["PATCH"])
@require_auth
def update_me():
    """
    Update current user profile.
    
    Headers:
        - Authorization: Bearer {access_token}
    
    Input:
        - first_name: New first name (optional)
        - last_name: New last name (optional)
        - phone: New phone (optional)
        - avatar_url: New avatar URL (optional)
    
    Returns:
        200: Updated user profile
        401: Unauthorized
        404: User not found
    """
    data = request.get_json()
    
    if not data:
        return error_response("Request body is required", 400)
    
    validated, errors = _validate_schema(update_profile_schema, data)
    
    if errors:
        return error_response("Validation error", 422, errors)
    
    try:
        profile = update_user_profile(
            user_id=g.current_user_id,
            first_name=validated.get("first_name"),
            last_name=validated.get("last_name"),
            phone=validated.get("phone"),
            avatar_url=validated.get("avatar_url"),
        )
        
        return success_response(profile, "Profile updated successfully")
    
    except UserNotFoundError as e:
        return _handle_auth_error(e)
    except AuthServiceError as e:
        return _handle_auth_error(e)
    except Exception as e:
        logger.error(f"Update profile failed: {e}")
        return error_response("Failed to update profile", 500)


@auth_bp.route("/magic-link/verify", methods=["POST"])
def verify_magic():
    """
    Verify magic link and get access token.
    
    Input:
        - token: Magic link token
    
    Returns:
        200: Access token with exam info
        401: Invalid or expired token
    """
    data = request.get_json()
    
    if not data:
        return error_response("Request body is required", 400)
    
    validated, errors = _validate_schema(magic_link_verify_schema, data)
    
    if errors:
        return error_response("Validation error", 422, errors)
    
    try:
        result = verify_magic_link(validated["token"])
        
        return success_response(result, "Magic link verified")
    
    except InvalidTokenError as e:
        return _handle_auth_error(e)
    except UserNotFoundError as e:
        return _handle_auth_error(e)
    except AuthServiceError as e:
        return _handle_auth_error(e)
    except Exception as e:
        logger.error(f"Magic link verification failed: {e}")
        return error_response("Magic link verification failed", 500)


@auth_bp.route("/resend-otp", methods=["POST"])
def resend_otp_route():
    """
    Resend OTP to email.
    
    Input:
        - email: User's email address
        - purpose: OTP purpose (verify_email or forgot_password)
    
    Returns:
        200: {"message": "OTP sent successfully"}
        404: User not found (for verify_email)
    """
    data = request.get_json()
    
    if not data:
        return error_response("Request body is required", 400)
    
    validated, errors = _validate_schema(resend_otp_schema, data)
    
    if errors:
        return error_response("Validation error", 422, errors)
    
    try:
        resend_otp(
            email=validated["email"],
            purpose=validated["purpose"],
        )
        
        return success_response(None, "OTP sent successfully")
    
    except UserNotFoundError as e:
        return _handle_auth_error(e)
    except AuthServiceError as e:
        return _handle_auth_error(e)
    except Exception as e:
        logger.error(f"Resend OTP failed: {e}")
        return error_response("Failed to send OTP", 500)
