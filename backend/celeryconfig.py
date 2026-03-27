"""
Celery configuration for ExamSaaS platform.
Defines task routes, queues, and beat schedule.
"""
import logging

from celery import Celery
from celery.schedules import crontab

logger = logging.getLogger(__name__)

# Create Celery app instance
celery = Celery("exam_saas")

# Task queues
CELERY_QUEUES = [
    "default",
    "email",
    "pdf",
    "results",
    "certificates",
    "ai_queue",
]

# Task routes
CELERY_TASK_ROUTES = {
    "tasks.email_tasks.*": {"queue": "email"},
    "tasks.pdf_tasks.*": {"queue": "pdf"},
    "tasks.result_tasks.*": {"queue": "results"},
    "tasks.certificate_tasks.*": {"queue": "certificates"},
    "tasks.ai.*": {"queue": "ai_queue"},
}

# Beat schedule (periodic tasks)
CELERY_BEAT_SCHEDULE = {
    "subscription_reminder_7d": {
        "task": "tasks.subscription_tasks.send_7day_reminder",
        "schedule": crontab(hour=9, minute=0),
        "options": {"queue": "email"},
    },
    "subscription_reminder_3d": {
        "task": "tasks.subscription_tasks.send_3day_reminder",
        "schedule": crontab(hour=9, minute=0),
        "options": {"queue": "email"},
    },
    "subscription_reminder_1d": {
        "task": "tasks.subscription_tasks.send_1day_reminder",
        "schedule": crontab(hour=9, minute=0),
        "options": {"queue": "email"},
    },
    "weekly_admin_summary": {
        "task": "tasks.admin_tasks.send_weekly_summary",
        "schedule": crontab(hour=8, minute=0, day_of_week=1),
        "options": {"queue": "email"},
    },
    "auto_close_exams": {
        "task": "tasks.exam_tasks.auto_close_completed_exams",
        "schedule": crontab(minute="*/5"),
        "options": {"queue": "default"},
    },
    "auto_publish_exams": {
        "task": "tasks.exam_tasks.auto_publish_scheduled_exams",
        "schedule": crontab(minute="*/5"),
        "options": {"queue": "default"},
    },
}

# Celery configuration
celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
    task_soft_time_limit=3300,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_routes=CELERY_TASK_ROUTES,
    beat_schedule=CELERY_BEAT_SCHEDULE,
    task_default_queue="default",
    task_default_exchange="default",
    task_default_routing_key="default",
)

logger.info("Celery configuration loaded")

# Import tasks to register them with Celery
# These will be implemented in later stages
try:
    from app.tasks import email_tasks
    from app.tasks import pdf_tasks
    from app.tasks import result_tasks
    from app.tasks import certificate_tasks
    from app.tasks import ai_tasks
    logger.info("Celery tasks imported successfully")
except ImportError as e:
    logger.warning(f"Some task modules not available yet: {e}")
