"""
Services package for ExamSaaS platform.
Business logic services.
"""
from app.services.auth_service import (
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
    create_magic_link as auth_create_magic_link,
    verify_magic_link as auth_verify_magic_link,
    resend_otp,
)

import app.services.exam_service as exam_service
import app.services.question_service as question_service
import app.services.attempt_service as attempt_service
import app.services.result_service as result_service
import app.services.wallet_service as wallet_service
import app.services.payment_service as payment_service
import app.services.subscription_service as subscription_service

__all__ = [
    "AuthServiceError",
    "EmailExistsError",
    "InvalidCredentialsError",
    "AccountSuspendedError",
    "EmailNotVerifiedError",
    "InvalidTokenError",
    "InvalidOtpError",
    "UserNotFoundError",
    "GoogleAuthError",
    "InstituteSuspendedError",
    "register_user",
    "verify_email",
    "authenticate_user",
    "authenticate_google",
    "refresh_access_token",
    "logout_user",
    "request_password_reset",
    "reset_password_with_otp",
    "get_user_profile",
    "update_user_profile",
    "auth_create_magic_link",
    "auth_verify_magic_link",
    "resend_otp",
    "exam_service",
    "question_service",
    "attempt_service",
    "result_service",
    "wallet_service",
    "payment_service",
    "subscription_service",
]
