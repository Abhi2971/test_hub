"""
Rate limiter middleware for ExamSaaS platform.
Redis-based sliding window rate limiting.
"""
import logging
import time
from datetime import datetime, timezone
from typing import Optional, Callable, Tuple

from flask import Flask, request, g, Response

from app.exceptions import RateLimitError

logger = logging.getLogger(__name__)

REDIS_CLIENT = None


def _get_redis():
    """Get Redis client from extensions."""
    global REDIS_CLIENT
    if REDIS_CLIENT is None:
        try:
            from app.extensions import get_redis
            REDIS_CLIENT = get_redis()
        except RuntimeError:
            logger.warning("Redis not available for rate limiter")
            return None
    return REDIS_CLIENT


class RateLimitRule:
    """Rate limit rule configuration."""
    
    def __init__(
        self,
        limit: int,
        window: int,
        key_func: Callable[[], str],
        scope: str = "global"
    ):
        """
        Initialize rate limit rule.
        
        Args:
            limit: Maximum requests allowed in window
            window: Time window in seconds
            key_func: Function to generate Redis key
            scope: Scope of the rule (global, auth, ai, etc.)
        """
        self.limit = limit
        self.window = window
        self.key_func = key_func
        self.scope = scope


class RateLimiter:
    """
    Redis sliding window rate limiter.
    
    Rules:
      - Global: 100 requests/minute per IP
      - /api/v1/auth/*: 5 requests/minute per IP
      - /api/v1/payments/webhook: 30 requests/minute per IP
      - /api/v1/ai/*: 10 requests/minute per user_id
    
    Redis keys:
      "rl:global:{ip}:{minute_bucket}"     TTL 60s
      "rl:auth:{ip}:{minute_bucket}"       TTL 60s
      "rl:ai:{user_id}:{minute_bucket}"    TTL 60s
    """
    
    def __init__(self, app: Optional[Flask] = None):
        self.app = app
        self._rules = []
        self._excluded_paths = {
            '/health',
            '/favicon.ico',
        }
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask) -> None:
        """Initialize the middleware with Flask app."""
        self.app = app
        
        self._register_rules()
        
        @app.before_request
        def check_rate_limit():
            """Check rate limits before processing request."""
            if self._is_excluded(request.path):
                return None
            
            error = self._check_all_limits()
            if error:
                raise error
            
            return None
        
        app.logger.info("RateLimiter middleware initialized")
    
    def _is_excluded(self, path: str) -> bool:
        """Check if path is excluded from rate limiting."""
        for excluded in self._excluded_paths:
            if path.startswith(excluded):
                return True
        return False
    
    def _get_client_ip(self) -> str:
        """Get client IP address, considering proxies."""
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()
        if request.headers.get('X-Real-IP'):
            return request.headers.get('X-Real-IP')
        return request.remote_addr or '0.0.0.0'
    
    def _get_user_id_from_token(self) -> Optional[str]:
        """Extract user_id from JWT token."""
        try:
            auth_header = request.headers.get('Authorization', '')
            
            if not auth_header.startswith('Bearer '):
                return None
            
            token = auth_header[7:]
            
            import jwt
            
            jwt_secret = self.app.config.get('JWT_SECRET_KEY', 'dev-jwt-secret')
            
            payload = jwt.decode(
                token,
                jwt_secret,
                algorithms=['HS256'],
                options={'verify_exp': False}
            )
            
            return payload.get('user_id')
        
        except Exception:
            return None
    
    def _get_minute_bucket(self) -> int:
        """Get current minute bucket for sliding window."""
        return int(time.time() // 60)
    
    def _register_rules(self) -> None:
        """Register rate limit rules."""
        def global_key():
            ip = self._get_client_ip()
            bucket = self._get_minute_bucket()
            return f"rl:global:{ip}:{bucket}"
        
        def auth_key():
            ip = self._get_client_ip()
            bucket = self._get_minute_bucket()
            return f"rl:auth:{ip}:{bucket}"
        
        def ai_key():
            user_id = self._get_user_id_from_token() or self._get_client_ip()
            bucket = self._get_minute_bucket()
            return f"rl:ai:{user_id}:{bucket}"
        
        def webhook_key():
            ip = self._get_client_ip()
            bucket = self._get_minute_bucket()
            return f"rl:webhook:{ip}:{bucket}"
        
        self._rules = [
            RateLimitRule(
                limit=100,
                window=60,
                key_func=global_key,
                scope="global"
            ),
            RateLimitRule(
                limit=5,
                window=60,
                key_func=auth_key,
                scope="auth"
            ),
            RateLimitRule(
                limit=30,
                window=60,
                key_func=webhook_key,
                scope="webhook"
            ),
            RateLimitRule(
                limit=10,
                window=60,
                key_func=ai_key,
                scope="ai"
            ),
        ]
    
    def _should_apply_rule(self, rule: RateLimitRule) -> bool:
        """Check if a rule should be applied to current request."""
        path = request.path
        
        if rule.scope == "auth":
            return path.startswith('/api/v1/auth/')
        
        if rule.scope == "ai":
            return path.startswith('/api/v1/ai/')
        
        if rule.scope == "webhook":
            return path.startswith('/api/v1/payments/webhook')
        
        return True
    
    def _check_all_limits(self) -> Optional[RateLimitError]:
        """Check all applicable rate limits."""
        redis = _get_redis()
        
        if redis is None:
            return None
        
        for rule in self._rules:
            if not self._should_apply_rule(rule):
                continue
            
            result = self._check_limit(redis, rule)
            
            if result is not None:
                return result
        
        return None
    
    def _check_limit(
        self,
        redis,
        rule: RateLimitRule
    ) -> Optional[RateLimitError]:
        """
        Check a single rate limit using Redis sliding window.
        
        Uses Redis pipeline for atomic INCR + EXPIRE to prevent race conditions.
        
        Args:
            redis: Redis client
            rule: Rate limit rule to check
        
        Returns:
            RateLimitError if limit exceeded, None otherwise
        """
        try:
            key = rule.key_func()
            
            pipe = redis.pipeline()
            pipe.incr(key)
            pipe.expire(key, rule.window)
            results = pipe.execute()
            
            current_count = results[0]
            retry_after = rule.window - (int(time.time()) % rule.window)
            
            if current_count > rule.limit:
                logger.warning(
                    f"Rate limit exceeded: scope={rule.scope}, "
                    f"limit={rule.limit}, current={current_count}, "
                    f"key={key}"
                )
                
                return RateLimitError(
                    message=f"Too many requests. Please try again in {retry_after} seconds.",
                    retry_after=retry_after,
                    errors={
                        "limit": rule.limit,
                        "remaining": 0,
                        "retry_after": retry_after,
                    }
                )
            
            return None
        
        except Exception as e:
            logger.error(f"Rate limiter error: {e}")
            return None
    
    def _add_rate_limit_headers(
        self,
        response: Response,
        rule: RateLimitRule,
        current: int
    ) -> None:
        """Add rate limit headers to response."""
        remaining = max(0, rule.limit - current)
        retry_after = rule.window - (int(time.time()) % rule.window)
        
        response.headers['X-RateLimit-Limit'] = str(rule.limit)
        response.headers['X-RateLimit-Remaining'] = str(remaining)
        response.headers['X-RateLimit-Window'] = str(rule.window)
        
        if remaining == 0:
            response.headers['Retry-After'] = str(retry_after)


def create_rate_limiter(app: Flask) -> RateLimiter:
    """
    Create and initialize rate limiter for Flask app.
    
    Args:
        app: Flask application instance
    
    Returns:
        Initialized RateLimiter instance
    """
    limiter = RateLimiter()
    limiter.init_app(app)
    return limiter


rate_limiter = RateLimiter()
