"""
Email tasks for ExamSaaS platform.
Celery tasks for sending transactional emails.
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any

logger = logging.getLogger(__name__)

BRAND_COLOR = "#2563EB"
BRAND_NAME = "ExamSaaS"


def _get_email_config() -> Dict[str, Any]:
    """Get email configuration from Flask app."""
    try:
        from flask import current_app
        return {
            "host": current_app.config.get("SMTP_HOST", "smtp.gmail.com"),
            "port": current_app.config.get("SMTP_PORT", 587),
            "user": current_app.config.get("SMTP_USER", ""),
            "password": current_app.config.get("SMTP_PASSWORD", ""),
            "from_email": current_app.config.get("EMAIL_FROM", "noreply@examsaas.com"),
            "from_name": current_app.config.get("EMAIL_FROM_NAME", "ExamSaaS"),
            "app_url": current_app.config.get("APP_URL", "http://localhost:5173"),
        }
    except RuntimeError:
        return {
            "host": "smtp.gmail.com",
            "port": 587,
            "user": "",
            "password": "",
            "from_email": "noreply@examsaas.com",
            "from_name": "ExamSaaS",
            "app_url": "http://localhost:5173",
        }


def _send_email(to_email: str, subject: str, html_body: str, text_body: str = None) -> bool:
    """Send email using email service."""
    try:
        from app.services.email_service import EmailService
        config = _get_email_config()
        service = EmailService(
            host=config["host"],
            port=config["port"],
            user=config["user"],
            password=config["password"],
            from_email=config["from_email"],
            from_name=config["from_name"],
        )
        return service.send_email(to_email, subject, html_body, text_body)
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False


def _build_html(content: str) -> str:
    """Wrap content in branded HTML template."""
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{BRAND_NAME}</title>
</head>
<body style="margin:0;padding:0;background-color:#f5f5f5;font-family:Arial,sans-serif;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f5f5f5;padding:20px;">
        <tr>
            <td align="center">
                <table width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff;border-radius:8px;overflow:hidden;">
                    <tr>
                        <td style="background-color:{BRAND_COLOR};padding:24px;text-align:center;">
                            <h1 style="color:#ffffff;margin:0;font-size:24px;">{BRAND_NAME}</h1>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding:32px;">
                            {content}
                        </td>
                    </tr>
                    <tr>
                        <td style="background-color:#f9fafb;padding:20px;text-align:center;border-top:1px solid #e5e7eb;">
                            <p style="color:#6b7280;font-size:12px;margin:0;">&copy; {datetime.now().year} {BRAND_NAME}. All rights reserved.</p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""


def _otp_email_html(otp: str, purpose: str) -> str:
    """Build OTP email HTML."""
    if purpose == "forgot_password":
        subject = "Reset your ExamSaaS password"
        title = "Password Reset"
    else:
        subject = "Your ExamSaaS OTP"
        title = "Email Verification"
    
    content = f"""
    <h2 style="color:#1f2937;margin:0 0 16px;">{title}</h2>
    <p style="color:#4b5563;margin:0 0 24px;">Your one-time password is:</p>
    <div style="background-color:#f3f4f6;border:2px dashed {BRAND_COLOR};border-radius:8px;padding:24px;text-align:center;margin:0 0 24px;">
        <span style="font-size:32px;font-weight:bold;letter-spacing:8px;color:{BRAND_COLOR};">{otp}</span>
    </div>
    <p style="color:#6b7280;font-size:14px;margin:0 0 16px;">This code expires in <strong>10 minutes</strong>. Do not share it with anyone.</p>
    <p style="color:#9ca3af;font-size:12px;margin:0;">If you didn't request this, please ignore this email.</p>
    """
    return _build_html(content), subject


def _welcome_email_html(name: str, role: str) -> str:
    """Build welcome email HTML based on role."""
    subject = "Welcome to ExamSaaS!"
    
    if role in ["student_registered", "student_assigned"]:
        content = f"""
        <h2 style="color:#1f2937;margin:0 0 16px;">Welcome, {name}!</h2>
        <p style="color:#4b5563;margin:0 0 24px;">Thank you for joining ExamSaaS. Your account has been created successfully.</p>
        <p style="color:#4b5563;margin:0 0 24px;">With ExamSaaS, you can:</p>
        <ul style="color:#4b5563;margin:0 0 24px;padding-left:20px;">
            <li>Take exams online from anywhere</li>
            <li>Track your progress and results</li>
            <li>Earn certificates</li>
            <li>Access personalized study recommendations</li>
        </ul>
        <p style="color:#4b5563;margin:0 0 24px;">Get started by exploring your dashboard!</p>
        <p style="color:#6b7280;font-size:12px;margin:0;">Questions? Reply to this email or visit our help center.</p>
        """
    elif role in ["teacher", "admin_college", "admin_public"]:
        content = f"""
        <h2 style="color:#1f2937;margin:0 0 16px;">Welcome, {name}!</h2>
        <p style="color:#4b5563;margin:0 0 24px;">Thank you for joining ExamSaaS. Your educator account is ready.</p>
        <p style="color:#4b5563;margin:0 0 24px;">As an educator, you can:</p>
        <ul style="color:#4b5563;margin:0 0 24px;padding-left:20px;">
            <li>Create and publish exams</li>
            <li>Import questions from PDFs using AI</li>
            <li>Track student performance</li>
            <li>Generate certificates for successful students</li>
        </ul>
        <p style="color:#4b5563;margin:0 0 24px;"><strong>Quick start:</strong> Go to Exams → Create New Exam to get started!</p>
        <p style="color:#6b7280;font-size:12px;margin:0;">Questions? Reply to this email or visit our help center.</p>
        """
    else:
        content = f"""
        <h2 style="color:#1f2937;margin:0 0 16px;">Welcome, {name}!</h2>
        <p style="color:#4b5563;margin:0 0 24px;">Thank you for joining ExamSaaS. Your account has been created successfully.</p>
        <p style="color:#4b5563;margin:0 0 24px;">Get started by exploring your dashboard!</p>
        """
    
    return _build_html(content), subject


def _password_reset_email_html(name: str, otp: str) -> str:
    """Build password reset email HTML."""
    subject = "Reset your ExamSaaS password"
    
    content = f"""
    <h2 style="color:#1f2937;margin:0 0 16px;">Password Reset Request</h2>
    <p style="color:#4b5563;margin:0 0 24px;">Hi {name},</p>
    <p style="color:#4b5563;margin:0 0 24px;">We received a request to reset your password. Use this OTP to create a new password:</p>
    <div style="background-color:#f3f4f6;border:2px dashed #dc2626;border-radius:8px;padding:24px;text-align:center;margin:0 0 24px;">
        <span style="font-size:32px;font-weight:bold;letter-spacing:8px;color:#dc2626;">{otp}</span>
    </div>
    <p style="color:#6b7280;font-size:14px;margin:0 0 16px;">This code expires in <strong>10 minutes</strong>.</p>
    <p style="color:#9ca3af;font-size:12px;margin:0;">If you didn't request this password reset, please ignore this email. Your password will remain unchanged.</p>
    """
    
    return _build_html(content), subject


def _magic_link_email_html(magic_link_url: str, exam_title: str, exam_start_at: str, valid_hours: int) -> str:
    """Build magic link email HTML."""
    subject = f"Your exam link: {exam_title}"
    
    content = f"""
    <h2 style="color:#1f2937;margin:0 0 16px;">Your Exam is Ready</h2>
    <p style="color:#4b5563;margin:0 0 24px;">You have been granted access to:</p>
    <div style="background-color:#f3f4f6;border-radius:8px;padding:20px;margin:0 0 24px;">
        <h3 style="color:{BRAND_COLOR};margin:0 0 8px;">{exam_title}</h3>
        <p style="color:#6b7280;font-size:14px;margin:0;">Starts at: {exam_start_at}</p>
    </div>
    <p style="color:#4b5563;margin:0 0 24px;text-align:center;">
        <a href="{magic_link_url}" style="display:inline-block;background-color:{BRAND_COLOR};color:#ffffff;padding:14px 32px;text-decoration:none;border-radius:6px;font-weight:bold;">Access Exam</a>
    </p>
    <p style="color:#9ca3af;font-size:12px;margin:0 0 16px;"><strong>Important:</strong></p>
    <ul style="color:#6b7280;font-size:14px;margin:0 0 24px;padding-left:20px;">
        <li>This link is valid for {valid_hours} hour(s)</li>
        <li>Ensure you have a stable internet connection</li>
        <li>Keep this browser window open during the exam</li>
    </ul>
    <p style="color:#9ca3af;font-size:12px;margin:0;">If the button doesn't work, copy and paste this link into your browser:</p>
    <p style="color:#9ca3af;font-size:12px;word-break:break-all;margin:8px 0 0;">{magic_link_url}</p>
    """
    
    return _build_html(content), subject


def _result_notification_html(
    student_name: str,
    exam_title: str,
    score: float,
    total_marks: float,
    percentage: float,
    grade: str,
    passed: bool,
    certificate_url: str = None,
) -> str:
    """Build result notification email HTML."""
    if passed:
        subject = f"Congratulations! Your result for {exam_title}"
        status_color = "#059669"
        status_text = "PASSED"
        status_message = "Congratulations on passing! You can download your certificate below."
    else:
        subject = f"Your result is ready: {exam_title}"
        status_color = "#dc2626"
        status_text = "NOT PASSED"
        status_message = "Keep practicing! Review the topics you struggled with and try again."
    
    cert_section = ""
    if passed and certificate_url:
        cert_section = f"""
        <p style="text-align:center;margin:24px 0;">
            <a href="{certificate_url}" style="display:inline-block;background-color:#059669;color:#ffffff;padding:14px 32px;text-decoration:none;border-radius:6px;font-weight:bold;">Download Certificate</a>
        </p>
        """
    
    content = f"""
    <h2 style="color:#1f2937;margin:0 0 16px;">Hi {student_name}!</h2>
    <p style="color:#4b5563;margin:0 0 24px;">Your results for <strong>{exam_title}</strong> are now available.</p>
    <div style="background-color:#f3f4f6;border-radius:8px;padding:24px;margin:0 0 24px;">
        <table width="100%" cellpadding="0" cellspacing="0">
            <tr>
                <td style="padding:8px 0;border-bottom:1px solid #e5e7eb;">
                    <span style="color:#6b7280;">Score</span>
                </td>
                <td style="padding:8px 0;border-bottom:1px solid #e5e7eb;text-align:right;">
                    <strong style="color:#1f2937;">{score:.1f} / {total_marks:.1f}</strong>
                </td>
            </tr>
            <tr>
                <td style="padding:8px 0;border-bottom:1px solid #e5e7eb;">
                    <span style="color:#6b7280;">Percentage</span>
                </td>
                <td style="padding:8px 0;border-bottom:1px solid #e5e7eb;text-align:right;">
                    <strong style="color:#1f2937;">{percentage:.1f}%</strong>
                </td>
            </tr>
            <tr>
                <td style="padding:8px 0;border-bottom:1px solid #e5e7eb;">
                    <span style="color:#6b7280;">Grade</span>
                </td>
                <td style="padding:8px 0;border-bottom:1px solid #e5e7eb;text-align:right;">
                    <strong style="color:#1f2937;">{grade}</strong>
                </td>
            </tr>
            <tr>
                <td style="padding:8px 0;">
                    <span style="color:#6b7280;">Status</span>
                </td>
                <td style="padding:8px 0;text-align:right;">
                    <span style="display:inline-block;background-color:{status_color};color:#ffffff;padding:4px 12px;border-radius:4px;font-size:12px;font-weight:bold;">{status_text}</span>
                </td>
            </tr>
        </table>
    </div>
    <p style="color:#4b5563;margin:0 0 24px;">{status_message}</p>
    {cert_section}
    <p style="color:#6b7280;font-size:12px;margin:0;">View detailed results in your ExamSaaS dashboard.</p>
    """
    
    return _build_html(content), subject


def _certificate_email_html(student_name: str, exam_title: str, certificate_url: str, certificate_id: str) -> str:
    """Build certificate email HTML."""
    subject = f"Certificate: {exam_title} — ExamSaaS"
    
    content = f"""
    <h2 style="color:#1f2937;margin:0 0 16px;">Congratulations, {student_name}!</h2>
    <p style="color:#4b5563;margin:0 0 24px;">You have successfully completed <strong>{exam_title}</strong> and earned your certificate!</p>
    <div style="background-color:#fef3c7;border:2px solid #d97706;border-radius:8px;padding:20px;margin:0 0 24px;text-align:center;">
        <p style="color:#92400e;font-size:14px;margin:0 0 8px;">Certificate ID</p>
        <p style="color:#92400e;font-size:18px;font-weight:bold;margin:0;letter-spacing:2px;">{certificate_id}</p>
    </div>
    <p style="text-align:center;margin:0 0 24px;">
        <a href="{certificate_url}" style="display:inline-block;background-color:#059669;color:#ffffff;padding:14px 32px;text-decoration:none;border-radius:6px;font-weight:bold;">View Certificate</a>
    </p>
    <p style="color:#6b7280;font-size:12px;margin:0;">Share your achievement on LinkedIn or add it to your portfolio!</p>
    """
    
    return _build_html(content), subject


def _renewal_reminder_html(name: str, plan_name: str, expiry_date: str, days_remaining: int, renewal_url: str) -> str:
    """Build renewal reminder email HTML."""
    subject = f"Your ExamSaaS subscription expires in {days_remaining} day(s)"
    
    urgency_color = "#dc2626" if days_remaining <= 3 else "#f59e0b"
    
    content = f"""
    <h2 style="color:#1f2937;margin:0 0 16px;">Subscription Reminder</h2>
    <p style="color:#4b5563;margin:0 0 24px;">Hi {name},</p>
    <div style="background-color:#fef2f2;border:2px solid {urgency_color};border-radius:8px;padding:20px;margin:0 0 24px;text-align:center;">
        <p style="color:{urgency_color};font-size:14px;margin:0 0 8px;">Your <strong>{plan_name}</strong> plan expires in</p>
        <p style="color:{urgency_color};font-size:36px;font-weight:bold;margin:0;">{days_remaining} day(s)</p>
        <p style="color:#6b7280;font-size:14px;margin:8px 0 0;">on {expiry_date}</p>
    </div>
    <p style="color:#4b5563;margin:0 0 24px;">To continue enjoying uninterrupted access to ExamSaaS, please renew before expiration.</p>
    <p style="text-align:center;margin:0 0 24px;">
        <a href="{renewal_url}" style="display:inline-block;background-color:{BRAND_COLOR};color:#ffffff;padding:14px 32px;text-decoration:none;border-radius:6px;font-weight:bold;">Renew Now</a>
    </p>
    <p style="color:#9ca3af;font-size:12px;margin:0;">Questions? Reply to this email or contact support.</p>
    """
    
    return _build_html(content), subject


def _admin_weekly_summary_html(
    name: str,
    exams_created: int,
    students_added: int,
    attempts_taken: int,
    pass_rate: float,
) -> str:
    """Build admin weekly summary HTML."""
    subject = "Your Weekly ExamSaaS Summary"
    
    content = f"""
    <h2 style="color:#1f2937;margin:0 0 16px;">Weekly Summary</h2>
    <p style="color:#4b5563;margin:0 0 24px;">Hi {name},</p>
    <p style="color:#4b5563;margin:0 0 24px;">Here's your weekly activity summary:</p>
    <div style="background-color:#f3f4f6;border-radius:8px;padding:24px;margin:0 0 24px;">
        <table width="100%" cellpadding="0" cellspacing="0">
            <tr>
                <td style="padding:12px 0;border-bottom:1px solid #e5e7eb;">
                    <span style="color:#6b7280;">Exams Created</span>
                </td>
                <td style="padding:12px 0;border-bottom:1px solid #e5e7eb;text-align:right;">
                    <strong style="color:#1f2937;font-size:20px;">{exams_created}</strong>
                </td>
            </tr>
            <tr>
                <td style="padding:12px 0;border-bottom:1px solid #e5e7eb;">
                    <span style="color:#6b7280;">Students Added</span>
                </td>
                <td style="padding:12px 0;border-bottom:1px solid #e5e7eb;text-align:right;">
                    <strong style="color:#1f2937;font-size:20px;">{students_added}</strong>
                </td>
            </tr>
            <tr>
                <td style="padding:12px 0;border-bottom:1px solid #e5e7eb;">
                    <span style="color:#6b7280;">Attempts Taken</span>
                </td>
                <td style="padding:12px 0;border-bottom:1px solid #e5e7eb;text-align:right;">
                    <strong style="color:#1f2937;font-size:20px;">{attempts_taken}</strong>
                </td>
            </tr>
            <tr>
                <td style="padding:12px 0;">
                    <span style="color:#6b7280;">Pass Rate</span>
                </td>
                <td style="padding:12px 0;text-align:right;">
                    <strong style="color:#059669;font-size:20px;">{pass_rate:.1f}%</strong>
                </td>
            </tr>
        </table>
    </div>
    <p style="color:#6b7280;font-size:12px;margin:0;">Data covers the last 7 days. Log in to your dashboard for more insights.</p>
    """
    
    return _build_html(content), subject


def _payment_failed_email_html(name: str, razorpay_order_id: str, amount_paise: int) -> str:
    """Build payment failed notification email HTML."""
    subject = "Payment Failed — ExamSaaS"
    amount_rupees = amount_paise / 100.0 if amount_paise else 0
    
    content = f"""
    <h2 style="color:#1f2937;margin:0 0 16px;">Payment Failed</h2>
    <p style="color:#4b5563;margin:0 0 24px;">Hi {name},</p>
    <p style="color:#4b5563;margin:0 0 24px;">Your payment for ExamSaaS was unsuccessful. No amount has been deducted from your account.</p>
    <div style="background-color:#fef2f2;border:2px solid #dc2626;border-radius:8px;padding:20px;margin:0 0 24px;">
        <table width="100%" cellpadding="0" cellspacing="0">
            <tr>
                <td style="padding:4px 0;"><span style="color:#6b7280;">Order ID</span></td>
                <td style="padding:4px 0;text-align:right;"><strong style="color:#1f2937;">{razorpay_order_id}</strong></td>
            </tr>
            <tr>
                <td style="padding:4px 0;"><span style="color:#6b7280;">Amount</span></td>
                <td style="padding:4px 0;text-align:right;"><strong style="color:#1f2937;">₹{amount_rupees:.2f}</strong></td>
            </tr>
        </table>
    </div>
    <p style="color:#4b5563;margin:0 0 24px;">Please try again or use a different payment method. If the problem persists, contact our support team.</p>
    <p style="color:#6b7280;font-size:12px;margin:0;">Questions? Reply to this email or visit our help center.</p>
    """
    
    return _build_html(content), subject


def _exam_invitation_email_html(
    name: str,
    exam_title: str,
    exam_date: str,
    duration: int,
    total_marks: float,
    exam_url: str,
) -> str:
    """Build exam invitation email HTML."""
    subject = f"You've been invited to: {exam_title}"
    
    content = f"""
    <h2 style="color:#1f2937;margin:0 0 16px;">Exam Invitation</h2>
    <p style="color:#4b5563;margin:0 0 24px;">Hi {name},</p>
    <p style="color:#4b5563;margin:0 0 24px;">You have been invited to take an exam:</p>
    <div style="background-color:#f3f4f6;border-radius:8px;padding:20px;margin:0 0 24px;">
        <h3 style="color:{BRAND_COLOR};margin:0 0 16px;">{exam_title}</h3>
        <table width="100%" cellpadding="0" cellspacing="0">
            <tr>
                <td style="padding:4px 0;"><span style="color:#6b7280;">Date:</span></td>
                <td style="padding:4px 0;text-align:right;"><strong style="color:#1f2937;">{exam_date}</strong></td>
            </tr>
            <tr>
                <td style="padding:4px 0;"><span style="color:#6b7280;">Duration:</span></td>
                <td style="padding:4px 0;text-align:right;"><strong style="color:#1f2937;">{duration} minutes</strong></td>
            </tr>
            <tr>
                <td style="padding:4px 0;"><span style="color:#6b7280;">Total Marks:</span></td>
                <td style="padding:4px 0;text-align:right;"><strong style="color:#1f2937;">{total_marks:.1f}</strong></td>
            </tr>
        </table>
    </div>
    <p style="text-align:center;margin:0 0 24px;">
        <a href="{exam_url}" style="display:inline-block;background-color:{BRAND_COLOR};color:#ffffff;padding:14px 32px;text-decoration:none;border-radius:6px;font-weight:bold;">Take Exam</a>
    </p>
    <p style="color:#9ca3af;font-size:12px;margin:0;">Make sure you have a stable internet connection before starting.</p>
    """
    
    return _build_html(content), subject


try:
    from celery import Task
    
    class EmailTask(Task):
        """Base task class for email operations."""
        max_retries = 2
        default_retry_delay = 30
        acks_late = True
        reject_on_worker_lost = True
        
        def on_failure(self, exc, task_id, args, kwargs, einfo):
            logger.error(f"Email task {task_id} failed: {exc}")
            super().on_failure(exc, task_id, args, kwargs, einfo)
    
    def _celery_task(func):
        """Decorator to make a function a Celery task."""
        from app.extensions import celery
        return celery.task(
            bind=True,
            max_retries=2,
            default_retry_delay=30,
            acks_late=True,
            reject_on_worker_lost=True,
        )(func)
    
    @_celery_task
    def send_otp_email_task(self, email: str, otp: str, purpose: str) -> dict:
        """
        Send OTP email.
        
        Args:
            email: Recipient email
            otp: 6-digit OTP
            purpose: 'verify_email' or 'forgot_password'
        
        Returns:
            dict with status
        """
        try:
            html, subject = _otp_email_html(otp, purpose)
            success = _send_email(email, subject, html)
            
            if not success and self.request.retries < self.max_retries:
                raise self.retry(exc=Exception("Email send failed"), countdown=30 * (2 ** self.request.retries))
            
            return {"status": "sent" if success else "failed", "to": email}
        except Exception as exc:
            logger.exception(f"send_otp_email_task failed: {exc}")
            if self.request.retries < self.max_retries:
                raise self.retry(exc=exc, countdown=30 * (2 ** self.request.retries))
            return {"status": "failed", "error": str(exc), "to": email}
    
    @_celery_task
    def send_welcome_email_task(self, email: str, name: str, role: str) -> dict:
        """
        Send welcome email based on role.
        
        Args:
            email: Recipient email
            name: User's name
            role: User role
        
        Returns:
            dict with status
        """
        try:
            html, subject = _welcome_email_html(name, role)
            success = _send_email(email, subject, html)
            
            if not success and self.request.retries < self.max_retries:
                raise self.retry(exc=Exception("Email send failed"), countdown=30 * (2 ** self.request.retries))
            
            return {"status": "sent" if success else "failed", "to": email}
        except Exception as exc:
            logger.exception(f"send_welcome_email_task failed: {exc}")
            if self.request.retries < self.max_retries:
                raise self.retry(exc=exc, countdown=30 * (2 ** self.request.retries))
            return {"status": "failed", "error": str(exc), "to": email}
    
    @_celery_task
    def send_password_reset_email_task(self, email: str, name: str, otp: str) -> dict:
        """
        Send password reset email.
        
        Args:
            email: Recipient email
            name: User's name
            otp: 6-digit OTP
        
        Returns:
            dict with status
        """
        try:
            html, subject = _password_reset_email_html(name, otp)
            success = _send_email(email, subject, html)
            
            if not success and self.request.retries < self.max_retries:
                raise self.retry(exc=Exception("Email send failed"), countdown=30 * (2 ** self.request.retries))
            
            return {"status": "sent" if success else "failed", "to": email}
        except Exception as exc:
            logger.exception(f"send_password_reset_email_task failed: {exc}")
            if self.request.retries < self.max_retries:
                raise self.retry(exc=exc, countdown=30 * (2 ** self.request.retries))
            return {"status": "failed", "error": str(exc), "to": email}
    
    @_celery_task
    def send_magic_link_email_task(
        self,
        email: str,
        magic_link_url: str,
        exam_title: str,
        exam_start_at: str,
        valid_hours: int = 1,
    ) -> dict:
        """
        Send magic link email for exam access.
        
        Args:
            email: Recipient email
            magic_link_url: Full magic link URL
            exam_title: Exam title
            exam_start_at: Exam start datetime string
            valid_hours: Link validity in hours
        
        Returns:
            dict with status
        """
        try:
            html, subject = _magic_link_email_html(magic_link_url, exam_title, exam_start_at, valid_hours)
            success = _send_email(email, subject, html)
            
            if not success and self.request.retries < self.max_retries:
                raise self.retry(exc=Exception("Email send failed"), countdown=30 * (2 ** self.request.retries))
            
            return {"status": "sent" if success else "failed", "to": email}
        except Exception as exc:
            logger.exception(f"send_magic_link_email_task failed: {exc}")
            if self.request.retries < self.max_retries:
                raise self.retry(exc=exc, countdown=30 * (2 ** self.request.retries))
            return {"status": "failed", "error": str(exc), "to": email}
    
    @_celery_task
    def send_result_notification_task(
        self,
        student_email: str,
        student_name: str,
        exam_title: str,
        result_data: Dict[str, Any],
    ) -> dict:
        """
        Send result notification email.
        
        Args:
            student_email: Student's email
            student_name: Student's name
            exam_title: Exam title
            result_data: dict with score, total_marks, percentage, grade, passed
        
        Returns:
            dict with status
        """
        try:
            html, subject = _result_notification_html(
                student_name,
                exam_title,
                result_data.get("score", 0),
                result_data.get("total_marks", 0),
                result_data.get("percentage", 0),
                result_data.get("grade", "F"),
                result_data.get("passed", False),
                result_data.get("certificate_url"),
            )
            success = _send_email(student_email, subject, html)
            
            if not success and self.request.retries < self.max_retries:
                raise self.retry(exc=Exception("Email send failed"), countdown=30 * (2 ** self.request.retries))
            
            return {"status": "sent" if success else "failed", "to": student_email}
        except Exception as exc:
            logger.exception(f"send_result_notification_task failed: {exc}")
            if self.request.retries < self.max_retries:
                raise self.retry(exc=exc, countdown=30 * (2 ** self.request.retries))
            return {"status": "failed", "error": str(exc), "to": student_email}
    
    @_celery_task
    def send_certificate_email_task(
        self,
        student_email: str,
        student_name: str,
        exam_title: str,
        certificate_url: str,
        certificate_id: str,
    ) -> dict:
        """
        Send certificate email.
        
        Args:
            student_email: Student's email
            student_name: Student's name
            exam_title: Exam title
            certificate_url: Cloudinary certificate URL
            certificate_id: Certificate ID
        
        Returns:
            dict with status
        """
        try:
            html, subject = _certificate_email_html(student_name, exam_title, certificate_url, certificate_id)
            success = _send_email(student_email, subject, html)
            
            if not success and self.request.retries < self.max_retries:
                raise self.retry(exc=Exception("Email send failed"), countdown=30 * (2 ** self.request.retries))
            
            return {"status": "sent" if success else "failed", "to": student_email}
        except Exception as exc:
            logger.exception(f"send_certificate_email_task failed: {exc}")
            if self.request.retries < self.max_retries:
                raise self.retry(exc=exc, countdown=30 * (2 ** self.request.retries))
            return {"status": "failed", "error": str(exc), "to": student_email}
    
    @_celery_task
    def send_renewal_reminder_task(self, days_remaining: int) -> dict:
        """
        Send renewal reminder to all expiring institutes.
        Called by Celery beat with days_remaining = 7 | 3 | 1.
        
        Args:
            days_remaining: Days until expiration
        
        Returns:
            dict with sent count
        """
        try:
            from app.models import Institute, User
            
            expiry_date = datetime.now(timezone.utc) + timedelta(days=days_remaining)
            start_of_day = expiry_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = start_of_day + timedelta(days=1)
            
            from app.models import Subscription
            expiring_subs = Subscription.objects(
                status="active",
                expires_at__gte=start_of_day,
                expires_at__lt=end_of_day,
            )
            
            sent = 0
            failed = 0
            config = _get_email_config()
            
            for sub in expiring_subs:
                institute = sub.institute
                if not institute:
                    continue
                
                admin = User.objects(institute=institute, role__in=["admin_college", "admin_public"]).first()
                if not admin:
                    continue
                
                expiry_str = sub.expires_at.strftime("%B %d, %Y")
                renewal_url = f"{config['app_url']}/dashboard/subscription/renew"
                
                html, subject = _renewal_reminder_html(
                    admin.first_name or "Admin",
                    sub.plan.name if sub.plan else "Subscription",
                    expiry_str,
                    days_remaining,
                    renewal_url,
                )
                
                if _send_email(admin.email, subject, html):
                    sent += 1
                else:
                    failed += 1
            
            return {"sent": sent, "failed": failed, "days_remaining": days_remaining}
        except Exception as exc:
            logger.exception(f"send_renewal_reminder_task failed: {exc}")
            return {"error": str(exc), "days_remaining": days_remaining}
    
    @_celery_task
    def send_admin_weekly_summary_task(self) -> dict:
        """
        Send weekly summary to all active institute admins.
        Called every Monday at 08:00.
        
        Returns:
            dict with sent count
        """
        try:
            from app.models import User, Institute, Exam, ExamAttempt, Result
            
            now = datetime.now(timezone.utc)
            week_ago = now - timedelta(days=7)
            
            admins = User.objects(role__in=["admin_college", "admin_public"], is_active=True)
            
            sent = 0
            failed = 0
            
            for admin in admins:
                if not admin.institute:
                    continue
                
                institute = admin.institute
                
                exams_created = Exam.objects(
                    institute=institute,
                    created_at__gte=week_ago,
                ).count()
                
                students_added = User.objects(
                    institute=institute,
                    role__in=["student_registered", "student_assigned"],
                    created_at__gte=week_ago,
                ).count()
                
                exam_ids = [str(e.id) for e in Exam.objects(institute=institute)]
                attempts_taken = ExamAttempt.objects(
                    exam__in=exam_ids,
                    created_at__gte=week_ago,
                ).count()
                
                results = Result.objects(
                    exam__in=exam_ids,
                    created_at__gte=week_ago,
                )
                
                total_results = results.count()
                passed_results = results.filter(passed=True).count()
                pass_rate = (passed_results / total_results * 100) if total_results > 0 else 0.0
                
                html, subject = _admin_weekly_summary_html(
                    admin.first_name or "Admin",
                    exams_created,
                    students_added,
                    attempts_taken,
                    pass_rate,
                )
                
                if _send_email(admin.email, subject, html):
                    sent += 1
                else:
                    failed += 1
            
            return {"sent": sent, "failed": failed}
        except Exception as exc:
            logger.exception(f"send_admin_weekly_summary_task failed: {exc}")
            return {"error": str(exc)}
    
    @_celery_task
    def send_exam_invitation_email_task(
        self,
        email: str,
        name: str,
        exam_title: str,
        exam_date: str,
        duration: int,
        total_marks: float,
        exam_url: str,
    ) -> dict:
        """
        Send exam invitation email.
        
        Args:
            email: Student's email
            name: Student's name
            exam_title: Exam title
            exam_date: Exam datetime string
            duration: Duration in minutes
            total_marks: Total marks
            exam_url: Exam access URL
        
        Returns:
            dict with status
        """
        try:
            html, subject = _exam_invitation_email_html(
                name, exam_title, exam_date, duration, total_marks, exam_url
            )
            success = _send_email(email, subject, html)
            
            if not success and self.request.retries < self.max_retries:
                raise self.retry(exc=Exception("Email send failed"), countdown=30 * (2 ** self.request.retries))
            
            return {"status": "sent" if success else "failed", "to": email}
        except Exception as exc:
            logger.exception(f"send_exam_invitation_email_task failed: {exc}")
            if self.request.retries < self.max_retries:
                raise self.retry(exc=exc, countdown=30 * (2 ** self.request.retries))
            return {"status": "failed", "error": str(exc), "to": email}
    
    @_celery_task
    def send_payment_failed_email_task(
        self,
        user_id: str,
        razorpay_order_id: str,
        amount_paise: str,
    ) -> dict:
        """
        Send payment failure notification email.
        
        Args:
            user_id: User document ID
            razorpay_order_id: Failed Razorpay order ID
            amount_paise: Amount in paise as string
        
        Returns:
            dict with status
        """
        try:
            from app.models import User
            
            try:
                from bson import ObjectId
                user_oid = ObjectId(user_id)
            except Exception:
                return {"status": "failed", "error": "Invalid user_id"}
            
            user = User.objects(id=user_oid).first()
            if not user:
                return {"status": "failed", "error": "User not found"}
            
            html, subject = _payment_failed_email_html(
                user.first_name or "User",
                razorpay_order_id,
                int(amount_paise) if amount_paise.isdigit() else 0,
            )
            success = _send_email(user.email, subject, html)
            
            if not success and self.request.retries < self.max_retries:
                raise self.retry(exc=Exception("Email send failed"), countdown=30 * (2 ** self.request.retries))
            
            return {"status": "sent" if success else "failed", "to": user.email}
        except Exception as exc:
            logger.exception(f"send_payment_failed_email_task failed: {exc}")
            if self.request.retries < self.max_retries:
                raise self.retry(exc=exc, countdown=30 * (2 ** self.request.retries))
            return {"status": "failed", "error": str(exc)}


except ImportError:
    logger.warning("Celery not available - task decorators not applied")


logger.info("Email tasks module loaded")
