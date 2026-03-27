"""
Result service for ExamSaaS platform.
Pure Python - zero Flask imports, zero HTTP concepts.
"""
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class ResultServiceError(Exception):
    """Base exception for result service errors."""
    def __init__(self, message: str, code: str, status_code: int = 400):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class ResultNotFoundError(ResultServiceError):
    """Result not found."""
    def __init__(self):
        super().__init__("Result not found", "RESULT_NOT_FOUND", 404)


class ResultNotPublishedError(ResultServiceError):
    """Result not published."""
    def __init__(self):
        super().__init__("Result not published", "RESULT_NOT_PUBLISHED", 403)


def _compute_grade(percentage: float) -> str:
    """
    Compute grade from percentage.
    
    Args:
        percentage: Score percentage
    
    Returns:
        Grade string
    """
    if percentage >= 90:
        return "A+"
    elif percentage >= 80:
        return "A"
    elif percentage >= 70:
        return "B"
    elif percentage >= 60:
        return "C"
    elif percentage >= 50:
        return "D"
    else:
        return "F"


def calculate_result(attempt_id: str) -> Dict[str, Any]:
    """
    Calculate and store result for an attempt.
    Pure Python - no DB side effects besides final save.
    
    Args:
        attempt_id: Attempt ID
    
    Returns:
        Result dictionary
    """
    from app.models import ExamAttempt, Result, Question, PerQuestionAnalysis, TopicPerformance
    
    attempt = ExamAttempt.objects(id=attempt_id).first()
    if not attempt:
        raise ResultServiceError("Attempt not found", "ATTEMPT_NOT_FOUND", 404)
    
    exam = attempt.exam
    student = attempt.student
    
    existing_result = Result.objects(attempt=attempt).first()
    if existing_result:
        return _format_result(existing_result)
    
    if exam:
        questions_query = Question.objects(exam=exam)
    else:
        questions_query = Question.objects()
    
    all_questions = list(questions_query)
    question_ids = [str(q.id) for q in all_questions[:50]]
    question_map = {q.id: q for q in all_questions}
    
    answer_map = {a.question_id: a for a in attempt.answers}
    
    correct_count = 0
    wrong_count = 0
    unattempted_count = 0
    total_score = 0.0
    topic_stats = {}
    
    per_question_analysis = []
    
    for qid in question_ids:
        q = question_map.get(qid)
        if not q:
            continue
        
        topic = q.topic or "General"
        if topic not in topic_stats:
            topic_stats[topic] = {"correct": 0, "total": 0, "time": 0}
        
        answer = answer_map.get(qid)
        
        time_spent = answer.time_spent_seconds if answer else 0
        topic_stats[topic]["total"] += 1
        topic_stats[topic]["time"] += time_spent
        
        if not answer or not answer.selected_option_id:
            unattempted_count += 1
            per_question_analysis.append(PerQuestionAnalysis(
                question_id=qid,
                correct=False,
                time_spent_seconds=time_spent,
                topic=topic,
            ))
            continue
        
        is_correct = answer.selected_option_id == q.correct_option_id
        
        if is_correct:
            correct_count += 1
            total_score += q.marks
            topic_stats[topic]["correct"] += 1
        
        per_question_analysis.append(PerQuestionAnalysis(
            question_id=qid,
            correct=is_correct,
            time_spent_seconds=time_spent,
            topic=topic,
        ))
    
    wrong_count = len(question_ids) - correct_count - unattempted_count
    
    total_marks = exam.total_marks
    if total_marks <= 0:
        total_marks = sum(q.marks for q in question_map.values())
    
    percentage = (total_score / total_marks * 100) if total_marks > 0 else 0
    passed = percentage >= exam.passing_percentage
    grade = _compute_grade(percentage)
    
    topic_performance = []
    for topic, stats in topic_stats.items():
        topic_pct = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0
        topic_performance.append(TopicPerformance(
            topic=topic,
            correct=stats["correct"],
            total=stats["total"],
            percentage=round(topic_pct, 2),
        ))
    
    result = Result(
        exam=exam,
        student=student,
        attempt=attempt,
        institute=exam.institute,
        score=total_score,
        total_marks=total_marks,
        percentage=round(percentage, 2),
        passed=passed,
        grade=grade,
        correct_count=correct_count,
        wrong_count=wrong_count,
        unattempted_count=unattempted_count,
        per_question_analysis=per_question_analysis,
        topic_performance=topic_performance,
        rank=None,
        is_published=exam.result_mode == "instant",
    )
    result.save()
    
    logger.info(f"Result calculated for attempt {attempt_id}: score={total_score}, percentage={percentage}%")
    
    return _format_result(result)


def _format_result(result) -> Dict[str, Any]:
    """Format result for response."""
    return {
        "id": str(result.id),
        "exam_id": str(result.exam.id) if result.exam else None,
        "student_id": str(result.student.id) if result.student else None,
        "attempt_id": str(result.attempt.id) if result.attempt else None,
        "score": result.score,
        "total_marks": result.total_marks,
        "percentage": result.percentage,
        "passed": result.passed,
        "grade": result.grade,
        "correct_count": result.correct_count,
        "wrong_count": result.wrong_count,
        "unattempted_count": result.unattempted_count,
        "rank": result.rank,
        "is_published": result.is_published,
        "per_question_analysis": [
            {
                "question_id": a.question_id,
                "correct": a.correct,
                "time_spent_seconds": a.time_spent_seconds,
                "topic": a.topic,
            }
            for a in result.per_question_analysis
        ],
        "topic_performance": [
            {
                "topic": t.topic,
                "correct": t.correct,
                "total": t.total,
                "percentage": t.percentage,
            }
            for t in result.topic_performance
        ],
        "created_at": result.created_at.isoformat() if result.created_at else None,
    }


def compute_rank(exam_id: str) -> List[Dict[str, Any]]:
    """
    Compute and update ranks for all results of an exam.
    
    Args:
        exam_id: Exam ID
    
    Returns:
        Ranked results
    """
    from app.models import Result, Exam
    
    exam = Exam.objects(id=exam_id).first()
    if not exam:
        raise ResultServiceError("Exam not found", "EXAM_NOT_FOUND", 404)
    
    results = Result.objects(exam=exam, is_published=True).order_by("-percentage", "created_at")
    
    ranked = []
    for rank, result in enumerate(results, 1):
        result.rank = rank
        result.save()
        ranked.append({
            "rank": rank,
            "student_id": str(result.student.id) if result.student else None,
            "student_name": result.student.full_name if result.student else None,
            "score": result.score,
            "percentage": result.percentage,
            "grade": result.grade,
        })
    
    logger.info(f"Computed ranks for exam {exam_id}")
    
    return ranked


def publish_result(result_id: str, admin_id: str) -> Dict[str, Any]:
    """
    Publish a result.
    
    Args:
        result_id: Result ID
        admin_id: Admin user ID
    
    Returns:
        Updated result
    """
    from app.models import Result, User
    
    result = Result.objects(id=result_id).first()
    if not result:
        raise ResultNotFoundError()
    
    admin = User.objects(id=admin_id).first()
    if not admin:
        raise ResultServiceError("Admin not found", "USER_NOT_FOUND", 404)
    
    if admin.role not in ["super_admin", "admin_public", "admin_college", "teacher"]:
        raise ResultServiceError("Not authorized", "UNAUTHORIZED", 403)
    
    result.is_published = True
    result.save()
    
    logger.info(f"Result {result_id} published by admin {admin_id}")
    
    return _format_result(result)


def publish_all_results(exam_id: str, admin_id: str) -> Dict[str, Any]:
    """
    Publish all results for an exam.
    
    Args:
        exam_id: Exam ID
        admin_id: Admin user ID
    
    Returns:
        Publication summary
    """
    from app.models import Result, Exam, User
    
    exam = Exam.objects(id=exam_id).first()
    if not exam:
        raise ResultServiceError("Exam not found", "EXAM_NOT_FOUND", 404)
    
    admin = User.objects(id=admin_id).first()
    if not admin:
        raise ResultServiceError("Admin not found", "USER_NOT_FOUND", 404)
    
    if admin.role not in ["super_admin", "admin_public", "admin_college", "teacher"]:
        raise ResultServiceError("Not authorized", "UNAUTHORIZED", 403)
    
    results = Result.objects(exam=exam)
    count = 0
    
    for result in results:
        result.is_published = True
        result.save()
        count += 1
    
    compute_rank(exam_id)
    
    logger.info(f"Published {count} results for exam {exam_id} by admin {admin_id}")
    
    return {
        "exam_id": exam_id,
        "published_count": count,
    }


def get_result(result_id: str, user_id: str) -> Dict[str, Any]:
    """
    Get result by ID.
    
    Args:
        result_id: Result ID
        user_id: Requesting user ID
    
    Returns:
        Result dictionary
    """
    from app.models import Result, User
    
    result = Result.objects(id=result_id).first()
    if not result:
        raise ResultNotFoundError()
    
    user = User.objects(id=user_id).first()
    if not user:
        raise ResultServiceError("User not found", "USER_NOT_FOUND", 404)
    
    is_owner = str(result.student.id) == user_id
    is_creator = str(result.exam.created_by.id) == user_id if result.exam and result.exam.created_by else False
    is_admin = user.role in ["super_admin", "admin_public", "admin_college", "teacher"]
    
    if not (is_owner or is_creator or is_admin):
        if not result.is_published:
            raise ResultNotPublishedError()
    
    return _format_result(result)


def get_student_result(exam_id: str, student_id: str) -> Dict[str, Any]:
    """
    Get student's result for an exam.
    
    Args:
        exam_id: Exam ID
        student_id: Student ID
    
    Returns:
        Result dictionary
    """
    from app.models import Exam, User
    
    exam = Exam.objects(id=exam_id).first()
    if not exam:
        raise ResultServiceError("Exam not found", "EXAM_NOT_FOUND", 404)
    
    student = User.objects(id=student_id).first()
    if not student:
        raise ResultServiceError("Student not found", "STUDENT_NOT_FOUND", 404)
    
    from app.models import Result
    result = Result.objects(exam=exam, student=student).first()
    
    if not result:
        raise ResultNotFoundError()
    
    if not result.is_published:
        raise ResultNotPublishedError()
    
    return _format_result(result)


def list_results(
    user_id: str,
    exam_id: Optional[str] = None,
    page: int = 1,
    per_page: int = 20,
    include_unpublished: bool = False,
) -> Dict[str, Any]:
    """
    List results with pagination.
    
    Args:
        user_id: Requesting user ID
        exam_id: Filter by exam
        page: Page number
        per_page: Items per page
        include_unpublished: Include unpublished results
    
    Returns:
        Paginated result list
    """
    from app.models import Result, User, Exam
    
    user = User.objects(id=user_id).first()
    if not user:
        raise ResultServiceError("User not found", "USER_NOT_FOUND", 404)
    
    query = {}
    
    if user.role in ["student_registered", "student_assigned"]:
        query["student"] = user
        if not include_unpublished:
            query["is_published"] = True
    elif exam_id:
        query["exam"] = exam_id
        if not include_unpublished:
            query["is_published"] = True
    elif user.role in ["super_admin", "admin_public", "admin_college", "teacher"]:
        if not include_unpublished:
            query["is_published"] = True
    else:
        query["student"] = user
        query["is_published"] = True
    
    if exam_id:
        query["exam"] = exam_id
    
    skip = (page - 1) * per_page
    results = Result.objects(**query).order_by("-created_at").skip(skip).limit(per_page)
    total = Result.objects(**query).count()
    
    items = []
    for result in results:
        items.append(_format_result(result))
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page if total > 0 else 0,
    }


def get_exam_analytics(exam_id: str, user_id: str) -> Dict[str, Any]:
    """
    Get analytics for an exam.
    
    Args:
        exam_id: Exam ID
        user_id: Requesting user ID
    
    Returns:
        Analytics dictionary
    """
    from app.models import Result, Exam, User, ExamAttempt
    
    exam = Exam.objects(id=exam_id).first()
    if not exam:
        raise ResultServiceError("Exam not found", "EXAM_NOT_FOUND", 404)
    
    user = User.objects(id=user_id).first()
    if not user:
        raise ResultServiceError("User not found", "USER_NOT_FOUND", 404)
    
    if user.role not in ["super_admin", "admin_public", "admin_college", "teacher"]:
        raise ResultServiceError("Not authorized", "UNAUTHORIZED", 403)
    
    results = Result.objects(exam=exam)
    attempts = ExamAttempt.objects(exam=exam)
    
    total_students = attempts.distinct("student")
    total_attempts = attempts.count()
    total_results = results.count()
    published_results = results.filter(is_published=True).count()
    
    scores = [r.percentage for r in results]
    avg_score = sum(scores) / len(scores) if scores else 0
    max_score = max(scores) if scores else 0
    min_score = min(scores) if scores else 0
    
    passed_count = results.filter(passed=True).count()
    fail_count = total_results - passed_count
    
    grade_dist = {"A+": 0, "A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
    for r in results:
        if r.grade in grade_dist:
            grade_dist[r.grade] += 1
    
    denominator = len(total_students) * max(exam.allowed_attempts or 1, 1)
    attendance_rate = (total_attempts / denominator * 100) if denominator > 0 and total_students else 0
    
    return {
        "exam_id": exam_id,
        "exam_title": exam.title,
        "total_enrolled": len(total_students),
        "total_attempts": total_attempts,
        "completed_results": total_results,
        "published_results": published_results,
        "avg_score": round(avg_score, 2),
        "max_score": max_score,
        "min_score": min_score,
        "passed_count": passed_count,
        "failed_count": fail_count,
        "pass_rate": round(passed_count / total_results * 100, 2) if total_results > 0 else 0,
        "grade_distribution": grade_dist,
        "attendance_rate": round(attendance_rate, 2),
    }
