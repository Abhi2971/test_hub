"""
Models package for ExamSaaS platform.
Exports all MongoEngine document models.
"""
import logging

logger = logging.getLogger(__name__)

from app.models.institute import Institute
from app.models.user import User, FaceData
from app.models.student_profile import StudentProfile
from app.models.teacher_profile import TeacherProfile
from app.models.plan import Plan, FeatureFlags
from app.models.subscription import Subscription
from app.models.wallet import Wallet
from app.models.wallet_transaction import WalletTransaction, TransactionType, TransactionSource, TransactionPurpose
from app.models.payment import Payment
from app.models.exam import Exam, Schedule, Security
from app.models.question import Question, QuestionOption
from app.models.exam_attempt import ExamAttempt, Answer, Violation
from app.models.result import Result, PerQuestionAnalysis, TopicPerformance
from app.models.ai_recommendation import AIRecommendation
from app.models.ebook import Ebook
from app.models.pdf_upload import PDFUpload
from app.models.certificate import Certificate
from app.models.support_ticket import SupportTicket, TicketAttachment
from app.models.ticket_message import TicketMessage, MessageAttachment
from app.models.audit_log import AuditLog

__all__ = [
    "Institute",
    "User",
    "FaceData",
    "StudentProfile",
    "TeacherProfile",
    "Plan",
    "FeatureFlags",
    "Subscription",
    "Wallet",
    "WalletTransaction",
    "TransactionType",
    "TransactionSource",
    "TransactionPurpose",
    "Payment",
    "Exam",
    "Schedule",
    "Security",
    "Question",
    "QuestionOption",
    "ExamAttempt",
    "Answer",
    "Violation",
    "Result",
    "PerQuestionAnalysis",
    "TopicPerformance",
    "AIRecommendation",
    "Ebook",
    "PDFUpload",
    "Certificate",
    "SupportTicket",
    "TicketAttachment",
    "TicketMessage",
    "MessageAttachment",
    "AuditLog",
]

logger.info("All models loaded and exported")
