"""CRUD operations for company follows."""

from typing import List
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.company_follow import CompanyFollow
from app.schemas.company_follow import CompanyFollowCreate, CompanyFollowUpdate


class CRUDCompanyFollow(CRUDBase[CompanyFollow, CompanyFollowCreate, CompanyFollowUpdate]):
    """CRUD operations for company follows."""

    async def get_by_candidate_and_company(
        self, 
        db: AsyncSession, 
        candidate_id: int, 
        company_id: int
    ) -> CompanyFollow | None:
        """Get a follow relationship by candidate and company IDs."""
        result = await db.execute(
            select(CompanyFollow).where(
                and_(
                    CompanyFollow.candidate_id == candidate_id,
                    CompanyFollow.company_id == company_id
                )
            )
        )
        return result.scalars().first()

    async def get_followed_companies_by_candidate(
        self, 
        db: AsyncSession, 
        candidate_id: int, 
        active_only: bool = True
    ) -> List[CompanyFollow]:
        """Get all companies followed by a candidate."""
        query = select(CompanyFollow).options(
            selectinload(CompanyFollow.company)
        ).where(CompanyFollow.candidate_id == candidate_id)
        
        if active_only:
            query = query.where(CompanyFollow.is_active == True)
            
        result = await db.execute(query)
        return result.scalars().all()

    async def get_company_followers(
        self, 
        db: AsyncSession, 
        company_id: int, 
        active_only: bool = True
    ) -> List[CompanyFollow]:
        """Get all followers of a company."""
        query = select(CompanyFollow).options(
            selectinload(CompanyFollow.candidate)
        ).where(CompanyFollow.company_id == company_id)
        
        if active_only:
            query = query.where(CompanyFollow.is_active == True)
            
        result = await db.execute(query)
        return result.scalars().all()

    async def follow_company(
        self, 
        db: AsyncSession, 
        candidate_id: int, 
        company_id: int,
        follow_data: CompanyFollowCreate
    ) -> CompanyFollow:
        """Create or reactivate a company follow."""
        # Check if follow relationship already exists
        existing_follow = await self.get_by_candidate_and_company(
            db, candidate_id, company_id
        )
        
        if existing_follow:
            if not existing_follow.is_active:
                # Reactivate the follow
                existing_follow.refollow()
                # Update preferences
                for key, value in follow_data.dict(exclude={"company_id"}).items():
                    setattr(existing_follow, key, value)
                await db.commit()
                await db.refresh(existing_follow)
            return existing_follow
        else:
            # Create new follow
            db_obj = CompanyFollow(
                candidate_id=candidate_id,
                company_id=company_id,
                **follow_data.dict(exclude={"company_id"})
            )
            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
            return db_obj

    async def unfollow_company(
        self, 
        db: AsyncSession, 
        candidate_id: int, 
        company_id: int
    ) -> bool:
        """Unfollow a company (soft delete)."""
        follow = await self.get_by_candidate_and_company(
            db, candidate_id, company_id
        )
        
        if follow and follow.is_active:
            follow.unfollow()
            await db.commit()
            return True
        return False

    async def update_follow_preferences(
        self, 
        db: AsyncSession, 
        candidate_id: int, 
        company_id: int,
        update_data: CompanyFollowUpdate
    ) -> CompanyFollow | None:
        """Update follow notification preferences."""
        follow = await self.get_by_candidate_and_company(
            db, candidate_id, company_id
        )
        
        if follow and follow.is_active:
            update_dict = update_data.dict(exclude_unset=True)
            for key, value in update_dict.items():
                setattr(follow, key, value)
            await db.commit()
            await db.refresh(follow)
            return follow
        return None

    async def get_follower_count(
        self, 
        db: AsyncSession, 
        company_id: int
    ) -> int:
        """Get the number of active followers for a company."""
        result = await db.execute(
            select(CompanyFollow).where(
                and_(
                    CompanyFollow.company_id == company_id,
                    CompanyFollow.is_active == True
                )
            )
        )
        return len(result.scalars().all())

    async def get_following_count(
        self, 
        db: AsyncSession, 
        candidate_id: int
    ) -> int:
        """Get the number of companies a candidate is following."""
        result = await db.execute(
            select(CompanyFollow).where(
                and_(
                    CompanyFollow.candidate_id == candidate_id,
                    CompanyFollow.is_active == True
                )
            )
        )
        return len(result.scalars().all())

    async def is_following(
        self, 
        db: AsyncSession, 
        candidate_id: int, 
        company_id: int
    ) -> bool:
        """Check if a candidate is following a company."""
        follow = await self.get_by_candidate_and_company(
            db, candidate_id, company_id
        )
        return follow is not None and follow.is_active


company_follow = CRUDCompanyFollow(CompanyFollow)