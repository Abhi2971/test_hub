"""
Exam tasks for ExamSaaS platform.
Celery tasks for exam operations.
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any

logger = logging.getLogger(__name__)

try:
    from celery import Task
    
    class ExamTask(Task):
        """Base task class for exam operations."""
        max_retries = 1
        default_retry_delay = 300
        acks_late = True
        reject_on_worker_lost = True
        
        def on_failure(self, exc, task_id, args, kwargs, einfo):
            logger.error(f"Exam task {task_id} failed: {exc}")
            super().on_failure(exc, task_id, args, kwargs, einfo)
    
    def _celery_task(func):
        """Decorator to make a function a Celery task."""
        from app.extensions import celery
        return celery.task(
            bind=True,
            max_retries=1,
            default_retry_delay=300,
            acks_late=True,
            reject_on_worker_lost=True,
        )(func)

    @_celery_task
    def auto_close_expired_exams_task(self) -> Dict[str, Any]:
        """
        Auto-close exams that have ended and auto-submit in-progress attempts.
        Runs every 5 minutes via Celery beat.
        
        Returns:
            dict with count of closed exams and auto-submitted attempts
        """
        try:
            from app.models import Exam, ExamAttempt
            
            now = datetime.now(timezone.utc)
            
            exams = Exam.objects(status="active")
            closed_count = 0
            auto_submitted_count = 0
            
            for exam in exams:
                should_close = False
                
                if exam.schedule and exam.schedule.end_at:
                    grace = exam.schedule.grace_minutes or 0
                    grace_end = exam.schedule.end_at + timedelta(minutes=grace)
                    
                    if now > grace_end:
                        should_close = True
                
                if should_close:
                    exam.status = "closed"
                    exam.save()
                    closed_count += 1
                    
                    in_progress_attempts = ExamAttempt.objects(
                        exam=exam,
                        status="in_progress"
                    )
                    
                    for attempt in in_progress_attempts:
                        attempt.status = "auto_submitted"
                        attempt.submitted_at = now
                        attempt.save()
                        auto_submitted_count += 1
                        
                        try:
                            from app.services.result_service import calculate_result
                            calculate_result(str(attempt.id))
                        except Exception as e:
                            logger.error(f"Failed to calculate result for attempt {attempt.id}: {e}")
                    
                    logger.info(f"Auto-closed exam {exam.id} with {in_progress_attempts.count()} auto-submitted attempts")
            
            logger.info(f"Auto-close task completed: {closed_count} exams closed, {auto_submitted_count} attempts auto-submitted")
            
            return {
                "closed_exams": closed_count,
                "auto_submitted_attempts": auto_submitted_count,
                "checked_at": now.isoformat(),
            }
        
        except Exception as exc:
            logger.exception(f"auto_close_expired_exams_task failed: {exc}")
            return {"error": str(exc)}

    @_celery_task
    def auto_publish_scheduled_exams_task(self) -> Dict[str, Any]:
        """
        Check for exams that need to be activated.
        Published exams are automatically active during their schedule window.
        
        Returns:
            dict with processing stats
        """
        try:
            from app.models import Exam
            
            now = datetime.now(timezone.utc)
            activated_count = 0
            
            exams_to_activate = Exam.objects(
                status="published",
                schedule__end_at__gte=now,
            )
            
            for exam in exams_to_activate:
                if exam.schedule and exam.schedule.start_at:
                    if exam.schedule.start_at <= now <= exam.schedule.end_at + timedelta(minutes=exam.schedule.grace_minutes or 0):
                        exam.status = "active"
                        exam.save()
                        activated_count += 1
                        logger.info(f"Activated exam {exam.id}: {exam.title}")
            
            logger.info(f"Auto-publish task completed: {activated_count} exams activated")
            
            return {
                "activated_exams": activated_count,
                "checked_at": now.isoformat(),
            }
        
        except Exception as exc:
            logger.exception(f"auto_publish_scheduled_exams_task failed: {exc}")
            return {"error": str(exc)}

except ImportError:
    logger.warning("Celery not available - exam task decorators not applied")
    
    def auto_close_expired_exams_task() -> Dict[str, Any]:
        """Fallback when Celery not available."""
        logger.warning("auto_close_expired_exams_task called without Celery")
        return {"error": "Celery not available"}
    
    def auto_publish_scheduled_exams_task() -> Dict[str, Any]:
        """Fallback when Celery not available."""
        logger.warning("auto_publish_scheduled_exams_task called without Celery")
        return {"error": "Celery not available"}


    @_celery_task
    def reset_monthly_ai_usage_task(self) -> Dict[str, Any]:
        """
        Reset AI usage counters for all active subscriptions.
        Runs on the 1st of every month at 00:05 via Celery beat.
        
        Returns:
            dict with count of updated subscriptions
        """
        try:
            from app.services.subscription_service import reset_monthly_usage
            
            updated = reset_monthly_usage()
            logger.info(f"Monthly AI usage reset task completed")
            
            return {"status": "completed", "updated": updated}
        
        except Exception as exc:
            logger.exception(f"reset_monthly_ai_usage_task failed: {exc}")
            return {"error": str(exc)}


logger.info("Exam tasks module loaded")
