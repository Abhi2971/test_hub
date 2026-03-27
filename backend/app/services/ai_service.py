"""
AI service for ExamSaaS platform.
Groq API wrapper with retry logic and fallbacks.
"""
import json
import logging
import re
import time
from typing import Dict, Any, Optional, List

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
            logger.warning("Redis not available for AI service")
            return None
    return REDIS_CLIENT


def _get_config(key: str, default: Any = None) -> Any:
    """Get configuration value."""
    try:
        from flask import current_app
        return current_app.config.get(key, default)
    except RuntimeError:
        return default


class AIServiceError(Exception):
    """Base exception for AI service errors."""
    pass


class RateLimitError(AIServiceError):
    """Rate limit exceeded."""
    pass


class ParseError(AIServiceError):
    """Failed to parse AI response."""
    pass


def call_groq(
    prompt: str,
    max_tokens: int = 1000,
    temperature: float = 0.3,
    model: Optional[str] = None,
) -> str:
    """
    Call Groq API with retry logic.
    
    Args:
        prompt: System prompt
        max_tokens: Maximum tokens in response
        temperature: Temperature for generation
        model: Model name (defaults to config GROQ_MODEL)
    
    Returns:
        Raw text response from Groq
    
    Raises:
        AIServiceError: If API fails after retries
    """
    api_key = _get_config("GROQ_API_KEY")
    if not api_key:
        raise AIServiceError("Groq API key not configured")
    
    model = model or _get_config("GROQ_MODEL", "llama-3.1-70b-versatile")
    
    try:
        from groq import Groq, RateLimitError as GroqRateLimitError
    except ImportError:
        raise AIServiceError("Groq library not installed")
    
    client = Groq(api_key=api_key)
    
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            
            content = response.choices[0].message.content
            logger.info(f"Groq API call successful (attempt {attempt + 1})")
            return content
        
        except Exception as e:
            error_str = str(e).lower()
            
            if "rate limit" in error_str or "429" in error_str:
                wait_time = 5 * (2 ** attempt)
                logger.warning(f"Groq rate limit, waiting {wait_time}s (attempt {attempt + 1})")
                time.sleep(wait_time)
                continue
            
            logger.error(f"Groq API error attempt {attempt + 1}: {e}")
            
            if attempt == 2:
                raise AIServiceError(f"Groq API failed after 3 attempts: {e}")
    
    raise AIServiceError("Groq API unavailable after 3 attempts")


def parse_json_response(text: str) -> Dict[Any, Any] | List[Any]:
    """
    Strip markdown fences and parse JSON.
    
    Args:
        text: Raw text containing JSON
    
    Returns:
        Parsed JSON (dict or list)
    
    Raises:
        ParseError: If JSON is malformed
    """
    text = text.strip()
    
    text = re.sub(r"```(?:json)?\s*", "", text)
    text = re.sub(r"```\s*$", "", text)
    text = text.strip()
    
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ParseError(f"Failed to parse JSON: {e}")


def generate_questions_from_text(
    text: str,
    n_questions: int = 5,
    difficulty: str = "medium",
    topic: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Generate MCQ questions from educational text.
    
    Args:
        text: Educational text content
        n_questions: Number of questions to generate
        difficulty: Target difficulty level
        topic: Topic name (optional)
    
    Returns:
        List of question dictionaries
    """
    topic_hint = f"Topic: {topic}\n" if topic else ""
    
    prompt = f"""You are an expert educator creating exam questions.
From the educational text below, generate {n_questions} high-quality MCQ questions.
Return ONLY a valid JSON array. No markdown, no explanation, no preamble.
Each object must have exactly these fields:
[{{
  "question": "Clear question text ending with ?",
  "options": ["A. option1", "B. option2", "C. option3", "D. option4"],
  "correct_answer": "A",
  "difficulty": "{difficulty}",
  "topic": "specific topic from the text",
  "explanation": "Why this is the correct answer"
}}]
{topic_hint}TEXT: {text[:4000]}"""
    
    response = call_groq(prompt, max_tokens=2000, temperature=0.3)
    
    parsed = parse_json_response(response)
    
    if not isinstance(parsed, list):
        raise ParseError("Expected JSON array of questions")
    
    questions = []
    for item in parsed:
        if not all(k in item for k in ["question", "options", "correct_answer", "explanation"]):
            continue
        
        if len(item.get("options", [])) < 2:
            continue
        
        questions.append({
            "text": item["question"],
            "options": item["options"],
            "correct_answer": item["correct_answer"],
            "difficulty": item.get("difficulty", difficulty),
            "topic": item.get("topic", topic or "General"),
            "explanation": item["explanation"],
        })
    
    return questions


def generate_ai_recommendations(
    weak_topics: List[str],
    score_percentage: float,
    grade: str,
    exam_subject: Optional[str] = None,
    history: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Generate personalized learning recommendations.
    
    Args:
        weak_topics: List of topics with low scores
        score_percentage: Overall score percentage
        grade: Letter grade
        exam_subject: Subject name (optional)
        history: List of past results (optional)
    
    Returns:
        Dict with recommendations
    """
    history_text = ""
    if history:
        history_text = "\n".join([
            f"- {h.get('exam_title', 'Exam')}: {h.get('percentage', 0):.1f}% ({h.get('grade', 'N/A')})"
            for h in history[:5]
        ])
        history_text = f"\nRecent history:\n{history_text}"
    
    subject_hint = f"Subject: {exam_subject}\n" if exam_subject else ""
    
    prompt = f"""Analyze this student's exam performance and provide personalized recommendations.
{subject_hint}Weak topics (< 60%): {', '.join(weak_topics)}
Score: {score_percentage:.1f}% (Grade: {grade})
{history_text}

Return ONLY valid JSON (no markdown):
{{
  "weak_areas": ["specific concept 1", "specific concept 2"],
  "recommendations": [
    "Actionable study tip 1 (specific, not generic)",
    "Actionable study tip 2",
    "Actionable study tip 3"
  ],
  "learning_path": ["topic to study first", "then second", "then third"],
  "next_difficulty": "easy|medium|hard",
  "motivational_message": "One encouraging sentence."
}}"""
    
    response = call_groq(prompt, max_tokens=800, temperature=0.4)
    
    parsed = parse_json_response(response)
    
    if not isinstance(parsed, dict):
        raise ParseError("Expected JSON object with recommendations")
    
    return {
        "weak_areas": parsed.get("weak_areas", weak_topics[:3]),
        "recommendations": parsed.get("recommendations", [
            f"Review {t}" for t in weak_topics[:3]
        ]),
        "learning_path": parsed.get("learning_path", weak_topics),
        "next_difficulty": parsed.get("next_difficulty", "medium"),
        "motivational_message": parsed.get("motivational_message", "Keep practicing!"),
    }


def generate_fallback_recommendations(
    weak_topics: List[str],
    score_percentage: float,
) -> Dict[str, Any]:
    """
    Generate rule-based fallback recommendations.
    
    Args:
        weak_topics: Topics with low scores
        score_percentage: Overall percentage
    
    Returns:
        Dict with basic recommendations
    """
    next_difficulty = "easy" if score_percentage < 40 else "medium"
    
    return {
        "weak_areas": weak_topics[:3],
        "recommendations": [
            f"Review {t} — you scored below 60% on this topic"
            for t in weak_topics[:3]
        ],
        "learning_path": weak_topics,
        "next_difficulty": next_difficulty,
        "motivational_message": "Keep practicing — improvement comes with consistency.",
        "is_fallback": True,
    }


def cache_ai_response(cache_key: str, data: Dict[str, Any], ttl: int = 86400) -> None:
    """
    Cache AI response in Redis.
    
    Args:
        cache_key: Cache key
        data: Data to cache
        ttl: Time to live in seconds (default 24h)
    """
    redis = _get_redis()
    if not redis:
        return
    
    try:
        redis.setex(cache_key, ttl, json.dumps(data))
        logger.debug(f"Cached AI response: {cache_key}")
    except Exception as e:
        logger.error(f"Failed to cache AI response: {e}")


def get_cached_ai_response(cache_key: str) -> Optional[Dict[str, Any]]:
    """
    Get cached AI response from Redis.
    
    Args:
        cache_key: Cache key
    
    Returns:
        Cached data or None
    """
    redis = _get_redis()
    if not redis:
        return None
    
    try:
        data = redis.get(cache_key)
        if data:
            logger.debug(f"Cache hit: {cache_key}")
            return json.loads(data)
    except Exception as e:
        logger.error(f"Failed to get cached AI response: {e}")
    
    return None


def generate_cache_key(*parts: str) -> str:
    """
    Generate a cache key from parts.
    
    Args:
        *parts: Key components
    
    Returns:
        Cache key string
    """
    import hashlib
    sorted_parts = sorted(str(p) for p in parts)
    combined = "_".join(sorted_parts)
    return f"ai:{hashlib.md5(combined.encode()).hexdigest()}"


def generate_questions(data: dict) -> dict:
    """Wrapper for generating questions from text. Routes expect this function name."""
    topic = data.get('topic', 'General')
    difficulty = data.get('difficulty', 'medium')
    count = data.get('count', 10)
    subject = data.get('subject', '')
    
    result = generate_questions_from_text(
        text=f"Generate {count} {difficulty} questions about {topic}" + (f" in {subject}" if subject else ""),
        topic=topic,
        difficulty=difficulty,
        count=count,
    )
    return {
        'questions': result.get('questions', []),
        'topic': topic,
        'difficulty': difficulty,
    }


def get_task_status(task_id: str) -> dict:
    """Get Celery task status from Redis."""
    redis = _get_redis()
    if redis is None:
        return {'status': 'unknown', 'result': None}
    
    try:
        key = f"celery_task:{task_id}"
        data = redis.get(key)
        if data:
            import json
            return json.loads(data)
    except Exception as e:
        logger.error(f"Failed to get task status: {e}")
    
    return {'status': 'PENDING', 'result': None}


def analyze_exam(exam_id: str, user_id: str) -> dict:
    """Analyze exam quality using AI."""
    from app.models import Exam, Question
    
    try:
        exam = Exam.objects(id=exam_id).first()
        if not exam:
            raise AIServiceError("Exam not found")
        
        questions = Question.objects(exam=exam)
        question_texts = [q.text for q in questions]
        
        prompt = f"Analyze the following exam questions for quality:\n" + "\n".join(f"- {t}" for t in question_texts)
        
        result = call_groq(prompt, system="You are an educational assessment expert.")
        
        return {
            'exam_id': str(exam_id),
            'analysis': result,
            'question_count': len(question_texts),
        }
    except Exception as e:
        logger.error(f"Exam analysis failed: {e}")
        raise AIServiceError(f"Failed to analyze exam: {str(e)}")


def get_recommendations(result_id: str, user_id: str) -> dict:
    """Get AI recommendations for a result."""
    from app.models import AIRecommendation
    
    try:
        rec = AIRecommendation.objects(result=result_id).first()
        if not rec:
            return {'status': 'pending', 'recommendations': None}
        
        return {
            'status': 'completed' if rec.is_generated else 'pending',
            'recommendations': rec.recommendations if rec.is_generated else None,
            'strengths': rec.strengths if rec.is_generated else None,
            'topics_to_improve': rec.topics_to_improve if rec.is_generated else None,
        }
    except Exception as e:
        logger.error(f"Failed to get recommendations: {e}")
        raise AIServiceError(f"Failed to get recommendations: {str(e)}")


logger.info("AI service loaded")
