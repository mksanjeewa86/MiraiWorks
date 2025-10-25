"""
Pydantic schemas for Blocked Companies
"""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class BlockedCompanyBase(BaseModel):
    """Base schema for BlockedCompany."""

    company_id: int | None = Field(
        None, description="ID of company to block (if exists in system)"
    )
    company_name: str | None = Field(
        None, max_length=255, description="Name of company to block (free text)"
    )
    reason: str | None = Field(
        None, max_length=500, description="Reason for blocking (optional)"
    )

    @field_validator("company_name")
    @classmethod
    def validate_company_name(cls, v):
        """Validate and sanitize company name."""
        if v is not None:
            v = v.strip()
            if not v:
                return None
        return v


class BlockedCompanyCreate(BlockedCompanyBase):
    """Schema for creating a blocked company entry."""

    @field_validator("company_id", "company_name")
    @classmethod
    def validate_at_least_one_identifier(cls, v, info):
        """Ensure either company_id or company_name is provided."""
        # This validation will be done in the endpoint logic
        return v


class BlockedCompanyUpdate(BaseModel):
    """Schema for updating a blocked company entry."""

    reason: str | None = Field(None, max_length=500)


class BlockedCompanyInfo(BlockedCompanyBase):
    """Schema for blocked company response."""

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CompanySearchResult(BaseModel):
    """Schema for company search results (for autocomplete)."""

    id: int
    name: str

    class Config:
        from_attributes = True
