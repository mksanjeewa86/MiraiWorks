from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, EmailStr


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
    display_name: Optional[str] = None
    is_enabled: bool = True
    sync_events: bool = True
    sync_reminders: bool = True
    auto_create_meetings: bool = False


class CalendarConnectionCreate(CalendarConnectionBase):
    access_token: str
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    provider_account_id: str
    calendar_ids: Optional[List[str]] = None
    default_calendar_id: Optional[str] = None


class CalendarConnectionUpdate(BaseModel):
    display_name: Optional[str] = None
    is_enabled: Optional[bool] = None
    sync_events: Optional[bool] = None
    sync_reminders: Optional[bool] = None
    auto_create_meetings: Optional[bool] = None
    calendar_ids: Optional[List[str]] = None
    default_calendar_id: Optional[str] = None


class CalendarConnection(CalendarConnectionBase):
    id: int
    user_id: int
    provider_account_id: str
    status: str
    last_sync_at: Optional[datetime] = None
    sync_error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CalendarConnectionPublic(BaseModel):
    """Public version without sensitive tokens"""
    id: int
    provider: str
    provider_email: EmailStr
    display_name: Optional[str]
    is_enabled: bool
    sync_events: bool
    sync_reminders: bool
    auto_create_meetings: bool
    status: str
    last_sync_at: Optional[datetime]
    sync_error: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GoogleCalendarAuth(BaseModel):
    """Google Calendar OAuth response"""
    code: str
    state: Optional[str] = None


class OutlookCalendarAuth(BaseModel):
    """Outlook Calendar OAuth response"""
    code: str
    state: Optional[str] = None


class CalendarConnectionResponse(BaseModel):
    message: str
    connection: CalendarConnectionPublic


class CalendarListResponse(BaseModel):
    connections: List[CalendarConnectionPublic]