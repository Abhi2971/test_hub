"""
PDF tasks for ExamSaaS platform.
Celery tasks for PDF processing and AI question generation.
"""
import logging
from datetime import datetime, timezone
from typing import Dict, Any

logger = logging.getLogger(__name__)

try:
    from celery import Task
    
    class PDFTask(Task):
        """Base task class for PDF operations."""
        max_retries = 2
        default_retry_delay = 60
        acks_late = True
        reject_on_worker_lost = True
        
        def on_failure(self, exc, task_id, args, kwargs, einfo):
            logger.error(f"PDF task {task_id} failed: {exc}")
            super().on_failure(exc, task_id, args, kwargs, einfo)
    
    def _celery_task(func):
        """Decorator to make a function a Celery task."""
        from app.extensions import celery
        return celery.task(
            bind=True,
            max_retries=2,
            default_retry_delay=60,
            acks_late=True,
            reject_on_worker_lost=True,
        )(func)

    @_celery_task
    def process_pdf_with_groq_task(self, pdf_upload_id: str) -> Dict[str, Any]:
        """
        Process PDF: extract text, chunk, generate questions with AI.
        
        Args:
            pdf_upload_id: PDFUpload document ID
        
        Returns:
            Processing result
        """
        from app.models import PDFUpload, Question, QuestionOption
        from app.services.cloudinary_service import download_file
        from app.services.ai_service import generate_questions_from_text, AIServiceError, ParseError
        
        try:
            pdf_upload = PDFUpload.objects(id=pdf_upload_id).first()
            if not pdf_upload:
                logger.error(f"PDFUpload not found: {pdf_upload_id}")
                return {"status": "failed", "error": "PDF not found"}
            
            pdf_upload.processing_status = "extracting"
            pdf_upload.save()
            
            file_bytes = download_file(pdf_upload.cloudinary_public_id, resource_type="raw")
            if not file_bytes:
                pdf_upload.processing_status = "failed"
                pdf_upload.processing_error = "Failed to download PDF from Cloudinary"
                pdf_upload.save()
                return {"status": "failed", "error": "Download failed"}
            
            full_text = ""
            page_count = 0
            
            try:
                import fitz
                doc = fitz.open(stream=file_bytes, filetype="pdf")
                page_count = len(doc)
                
                text_parts = []
                for page in doc:
                    text = page.get_text()
                    if text.strip():
                        text_parts.append(text)
                
                full_text = "\n\n".join(text_parts)
                doc.close()
            
            except ImportError:
                logger.warning("PyMuPDF not available, trying PyPDF2")
                try:
                    import PyPDF2
                    reader = PyPDF2.PdfReader(file_bytes)
                    page_count = len(reader.pages)
                    
                    text_parts = []
                    for page in reader.pages:
                        text = page.extract_text()
                        if text:
                            text_parts.append(text)
                    
                    full_text = "\n\n".join(text_parts)
                except ImportError:
                    pdf_upload.processing_status = "failed"
                    pdf_upload.processing_error = "No PDF library available"
                    pdf_upload.save()
                    return {"status": "failed", "error": "PDF library not available"}
            
            if not full_text.strip():
                pdf_upload.processing_status = "failed"
                pdf_upload.processing_error = "No text found in PDF (scanned document)"
                pdf_upload.save()
                return {"status": "failed", "error": "No extractable text"}
            
            pdf_upload.text_extracted = True
            pdf_upload.page_count = page_count
            pdf_upload.save()
            
            pdf_upload.processing_status = "chunking"
            pdf_upload.save()
            
            chunks = _chunk_text(full_text, chunk_size=2000, overlap=100)
            
            pdf_upload.total_chunks = len(chunks)
            pdf_upload.save()
            
            pdf_upload.processing_status = "generating"
            pdf_upload.save()
            
            questions_created = 0
            chunks_processed = 0
            
            for i, chunk in enumerate(chunks):
                n_questions = min(5, max(2, len(chunk.split()) // 100))
                
                try:
                    questions = generate_questions_from_text(
                        chunk,
                        n_questions=n_questions,
                        difficulty="medium",
                        topic=pdf_upload.topic or "General",
                    )
                    
                    for q_data in questions:
                        options = []
                        correct_idx = 0
                        
                        for j, opt_text in enumerate(q_data.get("options", [])):
                            option_id = f"opt_{j}"
                            clean_text = opt_text
                            for prefix in [f"{chr(65+k)}. " for k in range(10)]:
                                if opt_text.startswith(prefix):
                                    clean_text = opt_text[len(prefix):]
                                    break
                            
                            options.append(QuestionOption(
                                option_id=option_id,
                                text=clean_text,
                            ))
                            
                            correct_answer = q_data.get("correct_answer", "").upper()
                            if correct_answer == chr(65 + j) or correct_answer == chr(97 + j):
                                correct_idx = j
                        
                        correct_option_id = f"opt_{correct_idx}"
                        
                        question = Question(
                            text=q_data["question"],
                            question_type="mcq",
                            options=options,
                            correct_option_id=correct_option_id,
                            explanation=q_data.get("explanation", ""),
                            difficulty=q_data.get("difficulty", "medium"),
                            topic=q_data.get("topic", pdf_upload.topic or "General"),
                            source="pdf",
                            pdf_upload=pdf_upload,
                            is_reviewed=False,
                            is_approved=False,
                            created_by=pdf_upload.uploaded_by,
                            institute=pdf_upload.institute,
                        )
                        question.save()
                        questions_created += 1
                    
                    chunks_processed += 1
                    pdf_upload.chunks_processed = chunks_processed
                    pdf_upload.questions_generated = questions_created
                    pdf_upload.save()
                
                except (AIServiceError, ParseError) as e:
                    logger.warning(f"Failed to generate questions for chunk {i}: {e}")
                    chunks_processed += 1
                    continue
            
            pdf_upload.processing_status = "reviewing"
            pdf_upload.save()
            
            logger.info(f"PDF processing completed: {pdf_upload_id} - {questions_created} questions created")
            
            return {
                "status": "completed",
                "questions_created": questions_created,
                "chunks_processed": chunks_processed,
            }
        
        except Exception as exc:
            logger.exception(f"process_pdf_with_groq_task failed: {exc}")
            
            try:
                from app.models import PDFUpload
                pdf_upload = PDFUpload.objects(id=pdf_upload_id).first()
                if pdf_upload:
                    pdf_upload.processing_status = "failed"
                    pdf_upload.processing_error = str(exc)
                    pdf_upload.save()
            except Exception:
                pass
            
            if self.request.retries < self.max_retries:
                raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
            
            return {"status": "failed", "error": str(exc)}

except ImportError:
    logger.warning("Celery not available - PDF task decorators not applied")
    
    def process_pdf_with_groq_task(pdf_upload_id: str) -> Dict[str, Any]:
        """Fallback when Celery not available."""
        logger.warning("process_pdf_with_groq_task called without Celery")
        return {"status": "failed", "error": "Celery not available"}


def _chunk_text(text: str, chunk_size: int = 2000, overlap: int = 100) -> list:
    """
    Split text into chunks with overlap.
    
    Args:
        text: Full text to chunk
        chunk_size: Target chunk size in tokens (approx)
        overlap: Overlap between chunks
    
    Returns:
        List of text chunks
    """
    words = text.split()
    chunks = []
    
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunks.append(" ".join(chunk_words))
        
        start = end - overlap
        if start >= len(words):
            break
    
    return chunks


logger.info("PDF tasks module loaded")
