import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.company import Company
from app.models.calendar_integration import CalendarIntegration, CalendarEvent
from app.services.calendar_service import CalendarService
from app.services.microsoft_calendar_service import MicrosoftCalendarService


class TestCalendarService:
    
    @pytest.fixture
    async def calendar_service(self):
        return CalendarService()
    
    @pytest.fixture
    async def mock_user(self, db_session: AsyncSession):
        user = User(
            email="test@example.com",
            full_name="Test User",
            password_hash="hashed_password",
            role="recruiter",
            is_active=True
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user
    
    @pytest.fixture
    async def calendar_integration(self, db_session: AsyncSession, mock_user: User):
        integration = CalendarIntegration(
            user_id=mock_user.id,
            provider="google",
            email="test@example.com",
            access_token="test_access_token",
            refresh_token="test_refresh_token",
            token_expires_at=datetime.utcnow() + timedelta(hours=1),
            calendar_id="primary",
            sync_enabled=True,
            is_active=True
        )
        db_session.add(integration)
        await db_session.commit()
        await db_session.refresh(integration)
        return integration
    
    @patch('httpx.AsyncClient.get')
    async def test_get_oauth_url(self, mock_get, calendar_service):
        """Test OAuth URL generation."""
        url = await calendar_service.get_oauth_url("test_state")
        
        assert "https://accounts.google.com/o/oauth2/v2/auth" in url
        assert "state=test_state" in url
        assert "scope=" in url
    
    @patch('httpx.AsyncClient.post')
    async def test_exchange_code_for_tokens(self, mock_post, calendar_service):
        """Test OAuth code exchange."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "access_token": "access_token_123",
            "refresh_token": "refresh_token_123",
            "expires_in": 3600,
            "token_type": "Bearer"
        }
        mock_post.return_value = mock_response
        
        tokens = await calendar_service.exchange_code_for_tokens("auth_code_123")
        
        assert tokens["access_token"] == "access_token_123"
        assert tokens["refresh_token"] == "refresh_token_123"
        assert tokens["expires_in"] == 3600
    
    @patch('httpx.AsyncClient.get')
    async def test_get_user_info(self, mock_get, calendar_service):
        """Test getting user info from Google."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "email": "test@example.com",
            "name": "Test User",
            "id": "123456789"
        }
        mock_get.return_value = mock_response
        
        user_info = await calendar_service.get_user_info("access_token_123")
        
        assert user_info["email"] == "test@example.com"
        assert user_info["name"] == "Test User"
    
    @patch('httpx.AsyncClient.get')
    async def test_list_calendars(self, mock_get, calendar_service):
        """Test listing user's calendars."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "items": [
                {
                    "id": "primary",
                    "summary": "Primary Calendar",
                    "primary": True,
                    "timeZone": "America/New_York"
                },
                {
                    "id": "calendar2",
                    "summary": "Work Calendar",
                    "primary": False,
                    "timeZone": "America/New_York"
                }
            ]
        }
        mock_get.return_value = mock_response
        
        calendars = await calendar_service.list_calendars("access_token_123")
        
        assert len(calendars["items"]) == 2
        assert calendars["items"][0]["primary"] is True
    
    @patch('httpx.AsyncClient.get')
    async def test_list_events(self, mock_get, calendar_service):
        """Test listing calendar events."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "items": [
                {
                    "id": "event1",
                    "summary": "Test Event",
                    "start": {"dateTime": "2024-01-01T10:00:00Z"},
                    "end": {"dateTime": "2024-01-01T11:00:00Z"}
                }
            ],
            "nextSyncToken": "sync_token_123"
        }
        mock_get.return_value = mock_response
        
        events = await calendar_service.list_events("access_token_123", "primary")
        
        assert len(events["items"]) == 1
        assert events["items"][0]["summary"] == "Test Event"
        assert "nextSyncToken" in events
    
    @patch('httpx.AsyncClient.post')
    async def test_create_event(self, mock_post, calendar_service):
        """Test creating a calendar event."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": "created_event_123",
            "summary": "New Event",
            "start": {"dateTime": "2024-01-01T10:00:00Z"},
            "end": {"dateTime": "2024-01-01T11:00:00Z"}
        }
        mock_post.return_value = mock_response
        
        event_data = {
            "summary": "New Event",
            "start": {"dateTime": "2024-01-01T10:00:00Z"},
            "end": {"dateTime": "2024-01-01T11:00:00Z"}
        }
        
        created_event = await calendar_service.create_event(
            "access_token_123", "primary", event_data
        )
        
        assert created_event["id"] == "created_event_123"
        assert created_event["summary"] == "New Event"
    
    @patch('httpx.AsyncClient.patch')
    async def test_update_event(self, mock_patch, calendar_service):
        """Test updating a calendar event."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": "event_123",
            "summary": "Updated Event",
            "start": {"dateTime": "2024-01-01T10:00:00Z"},
            "end": {"dateTime": "2024-01-01T12:00:00Z"}
        }
        mock_patch.return_value = mock_response
        
        update_data = {
            "summary": "Updated Event",
            "end": {"dateTime": "2024-01-01T12:00:00Z"}
        }
        
        updated_event = await calendar_service.update_event(
            "access_token_123", "primary", "event_123", update_data
        )
        
        assert updated_event["summary"] == "Updated Event"
    
    @patch('httpx.AsyncClient.delete')
    async def test_delete_event(self, mock_delete, calendar_service):
        """Test deleting a calendar event."""
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_delete.return_value = mock_response
        
        result = await calendar_service.delete_event(
            "access_token_123", "primary", "event_123"
        )
        
        assert result is True
    
    async def test_is_token_expired(self, calendar_service, calendar_integration):
        """Test token expiration check."""
        # Token expires in future - should not be expired
        assert not await calendar_service.is_token_expired(calendar_integration)
        
        # Expired token
        calendar_integration.token_expires_at = datetime.utcnow() - timedelta(hours=1)
        assert await calendar_service.is_token_expired(calendar_integration)


class TestMicrosoftCalendarService:
    
    @pytest.fixture
    async def microsoft_service(self):
        return MicrosoftCalendarService()
    
    @pytest.fixture
    async def microsoft_integration(self, db_session: AsyncSession, mock_user: User):
        integration = CalendarIntegration(
            user_id=mock_user.id,
            provider="microsoft",
            email="test@example.com",
            access_token="test_access_token",
            refresh_token="test_refresh_token",
            token_expires_at=datetime.utcnow() + timedelta(hours=1),
            calendar_id="primary",
            sync_enabled=True,
            is_active=True
        )
        db_session.add(integration)
        await db_session.commit()
        await db_session.refresh(integration)
        return integration
    
    @patch('httpx.AsyncClient.get')
    async def test_list_events_microsoft(self, mock_get, microsoft_service):
        """Test listing Microsoft calendar events."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "value": [
                {
                    "id": "event1",
                    "subject": "Microsoft Event",
                    "start": {"dateTime": "2024-01-01T10:00:00Z", "timeZone": "UTC"},
                    "end": {"dateTime": "2024-01-01T11:00:00Z", "timeZone": "UTC"}
                }
            ]
        }
        mock_get.return_value = mock_response
        
        events = await microsoft_service.list_events("access_token_123")
        
        assert len(events["value"]) == 1
        assert events["value"][0]["subject"] == "Microsoft Event"
    
    @patch('httpx.AsyncClient.post')
    async def test_create_event_microsoft(self, mock_post, microsoft_service):
        """Test creating a Microsoft calendar event."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": "created_event_123",
            "subject": "New Microsoft Event",
            "start": {"dateTime": "2024-01-01T10:00:00Z", "timeZone": "UTC"},
            "end": {"dateTime": "2024-01-01T11:00:00Z", "timeZone": "UTC"}
        }
        mock_post.return_value = mock_response
        
        event_data = {
            "subject": "New Microsoft Event",
            "start": {"dateTime": "2024-01-01T10:00:00Z", "timeZone": "UTC"},
            "end": {"dateTime": "2024-01-01T11:00:00Z", "timeZone": "UTC"}
        }
        
        created_event = await microsoft_service.create_event("access_token_123", event_data)
        
        assert created_event["id"] == "created_event_123"
        assert created_event["subject"] == "New Microsoft Event"


class TestCalendarIntegrationAPI:
    """Test calendar integration API endpoints."""
    
    @pytest.fixture
    async def auth_headers(self, authenticated_user):
        return {"Authorization": f"Bearer {authenticated_user['access_token']}"}
    
    def test_get_calendar_accounts(self, client: TestClient, auth_headers):
        """Test getting user's calendar accounts."""
        response = client.get("/api/v1/calendar/accounts", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "accounts" in data
        assert isinstance(data["accounts"], list)
    
    @patch('app.services.calendar_service.CalendarService.get_oauth_url')
    def test_connect_google_calendar(self, mock_get_oauth_url, client: TestClient, auth_headers):
        """Test initiating Google Calendar connection."""
        mock_get_oauth_url.return_value = "https://accounts.google.com/oauth/authorize?..."
        
        response = client.post(
            "/api/v1/calendar/connect",
            json={"provider": "google"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "auth_url" in data
        assert "state" in data
    
    def test_connect_invalid_provider(self, client: TestClient, auth_headers):
        """Test connecting with invalid provider."""
        response = client.post(
            "/api/v1/calendar/connect",
            json={"provider": "invalid"},
            headers=auth_headers
        )
        
        assert response.status_code == 422
    
    def test_list_calendars_no_integration(self, client: TestClient, auth_headers):
        """Test listing calendars without integration."""
        response = client.get("/api/v1/calendar/calendars", headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_sync_calendars_no_integration(self, client: TestClient, auth_headers):
        """Test syncing calendars without integration."""
        response = client.post(
            "/api/v1/calendar/sync",
            json={},
            headers=auth_headers
        )
        
        assert response.status_code == 404


class TestCalendarEvents:
    """Test calendar event operations."""
    
    @pytest.fixture
    async def calendar_event(self, db_session: AsyncSession, calendar_integration):
        event = CalendarEvent(
            calendar_integration_id=calendar_integration.id,
            external_event_id="event_123",
            title="Test Event",
            description="Test Description",
            start_datetime=datetime.utcnow() + timedelta(hours=1),
            end_datetime=datetime.utcnow() + timedelta(hours=2),
            timezone="UTC",
            is_all_day=False
        )
        db_session.add(event)
        await db_session.commit()
        await db_session.refresh(event)
        return event
    
    async def test_calendar_event_creation(self, db_session: AsyncSession, calendar_integration):
        """Test creating a calendar event record."""
        event = CalendarEvent(
            calendar_integration_id=calendar_integration.id,
            external_event_id="test_event_123",
            title="Test Meeting",
            start_datetime=datetime(2024, 1, 1, 10, 0),
            end_datetime=datetime(2024, 1, 1, 11, 0),
            timezone="UTC"
        )
        
        db_session.add(event)
        await db_session.commit()
        await db_session.refresh(event)
        
        assert event.id is not None
        assert event.title == "Test Meeting"
        assert event.calendar_integration_id == calendar_integration.id
    
    async def test_get_events_by_date_range(self, db_session: AsyncSession, calendar_event):
        """Test querying events by date range."""
        start_date = datetime.utcnow()
        end_date = datetime.utcnow() + timedelta(days=1)
        
        events = await CalendarEvent.get_by_date_range(
            db_session, calendar_event.calendar_integration_id, start_date, end_date
        )
        
        assert len(events) == 1
        assert events[0].id == calendar_event.id
    
    async def test_event_conflict_detection(self, db_session: AsyncSession, calendar_integration):
        """Test detecting overlapping events."""
        # Create overlapping events
        event1 = CalendarEvent(
            calendar_integration_id=calendar_integration.id,
            external_event_id="event1",
            title="Event 1",
            start_datetime=datetime(2024, 1, 1, 10, 0),
            end_datetime=datetime(2024, 1, 1, 11, 0),
            timezone="UTC"
        )
        
        event2 = CalendarEvent(
            calendar_integration_id=calendar_integration.id,
            external_event_id="event2",
            title="Event 2",
            start_datetime=datetime(2024, 1, 1, 10, 30),
            end_datetime=datetime(2024, 1, 1, 11, 30),
            timezone="UTC"
        )
        
        db_session.add_all([event1, event2])
        await db_session.commit()
        
        conflicts = await CalendarEvent.find_conflicts(
            db_session,
            calendar_integration.id,
            datetime(2024, 1, 1, 10, 15),
            datetime(2024, 1, 1, 10, 45)
        )
        
        assert len(conflicts) == 2  # Both events conflict
    
    def test_all_day_event_handling(self, db_session: AsyncSession, calendar_integration):
        """Test handling all-day events."""
        event = CalendarEvent(
            calendar_integration_id=calendar_integration.id,
            external_event_id="all_day_event",
            title="All Day Event",
            start_datetime=datetime(2024, 1, 1),
            end_datetime=datetime(2024, 1, 2),
            timezone="UTC",
            is_all_day=True
        )
        
        assert event.is_all_day is True
        assert event.start_datetime.hour == 0
        assert event.start_datetime.minute == 0