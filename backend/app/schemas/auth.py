from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator
from app.utils.constants import CompanyType


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    require_2fa: bool = False
    user: Optional["UserInfo"] = None


class TwoFAVerifyRequest(BaseModel):
    user_id: int
    code: str


class TwoFAVerifyResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: "UserInfo"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetApproveRequest(BaseModel):
    request_id: int
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v


class ActivateAccountRequest(BaseModel):
    userId: int
    email: EmailStr
    temporaryPassword: str
    newPassword: str

    @field_validator("newPassword")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v


class ActivateAccountResponse(BaseModel):
    message: str
    success: bool = True
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: Optional[int] = None
    user: Optional["UserInfo"] = None


class RoleInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str] = None


class UserRoleInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    role_id: int
    created_at: datetime
    role: RoleInfo


class CompanyInfo(BaseModel):
    """Simplified company info for user responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    type: CompanyType


class UserInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    first_name: str
    last_name: str
    full_name: str
    company_id: Optional[int]
    company: Optional[CompanyInfo] = None
    roles: list[UserRoleInfo]
    is_active: bool
    last_login: Optional[datetime]


class PasswordResetRequestInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    user_email: str
    user_name: str
    is_used: bool
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    created_at: datetime


# Update forward references
LoginResponse.model_rebuild()
TwoFAVerifyResponse.model_rebuild()
