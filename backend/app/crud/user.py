from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models import User, UserRole
from app.models.company import Company
from app.models.role import Role
from app.schemas.user import UserCreate, UserUpdate
from app.utils.constants import UserRole as UserRoleEnum
from app.utils.datetime_utils import get_utc_now


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """User CRUD operations."""

    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        """Get user by email."""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_with_company_and_roles(
        self, db: AsyncSession, user_id: int
    ) -> User | None:
        """Get user with company and roles loaded."""
        result = await db.execute(
            select(User)
            .options(
                selectinload(User.company),
                selectinload(User.user_roles).selectinload(UserRole.role),
            )
            .where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_users_paginated(
        self,
        db: AsyncSession,
        page: int = 1,
        size: int = 20,
        search: str | None = None,
        company_id: int | None = None,
        is_active: bool | None = None,
        is_admin: bool | None = None,
        is_suspended: bool | None = None,
        require_2fa: bool | None = None,
        role: UserRoleEnum | None = None,
        include_deleted: bool = False,
        current_user_id: int | None = None,
    ):
        """Get paginated list of users with filters."""
        query_conditions = []

        # Handle logical deletion
        if include_deleted:
            # When include_deleted is True, show all users (no filter)
            pass
        else:
            # When include_deleted is False (default), show only non-deleted users
            query_conditions.append(User.is_deleted == False)

        # Apply filters
        if company_id is not None:
            query_conditions.append(User.company_id == company_id)

        if search:
            search_term = f"%{search}%"
            query_conditions.append(
                or_(
                    User.first_name.ilike(search_term),
                    User.last_name.ilike(search_term),
                    User.email.ilike(search_term),
                    Company.name.ilike(search_term),
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

        # Build base query with join for company search
        base_query = (
            select(User)
            .outerjoin(Company, User.company_id == Company.id)
            .options(
                selectinload(User.company),
                selectinload(User.user_roles).selectinload(UserRole.role),
            )
        )

        # Handle role filter
        if role:
            role_id_query = select(Role.id).where(Role.name == role.value)
            role_subquery = select(UserRole.user_id).where(
                UserRole.role_id.in_(role_id_query)
            )
            base_query = base_query.where(User.id.in_(role_subquery))

        # Apply all accumulated query conditions
        if query_conditions:
            base_query = base_query.where(and_(*query_conditions))

        # Exclude current user if specified
        if current_user_id:
            base_query = base_query.where(User.id != current_user_id)

        # Get total count
        count_query = select(func.count()).select_from(base_query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Apply pagination
        offset = (page - 1) * size
        users_query = (
            base_query.offset(offset).limit(size).order_by(User.created_at.desc())
        )

        result = await db.execute(users_query)
        users = result.scalars().all()

        return users, total

    async def check_company_admin_exists(
        self, db: AsyncSession, company_id: int
    ) -> int:
        """Check if company already has admin users."""
        admin_query = select(func.count(User.id)).where(
            and_(
                User.company_id == company_id,
                User.is_admin is True,
                User.is_deleted is False,
            )
        )
        result = await db.execute(admin_query)
        return result.scalar() or 0

    async def bulk_delete(
        self, db: AsyncSession, user_ids: list[int], deleted_by: int
    ) -> tuple[int, list[str]]:
        """Soft delete multiple users."""
        deleted_count = 0
        errors = []

        for user_id in user_ids:
            try:
                user = await self.get(db, user_id)
                if not user:
                    errors.append(f"User {user_id} not found")
                    continue

                user.is_deleted = True
                user.deleted_at = get_utc_now()
                user.deleted_by = deleted_by
                user.is_active = False
                deleted_count += 1

            except Exception as e:
                errors.append(f"Error deleting user {user_id}: {str(e)}")

        await db.commit()
        return deleted_count, errors

    async def bulk_suspend(
        self, db: AsyncSession, user_ids: list[int], suspended_by: int
    ) -> tuple[int, list[str]]:
        """Suspend multiple users."""
        suspended_count = 0
        errors = []

        for user_id in user_ids:
            try:
                user = await self.get(db, user_id)
                if not user:
                    errors.append(f"User {user_id} not found")
                    continue

                if not user.is_suspended:
                    user.is_suspended = True
                    user.suspended_at = get_utc_now()
                    user.suspended_by = suspended_by
                    suspended_count += 1

            except Exception as e:
                errors.append(f"Error suspending user {user_id}: {str(e)}")

        await db.commit()
        return suspended_count, errors

    async def bulk_unsuspend(
        self, db: AsyncSession, user_ids: list[int]
    ) -> tuple[int, list[str]]:
        """Unsuspend multiple users."""
        unsuspended_count = 0
        errors = []

        for user_id in user_ids:
            try:
                user = await self.get(db, user_id)
                if not user:
                    errors.append(f"User {user_id} not found")
                    continue

                if user.is_suspended:
                    user.is_suspended = False
                    user.suspended_at = None
                    user.suspended_by = None
                    unsuspended_count += 1

            except Exception as e:
                errors.append(f"Error unsuspending user {user_id}: {str(e)}")

        await db.commit()
        return unsuspended_count, errors

    async def assign_roles(
        self, db: AsyncSession, user_id: int, roles: list[UserRoleEnum]
    ):
        """Assign roles to user."""
        # Remove existing roles
        existing_roles_query = select(UserRole).where(UserRole.user_id == user_id)
        existing_roles = await db.execute(existing_roles_query)
        for role in existing_roles.scalars().all():
            await db.delete(role)

        # Add new roles
        for role_name in roles:
            role_query = select(Role.id).where(Role.name == role_name.value)
            role_result = await db.execute(role_query)
            role_id = role_result.scalar_one_or_none()
            if role_id:
                user_role = UserRole(user_id=user_id, role_id=role_id)
                db.add(user_role)

        await db.commit()

    async def soft_delete(self, db: AsyncSession, user_id: int, deleted_by: int):
        """Soft delete a user."""
        user = await self.get(db, user_id)
        if user:
            user.is_deleted = True
            user.deleted_at = get_utc_now()
            user.deleted_by = deleted_by
            user.is_active = False
            await db.commit()
        return user

    async def suspend_user(self, db: AsyncSession, user_id: int, suspended_by: int):
        """Suspend a user."""
        user = await self.get(db, user_id)
        if user and not user.is_suspended:
            user.is_suspended = True
            user.suspended_at = get_utc_now()
            user.suspended_by = suspended_by
            await db.commit()
        return user

    async def unsuspend_user(self, db: AsyncSession, user_id: int):
        """Unsuspend a user."""
        user = await self.get(db, user_id)
        if user and user.is_suspended:
            user.is_suspended = False
            user.suspended_at = None
            user.suspended_by = None
            await db.commit()
        return user


# Create the CRUD instance
user = CRUDUser(User)
