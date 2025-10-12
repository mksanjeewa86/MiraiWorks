"""CRUD operations for privacy settings"""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.privacy_settings import PrivacySettings
from app.schemas.privacy_settings import PrivacySettingsCreate, PrivacySettingsUpdate


class CRUDPrivacySettings:
    """CRUD operations for privacy settings"""

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
        obj_in: Optional[PrivacySettingsCreate] = None,
    ) -> PrivacySettings:
        """Create privacy settings for a user with defaults"""
        data = obj_in.model_dump() if obj_in else {}
        data["user_id"] = user_id

        db_obj = PrivacySettings(**data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update_by_user(
        self, db: AsyncSession, user_id: int, obj_in: PrivacySettingsUpdate
    ) -> Optional[PrivacySettings]:
        """Update privacy settings for a user"""
        db_obj = await self.get_by_user(db, user_id=user_id)
        if not db_obj:
            return None

        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

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

    async def delete_by_user(self, db: AsyncSession, user_id: int) -> bool:
        """Delete privacy settings for a user"""
        db_obj = await self.get_by_user(db, user_id=user_id)
        if not db_obj:
            return False

        await db.delete(db_obj)
        await db.commit()
        return True


# Create a singleton instance
privacy_settings = CRUDPrivacySettings()
