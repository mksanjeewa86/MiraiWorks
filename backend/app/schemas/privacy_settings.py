"""Privacy settings schemas - Section-specific profile visibility controls"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ProfileVisibility(str, Enum):
    """Profile visibility levels"""

    PUBLIC = "public"
    RECRUITERS_ONLY = "recruiters"
    PRIVATE = "private"


class PrivacySettingsBase(BaseModel):
    """Base privacy settings schema with default values"""

    profile_visibility: str | None = Field(
        default="public", description="Profile visibility level"
    )
    searchable: bool | None = Field(
        default=True, description="Allow profile to appear in searches"
    )
    show_email: bool | None = Field(default=False, description="Show email address")
    show_phone: bool | None = Field(default=False, description="Show phone number")
    show_work_experience: bool | None = Field(
        default=True, description="Show work experience"
    )
    show_education: bool | None = Field(default=True, description="Show education")
    show_skills: bool | None = Field(default=True, description="Show skills")
    show_certifications: bool | None = Field(
        default=True, description="Show certifications"
    )
    show_projects: bool | None = Field(default=True, description="Show projects")
    show_resume: bool | None = Field(default=True, description="Allow resume download")


class PrivacySettingsUpdate(BaseModel):
    """
    Schema for updating privacy settings.

    Supports partial updates - only include fields you want to update.
    Used by section-specific privacy toggles on profile pages.

    Example: {"show_work_experience": false} updates only that field.
    """

    profile_visibility: str | None = None
    searchable: bool | None = None
    show_email: bool | None = None
    show_phone: bool | None = None
    show_work_experience: bool | None = None
    show_education: bool | None = None
    show_skills: bool | None = None
    show_certifications: bool | None = None
    show_projects: bool | None = None
    show_resume: bool | None = None


class PrivacySettingsInfo(PrivacySettingsBase):
    """Schema for privacy settings response"""

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
