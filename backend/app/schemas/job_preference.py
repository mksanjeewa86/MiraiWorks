"""Job Preference schemas for API validation and serialization."""

from datetime import date

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

    desired_job_types: str | None = None  # Comma-separated: Full-time, Part-time, etc.
    desired_salary_min: int | None = Field(None, ge=0)
    desired_salary_max: int | None = Field(None, ge=0)
    salary_currency: str = Field(default="USD", max_length=10)
    salary_period: str = Field(default="yearly", max_length=20)
    willing_to_relocate: bool = False
    preferred_locations: str | None = None  # Comma-separated
    work_mode_preferences: str | None = None  # Remote, Hybrid, Onsite
    available_from: date | None = None
    notice_period_days: int | None = Field(None, ge=0, le=365)
    job_search_status: str = Field(default="not_looking", max_length=50)
    preferred_industries: str | None = None  # Comma-separated
    preferred_company_sizes: str | None = None  # Startup, SME, Enterprise
    other_preferences: str | None = None


# Create schema (for POST requests)
class JobPreferenceCreate(JobPreferenceBase):
    """Schema for creating a new job preference."""

    pass


# Update schema (for PUT/PATCH requests)
class JobPreferenceUpdate(BaseModel):
    """Schema for updating an existing job preference."""

    desired_job_types: str | None = None
    desired_salary_min: int | None = Field(None, ge=0)
    desired_salary_max: int | None = Field(None, ge=0)
    salary_currency: str | None = Field(None, max_length=10)
    salary_period: str | None = Field(None, max_length=20)
    willing_to_relocate: bool | None = None
    preferred_locations: str | None = None
    work_mode_preferences: str | None = None
    available_from: date | None = None
    notice_period_days: int | None = Field(None, ge=0, le=365)
    job_search_status: str | None = Field(None, max_length=50)
    preferred_industries: str | None = None
    preferred_company_sizes: str | None = None
    other_preferences: str | None = None


# Response schema (what API returns)
class JobPreferenceInfo(JobPreferenceBase):
    """Schema for job preference information in API responses."""

    id: int
    user_id: int

    class Config:
        from_attributes = True  # Allows Pydantic to work with ORM models
