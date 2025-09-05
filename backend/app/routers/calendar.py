import logging
from datetime import datetime
from datetime import timedelta
from typing import List
from typing import Optional

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from fastapi import Request
from fastapi import status
from sqlalchemy import and_
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.calendar_integration import ExternalCalendarAccount
from app.models.user import User
from app.schemas.calendar import CalendarAccountInfo
from app.schemas.calendar import CalendarInfo
from app.schemas.calendar import CalendarSyncRequest
from app.schemas.calendar import CalendarSyncResponse
from app.schemas.calendar import CalendarWebhookData
from app.schemas.calendar import EventInfo
from app.schemas.calendar import EventsListRequest
from app.schemas.calendar import EventsListResponse
from app.services.calendar_service import google_calendar_service
from app.services.microsoft_calendar_service import microsoft_calendar_service

router = APIRouter()
logger = logging.getLogger(__name__)


# OAuth endpoints
@router.get("/oauth/google/start")
async def start_google_oauth(
    current_user: User = Depends(get_current_active_user),
    state: Optional[str] = None
):
    """Start Google Calendar OAuth flow."""
    auth_url = google_calendar_service.get_auth_url(current_user.id, state)
    return {"auth_url": auth_url}


@router.get("/oauth/google/callback")
async def google_oauth_callback(
    code: str = Query(...),
    state: Optional[str] = Query(None),
    error: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Handle Google OAuth callback."""
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth error: {error}"
        )
    
    # Exchange code for tokens
    tokens = await google_calendar_service.exchange_code_for_tokens(code)
    
    # Get user info
    user_info = await google_calendar_service.get_user_info(tokens["access_token"])
    
    # Find user by state parameter or email
    user_id = int(state) if state and state.isdigit() else None
    if not user_id:
        # Try to find user by email
        user_result = await db.execute(
            select(User).where(User.email == user_info["email"])
        )
        user = user_result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        user_id = user.id
    
    # Check if calendar account already exists
    existing_account = await db.execute(
        select(ExternalCalendarAccount).where(
            and_(
                ExternalCalendarAccount.user_id == user_id,
                ExternalCalendarAccount.provider == "google",
                ExternalCalendarAccount.provider_account_id == user_info["id"]
            )
        )
    )
    
    account = existing_account.scalar_one_or_none()
    
    if account:
        # Update existing account
        account.access_token = tokens["access_token"]
        account.refresh_token = tokens.get("refresh_token", account.refresh_token)
        account.token_expires_at = datetime.utcnow() + timedelta(seconds=tokens.get("expires_in", 3600))
        account.is_active = True
        account.sync_enabled = True
        account.email = user_info["email"]
        account.display_name = user_info.get("name")
    else:
        # Create new account
        account = ExternalCalendarAccount(
            user_id=user_id,
            provider="google",
            provider_account_id=user_info["id"],
            email=user_info["email"],
            display_name=user_info.get("name"),
            access_token=tokens["access_token"],
            refresh_token=tokens.get("refresh_token"),
            token_expires_at=datetime.utcnow() + timedelta(seconds=tokens.get("expires_in", 3600)),
            is_active=True,
            sync_enabled=True
        )
        db.add(account)
    
    await db.commit()
    await db.refresh(account)
    
    # Set up webhook
    try:
        webhook_data = await google_calendar_service.create_webhook_watch(account)
        if webhook_data:
            account.webhook_id = webhook_data.get("id")
            account.webhook_expires_at = datetime.fromtimestamp(webhook_data.get("expiration", 0) / 1000)
            await db.commit()
    except Exception as e:
        logger.warning(f"Failed to set up Google Calendar webhook: {e}")
    
    return {"message": "Google Calendar connected successfully", "account_id": account.id}


@router.get("/oauth/microsoft/start")
async def start_microsoft_oauth(
    current_user: User = Depends(get_current_active_user),
    state: Optional[str] = None
):
    """Start Microsoft Calendar OAuth flow."""
    auth_url = microsoft_calendar_service.get_auth_url(current_user.id, state)
    return {"auth_url": auth_url}


@router.get("/oauth/microsoft/callback")
async def microsoft_oauth_callback(
    code: str = Query(...),
    state: Optional[str] = Query(None),
    error: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Handle Microsoft OAuth callback."""
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth error: {error}"
        )
    
    # Exchange code for tokens
    tokens = await microsoft_calendar_service.exchange_code_for_tokens(code)
    
    # Get user info
    user_info = await microsoft_calendar_service.get_user_info(tokens["access_token"])
    
    # Find user by state parameter or email
    user_id = int(state) if state and state.isdigit() else None
    if not user_id:
        # Try to find user by email
        user_result = await db.execute(
            select(User).where(User.email == user_info["mail"] or user_info["userPrincipalName"])
        )
        user = user_result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        user_id = user.id
    
    # Check if calendar account already exists
    existing_account = await db.execute(
        select(ExternalCalendarAccount).where(
            and_(
                ExternalCalendarAccount.user_id == user_id,
                ExternalCalendarAccount.provider == "microsoft",
                ExternalCalendarAccount.provider_account_id == user_info["id"]
            )
        )
    )
    
    account = existing_account.scalar_one_or_none()
    
    if account:
        # Update existing account
        account.access_token = tokens["access_token"]
        account.refresh_token = tokens.get("refresh_token", account.refresh_token)
        account.token_expires_at = datetime.utcnow() + timedelta(seconds=tokens.get("expires_in", 3600))
        account.is_active = True
        account.sync_enabled = True
        account.email = user_info.get("mail", user_info.get("userPrincipalName"))
        account.display_name = user_info.get("displayName")
    else:
        # Create new account
        account = ExternalCalendarAccount(
            user_id=user_id,
            provider="microsoft",
            provider_account_id=user_info["id"],
            email=user_info.get("mail", user_info.get("userPrincipalName")),
            display_name=user_info.get("displayName"),
            access_token=tokens["access_token"],
            refresh_token=tokens.get("refresh_token"),
            token_expires_at=datetime.utcnow() + timedelta(seconds=tokens.get("expires_in", 3600)),
            is_active=True,
            sync_enabled=True
        )
        db.add(account)
    
    await db.commit()
    await db.refresh(account)
    
    # Set up webhook
    try:
        subscription_data = await microsoft_calendar_service.create_webhook_subscription(account)
        if subscription_data:
            account.webhook_id = subscription_data.get("id")
            account.webhook_expires_at = datetime.fromisoformat(subscription_data.get("expirationDateTime").replace("Z", "+00:00"))
            await db.commit()
    except Exception as e:
        logger.warning(f"Failed to set up Microsoft Calendar webhook: {e}")
    
    return {"message": "Microsoft Calendar connected successfully", "account_id": account.id}


# Calendar account management
@router.get("/accounts", response_model=List[CalendarAccountInfo])
async def get_calendar_accounts(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's connected calendar accounts."""
    result = await db.execute(
        select(ExternalCalendarAccount).where(
            ExternalCalendarAccount.user_id == current_user.id,
            ExternalCalendarAccount.is_active == True
        ).order_by(ExternalCalendarAccount.created_at)
    )
    
    accounts = result.scalars().all()
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
            created_at=account.created_at
        )
        for account in accounts
    ]


@router.delete("/accounts/{account_id}")
async def disconnect_calendar_account(
    account_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Disconnect a calendar account."""
    # Get account
    result = await db.execute(
        select(ExternalCalendarAccount).where(
            and_(
                ExternalCalendarAccount.id == account_id,
                ExternalCalendarAccount.user_id == current_user.id
            )
        )
    )
    
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar account not found"
        )
    
    # Deactivate account
    account.is_active = False
    account.sync_enabled = False
    
    # Clean up webhook (optional - let it expire naturally)
    
    await db.commit()
    
    return {"message": "Calendar account disconnected successfully"}


@router.post("/accounts/{account_id}/sync", response_model=CalendarSyncResponse)
async def sync_calendar_account(
    account_id: int,
    sync_request: CalendarSyncRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Manually trigger calendar sync."""
    # Get account
    result = await db.execute(
        select(ExternalCalendarAccount).where(
            and_(
                ExternalCalendarAccount.id == account_id,
                ExternalCalendarAccount.user_id == current_user.id,
                ExternalCalendarAccount.is_active == True
            )
        )
    )
    
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar account not found"
        )
    
    # Trigger sync (this would typically be done by a background worker)
    try:
        if account.provider == "google":
            events = await google_calendar_service.get_events(
                account,
                time_min=datetime.utcnow() - timedelta(days=30),
                time_max=datetime.utcnow() + timedelta(days=90)
            )
        elif account.provider == "microsoft":
            events = await microsoft_calendar_service.get_events(
                account,
                time_min=datetime.utcnow() - timedelta(days=30),
                time_max=datetime.utcnow() + timedelta(days=90)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported calendar provider"
            )
        
        # Update last sync time
        account.last_sync_at = datetime.utcnow()
        await db.commit()
        
        return CalendarSyncResponse(
            success=True,
            synced_events=len(events),
            errors=[]
        )
        
    except Exception as e:
        logger.error(f"Calendar sync failed for account {account_id}: {e}")
        return CalendarSyncResponse(
            success=False,
            synced_events=0,
            errors=[str(e)]
        )


@router.get("/calendars")
async def get_calendars(
    account_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get available calendars for user's accounts."""
    query = select(ExternalCalendarAccount).where(
        ExternalCalendarAccount.user_id == current_user.id,
        ExternalCalendarAccount.is_active == True
    )
    
    if account_id:
        query = query.where(ExternalCalendarAccount.id == account_id)
    
    result = await db.execute(query)
    accounts = result.scalars().all()
    
    all_calendars = []
    
    for account in accounts:
        try:
            if account.provider == "google":
                calendars = await google_calendar_service.get_calendars(account)
                for cal in calendars:
                    all_calendars.append(CalendarInfo(
                        id=cal["id"],
                        name=cal.get("summary", ""),
                        description=cal.get("description"),
                        primary=cal.get("primary", False),
                        timezone=cal.get("timeZone"),
                        access_role=cal.get("accessRole")
                    ))
                    
            elif account.provider == "microsoft":
                calendars = await microsoft_calendar_service.get_calendars(account)
                for cal in calendars:
                    all_calendars.append(CalendarInfo(
                        id=cal["id"],
                        name=cal.get("name", ""),
                        description=None,
                        primary=cal.get("isDefaultCalendar", False),
                        timezone=None,
                        access_role="owner"
                    ))
                    
        except Exception as e:
            logger.error(f"Failed to get calendars for account {account.id}: {e}")
    
    return {"calendars": all_calendars}


@router.get("/events", response_model=EventsListResponse)
async def get_events(
    request: EventsListRequest = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get calendar events."""
    # Get user's calendar accounts
    accounts_result = await db.execute(
        select(ExternalCalendarAccount).where(
            ExternalCalendarAccount.user_id == current_user.id,
            ExternalCalendarAccount.is_active == True,
            ExternalCalendarAccount.sync_enabled == True
        )
    )
    accounts = accounts_result.scalars().all()
    
    all_events = []
    
    for account in accounts:
        try:
            if account.provider == "google":
                events = await google_calendar_service.get_events(
                    account,
                    request.calendar_id or "primary",
                    request.start_date,
                    request.end_date,
                    request.max_results
                )
                
                for event in events:
                    # Parse Google Calendar event format
                    start_dt = event.get("start", {})
                    end_dt = event.get("end", {})
                    
                    start_datetime = datetime.fromisoformat(
                        start_dt.get("dateTime", start_dt.get("date", "")).replace("Z", "+00:00")
                    )
                    end_datetime = datetime.fromisoformat(
                        end_dt.get("dateTime", end_dt.get("date", "")).replace("Z", "+00:00")
                    )
                    
                    all_events.append(EventInfo(
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
                        attendees=[att.get("email", "") for att in event.get("attendees", [])],
                        status=event.get("status"),
                        created_at=datetime.fromisoformat(event.get("created", "").replace("Z", "+00:00")),
                        updated_at=datetime.fromisoformat(event.get("updated", "").replace("Z", "+00:00"))
                    ))
                    
            elif account.provider == "microsoft":
                events = await microsoft_calendar_service.get_events(
                    account,
                    request.calendar_id,
                    request.start_date,
                    request.end_date,
                    request.max_results
                )
                
                for event in events:
                    start_datetime = datetime.fromisoformat(
                        event["start"]["dateTime"].replace("Z", "+00:00")
                    )
                    end_datetime = datetime.fromisoformat(
                        event["end"]["dateTime"].replace("Z", "+00:00")
                    )
                    
                    all_events.append(EventInfo(
                        id=event["id"],
                        title=event.get("subject", ""),
                        description=event.get("body", {}).get("content"),
                        location=event.get("location", {}).get("displayName"),
                        start_datetime=start_datetime,
                        end_datetime=end_datetime,
                        timezone=event["start"].get("timeZone", "UTC"),
                        is_all_day=event.get("isAllDay", False),
                        is_recurring=event.get("recurrence") is not None,
                        organizer_email=event.get("organizer", {}).get("emailAddress", {}).get("address"),
                        attendees=[att.get("emailAddress", {}).get("address", "") for att in event.get("attendees", [])],
                        status=event.get("showAs"),
                        created_at=datetime.fromisoformat(event.get("createdDateTime", "").replace("Z", "+00:00")),
                        updated_at=datetime.fromisoformat(event.get("lastModifiedDateTime", "").replace("Z", "+00:00"))
                    ))
                    
        except Exception as e:
            logger.error(f"Failed to get events for account {account.id}: {e}")
    
    # Sort by start time
    all_events.sort(key=lambda x: x.start_datetime)
    
    return EventsListResponse(
        events=all_events[:request.max_results],
        has_more=len(all_events) > request.max_results
    )


# Webhook endpoints
@router.post("/webhooks/google")
async def google_calendar_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
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


@router.post("/webhooks/microsoft")
async def microsoft_calendar_webhook(
    webhook_data: CalendarWebhookData,
    validation_token: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
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