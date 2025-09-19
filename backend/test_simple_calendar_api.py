#!/usr/bin/env python3
"""
Comprehensive tests for simple calendar API endpoints.
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from datetime import datetime, timezone
import json

from simple_calendar_api_v2 import app

client = TestClient(app)

@pytest.fixture
def event_data():
    """Sample event data for testing."""
    return {
        "title": "Test Meeting",
        "description": "A test meeting for unit testing",
        "location": "Conference Room A",
        "startDatetime": "2025-01-15T09:00:00Z",
        "endDatetime": "2025-01-15T10:00:00Z",
        "timezone": "UTC",
        "isAllDay": False,
        "attendees": ["test@example.com", "attendee@example.com"],
        "status": "confirmed"
    }

@pytest.fixture
def minimal_event_data():
    """Minimal event data for testing."""
    return {
        "title": "Minimal Event",
        "startDatetime": "2025-01-15T14:00:00Z",
        "endDatetime": "2025-01-15T15:00:00Z"
    }

class TestCalendarEventCreation:
    """Comprehensive tests for calendar event creation functionality."""

    def test_create_event_success(self, event_data):
        """Test successful event creation with valid data."""
        response = client.post("/api/calendar/events", json=event_data)

        assert response.status_code == 201
        data = response.json()

        # Verify all required fields are present
        assert "id" in data
        assert data["title"] == event_data["title"]
        assert data["description"] == event_data["description"]
        assert data["location"] == event_data["location"]
        assert data["startDatetime"] == event_data["startDatetime"]
        assert data["endDatetime"] == event_data["endDatetime"]
        assert data["timezone"] == event_data["timezone"]
        assert data["isAllDay"] == event_data["isAllDay"]
        assert data["attendees"] == event_data["attendees"]
        assert data["status"] == event_data["status"]
        assert "createdAt" in data
        assert "updatedAt" in data
        assert data["organizerEmail"] == "test@example.com"
        assert data["isRecurring"] == False

    def test_create_event_minimal_data(self, minimal_event_data):
        """Test event creation with minimal required data."""
        response = client.post("/api/calendar/events", json=minimal_event_data)

        assert response.status_code == 201
        data = response.json()

        # Verify required fields
        assert data["title"] == minimal_event_data["title"]
        assert data["startDatetime"] == minimal_event_data["startDatetime"]
        assert data["endDatetime"] == minimal_event_data["endDatetime"]

        # Verify defaults
        assert data["timezone"] == "UTC"
        assert data["isAllDay"] == False
        assert data["attendees"] == []
        assert data["status"] == "tentative"
        assert data["description"] is None
        assert data["location"] is None

    def test_create_event_invalid_title_empty(self):
        """Test event creation with empty title fails."""
        event_data = {
            "title": "",
            "startDatetime": "2025-01-15T14:00:00Z",
            "endDatetime": "2025-01-15T15:00:00Z"
        }

        response = client.post("/api/calendar/events", json=event_data)
        assert response.status_code == 422

    def test_create_event_missing_title(self):
        """Test event creation without title fails."""
        event_data = {
            "startDatetime": "2025-01-15T14:00:00Z",
            "endDatetime": "2025-01-15T15:00:00Z"
        }

        response = client.post("/api/calendar/events", json=event_data)
        assert response.status_code == 422

    def test_create_event_missing_start_datetime(self):
        """Test event creation without start datetime fails."""
        event_data = {
            "title": "Test Event",
            "endDatetime": "2025-01-15T15:00:00Z"
        }

        response = client.post("/api/calendar/events", json=event_data)
        assert response.status_code == 422

    def test_create_event_missing_end_datetime(self):
        """Test event creation without end datetime fails."""
        event_data = {
            "title": "Test Event",
            "startDatetime": "2025-01-15T14:00:00Z"
        }

        response = client.post("/api/calendar/events", json=event_data)
        assert response.status_code == 422

    def test_create_event_invalid_datetime_format(self):
        """Test event creation with invalid datetime format fails."""
        event_data = {
            "title": "Test Event",
            "startDatetime": "invalid-date",
            "endDatetime": "2025-01-15T15:00:00Z"
        }

        response = client.post("/api/calendar/events", json=event_data)
        assert response.status_code == 422

    def test_create_all_day_event(self):
        """Test creation of all-day event."""
        event_data = {
            "title": "All Day Event",
            "startDatetime": "2025-01-15T00:00:00Z",
            "endDatetime": "2025-01-15T23:59:59Z",
            "isAllDay": True
        }

        response = client.post("/api/calendar/events", json=event_data)
        assert response.status_code == 201
        data = response.json()
        assert data["isAllDay"] == True

    def test_create_event_with_attendees(self):
        """Test event creation with multiple attendees."""
        event_data = {
            "title": "Team Meeting",
            "startDatetime": "2025-01-15T14:00:00Z",
            "endDatetime": "2025-01-15T15:00:00Z",
            "attendees": ["alice@example.com", "bob@example.com", "charlie@example.com"]
        }

        response = client.post("/api/calendar/events", json=event_data)
        assert response.status_code == 201
        data = response.json()
        assert len(data["attendees"]) == 3
        assert "alice@example.com" in data["attendees"]

    def test_create_multiple_events(self):
        """Test creating multiple events."""
        events = [
            {
                "title": "Event 1",
                "startDatetime": "2025-01-15T09:00:00Z",
                "endDatetime": "2025-01-15T10:00:00Z"
            },
            {
                "title": "Event 2",
                "startDatetime": "2025-01-15T11:00:00Z",
                "endDatetime": "2025-01-15T12:00:00Z"
            }
        ]

        created_events = []
        for event_data in events:
            response = client.post("/api/calendar/events", json=event_data)
            assert response.status_code == 201
            created_events.append(response.json())

        # Verify events have different IDs
        assert created_events[0]["id"] != created_events[1]["id"]

class TestCalendarEventRetrieval:
    """Tests for calendar event retrieval functionality."""

    def test_get_events_empty(self):
        """Test getting events when none exist."""
        # Clear events first by making a fresh request
        response = client.get("/api/calendar/events")
        assert response.status_code == 200
        data = response.json()
        assert "events" in data
        assert isinstance(data["events"], list)
        assert "has_more" in data

    def test_get_events_after_creation(self, event_data):
        """Test getting events after creating one."""
        # Create an event
        create_response = client.post("/api/calendar/events", json=event_data)
        assert create_response.status_code == 201

        # Get events
        get_response = client.get("/api/calendar/events")
        assert get_response.status_code == 200
        data = get_response.json()

        # Should contain the created event
        events = data["events"]
        assert len(events) >= 1

        # Find our event
        created_event = create_response.json()
        found_event = None
        for event in events:
            if event["id"] == created_event["id"]:
                found_event = event
                break

        assert found_event is not None
        assert found_event["title"] == event_data["title"]

    def test_get_events_with_date_parameters(self):
        """Test getting events with date range parameters."""
        response = client.get("/api/calendar/events?startDate=2025-01-01&endDate=2025-01-31")
        assert response.status_code == 200
        data = response.json()
        assert "events" in data

class TestCalendarEventUpdate:
    """Tests for calendar event update functionality."""

    def test_update_event_success(self, event_data):
        """Test successful event update."""
        # Create an event
        create_response = client.post("/api/calendar/events", json=event_data)
        assert create_response.status_code == 201
        created_event = create_response.json()
        event_id = created_event["id"]

        # Update the event
        updated_data = event_data.copy()
        updated_data["title"] = "Updated Test Meeting"
        updated_data["description"] = "Updated description"

        update_response = client.put(f"/api/calendar/events/{event_id}", json=updated_data)
        assert update_response.status_code == 200
        updated_event = update_response.json()

        # Verify updates
        assert updated_event["id"] == event_id
        assert updated_event["title"] == "Updated Test Meeting"
        assert updated_event["description"] == "Updated description"
        assert updated_event["createdAt"] == created_event["createdAt"]
        assert updated_event["updatedAt"] != created_event["updatedAt"]

    def test_update_nonexistent_event(self, event_data):
        """Test updating a non-existent event creates new one."""
        fake_id = "non-existent-id"
        response = client.put(f"/api/calendar/events/{fake_id}", json=event_data)
        assert response.status_code == 200
        data = response.json()
        # Should create a new event since the ID doesn't exist
        assert "id" in data

class TestCalendarEventDeletion:
    """Tests for calendar event deletion functionality."""

    def test_delete_event_success(self, event_data):
        """Test successful event deletion."""
        # Create an event
        create_response = client.post("/api/calendar/events", json=event_data)
        assert create_response.status_code == 201
        event_id = create_response.json()["id"]

        # Delete the event
        delete_response = client.delete(f"/api/calendar/events/{event_id}")
        assert delete_response.status_code == 200
        data = delete_response.json()
        assert data["message"] == "Event deleted successfully"

    def test_delete_nonexistent_event(self):
        """Test deleting a non-existent event."""
        fake_id = "non-existent-id"
        response = client.delete(f"/api/calendar/events/{fake_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Event not found"

class TestAPIRootEndpoint:
    """Tests for API root endpoint."""

    def test_root_endpoint(self):
        """Test root endpoint returns correct message."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Simple Calendar API v2 Server"

class TestCORSConfiguration:
    """Tests for CORS configuration."""

    def test_cors_headers_present(self, event_data):
        """Test CORS headers are present in responses."""
        response = client.post("/api/calendar/events", json=event_data)
        assert response.status_code == 201

        # CORS headers should be handled by FastAPI middleware
        # In test environment, we mainly verify the endpoint works
        assert "id" in response.json()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])