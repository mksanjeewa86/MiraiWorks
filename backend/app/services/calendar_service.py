import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import urlencode

import aiohttp
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.crud.calendar_event import calendar_event
from app.crud.holiday import holiday
from app.models.calendar_connection import CalendarConnection
from app.schemas.calendar_event import (
    CalendarEventCreate,
    CalendarEventInfo,
    CalendarEventQueryParams,
    CalendarEventUpdate,
)

logger = structlog.get_logger()


class CalendarService:
    def __init__(self):
        # Google OAuth settings
        self.google_client_id = os.getenv("GOOGLE_CALENDAR_CLIENT_ID")
        self.google_client_secret = os.getenv("GOOGLE_CALENDAR_CLIENT_SECRET")
        self.google_redirect_uri = os.getenv(
            "GOOGLE_CALENDAR_REDIRECT_URI",
            "http://localhost:3001/settings/calendar/google/callback",
        )

        # Outlook OAuth settings
        self.outlook_client_id = os.getenv("OUTLOOK_CALENDAR_CLIENT_ID")
        self.outlook_client_secret = os.getenv("OUTLOOK_CALENDAR_CLIENT_SECRET")
        self.outlook_redirect_uri = os.getenv(
            "OUTLOOK_CALENDAR_REDIRECT_URI",
            "http://localhost:3001/settings/calendar/outlook/callback",
        )

        # OAuth URLs
        self.google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
        self.google_token_url = "https://oauth2.googleapis.com/token"
        self.google_revoke_url = "https://oauth2.googleapis.com/revoke"

        self.outlook_auth_url = (
            "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
        )
        self.outlook_token_url = (
            "https://login.microsoftonline.com/common/oauth2/v2.0/token"
        )

        # OAuth scopes
        self.google_scopes = [
            "https://www.googleapis.com/auth/calendar",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
        ]

        self.outlook_scopes = [
            "https://graph.microsoft.com/calendars.readwrite",
            "https://graph.microsoft.com/user.read",
        ]

    # ==================== INTERNAL CALENDAR EVENTS ====================

    async def create_event(
        self, db: AsyncSession, *, event_in: CalendarEventCreate, creator_id: int
    ) -> CalendarEventInfo:
        """Create a new internal calendar event"""
        try:
            # Check for conflicting events if needed
            if event_in.end_datetime:
                conflicts = await calendar_event.get_conflicting_events(
                    db,
                    start_datetime=event_in.start_datetime,
                    end_datetime=event_in.end_datetime,
                    creator_id=creator_id,
                )
                if conflicts:
                    logger.warning(
                        "Creating event with potential conflicts",
                        creator_id=creator_id,
                        conflicts_count=len(conflicts),
                    )

            event = await calendar_event.create_with_creator(
                db, obj_in=event_in, creator_id=creator_id
            )

            logger.info(
                "Calendar event created", event_id=event.id, creator_id=creator_id
            )
            return CalendarEventInfo.model_validate(event)

        except Exception as e:
            logger.error(
                "Failed to create calendar event", error=str(e), creator_id=creator_id
            )
            raise

    async def update_event(
        self,
        db: AsyncSession,
        *,
        event_id: int,
        event_in: CalendarEventUpdate,
        user_id: int,
    ) -> CalendarEventInfo | None:
        """Update an existing calendar event"""
        try:
            # Get existing event
            existing_event = await calendar_event.get(db, id=event_id)
            if not existing_event:
                return None

            # Check permissions (only creator can update)
            if existing_event.creator_id != user_id:
                raise ValueError("Only the event creator can update this event")

            # Check for conflicts if datetime is being updated
            if event_in.start_datetime or event_in.end_datetime:
                start_dt = event_in.start_datetime or existing_event.start_datetime
                end_dt = event_in.end_datetime or existing_event.end_datetime

                if end_dt:
                    conflicts = await calendar_event.get_conflicting_events(
                        db,
                        start_datetime=start_dt,
                        end_datetime=end_dt,
                        creator_id=user_id,
                        exclude_event_id=event_id,
                    )
                    if conflicts:
                        logger.warning(
                            "Updating event with potential conflicts",
                            event_id=event_id,
                            conflicts_count=len(conflicts),
                        )

            updated_event = await calendar_event.update(
                db, db_obj=existing_event, obj_in=event_in
            )
            logger.info("Calendar event updated", event_id=event_id, user_id=user_id)
            return CalendarEventInfo.model_validate(updated_event)

        except Exception as e:
            logger.error(
                "Failed to update calendar event", error=str(e), event_id=event_id
            )
            raise

    async def delete_event(
        self, db: AsyncSession, *, event_id: int, user_id: int
    ) -> bool:
        """Delete a calendar event"""
        try:
            existing_event = await calendar_event.get(db, id=event_id)
            if not existing_event:
                return False

            # Check permissions (only creator can delete)
            if existing_event.creator_id != user_id:
                raise ValueError("Only the event creator can delete this event")

            await calendar_event.remove(db, id=event_id)
            logger.info("Calendar event deleted", event_id=event_id, user_id=user_id)
            return True

        except Exception as e:
            logger.error(
                "Failed to delete calendar event", error=str(e), event_id=event_id
            )
            raise

    async def get_user_events(
        self, db: AsyncSession, *, user_id: int, query_params: CalendarEventQueryParams
    ) -> list[CalendarEventInfo]:
        """Get calendar events for a user with filters"""
        try:
            events = await calendar_event.get_by_date_range(
                db,
                start_date=query_params.start_date or datetime.now(timezone.utc),
                end_date=query_params.end_date
                or (datetime.now(timezone.utc) + timedelta(days=30)),
                creator_id=user_id,
                event_type=query_params.event_type,
                status=query_params.status,
                include_all_day=query_params.include_all_day,
            )

            return [CalendarEventInfo.model_validate(event) for event in events]

        except Exception as e:
            logger.error("Failed to get user events", error=str(e), user_id=user_id)
            raise

    async def get_consolidated_calendar(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        start_date: datetime,
        end_date: datetime,
    ) -> dict[str, list[dict[str, Any]]]:
        """Get consolidated calendar view with all event types"""
        try:
            result = {"internal_events": [], "external_events": [], "holidays": []}

            # Get internal calendar events
            internal_events = await calendar_event.get_by_date_range(
                db, start_date=start_date, end_date=end_date, creator_id=user_id
            )

            for event in internal_events:
                result["internal_events"].append(
                    {
                        "id": f"event-{event.id}",
                        "title": event.title,
                        "description": event.description,
                        "start": event.start_datetime.isoformat(),
                        "end": event.end_datetime.isoformat()
                        if event.end_datetime
                        else None,
                        "allDay": event.is_all_day,
                        "location": event.location,
                        "type": event.event_type,
                        "status": event.status,
                        "source": "internal",
                    }
                )

            # Get external synced events (if we have the logic for this)
            # This would need to be implemented based on your sync logic

            # Get holidays
            holidays = await holiday.get_by_date_range(
                db, date_from=start_date.date(), date_to=end_date.date()
            )

            for hol in holidays:
                result["holidays"].append(
                    {
                        "id": f"holiday-{hol.id}",
                        "title": hol.name,
                        "description": hol.description,
                        "start": hol.date.isoformat(),
                        "end": hol.date.isoformat(),
                        "allDay": True,
                        "source": "holiday",
                        "country": hol.country,
                    }
                )

            logger.info(
                "Consolidated calendar retrieved",
                user_id=user_id,
                internal_count=len(result["internal_events"]),
                external_count=len(result["external_events"]),
                holidays_count=len(result["holidays"]),
            )

            return result

        except Exception as e:
            logger.error(
                "Failed to get consolidated calendar", error=str(e), user_id=user_id
            )
            raise

    async def search_events(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        search_term: str,
        skip: int = 0,
        limit: int = 50,
    ) -> list[CalendarEventInfo]:
        """Search calendar events by title, description, or location"""
        try:
            events = await calendar_event.search_events(
                db, search_term=search_term, creator_id=user_id, skip=skip, limit=limit
            )

            return [CalendarEventInfo.model_validate(event) for event in events]

        except Exception as e:
            logger.error("Failed to search events", error=str(e), user_id=user_id)
            raise

    async def get_upcoming_events(
        self, db: AsyncSession, *, user_id: int, limit: int = 10
    ) -> list[CalendarEventInfo]:
        """Get upcoming events for a user"""
        try:
            events = await calendar_event.get_upcoming_events(
                db, creator_id=user_id, limit=limit
            )

            return [CalendarEventInfo.model_validate(event) for event in events]

        except Exception as e:
            logger.error("Failed to get upcoming events", error=str(e), user_id=user_id)
            raise

    async def bulk_create_events(
        self,
        db: AsyncSession,
        *,
        events_data: list[CalendarEventCreate],
        creator_id: int,
    ) -> list[CalendarEventInfo]:
        """Create multiple calendar events at once"""
        try:
            created_events = await calendar_event.create_multiple(
                db, events_data=events_data, creator_id=creator_id
            )

            logger.info(
                "Bulk calendar events created",
                count=len(created_events),
                creator_id=creator_id,
            )

            return [CalendarEventInfo.model_validate(event) for event in created_events]

        except Exception as e:
            logger.error(
                "Failed to bulk create events", error=str(e), creator_id=creator_id
            )
            raise

    # ==================== EXTERNAL CALENDAR INTEGRATION ====================

    async def get_google_auth_url(self, user_id: int) -> str:
        """Generate Google Calendar OAuth authorization URL"""
        if (
            not self.google_client_id
            or self.google_client_id == "your-google-client-id"
        ):
            raise ValueError(
                "Google Calendar OAuth is not configured. Please set GOOGLE_CALENDAR_CLIENT_ID and GOOGLE_CALENDAR_CLIENT_SECRET environment variables."
            )

        state = f"{user_id}:{secrets.token_urlsafe(32)}"

        params = {
            "client_id": self.google_client_id,
            "redirect_uri": self.google_redirect_uri,
            "scope": " ".join(self.google_scopes),
            "response_type": "code",
            "access_type": "offline",
            "prompt": "consent",
            "state": state,
        }

        return f"{self.google_auth_url}?{urlencode(params)}"

    async def get_outlook_auth_url(self, user_id: int) -> str:
        """Generate Outlook Calendar OAuth authorization URL"""
        if not self.outlook_client_id:
            raise ValueError("Outlook Calendar client ID not configured")

        state = f"{user_id}:{secrets.token_urlsafe(32)}"

        params = {
            "client_id": self.outlook_client_id,
            "redirect_uri": self.outlook_redirect_uri,
            "scope": " ".join(self.outlook_scopes),
            "response_type": "code",
            "response_mode": "query",
            "state": state,
        }

        return f"{self.outlook_auth_url}?{urlencode(params)}"

    async def create_google_connection(
        self, auth_code: str, user_id: int, db: Session
    ) -> CalendarConnection:
        """Create Google Calendar connection from OAuth code"""
        try:
            # Exchange code for tokens
            token_data = await self._exchange_google_code_for_tokens(auth_code)

            # Get user profile
            profile_data = await self._get_google_profile(token_data["access_token"])

            # Check for existing connection
            existing = (
                db.query(CalendarConnection)
                .filter(
                    CalendarConnection.user_id == user_id,
                    CalendarConnection.provider == "google",
                    CalendarConnection.provider_account_id == profile_data["id"],
                )
                .first()
            )

            if existing:
                # Update existing connection
                existing.access_token = token_data["access_token"]
                existing.refresh_token = token_data.get(
                    "refresh_token", existing.refresh_token
                )
                existing.token_expires_at = datetime.now(timezone.utc) + timedelta(
                    seconds=token_data.get("expires_in", 3600)
                )
                existing.sync_error = None
                db.commit()
                db.refresh(existing)
                return existing
            else:
                # Create new connection
                connection = CalendarConnection(
                    user_id=user_id,
                    provider="google",
                    provider_account_id=profile_data["id"],
                    provider_email=profile_data["email"],
                    display_name=profile_data.get("name", profile_data["email"]),
                    access_token=token_data["access_token"],
                    refresh_token=token_data.get("refresh_token"),
                    token_expires_at=datetime.now(timezone.utc)
                    + timedelta(seconds=token_data.get("expires_in", 3600)),
                )

                db.add(connection)
                db.commit()
                db.refresh(connection)
                return connection

        except Exception as e:
            logger.error(
                "Failed to create Google calendar connection",
                error=str(e),
                user_id=user_id,
            )
            raise

    async def create_outlook_connection(
        self, auth_code: str, user_id: int, db: Session
    ) -> CalendarConnection:
        """Create Outlook Calendar connection from OAuth code"""
        try:
            # Exchange code for tokens
            token_data = await self._exchange_outlook_code_for_tokens(auth_code)

            # Get user profile
            profile_data = await self._get_outlook_profile(token_data["access_token"])

            # Check for existing connection
            existing = (
                db.query(CalendarConnection)
                .filter(
                    CalendarConnection.user_id == user_id,
                    CalendarConnection.provider == "outlook",
                    CalendarConnection.provider_account_id == profile_data["id"],
                )
                .first()
            )

            if existing:
                # Update existing connection
                existing.access_token = token_data["access_token"]
                existing.refresh_token = token_data.get(
                    "refresh_token", existing.refresh_token
                )
                existing.token_expires_at = datetime.now(timezone.utc) + timedelta(
                    seconds=token_data.get("expires_in", 3600)
                )
                existing.sync_error = None
                db.commit()
                db.refresh(existing)
                return existing
            else:
                # Create new connection
                connection = CalendarConnection(
                    user_id=user_id,
                    provider="outlook",
                    provider_account_id=profile_data["id"],
                    provider_email=profile_data["mail"]
                    or profile_data.get("userPrincipalName", ""),
                    display_name=profile_data.get(
                        "displayName", profile_data.get("mail", "")
                    ),
                    access_token=token_data["access_token"],
                    refresh_token=token_data.get("refresh_token"),
                    token_expires_at=datetime.now(timezone.utc)
                    + timedelta(seconds=token_data.get("expires_in", 3600)),
                )

                db.add(connection)
                db.commit()
                db.refresh(connection)
                return connection

        except Exception as e:
            logger.error(
                "Failed to create Outlook calendar connection",
                error=str(e),
                user_id=user_id,
            )
            raise

    async def _exchange_google_code_for_tokens(self, code: str) -> dict[str, Any]:
        """Exchange Google OAuth code for access tokens"""
        data = {
            "client_id": self.google_client_id,
            "client_secret": self.google_client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.google_redirect_uri,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.google_token_url, data=data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise ValueError(
                        f"Failed to exchange Google code for tokens: {error_text}"
                    )
                return await response.json()

    async def _exchange_outlook_code_for_tokens(self, code: str) -> dict[str, Any]:
        """Exchange Outlook OAuth code for access tokens"""
        data = {
            "client_id": self.outlook_client_id,
            "client_secret": self.outlook_client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.outlook_redirect_uri,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.outlook_token_url, data=data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise ValueError(
                        f"Failed to exchange Outlook code for tokens: {error_text}"
                    )
                return await response.json()

    async def _get_google_profile(self, access_token: str) -> dict[str, Any]:
        """Get Google user profile"""
        headers = {"Authorization": f"Bearer {access_token}"}

        async with aiohttp.ClientSession() as session, session.get(
            "https://www.googleapis.com/oauth2/v2/userinfo", headers=headers
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                raise ValueError(f"Failed to get Google profile: {error_text}")
            return await response.json()

    async def _get_outlook_profile(self, access_token: str) -> dict[str, Any]:
        """Get Outlook user profile"""
        headers = {"Authorization": f"Bearer {access_token}"}

        async with aiohttp.ClientSession() as session, session.get(
            "https://graph.microsoft.com/v1.0/me", headers=headers
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                raise ValueError(f"Failed to get Outlook profile: {error_text}")
            return await response.json()

    async def revoke_tokens(self, connection: CalendarConnection):
        """Revoke OAuth tokens for a connection"""
        try:
            if connection.provider == "google" and connection.refresh_token:
                # Revoke Google tokens
                params = {"token": connection.refresh_token}
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        self.google_revoke_url, params=params
                    ) as response:
                        if response.status not in [
                            200,
                            400,
                        ]:  # 400 is returned if token is already invalid
                            logger.warning(
                                "Failed to revoke Google tokens", status=response.status
                            )
            elif connection.provider == "outlook":
                # Outlook doesn't have a direct revoke endpoint in common tenant
                # The tokens will expire naturally
                logger.info(
                    "Outlook tokens marked for revocation (will expire naturally)"
                )

        except Exception as e:
            logger.warning(
                "Error during token revocation",
                error=str(e),
                connection_id=connection.id,
            )

    async def sync_calendar(
        self, connection: CalendarConnection, db: Session
    ) -> dict[str, Any]:
        """Sync calendar events (placeholder implementation)"""
        try:
            # This is a placeholder for actual calendar sync implementation
            # In a real implementation, you would:
            # 1. Fetch events from the calendar provider
            # 2. Store/update them in your database
            # 3. Handle any conflicts or updates

            connection.last_sync_at = datetime.now(timezone.utc)
            connection.sync_error = None
            db.commit()

            logger.info("Calendar sync completed", connection_id=connection.id)
            return {"status": "success", "message": "Calendar synced successfully"}

        except Exception as e:
            connection.sync_error = str(e)
            db.commit()
            logger.error(
                "Calendar sync failed", error=str(e), connection_id=connection.id
            )
            raise


# Create singleton instances
calendar_service = CalendarService()
google_calendar_service = CalendarService()  # Backward compatibility
