"""Education schemas for API validation and serialization."""

from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


# Enums
class DegreeType:
    """Degree type constants."""

    HIGH_SCHOOL = "High School"
    ASSOCIATE = "Associate Degree"
    BACHELOR = "Bachelor's Degree"
    MASTER = "Master's Degree"
    DOCTORATE = "Doctorate (PhD)"
    MBA = "MBA"
    CERTIFICATE = "Certificate"
    DIPLOMA = "Diploma"
    OTHER = "Other"


# Base schema
class EducationBase(BaseModel):
    """Base education schema with common fields."""

    institution_name: str = Field(..., min_length=1, max_length=255)
    institution_logo_url: Optional[str] = Field(None, max_length=500)
    degree_type: str = Field(..., min_length=1, max_length=100)
    field_of_study: str = Field(..., min_length=1, max_length=255)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    graduation_year: Optional[int] = Field(None, ge=1900, le=2100)
    gpa: Optional[Decimal] = Field(None, ge=0, le=10)  # Support different GPA scales
    gpa_max: Optional[Decimal] = Field(None, ge=0, le=10)
    honors_awards: Optional[str] = None
    description: Optional[str] = None
    display_order: int = 0


# Create schema (for POST requests)
class EducationCreate(EducationBase):
    """Schema for creating a new education entry."""

    pass


# Update schema (for PUT/PATCH requests)
class EducationUpdate(BaseModel):
    """Schema for updating an existing education entry."""

    institution_name: Optional[str] = Field(None, min_length=1, max_length=255)
    institution_logo_url: Optional[str] = Field(None, max_length=500)
    degree_type: Optional[str] = Field(None, min_length=1, max_length=100)
    field_of_study: Optional[str] = Field(None, min_length=1, max_length=255)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    graduation_year: Optional[int] = Field(None, ge=1900, le=2100)
    gpa: Optional[Decimal] = Field(None, ge=0, le=10)
    gpa_max: Optional[Decimal] = Field(None, ge=0, le=10)
    honors_awards: Optional[str] = None
    description: Optional[str] = None
    display_order: Optional[int] = None


# Response schema (what API returns)
class EducationInfo(EducationBase):
    """Schema for education information in API responses."""

    id: int
    user_id: int

    class Config:
        from_attributes = True  # Allows Pydantic to work with ORM models
