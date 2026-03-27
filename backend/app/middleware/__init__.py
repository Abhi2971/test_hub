"""
Middleware package for ExamSaaS platform.
Contains all middleware components.
"""
from app.middleware.request_logger import RequestLogger, request_logger, log_audit_event, get_request_id
from app.middleware.rate_limiter import RateLimiter, rate_limiter
from app.middleware.error_handler import ErrorHandler, error_handler
from app.middleware.institute_context import (
    InstituteContext,
    institute_context,
    require_institute,
    get_current_institute,
    get_current_institute_id,
)
from app.middleware.subscription_check import (
    SubscriptionChecker,
    subscription_checker,
    check_feature,
)
from app.middleware.security_headers import SecurityHeaders, security_headers, get_nonce

__all__ = [
    "RequestLogger",
    "request_logger",
    "log_audit_event",
    "get_request_id",
    "RateLimiter",
    "rate_limiter",
    "ErrorHandler",
    "error_handler",
    "InstituteContext",
    "institute_context",
    "require_institute",
    "get_current_institute",
    "get_current_institute_id",
    "SubscriptionChecker",
    "subscription_checker",
    "check_feature",
    "SecurityHeaders",
    "security_headers",
    "get_nonce",
]
