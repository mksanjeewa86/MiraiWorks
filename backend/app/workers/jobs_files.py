import asyncio
import logging

from app.database import AsyncSessionLocal
from app.services.antivirus_service import antivirus_service
from app.workers.queue import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, retry_backoff=True, retry_kwargs={"max_retries": 3})
def scan_uploaded_file(self, attachment_id: int):
    """
    Background task to scan uploaded file for viruses.
    """
    try:
        # Run async function in sync context
        result = asyncio.run(_scan_file_async(attachment_id))

        if result:
            logger.info(
                f"File scan completed successfully for attachment {attachment_id}"
            )
            return {"status": "completed", "attachment_id": attachment_id}
        else:
            logger.error(f"File scan failed for attachment {attachment_id}")
            raise Exception("File scan failed")

    except Exception as exc:
        logger.error(f"File scan task failed for attachment {attachment_id}: {exc}")

        # Retry the task
        if self.request.retries < 3:
            raise self.retry(countdown=60 * (self.request.retries + 1))

        # Final failure
        asyncio.run(_mark_scan_failed(attachment_id))
        raise


async def _scan_file_async(attachment_id: int) -> bool:
    """Async helper for file scanning."""
    async with AsyncSessionLocal() as db:
        return await antivirus_service.scan_attachment(db, attachment_id)


async def _mark_scan_failed(attachment_id: int):
    """Mark file scan as failed."""
    from datetime import datetime

    from sqlalchemy import update

    from app.models.attachment import Attachment
    from app.utils.constants import VirusStatus

    async with AsyncSessionLocal() as db:
        await db.execute(
            update(Attachment)
            .where(Attachment.id == attachment_id)
            .values(
                virus_status=VirusStatus.ERROR.value,
                virus_scan_result="Scan failed after retries",
                scanned_at=datetime.utcnow(),
                is_available=False,
            )
        )
        await db.commit()


@celery_app.task
def bulk_scan_pending_files():
    """
    Periodic task to scan pending files that haven't been processed.
    """
    try:
        scanned_count = asyncio.run(_bulk_scan_async())
        logger.info(f"Bulk scan completed: {scanned_count} files processed")
        return {"status": "completed", "scanned_count": scanned_count}

    except Exception as exc:
        logger.error(f"Bulk scan task failed: {exc}")
        raise


async def _bulk_scan_async() -> int:
    """Async helper for bulk scanning."""
    async with AsyncSessionLocal() as db:
        return await antivirus_service.bulk_scan_pending_files(db, limit=20)


@celery_app.task
def cleanup_old_attachments():
    """
    Periodic task to clean up old deleted attachments.
    """
    try:
        cleaned_count = asyncio.run(_cleanup_attachments_async())
        logger.info(f"Attachment cleanup completed: {cleaned_count} files removed")
        return {"status": "completed", "cleaned_count": cleaned_count}

    except Exception as exc:
        logger.error(f"Attachment cleanup task failed: {exc}")
        raise


async def _cleanup_attachments_async() -> int:
    """Clean up old deleted attachments."""
    from datetime import datetime, timedelta

    from sqlalchemy import delete, select

    from app.models.attachment import Attachment
    from app.services.storage_service import get_storage_service

    storage_service = get_storage_service()

    cleaned_count = 0

    async with AsyncSessionLocal() as db:
        # Find attachments marked as deleted over 30 days ago
        cutoff_date = datetime.utcnow() - timedelta(days=30)

        result = await db.execute(
            select(Attachment)
            .where(Attachment.is_deleted == True, Attachment.deleted_at < cutoff_date)
            .limit(100)
        )

        attachments = result.scalars().all()

        for attachment in attachments:
            try:
                # Delete from S3
                if storage_service.delete_file(attachment.s3_key):
                    # Delete from database
                    await db.execute(
                        delete(Attachment).where(Attachment.id == attachment.id)
                    )
                    cleaned_count += 1

            except Exception as e:
                logger.error(f"Failed to cleanup attachment {attachment.id}: {e}")
                continue

        await db.commit()

    return cleaned_count
