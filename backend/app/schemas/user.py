from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel, ConfigDict, field_validator

from app.utils.constants import UserRole

if TYPE_CHECKING:
    pass


class UserCreate(BaseModel):
    email: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    company_id: Optional[int] = None
    roles: List[UserRole] = []
    is_admin: Optional[bool] = False
    require_2fa: Optional[bool] = False


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    require_2fa: Optional[bool] = None
    company_id: Optional[int] = None
    roles: Optional[List[UserRole]] = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    first_name: str
    last_name: str
    full_name: str
    phone: Optional[str]
    company_id: Optional[int]
    company_name: Optional[str]
    roles: list[str]
    is_active: bool
    is_admin: bool
    require_2fa: bool
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class UserListResponse(BaseModel):
    users: List["UserInfo"]
    total: int
    page: int
    per_page: int
    pages: int


class BulkUserImportRequest(BaseModel):
    csv_data: str  # Base64 encoded CSV data
    company_id: Optional[int] = None  # Required for non-super-admin users


class BulkUserImportResponse(BaseModel):
    success: bool
    created_users: int
    failed_users: int
    errors: list[str]
    created_user_ids: list[int]


class UserFilters(BaseModel):
    page: int = 1
    size: int = 20
    search: Optional[str] = None
    company_id: Optional[int] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    is_suspended: Optional[bool] = None
    require_2fa: Optional[bool] = None
    role: Optional[UserRole] = None


class UserInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    first_name: str
    last_name: str
    full_name: str
    phone: Optional[str] = None
    is_active: bool
    is_admin: bool
    require_2fa: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    company_id: Optional[int] = None
    company_name: Optional[str] = None
    roles: List[str] = []
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    is_suspended: bool = False
    suspended_at: Optional[datetime] = None
    suspended_by: Optional[int] = None


class PasswordResetRequest(BaseModel):
    user_id: int
    send_email: bool = True


class ResendActivationRequest(BaseModel):
    user_id: int


class BulkUserOperation(BaseModel):
    user_ids: List[int]
    send_email: bool = True


class UserHoldRequest(BaseModel):
    reason: str
    duration_hours: Optional[int] = 24  # Default 24 hours


class UserSearchRequest(BaseModel):
    email: Optional[str] = None
    name: Optional[str] = None
    company_id: Optional[int] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    page: int = 1
    per_page: int = 20

    @field_validator("per_page")
    @classmethod
    def validate_per_page(cls, v):
        if v > 100:
            raise ValueError("per_page cannot exceed 100")
        return v
