"""
Tests for calendar event timezone handling.

This test verifies that calendar events are properly serialized with UTC timezone
information, ensuring correct display in user's local timezone.
"""

from datetime import UTC, datetime

from app.schemas.calendar import EventInfo
from app.schemas.calendar_event import CalendarEventInfo


def test_event_info_serializes_datetime_with_timezone():
    """Test that EventInfo properly serializes datetime fields with UTC timezone."""
    # Create a timezone-naive datetime (simulating MySQL TIMESTAMP behavior)
    naive_datetime = datetime(2025, 10, 20, 4, 0, 0)  # 2025-10-20 04:00:00 (UTC)

    # Create EventInfo with naive datetime
    event = EventInfo.model_construct(
        id="event-1",
        title="Test Event",
        description="Test Description",
        location="Test Location",
        start_datetime=naive_datetime,
        end_datetime=datetime(2025, 10, 20, 5, 0, 0),
        timezone="UTC",
        is_all_day=False,
        is_recurring=False,
        organizer_email="test@example.com",
        attendees=[],
        status="confirmed",
        created_at=naive_datetime,
        updated_at=naive_datetime,
    )

    # Serialize to dict (this uses field_serializer)
    event_dict = event.model_dump(mode="json", by_alias=True)

    # Verify datetime strings include timezone information (Z suffix or +00:00)
    assert (
        event_dict["startDatetime"].endswith("Z")
        or "+00:00" in event_dict["startDatetime"]
    )
    assert (
        event_dict["endDatetime"].endswith("Z") or "+00:00" in event_dict["endDatetime"]
    )
    assert event_dict["createdAt"].endswith("Z") or "+00:00" in event_dict["createdAt"]
    assert event_dict["updatedAt"].endswith("Z") or "+00:00" in event_dict["updatedAt"]

    # Verify the datetime can be parsed back correctly
    parsed_start = datetime.fromisoformat(
        event_dict["startDatetime"].replace("Z", "+00:00")
    )
    assert parsed_start.tzinfo is not None  # Has timezone info
    assert parsed_start.replace(tzinfo=None) == naive_datetime  # Same time


def test_calendar_event_info_serializes_datetime_with_timezone():
    """Test that CalendarEventInfo properly serializes datetime fields with UTC timezone."""
    # Create a timezone-naive datetime (simulating MySQL TIMESTAMP behavior)
    naive_datetime = datetime(2025, 10, 20, 4, 0, 0)  # 2025-10-20 04:00:00 (UTC)

    # Create CalendarEventInfo with naive datetime
    event = CalendarEventInfo.model_construct(
        id=1,
        creator_id=123,
        title="Test Calendar Event",
        description="Test Description",
        start_datetime=naive_datetime,
        end_datetime=datetime(2025, 10, 20, 5, 0, 0),
        is_all_day=False,
        location="Test Location",
        event_type="event",
        status="confirmed",
        timezone="UTC",
        created_at=naive_datetime,
        updated_at=naive_datetime,
    )

    # Serialize to dict (this uses field_serializer)
    event_dict = event.model_dump(mode="json")

    # Verify datetime strings include timezone information (Z suffix or +00:00)
    assert (
        event_dict["start_datetime"].endswith("Z")
        or "+00:00" in event_dict["start_datetime"]
    )
    assert (
        event_dict["end_datetime"].endswith("Z")
        or "+00:00" in event_dict["end_datetime"]
    )
    assert (
        event_dict["created_at"].endswith("Z") or "+00:00" in event_dict["created_at"]
    )
    assert (
        event_dict["updated_at"].endswith("Z") or "+00:00" in event_dict["updated_at"]
    )

    # Verify the datetime can be parsed back correctly
    parsed_start = datetime.fromisoformat(
        event_dict["start_datetime"].replace("Z", "+00:00")
    )
    assert parsed_start.tzinfo is not None  # Has timezone info
    assert parsed_start.replace(tzinfo=None) == naive_datetime  # Same time


def test_timezone_aware_datetime_preserved():
    """Test that timezone-aware datetimes are preserved correctly."""
    # Create a timezone-aware datetime
    aware_datetime = datetime(2025, 10, 20, 4, 0, 0, tzinfo=UTC)

    # Create EventInfo with timezone-aware datetime
    event = EventInfo.model_construct(
        id="event-2",
        title="Test Event with Timezone",
        description="Test",
        location="Test",
        start_datetime=aware_datetime,
        end_datetime=datetime(2025, 10, 20, 5, 0, 0, tzinfo=UTC),
        timezone="UTC",
        is_all_day=False,
        is_recurring=False,
        organizer_email="test@example.com",
        attendees=[],
        status="confirmed",
        created_at=aware_datetime,
        updated_at=aware_datetime,
    )

    # Serialize to dict
    event_dict = event.model_dump(mode="json", by_alias=True)

    # Verify timezone information is included
    assert (
        event_dict["startDatetime"].endswith("Z")
        or "+00:00" in event_dict["startDatetime"]
    )

    # Parse back and verify
    parsed_start = datetime.fromisoformat(
        event_dict["startDatetime"].replace("Z", "+00:00")
    )
    assert parsed_start == aware_datetime


def test_fullcalendar_can_parse_serialized_datetime():
    """Test that FullCalendar can properly parse the serialized datetime strings."""
    # Simulate what happens in the calendar page
    naive_datetime = datetime(2025, 10, 20, 4, 0, 0)  # 2025-10-20 04:00:00 UTC

    event = EventInfo.model_construct(
        id="event-3",
        title="Interview",
        description="",
        location="Video Call",
        start_datetime=naive_datetime,
        end_datetime=datetime(2025, 10, 20, 5, 0, 0),
        timezone="UTC",
        is_all_day=False,
        is_recurring=False,
        organizer_email="admin@miraiworks.com",
        attendees=[],
        status="confirmed",
        created_at=naive_datetime,
        updated_at=naive_datetime,
    )

    # Serialize
    event_dict = event.model_dump(mode="json", by_alias=True)

    # This is what FullCalendar receives
    start_str = event_dict["startDatetime"]

    # FullCalendar parses ISO strings with timezone
    # If the string has Z or +00:00, it knows it's UTC
    # Expected: '2025-10-20T04:00:00Z' or '2025-10-20T04:00:00+00:00'

    # Verify the format is correct for FullCalendar
    assert "T" in start_str  # ISO format with T separator
    assert start_str.endswith("Z") or "+00:00" in start_str  # Has timezone indicator

    # When user is in JST (UTC+9), this should display as:
    # 2025-10-20 13:00:00 JST (4:00 UTC + 9 hours = 13:00 JST)
    # The date should be October 20, not October 19

    parsed = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
    assert parsed.day == 20  # Correct day
    assert parsed.hour == 4  # Correct UTC hour


if __name__ == "__main__":
    # Run tests
    print("Running timezone serialization tests...\n")

    test_event_info_serializes_datetime_with_timezone()
    print("✓ EventInfo serializes datetime with timezone")

    test_calendar_event_info_serializes_datetime_with_timezone()
    print("✓ CalendarEventInfo serializes datetime with timezone")

    test_timezone_aware_datetime_preserved()
    print("✓ Timezone-aware datetime preserved")

    test_fullcalendar_can_parse_serialized_datetime()
    print("✓ FullCalendar can parse serialized datetime")

    print("\n✅ All timezone tests passed!")
