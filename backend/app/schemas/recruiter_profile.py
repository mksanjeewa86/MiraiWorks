"""Recruiter profile schemas"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class RecruiterProfileBase(BaseModel):
    """Base schema for recruiter profile"""

    years_of_experience: Optional[int] = Field(None, ge=0, le=50)
    specializations: Optional[str] = Field(
        None, max_length=500, description="Comma-separated specializations"
    )
    bio: Optional[str] = Field(None, max_length=1000)
    company_description: Optional[str] = Field(None, max_length=1000)

    # Recruitment focus
    industries: Optional[str] = Field(
        None, max_length=500, description="Comma-separated industries"
    )
    job_types: Optional[str] = Field(
        None, max_length=200, description="Comma-separated job types"
    )
    locations: Optional[str] = Field(
        None, max_length=500, description="Comma-separated locations"
    )
    experience_levels: Optional[str] = Field(
        None, max_length=200, description="Comma-separated experience levels"
    )

    # Contact preferences
    calendar_link: Optional[str] = Field(None, max_length=500)
    linkedin_url: Optional[str] = Field(None, max_length=500)

    # Activity stats
    jobs_posted: Optional[int] = Field(0, ge=0)
    candidates_placed: Optional[int] = Field(0, ge=0)
    active_openings: Optional[int] = Field(0, ge=0)

    display_order: int = Field(0, ge=0)


class RecruiterProfileCreate(RecruiterProfileBase):
    """Schema for creating recruiter profile"""

    pass


class RecruiterProfileUpdate(BaseModel):
    """Schema for updating recruiter profile"""

    years_of_experience: Optional[int] = Field(None, ge=0, le=50)
    specializations: Optional[str] = Field(None, max_length=500)
    bio: Optional[str] = Field(None, max_length=1000)
    company_description: Optional[str] = Field(None, max_length=1000)

    industries: Optional[str] = Field(None, max_length=500)
    job_types: Optional[str] = Field(None, max_length=200)
    locations: Optional[str] = Field(None, max_length=500)
    experience_levels: Optional[str] = Field(None, max_length=200)

    calendar_link: Optional[str] = Field(None, max_length=500)
    linkedin_url: Optional[str] = Field(None, max_length=500)

    jobs_posted: Optional[int] = Field(None, ge=0)
    candidates_placed: Optional[int] = Field(None, ge=0)
    active_openings: Optional[int] = Field(None, ge=0)

    display_order: Optional[int] = Field(None, ge=0)


class RecruiterProfileInfo(RecruiterProfileBase):
    """Schema for recruiter profile info (response)"""

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EmployerProfileInfo(BaseModel):
    """
    Schema for employer profile info (minimal)
    Employers don't have a separate table - just use User fields
    """

    user_id: int
    full_name: str
    email: str
    phone: Optional[str] = None
    job_title: Optional[str] = None
    bio: Optional[str] = None
    company_name: Optional[str] = None
    company_logo_url: Optional[str] = None
    linkedin_url: Optional[str] = None

    class Config:
        from_attributes = True
