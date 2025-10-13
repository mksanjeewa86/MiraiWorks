"""Privacy settings schemas - Section-specific profile visibility controls"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ProfileVisibility(str, Enum):
    """Profile visibility levels"""

    PUBLIC = "public"
    RECRUITERS_ONLY = "recruiters"
    PRIVATE = "private"


class PrivacySettingsBase(BaseModel):
    """Base privacy settings schema with default values"""
    profile_visibility: Optional[str] = Field(default="public", description="Profile visibility level")
    searchable: Optional[bool] = Field(default=True, description="Allow profile to appear in searches")
    show_email: Optional[bool] = Field(default=False, description="Show email address")
    show_phone: Optional[bool] = Field(default=False, description="Show phone number")
    show_work_experience: Optional[bool] = Field(default=True, description="Show work experience")
    show_education: Optional[bool] = Field(default=True, description="Show education")
    show_skills: Optional[bool] = Field(default=True, description="Show skills")
    show_certifications: Optional[bool] = Field(default=True, description="Show certifications")
    show_projects: Optional[bool] = Field(default=True, description="Show projects")
    show_resume: Optional[bool] = Field(default=True, description="Allow resume download")


class PrivacySettingsUpdate(BaseModel):
    """
    Schema for updating privacy settings.

    Supports partial updates - only include fields you want to update.
    Used by section-specific privacy toggles on profile pages.

    Example: {"show_work_experience": false} updates only that field.
    """
    profile_visibility: Optional[str] = None
    searchable: Optional[bool] = None
    show_email: Optional[bool] = None
    show_phone: Optional[bool] = None
    show_work_experience: Optional[bool] = None
    show_education: Optional[bool] = None
    show_skills: Optional[bool] = None
    show_certifications: Optional[bool] = None
    show_projects: Optional[bool] = None
    show_resume: Optional[bool] = None


class PrivacySettingsInfo(PrivacySettingsBase):
    """Schema for privacy settings response"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
