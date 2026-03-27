"""
Security utilities for ExamSaaS platform.
Contains bcrypt helpers, OTP generation, and token utilities.
"""
import os
import re
import hmac
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass

import bcrypt


@dataclass
class PasswordValidationResult:
    """Result of password validation."""
    is_valid: bool
    error_message: Optional[str] = None


@dataclass
class TokenPayload:
    """JWT token payload."""
    user_id: str
    email: str
    role: str
    institute_id: Optional[str]
    jti: str
    token_type: str
    exp: datetime
    iat: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "user_id": self.user_id,
            "email": self.email,
            "role": self.role,
            "institute_id": self.institute_id,
            "jti": self.jti,
            "token_type": self.token_type,
            "exp": self.exp,
            "iat": self.iat,
        }


def generate_jti() -> str:
    """
    Generate a unique JWT ID.
    
    Returns:
        Unique string identifier
    """
    return f"{secrets.token_hex(16)}{datetime.now(timezone.utc).timestamp()}"


def hash_password(password: str, cost: int = 12) -> str:
    """
    Hash a password using bcrypt with cost factor 12.
    
    Args:
        password: Plain text password
        cost: Bcrypt cost factor (default: 12)
    
    Returns:
        Hashed password string
    """
    if cost < 12:
        raise ValueError("Bcrypt cost factor must be at least 12")
    
    salt = bcrypt.gensalt(rounds=cost)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """
    Verify password against hash using constant-time comparison.
    
    Args:
        password: Plain text password
        hashed: Hashed password string
    
    Returns:
        True if password matches, False otherwise
    """
    if not password or not hashed:
        return False
    
    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            hashed.encode("utf-8")
        )
    except (ValueError, TypeError):
        return False


def validate_password_strength(password: str) -> PasswordValidationResult:
    """
    Validate password strength requirements.
    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    
    Args:
        password: Password to validate
    
    Returns:
        PasswordValidationResult with validation status
    """
    if not password:
        return PasswordValidationResult(False, "Password is required")
    
    if len(password) < 8:
        return PasswordValidationResult(False, "Password must be at least 8 characters long")
    
    if not re.search(r"[A-Z]", password):
        return PasswordValidationResult(False, "Password must contain at least one uppercase letter")
    
    if not re.search(r"[a-z]", password):
        return PasswordValidationResult(False, "Password must contain at least one lowercase letter")
    
    if not re.search(r"\d", password):
        return PasswordValidationResult(False, "Password must contain at least one digit")
    
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password):
        return PasswordValidationResult(False, "Password must contain at least one special character")
    
    return PasswordValidationResult(True)


def validate_email_format(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email address to validate
    
    Returns:
        True if valid format, False otherwise
    """
    if not email:
        return False
    
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email.strip()))


def validate_name(name: str, field_name: str = "Name") -> PasswordValidationResult:
    """
    Validate name field.
    Requirements:
    - 2-50 characters
    - Alphabetic only (including spaces, hyphens, apostrophes)
    
    Args:
        name: Name to validate
        field_name: Field name for error messages
    
    Returns:
        PasswordValidationResult with validation status
    """
    if not name:
        return PasswordValidationResult(False, f"{field_name} is required")
    
    name = name.strip()
    
    if len(name) < 2:
        return PasswordValidationResult(False, f"{field_name} must be at least 2 characters")
    
    if len(name) > 50:
        return PasswordValidationResult(False, f"{field_name} must not exceed 50 characters")
    
    if not re.match(r"^[a-zA-Z\s\-']+$", name):
        return PasswordValidationResult(False, f"{field_name} must contain only letters, spaces, hyphens, or apostrophes")
    
    return PasswordValidationResult(True)


def generate_otp(length: int = 6) -> str:
    """
    Generate a numeric OTP.
    
    Args:
        length: Length of OTP (default: 6)
    
    Returns:
        OTP string
    """
    return "".join(secrets.choice("0123456789") for _ in range(length))


def generate_magic_link_token() -> str:
    """
    Generate a magic link token.
    
    Returns:
        Secure random token
    """
    return secrets.token_urlsafe(32)


def constant_time_compare(val1: str, val2: str) -> bool:
    """
    Compare two strings in constant time to prevent timing attacks.
    
    Args:
        val1: First value
        val2: Second value
    
    Returns:
        True if equal, False otherwise
    """
    if len(val1) != len(val2):
        return False
    
    return hmac.compare_digest(val1.encode("utf-8"), val2.encode("utf-8"))


def sanitize_input(text: str) -> str:
    """
    Sanitize user input to remove potentially harmful content.
    
    Args:
        text: Raw input text
    
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    import bleach
    
    cleaned = bleach.clean(
        text,
        tags=[],
        attributes={},
        strip=True,
        strip_comments=True,
    )
    
    return cleaned.strip()


def generate_verification_token(user_id: str) -> str:
    """
    Generate email verification token.
    
    Args:
        user_id: User's MongoDB ObjectId as string
    
    Returns:
        Secure token string
    """
    timestamp = datetime.now(timezone.utc).timestamp()
    random_bytes = secrets.token_hex(16)
    data = f"{user_id}:{timestamp}:{random_bytes}"
    return hashlib.sha256(data.encode()).hexdigest()


def create_token_payload(
    user_id: str,
    email: str,
    role: str,
    institute_id: Optional[str],
    token_type: str,
    expires_delta: timedelta
) -> TokenPayload:
    """
    Create a token payload.
    
    Args:
        user_id: User ID
        email: User email
        role: User role
        institute_id: Institute ID (optional)
        token_type: Type of token (access/refresh)
        expires_delta: Time until expiration
    
    Returns:
        TokenPayload instance
    """
    now = datetime.now(timezone.utc)
    jti = generate_jti()
    
    return TokenPayload(
        user_id=user_id,
        email=email,
        role=role,
        institute_id=institute_id,
        jti=jti,
        token_type=token_type,
        exp=now + expires_delta,
        iat=now,
    )


def mask_email(email: str) -> str:
    """
    Mask email address for display (e.g., t***@example.com).
    
    Args:
        email: Email address
    
    Returns:
        Masked email string
    """
    if not email or "@" not in email:
        return "***"
    
    local, domain = email.rsplit("@", 1)
    
    if len(local) <= 2:
        masked_local = local[0] + "***"
    else:
        masked_local = local[0] + "***" + local[-1]
    
    return f"{masked_local}@{domain}"


def mask_phone(phone: str) -> str:
    """
    Mask phone number for display (e.g., ***1234).
    
    Args:
        phone: Phone number
    
    Returns:
        Masked phone string
    """
    if not phone or len(phone) < 4:
        return "***"
    
    return "***" + phone[-4:]


ROLE_REDIRECT_MAP = {
    "super_admin": "/dashboard/superadmin",
    "admin_public": "/dashboard/admin-public",
    "admin_college": "/dashboard/admin-college",
    "teacher": "/dashboard/teacher",
    "student_registered": "/dashboard/student",
    "student_assigned": "/dashboard/student",
    "support_agent": "/dashboard/support",
}


def get_redirect_path(role: str) -> str:
    """
    Get redirect path based on user role.
    
    Args:
        role: User role
    
    Returns:
        Redirect path
    """
    return ROLE_REDIRECT_MAP.get(role, "/dashboard")
