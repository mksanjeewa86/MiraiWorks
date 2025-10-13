"""CRUD operations for privacy settings - Section-specific profile visibility controls"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.privacy_settings import PrivacySettings
from app.schemas.privacy_settings import PrivacySettingsUpdate


class CRUDPrivacySettings:
    """
    CRUD operations for privacy settings.

    Supports section-specific privacy controls on profile pages,
    allowing users to toggle visibility of individual profile sections.
    """

    async def get_by_user(
        self, db: AsyncSession, user_id: int
    ) -> Optional[PrivacySettings]:
        """Get privacy settings by user ID"""
        result = await db.execute(
            select(PrivacySettings).where(PrivacySettings.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create_for_user(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> PrivacySettings:
        """Create default privacy settings for a user"""
        db_obj = PrivacySettings(user_id=user_id)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update_by_user(
        self, db: AsyncSession, user_id: int, obj_in: PrivacySettingsUpdate
    ) -> Optional[PrivacySettings]:
        """
        Update privacy settings for a user (supports partial updates).

        This allows section-specific updates where only changed fields are provided.
        Example: {"show_work_experience": false} updates only that field.
        """
        from app.utils.datetime_utils import get_utc_now

        db_obj = await self.get_by_user(db, user_id=user_id)
        if not db_obj:
            return None

        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        # Explicitly set updated_at to ensure it's updated
        db_obj.updated_at = get_utc_now()

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_or_create(
        self, db: AsyncSession, user_id: int
    ) -> PrivacySettings:
        """Get privacy settings or create with defaults if not exists"""
        db_obj = await self.get_by_user(db, user_id=user_id)
        if db_obj:
            return db_obj

        return await self.create_for_user(db, user_id=user_id)


# Create a singleton instance
privacy_settings = CRUDPrivacySettings()
