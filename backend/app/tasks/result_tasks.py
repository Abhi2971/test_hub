"""
Result tasks for ExamSaaS platform.
Celery tasks for AI recommendations post-exam.
"""
import logging
import json
from datetime import datetime, timezone
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

try:
    from celery import Task
    
    class ResultTask(Task):
        """Base task class for result operations."""
        max_retries = 2
        default_retry_delay = 30
        acks_late = True
        reject_on_worker_lost = True
        queue = "ai_queue"
        
        def on_failure(self, exc, task_id, args, kwargs, einfo):
            logger.error(f"Result task {task_id} failed: {exc}")
            super().on_failure(exc, task_id, args, kwargs, einfo)
    
    def _celery_task(func):
        """Decorator to make a function a Celery task."""
        from app.extensions import celery
        return celery.task(
            bind=True,
            max_retries=2,
            default_retry_delay=30,
            acks_late=True,
            reject_on_worker_lost=True,
            queue="ai_queue",
        )(func)

    @_celery_task
    def generate_ai_recommendation_task(self, result_id: str) -> Dict[str, Any]:
        """
        Generate AI-powered learning recommendations for a student.
        
        Args:
            result_id: Result document ID
        
        Returns:
            Recommendation result
        """
        from app.models import Result, AIRecommendation
        from app.services.ai_service import (
            generate_ai_recommendations,
            generate_fallback_recommendations,
            cache_ai_response,
            get_cached_ai_response,
            generate_cache_key,
            AIServiceError,
        )
        
        try:
            result = Result.objects(id=result_id).first()
            if not result:
                logger.error(f"Result not found: {result_id}")
                return {"status": "failed", "error": "Result not found"}
            
            existing = AIRecommendation.objects(result=result).first()
            if existing:
                return {"status": "exists", "recommendation_id": str(existing.id)}
            
            weak_topics = []
            for topic_perf in (result.topic_performance or []):
                if topic_perf.percentage and topic_perf.percentage < 60:
                    weak_topics.append(topic_perf.topic or "General")
            
            if not weak_topics:
                weak_topics = ["General topics"]
            
            cache_key = generate_cache_key(
                str(result.exam.id if result.exam else "unknown"),
                "_".join(sorted(weak_topics)),
            )
            
            cached = get_cached_ai_response(cache_key)
            if cached:
                logger.info(f"Using cached AI recommendation for result {result_id}")
                
                recommendation = AIRecommendation(
                    result=result,
                    student=result.student,
                    exam=result.exam,
                    weak_topics=cached.get("weak_areas", weak_topics),
                    recommendations=cached.get("recommendations", []),
                    learning_path=cached.get("learning_path", weak_topics),
                    next_difficulty=cached.get("next_difficulty", "medium"),
                    motivational_message=cached.get("motivational_message", ""),
                    processing_status="completed",
                    is_from_cache=True,
                )
                recommendation.save()
                
                _suggest_ebooks(recommendation, weak_topics)
                
                return {"status": "completed", "recommendation_id": str(recommendation.id), "from_cache": True}
            
            recommendation = AIRecommendation(
                result=result,
                student=result.student,
                exam=result.exam,
                processing_status="processing",
            )
            recommendation.save()
            
            history_summary = []
            if result.student:
                from app.models import Result as ResultModel
                past_results = ResultModel.objects(
                    student=result.student,
                    created_at__lt=result.created_at,
                ).order_by("-created_at")[:5]
                
                for pr in past_results:
                    history_summary.append({
                        "exam_title": pr.exam.title if pr.exam else "Unknown",
                        "percentage": pr.percentage or 0,
                        "grade": pr.grade or "N/A",
                    })
            
            try:
                ai_response = generate_ai_recommendations(
                    weak_topics=weak_topics,
                    score_percentage=result.percentage or 0,
                    grade=result.grade or "F",
                    exam_subject=result.exam.subject if result.exam else None,
                    history=history_summary,
                )
                
                recommendation.weak_topics = ai_response.get("weak_areas", weak_topics)
                recommendation.recommendations = ai_response.get("recommendations", [])
                recommendation.learning_path = ai_response.get("learning_path", weak_topics)
                recommendation.next_difficulty = ai_response.get("next_difficulty", "medium")
                recommendation.motivational_message = ai_response.get("motivational_message", "")
                recommendation.processing_status = "completed"
                recommendation.save()
                
                cache_ai_response(cache_key, ai_response, ttl=86400)
                
            except AIServiceError as e:
                logger.warning(f"AI service failed, using fallback: {e}")
                
                fallback = generate_fallback_recommendations(
                    weak_topics=weak_topics,
                    score_percentage=result.percentage or 0,
                )
                
                recommendation.weak_topics = fallback["weak_areas"]
                recommendation.recommendations = fallback["recommendations"]
                recommendation.learning_path = fallback["learning_path"]
                recommendation.next_difficulty = fallback["next_difficulty"]
                recommendation.motivational_message = fallback["motivational_message"]
                recommendation.processing_status = "completed"
                recommendation.save()
            
            _suggest_ebooks(recommendation, recommendation.weak_topics or [])
            
            logger.info(f"AI recommendation generated for result {result_id}")
            
            return {"status": "completed", "recommendation_id": str(recommendation.id)}
        
        except Exception as exc:
            logger.exception(f"generate_ai_recommendation_task failed: {exc}")
            
            if self.request.retries < self.max_retries:
                raise self.retry(exc=exc, countdown=30 * (2 ** self.request.retries))
            
            return {"status": "failed", "error": str(exc)}

except ImportError:
    logger.warning("Celery not available - result task decorators not applied")
    
    def generate_ai_recommendation_task(result_id: str) -> Dict[str, Any]:
        """Fallback when Celery not available."""
        logger.warning("generate_ai_recommendation_task called without Celery")
        return {"status": "failed", "error": "Celery not available"}


def _suggest_ebooks(recommendation, weak_topics: List[str]) -> None:
    """
    Match weak topics to suggested ebooks.
    
    Args:
        recommendation: AIRecommendation document
        weak_topics: List of weak topics
    """
    try:
        from app.models import Ebook
        
        if not weak_topics:
            return
        
        suggested_ebooks = Ebook.objects(
            topics__overlap=weak_topics,
            is_active=True,
        )[:5]
        
        if suggested_ebooks:
            recommendation.suggested_ebook_ids = [str(eb.id) for eb in suggested_ebooks]
            recommendation.save()
    
    except Exception as e:
        logger.warning(f"Failed to suggest ebooks: {e}")


logger.info("Result tasks module loaded")
