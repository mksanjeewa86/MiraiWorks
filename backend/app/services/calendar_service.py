import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from fastapi import HTTPException, status
import httpx
from app.config import settings
from app.models.calendar_integration import ExternalCalendarAccount, SyncedEvent
from app.models.user import User
from app.utils.constants import UserRole

logger = logging.getLogger(__name__)


class GoogleCalendarService:
    """Google Calendar integration service."""
    
    def __init__(self):
        self.client_id = settings.google_oauth_client_id
        self.client_secret = settings.google_oauth_client_secret
        self.redirect_uri = f"{settings.app_base_url}/api/calendar/oauth/google/callback"
        
        # Google Calendar API endpoints
        self.oauth_url = "https://accounts.google.com/o/oauth2/v2/auth"
        self.token_url = "https://oauth2.googleapis.com/token"
        self.calendar_api_base = "https://www.googleapis.com/calendar/v3"
        self.userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    
    def get_auth_url(self, user_id: int, state: str = None) -> str:
        """Generate Google OAuth authorization URL."""
        scopes = [
            "https://www.googleapis.com/auth/calendar",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile"
        ]
        
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(scopes),
            "access_type": "offline",
            "prompt": "consent",
            "state": state or str(user_id)
        }
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.oauth_url}?{query_string}"
    
    async def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access/refresh tokens."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.token_url, data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": self.redirect_uri
                })
                
                if response.status_code != 200:
                    logger.error(f"Token exchange failed: {response.text}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Failed to exchange authorization code"
                    )
                
                return response.json()
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error during token exchange: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Calendar service temporarily unavailable"
            )
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from Google."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.userinfo_url,
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Failed to get user info"
                    )
                
                return response.json()
                
        except httpx.HTTPError as e:
            logger.error(f"Error getting user info: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Calendar service temporarily unavailable"
            )
    
    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token using refresh token."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.token_url, data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token"
                })
                
                if response.status_code != 200:
                    logger.error(f"Token refresh failed: {response.text}")
                    return None
                
                return response.json()
                
        except httpx.HTTPError as e:
            logger.error(f"Error refreshing token: {e}")
            return None
    
    async def _ensure_valid_token(self, calendar_account: ExternalCalendarAccount) -> str:
        """Ensure calendar account has a valid access token."""
        # Check if token is expired (with 5 minute buffer)
        if (calendar_account.token_expires_at and 
            calendar_account.token_expires_at <= datetime.utcnow() + timedelta(minutes=5)):
            
            # Refresh the token
            token_data = await self.refresh_access_token(calendar_account.refresh_token)
            if not token_data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Calendar access token expired and refresh failed"
                )
            
            # Update the token in database
            from app.database import AsyncSessionLocal
            async with AsyncSessionLocal() as db:
                await db.execute(
                    update(ExternalCalendarAccount)
                    .where(ExternalCalendarAccount.id == calendar_account.id)
                    .values(
                        access_token=token_data["access_token"],
                        token_expires_at=datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 3600))
                    )
                )
                await db.commit()
            
            return token_data["access_token"]
        
        return calendar_account.access_token
    
    async def get_calendars(self, calendar_account: ExternalCalendarAccount) -> List[Dict[str, Any]]:
        """Get list of user's calendars."""
        access_token = await self._ensure_valid_token(calendar_account)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.calendar_api_base}/users/me/calendarList",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                
                if response.status_code != 200:
                    logger.error(f"Failed to get calendars: {response.text}")
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="Failed to fetch calendars"
                    )
                
                data = response.json()
                return data.get("items", [])
                
        except httpx.HTTPError as e:
            logger.error(f"Error fetching calendars: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Calendar service temporarily unavailable"
            )
    
    async def get_events(
        self,
        calendar_account: ExternalCalendarAccount,
        calendar_id: str = "primary",
        time_min: Optional[datetime] = None,
        time_max: Optional[datetime] = None,
        max_results: int = 100
    ) -> List[Dict[str, Any]]:
        """Get events from calendar."""
        access_token = await self._ensure_valid_token(calendar_account)
        
        params = {
            "maxResults": max_results,
            "singleEvents": True,
            "orderBy": "startTime"
        }
        
        if time_min:
            params["timeMin"] = time_min.isoformat() + "Z"
        if time_max:
            params["timeMax"] = time_max.isoformat() + "Z"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.calendar_api_base}/calendars/{calendar_id}/events",
                    headers={"Authorization": f"Bearer {access_token}"},
                    params=params
                )
                
                if response.status_code != 200:
                    logger.error(f"Failed to get events: {response.text}")
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="Failed to fetch calendar events"
                    )
                
                data = response.json()
                return data.get("items", [])
                
        except httpx.HTTPError as e:
            logger.error(f"Error fetching events: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Calendar service temporarily unavailable"
            )
    
    async def create_event(
        self,
        calendar_account: ExternalCalendarAccount,
        event_data: Dict[str, Any],
        calendar_id: str = "primary"
    ) -> Dict[str, Any]:
        """Create event in calendar."""
        access_token = await self._ensure_valid_token(calendar_account)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.calendar_api_base}/calendars/{calendar_id}/events",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    },
                    json=event_data
                )
                
                if response.status_code not in [200, 201]:
                    logger.error(f"Failed to create event: {response.text}")
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="Failed to create calendar event"
                    )
                
                return response.json()
                
        except httpx.HTTPError as e:
            logger.error(f"Error creating event: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Calendar service temporarily unavailable"
            )
    
    async def update_event(
        self,
        calendar_account: ExternalCalendarAccount,
        event_id: str,
        event_data: Dict[str, Any],
        calendar_id: str = "primary"
    ) -> Dict[str, Any]:
        """Update event in calendar."""
        access_token = await self._ensure_valid_token(calendar_account)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    f"{self.calendar_api_base}/calendars/{calendar_id}/events/{event_id}",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    },
                    json=event_data
                )
                
                if response.status_code != 200:
                    logger.error(f"Failed to update event: {response.text}")
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="Failed to update calendar event"
                    )
                
                return response.json()
                
        except httpx.HTTPError as e:
            logger.error(f"Error updating event: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Calendar service temporarily unavailable"
            )
    
    async def delete_event(
        self,
        calendar_account: ExternalCalendarAccount,
        event_id: str,
        calendar_id: str = "primary"
    ) -> bool:
        """Delete event from calendar."""
        access_token = await self._ensure_valid_token(calendar_account)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.calendar_api_base}/calendars/{calendar_id}/events/{event_id}",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                
                return response.status_code in [200, 204, 410]  # 410 = already deleted
                
        except httpx.HTTPError as e:
            logger.error(f"Error deleting event: {e}")
            return False
    
    async def create_webhook_watch(
        self,
        calendar_account: ExternalCalendarAccount,
        calendar_id: str = "primary"
    ) -> Optional[Dict[str, Any]]:
        """Create webhook watch for calendar changes."""
        access_token = await self._ensure_valid_token(calendar_account)
        
        webhook_url = f"{settings.app_base_url}/api/calendar/webhooks/google"
        watch_data = {
            "id": f"miraiworks-{calendar_account.id}-{int(datetime.utcnow().timestamp())}",
            "type": "web_hook",
            "address": webhook_url,
            "token": f"user_{calendar_account.user_id}",  # For verification
            "expiration": int((datetime.utcnow() + timedelta(days=30)).timestamp() * 1000)
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.calendar_api_base}/calendars/{calendar_id}/events/watch",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    },
                    json=watch_data
                )
                
                if response.status_code in [200, 201]:
                    return response.json()
                else:
                    logger.error(f"Failed to create webhook: {response.text}")
                    return None
                    
        except httpx.HTTPError as e:
            logger.error(f"Error creating webhook: {e}")
            return None


# Global instance
google_calendar_service = GoogleCalendarService()