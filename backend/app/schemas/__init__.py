"""
Schemas package for ExamSaaS platform.
Marshmallow schemas for request validation.
"""
from app.schemas.auth_schemas import (
    RegisterSchema,
    LoginSchema,
    GoogleAuthSchema,
    VerifyEmailSchema,
    ForgotPasswordSchema,
    ResetPasswordSchema,
    MagicLinkVerifySchema,
    UpdateProfileSchema,
    RefreshTokenSchema,
    ResendOtpSchema,
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

__all__ = [
    "RegisterSchema",
    "LoginSchema",
    "GoogleAuthSchema",
    "VerifyEmailSchema",
    "ForgotPasswordSchema",
    "ResetPasswordSchema",
    "MagicLinkVerifySchema",
    "UpdateProfileSchema",
    "RefreshTokenSchema",
    "ResendOtpSchema",
    "register_schema",
    "login_schema",
    "google_auth_schema",
    "verify_email_schema",
    "forgot_password_schema",
    "reset_password_schema",
    "magic_link_verify_schema",
    "update_profile_schema",
    "refresh_token_schema",
    "resend_otp_schema",
]
