import hashlib
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Optional

from fastapi import HTTPException, UploadFile, status
from minio import Minio
from minio.error import S3Error

from app.config import settings

logger = logging.getLogger(__name__)


class StorageService:
    """MinIO S3-compatible storage service."""

    def __init__(self):
        self.client = Minio(
            settings.s3_endpoint.replace("http://", "").replace("https://", ""),
            access_key=settings.s3_access_key,
            secret_key=settings.s3_secret_key,
            secure=settings.s3_endpoint.startswith("https://"),
        )
        self.bucket = settings.s3_bucket
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """Ensure the S3 bucket exists."""
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
                logger.info(f"Created S3 bucket: {self.bucket}")
        except S3Error as e:
            logger.error(f"Failed to create/check bucket: {e}")

    def generate_s3_key(
        self, user_id: int, filename: str, folder: str = "attachments"
    ) -> str:
        """Generate a unique S3 key for file storage."""
        # Create folder structure: folder/user_id/year/month/uuid_filename
        now = datetime.utcnow()
        unique_id = str(uuid.uuid4())

        # Sanitize filename
        safe_filename = "".join(
            c for c in filename if c.isalnum() or c in ".-_"
        ).rstrip()
        if not safe_filename:
            safe_filename = "file"

        s3_key = (
            f"{folder}/{user_id}/{now.year}/{now.month:02d}/{unique_id}_{safe_filename}"
        )
        return s3_key

    def calculate_file_hash(self, file_data: bytes) -> str:
        """Calculate SHA256 hash of file data."""
        return hashlib.sha256(file_data).hexdigest()

    async def upload_file_data(
        self, file_data: bytes, filename: str, content_type: str, user_id: int, folder: str = "attachments"
    ) -> tuple[str, str, int]:
        """
        Upload file data to S3 and return (s3_key, sha256_hash, file_size).
        """
        try:
            file_size = len(file_data)

            # Calculate hash
            file_hash = self.calculate_file_hash(file_data)

            # Generate S3 key
            s3_key = self.generate_s3_key(user_id, filename, folder)

            # Upload to S3
            from io import BytesIO

            self.client.put_object(
                bucket_name=self.bucket,
                object_name=s3_key,
                data=BytesIO(file_data),
                length=file_size,
                content_type=content_type,
            )

            logger.info(f"Uploaded file to S3: {s3_key}")
            return s3_key, file_hash, file_size

        except S3Error as e:
            logger.error(f"S3 upload failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="File upload failed",
            )
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="File upload failed",
            )

    async def upload_file(
        self, file: UploadFile, user_id: int, folder: str = "attachments"
    ) -> tuple[str, str, int]:
        """
        Upload file to S3 and return (s3_key, sha256_hash, file_size).
        """
        try:
            # Read file data
            file_data = await file.read()
            return await self.upload_file_data(file_data, file.filename, file.content_type, user_id, folder)

        except Exception as e:
            logger.error(f"File upload error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="File processing failed",
            )

    def get_presigned_url(
        self, s3_key: str, expires: timedelta = timedelta(hours=1), method: str = "GET"
    ) -> str:
        """Get presigned URL for file access."""
        try:
            url = self.client.presigned_url(
                method=method,
                bucket_name=self.bucket,
                object_name=s3_key,
                expires=expires,
            )
            return url
        except S3Error as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate file URL",
            )

    def get_presigned_upload_url(
        self, s3_key: str, expires: timedelta = timedelta(minutes=15)
    ) -> dict[str, Any]:
        """Get presigned URL for direct upload."""
        try:
            # Generate presigned POST URL
            policy = {
                "expiration": (datetime.utcnow() + expires).isoformat() + "Z",
                "conditions": [
                    {"bucket": self.bucket},
                    {"key": s3_key},
                    ["content-length-range", 1, 100 * 1024 * 1024],  # 1 byte to 100MB
                ],
            }

            url = self.client.presigned_url(
                method="PUT",
                bucket_name=self.bucket,
                object_name=s3_key,
                expires=expires,
            )

            return {
                "upload_url": url,
                "s3_key": s3_key,
                "expires_at": (datetime.utcnow() + expires).isoformat(),
            }

        except S3Error as e:
            logger.error(f"Failed to generate presigned upload URL: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate upload URL",
            )

    def delete_file(self, s3_key: str) -> bool:
        """Delete file from S3."""
        try:
            self.client.remove_object(self.bucket, s3_key)
            logger.info(f"Deleted file from S3: {s3_key}")
            return True
        except S3Error as e:
            logger.error(f"Failed to delete file: {e}")
            return False

    def get_file_info(self, s3_key: str) -> Optional[dict[str, Any]]:
        """Get file information from S3."""
        try:
            stat = self.client.stat_object(self.bucket, s3_key)
            return {
                "size": stat.size,
                "content_type": stat.content_type,
                "last_modified": stat.last_modified,
                "etag": stat.etag,
            }
        except S3Error as e:
            logger.error(f"Failed to get file info: {e}")
            return None

    def file_exists(self, s3_key: str) -> bool:
        """Check if file exists in S3."""
        try:
            self.client.stat_object(self.bucket, s3_key)
            return True
        except S3Error:
            return False


# Global instance
storage_service = StorageService()
