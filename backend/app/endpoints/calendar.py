import logging
from datetime import datetime, timedelta

from app.config.endpoints import API_ROUTES
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.calendar_integration import calendar_integration
from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.calendar import (
    CalendarAccountInfo,
    CalendarInfo,
    CalendarSyncRequest,
    CalendarSyncResponse,
    CalendarWebhookData,
    EventInfo,
    EventsListResponse,
)
from app.schemas.calendar_event import (
    CalendarEventBulkCreate,
    CalendarEventBulkResponse,
    CalendarEventCreate,
    CalendarEventInfo,
    CalendarEventListResponse,
    CalendarEventQueryParams,
    CalendarEventUpdate,
)
from app.services.calendar_service import calendar_service
from app.services.google_calendar_service import google_calendar_service
from app.services.microsoft_calendar_service import microsoft_calendar_service

router = APIRouter()
logger = logging.getLogger(__name__)


# OAuth endpoints
@router.get(API_ROUTES.CALENDAR.GOOGLE_OAUTH_START)
async def start_google_oauth(
    current_user: User = Depends(get_current_active_user), state: str | None = None
):
    """Start Google Calendar OAuth flow."""
    try:
        auth_url = await google_calendar_service.get_auth_url(current_user.id, state)
        return {"auth_url": auth_url}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        )


@router.get(API_ROUTES.CALENDAR.GOOGLE_OAUTH_CALLBACK)
async def google_oauth_callback(
    code: str = Query(...),
    state: str | None = Query(None),
    error: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Handle Google OAuth callback."""
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"OAuth error: {error}"
        )

    # Exchange code for tokens
    tokens = await google_calendar_service.exchange_code_for_tokens(code)

    # Get user info
    user_info = await google_calendar_service.get_user_info(tokens["access_token"])

    # Find user by state parameter or email
    user_id = int(state) if state and state.isdigit() else None
    if not user_id:
        # Try to find user by email
        user = await calendar_integration.get_user_by_email(db, user_info["email"])
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        user_id = user.id

    # Check if calendar account already exists
    account = await calendar_integration.get_by_user_and_provider_account(
        db, user_id, "google", user_info["id"]
    )

    token_expires_at = datetime.utcnow() + timedelta(
        seconds=tokens.get("expires_in", 3600)
    )

    if account:
        # Update existing account
        account = await calendar_integration.update_account_tokens(
            db,
            account,
            tokens["access_token"],
            tokens.get("refresh_token"),
            token_expires_at,
            user_info["email"],
            user_info.get("name"),
        )
    else:
        # Create new account
        account = await calendar_integration.create_calendar_account(
            db,
            user_id,
            "google",
            user_info["id"],
            user_info["email"],
            user_info.get("name"),
            tokens["access_token"],
            tokens.get("refresh_token"),
            token_expires_at,
        )

    # Set up webhook
    try:
        webhook_data = await google_calendar_service.create_webhook_watch(account)
        if webhook_data:
            webhook_expires_at = datetime.fromtimestamp(
                webhook_data.get("expiration", 0) / 1000
            )
            account = await calendar_integration.update_webhook_info(
                db, account, webhook_data.get("id"), webhook_expires_at
            )
    except Exception as e:
        logger.warning(f"Failed to set up Google Calendar webhook: {e}")

    return {
        "message": "Google Calendar connected successfully",
        "account_id": account.id,
    }


@router.get(API_ROUTES.CALENDAR.MICROSOFT_OAUTH_START)
async def start_microsoft_oauth(
    current_user: User = Depends(get_current_active_user), state: str | None = None
):
    """Start Microsoft Calendar OAuth flow."""
    auth_url = microsoft_calendar_service.get_auth_url(current_user.id, state)
    return {"auth_url": auth_url}


@router.get(API_ROUTES.CALENDAR.MICROSOFT_OAUTH_CALLBACK)
async def microsoft_oauth_callback(
    code: str = Query(...),
    state: str | None = Query(None),
    error: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Handle Microsoft OAuth callback."""
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"OAuth error: {error}"
        )

    # Exchange code for tokens
    tokens = await microsoft_calendar_service.exchange_code_for_tokens(code)

    # Get user info
    user_info = await microsoft_calendar_service.get_user_info(tokens["access_token"])

    # Find user by state parameter or email
    user_id = int(state) if state and state.isdigit() else None
    if not user_id:
        # Try to find user by email
        user_email = user_info.get("mail") or user_info.get("userPrincipalName")
        user = await calendar_integration.get_user_by_email(db, user_email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        user_id = user.id

    # Check if calendar account already exists
    account = await calendar_integration.get_by_user_and_provider_account(
        db, user_id, "microsoft", user_info["id"]
    )

    token_expires_at = datetime.utcnow() + timedelta(
        seconds=tokens.get("expires_in", 3600)
    )
    user_email = user_info.get("mail", user_info.get("userPrincipalName"))
    display_name = user_info.get("displayName")

    if account:
        # Update existing account
        account = await calendar_integration.update_account_tokens(
            db,
            account,
            tokens["access_token"],
            tokens.get("refresh_token"),
            token_expires_at,
            user_email,
            display_name,
        )
    else:
        # Create new account
        account = await calendar_integration.create_calendar_account(
            db,
            user_id,
            "microsoft",
            user_info["id"],
            user_email,
            display_name,
            tokens["access_token"],
            tokens.get("refresh_token"),
            token_expires_at,
        )

    # Set up webhook
    try:
        subscription_data = (
            await microsoft_calendar_service.create_webhook_subscription(account)
        )
        if subscription_data:
            webhook_expires_at = datetime.fromisoformat(
                subscription_data.get("expirationDateTime").replace("Z", "+00:00")
            )
            account = await calendar_integration.update_webhook_info(
                db, account, subscription_data.get("id"), webhook_expires_at
            )
    except Exception as e:
        logger.warning(f"Failed to set up Microsoft Calendar webhook: {e}")

    return {
        "message": "Microsoft Calendar connected successfully",
        "account_id": account.id,
    }


# Calendar account management
@router.get(API_ROUTES.CALENDAR.ACCOUNTS, response_model=list[CalendarAccountInfo])
async def get_calendar_accounts(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get user's connected calendar accounts."""
    accounts = await calendar_integration.get_active_accounts_by_user(
        db, current_user.id
    )
    return [
        CalendarAccountInfo(
            id=account.id,
            provider=account.provider,
            email=account.email,
            display_name=account.display_name,
            calendar_id=account.calendar_id,
            calendar_timezone=account.calendar_timezone,
            is_active=account.is_active,
            sync_enabled=account.sync_enabled,
            last_sync_at=account.last_sync_at,
            created_at=account.created_at,
        )
        for account in accounts
    ]


@router.delete(API_ROUTES.CALENDAR.ACCOUNT_BY_ID)
async def disconnect_calendar_account(
    account_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Disconnect a calendar account."""
    # Get account
    account = await calendar_integration.get_user_account_by_id(
        db, account_id, current_user.id
    )
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Calendar account not found"
        )

    # Deactivate account
    await calendar_integration.deactivate_account(db, account)

    return {"message": "Calendar account disconnected successfully"}


@router.post(API_ROUTES.CALENDAR.ACCOUNT_SYNC, response_model=CalendarSyncResponse)
async def sync_calendar_account(
    account_id: int,
    sync_request: CalendarSyncRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Manually trigger calendar sync."""
    # Get account
    account = await calendar_integration.get_active_user_account_by_id(
        db, account_id, current_user.id
    )
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Calendar account not found"
        )

    # Trigger sync (this would typically be done by a background worker)
    try:
        if account.provider == "google":
            events = await google_calendar_service.get_events(
                account,
                time_min=datetime.utcnow() - timedelta(days=30),
                time_max=datetime.utcnow() + timedelta(days=90),
            )
        elif account.provider == "microsoft":
            events = await microsoft_calendar_service.get_events(
                account,
                time_min=datetime.utcnow() - timedelta(days=30),
                time_max=datetime.utcnow() + timedelta(days=90),
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported calendar provider",
            )

        # Update last sync time
        await calendar_integration.update_last_sync(db, account, datetime.utcnow())

        return CalendarSyncResponse(success=True, synced_events=len(events), errors=[])

    except Exception as e:
        logger.error(f"Calendar sync failed for account {account_id}: {e}")
        return CalendarSyncResponse(success=False, synced_events=0, errors=[str(e)])


@router.get(API_ROUTES.CALENDAR.CALENDARS)
async def get_calendars(
    account_id: int | None = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get available calendars for user's accounts."""
    accounts = await calendar_integration.get_filtered_accounts_by_user(
        db, current_user.id, account_id
    )

    all_calendars = []

    for account in accounts:
        try:
            if account.provider == "google":
                calendars = await google_calendar_service.get_calendars(account)
                for cal in calendars:
                    all_calendars.append(
                        CalendarInfo(
                            id=cal["id"],
                            name=cal.get("summary", ""),
                            description=cal.get("description"),
                            primary=cal.get("primary", False),
                            timezone=cal.get("timeZone"),
                            access_role=cal.get("accessRole"),
                        )
                    )

            elif account.provider == "microsoft":
                calendars = await microsoft_calendar_service.get_calendars(account)
                for cal in calendars:
                    all_calendars.append(
                        CalendarInfo(
                            id=cal["id"],
                            name=cal.get("name", ""),
                            description=None,
                            primary=cal.get("isDefaultCalendar", False),
                            timezone=None,
                            access_role="owner",
                        )
                    )

        except Exception as e:
            logger.error(f"Failed to get calendars for account {account.id}: {e}")

    return {"calendars": all_calendars}


@router.get(API_ROUTES.CALENDAR.EVENTS, response_model=EventsListResponse)
async def get_events(
    startDate: str | None = Query(None),
    endDate: str | None = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get consolidated calendar events including internal events, external events, and holidays."""
    logger.info(
        f"GET /api/calendar/events - startDate: {startDate}, endDate: {endDate}"
    )

    # Set default date range if not provided
    if not startDate:
        start_date = datetime.utcnow()
    else:
        start_date = datetime.fromisoformat(startDate.replace("Z", "+00:00"))

    if not endDate:
        end_date = start_date + timedelta(days=30)
    else:
        end_date = datetime.fromisoformat(endDate.replace("Z", "+00:00"))

    try:
        # Get consolidated calendar data from service
        calendar_data = await calendar_service.get_consolidated_calendar(
            db, user_id=current_user.id, start_date=start_date, end_date=end_date
        )

        all_events = []

        # Convert internal events to EventInfo format
        for event in calendar_data["internal_events"]:
            event_info = EventInfo(
                id=event["id"],
                title=event["title"],
                description=event.get("description"),
                location=event.get("location"),
                start_datetime=datetime.fromisoformat(event["start"]),
                end_datetime=datetime.fromisoformat(event["end"])
                if event["end"]
                else None,
                timezone="UTC",
                is_all_day=event["allDay"],
                is_recurring=False,  # Will be enhanced later for recurring events
                organizer_email=current_user.email,
                attendees=[],
                status=event["status"],
                created_at=datetime.utcnow(),  # This should come from the event data
                updated_at=datetime.utcnow(),  # This should come from the event data
            )
            all_events.append(event_info)

        # Convert holidays to EventInfo format
        for holiday in calendar_data["holidays"]:
            holiday_event = EventInfo(
                id=holiday["id"],
                title=holiday["title"],
                description=holiday.get("description"),
                location=None,
                start_datetime=datetime.fromisoformat(holiday["start"]),
                end_datetime=datetime.fromisoformat(holiday["end"]),
                timezone="Asia/Tokyo",
                is_all_day=holiday["allDay"],
                is_recurring=False,
                organizer_email=None,
                attendees=[],
                status="confirmed",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            all_events.append(holiday_event)

        # Sort by start time
        all_events.sort(key=lambda x: x.start_datetime)

        logger.info(f"Retrieved {len(all_events)} events for user {current_user.id}")

        return EventsListResponse(
            events=all_events,
            has_more=False,
        )

    except Exception as e:
        logger.error(f"Failed to get calendar events: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve calendar events",
        )

    # Original implementation (commented out for testing):
    """
    # Get user's calendar accounts
    accounts = await calendar_integration.get_sync_enabled_accounts_by_user(
        db, current_user.id
    )

    all_events = []

    for account in accounts:
        try:
            if account.provider == "google":
                events = await google_calendar_service.get_events(
                    account,
                    request.calendar_id or "primary",
                    request.start_date,
                    request.end_date,
                    request.max_results,
                )

                for event in events:
                    # Parse Google Calendar event format
                    start_dt = event.get("start", {})
                    end_dt = event.get("end", {})

                    start_datetime = datetime.fromisoformat(
                        start_dt.get("dateTime", start_dt.get("date", "")).replace(
                            "Z", "+00:00"
                        )
                    )
                    end_datetime = datetime.fromisoformat(
                        end_dt.get("dateTime", end_dt.get("date", "")).replace(
                            "Z", "+00:00"
                        )
                    )

                    all_events.append(
                        EventInfo(
                            id=event["id"],
                            title=event.get("summary", ""),
                            description=event.get("description"),
                            location=event.get("location"),
                            start_datetime=start_datetime,
                            end_datetime=end_datetime,
                            timezone=start_dt.get("timeZone", "UTC"),
                            is_all_day="date" in start_dt,
                            is_recurring=event.get("recurringEventId") is not None,
                            organizer_email=event.get("organizer", {}).get("email"),
                            attendees=[
                                att.get("email", "")
                                for att in event.get("attendees", [])
                            ],
                            status=event.get("status"),
                            created_at=datetime.fromisoformat(
                                event.get("created", "").replace("Z", "+00:00")
                            ),
                            updated_at=datetime.fromisoformat(
                                event.get("updated", "").replace("Z", "+00:00")
                            ),
                        )
                    )

            elif account.provider == "microsoft":
                events = await microsoft_calendar_service.get_events(
                    account,
                    request.calendar_id,
                    request.start_date,
                    request.end_date,
                    request.max_results,
                )

                for event in events:
                    start_datetime = datetime.fromisoformat(
                        event["start"]["dateTime"].replace("Z", "+00:00")
                    )
                    end_datetime = datetime.fromisoformat(
                        event["end"]["dateTime"].replace("Z", "+00:00")
                    )

                    all_events.append(
                        EventInfo(
                            id=event["id"],
                            title=event.get("subject", ""),
                            description=event.get("body", {}).get("content"),
                            location=event.get("location", {}).get("displayName"),
                            start_datetime=start_datetime,
                            end_datetime=end_datetime,
                            timezone=event["start"].get("timeZone", "UTC"),
                            is_all_day=event.get("isAllDay", False),
                            is_recurring=event.get("recurrence") is not None,
                            organizer_email=event.get("organizer", {})
                            .get("emailAddress", {})
                            .get("address"),
                            attendees=[
                                att.get("emailAddress", {}).get("address", "")
                                for att in event.get("attendees", [])
                            ],
                            status=event.get("showAs"),
                            created_at=datetime.fromisoformat(
                                event.get("createdDateTime", "").replace("Z", "+00:00")
                            ),
                            updated_at=datetime.fromisoformat(
                                event.get("lastModifiedDateTime", "").replace(
                                    "Z", "+00:00"
                                )
                            ),
                        )
                    )

        except Exception as e:
            logger.error(f"Failed to get events for account {account.id}: {e}")

    # Sort by start time
    all_events.sort(key=lambda x: x.start_datetime)

    return EventsListResponse(
        events=all_events[: request.max_results],
        has_more=len(all_events) > request.max_results,
    )
    """


# Webhook endpoints
@router.post(API_ROUTES.CALENDAR.WEBHOOKS_GOOGLE)
async def google_calendar_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Handle Google Calendar webhook notifications."""
    # Verify webhook (simplified - should validate signature in production)
    headers = request.headers

    # Get the user token from headers
    user_token = headers.get("x-goog-channel-token")
    if not user_token or not user_token.startswith("user_"):
        logger.warning("Invalid or missing user token in Google webhook")
        return {"status": "ignored"}

    user_id = int(user_token.replace("user_", ""))

    # Trigger sync for user's Google calendars
    # This would typically queue a background job
    logger.info(f"Google Calendar webhook received for user {user_id}")

    return {"status": "received"}


@router.post(API_ROUTES.CALENDAR.WEBHOOKS_MICROSOFT)
async def microsoft_calendar_webhook(
    webhook_data: CalendarWebhookData,
    validation_token: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Handle Microsoft Graph webhook notifications."""
    # Handle validation
    if validation_token:
        return {"validationToken": validation_token}

    # Get user from client state
    client_state = webhook_data.client_state
    if not client_state or not client_state.startswith("user_"):
        logger.warning("Invalid or missing client state in Microsoft webhook")
        return {"status": "ignored"}

    user_id = int(client_state.replace("user_", ""))

    # Trigger sync for user's Microsoft calendars
    # This would typically queue a background job
    logger.info(f"Microsoft Calendar webhook received for user {user_id}")

    return {"status": "received"}


# ==================== INTERNAL CALENDAR EVENT ENDPOINTS ====================


@router.post(
    API_ROUTES.CALENDAR.EVENTS, response_model=CalendarEventInfo, status_code=201
)
async def create_calendar_event(
    event_data: CalendarEventCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new internal calendar event."""
    try:
        event = await calendar_service.create_event(
            db, event_in=event_data, creator_id=current_user.id
        )
        logger.info(f"Created calendar event: {event.title} for user {current_user.id}")
        return event
    except Exception as e:
        logger.error(f"Failed to create calendar event: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(API_ROUTES.CALENDAR.EVENT_BY_ID, response_model=CalendarEventInfo)
async def get_calendar_event(
    event_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific calendar event."""
    try:
        # Get event from database
        from app.crud.calendar_event import calendar_event

        event = await calendar_event.get(db, id=event_id)

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
            )

        # Check if user has permission to view this event
        if event.creator_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this event",
            )

        return CalendarEventInfo.model_validate(event)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get calendar event {event_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve event",
        )


@router.put(API_ROUTES.CALENDAR.EVENT_BY_ID, response_model=CalendarEventInfo)
async def update_calendar_event(
    event_id: int,
    event_data: CalendarEventUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a calendar event."""
    try:
        updated_event = await calendar_service.update_event(
            db, event_id=event_id, event_in=event_data, user_id=current_user.id
        )

        if not updated_event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
            )

        logger.info(f"Updated calendar event {event_id} for user {current_user.id}")
        return updated_event

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update calendar event {event_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update event",
        )


@router.delete(API_ROUTES.CALENDAR.EVENT_BY_ID)
async def delete_calendar_event(
    event_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a calendar event."""
    try:
        deleted = await calendar_service.delete_event(
            db, event_id=event_id, user_id=current_user.id
        )

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
            )

        logger.info(f"Deleted calendar event {event_id} for user {current_user.id}")
        return {"message": "Event deleted successfully"}

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to delete calendar event {event_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete event",
        )


# ==================== ADDITIONAL CALENDAR ENDPOINTS ====================


@router.get(API_ROUTES.CALENDAR.EVENTS_RANGE, response_model=CalendarEventListResponse)
async def get_events_in_range(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    event_type: str = Query(None),
    status: str = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get calendar events within a specific date range."""
    try:
        query_params = CalendarEventQueryParams(
            start_date=start_date,
            end_date=end_date,
            event_type=event_type,
            status=status,
        )

        events = await calendar_service.get_user_events(
            db, user_id=current_user.id, query_params=query_params
        )

        return CalendarEventListResponse(
            events=events, total=len(events), start_date=start_date, end_date=end_date
        )

    except Exception as e:
        logger.error(f"Failed to get events in range: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve events",
        )


@router.get(API_ROUTES.CALENDAR.EVENTS_UPCOMING, response_model=list[CalendarEventInfo])
async def get_upcoming_events(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get upcoming calendar events for the user."""
    try:
        events = await calendar_service.get_upcoming_events(
            db, user_id=current_user.id, limit=limit
        )
        return events

    except Exception as e:
        logger.error(f"Failed to get upcoming events: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve upcoming events",
        )


@router.post(API_ROUTES.CALENDAR.EVENTS_BULK, response_model=CalendarEventBulkResponse)
async def bulk_create_events(
    bulk_data: CalendarEventBulkCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Create multiple calendar events at once."""
    try:
        created_events = await calendar_service.bulk_create_events(
            db, events_data=bulk_data.events, creator_id=current_user.id
        )

        return CalendarEventBulkResponse(
            created_events=created_events,
            failed_events=[],
            total_created=len(created_events),
            total_failed=0,
        )

    except Exception as e:
        logger.error(f"Failed to bulk create events: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(API_ROUTES.CALENDAR.EVENTS_SEARCH)
async def search_events(
    q: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Search calendar events by title, description, or location."""
    try:
        events = await calendar_service.search_events(
            db, user_id=current_user.id, search_term=q, skip=skip, limit=limit
        )
        return {"events": events, "total": len(events)}

    except Exception as e:
        logger.error(f"Failed to search events: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search events",
        )
