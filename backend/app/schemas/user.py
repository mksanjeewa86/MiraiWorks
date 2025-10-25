from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, field_validator

from app.utils.constants import UserRole

if TYPE_CHECKING:
    pass


class UserCreate(BaseModel):
    email: str
    first_name: str
    last_name: str
    phone: str | None = None
    company_id: int | None = None
    roles: list[UserRole] = []
    is_admin: bool | None = False
    require_2fa: bool | None = False


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    is_active: bool | None = None
    is_admin: bool | None = None
    require_2fa: bool | None = None
    company_id: int | None = None
    roles: list[UserRole] | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    first_name: str
    last_name: str
    full_name: str
    phone: str | None
    company_id: int | None
    company_name: str | None
    roles: list[str]
    is_active: bool
    is_admin: bool
    require_2fa: bool
    last_login: datetime | None
    created_at: datetime
    updated_at: datetime


class UserListResponse(BaseModel):
    users: list["UserInfo"]
    total: int
    page: int
    per_page: int
    pages: int


class BulkUserImportRequest(BaseModel):
    csv_data: str  # Base64 encoded CSV data
    company_id: int | None = None  # Required for non-super-admin users


class BulkUserImportResponse(BaseModel):
    success: bool
    created_users: int
    failed_users: int
    errors: list[str]
    created_user_ids: list[int]


class UserFilters(BaseModel):
    page: int = 1
    size: int = 20
    search: str | None = None
    company_id: int | None = None
    is_active: bool | None = None
    is_admin: bool | None = None
    is_suspended: bool | None = None
    require_2fa: bool | None = None
    role: UserRole | None = None


class UserInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    first_name: str
    last_name: str
    full_name: str
    phone: str | None = None
    is_active: bool
    is_admin: bool
    require_2fa: bool
    last_login: datetime | None = None
    created_at: datetime
    updated_at: datetime
    company_id: int | None = None
    company_name: str | None = None
    roles: list[str] = []
    is_deleted: bool = False
    deleted_at: datetime | None = None
    is_suspended: bool = False
    suspended_at: datetime | None = None
    suspended_by: int | None = None


class PasswordResetRequest(BaseModel):
    user_id: int
    send_email: bool = True


class ResendActivationRequest(BaseModel):
    user_id: int


class BulkUserOperation(BaseModel):
    user_ids: list[int]
    send_email: bool = True


class UserHoldRequest(BaseModel):
    reason: str
    duration_hours: int | None = 24  # Default 24 hours


class UserSearchRequest(BaseModel):
    email: str | None = None
    name: str | None = None
    company_id: int | None = None
    role: UserRole | None = None
    is_active: bool | None = None
    page: int = 1
    per_page: int = 20

    @field_validator("per_page")
    @classmethod
    def validate_per_page(cls, v):
        if v > 100:
            raise ValueError("per_page cannot exceed 100")
        return v
