from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


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
    description: str | None = Field(None)
    start_datetime: datetime
    end_datetime: datetime | None = None
    is_all_day: bool = Field(default=False)
    location: str | None = Field(None, max_length=255)
    event_type: EventType = Field(default=EventType.EVENT)
    status: EventStatus = Field(default=EventStatus.CONFIRMED)
    recurrence_rule: str | None = Field(None, max_length=255)
    timezone: str = Field(default="UTC", max_length=50)

    @field_validator('end_datetime')
    @classmethod
    def validate_end_datetime(cls, v, info):
        if v and info.data.get('start_datetime') and v <= info.data['start_datetime']:
            raise ValueError('end_datetime must be after start_datetime')
        return v

    @field_validator('start_datetime')
    @classmethod
    def validate_start_datetime(cls, v):
        if v < datetime(1900, 1, 1) or v > datetime(2100, 12, 31):
            raise ValueError('start_datetime must be between 1900 and 2100')
        return v


class CalendarEventCreate(CalendarEventBase):
    """Schema for creating a new calendar event."""
    pass


class CalendarEventUpdate(BaseModel):
    """Schema for updating an existing calendar event."""
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    start_datetime: datetime | None = None
    end_datetime: datetime | None = None
    is_all_day: bool | None = None
    location: str | None = Field(None, max_length=255)
    event_type: EventType | None = None
    status: EventStatus | None = None
    recurrence_rule: str | None = Field(None, max_length=255)
    timezone: str | None = Field(None, max_length=50)

    @field_validator('end_datetime')
    @classmethod
    def validate_end_datetime(cls, v, info):
        if v and info.data.get('start_datetime') and v <= info.data['start_datetime']:
            raise ValueError('end_datetime must be after start_datetime')
        return v

    @field_validator('start_datetime')
    @classmethod
    def validate_start_datetime(cls, v):
        if v and (v < datetime(1900, 1, 1) or v > datetime(2100, 12, 31)):
            raise ValueError('start_datetime must be between 1900 and 2100')
        return v


class CalendarEventInfo(CalendarEventBase):
    """Schema for calendar event responses."""
    id: int
    creator_id: int | None = None
    created_at: datetime
    updated_at: datetime
    parent_event_id: int | None = None
    is_recurring: bool = False
    is_instance: bool = False


class CalendarEventListResponse(BaseModel):
    """Schema for calendar event list responses."""
    events: list[CalendarEventInfo]
    total: int
    start_date: datetime | None = None
    end_date: datetime | None = None


class CalendarEventQueryParams(BaseModel):
    """Schema for calendar event query parameters."""
    start_date: datetime | None = Field(None)
    end_date: datetime | None = Field(None)
    event_type: EventType | None = Field(None)
    status: EventStatus | None = Field(None)
    creator_id: int | None = Field(None)
    include_all_day: bool = Field(default=True)
    include_recurring: bool = Field(default=True)
    timezone: str | None = Field(None, max_length=50)

    @field_validator('end_date')
    @classmethod
    def validate_date_range(cls, v, info):
        if v and info.data.get('start_date') and v < info.data['start_date']:
            raise ValueError('end_date must be after start_date')
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
    count: int | None = Field(None, ge=1, le=999)
    until: datetime | None = None
    by_weekday: list[int] | None = Field(None, description="0=Monday, 6=Sunday")
    by_monthday: list[int] | None = Field(None, description="1-31")
    by_month: list[int] | None = Field(None, description="1-12")

    @field_validator('frequency')
    @classmethod
    def validate_frequency(cls, v):
        allowed = ['DAILY', 'WEEKLY', 'MONTHLY', 'YEARLY']
        if v.upper() not in allowed:
            raise ValueError(f'frequency must be one of: {", ".join(allowed)}')
        return v.upper()
