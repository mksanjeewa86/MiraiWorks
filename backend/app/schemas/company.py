from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr

from app.utils.constants import CompanyType


class CompanyBase(BaseModel):
    """Base company schema with common fields."""

    name: str
    type: CompanyType
    email: EmailStr
    phone: str
    website: Optional[str] = None
    postal_code: Optional[str] = None
    prefecture: Optional[str] = None
    city: Optional[str] = None
    description: Optional[str] = None


class CompanyCreate(CompanyBase):
    """Schema for creating a new company."""

    # Subscription options (optional - if not provided, will auto-assign basic plan)
    plan_id: Optional[int] = None  # Which plan to assign
    is_trial: Optional[bool] = False  # Whether to create as trial subscription
    trial_days: Optional[int] = 30  # Trial period in days (if is_trial=True)


class CompanyUpdate(BaseModel):
    """Schema for updating a company."""

    name: Optional[str] = None
    type: Optional[CompanyType] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    postal_code: Optional[str] = None
    prefecture: Optional[str] = None
    city: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class CompanyResponse(CompanyBase):
    """Schema for company response."""

    id: int
    is_active: bool
    user_count: int
    job_count: int
    is_deleted: bool
    deleted_at: Optional[str] = None
    deleted_by: Optional[int] = None
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)


class CompanyListResponse(BaseModel):
    """Schema for paginated company list response."""

    companies: list[CompanyResponse]
    total: int
    page: int
    size: int
    pages: int


class CompanyAdminStatus(BaseModel):
    """Schema for company admin status."""

    company_id: int
    has_active_admin: bool
    admin_count: int
