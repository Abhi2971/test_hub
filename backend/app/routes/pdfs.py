"""
PDF routes for ExamSaaS platform.
Blueprint: /api/v1/pdfs
"""
import logging
from flask import Blueprint, request, g

from app.response import success_response, error_response
from app.utils.decorators import require_roles
from app.services.pdf_service import (
    create_pdf_upload,
    get_pdf_status,
    get_pdf_questions,
    approve_questions,
    PDFServiceError,
    PDFNotFoundError,
)
from app.services.cloudinary_service import upload_file, delete_file

logger = logging.getLogger(__name__)

pdfs_bp = Blueprint("pdfs", __name__, url_prefix="/pdfs")

ALLOWED_MIME_TYPES = [
    "application/pdf",
    "application/x-pdf",
]

MAX_FILE_SIZE = 25 * 1024 * 1024


def _handle_service_error(error: PDFServiceError):
    """Handle PDF service errors."""
    return error_response(error.message, error.status_code)


def _validate_schema(schema, data):
    """Validate request data against schema."""
    try:
        return schema.load(data), None
    except Exception as e:
        errors = e.messages if hasattr(e, "messages") else str(e)
        return None, errors


@pdfs_bp.route("/upload", methods=["POST"])
@require_roles("admin_public", "admin_college")
def upload():
    """
    Upload a PDF file for question generation.
    
    Multipart form data:
        - file: PDF file (max 25MB)
        - topic: Topic for the questions (optional)
        - subject: Subject (optional)
    
    Returns:
        201: PDF upload record with processing status
    """
    if "file" not in request.files:
        return error_response("No file provided", 400)
    
    file = request.files["file"]
    
    if not file.filename:
        return error_response("No file selected", 400)
    
    if not file.filename.lower().endswith(".pdf"):
        return error_response("Only PDF files are allowed", 400)
    
    content_type = file.content_type
    if content_type not in ALLOWED_MIME_TYPES:
        return error_response(
            f"Invalid file type. Allowed types: {ALLOWED_MIME_TYPES}",
            400
        )
    
    file.seek(0, 2)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        return error_response(f"File too large. Maximum size is 25MB", 400)
    
    try:
        topic = request.form.get("topic")
        subject = request.form.get("subject")
        
        institute_id = getattr(g, "current_institute_id", None)
        
        upload_result = upload_file(
            file=file.read(),
            folder=f"pdfs/{g.current_user_id}",
            resource_type="raw",
        )
        
        if not upload_result or not upload_result.get("public_id"):
            return error_response("Failed to upload file to cloud storage", 500)
        
        pdf_record = upload_pdf(
            cloudinary_public_id=upload_result["public_id"],
            file_name=file.filename,
            file_size=file_size,
            topic=topic,
            subject=subject,
            uploaded_by_id=g.current_user_id,
            institute_id=institute_id,
        )
        
        try:
            from app.tasks.pdf_tasks import process_pdf_with_groq_task
            process_pdf_with_groq_task.delay(str(pdf_record.id))
        except Exception as e:
            logger.warning(f"Failed to queue PDF processing task: {e}")
        
        return success_response(pdf_record, "PDF uploaded successfully", status=201)
    
    except PDFServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"PDF upload failed: {e}")
        return error_response("Failed to upload PDF", 500)


@pdfs_bp.route("/<pdf_id>/status", methods=["GET"])
@require_roles("admin_public", "admin_college")
def get_status(pdf_id: str):
    """
    Get PDF processing status.
    
    Returns:
        200: { processing_status, chunks_processed, total_chunks, questions_generated, processing_error }
    """
    try:
        status_data = get_pdf_status(
            pdf_id=pdf_id,
            user_id=g.current_user_id,
            user_role=g.current_role,
        )
        
        return success_response(status_data)
    
    except PDFNotFoundError as e:
        return _handle_service_error(e)
    except PDFServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Get PDF status failed: {e}")
        return error_response("Failed to get PDF status", 500)


@pdfs_bp.route("/<pdf_id>/questions", methods=["GET"])
@require_roles("admin_public", "admin_college")
def get_questions(pdf_id: str):
    """
    Get questions generated from PDF.
    
    Query params:
        - page: Page number (default: 1)
        - per_page: Items per page (default: 20)
        - is_reviewed: Filter by review status
    
    Returns:
        200: Paginated list of generated questions (is_reviewed=False)
    """
    args = request.args.to_dict()
    
    try:
        page = int(args.get("page", 1))
        per_page = int(args.get("per_page", 20))
        
        is_reviewed = None
        if "is_reviewed" in args:
            is_reviewed = args["is_reviewed"].lower() == "true"
        
        result = get_pdf_questions(
            pdf_id=pdf_id,
            user_id=g.current_user_id,
            user_role=g.current_role,
            page=page,
            per_page=per_page,
            is_reviewed=is_reviewed,
        )
        
        return success_response(result)
    
    except PDFNotFoundError as e:
        return _handle_service_error(e)
    except PDFServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Get PDF questions failed: {e}")
        return error_response("Failed to get questions", 500)


@pdfs_bp.route("/<pdf_id>/approve-questions", methods=["POST"])
@require_roles("admin_public", "admin_college")
def approve(pdf_id: str):
    """
    Approve questions generated from PDF.
    
    Input:
        - question_ids: Array of question IDs to approve
    
    Returns:
        200: Approved questions count
    """
    data = request.get_json()
    
    if not data or "question_ids" not in data:
        return error_response("question_ids is required", 400)
    
    if not isinstance(data["question_ids"], list):
        return error_response("question_ids must be an array", 400)
    
    try:
        result = approve_questions(
            pdf_id=pdf_id,
            question_ids=data["question_ids"],
            approved_by=g.current_user_id,
        )
        
        return success_response(result, "Questions approved successfully")
    
    except PDFNotFoundError as e:
        return _handle_service_error(e)
    except PDFServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Approve questions failed: {e}")
        return error_response("Failed to approve questions", 500)