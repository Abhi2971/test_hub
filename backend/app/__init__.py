"""
Flask application factory for ExamSaaS platform.
"""
import logging
import os
from datetime import timedelta
from flask import Flask, jsonify

from app.config import Config
from app.response import success_response
from app.constants import CeleryQueues

logger = logging.getLogger(__name__)


def create_app(config: Config = None) -> Flask:
    """
    Create and configure the Flask application.
    
    Args:
        config: Configuration object (optional, loads from env if not provided)
    
    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    if config is None:
        config = Config.from_env()
    
    # Apply config to Flask app
    app.config["SECRET_KEY"] = config.SECRET_KEY
    app.config["DEBUG"] = config.DEBUG
    app.config["FLASK_ENV"] = config.FLASK_ENV
    
    # JWT Configuration
    app.config["JWT_SECRET_KEY"] = config.JWT_SECRET_KEY
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(seconds=config.JWT_ACCESS_TOKEN_EXPIRES)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(seconds=config.JWT_REFRESH_TOKEN_EXPIRES)
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]
    app.config["JWT_HEADER_NAME"] = "Authorization"
    app.config["JWT_HEADER_TYPE"] = "Bearer"
    
    # MongoDB Configuration
    app.config["MONGO_URI"] = config.get_mongo_uri()
    
    # Redis Configuration
    app.config["REDIS_URL"] = config.REDIS_URL
    app.config["REDIS_PASSWORD"] = config.REDIS_PASSWORD
    
    # Celery Configuration
    app.config["CELERY_BROKER_URL"] = config.CELERY_BROKER_URL
    app.config["CELERY_RESULT_BACKEND"] = config.CELERY_RESULT_BACKEND
    
    # File Upload Configuration
    app.config["MAX_CONTENT_LENGTH"] = config.MAX_CONTENT_LENGTH
    app.config["UPLOAD_FOLDER"] = config.UPLOAD_FOLDER
    
    # Cloudinary Configuration
    app.config["CLOUDINARY_CLOUD_NAME"] = config.CLOUDINARY_CLOUD_NAME
    app.config["CLOUDINARY_API_KEY"] = config.CLOUDINARY_API_KEY
    app.config["CLOUDINARY_API_SECRET"] = config.CLOUDINARY_API_SECRET
    
    # Third-party API Keys
    app.config["RAZORPAY_KEY_ID"] = config.RAZORPAY_KEY_ID
    app.config["RAZORPAY_KEY_SECRET"] = config.RAZORPAY_KEY_SECRET
    app.config["RAZORPAY_WEBHOOK_SECRET"] = config.RAZORPAY_WEBHOOK_SECRET
    app.config["GROQ_API_KEY"] = config.GROQ_API_KEY
    app.config["GROQ_MODEL"] = config.GROQ_MODEL
    
    # Email Configuration
    app.config["SMTP_HOST"] = config.SMTP_HOST
    app.config["SMTP_PORT"] = config.SMTP_PORT
    app.config["SMTP_USER"] = config.SMTP_USER
    app.config["SMTP_PASSWORD"] = config.SMTP_PASSWORD
    app.config["EMAIL_FROM"] = config.EMAIL_FROM
    app.config["EMAIL_FROM_NAME"] = config.EMAIL_FROM_NAME
    
    # OAuth Configuration
    app.config["GOOGLE_CLIENT_ID"] = config.GOOGLE_CLIENT_ID
    app.config["GOOGLE_CLIENT_SECRET"] = config.GOOGLE_CLIENT_SECRET
    
    # URL Configuration
    app.config["APP_URL"] = config.APP_URL
    app.config["API_URL"] = config.API_URL
    app.config["ALLOWED_ORIGINS"] = config.ALLOWED_ORIGINS
    
    # Feature Flags
    app.config["ENABLE_GOOGLE_OAUTH"] = config.ENABLE_GOOGLE_OAUTH
    app.config["ENABLE_RAZORPAY"] = config.ENABLE_RAZORPAY
    app.config["ENABLE_AI_FEATURES"] = config.ENABLE_AI_FEATURES
    
    # Pagination
    app.config["DEFAULT_PAGE_SIZE"] = config.DEFAULT_PAGE_SIZE
    app.config["MAX_PAGE_SIZE"] = config.MAX_PAGE_SIZE
    
    # Configure logging
    configure_logging(app, config)
    
    # Validate configuration for production
    config.validate()
    
    # Initialize security headers FIRST (before any other middleware)
    # Only in production - disabled for development
    # from app.middleware.security_headers import security_headers
    # security_headers.init_app(app)
    
    # Initialize extensions (CORS should come early)
    from app import extensions
    extensions.init_pymongo(app)
    extensions.init_jwt(app)
    extensions.init_celery(app)
    extensions.init_redis(app)
    extensions.init_cloudinary(app)
    extensions.init_cors(app)
    
    # Initialize request logger (before_request + after_request)
    from app.middleware.request_logger import request_logger
    request_logger.init_app(app)
    
    # Initialize rate limiter (before_request)
    from app.middleware.rate_limiter import rate_limiter
    rate_limiter.init_app(app)
    
    # Initialize institute context (before_request for authenticated routes)
    from app.middleware.institute_context import institute_context
    institute_context.init_app(app)
    
    # Register error handlers LAST (after extensions)
    from app.middleware.error_handler import error_handler
    error_handler.init_app(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register health check endpoint
    register_health_check(app)
    
    logger.info(f"ExamSaaS application created for environment: {config.FLASK_ENV}")
    return app


def configure_logging(app: Flask, config: Config) -> None:
    """
    Configure application logging.
    
    Args:
        app: Flask application instance
        config: Configuration object
    """
    log_level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)
    
    # Create JSON formatter
    class JSONFormatter(logging.Formatter):
        def format(self, record):
            log_obj = {
                "timestamp": self.formatTime(record),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
            }
            if record.exc_info:
                log_obj["exception"] = self.formatException(record.exc_info)
            return str(log_obj)
    
    # Configure root logger
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    handler.setLevel(log_level)
    
    logging.basicConfig(
        level=log_level,
        handlers=[handler]
    )
    
    # Reduce noise from third-party libraries
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("botocore").setLevel(logging.WARNING)


def register_blueprints(app: Flask) -> None:
    """
    Register Flask blueprints.
    
    Args:
        app: Flask application instance
    """
    from app.routes.auth import auth_bp
    from app.routes.exams import exams_bp
    from app.routes.questions import questions_bp
    from app.routes.attempts import attempts_bp
    from app.routes.results import results_bp
    from app.routes.users import users_bp
    from app.routes.payments import payments_bp
    from app.routes.wallet import wallet_bp
    from app.routes.plans import plans_bp
    from app.routes.subscriptions import subscriptions_bp
    from app.routes.institutes import institutes_bp
    from app.routes.support import support_bp
    from app.routes.analytics import analytics_bp
    from app.routes.superadmin_analytics import superadmin_bp
    from app.routes.pdfs import pdfs_bp
    from app.routes.certificates import certificates_bp
    from app.routes.ebooks import ebooks_bp
    from app.routes.ai import ai_bp
    
    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(exams_bp, url_prefix="/api/v1/exams")
    app.register_blueprint(questions_bp, url_prefix="/api/v1/questions")
    app.register_blueprint(attempts_bp, url_prefix="/api/v1/attempts")
    app.register_blueprint(results_bp, url_prefix="/api/v1/results")
    app.register_blueprint(users_bp, url_prefix="/api/v1/users")
    app.register_blueprint(payments_bp, url_prefix="/api/v1/payments")
    app.register_blueprint(wallet_bp, url_prefix="/api/v1/wallet")
    app.register_blueprint(plans_bp, url_prefix="/api/v1/plans")
    app.register_blueprint(subscriptions_bp, url_prefix="/api/v1/subscriptions")
    app.register_blueprint(institutes_bp, url_prefix="/api/v1/institutes")
    app.register_blueprint(support_bp, url_prefix="/api/v1/support")
    app.register_blueprint(analytics_bp, url_prefix="/api/v1/admin")
    app.register_blueprint(superadmin_bp, url_prefix="/api/v1/superadmin")
    app.register_blueprint(pdfs_bp, url_prefix="/api/v1/pdfs")
    app.register_blueprint(certificates_bp, url_prefix="/api/v1/certificates")
    app.register_blueprint(ebooks_bp, url_prefix="/api/v1/ebooks")
    app.register_blueprint(ai_bp, url_prefix="/api/v1/ai")
    
    logger.info("Blueprints registered: auth, exams, questions, attempts, results, users, payments, wallet, plans, subscriptions, institutes, support, analytics, superadmin, pdfs, certificates, ebooks, ai")


def register_error_handlers(app: Flask) -> None:
    """
    Register global error handlers.
    
    Args:
        app: Flask application instance
    """
    from app.response import error_response
    
    @app.errorhandler(400)
    def bad_request(error):
        return error_response(message="Bad request", status=400)
    
    @app.errorhandler(401)
    def unauthorized(error):
        return error_response(message="Unauthorized", status=401)
    
    @app.errorhandler(403)
    def forbidden(error):
        return error_response(message="Forbidden", status=403)
    
    @app.errorhandler(404)
    def not_found(error):
        return error_response(message="Resource not found", status=404)
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return error_response(message="Method not allowed", status=405)
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        return error_response(message="Rate limit exceeded", status=429)
    
    @app.errorhandler(500)
    def internal_server_error(error):
        logger.error(f"Internal server error: {str(error)}")
        return error_response(message="Internal server error", status=500)
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        logger.error(f"Unhandled exception: {str(error)}", exc_info=True)
        return error_response(message="An unexpected error occurred", status=500)
    
    logger.info("Error handlers registered")


def register_health_check(app: Flask) -> None:
    """
    Register health check endpoint.
    
    Args:
        app: Flask application instance
    """
    @app.route("/health", methods=["GET"])
    def health_check():
        """
        Health check endpoint for load balancers and monitoring.
        
        Returns:
            JSON response with service status
        """
        from app.response import success_response
        
        return success_response(
            data={
                "version": "1.0.0",
                "env": app.config.get("FLASK_ENV", "development"),
            },
            message="ExamSaaS API is running",
            status=200
        )
    
    logger.info("Health check endpoint registered")
