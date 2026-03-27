"""
Certificate tasks for ExamSaaS platform.
Celery tasks for certificate generation with reportlab and Cloudinary.
"""
import logging
from datetime import datetime, timezone
from io import BytesIO
from typing import Dict, Any
import uuid

logger = logging.getLogger(__name__)

try:
    from celery import Task
    
    class CertificateTask(Task):
        """Base task class for certificate operations."""
        max_retries = 1
        default_retry_delay = 60
        acks_late = True
        reject_on_worker_lost = True
        queue = "certificates"
        
        def on_failure(self, exc, task_id, args, kwargs, einfo):
            logger.error(f"Certificate task {task_id} failed: {exc}")
            super().on_failure(exc, task_id, args, kwargs, einfo)
    
    def _celery_task(func):
        """Decorator to make a function a Celery task."""
        from app.extensions import celery
        return celery.task(
            bind=True,
            max_retries=1,
            default_retry_delay=60,
            acks_late=True,
            reject_on_worker_lost=True,
            queue="certificates",
        )(func)

    @_celery_task
    def generate_and_upload_certificate_task(self, result_id: str) -> Dict[str, Any]:
        """
        Generate and upload certificate PDF.
        
        Args:
            result_id: Result document ID
        
        Returns:
            Certificate details
        """
        from app.models import Result, Certificate
        from app.services.cloudinary_service import upload_certificate
        from app.tasks.email_tasks import send_certificate_email_task
        
        try:
            existing_cert = Certificate.objects(result=result_id).first()
            if existing_cert:
                logger.info(f"Certificate already exists for result {result_id}")
                return {
                    "status": "exists",
                    "certificate_id": str(existing_cert.id),
                    "certificate_code": existing_cert.certificate_code,
                }
            
            result = Result.objects(id=result_id).first()
            if not result:
                logger.error(f"Result not found: {result_id}")
                return {"status": "failed", "error": "Result not found"}
            
            if not result.passed:
                logger.warning(f"Result {result_id} not passed, skipping certificate")
                return {"status": "skipped", "error": "Student did not pass"}
            
            exam = result.exam
            if not exam or not exam.certificate_enabled:
                logger.warning(f"Certificate not enabled for exam {exam.id if exam else 'unknown'}")
                return {"status": "skipped", "error": "Certificate not enabled"}
            
            student = result.student
            institute = exam.institute
            
            certificate_code = uuid.uuid4().hex[:16].upper()
            
            pdf_buffer = _generate_certificate_pdf(
                student_name=student.full_name if student else "Student",
                exam_title=exam.title,
                score=result.score,
                total_marks=result.total_marks,
                percentage=result.percentage,
                grade=result.grade,
                issued_at=result.created_at or datetime.now(timezone.utc),
                institute_name=institute.name if institute else "ExamSaaS",
                institute_logo=institute.logo_url if institute else None,
                certificate_code=certificate_code,
                app_url=_get_config("APP_URL", "http://localhost:5173"),
            )
            
            institute_id = str(institute.id) if institute else "general"
            
            upload_result = upload_certificate(
                file_bytes=pdf_buffer.getvalue(),
                certificate_code=certificate_code,
                institute_id=institute_id,
            )
            
            certificate = Certificate(
                result=result,
                student=student,
                exam=exam,
                institute=institute,
                certificate_code=certificate_code,
                certificate_url=upload_result["url"],
                public_id=upload_result["public_id"],
                issued_at=datetime.now(timezone.utc),
            )
            certificate.save()
            
            if student and student.email:
                try:
                    send_certificate_email_task.delay(
                        student.email,
                        student.full_name or "Student",
                        exam.title,
                        upload_result["url"],
                        certificate_code,
                    )
                except Exception as e:
                    logger.warning(f"Failed to queue certificate email: {e}")
            
            logger.info(f"Certificate generated for result {result_id}: {certificate_code}")
            
            return {
                "status": "completed",
                "certificate_id": str(certificate.id),
                "certificate_code": certificate_code,
                "url": upload_result["url"],
            }
        
        except Exception as exc:
            logger.exception(f"generate_and_upload_certificate_task failed: {exc}")
            
            if self.request.retries < self.max_retries:
                raise self.retry(exc=exc, countdown=60)
            
            return {"status": "failed", "error": str(exc)}

except ImportError:
    logger.warning("Celery not available - certificate task decorators not applied")
    
    def generate_and_upload_certificate_task(result_id: str) -> Dict[str, Any]:
        """Fallback when Celery not available."""
        logger.warning("generate_and_upload_certificate_task called without Celery")
        return {"status": "failed", "error": "Celery not available"}


def _get_config(key: str, default: Any = None) -> Any:
    """Get configuration value."""
    try:
        from flask import current_app
        return current_app.config.get(key, default)
    except RuntimeError:
        return default


def _generate_certificate_pdf(
    student_name: str,
    exam_title: str,
    score: float,
    total_marks: float,
    percentage: float,
    grade: str,
    issued_at: datetime,
    institute_name: str,
    institute_logo: str = None,
    certificate_code: str = "",
    app_url: str = "http://localhost:5173",
) -> BytesIO:
    """
    Generate certificate PDF using reportlab.
    
    Args:
        student_name: Student's full name
        exam_title: Exam title
        score: Score obtained
        total_marks: Total marks
        percentage: Percentage score
        grade: Letter grade
        issued_at: Issue datetime
        institute_name: Institute name
        institute_logo: Institute logo URL
        certificate_code: Unique certificate code
        app_url: App URL for QR code
    
    Returns:
        BytesIO buffer with PDF content
    """
    try:
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.units import inch
        from reportlab.pdfgen import canvas
        from reportlab.lib.colors import HexColor, black, white
        from reportlab.lib.utils import ImageReader
        import qrcode
    except ImportError:
        logger.warning("reportlab or qrcode not available, using fallback")
        return _generate_simple_certificate(
            student_name, exam_title, score, percentage, grade, issued_at, certificate_code
        )
    
    buffer = BytesIO()
    page_width, page_height = landscape(A4)
    
    c = canvas.Canvas(buffer, pagesize=landscape(A4))
    
    gold_color = HexColor("#D97706")
    blue_color = HexColor("#2563EB")
    dark_color = HexColor("#0F172A")
    gray_color = HexColor("#6B7280")
    light_gray = HexColor("#374151")
    
    c.setStrokeColor(gold_color)
    c.setLineWidth(3)
    c.rect(20, 20, page_width - 40, page_height - 40)
    
    c.setStrokeColor(blue_color)
    c.setLineWidth(1)
    c.setStrokeAlpha(0.3)
    c.rect(30, 30, page_width - 60, page_height - 60)
    c.setStrokeAlpha(1)
    
    if institute_logo:
        try:
            import urllib.request
            logo_buffer = BytesIO(urllib.request.urlopen(institute_logo).read())
            c.drawImage(ImageReader(logo_buffer), page_width / 2 - 60, page_height - 80, width=120, height=40, preserveAspectRatio=True)
        except Exception:
            pass
    
    c.setFillColor(dark_color)
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(page_width / 2, page_height - 120, "Certificate of Achievement")
    
    c.setFillColor(gray_color)
    c.setFont("Helvetica", 16)
    c.drawCentredString(page_width / 2, page_height - 155, "This is to certify that")
    
    c.setFillColor(blue_color)
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(page_width / 2, page_height - 195, student_name)
    
    c.setFillColor(gray_color)
    c.setFont("Helvetica", 16)
    c.drawCentredString(page_width / 2, page_height - 230, "has successfully completed")
    
    c.setFillColor(dark_color)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(page_width / 2, page_height - 260, exam_title)
    
    c.setFillColor(light_gray)
    c.setFont("Helvetica", 18)
    score_text = f"with a score of {score:.1f}% (Grade: {grade})"
    c.drawCentredString(page_width / 2, page_height - 290, score_text)
    
    c.setFillColor(gray_color)
    c.setFont("Helvetica", 14)
    date_text = f"on {issued_at.strftime('%B %d, %Y')}"
    c.drawCentredString(page_width / 2, page_height - 315, date_text)
    
    c.setFont("Helvetica", 14)
    c.drawCentredString(page_width / 2, page_height - 345, institute_name)
    
    c.setStrokeColor(gray_color)
    c.setLineWidth(1)
    c.line(100, page_height - 370, page_width - 100, page_height - 370)
    
    c.setFillColor(HexColor("#9CA3AF"))
    c.setFont("Helvetica", 10)
    c.drawString(60, 50, f"Certificate Code: {certificate_code}")
    
    c.setFillColor(HexColor("#9CA3AF"))
    c.drawRightString(page_width - 60, 50, "Verify at: examsaas.com/verify")
    
    qr_url = f"{app_url}/certificates/verify/{certificate_code}"
    qr_img = qrcode.make(qr_url)
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    
    c.drawImage(ImageReader(qr_buffer), page_width - 110, 30, width=80, height=80)
    
    c.save()
    buffer.seek(0)
    
    return buffer


def _generate_simple_certificate(
    student_name: str,
    exam_title: str,
    score: float,
    percentage: float,
    grade: str,
    issued_at: datetime,
    certificate_code: str,
) -> BytesIO:
    """
    Generate a simple certificate PDF without reportlab.
    
    Returns:
        BytesIO buffer with basic PDF content
    """
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4, landscape
    from io import BytesIO as IOBytesIO
    
    buffer = IOBytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(A4))
    
    width, height = landscape(A4)
    
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(width / 2, height - 100, "Certificate of Achievement")
    
    c.setFont("Helvetica", 16)
    c.drawCentredString(width / 2, height - 150, "This is to certify that")
    
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(width / 2, height - 200, student_name)
    
    c.setFont("Helvetica", 16)
    c.drawCentredString(width / 2, height - 240, "has successfully completed")
    
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(width / 2, height - 280, exam_title)
    
    c.setFont("Helvetica", 18)
    c.drawCentredString(width / 2, height - 320, f"Score: {percentage:.1f}% | Grade: {grade}")
    
    c.setFont("Helvetica", 10)
    c.drawCentredString(width / 2, height - 360, f"Certificate Code: {certificate_code}")
    c.drawCentredString(width / 2, height - 375, f"Issued: {issued_at.strftime('%B %d, %Y')}")
    
    c.save()
    buffer.seek(0)
    
    return buffer


logger.info("Certificate tasks module loaded")
