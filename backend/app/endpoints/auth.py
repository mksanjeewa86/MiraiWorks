import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies import (
    check_rate_limit,
    get_client_ip,
    get_current_active_user,
    store_2fa_code,
    verify_2fa_code,
)
from app.models.auth import PasswordResetRequest
from app.models.company import Company
from app.models.notification import Notification
from app.models.role import UserRole as UserRoleModel
from app.models.user import User
from app.models.user_settings import UserSettings
from app.schemas.auth import (
    ActivateAccountRequest,
    ActivateAccountResponse,
    ChangePasswordRequest,
    LoginRequest,
    LoginResponse,
    PasswordResetApproveRequest,
    PasswordResetRequestInfo,
    RefreshTokenRequest,
    RefreshTokenResponse,
    TwoFAVerifyRequest,
    TwoFAVerifyResponse,
    UserInfo,
)
from app.schemas.auth import PasswordResetRequest as PWResetSchema
from app.services.auth_service import auth_service
from app.services.email_service import email_service
from app.utils.constants import NotificationType
from app.utils.logging import get_logger
from app.utils.permissions import is_company_admin, is_super_admin

router = APIRouter()
logger = get_logger(__name__)


@router.post("/login", response_model=LoginResponse)
async def login(
    request: Request, login_data: LoginRequest, db: AsyncSession = Depends(get_db)
):
    """Authenticate user with email and password."""
    client_ip = await get_client_ip(request)

    # Rate limiting (more generous limits for development)
    rate_key = f"login_attempts:{client_ip}:{login_data.email}"
    if not await check_rate_limit(rate_key, limit=20, window=300):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later.",
        )

    # Authenticate user
    logger.info(
        "Attempting user authentication", email=login_data.email, component="auth"
    )

    user = await auth_service.authenticate_user(
        db, login_data.email, login_data.password
    )
    if not user:
        logger.warning(
            "Authentication failed",
            email=login_data.email,
            reason="invalid_credentials",
            component="auth",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    if not user.is_active:
        logger.warning(
            "Authentication failed",
            email=login_data.email,
            user_id=user.id,
            reason="account_deactivated",
            component="auth",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Account is deactivated"
        )

    logger.info(
        "User authenticated successfully",
        email=login_data.email,
        user_id=user.id,
        component="auth",
    )

    # Debug: Check what the user object actually contains
    user_dict = {
        "id": user.id,
        "email": user.email,
        "require_2fa": user.require_2fa,
        "require_2fa_type": type(user.require_2fa),
        "is_active": user.is_active,
        "is_admin": user.is_admin,
    }
    print(f"[DEBUG] User object: {user_dict}")

    # Check if 2FA is required (either individual setting or role-based requirement)
    requires_2fa = await auth_service.requires_2fa(db, user)
    if requires_2fa:
        logger.info(
            "2FA required for user", user_id=user.id, email=user.email, component="2fa"
        )

        # Generate and send 2FA code
        code = auth_service.generate_2fa_code()
        await store_2fa_code(user.id, code, ttl=600)  # 10 minutes

        # Send 2FA code via email
        await email_service.send_2fa_code(user.email, code, user.full_name)
        logger.info("2FA code sent", user_id=user.id, component="2fa")

        # Determine if this is individual user 2FA or admin role-based 2FA
        user_data = None
        if user.require_2fa:
            # Individual user 2FA - include user data in response
            user_data = UserInfo(
                id=user.id,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                full_name=user.full_name,
                company_id=user.company_id,
                company=user.company,
                roles=user.user_roles,
                is_active=user.is_active,
                last_login=user.last_login,
            )

        return LoginResponse(
            access_token="",
            refresh_token="",
            require_2fa=True,
            expires_in=0,
            user=user_data,
        )

    # Create tokens without 2FA
    logger.info("Creating login tokens", user_id=user.id, component="auth")
    tokens = await auth_service.create_login_tokens(db, user)
    logger.info("Login successful", user_id=user.id, email=user.email, component="auth")

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
            company=user.company,
            roles=user.user_roles,
            is_active=user.is_active,
            last_login=user.last_login,
        ),
    )


@router.post("/2fa/verify", response_model=TwoFAVerifyResponse)
async def verify_2fa(
    verify_data: TwoFAVerifyRequest, db: AsyncSession = Depends(get_db)
):
    """Verify 2FA code and complete login."""
    # Verify 2FA code
    if not await verify_2fa_code(verify_data.user_id, verify_data.code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired verification code",
        )

    # Get user
    result = await db.execute(
        select(User)
        .options(
            selectinload(User.company),
            selectinload(User.user_roles).selectinload(UserRoleModel.role),
        )
        .where(User.id == verify_data.user_id, User.is_active == True)
    )

    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
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
            company=user.company,
            roles=user.user_roles,
            is_active=user.is_active,
            last_login=user.last_login,
        ),
    )


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest, db: AsyncSession = Depends(get_db)
):
    """Refresh access token using refresh token."""
    user = await auth_service.verify_refresh_token(db, refresh_data.refresh_token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Account is deactivated"
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
        expires_in=auth_service.access_token_expire_minutes * 60,
    )


@router.post("/logout")
async def logout(
    logout_data: RefreshTokenRequest | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Logout user by revoking refresh token."""
    # Check if request body is provided
    if not logout_data or not logout_data.refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token required for logout"
        )

    # Find user by refresh token and revoke it
    user = await auth_service.verify_refresh_token(db, logout_data.refresh_token)
    if user:
        # Revoke all refresh tokens for this user
        await auth_service.revoke_user_tokens(db, user.id)

    # Always return success to prevent token enumeration
    return {"message": "Logged out successfully"}


@router.post("/password-reset/request")
async def request_password_reset(
    reset_data: PWResetSchema, db: AsyncSession = Depends(get_db)
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
        return {
            "message": "If the email exists, a password reset request has been submitted"
        }

    # Create password reset request
    reset_token = secrets.token_urlsafe(32)
    token_hash = auth_service.hash_token(reset_token)
    expires_at = datetime.utcnow() + timedelta(hours=24)

    password_reset = PasswordResetRequest(
        user_id=user.id, token_hash=token_hash, expires_at=expires_at
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
            .join(UserRoleModel.role)
            .where(
                User.company_id == user.company_id,
                User.is_active == True,
                User.is_admin == True,
            )
        )
        company_admins = admin_result.scalars().all()
    else:
        # Find super admins for users without company
        admin_result = await db.execute(
            select(User)
            .join(User.user_roles)
            .join(UserRoleModel.role)
            .where(User.is_active == True, User.is_admin == True)
        )
        company_admins = admin_result.scalars().all()

    # Create notifications and send emails
    for admin in company_admins:
        notification = Notification(
            user_id=admin.id,
            type=NotificationType.PASSWORD_RESET_REQUEST.value,
            title="Password Reset Request",
            message=f"Password reset requested for {user.full_name} ({user.email})",
            payload={"reset_request_id": password_reset.id, "user_id": user.id},
        )
        db.add(notification)

        # Send email notification
        await email_service.send_password_reset_notification(
            admin.email, admin.full_name, user.full_name
        )

    await db.commit()

    return {
        "message": "If the email exists, a password reset request has been submitted"
    }


@router.post("/password-reset/approve")
async def approve_password_reset(
    approve_data: PasswordResetApproveRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Approve password reset request (admin only)."""
    if not is_company_admin(current_user) and not is_super_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required"
        )

    # Find password reset request
    result = await db.execute(
        select(PasswordResetRequest)
        .options(selectinload(PasswordResetRequest.user))
        .where(
            PasswordResetRequest.id == approve_data.request_id,
            PasswordResetRequest.is_used == False,
            PasswordResetRequest.expires_at > datetime.utcnow(),
        )
    )

    reset_request = result.scalar_one_or_none()
    if not reset_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Password reset request not found or expired",
        )

    # Check company access
    target_user = reset_request.user
    if (
        not is_super_admin(current_user)
        and current_user.company_id != target_user.company_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot approve reset for user in different company",
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
    db: AsyncSession = Depends(get_db),
):
    """Change user's own password."""
    # Verify current password
    if not current_user.hashed_password or not auth_service.verify_password(
        password_data.current_password, current_user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect",
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
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user information."""
    # Fetch user with company relationship
    result = await db.execute(
        select(User)
        .options(
            selectinload(User.company),
            selectinload(User.user_roles).selectinload(UserRoleModel.role),
        )
        .where(User.id == current_user.id)
    )

    user_with_company = result.scalar_one()

    return UserInfo(
        id=user_with_company.id,
        email=user_with_company.email,
        first_name=user_with_company.first_name,
        last_name=user_with_company.last_name,
        full_name=user_with_company.full_name,
        company_id=user_with_company.company_id,
        company=user_with_company.company,
        roles=user_with_company.user_roles,
        is_active=user_with_company.is_active,
        last_login=user_with_company.last_login,
    )


@router.get("/password-reset/requests", response_model=list[PasswordResetRequestInfo])
async def get_password_reset_requests(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get pending password reset requests (admin only)."""
    if not is_company_admin(current_user) and not is_super_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required"
        )

    query = (
        select(PasswordResetRequest)
        .options(selectinload(PasswordResetRequest.user))
        .where(
            PasswordResetRequest.is_used == False,
            PasswordResetRequest.expires_at > datetime.utcnow(),
        )
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
            created_at=req.created_at,
        )
        for req in requests
    ]


@router.post("/activate", response_model=ActivateAccountResponse)
async def activate_account(
    activation_data: ActivateAccountRequest, db: AsyncSession = Depends(get_db)
):
    """Activate user account with temporary password and set new password."""
    # Get user with the provided ID
    result = await db.execute(
        select(User)
        .options(
            selectinload(User.company),
            selectinload(User.user_roles).selectinload(UserRoleModel.role),
        )
        .where(User.id == activation_data.userId)
    )

    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Verify email matches
    if user.email != activation_data.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email does not match user record",
        )

    # Verify user is inactive (waiting for activation)
    if user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is already activated",
        )

    # Verify temporary password
    if not user.hashed_password:
        logger.error(
            "Account activation failed - no hashed password set",
            user_id=user.id,
            email=user.email,
            component="auth"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account not properly configured. Please contact administrator.",
        )

    password_valid = auth_service.verify_password(
        activation_data.temporaryPassword, user.hashed_password
    )

    if not password_valid:
        logger.warning(
            "Account activation failed - invalid temporary password",
            user_id=user.id,
            email=user.email,
            password_length=len(activation_data.temporaryPassword),
            component="auth"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid temporary password",
        )

    # Update user with new password and activate account, add default phone if missing
    hashed_password = auth_service.get_password_hash(activation_data.newPassword)
    update_values = {
        "hashed_password": hashed_password,
        "is_active": True,
        "last_login": datetime.utcnow(),
    }
    
    # Add default phone number if user doesn't have one
    if not user.phone:
        update_values["phone"] = "+1-555-0100"  # Default placeholder phone
    
    await db.execute(
        update(User)
        .where(User.id == user.id)
        .values(**update_values)
    )

    # Check if user already has settings, if not create default ones
    existing_settings_query = select(UserSettings).where(UserSettings.user_id == user.id)
    existing_settings_result = await db.execute(existing_settings_query)
    existing_settings = existing_settings_result.scalar_one_or_none()
    
    if not existing_settings:
        # Create default user settings for activated user
        default_settings = UserSettings(
            user_id=user.id,
            # Profile settings with defaults
            job_title="User" if not user.is_admin else "Administrator",
            bio=f"Welcome to {user.company.name if user.company else 'MiraiWorks'}!",
            # Notification preferences (use model defaults)
            email_notifications=True,
            push_notifications=True,
            sms_notifications=False,
            interview_reminders=True,
            application_updates=True,
            message_notifications=True,
            # UI preferences (use model defaults)
            language="en",
            timezone="America/New_York",
            date_format="MM/DD/YYYY",
        )
        db.add(default_settings)

    # If this is an admin user activating, also activate their company
    if user.is_admin and user.company_id:
        await db.execute(
            update(Company).where(Company.id == user.company_id).values(is_active="1")
        )

    await db.commit()
    
    # Refresh user object to get updated data
    await db.refresh(user)
    
    logger.info(
        "User account activated successfully",
        user_id=user.id,
        email=user.email,
        component="auth",
    )

    # Generate authentication tokens for automatic login
    tokens = await auth_service.create_login_tokens(db, user)

    return ActivateAccountResponse(
        message="Account activated successfully",
        success=True,
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
            company=user.company,
            roles=user.user_roles,
            is_active=user.is_active,
            last_login=user.last_login,
        ),
    )
