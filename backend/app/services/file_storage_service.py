import contextlib
import logging
import mimetypes
import os
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import HTTPException, UploadFile

from app.config import settings

logger = logging.getLogger(__name__)


class FileStorageService:
    """Service for handling file storage operations with 25MB limit."""

    MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB in bytes
    UPLOAD_DIR = "uploads/todo_attachments"

    def __init__(self):
        self.base_upload_dir = Path(
            settings.upload_directory
            if hasattr(settings, "upload_directory")
            else self.UPLOAD_DIR
        )
        self.ensure_upload_directory()

    def ensure_upload_directory(self) -> None:
        """Ensure the upload directory exists."""
        try:
            self.base_upload_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Upload directory ensured: {self.base_upload_dir}")
        except Exception as e:
            logger.error(f"Failed to create upload directory: {e}")
            raise HTTPException(
                status_code=500, detail="Failed to initialize file storage"
            ) from e

    def validate_file(self, file: UploadFile) -> dict:
        """Validate uploaded file against size and type constraints."""
        validation_result = {"valid": True, "errors": [], "file_info": {}}

        # Check if file is provided
        if not file or not file.filename:
            validation_result["valid"] = False
            validation_result["errors"].append("No file provided")
            return validation_result

        # Get file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning

        # Check file size (25MB limit)
        if file_size > self.MAX_FILE_SIZE:
            validation_result["valid"] = False
            validation_result["errors"].append(
                f"File size {file_size / (1024 * 1024):.2f}MB exceeds 25MB limit"
            )

        if file_size == 0:
            validation_result["valid"] = False
            validation_result["errors"].append("File is empty")

        # Detect MIME type
        mime_type, _ = mimetypes.guess_type(file.filename)
        if not mime_type:
            # Fallback to content type from upload
            mime_type = file.content_type or "application/octet-stream"

        # Get file extension
        file_extension = Path(file.filename).suffix.lower() if file.filename else ""

        validation_result["file_info"] = {
            "original_filename": file.filename,
            "file_size": file_size,
            "mime_type": mime_type,
            "file_extension": file_extension,
            "content_type": file.content_type,
        }

        return validation_result

    def generate_unique_filename(self, original_filename: str) -> tuple[str, str]:
        """Generate a unique filename for storage."""
        # Extract extension from original filename
        file_path = Path(original_filename)
        extension = file_path.suffix.lower()

        # Generate unique filename with timestamp and UUID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        stored_filename = f"{timestamp}_{unique_id}{extension}"

        # Create subdirectory based on date for organization
        date_dir = datetime.now().strftime("%Y/%m")
        full_path = self.base_upload_dir / date_dir / stored_filename

        return stored_filename, str(full_path)

    async def save_file(self, file: UploadFile) -> dict:
        """Save uploaded file to storage."""
        # Validate file first
        validation = self.validate_file(file)
        if not validation["valid"]:
            raise HTTPException(
                status_code=400,
                detail=f"File validation failed: {', '.join(validation['errors'])}",
            )

        file_info = validation["file_info"]
        stored_filename, full_path = self.generate_unique_filename(
            file_info["original_filename"]
        )

        try:
            # Ensure directory exists
            Path(full_path).parent.mkdir(parents=True, exist_ok=True)

            # Save file
            with open(full_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)

            # Verify file was saved correctly
            if not os.path.exists(full_path):
                raise Exception("File was not saved successfully")

            # Verify file size matches
            actual_size = os.path.getsize(full_path)
            if actual_size != file_info["file_size"]:
                os.remove(full_path)  # Clean up
                raise Exception(
                    f"File size mismatch: expected {file_info['file_size']}, got {actual_size}"
                )

            logger.info(f"File saved successfully: {stored_filename}")

            return {
                "stored_filename": stored_filename,
                "file_path": full_path,
                "file_size": actual_size,
                **file_info,
            }

        except Exception as e:
            logger.error(f"Failed to save file {file.filename}: {e}")
            # Clean up partial file if it exists
            if os.path.exists(full_path):
                with contextlib.suppress(Exception):
                    os.remove(full_path)
            raise HTTPException(
                status_code=500, detail=f"Failed to save file: {str(e)}"
            ) from e

    def delete_file(self, file_path: str) -> bool:
        """Delete a file from storage."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"File deleted: {file_path}")

                # Try to remove empty parent directories
                try:
                    parent_dir = Path(file_path).parent
                    if parent_dir.exists() and not any(parent_dir.iterdir()):
                        parent_dir.rmdir()
                except Exception:
                    pass  # Ignore errors when cleaning up directories

                return True
            else:
                logger.warning(f"File not found for deletion: {file_path}")
                return False
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {e}")
            return False

    def get_file_info(self, file_path: str) -> dict | None:
        """Get information about a stored file."""
        try:
            if not os.path.exists(file_path):
                return None

            stat = os.stat(file_path)
            file_path_obj = Path(file_path)

            return {
                "file_path": file_path,
                "file_size": stat.st_size,
                "file_size_mb": stat.st_size / (1024 * 1024),
                "modified_at": datetime.fromtimestamp(stat.st_mtime),
                "filename": file_path_obj.name,
                "extension": file_path_obj.suffix.lower(),
                "exists": True,
            }
        except Exception as e:
            logger.error(f"Failed to get file info for {file_path}: {e}")
            return None

    def get_file_content(self, file_path: str) -> bytes | None:
        """Read file content for download/preview."""
        try:
            if not os.path.exists(file_path):
                return None

            with open(file_path, "rb") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            return None

    def get_storage_stats(self) -> dict:
        """Get storage statistics."""
        try:
            total_files = 0
            total_size = 0

            for root, _dirs, files in os.walk(self.base_upload_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        size = os.path.getsize(file_path)
                        total_files += 1
                        total_size += size
                    except Exception:
                        continue

            return {
                "total_files": total_files,
                "total_size_bytes": total_size,
                "total_size_mb": total_size / (1024 * 1024),
                "upload_directory": str(self.base_upload_dir),
            }
        except Exception as e:
            logger.error(f"Failed to get storage stats: {e}")
            return {
                "total_files": 0,
                "total_size_bytes": 0,
                "total_size_mb": 0,
                "upload_directory": str(self.base_upload_dir),
                "error": str(e),
            }

    def cleanup_orphaned_files(self, valid_file_paths: list[str]) -> dict:
        """Clean up files that are not referenced in the database."""
        try:
            valid_paths_set = set(valid_file_paths)
            deleted_files = []
            deleted_size = 0

            for root, _dirs, files in os.walk(self.base_upload_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    if file_path not in valid_paths_set:
                        try:
                            size = os.path.getsize(file_path)
                            os.remove(file_path)
                            deleted_files.append(file_path)
                            deleted_size += size
                            logger.info(f"Deleted orphaned file: {file_path}")
                        except Exception as e:
                            logger.error(
                                f"Failed to delete orphaned file {file_path}: {e}"
                            )

            return {
                "deleted_files_count": len(deleted_files),
                "deleted_files": deleted_files,
                "freed_space_mb": deleted_size / (1024 * 1024),
            }
        except Exception as e:
            logger.error(f"Failed to cleanup orphaned files: {e}")
            return {"error": str(e)}


# Global file storage service instance
file_storage_service = FileStorageService()
