import hashlib
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

from app.utils.logging import get_logger

logger = get_logger(__name__)


class LocalStorageService:
    """Simple local file storage service for testing/development."""

    def __init__(self, base_path: str = "uploads"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        logger.info(
            f"LocalStorageService initialized with path: {self.base_path.absolute()}"
        )

    def generate_file_path(
        self, user_id: int, filename: str, folder: str = "attachments"
    ) -> str:
        """Generate a unique file path for storage."""
        now = datetime.utcnow()
        unique_id = str(uuid.uuid4())

        # Sanitize filename
        safe_filename = "".join(
            c for c in filename if c.isalnum() or c in ".-_"
        ).rstrip()
        if not safe_filename:
            safe_filename = "file"

        # Create folder structure: folder/user_id/year/month/uuid_filename
        file_path = (
            self.base_path
            / folder
            / str(user_id)
            / str(now.year)
            / f"{now.month:02d}"
            / f"{unique_id}_{safe_filename}"
        )

        return str(file_path)

    async def upload_file_data(
        self,
        file_content: bytes,
        filename: str,
        content_type: str,
        user_id: int,
        folder: str = "attachments",
    ) -> Tuple[str, str, int]:
        """Upload file data and return (file_path, file_hash, file_size)."""

        file_path = self.generate_file_path(user_id, filename, folder)

        # Create directory
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        # Write file
        with open(file_path, "wb") as f:
            f.write(file_content)

        # Calculate hash
        file_hash = hashlib.md5(file_content).hexdigest()
        file_size = len(file_content)

        logger.info(f"File uploaded to local storage: {filename} -> {file_path}")

        return file_path, file_hash, file_size

    def get_download_url(self, file_path: str) -> str:
        """Generate a download URL for the file."""
        # For local storage, we'll use the API endpoint
        # Convert absolute path to relative path from base
        try:
            rel_path = Path(file_path).relative_to(self.base_path)
            # URL encode the path
            import urllib.parse

            encoded_path = urllib.parse.quote(str(rel_path))
            return f"/api/files/download/{encoded_path}"
        except ValueError:
            # If file is not under base_path, use absolute path
            encoded_path = urllib.parse.quote(file_path)
            return f"/api/files/download/{encoded_path}"

    def file_exists(self, file_path: str) -> bool:
        """Check if file exists."""
        return Path(file_path).exists()

    def get_file_content(self, file_path: str) -> Optional[bytes]:
        """Get file content."""
        try:
            with open(file_path, "rb") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            return None

    def delete_file(self, file_path: str) -> bool:
        """Delete file."""
        try:
            Path(file_path).unlink()
            return True
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {e}")
            return False


# Global storage service instance
_storage_service = None


def get_local_storage_service() -> LocalStorageService:
    """Get the global local storage service instance."""
    global _storage_service
    if _storage_service is None:
        _storage_service = LocalStorageService()
    return _storage_service
