import os
from pathlib import Path, PurePosixPath
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
from app.utils.permissions import is_super_admin

router = APIRouter()
logger = get_logger(__name__)


@router.get("/test")
async def test_endpoint():
    """Simple test endpoint to verify routing works."""
    import sys
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




def _normalize_storage_key(raw_key: str) -> str:
    """Validate and normalize inbound storage keys."""
    key = raw_key.strip().replace('\\', '/')
    if not key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid file key'
        )
    if key.startswith('/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid file key'
        )

    posix_path = PurePosixPath(key)
    if any(part == '..' for part in posix_path.parts):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid file key'
        )

    return str(posix_path)


def _resolve_local_path(base_path: Path, key: str) -> Path:
    """Resolve file key against base path and block path traversal."""
    base = Path(base_path).resolve()
    candidate = (base / Path(key)).resolve()
    if not candidate.is_relative_to(base):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You do not have permission to access this file',
        )
    return candidate


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
        from sqlalchemy import or_

        # Create search patterns to handle different scenarios
        patterns_to_try = []

        # Pattern 1: If file_path looks like a URL path, use it directly
        if file_path.startswith("/api/files/download/"):
            patterns_to_try.append(file_path)
            # Also try without the /api/files/download/ prefix
            path_only = file_path.replace("/api/files/download/", "")
            patterns_to_try.append(path_only)
        else:
            # Pattern 2: Create the expected URL pattern from file path
            expected_url = f"/api/files/download/{file_path}"
            patterns_to_try.append(expected_url)
            # Also try the path only
            patterns_to_try.append(file_path)

        # Pattern 3: Always include filename-only matching as fallback
        filename = os.path.basename(file_path)
        patterns_to_try.append(filename)

        # Build OR conditions for pattern matching
        file_conditions = []
        for pattern in patterns_to_try:
            # Exact match
            file_conditions.append(DirectMessage.file_url == pattern)
            # LIKE match (contains the pattern)
            file_conditions.append(DirectMessage.file_url.like(f"%{pattern}%"))

            # URL decoded version if different
            try:
                decoded = urllib.parse.unquote(pattern)
                if decoded != pattern:
                    file_conditions.append(DirectMessage.file_url.like(f"%{decoded}%"))
            except:
                pass

        # Check if this file is attached to any message where user is sender or recipient
        message_result = await db.execute(
            select(DirectMessage).where(
                or_(*file_conditions) &
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
    logger.info(f"Upload request received - filename: {file.filename}, content_type: {file.content_type}, user: {current_user.id}")

    # Validate file
    if not file.filename:
        logger.error("No filename provided")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No file provided"
        )

    logger.info(f"File validation passed: {file.filename}")

    if not is_allowed_file(file.filename):
        logger.error(f"File type not allowed: {file.filename}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="File type not allowed"
        )

    logger.info(f"File type allowed: {file.filename}")

    # Check file size
    file_content = await file.read()
    logger.info(f"File content read: {len(file_content)} bytes")

    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE} bytes",
        )


    # Try local storage directly (skip MinIO for now)

    try:
        from app.services.local_storage_service import get_local_storage_service

        storage_service = get_local_storage_service()

        # Upload with local storage
        file_path, file_hash, file_size = await storage_service.upload_file_data(
            file_content, file.filename, file.content_type, current_user.id, "message-attachments"
        )

        # Generate download URL
        download_url = storage_service.get_download_url(file_path)

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
        return response_data

    except Exception as e:
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

    # Validate and normalise the requested key
    safe_key = _normalize_storage_key(s3_key)

    # Check if user has permission to access this file
    has_permission = await check_file_access_permission(db, current_user.id, safe_key)
    if not has_permission:
        logger.warning(f"User {current_user.id} denied access to file {safe_key}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this file"
        )

    logger.info(f"User {current_user.id} granted access to file {safe_key}")

    # Try MinIO first
    try:
        from app.services.storage_service import get_storage_service
        storage_service = get_storage_service()

        # Check if file exists
        if storage_service.file_exists(safe_key):
            # Generate presigned URL for download
            download_url = storage_service.get_presigned_url(safe_key)
            return {"download_url": download_url, "s3_key": safe_key, "expires_in": "1 hour"}

    except Exception as e:
        logger.warning(f"MinIO download failed, trying local storage: {str(e)}")

    # Fall back to local storage
    try:
        from fastapi.responses import FileResponse
        from app.services.local_storage_service import get_local_storage_service

        storage_service = get_local_storage_service()

        # Resolve the full path to the file
        # s3_key comes in as: "message-attachments/8/2025/09/file.pdf"
        # We need to make it: "uploads/message-attachments/8/2025/09/file.pdf"
        full_file_path = _resolve_local_path(storage_service.base_path, safe_key)

        # Check if file exists
        if full_file_path.exists():
            # Determine media type and disposition based on file extension
            filename = os.path.basename(safe_key)
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
                path=str(full_file_path),
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
        logger.error(f"Error downloading file {safe_key}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error downloading file",
        )



@router.delete("/{s3_key:path}")
async def delete_file(
    s3_key: str,
    current_user: User = Depends(get_current_active_user),
):
    """Delete a file from storage (super admin only)."""

    safe_key = _normalize_storage_key(s3_key)

    if not is_super_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Super admin privileges required to delete files',
        )

    try:
        from app.services.storage_service import get_storage_service

        storage_service = get_storage_service()

        if storage_service.file_exists(safe_key):
            success = storage_service.delete_file(safe_key)

            if success:
                logger.info(
                    f"File deleted from MinIO: {safe_key} by user {current_user.id}"
                )
                return {"message": "File deleted successfully"}

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Failed to delete file',
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file {safe_key}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Error deleting file',
        )

    # Fall back to local storage deletion
    try:
        from app.services.local_storage_service import get_local_storage_service

        local_storage = get_local_storage_service()
        local_path = _resolve_local_path(local_storage.base_path, safe_key)
        if local_path.exists():
            local_path.unlink()
            logger.info(
                f"File deleted from local storage: {safe_key} by user {current_user.id}"
            )
            return {"message": "File deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting local file {safe_key}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Error deleting file',
        )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail='File not found',
    )
