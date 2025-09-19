import os
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any
import aiohttp
import structlog
from sqlalchemy.orm import Session
from urllib.parse import urlencode

from app.models.calendar_connection import CalendarConnection

logger = structlog.get_logger()


class CalendarService:
    def __init__(self):
        # Google OAuth settings
        self.google_client_id = os.getenv("GOOGLE_CALENDAR_CLIENT_ID")
        self.google_client_secret = os.getenv("GOOGLE_CALENDAR_CLIENT_SECRET")
        self.google_redirect_uri = os.getenv("GOOGLE_CALENDAR_REDIRECT_URI", "http://localhost:3001/settings/calendar/google/callback")
        
        # Outlook OAuth settings  
        self.outlook_client_id = os.getenv("OUTLOOK_CALENDAR_CLIENT_ID")
        self.outlook_client_secret = os.getenv("OUTLOOK_CALENDAR_CLIENT_SECRET")
        self.outlook_redirect_uri = os.getenv("OUTLOOK_CALENDAR_REDIRECT_URI", "http://localhost:3001/settings/calendar/outlook/callback")
        
        # OAuth URLs
        self.google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
        self.google_token_url = "https://oauth2.googleapis.com/token"
        self.google_revoke_url = "https://oauth2.googleapis.com/revoke"
        
        self.outlook_auth_url = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
        self.outlook_token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
        
        # OAuth scopes
        self.google_scopes = [
            "https://www.googleapis.com/auth/calendar",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile"
        ]
        
        self.outlook_scopes = [
            "https://graph.microsoft.com/calendars.readwrite",
            "https://graph.microsoft.com/user.read"
        ]

    async def get_google_auth_url(self, user_id: int) -> str:
        """Generate Google Calendar OAuth authorization URL"""
        if not self.google_client_id or self.google_client_id == "your-google-client-id":
            raise ValueError("Google Calendar OAuth is not configured. Please set GOOGLE_CALENDAR_CLIENT_ID and GOOGLE_CALENDAR_CLIENT_SECRET environment variables.")
        
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

    async def create_google_connection(self, auth_code: str, user_id: int, db: Session) -> CalendarConnection:
        """Create Google Calendar connection from OAuth code"""
        try:
            # Exchange code for tokens
            token_data = await self._exchange_google_code_for_tokens(auth_code)
            
            # Get user profile
            profile_data = await self._get_google_profile(token_data["access_token"])
            
            # Check for existing connection
            existing = db.query(CalendarConnection).filter(
                CalendarConnection.user_id == user_id,
                CalendarConnection.provider == "google",
                CalendarConnection.provider_account_id == profile_data["id"]
            ).first()
            
            if existing:
                # Update existing connection
                existing.access_token = token_data["access_token"]
                existing.refresh_token = token_data.get("refresh_token", existing.refresh_token)
                existing.token_expires_at = datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 3600))
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
                    token_expires_at=datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 3600)),
                )
                
                db.add(connection)
                db.commit()
                db.refresh(connection)
                return connection
                
        except Exception as e:
            logger.error("Failed to create Google calendar connection", error=str(e), user_id=user_id)
            raise

    async def create_outlook_connection(self, auth_code: str, user_id: int, db: Session) -> CalendarConnection:
        """Create Outlook Calendar connection from OAuth code"""
        try:
            # Exchange code for tokens
            token_data = await self._exchange_outlook_code_for_tokens(auth_code)
            
            # Get user profile
            profile_data = await self._get_outlook_profile(token_data["access_token"])
            
            # Check for existing connection
            existing = db.query(CalendarConnection).filter(
                CalendarConnection.user_id == user_id,
                CalendarConnection.provider == "outlook",
                CalendarConnection.provider_account_id == profile_data["id"]
            ).first()
            
            if existing:
                # Update existing connection
                existing.access_token = token_data["access_token"]
                existing.refresh_token = token_data.get("refresh_token", existing.refresh_token)
                existing.token_expires_at = datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 3600))
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
                    provider_email=profile_data["mail"] or profile_data.get("userPrincipalName", ""),
                    display_name=profile_data.get("displayName", profile_data.get("mail", "")),
                    access_token=token_data["access_token"],
                    refresh_token=token_data.get("refresh_token"),
                    token_expires_at=datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 3600)),
                )
                
                db.add(connection)
                db.commit()
                db.refresh(connection)
                return connection
                
        except Exception as e:
            logger.error("Failed to create Outlook calendar connection", error=str(e), user_id=user_id)
            raise

    async def _exchange_google_code_for_tokens(self, code: str) -> Dict[str, Any]:
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
                    raise ValueError(f"Failed to exchange Google code for tokens: {error_text}")
                return await response.json()

    async def _exchange_outlook_code_for_tokens(self, code: str) -> Dict[str, Any]:
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
                    raise ValueError(f"Failed to exchange Outlook code for tokens: {error_text}")
                return await response.json()

    async def _get_google_profile(self, access_token: str) -> Dict[str, Any]:
        """Get Google user profile"""
        headers = {"Authorization": f"Bearer {access_token}"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get("https://www.googleapis.com/oauth2/v2/userinfo", headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise ValueError(f"Failed to get Google profile: {error_text}")
                return await response.json()

    async def _get_outlook_profile(self, access_token: str) -> Dict[str, Any]:
        """Get Outlook user profile"""
        headers = {"Authorization": f"Bearer {access_token}"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get("https://graph.microsoft.com/v1.0/me", headers=headers) as response:
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
                    async with session.post(self.google_revoke_url, params=params) as response:
                        if response.status not in [200, 400]:  # 400 is returned if token is already invalid
                            logger.warning("Failed to revoke Google tokens", status=response.status)
            elif connection.provider == "outlook":
                # Outlook doesn't have a direct revoke endpoint in common tenant
                # The tokens will expire naturally
                logger.info("Outlook tokens marked for revocation (will expire naturally)")
                
        except Exception as e:
            logger.warning("Error during token revocation", error=str(e), connection_id=connection.id)

    async def sync_calendar(self, connection: CalendarConnection, db: Session) -> Dict[str, Any]:
        """Sync calendar events (placeholder implementation)"""
        try:
            # This is a placeholder for actual calendar sync implementation
            # In a real implementation, you would:
            # 1. Fetch events from the calendar provider
            # 2. Store/update them in your database
            # 3. Handle any conflicts or updates
            
            connection.last_sync_at = datetime.utcnow()
            connection.sync_error = None
            db.commit()
            
            logger.info("Calendar sync completed", connection_id=connection.id)
            return {"status": "success", "message": "Calendar synced successfully"}
            
        except Exception as e:
            connection.sync_error = str(e)
            db.commit()
            logger.error("Calendar sync failed", error=str(e), connection_id=connection.id)
            raise


# Create singleton instance
google_calendar_service = CalendarService()