"""Recruiter profile schemas"""

from datetime import datetime

from pydantic import BaseModel, Field


class RecruiterProfileBase(BaseModel):
    """Base schema for recruiter profile"""

    years_of_experience: int | None = Field(None, ge=0, le=50)
    specializations: str | None = Field(
        None, max_length=500, description="Comma-separated specializations"
    )
    bio: str | None = Field(None, max_length=1000)
    company_description: str | None = Field(None, max_length=1000)

    # Recruitment focus
    industries: str | None = Field(
        None, max_length=500, description="Comma-separated industries"
    )
    job_types: str | None = Field(
        None, max_length=200, description="Comma-separated job types"
    )
    locations: str | None = Field(
        None, max_length=500, description="Comma-separated locations"
    )
    experience_levels: str | None = Field(
        None, max_length=200, description="Comma-separated experience levels"
    )

    # Contact preferences
    calendar_link: str | None = Field(None, max_length=500)
    linkedin_url: str | None = Field(None, max_length=500)

    # Activity stats
    jobs_posted: int | None = Field(0, ge=0)
    candidates_placed: int | None = Field(0, ge=0)
    active_openings: int | None = Field(0, ge=0)

    display_order: int = Field(0, ge=0)


class RecruiterProfileCreate(RecruiterProfileBase):
    """Schema for creating recruiter profile"""

    pass


class RecruiterProfileUpdate(BaseModel):
    """Schema for updating recruiter profile"""

    years_of_experience: int | None = Field(None, ge=0, le=50)
    specializations: str | None = Field(None, max_length=500)
    bio: str | None = Field(None, max_length=1000)
    company_description: str | None = Field(None, max_length=1000)

    industries: str | None = Field(None, max_length=500)
    job_types: str | None = Field(None, max_length=200)
    locations: str | None = Field(None, max_length=500)
    experience_levels: str | None = Field(None, max_length=200)

    calendar_link: str | None = Field(None, max_length=500)
    linkedin_url: str | None = Field(None, max_length=500)

    jobs_posted: int | None = Field(None, ge=0)
    candidates_placed: int | None = Field(None, ge=0)
    active_openings: int | None = Field(None, ge=0)

    display_order: int | None = Field(None, ge=0)


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
    phone: str | None = None
    job_title: str | None = None
    bio: str | None = None
    company_name: str | None = None
    company_logo_url: str | None = None
    linkedin_url: str | None = None

    class Config:
        from_attributes = True
