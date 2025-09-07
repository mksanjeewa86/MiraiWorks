from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, validator

from app.utils.constants import UserRole


class UserCreate(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str] = None
    company_id: Optional[int] = None
    roles: list[UserRole]
    is_admin: bool = False
    require_2fa: bool = False

    @validator("first_name", "last_name")
    def validate_names(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError("Names must be at least 2 characters long")
        return v.strip()


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    require_2fa: Optional[bool] = None

    @validator("first_name", "last_name")
    def validate_names(cls, v):
        if v is not None and (not v or len(v.strip()) < 2):
            raise ValueError("Names must be at least 2 characters long")
        return v.strip() if v else v


class UserResponse(BaseModel):
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

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    users: list[UserResponse]
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

    @validator("per_page")
    def validate_per_page(cls, v):
        if v > 100:
            raise ValueError("per_page cannot exceed 100")
        return v
