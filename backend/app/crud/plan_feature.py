from typing import Optional

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.feature import Feature
from app.models.plan_feature import PlanFeature
from app.schemas.subscription import FeatureWithChildren


class CRUDPlanFeature(CRUDBase[PlanFeature, dict, dict]):
    """CRUD operations for plan-feature junction table."""

    async def add_feature_to_plan(
        self,
        db: AsyncSession,
        *,
        plan_id: int,
        feature_id: int,
        added_by: Optional[int] = None,
    ) -> PlanFeature:
        """Add a feature to a plan."""
        try:
            plan_feature = PlanFeature(
                plan_id=plan_id, feature_id=feature_id, added_by=added_by
            )
            db.add(plan_feature)
            await db.commit()
            await db.refresh(plan_feature)
            return plan_feature
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=400, detail="Feature already exists in this plan"
            )

    async def remove_feature_from_plan(
        self, db: AsyncSession, *, plan_id: int, feature_id: int
    ) -> bool:
        """Remove a feature from a plan."""
        result = await db.execute(
            select(PlanFeature)
            .where(PlanFeature.plan_id == plan_id)
            .where(PlanFeature.feature_id == feature_id)
        )
        plan_feature = result.scalar_one_or_none()

        if not plan_feature:
            return False

        await db.delete(plan_feature)
        await db.commit()
        return True

    async def get_plan_features(
        self, db: AsyncSession, *, plan_id: int
    ) -> list[PlanFeature]:
        """Get all features for a plan."""
        result = await db.execute(
            select(PlanFeature)
            .where(PlanFeature.plan_id == plan_id)
            .options(selectinload(PlanFeature.feature))
        )
        return result.scalars().all()

    async def get_plan_features_hierarchical(
        self, db: AsyncSession, *, plan_id: int
    ) -> list[FeatureWithChildren]:
        """
        Get all features for a plan in hierarchical structure.
        Returns only root features with their children nested.
        """
        # Get all plan features
        result = await db.execute(
            select(PlanFeature)
            .where(PlanFeature.plan_id == plan_id)
            .options(selectinload(PlanFeature.feature).selectinload(Feature.children))
        )
        plan_features = result.scalars().all()

        # Extract features and build dictionary
        features = [pf.feature for pf in plan_features]
        feature_ids = {f.id for f in features}

        # Build hierarchical structure
        def build_tree(feature: Feature) -> FeatureWithChildren:
            """Recursively build tree structure."""
            children = []
            for child in feature.children:
                if child.id in feature_ids and child.is_active:
                    children.append(build_tree(child))

            return FeatureWithChildren(
                id=feature.id,
                name=feature.name,
                display_name=feature.display_name,
                description=feature.description,
                category=feature.category,
                parent_feature_id=feature.parent_feature_id,
                permission_key=feature.permission_key,
                is_active=feature.is_active,
                created_at=feature.created_at,
                updated_at=feature.updated_at,
                children=children,
            )

        # Get root features and build tree
        root_features = [f for f in features if f.parent_feature_id is None]
        return [build_tree(root) for root in root_features]

    async def plan_has_feature(
        self, db: AsyncSession, *, plan_id: int, feature_id: int
    ) -> bool:
        """Check if a plan has a specific feature."""
        result = await db.execute(
            select(PlanFeature)
            .where(PlanFeature.plan_id == plan_id)
            .where(PlanFeature.feature_id == feature_id)
        )
        return result.scalar_one_or_none() is not None

    async def plan_has_feature_by_name(
        self, db: AsyncSession, *, plan_id: int, feature_name: str
    ) -> bool:
        """Check if a plan has a feature by feature name."""
        result = await db.execute(
            select(PlanFeature)
            .join(Feature)
            .where(PlanFeature.plan_id == plan_id)
            .where(Feature.name == feature_name)
        )
        return result.scalar_one_or_none() is not None

    async def plan_has_feature_by_permission_key(
        self, db: AsyncSession, *, plan_id: int, permission_key: str
    ) -> bool:
        """Check if a plan has a feature by permission key."""
        result = await db.execute(
            select(PlanFeature)
            .join(Feature)
            .where(PlanFeature.plan_id == plan_id)
            .where(Feature.permission_key == permission_key)
        )
        return result.scalar_one_or_none() is not None

    async def get_plans_with_feature(
        self, db: AsyncSession, *, feature_id: int
    ) -> list[PlanFeature]:
        """Get all plans that have a specific feature."""
        result = await db.execute(
            select(PlanFeature)
            .where(PlanFeature.feature_id == feature_id)
            .options(selectinload(PlanFeature.plan))
        )
        return result.scalars().all()


plan_feature = CRUDPlanFeature(PlanFeature)
