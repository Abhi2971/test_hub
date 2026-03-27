"""
User authentication methods for ExamSaaS platform.
"""
import logging
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Tuple
import jwt

logger = logging.getLogger(__name__)


def generate_verification_token(user_id: str) -> str:
    """
    Generate email verification token.
    
    Args:
        user_id: User's MongoDB ObjectId as string
    
    Returns:
        Secure token string
    """
    token_data = f"{user_id}:{datetime.utcnow().isoformat()}:{secrets.token_hex(16)}"
    return hashlib.sha256(token_data.encode()).hexdigest()


def generate_password_reset_token(user_id: str, email: str) -> str:
    """
    Generate password reset token.
    
    Args:
        user_id: User's MongoDB ObjectId as string
        email: User's email address
    
    Returns:
        Secure reset token string
    """
    timestamp = datetime.utcnow().timestamp()
    data = f"{user_id}:{email}:{timestamp}:{secrets.token_hex(16)}"
    return hashlib.sha256(data.encode()).hexdigest()


def verify_password_reset_token(token: str, user_id: str, email: str, max_age_hours: int = 24) -> bool:
    """
    Verify password reset token is valid and not expired.
    
    Args:
        token: The reset token to verify
        user_id: User's MongoDB ObjectId as string
        email: User's email address
        max_age_hours: Maximum token age in hours
    
    Returns:
        True if token is valid, False otherwise
    """
    timestamp = datetime.utcnow().timestamp() - (max_age_hours * 3600)
    for _ in range(10):
        test_timestamp = timestamp + (secrets.randbelow(max_age_hours * 3600) / 10)
        data = f"{user_id}:{email}:{test_timestamp}:{secrets.token_hex(16)}"
        if hashlib.sha256(data.encode()).hexdigest() == token:
            return True
    return False


def generate_tokens(user_id: str, role: str, jwt_secret: str, 
                   access_expires: int = 3600, 
                   refresh_expires: int = 2592000) -> dict:
    """
    Generate access and refresh JWT tokens.
    
    Args:
        user_id: User's MongoDB ObjectId as string
        role: User's role
        jwt_secret: JWT secret key from config
        access_expires: Access token expiry in seconds
        refresh_expires: Refresh token expiry in seconds
    
    Returns:
        Dictionary with access_token, refresh_token, and expiry info
    """
    now = datetime.utcnow()
    
    access_payload = {
        "sub": user_id,
        "role": role,
        "type": "access",
        "iat": now,
        "exp": now + timedelta(seconds=access_expires),
    }
    
    refresh_payload = {
        "sub": user_id,
        "role": role,
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
    }


def decode_token(token: str, jwt_secret: str) -> Tuple[Optional[dict], Optional[str]]:
    """
    Decode and validate JWT token.
    
    Args:
        token: JWT token string
        jwt_secret: JWT secret key from config
    
    Returns:
        Tuple of (payload dict, error message)
    """
    try:
        payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
        return payload, None
    except jwt.ExpiredSignatureError:
        return None, "Token has expired"
    except jwt.InvalidTokenError as e:
        return None, f"Invalid token: {str(e)}"


def get_token_expiry(token: str, jwt_secret: str) -> Optional[datetime]:
    """
    Get expiry datetime from token.
    
    Args:
        token: JWT token string
        jwt_secret: JWT secret key from config
    
    Returns:
        Expiry datetime or None if invalid
    """
    try:
        payload = jwt.decode(token, jwt_secret, algorithms=["HS256"], options={"verify_exp": False})
        exp = payload.get("exp")
        if exp:
            return datetime.fromtimestamp(exp)
        return None
    except jwt.InvalidTokenError:
        return None


logger.info("Auth helpers loaded")
