"""
Tasks package for ExamSaaS platform.
Celery task definitions.
"""
import logging

logger = logging.getLogger(__name__)

__all__ = [
    "send_otp_email_task",
    "send_welcome_email_task",
    "send_password_reset_email_task",
    "send_magic_link_email_task",
    "send_result_notification_task",
    "send_certificate_email_task",
    "send_renewal_reminder_task",
    "send_admin_weekly_summary_task",
    "send_exam_invitation_email_task",
    "send_payment_failed_email_task",
    "process_pdf_with_groq_task",
    "generate_ai_recommendation_task",
    "generate_and_upload_certificate_task",
    "auto_close_expired_exams_task",
    "auto_publish_scheduled_exams_task",
    "generate_questions_with_ai_task",
    "reset_monthly_ai_usage_task",
]

logger.info("All tasks loaded and exported")
