"""
Email service for ExamSaaS platform.
Handles sending emails via SMTP or SendGrid.
"""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class EmailService:
    """Email service class supporting SMTP and SendGrid backends."""
    
    def __init__(self, host: str, port: int, user: str, password: str,
                 from_email: str, from_name: str = "ExamSaaS"):
        """
        Initialize email service.
        
        Args:
            host: SMTP server host
            port: SMTP server port
            user: SMTP username
            password: SMTP password
            from_email: From email address
            from_name: From display name
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.from_email = from_email
        self.from_name = from_name
    
    def send_email(self, to_email: str, subject: str, html_body: str,
                   text_body: Optional[str] = None) -> bool:
        """
        Send an email.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_body: HTML content
            text_body: Plain text content (optional)
        
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to_email
            
            if text_body:
                msg.attach(MIMEText(text_body, "plain"))
            
            msg.attach(MIMEText(html_body, "html"))
            
            with smtplib.SMTP(self.host, self.port) as server:
                server.starttls()
                server.login(self.user, self.password)
                server.sendmail(self.from_email, [to_email], msg.as_string())
            
            logger.info(f"Email sent successfully to {to_email}: {subject}")
            return True
        
        except smtplib.SMTPAuthenticationError:
            logger.error(f"SMTP authentication failed for {to_email}")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error sending to {to_email}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending email to {to_email}: {e}")
            return False
    
    def send_template_email(self, to_email: str, template: str,
                           context: Dict[str, Any]) -> bool:
        """
        Send an email using a template.
        
        Args:
            to_email: Recipient email address
            template: Template name
            context: Template context variables
        
        Returns:
            True if sent successfully, False otherwise
        """
        subject, html_body = render_email_template(template, context)
        return self.send_email(to_email, subject, html_body)


def render_email_template(template: str, context: Dict[str, Any]) -> tuple:
    """
    Render an email template.
    
    Args:
        template: Template name
        context: Template context variables
    
    Returns:
        Tuple of (subject, html_body)
    """
    templates = {
        "verify_email": _verify_email_template,
        "password_reset": _password_reset_template,
        "welcome": _welcome_template,
        "exam_invitation": _exam_invitation_template,
        "result_published": _result_published_template,
        "subscription_expiring": _subscription_expiring_template,
        "certificate_generated": _certificate_generated_template,
        "otp_email": _otp_email_template,
        "magic_link": _magic_link_template,
        "account_locked": _account_locked_template,
        "password_changed": _password_changed_template,
        "login_alert": _login_alert_template,
    }
    
    render_func = templates.get(template, _default_template)
    return render_func(context)


def _otp_email_template(context: Dict[str, Any]) -> tuple:
    """Render OTP email template."""
    purpose = context.get('purpose', 'verification')
    if purpose == 'forgot_password':
        subject = "Reset your ExamSaaS password"
    else:
        subject = "Your ExamSaaS OTP"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #2563EB; color: white; padding: 24px; text-align: center; }}
            .content {{ padding: 32px; background: #f9f9f9; }}
            .otp-box {{ background: white; padding: 30px; border-radius: 8px; margin: 20px 0; text-align: center; border: 2px solid #2563EB; }}
            .otp-code {{ font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #2563EB; }}
            .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            .warning {{ color: #dc2626; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>ExamSaaS</h1>
            </div>
            <div class="content">
                <h2>Your OTP Code</h2>
                <p>Your one-time password for {purpose}:</p>
                <div class="otp-box">
                    <p class="otp-code">{context.get('otp', '000000')}</p>
                </div>
                <p class="warning">This code expires in 10 minutes. Do not share it with anyone.</p>
                <p>If you didn't request this code, please ignore this email.</p>
            </div>
            <div class="footer">
                <p>&copy; 2024 ExamSaaS. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return subject, html


def _verify_email_template(context: Dict[str, Any]) -> tuple:
    """Render email verification template."""
    subject = "Verify your ExamSaaS account"
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #2563EB; color: white; padding: 24px; text-align: center; }}
            .content {{ padding: 32px; background: #f9f9f9; }}
            .button {{ display: inline-block; background: #2563EB; color: white; padding: 14px 32px; text-decoration: none; border-radius: 6px; margin: 20px 0; font-weight: bold; }}
            .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>ExamSaaS</h1>
            </div>
            <div class="content">
                <h2>Hello {context.get('first_name', 'there')}!</h2>
                <p>Thank you for registering with ExamSaaS. Please verify your email address:</p>
                <p style="text-align: center;">
                    <a href="{context.get('verify_url', '#')}" class="button">Verify Email</a>
                </p>
                <p>This link will expire in 7 days.</p>
            </div>
            <div class="footer">
                <p>&copy; 2024 ExamSaaS. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return subject, html


def _password_reset_template(context: Dict[str, Any]) -> tuple:
    """Render password reset template."""
    subject = "Reset your ExamSaaS password"
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #dc2626; color: white; padding: 24px; text-align: center; }}
            .content {{ padding: 32px; background: #f9f9f9; }}
            .button {{ display: inline-block; background: #dc2626; color: white; padding: 14px 32px; text-decoration: none; border-radius: 6px; margin: 20px 0; font-weight: bold; }}
            .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Password Reset</h1>
            </div>
            <div class="content">
                <h2>Hello {context.get('first_name', 'there')}!</h2>
                <p>We received a request to reset your password. Use this OTP:</p>
                <p style="font-size: 24px; font-weight: bold; text-align: center; color: #dc2626;">{context.get('otp', '000000')}</p>
                <p>This code expires in 10 minutes.</p>
                <p>If you didn't request this, please ignore this email.</p>
            </div>
            <div class="footer">
                <p>&copy; 2024 ExamSaaS. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return subject, html


def _welcome_template(context: Dict[str, Any]) -> tuple:
    """Render welcome email template."""
    subject = "Welcome to ExamSaaS!"
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #2563EB; color: white; padding: 24px; text-align: center; }}
            .content {{ padding: 32px; background: #f9f9f9; }}
            .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Welcome to ExamSaaS!</h1>
            </div>
            <div class="content">
                <h2>Hello {context.get('first_name', 'there')}!</h2>
                <p>Thank you for joining ExamSaaS. Your account has been created successfully.</p>
                <p>Get started by exploring your dashboard!</p>
            </div>
            <div class="footer">
                <p>&copy; 2024 ExamSaaS. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return subject, html


def _exam_invitation_template(context: Dict[str, Any]) -> tuple:
    """Render exam invitation template."""
    subject = f"You've been invited to: {context.get('exam_title', 'an exam')}"
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #059669; color: white; padding: 24px; text-align: center; }}
            .content {{ padding: 32px; background: #f9f9f9; }}
            .button {{ display: inline-block; background: #059669; color: white; padding: 14px 32px; text-decoration: none; border-radius: 6px; margin: 20px 0; font-weight: bold; }}
            .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Exam Invitation</h1>
            </div>
            <div class="content">
                <h2>Hello {context.get('first_name', 'there')}!</h2>
                <p>You have been invited to take an exam:</p>
                <h3>{context.get('exam_title', 'Exam')}</h3>
                <p><strong>Date:</strong> {context.get('exam_date', 'TBD')}</p>
                <p><strong>Duration:</strong> {context.get('duration', 'N/A')} minutes</p>
                <p><strong>Total Marks:</strong> {context.get('total_marks', 'N/A')}</p>
                <p style="text-align: center;">
                    <a href="{context.get('exam_url', '#')}" class="button">Take Exam</a>
                </p>
            </div>
            <div class="footer">
                <p>&copy; 2024 ExamSaaS. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return subject, html


def _result_published_template(context: Dict[str, Any]) -> tuple:
    """Render result published template."""
    subject = f"Results Published: {context.get('exam_title', 'Your exam')}"
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #7C3AED; color: white; padding: 24px; text-align: center; }}
            .content {{ padding: 32px; background: #f9f9f9; }}
            .result-box {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #7C3AED; }}
            .button {{ display: inline-block; background: #7C3AED; color: white; padding: 14px 32px; text-decoration: none; border-radius: 6px; margin: 20px 0; font-weight: bold; }}
            .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Results Published</h1>
            </div>
            <div class="content">
                <h2>Hello {context.get('first_name', 'there')}!</h2>
                <p>Your results for <strong>{context.get('exam_title', 'the exam')}</strong> are now available.</p>
                <div class="result-box">
                    <p><strong>Marks:</strong> {context.get('marks_obtained', 'N/A')} / {context.get('total_marks', 'N/A')}</p>
                    <p><strong>Percentage:</strong> {context.get('percentage', 'N/A')}%</p>
                    <p><strong>Status:</strong> {context.get('status', 'N/A')}</p>
                </div>
                <p style="text-align: center;">
                    <a href="{context.get('results_url', '#')}" class="button">View Results</a>
                </p>
            </div>
            <div class="footer">
                <p>&copy; 2024 ExamSaaS. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return subject, html


def _subscription_expiring_template(context: Dict[str, Any]) -> tuple:
    """Render subscription expiring template."""
    subject = "Your ExamSaaS subscription is expiring soon"
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #f59e0b; color: white; padding: 24px; text-align: center; }}
            .content {{ padding: 32px; background: #f9f9f9; }}
            .button {{ display: inline-block; background: #f59e0b; color: white; padding: 14px 32px; text-decoration: none; border-radius: 6px; margin: 20px 0; font-weight: bold; }}
            .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Subscription Reminder</h1>
            </div>
            <div class="content">
                <h2>Hello {context.get('first_name', 'there')}!</h2>
                <p>Your <strong>{context.get('plan_name', 'subscription')}</strong> plan will expire on <strong>{context.get('expiry_date', 'soon')}</strong>.</p>
                <p style="text-align: center;">
                    <a href="{context.get('subscription_url', '#')}" class="button">Renew Now</a>
                </p>
            </div>
            <div class="footer">
                <p>&copy; 2024 ExamSaaS. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return subject, html


def _certificate_generated_template(context: Dict[str, Any]) -> tuple:
    """Render certificate generated template."""
    subject = "Congratulations! Your certificate is ready"
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #10B981; color: white; padding: 24px; text-align: center; }}
            .content {{ padding: 32px; background: #f9f9f9; }}
            .button {{ display: inline-block; background: #10B981; color: white; padding: 14px 32px; text-decoration: none; border-radius: 6px; margin: 20px 0; font-weight: bold; }}
            .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Congratulations!</h1>
            </div>
            <div class="content">
                <h2>Hello {context.get('first_name', 'there')}!</h2>
                <p>You have successfully completed <strong>{context.get('exam_title', 'the exam')}</strong> and earned your certificate!</p>
                <p><strong>Certificate ID:</strong> {context.get('certificate_id', 'N/A')}</p>
                <p style="text-align: center;">
                    <a href="{context.get('certificate_url', '#')}" class="button">View Certificate</a>
                </p>
            </div>
            <div class="footer">
                <p>&copy; 2024 ExamSaaS. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return subject, html


def _magic_link_template(context: Dict[str, Any]) -> tuple:
    """Render magic link email template."""
    subject = f"Access Exam: {context.get('exam_title', 'Exam')}"
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #059669; color: white; padding: 24px; text-align: center; }}
            .content {{ padding: 32px; background: #f9f9f9; }}
            .button {{ display: inline-block; background: #059669; color: white; padding: 14px 32px; text-decoration: none; border-radius: 6px; margin: 20px 0; font-weight: bold; }}
            .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Exam Access</h1>
            </div>
            <div class="content">
                <h2>Hello!</h2>
                <p>You have been granted access to the exam: <strong>{context.get('exam_title', 'Exam')}</strong></p>
                <p style="text-align: center;">
                    <a href="{context.get('magic_url', '#')}" class="button">Access Exam</a>
                </p>
                <p><strong>Note:</strong> This link is valid for {context.get('valid_hours', 2)} hour(s).</p>
            </div>
            <div class="footer">
                <p>&copy; 2024 ExamSaaS. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return subject, html


def _account_locked_template(context: Dict[str, Any]) -> tuple:
    """Render account locked email template."""
    subject = "Your ExamSaaS account has been temporarily locked"
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #dc2626; color: white; padding: 24px; text-align: center; }}
            .content {{ padding: 32px; background: #f9f9f9; }}
            .warning-box {{ background: #FEF2F2; border: 1px solid #dc2626; padding: 20px; border-radius: 8px; margin: 20px 0; }}
            .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Account Locked</h1>
            </div>
            <div class="content">
                <h2>Security Alert</h2>
                <div class="warning-box">
                    <p>Your ExamSaaS account has been temporarily locked due to multiple failed login attempts.</p>
                </div>
                <p>Please wait for the lockout period to expire before trying again.</p>
            </div>
            <div class="footer">
                <p>&copy; 2024 ExamSaaS. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return subject, html


def _password_changed_template(context: Dict[str, Any]) -> tuple:
    """Render password changed email template."""
    subject = "Your ExamSaaS password has been changed"
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #2563EB; color: white; padding: 24px; text-align: center; }}
            .content {{ padding: 32px; background: #f9f9f9; }}
            .info-box {{ background: #EFF6FF; border: 1px solid #2563EB; padding: 20px; border-radius: 8px; margin: 20px 0; }}
            .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Password Changed</h1>
            </div>
            <div class="content">
                <h2>Hello!</h2>
                <p>Your ExamSaaS password was recently changed.</p>
                <div class="info-box">
                    <p>If you made this change, you can safely ignore this email.</p>
                    <p>If you didn't make this change, please contact support immediately.</p>
                </div>
            </div>
            <div class="footer">
                <p>&copy; 2024 ExamSaaS. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return subject, html


def _login_alert_template(context: Dict[str, Any]) -> tuple:
    """Render login alert email template."""
    subject = "New login to your ExamSaaS account"
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #f59e0b; color: white; padding: 24px; text-align: center; }}
            .content {{ padding: 32px; background: #f9f9f9; }}
            .info-box {{ background: #FEF3C7; border: 1px solid #f59e0b; padding: 20px; border-radius: 8px; margin: 20px 0; }}
            .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Login Alert</h1>
            </div>
            <div class="content">
                <h2>New Login Detected</h2>
                <div class="info-box">
                    <p><strong>Time:</strong> {context.get('login_time', 'Unknown')}</p>
                    <p><strong>IP Address:</strong> {context.get('ip_address', 'Unknown')}</p>
                    <p><strong>Device:</strong> {context.get('device_info', 'Unknown')}</p>
                </div>
                <p>If this wasn't you, please change your password immediately.</p>
            </div>
            <div class="footer">
                <p>&copy; 2024 ExamSaaS. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return subject, html


def _default_template(context: Dict[str, Any]) -> tuple:
    """Render default template."""
    subject = "Message from ExamSaaS"
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #2563EB; color: white; padding: 24px; text-align: center; }}
            .content {{ padding: 32px; background: #f9f9f9; }}
            .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>ExamSaaS</h1>
            </div>
            <div class="content">
                <p>Hello {context.get('first_name', 'there')}!</p>
                <p>{context.get('message', 'You have a new message from ExamSaaS.')}</p>
            </div>
            <div class="footer">
                <p>&copy; 2024 ExamSaaS. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return subject, html


logger.info("Email service loaded")
