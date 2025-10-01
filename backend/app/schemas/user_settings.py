
from typing import Optional

from pydantic import BaseModel, ConfigDict


class UserSettingsResponse(BaseModel):
    # Profile settings
    job_title: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

    # Notification preferences
    email_notifications: bool = True
    push_notifications: bool = True
    sms_notifications: bool = False
    interview_reminders: bool = True
    application_updates: bool = True
    message_notifications: bool = True

    # UI preferences
    language: str = "en"
    timezone: str = "America/New_York"
    date_format: str = "MM/DD/YYYY"

    # Security settings (from User model)
    require_2fa: bool = False

    model_config = ConfigDict(from_attributes=True)


class UserSettingsUpdate(BaseModel):
    # Profile settings
    job_title: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

    # Notification preferences
    email_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None
    sms_notifications: Optional[bool] = None
    interview_reminders: Optional[bool] = None
    application_updates: Optional[bool] = None
    message_notifications: Optional[bool] = None

    # UI preferences
    language: Optional[str] = None
    timezone: Optional[str] = None
    date_format: Optional[str] = None

    # Security settings (from User model)
    require_2fa: Optional[bool] = None


class UserProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    job_title: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None


class UserProfileResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    full_name: str
    job_title: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
