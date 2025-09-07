from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, validator


class CalendarAccountCreate(BaseModel):
    provider: str  # 'google' or 'microsoft'

    @validator("provider")
    def validate_provider(cls, v):
        if v not in ["google", "microsoft"]:
            raise ValueError('Provider must be "google" or "microsoft"')
        return v


class CalendarAccountInfo(BaseModel):
    id: int
    provider: str
    email: str
    display_name: Optional[str]
    calendar_id: Optional[str]
    calendar_timezone: Optional[str]
    is_active: bool
    sync_enabled: bool
    last_sync_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class CalendarInfo(BaseModel):
    id: str
    name: str
    description: Optional[str]
    primary: bool = False
    timezone: Optional[str]
    access_role: Optional[str]  # owner, writer, reader


class EventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    start_datetime: datetime
    end_datetime: datetime
    timezone: str = "UTC"
    is_all_day: bool = False
    attendees: list[str] = []  # Email addresses

    @validator("title")
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError("Title is required")
        return v.strip()

    @validator("end_datetime")
    def validate_end_after_start(cls, v, values):
        if "start_datetime" in values and v <= values["start_datetime"]:
            raise ValueError("End datetime must be after start datetime")
        return v


class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    timezone: Optional[str] = None
    attendees: Optional[list[str]] = None

    @validator("title")
    def validate_title(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError("Title cannot be empty")
        return v.strip() if v else v


class EventInfo(BaseModel):
    id: str
    title: str
    description: Optional[str]
    location: Optional[str]
    start_datetime: datetime
    end_datetime: datetime
    timezone: Optional[str]
    is_all_day: bool
    is_recurring: bool
    organizer_email: Optional[str]
    attendees: list[str]
    status: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CalendarSyncRequest(BaseModel):
    calendar_ids: Optional[list[str]] = None  # Specific calendars to sync
    full_sync: bool = False  # Full sync vs incremental


class CalendarSyncResponse(BaseModel):
    success: bool
    synced_events: int
    errors: list[str] = []
    last_sync_token: Optional[str] = None


class EventsListRequest(BaseModel):
    calendar_id: Optional[str] = None  # Default calendar if not specified
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    max_results: int = 100
    search_query: Optional[str] = None

    @validator("max_results")
    def validate_max_results(cls, v):
        if v > 500:
            raise ValueError("max_results cannot exceed 500")
        return v


class EventsListResponse(BaseModel):
    events: list[EventInfo]
    next_sync_token: Optional[str] = None
    has_more: bool = False


class CalendarConflict(BaseModel):
    conflicting_event_id: str
    conflicting_event_title: str
    conflict_start: datetime
    conflict_end: datetime
    overlap_minutes: int


class AvailabilitySlot(BaseModel):
    start_datetime: datetime
    end_datetime: datetime
    duration_minutes: int
    conflicts: list[CalendarConflict] = []


class AvailabilityRequest(BaseModel):
    user_ids: list[int]
    start_date: datetime
    end_date: datetime
    duration_minutes: int = 60
    working_hours_start: str = "09:00"  # HH:MM format
    working_hours_end: str = "17:00"  # HH:MM format
    timezone: str = "UTC"
    exclude_weekends: bool = True

    @validator("user_ids")
    def validate_user_ids(cls, v):
        if not v:
            raise ValueError("At least one user ID is required")
        return v

    @validator("duration_minutes")
    def validate_duration(cls, v):
        if v <= 0 or v > 480:  # Max 8 hours
            raise ValueError("Duration must be between 1 and 480 minutes")
        return v


class AvailabilityResponse(BaseModel):
    available_slots: list[AvailabilitySlot]
    participants: list[int]
    timezone: str
    total_slots: int


class WebhookVerification(BaseModel):
    challenge: Optional[str] = None
    validation_token: Optional[str] = None


class CalendarWebhookData(BaseModel):
    resource: str
    change_type: str
    client_state: Optional[str] = None
    subscription_id: Optional[str] = None
    resource_data: Optional[dict[str, Any]] = None
