"""
Configuration module for ExamSaaS platform.
Loads all environment variables with defaults and validation.
"""
import logging
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)

_env_loaded = False


def _load_env():
    """Load .env file if it exists."""
    global _env_loaded
    if _env_loaded:
        return
    _env_loaded = True
    
    possible_paths = [
        Path(__file__).parent.parent / '.env',
        Path(__file__).parent.parent.parent / '.env',
    ]
    
    for env_path in possible_paths:
        if env_path.exists():
            logger.info(f"Loading environment from {env_path}")
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, _, value = line.partition('=')
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        if key and key not in os.environ:
                            os.environ[key] = value
            break


@dataclass
class Config:
    """
    Application configuration class that loads all settings from environment variables.
    Raises ValueError on startup if required vars are missing in production.
    """
    
    # Flask settings
    FLASK_ENV: str = "development"
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    DEBUG: bool = True
    
    # JWT settings
    JWT_SECRET_KEY: str = "dev-jwt-secret-change-in-production"
    JWT_ACCESS_TOKEN_EXPIRES: int = 3600  # 1 hour
    JWT_REFRESH_TOKEN_EXPIRES: int = 2592000  # 30 days
    
    # MongoDB settings
    MONGO_URI: str = "mongodb://localhost:27017/examsaas"
    MONGO_USER: str = ""
    MONGO_PASSWORD: str = ""
    MONGO_DB: str = "examsaas"
    
    # Redis settings
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: Optional[str] = None
    
    # Cloudinary settings
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""
    
    # Razorpay settings
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""
    RAZORPAY_WEBHOOK_SECRET: str = ""
    
    # AI settings (Groq)
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.1-70b-versatile"
    
    # Email settings (Gmail SMTP)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@examsaas.com"
    EMAIL_FROM_NAME: str = "ExamSaaS"
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    
    # App URLs
    APP_URL: str = "http://localhost:5173"
    API_URL: str = "http://localhost:5000"
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    
    # Celery settings
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # File upload settings
    MAX_CONTENT_LENGTH: int = 100 * 1024 * 1024  # 100MB
    UPLOAD_FOLDER: str = "uploads"
    
    # Rate limiting
    RATELIMIT_STORAGE_URL: str = "redis://localhost:6379/3"
    RATELIMIT_DEFAULT: str = "100 per minute"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = '{"time":"%(asctime)s","level":"%(levelname)s","name":"%(name)s","message":"%(message)s}'
    
    # Celery task queues
    CELERY_TASK_QUEUES: list = field(default_factory=lambda: [
        "default",
        "email",
        "pdf",
        "results",
        "certificates",
        "ai_queue"
    ])
    
    # Celery task routes
    CELERY_TASK_ROUTES: dict = field(default_factory=lambda: {
        "tasks.email_tasks.*": {"queue": "email"},
        "tasks.pdf_tasks.*": {"queue": "pdf"},
        "tasks.result_tasks.*": {"queue": "results"},
        "tasks.certificate_tasks.*": {"queue": "certificates"},
        "tasks.ai.*": {"queue": "ai_queue"},
    })
    
    # Security settings
    SESSION_COOKIE_SECURE: bool = False
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "Lax"
    CORS_HEADERS: str = "Content-Type"
    
    # Feature flags
    ENABLE_GOOGLE_OAUTH: bool = False
    ENABLE_RAZORPAY: bool = False
    ENABLE_AI_FEATURES: bool = False
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    @classmethod
    def from_env(cls) -> "Config":
        """
        Load configuration from environment variables.
        
        Returns:
            Config instance with values from environment
            
        Raises:
            ValueError: If required variables are missing in production
        """
        _load_env()
        config = cls()
        
        # Load all environment variables
        env_mappings = {
            "FLASK_ENV": ("FLASK_ENV", str),
            "SECRET_KEY": ("SECRET_KEY", str),
            "JWT_SECRET_KEY": ("JWT_SECRET_KEY", str),
            "MONGO_URI": ("MONGO_URI", str),
            "MONGO_USER": ("MONGO_USER", str),
            "MONGO_PASSWORD": ("MONGO_PASSWORD", str),
            "REDIS_URL": ("REDIS_URL", str),
            "REDIS_PASSWORD": ("REDIS_PASSWORD", str),
            "CLOUDINARY_CLOUD_NAME": ("CLOUDINARY_CLOUD_NAME", str),
            "CLOUDINARY_API_KEY": ("CLOUDINARY_API_KEY", str),
            "CLOUDINARY_API_SECRET": ("CLOUDINARY_API_SECRET", str),
            "RAZORPAY_KEY_ID": ("RAZORPAY_KEY_ID", str),
            "RAZORPAY_KEY_SECRET": ("RAZORPAY_KEY_SECRET", str),
            "RAZORPAY_WEBHOOK_SECRET": ("RAZORPAY_WEBHOOK_SECRET", str),
            "GROQ_API_KEY": ("GROQ_API_KEY", str),
            "GROQ_MODEL": ("GROQ_MODEL", str),
            "SMTP_HOST": ("SMTP_HOST", str),
            "SMTP_PORT": ("SMTP_PORT", int),
            "SMTP_USER": ("SMTP_USER", str),
            "SMTP_PASSWORD": ("SMTP_PASSWORD", str),
            "EMAIL_FROM": ("EMAIL_FROM", str),
            "EMAIL_FROM_NAME": ("EMAIL_FROM_NAME", str),
            "GOOGLE_CLIENT_ID": ("GOOGLE_CLIENT_ID", str),
            "GOOGLE_CLIENT_SECRET": ("GOOGLE_CLIENT_SECRET", str),
            "APP_URL": ("APP_URL", str),
            "API_URL": ("API_URL", str),
            "ALLOWED_ORIGINS": ("ALLOWED_ORIGINS", str),
            "CELERY_BROKER_URL": ("CELERY_BROKER_URL", str),
            "CELERY_RESULT_BACKEND": ("CELERY_RESULT_BACKEND", str),
            "LOG_LEVEL": ("LOG_LEVEL", str),
        }
        
        for attr_name, (env_var, type_func) in env_mappings.items():
            value = os.environ.get(env_var)
            if value is not None:
                if type_func == int:
                    setattr(config, attr_name, int(value))
                else:
                    setattr(config, attr_name, value)
        
        # Set boolean flags
        config.DEBUG = config.FLASK_ENV == "development"
        config.SECRET_KEY = os.environ.get("SECRET_KEY", config.SECRET_KEY)
        config.JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", config.JWT_SECRET_KEY)
        
        # Feature flags
        config.ENABLE_GOOGLE_OAUTH = bool(config.GOOGLE_CLIENT_ID)
        config.ENABLE_RAZORPAY = bool(config.RAZORPAY_KEY_ID and config.RAZORPAY_KEY_SECRET)
        config.ENABLE_AI_FEATURES = bool(config.GROQ_API_KEY)
        
        # Security settings for production
        if config.FLASK_ENV == "production":
            config.SESSION_COOKIE_SECURE = True
            config.DEBUG = False
        
        return config
    
    def validate(self) -> None:
        """
        Validate required configuration for production.
        
        Raises:
            ValueError: If required variables are missing in production
        """
        if self.FLASK_ENV == "production":
            required_vars = [
                ("SECRET_KEY", self.SECRET_KEY),
                ("JWT_SECRET_KEY", self.JWT_SECRET_KEY),
                ("MONGO_URI", self.MONGO_URI),
                ("REDIS_URL", self.REDIS_URL),
            ]
            
            missing = [
                var_name for var_name, var_value in required_vars
                if not var_value or var_value.startswith("dev-") or var_value.startswith("change")
            ]
            
            if missing:
                raise ValueError(
                    f"Missing required configuration in production: {', '.join(missing)}. "
                    f"Please set these environment variables before starting the application."
                )
            
            logger.info("Production configuration validated successfully")
        else:
            logger.info(f"Running in {self.FLASK_ENV} mode - skipping strict validation")
    
    def get_mongo_uri(self) -> str:
        """
        Get the MongoDB connection URI with credentials.
        
        Returns:
            Complete MongoDB connection string
        """
        if self.MONGO_URI:
            return self.MONGO_URI
        if self.MONGO_USER and self.MONGO_PASSWORD:
            return f"mongodb://{self.MONGO_USER}:{self.MONGO_PASSWORD}@localhost:27017/{self.MONGO_DB}"
        return f"mongodb://localhost:27017/{self.MONGO_DB}"
    
    def get_allowed_origins(self) -> list[str]:
        """
        Parse ALLOWED_ORIGINS into a list.
        
        Returns:
            List of allowed origin URLs
        """
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]


# Global config instance
config = Config.from_env()

logger.info(f"Configuration loaded for environment: {config.FLASK_ENV}")
