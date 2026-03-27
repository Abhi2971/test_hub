"""
Cloudinary service for ExamSaaS platform.
Handles file uploads, deletions, and signed URLs.
"""
import logging
import time
from typing import Dict, Any, Optional

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
            logger.warning("Redis not available for cloudinary service")
            return None
    return REDIS_CLIENT


def _get_config(key: str, default: Any = None) -> Any:
    """Get configuration value."""
    try:
        from flask import current_app
        return current_app.config.get(key, default)
    except RuntimeError:
        return default


class ValidationError(Exception):
    """Validation error for file uploads."""
    pass


def upload_file(
    file_bytes: bytes,
    public_id: str,
    folder: str,
    resource_type: str = "auto",
    **kwargs
) -> Dict[str, Any]:
    """
    Upload file to Cloudinary.
    
    Args:
        file_bytes: File content as bytes
        public_id: Public ID for the file
        folder: Folder path in Cloudinary
        resource_type: Type of resource (auto, image, video, raw)
        **kwargs: Additional Cloudinary upload options
    
    Returns:
        dict with url, public_id, bytes
    """
    try:
        import cloudinary
        import cloudinary.uploader
        
        cloud_name = _get_config("CLOUDINARY_CLOUD_NAME")
        api_key = _get_config("CLOUDINARY_API_KEY")
        api_secret = _get_config("CLOUDINARY_API_SECRET")
        
        if not all([cloud_name, api_key, api_secret]):
            logger.warning("Cloudinary not configured, using mock upload")
            return {
                "url": f"https://res.cloudinary.com/{cloud_name}/{resource_type}/{folder}/{public_id}",
                "public_id": f"{folder}/{public_id}",
                "bytes": len(file_bytes),
            }
        
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
        )
        
        full_public_id = f"{folder}/{public_id}"
        
        result = cloudinary.uploader.upload(
            file_bytes,
            public_id=public_id,
            folder=folder,
            resource_type=resource_type,
            overwrite=False,
            **kwargs
        )
        
        return {
            "url": result["secure_url"],
            "public_id": result["public_id"],
            "bytes": result["bytes"],
        }
    
    except Exception as e:
        logger.error(f"Cloudinary upload failed: {e}")
        raise


def get_signed_url(public_id: str, expires_in: int = 3600) -> str:
    """
    Generate signed URL expiring in N seconds.
    
    Args:
        public_id: Cloudinary public ID
        expires_in: Seconds until expiration
    
    Returns:
        Signed URL string
    """
    try:
        import cloudinary
        
        cloud_name = _get_config("CLOUDINARY_CLOUD_NAME")
        api_key = _get_config("CLOUDINARY_API_KEY")
        api_secret = _get_config("CLOUDINARY_API_SECRET")
        
        if not all([cloud_name, api_key, api_secret]):
            logger.warning("Cloudinary not configured, using mock URL")
            return f"https://res.cloudinary.com/{cloud_name}/raw/upload/{public_id}?sign=true"
        
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
        )
        
        expires_at = int(time.time()) + expires_in
        
        url, _ = cloudinary.utils.cloudinary_url(
            public_id,
            sign_url=True,
            expires_at=expires_at,
        )
        
        return url
    
    except Exception as e:
        logger.error(f"Cloudinary signed URL failed: {e}")
        raise


def delete_file(public_id: str, resource_type: str = "auto") -> bool:
    """
    Delete file from Cloudinary.
    
    Args:
        public_id: Cloudinary public ID
        resource_type: Type of resource
    
    Returns:
        True if deleted successfully
    """
    try:
        import cloudinary
        import cloudinary.uploader
        
        cloud_name = _get_config("CLOUDINARY_CLOUD_NAME")
        api_key = _get_config("CLOUDINARY_API_KEY")
        api_secret = _get_config("CLOUDINARY_API_SECRET")
        
        if not all([cloud_name, api_key, api_secret]):
            logger.warning("Cloudinary not configured, using mock delete")
            return True
        
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
        )
        
        result = cloudinary.uploader.destroy(public_id, resource_type=resource_type)
        
        return result.get("result") == "ok"
    
    except Exception as e:
        logger.error(f"Cloudinary delete failed: {e}")
        return False


def validate_upload(
    file_bytes: bytes,
    allowed_types: list,
    max_size_bytes: int
) -> None:
    """
    Validate file upload.
    
    Args:
        file_bytes: File content as bytes
        allowed_types: List of allowed MIME types
        max_size_bytes: Maximum file size in bytes
    
    Raises:
        ValidationError: If validation fails
    """
    if len(file_bytes) > max_size_bytes:
        max_mb = max_size_bytes // (1024 * 1024)
        raise ValidationError(f"File too large. Max {max_mb}MB")
    
    try:
        import magic
        
        mime = magic.from_buffer(file_bytes[:2048], mime=True)
        
        if mime not in allowed_types:
            raise ValidationError(f"Invalid file type: {mime}. Allowed: {', '.join(allowed_types)}")
    
    except ImportError:
        logger.warning("python-magic not available, skipping MIME validation")


def download_file(public_id: str, resource_type: str = "raw") -> Optional[bytes]:
    """
    Download file from Cloudinary.
    
    Args:
        public_id: Cloudinary public ID
        resource_type: Type of resource
    
    Returns:
        File content as bytes or None
    """
    try:
        import cloudinary.api
        import cloudinary
        
        cloud_name = _get_config("CLOUDINARY_CLOUD_NAME")
        api_key = _get_config("CLOUDINARY_API_KEY")
        api_secret = _get_config("CLOUDINARY_API_SECRET")
        
        if not all([cloud_name, api_key, api_secret]):
            logger.warning("Cloudinary not configured")
            return None
        
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
        )
        
        result = cloudinary.api.resource(public_id, type=resource_type)
        
        if result.get("secure_url"):
            import requests
            response = requests.get(result["secure_url"])
            return response.content
        
        return None
    
    except Exception as e:
        logger.error(f"Cloudinary download failed: {e}")
        return None


def upload_pdf(
    file_bytes: bytes,
    public_id: str,
    institute_id: str,
) -> Dict[str, Any]:
    """
    Upload PDF to Cloudinary.
    
    Args:
        file_bytes: PDF content as bytes
        public_id: Public ID for the file
        institute_id: Institute ID for folder path
    
    Returns:
        Upload result with url, public_id
    """
    validate_upload(
        file_bytes,
        ["application/pdf"],
        30 * 1024 * 1024,
    )
    
    return upload_file(
        file_bytes,
        public_id,
        f"pdfs/{institute_id}",
        resource_type="raw",
    )


def upload_certificate(
    file_bytes: bytes,
    certificate_code: str,
    institute_id: str,
) -> Dict[str, Any]:
    """
    Upload certificate PDF to Cloudinary.
    
    Args:
        file_bytes: PDF content as bytes
        certificate_code: Certificate code
        institute_id: Institute ID for folder path
    
    Returns:
        Upload result with url, public_id
    """
    return upload_file(
        file_bytes,
        certificate_code,
        f"certificates/{institute_id}",
        resource_type="raw",
    )


logger.info("Cloudinary service loaded")
