from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.feature import Feature
from app.schemas.subscription import FeatureCreate, FeatureUpdate, FeatureWithChildren


class CRUDFeature(CRUDBase[Feature, FeatureCreate, FeatureUpdate]):
    """CRUD operations for features with hierarchical support."""

    async def get_by_name(self, db: AsyncSession, *, name: str) -> Optional[Feature]:
        """Get feature by name."""
        result = await db.execute(
            select(Feature).where(Feature.name == name)
        )
        return result.scalar_one_or_none()

    async def get_by_permission_key(
        self, db: AsyncSession, *, permission_key: str
    ) -> Optional[Feature]:
        """Get feature by permission key."""
        result = await db.execute(
            select(Feature).where(Feature.permission_key == permission_key)
        )
        return result.scalar_one_or_none()

    async def get_active_features(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> list[Feature]:
        """Get all active features."""
        result = await db.execute(
            select(Feature)
            .where(Feature.is_active == True)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_root_features(self, db: AsyncSession) -> list[Feature]:
        """
        Get all root features (features without parent).
        These are the main/top-level features.
        """
        result = await db.execute(
            select(Feature)
            .where(Feature.parent_feature_id.is_(None))
            .where(Feature.is_active == True)
            .options(selectinload(Feature.children))
            .order_by(Feature.display_name)
        )
        return result.scalars().all()

    async def get_children(
        self, db: AsyncSession, *, parent_id: int
    ) -> list[Feature]:
        """Get all child features of a parent feature."""
        result = await db.execute(
            select(Feature)
            .where(Feature.parent_feature_id == parent_id)
            .where(Feature.is_active == True)
            .order_by(Feature.display_name)
        )
        return result.scalars().all()

    async def get_with_children(
        self, db: AsyncSession, *, feature_id: int
    ) -> Optional[Feature]:
        """Get feature with all its children loaded."""
        result = await db.execute(
            select(Feature)
            .where(Feature.id == feature_id)
            .options(selectinload(Feature.children))
        )
        return result.scalar_one_or_none()

    async def get_hierarchical_tree(self, db: AsyncSession) -> list[FeatureWithChildren]:
        """
        Get all features organized in hierarchical tree structure.
        Returns only root features with their children nested.
        """
        # Get all active features
        result = await db.execute(
            select(Feature)
            .where(Feature.is_active == True)
            .options(selectinload(Feature.children))
        )
        all_features = result.scalars().all()

        # Build a dictionary for quick lookup
        feature_dict = {f.id: f for f in all_features}

        # Build hierarchical structure
        def build_tree(feature: Feature) -> FeatureWithChildren:
            """Recursively build tree structure."""
            children = []
            for child in feature.children:
                if child.is_active:
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
        root_features = [f for f in all_features if f.parent_feature_id is None]
        return [build_tree(root) for root in root_features]

    async def get_by_category(
        self, db: AsyncSession, *, category: str, skip: int = 0, limit: int = 100
    ) -> list[Feature]:
        """Get features by category."""
        result = await db.execute(
            select(Feature)
            .where(Feature.category == category)
            .where(Feature.is_active == True)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def search_features(
        self, db: AsyncSession, *, search_term: str
    ) -> list[Feature]:
        """Search features by name or display_name."""
        search_pattern = f"%{search_term}%"
        result = await db.execute(
            select(Feature)
            .where(
                (Feature.name.ilike(search_pattern))
                | (Feature.display_name.ilike(search_pattern))
            )
            .where(Feature.is_active == True)
        )
        return result.scalars().all()


feature = CRUDFeature(Feature)
