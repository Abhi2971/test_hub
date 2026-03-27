"""
Email helper utilities for ExamSaaS platform.
These are sync wrappers that queue Celery tasks for actual email sending.
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def _get_celery_task(task_name: str):
    """
    Get a Celery task function by name.
    
    Args:
        task_name: Name of the task
    
    Returns:
        Task function or None if not available
    """
    try:
        if task_name == "send_otp_email_task":
            from app.tasks.email_tasks import send_email_task
            return send_email_task
        elif task_name == "send_welcome_email_task":
            from app.tasks.email_tasks import send_welcome_email
            return send_welcome_email
        elif task_name == "send_password_reset_email_task":
            from app.tasks.email_tasks import send_password_reset_email
            return send_password_reset_email
        else:
            from app.tasks.email_tasks import send_email_task
            return send_email_task
    except ImportError:
        logger.warning(f"Email tasks module not available: {task_name}")
        return None
    except Exception as e:
        logger.warning(f"Failed to get Celery task {task_name}: {e}")
        return None


def _queue_or_send(task_name: str, func, *args, **kwargs) -> bool:
    """
    Try to queue a task via Celery, fall back to synchronous execution.
    
    Args:
        task_name: Name of the task
        func: Task function to call
        *args: Positional arguments
        **kwargs: Keyword arguments
    
    Returns:
        True if executed successfully
    """
    try:
        from celery import Celery
        celery_app = Celery("exam_saas")
        celery_app.config_from_object("celeryconfig")
        
        if hasattr(celery_app, 'send_task'):
            celery_app.send_task(f"app.tasks.email_tasks.{task_name}", args=args, kwargs=kwargs)
            logger.info(f"Queued task: {task_name}")
            return True
    except Exception:
        pass
    
    try:
        func(*args, **kwargs)
        logger.info(f"Executed task synchronously: {task_name}")
        return True
    except Exception as e:
        logger.error(f"Failed to execute task {task_name}: {e}")
        return False


def send_otp_email(email: str, otp: str, purpose: str) -> bool:
    """
    Send an OTP email.
    
    Args:
        email: Recipient email address
        otp: One-time password
        purpose: Purpose of OTP ('verify_email' or 'forgot_password')
    
    Returns:
        True if sent successfully
    """
    try:
        task_func = _get_celery_task("send_otp_email_task")
        
        if task_func is None:
            logger.warning(f"Cannot send OTP email to {email}: tasks not available")
            return False
        
        _queue_or_send(
            "send_otp_email_task",
            task_func,
            to_email=email,
            subject="Your OTP Code",
            template="otp_email",
            context={
                "otp": otp,
                "purpose": purpose,
                "email": email,
            }
        )
        
        logger.info(f"OTP email queued for {email}, purpose: {purpose}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to send OTP email to {email}: {e}")
        return False


def send_welcome_email(email: str, name: str) -> bool:
    """
    Send a welcome email.
    
    Args:
        email: Recipient email address
        name: Recipient name
    
    Returns:
        True if sent successfully
    """
    try:
        task_func = _get_celery_task("send_welcome_email_task")
        
        if task_func is None:
            logger.warning(f"Cannot send welcome email to {email}: tasks not available")
            return False
        
        _queue_or_send(
            "send_welcome_email_task",
            task_func,
            to_email=email,
            first_name=name
        )
        
        logger.info(f"Welcome email queued for {email}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to send welcome email to {email}: {e}")
        return False


def send_password_reset_email(email: str, otp: str) -> bool:
    """
    Send a password reset email.
    
    Args:
        email: Recipient email address
        otp: One-time password
    
    Returns:
        True if sent successfully
    """
    return send_otp_email(email, otp, purpose="forgot_password")


def send_verification_email(email: str, otp: str) -> bool:
    """
    Send an email verification email.
    
    Args:
        email: Recipient email address
        otp: One-time password
    
    Returns:
        True if sent successfully
    """
    return send_otp_email(email, otp, purpose="verify_email")


def send_magic_link_email(email: str, magic_url: str, exam_title: str, valid_hours: int = 2) -> bool:
    """
    Send a magic link email.
    
    Args:
        email: Recipient email address
        magic_url: Magic link URL
        exam_title: Title of the exam
        valid_hours: Hours until link expires
    
    Returns:
        True if sent successfully
    """
    try:
        task_func = _get_celery_task("send_magic_link_email_task")
        
        if task_func is None:
            logger.warning(f"Cannot send magic link email to {email}: tasks not available")
            return False
        
        _queue_or_send(
            "send_magic_link_email_task",
            task_func,
            to_email=email,
            subject=f"Access Exam: {exam_title}",
            template="magic_link",
            context={
                "magic_url": magic_url,
                "exam_title": exam_title,
                "valid_hours": valid_hours,
                "email": email,
            }
        )
        
        logger.info(f"Magic link email queued for {email}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to send magic link email to {email}: {e}")
        return False


def send_account_locked_email(email: str, locked_until: str) -> bool:
    """
    Send an account locked notification email.
    
    Args:
        email: Recipient email address
        locked_until: Time when account will be unlocked
    
    Returns:
        True if sent successfully
    """
    try:
        task_func = _get_celery_task("send_account_locked_email_task")
        
        if task_func is None:
            logger.warning(f"Cannot send account locked email to {email}: tasks not available")
            return False
        
        _queue_or_send(
            "send_account_locked_email_task",
            task_func,
            to_email=email,
            subject="Your ExamSaaS account has been temporarily locked",
            template="account_locked",
            context={
                "email": email,
                "locked_until": locked_until,
            }
        )
        
        logger.info(f"Account locked email queued for {email}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to send account locked email to {email}: {e}")
        return False


def send_password_changed_email(email: str) -> bool:
    """
    Send a password changed notification email.
    
    Args:
        email: Recipient email address
    
    Returns:
        True if sent successfully
    """
    try:
        task_func = _get_celery_task("send_password_changed_email_task")
        
        if task_func is None:
            logger.warning(f"Cannot send password changed email to {email}: tasks not available")
            return False
        
        _queue_or_send(
            "send_password_changed_email_task",
            task_func,
            to_email=email,
            subject="Your ExamSaaS password has been changed",
            template="password_changed",
            context={
                "email": email,
            }
        )
        
        logger.info(f"Password changed email queued for {email}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to send password changed email to {email}: {e}")
        return False


def send_login_alert_email(email: str, login_time: str, ip_address: str, device_info: str) -> bool:
    """
    Send a login alert notification email.
    
    Args:
        email: Recipient email address
        login_time: Time of login
        ip_address: IP address of login
        device_info: Device/browser information
    
    Returns:
        True if sent successfully
    """
    try:
        task_func = _get_celery_task("send_login_alert_email_task")
        
        if task_func is None:
            logger.warning(f"Cannot send login alert email to {email}: tasks not available")
            return False
        
        _queue_or_send(
            "send_login_alert_email_task",
            task_func,
            to_email=email,
            subject="New login to your ExamSaaS account",
            template="login_alert",
            context={
                "email": email,
                "login_time": login_time,
                "ip_address": ip_address,
                "device_info": device_info,
            }
        )
        
        logger.info(f"Login alert email queued for {email}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to send login alert email to {email}: {e}")
        return False
