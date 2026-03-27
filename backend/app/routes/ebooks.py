"""
Ebook routes for ExamSaaS platform.
Blueprint: /api/v1/ebooks
"""
import logging
from flask import Blueprint, request, g

from app.response import success_response, error_response
from app.utils.decorators import require_roles
from app.services.ebook_service import (
    create_ebook,
    list_ebooks,
    get_ebook_detail,
    get_ebook_read_url,
    delete_ebook,
    EbookServiceError,
    EbookNotFoundError,
)
from app.services.cloudinary_service import upload_file, delete_file

logger = logging.getLogger(__name__)

ebooks_bp = Blueprint("ebooks", __name__, url_prefix="/ebooks")

ALLOWED_EXTENSIONS = [".pdf", ".epub", ".mobi"]
MAX_FILE_SIZE = 100 * 1024 * 1024


def _handle_service_error(error: EbookServiceError):
    """Handle ebook service errors."""
    return error_response(error.message, error.status_code)


def _validate_schema(schema, data):
    """Validate request data against schema."""
    try:
        return schema.load(data), None
    except Exception as e:
        errors = e.messages if hasattr(e, "messages") else str(e)
        return None, errors


@ebooks_bp.route("", methods=["POST"])
@require_roles("admin_public", "admin_college")
def create():
    """
    Upload and create a new ebook.
    
    Multipart form data:
        - file: Ebook file (PDF, EPUB, MOBI - max 100MB)
        - title: Ebook title
        - author: Author name
        - description: Description
        - subject: Subject
        - access_level: free, premium, institute_only (default: free)
        - price: Price in rupees (if premium)
    
    Returns:
        201: Created ebook record
    """
    if "file" not in request.files:
        return error_response("No file provided", 400)
    
    file = request.files["file"]
    
    if not file.filename:
        return error_response("No file selected", 400)
    
    ext = file.filename.lower().split(".")[-1]
    if f".{ext}" not in ALLOWED_EXTENSIONS:
        return error_response(
            f"Invalid file type. Allowed: {ALLOWED_EXTENSIONS}",
            400
        )
    
    file.seek(0, 2)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        return error_response(f"File too large. Maximum size is 100MB", 400)
    
    title = request.form.get("title")
    if not title:
        return error_response("title is required", 400)
    
    try:
        upload_result = upload_file(
            file=file.read(),
            folder=f"ebooks/{g.current_user_id}",
            resource_type="raw",
        )
        
        if not upload_result or not upload_result.get("public_id"):
            return error_response("Failed to upload file to cloud storage", 500)
        
        institute_id = getattr(g, "current_institute_id", None)
        
        ebook = create_ebook(
            cloudinary_public_id=upload_result["public_id"],
            file_name=file.filename,
            file_size=file_size,
            title=title,
            author=request.form.get("author"),
            description=request.form.get("description"),
            subject=request.form.get("subject"),
            access_level=request.form.get("access_level", "free"),
            price=float(request.form.get("price", 0)) if request.form.get("price") else 0,
            uploaded_by_id=g.current_user_id,
            institute_id=institute_id,
        )
        
        return success_response(ebook, "Ebook created successfully", status=201)
    
    except EbookServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Create ebook failed: {e}")
        return error_response("Failed to create ebook", 500)


@ebooks_bp.route("", methods=["GET"])
@require_roles("student_registered", "student_assigned")
def list():
    """
    List available ebooks.
    
    Query params:
        - page: Page number (default: 1)
        - per_page: Items per page (default: 20)
        - access_level: Filter by access level
        - subject: Filter by subject
        - search: Search by title or author
    
    Returns:
        200: Paginated list of ebooks
    """
    args = request.args.to_dict()
    
    try:
        page = int(args.get("page", 1))
        per_page = int(args.get("per_page", 20))
        
        filters = {}
        if args.get("access_level"):
            filters["access_level"] = args["access_level"]
        if args.get("subject"):
            filters["subject"] = args["subject"]
        if args.get("search"):
            filters["search"] = args["search"]
        
        institute_id = getattr(g, "current_institute_id", None)
        
        result = list_ebooks(
            filters=filters,
            page=page,
            limit=per_page,
        )
        
        return success_response(result)
    
    except EbookServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"List ebooks failed: {e}")
        return error_response("Failed to list ebooks", 500)


@ebooks_bp.route("/<ebook_id>", methods=["GET"])
@require_roles("student_registered", "student_assigned")
def get(ebook_id: str):
    """
    Get ebook details and increment view count.
    
    Returns:
        200: Ebook details
    """
    try:
        institute_id = getattr(g, "current_institute_id", None)
        
        ebook = get_ebook_detail(
            ebook_id=ebook_id,
            user_id=g.current_user_id,
            user_role=g.current_role,
            institute_id=institute_id,
        )
        
        return success_response(ebook)
    
    except EbookNotFoundError as e:
        return _handle_service_error(e)
    except EbookServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Get ebook failed: {e}")
        return error_response("Failed to get ebook", 500)


@ebooks_bp.route("/<ebook_id>/read", methods=["GET"])
@require_roles("student_registered", "student_assigned")
def read(ebook_id: str):
    """
    Get signed URL for reading the ebook.
    
    Returns:
        200: { read_url, expires_in }
    """
    try:
        institute_id = getattr(g, "current_institute_id", None)
        
        result = get_ebook_read_url(
            ebook_id=ebook_id,
            user_id=g.current_user_id,
            user_role=g.current_role,
            institute_id=institute_id,
        )
        
        return success_response(result)
    
    except EbookNotFoundError as e:
        return _handle_service_error(e)
    except EbookServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Get ebook read URL failed: {e}")
        return error_response("Failed to get read URL", 500)


@ebooks_bp.route("/<ebook_id>", methods=["DELETE"])
@require_roles("admin_public", "admin_college")
def delete(ebook_id: str):
    """
    Soft delete an ebook (set is_active=False).
    
    Returns:
        200: Ebook deleted successfully
    """
    try:
        result = delete_ebook(
            ebook_id=ebook_id,
            deleted_by=g.current_user_id,
        )
        
        return success_response(result, "Ebook deleted successfully")
    
    except EbookNotFoundError as e:
        return _handle_service_error(e)
    except EbookServiceError as e:
        return _handle_service_error(e)
    except Exception as e:
        logger.error(f"Delete ebook failed: {e}")
        return error_response("Failed to delete ebook", 500)