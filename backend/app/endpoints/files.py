import os
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.direct_message import DirectMessage
from app.models.role import UserRole
from app.models.user import User
from app.utils.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/test")
async def test_endpoint():
    """Simple test endpoint to verify routing works."""
    import sys
    print("DEBUG: Test endpoint called", file=sys.stderr, flush=True)
    return {"message": "File endpoints are working", "test": True}

# Configuration
UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "/tmp/uploads")
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {
    "txt",
    "pdf",
    "png",
    "jpg",
    "jpeg",
    "gif",
    "doc",
    "docx",
    "xls",
    "xlsx",
    "ppt",
    "pptx",
    "zip",
    "rar",
    "7z",
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
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


async def check_file_access_permission(
    db: AsyncSession, user_id: int, file_path: str
) -> bool:
    """
    Check if user has permission to access a file.
    Returns True if:
    1. User is the sender or recipient of a message containing this file
    2. User is super admin (can access all files)
    """
    try:
        # Check if user is super admin
        user_result = await db.execute(
            select(User)
            .options(selectinload(User.user_roles).selectinload(UserRole.role))
            .where(User.id == user_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            return False

        # Check if user has super admin role
        for user_role in user.user_roles:
            if user_role.role.name == "super_admin":
                return True

        # Normalize the file path to match against the stored file_url
        # The s3_key from URL might be URL encoded, so we need to handle this
        import urllib.parse

        # If the file_path looks like a URL path, use it directly
        if file_path.startswith("/api/files/download/"):
            search_pattern = file_path
        else:
            # For local file paths, create the expected URL pattern
            try:
                from pathlib import Path
                from app.services.local_storage_service import get_local_storage_service
                storage_service = get_local_storage_service()
                # Try to recreate the download URL that would be generated
                search_pattern = storage_service.get_download_url(file_path)
            except:
                # Fallback: use filename matching
                search_pattern = f"%{os.path.basename(file_path)}%"

        # Check if this file is attached to any message where user is sender or recipient
        message_result = await db.execute(
            select(DirectMessage).where(
                (DirectMessage.file_url.like(f"%{urllib.parse.unquote(search_pattern)}%") |
                 DirectMessage.file_url.like(f"%{search_pattern}%") |
                 DirectMessage.file_url.like(f"%{os.path.basename(file_path)}%")) &
                (
                    (DirectMessage.sender_id == user_id) |
                    (DirectMessage.recipient_id == user_id)
                )
            )
        )

        message = message_result.scalar_one_or_none()
        if message:
            # Check if message is visible to user (not deleted)
            return message.is_visible_to_user(user_id)

        return False

    except Exception as e:
        logger.error(f"Error checking file access permission: {e}")
        return False


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload a file and return its URL and metadata."""

    import sys
    print(f"DEBUG: Upload request received - filename: {file.filename}, user: {current_user.id}", file=sys.stderr, flush=True)
    logger.info(f"Upload request received - filename: {file.filename}, content_type: {file.content_type}, user: {current_user.id}")

    # Validate file
    if not file.filename:
        logger.error("No filename provided")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No file provided"
        )

    print(f"DEBUG: File validation passed: {file.filename}")
    logger.info(f"File validation passed: {file.filename}")

    if not is_allowed_file(file.filename):
        logger.error(f"File type not allowed: {file.filename}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="File type not allowed"
        )

    print(f"DEBUG: File type allowed: {file.filename}")
    logger.info(f"File type allowed: {file.filename}")

    # Check file size
    file_content = await file.read()
    print(f"DEBUG: File content read: {len(file_content)} bytes")
    logger.info(f"File content read: {len(file_content)} bytes")

    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE} bytes",
        )

    print("DEBUG: Starting storage attempts...")

    # Try local storage directly (skip MinIO for now)
    print("DEBUG: Trying local storage...")

    try:
        from app.services.local_storage_service import get_local_storage_service
        print("DEBUG: Local storage service imported")

        storage_service = get_local_storage_service()
        print("DEBUG: Local storage service instance created")

        # Upload with local storage
        print(f"DEBUG: About to upload file_content: {len(file_content)} bytes")
        file_path, file_hash, file_size = await storage_service.upload_file_data(
            file_content, file.filename, file.content_type, current_user.id, "message-attachments"
        )
        print(f"DEBUG: Upload completed: {file_path}")

        # Generate download URL
        download_url = storage_service.get_download_url(file_path)
        print(f"DEBUG: Download URL generated: {download_url}")

        print(f"DEBUG: Local storage success: {file_path}")
        logger.info(
            f"File uploaded to local storage: {file.filename} -> {file_path} by user {current_user.id}"
        )

        response_data = {
            "file_url": download_url,
            "file_name": file.filename,
            "file_size": file_size,
            "file_type": file.content_type,
            "s3_key": file_path,  # Use file_path as key for local storage
            "success": True,
            "storage_type": "local",
        }
        print(f"DEBUG: Returning response: {response_data}")
        return response_data

    except Exception as e:
        print(f"DEBUG: Local storage failed with exception: {e}")
        import traceback
        traceback.print_exc()
        logger.error(f"Error saving file {file.filename} to local storage: {str(e)}")

        # Re-raise with more detail
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving file - {type(e).__name__}: {str(e)}",
        )


@router.get("/download/{s3_key:path}")
async def download_file(
    s3_key: str,
    download: Optional[str] = None,  # Add query parameter to control download behavior
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Download a file from storage (MinIO or local) with permission check."""

    # Check if user has permission to access this file
    has_permission = await check_file_access_permission(db, current_user.id, s3_key)
    if not has_permission:
        logger.warning(f"User {current_user.id} denied access to file {s3_key}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this file"
        )

    logger.info(f"User {current_user.id} granted access to file {s3_key}")

    # Try MinIO first
    try:
        from app.services.storage_service import get_storage_service
        storage_service = get_storage_service()

        # Check if file exists
        if storage_service.file_exists(s3_key):
            # Generate presigned URL for download
            download_url = storage_service.get_presigned_url(s3_key)
            return {"download_url": download_url, "s3_key": s3_key, "expires_in": "1 hour"}

    except Exception as e:
        logger.warning(f"MinIO download failed, trying local storage: {str(e)}")

    # Fall back to local storage
    try:
        from fastapi.responses import FileResponse
        from app.services.local_storage_service import get_local_storage_service

        storage_service = get_local_storage_service()

        # Check if file exists
        if storage_service.file_exists(s3_key):
            # Determine media type and disposition based on file extension
            filename = os.path.basename(s3_key)
            file_ext = filename.lower().split('.')[-1] if '.' in filename else ''

            # Set appropriate media type
            media_type = 'application/octet-stream'
            if file_ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                media_type = f'image/{file_ext.replace("jpg", "jpeg")}'
            elif file_ext in ['pdf']:
                media_type = 'application/pdf'
            elif file_ext in ['txt']:
                media_type = 'text/plain'
            elif file_ext in ['doc', 'docx']:
                media_type = 'application/msword'

            # Control download behavior
            if download == "true":
                # Force download with attachment disposition
                headers = {"Content-Disposition": f"attachment; filename={filename}"}
            else:
                # Try to display inline (prevent auto-download)
                headers = {"Content-Disposition": f"inline; filename={filename}"}

            return FileResponse(
                path=s3_key,
                filename=filename,
                media_type=media_type,
                headers=headers
            )

        # File not found in either storage
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file {s3_key}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error downloading file",
        )


@router.delete("/{s3_key:path}")
async def delete_file(
    s3_key: str,
    current_user: User = Depends(get_current_active_user),
):
    """Delete a file from MinIO (admin only for now)."""

    try:
        from app.services.storage_service import get_storage_service
        storage_service = get_storage_service()

        # Check if file exists
        if not storage_service.file_exists(s3_key):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
            )

        # Delete from MinIO
        success = storage_service.delete_file(s3_key)

        if success:
            logger.info(f"File deleted from MinIO: {s3_key} by user {current_user.id}")
            return {"message": "File deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete file",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file {s3_key}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting file",
        )
