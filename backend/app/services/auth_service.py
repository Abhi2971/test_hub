"""
Authentication service for ExamSaaS platform.
Pure Python - zero Flask imports, zero HTTP concepts.
"""
import logging
import json
import hmac
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple, Dict, Any, List

import jwt
import bcrypt

from app.utils.security import (
    generate_otp,
    hash_password,
    verify_password,
    constant_time_compare,
    sanitize_input,
    generate_jti,
    get_redirect_path,
    generate_magic_link_token,
)
from app.utils.email_helper import (
    send_otp_email,
    send_welcome_email,
    send_password_reset_email,
)

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
            logger.warning("Redis not available for auth service")
            return None
    return REDIS_CLIENT


def _get_config(key: str, default: Any = None) -> Any:
    """Get configuration value."""
    try:
        from flask import current_app
        return current_app.config.get(key, default)
    except RuntimeError:
        return default


OTP_TTL = 600
SESSION_TTL = 7 * 24 * 3600
MAGIC_LINK_TTL = 3600


class AuthServiceError(Exception):
    """Base exception for auth service errors."""
    def __init__(self, message: str, code: str, status_code: int = 400):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class EmailExistsError(AuthServiceError):
    """Email already exists."""
    def __init__(self):
        super().__init__("Email already registered", "EMAIL_EXISTS", 409)


class InvalidCredentialsError(AuthServiceError):
    """Invalid credentials."""
    def __init__(self):
        super().__init__("Invalid email or password", "INVALID_CREDENTIALS", 401)


class AccountSuspendedError(AuthServiceError):
    """Account is suspended."""
    def __init__(self, reason: str = None):
        message = "Account has been suspended"
        if reason:
            message += f": {reason}"
        super().__init__(message, "ACCOUNT_SUSPENDED", 403)


class EmailNotVerifiedError(AuthServiceError):
    """Email not verified."""
    def __init__(self):
        super().__init__("Email verification required", "EMAIL_NOT_VERIFIED", 403)


class InvalidTokenError(AuthServiceError):
    """Invalid or expired token."""
    def __init__(self, message: str = "Invalid or expired token"):
        super().__init__(message, "INVALID_TOKEN", 401)


class InvalidOtpError(AuthServiceError):
    """Invalid or expired OTP."""
    def __init__(self):
        super().__init__("Invalid or expired OTP", "INVALID_OTP", 400)


class UserNotFoundError(AuthServiceError):
    """User not found."""
    def __init__(self):
        super().__init__("User not found", "USER_NOT_FOUND", 404)


class GoogleAuthError(AuthServiceError):
    """Google authentication failed."""
    def __init__(self, message: str = "Google authentication failed"):
        super().__init__(message, "GOOGLE_AUTH_FAILED", 401)


class InstituteSuspendedError(AuthServiceError):
    """Institute is suspended."""
    def __init__(self):
        super().__init__("Institute has been suspended", "INSTITUTE_SUSPENDED", 423)


def _generate_tokens(
    user_id: str,
    email: str,
    role: str,
    institute_id: Optional[str],
    access_expires: int = 900,
    refresh_expires: int = 7 * 24 * 3600
) -> Dict[str, Any]:
    """
    Generate access and refresh tokens.
    
    Args:
        user_id: User ID
        email: User email
        role: User role
        institute_id: Institute ID
        access_expires: Access token expiry in seconds (default 15 min)
        refresh_expires: Refresh token expiry in seconds (default 7 days)
    
    Returns:
        Dictionary with tokens and metadata
    """
    jwt_secret = _get_config("JWT_SECRET_KEY", "dev-jwt-secret-change-in-production")
    now = datetime.now(timezone.utc)
    
    access_jti = generate_jti()
    refresh_jti = generate_jti()
    
    access_payload = {
        "sub": user_id,
        "user_id": user_id,
        "email": email,
        "role": role,
        "institute_id": institute_id,
        "jti": access_jti,
        "type": "access",
        "iat": now,
        "exp": now + timedelta(seconds=access_expires),
    }
    
    refresh_payload = {
        "sub": user_id,
        "user_id": user_id,
        "email": email,
        "role": role,
        "institute_id": institute_id,
        "jti": refresh_jti,
        "type": "refresh",
        "iat": now,
        "exp": now + timedelta(seconds=refresh_expires),
    }
    
    access_token = jwt.encode(access_payload, jwt_secret, algorithm="HS256")
    refresh_token = jwt.encode(refresh_payload, jwt_secret, algorithm="HS256")
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "expires_in": access_expires,
        "refresh_expires_in": refresh_expires,
        "access_jti": access_jti,
        "refresh_jti": refresh_jti,
    }


def _store_session(user_id: str, jti: str) -> None:
    """Store user session in Redis."""
    redis = _get_redis()
    if redis:
        try:
            redis.setex(f"session:{user_id}", SESSION_TTL, jti)
        except Exception as e:
            logger.error(f"Failed to store session in Redis: {e}")


def _get_session(user_id: str) -> Optional[str]:
    """Get stored session JTI for user."""
    redis = _get_redis()
    if redis:
        try:
            return redis.get(f"session:{user_id}")
        except Exception as e:
            logger.error(f"Failed to get session from Redis: {e}")
    return None


def _blacklist_token(jti: str, ttl: int) -> None:
    """Blacklist a token in Redis."""
    redis = _get_redis()
    if redis:
        try:
            redis.setex(f"blacklist:{jti}", ttl, "1")
        except Exception as e:
            logger.error(f"Failed to blacklist token in Redis: {e}")


def _is_blacklisted(jti: str) -> bool:
    """Check if token is blacklisted."""
    redis = _get_redis()
    if redis:
        try:
            return redis.exists(f"blacklist:{jti}") > 0
        except Exception as e:
            logger.error(f"Failed to check blacklist in Redis: {e}")
    return False


def _store_otp(email: str, purpose: str, otp: str) -> None:
    """Store OTP in Redis."""
    redis = _get_redis()
    if redis:
        try:
            key = f"otp:{email}:{purpose}"
            redis.setex(key, OTP_TTL, otp)
        except Exception as e:
            logger.error(f"Failed to store OTP in Redis: {e}")


def _get_otp(email: str, purpose: str) -> Optional[str]:
    """Get stored OTP from Redis."""
    redis = _get_redis()
    if redis:
        try:
            key = f"otp:{email}:{purpose}"
            return redis.get(key)
        except Exception as e:
            logger.error(f"Failed to get OTP from Redis: {e}")
    return None


def _delete_otp(email: str, purpose: str) -> None:
    """Delete OTP from Redis."""
    redis = _get_redis()
    if redis:
        try:
            key = f"otp:{email}:{purpose}"
            redis.delete(key)
        except Exception as e:
            logger.error(f"Failed to delete OTP from Redis: {e}")


def _store_magic_link(token: str, data: Dict[str, Any]) -> None:
    """Store magic link data in Redis."""
    redis = _get_redis()
    if redis:
        try:
            key = f"magic:{token}"
            redis.setex(key, MAGIC_LINK_TTL, json.dumps(data))
        except Exception as e:
            logger.error(f"Failed to store magic link in Redis: {e}")


def _get_magic_link(token: str) -> Optional[Dict[str, Any]]:
    """Get magic link data from Redis."""
    redis = _get_redis()
    if redis:
        try:
            key = f"magic:{token}"
            data = redis.get(key)
            if data == "used":
                return None
            if data:
                return json.loads(data)
        except Exception as e:
            logger.error(f"Failed to get magic link from Redis: {e}")
    return None


def _mark_magic_link_used(token: str) -> None:
    """Mark magic link as used."""
    redis = _get_redis()
    if redis:
        try:
            key = f"magic:{token}"
            redis.setex(key, MAGIC_LINK_TTL, "used")
        except Exception as e:
            logger.error(f"Failed to mark magic link as used: {e}")


def _blacklist_all_user_sessions(user_id: str) -> None:
    """Blacklist all sessions for a user."""
    redis = _get_redis()
    if redis:
        try:
            session_jti = redis.get(f"session:{user_id}")
            if session_jti:
                redis.delete(f"session:{user_id}")
                logger.info(f"Blacklisted all sessions for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to blacklist user sessions: {e}")


def register_user(
    email: str,
    password: str,
    first_name: str,
    last_name: Optional[str] = None
) -> Tuple[str, str]:
    """
    Register a new user.
    
    Args:
        email: User email
        password: User password
        first_name: First name
        last_name: Last name (optional)
    
    Returns:
        Tuple of (user_id, masked_email)
    
    Raises:
        EmailExistsError: If email already registered
    """
    email = sanitize_input(email).lower()
    first_name = sanitize_input(first_name)
    last_name = sanitize_input(last_name) if last_name else None
    
    from app.models import User, Wallet
    
    existing_user = User.objects(email=email).first()
    if existing_user:
        raise EmailExistsError()
    
    password_hash = hash_password(password, cost=12)
    
    user = User(
        email=email,
        password_hash=password_hash,
        first_name=first_name,
        last_name=last_name,
        role="student_registered",
        is_email_verified=False,
        auth_provider="local",
        is_active=True,
    )
    user.save()
    
    wallet = Wallet(user=user.id, balance=0)
    wallet.save()
    
    user.wallet = wallet
    user.save()
    
    otp = generate_otp()
    _store_otp(email, "verify_email", otp)
    send_otp_email(email, otp, "verify_email")
    
    logger.info(f"User registered: {email}")
    
    masked = email[:2] + "***@" + email.split("@")[1]
    return str(user.id), masked


def verify_email(email: str, otp: str) -> bool:
    """
    Verify user email with OTP.
    
    Args:
        email: User email
        otp: One-time password
    
    Returns:
        True if verified
    
    Raises:
        UserNotFoundError: If user not found
        InvalidOtpError: If OTP invalid or expired
    """
    email = email.lower().strip()
    
    from app.models import User
    
    user = User.objects(email=email).first()
    if not user:
        raise UserNotFoundError()
    
    stored_otp = _get_otp(email, "verify_email")
    
    if not stored_otp or not constant_time_compare(otp, stored_otp):
        raise InvalidOtpError()
    
    user.is_email_verified = True
    user.save()
    
    _delete_otp(email, "verify_email")
    
    logger.info(f"Email verified for user: {email}")
    
    return True


def authenticate_user(
    email: str,
    password: str,
    role_hint: Optional[str] = None
) -> Dict[str, Any]:
    """
    Authenticate user and return tokens.
    
    Args:
        email: User email
        password: User password
        role_hint: Optional role hint
    
    Returns:
        Login response dictionary
    
    Raises:
        InvalidCredentialsError: If credentials invalid
        AccountSuspendedError: If account suspended
        EmailNotVerifiedError: If email not verified
        InstituteSuspendedError: If institute suspended
    """
    email = email.lower().strip()
    
    from app.models import User, Institute
    
    user = User.objects(email=email).first()
    
    if not user or not user.check_password(password):
        raise InvalidCredentialsError()
    
    if not user.is_active:
        raise AccountSuspendedError()
    
    if user.auth_provider == "google":
        raise InvalidCredentialsError()
    
    if user.role in ["student_registered", "student_assigned"] and not user.is_email_verified:
        raise EmailNotVerifiedError()
    
    institute_id = None
    institute_name = None
    if user.institute:
        institute_id = str(user.institute.id)
        institute = Institute.objects(id=user.institute.id).first()
        if institute:
            institute_name = institute.name
            if institute.is_suspended:
                raise InstituteSuspendedError()
    
    old_session_jti = _get_session(str(user.id))
    if old_session_jti:
        _blacklist_token(old_session_jti, SESSION_TTL)
    
    tokens = _generate_tokens(
        user_id=str(user.id),
        email=user.email,
        role=user.role,
        institute_id=institute_id,
    )
    
    _store_session(str(user.id), tokens["access_jti"])
    
    user.last_login_at = datetime.now(timezone.utc)
    user.save()
    
    logger.info(f"User logged in: {email}")
    
    return {
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "user": {
            "id": str(user.id),
            "email": user.email,
            "role": user.role,
            "full_name": user.full_name,
            "avatar_url": user.avatar_url,
            "institute_id": institute_id,
            "institute_name": institute_name,
            "is_email_verified": user.is_email_verified,
        },
        "redirect_to": get_redirect_path(user.role),
    }


def authenticate_google(
    id_token: str,
    role_hint: Optional[str] = None
) -> Dict[str, Any]:
    """
    Authenticate user with Google OAuth.
    
    Args:
        id_token: Google ID token
        role_hint: Optional role hint
    
    Returns:
        Login response dictionary
    
    Raises:
        GoogleAuthError: If authentication failed
        AccountSuspendedError: If account suspended
    """
    try:
        from google.oauth2 import id_token as google_id_token
        from google.auth.transport import requests as google_requests
        
        client_id = _get_config("GOOGLE_CLIENT_ID")
        
        if not client_id:
            raise GoogleAuthError("Google OAuth not configured")
        
        idinfo = google_id_token.verify_oauth2_token(
            id_token,
            google_requests.Request(),
            client_id
        )
        
        if idinfo.get("iss") not in ["accounts.google.com", "https://accounts.google.com"]:
            raise GoogleAuthError("Invalid issuer")
        
        google_id = idinfo.get("sub")
        email = idinfo.get("email", "").lower()
        name = idinfo.get("name", "")
        picture = idinfo.get("picture")
        
    except Exception as e:
        logger.error(f"Google auth failed: {e}")
        raise GoogleAuthError(str(e))
    
    from app.models import User, Wallet, Institute
    
    user = User.objects(google_id=google_id).first()
    
    if not user:
        user = User.objects(email=email).first()
        
        if user:
            if user.google_id:
                raise GoogleAuthError("Google account already linked to another user")
            
            user.google_id = google_id
            user.auth_provider = "google"
            if not user.avatar_url:
                user.avatar_url = picture
            user.is_email_verified = True
            user.save()
            logger.info(f"Google account linked for user: {email}")
        else:
            user = User(
                email=email,
                first_name=name.split()[0] if name else "User",
                last_name=" ".join(name.split()[1:]) if len(name.split()) > 1 else None,
                role="student_registered",
                auth_provider="google",
                google_id=google_id,
                avatar_url=picture,
                is_email_verified=True,
                is_active=True,
            )
            user.save()
            
            wallet = Wallet(user=user.id, balance=0)
            wallet.save()
            
            user.wallet = wallet
            user.save()
            
            logger.info(f"New user registered via Google: {email}")
    
    if not user.is_active:
        raise AccountSuspendedError()
    
    institute_id = None
    institute_name = None
    if user.institute:
        institute_id = str(user.institute.id)
        institute = Institute.objects(id=user.institute.id).first()
        if institute and institute.is_suspended:
            raise InstituteSuspendedError()
    
    old_session_jti = _get_session(str(user.id))
    if old_session_jti:
        _blacklist_token(old_session_jti, SESSION_TTL)
    
    tokens = _generate_tokens(
        user_id=str(user.id),
        email=user.email,
        role=user.role,
        institute_id=institute_id,
    )
    
    _store_session(str(user.id), tokens["access_jti"])
    
    user.last_login_at = datetime.now(timezone.utc)
    user.save()
    
    logger.info(f"User logged in via Google: {email}")
    
    return {
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "user": {
            "id": str(user.id),
            "email": user.email,
            "role": user.role,
            "full_name": user.full_name,
            "avatar_url": user.avatar_url,
            "institute_id": institute_id,
            "institute_name": institute_name,
            "is_email_verified": user.is_email_verified,
        },
        "redirect_to": get_redirect_path(user.role),
    }


def refresh_access_token(refresh_token: str) -> Dict[str, Any]:
    """
    Refresh access token using refresh token.
    
    Args:
        refresh_token: Refresh token
    
    Returns:
        New tokens dictionary
    
    Raises:
        InvalidTokenError: If token invalid or blacklisted
    """
    jwt_secret = _get_config("JWT_SECRET_KEY", "dev-jwt-secret-change-in-production")
    
    try:
        payload = jwt.decode(refresh_token, jwt_secret, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise InvalidTokenError("Refresh token has expired")
    except jwt.InvalidTokenError:
        raise InvalidTokenError("Invalid refresh token")
    
    if payload.get("type") != "refresh":
        raise InvalidTokenError("Invalid token type")
    
    jti = payload.get("jti")
    user_id = payload.get("user_id")
    
    if _is_blacklisted(jti):
        raise InvalidTokenError("Token has been revoked")
    
    session_jti = _get_session(user_id)
    if session_jti and session_jti != jti:
        raise InvalidTokenError("Session invalidated")
    
    from app.models import User, Institute
    
    user = User.objects(id=user_id).first()
    if not user or not user.is_active:
        raise InvalidTokenError("User not found or inactive")
    
    institute_id = None
    if user.institute:
        institute_id = str(user.institute.id)
    
    tokens = _generate_tokens(
        user_id=str(user.id),
        email=user.email,
        role=user.role,
        institute_id=institute_id,
    )
    
    _blacklist_token(jti, 7 * 24 * 3600)
    
    _store_session(user_id, tokens["access_jti"])
    
    logger.info(f"Token refreshed for user: {user.email}")
    
    return {
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "token_type": "Bearer",
        "expires_in": tokens["expires_in"],
    }


def logout_user(access_token: str) -> bool:
    """
    Logout user by blacklisting token and deleting session.
    
    Args:
        access_token: Current access token
    
    Returns:
        True if successful
    """
    jwt_secret = _get_config("JWT_SECRET_KEY", "dev-jwt-secret-change-in-production")
    
    try:
        payload = jwt.decode(access_token, jwt_secret, algorithms=["HS256"])
    except jwt.InvalidTokenError:
        return True
    
    jti = payload.get("jti")
    user_id = payload.get("user_id")
    
    if jti:
        exp = payload.get("exp")
        now = datetime.now(timezone.utc).timestamp()
        ttl = max(int(exp - now), 0)
        _blacklist_token(jti, ttl)
    
    if user_id:
        redis = _get_redis()
        if redis:
            try:
                redis.delete(f"session:{user_id}")
            except Exception as e:
                logger.error(f"Failed to delete session: {e}")
    
    logger.info(f"User logged out: {user_id}")
    
    return True


def request_password_reset(email: str) -> bool:
    """
    Request password reset OTP.
    
    Args:
        email: User email
    
    Returns:
        True if email exists and OTP sent
    """
    email = email.lower().strip()
    
    from app.models import User
    
    user = User.objects(email=email).first()
    
    if user and user.auth_provider == "local":
        otp = generate_otp()
        _store_otp(email, "forgot_password", otp)
        send_password_reset_email(email, otp)
        logger.info(f"Password reset requested for: {email}")
    
    return True


def reset_password_with_otp(email: str, otp: str, new_password: str) -> bool:
    """
    Reset password using OTP.
    
    Args:
        email: User email
        otp: One-time password
        new_password: New password
    
    Returns:
        True if successful
    
    Raises:
        UserNotFoundError: If user not found
        InvalidOtpError: If OTP invalid or expired
    """
    email = email.lower().strip()
    
    from app.models import User
    
    user = User.objects(email=email).first()
    if not user:
        raise UserNotFoundError()
    
    stored_otp = _get_otp(email, "forgot_password")
    
    if not stored_otp or not constant_time_compare(otp, stored_otp):
        raise InvalidOtpError()
    
    password_hash = hash_password(new_password, cost=12)
    user.password_hash = password_hash
    user.save()
    
    _delete_otp(email, "forgot_password")
    
    _blacklist_all_user_sessions(str(user.id))
    
    logger.info(f"Password reset for user: {email}")
    
    return True


def get_user_profile(user_id: str) -> Dict[str, Any]:
    """
    Get user profile with institute details.
    
    Args:
        user_id: User ID
    
    Returns:
        User profile dictionary
    
    Raises:
        UserNotFoundError: If user not found
    """
    from app.models import User, Institute
    
    user = User.objects(id=user_id).first()
    if not user:
        raise UserNotFoundError()
    
    institute_id = None
    institute_name = None
    institute_data = None
    
    if user.institute:
        institute_id = str(user.institute.id)
        institute = Institute.objects(id=user.institute.id).first()
        if institute:
            institute_name = institute.name
            institute_data = {
                "id": str(institute.id),
                "name": institute.name,
                "domain": institute.domain,
                "logo_url": institute.logo_url,
            }
    
    return {
        "id": str(user.id),
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "full_name": user.full_name,
        "role": user.role,
        "avatar_url": user.avatar_url,
        "phone": user.phone,
        "is_active": user.is_active,
        "is_email_verified": user.is_email_verified,
        "auth_provider": user.auth_provider,
        "institute_id": institute_id,
        "institute": institute_data,
        "wallet_balance": float(user.wallet.balance) if user.wallet else 0,
        "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


def update_user_profile(
    user_id: str,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    phone: Optional[str] = None,
    avatar_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update user profile.
    
    Args:
        user_id: User ID
        first_name: New first name (optional)
        last_name: New last name (optional)
        phone: New phone (optional)
        avatar_url: New avatar URL (optional)
    
    Returns:
        Updated profile dictionary
    
    Raises:
        UserNotFoundError: If user not found
    """
    from app.models import User
    
    user = User.objects(id=user_id).first()
    if not user:
        raise UserNotFoundError()
    
    if first_name is not None:
        user.first_name = sanitize_input(first_name)
    
    if last_name is not None:
        user.last_name = sanitize_input(last_name) if last_name else None
    
    if phone is not None:
        user.phone = sanitize_input(phone) if phone else None
    
    if avatar_url is not None:
        user.avatar_url = avatar_url
    
    user.save()
    
    logger.info(f"Profile updated for user: {user.email}")
    
    return get_user_profile(user_id)


def create_magic_link(student_id: str, exam_id: str) -> str:
    """
    Create a magic link for exam access.
    
    Args:
        student_id: Student ID
        exam_id: Exam ID
    
    Returns:
        Magic link token
    """
    token = generate_magic_link_token()
    
    data = {
        "student_id": student_id,
        "exam_id": exam_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    
    _store_magic_link(token, data)
    
    logger.info(f"Magic link created for student {student_id}, exam {exam_id}")
    
    return token


def verify_magic_link(token: str) -> Dict[str, Any]:
    """
    Verify magic link and return access token.
    
    Args:
        token: Magic link token
    
    Returns:
        Access token and exam info
    
    Raises:
        InvalidTokenError: If token invalid or expired
        UserNotFoundError: If student not found
    """
    data = _get_magic_link(token)
    
    if not data:
        raise InvalidTokenError("Invalid or expired magic link")
    
    student_id = data.get("student_id")
    exam_id = data.get("exam_id")
    
    if not student_id or not exam_id:
        raise InvalidTokenError("Invalid magic link data")
    
    _mark_magic_link_used(token)
    
    from app.models import User, Exam
    
    student = User.objects(id=student_id).first()
    if not student:
        raise UserNotFoundError()
    
    exam = Exam.objects(id=exam_id).first()
    if not exam:
        raise InvalidTokenError("Exam not found")
    
    tokens = _generate_tokens(
        user_id=str(student.id),
        email=student.email,
        role=student.role,
        institute_id=str(student.institute.id) if student.institute else None,
        access_expires=2 * 3600,
        refresh_expires=2 * 3600,
    )
    
    logger.info(f"Magic link verified for student {student_id}, exam {exam_id}")
    
    return {
        "access_token": tokens["access_token"],
        "student": {
            "id": str(student.id),
            "name": student.full_name,
        },
        "exam_id": exam_id,
        "redirect_to": f"/exam/{exam_id}",
    }


def resend_otp(email: str, purpose: str) -> bool:
    """
    Resend OTP to email.
    
    Args:
        email: User email
        purpose: OTP purpose (verify_email or forgot_password)
    
    Returns:
        True if sent
    
    Raises:
        UserNotFoundError: If user not found (for verify_email)
    """
    email = email.lower().strip()
    
    from app.models import User
    
    if purpose == "verify_email":
        user = User.objects(email=email).first()
        if not user:
            raise UserNotFoundError()
        if user.is_email_verified:
            return True
    
    otp = generate_otp()
    _store_otp(email, purpose, otp)
    
    send_otp_email(email, otp, purpose)
    
    logger.info(f"OTP resent to {email}, purpose: {purpose}")
    
    return True
