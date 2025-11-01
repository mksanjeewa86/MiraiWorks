from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.utils.constants import (
    ResumeFormat,
    ResumeLanguage,
    ResumeStatus,
    ResumeVisibility,
    SectionType,
)
from app.utils.datetime_utils import get_utc_now


class Resume(BaseModel):
    __tablename__ = "resumes"

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )

    # Basic info
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    # Personal information
    full_name: Mapped[str | None] = mapped_column(String(100))
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(20))
    location: Mapped[str | None] = mapped_column(String(200))
    website: Mapped[str | None] = mapped_column(String(500))
    linkedin_url: Mapped[str | None] = mapped_column(String(500))
    github_url: Mapped[str | None] = mapped_column(String(500))

    # Professional summary
    professional_summary: Mapped[str | None] = mapped_column(Text)
    objective: Mapped[str | None] = mapped_column(Text)

    # Status and visibility
    status: Mapped[ResumeStatus] = mapped_column(
        SQLEnum(ResumeStatus, values_callable=lambda x: [e.value for e in x]),
        default=ResumeStatus.DRAFT.value,
    )
    visibility: Mapped[ResumeVisibility] = mapped_column(
        SQLEnum(ResumeVisibility, values_callable=lambda x: [e.value for e in x]),
        default=ResumeVisibility.PRIVATE.value,
    )

    # Template and styling
    template_id: Mapped[str | None] = mapped_column(String(50), default="modern")
    resume_format: Mapped[ResumeFormat] = mapped_column(
        SQLEnum(ResumeFormat, values_callable=lambda x: [e.value for e in x]),
        default=ResumeFormat.INTERNATIONAL.value,
    )
    resume_language: Mapped[ResumeLanguage] = mapped_column(
        SQLEnum(ResumeLanguage, values_callable=lambda x: [e.value for e in x]),
        default=ResumeLanguage.ENGLISH.value,
    )
    theme_color: Mapped[str | None] = mapped_column(String(7), default="#2563eb")
    font_family: Mapped[str | None] = mapped_column(String(50), default="Inter")
    custom_css: Mapped[str | None] = mapped_column(Text)

    # Japanese-specific fields
    furigana_name: Mapped[str | None] = mapped_column(
        String(100)
    )  # phonetic name (furigana)
    birth_date: Mapped[datetime | None] = mapped_column(DateTime)
    gender: Mapped[str | None] = mapped_column(String(10))
    nationality: Mapped[str | None] = mapped_column(String(50))
    marital_status: Mapped[str | None] = mapped_column(String(20))
    emergency_contact: Mapped[dict | None] = mapped_column(JSON)
    photo_path: Mapped[str | None] = mapped_column(String(500))

    # Metadata
    is_primary: Mapped[bool | None] = mapped_column(Boolean, default=False)
    view_count: Mapped[int | None] = mapped_column(Integer, default=0)
    download_count: Mapped[int | None] = mapped_column(Integer, default=0)
    last_viewed_at: Mapped[datetime | None] = mapped_column(DateTime)

    # File attachments
    pdf_file_path: Mapped[str | None] = mapped_column(String(500))
    pdf_generated_at: Mapped[datetime | None] = mapped_column(DateTime)
    original_file_path: Mapped[str | None] = mapped_column(String(500))

    # Sharing and public access
    is_public: Mapped[bool | None] = mapped_column(Boolean, default=False)
    public_url_slug: Mapped[str | None] = mapped_column(
        String(100), unique=True, index=True
    )
    share_token: Mapped[str | None] = mapped_column(String(64), unique=True, index=True)
    can_download_pdf: Mapped[bool | None] = mapped_column(Boolean, default=True)
    can_edit: Mapped[bool | None] = mapped_column(Boolean, default=True)
    can_delete: Mapped[bool | None] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=get_utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=get_utc_now, onupdate=get_utc_now, nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="resumes")
    sections = relationship(
        "ResumeSection", back_populates="resume", cascade="all, delete-orphan"
    )
    experiences = relationship(
        "WorkExperience", back_populates="resume", cascade="all, delete-orphan"
    )
    educations = relationship(
        "Education", back_populates="resume", cascade="all, delete-orphan"
    )
    skills = relationship(
        "Skill", back_populates="resume", cascade="all, delete-orphan"
    )
    projects = relationship(
        "Project", back_populates="resume", cascade="all, delete-orphan"
    )
    certifications = relationship(
        "Certification", back_populates="resume", cascade="all, delete-orphan"
    )
    languages = relationship(
        "Language", back_populates="resume", cascade="all, delete-orphan"
    )
    references = relationship(
        "Reference", back_populates="resume", cascade="all, delete-orphan"
    )

    @classmethod
    async def get_by_user_id(cls, db, user_id: int, limit: int = 10, offset: int = 0):
        """Get resumes by user ID."""
        from sqlalchemy import select

        result = await db.execute(
            select(cls)
            .where(cls.user_id == user_id)
            .order_by(cls.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()

    @classmethod
    async def get_by_public_slug(cls, db, slug: str):
        """Get public resume by slug."""
        from sqlalchemy import select

        result = await db.execute(
            select(cls).where(cls.public_url_slug == slug, cls.is_public.is_(True))
        )
        return result.scalars().first()

    @classmethod
    async def get_by_share_token(cls, db, token: str):
        """Get resume by share token."""
        from sqlalchemy import select

        result = await db.execute(select(cls).where(cls.share_token == token))
        return result.scalars().first()

    def increment_view_count(self):
        """Increment view count."""
        self.view_count = (self.view_count or 0) + 1
        self.last_viewed_at = get_utc_now()

    def increment_download_count(self):
        """Increment download count."""
        self.download_count = (self.download_count or 0) + 1

    def can_be_edited(self) -> bool:
        """Check if resume can be edited."""
        return bool(self.can_edit and self.status != ResumeStatus.ARCHIVED)

    def can_be_deleted(self) -> bool:
        """Check if resume can be deleted."""
        return bool(self.can_delete and self.status != ResumeStatus.ARCHIVED)


class ResumeSection(BaseModel):
    __tablename__ = "resume_sections"

    resume_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("resumes.id"), nullable=False
    )

    # Section info
    section_type: Mapped[SectionType] = mapped_column(
        SQLEnum(SectionType), nullable=False
    )
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str | None] = mapped_column(Text)

    # Display options
    is_visible: Mapped[bool | None] = mapped_column(Boolean, default=True)
    display_order: Mapped[int | None] = mapped_column(Integer, default=0)

    # Custom styling
    custom_css: Mapped[str | None] = mapped_column(Text)

    # Relationships
    resume = relationship("Resume", back_populates="sections")


class WorkExperience(BaseModel):
    __tablename__ = "work_experiences"

    resume_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("resumes.id"), nullable=False
    )

    # Job details
    company_name: Mapped[str] = mapped_column(String(200), nullable=False)
    position_title: Mapped[str] = mapped_column(String(200), nullable=False)
    location: Mapped[str | None] = mapped_column(String(200))
    company_website: Mapped[str | None] = mapped_column(String(500))

    # Employment period
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_date: Mapped[datetime | None] = mapped_column(DateTime)
    is_current: Mapped[bool | None] = mapped_column(Boolean, default=False)

    # Job description
    description: Mapped[str | None] = mapped_column(Text)
    achievements: Mapped[dict | None] = mapped_column(JSON)
    technologies: Mapped[dict | None] = mapped_column(JSON)

    # Display options
    is_visible: Mapped[bool | None] = mapped_column(Boolean, default=True)
    display_order: Mapped[int | None] = mapped_column(Integer, default=0)

    # Relationships
    resume = relationship("Resume", back_populates="experiences")


class Education(BaseModel):
    __tablename__ = "educations"

    resume_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("resumes.id"), nullable=False
    )

    # Education details
    institution_name: Mapped[str] = mapped_column(String(200), nullable=False)
    degree: Mapped[str] = mapped_column(String(200), nullable=False)
    field_of_study: Mapped[str | None] = mapped_column(String(200))
    location: Mapped[str | None] = mapped_column(String(200))

    # Academic period
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_date: Mapped[datetime | None] = mapped_column(DateTime)
    is_current: Mapped[bool | None] = mapped_column(Boolean, default=False)

    # Academic performance
    gpa: Mapped[str | None] = mapped_column(String(10))
    honors: Mapped[str | None] = mapped_column(String(200))

    # Additional info
    description: Mapped[str | None] = mapped_column(Text)
    courses: Mapped[dict | None] = mapped_column(JSON)

    # Display options
    is_visible: Mapped[bool | None] = mapped_column(Boolean, default=True)
    display_order: Mapped[int | None] = mapped_column(Integer, default=0)

    # Relationships
    resume = relationship("Resume", back_populates="educations")


class Skill(BaseModel):
    __tablename__ = "skills"

    resume_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("resumes.id"), nullable=False
    )

    # Skill details
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str | None] = mapped_column(String(50))
    proficiency_level: Mapped[int | None] = mapped_column(Integer)
    proficiency_label: Mapped[str | None] = mapped_column(String(20))

    # Display options
    is_visible: Mapped[bool | None] = mapped_column(Boolean, default=True)
    display_order: Mapped[int | None] = mapped_column(Integer, default=0)

    # Relationships
    resume = relationship("Resume", back_populates="skills")


class Project(BaseModel):
    __tablename__ = "projects"

    resume_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("resumes.id"), nullable=False
    )

    # Project details
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Project links
    project_url: Mapped[str | None] = mapped_column(String(500))
    github_url: Mapped[str | None] = mapped_column(String(500))
    demo_url: Mapped[str | None] = mapped_column(String(500))

    # Project period
    start_date: Mapped[datetime | None] = mapped_column(DateTime)
    end_date: Mapped[datetime | None] = mapped_column(DateTime)
    is_ongoing: Mapped[bool | None] = mapped_column(Boolean, default=False)

    # Technical details
    technologies: Mapped[dict | None] = mapped_column(JSON)
    role: Mapped[str | None] = mapped_column(String(100))

    # Display options
    is_visible: Mapped[bool | None] = mapped_column(Boolean, default=True)
    display_order: Mapped[int | None] = mapped_column(Integer, default=0)

    # Relationships
    resume = relationship("Resume", back_populates="projects")


class Certification(BaseModel):
    __tablename__ = "certifications"

    resume_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("resumes.id"), nullable=False
    )

    # Certification details
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    issuing_organization: Mapped[str] = mapped_column(String(200), nullable=False)
    credential_id: Mapped[str | None] = mapped_column(String(100))
    credential_url: Mapped[str | None] = mapped_column(String(500))

    # Dates
    issue_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    expiration_date: Mapped[datetime | None] = mapped_column(DateTime)
    does_not_expire: Mapped[bool | None] = mapped_column(Boolean, default=False)

    # Additional info
    description: Mapped[str | None] = mapped_column(Text)

    # Display options
    is_visible: Mapped[bool | None] = mapped_column(Boolean, default=True)
    display_order: Mapped[int | None] = mapped_column(Integer, default=0)

    # Relationships
    resume = relationship("Resume", back_populates="certifications")


class Language(BaseModel):
    __tablename__ = "languages"

    resume_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("resumes.id"), nullable=False
    )

    # Language details
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    proficiency: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # e.g., "Native", "Fluent", "Conversational", "Professional Working Proficiency (TOEIC 800)"

    # Display options
    is_visible: Mapped[bool | None] = mapped_column(Boolean, default=True)
    display_order: Mapped[int | None] = mapped_column(Integer, default=0)

    # Relationships
    resume = relationship("Resume", back_populates="languages")


class Reference(BaseModel):
    __tablename__ = "references"

    resume_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("resumes.id"), nullable=False
    )

    # Reference details
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    position_title: Mapped[str | None] = mapped_column(String(100))
    company_name: Mapped[str | None] = mapped_column(String(200))
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(20))
    reference_relationship: Mapped[str | None] = mapped_column(String(100))

    # Display options
    is_visible: Mapped[bool | None] = mapped_column(Boolean, default=True)
    display_order: Mapped[int | None] = mapped_column(Integer, default=0)

    # Relationships
    resume = relationship("Resume", back_populates="references")


class ResumeTemplate(BaseModel):
    __tablename__ = "resume_templates"

    # Template details
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    # Template structure
    template_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    css_styles: Mapped[str] = mapped_column(Text, nullable=False)
    html_template: Mapped[str] = mapped_column(Text, nullable=False)

    # Template metadata
    category: Mapped[str | None] = mapped_column(String(50))
    color_scheme: Mapped[dict | None] = mapped_column(JSON)
    font_options: Mapped[dict | None] = mapped_column(JSON)

    # Usage and status
    is_active: Mapped[bool | None] = mapped_column(Boolean, default=True)
    is_premium: Mapped[bool | None] = mapped_column(Boolean, default=False)
    usage_count: Mapped[int | None] = mapped_column(Integer, default=0)

    # Preview
    preview_image_url: Mapped[str | None] = mapped_column(String(500))

    @classmethod
    async def get_active_templates(cls, db, include_premium: bool = False):
        """Get all active templates."""
        from sqlalchemy import select

        query = select(cls).where(cls.is_active.is_(True))
        if not include_premium:
            query = query.where(cls.is_premium.is_(False))
        result = await db.execute(query.order_by(cls.usage_count.desc()))
        return result.scalars().all()


class ResumeShare(BaseModel):
    __tablename__ = "resume_shares"

    resume_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("resumes.id"), nullable=False
    )

    # Share details
    share_token: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True, index=True
    )
    recipient_email: Mapped[str | None] = mapped_column(String(255))
    recipient_name: Mapped[str | None] = mapped_column(String(100))

    # Access control
    password_protected: Mapped[bool | None] = mapped_column(Boolean, default=False)
    password_hash: Mapped[str | None] = mapped_column(String(255))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime)
    max_views: Mapped[int | None] = mapped_column(Integer)
    view_count: Mapped[int | None] = mapped_column(Integer, default=0)

    # Share options
    allow_download: Mapped[bool | None] = mapped_column(Boolean, default=True)
    show_contact_info: Mapped[bool | None] = mapped_column(Boolean, default=True)

    # Tracking
    last_viewed_at: Mapped[datetime | None] = mapped_column(DateTime)

    # Relationships
    resume = relationship("Resume")

    @classmethod
    async def get_by_token(cls, db, token: str):
        """Get share by token."""
        from sqlalchemy import select

        result = await db.execute(select(cls).where(cls.share_token == token))
        return result.scalars().first()

    def is_expired(self) -> bool:
        """Check if share is expired."""
        return bool(
            (self.expires_at and self.expires_at < get_utc_now())
            or (
                self.max_views
                and self.view_count is not None
                and self.view_count >= self.max_views
            )
        )


class ResumeMessageAttachment(BaseModel):
    __tablename__ = "resume_message_attachments"

    resume_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("resumes.id"), nullable=False
    )
    message_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("messages.id"), nullable=False
    )

    # Attachment settings
    auto_attached: Mapped[bool | None] = mapped_column(
        Boolean, default=False
    )  # Automatically attached when contacting
    attachment_format: Mapped[str | None] = mapped_column(String(20), default="pdf")

    # Relationships
    resume = relationship("Resume")
    # message relationship will be added to Message model
