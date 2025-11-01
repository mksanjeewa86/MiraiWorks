import asyncio
import logging

from celery import Celery
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.models.interview import Interview
from app.services.interview_service import InterviewService

# Initialize Celery
celery_app = Celery(
    "calendar_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.workers.calendar_tasks"],
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    task_soft_time_limit=240,  # 4 minutes
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_disable_rate_limits=False,
    task_default_retry_delay=60,  # 1 minute
    task_max_retries=3,
)

logger = logging.getLogger(__name__)

# Database setup for async tasks
engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(  # type: ignore[call-overload]
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db_session():
    """Get async database session for worker tasks."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def run_async_task(coro):
    """Helper to run async functions in Celery tasks."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(bind=True, name="sync_calendar_events")
def sync_calendar_events_task(
    self, calendar_integration_id: int, force_full_sync: bool = False
):
    """Periodic task to sync calendar events for a specific integration."""
    return run_async_task(
        _sync_calendar_events(calendar_integration_id, force_full_sync)
    )


@celery_app.task(bind=True, name="sync_all_calendar_integrations")
def sync_all_calendar_integrations_task(self):
    """Task to sync all active calendar integrations."""
    return run_async_task(_sync_all_calendar_integrations())


@celery_app.task(bind=True, name="check_interview_conflicts")
def check_interview_conflicts_task(self, interview_id: int):
    """Task to check for calendar conflicts for a specific interview."""
    return run_async_task(_check_interview_conflicts(interview_id))


@celery_app.task(bind=True, name="cleanup_expired_calendar_tokens")
def cleanup_expired_calendar_tokens_task(self):
    """Task to clean up expired calendar tokens and refresh where possible."""
    return run_async_task(_cleanup_expired_calendar_tokens())


@celery_app.task(bind=True, name="sync_interview_to_calendar")
def sync_interview_to_calendar_task(self, interview_id: int, operation: str = "create"):
    """Task to sync interview changes to connected calendars."""
    return run_async_task(_sync_interview_to_calendar(interview_id, operation))


async def _sync_calendar_events(
    calendar_integration_id: int, force_full_sync: bool = False
):
    """Internal async function to sync calendar events."""
    try:
        # ExternalCalendarAccount model methods not implemented
        logger.warning("Calendar integration methods not implemented")
        return {"status": "skipped", "reason": "not implemented"}

    except Exception as e:
        logger.error(f"Error syncing calendar events: {str(e)}")
        raise


async def _sync_all_calendar_integrations():
    """Internal async function to sync all active calendar integrations."""
    try:
        # ExternalCalendarAccount model methods not implemented
        logger.warning("Calendar integration methods not implemented")
        return {"status": "skipped", "reason": "not implemented"}

    except Exception as e:
        logger.error(f"Error in bulk calendar sync: {str(e)}")
        raise


async def _check_interview_conflicts(interview_id: int):
    """Internal async function to check for calendar conflicts."""
    async with AsyncSessionLocal() as db:
        try:
            interview_service = InterviewService()
            conflicts = await interview_service.check_interview_conflicts(  # type: ignore[attr-defined]
                db, interview_id
            )

            if conflicts:
                logger.warning(
                    f"Interview {interview_id} has {len(conflicts)} conflicts"
                )
                # Could trigger notifications here

            return {"status": "checked", "conflicts": len(conflicts)}

        except Exception as e:
            logger.error(f"Error checking interview conflicts: {str(e)}")
            raise


async def _cleanup_expired_calendar_tokens():
    """Internal async function to clean up expired calendar tokens."""
    try:
        # ExternalCalendarAccount model methods not implemented
        logger.warning("Calendar integration methods not implemented")
        return {"status": "skipped", "reason": "not implemented"}

    except Exception as e:
        logger.error(f"Error cleaning up expired tokens: {str(e)}")
        raise


async def _sync_interview_to_calendar(interview_id: int, operation: str = "create"):
    """Internal async function to sync interview to connected calendars."""
    async with AsyncSessionLocal() as db:
        try:
            interview_service = InterviewService()
            interview = await interview_service.get_interview(db, interview_id)  # type: ignore[attr-defined]

            if not interview:
                logger.warning(f"Interview {interview_id} not found")
                return {"status": "skipped", "reason": "interview not found"}

            # ExternalCalendarAccount model methods not implemented
            logger.warning("Calendar integration methods not implemented")
            return {"status": "skipped", "reason": "not implemented"}

        except Exception as e:
            logger.error(f"Error syncing interview to calendar: {str(e)}")
            raise


async def _process_calendar_event(
    db: AsyncSession,
    calendar_integration,  # TODO: Fix ExternalCalendarAccount type
    event_data: dict,
    provider: str,
):
    """Process a calendar event from webhook or sync."""
    # TODO: Implement when ExternalCalendarAccount model is fixed
    logger.warning("Calendar event processing not implemented")


async def _create_calendar_event_for_interview(
    db: AsyncSession,
    integration,
    interview: Interview,  # TODO: Fix ExternalCalendarAccount type
):
    """Create a calendar event for an interview."""
    # TODO: Implement when ExternalCalendarAccount model is fixed
    logger.warning("Calendar event creation not implemented")


async def _update_calendar_event_for_interview(
    db: AsyncSession,
    integration,
    interview: Interview,  # TODO: Fix ExternalCalendarAccount type
):
    """Update a calendar event for an interview."""
    # TODO: Implement when ExternalCalendarAccount model is fixed
    logger.warning("Calendar event update not implemented")


async def _delete_calendar_event_for_interview(
    db: AsyncSession,
    integration,
    interview: Interview,  # TODO: Fix ExternalCalendarAccount type
):
    """Delete a calendar event for an interview."""
    # TODO: Implement when ExternalCalendarAccount model is fixed
    logger.warning("Calendar event deletion not implemented")


# Periodic task scheduling
@celery_app.on_after_configure.connect  # type: ignore[union-attr]
def setup_periodic_tasks(sender, **kwargs):
    """Setup periodic tasks for calendar synchronization."""

    # Sync all calendar integrations every 15 minutes
    sender.add_periodic_task(
        900.0,  # 15 minutes
        sync_all_calendar_integrations_task.s(),  # type: ignore[attr-defined]
        name="sync all calendar integrations",
    )

    # Clean up expired tokens every hour
    sender.add_periodic_task(
        3600.0,  # 1 hour
        cleanup_expired_calendar_tokens_task.s(),  # type: ignore[attr-defined]
        name="cleanup expired calendar tokens",
    )


if __name__ == "__main__":
    celery_app.start()
