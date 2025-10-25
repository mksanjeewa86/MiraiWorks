"""Work Experience schemas for API validation and serialization."""

from datetime import date

from pydantic import BaseModel, Field


# Enums
class EmploymentType:
    """Employment type constants."""

    FULL_TIME = "Full-time"
    PART_TIME = "Part-time"
    CONTRACT = "Contract"
    FREELANCE = "Freelance"
    INTERNSHIP = "Internship"


# Base schema
class WorkExperienceBase(BaseModel):
    """Base work experience schema with common fields."""

    company_name: str = Field(..., min_length=1, max_length=255)
    company_logo_url: str | None = Field(None, max_length=500)
    position_title: str = Field(..., min_length=1, max_length=255)
    employment_type: str | None = Field(None, max_length=50)
    location: str | None = Field(None, max_length=255)
    start_date: date
    end_date: date | None = None
    is_current: bool = False
    description: str | None = None
    skills: str | None = None  # Comma-separated skills
    display_order: int = 0


# Create schema (for POST requests)
class WorkExperienceCreate(WorkExperienceBase):
    """Schema for creating a new work experience entry."""

    pass


# Update schema (for PUT/PATCH requests)
class WorkExperienceUpdate(BaseModel):
    """Schema for updating an existing work experience entry."""

    company_name: str | None = Field(None, min_length=1, max_length=255)
    company_logo_url: str | None = Field(None, max_length=500)
    position_title: str | None = Field(None, min_length=1, max_length=255)
    employment_type: str | None = Field(None, max_length=50)
    location: str | None = Field(None, max_length=255)
    start_date: date | None = None
    end_date: date | None = None
    is_current: bool | None = None
    description: str | None = None
    skills: str | None = None
    display_order: int | None = None


# Response schema (what API returns)
class WorkExperienceInfo(WorkExperienceBase):
    """Schema for work experience information in API responses."""

    id: int
    user_id: int

    class Config:
        from_attributes = True  # Allows Pydantic to work with ORM models
