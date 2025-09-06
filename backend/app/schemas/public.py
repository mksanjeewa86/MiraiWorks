from datetime import datetime
from enum import Enum
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Field
from pydantic import validator


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


# Company Profile Schemas
class CompanyProfileBase(BaseModel):
    tagline: Optional[str] = None
    mission: Optional[str] = None
    values: Optional[List[str]] = None
    culture: Optional[str] = None
    logo_url: Optional[str] = None
    banner_url: Optional[str] = None
    gallery_images: Optional[List[str]] = None
    company_video_url: Optional[str] = None
    contact_email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None
    facebook_url: Optional[str] = None
    instagram_url: Optional[str] = None
    youtube_url: Optional[str] = None
    founded_year: Optional[int] = Field(None, ge=1800, le=datetime.now().year)
    employee_count: Optional[str] = None
    headquarters: Optional[str] = None
    funding_stage: Optional[str] = None
    benefits_summary: Optional[str] = None
    perks_highlights: Optional[List[str]] = None
    custom_slug: Optional[str] = Field(None, min_length=3, max_length=100, pattern="^[a-z0-9-]+$")


class CompanyProfileCreate(CompanyProfileBase):
    pass


class CompanyProfileUpdate(BaseModel):
    tagline: Optional[str] = None
    mission: Optional[str] = None
    values: Optional[List[str]] = None
    culture: Optional[str] = None
    logo_url: Optional[str] = None
    banner_url: Optional[str] = None
    gallery_images: Optional[List[str]] = None
    company_video_url: Optional[str] = None
    contact_email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None
    facebook_url: Optional[str] = None
    instagram_url: Optional[str] = None
    youtube_url: Optional[str] = None
    founded_year: Optional[int] = Field(None, ge=1800, le=datetime.now().year)
    employee_count: Optional[str] = None
    headquarters: Optional[str] = None
    funding_stage: Optional[str] = None
    benefits_summary: Optional[str] = None
    perks_highlights: Optional[List[str]] = None
    is_public: Optional[bool] = None
    custom_slug: Optional[str] = Field(None, min_length=3, max_length=100, pattern="^[a-z0-9-]+$")


class CompanyProfileResponse(CompanyProfileBase):
    id: int
    company_id: int
    is_public: bool
    profile_views: int
    public_slug: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Public Company Schema
class PublicCompany(BaseModel):
    id: int
    name: str
    domain: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    profile: Optional[CompanyProfileResponse] = None

    class Config:
        from_attributes = True


# Job Schemas
class JobBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    summary: Optional[str] = Field(None, max_length=500)
    description: str = Field(..., min_length=50)
    department: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=255)
    country: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    job_type: JobType = JobType.FULL_TIME
    experience_level: ExperienceLevel = ExperienceLevel.MID_LEVEL
    remote_type: RemoteType = RemoteType.ON_SITE
    requirements: Optional[str] = None
    preferred_skills: Optional[List[str]] = None
    required_skills: Optional[List[str]] = None
    salary_min: Optional[int] = Field(None, ge=0)  # In cents
    salary_max: Optional[int] = Field(None, ge=0)  # In cents
    salary_type: SalaryType = SalaryType.ANNUAL
    salary_currency: str = Field("USD", min_length=3, max_length=3)
    show_salary: bool = False
    benefits: Optional[List[str]] = None
    perks: Optional[List[str]] = None
    application_deadline: Optional[datetime] = None
    external_apply_url: Optional[str] = None
    application_questions: Optional[List[Dict[str, Any]]] = None

    @validator('salary_max')
    def salary_max_greater_than_min(cls, v, values):
        if v is not None and 'salary_min' in values and values['salary_min'] is not None:
            if v <= values['salary_min']:
                raise ValueError('salary_max must be greater than salary_min')
        return v

    @validator('application_deadline')
    def deadline_in_future(cls, v):
        if v is not None and v <= datetime.utcnow():
            raise ValueError('application_deadline must be in the future')
        return v


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    summary: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = Field(None, min_length=50)
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
    salary_min: Optional[int] = Field(None, ge=0)
    salary_max: Optional[int] = Field(None, ge=0)
    salary_type: Optional[SalaryType] = None
    salary_currency: Optional[str] = Field(None, min_length=3, max_length=3)
    show_salary: Optional[bool] = None
    benefits: Optional[List[str]] = None
    perks: Optional[List[str]] = None
    application_deadline: Optional[datetime] = None
    external_apply_url: Optional[str] = None
    application_questions: Optional[List[Dict[str, Any]]] = None
    status: Optional[JobStatus] = None
    is_featured: Optional[bool] = None
    is_urgent: Optional[bool] = None


class JobResponse(JobBase):
    id: int
    slug: str
    company_id: int
    status: JobStatus
    is_featured: bool
    is_urgent: bool
    view_count: int
    application_count: int
    published_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    # Computed properties
    is_active: bool
    days_since_published: Optional[int] = None
    salary_range_display: Optional[str] = None
    can_apply: bool

    # Company information (populated from relationship)
    company: Optional[PublicCompany] = None

    class Config:
        from_attributes = True


class JobSummary(BaseModel):
    """Lightweight job summary for listings"""
    id: int
    title: str
    slug: str
    summary: Optional[str] = None
    company_id: int
    company_name: str
    company_logo: Optional[str] = None
    location: Optional[str] = None
    job_type: JobType
    experience_level: ExperienceLevel
    remote_type: RemoteType
    salary_range_display: Optional[str] = None
    is_featured: bool
    is_urgent: bool
    published_at: Optional[datetime] = None
    days_since_published: Optional[int] = None

    class Config:
        from_attributes = True


# Job Application Schemas
class JobApplicationBase(BaseModel):
    cover_letter: Optional[str] = Field(None, max_length=5000)
    application_answers: Optional[Dict[str, Any]] = None
    source: Optional[str] = Field(None, max_length=100)


class JobApplicationCreate(JobApplicationBase):
    job_id: int
    resume_id: Optional[int] = None


class JobApplicationUpdate(BaseModel):
    cover_letter: Optional[str] = Field(None, max_length=5000)
    status: Optional[ApplicationStatus] = None
    notes: Optional[str] = None


class JobApplicationResponse(JobApplicationBase):
    id: int
    job_id: int
    candidate_id: int
    resume_id: Optional[int] = None
    status: ApplicationStatus
    status_updated_at: datetime
    applied_at: datetime
    updated_at: datetime

    # Computed properties
    is_active: bool
    days_since_applied: int

    # Related data (populated when needed)
    job: Optional[JobResponse] = None
    candidate: Optional[Dict[str, Any]] = None  # Limited candidate info

    class Config:
        from_attributes = True


# Search and filtering schemas
class JobSearchParams(BaseModel):
    q: Optional[str] = None  # Search query
    location: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    company_id: Optional[int] = None
    job_type: Optional[JobType] = None
    experience_level: Optional[ExperienceLevel] = None
    remote_type: Optional[RemoteType] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    skills: Optional[List[str]] = None
    sort_by: str = Field("published_date", pattern="^(published_date|relevance|salary|company)$")
    sort_order: str = Field("desc", pattern="^(asc|desc)$")
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)
    featured_only: bool = False


class JobSearchResponse(BaseModel):
    jobs: List[JobSummary]
    total: int
    page: int
    limit: int
    total_pages: int
    filters: Dict[str, Any]  # Available filter values


class CompanySearchParams(BaseModel):
    q: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    employee_count: Optional[str] = None
    funding_stage: Optional[str] = None
    sort_by: str = Field("name", pattern="^(name|founded_year|employee_count)$")
    sort_order: str = Field("asc", pattern="^(asc|desc)$")
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)


class CompanySearchResponse(BaseModel):
    companies: List[PublicCompany]
    total: int
    page: int
    limit: int
    total_pages: int


# Public statistics
class PublicStats(BaseModel):
    total_companies: int
    total_jobs: int
    total_applications: int
    featured_companies: List[PublicCompany]
    latest_jobs: List[JobSummary]
    job_categories: Dict[str, int]  # job_type -> count
    location_stats: Dict[str, int]  # location -> count