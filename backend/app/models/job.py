from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from .base import Base


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


class Job(Base):
    __tablename__ = 'jobs'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    # Basic job information
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    description: Mapped[str] = mapped_column(LONGTEXT, nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Short description for listings
    
    # Company and location
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey('companies.id', ondelete='CASCADE'), nullable=False, index=True)
    department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    
    # Job details
    job_type: Mapped[str] = mapped_column(String(50), nullable=False, default=JobType.FULL_TIME, index=True)
    experience_level: Mapped[str] = mapped_column(String(50), nullable=False, default=ExperienceLevel.MID_LEVEL, index=True)
    remote_type: Mapped[str] = mapped_column(String(50), nullable=False, default=RemoteType.ON_SITE, index=True)
    
    # Requirements and skills
    requirements: Mapped[Optional[str]] = mapped_column(LONGTEXT, nullable=True)
    preferred_skills: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array
    required_skills: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array
    
    # Compensation
    salary_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # In cents
    salary_max: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # In cents
    salary_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, default=SalaryType.ANNUAL)
    salary_currency: Mapped[str] = mapped_column(String(3), nullable=False, default='USD')
    show_salary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    
    # Benefits and perks
    benefits: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array
    perks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array
    
    # Application settings
    application_deadline: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, index=True)
    external_apply_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)  # If using external ATS
    application_questions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array
    
    # Status and visibility
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=JobStatus.DRAFT, index=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    is_urgent: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    
    # SEO and social
    seo_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    seo_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    social_image_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    
    # Analytics
    view_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    application_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # Publishing dates
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, index=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, index=True)
    
    # Metadata
    posted_by: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="jobs")
    posted_by_user = relationship("User", foreign_keys=[posted_by])
    applications = relationship("JobApplication", back_populates="job", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_jobs_company_status', 'company_id', 'status'),
        Index('idx_jobs_published', 'published_at', 'status'),
        Index('idx_jobs_location_type', 'country', 'city', 'job_type'),
        Index('idx_jobs_experience_remote', 'experience_level', 'remote_type'),
        Index('idx_jobs_featured_status', 'is_featured', 'status', 'published_at'),
    )

    @property
    def is_active(self) -> bool:
        """Check if job is currently active and accepting applications"""
        now = datetime.utcnow()
        return (
            self.status == JobStatus.PUBLISHED and
            (self.application_deadline is None or self.application_deadline > now) and
            (self.expires_at is None or self.expires_at > now)
        )

    @property
    def days_since_published(self) -> Optional[int]:
        """Get number of days since job was published"""
        if not self.published_at:
            return None
        return (datetime.utcnow() - self.published_at).days

    @property
    def salary_range_display(self) -> Optional[str]:
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


class JobApplication(Base):
    __tablename__ = 'job_applications'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    # References
    job_id: Mapped[int] = mapped_column(Integer, ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False, index=True)
    candidate_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    resume_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('resumes.id', ondelete='SET NULL'), nullable=True)
    
    # Application data
    cover_letter: Mapped[Optional[str]] = mapped_column(LONGTEXT, nullable=True)
    application_answers: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON responses to custom questions
    
    # Status tracking
    status: Mapped[str] = mapped_column(String(50), nullable=False, default=ApplicationStatus.APPLIED, index=True)
    status_updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    status_updated_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Communication
    last_contacted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Internal recruiter notes
    
    # Source tracking
    source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # Where they found the job
    referrer_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Metadata
    applied_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    job = relationship("Job", back_populates="applications")
    candidate = relationship("User", foreign_keys=[candidate_id])
    resume = relationship("Resume")
    status_updater = relationship("User", foreign_keys=[status_updated_by])
    referrer = relationship("User", foreign_keys=[referrer_id])
    
    # Indexes
    __table_args__ = (
        Index('idx_applications_job_status', 'job_id', 'status'),
        Index('idx_applications_candidate', 'candidate_id', 'applied_at'),
        Index('idx_applications_status_date', 'status', 'status_updated_at'),
    )

    @property
    def is_active(self) -> bool:
        """Check if application is still in active consideration"""
        return self.status not in [
            ApplicationStatus.REJECTED,
            ApplicationStatus.WITHDRAWN,
            ApplicationStatus.HIRED
        ]

    @property
    def days_since_applied(self) -> int:
        """Get number of days since application was submitted"""
        return (datetime.utcnow() - self.applied_at).days


class CompanyProfile(Base):
    __tablename__ = 'company_profiles'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey('companies.id', ondelete='CASCADE'), nullable=False, unique=True)
    
    # Public profile information
    tagline: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Short company tagline
    mission: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    values: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array
    culture: Mapped[Optional[str]] = mapped_column(LONGTEXT, nullable=True)  # Company culture description
    
    # Media and branding
    logo_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    banner_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    gallery_images: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array of image URLs
    company_video_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    
    # Contact and social
    contact_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Social media links
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    twitter_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    facebook_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    instagram_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    youtube_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Stats and highlights
    founded_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    employee_count: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # e.g., "11-50", "201-500"
    headquarters: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    funding_stage: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # Seed, Series A, etc.
    
    # Benefits and perks
    benefits_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    perks_highlights: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array
    
    # SEO and visibility
    is_public: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    seo_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    seo_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    custom_slug: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, unique=True)
    
    # Analytics
    profile_views: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_updated_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="profile")
    updater = relationship("User", foreign_keys=[last_updated_by])
    
    # Indexes
    __table_args__ = (
        Index('idx_company_profiles_public', 'is_public'),
        Index('idx_company_profiles_slug', 'custom_slug'),
    )

    @property
    def public_slug(self) -> str:
        """Get the public URL slug for this company"""
        if self.custom_slug:
            return self.custom_slug
        # Fallback to company domain or ID
        return self.company.domain.split('.')[0] if self.company.domain else f"company-{self.company_id}"

    def increment_view_count(self):
        """Increment profile view count"""
        self.profile_views += 1