import logging
import secrets
from datetime import datetime
from datetime import timedelta
from typing import List

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi import status
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies import check_rate_limit
from app.dependencies import get_client_ip
from app.dependencies import get_current_active_user
from app.dependencies import store_2fa_code
from app.dependencies import verify_2fa_code
from app.models.auth import PasswordResetRequest
from app.models.notification import Notification
from app.models.user import User
from app.schemas.auth import ChangePasswordRequest
from app.schemas.auth import LoginRequest
from app.schemas.auth import LoginResponse
from app.schemas.auth import PasswordResetApproveRequest
from app.schemas.auth import PasswordResetRequest as PWResetSchema
from app.schemas.auth import PasswordResetRequestInfo
from app.schemas.auth import RefreshTokenRequest
from app.schemas.auth import RefreshTokenResponse
from app.schemas.auth import TwoFAVerifyRequest
from app.schemas.auth import TwoFAVerifyResponse
from app.schemas.auth import UserInfo
from app.services.auth_service import auth_service
from app.services.email_service import email_service
from app.utils.constants import NotificationType
from app.utils.permissions import is_company_admin
from app.utils.permissions import is_super_admin

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/login", response_model=LoginResponse)
async def login(
    request: Request,
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Authenticate user with email and password."""
    client_ip = get_client_ip(request)
    
    # Rate limiting
    rate_key = f"login_attempts:{client_ip}:{login_data.email}"
    if not await check_rate_limit(rate_key, limit=5, window=300):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later."
        )
    
    # Authenticate user
    user = await auth_service.authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated"
        )
    
    # Check if 2FA is required
    requires_2fa = auth_service.requires_2fa(user)
    
    if requires_2fa:
        # Generate and send 2FA code
        code = auth_service.generate_2fa_code()
        await store_2fa_code(user.id, code, ttl=600)  # 10 minutes
        
        # Send 2FA code via email
        await email_service.send_2fa_code(user.email, code, user.full_name)
        
        return LoginResponse(
            access_token="",
            refresh_token="",
            require_2fa=True,
            expires_in=0
        )
    
    # Create tokens without 2FA
    tokens = await auth_service.create_login_tokens(db, user)
    
    return LoginResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        expires_in=tokens["expires_in"],
        user=UserInfo(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            full_name=user.full_name,
            company_id=user.company_id,
            roles=[ur.role.name for ur in user.user_roles],
            is_active=user.is_active,
            last_login=user.last_login
        )
    )


@router.post("/2fa/verify", response_model=TwoFAVerifyResponse)
async def verify_2fa(
    verify_data: TwoFAVerifyRequest,
    db: AsyncSession = Depends(get_db)
):
    """Verify 2FA code and complete login."""
    # Verify 2FA code
    if not await verify_2fa_code(verify_data.user_id, verify_data.code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired verification code"
        )
    
    # Get user
    result = await db.execute(
        select(User)
        .options(
            selectinload(User.company),
            selectinload(User.user_roles).selectinload("role")
        )
        .where(User.id == verify_data.user_id, User.is_active == True)
    )
    
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Create tokens
    tokens = await auth_service.create_login_tokens(db, user)
    
    return TwoFAVerifyResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        expires_in=tokens["expires_in"],
        user=UserInfo(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            full_name=user.full_name,
            company_id=user.company_id,
            roles=[ur.role.name for ur in user.user_roles],
            is_active=user.is_active,
            last_login=user.last_login
        )
    )


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token using refresh token."""
    user = await auth_service.verify_refresh_token(db, refresh_data.refresh_token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated"
        )
    
    # Create new access token
    access_token_data = {
        "sub": str(user.id),
        "email": user.email,
        "company_id": user.company_id,
        "roles": [ur.role.name for ur in user.user_roles],
    }
    
    access_token = auth_service.create_access_token(access_token_data)
    
    return RefreshTokenResponse(
        access_token=access_token,
        expires_in=auth_service.access_token_expire_minutes * 60
    )


@router.post("/logout")
async def logout(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """Logout user by revoking refresh token."""
    await auth_service.revoke_refresh_token(db, refresh_data.refresh_token)
    return {"message": "Logged out successfully"}


@router.post("/password-reset/request")
async def request_password_reset(
    reset_data: PWResetSchema,
    db: AsyncSession = Depends(get_db)
):
    """Request password reset (creates notification for admin approval)."""
    # Find user
    result = await db.execute(
        select(User)
        .options(selectinload(User.company))
        .where(User.email == reset_data.email, User.is_active == True)
    )
    
    user = result.scalar_one_or_none()
    if not user:
        # Don't reveal if email exists or not
        return {"message": "If the email exists, a password reset request has been submitted"}
    
    # Create password reset request
    reset_token = secrets.token_urlsafe(32)
    token_hash = auth_service.hash_token(reset_token)
    expires_at = datetime.utcnow() + timedelta(hours=24)
    
    password_reset = PasswordResetRequest(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at
    )
    
    db.add(password_reset)
    await db.commit()
    await db.refresh(password_reset)
    
    # Create notification for company admins
    if user.company_id:
        # Find company admins
        admin_result = await db.execute(
            select(User)
            .join(User.user_roles)
            .join("role")
            .where(
                User.company_id == user.company_id,
                User.is_active == True,
                User.is_admin == True
            )
        )
        company_admins = admin_result.scalars().all()
    else:
        # Find super admins for users without company
        admin_result = await db.execute(
            select(User)
            .join(User.user_roles)
            .join("role")
            .where(
                User.is_active == True,
                User.is_admin == True
            )
        )
        company_admins = admin_result.scalars().all()
    
    # Create notifications and send emails
    for admin in company_admins:
        notification = Notification(
            user_id=admin.id,
            type=NotificationType.PASSWORD_RESET_REQUEST.value,
            title="Password Reset Request",
            message=f"Password reset requested for {user.full_name} ({user.email})",
            payload={"reset_request_id": password_reset.id, "user_id": user.id}
        )
        db.add(notification)
        
        # Send email notification
        await email_service.send_password_reset_notification(
            admin.email,
            admin.full_name,
            user.full_name
        )
    
    await db.commit()
    
    return {"message": "If the email exists, a password reset request has been submitted"}


@router.post("/password-reset/approve")
async def approve_password_reset(
    approve_data: PasswordResetApproveRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Approve password reset request (admin only)."""
    if not is_company_admin(current_user) and not is_super_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    # Find password reset request
    result = await db.execute(
        select(PasswordResetRequest)
        .options(selectinload(PasswordResetRequest.user))
        .where(
            PasswordResetRequest.id == approve_data.request_id,
            PasswordResetRequest.is_used == False,
            PasswordResetRequest.expires_at > datetime.utcnow()
        )
    )
    
    reset_request = result.scalar_one_or_none()
    if not reset_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Password reset request not found or expired"
        )
    
    # Check company access
    target_user = reset_request.user
    if not is_super_admin(current_user) and current_user.company_id != target_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot approve reset for user in different company"
        )
    
    # Update user password
    hashed_password = auth_service.get_password_hash(approve_data.new_password)
    await db.execute(
        update(User)
        .where(User.id == target_user.id)
        .values(hashed_password=hashed_password)
    )
    
    # Mark reset request as used
    reset_request.is_used = True
    reset_request.approved_by = current_user.id
    reset_request.approved_at = datetime.utcnow()
    
    await db.commit()
    
    return {"message": "Password reset approved and updated"}


@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Change user's own password."""
    # Verify current password
    if not current_user.hashed_password or not auth_service.verify_password(
        password_data.current_password, current_user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )
    
    # Update password
    hashed_password = auth_service.get_password_hash(password_data.new_password)
    await db.execute(
        update(User)
        .where(User.id == current_user.id)
        .values(hashed_password=hashed_password)
    )
    
    await db.commit()
    
    return {"message": "Password changed successfully"}


@router.get("/me", response_model=UserInfo)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user information."""
    return UserInfo(
        id=current_user.id,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        full_name=current_user.full_name,
        company_id=current_user.company_id,
        roles=[ur.role.name for ur in current_user.user_roles],
        is_active=current_user.is_active,
        last_login=current_user.last_login
    )


@router.get("/password-reset/requests", response_model=List[PasswordResetRequestInfo])
async def get_password_reset_requests(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get pending password reset requests (admin only)."""
    if not is_company_admin(current_user) and not is_super_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    query = select(PasswordResetRequest).options(
        selectinload(PasswordResetRequest.user)
    ).where(
        PasswordResetRequest.is_used == False,
        PasswordResetRequest.expires_at > datetime.utcnow()
    )
    
    # Company scoping for non-super-admin
    if not is_super_admin(current_user):
        query = query.join(PasswordResetRequest.user).where(
            User.company_id == current_user.company_id
        )
    
    result = await db.execute(query)
    requests = result.scalars().all()
    
    return [
        PasswordResetRequestInfo(
            id=req.id,
            user_id=req.user_id,
            user_email=req.user.email,
            user_name=req.user.full_name,
            is_used=req.is_used,
            approved_by=req.approved_by,
            approved_at=req.approved_at,
            created_at=req.created_at
        )
        for req in requests
    ]