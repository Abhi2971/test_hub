"""
Analytics service for ExamSaaS platform.
Pure Python - zero Flask imports, zero HTTP concepts.
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class AnalyticsServiceError(Exception):
    """Base exception for analytics service errors."""
    def __init__(self, message: str, code: str = "ANALYTICS_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


def get_overview_analytics(institute_id: str, user_id: str, user_role: str) -> Dict[str, Any]:
    """
    Overview: total_exams, total_students, total_attempts, avg_pass_rate
    
    Args:
        institute_id: The institute ID to fetch analytics for
        user_id: The requesting user ID
        user_role: The role of the requesting user
    
    Returns:
        Dict with total_exams, total_students, total_attempts, avg_pass_rate
    """
    from app.models import Exam, User, ExamAttempt, Result, Institute
    
    try:
        institute = Institute.objects.get(id=institute_id)
    except Institute.DoesNotExist:
        raise AnalyticsServiceError("Institute not found", "INSTITUTE_NOT_FOUND")
    
    total_exams = Exam.objects(institute=institute, status='published').count()
    
    total_students = User.objects(
        institute=institute,
        role__in=['student_registered', 'student_assigned']
    ).count()
    
    total_attempts = ExamAttempt.objects(exam__in=Exam.objects(institute=institute)).count()
    
    passed_results = Result.objects(
        exam__in=Exam.objects(institute=institute),
        passed=True
    ).count()
    
    total_results = Result.objects(
        exam__in=Exam.objects(institute=institute)
    ).count()
    
    avg_pass_rate = 0.0
    if total_results > 0:
        avg_pass_rate = round((passed_results / total_results) * 100, 2)
    
    return {
        "total_exams": total_exams,
        "total_students": total_students,
        "total_attempts": total_attempts,
        "avg_pass_rate": avg_pass_rate
    }


def get_exam_analytics(institute_id: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """
    Per-exam stats grouped by month for charts
    
    Args:
        institute_id: The institute ID
        start_date: Start date in ISO format (YYYY-MM-DD)
        end_date: End date in ISO format (YYYY-MM-DD)
    
    Returns:
        List of dicts with exam_title, month, attempt_count, pass_count, avg_score
    """
    from app.models import Exam, ExamAttempt, Result, Institute
    
    try:
        institute = Institute.objects.get(id=institute_id)
    except Institute.DoesNotExist:
        raise AnalyticsServiceError("Institute not found", "INSTITUTE_NOT_FOUND")
    
    start_dt = datetime.fromisoformat(start_date)
    end_dt = datetime.fromisoformat(end_date)
    
    exams = Exam.objects(institute=institute)
    exam_ids = [exam.id for exam in exams]
    
    if not exam_ids:
        return []
    
    attempts = ExamAttempt.objects(
        exam__in=exam_ids,
        created_at__gte=start_dt,
        created_at__lte=end_dt
    )
    
    exam_stats = {}
    for attempt in attempts:
        exam_obj = attempt.exam
        exam_title = exam_obj.title if exam_obj else "Unknown"
        
        month_key = attempt.created_at.strftime("%Y-%m")
        
        key = (exam_obj.id, month_key)
        if key not in exam_stats:
            exam_stats[key] = {
                "exam_title": exam_title,
                "exam_id": str(exam_obj.id) if exam_obj else None,
                "month": month_key,
                "attempt_count": 0,
                "pass_count": 0,
                "total_score": 0.0,
                "result_count": 0
            }
        
        exam_stats[key]["attempt_count"] += 1
        
        result = Result.objects(attempt=attempt).first()
        if result:
            exam_stats[key]["result_count"] += 1
            exam_stats[key]["total_score"] += result.percentage
            if result.passed:
                exam_stats[key]["pass_count"] += 1
    
    result_list = []
    for key, stats in exam_stats.items():
        avg_score = 0.0
        if stats["result_count"] > 0:
            avg_score = round(stats["total_score"] / stats["result_count"], 2)
        
        result_list.append({
            "exam_title": stats["exam_title"],
            "exam_id": stats["exam_id"],
            "month": stats["month"],
            "attempt_count": stats["attempt_count"],
            "pass_count": stats["pass_count"],
            "avg_score": avg_score
        })
    
    result_list.sort(key=lambda x: (x["exam_title"], x["month"]))
    
    return result_list


def get_student_analytics(institute_id: str) -> Dict[str, Any]:
    """
    Student growth and active students
    
    Args:
        institute_id: The institute ID
    
    Returns:
        Dict with total_students, new_students_30d, active_students_30d
    """
    from app.models import User, ExamAttempt, Exam, Institute
    
    try:
        institute = Institute.objects.get(id=institute_id)
    except Institute.DoesNotExist:
        raise AnalyticsServiceError("Institute not found", "INSTITUTE_NOT_FOUND")
    
    total_students = User.objects(
        institute=institute,
        role__in=['student_registered', 'student_assigned']
    ).count()
    
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    new_students_30d = User.objects(
        institute=institute,
        role__in=['student_registered', 'student_assigned'],
        created_at__gte=thirty_days_ago
    ).count()
    
    exam_ids = [exam.id for exam in Exam.objects(institute=institute)]
    
    active_students_30d = 0
    if exam_ids:
        active_students_30d = ExamAttempt.objects(
            exam__in=exam_ids,
            created_at__gte=thirty_days_ago
        ).distinct('student')
        active_students_30d = len(active_students_30d)
    
    return {
        "total_students": total_students,
        "new_students_30d": new_students_30d,
        "active_students_30d": active_students_30d
    }


def get_revenue_analytics(institute_id: str) -> Dict[str, Any]:
    """
    Wallet transactions, subscription costs, AI usage
    
    Args:
        institute_id: The institute ID
    
    Returns:
        Dict with total_credits, subscription_costs, ai_tasks_30d
    """
    from app.models import WalletTransaction, Wallet, User, Institute, AIRecommendation
    
    try:
        institute = Institute.objects.get(id=institute_id)
    except Institute.DoesNotExist:
        raise AnalyticsServiceError("Institute not found", "INSTITUTE_NOT_FOUND")
    
    institute_users = User.objects(institute=institute)
    user_ids = [user.id for user in institute_users]
    
    wallets = Wallet.objects(user__in=user_ids)
    wallet_ids = [w.id for w in wallets]
    
    total_credits = 0
    if wallet_ids:
        total_credits = WalletTransaction.objects(
            wallet__in=wallet_ids,
            type='credit'
        ).sum('amount') or 0
    
    subscription_costs = 0
    if wallet_ids:
        subscription_costs = WalletTransaction.objects(
            wallet__in=wallet_ids,
            source='subscription'
        ).sum('amount') or 0
    
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    ai_tasks_30d = AIRecommendation.objects(
        student__in=user_ids,
        created_at__gte=thirty_days_ago
    ).count()
    
    return {
        "total_credits": total_credits,
        "subscription_costs": subscription_costs,
        "ai_tasks_30d": ai_tasks_30d
    }


def get_live_attempts(exam_id: str, user_id: str) -> List[Dict[str, Any]]:
    """
    Live monitoring - students currently taking exam
    
    Args:
        exam_id: The exam ID to monitor
        user_id: The requesting user ID (teacher/admin)
    
    Returns:
        List of dicts with student_name, started_at, answered_count, tab_switch_count, violations
    """
    from app.models import ExamAttempt, Exam, User
    
    try:
        exam = Exam.objects.get(id=exam_id)
    except Exam.DoesNotExist:
        raise AnalyticsServiceError("Exam not found", "EXAM_NOT_FOUND")
    
    attempts = ExamAttempt.objects(
        exam=exam,
        status='in_progress'
    )
    
    result_list = []
    for attempt in attempts:
        student = attempt.student
        answered_count = len([a for a in attempt.answers if a.selected_option_id])
        
        violations_list = []
        for violation in attempt.violations:
            violations_list.append({
                "type": violation.type,
                "occurred_at": violation.occurred_at.isoformat() if violation.occurred_at else None,
                "screenshot_url": violation.screenshot_url
            })
        
        result_list.append({
            "attempt_id": str(attempt.id),
            "student_id": str(student.id) if student else None,
            "student_name": student.full_name if student else "Unknown",
            "student_email": student.email if student else None,
            "started_at": attempt.started_at.isoformat() if attempt.started_at else None,
            "answered_count": answered_count,
            "total_questions": len(attempt.answers),
            "tab_switch_count": attempt.tab_switch_count,
            "face_mismatch_count": attempt.face_mismatch_count,
            "violations": violations_list,
            "ip_address": attempt.ip_address
        })
    
    result_list.sort(key=lambda x: x["started_at"] or "", reverse=True)
    
    return result_list
