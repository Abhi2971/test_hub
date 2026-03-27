"""
Extensions module for ExamSaaS platform.
Initializes all Flask extensions and external services.
"""
import logging
from typing import Optional

import bleach
from flask import Flask, request, make_response
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager
try:
    from celery import Celery
    from celery.schedules import crontab
    celery_imported = True
except ImportError:
    celery_imported = False
    Celery = None
    crontab = None
try:
    import cloudinary
    cloudinary_imported = True
except ImportError:
    cloudinary_imported = False
import redis

logger = logging.getLogger(__name__)

# Global extension instances
mongo: Optional[PyMongo] = None
jwt: Optional[JWTManager] = None
celery: Optional[Celery] = None
redis_client: Optional[redis.Redis] = None

# Cloudinary config
cloudinary_configured: bool = False


def init_pymongo(app: Flask) -> PyMongo:
    """
    Initialize PyMongo extension and MongoEngine connection.
    
    Args:
        app: Flask application instance
    
    Returns:
        PyMongo instance
    """
    global mongo
    
    import mongoengine
    
    mongo_uri = app.config.get("MONGO_URI", "mongodb://localhost:27017/examsaas")
    
    db_name = "examsaas"
    import re
    match = re.search(r'/([a-zA-Z0-9_]+)(?:\?|$)', mongo_uri)
    if match:
        db_name = match.group(1)
    
    try:
        mongoengine.disconnect_all()
    except Exception:
        pass
    
    mongoengine.connect(host=mongo_uri, db=db_name, alias="default", tz_aware=True)
    
    mongo = PyMongo(app)
    logger.info("PyMongo and MongoEngine initialized")
    return mongo


def init_jwt(app: Flask) -> JWTManager:
    """
    Initialize JWT Manager extension.
    
    Args:
        app: Flask application instance
    
    Returns:
        JWTManager instance
    """
    global jwt
    jwt = JWTManager(app)
    logger.info("JWT Manager initialized")
    return jwt


def init_celery(app: Flask = None) -> Celery:
    """
    Initialize Celery with Flask app configuration.
    
    Args:
        app: Flask application instance (optional for standalone workers)
    
    Returns:
        Celery instance
    """
    global celery
    
    celery = Celery(
        "exam_saas",
        broker=app.config.get("CELERY_BROKER_URL") if app else None,
        backend=app.config.get("CELERY_RESULT_BACKEND") if app else None,
        include=[
            "app.tasks.email_tasks",
            "app.tasks.pdf_tasks",
            "app.tasks.result_tasks",
            "app.tasks.certificate_tasks",
            "app.tasks.ai_tasks",
            "app.tasks.exam_tasks",
        ]
    )
    
    # Configure celery if app is provided
    if app:
        celery.conf.update(
            task_serializer="json",
            accept_content=["json"],
            result_serializer="json",
            timezone="UTC",
            enable_utc=True,
            task_track_started=True,
            task_time_limit=3600,  # 1 hour max
            task_soft_time_limit=3300,  # 55 minutes soft limit
            worker_prefetch_multiplier=1,
            task_acks_late=True,
            task_reject_on_worker_lost=True,
            task_routes={
                "app.tasks.email_tasks.*": {"queue": "email"},
                "app.tasks.pdf_tasks.*": {"queue": "pdf"},
                "app.tasks.result_tasks.*": {"queue": "results"},
                "app.tasks.certificate_tasks.*": {"queue": "certificates"},
                "app.tasks.ai_tasks.*": {"queue": "ai_queue"},
                "app.tasks.exam_tasks.*": {"queue": "exam"},
            },
            beat_schedule={
                "subscription_reminder_7d": {
                    "task": "app.tasks.email_tasks.send_renewal_reminder_task",
                    "schedule": crontab(hour=9, minute=0),
                    "kwargs": {"days_remaining": 7},
                },
                "subscription_reminder_3d": {
                    "task": "app.tasks.email_tasks.send_renewal_reminder_task",
                    "schedule": crontab(hour=9, minute=0),
                    "kwargs": {"days_remaining": 3},
                },
                "subscription_reminder_1d": {
                    "task": "app.tasks.email_tasks.send_renewal_reminder_task",
                    "schedule": crontab(hour=9, minute=0),
                    "kwargs": {"days_remaining": 1},
                },
                "weekly_admin_summary": {
                    "task": "app.tasks.email_tasks.send_admin_weekly_summary_task",
                    "schedule": crontab(hour=8, minute=0, day_of_week=1),
                },
                "auto_close_exams": {
                    "task": "app.tasks.exam_tasks.auto_close_expired_exams_task",
                    "schedule": crontab(minute="*/5"),
                },
                "auto_publish_exams": {
                    "task": "app.tasks.exam_tasks.auto_publish_scheduled_exams_task",
                    "schedule": crontab(minute="*/5"),
                },
                "monthly_ai_usage_reset": {
                    "task": "app.tasks.exam_tasks.reset_monthly_ai_usage_task",
                    "schedule": crontab(minute=5, hour=0, day_of_month=1),
                },
            },
        )
    
    logger.info("Celery initialized")
    return celery


def init_redis(app: Flask) -> redis.Redis:
    """
    Initialize Redis client.
    
    Args:
        app: Flask application instance
    
    Returns:
        Redis client instance
    """
    global redis_client
    
    redis_url = app.config.get("REDIS_URL", "redis://localhost:6379/0")
    redis_password = app.config.get("REDIS_PASSWORD")
    
    # Parse Redis URL
    import re
    match = re.match(r"redis://(?:(?P<password>[^@]+)@)?(?P<host>[^:/]+)(?::(?P<port>\d+))?(?:/(?P<db>\d+))?", redis_url)
    
    if match:
        host = match.group("host") or "localhost"
        port = int(match.group("port") or 6379)
        db = int(match.group("db") or 0)
        password = match.group("password") or redis_password
    else:
        host, port, db = "localhost", 6379, 0
        password = redis_password
    
    redis_client = redis.Redis(
        host=host,
        port=port,
        db=db,
        password=password,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
    )
    
    logger.info(f"Redis client initialized: {host}:{port}/{db}")
    return redis_client


def init_cloudinary(app: Flask) -> bool:
    """
    Initialize Cloudinary configuration.
    
    Args:
        app: Flask application instance
    
    Returns:
        True if Cloudinary is configured, False otherwise
    """
    global cloudinary_configured
    
    if not cloudinary_imported:
        cloudinary_configured = False
        logger.warning("Cloudinary not installed - cloud storage features disabled")
        return False
    
    cloud_name = app.config.get("CLOUDINARY_CLOUD_NAME")
    api_key = app.config.get("CLOUDINARY_API_KEY")
    api_secret = app.config.get("CLOUDINARY_API_SECRET")
    
    if cloud_name and api_key and api_secret:
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True,
        )
        cloudinary_configured = True
        logger.info("Cloudinary initialized")
    else:
        cloudinary_configured = False
        logger.warning("Cloudinary not configured - cloud storage features disabled")
    
    return cloudinary_configured


def init_cors(app: Flask) -> None:
    """
    Initialize CORS with custom handling.
    
    Args:
        app: Flask application instance
    """
    allowed_origins = app.config.get("ALLOWED_ORIGINS", "http://localhost:5173")
    if isinstance(allowed_origins, str):
        allowed_origins_list = [origin.strip() for origin in allowed_origins.split(",")]
    else:
        allowed_origins_list = allowed_origins
    
    def cors_before_request():
        """Handle OPTIONS preflight requests manually."""
        from flask import request
        if request.method == 'OPTIONS' and request.path.startswith('/api/'):
            origin = request.headers.get('Origin', '')
            logger.info(f"OPTIONS request received from {origin}, allowed: {allowed_origins_list}")
            if origin in allowed_origins_list or '*' in allowed_origins_list:
                response = make_response('')
                response.status_code = 204
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
                response.headers['Access-Control-Allow-Credentials'] = 'true'
                logger.info("Sending CORS response for OPTIONS")
                return response
    
    def cors_after_request(response):
        """Add CORS headers to all API responses."""
        from flask import request
        origin = request.headers.get('Origin', '')
        if request.path.startswith('/api/') and (origin in allowed_origins_list or '*' in allowed_origins_list):
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response
    
    app.before_request_funcs.setdefault(None, []).insert(0, cors_before_request)
    app.after_request_funcs.setdefault(None, []).append(cors_after_request)
    
    logger.info(f"CORS initialized with origins: {allowed_origins_list}")


def sanitize_input(text: str) -> str:
    """
    Sanitize user input using bleach.
    
    Args:
        text: Raw user input
    
    Returns:
        Sanitized text safe for display/storage
    """
    if not text:
        return ""
    
    # Clean HTML tags and attributes
    cleaned = bleach.clean(
        text,
        tags=[],  # No HTML tags allowed
        attributes={},
        strip=True,
        strip_comments=True,
    )
    
    return cleaned.strip()


def sanitize_html(text: str) -> str:
    """
    Sanitize HTML content allowing safe tags.
    
    Args:
        text: Raw HTML input
    
    Returns:
        Sanitized HTML with only safe tags
    """
    if not text:
        return ""
    
    allowed_tags = [
        "p", "br", "strong", "em", "u", "s", "h1", "h2", "h3", "h4", "h5", "h6",
        "ul", "ol", "li", "blockquote", "code", "pre", "a", "img",
        "table", "thead", "tbody", "tr", "th", "td",
    ]
    
    allowed_attributes = {
        "a": ["href", "title", "target"],
        "img": ["src", "alt", "title", "width", "height"],
        "code": ["class"],
        "pre": ["class"],
    }
    
    cleaned = bleach.clean(
        text,
        tags=allowed_tags,
        attributes=allowed_attributes,
        strip=True,
        strip_comments=True,
    )
    
    return cleaned


def get_mongo() -> PyMongo:
    """
    Get the global PyMongo instance.
    
    Returns:
        PyMongo instance
    
    Raises:
        RuntimeError: If PyMongo not initialized
    """
    if mongo is None:
        raise RuntimeError("PyMongo not initialized. Call init_pymongo first.")
    return mongo


def get_jwt() -> JWTManager:
    """
    Get the global JWTManager instance.
    
    Returns:
        JWTManager instance
    
    Raises:
        RuntimeError: If JWT not initialized
    """
    if jwt is None:
        raise RuntimeError("JWT not initialized. Call init_jwt first.")
    return jwt


def get_celery() -> Celery:
    """
    Get the global Celery instance.
    
    Returns:
        Celery instance
    
    Raises:
        RuntimeError: If Celery not initialized
    """
    if celery is None:
        raise RuntimeError("Celery not initialized. Call init_celery first.")
    return celery


def get_redis() -> redis.Redis:
    """
    Get the global Redis client instance.
    
    Returns:
        Redis client instance
    
    Raises:
        RuntimeError: If Redis not initialized
    """
    if redis_client is None:
        raise RuntimeError("Redis not initialized. Call init_redis first.")
    return redis_client


logger.info("Extensions module initialized")
