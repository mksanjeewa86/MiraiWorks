"""Job Preference schemas for API validation and serialization."""

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


# Enums
class JobSearchStatus:
    """Job search status constants."""

    ACTIVELY_LOOKING = "actively_looking"
    OPEN_TO_OPPORTUNITIES = "open_to_opportunities"
    NOT_LOOKING = "not_looking"


class SalaryPeriod:
    """Salary period constants."""

    YEARLY = "yearly"
    MONTHLY = "monthly"
    HOURLY = "hourly"


# Base schema
class JobPreferenceBase(BaseModel):
    """Base job preference schema with common fields."""

    desired_job_types: Optional[
        str
    ] = None  # Comma-separated: Full-time, Part-time, etc.
    desired_salary_min: Optional[int] = Field(None, ge=0)
    desired_salary_max: Optional[int] = Field(None, ge=0)
    salary_currency: str = Field(default="USD", max_length=10)
    salary_period: str = Field(default="yearly", max_length=20)
    willing_to_relocate: bool = False
    preferred_locations: Optional[str] = None  # Comma-separated
    work_mode_preferences: Optional[str] = None  # Remote, Hybrid, Onsite
    available_from: Optional[date] = None
    notice_period_days: Optional[int] = Field(None, ge=0, le=365)
    job_search_status: str = Field(default="not_looking", max_length=50)
    preferred_industries: Optional[str] = None  # Comma-separated
    preferred_company_sizes: Optional[str] = None  # Startup, SME, Enterprise
    other_preferences: Optional[str] = None


# Create schema (for POST requests)
class JobPreferenceCreate(JobPreferenceBase):
    """Schema for creating a new job preference."""

    pass


# Update schema (for PUT/PATCH requests)
class JobPreferenceUpdate(BaseModel):
    """Schema for updating an existing job preference."""

    desired_job_types: Optional[str] = None
    desired_salary_min: Optional[int] = Field(None, ge=0)
    desired_salary_max: Optional[int] = Field(None, ge=0)
    salary_currency: Optional[str] = Field(None, max_length=10)
    salary_period: Optional[str] = Field(None, max_length=20)
    willing_to_relocate: Optional[bool] = None
    preferred_locations: Optional[str] = None
    work_mode_preferences: Optional[str] = None
    available_from: Optional[date] = None
    notice_period_days: Optional[int] = Field(None, ge=0, le=365)
    job_search_status: Optional[str] = Field(None, max_length=50)
    preferred_industries: Optional[str] = None
    preferred_company_sizes: Optional[str] = None
    other_preferences: Optional[str] = None


# Response schema (what API returns)
class JobPreferenceInfo(JobPreferenceBase):
    """Schema for job preference information in API responses."""

    id: int
    user_id: int

    class Config:
        from_attributes = True  # Allows Pydantic to work with ORM models
