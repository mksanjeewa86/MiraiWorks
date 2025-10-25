
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.subscription_plan import SubscriptionPlan
from app.schemas.subscription import SubscriptionPlanCreate, SubscriptionPlanUpdate


class CRUDSubscriptionPlan(
    CRUDBase[SubscriptionPlan, SubscriptionPlanCreate, SubscriptionPlanUpdate]
):
    """CRUD operations for subscription plans."""

    async def get_by_name(
        self, db: AsyncSession, *, name: str
    ) -> SubscriptionPlan | None:
        """Get plan by name (e.g., 'basic', 'premium')."""
        result = await db.execute(
            select(SubscriptionPlan).where(SubscriptionPlan.name == name)
        )
        return result.scalar_one_or_none()

    async def get_active_plans(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> list[SubscriptionPlan]:
        """Get all active plans."""
        result = await db.execute(
            select(SubscriptionPlan)
            .where(SubscriptionPlan.is_active is True)
            .order_by(SubscriptionPlan.display_order)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_public_plans(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> list[SubscriptionPlan]:
        """Get all public plans (shown on pricing page)."""
        result = await db.execute(
            select(SubscriptionPlan)
            .where(SubscriptionPlan.is_active is True)
            .where(SubscriptionPlan.is_public is True)
            .order_by(SubscriptionPlan.display_order)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_with_features(
        self, db: AsyncSession, *, plan_id: int
    ) -> SubscriptionPlan | None:
        """Get plan with all its features loaded."""
        result = await db.execute(
            select(SubscriptionPlan)
            .where(SubscriptionPlan.id == plan_id)
            .options(selectinload(SubscriptionPlan.plan_features))
        )
        return result.scalar_one_or_none()


subscription_plan = CRUDSubscriptionPlan(SubscriptionPlan)
