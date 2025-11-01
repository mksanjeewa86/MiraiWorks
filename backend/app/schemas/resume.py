from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator

from app.utils.constants import (
    ResumeFormat,
    ResumeLanguage,
    ResumeStatus,
    ResumeVisibility,
    SectionType,
)


def _normalize_enum(enum_cls, value, field_name: str):
    if value is None or isinstance(value, enum_cls):
        return value
    if isinstance(value, str):
        candidate = value.strip()
        if not candidate:
            return None
        try:
            return enum_cls(candidate.upper())
        except ValueError as exc:  # pragma: no cover - validation ensures clarity
            raise ValueError(f"Invalid value {value!r} for {field_name}") from exc
    raise ValueError(f"Invalid type for {field_name}: {type(value).__name__}")


# Base schemas
class ResumeBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None

    # Personal information
    full_name: str | None = Field(None, max_length=100)
    email: str | None = Field(None, max_length=255)
    phone: str | None = Field(None, max_length=20)
    location: str | None = Field(None, max_length=200)
    website: str | None = Field(None, max_length=500)
    linkedin_url: str | None = Field(None, max_length=500)
    github_url: str | None = Field(None, max_length=500)

    # Professional summary
    professional_summary: str | None = None
    objective: str | None = None

    # Template and styling
    template_id: str | None = Field("modern", max_length=50)
    resume_format: ResumeFormat | None = ResumeFormat.INTERNATIONAL
    resume_language: ResumeLanguage | None = ResumeLanguage.ENGLISH
    theme_color: str | None = Field("#2563eb", pattern=r"^#[0-9A-Fa-f]{6}$")
    font_family: str | None = Field("Inter", max_length=50)
    custom_css: str | None = None

    # Japanese-specific fields
    furigana_name: str | None = Field(None, max_length=100)  # phonetic name (furigana)
    birth_date: datetime | None = None  # birth date
    gender: str | None = Field(None, max_length=10)  # gender
    nationality: str | None = Field(None, max_length=50)  # nationality
    marital_status: str | None = Field(None, max_length=20)  # marital status
    emergency_contact: dict | None = None  # emergency contact info
    photo_path: str | None = Field(None, max_length=500)  # optional profile photo
    # Public sharing
    is_public: bool | None = False
    can_download_pdf: bool | None = True

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
    status: ResumeStatus | None = ResumeStatus.DRAFT
    visibility: ResumeVisibility | None = ResumeVisibility.PRIVATE

    @field_validator("status", mode="before")
    @classmethod
    def _validate_status(cls, value):
        return _normalize_enum(ResumeStatus, value, "status")


class ResumeUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    full_name: str | None = Field(None, max_length=100)
    email: str | None = Field(None, max_length=255)
    phone: str | None = Field(None, max_length=20)
    location: str | None = Field(None, max_length=200)
    website: str | None = Field(None, max_length=500)
    linkedin_url: str | None = Field(None, max_length=500)
    github_url: str | None = Field(None, max_length=500)
    professional_summary: str | None = None
    objective: str | None = None
    template_id: str | None = Field(None, max_length=50)
    resume_format: ResumeFormat | None = None
    resume_language: ResumeLanguage | None = None
    theme_color: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    font_family: str | None = Field(None, max_length=50)
    custom_css: str | None = None

    # Japanese-specific fields
    furigana_name: str | None = Field(None, max_length=100)
    birth_date: datetime | None = None
    gender: str | None = Field(None, max_length=10)
    nationality: str | None = Field(None, max_length=50)
    marital_status: str | None = Field(None, max_length=20)
    emergency_contact: dict | None = None
    photo_path: str | None = Field(None, max_length=500)

    # Settings
    status: ResumeStatus | None = None
    visibility: ResumeVisibility | None = None

    @field_validator("status", mode="before")
    @classmethod
    def _validate_update_status(cls, value):
        return _normalize_enum(ResumeStatus, value, "status")

    is_primary: bool | None = None
    is_public: bool | None = None
    can_download_pdf: bool | None = None
    can_edit: bool | None = None
    can_delete: bool | None = None


# Work Experience schemas
class WorkExperienceBase(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=200)
    position_title: str = Field(..., min_length=1, max_length=200)
    location: str | None = Field(None, max_length=200)
    company_website: str | None = Field(None, max_length=500)
    start_date: datetime
    end_date: datetime | None = None
    is_current: bool = False
    description: str | None = None
    achievements: list[str] | None = []
    technologies: list[str] | None = []
    display_order: int | None = 0

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
    company_name: str | None = Field(None, min_length=1, max_length=200)
    position_title: str | None = Field(None, min_length=1, max_length=200)
    location: str | None = Field(None, max_length=200)
    company_website: str | None = Field(None, max_length=500)
    start_date: datetime | None = None
    end_date: datetime | None = None
    is_current: bool | None = None
    description: str | None = None
    achievements: list[str] | None = None
    technologies: list[str] | None = None
    display_order: int | None = None
    is_visible: bool | None = None


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
    field_of_study: str | None = Field(None, max_length=200)
    location: str | None = Field(None, max_length=200)
    start_date: datetime
    end_date: datetime | None = None
    is_current: bool = False
    gpa: str | None = Field(None, max_length=10)
    honors: str | None = Field(None, max_length=200)
    description: str | None = None
    courses: list[str] | None = []
    display_order: int | None = 0

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
    institution_name: str | None = Field(None, min_length=1, max_length=200)
    degree: str | None = Field(None, min_length=1, max_length=200)
    field_of_study: str | None = Field(None, max_length=200)
    location: str | None = Field(None, max_length=200)
    start_date: datetime | None = None
    end_date: datetime | None = None
    is_current: bool | None = None
    gpa: str | None = Field(None, max_length=10)
    honors: str | None = Field(None, max_length=200)
    description: str | None = None
    courses: list[str] | None = None
    display_order: int | None = None
    is_visible: bool | None = None


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
    category: str | None = Field(None, max_length=50)
    proficiency_level: int | None = Field(None, ge=1, le=10)
    proficiency_label: str | None = Field(None, max_length=20)
    display_order: int | None = 0


class SkillCreate(SkillBase):
    pass


class SkillUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    category: str | None = Field(None, max_length=50)
    proficiency_level: int | None = Field(None, ge=1, le=10)
    proficiency_label: str | None = Field(None, max_length=20)
    display_order: int | None = None
    is_visible: bool | None = None


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
    project_url: str | None = Field(None, max_length=500)
    github_url: str | None = Field(None, max_length=500)
    demo_url: str | None = Field(None, max_length=500)
    start_date: datetime | None = None
    end_date: datetime | None = None
    is_ongoing: bool = False
    technologies: list[str] | None = []
    role: str | None = Field(None, max_length=100)
    display_order: int | None = 0

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
    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, min_length=1)
    project_url: str | None = Field(None, max_length=500)
    github_url: str | None = Field(None, max_length=500)
    demo_url: str | None = Field(None, max_length=500)
    start_date: datetime | None = None
    end_date: datetime | None = None
    is_ongoing: bool | None = None
    technologies: list[str] | None = None
    role: str | None = Field(None, max_length=100)
    display_order: int | None = None
    is_visible: bool | None = None


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
    credential_id: str | None = Field(None, max_length=100)
    credential_url: str | None = Field(None, max_length=500)
    issue_date: datetime
    expiration_date: datetime | None = None
    does_not_expire: bool = False
    description: str | None = None
    display_order: int | None = 0

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
    name: str | None = Field(None, min_length=1, max_length=200)
    issuing_organization: str | None = Field(None, min_length=1, max_length=200)
    credential_id: str | None = Field(None, max_length=100)
    credential_url: str | None = Field(None, max_length=500)
    issue_date: datetime | None = None
    expiration_date: datetime | None = None
    does_not_expire: bool | None = None
    description: str | None = None
    display_order: int | None = None
    is_visible: bool | None = None


class CertificationInfo(CertificationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    resume_id: int
    is_visible: bool
    created_at: datetime


# Language schemas
class LanguageBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    proficiency: str = Field(..., min_length=1, max_length=100)
    display_order: int | None = 0


class LanguageCreate(LanguageBase):
    pass


class LanguageUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=50)
    proficiency: str | None = Field(None, min_length=1, max_length=100)
    display_order: int | None = None
    is_visible: bool | None = None


class LanguageInfo(LanguageBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    resume_id: int
    is_visible: bool
    created_at: datetime


# Reference schemas
class ReferenceBase(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=100)
    position_title: str | None = Field(None, max_length=100)
    company_name: str | None = Field(None, max_length=200)
    email: str | None = Field(None, max_length=255)
    phone: str | None = Field(None, max_length=20)
    relationship: str | None = Field(None, max_length=100)
    display_order: int | None = 0

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        if v and "@" not in v:
            raise ValueError("Invalid email format")
        return v


class ReferenceCreate(ReferenceBase):
    pass


class ReferenceUpdate(BaseModel):
    full_name: str | None = Field(None, min_length=1, max_length=100)
    position_title: str | None = Field(None, max_length=100)
    company_name: str | None = Field(None, max_length=200)
    email: str | None = Field(None, max_length=255)
    phone: str | None = Field(None, max_length=20)
    relationship: str | None = Field(None, max_length=100)
    display_order: int | None = None
    is_visible: bool | None = None


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
    content: str | None = None
    is_visible: bool = True
    display_order: int = 0
    custom_css: str | None = None


class SectionCreate(SectionBase):
    pass


class SectionUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=100)
    content: str | None = None
    is_visible: bool | None = None
    display_order: int | None = None
    custom_css: str | None = None


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
    last_viewed_at: datetime | None

    # Enhanced sharing features
    public_url_slug: str | None
    share_token: str
    can_edit: bool
    can_delete: bool

    # Japanese-specific fields
    furigana_name: str | None = None
    birth_date: datetime | None = None
    gender: str | None = None
    nationality: str | None = None
    marital_status: str | None = None
    emergency_contact: dict | None = None
    photo_path: str | None = None

    # File paths
    pdf_file_path: str | None
    pdf_generated_at: datetime | None

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

    @field_serializer("status", when_used="json")
    def _serialize_status(self, status: ResumeStatus) -> str:
        return status.value.lower()

    @field_serializer("resume_format", when_used="json")
    def _serialize_resume_format(self, resume_format: ResumeFormat) -> str:
        return resume_format.value

    @field_serializer("resume_language", when_used="json")
    def _serialize_resume_language(self, resume_language: ResumeLanguage) -> str:
        return resume_language.value


# List response schemas
class ResumeListRequest(BaseModel):
    status: ResumeStatus | None = None
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
    description: str | None
    category: str | None
    color_scheme: dict[str, Any] | None
    font_options: dict[str, Any] | None
    is_premium: bool
    usage_count: int
    preview_image_url: str | None


# Share schemas
class ShareLinkCreate(BaseModel):
    recipient_email: str | None = Field(None, max_length=255)
    password: str | None = Field(None, min_length=4)
    expires_in_days: int | None = Field(None, ge=1, le=365)
    max_views: int | None = Field(None, ge=1)
    allow_download: bool = True
    show_contact_info: bool = True


class ShareLinkInfo(BaseModel):
    share_token: str
    recipient_email: str | None
    password_protected: bool
    expires_at: datetime | None
    max_views: int | None
    view_count: int
    allow_download: bool
    show_contact_info: bool
    last_viewed_at: datetime | None
    created_at: datetime


# Resume statistics
class ResumeStats(BaseModel):
    total_resumes: int
    by_status: dict[str, int]
    by_visibility: dict[str, int]
    total_views: int
    total_downloads: int
    most_viewed_resume: str | None  # Resume title
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
    watermark: str | None = None


class PDFGenerationResponse(BaseModel):
    pdf_url: str
    expires_at: datetime
    file_size: int  # in bytes


# Japanese Resume specific schemas
class RirekishoData(BaseModel):
    """Rirekisho (traditional Japanese resume) specific data structure"""

    personal_info: dict = Field(..., description="Personal information including photo")
    education_history: list[dict] = Field([], description="Educational background")
    work_history: list[dict] = Field([], description="Work experience")
    qualifications: list[dict] = Field([], description="Licenses and certifications")
    motivation: str | None = Field(None, description="Motivation and self-PR")
    commute_time: str | None = Field(None, description="Commute time")
    spouse: str | None = Field(None, description="Spouse information")
    dependents: str | None = Field(None, description="Number of dependents")


class ShokumuKeirekishoData(BaseModel):
    """Shokumu Keirekisho (career history) specific data structure"""

    career_summary: str = Field(..., description="Career summary")
    detailed_experience: list[dict] = Field(..., description="Detailed work experience")
    skills_and_expertise: dict = Field(
        ..., description="Technical skills and expertise"
    )
    achievements: list[str] = Field([], description="Key achievements")
    self_pr: str = Field(..., description="Self-promotion section")


# Public Resume schemas
class PublicResumeInfo(BaseModel):
    """Public resume view (limited information)"""

    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    full_name: str | None
    professional_summary: str | None
    resume_format: ResumeFormat
    resume_language: ResumeLanguage
    view_count: int
    last_viewed_at: datetime | None
    can_download_pdf: bool
    theme_color: str | None
    font_family: str | None

    # Limited related data
    experiences: list[WorkExperienceInfo] = []
    educations: list[EducationInfo] = []
    skills: list[SkillInfo] = []

    @field_serializer("resume_format", when_used="json")
    def _serialize_public_format(self, resume_format: ResumeFormat) -> str:
        return resume_format.value

    @field_serializer("resume_language", when_used="json")
    def _serialize_public_language(self, resume_language: ResumeLanguage) -> str:
        return resume_language.value


class EmailResumeRequest(BaseModel):
    """Request to send resume via email"""

    recipient_emails: list[str] = Field(..., min_length=1, max_length=10)
    subject: str | None = Field(None, max_length=200)
    message: str | None = Field(None, max_length=2000)
    include_pdf: bool = True
    sender_name: str | None = Field(None, max_length=100)

    @field_validator("recipient_emails")
    @classmethod
    def validate_emails(cls, v):
        for email in v:
            if "@" not in email:
                raise ValueError(f"Invalid email format: {email}")
        return v


class MessageAttachmentRequest(BaseModel):
    """Request to attach resume to message"""

    message_id: int
    include_pdf: bool = True
    auto_attach: bool = False


class ResumePublicSettings(BaseModel):
    """Settings for public resume sharing"""

    is_public: bool
    custom_slug: str | None = Field(None, max_length=100)
    show_contact_info: bool = True
    allow_pdf_download: bool = True
    password_protect: bool = False
    password: str | None = Field(None, min_length=4)


# Resume format templates
class JapaneseResumeTemplate(BaseModel):
    """Template configuration for Japanese resume formats"""

    format_type: ResumeFormat
    sections: list[str] = Field(..., description="Required sections for this format")
    field_mappings: dict = Field(..., description="Field mappings for template")
    validation_rules: dict = Field({}, description="Format-specific validation rules")
