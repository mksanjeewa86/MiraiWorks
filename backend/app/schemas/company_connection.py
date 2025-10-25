"""Pydantic schemas for company connections."""

from datetime import datetime

from pydantic import BaseModel, Field


class CompanyConnectionBase(BaseModel):
    """Base schema for company connection."""

    connection_type: str = Field(default="standard", max_length=50)
    can_message: bool = Field(default=True)
    can_view_profile: bool = Field(default=True)
    can_assign_tasks: bool = Field(default=False)


class UserToCompanyConnectionCreate(CompanyConnectionBase):
    """Schema for creating user-to-company connection."""

    target_company_id: int = Field(..., description="Target company ID")


class CompanyToCompanyConnectionCreate(CompanyConnectionBase):
    """Schema for creating company-to-company connection."""

    source_company_id: int = Field(..., description="Source company ID")
    target_company_id: int = Field(..., description="Target company ID")


class CompanyConnectionInfo(BaseModel):
    """Schema for company connection response."""

    id: int
    source_type: str
    source_user_id: int | None = None
    source_company_id: int | None = None
    target_company_id: int
    is_active: bool
    connection_type: str
    can_message: bool
    can_view_profile: bool
    can_assign_tasks: bool
    creation_type: str
    created_by: int | None = None
    created_at: datetime
    updated_at: datetime | None = None

    # Computed fields for display
    source_display_name: str | None = None
    target_company_name: str | None = None

    class Config:
        from_attributes = True


class CompanyConnectionUpdate(BaseModel):
    """Schema for updating company connection permissions."""

    connection_type: str | None = Field(None, max_length=50)
    can_message: bool | None = None
    can_view_profile: bool | None = None
    can_assign_tasks: bool | None = None
