"""Work Experience schemas for API validation and serialization."""

from datetime import date
from typing import Optional

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
    company_logo_url: Optional[str] = Field(None, max_length=500)
    position_title: str = Field(..., min_length=1, max_length=255)
    employment_type: Optional[str] = Field(None, max_length=50)
    location: Optional[str] = Field(None, max_length=255)
    start_date: date
    end_date: Optional[date] = None
    is_current: bool = False
    description: Optional[str] = None
    skills: Optional[str] = None  # Comma-separated skills
    display_order: int = 0


# Create schema (for POST requests)
class WorkExperienceCreate(WorkExperienceBase):
    """Schema for creating a new work experience entry."""

    pass


# Update schema (for PUT/PATCH requests)
class WorkExperienceUpdate(BaseModel):
    """Schema for updating an existing work experience entry."""

    company_name: Optional[str] = Field(None, min_length=1, max_length=255)
    company_logo_url: Optional[str] = Field(None, max_length=500)
    position_title: Optional[str] = Field(None, min_length=1, max_length=255)
    employment_type: Optional[str] = Field(None, max_length=50)
    location: Optional[str] = Field(None, max_length=255)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: Optional[bool] = None
    description: Optional[str] = None
    skills: Optional[str] = None
    display_order: Optional[int] = None


# Response schema (what API returns)
class WorkExperienceInfo(WorkExperienceBase):
    """Schema for work experience information in API responses."""

    id: int
    user_id: int

    class Config:
        from_attributes = True  # Allows Pydantic to work with ORM models
