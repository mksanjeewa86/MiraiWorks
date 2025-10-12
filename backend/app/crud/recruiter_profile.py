"""CRUD operations for recruiter profiles"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.crud.base import CRUDBase
from app.models.recruiter_profile import RecruiterProfile
from app.schemas.recruiter_profile import RecruiterProfileCreate, RecruiterProfileUpdate


class CRUDRecruiterProfile(CRUDBase[RecruiterProfile, RecruiterProfileCreate, RecruiterProfileUpdate]):
    """CRUD operations for recruiter profiles"""

    async def get_by_user(
        self, db: AsyncSession, *, user_id: int
    ) -> Optional[RecruiterProfile]:
        """Get recruiter profile by user ID"""
        result = await db.execute(
            select(RecruiterProfile).where(RecruiterProfile.user_id == user_id)
        )
        return result.scalars().first()

    async def create_for_user(
        self, db: AsyncSession, *, obj_in: RecruiterProfileCreate, user_id: int
    ) -> RecruiterProfile:
        """Create recruiter profile for a specific user"""
        db_obj = RecruiterProfile(
            user_id=user_id,
            **obj_in.model_dump()
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update_by_user(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        obj_in: RecruiterProfileUpdate
    ) -> Optional[RecruiterProfile]:
        """Update recruiter profile for a specific user"""
        db_obj = await self.get_by_user(db, user_id=user_id)
        if not db_obj:
            return None

        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete_by_user(
        self, db: AsyncSession, *, user_id: int
    ) -> bool:
        """Delete recruiter profile for a specific user"""
        db_obj = await self.get_by_user(db, user_id=user_id)
        if not db_obj:
            return False

        await db.delete(db_obj)
        await db.commit()
        return True


recruiter_profile = CRUDRecruiterProfile(RecruiterProfile)
