"""
AI tasks for ExamSaaS platform.
Celery tasks for AI-powered features using Groq.
"""
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

try:
    from celery import Task
    
    class AITask(Task):
        """Base task class for AI operations."""
        max_retries = 2
        default_retry_delay = 30
        acks_late = True
        reject_on_worker_lost = True
        queue = "ai_queue"
        
        def on_failure(self, exc, task_id, args, kwargs, einfo):
            logger.error(f"AI task {task_id} failed: {exc}")
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
    def generate_questions_with_ai_task(
        self,
        creator_id: str,
        institute_id: str,
        topic: str,
        difficulty: str = "medium",
        n_questions: int = 5,
    ) -> Dict[str, Any]:
        """
        Generate questions with AI (manual teacher request).
        
        Args:
            creator_id: User ID of requesting teacher
            institute_id: Institute ID
            topic: Topic for questions
            difficulty: easy, medium, hard
            n_questions: Number of questions
        
        Returns:
            dict with generated questions
        """
        from app.models import Question, QuestionOption, User, Institute
        from app.services.ai_service import (
            generate_questions_from_text,
            AIServiceError,
            ParseError,
        )
        
        try:
            creator = User.objects(id=creator_id).first()
            if not creator:
                return {"status": "failed", "error": "User not found"}
            
            institute = None
            if institute_id:
                institute = Institute.objects(id=institute_id).first()
            
            try:
                questions = generate_questions_from_text(
                    text=f"Generate questions about {topic}",
                    n_questions=n_questions,
                    difficulty=difficulty,
                    topic=topic,
                )
            except (AIServiceError, ParseError) as e:
                logger.warning(f"AI question generation failed: {e}")
                return {"status": "failed", "error": str(e)}
            
            created = 0
            for q_data in questions:
                options = []
                correct_idx = 0
                
                for j, opt_text in enumerate(q_data.get("options", [])):
                    option_id = f"opt_{j}"
                    clean_text = opt_text
                    for prefix in [f"{chr(65+k)}. " for k in range(10)]:
                        if opt_text.startswith(prefix):
                            clean_text = opt_text[len(prefix):]
                            break
                    
                    options.append(QuestionOption(
                        option_id=option_id,
                        text=clean_text,
                    ))
                    
                    correct_answer = q_data.get("correct_answer", "").upper()
                    if correct_answer == chr(65 + j) or correct_answer == chr(97 + j):
                        correct_idx = j
                
                correct_option_id = f"opt_{correct_idx}"
                
                question = Question(
                    text=q_data["question"],
                    question_type="mcq",
                    options=options,
                    correct_option_id=correct_option_id,
                    explanation=q_data.get("explanation", ""),
                    difficulty=q_data.get("difficulty", difficulty),
                    topic=q_data.get("topic", topic),
                    source="ai_generated",
                    is_reviewed=False,
                    is_approved=False,
                    created_by=creator,
                    institute=institute,
                )
                question.save()
                created += 1
            
            logger.info(f"Generated {created} questions for topic '{topic}' by user {creator_id}")
            
            return {
                "status": "completed",
                "questions_created": created,
                "topic": topic,
                "difficulty": difficulty,
            }
        
        except Exception as exc:
            logger.exception(f"generate_questions_with_ai_task failed: {exc}")
            
            if self.request.retries < self.max_retries:
                raise self.retry(exc=exc, countdown=30 * (2 ** self.request.retries))
            
            return {"status": "failed", "error": str(exc)}

    @_celery_task
    def analyze_exam_quality_task(self, exam_id: str) -> Dict[str, Any]:
        """
        Analyze exam questions for quality and balance.
        
        Args:
            exam_id: Exam ID
        
        Returns:
            Analysis results
        """
        from app.models import Exam, Question
        from app.services.ai_service import call_groq, AIServiceError
        
        try:
            exam = Exam.objects(id=exam_id).first()
            if not exam:
                return {"status": "failed", "error": "Exam not found"}
            
            questions = list(Question.objects(institute=exam.institute)[:20])
            
            if not questions:
                return {"status": "failed", "error": "No questions found"}
            
            difficulty_dist = {"easy": 0, "medium": 0, "hard": 0}
            topics = {}
            
            for q in questions:
                difficulty_dist[q.difficulty] = difficulty_dist.get(q.difficulty, 0) + 1
                topic = q.topic or "General"
                topics[topic] = topics.get(topic, 0) + 1
            
            analysis = {
                "total_questions": len(questions),
                "difficulty_distribution": difficulty_dist,
                "topics_covered": list(topics.keys()),
                "balance_score": _calculate_balance_score(difficulty_dist, topics),
            }
            
            logger.info(f"Exam quality analysis for {exam_id}: {analysis}")
            
            return {"status": "completed", "analysis": analysis}
        
        except Exception as exc:
            logger.exception(f"analyze_exam_quality_task failed: {exc}")
            return {"status": "failed", "error": str(exc)}

    @_celery_task
    def suggest_exam_improvements_task(self, exam_id: str) -> Dict[str, Any]:
        """
        Suggest improvements for exam questions.
        
        Args:
            exam_id: Exam ID
        
        Returns:
            Improvement suggestions
        """
        from app.models import Exam, Question
        
        try:
            exam = Exam.objects(id=exam_id).first()
            if not exam:
                return {"status": "failed", "error": "Exam not found"}
            
            suggestions = []
            
            if exam.total_marks == 0:
                suggestions.append("Exam has no total marks configured")
            
            if exam.duration_minutes == 0:
                suggestions.append("Exam has no duration set")
            
            questions = Question.objects(institute=exam.institute)
            if questions.count() < 5:
                suggestions.append(f"Consider adding more questions (current: {questions.count()})")
            
            logger.info(f"Improvement suggestions for exam {exam_id}: {suggestions}")
            
            return {"status": "completed", "suggestions": suggestions}
        
        except Exception as exc:
            logger.exception(f"suggest_exam_improvements_task failed: {exc}")
            return {"status": "failed", "error": str(exc)}

except ImportError:
    logger.warning("Celery not available - AI task decorators not applied")
    
    def generate_questions_with_ai_task(
        creator_id: str,
        institute_id: str,
        topic: str,
        difficulty: str = "medium",
        n_questions: int = 5,
    ) -> Dict[str, Any]:
        """Fallback when Celery not available."""
        logger.warning("generate_questions_with_ai_task called without Celery")
        return {"status": "failed", "error": "Celery not available"}
    
    def analyze_exam_quality_task(exam_id: str) -> Dict[str, Any]:
        """Fallback when Celery not available."""
        logger.warning("analyze_exam_quality_task called without Celery")
        return {"status": "failed", "error": "Celery not available"}
    
    def suggest_exam_improvements_task(exam_id: str) -> Dict[str, Any]:
        """Fallback when Celery not available."""
        logger.warning("suggest_exam_improvements_task called without Celery")
        return {"status": "failed", "error": "Celery not available"}


def _calculate_balance_score(difficulty_dist: Dict[str, int], topics: Dict[str, int]) -> float:
    """
    Calculate exam balance score based on difficulty and topic distribution.
    
    Returns:
        Score from 0 to 100
    """
    if not difficulty_dist or not topics:
        return 0.0
    
    difficulty_score = 50.0
    if difficulty_dist.get("easy", 0) > 0 and difficulty_dist.get("hard", 0) > 0:
        difficulty_score = 75.0
    
    topic_score = min(25.0, len(topics) * 5)
    
    return round(difficulty_score + topic_score, 2)


logger.info("AI tasks module loaded")
