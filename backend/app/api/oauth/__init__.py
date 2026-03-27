"""
Google OAuth routes for ExamSaaS platform.
"""
import logging
import secrets
from datetime import datetime
from flask import Blueprint, request, current_app
from flask_jwt_extended import get_jwt_identity

from app.models import User, Wallet, AuditLog
from app.response import success_response, error_response
from app.auth_helpers import generate_tokens
from app.constants import AuditAction

logger = logging.getLogger(__name__)

oauth_bp = Blueprint("oauth", __name__, url_prefix="/oauth/google")


def get_google_provider_config():
    """Get Google OAuth provider configuration."""
    return {
        "client_id": current_app.config.get("GOOGLE_CLIENT_ID"),
        "redirect_uri": f"{current_app.config.get('API_URL')}/api/oauth/google/callback",
        "scope": "openid email profile",
        "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "userinfo_url": "https://www.googleapis.com/oauth2/v3/userinfo",
    }


def exchange_code_for_tokens(code: str) -> dict:
    """Exchange authorization code for tokens."""
    import requests
    
    config = get_google_provider_config()
    
    response = requests.post(
        config["token_url"],
        data={
            "code": code,
            "client_id": config["client_id"],
            "client_secret": current_app.config.get("GOOGLE_CLIENT_SECRET"),
            "redirect_uri": config["redirect_uri"],
            "grant_type": "authorization_code",
        },
        headers={"Accept": "application/json"},
    )
    
    if response.status_code != 200:
        logger.error(f"Token exchange failed: {response.text}")
        return None
    
    return response.json()


def get_google_user_info(access_token: str) -> dict:
    """Get user info from Google."""
    import requests
    
    config = get_google_provider_config()
    
    response = requests.get(
        config["userinfo_url"],
        headers={"Authorization": f"Bearer {access_token}"},
    )
    
    if response.status_code != 200:
        logger.error(f"User info fetch failed: {response.text}")
        return None
    
    return response.json()


@oauth_bp.route("/authorize", methods=["GET"])
def authorize():
    """
    Get Google OAuth authorization URL.
    
    Query params:
        - state: Optional state for CSRF protection
    
    Returns:
        Authorization URL to redirect user
    """
    if not current_app.config.get("ENABLE_GOOGLE_OAUTH"):
        return error_response("Google OAuth is not enabled", 400)
    
    config = get_google_provider_config()
    state = request.args.get("state", secrets.token_hex(16))
    
    from urllib.parse import urlencode
    
    params = {
        "client_id": config["client_id"],
        "redirect_uri": config["redirect_uri"],
        "response_type": "code",
        "scope": config["scope"],
        "state": state,
        "access_type": "offline",
        "prompt": "select_account",
    }
    
    auth_url = f"{config['auth_url']}?{urlencode(params)}"
    
    return success_response({
        "auth_url": auth_url,
        "state": state,
    })


@oauth_bp.route("/callback", methods=["POST"])
def callback():
    """
    Handle Google OAuth callback.
    
    Request body:
        - code: Authorization code from Google
        - state: State for CSRF verification
    
    Returns:
        User data with tokens
    """
    if not current_app.config.get("ENABLE_GOOGLE_OAUTH"):
        return error_response("Google OAuth is not enabled", 400)
    
    data = request.get_json()
    
    if not data:
        return error_response("Request body is required", 400)
    
    code = data.get("code")
    state = data.get("state")
    
    if not code:
        return error_response("Authorization code is required", 400)
    
    tokens = exchange_code_for_tokens(code)
    
    if not tokens:
        return error_response("Failed to exchange authorization code", 400)
    
    access_token = tokens.get("access_token")
    id_token = tokens.get("id_token")
    
    if not access_token:
        return error_response("No access token received", 400)
    
    google_user = get_google_user_info(access_token)
    
    if not google_user:
        return error_response("Failed to get user info from Google", 400)
    
    google_id = google_user.get("sub")
    email = google_user.get("email", "").lower()
    first_name = google_user.get("given_name", "Google")
    last_name = google_user.get("family_name", "")
    avatar_url = google_user.get("picture")
    
    user = User.objects(google_id=google_id).first()
    
    if not user:
        user = User.objects(email=email).first()
        
        if user:
            user.google_id = google_id
            user.auth_provider = "google"
            if not user.avatar_url:
                user.avatar_url = avatar_url
            user.is_email_verified = True
            user.save()
            logger.info(f"Google account linked for user: {email}")
        else:
            user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                role="student_registered",
                auth_provider="google",
                google_id=google_id,
                avatar_url=avatar_url,
                is_email_verified=True,
            )
            user.save()
            
            wallet = Wallet(user=user.id, balance=0)
            wallet.save()
            user.wallet = wallet
            user.save()
            
            logger.info(f"New user registered via Google OAuth: {email}")
    
    user.last_login_at = datetime.utcnow()
    user.save()
    
    jwt_config = current_app.config
    auth_tokens = generate_tokens(
        user_id=str(user.id),
        role=user.role,
        jwt_secret=jwt_config["JWT_SECRET_KEY"],
        access_expires=jwt_config.get("JWT_ACCESS_TOKEN_EXPIRES", 3600),
        refresh_expires=jwt_config.get("JWT_REFRESH_TOKEN_EXPIRES", 2592000),
    )
    
    try:
        AuditLog(
            user=user.id,
            action=AuditAction.LOGIN.value,
            details={"method": "google_oauth"},
            ip_address=request.remote_addr,
            user_agent=request.headers.get("User-Agent", "")[:500],
        ).save()
    except Exception as e:
        logger.warning(f"Failed to create audit log: {e}")
    
    logger.info(f"User logged in via Google OAuth: {email}")
    
    return success_response({
        "user": user.to_dict(include_sensitive=True),
        **auth_tokens,
    }, "Login successful")


@oauth_bp.route("/link", methods=["POST"])
def link_google_account():
    """
    Link Google account to existing user.
    
    Request body:
        - code: Authorization code from Google
    
    Returns:
        Success message
    """
    identity = get_jwt_identity()
    
    if not identity:
        return error_response("Unauthorized", 401)
    
    user = User.objects(id=identity).first()
    
    if not user:
        return error_response("User not found", 401)
    
    if user.auth_provider == "google":
        return error_response("Account is already linked to Google", 400)
    
    data = request.get_json()
    code = data.get("code") if data else None
    
    if not code:
        return error_response("Authorization code is required", 400)
    
    tokens = exchange_code_for_tokens(code)
    
    if not tokens:
        return error_response("Failed to exchange authorization code", 400)
    
    access_token = tokens.get("access_token")
    
    if not access_token:
        return error_response("No access token received", 400)
    
    google_user = get_google_user_info(access_token)
    
    if not google_user:
        return error_response("Failed to get user info from Google", 400)
    
    google_id = google_user.get("sub")
    
    existing = User.objects(google_id=google_id).first()
    
    if existing and existing.id != user.id:
        return error_response("This Google account is already linked to another user", 400)
    
    user.google_id = google_id
    user.auth_provider = "google"
    if not user.avatar_url:
        user.avatar_url = google_user.get("picture")
    user.is_email_verified = True
    user.save()
    
    logger.info(f"Google account linked for user: {user.email}")
    
    return success_response(None, "Google account linked successfully")


@oauth_bp.route("/unlink", methods=["POST"])
def unlink_google_account():
    """
    Unlink Google account from user.
    
    Returns:
        Success message
    """
    identity = get_jwt_identity()
    
    if not identity:
        return error_response("Unauthorized", 401)
    
    user = User.objects(id=identity).first()
    
    if not user:
        return error_response("User not found", 401)
    
    if user.auth_provider != "google":
        return error_response("Account is not linked to Google", 400)
    
    if not user.password_hash:
        return error_response("Cannot unlink Google. Set a password first.", 400)
    
    user.google_id = None
    user.auth_provider = "local"
    user.save()
    
    logger.info(f"Google account unlinked for user: {user.email}")
    
    return success_response(None, "Google account unlinked successfully")
