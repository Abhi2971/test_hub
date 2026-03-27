"""
Attempt service for ExamSaaS platform.
Pure Python - zero Flask imports, zero HTTP concepts.
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List

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
            logger.warning("Redis not available for attempt service")
            return None
    return REDIS_CLIENT


class AttemptServiceError(Exception):
    """Base exception for attempt service errors."""
    def __init__(self, message: str, code: str, status_code: int = 400):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class AttemptNotFoundError(AttemptServiceError):
    """Attempt not found."""
    def __init__(self):
        super().__init__("Attempt not found", "ATTEMPT_NOT_FOUND", 404)


class AttemptNotInProgressError(AttemptServiceError):
    """Attempt not in progress."""
    def __init__(self):
        super().__init__("Attempt is not in progress", "ATTEMPT_NOT_IN_PROGRESS", 400)


class AttemptAlreadySubmittedError(AttemptServiceError):
    """Attempt already submitted."""
    def __init__(self):
        super().__init__("Attempt already submitted", "ATTEMPT_ALREADY_SUBMITTED", 400)


class ExamNotAvailableError(AttemptServiceError):
    """Exam not available."""
    def __init__(self, message: str = "Exam is not available"):
        super().__init__(message, "EXAM_NOT_AVAILABLE", 403)


class MaxAttemptsReachedError(AttemptServiceError):
    """Maximum attempts reached."""
    def __init__(self):
        super().__init__("Maximum attempts reached", "MAX_ATTEMPTS_REACHED", 403)


class InvalidPasscodeError(AttemptServiceError):
    """Invalid passcode."""
    def __init__(self):
        super().__init__("Invalid passcode", "INVALID_PASSCODE", 401)


def _check_rate_limit(user_id: str, exam_id: str, max_requests: int = 30, window: int = 60) -> bool:
    """Check rate limit for answer saves."""
    redis = _get_redis()
    if not redis:
        return True
    
    try:
        key = f"attempt_save:{user_id}:{exam_id}"
        current = redis.get(key)
        
        if current is None:
            redis.setex(key, window, 1)
            return True
        
        if int(current) >= max_requests:
            return False
        
        redis.incr(key)
        return True
    except Exception as e:
        logger.error(f"Rate limit check failed: {e}")
        return True


def start_attempt(
    exam_id: str,
    student_id: str,
    passcode: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Start a new exam attempt.
    
    Args:
        exam_id: Exam ID
        student_id: Student ID
        passcode: Exam passcode (if required)
        ip_address: Student IP address
        user_agent: Browser user agent
    
    Returns:
        Attempt data with exam info
    """
    from app.models import Exam, User, ExamAttempt, Question
    
    exam = Exam.objects(id=exam_id).first()
    if not exam:
        raise AttemptServiceError("Exam not found", "EXAM_NOT_FOUND", 404)
    
    student = User.objects(id=student_id).first()
    if not student:
        raise AttemptServiceError("Student not found", "STUDENT_NOT_FOUND", 404)
    
    if exam.status not in ["published", "active"]:
        raise ExamNotAvailableError("Exam is not available")
    
    now = datetime.now(timezone.utc)
    if exam.schedule:
        if exam.schedule.start_at and now < exam.schedule.start_at:
            raise ExamNotAvailableError("Exam has not started yet")
        if exam.schedule.end_at:
            grace = exam.schedule.grace_minutes or 0
            grace_end = exam.schedule.end_at + timedelta(minutes=grace)
            if now > grace_end:
                raise ExamNotAvailableError("Exam has ended")
    
    if exam.access_mode == "passcode":
        if not passcode:
            raise InvalidPasscodeError()
        try:
            from app.utils.security import verify_password
            if not verify_password(passcode, exam.security.passcode_hash or ""):
                raise InvalidPasscodeError()
        except Exception:
            raise InvalidPasscodeError()
    
    existing_count = ExamAttempt.objects(exam=exam, student=student).count()
    if existing_count >= exam.allowed_attempts:
        raise MaxAttemptsReachedError()
    
    in_progress = ExamAttempt.objects(exam=exam, student=student, status="in_progress").first()
    if in_progress:
        return _format_attempt(in_progress, exam, student)
    
    attempt = ExamAttempt(
        exam=exam,
        student=student,
        status="in_progress",
        started_at=now,
        access_method="passcode" if passcode else ("magic_link" if exam.access_mode == "magic_link" else "direct"),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    attempt.save()
    
    logger.info(f"Attempt started: {attempt.id} for student {student_id}, exam {exam_id}")
    
    return _format_attempt(attempt, exam, student)


def _format_attempt(attempt, exam, student) -> Dict[str, Any]:
    """Format attempt for response."""
    now = datetime.now(timezone.utc)
    started = attempt.started_at or now
    duration_seconds = exam.duration_minutes * 60
    elapsed = (now - started).total_seconds()
    remaining = max(0, duration_seconds - elapsed)
    
    security = {}
    if exam.security:
        security = {
            "camera_required": exam.security.camera_required,
            "tab_switch_limit": exam.security.tab_switch_limit,
            "fullscreen_required": exam.security.fullscreen_required,
            "copy_paste_disabled": exam.security.copy_paste_disabled,
            "shuffle_questions": exam.security.shuffle_questions,
            "shuffle_options": exam.security.shuffle_options,
        }
    
    return {
        "id": str(attempt.id),
        "exam_id": str(exam.id),
        "exam_title": exam.title,
        "student_id": str(student.id),
        "status": attempt.status,
        "started_at": attempt.started_at.isoformat() if attempt.started_at else None,
        "duration_minutes": exam.duration_minutes,
        "remaining_seconds": int(remaining),
        "total_marks": exam.total_marks,
        "result_mode": exam.result_mode,
        "certificate_enabled": exam.certificate_enabled,
        "security": security,
        "tab_switch_count": attempt.tab_switch_count,
        "face_mismatch_count": attempt.face_mismatch_count,
    }


def get_attempt(attempt_id: str, user_id: str) -> Dict[str, Any]:
    """
    Get attempt by ID.
    
    Args:
        attempt_id: Attempt ID
        user_id: Requesting user ID
    
    Returns:
        Attempt dictionary
    """
    from app.models import ExamAttempt, User
    
    attempt = ExamAttempt.objects(id=attempt_id).first()
    if not attempt:
        raise AttemptNotFoundError()
    
    user = User.objects(id=user_id).first()
    if not user:
        raise AttemptServiceError("User not found", "USER_NOT_FOUND", 404)
    
    if str(attempt.student.id) != user_id and user.role not in ["super_admin", "admin_public", "admin_college", "teacher"]:
        raise AttemptServiceError("Access denied", "ACCESS_DENIED", 403)
    
    exam = attempt.exam
    student = attempt.student
    
    return _format_attempt(attempt, exam, student)


def save_answers(
    attempt_id: str,
    student_id: str,
    answers: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Save answers for an attempt.
    
    Args:
        attempt_id: Attempt ID
        student_id: Student ID
        answers: List of answer dicts with question_id, selected_option_id, flagged, time_spent
    
    Returns:
        Save confirmation
    """
    from app.models import ExamAttempt, Answer, User
    
    if not _check_rate_limit(student_id, attempt_id):
        raise AttemptServiceError("Too many requests. Please wait.", "RATE_LIMITED", 429)
    
    attempt = ExamAttempt.objects(id=attempt_id, student=student_id).first()
    if not attempt:
        raise AttemptNotFoundError()
    
    if attempt.status != "in_progress":
        raise AttemptAlreadySubmittedError()
    
    now = datetime.now(timezone.utc)
    exam = attempt.exam
    started = attempt.started_at or now
    duration_seconds = exam.duration_minutes * 60
    
    if (now - started).total_seconds() > duration_seconds:
        return submit_attempt(attempt_id, student_id)
    
    existing_answers = {a.question_id: a for a in (attempt.answers or [])}
    
    for ans in answers:
        question_id = ans.get("question_id")
        if not question_id:
            continue
        
        if question_id in existing_answers:
            existing = existing_answers[question_id]
            existing.selected_option_id = ans.get("selected_option_id")
            existing.flagged = ans.get("flagged", False)
            existing.time_spent_seconds = ans.get("time_spent_seconds", 0)
        else:
            new_answer = Answer(
                question_id=question_id,
                selected_option_id=ans.get("selected_option_id"),
                flagged=ans.get("flagged", False),
                time_spent_seconds=ans.get("time_spent_seconds", 0),
            )
            attempt.answers.append(new_answer)
    
    attempt.save()
    
    logger.info(f"Answers saved for attempt {attempt_id}")
    
    return {
        "attempt_id": str(attempt.id),
        "saved": True,
        "answer_count": len(attempt.answers),
    }


def submit_attempt(
    attempt_id: str,
    student_id: str,
) -> Dict[str, Any]:
    """
    Submit an exam attempt.
    
    Args:
        attempt_id: Attempt ID
        student_id: Student ID
    
    Returns:
        Submission confirmation
    """
    from app.models import ExamAttempt, User, Result
    
    attempt = ExamAttempt.objects(id=attempt_id, student=student_id).first()
    if not attempt:
        raise AttemptNotFoundError()
    
    if attempt.status != "in_progress":
        raise AttemptAlreadySubmittedError()
    
    now = datetime.now(timezone.utc)
    attempt.status = "submitted"
    attempt.submitted_at = now
    attempt.save()
    
    from app.services import result_service
    try:
        result = result_service.calculate_result(str(attempt.id))
    except Exception as e:
        logger.error(f"Failed to calculate result for attempt {attempt_id}: {e}")
        result = None
    
    logger.info(f"Attempt submitted: {attempt_id}")
    
    return {
        "attempt_id": str(attempt.id),
        "status": "submitted",
        "submitted_at": now.isoformat(),
        "result_available": result is not None,
    }


def log_violation(
    attempt_id: str,
    student_id: str,
    violation_type: str,
    screenshot_url: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Log a violation during exam.
    
    Args:
        attempt_id: Attempt ID
        student_id: Student ID
        violation_type: Type of violation
        screenshot_url: Optional screenshot URL
    
    Returns:
        Violation status
    """
    from app.models import ExamAttempt, Violation, User
    
    attempt = ExamAttempt.objects(id=attempt_id, student=student_id).first()
    if not attempt:
        raise AttemptNotFoundError()
    
    if attempt.status != "in_progress":
        raise AttemptAlreadySubmittedError()
    
    now = datetime.now(timezone.utc)
    
    violation = Violation(
        type=violation_type,
        occurred_at=now,
        screenshot_url=screenshot_url,
    )
    attempt.violations.append(violation)
    
    if violation_type == "tab_switch":
        attempt.tab_switch_count += 1
    elif violation_type == "face_mismatch":
        attempt.face_mismatch_count += 1
    
    attempt.save()
    
    exam = attempt.exam
    violations_exceeded = False
    
    if exam.security:
        if violation_type == "tab_switch" and attempt.tab_switch_count >= exam.security.tab_switch_limit:
            violations_exceeded = True
        elif violation_type == "face_mismatch" and attempt.face_mismatch_count >= 3:
            violations_exceeded = True
    
    logger.info(f"Violation logged for attempt {attempt_id}: {violation_type}")
    
    return {
        "attempt_id": str(attempt.id),
        "violation_type": violation_type,
        "count": attempt.tab_switch_count if violation_type == "tab_switch" else attempt.face_mismatch_count,
        "limit_exceeded": violations_exceeded,
        "force_submit": violations_exceeded,
    }


def force_submit_attempt(
    attempt_id: str,
    admin_id: str,
    reason: str = "Admin forced submission",
) -> Dict[str, Any]:
    """
    Force submit an attempt (admin action).
    
    Args:
        attempt_id: Attempt ID
        admin_id: Admin user ID
        reason: Reason for force submission
    
    Returns:
        Submission confirmation
    """
    from app.models import ExamAttempt, User
    
    attempt = ExamAttempt.objects(id=attempt_id).first()
    if not attempt:
        raise AttemptNotFoundError()
    
    admin = User.objects(id=admin_id).first()
    if not admin:
        raise AttemptServiceError("Admin not found", "USER_NOT_FOUND", 404)
    
    if admin.role not in ["super_admin", "admin_public", "admin_college", "teacher"]:
        raise AttemptServiceError("Not authorized", "UNAUTHORIZED", 403)
    
    if attempt.status != "in_progress":
        raise AttemptAlreadySubmittedError()
    
    now = datetime.now(timezone.utc)
    attempt.status = "force_submitted"
    attempt.submitted_at = now
    attempt.save()
    
    from app.services import result_service
    try:
        result_service.calculate_result(str(attempt.id))
    except Exception as e:
        logger.error(f"Failed to calculate result for attempt {attempt_id}: {e}")
    
    logger.info(f"Attempt force submitted: {attempt_id} by admin {admin_id}, reason: {reason}")
    
    return {
        "attempt_id": str(attempt.id),
        "status": "force_submitted",
        "submitted_at": now.isoformat(),
        "reason": reason,
    }


def get_attempt_questions(
    attempt_id: str,
    student_id: str,
) -> List[Dict[str, Any]]:
    """
    Get questions for an active attempt (with shuffling).
    
    Args:
        attempt_id: Attempt ID
        student_id: Student ID
    
    Returns:
        List of questions
    """
    import random
    from app.models import ExamAttempt, Question, User
    
    attempt = ExamAttempt.objects(id=attempt_id, student=student_id).first()
    if not attempt:
        raise AttemptNotFoundError()
    
    if attempt.status != "in_progress":
        raise AttemptAlreadySubmittedError()
    
    exam = attempt.exam
    
    now = datetime.now(timezone.utc)
    started = attempt.started_at or now
    elapsed = (now - started).total_seconds()
    duration_seconds = exam.duration_minutes * 60
    
    if elapsed > duration_seconds:
        submit_attempt(attempt_id, student_id)
        raise AttemptAlreadySubmittedError()
    
    if exam:
        questions_query = Question.objects(exam=exam)
    else:
        questions_query = Question.objects()
    
    questions = list(questions_query[:50])
    
    if exam.security:
        if exam.security.shuffle_questions:
            random.shuffle(questions)
    
    result = []
    for q in questions:
        options = [{"option_id": opt.option_id, "text": opt.text} for opt in q.options]
        
        if exam.security and exam.security.shuffle_options and options:
            shuffled_options = options.copy()
            random.shuffle(shuffled_options)
            options = shuffled_options
        
        answer_map = {a.question_id: a for a in attempt.answers}
        existing = answer_map.get(str(q.id), None)
        
        result.append({
            "id": str(q.id),
            "text": q.text,
            "question_type": q.question_type,
            "options": options,
            "marks": q.marks,
            "selected_option_id": existing.selected_option_id if existing else None,
            "flagged": existing.flagged if existing else False,
            "time_spent_seconds": existing.time_spent_seconds if existing else 0,
        })
    
    return result


def list_attempts(
    user_id: str,
    exam_id: Optional[str] = None,
    page: int = 1,
    per_page: int = 20,
    status: Optional[str] = None,
) -> Dict[str, Any]:
    """
    List attempts for a user or exam.
    
    Args:
        user_id: Requesting user ID
        exam_id: Filter by exam
        page: Page number
        per_page: Items per page
        status: Filter by status
    
    Returns:
        Paginated attempt list
    """
    from app.models import ExamAttempt, User, Exam
    
    user = User.objects(id=user_id).first()
    if not user:
        raise AttemptServiceError("User not found", "USER_NOT_FOUND", 404)
    
    query = {}
    
    if user.role in ["student_registered", "student_assigned"]:
        query["student"] = user
    elif exam_id:
        query["exam"] = exam_id
    elif user.role in ["super_admin", "admin_public", "admin_college", "teacher"]:
        pass
    else:
        query["student"] = user
    
    if exam_id:
        query["exam"] = exam_id
    if status:
        query["status"] = status
    
    skip = (page - 1) * per_page
    attempts = ExamAttempt.objects(**query).order_by("-created_at").skip(skip).limit(per_page)
    total = ExamAttempt.objects(**query).count()
    
    items = []
    for attempt in attempts:
        exam = attempt.exam
        student = attempt.student
        items.append({
            "id": str(attempt.id),
            "exam_id": str(exam.id) if exam else None,
            "exam_title": exam.title if exam else None,
            "student_id": str(student.id) if student else None,
            "student_name": student.full_name if student else None,
            "status": attempt.status,
            "started_at": attempt.started_at.isoformat() if attempt.started_at else None,
            "submitted_at": attempt.submitted_at.isoformat() if attempt.submitted_at else None,
            "tab_switch_count": attempt.tab_switch_count,
            "violation_count": len(attempt.violations),
        })
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page if total > 0 else 0,
    }
