import os
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.user import User
from app.utils.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)

# Configuration
UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "/tmp/uploads")
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {
    'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 
    'xls', 'xlsx', 'ppt', 'pptx', 'zip', 'rar', '7z'
}

# Create uploads directory if it doesn't exist (only if writable)
try:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
except OSError as e:
    logger.warning(f"Could not create upload directory {UPLOAD_DIR}: {e}")
    # Use /tmp as fallback for Docker containers
    UPLOAD_DIR = "/tmp/uploads"
    os.makedirs(UPLOAD_DIR, exist_ok=True)


def is_allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload a file and return its URL and metadata."""
    
    # Validate file
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    if not is_allowed_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File type not allowed"
        )
    
    # Check file size
    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE} bytes"
        )
    
    # Use MinIO storage service
    try:
        from app.services.storage_service import storage_service
        
        # Create a temporary file-like object for upload
        file.file.seek(0)  # Reset file pointer
        
        # Upload to MinIO
        s3_key, file_hash, file_size = await storage_service.upload_file(
            file, current_user.id, "message-attachments"
        )
        
        # Generate presigned URL for download
        download_url = storage_service.get_presigned_url(s3_key)
        
        logger.info(f"File uploaded to MinIO: {file.filename} -> {s3_key} by user {current_user.id}")
        
        return {
            "file_url": download_url,
            "file_name": file.filename,
            "file_size": file_size,
            "file_type": file.content_type,
            "s3_key": s3_key,
            "success": True,
            "minio_console": "http://localhost:9001"
        }
        
    except Exception as e:
        logger.error(f"Error saving file {file.filename}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error saving file"
        )


@router.get("/download/{s3_key:path}")
async def download_file(
    s3_key: str,
    current_user: User = Depends(get_current_active_user),
):
    """Generate a presigned URL for downloading a file from MinIO."""
    
    try:
        from app.services.storage_service import storage_service
        
        # Check if file exists
        if not storage_service.file_exists(s3_key):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        # Generate presigned URL for download
        download_url = storage_service.get_presigned_url(s3_key)
        
        return {
            "download_url": download_url,
            "s3_key": s3_key,
            "expires_in": "1 hour"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating download URL for {s3_key}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating download URL"
        )


@router.delete("/{s3_key:path}")
async def delete_file(
    s3_key: str,
    current_user: User = Depends(get_current_active_user),
):
    """Delete a file from MinIO (admin only for now)."""
    
    try:
        from app.services.storage_service import storage_service
        
        # Check if file exists
        if not storage_service.file_exists(s3_key):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        # Delete from MinIO
        success = storage_service.delete_file(s3_key)
        
        if success:
            logger.info(f"File deleted from MinIO: {s3_key} by user {current_user.id}")
            return {"message": "File deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete file"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file {s3_key}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting file"
        )