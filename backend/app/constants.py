"""
Constants module containing all Enums for ExamSaaS platform.
"""
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class Role(str, Enum):
    """User roles in the system."""
    SUPER_ADMIN = "super_admin"
    ORG_ADMIN = "org_admin"
    EXAMINER = "examiner"
    STUDENT = "student"
    
    @classmethod
    def values(cls) -> list[str]:
        return [role.value for role in cls]


class ExamStatus(str, Enum):
    """Exam lifecycle statuses."""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    LIVE = "live"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    
    @classmethod
    def values(cls) -> list[str]:
        return [status.value for status in cls]


class AttemptStatus(str, Enum):
    """Student exam attempt statuses."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    AUTO_SUBMITTED = "auto_submitted"
    GRADED = "graded"
    REVIEWED = "reviewed"
    EXPIRED = "expired"
    
    @classmethod
    def values(cls) -> list[str]:
        return [status.value for status in cls]


class QuestionType(str, Enum):
    """Question types supported by the platform."""
    MULTIPLE_CHOICE = "multiple_choice"
    MULTIPLE_SELECT = "multiple_select"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    LONG_ANSWER = "long_answer"
    CODING = "coding"
    FILE_UPLOAD = "file_upload"
    
    @classmethod
    def values(cls) -> list[str]:
        return [qtype.value for qtype in cls]


class SubscriptionPlan(str, Enum):
    """Subscription plan types."""
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    
    @classmethod
    def values(cls) -> list[str]:
        return [plan.value for plan in cls]


class SubscriptionStatus(str, Enum):
    """Subscription status values."""
    ACTIVE = "active"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    TRIAL = "trial"
    
    @classmethod
    def values(cls) -> list[str]:
        return [status.value for status in cls]


class PaymentStatus(str, Enum):
    """Payment transaction statuses."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"
    
    @classmethod
    def values(cls) -> list[str]:
        return [status.value for status in cls]


class PaymentMethod(str, Enum):
    """Supported payment methods."""
    RAZORPAY = "razorpay"
    STRIPE = "stripe"
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"
    
    @classmethod
    def values(cls) -> list[str]:
        return [method.value for method in cls]


class NotificationType(str, Enum):
    """System notification types."""
    EXAM_INVITATION = "exam_invitation"
    EXAM_REMINDER = "exam_reminder"
    RESULT_PUBLISHED = "result_published"
    CERTIFICATE_GENERATED = "certificate_generated"
    SUBSCRIPTION_EXPIRING = "subscription_expiring"
    PAYMENT_RECEIVED = "payment_received"
    SYSTEM_ALERT = "system_alert"
    
    @classmethod
    def values(cls) -> list[str]:
        return [ntype.value for ntype in cls]


class LogLevel(str, Enum):
    """Logging levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class AuditAction(str, Enum):
    """Audit log action types."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    EXPORT = "export"
    IMPORT = "import"
    APPROVE = "approve"
    REJECT = "reject"
    
    @classmethod
    def values(cls) -> list[str]:
        return [action.value for action in cls]


# Celery task queue names
class CeleryQueues:
    """Celery queue names for task routing."""
    DEFAULT = "default"
    EMAIL = "email"
    PDF = "pdf"
    RESULTS = "results"
    CERTIFICATES = "certificates"
    AI_QUEUE = "ai_queue"
    
    @classmethod
    def all(cls) -> list[str]:
        return [
            cls.DEFAULT,
            cls.EMAIL,
            cls.PDF,
            cls.RESULTS,
            cls.CERTIFICATES,
            cls.AI_QUEUE
        ]


# Pagination defaults
class PaginationDefaults:
    """Default pagination values."""
    DEFAULT_PAGE = 1
    DEFAULT_PER_PAGE = 20
    MAX_PER_PAGE = 100
    MIN_PER_PAGE = 1


# File size limits
class FileLimits:
    """File upload size limits in bytes."""
    IMAGE_MAX_SIZE = 5 * 1024 * 1024  # 5MB
    PDF_MAX_SIZE = 30 * 1024 * 1024  # 30MB
    VIDEO_MAX_SIZE = 100 * 1024 * 1024  # 100MB
    ALLOWED_IMAGE_TYPES = ["jpg", "jpeg", "png", "gif", "webp"]
    ALLOWED_DOCUMENT_TYPES = ["pdf", "doc", "docx", "xls", "xlsx"]
    ALLOWED_VIDEO_TYPES = ["mp4", "webm", "mov"]


# API rate limits
class RateLimits:
    """API rate limit values."""
    DEFAULT = "100 per minute"
    AUTH = "10 per minute"
    EXAM_SUBMISSION = "30 per minute"
    FILE_UPLOAD = "10 per minute"
    REPORT_GENERATION = "5 per minute"


logger.info("Constants module initialized with all enums")
