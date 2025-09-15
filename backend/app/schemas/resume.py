from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.utils.constants import ResumeStatus, ResumeVisibility, SectionType


# Base schemas
class ResumeBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None

    # Personal information
    full_name: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    location: Optional[str] = Field(None, max_length=200)
    website: Optional[str] = Field(None, max_length=500)
    linkedin_url: Optional[str] = Field(None, max_length=500)
    github_url: Optional[str] = Field(None, max_length=500)

    # Professional summary
    professional_summary: Optional[str] = None
    objective: Optional[str] = None

    # Template and styling
    template_id: Optional[str] = Field("modern", max_length=50)
    theme_color: Optional[str] = Field("#2563eb", pattern=r"^#[0-9A-Fa-f]{6}$")
    font_family: Optional[str] = Field("Inter", max_length=50)
    custom_css: Optional[str] = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        if v and "@" not in v:
            raise ValueError("Invalid email format")
        return v

    @field_validator("website", "linkedin_url", "github_url")
    @classmethod
    def validate_urls(cls, v):
        if v and not (v.startswith("http://") or v.startswith("https://")):
            return f"https://{v}"
        return v


class ResumeCreate(ResumeBase):
    visibility: Optional[ResumeVisibility] = ResumeVisibility.PRIVATE


class ResumeUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    full_name: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    location: Optional[str] = Field(None, max_length=200)
    website: Optional[str] = Field(None, max_length=500)
    linkedin_url: Optional[str] = Field(None, max_length=500)
    github_url: Optional[str] = Field(None, max_length=500)
    professional_summary: Optional[str] = None
    objective: Optional[str] = None
    template_id: Optional[str] = Field(None, max_length=50)
    theme_color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    font_family: Optional[str] = Field(None, max_length=50)
    custom_css: Optional[str] = None
    status: Optional[ResumeStatus] = None
    visibility: Optional[ResumeVisibility] = None
    is_primary: Optional[bool] = None


# Work Experience schemas
class WorkExperienceBase(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=200)
    position_title: str = Field(..., min_length=1, max_length=200)
    location: Optional[str] = Field(None, max_length=200)
    company_website: Optional[str] = Field(None, max_length=500)
    start_date: datetime
    end_date: Optional[datetime] = None
    is_current: bool = False
    description: Optional[str] = None
    achievements: Optional[list[str]] = []
    technologies: Optional[list[str]] = []
    display_order: Optional[int] = 0

    @field_validator("end_date")
    @classmethod
    def validate_end_date(cls, v, info):
        start_date = info.data.get("start_date")
        if v and start_date and v <= start_date:
            raise ValueError("End date must be after start date")
        return v

    @field_validator("is_current")
    @classmethod
    def validate_current_job(cls, v, info):
        if v and info.data.get("end_date"):
            raise ValueError("Current job cannot have end date")
        return v


class WorkExperienceCreate(WorkExperienceBase):
    pass


class WorkExperienceUpdate(BaseModel):
    company_name: Optional[str] = Field(None, min_length=1, max_length=200)
    position_title: Optional[str] = Field(None, min_length=1, max_length=200)
    location: Optional[str] = Field(None, max_length=200)
    company_website: Optional[str] = Field(None, max_length=500)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_current: Optional[bool] = None
    description: Optional[str] = None
    achievements: Optional[list[str]] = None
    technologies: Optional[list[str]] = None
    display_order: Optional[int] = None
    is_visible: Optional[bool] = None


class WorkExperienceInfo(WorkExperienceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    resume_id: int
    is_visible: bool
    created_at: datetime
    updated_at: datetime


# Education schemas
class EducationBase(BaseModel):
    institution_name: str = Field(..., min_length=1, max_length=200)
    degree: str = Field(..., min_length=1, max_length=200)
    field_of_study: Optional[str] = Field(None, max_length=200)
    location: Optional[str] = Field(None, max_length=200)
    start_date: datetime
    end_date: Optional[datetime] = None
    is_current: bool = False
    gpa: Optional[str] = Field(None, max_length=10)
    honors: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    courses: Optional[list[str]] = []
    display_order: Optional[int] = 0

    @field_validator("end_date")
    @classmethod
    def validate_end_date(cls, v, info):
        start_date = info.data.get("start_date")
        if v and start_date and v <= start_date:
            raise ValueError("End date must be after start date")
        return v


class EducationCreate(EducationBase):
    pass


class EducationUpdate(BaseModel):
    institution_name: Optional[str] = Field(None, min_length=1, max_length=200)
    degree: Optional[str] = Field(None, min_length=1, max_length=200)
    field_of_study: Optional[str] = Field(None, max_length=200)
    location: Optional[str] = Field(None, max_length=200)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_current: Optional[bool] = None
    gpa: Optional[str] = Field(None, max_length=10)
    honors: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    courses: Optional[list[str]] = None
    display_order: Optional[int] = None
    is_visible: Optional[bool] = None


class EducationInfo(EducationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    resume_id: int
    is_visible: bool
    created_at: datetime
    updated_at: datetime


# Skill schemas
class SkillBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category: Optional[str] = Field(None, max_length=50)
    proficiency_level: Optional[int] = Field(None, ge=1, le=10)
    proficiency_label: Optional[str] = Field(None, max_length=20)
    display_order: Optional[int] = 0


class SkillCreate(SkillBase):
    pass


class SkillUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    category: Optional[str] = Field(None, max_length=50)
    proficiency_level: Optional[int] = Field(None, ge=1, le=10)
    proficiency_label: Optional[str] = Field(None, max_length=20)
    display_order: Optional[int] = None
    is_visible: Optional[bool] = None


class SkillInfo(SkillBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    resume_id: int
    is_visible: bool
    created_at: datetime


# Project schemas
class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    project_url: Optional[str] = Field(None, max_length=500)
    github_url: Optional[str] = Field(None, max_length=500)
    demo_url: Optional[str] = Field(None, max_length=500)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_ongoing: bool = False
    technologies: Optional[list[str]] = []
    role: Optional[str] = Field(None, max_length=100)
    display_order: Optional[int] = 0

    @field_validator("end_date")
    @classmethod
    def validate_end_date(cls, v, info):
        start_date = info.data.get("start_date")
        if v and start_date and v <= start_date:
            raise ValueError("End date must be after start date")
        return v


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    project_url: Optional[str] = Field(None, max_length=500)
    github_url: Optional[str] = Field(None, max_length=500)
    demo_url: Optional[str] = Field(None, max_length=500)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_ongoing: Optional[bool] = None
    technologies: Optional[list[str]] = None
    role: Optional[str] = Field(None, max_length=100)
    display_order: Optional[int] = None
    is_visible: Optional[bool] = None


class ProjectInfo(ProjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    resume_id: int
    is_visible: bool
    created_at: datetime
    updated_at: datetime


# Certification schemas
class CertificationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    issuing_organization: str = Field(..., min_length=1, max_length=200)
    credential_id: Optional[str] = Field(None, max_length=100)
    credential_url: Optional[str] = Field(None, max_length=500)
    issue_date: datetime
    expiration_date: Optional[datetime] = None
    does_not_expire: bool = False
    description: Optional[str] = None
    display_order: Optional[int] = 0

    @field_validator("expiration_date")
    @classmethod
    def validate_expiration_date(cls, v, info):
        issue_date = info.data.get("issue_date")
        if v and issue_date and v <= issue_date:
            raise ValueError("Expiration date must be after issue date")
        return v


class CertificationCreate(CertificationBase):
    pass


class CertificationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    issuing_organization: Optional[str] = Field(None, min_length=1, max_length=200)
    credential_id: Optional[str] = Field(None, max_length=100)
    credential_url: Optional[str] = Field(None, max_length=500)
    issue_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    does_not_expire: Optional[bool] = None
    description: Optional[str] = None
    display_order: Optional[int] = None
    is_visible: Optional[bool] = None


class CertificationInfo(CertificationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    resume_id: int
    is_visible: bool
    created_at: datetime


# Language schemas
class LanguageBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    proficiency: str = Field(..., min_length=1, max_length=20)
    display_order: Optional[int] = 0


class LanguageCreate(LanguageBase):
    pass


class LanguageUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    proficiency: Optional[str] = Field(None, min_length=1, max_length=20)
    display_order: Optional[int] = None
    is_visible: Optional[bool] = None


class LanguageInfo(LanguageBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    resume_id: int
    is_visible: bool
    created_at: datetime


# Reference schemas
class ReferenceBase(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=100)
    position_title: Optional[str] = Field(None, max_length=100)
    company_name: Optional[str] = Field(None, max_length=200)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    relationship: Optional[str] = Field(None, max_length=100)
    display_order: Optional[int] = 0

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        if v and "@" not in v:
            raise ValueError("Invalid email format")
        return v


class ReferenceCreate(ReferenceBase):
    pass


class ReferenceUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    position_title: Optional[str] = Field(None, max_length=100)
    company_name: Optional[str] = Field(None, max_length=200)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    relationship: Optional[str] = Field(None, max_length=100)
    display_order: Optional[int] = None
    is_visible: Optional[bool] = None


class ReferenceInfo(ReferenceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    resume_id: int
    is_visible: bool
    created_at: datetime
    updated_at: datetime


# Section schemas
class SectionBase(BaseModel):
    section_type: SectionType
    title: str = Field(..., min_length=1, max_length=100)
    content: Optional[str] = None
    is_visible: bool = True
    display_order: int = 0
    custom_css: Optional[str] = None


class SectionCreate(SectionBase):
    pass


class SectionUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    content: Optional[str] = None
    is_visible: Optional[bool] = None
    display_order: Optional[int] = None
    custom_css: Optional[str] = None


class SectionInfo(SectionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    resume_id: int
    created_at: datetime
    updated_at: datetime


# Main resume response schema
class ResumeInfo(ResumeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    status: ResumeStatus
    visibility: ResumeVisibility
    is_primary: bool
    view_count: int
    download_count: int
    last_viewed_at: Optional[datetime]
    slug: str
    share_token: str
    created_at: datetime
    updated_at: datetime

    # Related data
    sections: list[SectionInfo] = []
    experiences: list[WorkExperienceInfo] = []
    educations: list[EducationInfo] = []
    skills: list[SkillInfo] = []
    projects: list[ProjectInfo] = []
    certifications: list[CertificationInfo] = []
    languages: list[LanguageInfo] = []
    references: list[ReferenceInfo] = []


# List response schemas
class ResumeListRequest(BaseModel):
    status: Optional[ResumeStatus] = None
    limit: int = Field(10, ge=1, le=100)
    offset: int = Field(0, ge=0)


class ResumeListResponse(BaseModel):
    resumes: list[ResumeInfo]
    total: int
    has_more: bool


# Template schemas
class ResumeTemplateInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    display_name: str
    description: Optional[str]
    category: Optional[str]
    color_scheme: Optional[dict[str, Any]]
    font_options: Optional[dict[str, Any]]
    is_premium: bool
    usage_count: int
    preview_image_url: Optional[str]


# Share schemas
class ShareLinkCreate(BaseModel):
    recipient_email: Optional[str] = Field(None, max_length=255)
    password: Optional[str] = Field(None, min_length=4)
    expires_in_days: Optional[int] = Field(None, ge=1, le=365)
    max_views: Optional[int] = Field(None, ge=1)
    allow_download: bool = True
    show_contact_info: bool = True


class ShareLinkInfo(BaseModel):
    share_token: str
    recipient_email: Optional[str]
    password_protected: bool
    expires_at: Optional[datetime]
    max_views: Optional[int]
    view_count: int
    allow_download: bool
    show_contact_info: bool
    last_viewed_at: Optional[datetime]
    created_at: datetime


# Resume statistics
class ResumeStats(BaseModel):
    total_resumes: int
    by_status: dict[str, int]
    by_visibility: dict[str, int]
    total_views: int
    total_downloads: int
    most_viewed_resume: Optional[str]  # Resume title
    recent_activity: int  # Views/downloads in last 30 days


# Bulk operations
class BulkResumeAction(BaseModel):
    action: str = Field(
        ..., pattern="^(delete|archive|publish|make_private|make_public)$"
    )
    resume_ids: list[int] = Field(..., min_length=1)


class BulkActionResult(BaseModel):
    success_count: int
    error_count: int
    errors: list[str] = []


# PDF generation
class PDFGenerationRequest(BaseModel):
    resume_id: int
    format: str = Field("A4", pattern="^(A4|Letter)$")
    include_contact_info: bool = True
    watermark: Optional[str] = None


class PDFGenerationResponse(BaseModel):
    pdf_url: str
    expires_at: datetime
    file_size: int  # in bytes
