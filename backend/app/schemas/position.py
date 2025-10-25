from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


# Enums
class PositionStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    PAUSED = "paused"
    CLOSED = "closed"
    ARCHIVED = "archived"


class PositionType(str, Enum):
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
class PositionBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    title: str = Field(..., max_length=255, min_length=1)
    description: str = Field(..., min_length=10)
    summary: str | None = Field(None, max_length=1000)
    department: str | None = Field(None, max_length=100)
    location: str | None = Field(None, max_length=255)
    country: str | None = Field(None, max_length=100)
    city: str | None = Field(None, max_length=100)
    job_type: PositionType = PositionType.FULL_TIME
    experience_level: ExperienceLevel = ExperienceLevel.MID_LEVEL
    remote_type: RemoteType = RemoteType.ON_SITE
    requirements: str | None = None
    preferred_skills: list[str] | None = None  # Will be JSON serialized
    required_skills: list[str] | None = None  # Will be JSON serialized
    benefits: list[str] | None = None  # Will be JSON serialized
    perks: list[str] | None = None  # Will be JSON serialized
    application_deadline: datetime | None = Field(None, alias="deadline")
    external_apply_url: str | None = Field(None, max_length=1000)
    application_questions: list[dict] | None = None  # Will be JSON serialized
    is_featured: bool = False
    is_urgent: bool = False
    seo_title: str | None = Field(None, max_length=255)
    seo_description: str | None = Field(None, max_length=500)
    social_image_url: str | None = Field(None, max_length=1000)

    @field_validator("job_type", mode="before")
    @classmethod
    def normalize_job_type(cls, value):
        if isinstance(value, str):
            normalized = value.replace("-", "_").lower()
            try:
                return PositionType(normalized)
            except ValueError:
                return value
        return value

    @field_validator("experience_level", mode="before")
    @classmethod
    def normalize_experience_level(cls, value):
        if isinstance(value, str):
            normalized = value.replace("-", "_").lower()
            try:
                return ExperienceLevel(normalized)
            except ValueError:
                return value
        return value

    @field_validator("remote_type", mode="before")
    @classmethod
    def normalize_remote_type(cls, value):
        if isinstance(value, str):
            normalized = value.replace("-", "_").lower()
            try:
                return RemoteType(normalized)
            except ValueError:
                return value
        return value


class PositionSalaryInfo(BaseModel):
    salary_min: int | None = Field(None, gt=0)  # In cents
    salary_max: int | None = Field(None, gt=0)  # In cents
    salary_type: SalaryType = SalaryType.ANNUAL
    salary_currency: str = Field("USD", max_length=3)
    show_salary: bool = False

    @field_validator("salary_max")
    @classmethod
    def salary_max_greater_than_min(cls, v, info):
        if info.data.get("salary_min") and v and v <= info.data["salary_min"]:
            raise ValueError("salary_max must be greater than salary_min")
        return v


class PositionCreate(PositionBase, PositionSalaryInfo):
    company_id: int
    posted_by: int | None = None


class PositionUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    title: str | None = Field(None, max_length=255, min_length=1)
    description: str | None = Field(None, min_length=10)
    summary: str | None = Field(None, max_length=1000)
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
    benefits: list[str] | None = None
    perks: list[str] | None = None
    salary_min: int | None = Field(None, gt=0)
    salary_max: int | None = Field(None, gt=0)
    salary_type: SalaryType | None = None
    salary_currency: str | None = Field(None, max_length=3)
    show_salary: bool | None = None
    application_deadline: datetime | None = Field(None, alias="deadline")
    external_apply_url: str | None = Field(None, max_length=1000)
    application_questions: list[dict] | None = None
    status: PositionStatus | None = None
    is_featured: bool | None = None
    is_urgent: bool | None = None
    seo_title: str | None = Field(None, max_length=255)
    seo_description: str | None = Field(None, max_length=500)
    social_image_url: str | None = Field(None, max_length=1000)

    @field_validator("job_type", mode="before")
    @classmethod
    def normalize_job_type_update(cls, value):
        if isinstance(value, str):
            normalized = value.replace("-", "_").lower()
            try:
                return PositionType(normalized)
            except ValueError:
                return value
        return value

    @field_validator("experience_level", mode="before")
    @classmethod
    def normalize_experience_level_update(cls, value):
        if isinstance(value, str):
            normalized = value.replace("-", "_").lower()
            try:
                return ExperienceLevel(normalized)
            except ValueError:
                return value
        return value

    @field_validator("remote_type", mode="before")
    @classmethod
    def normalize_remote_type_update(cls, value):
        if isinstance(value, str):
            normalized = value.replace("-", "_").lower()
            try:
                return RemoteType(normalized)
            except ValueError:
                return value
        return value


class PositionInfo(PositionBase, PositionSalaryInfo):
    title: str = Field(default="", max_length=255)
    description: str | None = None
    id: int
    slug: str | None = None
    company_id: int
    status: PositionStatus = PositionStatus.DRAFT
    view_count: int = 0
    application_count: int = 0
    published_at: datetime | None = None
    expires_at: datetime | None = None
    posted_by: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @field_validator("title", mode="before")
    @classmethod
    def _default_title(cls, value):
        return value or ""

    @field_validator(
        "job_type",
        "experience_level",
        "remote_type",
        "salary_type",
        "status",
        mode="before",
    )
    @classmethod
    def _default_enum_fields(cls, value, info):
        if value is None:
            defaults = {
                "job_type": PositionType.FULL_TIME,
                "experience_level": ExperienceLevel.MID_LEVEL,
                "remote_type": RemoteType.ON_SITE,
                "salary_type": SalaryType.ANNUAL,
                "status": PositionStatus.DRAFT,
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

    @field_validator(
        "preferred_skills", "required_skills", "benefits", "perks", mode="before"
    )
    @classmethod
    def _parse_json_list_fields(cls, value):
        """Parse JSON string fields into lists if needed."""
        if value is None:
            return None
        if isinstance(value, str):
            try:
                import json

                return json.loads(value)
            except (json.JSONDecodeError, ValueError):
                # If it's not valid JSON, return empty list
                return []
        if isinstance(value, list):
            return value
        return []

    @field_validator("experience_level", mode="before")
    @classmethod
    def _normalize_experience_level_final(cls, value):
        """Additional normalization for experience level."""
        if isinstance(value, str):
            # Map common variations to standard values
            mapping = {
                "entry": "entry_level",
                "junior": "entry_level",
                "mid": "mid_level",
                "middle": "mid_level",
                "senior": "senior_level",
                "lead": "senior_level",
                "executive": "executive",
                "intern": "internship",
                "internship": "internship",
            }
            normalized = value.replace("-", "_").lower()
            if normalized in mapping:
                return ExperienceLevel(mapping[normalized])
            try:
                return ExperienceLevel(normalized)
            except ValueError:
                # Default to mid_level if can't parse
                return ExperienceLevel.MID_LEVEL
        return value

    # Computed properties
    is_active: bool = False
    days_since_published: int | None = None
    salary_range_display: str | None = None

    # Company info (from relationship)
    company_name: str | None = None
    company_logo_url: str | None = None

    model_config = ConfigDict(from_attributes=True)


# Job Application Schemas
class PositionApplicationBase(BaseModel):
    cover_letter: str | None = None
    application_answers: list[dict] | None = None  # Will be JSON serialized
    source: str | None = Field(None, max_length=100)


class PositionApplicationCreate(PositionApplicationBase):
    position_id: int
    resume_id: int | None = None


class PositionApplicationUpdate(BaseModel):
    status: ApplicationStatus | None = None
    cover_letter: str | None = None
    notes: str | None = None
    last_contacted_at: datetime | None = None


class PositionApplicationInfo(PositionApplicationBase):
    id: int
    position_id: int
    candidate_id: int
    resume_id: int | None = None
    status: ApplicationStatus = ApplicationStatus.APPLIED
    status_updated_at: datetime
    status_updated_by: int | None = None
    last_contacted_at: datetime | None = None
    notes: str | None = None
    referrer_id: int | None = None
    applied_at: datetime
    updated_at: datetime

    # Computed properties
    is_active: bool = False
    days_since_applied: int = 0

    # Related info
    job_title: str | None = None
    candidate_name: str | None = None
    candidate_email: str | None = None

    model_config = ConfigDict(from_attributes=True)


# Company Profile Schemas
class CompanyProfileBase(BaseModel):
    tagline: str | None = Field(None, max_length=255)
    mission: str | None = None
    values: list[str] | None = None  # Will be JSON serialized
    culture: str | None = None
    logo_url: str | None = Field(None, max_length=1000)
    banner_url: str | None = Field(None, max_length=1000)
    gallery_images: list[str] | None = None  # Will be JSON serialized
    company_video_url: str | None = Field(None, max_length=1000)
    contact_email: str | None = Field(None, max_length=255)
    phone: str | None = Field(None, max_length=50)
    address: str | None = None
    linkedin_url: str | None = Field(None, max_length=500)
    twitter_url: str | None = Field(None, max_length=500)
    facebook_url: str | None = Field(None, max_length=500)
    instagram_url: str | None = Field(None, max_length=500)
    youtube_url: str | None = Field(None, max_length=500)
    founded_year: int | None = Field(None, ge=1800, le=2030)
    employee_count: str | None = Field(None, max_length=50)
    headquarters: str | None = Field(None, max_length=255)
    funding_stage: str | None = Field(None, max_length=100)
    benefits_summary: str | None = None
    perks_highlights: list[str] | None = None  # Will be JSON serialized
    is_public: bool = True
    seo_title: str | None = Field(None, max_length=255)
    seo_description: str | None = Field(None, max_length=500)
    custom_slug: str | None = Field(
        None, max_length=100, pattern=r"^[a-zA-Z0-9-_]+$"
    )


class CompanyProfileCreate(CompanyProfileBase):
    company_id: int


class CompanyProfileUpdate(CompanyProfileBase):
    pass


class CompanyProfileInfo(CompanyProfileBase):
    id: int
    company_id: int
    profile_views: int = 0
    last_updated_by: int | None = None
    created_at: datetime
    updated_at: datetime
    public_slug: str

    # Company info
    company_name: str | None = None

    model_config = ConfigDict(from_attributes=True)


# List and Filter Schemas
class PositionListParams(BaseModel):
    search: str | None = None
    company_id: int | None = None
    job_type: PositionType | None = None
    experience_level: ExperienceLevel | None = None
    remote_type: RemoteType | None = None
    location: str | None = None
    country: str | None = None
    city: str | None = None
    status: PositionStatus | None = None
    is_featured: bool | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    sort_by: str | None = Field(
        "published_at",
        pattern=r"^(published_at|created_at|title|salary_min|view_count)$",
    )
    sort_order: str | None = Field("desc", pattern=r"^(asc|desc)$")
    limit: int = Field(50, ge=1, le=100)
    offset: int = Field(0, ge=0)


class PositionListResponse(BaseModel):
    positions: list[PositionInfo]
    total: int
    skip: int = 0
    limit: int = 0
    has_more: bool = False

    model_config = ConfigDict(from_attributes=True)

    @property
    def jobs(self) -> list[PositionInfo]:
        return self.positions


class PositionStatusUpdateRequest(BaseModel):
    status: PositionStatus


class PositionBulkStatusUpdateRequest(BaseModel):
    position_ids: list[int] = Field(..., min_length=1, alias="position_ids")
    status: PositionStatus


class PositionApplicationListParams(BaseModel):
    position_id: int | None = None
    candidate_id: int | None = None
    status: ApplicationStatus | None = None
    applied_after: datetime | None = None
    applied_before: datetime | None = None
    sort_by: str | None = Field(
        "applied_at", pattern=r"^(applied_at|status_updated_at)$"
    )
    sort_order: str | None = Field("desc", pattern=r"^(asc|desc)$")
    limit: int = Field(50, ge=1, le=100)
    offset: int = Field(0, ge=0)


class PositionApplicationListResponse(BaseModel):
    applications: list[PositionApplicationInfo]
    total: int
    has_more: bool = False


class PositionStatsResponse(BaseModel):
    total_positions: int
    by_status: dict = Field(default_factory=dict)
    by_type: dict = Field(default_factory=dict)
    by_experience_level: dict = Field(default_factory=dict)
    published_this_month: int = 0
    total_applications: int = 0
    average_applications_per_position: float = 0
    most_viewed_positions: list[PositionInfo] = Field(default_factory=list)


class PositionSearchResponse(BaseModel):
    positions: list[PositionInfo]
    total: int
    facets: dict = Field(default_factory=dict)  # For search faceting
    has_more: bool = False
    search_query: str | None = None

    model_config = ConfigDict(from_attributes=True)

    @property
    def jobs(self) -> list[PositionInfo]:
        return self.positions
