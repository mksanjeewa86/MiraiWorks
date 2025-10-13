from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.utils.datetime_utils import get_utc_now
from app.utils.db_types import LONGTEXT


class Position(BaseModel):
    __tablename__ = "positions"

    # Basic job information
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )
    description: Mapped[str] = mapped_column(LONGTEXT, nullable=False)
    summary: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # Short description for listings

    # Company and location
    company_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)

    # Position details
    job_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="full_time", index=True
    )
    experience_level: Mapped[str] = mapped_column(
        String(50), nullable=False, default="mid_level", index=True
    )
    remote_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="on_site", index=True
    )

    # Requirements and skills
    requirements: Mapped[str | None] = mapped_column(LONGTEXT, nullable=True)
    preferred_skills: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # JSON array
    required_skills: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # JSON array

    # Compensation
    salary_min: Mapped[int | None] = mapped_column(Integer, nullable=True)  # In cents
    salary_max: Mapped[int | None] = mapped_column(Integer, nullable=True)  # In cents
    salary_type: Mapped[str | None] = mapped_column(
        String(20), nullable=True, default="annual"
    )
    salary_currency: Mapped[str] = mapped_column(
        String(3), nullable=False, default="USD"
    )
    show_salary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Benefits and perks
    benefits: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array
    perks: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array

    # Application settings
    application_deadline: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, index=True
    )
    external_apply_url: Mapped[str | None] = mapped_column(
        String(1000), nullable=True
    )  # If using external ATS
    application_questions: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # JSON array

    # Status and visibility
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="draft", index=True
    )
    is_featured: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, index=True
    )
    is_urgent: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # SEO and social
    seo_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    seo_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    social_image_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # Analytics
    view_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    application_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Publishing dates
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, index=True
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, index=True
    )

    # Metadata
    posted_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )

    # Relationships
    company = relationship("Company", back_populates="positions")
    posted_by_user = relationship("User", foreign_keys=[posted_by])
    applications = relationship(
        "PositionApplication", back_populates="position", cascade="all, delete-orphan"
    )
    workflows = relationship(
        "Workflow", back_populates="position", cascade="all, delete-orphan"
    )

    # Indexes for performance
    __table_args__ = (
        Index("idx_positions_company_status", "company_id", "status"),
        Index("idx_positions_published", "published_at", "status"),
        Index("idx_positions_location_type", "country", "city", "job_type"),
        Index("idx_positions_experience_remote", "experience_level", "remote_type"),
        Index("idx_positions_featured_status", "is_featured", "status", "published_at"),
    )

    @property
    def is_active(self) -> bool:
        """Check if job is currently active and accepting applications"""
        now = get_utc_now()
        return (
            self.status == "published"
            and (self.application_deadline is None or self.application_deadline > now)
            and (self.expires_at is None or self.expires_at > now)
        )

    @property
    def days_since_published(self) -> int | None:
        """Get number of days since job was published"""
        if not self.published_at:
            return None
        return (get_utc_now() - self.published_at).days

    @property
    def salary_range_display(self) -> str | None:
        """Format salary range for display"""
        if not self.show_salary or not (self.salary_min or self.salary_max):
            return None

        def format_salary(amount_cents: int) -> str:
            amount = amount_cents / 100
            if amount >= 1000000:
                return f"{amount/1000000:.1f}M"
            elif amount >= 1000:
                return f"{amount/1000:.0f}K"
            else:
                return f"{amount:.0f}"

        if self.salary_min and self.salary_max:
            return f"{self.salary_currency} {format_salary(self.salary_min)}-{format_salary(self.salary_max)}"
        elif self.salary_min:
            return f"{self.salary_currency} {format_salary(self.salary_min)}+"
        elif self.salary_max:
            return f"{self.salary_currency} Up to {format_salary(self.salary_max)}"

        return None

    def increment_view_count(self):
        """Increment job view count"""
        self.view_count += 1

    def can_apply(self) -> bool:
        """Check if applications are currently accepted"""
        return self.is_active and not self.external_apply_url


class PositionApplication(BaseModel):
    __tablename__ = "position_applications"

    # References
    position_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("positions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    candidate_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    resume_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("resumes.id", ondelete="SET NULL"), nullable=True
    )

    # Application data
    cover_letter: Mapped[str | None] = mapped_column(LONGTEXT, nullable=True)
    application_answers: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # JSON responses to custom questions

    # Status tracking
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="applied", index=True
    )
    status_updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=get_utc_now
    )
    status_updated_by: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )

    # Communication
    last_contacted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    notes: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # Internal recruiter notes

    # Source tracking
    source: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )  # Where they found the job
    referrer_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )

    # Metadata
    applied_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=get_utc_now, index=True
    )

    # Relationships
    position = relationship("Position", back_populates="applications")
    candidate = relationship("User", foreign_keys=[candidate_id])
    resume = relationship("Resume")
    status_updater = relationship("User", foreign_keys=[status_updated_by])
    referrer = relationship("User", foreign_keys=[referrer_id])

    # Indexes
    __table_args__ = (
        Index("idx_applications_position_status", "position_id", "status"),
        Index("idx_applications_candidate", "candidate_id", "applied_at"),
        Index("idx_applications_status_date", "status", "status_updated_at"),
    )

    @property
    def is_active(self) -> bool:
        """Check if application is still in active consideration"""
        return self.status not in [
            "rejected",
            "withdrawn",
            "hired",
        ]

    @property
    def days_since_applied(self) -> int:
        """Get number of days since application was submitted"""
        return (get_utc_now() - self.applied_at).days


class CompanyProfile(BaseModel):
    __tablename__ = "company_profiles"

    company_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    # Public profile information
    tagline: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )  # Short company tagline
    mission: Mapped[str | None] = mapped_column(Text, nullable=True)
    values: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array
    culture: Mapped[str | None] = mapped_column(
        LONGTEXT, nullable=True
    )  # Company culture description

    # Media and branding
    logo_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    banner_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    gallery_images: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # JSON array of image URLs
    company_video_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # Contact and social
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Social media links
    linkedin_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    twitter_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    facebook_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    instagram_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    youtube_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Stats and highlights
    founded_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    employee_count: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # e.g., "11-50", "201-500"
    headquarters: Mapped[str | None] = mapped_column(String(255), nullable=True)
    funding_stage: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )  # Seed, Series A, etc.

    # Benefits and perks
    benefits_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    perks_highlights: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # JSON array

    # SEO and visibility
    is_public: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    seo_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    seo_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    custom_slug: Mapped[str | None] = mapped_column(
        String(100), nullable=True, unique=True
    )

    # Analytics
    profile_views: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_updated_by: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )

    # Relationships
    company = relationship("Company", back_populates="profile")
    updater = relationship("User", foreign_keys=[last_updated_by])

    # Indexes
    __table_args__ = (
        Index("idx_company_profiles_public", "is_public"),
        Index("idx_company_profiles_slug", "custom_slug"),
    )

    @property
    def public_slug(self) -> str:
        """Get the public URL slug for this company"""
        if self.custom_slug:
            return self.custom_slug
        # Fallback to company domain or ID
        return (
            self.company.domain.split(".")[0]
            if self.company.domain
            else f"company-{self.company_id}"
        )

    def increment_view_count(self):
        """Increment profile view count"""
        self.profile_views += 1
