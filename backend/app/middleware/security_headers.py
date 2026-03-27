"""
Security headers middleware for ExamSaaS platform.
CSP, HSTS, X-Frame, and other security headers using flask-talisman.
"""
import logging
from typing import Optional

from flask import Flask, request

logger = logging.getLogger(__name__)


CONTENT_SECURITY_POLICY = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline' https://checkout.razorpay.com https://cdnjs.cloudflare.com; "
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
    "font-src 'self' https://fonts.gstatic.com; "
    "img-src 'self' data: https://res.cloudinary.com https://lh3.googleusercontent.com https://*.googleusercontent.com; "
    "connect-src 'self' https://api.razorpay.com https://api.groq.com; "
    "frame-src https://checkout.razorpay.com; "
    "object-src 'none'; "
    "base-uri 'self'; "
    "form-action 'self'; "
    "frame-ancestors 'none';"
)


class SecurityHeaders:
    """
    Security headers middleware using flask-talisman.
    
    Headers configured:
      - Content-Security-Policy
      - Strict-Transport-Security (production only)
      - X-Frame-Options
      - X-Content-Type-Options
      - Referrer-Policy
      - X-XSS-Protection (deprecated but still useful for older browsers)
    """
    
    def __init__(self, app: Optional[Flask] = None):
        self.app = app
        self._talisman = None
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask) -> None:
        """Initialize security headers with Flask app."""
        self.app = app
        
        is_production = app.config.get('FLASK_ENV') == 'production'
        
        if not is_production:
            app.logger.info("Development mode - using fallback security headers")
            self._register_fallback_headers(app)
            return
        
        try:
            from flask_talisman import Talisman
            
            talisman = Talisman(
                app,
                content_security_policy=CONTENT_SECURITY_POLICY,
                strict_transport_security=True,
                strict_transport_security_max_age=31536000,
                frame_options='DENY',
                x_content_type_options='nosniff',
                referrer_policy='strict-origin-when-cross-origin',
                force_https=False,
                force_https_permanent=False,
            )
            
            self._talisman = talisman
            app.logger.info("SecurityHeaders middleware initialized with Talisman")
        
        except ImportError:
            app.logger.warning("flask-talisman not installed, using fallback headers")
            self._register_fallback_headers(app)
    
    def _register_fallback_headers(self, app: Flask) -> None:
        """Register fallback security headers if Talisman not available."""
        
        @app.after_request
        def add_security_headers(response):
            is_production = app.config.get('FLASK_ENV') == 'production'
            
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            
            if request.method != 'OPTIONS':
                response.headers['Content-Security-Policy'] = CONTENT_SECURITY_POLICY
            
            if is_production:
                response.headers['Strict-Transport-Security'] = (
                    'max-age=31536000; includeSubDomains; preload'
                )
            
            return response
        
        app.logger.info("Fallback security headers registered")


def get_nonce() -> str:
    """
    Get Content Security Policy nonce for the current request.
    Must be called within request context.
    
    Returns:
        Nonce string for use in CSP policy
    """
    try:
        from flask_talisman import Talisman
        return Talisman.get_nonce()
    except ImportError:
        import secrets
        return secrets.token_hex(16)


security_headers = SecurityHeaders()
