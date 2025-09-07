import asyncio
import logging
from datetime import datetime, timedelta

from celery import Celery
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models.calendar_integration import CalendarIntegration
from app.models.interview import Interview
from app.services.calendar_service import GoogleCalendarService
from app.services.microsoft_calendar_service import MicrosoftCalendarService
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
AsyncSessionLocal = sessionmaker(
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
    async with AsyncSessionLocal() as db:
        try:
            calendar_integration = await CalendarIntegration.get(
                db, calendar_integration_id
            )
            if not calendar_integration or not calendar_integration.is_active:
                logger.warning(
                    f"Calendar integration {calendar_integration_id} not found or inactive"
                )
                return {"status": "skipped", "reason": "integration not active"}

            if calendar_integration.provider == "google":
                service = GoogleCalendarService()
                sync_token = (
                    None if force_full_sync else calendar_integration.sync_token
                )

                events = await service.list_events(
                    calendar_integration.access_token,
                    calendar_integration.calendar_id,
                    sync_token=sync_token,
                )

                synced_count = 0
                for event_data in events.get("items", []):
                    await _process_calendar_event(
                        db, calendar_integration, event_data, "google"
                    )
                    synced_count += 1

                # Update sync token
                next_sync_token = events.get("nextSyncToken")
                if next_sync_token:
                    calendar_integration.sync_token = next_sync_token

            elif calendar_integration.provider == "microsoft":
                service = MicrosoftCalendarService()

                # For Microsoft, we'll get events from the last sync time
                start_time = None
                if not force_full_sync and calendar_integration.last_sync_at:
                    start_time = calendar_integration.last_sync_at

                events = await service.list_events(
                    calendar_integration.access_token, start_time=start_time
                )

                synced_count = 0
                for event_data in events.get("value", []):
                    await _process_calendar_event(
                        db, calendar_integration, event_data, "microsoft"
                    )
                    synced_count += 1

            # Update last sync time
            calendar_integration.last_sync_at = datetime.utcnow()
            await calendar_integration.save(db)

            logger.info(
                f"Synced {synced_count} events for calendar integration {calendar_integration_id}"
            )
            return {"status": "success", "synced_events": synced_count}

        except Exception as e:
            logger.error(f"Error syncing calendar events: {str(e)}")
            raise


async def _sync_all_calendar_integrations():
    """Internal async function to sync all active calendar integrations."""
    async with AsyncSessionLocal() as db:
        try:
            integrations = await CalendarIntegration.get_active_integrations(db)

            total_synced = 0
            failed_syncs = 0

            for integration in integrations:
                try:
                    result = await _sync_calendar_events(
                        integration.id, force_full_sync=False
                    )
                    total_synced += result.get("synced_events", 0)
                except Exception as e:
                    logger.error(
                        f"Failed to sync integration {integration.id}: {str(e)}"
                    )
                    failed_syncs += 1

            logger.info(
                f"Bulk sync completed: {total_synced} events, {failed_syncs} failures"
            )
            return {
                "status": "completed",
                "total_synced": total_synced,
                "failed_syncs": failed_syncs,
                "total_integrations": len(integrations),
            }

        except Exception as e:
            logger.error(f"Error in bulk calendar sync: {str(e)}")
            raise


async def _check_interview_conflicts(interview_id: int):
    """Internal async function to check for calendar conflicts."""
    async with AsyncSessionLocal() as db:
        try:
            interview_service = InterviewService()
            conflicts = await interview_service.check_interview_conflicts(
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
    async with AsyncSessionLocal() as db:
        try:
            expired_integrations = await CalendarIntegration.get_expired_tokens(db)

            refreshed_count = 0
            disabled_count = 0

            for integration in expired_integrations:
                try:
                    if integration.provider == "google":
                        service = GoogleCalendarService()
                        new_tokens = await service.refresh_access_token(
                            integration.refresh_token
                        )

                        integration.access_token = new_tokens["access_token"]
                        if "refresh_token" in new_tokens:
                            integration.refresh_token = new_tokens["refresh_token"]
                        integration.token_expires_at = datetime.utcnow() + timedelta(
                            seconds=new_tokens.get("expires_in", 3600)
                        )
                        await integration.save(db)
                        refreshed_count += 1

                    elif integration.provider == "microsoft":
                        service = MicrosoftCalendarService()
                        new_tokens = await service.refresh_access_token(
                            integration.refresh_token
                        )

                        integration.access_token = new_tokens["access_token"]
                        if "refresh_token" in new_tokens:
                            integration.refresh_token = new_tokens["refresh_token"]
                        integration.token_expires_at = datetime.utcnow() + timedelta(
                            seconds=new_tokens.get("expires_in", 3600)
                        )
                        await integration.save(db)
                        refreshed_count += 1

                except Exception as e:
                    logger.error(
                        f"Failed to refresh token for integration {integration.id}: {str(e)}"
                    )
                    # Disable the integration
                    integration.is_active = False
                    await integration.save(db)
                    disabled_count += 1

            logger.info(
                f"Token cleanup: {refreshed_count} refreshed, {disabled_count} disabled"
            )
            return {
                "status": "completed",
                "refreshed": refreshed_count,
                "disabled": disabled_count,
            }

        except Exception as e:
            logger.error(f"Error cleaning up expired tokens: {str(e)}")
            raise


async def _sync_interview_to_calendar(interview_id: int, operation: str = "create"):
    """Internal async function to sync interview to connected calendars."""
    async with AsyncSessionLocal() as db:
        try:
            interview_service = InterviewService()
            interview = await interview_service.get_interview(db, interview_id)

            if not interview:
                logger.warning(f"Interview {interview_id} not found")
                return {"status": "skipped", "reason": "interview not found"}

            # Get calendar integrations for interview participants
            participant_ids = [interview.candidate_id, interview.recruiter_id]
            if interview.employer_company_id:
                # Get employer users from the company
                pass  # Would need to implement this

            synced_count = 0
            errors = []

            for user_id in participant_ids:
                try:
                    integrations = await CalendarIntegration.get_by_user_id(db, user_id)

                    for integration in integrations:
                        if not integration.sync_enabled:
                            continue

                        if operation == "create":
                            await _create_calendar_event_for_interview(
                                db, integration, interview
                            )
                        elif operation == "update":
                            await _update_calendar_event_for_interview(
                                db, integration, interview
                            )
                        elif operation == "delete":
                            await _delete_calendar_event_for_interview(
                                db, integration, interview
                            )

                        synced_count += 1

                except Exception as e:
                    error_msg = (
                        f"Failed to sync to calendar for user {user_id}: {str(e)}"
                    )
                    logger.error(error_msg)
                    errors.append(error_msg)

            return {
                "status": "completed",
                "synced_calendars": synced_count,
                "errors": errors,
            }

        except Exception as e:
            logger.error(f"Error syncing interview to calendar: {str(e)}")
            raise


async def _process_calendar_event(
    db: AsyncSession,
    calendar_integration: CalendarIntegration,
    event_data: dict,
    provider: str,
):
    """Process a calendar event from webhook or sync."""
    # This is similar to the webhook processing logic
    # Implementation would be similar to process_calendar_event_update in webhooks.py


async def _create_calendar_event_for_interview(
    db: AsyncSession, integration: CalendarIntegration, interview: Interview
):
    """Create a calendar event for an interview."""
    if not interview.scheduled_start or not interview.scheduled_end:
        return

    if integration.provider == "google":
        service = GoogleCalendarService()
        event_data = {
            "summary": interview.title,
            "description": interview.description,
            "location": interview.location,
            "start": {
                "dateTime": interview.scheduled_start.isoformat(),
                "timeZone": interview.timezone or "UTC",
            },
            "end": {
                "dateTime": interview.scheduled_end.isoformat(),
                "timeZone": interview.timezone or "UTC",
            },
        }

        created_event = await service.create_event(
            integration.access_token, integration.calendar_id, event_data
        )

        # Store the external event ID with the interview
        interview.external_calendar_event_id = created_event.get("id")
        await interview.save(db)

    elif integration.provider == "microsoft":
        service = MicrosoftCalendarService()
        event_data = {
            "subject": interview.title,
            "body": {"content": interview.description or ""},
            "location": {"displayName": interview.location or ""},
            "start": {
                "dateTime": interview.scheduled_start.isoformat(),
                "timeZone": interview.timezone or "UTC",
            },
            "end": {
                "dateTime": interview.scheduled_end.isoformat(),
                "timeZone": interview.timezone or "UTC",
            },
        }

        created_event = await service.create_event(integration.access_token, event_data)

        interview.external_calendar_event_id = created_event.get("id")
        await interview.save(db)


async def _update_calendar_event_for_interview(
    db: AsyncSession, integration: CalendarIntegration, interview: Interview
):
    """Update a calendar event for an interview."""
    if not interview.external_calendar_event_id:
        # Create if doesn't exist
        await _create_calendar_event_for_interview(db, integration, interview)
        return

    # Implementation would update the existing event


async def _delete_calendar_event_for_interview(
    db: AsyncSession, integration: CalendarIntegration, interview: Interview
):
    """Delete a calendar event for an interview."""
    if not interview.external_calendar_event_id:
        return

    if integration.provider == "google":
        service = GoogleCalendarService()
        await service.delete_event(
            integration.access_token,
            integration.calendar_id,
            interview.external_calendar_event_id,
        )
    elif integration.provider == "microsoft":
        service = MicrosoftCalendarService()
        await service.delete_event(
            integration.access_token, interview.external_calendar_event_id
        )


# Periodic task scheduling
@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """Setup periodic tasks for calendar synchronization."""

    # Sync all calendar integrations every 15 minutes
    sender.add_periodic_task(
        900.0,  # 15 minutes
        sync_all_calendar_integrations_task.s(),
        name="sync all calendar integrations",
    )

    # Clean up expired tokens every hour
    sender.add_periodic_task(
        3600.0,  # 1 hour
        cleanup_expired_calendar_tokens_task.s(),
        name="cleanup expired calendar tokens",
    )


if __name__ == "__main__":
    celery_app.start()
