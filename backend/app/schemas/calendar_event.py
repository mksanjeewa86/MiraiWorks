from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator


class EventType(str, Enum):
    EVENT = "event"
    MEETING = "meeting"
    TASK = "task"
    APPOINTMENT = "appointment"
    REMINDER = "reminder"
    BIRTHDAY = "birthday"
    DEADLINE = "deadline"


class EventStatus(str, Enum):
    CONFIRMED = "confirmed"
    TENTATIVE = "tentative"
    CANCELLED = "cancelled"
    POSTPONED = "postponed"


class CalendarEventBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None)
    start_datetime: datetime
    end_datetime: Optional[datetime] = None
    is_all_day: bool = Field(default=False)
    location: Optional[str] = Field(None, max_length=255)
    event_type: EventType = Field(default=EventType.EVENT)
    status: EventStatus = Field(default=EventStatus.CONFIRMED)
    recurrence_rule: Optional[str] = Field(None, max_length=255)
    timezone: str = Field(default="UTC", max_length=50)

    @field_validator("end_datetime")
    @classmethod
    def validate_end_datetime(cls, v, info):
        if v and info.data.get("start_datetime") and v <= info.data["start_datetime"]:
            raise ValueError("end_datetime must be after start_datetime")
        return v

    @field_validator("start_datetime")
    @classmethod
    def validate_start_datetime(cls, v):
        # Convert to timezone-aware datetime for comparison if needed
        min_date = datetime(1900, 1, 1, tzinfo=timezone.utc)
        max_date = datetime(2100, 12, 31, 23, 59, 59, tzinfo=timezone.utc)

        # Make value timezone-aware if it's naive
        v_aware = v if v.tzinfo is not None else v.replace(tzinfo=timezone.utc)

        if v_aware < min_date or v_aware > max_date:
            raise ValueError("start_datetime must be between 1900 and 2100")
        return v


class CalendarEventCreate(CalendarEventBase):
    """Schema for creating a new calendar event."""

    pass


class CalendarEventUpdate(BaseModel):
    """Schema for updating an existing calendar event."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    is_all_day: Optional[bool] = None
    location: Optional[str] = Field(None, max_length=255)
    event_type: Optional[EventType] = None
    status: Optional[EventStatus] = None
    recurrence_rule: Optional[str] = Field(None, max_length=255)
    timezone: Optional[str] = Field(None, max_length=50)

    @field_validator("end_datetime")
    @classmethod
    def validate_end_datetime(cls, v, info):
        if v and info.data.get("start_datetime") and v <= info.data["start_datetime"]:
            raise ValueError("end_datetime must be after start_datetime")
        return v

    @field_validator("start_datetime")
    @classmethod
    def validate_start_datetime(cls, v):
        if v:
            # Convert to timezone-aware datetime for comparison if needed
            min_date = datetime(1900, 1, 1, tzinfo=timezone.utc)
            max_date = datetime(2100, 12, 31, 23, 59, 59, tzinfo=timezone.utc)

            # Make value timezone-aware if it's naive
            v_aware = v if v.tzinfo is not None else v.replace(tzinfo=timezone.utc)

            if v_aware < min_date or v_aware > max_date:
                raise ValueError("start_datetime must be between 1900 and 2100")
        return v


class CalendarEventInfo(CalendarEventBase):
    """Schema for calendar event responses."""

    id: int
    creator_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    parent_event_id: Optional[int] = None
    is_recurring: bool = False
    is_instance: bool = False

    @field_serializer('start_datetime', 'end_datetime', 'created_at', 'updated_at')
    def serialize_datetime(self, dt: Optional[datetime], _info) -> Optional[str]:
        """Ensure datetime fields are serialized with UTC timezone information."""
        if dt is None:
            return None
        # If datetime is naive, assume it's UTC and add timezone
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        # Serialize to ISO format with Z suffix
        return dt.isoformat()


class CalendarEventListResponse(BaseModel):
    """Schema for calendar event list responses."""

    events: list[CalendarEventInfo]
    total: int
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class CalendarEventQueryParams(BaseModel):
    """Schema for calendar event query parameters."""

    start_date: Optional[datetime] = Field(None)
    end_date: Optional[datetime] = Field(None)
    event_type: Optional[EventType] = Field(None)
    status: Optional[EventStatus] = Field(None)
    creator_id: Optional[int] = Field(None)
    include_all_day: bool = Field(default=True)
    include_recurring: bool = Field(default=True)
    timezone: Optional[str] = Field(None, max_length=50)

    @field_validator("end_date")
    @classmethod
    def validate_date_range(cls, v, info):
        if v and info.data.get("start_date") and v < info.data["start_date"]:
            raise ValueError("end_date must be after start_date")
        return v


class CalendarEventBulkCreate(BaseModel):
    """Schema for creating multiple calendar events at once."""

    events: list[CalendarEventCreate] = Field(..., min_length=1, max_length=100)


class CalendarEventBulkResponse(BaseModel):
    """Schema for bulk create response."""

    created_events: list[CalendarEventInfo]
    failed_events: list[dict] = Field(default_factory=list)
    total_created: int
    total_failed: int


class RecurrencePattern(BaseModel):
    """Schema for recurring event patterns."""

    frequency: str = Field(..., description="DAILY, WEEKLY, MONTHLY, YEARLY")
    interval: int = Field(default=1, ge=1, le=999)
    count: Optional[int] = Field(None, ge=1, le=999)
    until: Optional[datetime] = None
    by_weekday: list[int] | None = Field(None, description="0=Monday, 6=Sunday")
    by_monthday: list[int] | None = Field(None, description="1-31")
    by_month: list[int] | None = Field(None, description="1-12")

    @field_validator("frequency")
    @classmethod
    def validate_frequency(cls, v):
        allowed = ["DAILY", "WEEKLY", "MONTHLY", "YEARLY"]
        if v.upper() not in allowed:
            raise ValueError(f'frequency must be one of: {", ".join(allowed)}')
        return v.upper()
