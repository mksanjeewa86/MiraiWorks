from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


# Enums
class JobStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    PAUSED = "paused"
    CLOSED = "closed"
    ARCHIVED = "archived"


class JobType(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    TEMPORARY = "temporary"
    INTERNSHIP = "internship"
    FREELANCE = "freelance"


class ExperienceLevel(str, Enum):
    ENTRY_LEVEL = "entry_level"
    MID_LEVEL = "mid_level"
    SENIOR_LEVEL = "senior_level"
    EXECUTIVE = "executive"
    INTERNSHIP = "internship"


class RemoteType(str, Enum):
    ON_SITE = "on_site"
    REMOTE = "remote"
    HYBRID = "hybrid"


class SalaryType(str, Enum):
    HOURLY = "hourly"
    DAILY = "daily"
    MONTHLY = "monthly"
    ANNUAL = "annual"
    PROJECT = "project"


class ApplicationStatus(str, Enum):
    APPLIED = "applied"
    UNDER_REVIEW = "under_review"
    PHONE_SCREEN = "phone_screen"
    INTERVIEW = "interview"
    TECHNICAL_TEST = "technical_test"
    FINAL_INTERVIEW = "final_interview"
    OFFER_SENT = "offer_sent"
    HIRED = "hired"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


# Base Schemas
class JobBase(BaseModel):
    title: str = Field(..., max_length=255, min_length=1)
    description: str = Field(..., min_length=10)
    summary: Optional[str] = Field(None, max_length=1000)
    department: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=255)
    country: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    job_type: JobType = JobType.FULL_TIME
    experience_level: ExperienceLevel = ExperienceLevel.MID_LEVEL
    remote_type: RemoteType = RemoteType.ON_SITE
    requirements: Optional[str] = None
    preferred_skills: Optional[List[str]] = None  # Will be JSON serialized
    required_skills: Optional[List[str]] = None  # Will be JSON serialized
    benefits: Optional[List[str]] = None  # Will be JSON serialized
    perks: Optional[List[str]] = None  # Will be JSON serialized
    application_deadline: Optional[datetime] = None
    external_apply_url: Optional[str] = Field(None, max_length=1000)
    application_questions: Optional[List[dict]] = None  # Will be JSON serialized
    is_featured: bool = False
    is_urgent: bool = False
    seo_title: Optional[str] = Field(None, max_length=255)
    seo_description: Optional[str] = Field(None, max_length=500)
    social_image_url: Optional[str] = Field(None, max_length=1000)


class JobSalaryInfo(BaseModel):
    salary_min: Optional[int] = Field(None, gt=0)  # In cents
    salary_max: Optional[int] = Field(None, gt=0)  # In cents
    salary_type: SalaryType = SalaryType.ANNUAL
    salary_currency: str = Field("USD", max_length=3)
    show_salary: bool = False

    @field_validator('salary_max')
    @classmethod
    def salary_max_greater_than_min(cls, v, info):
        if info.data.get('salary_min') and v and v <= info.data['salary_min']:
            raise ValueError('salary_max must be greater than salary_min')
        return v


class JobCreate(JobBase, JobSalaryInfo):
    company_id: int
    posted_by: Optional[int] = None


class JobUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255, min_length=1)
    description: Optional[str] = Field(None, min_length=10)
    summary: Optional[str] = Field(None, max_length=1000)
    department: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=255)
    country: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    job_type: Optional[JobType] = None
    experience_level: Optional[ExperienceLevel] = None
    remote_type: Optional[RemoteType] = None
    requirements: Optional[str] = None
    preferred_skills: Optional[List[str]] = None
    required_skills: Optional[List[str]] = None
    benefits: Optional[List[str]] = None
    perks: Optional[List[str]] = None
    salary_min: Optional[int] = Field(None, gt=0)
    salary_max: Optional[int] = Field(None, gt=0)
    salary_type: Optional[SalaryType] = None
    salary_currency: Optional[str] = Field(None, max_length=3)
    show_salary: Optional[bool] = None
    application_deadline: Optional[datetime] = None
    external_apply_url: Optional[str] = Field(None, max_length=1000)
    application_questions: Optional[List[dict]] = None
    status: Optional[JobStatus] = None
    is_featured: Optional[bool] = None
    is_urgent: Optional[bool] = None
    seo_title: Optional[str] = Field(None, max_length=255)
    seo_description: Optional[str] = Field(None, max_length=500)
    social_image_url: Optional[str] = Field(None, max_length=1000)


class JobInfo(JobBase, JobSalaryInfo):
    title: str = Field(default="", max_length=255)
    description: Optional[str] = None
    id: int
    slug: Optional[str] = None
    company_id: int
    status: JobStatus = JobStatus.DRAFT
    view_count: int = 0
    application_count: int = 0
    published_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    posted_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator("title", mode="before")
    @classmethod
    def _default_title(cls, value):
        return value or ""

    @field_validator("job_type", "experience_level", "remote_type", "salary_type", "status", mode="before")
    @classmethod
    def _default_enum_fields(cls, value, info):
        if value is None:
            defaults = {
                "job_type": JobType.FULL_TIME,
                "experience_level": ExperienceLevel.MID_LEVEL,
                "remote_type": RemoteType.ON_SITE,
                "salary_type": SalaryType.ANNUAL,
                "status": JobStatus.DRAFT,
            }
            return defaults[info.field_name]
        return value

    @field_validator("salary_currency", mode="before")
    @classmethod
    def _default_salary_currency(cls, value):
        return value or "USD"

    @field_validator("show_salary", "is_featured", "is_urgent", mode="before")
    @classmethod
    def _default_bool_fields(cls, value):
        return bool(value) if value is not None else False

    @field_validator("view_count", "application_count", mode="before")
    @classmethod
    def _default_int_fields(cls, value):
        return 0 if value is None else value

    # Computed properties
    is_active: bool = False
    days_since_published: Optional[int] = None
    salary_range_display: Optional[str] = None

    # Company info (from relationship)
    company_name: Optional[str] = None
    company_logo_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)



# Job Application Schemas
class JobApplicationBase(BaseModel):
    cover_letter: Optional[str] = None
    application_answers: Optional[List[dict]] = None  # Will be JSON serialized
    source: Optional[str] = Field(None, max_length=100)


class JobApplicationCreate(JobApplicationBase):
    job_id: int
    resume_id: Optional[int] = None


class JobApplicationUpdate(BaseModel):
    status: Optional[ApplicationStatus] = None
    cover_letter: Optional[str] = None
    notes: Optional[str] = None
    last_contacted_at: Optional[datetime] = None


class JobApplicationInfo(JobApplicationBase):
    id: int
    job_id: int
    candidate_id: int
    resume_id: Optional[int] = None
    status: ApplicationStatus = ApplicationStatus.APPLIED
    status_updated_at: datetime
    status_updated_by: Optional[int] = None
    last_contacted_at: Optional[datetime] = None
    notes: Optional[str] = None
    referrer_id: Optional[int] = None
    applied_at: datetime
    updated_at: datetime

    # Computed properties
    is_active: bool = False
    days_since_applied: int = 0

    # Related info
    job_title: Optional[str] = None
    candidate_name: Optional[str] = None
    candidate_email: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# Company Profile Schemas
class CompanyProfileBase(BaseModel):
    tagline: Optional[str] = Field(None, max_length=255)
    mission: Optional[str] = None
    values: Optional[List[str]] = None  # Will be JSON serialized
    culture: Optional[str] = None
    logo_url: Optional[str] = Field(None, max_length=1000)
    banner_url: Optional[str] = Field(None, max_length=1000)
    gallery_images: Optional[List[str]] = None  # Will be JSON serialized
    company_video_url: Optional[str] = Field(None, max_length=1000)
    contact_email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    linkedin_url: Optional[str] = Field(None, max_length=500)
    twitter_url: Optional[str] = Field(None, max_length=500)
    facebook_url: Optional[str] = Field(None, max_length=500)
    instagram_url: Optional[str] = Field(None, max_length=500)
    youtube_url: Optional[str] = Field(None, max_length=500)
    founded_year: Optional[int] = Field(None, ge=1800, le=2030)
    employee_count: Optional[str] = Field(None, max_length=50)
    headquarters: Optional[str] = Field(None, max_length=255)
    funding_stage: Optional[str] = Field(None, max_length=100)
    benefits_summary: Optional[str] = None
    perks_highlights: Optional[List[str]] = None  # Will be JSON serialized
    is_public: bool = True
    seo_title: Optional[str] = Field(None, max_length=255)
    seo_description: Optional[str] = Field(None, max_length=500)
    custom_slug: Optional[str] = Field(None, max_length=100, pattern=r'^[a-zA-Z0-9-_]+$')


class CompanyProfileCreate(CompanyProfileBase):
    company_id: int


class CompanyProfileUpdate(CompanyProfileBase):
    pass


class CompanyProfileInfo(CompanyProfileBase):
    id: int
    company_id: int
    profile_views: int = 0
    last_updated_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    public_slug: str

    # Company info
    company_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# List and Filter Schemas
class JobListParams(BaseModel):
    search: Optional[str] = None
    company_id: Optional[int] = None
    job_type: Optional[JobType] = None
    experience_level: Optional[ExperienceLevel] = None
    remote_type: Optional[RemoteType] = None
    location: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    status: Optional[JobStatus] = None
    is_featured: Optional[bool] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    sort_by: Optional[str] = Field("published_at", pattern=r'^(published_at|created_at|title|salary_min|view_count)$')
    sort_order: Optional[str] = Field("desc", pattern=r'^(asc|desc)$')
    limit: int = Field(50, ge=1, le=100)
    offset: int = Field(0, ge=0)


class JobListResponse(BaseModel):
    jobs: List[JobInfo]
    total: int
    skip: int = 0
    limit: int = 0
    has_more: bool = False

    model_config = ConfigDict(from_attributes=True)



class JobStatusUpdateRequest(BaseModel):
    status: JobStatus


class JobBulkStatusUpdateRequest(BaseModel):
    job_ids: List[int] = Field(..., min_length=1)
    status: JobStatus


class JobApplicationListParams(BaseModel):
    job_id: Optional[int] = None
    candidate_id: Optional[int] = None
    status: Optional[ApplicationStatus] = None
    applied_after: Optional[datetime] = None
    applied_before: Optional[datetime] = None
    sort_by: Optional[str] = Field("applied_at", pattern=r'^(applied_at|status_updated_at)$')
    sort_order: Optional[str] = Field("desc", pattern=r'^(asc|desc)$')
    limit: int = Field(50, ge=1, le=100)
    offset: int = Field(0, ge=0)


class JobApplicationListResponse(BaseModel):
    applications: List[JobApplicationInfo]
    total: int
    has_more: bool = False


class JobStatsResponse(BaseModel):
    total_jobs: int
    by_status: dict = Field(default_factory=dict)
    by_type: dict = Field(default_factory=dict)
    by_experience_level: dict = Field(default_factory=dict)
    published_this_month: int = 0
    total_applications: int = 0
    average_applications_per_job: float = 0
    most_viewed_jobs: List[JobInfo] = Field(default_factory=list)


class JobSearchResponse(BaseModel):
    jobs: List[JobInfo]
    total: int
    facets: dict = Field(default_factory=dict)  # For search faceting
    has_more: bool = False
    search_query: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


