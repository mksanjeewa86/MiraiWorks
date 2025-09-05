from pydantic import BaseModel, EmailStr, validator
from typing import List, Optional
from datetime import datetime


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    require_2fa: bool = False
    user: Optional['UserInfo'] = None


class TwoFAVerifyRequest(BaseModel):
    user_id: int
    code: str


class TwoFAVerifyResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: 'UserInfo'


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
    
    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserInfo(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    full_name: str
    company_id: Optional[int]
    roles: List[str]
    is_active: bool
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True


class PasswordResetRequestInfo(BaseModel):
    id: int
    user_id: int
    user_email: str
    user_name: str
    is_used: bool
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Update forward references
LoginResponse.model_rebuild()
TwoFAVerifyResponse.model_rebuild()