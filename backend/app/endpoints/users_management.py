import secrets
import string
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import and_, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies import get_current_active_user
from app.models import Company, User, UserRole, UserSettings
from app.models.role import Role
from app.services.auth_service import auth_service
from app.services.email_service import email_service
from app.utils.constants import UserRole as UserRoleEnum
from app.utils.permissions import is_company_admin, is_super_admin

router = APIRouter()


class UserCreate(BaseModel):
    email: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    company_id: Optional[int] = None
    roles: List[UserRoleEnum] = []
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
    roles: Optional[List[UserRoleEnum]] = None


class UserFilters(BaseModel):
    page: int = 1
    size: int = 20
    search: Optional[str] = None
    company_id: Optional[int] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    is_suspended: Optional[bool] = None
    require_2fa: Optional[bool] = None
    role: Optional[UserRoleEnum] = None


class UserInfo(BaseModel):
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

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    users: List[UserInfo]
    total: int
    pages: int
    page: int
    size: int


class PasswordResetRequest(BaseModel):
    user_id: int
    send_email: bool = True


class ResendActivationRequest(BaseModel):
    user_id: int


class BulkUserOperation(BaseModel):
    user_ids: List[int]
    send_email: bool = True


@router.get("/users", response_model=UserListResponse)
async def get_users(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    company_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(None),
    is_admin: Optional[bool] = Query(None),
    is_suspended: Optional[bool] = Query(None),
    require_2fa: Optional[bool] = Query(None),
    role: Optional[UserRoleEnum] = Query(None),
    include_deleted: bool = Query(False),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get paginated list of users with filters."""

    # Build query conditions based on user permissions
    query_conditions = []

    # Super admin can see all users, company admin can only see their company users
    if is_super_admin(current_user):
        # Super admin can filter by company or see all
        if company_id is not None:
            query_conditions.append(User.company_id == company_id)
    elif is_company_admin(current_user):
        # Company admin can only see users from their company
        query_conditions.append(User.company_id == current_user.company_id)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view users"
        )

    # Handle logical deletion
    if not include_deleted:
        query_conditions.append(User.is_deleted == False)

    # Apply filters
    if search:
        search_term = f"%{search}%"
        query_conditions.append(
            or_(
                User.first_name.ilike(search_term),
                User.last_name.ilike(search_term),
                User.email.ilike(search_term),
            )
        )

    if is_active is not None:
        query_conditions.append(User.is_active == is_active)

    if is_admin is not None:
        query_conditions.append(User.is_admin == is_admin)

    if is_suspended is not None:
        query_conditions.append(User.is_suspended == is_suspended)

    if require_2fa is not None:
        query_conditions.append(User.require_2fa == require_2fa)

    # Build base query
    base_query = select(User).options(
        selectinload(User.company),
        selectinload(User.user_roles).selectinload(UserRole.role)
    )

    # Handle role filter (requires join with UserRole)
    if role:
        # First get the role ID for the role name
        role_id_query = select(Role.id).where(Role.name == role.value)
        role_subquery = select(UserRole.user_id).where(
            UserRole.role_id.in_(role_id_query)
        )
        base_query = base_query.where(User.id.in_(role_subquery))

    # Apply all accumulated query conditions
    if query_conditions:
        base_query = base_query.where(and_(*query_conditions))

    # Always exclude the currently logged-in user from the list (applied after all other conditions)
    base_query = base_query.where(User.id != current_user.id)

    # Get total count
    count_query = select(func.count()).select_from(base_query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination
    offset = (page - 1) * size
    users_query = base_query.offset(offset).limit(size).order_by(User.created_at.desc())

    result = await db.execute(users_query)
    users = result.scalars().all()

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
            is_deleted=getattr(user, 'is_deleted', False),
            deleted_at=getattr(user, 'deleted_at', None),
            is_suspended=getattr(user, 'is_suspended', False),
            suspended_at=getattr(user, 'suspended_at', None),
            suspended_by=getattr(user, 'suspended_by', None),
        )
        user_list.append(user_info)

    pages = (total + size - 1) // size

    return UserListResponse(
        users=user_list,
        total=total,
        pages=pages,
        page=page,
        size=size,
    )


@router.post("/users", response_model=UserInfo)
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
            detail="Not enough permissions to create users"
        )

    # Company admin can only create users in their company
    if is_company_admin(current_user) and not is_super_admin(current_user):
        if user_data.company_id and user_data.company_id != current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot create users for other companies"
            )
        user_data.company_id = current_user.company_id

    # Check if user already exists
    existing_user = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    if existing_user.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    # Validate company exists if specified
    if user_data.company_id:
        company = await db.execute(
            select(Company).where(Company.id == user_data.company_id)
        )
        if not company.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )

    # Generate temporary password
    temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
    hashed_password = auth_service.get_password_hash(temp_password)

    # Check if user should be admin based on roles
    is_admin_user = user_data.is_admin or False
    admin_roles = [UserRoleEnum.COMPANY_ADMIN, UserRoleEnum.SUPER_ADMIN]
    if any(role in admin_roles for role in user_data.roles):
        is_admin_user = True

    # Check if company already has an admin (prevent duplicate company admins)
    if is_admin_user and user_data.company_id:
        existing_admin_query = select(func.count(User.id)).where(
            and_(
                User.company_id == user_data.company_id,
                User.is_admin == True,
                User.is_deleted == False
            )
        )
        existing_admin_result = await db.execute(existing_admin_query)
        existing_admin_count = existing_admin_result.scalar() or 0

        if existing_admin_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This company already has an admin user. Only one admin per company is allowed."
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
        is_active=False,  # User needs to activate account
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Assign roles
    if user_data.roles:
        for role_name in user_data.roles:
            role = await db.execute(
                select(Role.id).where(Role.name == role_name.value)
            )
            role_id = role.scalar_one_or_none()
            if role_id:
                user_role = UserRole(user_id=new_user.id, role_id=role_id)
                db.add(user_role)

    # Create user settings
    user_settings = UserSettings(user_id=new_user.id)
    db.add(user_settings)

    await db.commit()

    # Send activation email
    try:
        activation_token = auth_service.generate_activation_token(new_user.email)
        await email_service.send_activation_email(
            new_user.email,
            new_user.first_name,
            activation_token,
            temp_password,
            new_user.id
        )
    except Exception as e:
        # Log error but don't fail the user creation
        print(f"Failed to send activation email: {e}")

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


@router.post("/users/bulk/delete")
async def bulk_delete_users(
    operation: BulkUserOperation,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Bulk delete multiple users (logical deletion)."""

    if not operation.user_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No user IDs provided"
        )

    # Check permissions
    if not (is_super_admin(current_user) or is_company_admin(current_user)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete users"
        )

    deleted_count = 0
    errors = []

    for user_id in operation.user_ids:
        try:
            # Get user
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()

            if not user:
                errors.append(f"User {user_id} not found")
                continue

            # Company admin can only delete users from their company
            if is_company_admin(current_user) and not is_super_admin(current_user):
                if user.company_id != current_user.company_id:
                    errors.append(f"Cannot delete user {user_id} from other company")
                    continue

            # Prevent self-deletion
            if user_id == current_user.id:
                errors.append(f"Cannot delete your own account")
                continue

            # Soft delete
            user.is_deleted = True
            user.deleted_at = datetime.utcnow()
            user.deleted_by = current_user.id
            user.is_active = False
            deleted_count += 1

        except Exception as e:
            errors.append(f"Error deleting user {user_id}: {str(e)}")

    await db.commit()

    return {
        "message": f"Successfully deleted {deleted_count} user(s)",
        "deleted_count": deleted_count,
        "errors": errors
    }


@router.post("/users/bulk/reset-password")
async def bulk_reset_passwords(
    operation: BulkUserOperation,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Bulk reset passwords for multiple users."""

    if not operation.user_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No user IDs provided"
        )

    # Check permissions
    if not (is_super_admin(current_user) or is_company_admin(current_user)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to reset passwords"
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
                    errors.append(f"Cannot reset password for user {user_id} from other company")
                    continue

            # Generate new temporary password
            temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
            hashed_password = auth_service.get_password_hash(temp_password)

            # Update user password
            user.hashed_password = hashed_password
            reset_count += 1
            temp_passwords[user_id] = temp_password

            # Send email if requested
            if operation.send_email:
                try:
                    await email_service.send_password_reset_email(
                        user.email,
                        user.first_name,
                        temp_password
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
        "temporary_passwords": temp_passwords if not operation.send_email else None
    }


@router.post("/users/bulk/resend-activation")
async def bulk_resend_activation(
    operation: BulkUserOperation,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Bulk resend activation emails to multiple users."""

    if not operation.user_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No user IDs provided"
        )

    # Check permissions
    if not (is_super_admin(current_user) or is_company_admin(current_user)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to resend activation emails"
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
                    errors.append(f"Cannot resend activation for user {user_id} from other company")
                    continue

            # Check if user is already active
            if user.is_active:
                errors.append(f"User {user_id} is already active")
                continue

            # Generate new temporary password and activation token
            temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
            hashed_password = auth_service.get_password_hash(temp_password)
            user.hashed_password = hashed_password

            activation_token = auth_service.generate_activation_token(user.email)
            await email_service.send_activation_email(
                user.email,
                user.first_name,
                activation_token,
                temp_password,
                user.id
            )
            sent_count += 1

        except Exception as e:
            errors.append(f"Error sending activation email to user {user_id}: {str(e)}")

    return {
        "message": f"Successfully sent activation emails to {sent_count} user(s)",
        "sent_count": sent_count,
        "errors": errors
    }


@router.post("/users/bulk/suspend")
async def bulk_suspend_users(
    operation: BulkUserOperation,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Bulk suspend multiple users."""

    if not operation.user_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No user IDs provided"
        )

    # Check permissions - only super admin and company admin can suspend users
    if not (is_super_admin(current_user) or is_company_admin(current_user)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to suspend users"
        )

    suspended_count = 0
    errors = []

    for user_id in operation.user_ids:
        try:
            # Get user
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()

            if not user:
                errors.append(f"User {user_id} not found")
                continue

            # Company admin can only suspend users in their company
            if is_company_admin(current_user) and not is_super_admin(current_user):
                if user.company_id != current_user.company_id:
                    errors.append(f"Cannot suspend user {user_id} from other company")
                    continue

            # Prevent self-suspension
            if user_id == current_user.id:
                errors.append(f"Cannot suspend your own account")
                continue

            # Suspend user only if not already suspended
            if not user.is_suspended:
                user.is_suspended = True
                user.suspended_at = datetime.utcnow()
                user.suspended_by = current_user.id
                suspended_count += 1

        except Exception as e:
            errors.append(f"Error suspending user {user_id}: {str(e)}")

    await db.commit()

    return {
        "message": f"Successfully suspended {suspended_count} user(s)",
        "suspended_count": suspended_count,
        "errors": errors
    }


@router.post("/users/bulk/unsuspend")
async def bulk_unsuspend_users(
    operation: BulkUserOperation,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Bulk unsuspend multiple users."""

    if not operation.user_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No user IDs provided"
        )

    # Check permissions - only super admin and company admin can unsuspend users
    if not (is_super_admin(current_user) or is_company_admin(current_user)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to unsuspend users"
        )

    unsuspended_count = 0
    errors = []

    for user_id in operation.user_ids:
        try:
            # Get user
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()

            if not user:
                errors.append(f"User {user_id} not found")
                continue

            # Company admin can only unsuspend users in their company
            if is_company_admin(current_user) and not is_super_admin(current_user):
                if user.company_id != current_user.company_id:
                    errors.append(f"Cannot unsuspend user {user_id} from other company")
                    continue

            # Unsuspend user only if currently suspended
            if user.is_suspended:
                user.is_suspended = False
                user.suspended_at = None
                user.suspended_by = None
                unsuspended_count += 1

        except Exception as e:
            errors.append(f"Error unsuspending user {user_id}: {str(e)}")

    await db.commit()

    return {
        "message": f"Successfully unsuspended {unsuspended_count} user(s)",
        "unsuspended_count": unsuspended_count,
        "errors": errors
    }


@router.get("/users/{user_id}", response_model=UserInfo)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get specific user details."""

    # Get user with relationships
    result = await db.execute(
        select(User).options(
            selectinload(User.company),
            selectinload(User.user_roles).selectinload(UserRole.role)
        ).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check permissions
    if not (is_super_admin(current_user) or is_company_admin(current_user)):
        if current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to view this user"
            )

    # Company admin can only view users from their company
    if is_company_admin(current_user) and not is_super_admin(current_user):
        if user.company_id != current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot view users from other companies"
            )

    # Format response
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
        is_deleted=getattr(user, 'is_deleted', False),
        deleted_at=getattr(user, 'deleted_at', None),
        is_suspended=getattr(user, 'is_suspended', False),
        suspended_at=getattr(user, 'suspended_at', None),
        suspended_by=getattr(user, 'suspended_by', None),
    )


@router.put("/users/{user_id}", response_model=UserInfo)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update user information."""

    # Get user
    result = await db.execute(
        select(User).options(
            selectinload(User.company),
            selectinload(User.user_roles).selectinload(UserRole.role)
        ).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check permissions
    if not (is_super_admin(current_user) or is_company_admin(current_user)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update users"
        )

    # Company admin can only update users from their company
    if is_company_admin(current_user) and not is_super_admin(current_user):
        if user.company_id != current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot update users from other companies"
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
        await db.execute(
            select(UserRole).where(UserRole.user_id == user_id)
        )
        existing_roles = await db.execute(
            select(UserRole).where(UserRole.user_id == user_id)
        )
        for role in existing_roles.scalars().all():
            await db.delete(role)

        # Add new roles
        for role_name in user_data.roles:
            role = await db.execute(
                select(Role.id).where(Role.name == role_name.value)
            )
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
        is_deleted=getattr(user, 'is_deleted', False),
        deleted_at=getattr(user, 'deleted_at', None),
        is_suspended=getattr(user, 'is_suspended', False),
        suspended_at=getattr(user, 'suspended_at', None),
        suspended_by=getattr(user, 'suspended_by', None),
    )


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Soft delete a user (logical deletion)."""

    # Get user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check permissions
    if not (is_super_admin(current_user) or is_company_admin(current_user)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete users"
        )

    # Company admin can only delete users from their company
    if is_company_admin(current_user) and not is_super_admin(current_user):
        if user.company_id != current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete users from other companies"
            )

    # Prevent self-deletion
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )

    # Soft delete (logical deletion)
    user.is_deleted = True
    user.deleted_at = datetime.utcnow()
    user.deleted_by = current_user.id
    user.is_active = False  # Also deactivate

    await db.commit()

    return {"message": "User deleted successfully"}


@router.post("/users/{user_id}/reset-password")
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check permissions
    if not (is_super_admin(current_user) or is_company_admin(current_user)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to reset passwords"
        )

    # Company admin can only reset passwords for users in their company
    if is_company_admin(current_user) and not is_super_admin(current_user):
        if user.company_id != current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot reset passwords for users from other companies"
            )

    # Generate new temporary password
    temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
    hashed_password = auth_service.get_password_hash(temp_password)

    # Update user password
    user.hashed_password = hashed_password
    await db.commit()

    # Send email if requested
    if reset_data.send_email:
        try:
            await email_service.send_password_reset_email(
                user.email,
                user.first_name,
                temp_password
            )
        except Exception as e:
            # Log error but don't fail the operation
            print(f"Failed to send password reset email: {e}")

    return {
        "message": "Password reset successfully",
        "temporary_password": temp_password if not reset_data.send_email else None
    }


@router.post("/users/{user_id}/resend-activation")
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check permissions
    if not (is_super_admin(current_user) or is_company_admin(current_user)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to resend activation emails"
        )

    # Company admin can only resend for users in their company
    if is_company_admin(current_user) and not is_super_admin(current_user):
        if user.company_id != current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot resend activation for users from other companies"
            )

    # Check if user is already active
    if user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already active"
        )

    # Generate new temporary password and activation token
    try:
        temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
        hashed_password = auth_service.get_password_hash(temp_password)
        user.hashed_password = hashed_password
        await db.commit()

        activation_token = auth_service.generate_activation_token(user.email)
        await email_service.send_activation_email(
            user.email,
            user.first_name,
            activation_token,
            temp_password,
            user.id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send activation email: {str(e)}"
        )

    return {"message": "Activation email sent successfully"}


@router.post("/users/{user_id}/suspend")
async def suspend_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Suspend a user."""

    # Get user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check permissions - only super admin and company admin can suspend users
    if not (is_super_admin(current_user) or is_company_admin(current_user)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to suspend users"
        )

    # Company admin can only suspend users in their company
    if is_company_admin(current_user) and not is_super_admin(current_user):
        if user.company_id != current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot suspend users from other companies"
            )

    # Prevent self-suspension
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot suspend your own account"
        )

    # Check if user is already suspended
    if user.is_suspended:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already suspended"
        )

    # Suspend user
    user.is_suspended = True
    user.suspended_at = datetime.utcnow()
    user.suspended_by = current_user.id
    await db.commit()

    return {"message": "User suspended successfully", "is_suspended": user.is_suspended}


@router.post("/users/{user_id}/unsuspend")
async def unsuspend_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Unsuspend a user."""

    # Get user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check permissions - only super admin and company admin can unsuspend users
    if not (is_super_admin(current_user) or is_company_admin(current_user)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to unsuspend users"
        )

    # Company admin can only unsuspend users in their company
    if is_company_admin(current_user) and not is_super_admin(current_user):
        if user.company_id != current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot unsuspend users from other companies"
            )

    # Check if user is not suspended
    if not user.is_suspended:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not suspended"
        )

    # Unsuspend user
    user.is_suspended = False
    user.suspended_at = None
    user.suspended_by = None
    await db.commit()

    return {"message": "User unsuspended successfully", "is_suspended": user.is_suspended}