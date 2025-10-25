import logging
import secrets
import string

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config.endpoints import API_ROUTES
from app.crud import user as user_crud
from app.database import get_db
from app.dependencies import get_current_active_user
from app.models import Company, User, UserRole, UserSettings
from app.models.role import Role
from app.schemas.user import (
    BulkUserOperation,
    PasswordResetRequest,
    UserCreate,
    UserInfo,
    UserListResponse,
    UserUpdate,
)
from app.services.auth_service import auth_service
from app.services.email_service import email_service
from app.services.user_connection_service import user_connection_service
from app.utils.constants import UserRole as UserRoleEnum
from app.utils.permissions import is_company_admin, is_recruiter, is_super_admin

router = APIRouter()
logger = logging.getLogger(__name__)


async def get_super_admin_user(db: AsyncSession) -> User | None:
    """Get the first available super admin user."""
    super_admin_query = (
        select(User)
        .join(UserRole)
        .join(Role)
        .where(
            and_(
                Role.name == UserRoleEnum.SYSTEM_ADMIN.value,
                User.is_active is True,
                User.is_deleted is False,
            )
        )
        .limit(1)
    )
    result = await db.execute(super_admin_query)
    return result.scalar_one_or_none()


@router.get(API_ROUTES.USERS.ADMIN_USERS, response_model=UserListResponse)
async def get_users(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=500),
    search: str | None = Query(None),
    company_id: int | None = Query(None),
    is_active: bool | None = Query(None),
    is_admin: bool | None = Query(None),
    is_suspended: bool | None = Query(None),
    require_2fa: bool | None = Query(None),
    role: UserRoleEnum | None = Query(None),
    include_deleted: bool = Query(False),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get paginated list of users with filters."""

    # Ensure company relationship is loaded
    if current_user.company_id and not current_user.company:
        company_result = await db.execute(
            select(Company).where(Company.id == current_user.company_id)
        )
        current_user.company = company_result.scalar_one_or_none()

    # Check permissions
    # Allow recruiters to view candidates in their company
    is_viewing_candidates = role == UserRoleEnum.CANDIDATE
    has_permission = (
        is_super_admin(current_user)
        or is_company_admin(current_user)
        or (is_recruiter(current_user) and is_viewing_candidates)
    )

    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view users",
        )

    # Determine company filter based on permissions
    # Recruiters and company admins can only see users from their company
    if (
        is_company_admin(current_user) or is_recruiter(current_user)
    ) and not is_super_admin(current_user):
        company_id = current_user.company_id

    users, total = await user_crud.user.get_users_paginated(
        db=db,
        page=page,
        size=size,
        search=search,
        company_id=company_id,
        is_active=is_active,
        is_admin=is_admin,
        is_suspended=is_suspended,
        require_2fa=require_2fa,
        role=role,
        include_deleted=include_deleted,
        current_user_id=current_user.id,
    )

    # Format response
    user_list = []
    for user in users:
        user_roles = [role.role.name for role in user.user_roles]
        user_info = UserInfo(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            full_name=user.full_name,
            phone=user.phone,
            is_active=user.is_active,
            is_admin=user.is_admin,
            require_2fa=user.require_2fa,
            last_login=user.last_login,
            created_at=user.created_at,
            updated_at=user.updated_at,
            company_id=user.company_id,
            company_name=user.company.name if user.company else None,
            roles=user_roles,
            is_deleted=getattr(user, "is_deleted", False),
            deleted_at=getattr(user, "deleted_at", None),
            is_suspended=getattr(user, "is_suspended", False),
            suspended_at=getattr(user, "suspended_at", None),
            suspended_by=getattr(user, "suspended_by", None),
        )
        user_list.append(user_info)

    pages = (total + size - 1) // size
    return UserListResponse(
        users=user_list,
        total=total,
        pages=pages,
        page=page,
        per_page=size,
    )


@router.post(
    API_ROUTES.USERS.ADMIN_USERS,
    response_model=UserInfo,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new user."""

    # Check permissions
    if not (is_super_admin(current_user) or is_company_admin(current_user)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to create users",
        )

    # NEW RESTRICTION 1: Prevent creating system admins
    # System admin role can never be assigned to new users
    if UserRoleEnum.SYSTEM_ADMIN in user_data.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create system admin users. Only one system admin is allowed in the system.",
        )

    # NEW RESTRICTION 2: Only super admin can create company admins
    if UserRoleEnum.ADMIN in user_data.roles and not is_super_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admin can create company admin users.",
        )

    # NEW RESTRICTION 3: Prevent candidates in super admin's company
    # Get super admin's company
    super_admin_company_query = (
        select(User.company_id)
        .join(UserRole)
        .join(Role)
        .where(
            and_(
                Role.name == UserRoleEnum.SYSTEM_ADMIN.value,
                User.is_deleted is False,
            )
        )
        .limit(1)
    )
    super_admin_company_result = await db.execute(super_admin_company_query)
    super_admin_company_id = super_admin_company_result.scalar_one_or_none()

    # If trying to create a candidate in super admin's company, prevent it
    if (
        UserRoleEnum.CANDIDATE in user_data.roles
        and user_data.company_id == super_admin_company_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create candidates in super admin's company.",
        )

    # Company admin can only create users in their company
    if is_company_admin(current_user) and not is_super_admin(current_user):
        if user_data.company_id and user_data.company_id != current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot create users for other companies",
            )
        user_data.company_id = current_user.company_id

        # Company admin role restrictions
        forbidden_roles = [UserRoleEnum.SYSTEM_ADMIN]
        for role in user_data.roles:
            if role in forbidden_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Company admins cannot assign {role.value} role",
                )

        # Limit admin role assignment to prevent privilege escalation
        company_admin_roles = [
            role for role in user_data.roles if role == UserRoleEnum.ADMIN
        ]
        if len(company_admin_roles) > 0:
            # Check if current user is the only company admin
            existing_admin_query = select(func.count(User.id)).where(
                and_(
                    User.company_id == current_user.company_id,
                    User.is_admin is True,
                    User.is_deleted is False,
                    User.id != current_user.id,  # Exclude current user
                )
            )
            existing_admin_result = await db.execute(existing_admin_query)
            other_admin_count = existing_admin_result.scalar() or 0

            if other_admin_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot create another company admin. You are the only company admin.",
                )

    # Check if user already exists
    existing_user = await db.execute(select(User).where(User.email == user_data.email))
    if existing_user.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    # Validate company exists if specified
    if user_data.company_id:
        company = await db.execute(
            select(Company).where(Company.id == user_data.company_id)
        )
        if not company.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Company not found"
            )

    # Generate temporary password
    temp_password = "".join(
        secrets.choice(string.ascii_letters + string.digits) for _ in range(12)
    )
    hashed_password = auth_service.get_password_hash(temp_password)

    # Check if user should be admin based on roles
    is_admin_user = user_data.is_admin or False
    admin_roles = [UserRoleEnum.ADMIN, UserRoleEnum.SYSTEM_ADMIN]
    if any(role in admin_roles for role in user_data.roles):
        is_admin_user = True

    # Check if company already has an admin (prevent duplicate company admins)
    # Exception: Super admin's company can have unlimited admins
    if is_admin_user and user_data.company_id:
        # Super admin's company can have unlimited admins
        if user_data.company_id != super_admin_company_id:
            existing_admin_query = select(func.count(User.id)).where(
                and_(
                    User.company_id == user_data.company_id,
                    User.is_admin is True,
                    User.is_deleted is False,
                )
            )
            existing_admin_result = await db.execute(existing_admin_query)
            existing_admin_count = existing_admin_result.scalar() or 0

            if existing_admin_count > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="This company already has an admin user. Only one admin per company is allowed.",
                )

    # Auto-enable 2FA for admin users
    require_2fa = is_admin_user or user_data.require_2fa or False

    # Create user
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone,
        company_id=user_data.company_id,
        is_admin=is_admin_user,
        require_2fa=require_2fa,
        created_by=current_user.id,  # Track who created this user
        is_active=False,  # User needs to activate account
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Assign roles
    if user_data.roles:
        for role_name in user_data.roles:
            role = await db.execute(select(Role.id).where(Role.name == role_name.value))
            role_id = role.scalar_one_or_none()
            if role_id:
                user_role = UserRole(user_id=new_user.id, role_id=role_id)
                db.add(user_role)

    # Create user settings
    user_settings = UserSettings(user_id=new_user.id)
    db.add(user_settings)

    await db.commit()

    # Auto-connect admin users to super admin
    if is_admin_user:
        try:
            super_admin = await get_super_admin_user(db)
            if super_admin and super_admin.id != new_user.id:
                await user_connection_service.connect_users(
                    db=db,
                    user_id=new_user.id,
                    connected_user_id=super_admin.id,
                    creation_type="automatic",
                    created_by=None,
                )
                logger.info(
                    f"Automatically connected admin user {new_user.email} to super admin {super_admin.email}"
                )
        except Exception as e:
            # Log error but don't fail the user creation
            logger.error(
                f"Error creating automatic connection to super admin for {new_user.email}: {e}"
            )

    # Send activation email
    try:
        activation_token = auth_service.generate_activation_token(new_user.email)
        await email_service.send_activation_email(
            new_user.email,
            new_user.first_name,
            activation_token,
            temp_password,
            new_user.id,
        )
    except Exception as e:
        # Log error but don't fail the user creation
        logger.error(f"Error sending activation email to {new_user.email}: {e}")

    # Return user info
    await db.refresh(new_user)
    return UserInfo(
        id=new_user.id,
        email=new_user.email,
        first_name=new_user.first_name,
        last_name=new_user.last_name,
        full_name=new_user.full_name,
        phone=new_user.phone,
        is_active=new_user.is_active,
        is_admin=new_user.is_admin,
        require_2fa=new_user.require_2fa,
        last_login=new_user.last_login,
        created_at=new_user.created_at,
        updated_at=new_user.updated_at,
        company_id=new_user.company_id,
        roles=[],
        is_deleted=False,
        deleted_at=None,
    )


@router.post(API_ROUTES.ADMIN.USERS_BULK_DELETE)
async def bulk_delete_users(
    operation: BulkUserOperation,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Bulk delete multiple users (logical deletion)."""

    if not operation.user_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No user IDs provided"
        )

    if not (is_super_admin(current_user) or is_company_admin(current_user)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete users",
        )

    # Validate user permissions for each user
    errors = []
    valid_user_ids = []

    for user_id in operation.user_ids:
        if user_id == current_user.id:
            errors.append("Cannot delete your own account")
            continue

        user = await user_crud.user.get(db, user_id)
        if not user:
            errors.append(f"User {user_id} not found")
            continue

        if is_company_admin(current_user) and not is_super_admin(current_user):
            if user.company_id != current_user.company_id:
                errors.append(f"Cannot delete user {user_id} from other company")
                continue

        valid_user_ids.append(user_id)

    deleted_count, delete_errors = await user_crud.user.bulk_delete(
        db, valid_user_ids, current_user.id
    )
    errors.extend(delete_errors)

    return {
        "message": f"Successfully deleted {deleted_count} user(s)",
        "deleted_count": deleted_count,
        "errors": errors,
    }


@router.post(API_ROUTES.ADMIN.USERS_BULK_RESET_PASSWORD)
async def bulk_reset_passwords(
    operation: BulkUserOperation,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Bulk reset passwords for multiple users."""

    if not operation.user_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No user IDs provided"
        )

    # Check permissions
    if not (is_super_admin(current_user) or is_company_admin(current_user)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to reset passwords",
        )

    reset_count = 0
    errors = []
    temp_passwords = {}

    for user_id in operation.user_ids:
        try:
            # Get user
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()

            if not user:
                errors.append(f"User {user_id} not found")
                continue

            # Company admin can only reset passwords for users in their company
            if is_company_admin(current_user) and not is_super_admin(current_user):
                if user.company_id != current_user.company_id:
                    errors.append(
                        f"Cannot reset password for user {user_id} from other company"
                    )
                    continue

            # Generate new temporary password
            temp_password = "".join(
                secrets.choice(string.ascii_letters + string.digits) for _ in range(12)
            )
            hashed_password = auth_service.get_password_hash(temp_password)

            # Update user password
            user.hashed_password = hashed_password
            reset_count += 1
            temp_passwords[user_id] = temp_password

            # Send email if requested
            if operation.send_email:
                try:
                    await email_service.send_password_reset_email(
                        user.email, user.first_name, temp_password
                    )
                except Exception as e:
                    errors.append(f"Failed to send email to user {user_id}: {str(e)}")

        except Exception as e:
            errors.append(f"Error resetting password for user {user_id}: {str(e)}")

    await db.commit()

    return {
        "message": f"Successfully reset passwords for {reset_count} user(s)",
        "reset_count": reset_count,
        "errors": errors,
        "temporary_passwords": temp_passwords if not operation.send_email else None,
    }


@router.post(API_ROUTES.ADMIN.USERS_BULK_RESEND_ACTIVATION)
async def bulk_resend_activation(
    operation: BulkUserOperation,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Bulk resend activation emails to multiple users."""

    if not operation.user_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No user IDs provided"
        )

    # Check permissions
    if not (is_super_admin(current_user) or is_company_admin(current_user)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to resend activation emails",
        )

    sent_count = 0
    errors = []

    for user_id in operation.user_ids:
        try:
            # Get user
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()

            if not user:
                errors.append(f"User {user_id} not found")
                continue

            # Company admin can only resend for users in their company
            if is_company_admin(current_user) and not is_super_admin(current_user):
                if user.company_id != current_user.company_id:
                    errors.append(
                        f"Cannot resend activation for user {user_id} from other company"
                    )
                    continue

            # Check if user is already active
            if user.is_active:
                errors.append(f"User {user_id} is already active")
                continue

            # Generate new temporary password and activation token
            temp_password = "".join(
                secrets.choice(string.ascii_letters + string.digits) for _ in range(12)
            )
            hashed_password = auth_service.get_password_hash(temp_password)
            user.hashed_password = hashed_password

            activation_token = auth_service.generate_activation_token(user.email)
            await email_service.send_activation_email(
                user.email, user.first_name, activation_token, temp_password, user.id
            )
            sent_count += 1

        except Exception as e:
            errors.append(f"Error sending activation email to user {user_id}: {str(e)}")

    return {
        "message": f"Successfully sent activation emails to {sent_count} user(s)",
        "sent_count": sent_count,
        "errors": errors,
    }


@router.post(API_ROUTES.ADMIN.USERS_BULK_SUSPEND)
async def bulk_suspend_users(
    operation: BulkUserOperation,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Bulk suspend multiple users."""

    if not operation.user_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No user IDs provided"
        )

    if not (is_super_admin(current_user) or is_company_admin(current_user)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to suspend users",
        )

    # Validate user permissions
    errors = []
    valid_user_ids = []

    for user_id in operation.user_ids:
        if user_id == current_user.id:
            errors.append("Cannot suspend your own account")
            continue

        user = await user_crud.user.get(db, user_id)
        if not user:
            errors.append(f"User {user_id} not found")
            continue

        if is_company_admin(current_user) and not is_super_admin(current_user):
            if user.company_id != current_user.company_id:
                errors.append(f"Cannot suspend user {user_id} from other company")
                continue

        valid_user_ids.append(user_id)

    suspended_count, suspend_errors = await user_crud.user.bulk_suspend(
        db, valid_user_ids, current_user.id
    )
    errors.extend(suspend_errors)

    return {
        "message": f"Successfully suspended {suspended_count} user(s)",
        "suspended_count": suspended_count,
        "errors": errors,
    }


@router.post(API_ROUTES.ADMIN.USERS_BULK_UNSUSPEND)
async def bulk_unsuspend_users(
    operation: BulkUserOperation,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Bulk unsuspend multiple users."""

    if not operation.user_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No user IDs provided"
        )

    if not (is_super_admin(current_user) or is_company_admin(current_user)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to unsuspend users",
        )

    # Validate user permissions
    errors = []
    valid_user_ids = []

    for user_id in operation.user_ids:
        user = await user_crud.user.get(db, user_id)
        if not user:
            errors.append(f"User {user_id} not found")
            continue

        if is_company_admin(current_user) and not is_super_admin(current_user):
            if user.company_id != current_user.company_id:
                errors.append(f"Cannot unsuspend user {user_id} from other company")
                continue

        valid_user_ids.append(user_id)

    unsuspended_count, unsuspend_errors = await user_crud.user.bulk_unsuspend(
        db, valid_user_ids
    )
    errors.extend(unsuspend_errors)

    return {
        "message": f"Successfully unsuspended {unsuspended_count} user(s)",
        "unsuspended_count": unsuspended_count,
        "errors": errors,
    }


@router.get(API_ROUTES.USERS.ADMIN_USER_BY_ID, response_model=UserInfo)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get specific user details."""

    user = await user_crud.user.get_with_company_and_roles(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Check permissions
    if not (is_super_admin(current_user) or is_company_admin(current_user)):
        if current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to view this user",
            )

    if is_company_admin(current_user) and not is_super_admin(current_user):
        if user.company_id != current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot view users from other companies",
            )

    user_roles = [role.role.name for role in user.user_roles]
    return UserInfo(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        full_name=user.full_name,
        phone=user.phone,
        is_active=user.is_active,
        is_admin=user.is_admin,
        require_2fa=user.require_2fa,
        last_login=user.last_login,
        created_at=user.created_at,
        updated_at=user.updated_at,
        company_id=user.company_id,
        company_name=user.company.name if user.company else None,
        roles=user_roles,
        is_deleted=getattr(user, "is_deleted", False),
        deleted_at=getattr(user, "deleted_at", None),
        is_suspended=getattr(user, "is_suspended", False),
        suspended_at=getattr(user, "suspended_at", None),
        suspended_by=getattr(user, "suspended_by", None),
    )


@router.put(API_ROUTES.USERS.ADMIN_USER_BY_ID, response_model=UserInfo)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update user information."""

    # Get user
    result = await db.execute(
        select(User)
        .options(
            selectinload(User.company),
            selectinload(User.user_roles).selectinload(UserRole.role),
        )
        .where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Check permissions
    if not (is_super_admin(current_user) or is_company_admin(current_user)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update users",
        )

    # NEW RESTRICTION 1: Prevent updating to system admin role
    # System admin role can never be assigned through updates
    if user_data.roles is not None and UserRoleEnum.SYSTEM_ADMIN in user_data.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot assign system admin role. Only one system admin is allowed in the system.",
        )

    # NEW RESTRICTION 2: Only super admin can update users to company admin role
    if user_data.roles is not None and UserRoleEnum.ADMIN in user_data.roles:
        if not is_super_admin(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only super admin can assign company admin role.",
            )

    # NEW RESTRICTION 3: Prevent updating to candidate role in super admin's company
    if user_data.roles is not None and UserRoleEnum.CANDIDATE in user_data.roles:
        # Get super admin's company
        super_admin_company_query = (
            select(User.company_id)
            .join(UserRole)
            .join(Role)
            .where(
                and_(
                    Role.name == UserRoleEnum.SYSTEM_ADMIN.value,
                    User.is_deleted is False,
                )
            )
            .limit(1)
        )
        super_admin_company_result = await db.execute(super_admin_company_query)
        super_admin_company_id = super_admin_company_result.scalar_one_or_none()

        # Check if updating user to candidate in super admin's company
        target_company_id = (
            user_data.company_id
            if user_data.company_id is not None
            else user.company_id
        )
        if target_company_id == super_admin_company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot assign candidate role in super admin's company.",
            )

    # Company admin can only update users from their company
    if is_company_admin(current_user) and not is_super_admin(current_user):
        if user.company_id != current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot update users from other companies",
            )

        # Company admin role restrictions for updates
        if user_data.roles is not None:
            forbidden_roles = [UserRoleEnum.SYSTEM_ADMIN]
            for role in user_data.roles:
                if role in forbidden_roles:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Company admins cannot assign {role.value} role",
                    )

        # Prevent company_id changes by company admins
        if (
            user_data.company_id is not None
            and user_data.company_id != current_user.company_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Company admins cannot move users to other companies",
            )

    # Update user fields
    update_data = user_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if field == "roles":
            # Handle roles separately
            continue
        if hasattr(user, field):
            setattr(user, field, value)

    # Handle role updates
    if user_data.roles is not None:
        # Remove existing roles
        await db.execute(select(UserRole).where(UserRole.user_id == user_id))
        existing_roles = await db.execute(
            select(UserRole).where(UserRole.user_id == user_id)
        )
        for role in existing_roles.scalars().all():
            await db.delete(role)

        # Add new roles
        for role_name in user_data.roles:
            role = await db.execute(select(Role.id).where(Role.name == role_name.value))
            role_id = role.scalar_one_or_none()
            if role_id:
                user_role = UserRole(user_id=user_id, role_id=role_id)
                db.add(user_role)

    await db.commit()
    await db.refresh(user)

    # Return updated user info
    user_roles = [role.role.name for role in user.user_roles]

    return UserInfo(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        full_name=user.full_name,
        phone=user.phone,
        is_active=user.is_active,
        is_admin=user.is_admin,
        require_2fa=user.require_2fa,
        last_login=user.last_login,
        created_at=user.created_at,
        updated_at=user.updated_at,
        company_id=user.company_id,
        company_name=user.company.name if user.company else None,
        roles=user_roles,
        is_deleted=getattr(user, "is_deleted", False),
        deleted_at=getattr(user, "deleted_at", None),
        is_suspended=getattr(user, "is_suspended", False),
        suspended_at=getattr(user, "suspended_at", None),
        suspended_by=getattr(user, "suspended_by", None),
    )


@router.delete(API_ROUTES.USERS.ADMIN_USER_BY_ID)
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Soft delete a user (logical deletion)."""

    user = await user_crud.user.get(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if not (is_super_admin(current_user) or is_company_admin(current_user)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete users",
        )

    if is_company_admin(current_user) and not is_super_admin(current_user):
        if user.company_id != current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete users from other companies",
            )

    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )

    await user_crud.user.soft_delete(db, user_id, current_user.id)
    return {"message": "User deleted successfully"}


@router.post(API_ROUTES.USERS.ADMIN_USER_RESET_PASSWORD)
async def reset_user_password(
    user_id: int,
    reset_data: PasswordResetRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Reset user password and optionally send email."""

    # Get user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Check permissions
    if not (is_super_admin(current_user) or is_company_admin(current_user)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to reset passwords",
        )

    # Company admin can only reset passwords for users in their company
    if is_company_admin(current_user) and not is_super_admin(current_user):
        if user.company_id != current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot reset passwords for users from other companies",
            )

    # Generate new temporary password
    temp_password = "".join(
        secrets.choice(string.ascii_letters + string.digits) for _ in range(12)
    )
    hashed_password = auth_service.get_password_hash(temp_password)

    # Update user password
    user.hashed_password = hashed_password
    await db.commit()

    # Send email if requested
    if reset_data.send_email:
        try:
            await email_service.send_password_reset_email(
                user.email, user.first_name, temp_password
            )
        except Exception as e:
            # Log error but don't fail the operation
            logger.error(f"Error sending password reset email: {e}")

    return {
        "message": "Password reset successfully",
        "temporary_password": temp_password if not reset_data.send_email else None,
    }


@router.post(API_ROUTES.USERS.ADMIN_USER_RESEND_ACTIVATION)
async def resend_activation_email(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Resend activation email to user."""

    # Get user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Check permissions
    if not (is_super_admin(current_user) or is_company_admin(current_user)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to resend activation emails",
        )

    # Company admin can only resend for users in their company
    if is_company_admin(current_user) and not is_super_admin(current_user):
        if user.company_id != current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot resend activation for users from other companies",
            )

    # Check if user is already active
    if user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User is already active"
        )

    # Generate new temporary password and activation token
    try:
        temp_password = "".join(
            secrets.choice(string.ascii_letters + string.digits) for _ in range(12)
        )
        hashed_password = auth_service.get_password_hash(temp_password)
        user.hashed_password = hashed_password
        await db.commit()

        activation_token = auth_service.generate_activation_token(user.email)
        await email_service.send_activation_email(
            user.email, user.first_name, activation_token, temp_password, user.id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send activation email: {str(e)}",
        ) from e

    return {"message": "Activation email sent successfully"}


@router.post(API_ROUTES.USERS.ADMIN_USER_SUSPEND)
async def suspend_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Suspend a user."""

    user = await user_crud.user.get(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if not (is_super_admin(current_user) or is_company_admin(current_user)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to suspend users",
        )

    if is_company_admin(current_user) and not is_super_admin(current_user):
        if user.company_id != current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot suspend users from other companies",
            )

    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot suspend your own account",
        )

    if user.is_suspended:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User is already suspended"
        )

    await user_crud.user.suspend_user(db, user_id, current_user.id)
    return {"message": "User suspended successfully", "is_suspended": True}


@router.post(API_ROUTES.USERS.ADMIN_USER_UNSUSPEND)
async def unsuspend_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Unsuspend a user."""

    user = await user_crud.user.get(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if not (is_super_admin(current_user) or is_company_admin(current_user)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to unsuspend users",
        )

    if is_company_admin(current_user) and not is_super_admin(current_user):
        if user.company_id != current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot unsuspend users from other companies",
            )

    if not user.is_suspended:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User is not suspended"
        )

    await user_crud.user.unsuspend_user(db, user_id)
    return {"message": "User unsuspended successfully", "is_suspended": False}
