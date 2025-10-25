"""
CRUD operations for SystemUpdate model.
"""

from typing import Any

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.crud.base import CRUDBase
from app.models.system_update import SystemUpdate


class CRUDSystemUpdate(CRUDBase[SystemUpdate, dict, dict]):
    """CRUD operations for system updates."""

    async def get_all_active(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        include_inactive: bool = False,
    ) -> list[SystemUpdate]:
        """
        Get all system updates, ordered by creation date (newest first).

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_inactive: Whether to include inactive updates

        Returns:
            List of system updates
        """
        query = select(SystemUpdate).order_by(desc(SystemUpdate.created_at))

        if not include_inactive:
            query = query.where(SystemUpdate.is_active is True)

        query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_with_creator(
        self, db: AsyncSession, update_id: int
    ) -> SystemUpdate | None:
        """
        Get a system update with creator information loaded.

        Args:
            db: Database session
            update_id: ID of the system update

        Returns:
            SystemUpdate with creator loaded, or None if not found
        """
        query = (
            select(SystemUpdate)
            .options(joinedload(SystemUpdate.created_by))
            .where(SystemUpdate.id == update_id)
        )

        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_tags(
        self,
        db: AsyncSession,
        tags: list[str],
        skip: int = 0,
        limit: int = 100,
        include_inactive: bool = False,
    ) -> list[SystemUpdate]:
        """
        Get system updates filtered by tags.

        Args:
            db: Database session
            tags: List of tags to filter by (OR operation)
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_inactive: Whether to include inactive updates

        Returns:
            List of system updates matching any of the provided tags
        """
        query = select(SystemUpdate).order_by(desc(SystemUpdate.created_at))

        if not include_inactive:
            query = query.where(SystemUpdate.is_active is True)

        # Filter by tags - match if any tag in the list matches
        if tags:
            # Using JSON contains for PostgreSQL/SQLite compatibility
            tag_filters = []
            for tag in tags:
                tag_filters.append(SystemUpdate.tags.contains([tag]))

            from sqlalchemy import or_

            query = query.where(or_(*tag_filters))

        query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        return list(result.scalars().all())

    async def create_with_creator(
        self, db: AsyncSession, obj_in: dict[str, Any], creator_id: int
    ) -> SystemUpdate:
        """
        Create a new system update with creator ID.

        Args:
            db: Database session
            obj_in: System update data
            creator_id: ID of the user creating the update

        Returns:
            Created system update
        """
        obj_in["created_by_id"] = creator_id
        return await self.create(db, obj_in=obj_in)

    async def deactivate(self, db: AsyncSession, update_id: int) -> SystemUpdate | None:
        """
        Deactivate a system update (soft delete).

        Args:
            db: Database session
            update_id: ID of the update to deactivate

        Returns:
            Updated system update, or None if not found
        """
        update = await self.get(db, id=update_id)
        if update:
            return await self.update(db, db_obj=update, obj_in={"is_active": False})
        return None

    async def activate(self, db: AsyncSession, update_id: int) -> SystemUpdate | None:
        """
        Activate a previously deactivated system update.

        Args:
            db: Database session
            update_id: ID of the update to activate

        Returns:
            Updated system update, or None if not found
        """
        update = await self.get(db, id=update_id)
        if update:
            return await self.update(db, db_obj=update, obj_in={"is_active": True})
        return None


# Create singleton instance
system_update = CRUDSystemUpdate(SystemUpdate)
