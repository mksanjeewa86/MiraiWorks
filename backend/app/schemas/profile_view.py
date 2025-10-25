"""Pydantic schemas for profile views."""

from datetime import datetime

from pydantic import BaseModel, Field


class ProfileViewCreate(BaseModel):
    """Schema for creating a profile view."""

    profile_user_id: int = Field(
        ..., description="ID of the user whose profile was viewed"
    )
    view_duration: int | None = Field(
        None, description="Duration of view in seconds"
    )
    referrer: str | None = Field(None, max_length=500, description="Referrer URL")


class ProfileViewInfo(BaseModel):
    """Schema for profile view information."""

    id: int
    profile_user_id: int
    viewer_user_id: int | None = None
    viewer_company_id: int | None = None
    viewer_ip: str | None = None
    viewer_user_agent: str | None = None
    view_duration: int | None = None
    referrer: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class CompanyViewCount(BaseModel):
    """Schema for company view count."""

    company_id: int
    company_name: str
    view_count: int


class ViewOverTime(BaseModel):
    """Schema for views over time."""

    date: str
    count: int


class ProfileViewStats(BaseModel):
    """Schema for profile view statistics."""

    total_views: int = Field(..., description="Total number of profile views")
    unique_viewers: int = Field(..., description="Number of unique viewers")
    views_by_company: list[CompanyViewCount] = Field(
        default_factory=list,
        description="Top companies viewing the profile",
    )
    views_over_time: list[ViewOverTime] = Field(
        default_factory=list,
        description="Views grouped by date",
    )


class RecentViewer(BaseModel):
    """Schema for recent viewer information."""

    viewer_user_id: int
    first_name: str
    last_name: str
    email: str
    company_id: int | None = None
    company_name: str | None = None
    last_viewed: datetime
    view_count: int

    @property
    def full_name(self) -> str:
        """Get the full name of the viewer."""
        return f"{self.first_name} {self.last_name}"
