"""
Question service for ExamSaaS platform.
Pure Python - zero Flask imports, zero HTTP concepts.
"""
import logging
import secrets
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from app.utils.security import sanitize_input

logger = logging.getLogger(__name__)


class QuestionServiceError(Exception):
    """Base exception for question service errors."""
    def __init__(self, message: str, code: str, status_code: int = 400):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class QuestionNotFoundError(QuestionServiceError):
    """Question not found."""
    def __init__(self):
        super().__init__("Question not found", "QUESTION_NOT_FOUND", 404)


class QuestionAccessDeniedError(QuestionServiceError):
    """Access to question denied."""
    def __init__(self, message: str = "Access denied"):
        super().__init__(message, "QUESTION_ACCESS_DENIED", 403)


def _generate_option_id() -> str:
    """Generate unique option ID."""
    return secrets.token_hex(8)


def create_question(
    creator_id: str,
    institute_id: Optional[str],
    text: str,
    question_type: str,
    options: List[Dict[str, str]],
    correct_option_id: str,
    explanation: Optional[str] = None,
    subject: Optional[str] = None,
    topic: Optional[str] = None,
    difficulty: str = "medium",
    marks: int = 1,
    source: str = "manual",
) -> Dict[str, Any]:
    """
    Create a new question.
    
    Args:
        creator_id: ID of user creating the question
        institute_id: ID of institute (optional)
        text: Question text
        question_type: mcq, true_false, etc.
        options: List of option dicts with text
        correct_option_id: ID of correct option
        explanation: Explanation for answer
        subject: Subject name
        topic: Topic name
        difficulty: easy, medium, hard
        marks: Marks for question
        source: manual, pdf, ai_generated
    
    Returns:
        Created question dictionary
    """
    from app.models import Question, QuestionOption, User, Institute
    
    text = sanitize_input(text)[:5000]
    explanation = sanitize_input(explanation)[:2000] if explanation else None
    subject = sanitize_input(subject)[:100] if subject else None
    topic = sanitize_input(topic)[:100] if topic else None
    
    creator = User.objects(id=creator_id).first()
    if not creator:
        raise QuestionServiceError("Creator not found", "USER_NOT_FOUND", 404)
    
    institute = None
    if institute_id:
        institute = Institute.objects(id=institute_id).first()
    
    question_options = []
    for idx, opt in enumerate(options):
        option_text = sanitize_input(opt.get("text", ""))[:1000]
        if not option_text:
            continue
        
        option_id = opt.get("option_id") or _generate_option_id()
        
        question_options.append(QuestionOption(
            option_id=option_id,
            text=option_text,
        ))
    
    if len(question_options) < 2:
        raise QuestionServiceError("At least 2 options required", "INVALID_OPTIONS", 400)
    
    valid_option_ids = [opt.option_id for opt in question_options]
    if correct_option_id not in valid_option_ids:
        raise QuestionServiceError("Invalid correct option ID", "INVALID_CORRECT_OPTION", 400)
    
    question = Question(
        text=text,
        question_type=question_type,
        options=question_options,
        correct_option_id=correct_option_id,
        explanation=explanation,
        subject=subject,
        topic=topic,
        difficulty=difficulty,
        marks=marks,
        source=source,
        institute=institute,
        created_by=creator,
        is_reviewed=False,
        is_approved=False,
    )
    question.save()
    
    logger.info(f"Question created: {question.id} by user {creator_id}")
    
    return get_question(question.id, creator_id)


def get_question(question_id: str, user_id: str) -> Dict[str, Any]:
    """
    Get question by ID.
    
    Args:
        question_id: Question ID
        user_id: Requesting user ID
    
    Returns:
        Question dictionary
    """
    from app.models import Question, User
    
    question = Question.objects(id=question_id).first()
    if not question:
        raise QuestionNotFoundError()
    
    return _format_question(question)


def _format_question(question) -> Dict[str, Any]:
    """Format question for response."""
    return {
        "id": str(question.id),
        "text": question.text,
        "question_type": question.question_type,
        "options": [
            {"option_id": opt.option_id, "text": opt.text}
            for opt in question.options
        ],
        "correct_option_id": question.correct_option_id,
        "explanation": question.explanation,
        "subject": question.subject,
        "topic": question.topic,
        "difficulty": question.difficulty,
        "marks": question.marks,
        "source": question.source,
        "is_reviewed": question.is_reviewed,
        "is_approved": question.is_approved,
        "institute_id": str(question.institute.id) if question.institute else None,
        "created_by_id": str(question.created_by.id) if question.created_by else None,
        "created_at": question.created_at.isoformat() if question.created_at else None,
        "updated_at": question.updated_at.isoformat() if question.updated_at else None,
    }


def update_question(
    question_id: str,
    user_id: str,
    text: Optional[str] = None,
    question_type: Optional[str] = None,
    options: Optional[List[Dict[str, str]]] = None,
    correct_option_id: Optional[str] = None,
    explanation: Optional[str] = None,
    subject: Optional[str] = None,
    topic: Optional[str] = None,
    difficulty: Optional[str] = None,
    marks: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Update a question.
    
    Args:
        question_id: Question ID
        user_id: Requesting user ID
        ... other optional fields
    
    Returns:
        Updated question dictionary
    """
    from app.models import Question, QuestionOption, User
    
    question = Question.objects(id=question_id).first()
    if not question:
        raise QuestionNotFoundError()
    
    user = User.objects(id=user_id).first()
    if not user:
        raise QuestionServiceError("User not found", "USER_NOT_FOUND", 404)
    
    if not _can_edit_question(question, user):
        raise QuestionAccessDeniedError("You cannot edit this question")
    
    if text is not None:
        question.text = sanitize_input(text)[:5000]
    if explanation is not None:
        question.explanation = sanitize_input(explanation)[:2000]
    if subject is not None:
        question.subject = sanitize_input(subject)[:100] if subject else None
    if topic is not None:
        question.topic = sanitize_input(topic)[:100] if topic else None
    if question_type is not None:
        question.question_type = question_type
    if difficulty is not None:
        question.difficulty = difficulty
    if marks is not None:
        question.marks = marks
    
    if options is not None:
        question_options = []
        for opt in options:
            option_text = sanitize_input(opt.get("text", ""))[:1000]
            if not option_text:
                continue
            option_id = opt.get("option_id") or _generate_option_id()
            question_options.append(QuestionOption(
                option_id=option_id,
                text=option_text,
            ))
        
        if len(question_options) < 2:
            raise QuestionServiceError("At least 2 options required", "INVALID_OPTIONS", 400)
        
        question.options = question_options
    
    if correct_option_id is not None:
        valid_option_ids = [opt.option_id for opt in question.options]
        if correct_option_id not in valid_option_ids:
            raise QuestionServiceError("Invalid correct option ID", "INVALID_CORRECT_OPTION", 400)
        question.correct_option_id = correct_option_id
    
    question.save()
    
    logger.info(f"Question updated: {question.id} by user {user_id}")
    
    return _format_question(question)


def _can_edit_question(question, user) -> bool:
    """Check if user can edit question."""
    if user.role in ["super_admin", "admin_public"]:
        return True
    if question.created_by and str(question.created_by.id) == str(user.id):
        return True
    if user.role == "teacher" and question.institute and str(question.institute.id) == str(user.institute.id if user.institute else ""):
        return True
    return False


def delete_question(question_id: str, user_id: str) -> bool:
    """
    Delete a question.
    
    Args:
        question_id: Question ID
        user_id: Requesting user ID
    
    Returns:
        True if deleted
    """
    from app.models import Question, User
    
    question = Question.objects(id=question_id).first()
    if not question:
        raise QuestionNotFoundError()
    
    user = User.objects(id=user_id).first()
    if not user:
        raise QuestionServiceError("User not found", "USER_NOT_FOUND", 404)
    
    if not _can_edit_question(question, user):
        raise QuestionAccessDeniedError("You cannot delete this question")
    
    question.delete()
    
    logger.info(f"Question deleted: {question_id} by user {user_id}")
    
    return True


def list_questions(
    user_id: str,
    page: int = 1,
    per_page: int = 20,
    institute_id: Optional[str] = None,
    subject: Optional[str] = None,
    topic: Optional[str] = None,
    difficulty: Optional[str] = None,
    is_approved: Optional[bool] = None,
    is_reviewed: Optional[bool] = None,
    search: Optional[str] = None,
    question_type: Optional[str] = None,
) -> Dict[str, Any]:
    """
    List questions with pagination.
    
    Args:
        user_id: Requesting user ID
        page: Page number
        per_page: Items per page
        institute_id: Filter by institute
        subject: Filter by subject
        topic: Filter by topic
        difficulty: Filter by difficulty
        is_approved: Filter by approval status
        is_reviewed: Filter by review status
        search: Search in text
        question_type: Filter by type
    
    Returns:
        Paginated question list
    """
    from app.models import Question, User
    
    user = User.objects(id=user_id).first()
    if not user:
        raise QuestionServiceError("User not found", "USER_NOT_FOUND", 404)
    
    query = {}
    
    if user.role == "super_admin":
        pass
    elif user.role in ["admin_public", "admin_college", "teacher"]:
        if institute_id:
            query["institute"] = institute_id
        elif user.institute:
            query["institute"] = user.institute
    else:
        query["created_by"] = user
    
    if subject:
        query["subject"] = subject
    if topic:
        query["topic"] = topic
    if difficulty:
        query["difficulty"] = difficulty
    if is_approved is not None:
        query["is_approved"] = is_approved
    if is_reviewed is not None:
        query["is_reviewed"] = is_reviewed
    if search:
        query["text__icontains"] = search
    if question_type:
        query["question_type"] = question_type
    
    skip = (page - 1) * per_page
    questions = Question.objects(**query).order_by("-created_at").skip(skip).limit(per_page)
    total = Question.objects(**query).count()
    
    return {
        "items": [_format_question(q) for q in questions],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page,
    }


def bulk_create_questions(
    creator_id: str,
    institute_id: Optional[str],
    questions_data: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Create multiple questions at once.
    
    Args:
        creator_id: ID of user creating questions
        institute_id: ID of institute (optional)
        questions_data: List of question dicts
    
    Returns:
        Creation summary
    """
    from app.models import Question, QuestionOption, User, Institute
    
    creator = User.objects(id=creator_id).first()
    if not creator:
        raise QuestionServiceError("Creator not found", "USER_NOT_FOUND", 404)
    
    institute = None
    if institute_id:
        institute = Institute.objects(id=institute_id).first()
    
    created = 0
    failed = 0
    errors = []
    
    for idx, qdata in enumerate(questions_data):
        try:
            text = sanitize_input(qdata.get("text", ""))[:5000]
            if not text:
                failed += 1
                errors.append({"index": idx, "error": "Question text is required"})
                continue
            
            question_type = qdata.get("question_type", "mcq")
            options_data = qdata.get("options", [])
            
            question_options = []
            for opt in options_data:
                option_text = sanitize_input(opt.get("text", ""))[:1000]
                if not option_text:
                    continue
                option_id = opt.get("option_id") or _generate_option_id()
                question_options.append(QuestionOption(
                    option_id=option_id,
                    text=option_text,
                ))
            
            if len(question_options) < 2:
                failed += 1
                errors.append({"index": idx, "error": "At least 2 options required"})
                continue
            
            correct_option_id = qdata.get("correct_option_id")
            if not correct_option_id:
                correct_option_id = question_options[0].option_id
            
            valid_option_ids = [opt.option_id for opt in question_options]
            if correct_option_id not in valid_option_ids:
                correct_option_id = question_options[0].option_id
            
            question = Question(
                text=text,
                question_type=question_type,
                options=question_options,
                correct_option_id=correct_option_id,
                explanation=sanitize_input(qdata.get("explanation", ""))[:2000] or None,
                subject=sanitize_input(qdata.get("subject", ""))[:100] or None,
                topic=sanitize_input(qdata.get("topic", ""))[:100] or None,
                difficulty=qdata.get("difficulty", "medium"),
                marks=qdata.get("marks", 1),
                source=qdata.get("source", "manual"),
                institute=institute,
                created_by=creator,
                is_reviewed=False,
                is_approved=False,
            )
            question.save()
            created += 1
            
        except Exception as e:
            failed += 1
            errors.append({"index": idx, "error": str(e)})
    
    logger.info(f"Bulk created {created} questions, {failed} failed by user {creator_id}")
    
    return {
        "created": created,
        "failed": failed,
        "total": len(questions_data),
        "errors": errors if errors else None,
    }


def review_question(
    question_id: str,
    reviewer_id: str,
    action: str,
) -> Dict[str, Any]:
    """
    Review/approve a question.
    
    Args:
        question_id: Question ID
        reviewer_id: Reviewing user ID
        action: approve or reject
    
    Returns:
        Updated question
    """
    from app.models import Question, User
    
    question = Question.objects(id=question_id).first()
    if not question:
        raise QuestionNotFoundError()
    
    reviewer = User.objects(id=reviewer_id).first()
    if not reviewer:
        raise QuestionServiceError("Reviewer not found", "USER_NOT_FOUND", 404)
    
    if reviewer.role not in ["super_admin", "admin_public", "admin_college", "teacher"]:
        raise QuestionAccessDeniedError("You cannot review questions")
    
    if action == "approve":
        question.is_approved = True
        question.is_reviewed = True
    elif action == "reject":
        question.is_approved = False
        question.is_reviewed = True
    else:
        raise QuestionServiceError("Invalid action", "INVALID_ACTION", 400)
    
    question.save()
    
    logger.info(f"Question {question_id} {action}d by user {reviewer_id}")
    
    return _format_question(question)
