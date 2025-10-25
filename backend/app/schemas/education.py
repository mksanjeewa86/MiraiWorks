"""Education schemas for API validation and serialization."""

from datetime import date
from decimal import Decimal

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
    institution_logo_url: str | None = Field(None, max_length=500)
    degree_type: str = Field(..., min_length=1, max_length=100)
    field_of_study: str = Field(..., min_length=1, max_length=255)
    start_date: date | None = None
    end_date: date | None = None
    graduation_year: int | None = Field(None, ge=1900, le=2100)
    gpa: Decimal | None = Field(None, ge=0, le=10)  # Support different GPA scales
    gpa_max: Decimal | None = Field(None, ge=0, le=10)
    honors_awards: str | None = None
    description: str | None = None
    display_order: int = 0


# Create schema (for POST requests)
class EducationCreate(EducationBase):
    """Schema for creating a new education entry."""

    pass


# Update schema (for PUT/PATCH requests)
class EducationUpdate(BaseModel):
    """Schema for updating an existing education entry."""

    institution_name: str | None = Field(None, min_length=1, max_length=255)
    institution_logo_url: str | None = Field(None, max_length=500)
    degree_type: str | None = Field(None, min_length=1, max_length=100)
    field_of_study: str | None = Field(None, min_length=1, max_length=255)
    start_date: date | None = None
    end_date: date | None = None
    graduation_year: int | None = Field(None, ge=1900, le=2100)
    gpa: Decimal | None = Field(None, ge=0, le=10)
    gpa_max: Decimal | None = Field(None, ge=0, le=10)
    honors_awards: str | None = None
    description: str | None = None
    display_order: int | None = None


# Response schema (what API returns)
class EducationInfo(EducationBase):
    """Schema for education information in API responses."""

    id: int
    user_id: int

    class Config:
        from_attributes = True  # Allows Pydantic to work with ORM models
