from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr


# Enums
class CalendarProvider(str, Enum):
    GOOGLE = "google"
    OUTLOOK = "outlook"


class CalendarConnectionStatus(str, Enum):
    CONNECTED = "connected"
    DISABLED = "disabled"
    EXPIRED = "expired"
    ERROR = "error"


class CalendarConnectionBase(BaseModel):
    provider: str
    provider_email: EmailStr
    display_name: str | None = None
    is_enabled: bool = True
    sync_events: bool = True
    sync_reminders: bool = True
    auto_create_meetings: bool = False


class CalendarConnectionCreate(CalendarConnectionBase):
    access_token: str
    refresh_token: str | None = None
    token_expires_at: datetime | None = None
    provider_account_id: str
    calendar_ids: list[str] | None = None
    default_calendar_id: str | None = None


class CalendarConnectionUpdate(BaseModel):
    display_name: str | None = None
    is_enabled: bool | None = None
    sync_events: bool | None = None
    sync_reminders: bool | None = None
    auto_create_meetings: bool | None = None
    calendar_ids: list[str] | None = None
    default_calendar_id: str | None = None


class CalendarConnection(CalendarConnectionBase):
    id: int
    user_id: int
    provider_account_id: str
    status: str
    last_sync_at: datetime | None = None
    sync_error: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CalendarConnectionPublic(BaseModel):
    """Public version without sensitive tokens"""

    id: int
    provider: str
    provider_email: EmailStr
    display_name: str | None
    is_enabled: bool
    sync_events: bool
    sync_reminders: bool
    auto_create_meetings: bool
    status: str
    last_sync_at: datetime | None
    sync_error: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GoogleCalendarAuth(BaseModel):
    """Google Calendar OAuth response"""

    code: str
    state: str | None = None


class OutlookCalendarAuth(BaseModel):
    """Outlook Calendar OAuth response"""

    code: str
    state: str | None = None


class CalendarConnectionResponse(BaseModel):
    message: str
    connection: CalendarConnectionPublic


class CalendarListResponse(BaseModel):
    connections: list[CalendarConnectionPublic]
