from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.company_subscription import CompanySubscription
from app.models.subscription_plan import SubscriptionPlan
from app.schemas.subscription import (
    CompanySubscriptionCreate,
    CompanySubscriptionUpdate,
)


class CRUDCompanySubscription(
    CRUDBase[
        CompanySubscription, CompanySubscriptionCreate, CompanySubscriptionUpdate
    ]
):
    """CRUD operations for company subscriptions."""

    async def get_by_company_id(
        self, db: AsyncSession, *, company_id: int
    ) -> Optional[CompanySubscription]:
        """Get subscription by company ID."""
        result = await db.execute(
            select(CompanySubscription)
            .where(CompanySubscription.company_id == company_id)
            .options(selectinload(CompanySubscription.plan))
        )
        return result.scalar_one_or_none()

    async def get_active_by_company_id(
        self, db: AsyncSession, *, company_id: int
    ) -> Optional[CompanySubscription]:
        """Get active subscription by company ID."""
        result = await db.execute(
            select(CompanySubscription)
            .where(CompanySubscription.company_id == company_id)
            .where(CompanySubscription.is_active == True)
            .options(selectinload(CompanySubscription.plan))
        )
        return result.scalar_one_or_none()

    async def get_with_plan_features(
        self, db: AsyncSession, *, company_id: int
    ) -> Optional[CompanySubscription]:
        """Get subscription with plan and all features."""
        result = await db.execute(
            select(CompanySubscription)
            .where(CompanySubscription.company_id == company_id)
            .options(
                selectinload(CompanySubscription.plan).selectinload(
                    SubscriptionPlan.plan_features
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_subscriptions_by_plan(
        self, db: AsyncSession, *, plan_id: int, skip: int = 0, limit: int = 100
    ) -> list[CompanySubscription]:
        """Get all subscriptions for a specific plan."""
        result = await db.execute(
            select(CompanySubscription)
            .where(CompanySubscription.plan_id == plan_id)
            .options(selectinload(CompanySubscription.company))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_active_subscriptions(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> list[CompanySubscription]:
        """Get all active subscriptions."""
        result = await db.execute(
            select(CompanySubscription)
            .where(CompanySubscription.is_active == True)
            .options(
                selectinload(CompanySubscription.company),
                selectinload(CompanySubscription.plan),
            )
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_trial_subscriptions(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> list[CompanySubscription]:
        """Get all trial subscriptions."""
        result = await db.execute(
            select(CompanySubscription)
            .where(CompanySubscription.is_trial == True)
            .where(CompanySubscription.is_active == True)
            .options(
                selectinload(CompanySubscription.company),
                selectinload(CompanySubscription.plan),
            )
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def cancel_subscription(
        self, db: AsyncSession, *, company_id: int, reason: Optional[str] = None
    ) -> Optional[CompanySubscription]:
        """Cancel a company's subscription."""
        from app.utils.datetime_utils import get_utc_now

        subscription = await self.get_by_company_id(db, company_id=company_id)
        if not subscription:
            return None

        subscription.is_active = False
        subscription.cancelled_at = get_utc_now()
        subscription.cancellation_reason = reason

        db.add(subscription)
        await db.commit()
        await db.refresh(subscription)
        return subscription

    async def reactivate_subscription(
        self, db: AsyncSession, *, company_id: int
    ) -> Optional[CompanySubscription]:
        """Reactivate a cancelled subscription."""
        subscription = await self.get_by_company_id(db, company_id=company_id)
        if not subscription:
            return None

        subscription.is_active = True
        subscription.cancelled_at = None
        subscription.cancellation_reason = None

        db.add(subscription)
        await db.commit()
        await db.refresh(subscription)
        return subscription


company_subscription = CRUDCompanySubscription(CompanySubscription)
