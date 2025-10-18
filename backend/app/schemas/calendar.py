from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, field_serializer


class CalendarAccountCreate(BaseModel):
    provider: str  # 'google' or 'microsoft'

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, v):
        if v not in ["google", "microsoft"]:
            raise ValueError('Provider must be "google" or "microsoft"')
        return v


class CalendarAccountInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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
    start_datetime: datetime = Field(alias="startDatetime")
    end_datetime: datetime = Field(alias="endDatetime")
    timezone: str = "UTC"
    is_all_day: bool = Field(default=False, alias="isAllDay")
    attendees: list[str] = Field(default_factory=list)  # Email addresses

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError("Title is required")
        return v.strip()

    @field_validator("end_datetime")
    @classmethod
    def validate_end_after_start(cls, v, info):
        start_datetime = info.data.get("start_datetime") or info.data.get(
            "startDatetime"
        )
        if start_datetime and v <= start_datetime:
            raise ValueError("End datetime must be after start datetime")
        return v


class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    timezone: Optional[str] = None
    attendees: list[str] | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError("Title cannot be empty")
        return v.strip() if v else v


class EventInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    title: str
    description: Optional[str]
    location: Optional[str]
    start_datetime: datetime = Field(alias="startDatetime")
    end_datetime: datetime = Field(alias="endDatetime")
    timezone: Optional[str]
    is_all_day: bool = Field(alias="isAllDay")
    is_recurring: bool = Field(alias="isRecurring")
    organizer_email: Optional[str] = Field(alias="organizerEmail")
    attendees: list[str]
    status: Optional[str]
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

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


class CalendarSyncRequest(BaseModel):
    calendar_ids: list[str] | None = None  # Specific calendars to sync
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

    @field_validator("max_results")
    @classmethod
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

    @field_validator("user_ids")
    @classmethod
    def validate_user_ids(cls, v):
        if not v:
            raise ValueError("At least one user ID is required")
        return v

    @field_validator("duration_minutes")
    @classmethod
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
    resource_data: dict[str, Any] | None = None
