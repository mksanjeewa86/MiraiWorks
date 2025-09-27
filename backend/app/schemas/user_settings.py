
from pydantic import BaseModel, ConfigDict


class UserSettingsResponse(BaseModel):
    # Profile settings
    job_title: str | None = None
    bio: str | None = None
    avatar_url: str | None = None

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
    job_title: str | None = None
    bio: str | None = None
    avatar_url: str | None = None

    # Notification preferences
    email_notifications: bool | None = None
    push_notifications: bool | None = None
    sms_notifications: bool | None = None
    interview_reminders: bool | None = None
    application_updates: bool | None = None
    message_notifications: bool | None = None

    # UI preferences
    language: str | None = None
    timezone: str | None = None
    date_format: str | None = None

    # Security settings (from User model)
    require_2fa: bool | None = None


class UserProfileUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    job_title: str | None = None
    bio: str | None = None
    avatar_url: str | None = None


class UserProfileResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    phone: str | None = None
    full_name: str
    job_title: str | None = None
    bio: str | None = None
    avatar_url: str | None = None

    model_config = ConfigDict(from_attributes=True)
