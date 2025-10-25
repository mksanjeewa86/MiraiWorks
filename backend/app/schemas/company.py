
from pydantic import BaseModel, ConfigDict, EmailStr

from app.utils.constants import CompanyType


class CompanyBase(BaseModel):
    """Base company schema with common fields."""

    name: str
    type: CompanyType
    email: EmailStr
    phone: str
    website: str | None = None
    postal_code: str | None = None
    prefecture: str | None = None
    city: str | None = None
    description: str | None = None


class CompanyCreate(CompanyBase):
    """Schema for creating a new company."""

    # Subscription options (optional - if not provided, will auto-assign basic plan)
    plan_id: int | None = None  # Which plan to assign
    is_trial: bool | None = False  # Whether to create as trial subscription
    trial_days: int | None = 30  # Trial period in days (if is_trial=True)


class CompanyUpdate(BaseModel):
    """Schema for updating a company."""

    name: str | None = None
    type: CompanyType | None = None
    email: EmailStr | None = None
    phone: str | None = None
    website: str | None = None
    postal_code: str | None = None
    prefecture: str | None = None
    city: str | None = None
    description: str | None = None
    is_active: bool | None = None


class CompanyResponse(CompanyBase):
    """Schema for company response."""

    id: int
    is_active: bool
    user_count: int
    job_count: int
    is_deleted: bool
    deleted_at: str | None = None
    deleted_by: int | None = None
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
