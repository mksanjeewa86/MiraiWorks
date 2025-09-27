from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.position import (
    ApplicationStatus,
    ExperienceLevel,
    PositionStatus,
    PositionType,
    RemoteType,
    SalaryType,
)


# Company Profile Schemas
class CompanyProfileBase(BaseModel):
    tagline: str | None = None
    mission: str | None = None
    values: list[str] | None = None
    culture: str | None = None
    logo_url: str | None = None
    banner_url: str | None = None
    gallery_images: list[str] | None = None
    company_video_url: str | None = None
    contact_email: str | None = None
    phone: str | None = None
    address: str | None = None
    linkedin_url: str | None = None
    twitter_url: str | None = None
    facebook_url: str | None = None
    instagram_url: str | None = None
    youtube_url: str | None = None
    founded_year: int | None = Field(None, ge=1800, le=datetime.now().year)
    employee_count: str | None = None
    headquarters: str | None = None
    funding_stage: str | None = None
    benefits_summary: str | None = None
    perks_highlights: list[str] | None = None
    custom_slug: str | None = Field(
        None, min_length=3, max_length=100, pattern="^[a-z0-9-]+$"
    )


class CompanyProfileCreate(CompanyProfileBase):
    pass


class CompanyProfileUpdate(BaseModel):
    tagline: str | None = None
    mission: str | None = None
    values: list[str] | None = None
    culture: str | None = None
    logo_url: str | None = None
    banner_url: str | None = None
    gallery_images: list[str] | None = None
    company_video_url: str | None = None
    contact_email: str | None = None
    phone: str | None = None
    address: str | None = None
    linkedin_url: str | None = None
    twitter_url: str | None = None
    facebook_url: str | None = None
    instagram_url: str | None = None
    youtube_url: str | None = None
    founded_year: int | None = Field(None, ge=1800, le=datetime.now().year)
    employee_count: str | None = None
    headquarters: str | None = None
    funding_stage: str | None = None
    benefits_summary: str | None = None
    perks_highlights: list[str] | None = None
    is_public: bool | None = None
    custom_slug: str | None = Field(
        None, min_length=3, max_length=100, pattern="^[a-z0-9-]+$"
    )


class CompanyProfileResponse(CompanyProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    is_public: bool
    profile_views: int
    public_slug: str
    created_at: datetime
    updated_at: datetime


# Public Company Schema
class PublicCompany(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    domain: str | None = None
    website: str | None = None
    description: str | None = None
    profile: CompanyProfileResponse | None = None


# Position Schemas
class PositionBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    summary: str | None = Field(None, max_length=500)
    description: str = Field(..., min_length=50)
    department: str | None = Field(None, max_length=100)
    location: str | None = Field(None, max_length=255)
    country: str | None = Field(None, max_length=100)
    city: str | None = Field(None, max_length=100)
    job_type: PositionType = PositionType.FULL_TIME
    experience_level: ExperienceLevel = ExperienceLevel.MID_LEVEL
    remote_type: RemoteType = RemoteType.ON_SITE
    requirements: str | None = None
    preferred_skills: list[str] | None = None
    required_skills: list[str] | None = None
    salary_min: int | None = Field(None, ge=0)  # In cents
    salary_max: int | None = Field(None, ge=0)  # In cents
    salary_type: SalaryType = SalaryType.ANNUAL
    salary_currency: str = Field("USD", min_length=3, max_length=3)
    show_salary: bool = False
    benefits: list[str] | None = None
    perks: list[str] | None = None
    application_deadline: datetime | None = None
    external_apply_url: str | None = None
    application_questions: list[dict[str, Any]] | None = None

    @field_validator("salary_max")
    @classmethod
    def salary_max_greater_than_min(cls, v, info):
        salary_min = info.data.get("salary_min")
        if v is not None and salary_min is not None and v <= salary_min:
            raise ValueError("salary_max must be greater than salary_min")
        return v

    @field_validator("application_deadline")
    @classmethod
    def deadline_in_future(cls, v):
        if v is not None and v <= datetime.utcnow():
            raise ValueError("application_deadline must be in the future")
        return v


class PositionCreate(PositionBase):
    pass


class PositionUpdate(BaseModel):
    title: str | None = Field(None, min_length=3, max_length=255)
    summary: str | None = Field(None, max_length=500)
    description: str | None = Field(None, min_length=50)
    department: str | None = Field(None, max_length=100)
    location: str | None = Field(None, max_length=255)
    country: str | None = Field(None, max_length=100)
    city: str | None = Field(None, max_length=100)
    job_type: PositionType | None = None
    experience_level: ExperienceLevel | None = None
    remote_type: RemoteType | None = None
    requirements: str | None = None
    preferred_skills: list[str] | None = None
    required_skills: list[str] | None = None
    salary_min: int | None = Field(None, ge=0)
    salary_max: int | None = Field(None, ge=0)
    salary_type: SalaryType | None = None
    salary_currency: str | None = Field(None, min_length=3, max_length=3)
    show_salary: bool | None = None
    benefits: list[str] | None = None
    perks: list[str] | None = None
    application_deadline: datetime | None = None
    external_apply_url: str | None = None
    application_questions: list[dict[str, Any]] | None = None
    status: PositionStatus | None = None
    is_featured: bool | None = None
    is_urgent: bool | None = None


class PositionResponse(PositionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    company_id: int
    status: PositionStatus
    is_featured: bool
    is_urgent: bool
    view_count: int
    application_count: int
    published_at: datetime | None = None
    expires_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    # Computed properties
    is_active: bool
    days_since_published: int | None = None
    salary_range_display: str | None = None
    can_apply: bool

    # Company information (populated from relationship)
    company: PublicCompany | None = None


class PositionSummary(BaseModel):
    """Lightweight job summary for listings"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    slug: str
    summary: str | None = None
    company_id: int
    company_name: str
    company_logo: str | None = None
    location: str | None = None
    job_type: PositionType
    experience_level: ExperienceLevel
    remote_type: RemoteType
    salary_range_display: str | None = None
    is_featured: bool
    is_urgent: bool
    published_at: datetime | None = None
    days_since_published: int | None = None


# Job Application Schemas
class PositionApplicationBase(BaseModel):
    cover_letter: str | None = Field(None, max_length=5000)
    application_answers: dict[str, Any] | None = None
    source: str | None = Field(None, max_length=100)


class PositionApplicationCreate(PositionApplicationBase):
    position_id: int
    resume_id: int | None = None


class PositionApplicationUpdate(BaseModel):
    cover_letter: str | None = Field(None, max_length=5000)
    status: ApplicationStatus | None = None
    notes: str | None = None


class PositionApplicationResponse(PositionApplicationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    position_id: int
    candidate_id: int
    resume_id: int | None = None
    status: ApplicationStatus
    status_updated_at: datetime
    applied_at: datetime
    updated_at: datetime

    # Computed properties
    is_active: bool
    days_since_applied: int

    # Related data (populated when needed)
    position: PositionResponse | None = None
    candidate: dict[str, Any] | None = None  # Limited candidate info


# Search and filtering schemas
class PositionSearchParams(BaseModel):
    q: str | None = None  # Search query
    location: str | None = None
    country: str | None = None
    city: str | None = None
    company_id: int | None = None
    job_type: PositionType | None = None
    experience_level: ExperienceLevel | None = None
    remote_type: RemoteType | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    skills: list[str] | None = None
    sort_by: str = Field(
        "published_date", pattern="^(published_date|relevance|salary|company)$"
    )
    sort_order: str = Field("desc", pattern="^(asc|desc)$")
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)
    featured_only: bool = False


class PositionSearchResponse(BaseModel):
    positions: list[PositionSummary]
    total: int
    page: int
    limit: int
    total_pages: int
    filters: dict[str, Any]  # Available filter values


class CompanySearchParams(BaseModel):
    q: str | None = None
    industry: str | None = None
    location: str | None = None
    employee_count: str | None = None
    funding_stage: str | None = None
    sort_by: str = Field("name", pattern="^(name|founded_year|employee_count)$")
    sort_order: str = Field("asc", pattern="^(asc|desc)$")
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)


class CompanySearchResponse(BaseModel):
    companies: list[PublicCompany]
    total: int
    page: int
    limit: int
    total_pages: int


# Public statistics
class PublicStats(BaseModel):
    total_companies: int
    total_positions: int
    total_applications: int
    featured_companies: list[PublicCompany]
    latest_positions: list[PositionSummary]
    job_categories: dict[str, int]  # job_type -> count
    location_stats: dict[str, int]  # location -> count
