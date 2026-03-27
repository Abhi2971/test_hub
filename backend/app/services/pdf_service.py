"""
PDF service for ExamSaaS platform.
Pure Python - zero Flask imports, zero HTTP concepts.
"""
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class PDFServiceError(Exception):
    """Base exception for PDF service errors."""
    def __init__(self, message: str, code: str, status_code: int = 400):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class PDFNotFoundError(PDFServiceError):
    """PDF not found."""
    def __init__(self):
        super().__init__("PDF not found", "PDF_NOT_FOUND", 404)


class PDFAccessDeniedError(PDFServiceError):
    """Access to PDF denied."""
    def __init__(self, message: str = "Access denied"):
        super().__init__(message, "PDF_ACCESS_DENIED", 403)


def _get_models():
    """Lazy-load models to avoid circular imports."""
    from app.models import PDFUpload, Question, User, Institute
    return PDFUpload, Question, User, Institute


def create_pdf_upload(
    data: dict,
    uploaded_by: str,
    institute_id: str,
) -> dict:
    """
    Create PDFUpload record after Cloudinary upload.
    
    Args:
        data: Dictionary with cloudinary_url, cloudinary_public_id, 
              original_filename, file_size_bytes, page_count
        uploaded_by: User ID who uploaded the PDF
        institute_id: Institute ID
    
    Returns:
        Created PDFUpload dict
    """
    PDFUpload, Question, User, Institute = _get_models()
    
    try:
        from bson import ObjectId
        user_oid = ObjectId(uploaded_by)
        institute_oid = ObjectId(institute_id)
    except Exception as e:
        raise PDFServiceError(f"Invalid ID: {e}", "INVALID_ID", 400)
    
    user = User.objects(id=user_oid).first()
    if not user:
        raise PDFServiceError("User not found", "USER_NOT_FOUND", 404)
    
    institute = Institute.objects(id=institute_oid).first()
    if not institute:
        raise PDFServiceError("Institute not found", "INSTITUTE_NOT_FOUND", 404)
    
    pdf_upload = PDFUpload(
        original_filename=data.get("original_filename", "unknown.pdf"),
        cloudinary_url=data.get("cloudinary_url"),
        cloudinary_public_id=data.get("cloudinary_public_id"),
        file_size_bytes=data.get("file_size_bytes", 0),
        page_count=data.get("page_count", 0),
        institute=institute,
        uploaded_by=user,
        processing_status="uploaded",
        processing_error=None,
        text_extracted=False,
        total_chunks=0,
        chunks_processed=0,
        questions_generated=0,
        questions_approved=0,
    )
    pdf_upload.save()
    
    logger.info(f"PDFUpload created: {pdf_upload.id} by user {uploaded_by}")
    
    try:
        from app.tasks.pdf_tasks import process_pdf_with_groq_task
        task = process_pdf_with_groq_task.delay(str(pdf_upload.id))
        pdf_upload.celery_task_id = task.id
        pdf_upload.save()
        logger.info(f"Queued Celery task {task.id} for PDF {pdf_upload.id}")
    except Exception as e:
        logger.warning(f"Failed to queue Celery task: {e}")
    
    return {
        "id": str(pdf_upload.id),
        "original_filename": pdf_upload.original_filename,
        "cloudinary_url": pdf_upload.cloudinary_url,
        "file_size_bytes": pdf_upload.file_size_bytes,
        "page_count": pdf_upload.page_count,
        "institute_id": str(pdf_upload.institute.id) if pdf_upload.institute else None,
        "uploaded_by_id": str(pdf_upload.uploaded_by.id) if pdf_upload.uploaded_by else None,
        "processing_status": pdf_upload.processing_status,
        "processing_error": pdf_upload.processing_error,
        "text_extracted": pdf_upload.text_extracted,
        "total_chunks": pdf_upload.total_chunks,
        "chunks_processed": pdf_upload.chunks_processed,
        "questions_generated": pdf_upload.questions_generated,
        "questions_approved": pdf_upload.questions_approved,
        "celery_task_id": pdf_upload.celery_task_id,
        "created_at": pdf_upload.created_at.isoformat() if pdf_upload.created_at else None,
    }


def get_pdf_status(
    pdf_id: str,
    user_id: str,
) -> dict:
    """
    Get processing status for PDF.
    
    Args:
        pdf_id: PDF ID
        user_id: Requesting user ID
    
    Returns:
        Status dict with processing info
    """
    PDFUpload, Question, User, Institute = _get_models()
    
    try:
        from bson import ObjectId
        pdf_oid = ObjectId(pdf_id)
        user_oid = ObjectId(user_id)
    except Exception:
        raise PDFServiceError("Invalid ID", "INVALID_ID", 400)
    
    pdf = PDFUpload.objects(id=pdf_oid).first()
    if not pdf:
        raise PDFNotFoundError()
    
    user = User.objects(id=user_oid).first()
    if not user:
        raise PDFServiceError("User not found", "USER_NOT_FOUND", 404)
    
    if user.role not in ["super_admin", "admin_public", "admin_college"]:
        if pdf.institute and user.institute:
            if str(pdf.institute.id) != str(user.institute.id):
                raise PDFAccessDeniedError()
        elif pdf.uploaded_by and str(pdf.uploaded_by.id) != str(user.id):
            if user.role != "teacher":
                raise PDFAccessDeniedError()
    
    return {
        "id": str(pdf.id),
        "original_filename": pdf.original_filename,
        "status": pdf.processing_status,
        "total_chunks": pdf.total_chunks,
        "chunks_processed": pdf.chunks_processed,
        "questions_generated": pdf.questions_generated,
        "questions_approved": pdf.questions_approved,
        "processing_error": pdf.processing_error,
        "celery_task_id": pdf.celery_task_id,
    }


def get_pdf_questions(
    pdf_id: str,
    page: int,
    limit: int,
    user_id: str,
) -> dict:
    """
    Get questions generated from PDF.
    
    Args:
        pdf_id: PDF ID
        page: Page number
        limit: Items per page
        user_id: Requesting user ID
    
    Returns:
        Paginated questions list
    """
    PDFUpload, Question, User, Institute = _get_models()
    
    try:
        from bson import ObjectId
        pdf_oid = ObjectId(pdf_id)
        user_oid = ObjectId(user_id)
    except Exception:
        raise PDFServiceError("Invalid ID", "INVALID_ID", 400)
    
    pdf = PDFUpload.objects(id=pdf_oid).first()
    if not pdf:
        raise PDFNotFoundError()
    
    user = User.objects(id=user_oid).first()
    if not user:
        raise PDFServiceError("User not found", "USER_NOT_FOUND", 404)
    
    total = Question.objects(pdf_upload=pdf, is_reviewed=False).count()
    
    skip = (page - 1) * limit
    questions = Question.objects(pdf_upload=pdf, is_reviewed=False).order_by("-created_at").skip(skip).limit(limit)
    
    items = []
    for q in questions:
        items.append({
            "id": str(q.id),
            "text": q.text,
            "question_type": q.question_type,
            "options": [{"option_id": opt.option_id, "text": opt.text} for opt in q.options],
            "correct_option_id": q.correct_option_id,
            "explanation": q.explanation,
            "subject": q.subject,
            "topic": q.topic,
            "difficulty": q.difficulty,
            "marks": q.marks,
            "source": q.source,
            "is_reviewed": q.is_reviewed,
            "is_approved": q.is_approved,
            "created_at": q.created_at.isoformat() if q.created_at else None,
        })
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
    }


def approve_questions(
    pdf_id: str,
    question_ids: List[str],
    exam_id: Optional[str],
    user_id: str,
) -> dict:
    """
    Approve questions. Optionally add to exam.
    
    Args:
        pdf_id: PDF ID
        question_ids: List of question IDs to approve
        exam_id: Optional exam ID to add questions to
        user_id: Requesting user ID
    
    Returns:
        Approval result
    """
    PDFUpload, Question, User, Institute = _get_models()
    
    try:
        from bson import ObjectId
        pdf_oid = ObjectId(pdf_id)
        user_oid = ObjectId(user_id)
    except Exception:
        raise PDFServiceError("Invalid ID", "INVALID_ID", 400)
    
    user = User.objects(id=user_oid).first()
    if not user:
        raise PDFServiceError("User not found", "USER_NOT_FOUND", 404)
    
    pdf = PDFUpload.objects(id=pdf_oid).first()
    if not pdf:
        raise PDFNotFoundError()
    
    approved_count = 0
    added_to_exam = 0
    
    for qid in question_ids:
        try:
            q_oid = ObjectId(qid)
        except Exception:
            continue
        
        question = Question.objects(id=q_oid, pdf_upload=pdf).first()
        if question:
            question.is_reviewed = True
            question.is_approved = True
            question.save()
            approved_count += 1
    
    pdf.questions_approved = (pdf.questions_approved or 0) + approved_count
    pdf.save()
    
    if exam_id and approved_count > 0:
        try:
            from app.services import exam_service
            result = exam_service.assign_questions_to_exam(
                exam_id=exam_id,
                user_id=user_id,
                question_ids=question_ids,
            )
            added_to_exam = result.get("question_count", 0)
        except Exception as e:
            logger.warning(f"Failed to add questions to exam: {e}")
    
    logger.info(f"Approved {approved_count} questions for PDF {pdf_id}")
    
    return {
        "approved_count": approved_count,
        "added_to_exam": added_to_exam,
    }


def get_user_pdfs(
    institute_id: str,
    page: int,
    limit: int,
) -> dict:
    """
    List PDFs for institute.
    
    Args:
        institute_id: Institute ID
        page: Page number
        limit: Items per page
    
    Returns:
        Paginated PDF list
    """
    PDFUpload, Question, User, Institute = _get_models()
    
    try:
        from bson import ObjectId
        institute_oid = ObjectId(institute_id)
    except Exception:
        raise PDFServiceError("Invalid institute ID", "INVALID_ID", 400)
    
    institute = Institute.objects(id=institute_oid).first()
    if not institute:
        raise PDFServiceError("Institute not found", "INSTITUTE_NOT_FOUND", 404)
    
    total = PDFUpload.objects(institute=institute).count()
    
    skip = (page - 1) * limit
    pdfs = PDFUpload.objects(institute=institute).order_by("-created_at").skip(skip).limit(limit)
    
    items = []
    for pdf in pdfs:
        items.append({
            "id": str(pdf.id),
            "original_filename": pdf.original_filename,
            "cloudinary_url": pdf.cloudinary_url,
            "file_size_bytes": pdf.file_size_bytes,
            "page_count": pdf.page_count,
            "processing_status": pdf.processing_status,
            "processing_error": pdf.processing_error,
            "questions_generated": pdf.questions_generated,
            "questions_approved": pdf.questions_approved,
            "uploaded_by_id": str(pdf.uploaded_by.id) if pdf.uploaded_by else None,
            "created_at": pdf.created_at.isoformat() if pdf.created_at else None,
        })
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
    }
