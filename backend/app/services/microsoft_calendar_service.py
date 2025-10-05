import logging
from datetime import datetime, timedelta
from typing import Any

import httpx
from fastapi import HTTPException, status
from sqlalchemy import update

from app.config import settings
from app.models.calendar_integration import ExternalCalendarAccount
from app.utils.datetime_utils import get_utc_now

logger = logging.getLogger(__name__)


class MicrosoftCalendarService:
    """Microsoft Graph Calendar integration service."""

    def __init__(self):
        self.client_id = settings.ms_oauth_client_id
        self.client_secret = settings.ms_oauth_client_secret
        self.redirect_uri = (
            f"{settings.app_base_url}/api/calendar/oauth/microsoft/callback"
        )

        # Microsoft Graph endpoints
        self.oauth_url = (
            "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
        )
        self.token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
        self.graph_api_base = "https://graph.microsoft.com/v1.0"

    def get_auth_url(self, user_id: int, state: str = None) -> str:
        """Generate Microsoft OAuth authorization URL."""
        scopes = [
            "https://graph.microsoft.com/User.Read",
            "https://graph.microsoft.com/Calendars.ReadWrite",
            "https://graph.microsoft.com/Calendars.Read.Shared",
            "offline_access",
        ]

        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(scopes),
            "response_mode": "query",
            "state": state or str(user_id),
        }

        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.oauth_url}?{query_string}"

    async def exchange_code_for_tokens(self, code: str) -> dict[str, Any]:
        """Exchange authorization code for access/refresh tokens."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.token_url,
                    data={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "code": code,
                        "grant_type": "authorization_code",
                        "redirect_uri": self.redirect_uri,
                    },
                )

                if response.status_code != 200:
                    logger.error(f"Token exchange failed: {response.text}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Failed to exchange authorization code",
                    )

                return response.json()

        except httpx.HTTPError as e:
            logger.error(f"HTTP error during token exchange: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Calendar service temporarily unavailable",
            )

    async def get_user_info(self, access_token: str) -> dict[str, Any]:
        """Get user information from Microsoft Graph."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.graph_api_base}/me",
                    headers={"Authorization": f"Bearer {access_token}"},
                )

                if response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Failed to get user info",
                    )

                return response.json()

        except httpx.HTTPError as e:
            logger.error(f"Error getting user info: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Calendar service temporarily unavailable",
            )

    async def refresh_access_token(self, refresh_token: str) -> dict[str, Any]:
        """Refresh access token using refresh token."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.token_url,
                    data={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "refresh_token": refresh_token,
                        "grant_type": "refresh_token",
                    },
                )

                if response.status_code != 200:
                    logger.error(f"Token refresh failed: {response.text}")
                    return None

                return response.json()

        except httpx.HTTPError as e:
            logger.error(f"Error refreshing token: {e}")
            return None

    async def _ensure_valid_token(
        self, calendar_account: ExternalCalendarAccount
    ) -> str:
        """Ensure calendar account has a valid access token."""
        # Check if token is expired (with 5 minute buffer)
        if (
            calendar_account.token_expires_at
            and calendar_account.token_expires_at
            <= get_utc_now() + timedelta(minutes=5)
        ):
            # Refresh the token
            token_data = await self.refresh_access_token(calendar_account.refresh_token)
            if not token_data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Calendar access token expired and refresh failed",
                )

            # Update the token in database
            from app.database import AsyncSessionLocal

            async with AsyncSessionLocal() as db:
                await db.execute(
                    update(ExternalCalendarAccount)
                    .where(ExternalCalendarAccount.id == calendar_account.id)
                    .values(
                        access_token=token_data["access_token"],
                        token_expires_at=get_utc_now()
                        + timedelta(seconds=token_data.get("expires_in", 3600)),
                    )
                )
                await db.commit()

            return token_data["access_token"]

        return calendar_account.access_token

    async def get_calendars(
        self, calendar_account: ExternalCalendarAccount
    ) -> list[dict[str, Any]]:
        """Get list of user's calendars."""
        access_token = await self._ensure_valid_token(calendar_account)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.graph_api_base}/me/calendars",
                    headers={"Authorization": f"Bearer {access_token}"},
                )

                if response.status_code != 200:
                    logger.error(f"Failed to get calendars: {response.text}")
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="Failed to fetch calendars",
                    )

                data = response.json()
                return data.get("value", [])

        except httpx.HTTPError as e:
            logger.error(f"Error fetching calendars: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Calendar service temporarily unavailable",
            )

    async def get_events(
        self,
        calendar_account: ExternalCalendarAccount,
        calendar_id: str = None,
        time_min: datetime | None = None,
        time_max: datetime | None = None,
        max_results: int = 100,
    ) -> list[dict[str, Any]]:
        """Get events from calendar."""
        access_token = await self._ensure_valid_token(calendar_account)

        # Use default calendar if not specified
        calendar_endpoint = f"{self.graph_api_base}/me/calendar/events"
        if calendar_id:
            calendar_endpoint = (
                f"{self.graph_api_base}/me/calendars/{calendar_id}/events"
            )

        params = {"$top": max_results, "$orderby": "start/dateTime"}

        # Add time filters
        filters = []
        if time_min:
            filters.append(f"start/dateTime ge '{time_min.isoformat()}'")
        if time_max:
            filters.append(f"end/dateTime le '{time_max.isoformat()}'")

        if filters:
            params["$filter"] = " and ".join(filters)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    calendar_endpoint,
                    headers={"Authorization": f"Bearer {access_token}"},
                    params=params,
                )

                if response.status_code != 200:
                    logger.error(f"Failed to get events: {response.text}")
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="Failed to fetch calendar events",
                    )

                data = response.json()
                return data.get("value", [])

        except httpx.HTTPError as e:
            logger.error(f"Error fetching events: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Calendar service temporarily unavailable",
            )

    async def create_event(
        self,
        calendar_account: ExternalCalendarAccount,
        event_data: dict[str, Any],
        calendar_id: str = None,
    ) -> dict[str, Any]:
        """Create event in calendar."""
        access_token = await self._ensure_valid_token(calendar_account)

        # Use default calendar if not specified
        calendar_endpoint = f"{self.graph_api_base}/me/calendar/events"
        if calendar_id:
            calendar_endpoint = (
                f"{self.graph_api_base}/me/calendars/{calendar_id}/events"
            )

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    calendar_endpoint,
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json",
                    },
                    json=event_data,
                )

                if response.status_code not in [200, 201]:
                    logger.error(f"Failed to create event: {response.text}")
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="Failed to create calendar event",
                    )

                return response.json()

        except httpx.HTTPError as e:
            logger.error(f"Error creating event: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Calendar service temporarily unavailable",
            )

    async def update_event(
        self,
        calendar_account: ExternalCalendarAccount,
        event_id: str,
        event_data: dict[str, Any],
        calendar_id: str = None,
    ) -> dict[str, Any]:
        """Update event in calendar."""
        access_token = await self._ensure_valid_token(calendar_account)

        # Use default calendar if not specified
        calendar_endpoint = f"{self.graph_api_base}/me/calendar/events/{event_id}"
        if calendar_id:
            calendar_endpoint = (
                f"{self.graph_api_base}/me/calendars/{calendar_id}/events/{event_id}"
            )

        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    calendar_endpoint,
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json",
                    },
                    json=event_data,
                )

                if response.status_code != 200:
                    logger.error(f"Failed to update event: {response.text}")
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="Failed to update calendar event",
                    )

                return response.json()

        except httpx.HTTPError as e:
            logger.error(f"Error updating event: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Calendar service temporarily unavailable",
            )

    async def delete_event(
        self,
        calendar_account: ExternalCalendarAccount,
        event_id: str,
        calendar_id: str = None,
    ) -> bool:
        """Delete event from calendar."""
        access_token = await self._ensure_valid_token(calendar_account)

        # Use default calendar if not specified
        calendar_endpoint = f"{self.graph_api_base}/me/calendar/events/{event_id}"
        if calendar_id:
            calendar_endpoint = (
                f"{self.graph_api_base}/me/calendars/{calendar_id}/events/{event_id}"
            )

        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    calendar_endpoint,
                    headers={"Authorization": f"Bearer {access_token}"},
                )

                return response.status_code in [200, 204, 404]  # 404 = already deleted

        except httpx.HTTPError as e:
            logger.error(f"Error deleting event: {e}")
            return False

    async def create_webhook_subscription(
        self, calendar_account: ExternalCalendarAccount, calendar_id: str = None
    ) -> dict[str, Any] | None:
        """Create webhook subscription for calendar changes."""
        access_token = await self._ensure_valid_token(calendar_account)

        webhook_url = f"{settings.app_base_url}/api/calendar/webhooks/microsoft"

        # Resource to watch (default calendar events or specific calendar)
        resource = "me/calendar/events"
        if calendar_id:
            resource = f"me/calendars/{calendar_id}/events"

        subscription_data = {
            "changeType": "created,updated,deleted",
            "notificationUrl": webhook_url,
            "resource": resource,
            "expirationDateTime": (get_utc_now() + timedelta(days=3)).isoformat() + "Z",
            "clientState": f"user_{calendar_account.user_id}",  # For verification
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.graph_api_base}/subscriptions",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json",
                    },
                    json=subscription_data,
                )

                if response.status_code in [200, 201]:
                    return response.json()
                else:
                    logger.error(f"Failed to create subscription: {response.text}")
                    return None

        except httpx.HTTPError as e:
            logger.error(f"Error creating subscription: {e}")
            return None


# Global instance
microsoft_calendar_service = MicrosoftCalendarService()
