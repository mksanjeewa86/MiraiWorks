from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.endpoints import API_ROUTES
from app.crud.feature import feature as feature_crud
from app.crud.plan_feature import plan_feature as plan_feature_crud
from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.subscription import (
    FeatureCreate,
    FeatureInfo,
    FeatureUpdate,
    FeatureWithChildren,
    PlanFeatureAdd,
    PlanFeatureInfo,
)
from app.utils.auth import require_roles
from app.utils.constants import UserRole

router = APIRouter(prefix="/features", tags=["features"])


# ============================================================================
# Feature Catalog Endpoints (System Admin)
# ============================================================================


@router.get(API_ROUTES.FEATURES.HIERARCHICAL, response_model=list[FeatureWithChildren])
async def get_features_hierarchical(db: AsyncSession = Depends(get_db)):
    """
    Get all features in hierarchical structure.
    Returns root features with their children nested.
    Public endpoint for viewing available features.
    """
    features = await feature_crud.get_hierarchical_tree(db)
    return features


@router.get(API_ROUTES.FEATURES.FLAT, response_model=list[FeatureInfo])
async def get_features_flat(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """
    Get all active features in flat list.
    Public endpoint.
    """
    features = await feature_crud.get_active_features(db, skip=skip, limit=limit)
    return features


@router.get(API_ROUTES.FEATURES.BY_ID, response_model=FeatureWithChildren)
async def get_feature(feature_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get a specific feature with its children.
    Public endpoint.
    """
    feature = await feature_crud.get_with_children(db, feature_id=feature_id)
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")

    # Build hierarchical response
    children = []
    for child in feature.children:
        if child.is_active:
            children.append(
                FeatureWithChildren(
                    **child.__dict__,
                    children=[],  # Don't include grandchildren for now
                )
            )

    return FeatureWithChildren(**feature.__dict__, children=children)


@router.post(
    API_ROUTES.FEATURES.BASE,
    response_model=FeatureInfo,
    status_code=status.HTTP_201_CREATED,
)
async def create_feature(
    feature_data: FeatureCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new feature in the catalog (System Admin only).
    Can create main features or sub-features by setting parent_feature_id.
    """
    require_roles(current_user, [UserRole.SYSTEM_ADMIN])

    # Check if feature with same name already exists
    existing = await feature_crud.get_by_name(db, name=feature_data.name)
    if existing:
        raise HTTPException(
            status_code=400, detail="Feature with this name already exists"
        )

    # If parent_feature_id is provided, verify parent exists
    if feature_data.parent_feature_id:
        parent = await feature_crud.get(db, id=feature_data.parent_feature_id)
        if not parent:
            raise HTTPException(status_code=404, detail="Parent feature not found")

    feature = await feature_crud.create(db, obj_in=feature_data)
    return feature


@router.put(API_ROUTES.FEATURES.BY_ID, response_model=FeatureInfo)
async def update_feature(
    feature_id: int,
    feature_data: FeatureUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update a feature (System Admin only).
    Can update display name, description, category, parent, etc.
    """
    require_roles(current_user, [UserRole.SYSTEM_ADMIN])

    feature = await feature_crud.get(db, id=feature_id)
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")

    # If updating parent_feature_id, verify parent exists
    if (
        feature_data.parent_feature_id is not None
        and feature_data.parent_feature_id != feature.parent_feature_id
    ):
        parent = await feature_crud.get(db, id=feature_data.parent_feature_id)
        if not parent:
            raise HTTPException(status_code=404, detail="Parent feature not found")

        # Prevent circular references
        if feature_data.parent_feature_id == feature_id:
            raise HTTPException(
                status_code=400, detail="Feature cannot be its own parent"
            )

    updated_feature = await feature_crud.update(db, db_obj=feature, obj_in=feature_data)
    return updated_feature


@router.delete(API_ROUTES.FEATURES.BY_ID, status_code=status.HTTP_204_NO_CONTENT)
async def delete_feature(
    feature_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete a feature (System Admin only).
    This will also remove it from all plans (cascade delete).
    """
    require_roles(current_user, [UserRole.SYSTEM_ADMIN])

    feature = await feature_crud.get(db, id=feature_id)
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")

    # Check if feature has children
    children = await feature_crud.get_children(db, parent_id=feature_id)
    if children:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete feature with sub-features. Delete sub-features first.",
        )

    await feature_crud.remove(db, id=feature_id)


# ============================================================================
# Plan-Feature Management Endpoints (System Admin)
# ============================================================================


@router.get(API_ROUTES.FEATURES.PLAN_FEATURES, response_model=list[FeatureWithChildren])
async def get_plan_features(plan_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get all features for a specific plan in hierarchical structure.
    Public endpoint to view plan features.
    """
    features = await plan_feature_crud.get_plan_features_hierarchical(
        db, plan_id=plan_id
    )
    return features


@router.post(
    API_ROUTES.FEATURES.ADD_FEATURE_TO_PLAN,
    response_model=PlanFeatureInfo,
    status_code=status.HTTP_201_CREATED,
)
async def add_feature_to_plan(
    plan_id: int,
    feature_data: PlanFeatureAdd,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Add a feature to a plan (System Admin only).
    This immediately grants the feature to all companies on this plan.
    """
    require_roles(current_user, [UserRole.SYSTEM_ADMIN])

    # Verify feature exists
    feature = await feature_crud.get(db, id=feature_data.feature_id)
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")

    # Check if already exists
    exists = await plan_feature_crud.plan_has_feature(
        db, plan_id=plan_id, feature_id=feature_data.feature_id
    )
    if exists:
        raise HTTPException(
            status_code=400, detail="Feature already exists in this plan"
        )

    # Add feature to plan
    plan_feature = await plan_feature_crud.add_feature_to_plan(
        db,
        plan_id=plan_id,
        feature_id=feature_data.feature_id,
        added_by=current_user.id,
    )

    # Load relationships for response
    await db.refresh(plan_feature, ["feature", "plan"])

    return plan_feature


@router.delete(
    API_ROUTES.FEATURES.REMOVE_FEATURE_FROM_PLAN, status_code=status.HTTP_204_NO_CONTENT
)
async def remove_feature_from_plan(
    plan_id: int,
    feature_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Remove a feature from a plan (System Admin only).
    This immediately revokes the feature from all companies on this plan.
    """
    require_roles(current_user, [UserRole.SYSTEM_ADMIN])

    # Remove feature from plan
    removed = await plan_feature_crud.remove_feature_from_plan(
        db, plan_id=plan_id, feature_id=feature_id
    )

    if not removed:
        raise HTTPException(status_code=404, detail="Feature not found in this plan")


@router.get(API_ROUTES.FEATURES.SEARCH, response_model=list[FeatureInfo])
async def search_features(search_term: str, db: AsyncSession = Depends(get_db)):
    """
    Search features by name or display name.
    Public endpoint.
    """
    features = await feature_crud.search_features(db, search_term=search_term)
    return features
