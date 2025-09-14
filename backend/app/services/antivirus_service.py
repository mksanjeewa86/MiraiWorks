import logging
import socket
import struct
from datetime import datetime
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.attachment import Attachment
from app.services.storage_service import get_storage_service
from app.utils.constants import VirusStatus

logger = logging.getLogger(__name__)


class AntivirusService:
    """ClamAV antivirus scanning service."""

    def __init__(self):
        self.clamav_host = settings.clamav_host
        self.clamav_port = settings.clamav_port
        self.timeout = 30  # 30 seconds timeout

    async def scan_file_by_s3_key(self, s3_key: str) -> tuple[VirusStatus, str]:
        """
        Scan file stored in S3 by downloading and scanning.
        Returns (status, scan_result_message).
        """
        try:
            # Download file from S3
            file_data = await self._download_file_from_s3(s3_key)
            if not file_data:
                return VirusStatus.ERROR, "Failed to download file from S3"

            # Scan the file data
            return await self._scan_data(file_data)

        except Exception as e:
            logger.error(f"File scan failed for {s3_key}: {e}")
            return VirusStatus.ERROR, f"Scan error: {str(e)}"

    async def _download_file_from_s3(self, s3_key: str) -> Optional[bytes]:
        """Download file data from S3."""
        try:
            # Get presigned URL and download
            url = get_storage_service().get_presigned_url(s3_key)

            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                if response.status_code == 200:
                    return response.content
                else:
                    logger.error(
                        f"Failed to download file from S3: {response.status_code}"
                    )
                    return None

        except Exception as e:
            logger.error(f"S3 download error: {e}")
            return None

    async def _scan_data(self, data: bytes) -> tuple[VirusStatus, str]:
        """Scan binary data using ClamAV."""
        try:
            # Connect to ClamAV daemon
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect((self.clamav_host, self.clamav_port))

            try:
                # Send INSTREAM command
                sock.send(b"zINSTREAM\0")

                # Send file data in chunks
                chunk_size = 1024
                for i in range(0, len(data), chunk_size):
                    chunk = data[i : i + chunk_size]
                    # Send chunk size (4 bytes, network byte order) + chunk
                    sock.send(struct.pack(">L", len(chunk)) + chunk)

                # Send 0-length chunk to indicate end
                sock.send(struct.pack(">L", 0))

                # Receive response
                response = sock.recv(1024).decode("utf-8").strip()

                # Parse response
                if "FOUND" in response:
                    virus_name = response.split(":")[1].strip()
                    return VirusStatus.INFECTED, f"Virus detected: {virus_name}"
                elif "OK" in response:
                    return VirusStatus.CLEAN, "File is clean"
                else:
                    return VirusStatus.ERROR, f"Unexpected response: {response}"

            finally:
                sock.close()

        except socket.timeout:
            return VirusStatus.ERROR, "Scan timeout"
        except ConnectionRefusedError:
            logger.error("Cannot connect to ClamAV daemon")
            return VirusStatus.ERROR, "Antivirus service unavailable"
        except Exception as e:
            logger.error(f"ClamAV scan error: {e}")
            return VirusStatus.ERROR, f"Scan failed: {str(e)}"

    async def ping_clamav(self) -> bool:
        """Test connection to ClamAV daemon."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((self.clamav_host, self.clamav_port))

            try:
                sock.send(b"zPING\0")
                response = sock.recv(1024).decode("utf-8").strip()
                return "PONG" in response
            finally:
                sock.close()

        except Exception as e:
            logger.error(f"ClamAV ping failed: {e}")
            return False

    async def scan_attachment(self, db: AsyncSession, attachment_id: int) -> bool:
        """
        Scan attachment and update its virus status.
        Returns True if scan completed successfully (regardless of result).
        """
        try:
            # Get attachment
            result = await db.execute(
                select(Attachment).where(Attachment.id == attachment_id)
            )
            attachment = result.scalar_one_or_none()

            if not attachment:
                logger.error(f"Attachment {attachment_id} not found")
                return False

            # Skip if already scanned
            if attachment.virus_status in [
                VirusStatus.CLEAN.value,
                VirusStatus.INFECTED.value,
            ]:
                logger.info(
                    f"Attachment {attachment_id} already scanned: {attachment.virus_status}"
                )
                return True

            # Scan the file
            status, result_message = await self.scan_file_by_s3_key(attachment.s3_key)

            # Update attachment
            await db.execute(
                update(Attachment)
                .where(Attachment.id == attachment_id)
                .values(
                    virus_status=status.value,
                    virus_scan_result=result_message,
                    scanned_at=datetime.utcnow(),
                    is_available=(status == VirusStatus.CLEAN),
                )
            )

            await db.commit()

            logger.info(f"Attachment {attachment_id} scan completed: {status.value}")

            # If infected, log security event
            if status == VirusStatus.INFECTED:
                logger.warning(
                    f"SECURITY: Infected file detected - Attachment ID: {attachment_id}, "
                    f"Owner: {attachment.owner_id}, Result: {result_message}"
                )

                # TODO: Create security notification for admins
                # TODO: Consider quarantining the file

            return True

        except Exception as e:
            logger.error(f"Attachment scan failed for {attachment_id}: {e}")

            # Mark as error
            try:
                await db.execute(
                    update(Attachment)
                    .where(Attachment.id == attachment_id)
                    .values(
                        virus_status=VirusStatus.ERROR.value,
                        virus_scan_result=f"Scan error: {str(e)}",
                        scanned_at=datetime.utcnow(),
                        is_available=False,
                    )
                )
                await db.commit()
            except Exception as update_error:
                logger.error(f"Failed to update attachment status: {update_error}")

            return False

    async def bulk_scan_pending_files(self, db: AsyncSession, limit: int = 10) -> int:
        """
        Scan pending files in batch.
        Returns number of files scanned.
        """
        try:
            # Get pending attachments
            result = await db.execute(
                select(Attachment.id)
                .where(Attachment.virus_status == VirusStatus.PENDING.value)
                .limit(limit)
            )

            attachment_ids = result.scalars().all()
            scanned_count = 0

            for attachment_id in attachment_ids:
                if await self.scan_attachment(db, attachment_id):
                    scanned_count += 1

                # Small delay between scans to avoid overwhelming ClamAV
                import asyncio

                await asyncio.sleep(0.1)

            return scanned_count

        except Exception as e:
            logger.error(f"Bulk scan failed: {e}")
            return 0

    def get_scan_stats(self) -> dict:
        """Get scanning statistics (for monitoring)."""
        return {
            "clamav_host": self.clamav_host,
            "clamav_port": self.clamav_port,
            "timeout": self.timeout,
            "service_available": False,  # Will be updated by health check
        }


# Global instance
antivirus_service = AntivirusService()
