"""
Exam service for ExamSaaS platform.
Pure Python - zero Flask imports, zero HTTP concepts.
"""
import logging
import random
import secrets
from datetime import datetime, timezone
from typing import Optional, Tuple, Dict, Any, List

from app.utils.security import sanitize_input

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
            logger.warning("Redis not available for exam service")
            return None
    return REDIS_CLIENT


EXAM_TTL = 24 * 3600
MAGIC_LINK_TTL = 7 * 24 * 3600


class ExamServiceError(Exception):
    """Base exception for exam service errors."""
    def __init__(self, message: str, code: str, status_code: int = 400):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class ExamNotFoundError(ExamServiceError):
    """Exam not found."""
    def __init__(self):
        super().__init__("Exam not found", "EXAM_NOT_FOUND", 404)


class ExamAccessDeniedError(ExamServiceError):
    """Access to exam denied."""
    def __init__(self, message: str = "Access denied"):
        super().__init__(message, "EXAM_ACCESS_DENIED", 403)


class ExamNotPublishedError(ExamServiceError):
    """Exam not published."""
    def __init__(self):
        super().__init__("Exam is not published", "EXAM_NOT_PUBLISHED", 403)


class ExamScheduleError(ExamServiceError):
    """Exam schedule error."""
    def __init__(self, message: str = "Exam is not available"):
        super().__init__(message, "EXAM_SCHEDULE_ERROR", 403)


class MaxAttemptsReachedError(ExamServiceError):
    """Maximum attempts reached."""
    def __init__(self):
        super().__init__("Maximum attempts reached", "MAX_ATTEMPTS_REACHED", 403)


class InvalidPasscodeError(ExamServiceError):
    """Invalid passcode."""
    def __init__(self):
        super().__init__("Invalid passcode", "INVALID_PASSCODE", 401)


class QuestionNotFoundError(ExamServiceError):
    """Question not found."""
    def __init__(self):
        super().__init__("Question not found", "QUESTION_NOT_FOUND", 404)


class AttemptNotFoundError(ExamServiceError):
    """Attempt not found."""
    def __init__(self):
        super().__init__("Attempt not found", "ATTEMPT_NOT_FOUND", 404)


class AttemptNotInProgressError(ExamServiceError):
    """Attempt not in progress."""
    def __init__(self):
        super().__init__("Attempt is not in progress", "ATTEMPT_NOT_IN_PROGRESS", 400)


def _store_magic_link(token: str, data: Dict[str, Any]) -> None:
    """Store magic link data in Redis."""
    redis = _get_redis()
    if redis:
        try:
            key = f"exam_magic:{token}"
            redis.setex(key, MAGIC_LINK_TTL, __import__('json').dumps(data))
        except Exception as e:
            logger.error(f"Failed to store magic link in Redis: {e}")


def _get_magic_link(token: str) -> Optional[Dict[str, Any]]:
    """Get magic link data from Redis."""
    redis = _get_redis()
    if redis:
        try:
            key = f"exam_magic:{token}"
            data = redis.get(key)
            if data == "used":
                return None
            if data:
                return __import__('json').loads(data)
        except Exception as e:
            logger.error(f"Failed to get magic link from Redis: {e}")
    return None


def _mark_magic_link_used(token: str) -> None:
    """Mark magic link as used."""
    redis = _get_redis()
    if redis:
        try:
            key = f"exam_magic:{token}"
            redis.setex(key, MAGIC_LINK_TTL, "used")
        except Exception as e:
            logger.error(f"Failed to mark magic link as used: {e}")


def _verify_passcode(exam, passcode: str) -> bool:
    """Verify exam passcode."""
    if not exam.security or not exam.security.passcode_hash:
        return True
    try:
        from app.utils.security import verify_password
        return verify_password(passcode, exam.security.passcode_hash)
    except Exception:
        return False


def _generate_magic_link_token() -> str:
    """Generate a secure magic link token."""
    return secrets.token_urlsafe(32)


def create_exam(
    creator_id: str,
    institute_id: Optional[str],
    title: str,
    description: Optional[str] = None,
    subject: Optional[str] = None,
    topic: Optional[str] = None,
    duration_minutes: int = 60,
    total_marks: int = 0,
    passing_percentage: float = 40.0,
    exam_type: str = "institute",
    result_mode: str = "instant",
    access_mode: str = "open",
    price: int = 0,
    allowed_attempts: int = 1,
    certificate_enabled: bool = False,
    start_at: Optional[datetime] = None,
    end_at: Optional[datetime] = None,
    grace_minutes: int = 5,
    camera_required: bool = False,
    tab_switch_limit: int = 3,
    fullscreen_required: bool = False,
    copy_paste_disabled: bool = False,
    shuffle_questions: bool = False,
    shuffle_options: bool = False,
    passcode: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a new exam.
    
    Args:
        creator_id: ID of user creating the exam
        institute_id: ID of institute (optional)
        title: Exam title
        description: Exam description
        subject: Subject name
        topic: Topic name
        duration_minutes: Exam duration
        total_marks: Total marks for exam
        passing_percentage: Passing percentage
        exam_type: institute or public
        result_mode: instant or delayed
        access_mode: open, passcode, or magic_link
        price: Exam price in rupees
        allowed_attempts: Max attempts per student
        certificate_enabled: Enable certificate on pass
        start_at: Schedule start time
        end_at: Schedule end time
        grace_minutes: Grace period after end time
        camera_required: Require camera
        tab_switch_limit: Max tab switches allowed
        fullscreen_required: Require fullscreen
        copy_paste_disabled: Disable copy/paste
        shuffle_questions: Shuffle question order
        shuffle_options: Shuffle option order
        passcode: Passcode for access
    
    Returns:
        Created exam dictionary
    
    Raises:
        ExamServiceError: If creation fails
    """
    from app.models import Exam, Schedule, Security, User
    
    title = sanitize_input(title)[:255]
    description = sanitize_input(description)[:2000] if description else None
    subject = sanitize_input(subject)[:100] if subject else None
    topic = sanitize_input(topic)[:100] if topic else None
    
    creator = User.objects(id=creator_id).first()
    if not creator:
        raise ExamServiceError("Creator not found", "USER_NOT_FOUND", 404)
    
    from app.models import Institute
    institute = None
    if institute_id:
        institute = Institute.objects(id=institute_id).first()
    
    passcode_hash = None
    if passcode and access_mode == "passcode":
        from app.utils.security import hash_password
        passcode_hash = hash_password(passcode, cost=12)
    
    schedule = Schedule(
        start_at=start_at,
        end_at=end_at,
        grace_minutes=grace_minutes,
    )
    
    security = Security(
        camera_required=camera_required,
        tab_switch_limit=tab_switch_limit,
        fullscreen_required=fullscreen_required,
        copy_paste_disabled=copy_paste_disabled,
        shuffle_questions=shuffle_questions,
        shuffle_options=shuffle_options,
        passcode_hash=passcode_hash,
    )
    
    exam = Exam(
        title=title,
        description=description,
        subject=subject,
        topic=topic,
        institute=institute,
        created_by=creator,
        exam_type=exam_type,
        status="draft",
        total_marks=total_marks,
        passing_percentage=passing_percentage,
        duration_minutes=duration_minutes,
        schedule=schedule,
        security=security,
        result_mode=result_mode,
        access_mode=access_mode,
        price=price,
        allowed_attempts=allowed_attempts,
        certificate_enabled=certificate_enabled,
    )
    exam.save()
    
    logger.info(f"Exam created: {exam.id} by user {creator_id}")
    
    return get_exam(exam.id, creator_id)


def get_exam(exam_id: str, user_id: str) -> Dict[str, Any]:
    """
    Get exam by ID.
    
    Args:
        exam_id: Exam ID
        user_id: Requesting user ID
    
    Returns:
        Exam dictionary
    """
    from app.models import Exam, User
    
    exam = Exam.objects(id=exam_id).first()
    if not exam:
        raise ExamNotFoundError()
    
    user = User.objects(id=user_id).first()
    if not user:
        raise ExamServiceError("User not found", "USER_NOT_FOUND", 404)
    
    return _format_exam(exam, user)


def _format_exam(exam, user) -> Dict[str, Any]:
    """Format exam for response."""
    from app.models import ExamAttempt, Question
    
    can_edit = _can_edit_exam(exam, user)
    can_view_results = _can_view_results(exam, user)
    can_take = _can_take_exam(exam, user)
    
    # Get counts
    question_count = Question.objects(exam=exam).count() if exam else 0
    attempts_count = ExamAttempt.objects(exam=exam).count() if exam else 0
    
    result = {
        "id": str(exam.id),
        "title": exam.title,
        "description": exam.description,
        "subject": exam.subject,
        "topic": exam.topic,
        "institute_id": str(exam.institute.id) if exam.institute else None,
        "created_by_id": str(exam.created_by.id) if exam.created_by else None,
        "exam_type": exam.exam_type,
        "status": exam.status,
        "total_marks": exam.total_marks,
        "passing_percentage": exam.passing_percentage,
        "duration_minutes": exam.duration_minutes,
        "result_mode": exam.result_mode,
        "access_mode": exam.access_mode,
        "price": exam.price,
        "allowed_attempts": exam.allowed_attempts,
        "certificate_enabled": exam.certificate_enabled,
        "question_count": question_count,
        "attempts_count": attempts_count,
        "schedule": {
            "start_at": exam.schedule.start_at.isoformat() if exam.schedule and exam.schedule.start_at else None,
            "end_at": exam.schedule.end_at.isoformat() if exam.schedule and exam.schedule.end_at else None,
            "grace_minutes": exam.schedule.grace_minutes if exam.schedule else 5,
        },
        "security": {
            "camera_required": exam.security.camera_required if exam.security else False,
            "tab_switch_limit": exam.security.tab_switch_limit if exam.security else 3,
            "fullscreen_required": exam.security.fullscreen_required if exam.security else False,
            "copy_paste_disabled": exam.security.copy_paste_disabled if exam.security else False,
            "shuffle_questions": exam.security.shuffle_questions if exam.security else False,
            "shuffle_options": exam.security.shuffle_options if exam.security else False,
        },
        "permissions": {
            "can_edit": can_edit,
            "can_view_results": can_view_results,
            "can_take": can_take,
        },
        "created_at": exam.created_at.isoformat() if exam.created_at else None,
        "updated_at": exam.updated_at.isoformat() if exam.updated_at else None,
    }
    
    return result


def _can_edit_exam(exam, user) -> bool:
    """Check if user can edit exam."""
    if user.role in ["super_admin", "admin_public"]:
        return True
    if exam.created_by and str(exam.created_by.id) == str(user.id):
        return True
    if user.role == "teacher" and exam.institute and str(exam.institute.id) == str(user.institute.id if user.institute else ""):
        return True
    return False


def _can_view_results(exam, user) -> bool:
    """Check if user can view exam results."""
    if user.role in ["super_admin", "admin_public"]:
        return True
    if exam.created_by and str(exam.created_by.id) == str(user.id):
        return True
    if user.role == "teacher" and exam.institute and str(exam.institute.id) == str(user.institute.id if user.institute else ""):
        return True
    return False


def _can_take_exam(exam, user) -> bool:
    """Check if user can take exam."""
    if exam.status not in ["published", "active"]:
        return False
    
    from datetime import datetime, timedelta
    now = datetime.utcnow()
    if exam.schedule:
        start_at = exam.schedule.start_at
        end_at = exam.schedule.end_at
        if start_at:
            if start_at.tzinfo is not None:
                start_at = start_at.replace(tzinfo=None)
            if now < start_at:
                return False
        if end_at:
            if end_at.tzinfo is not None:
                end_at = end_at.replace(tzinfo=None)
            grace = exam.schedule.grace_minutes or 0
            grace_end = end_at + timedelta(minutes=grace)
            if now > grace_end:
                return False
    
    from app.models import ExamAttempt
    attempts = ExamAttempt.objects(exam=exam, student=user).count()
    return attempts < exam.allowed_attempts


def update_exam(
    exam_id: str,
    user_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    subject: Optional[str] = None,
    topic: Optional[str] = None,
    duration_minutes: Optional[int] = None,
    total_marks: Optional[int] = None,
    passing_percentage: Optional[float] = None,
    result_mode: Optional[str] = None,
    access_mode: Optional[str] = None,
    price: Optional[int] = None,
    allowed_attempts: Optional[int] = None,
    certificate_enabled: Optional[bool] = None,
    start_at: Optional[datetime] = None,
    end_at: Optional[datetime] = None,
    grace_minutes: Optional[int] = None,
    camera_required: Optional[bool] = None,
    tab_switch_limit: Optional[int] = None,
    fullscreen_required: Optional[bool] = None,
    copy_paste_disabled: Optional[bool] = None,
    shuffle_questions: Optional[bool] = None,
    shuffle_options: Optional[bool] = None,
    passcode: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Update an exam.
    
    Args:
        exam_id: Exam ID
        user_id: Requesting user ID
        ... other optional fields
    
    Returns:
        Updated exam dictionary
    """
    from app.models import Exam, User
    
    exam = Exam.objects(id=exam_id).first()
    if not exam:
        raise ExamNotFoundError()
    
    user = User.objects(id=user_id).first()
    if not user:
        raise ExamServiceError("User not found", "USER_NOT_FOUND", 404)
    
    if not _can_edit_exam(exam, user):
        raise ExamAccessDeniedError("You cannot edit this exam")
    
    if exam.status not in ["draft", "pending_approval"]:
        raise ExamServiceError("Cannot edit exam after publishing", "EXAM_NOT_EDITABLE", 400)
    
    if title is not None:
        exam.title = sanitize_input(title)[:255]
    if description is not None:
        exam.description = sanitize_input(description)[:2000]
    if subject is not None:
        exam.subject = sanitize_input(subject)[:100] if subject else None
    if topic is not None:
        exam.topic = sanitize_input(topic)[:100] if topic else None
    if duration_minutes is not None:
        exam.duration_minutes = duration_minutes
    if total_marks is not None:
        exam.total_marks = total_marks
    if passing_percentage is not None:
        exam.passing_percentage = passing_percentage
    if result_mode is not None:
        exam.result_mode = result_mode
    if access_mode is not None:
        exam.access_mode = access_mode
        if access_mode == "passcode" and passcode:
            from app.utils.security import hash_password
            exam.security.passcode_hash = hash_password(passcode, cost=12)
        elif access_mode != "passcode":
            exam.security.passcode_hash = None
    if price is not None:
        exam.price = price
    if allowed_attempts is not None:
        exam.allowed_attempts = allowed_attempts
    if certificate_enabled is not None:
        exam.certificate_enabled = certificate_enabled
    
    if hasattr(exam, 'schedule'):
        if start_at is not None:
            exam.schedule.start_at = start_at
        if end_at is not None:
            exam.schedule.end_at = end_at
        if grace_minutes is not None:
            exam.schedule.grace_minutes = grace_minutes
    
    if hasattr(exam, 'security'):
        if camera_required is not None:
            exam.security.camera_required = camera_required
        if tab_switch_limit is not None:
            exam.security.tab_switch_limit = tab_switch_limit
        if fullscreen_required is not None:
            exam.security.fullscreen_required = fullscreen_required
        if copy_paste_disabled is not None:
            exam.security.copy_paste_disabled = copy_paste_disabled
        if shuffle_questions is not None:
            exam.security.shuffle_questions = shuffle_questions
        if shuffle_options is not None:
            exam.security.shuffle_options = shuffle_options
    
    exam.save()
    
    logger.info(f"Exam updated: {exam.id} by user {user_id}")
    
    return _format_exam(exam, user)


def publish_exam(exam_id: str, user_id: str) -> Dict[str, Any]:
    """
    Publish an exam.
    
    Args:
        exam_id: Exam ID
        user_id: Requesting user ID
    
    Returns:
        Updated exam dictionary
    """
    from app.models import Exam, User, Question
    
    exam = Exam.objects(id=exam_id).first()
    if not exam:
        raise ExamNotFoundError()
    
    user = User.objects(id=user_id).first()
    if not user:
        raise ExamServiceError("User not found", "USER_NOT_FOUND", 404)
    
    if not _can_edit_exam(exam, user):
        raise ExamAccessDeniedError("You cannot publish this exam")
    
    if exam.status not in ["draft", "pending_approval"]:
        raise ExamServiceError("Exam cannot be published", "EXAM_NOT_PUBLISHABLE", 400)
    
    if exam.total_marks <= 0:
        raise ExamServiceError("Total marks must be greater than 0", "INVALID_MARKS", 400)
    
    question_count = Question.objects(exam=exam).count()
    if question_count == 0:
        raise ExamServiceError("Exam must have at least one question", "NO_QUESTIONS", 400)
    
    exam.status = "published"
    exam.save()
    
    logger.info(f"Exam published: {exam.id} by user {user_id}")
    
    return _format_exam(exam, user)


def activate_exam(exam_id: str, user_id: str) -> Dict[str, Any]:
    """
    Activate an exam (set to active status).
    
    Args:
        exam_id: Exam ID
        user_id: Requesting user ID
    
    Returns:
        Updated exam dictionary
    """
    from app.models import Exam, User
    
    exam = Exam.objects(id=exam_id).first()
    if not exam:
        raise ExamNotFoundError()
    
    user = User.objects(id=user_id).first()
    if not user:
        raise ExamServiceError("User not found", "USER_NOT_FOUND", 404)
    
    if not _can_edit_exam(exam, user):
        raise ExamAccessDeniedError("You cannot activate this exam")
    
    if exam.status != "published":
        raise ExamServiceError("Exam must be published first", "EXAM_NOT_PUBLISHED", 400)
    
    exam.status = "active"
    exam.save()
    
    logger.info(f"Exam activated: {exam.id} by user {user_id}")
    
    return _format_exam(exam, user)


def close_exam(exam_id: str, user_id: str) -> Dict[str, Any]:
    """
    Close an exam.
    
    Args:
        exam_id: Exam ID
        user_id: Requesting user ID
    
    Returns:
        Updated exam dictionary
    """
    from app.models import Exam, User
    
    exam = Exam.objects(id=exam_id).first()
    if not exam:
        raise ExamNotFoundError()
    
    user = User.objects(id=user_id).first()
    if not user:
        raise ExamServiceError("User not found", "USER_NOT_FOUND", 404)
    
    if not _can_edit_exam(exam, user):
        raise ExamAccessDeniedError("You cannot close this exam")
    
    exam.status = "closed"
    exam.save()
    
    logger.info(f"Exam closed: {exam.id} by user {user_id}")
    
    return _format_exam(exam, user)


def delete_exam(exam_id: str, user_id: str) -> bool:
    """
    Delete an exam.
    
    Args:
        exam_id: Exam ID
        user_id: Requesting user ID
    
    Returns:
        True if deleted
    """
    from app.models import Exam, User, ExamAttempt
    
    exam = Exam.objects(id=exam_id).first()
    if not exam:
        raise ExamNotFoundError()
    
    user = User.objects(id=user_id).first()
    if not user:
        raise ExamServiceError("User not found", "USER_NOT_FOUND", 404)
    
    if not _can_edit_exam(exam, user):
        raise ExamAccessDeniedError("You cannot delete this exam")
    
    attempt_count = ExamAttempt.objects(exam=exam).count()
    if attempt_count > 0:
        raise ExamServiceError("Cannot delete exam with attempts", "EXAM_HAS_ATTEMPTS", 400)
    
    exam.delete()
    
    logger.info(f"Exam deleted: {exam_id} by user {user_id}")
    
    return True


def list_exams(
    user_id: str,
    page: int = 1,
    per_page: int = 20,
    status: Optional[str] = None,
    institute_id: Optional[str] = None,
    search: Optional[str] = None,
    exam_type: Optional[str] = None,
) -> Dict[str, Any]:
    """
    List exams with pagination.
    
    Args:
        user_id: Requesting user ID
        page: Page number
        per_page: Items per page
        status: Filter by status
        institute_id: Filter by institute
        search: Search in title
        exam_type: Filter by type
    
    Returns:
        Paginated exam list
    """
    from app.models import Exam, User
    from mongoengine import Q
    
    user = User.objects(id=user_id).first()
    if not user:
        raise ExamServiceError("User not found", "USER_NOT_FOUND", 404)
    
    query = {}
    
    if user.role == "super_admin":
        pass  # Super admin sees all exams
    elif user.role in ["admin_public", "admin_college"]:
        if user.institute:
            query["institute"] = user.institute
    elif user.role in ["student_registered", "student_assigned"]:
        query["status__in"] = ["published", "active"]
    elif user.role == "teacher":
        pass  # Handle teacher separately below
    else:
        query["created_by"] = user
    
    if status:
        query["status"] = status
    
    if institute_id:
        query["institute"] = institute_id
    
    if search:
        query["title__icontains"] = search
    
    if exam_type:
        query["exam_type"] = exam_type
    
    skip = (page - 1) * per_page
    
    # Handle teacher role separately due to complex query
    if user.role == "teacher":
        from mongoengine import Q
        
        # Build base query for teacher
        teacher_conditions = [Q(created_by=user)]
        if user.institute:
            teacher_conditions.append(Q(institute=user.institute))
        
        if len(teacher_conditions) > 1:
            query_set = teacher_conditions[0]
            for cond in teacher_conditions[1:]:
                query_set = query_set | cond
        else:
            query_set = teacher_conditions[0]
        
        # Apply additional filters
        if status:
            query_set = query_set & Q(status=status)
        if search:
            query_set = query_set & Q(title__icontains=search)
        if exam_type:
            query_set = query_set & Q(exam_type=exam_type)
        if institute_id:
            query_set = query_set & Q(institute=institute_id)
        
        exams = Exam.objects(query_set).order_by("-created_at").skip(skip).limit(per_page)
        total = Exam.objects(query_set).count()
    else:
        exams = Exam.objects(**query).order_by("-created_at").skip(skip).limit(per_page)
        total = Exam.objects(**query).count()
    
    return {
        "items": [_format_exam(exam, user) for exam in exams],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page,
    }


def generate_magic_link(
    exam_id: str,
    creator_id: str,
    student_ids: Optional[List[str]] = None,
    valid_hours: int = 24,
) -> List[Dict[str, str]]:
    """
    Generate magic links for exam access.
    
    Args:
        exam_id: Exam ID
        creator_id: User generating the link
        student_ids: Specific student IDs (optional)
        valid_hours: Link validity in hours
    
    Returns:
        List of magic link entries
    """
    from app.models import Exam, User
    
    exam = Exam.objects(id=exam_id).first()
    if not exam:
        raise ExamNotFoundError()
    
    creator = User.objects(id=creator_id).first()
    if not creator:
        raise ExamServiceError("User not found", "USER_NOT_FOUND", 404)
    
    if not _can_edit_exam(exam, creator):
        raise ExamAccessDeniedError("You cannot generate links for this exam")
    
    if exam.status not in ["published", "active"]:
        raise ExamNotPublishedError()
    
    links = []
    
    if student_ids:
        students = User.objects(id__in=student_ids)
    else:
        if exam.institute:
            students = User.objects(institute=exam.institute, role__in=["student_registered", "student_assigned"])
        else:
            students = User.objects(role__in=["student_registered", "student_assigned"])
    
    for student in students:
        token = _generate_magic_link_token()
        
        data = {
            "exam_id": str(exam.id),
            "student_id": str(student.id),
            "creator_id": creator_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        
        _store_magic_link(token, data)
        
        links.append({
            "student_id": str(student.id),
            "student_name": student.full_name,
            "student_email": student.email,
            "token": token,
            "url": f"/exam/access/{token}",
        })
    
    logger.info(f"Generated {len(links)} magic links for exam {exam_id}")
    
    return links


def verify_magic_link(token: str) -> Dict[str, Any]:
    """
    Verify magic link and return access data.
    
    Args:
        token: Magic link token
    
    Returns:
        Access data with exam info
    """
    data = _get_magic_link(token)
    
    if not data:
        raise ExamServiceError("Invalid or expired magic link", "INVALID_MAGIC_LINK", 401)
    
    exam_id = data.get("exam_id")
    student_id = data.get("student_id")
    
    from app.models import Exam, User, ExamAttempt
    
    exam = Exam.objects(id=exam_id).first()
    if not exam:
        raise ExamNotFoundError()
    
    student = User.objects(id=student_id).first()
    if not student:
        raise ExamServiceError("Student not found", "STUDENT_NOT_FOUND", 404)
    
    if exam.status not in ["published", "active"]:
        raise ExamNotPublishedError()
    
    from datetime import datetime, timedelta
    now = datetime.utcnow()
    if exam.schedule:
        start_at = exam.schedule.start_at
        if start_at:
            if start_at.tzinfo is not None:
                start_at = start_at.replace(tzinfo=None)
            if now < start_at:
                raise ExamScheduleError("Exam has not started yet")
        if exam.schedule.end_at:
            end_at = exam.schedule.end_at
            if end_at.tzinfo is not None:
                end_at = end_at.replace(tzinfo=None)
            grace = exam.schedule.grace_minutes or 0
            grace_end = end_at + timedelta(minutes=grace)
            if now > grace_end:
                raise ExamScheduleError("Exam has ended")
    
    existing_attempts = ExamAttempt.objects(exam=exam, student=student).count()
    if existing_attempts >= exam.allowed_attempts:
        raise MaxAttemptsReachedError()
    
    _mark_magic_link_used(token)
    
    logger.info(f"Magic link verified for student {student_id}, exam {exam_id}")
    
    return {
        "exam_id": exam_id,
        "student_id": student_id,
        "exam_title": exam.title,
        "duration_minutes": exam.duration_minutes,
        "total_marks": exam.total_marks,
        "access_granted": True,
    }


def assign_questions_to_exam(
    exam_id: str,
    user_id: str,
    question_ids: List[str],
    marks_per_question: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Assign questions to an exam.
    
    Args:
        exam_id: Exam ID
        user_id: Requesting user ID
        question_ids: List of question IDs
        marks_per_question: Override marks per question
    
    Returns:
        Exam info with question count
    """
    from app.models import Exam, User, Question
    
    exam = Exam.objects(id=exam_id).first()
    if not exam:
        raise ExamNotFoundError()
    
    user = User.objects(id=user_id).first()
    if not user:
        raise ExamServiceError("User not found", "USER_NOT_FOUND", 404)
    
    if not _can_edit_exam(exam, user):
        raise ExamAccessDeniedError("You cannot modify this exam")
    
    if exam.status not in ["draft", "pending_approval"]:
        raise ExamServiceError("Cannot modify exam after publishing", "EXAM_NOT_EDITABLE", 400)
    
    if exam.institute:
        questions_query = Question.objects(id__in=question_ids, institute=exam.institute)
    else:
        questions_query = Question.objects(id__in=question_ids)
    
    questions_list = list(questions_query)
    
    if marks_per_question:
        total = len(questions_list) * marks_per_question
    else:
        total = sum(q.marks for q in questions_list)
    
    exam.total_marks = total
    exam.save()
    
    logger.info(f"Assigned {len(questions_list)} questions to exam {exam_id}")
    
    return {
        "exam_id": str(exam.id),
        "question_count": len(questions_list),
        "total_marks": total,
    }


def get_exam_questions(
    exam_id: str,
    user_id: str,
    attempt_id: Optional[str] = None,
    access_token: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Get questions for an exam (with shuffling if enabled).
    
    Args:
        exam_id: Exam ID
        user_id: Requesting user ID
        attempt_id: Attempt ID for answer restoration
        access_token: Magic link access token (optional)
    
    Returns:
        List of questions
    """
    from app.models import Exam, User, Question, ExamAttempt
    
    exam = Exam.objects(id=exam_id).first()
    if not exam:
        raise ExamNotFoundError()
    
    if exam.status not in ["published", "active"]:
        raise ExamNotPublishedError()
    
    from datetime import datetime, timedelta
    now = datetime.utcnow()
    if exam.schedule:
        start_at = exam.schedule.start_at
        if start_at:
            if start_at.tzinfo is not None:
                start_at = start_at.replace(tzinfo=None)
            if now < start_at:
                raise ExamScheduleError("Exam has not started yet")
        if exam.schedule.end_at:
            end_at = exam.schedule.end_at
            if end_at.tzinfo is not None:
                end_at = end_at.replace(tzinfo=None)
            grace = exam.schedule.grace_minutes or 0
            grace_end = end_at + timedelta(minutes=grace)
            if now > grace_end:
                raise ExamScheduleError("Exam has ended")
    
    user = User.objects(id=user_id).first()
    if not user:
        raise ExamServiceError("User not found", "USER_NOT_FOUND", 404)
    
    existing_attempts = ExamAttempt.objects(exam=exam, student=user).count()
    if existing_attempts >= exam.allowed_attempts:
        raise MaxAttemptsReachedError()
    
    if exam:
        questions_query = Question.objects(exam=exam)
    else:
        questions_query = Question.objects()
    
    questions = list(questions_query[:50])
    
    if exam.security and exam.security.shuffle_questions:
        random.shuffle(questions)
    
    result = []
    for q in questions:
        options = [{"option_id": opt.option_id, "text": opt.text} for opt in q.options]
        
        if exam.security and exam.security.shuffle_options and options:
            shuffled_options = options.copy()
            random.shuffle(shuffled_options)
            options = shuffled_options
        
        result.append({
            "id": str(q.id),
            "text": q.text,
            "question_type": q.question_type,
            "options": options,
            "marks": q.marks,
            "subject": q.subject,
            "topic": q.topic,
            "difficulty": q.difficulty,
        })
    
    return result

def get_exam_results(
    exam_id: str,
    user_id: str,
    user_role: Optional[str] = None,
    filters: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Get results and performance analytics for an exam.

    Args:
        exam_id: Exam ID
        user_id: Requesting user ID
        user_role: Role of the requesting user
        filters: Optional query filters (institute_id, page, etc.)

    Returns:
        Analytics dict with success_rate, total_attempts, average_score,
        percentile_distribution, and top_colleges.

    Raises:
        ExamNotFoundError: If exam does not exist
        ExamAccessDeniedError: If user cannot view results
    """
    from app.models import Exam, User, ExamAttempt

    exam = Exam.objects(id=exam_id).first()
    if not exam:
        raise ExamNotFoundError()

    user = User.objects(id=user_id).first()
    if not user:
        raise ExamServiceError("User not found", "USER_NOT_FOUND", 404)

    if not _can_view_results(exam, user):
        raise ExamAccessDeniedError("You cannot view results for this exam")

    filters = filters or {}

    # Base queryset — optionally narrow by institute for super_admin callers
    institute_id = filters.get("institute_id")
    if institute_id:
        from app.models import Institute
        institute = Institute.objects(id=institute_id).first()
        attempts_qs = ExamAttempt.objects(exam=exam, student__institute=institute)
    else:
        attempts_qs = ExamAttempt.objects(exam=exam)

    # Only count completed attempts
    completed_qs = attempts_qs.filter(status="completed")
    total_attempts = completed_qs.count()

    if total_attempts == 0:
        return {
            "total_attempts": 0,
            "success_rate": 0.0,
            "average_score": 0.0,
            "percentile_distribution": [],
            "top_colleges": [],
        }

    passing_mark = exam.passing_percentage or 40.0
    passed_count = 0
    score_sum = 0.0
    scores = []  # list of percentage scores (0-100)

    for attempt in completed_qs:
        percentage = (attempt.score / exam.total_marks * 100) if exam.total_marks else 0
        scores.append(percentage)
        score_sum += percentage
        if percentage >= passing_mark:
            passed_count += 1

    average_score = score_sum / total_attempts if total_attempts else 0.0
    success_rate = (passed_count / total_attempts * 100) if total_attempts else 0.0

    # Percentile distribution — bucket scores into bands
    scores_sorted = sorted(scores)
    percentile_distribution = []
    for p in [10, 25, 50, 75, 90, 95]:
        idx = int(len(scores_sorted) * p / 100)
        idx = min(idx, len(scores_sorted) - 1)
        percentile_distribution.append({
            "percentile": p,
            "score": round(scores_sorted[idx], 1),
            "percentage": round(p, 1),  # position on chart axis
        })

    # Top colleges — aggregate by institute
    top_colleges = []
    try:
        from app.models import Institute
        # Only meaningful when exam spans multiple institutes (super_admin view)
        if user.role in ["super_admin", "admin_public"]:
            college_stats: Dict[str, Dict[str, Any]] = {}

            for attempt in completed_qs:
                student = attempt.student
                if not student or not student.institute:
                    continue
                cid = str(student.institute.id)
                if cid not in college_stats:
                    college_stats[cid] = {
                        "institute": student.institute,
                        "total": 0,
                        "passed": 0,
                    }
                college_stats[cid]["total"] += 1
                pct = (attempt.score / exam.total_marks * 100) if exam.total_marks else 0
                if pct >= passing_mark:
                    college_stats[cid]["passed"] += 1

            for cid, stats in college_stats.items():
                inst = stats["institute"]
                total = stats["total"]
                passed = stats["passed"]
                sr = (passed / total * 100) if total else 0.0
                top_colleges.append({
                    "id": cid,
                    "name": inst.name,
                    "city": getattr(inst, "city", ""),
                    "state": getattr(inst, "state", ""),
                    "total_attempts": total,
                    "passed_count": passed,
                    "success_rate": round(sr, 1),
                })

            top_colleges.sort(key=lambda c: c["success_rate"], reverse=True)
            top_colleges = top_colleges[:10]
    except Exception as e:
        logger.warning(f"Could not compute top_colleges for exam {exam_id}: {e}")

    return {
        "total_attempts": total_attempts,
        "success_rate": round(success_rate, 1),
        "average_score": round(average_score, 1),
        "percentile_distribution": percentile_distribution,
        "top_colleges": top_colleges,
    }