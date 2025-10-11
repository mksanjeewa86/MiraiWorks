"""
System Update Schemas

Pydantic schemas for system-wide update announcements.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, validator


class SystemUpdateTag(str, Enum):
    """Predefined tags for system updates."""

    SECURITY = "security"
    TODO = "todo"
    INTERVIEW = "interview"
    EXAM = "exam"
    CALENDAR = "calendar"
    WORKFLOW = "workflow"
    MESSAGING = "messaging"
    PROFILE = "profile"
    GENERAL = "general"
    MAINTENANCE = "maintenance"
    FEATURE = "feature"
    BUGFIX = "bugfix"


class SystemUpdateBase(BaseModel):
    """Base schema for system updates."""

    title: str = Field(..., min_length=1, max_length=255, description="Update title")
    message: str = Field(..., min_length=1, description="Update message/content")
    tags: list[SystemUpdateTag] = Field(
        default_factory=list, description="Category tags for the update"
    )

    @validator("tags")
    def validate_tags(cls, v):
        """Ensure tags list doesn't have duplicates."""
        if v and len(v) != len(set(v)):
            raise ValueError("Tags must be unique")
        return v


class SystemUpdateCreate(SystemUpdateBase):
    """Schema for creating a new system update."""

    pass


class SystemUpdateUpdate(BaseModel):
    """Schema for updating an existing system update."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    message: Optional[str] = Field(None, min_length=1)
    tags: Optional[list[SystemUpdateTag]] = None
    is_active: Optional[bool] = None

    @validator("tags")
    def validate_tags(cls, v):
        """Ensure tags list doesn't have duplicates."""
        if v and len(v) != len(set(v)):
            raise ValueError("Tags must be unique")
        return v


class SystemUpdateInfo(SystemUpdateBase):
    """Schema for system update information."""

    id: int
    is_active: bool
    created_by_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SystemUpdateWithCreator(SystemUpdateInfo):
    """Schema for system update with creator information."""

    created_by_name: Optional[str] = None

    class Config:
        from_attributes = True
