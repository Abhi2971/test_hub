"""
Subscription check middleware for ExamSaaS platform.
Plan limits and feature flag enforcement.
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Callable, List
from functools import wraps

from flask import Flask, request, g, Response

from app.exceptions import (
    SubscriptionRequiredError,
    FeatureNotAvailableError,
    RateLimitError,
)

logger = logging.getLogger(__name__)


FEATURE_LIMITS = {
    "create_exam": "exam_limit",
    "add_student": "max_students",
    "add_teacher": "max_teachers",
    "ai_call": "ai_usage_limit",
}


class SubscriptionChecker:
    """
    Subscription and feature check middleware.
    
    Used as a decorator: @check_feature("pdf_exam_generation")
    
    Logic:
      1. Fetch institute's active Subscription via g.current_institute
      2. If no active subscription: raise SubscriptionRequiredError(402)
      3. If subscription.status == "expired" AND datetime.now() > grace_until:
         raise SubscriptionRequiredError(402, "Subscription expired")
      4. If subscription.status == "expired" AND within grace:
         set response header: X-Subscription-Warning: "Expires in N days"
      5. Check feature flag: if not plan.feature_flags[feature]: raise FeatureNotAvailableError
      6. Check limits:
         - "create_exam": count exams created this billing period vs plan.exam_limit
         - "add_student": count active students vs plan.max_students
         - "add_teacher": count active teachers vs plan.max_teachers
         - "ai_call": check subscription.ai_usage_this_month vs plan.ai_usage_limit
    """
    
    def __init__(self, app: Optional[Flask] = None):
        self.app = app
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask) -> None:
        """Initialize middleware with Flask app."""
        self.app = app
        app.logger.info("SubscriptionChecker middleware initialized")
    
    def _get_subscription(self) -> Optional[object]:
        """Get current subscription from g.current_institute."""
        institute = getattr(g, 'current_institute', None)
        
        if institute is None:
            institute_id = getattr(g, 'current_institute_id', None)
            if institute_id:
                try:
                    from app.models import Institute
                    institute = Institute.objects(id=institute_id).first()
                    g.current_institute = institute
                except Exception as e:
                    logger.error(f"Error loading institute: {e}")
        
        if institute and institute.subscription:
            try:
                from app.models import Subscription
                return Subscription.objects(id=institute.subscription.id).first()
            except Exception as e:
                logger.error(f"Error loading subscription: {e}")
        
        return None
    
    def _is_subscription_active(self, subscription) -> bool:
        """Check if subscription is active."""
        if not subscription:
            return False
        
        if subscription.status == "active":
            return True
        
        if subscription.status == "trial":
            return True
        
        if subscription.status == "expired":
            grace_until = getattr(subscription, 'grace_until', None)
            if grace_until:
                if datetime.now(timezone.utc) > grace_until:
                    return False
                return True
        
        return False
    
    def _check_expiration_warning(self, subscription) -> Optional[str]:
        """Check if subscription is about to expire and return warning message."""
        if not subscription:
            return None
        
        if subscription.status != "expired":
            return None
        
        grace_until = getattr(subscription, 'grace_until', None)
        if not grace_until:
            return None
        
        now = datetime.now(timezone.utc)
        if grace_until > now:
            days_remaining = (grace_until - now).days
            if days_remaining <= 7:
                return f"Expires in {days_remaining} days"
        
        return None
    
    def _get_plan(self, subscription) -> Optional[object]:
        """Get plan from subscription."""
        if not subscription or not subscription.plan:
            return None
        
        try:
            from app.models import Plan
            return Plan.objects(id=subscription.plan.id).first()
        except Exception:
            return None
    
    def _check_feature_flag(self, plan, feature: str) -> bool:
        """Check if feature is enabled in plan."""
        if not plan:
            return False
        
        feature_flags = getattr(plan, 'feature_flags', {})
        return feature_flags.get(feature, False)
    
    def _check_limit(self, plan, subscription, feature: str) -> Optional[str]:
        """
        Check if user has exceeded a limit.
        
        Returns:
            None if OK, error message if limit exceeded
        """
        limit_type = FEATURE_LIMITS.get(feature)
        
        if not limit_type:
            return None
        
        try:
            if feature == "create_exam":
                from app.models import Exam
                period_start = getattr(subscription, 'billing_period_start', None)
                if not period_start:
                    return None
                
                count = Exam.objects(
                    institute=subscription.institute,
                    created_at__gte=period_start
                ).count()
                limit = getattr(plan, 'exam_limit', 0)
                
                if count >= limit:
                    return f"Exam limit reached ({count}/{limit}). Upgrade your plan."
            
            elif feature == "add_student":
                from app.models import User
                count = User.objects(
                    institute=subscription.institute,
                    role__in=['student_registered', 'student_assigned'],
                    is_active=True
                ).count()
                limit = getattr(plan, 'max_students', 0)
                
                if count >= limit:
                    return f"Student limit reached ({count}/{limit}). Upgrade your plan."
            
            elif feature == "add_teacher":
                from app.models import User
                count = User.objects(
                    institute=subscription.institute,
                    role='teacher',
                    is_active=True
                ).count()
                limit = getattr(plan, 'max_teachers', 0)
                
                if count >= limit:
                    return f"Teacher limit reached ({count}/{limit}). Upgrade your plan."
            
            elif feature == "ai_call":
                usage = getattr(subscription, 'ai_usage_this_month', 0)
                limit = getattr(plan, 'ai_usage_limit', 0)
                
                if usage >= limit:
                    return f"AI usage limit reached ({usage}/{limit}). Upgrade your plan."
        
        except Exception as e:
            logger.error(f"Error checking limit: {e}")
        
        return None
    
    def check_feature(self, feature: str) -> None:
        """
        Check if feature is available for current subscription.
        
        Args:
            feature: Feature name to check
        
        Raises:
            SubscriptionRequiredError: If no active subscription
            FeatureNotAvailableError: If feature not in plan
            RateLimitError: If limit exceeded
        """
        if getattr(g, 'current_role', None) in ['super_admin', 'admin_public']:
            return
        
        subscription = self._get_subscription()
        
        if not self._is_subscription_active(subscription):
            raise SubscriptionRequiredError(
                "Active subscription required. Please subscribe to access this feature."
            )
        
        warning = self._check_expiration_warning(subscription)
        if warning and hasattr(g, '_response_headers'):
            g._response_headers['X-Subscription-Warning'] = warning
        
        plan = self._get_plan(subscription)
        
        if plan and not self._check_feature_flag(plan, feature):
            raise FeatureNotAvailableError(
                f"This feature is not available in your current plan. "
                f"Please upgrade to access it."
            )
        
        limit_error = self._check_limit(plan, subscription, feature)
        if limit_error:
            raise RateLimitError(
                message=limit_error,
                retry_after=0,
                errors={"limit_reached": True}
            )
    
    def add_subscription_headers(self, response: Response) -> None:
        """Add subscription-related headers to response."""
        subscription = self._get_subscription()
        
        if subscription:
            warning = self._check_expiration_warning(subscription)
            if warning:
                response.headers['X-Subscription-Warning'] = warning
            
            response.headers['X-Subscription-Status'] = subscription.status


def check_feature(feature: str) -> Callable:
    """
    Decorator to check feature availability.
    
    Usage:
        @exam_bp.route("/", methods=["POST"])
        @require_roles("teacher")
        @check_feature("create_exam")
        def create_exam(): ...
    
    Args:
        feature: Feature name to check
    
    Returns:
        Decorated function
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args, **kwargs):
            checker = SubscriptionChecker()
            checker.check_feature(feature)
            
            response = f(*args, **kwargs)
            
            if isinstance(response, Response):
                checker.add_subscription_headers(response)
            
            return response
        
        return decorated
    return decorator


subscription_checker = SubscriptionChecker()
