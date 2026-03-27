"""
Institute context middleware for ExamSaaS platform.
Injects current institute into Flask g object for authenticated requests.
"""
import logging
import json
from typing import Optional, Callable
from functools import wraps

from flask import Flask, request, g

from app.exceptions import InstituteSuspendedError, NotFoundError

logger = logging.getLogger(__name__)

REDIS_CLIENT = None
INSTITUTE_CACHE_TTL = 300


def _get_redis():
    """Get Redis client from extensions."""
    global REDIS_CLIENT
    if REDIS_CLIENT is None:
        try:
            from app.extensions import get_redis
            REDIS_CLIENT = get_redis()
        except RuntimeError:
            logger.warning("Redis not available for institute context")
            return None
    return REDIS_CLIENT


class InstituteContext:
    """
    Middleware to inject current institute context.
    
    For authenticated requests:
      1. Decode JWT (already validated by @require_roles)
      2. If claims contain institute_id: fetch Institute from DB (cache in Redis 5min)
      3. Inject: g.current_institute (Institute object or None)
      4. If institute is_suspended: raise InstituteSuspendedError
      5. If institute not found but institute_id present: raise NotFoundError
    """
    
    def __init__(self, app: Optional[Flask] = None):
        self.app = app
        self._excluded_paths = {
            '/health',
            '/favicon.ico',
            '/api/v1/auth/',
        }
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask) -> None:
        """Initialize middleware with Flask app."""
        self.app = app
        
        @app.before_request
        def load_institute_context():
            """Load institute context before processing request."""
            if self._is_excluded(request.path):
                return None
            
            auth_header = request.headers.get('Authorization', '')
            
            if not auth_header.startswith('Bearer '):
                return None
            
            try:
                self._load_institute()
            except (InstituteSuspendedError, NotFoundError):
                raise
            except Exception as e:
                logger.error(f"Error loading institute context: {e}")
            
            return None
        
        app.logger.info("InstituteContext middleware initialized")
    
    def _is_excluded(self, path: str) -> bool:
        """Check if path is excluded from institute context."""
        for excluded in self._excluded_paths:
            if path.startswith(excluded):
                return True
        return False
    
    def _get_institute_id_from_token(self) -> Optional[str]:
        """Extract institute_id from JWT token."""
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
            
            return payload.get('institute_id')
        
        except Exception:
            return None
    
    def _load_institute(self) -> None:
        """Load institute into Flask g object."""
        institute_id = self._get_institute_id_from_token()
        
        if not institute_id:
            g.current_institute = None
            g.current_institute_id = None
            return None
        
        g.current_institute_id = institute_id
        
        institute = self._get_institute_from_cache(institute_id)
        
        if institute is None:
            institute = self._load_institute_from_db(institute_id)
        
        if institute is None:
            raise NotFoundError(f"Institute not found: {institute_id}")
        
        if institute.is_suspended:
            raise InstituteSuspendedError(
                f"Institute {institute.name} has been suspended. "
                "Please contact support for assistance."
            )
        
        g.current_institute = institute
    
    def _get_institute_from_cache(self, institute_id: str) -> Optional[object]:
        """Get institute from Redis cache."""
        redis = _get_redis()
        
        if redis is None:
            return None
        
        try:
            cache_key = f"institute:{institute_id}"
            cached = redis.get(cache_key)
            
            if cached:
                from bson import ObjectId
                data = json.loads(cached)
                data['_id'] = ObjectId(data['id'])
                return self._dict_to_institute(data)
        
        except Exception as e:
            logger.error(f"Error reading institute from cache: {e}")
        
        return None
    
    def _load_institute_from_db(self, institute_id: str) -> Optional[object]:
        """Load institute from database and cache it."""
        try:
            from app.models import Institute
            
            institute = Institute.objects(id=institute_id).first()
            
            if institute:
                self._cache_institute(institute)
            
            return institute
        
        except Exception as e:
            logger.error(f"Error loading institute from DB: {e}")
            return None
    
    def _cache_institute(self, institute) -> None:
        """Cache institute in Redis."""
        redis = _get_redis()
        
        if redis is None:
            return
        
        try:
            cache_key = f"institute:{str(institute.id)}"
            cache_data = {
                'id': str(institute.id),
                'name': institute.name,
                'is_suspended': institute.is_suspended,
                'is_active': institute.is_active,
                'subscription_id': str(institute.subscription.id) if institute.subscription else None,
            }
            redis.setex(cache_key, INSTITUTE_CACHE_TTL, json.dumps(cache_data))
        
        except Exception as e:
            logger.error(f"Error caching institute: {e}")
    
    def _dict_to_institute(self, data: dict) -> object:
        """Convert cached dict back to Institute-like object."""
        class CachedInstitute:
            def __init__(self, d):
                self.id = d.get('id')
                self.name = d.get('name')
                self.is_suspended = d.get('is_suspended', False)
                self.is_active = d.get('is_active', True)
                self.subscription_id = d.get('subscription_id')
        
        return CachedInstitute(data)
    
    def invalidate_cache(self, institute_id: str) -> None:
        """Invalidate institute cache."""
        redis = _get_redis()
        
        if redis:
            try:
                cache_key = f"institute:{institute_id}"
                redis.delete(cache_key)
            except Exception as e:
                logger.error(f"Error invalidating institute cache: {e}")


def require_institute(f: Callable) -> Callable:
    """
    Decorator to require institute context.
    
    Usage:
        @app.route("/institute-data")
        @require_roles("teacher")
        @require_institute
        def get_institute_data():
            institute = g.current_institute
            return jsonify({"name": institute.name})
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if not hasattr(g, 'current_institute'):
            raise NotFoundError("Institute context required")
        return f(*args, **kwargs)
    return decorated


def get_current_institute() -> Optional[object]:
    """Get current institute from Flask g object."""
    return getattr(g, 'current_institute', None)


def get_current_institute_id() -> Optional[str]:
    """Get current institute ID from Flask g object."""
    return getattr(g, 'current_institute_id', None)


institute_context = InstituteContext()
