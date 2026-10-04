import logging
import os
import uuid
from typing import Optional
import cloudinary
import cloudinary.uploader
from fastapi import HTTPException, status
from app.core.config import settings

logger = logging.getLogger(__name__)

# Configure Cloudinary if credentials provided
if settings.CLOUDINARY_CLOUD_NAME and settings.CLOUDINARY_API_KEY and settings.CLOUDINARY_API_SECRET:
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True,
    )
    is_cloudinary_configured = True
else:
    is_cloudinary_configured = False
    logger.info("Cloudinary credentials not yet configured in .env. Fallback local uploads enabled.")


def save_local_upload(file_bytes: bytes, filename: str) -> str:
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    static_dir = os.path.join(base_dir, "static", "uploads")
    os.makedirs(static_dir, exist_ok=True)

    ext = filename.split(".")[-1] if "." in filename else "jpg"
    unique_name = f"proj_{uuid.uuid4().hex[:12]}.{ext}"
    target_path = os.path.join(static_dir, unique_name)

    with open(target_path, "wb") as f:
        f.write(file_bytes)

    return f"http://127.0.0.1:8000/static/uploads/{unique_name}"


def upload_project_image(file_bytes: bytes, filename: str, content_type: str) -> str:
    """
    Upload an image to Cloudinary (if operational) or seamlessly to local static storage.
    Returns the fully accessible HTTPS/HTTP URL ready for database storage.
    """
    # 1. Validation
    allowed_types = ["image/jpeg", "image/png", "image/webp", "image/gif", "image/jpg"]
    if content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported image format: {content_type}. Allowed: JPEG, PNG, WEBP, GIF.",
        )

    # 10 MB max size
    if len(file_bytes) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds maximum allowed limit (10MB).",
        )

    # 2. Upload to Cloudinary if configured
    if is_cloudinary_configured:
        try:
            unique_filename = f"proj_{uuid.uuid4().hex[:10]}"
            upload_result = cloudinary.uploader.upload(
                file_bytes,
                folder="portfolio_projects",
                public_id=unique_filename,
                resource_type="image",
                overwrite=True,
            )
            secure_url = upload_result.get("secure_url")
            if secure_url:
                return secure_url
        except Exception as exc:
            logger.warning("Cloudinary upload failed (%s). Falling back seamlessly to local static storage.", exc)

    # 3. Direct local static upload fallback (Guaranteed to succeed)
    try:
        return save_local_upload(file_bytes, filename)
    except Exception as exc:
        logger.error("Local upload fallback failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image upload failed: {str(exc)}",
        )
