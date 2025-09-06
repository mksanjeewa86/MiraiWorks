import json
import logging
from datetime import datetime
from typing import Any
from typing import Dict

from fastapi import APIRouter
from fastapi import BackgroundTasks
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.calendar_integration import ExternalCalendarAccount, SyncedEvent
from app.services.calendar_service import GoogleCalendarService
from app.services.interview_service import InterviewService
from app.services.microsoft_calendar_service import MicrosoftCalendarService

router = APIRouter(tags=["webhooks"])
logger = logging.getLogger(__name__)


@router.post("/google/calendar")
async def google_calendar_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Handle Google Calendar webhook notifications for event changes."""
    try:
        # Get the raw body for verification
        await request.body()
        headers = request.headers
        
        # Verify webhook authenticity
        resource_id = headers.get("x-goog-resource-id")
        resource_state = headers.get("x-goog-resource-state")
        channel_id = headers.get("x-goog-channel-id")
        
        if not all([resource_id, resource_state, channel_id]):
            raise HTTPException(status_code=400, detail="Missing required headers")
        
        logger.info(f"Received Google Calendar webhook: {resource_state} for {resource_id}")
        
        # Find the calendar integration for this channel
        calendar_integration = await ExternalCalendarAccount.get_by_channel_id(db, channel_id)
        if not calendar_integration:
            logger.warning(f"No calendar integration found for channel {channel_id}")
            return {"status": "ignored"}
        
        # Queue background sync task
        background_tasks.add_task(
            sync_google_calendar_events,
            db,
            calendar_integration.id,
            resource_state
        )
        
        return {"status": "received"}
        
    except Exception as e:
        logger.error(f"Error processing Google Calendar webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")


@router.post("/microsoft/calendar")
async def microsoft_calendar_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Handle Microsoft Graph webhook notifications for calendar changes."""
    try:
        body = await request.body()
        
        # Verify webhook with validation token (if present)
        query_params = request.query_params
        validation_token = query_params.get("validationToken")
        if validation_token:
            # This is a subscription validation request
            return validation_token
        
        # Parse webhook payload
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON payload")
        
        # Process each notification
        notifications = payload.get("value", [])
        for notification in notifications:
            resource = notification.get("resource")
            change_type = notification.get("changeType")
            subscription_id = notification.get("subscriptionId")
            
            logger.info(f"Microsoft webhook: {change_type} for {resource}")
            
            # Find calendar integration by subscription ID
            calendar_integration = await ExternalCalendarAccount.get_by_subscription_id(
                db, subscription_id
            )
            if calendar_integration:
                background_tasks.add_task(
                    sync_microsoft_calendar_events,
                    db,
                    calendar_integration.id,
                    change_type,
                    resource
                )
        
        return {"status": "received"}
        
    except Exception as e:
        logger.error(f"Error processing Microsoft Calendar webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")


async def sync_google_calendar_events(
    db: AsyncSession,
    calendar_integration_id: int,
    resource_state: str
):
    """Background task to sync Google Calendar events after webhook notification."""
    try:
        calendar_integration = await ExternalCalendarAccount.get(db, calendar_integration_id)
        if not calendar_integration:
            logger.error(f"Calendar integration {calendar_integration_id} not found")
            return
        
        calendar_service = GoogleCalendarService()
        
        # Get updated events from Google Calendar
        events = await calendar_service.list_events(
            calendar_integration.access_token,
            calendar_integration.calendar_id,
            sync_token=calendar_integration.sync_token
        )
        
        # Process events and update database
        for event_data in events.get("items", []):
            await process_calendar_event_update(
                db, calendar_integration, event_data, "google"
            )
        
        # Update sync token
        next_sync_token = events.get("nextSyncToken")
        if next_sync_token:
            calendar_integration.sync_token = next_sync_token
            calendar_integration.last_sync_at = datetime.utcnow()
            await calendar_integration.save(db)
        
        logger.info(f"Synced Google Calendar events for integration {calendar_integration_id}")
        
    except Exception as e:
        logger.error(f"Error syncing Google Calendar events: {str(e)}")


async def sync_microsoft_calendar_events(
    db: AsyncSession,
    calendar_integration_id: int,
    change_type: str,
    resource: str
):
    """Background task to sync Microsoft Calendar events after webhook notification."""
    try:
        calendar_integration = await ExternalCalendarAccount.get(db, calendar_integration_id)
        if not calendar_integration:
            logger.error(f"Calendar integration {calendar_integration_id} not found")
            return
        
        microsoft_service = MicrosoftCalendarService()
        
        # Extract event ID from resource path
        # Resource format: /me/events/{event-id}
        event_id = resource.split("/")[-1] if "/" in resource else resource
        
        if change_type in ["created", "updated"]:
            # Get the updated event
            event_data = await microsoft_service.get_event(
                calendar_integration.access_token,
                event_id
            )
            if event_data:
                await process_calendar_event_update(
                    db, calendar_integration, event_data, "microsoft"
                )
                
        elif change_type == "deleted":
            # Remove the event from our database
            await SyncedEvent.delete_by_external_id(db, event_id)
        
        # Update last sync time
        calendar_integration.last_sync_at = datetime.utcnow()
        await calendar_integration.save(db)
        
        logger.info(f"Processed Microsoft Calendar event {change_type}: {event_id}")
        
    except Exception as e:
        logger.error(f"Error syncing Microsoft Calendar event: {str(e)}")


async def process_calendar_event_update(
    db: AsyncSession,
    calendar_integration: ExternalCalendarAccount,
    event_data: Dict[str, Any],
    provider: str
):
    """Process a calendar event update from webhook notification."""
    try:
        if provider == "google":
            event_id = event_data.get("id")
            title = event_data.get("summary", "")
            description = event_data.get("description")
            location = event_data.get("location")
            
            # Parse start/end times
            start_data = event_data.get("start", {})
            end_data = event_data.get("end", {})
            
            start_datetime = None
            end_datetime = None
            is_all_day = False
            
            if "date" in start_data:
                # All-day event
                is_all_day = True
                start_datetime = datetime.fromisoformat(start_data["date"])
                end_datetime = datetime.fromisoformat(end_data["date"])
            elif "dateTime" in start_data:
                start_datetime = datetime.fromisoformat(start_data["dateTime"].replace("Z", "+00:00"))
                end_datetime = datetime.fromisoformat(end_data["dateTime"].replace("Z", "+00:00"))
            
        elif provider == "microsoft":
            event_id = event_data.get("id")
            title = event_data.get("subject", "")
            description = event_data.get("body", {}).get("content")
            location = event_data.get("location", {}).get("displayName")
            
            # Parse start/end times
            start_data = event_data.get("start", {})
            end_data = event_data.get("end", {})
            
            is_all_day = event_data.get("isAllDay", False)
            
            if is_all_day:
                start_datetime = datetime.fromisoformat(start_data["dateTime"].split("T")[0])
                end_datetime = datetime.fromisoformat(end_data["dateTime"].split("T")[0])
            else:
                start_datetime = datetime.fromisoformat(start_data["dateTime"].replace("Z", "+00:00"))
                end_datetime = datetime.fromisoformat(end_data["dateTime"].replace("Z", "+00:00"))
        
        if not all([event_id, start_datetime, end_datetime]):
            logger.warning(f"Incomplete event data for {event_id}")
            return
        
        # Check if this is an interview-related event
        interview_service = InterviewService()
        interview = await interview_service.get_interview_by_external_event_id(db, event_id)
        
        if interview:
            # Update interview with new calendar data
            await interview_service.update_interview_from_calendar_event(
                db,
                interview.id,
                {
                    "scheduled_start": start_datetime,
                    "scheduled_end": end_datetime,
                    "location": location,
                    "title": title
                }
            )
            logger.info(f"Updated interview {interview.id} from calendar event {event_id}")
        
        # Update or create calendar event record
        existing_event = await SyncedEvent.get_by_external_id(db, event_id)
        
        event_data_dict = {
            "calendar_account_id": calendar_integration.id,
            "external_event_id": event_id,
            "external_calendar_id": calendar_integration.calendar_id or "",
            "title": title,
            "description": description,
            "location": location,
            "start_datetime": start_datetime,
            "end_datetime": end_datetime,
            "is_all_day": is_all_day,
            "timezone": calendar_integration.calendar_timezone or "UTC",
            "last_modified": datetime.utcnow()
        }
        
        if existing_event:
            for key, value in event_data_dict.items():
                if key != "calendar_account_id":  # Don't update this
                    setattr(existing_event, key, value)
            await existing_event.save(db)
        else:
            calendar_event = SyncedEvent(**event_data_dict)
            await calendar_event.save(db)
        
    except Exception as e:
        logger.error(f"Error processing calendar event update: {str(e)}")


@router.get("/health")
async def webhook_health():
    """Health check endpoint for webhook services."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "webhooks": ["google_calendar", "microsoft_calendar"]
    }