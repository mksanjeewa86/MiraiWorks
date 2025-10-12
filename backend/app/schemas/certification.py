"""Certification schemas for API validation and serialization."""

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


# Base schema
class CertificationBase(BaseModel):
    """Base certification schema with common fields."""

    certification_name: str = Field(..., min_length=1, max_length=255)
    issuing_organization: str = Field(..., min_length=1, max_length=255)
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    does_not_expire: bool = False
    credential_id: Optional[str] = Field(None, max_length=255)
    credential_url: Optional[str] = Field(None, max_length=500)
    certificate_image_url: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    display_order: int = 0


# Create schema (for POST requests)
class CertificationCreate(CertificationBase):
    """Schema for creating a new certification entry."""

    pass


# Update schema (for PUT/PATCH requests)
class CertificationUpdate(BaseModel):
    """Schema for updating an existing certification entry."""

    certification_name: Optional[str] = Field(None, min_length=1, max_length=255)
    issuing_organization: Optional[str] = Field(None, min_length=1, max_length=255)
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    does_not_expire: Optional[bool] = None
    credential_id: Optional[str] = Field(None, max_length=255)
    credential_url: Optional[str] = Field(None, max_length=500)
    certificate_image_url: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    display_order: Optional[int] = None


# Response schema (what API returns)
class CertificationInfo(CertificationBase):
    """Schema for certification information in API responses."""

    id: int
    user_id: int

    class Config:
        from_attributes = True  # Allows Pydantic to work with ORM models
