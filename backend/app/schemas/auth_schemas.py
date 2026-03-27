"""
Auth schemas for ExamSaaS platform.
Marshmallow validators for all authentication inputs.
"""
import re
import logging
from typing import Optional

from marshmallow import Schema, fields, validate, validates, ValidationError, post_load, pre_load

logger = logging.getLogger(__name__)


class RegisterSchema(Schema):
    """Schema for user registration."""
    
    email = fields.Email(
        required=True,
        error_messages={
            "required": "Email is required",
            "invalid": "Invalid email format"
        }
    )
    
    password = fields.String(
        required=True,
        validate=validate.Length(min=8, max=128),
        error_messages={
            "required": "Password is required"
        }
    )
    
    first_name = fields.String(
        required=True,
        validate=validate.Length(min=2, max=50),
        error_messages={
            "required": "First name is required"
        }
    )
    
    last_name = fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(min=2, max=50),
        load_default=None
    )
    
    @validates("password")
    def validate_password_strength(self, value: str) -> None:
        """Validate password strength requirements."""
        errors = []
        
        if len(value) < 8:
            errors.append("Password must be at least 8 characters long")
        
        if not re.search(r"[A-Z]", value):
            errors.append("Password must contain at least one uppercase letter")
        
        if not re.search(r"[a-z]", value):
            errors.append("Password must contain at least one lowercase letter")
        
        if not re.search(r"\d", value):
            errors.append("Password must contain at least one digit")
        
        if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", value):
            errors.append("Password must contain at least one special character")
        
        if errors:
            raise ValidationError("; ".join(errors))
    
    @validates("first_name")
    def validate_first_name(self, value: str) -> None:
        """Validate first name contains only alphabetic characters."""
        if not re.match(r"^[a-zA-Z\s\-']+$", value.strip()):
            raise ValidationError("First name must contain only letters, spaces, hyphens, or apostrophes")
    
    @validates("last_name")
    def validate_last_name(self, value: Optional[str]) -> None:
        """Validate last name contains only alphabetic characters."""
        if value and not re.match(r"^[a-zA-Z\s\-']+$", value.strip()):
            raise ValidationError("Last name must contain only letters, spaces, hyphens, or apostrophes")
    
    @pre_load
    def normalize_email(self, data, **kwargs) -> dict:
        """Normalize email to lowercase and strip whitespace."""
        if "email" in data and data["email"]:
            data["email"] = data["email"].lower().strip()
        return data
    
    @pre_load
    def trim_strings(self, data, **kwargs) -> dict:
        """Trim whitespace from string fields."""
        for field in ["first_name", "last_name"]:
            if field in data and data[field]:
                data[field] = data[field].strip()
        return data


class LoginSchema(Schema):
    """Schema for user login."""
    
    email = fields.Email(
        required=True,
        error_messages={
            "required": "Email is required",
            "invalid": "Invalid email format"
        }
    )
    
    password = fields.String(
        required=True,
        error_messages={
            "required": "Password is required"
        }
    )
    
    role_hint = fields.String(
        required=False,
        allow_none=True,
        validate=validate.OneOf([
            "super_admin", "admin_public", "admin_college",
            "teacher", "student_registered", "student_assigned", "support_agent"
        ]),
        load_default=None
    )
    
    @pre_load
    def normalize_email(self, data, **kwargs) -> dict:
        """Normalize email to lowercase and strip whitespace."""
        if "email" in data and data["email"]:
            data["email"] = data["email"].lower().strip()
        return data


class GoogleAuthSchema(Schema):
    """Schema for Google OAuth authentication."""
    
    id_token = fields.String(
        required=True,
        error_messages={
            "required": "ID token is required"
        }
    )
    
    role_hint = fields.String(
        required=False,
        allow_none=True,
        validate=validate.OneOf([
            "super_admin", "admin_public", "admin_college",
            "teacher", "student_registered", "student_assigned", "support_agent"
        ]),
        load_default=None
    )


class VerifyEmailSchema(Schema):
    """Schema for email verification."""
    
    email = fields.Email(
        required=True,
        error_messages={
            "required": "Email is required",
            "invalid": "Invalid email format"
        }
    )
    
    otp = fields.String(
        required=True,
        validate=validate.Regexp(
            r"^\d{6}$",
            error="OTP must be exactly 6 digits"
        ),
        error_messages={
            "required": "OTP is required"
        }
    )
    
    @pre_load
    def normalize_email(self, data, **kwargs) -> dict:
        """Normalize email to lowercase and strip whitespace."""
        if "email" in data and data["email"]:
            data["email"] = data["email"].lower().strip()
        return data


class ForgotPasswordSchema(Schema):
    """Schema for forgot password request."""
    
    email = fields.Email(
        required=True,
        error_messages={
            "required": "Email is required",
            "invalid": "Invalid email format"
        }
    )
    
    @pre_load
    def normalize_email(self, data, **kwargs) -> dict:
        """Normalize email to lowercase and strip whitespace."""
        if "email" in data and data["email"]:
            data["email"] = data["email"].lower().strip()
        return data


class ResetPasswordSchema(Schema):
    """Schema for password reset."""
    
    email = fields.Email(
        required=True,
        error_messages={
            "required": "Email is required",
            "invalid": "Invalid email format"
        }
    )
    
    otp = fields.String(
        required=True,
        validate=validate.Regexp(
            r"^\d{6}$",
            error="OTP must be exactly 6 digits"
        ),
        error_messages={
            "required": "OTP is required"
        }
    )
    
    new_password = fields.String(
        required=True,
        validate=validate.Length(min=8, max=128),
        error_messages={
            "required": "New password is required"
        }
    )
    
    @validates("new_password")
    def validate_password_strength(self, value: str) -> None:
        """Validate password strength requirements."""
        errors = []
        
        if len(value) < 8:
            errors.append("Password must be at least 8 characters long")
        
        if not re.search(r"[A-Z]", value):
            errors.append("Password must contain at least one uppercase letter")
        
        if not re.search(r"[a-z]", value):
            errors.append("Password must contain at least one lowercase letter")
        
        if not re.search(r"\d", value):
            errors.append("Password must contain at least one digit")
        
        if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", value):
            errors.append("Password must contain at least one special character")
        
        if errors:
            raise ValidationError("; ".join(errors))
    
    @pre_load
    def normalize_email(self, data, **kwargs) -> dict:
        """Normalize email to lowercase and strip whitespace."""
        if "email" in data and data["email"]:
            data["email"] = data["email"].lower().strip()
        return data


class MagicLinkVerifySchema(Schema):
    """Schema for magic link verification."""
    
    token = fields.String(
        required=True,
        error_messages={
            "required": "Token is required"
        }
    )


class UpdateProfileSchema(Schema):
    """Schema for updating user profile."""
    
    first_name = fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(min=2, max=50),
        load_default=None
    )
    
    last_name = fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(min=2, max=50),
        load_default=None
    )
    
    phone = fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(max=20),
        load_default=None
    )
    
    avatar_url = fields.URL(
        required=False,
        allow_none=True,
        load_default=None
    )
    
    @validates("first_name")
    def validate_first_name(self, value: Optional[str]) -> None:
        """Validate first name contains only alphabetic characters."""
        if value and not re.match(r"^[a-zA-Z\s\-']+$", value.strip()):
            raise ValidationError("First name must contain only letters, spaces, hyphens, or apostrophes")
    
    @validates("last_name")
    def validate_last_name(self, value: Optional[str]) -> None:
        """Validate last name contains only alphabetic characters."""
        if value and not re.match(r"^[a-zA-Z\s\-']+$", value.strip()):
            raise ValidationError("Last name must contain only letters, spaces, hyphens, or apostrophes")
    
    @pre_load
    def trim_strings(self, data, **kwargs) -> dict:
        """Trim whitespace from string fields."""
        for field in ["first_name", "last_name", "phone"]:
            if field in data and data[field]:
                data[field] = data[field].strip()
        return data


class RefreshTokenSchema(Schema):
    """Schema for token refresh."""
    
    refresh_token = fields.String(
        required=True,
        error_messages={
            "required": "Refresh token is required"
        }
    )


class ResendOtpSchema(Schema):
    """Schema for resending OTP."""
    
    email = fields.Email(
        required=True,
        error_messages={
            "required": "Email is required",
            "invalid": "Invalid email format"
        }
    )
    
    purpose = fields.String(
        required=True,
        validate=validate.OneOf(["verify_email", "forgot_password"]),
        error_messages={
            "required": "Purpose is required"
        }
    )
    
    @pre_load
    def normalize_email(self, data, **kwargs) -> dict:
        """Normalize email to lowercase and strip whitespace."""
        if "email" in data and data["email"]:
            data["email"] = data["email"].lower().strip()
        return data


register_schema = RegisterSchema()
login_schema = LoginSchema()
google_auth_schema = GoogleAuthSchema()
verify_email_schema = VerifyEmailSchema()
forgot_password_schema = ForgotPasswordSchema()
reset_password_schema = ResetPasswordSchema()
magic_link_verify_schema = MagicLinkVerifySchema()
update_profile_schema = UpdateProfileSchema()
refresh_token_schema = RefreshTokenSchema()
resend_otp_schema = ResendOtpSchema()
