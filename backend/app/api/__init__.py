"""
API package for ExamSaaS platform.
"""
from app.api.auth import auth_bp
from app.api.oauth import oauth_bp

__all__ = ["auth_bp", "oauth_bp"]
