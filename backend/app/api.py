"""
API Blueprint for ExamSaaS platform.
Contains all API route registrations.
"""
import logging
from flask import Flask

from app.api.auth import auth_bp
from app.api.oauth import oauth_bp

logger = logging.getLogger(__name__)


def register_routes(app: Flask) -> None:
    """
    Register all API blueprints with the Flask app.
    
    Args:
        app: Flask application instance
    """
    api_prefix = "/api"
    
    app.register_blueprint(auth_bp, url_prefix=f"{api_prefix}/auth")
    app.register_blueprint(oauth_bp, url_prefix=f"{api_prefix}/oauth")
    
    logger.info(f"All API routes registered with prefix: {api_prefix}")


def register_health_routes(app: Flask) -> None:
    """
    Register health check routes.
    
    Args:
        app: Flask application instance
    """
    from app.response import success_response
    
    @app.route("/health")
    def health():
        """Basic health check endpoint."""
        return success_response({"status": "healthy"})
    
    @app.route(f"{app.config.get('API_URL', '')}/api/health")
    def api_health():
        """API health check endpoint."""
        return success_response({
            "status": "healthy",
            "version": "1.0.0",
            "timestamp": __import__('datetime').datetime.utcnow().isoformat(),
        })
    
    logger.info("Health routes registered")


logger.info("API blueprint module loaded")
