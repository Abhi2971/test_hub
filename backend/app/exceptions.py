"""
Custom exception classes for ExamSaaS platform.
All API exceptions should inherit from ExamSaaSException.
"""
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ExamSaaSException(Exception):
    """
    Base exception for all ExamSaaS application errors.
    
    Attributes:
        message: Human-readable error message
        status_code: HTTP status code
        errors: Additional field-specific errors dict
        code: Error code for client-side handling
    """
    
    def __init__(
        self,
        message: str = "An error occurred",
        status_code: int = 400,
        errors: Optional[Dict[str, Any]] = None,
        code: Optional[str] = None
    ):
        self.message = message
        self.status_code = status_code
        self.errors = errors or {}
        self.code = code or self.__class__.__name__.replace("Error", "").upper()
        super().__init__(message)
        logger.debug(f"Exception raised: {self.__class__.__name__} - {message}")


class AuthenticationError(ExamSaaSException):
    """Raised when authentication fails."""
    
    def __init__(
        self,
        message: str = "Authentication required",
        errors: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=401,
            errors=errors,
            code="AUTHENTICATION_REQUIRED"
        )


class AuthorizationError(ExamSaaSException):
    """Raised when user lacks required permissions."""
    
    def __init__(
        self,
        message: str = "Access denied",
        errors: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=403,
            errors=errors,
            code="ACCESS_DENIED"
        )


class NotFoundError(ExamSaaSException):
    """Raised when a resource is not found."""
    
    def __init__(
        self,
        message: str = "Resource not found",
        errors: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=404,
            errors=errors,
            code="NOT_FOUND"
        )


class ValidationError(ExamSaaSException):
    """Raised when input validation fails."""
    
    def __init__(
        self,
        message: str = "Validation failed",
        errors: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=422,
            errors=errors,
            code="VALIDATION_ERROR"
        )


class ConflictError(ExamSaaSException):
    """Raised when there's a resource conflict (e.g., duplicate email)."""
    
    def __init__(
        self,
        message: str = "Resource conflict",
        errors: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=409,
            errors=errors,
            code="CONFLICT"
        )


class InsufficientBalanceError(ExamSaaSException):
    """Raised when wallet has insufficient balance."""
    
    def __init__(
        self,
        message: str = "Insufficient balance",
        errors: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=422,
            errors=errors,
            code="INSUFFICIENT_BALANCE"
        )


class SubscriptionRequiredError(ExamSaaSException):
    """Raised when subscription is required or expired."""
    
    def __init__(
        self,
        message: str = "Active subscription required",
        errors: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=402,
            errors=errors,
            code="SUBSCRIPTION_REQUIRED"
        )


class FeatureNotAvailableError(ExamSaaSException):
    """Raised when a feature is not available in current plan."""
    
    def __init__(
        self,
        message: str = "Feature not available in your plan",
        errors: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=403,
            errors=errors,
            code="FEATURE_NOT_AVAILABLE"
        )


class InstituteSuspendedError(ExamSaaSException):
    """Raised when institute is suspended."""
    
    def __init__(
        self,
        message: str = "Institute has been suspended",
        errors: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=403,
            errors=errors,
            code="INSTITUTE_SUSPENDED"
        )


class RateLimitError(ExamSaaSException):
    """Raised when rate limit is exceeded."""
    
    def __init__(
        self,
        message: str = "Too many requests",
        retry_after: int = 60,
        errors: Optional[Dict[str, Any]] = None
    ):
        errors = errors or {}
        errors["retry_after"] = retry_after
        super().__init__(
            message=message,
            status_code=429,
            errors=errors,
            code="RATE_LIMIT_EXCEEDED"
        )


class PaymentError(ExamSaaSException):
    """Raised when payment processing fails."""
    
    def __init__(
        self,
        message: str = "Payment failed",
        errors: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=402,
            errors=errors,
            code="PAYMENT_ERROR"
        )


class ExamInProgressError(ExamSaaSException):
    """Raised when attempting to modify an in-progress exam."""
    
    def __init__(
        self,
        message: str = "Cannot modify exam while in progress",
        errors: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=409,
            errors=errors,
            code="EXAM_IN_PROGRESS"
        )


class ExamAttemptError(ExamSaaSException):
    """Raised when exam attempt validation fails."""
    
    def __init__(
        self,
        message: str = "Exam attempt error",
        errors: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=400,
            errors=errors,
            code="EXAM_ATTEMPT_ERROR"
        )


class CertificateError(ExamSaaSException):
    """Raised when certificate generation or validation fails."""
    
    def __init__(
        self,
        message: str = "Certificate error",
        errors: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=400,
            errors=errors,
            code="CERTIFICATE_ERROR"
        )


class AIError(ExamSaaSException):
    """Raised when AI service fails."""
    
    def __init__(
        self,
        message: str = "AI service error",
        errors: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=503,
            errors=errors,
            code="AI_ERROR"
        )


class ServiceUnavailableError(ExamSaaSException):
    """Raised when a service is temporarily unavailable."""
    
    def __init__(
        self,
        message: str = "Service temporarily unavailable",
        errors: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=503,
            errors=errors,
            code="SERVICE_UNAVAILABLE"
        )


logger.info("Custom exception classes loaded")
