"""
Subscription service for ExamSaaS platform.
Plan activation, renewal, and feature access checks.
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

SUB_CACHE_PREFIX = "sub:"
SUB_CACHE_TTL = 300


def _get_redis():
    """Get Redis client for caching."""
    try:
        from app.extensions import get_redis
        return get_redis()
    except Exception:
        return None


def _get_model(name: str):
    """Lazy-load model to avoid circular imports."""
    from app.models import Subscription, Plan, Institute
    return Subscription, Plan, Institute


def _invalidate_sub_cache(institute_id: str = None, student_id: str = None) -> None:
    """Invalidate subscription cache."""
    redis = _get_redis()
    if not redis:
        return
    try:
        if institute_id:
            redis.delete(f"{SUB_CACHE_PREFIX}institute:{institute_id}")
        if student_id:
            redis.delete(f"{SUB_CACHE_PREFIX}student:{student_id}")
    except Exception as exc:
        logger.warning(f"Failed to invalidate sub cache: {exc}")


def _get_cached_sub(institute_id: str = None, student_id: str = None) -> Optional[Dict]:
    """Get cached subscription data from Redis."""
    redis = _get_redis()
    if not redis:
        return None
    try:
        key = f"{SUB_CACHE_PREFIX}institute:{institute_id}" if institute_id else f"{SUB_CACHE_PREFIX}student:{student_id}"
        data = redis.get(key)
        if data:
            import json
            return json.loads(data)
    except Exception:
        pass
    return None


def _set_sub_cache(institute_id: str = None, student_id: str = None, data: Dict = None) -> None:
    """Cache subscription data in Redis."""
    redis = _get_redis()
    if not redis or not data:
        return
    try:
        key = f"{SUB_CACHE_PREFIX}institute:{institute_id}" if institute_id else f"{SUB_CACHE_PREFIX}student:{student_id}"
        import json
        redis.setex(key, SUB_CACHE_TTL, json.dumps(data, default=str))
    except Exception as exc:
        logger.warning(f"Failed to set sub cache: {exc}")


def activate_subscription(
    entity_id: str,
    plan_id: str,
    payment_id: str,
    entity_type: str = "institute",
) -> "Subscription":
    """
    Activate or renew a subscription for an institute or student.

    If an active subscription exists, it extends from current expires_at.
    Otherwise creates a new subscription starting now.

    Args:
        entity_id: Institute or Student document ID
        plan_id: Plan document ID
        payment_id: Payment document ID (for reference)
        entity_type: 'institute' or 'student'

    Returns:
        Subscription document
    """
    Subscription, Plan, Institute = _get_model("subscription")

    from bson import ObjectId
    from app.models import Payment

    try:
        plan_oid = ObjectId(plan_id)
        entity_oid = ObjectId(entity_id)
    except Exception as exc:
        raise ValueError(f"Invalid plan_id or entity_id: {exc}")

    plan = Plan.objects(id=plan_oid).first()
    if not plan:
        raise ValueError(f"Plan not found: {plan_id}")

    payment = None
    if payment_id:
        try:
            payment = Payment.objects(id=ObjectId(payment_id)).first()
        except Exception:
            pass

    lookup = {"status__in": ["active", "grace"]}
    if entity_type == "institute":
        lookup["institute"] = entity_oid
    else:
        lookup["student"] = entity_oid

    existing = Subscription.objects(**lookup).first()

    if existing:
        start = existing.expires_at
        if start.tzinfo is None:
            from datetime import timezone as tz
            start = start.replace(tzinfo=tz.utc)
        logger.info(f"Renewing existing subscription {existing.id}")
    else:
        start = datetime.now(timezone.utc)

    expires = start + timedelta(days=plan.duration_days)
    grace = expires + timedelta(days=7)

    sub = Subscription(
        plan=plan,
        payment=payment,
        status="active",
        starts_at=start,
        expires_at=expires,
        grace_until=grace,
        ai_usage_this_month=0,
    )

    if entity_type == "institute":
        sub.institute = entity_oid
    else:
        sub.student = entity_oid

    sub.save()

    if entity_type == "institute":
        Institute.objects(id=entity_oid).update_one(set__subscription=sub)
        _invalidate_sub_cache(institute_id=entity_id)

    logger.info(
        f"Subscription activated: entity={entity_id}, plan={plan.name}, "
        f"expires={expires.isoformat()}"
    )

    return sub


def get_active_subscription(
    entity_id: str,
    entity_type: str = "institute",
) -> Optional["Subscription"]:
    """
    Get the active subscription for an entity with Redis caching.

    Args:
        entity_id: Institute or Student document ID
        entity_type: 'institute' or 'student'

    Returns:
        Subscription document or None
    """
    cached = _get_cached_sub(
        institute_id=entity_id if entity_type == "institute" else None,
        student_id=entity_id if entity_type == "student" else None,
    )
    if cached:
        logger.debug(f"Subscription cache hit for {entity_type} {entity_id}")
        return None

    Subscription, _, _ = _get_model("subscription")
    from bson import ObjectId

    try:
        entity_oid = ObjectId(entity_id)
    except Exception:
        return None

    lookup = {"status__in": ["active", "grace"]}
    if entity_type == "institute":
        lookup["institute"] = entity_oid
    else:
        lookup["student"] = entity_oid

    sub = Subscription.objects(**lookup).order_by("-starts_at").first()

    if sub:
        _set_sub_cache(
            institute_id=entity_id if entity_type == "institute" else None,
            student_id=entity_id if entity_type == "student" else None,
            data={"id": str(sub.id), "status": sub.status},
        )

    return sub


def check_feature_access(
    institute_id: str,
    feature: str,
) -> None:
    """
    Check if institute has access to a feature.
    Raises SubscriptionRequiredError or FeatureNotAvailableError if blocked.

    Args:
        institute_id: Institute document ID
        feature: Feature flag name (e.g. 'ai_recommendations', 'certificate_generation')

    Raises:
        SubscriptionRequiredError: No active subscription
        ValueError: Feature not available in current plan
    """
    Subscription, Plan, Institute = _get_model("subscription")

    from app.exceptions import SubscriptionRequiredError, FeatureNotAvailableError
    from bson import ObjectId

    try:
        institute_oid = ObjectId(institute_id)
    except Exception:
        raise SubscriptionRequiredError("Invalid institute ID")

    institute = Institute.objects(id=institute_oid).first()
    if not institute:
        raise SubscriptionRequiredError("Institute not found")

    now = datetime.now(timezone.utc)

    lookup = {"institute": institute_oid, "status__in": ["active", "grace"]}
    sub = Subscription.objects(**lookup).order_by("-starts_at").first()

    if not sub:
        raise SubscriptionRequiredError(
            "No active subscription. Please subscribe to access this feature."
        )

    expires = sub.expires_at
    if expires.tzinfo is None:
        from datetime import timezone as tz
        expires = expires.replace(tzinfo=tz.utc)

    grace_until = sub.grace_until
    if grace_until and grace_until.tzinfo is None:
        from datetime import timezone as tz
        grace_until = grace_until.replace(tzinfo=tz.utc)

    if sub.status == "expired" or (now > expires and (not grace_until or now > grace_until)):
        _invalidate_sub_cache(institute_id=institute_id)
        raise SubscriptionRequiredError(
            "Subscription expired. Please renew to continue."
        )

    plan = sub.plan
    if not plan:
        raise SubscriptionRequiredError("Plan data unavailable")

    flags = plan.feature_flags
    if flags is None:
        raise FeatureNotAvailableError(
            f"Feature '{feature}' is not available in the current plan."
        )

    has_feature = getattr(flags, feature, False)
    if not has_feature:
        raise FeatureNotAvailableError(
            f"'{feature}' is not available on your {plan.name} plan. "
            f"Please upgrade to access this feature."
        )


def increment_ai_usage(institute_id: str) -> None:
    """
    Increment AI usage counter for an institute.
    Raises FeatureNotAvailableError if usage limit exceeded.

    Args:
        institute_id: Institute document ID

    Raises:
        SubscriptionRequiredError: No active subscription
        FeatureNotAvailableError: AI usage limit exceeded
    """
    Subscription, _, Institute = _get_model("subscription")

    from app.exceptions import SubscriptionRequiredError, FeatureNotAvailableError
    from bson import ObjectId

    try:
        institute_oid = ObjectId(institute_id)
    except Exception:
        raise SubscriptionRequiredError("Invalid institute ID")

    lookup = {"institute": institute_oid, "status__in": ["active", "grace"]}
    sub = Subscription.objects(**lookup).order_by("-starts_at").first()

    if not sub:
        raise SubscriptionRequiredError("No active subscription")

    plan = sub.plan
    if not plan or plan.ai_usage_limit <= 0:
        raise FeatureNotAvailableError("AI features are not available on your plan.")

    if sub.ai_usage_this_month >= plan.ai_usage_limit:
        raise FeatureNotAvailableError(
            f"AI usage limit reached ({sub.ai_usage_this_month}/{plan.ai_usage_limit}/month). "
            f"Upgrade to a higher plan for more usage."
        )

    Subscription.objects(id=sub.id).update_one(inc__ai_usage_this_month=1)

    logger.info(
        f"AI usage incremented for institute {institute_id}: "
        f"{sub.ai_usage_this_month + 1}/{plan.ai_usage_limit}"
    )


def cancel_subscription(entity_id: str, entity_type: str = "institute") -> None:
    """
    Cancel a subscription (marks as cancelled, does not delete).

    Args:
        entity_id: Institute or Student document ID
        entity_type: 'institute' or 'student'
    """
    Subscription, _, Institute = _get_model("subscription")

    from bson import ObjectId

    try:
        entity_oid = ObjectId(entity_id)
    except Exception:
        raise ValueError(f"Invalid entity_id: {entity_id}")

    lookup = {"status__in": ["active", "grace"]}
    if entity_type == "institute":
        lookup["institute"] = entity_oid
    else:
        lookup["student"] = entity_oid

    sub = Subscription.objects(**lookup).first()
    if not sub:
        return

    sub.status = "cancelled"
    sub.save()

    if entity_type == "institute":
        _invalidate_sub_cache(institute_id=entity_id)

    logger.info(f"Subscription cancelled for {entity_type} {entity_id}")


def reset_monthly_usage() -> None:
    """
    Reset AI usage counters for all active subscriptions.
    Should be called by Celery beat on the 1st of each month.
    """
    Subscription, _, _ = _get_model("subscription")

    updated = Subscription.objects(status__in=["active", "grace"]).update(set__ai_usage_this_month=0)
    logger.info(f"Reset AI usage for {updated} subscriptions")
