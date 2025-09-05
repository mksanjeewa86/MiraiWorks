from datetime import datetime

from sqlalchemy import JSON
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.utils.constants import ResumeStatus
from app.utils.constants import ResumeVisibility
from app.utils.constants import SectionType


class Resume(BaseModel):
    __tablename__ = "resumes"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Basic info
    title = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Personal information
    full_name = Column(String(100))
    email = Column(String(255))
    phone = Column(String(20))
    location = Column(String(200))
    website = Column(String(500))
    linkedin_url = Column(String(500))
    github_url = Column(String(500))
    
    # Professional summary
    professional_summary = Column(Text)
    objective = Column(Text)
    
    # Status and visibility
    status = Column(SQLEnum(ResumeStatus), default=ResumeStatus.DRAFT)
    visibility = Column(SQLEnum(ResumeVisibility), default=ResumeVisibility.PRIVATE)
    
    # Template and styling
    template_id = Column(String(50), default="modern")
    theme_color = Column(String(7), default="#2563eb")  # Hex color
    font_family = Column(String(50), default="Inter")
    custom_css = Column(Text)
    
    # Metadata
    is_primary = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)
    download_count = Column(Integer, default=0)
    last_viewed_at = Column(DateTime)
    
    # File attachments
    pdf_file_path = Column(String(500))
    pdf_generated_at = Column(DateTime)
    original_file_path = Column(String(500))  # For parsed resumes
    
    # SEO and sharing
    slug = Column(String(100), unique=True, index=True)
    share_token = Column(String(64), unique=True, index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="resumes")
    sections = relationship("ResumeSection", back_populates="resume", cascade="all, delete-orphan")
    experiences = relationship("WorkExperience", back_populates="resume", cascade="all, delete-orphan")
    educations = relationship("Education", back_populates="resume", cascade="all, delete-orphan")
    skills = relationship("Skill", back_populates="resume", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="resume", cascade="all, delete-orphan")
    certifications = relationship("Certification", back_populates="resume", cascade="all, delete-orphan")
    languages = relationship("Language", back_populates="resume", cascade="all, delete-orphan")
    references = relationship("Reference", back_populates="resume", cascade="all, delete-orphan")
    
    @classmethod
    async def get_by_user_id(cls, db, user_id: int, limit: int = 10, offset: int = 0):
        """Get resumes by user ID."""
        from sqlalchemy import select
        result = await db.execute(
            select(cls).where(cls.user_id == user_id)
            .order_by(cls.updated_at.desc())
            .limit(limit).offset(offset)
        )
        return result.scalars().all()
    
    @classmethod
    async def get_by_slug(cls, db, slug: str):
        """Get resume by slug."""
        from sqlalchemy import select
        result = await db.execute(select(cls).where(cls.slug == slug))
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
        self.last_viewed_at = datetime.utcnow()


class ResumeSection(BaseModel):
    __tablename__ = "resume_sections"
    
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    
    # Section info
    section_type = Column(SQLEnum(SectionType), nullable=False)
    title = Column(String(100), nullable=False)
    content = Column(Text)
    
    # Display options
    is_visible = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    
    # Custom styling
    custom_css = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    resume = relationship("Resume", back_populates="sections")


class WorkExperience(BaseModel):
    __tablename__ = "work_experiences"
    
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    
    # Job details
    company_name = Column(String(200), nullable=False)
    position_title = Column(String(200), nullable=False)
    location = Column(String(200))
    company_website = Column(String(500))
    
    # Employment period
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)  # NULL for current position
    is_current = Column(Boolean, default=False)
    
    # Job description
    description = Column(Text)
    achievements = Column(JSON)  # List of achievement strings
    technologies = Column(JSON)  # List of technology strings
    
    # Display options
    is_visible = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    resume = relationship("Resume", back_populates="experiences")


class Education(BaseModel):
    __tablename__ = "educations"
    
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    
    # Education details
    institution_name = Column(String(200), nullable=False)
    degree = Column(String(200), nullable=False)
    field_of_study = Column(String(200))
    location = Column(String(200))
    
    # Academic period
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    is_current = Column(Boolean, default=False)
    
    # Academic performance
    gpa = Column(String(10))  # e.g., "3.8/4.0"
    honors = Column(String(200))  # e.g., "Summa Cum Laude"
    
    # Additional info
    description = Column(Text)
    courses = Column(JSON)  # List of relevant courses
    
    # Display options
    is_visible = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    resume = relationship("Resume", back_populates="educations")


class Skill(BaseModel):
    __tablename__ = "skills"
    
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    
    # Skill details
    name = Column(String(100), nullable=False)
    category = Column(String(50))  # e.g., "Programming", "Design", "Languages"
    proficiency_level = Column(Integer)  # 1-5 or 1-10 scale
    proficiency_label = Column(String(20))  # e.g., "Expert", "Advanced", "Intermediate"
    
    # Display options
    is_visible = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    resume = relationship("Resume", back_populates="skills")


class Project(BaseModel):
    __tablename__ = "projects"
    
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    
    # Project details
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    
    # Project links
    project_url = Column(String(500))
    github_url = Column(String(500))
    demo_url = Column(String(500))
    
    # Project period
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    is_ongoing = Column(Boolean, default=False)
    
    # Technical details
    technologies = Column(JSON)  # List of technologies used
    role = Column(String(100))  # e.g., "Lead Developer", "Team Member"
    
    # Display options
    is_visible = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    resume = relationship("Resume", back_populates="projects")


class Certification(BaseModel):
    __tablename__ = "certifications"
    
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    
    # Certification details
    name = Column(String(200), nullable=False)
    issuing_organization = Column(String(200), nullable=False)
    credential_id = Column(String(100))
    credential_url = Column(String(500))
    
    # Dates
    issue_date = Column(DateTime, nullable=False)
    expiration_date = Column(DateTime)
    does_not_expire = Column(Boolean, default=False)
    
    # Additional info
    description = Column(Text)
    
    # Display options
    is_visible = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    resume = relationship("Resume", back_populates="certifications")


class Language(BaseModel):
    __tablename__ = "languages"
    
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    
    # Language details
    name = Column(String(50), nullable=False)
    proficiency = Column(String(20), nullable=False)  # e.g., "Native", "Fluent", "Conversational"
    
    # Display options
    is_visible = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    resume = relationship("Resume", back_populates="languages")


class Reference(BaseModel):
    __tablename__ = "references"
    
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    
    # Reference details
    full_name = Column(String(100), nullable=False)
    position_title = Column(String(100))
    company_name = Column(String(200))
    email = Column(String(255))
    phone = Column(String(20))
    reference_relationship = Column(String(100))  # e.g., "Former Manager", "Colleague"
    
    # Display options
    is_visible = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    resume = relationship("Resume", back_populates="references")


class ResumeTemplate(BaseModel):
    __tablename__ = "resume_templates"
    
    # Template details
    name = Column(String(100), nullable=False, unique=True)
    display_name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Template structure
    template_data = Column(JSON, nullable=False)  # Template configuration
    css_styles = Column(Text, nullable=False)  # CSS for the template
    html_template = Column(Text, nullable=False)  # HTML template
    
    # Template metadata
    category = Column(String(50))  # e.g., "Modern", "Classic", "Creative"
    color_scheme = Column(JSON)  # Available color options
    font_options = Column(JSON)  # Available font options
    
    # Usage and status
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)
    usage_count = Column(Integer, default=0)
    
    # Preview
    preview_image_url = Column(String(500))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @classmethod
    async def get_active_templates(cls, db, include_premium: bool = False):
        """Get all active templates."""
        from sqlalchemy import select
        query = select(cls).where(cls.is_active == True)
        if not include_premium:
            query = query.where(cls.is_premium == False)
        result = await db.execute(query.order_by(cls.usage_count.desc()))
        return result.scalars().all()


class ResumeShare(BaseModel):
    __tablename__ = "resume_shares"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    
    # Share details
    share_token = Column(String(64), nullable=False, unique=True, index=True)
    recipient_email = Column(String(255))
    recipient_name = Column(String(100))
    
    # Access control
    password_protected = Column(Boolean, default=False)
    password_hash = Column(String(255))
    expires_at = Column(DateTime)
    max_views = Column(Integer)
    view_count = Column(Integer, default=0)
    
    # Share options
    allow_download = Column(Boolean, default=True)
    show_contact_info = Column(Boolean, default=True)
    
    # Tracking
    last_viewed_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
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
        if self.expires_at and self.expires_at < datetime.utcnow():
            return True
        if self.max_views and self.view_count >= self.max_views:
            return True
        return False