from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.endpoints import API_ROUTES
from app.database import get_db
from app.crud.company_subscription import company_subscription as subscription_crud
from app.crud.plan_change_request import (
    plan_change_request as plan_change_request_crud,
)
from app.crud.plan_feature import plan_feature as plan_feature_crud
from app.crud.subscription_plan import subscription_plan as plan_crud
from app.models.user import User
from app.schemas.subscription import (
    CompanySubscriptionCreate,
    CompanySubscriptionInfo,
    CompanySubscriptionUpdate,
    CompanySubscriptionWithFeatures,
    FeatureAccessCheck,
    PlanChangeRequestCreate,
    PlanChangeRequestInfo,
    PlanChangeRequestReview,
    PlanChangeRequestWithDetails,
    SubscriptionPlanInfo,
    SubscriptionPlanWithFeatures,
)
from app.dependencies import get_current_active_user
from app.services.subscription_service import subscription_service
from app.utils.auth import require_roles
from app.utils.constants import PlanChangeRequestStatus, UserRole

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


# ============================================================================
# Subscription Plan Endpoints (Public & System Admin)
# ============================================================================


@router.get(API_ROUTES.SUBSCRIPTIONS.PLANS, response_model=list[SubscriptionPlanInfo])
async def get_public_plans(db: AsyncSession = Depends(get_db)):
    """
    Get all public subscription plans.
    No authentication required - public pricing page.
    """
    plans = await plan_crud.get_public_plans(db)
    return plans


@router.get(API_ROUTES.SUBSCRIPTIONS.PLAN_BY_ID, response_model=SubscriptionPlanWithFeatures)
async def get_plan_with_features(plan_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get a subscription plan with its features.
    Public endpoint for viewing plan details.
    """
    plan = await plan_crud.get_with_features(db, plan_id=plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    # Get plan features hierarchically
    features = await plan_feature_crud.get_plan_features_hierarchical(
        db, plan_id=plan_id
    )

    return SubscriptionPlanWithFeatures(**plan.__dict__, features=features)


# ============================================================================
# Company Subscription Endpoints (Company Admin)
# ============================================================================


@router.get(API_ROUTES.SUBSCRIPTIONS.MY_SUBSCRIPTION, response_model=CompanySubscriptionWithFeatures)
async def get_my_subscription(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get current company's subscription with plan features.
    Company Admin or Member can access.
    """
    if not current_user.company_id:
        raise HTTPException(
            status_code=400, detail="User is not associated with a company"
        )

    subscription = await subscription_crud.get_with_plan_features(
        db, company_id=current_user.company_id
    )

    if not subscription:
        raise HTTPException(status_code=404, detail="No subscription found")

    # Get plan features hierarchically
    features = await plan_feature_crud.get_plan_features_hierarchical(
        db, plan_id=subscription.plan_id
    )

    # Build response with features
    plan_with_features = SubscriptionPlanWithFeatures(
        **subscription.plan.__dict__, features=features
    )

    return CompanySubscriptionWithFeatures(
        **subscription.__dict__, plan=plan_with_features
    )


@router.post(API_ROUTES.SUBSCRIPTIONS.SUBSCRIBE, response_model=CompanySubscriptionInfo, status_code=201)
async def subscribe_to_plan(
    subscription_data: CompanySubscriptionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Subscribe company to a plan (initial subscription).
    Company Admin only.
    """
    require_roles(current_user, [UserRole.ADMIN])

    if not current_user.company_id:
        raise HTTPException(
            status_code=400, detail="User is not associated with a company"
        )

    # Check if company already has a subscription
    existing = await subscription_crud.get_by_company_id(
        db, company_id=current_user.company_id
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Company already has a subscription. Use plan change request to modify.",
        )

    # Verify plan exists
    plan = await plan_crud.get(db, id=subscription_data.plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    # Create subscription
    subscription_data.company_id = current_user.company_id
    subscription = await subscription_crud.create(db, obj_in=subscription_data)

    return subscription


@router.put(API_ROUTES.SUBSCRIPTIONS.UPDATE_SUBSCRIPTION, response_model=CompanySubscriptionInfo)
async def update_my_subscription(
    subscription_data: CompanySubscriptionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update subscription settings (billing cycle, auto-renew, etc.).
    Company Admin only.
    Cannot change plan - use plan change request for that.
    """
    require_roles(current_user, [UserRole.ADMIN])

    if not current_user.company_id:
        raise HTTPException(
            status_code=400, detail="User is not associated with a company"
        )

    subscription = await subscription_crud.get_by_company_id(
        db, company_id=current_user.company_id
    )
    if not subscription:
        raise HTTPException(status_code=404, detail="No subscription found")

    # Don't allow plan changes through this endpoint
    if subscription_data.plan_id is not None:
        raise HTTPException(
            status_code=400,
            detail="Cannot change plan directly. Use plan change request.",
        )

    updated_subscription = await subscription_crud.update(
        db, db_obj=subscription, obj_in=subscription_data
    )

    return updated_subscription


# ============================================================================
# Feature Access Check Endpoints (Company Users)
# ============================================================================


@router.get(API_ROUTES.SUBSCRIPTIONS.CHECK_FEATURE, response_model=FeatureAccessCheck)
async def check_feature_access(
    feature_name: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Check if current company has access to a specific feature.
    Any authenticated company user can check.
    """
    if not current_user.company_id:
        return FeatureAccessCheck(
            has_access=False,
            message="User is not associated with a company",
            feature_name=feature_name,
        )

    has_access, error_msg = await subscription_service.check_feature_access(
        db, company_id=current_user.company_id, feature_name=feature_name
    )

    subscription = await subscription_crud.get_active_by_company_id(
        db, company_id=current_user.company_id
    )
    plan_name = subscription.plan.name if subscription else None

    return FeatureAccessCheck(
        has_access=has_access,
        message=error_msg,
        feature_name=feature_name,
        plan_name=plan_name,
    )


# ============================================================================
# Plan Change Request Endpoints (Company Admin & System Admin)
# ============================================================================


@router.post(
    API_ROUTES.SUBSCRIPTIONS.REQUEST_PLAN_CHANGE, response_model=PlanChangeRequestInfo, status_code=201
)
async def request_plan_change(
    request_data: PlanChangeRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Request a plan change (upgrade or downgrade).
    Company Admin only. Requires System Admin approval.
    """
    require_roles(current_user, [UserRole.ADMIN])

    if not current_user.company_id:
        raise HTTPException(
            status_code=400, detail="User is not associated with a company"
        )

    change_request = await subscription_service.request_plan_change(
        db,
        company_id=current_user.company_id,
        requested_plan_id=request_data.requested_plan_id,
        requested_by=current_user.id,
        request_message=request_data.request_message,
    )

    return change_request


@router.get(API_ROUTES.SUBSCRIPTIONS.MY_PLAN_CHANGE_REQUESTS, response_model=list[PlanChangeRequestWithDetails])
async def get_my_plan_change_requests(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get all plan change requests for current company.
    Company Admin can view their company's requests.
    """
    require_roles(current_user, [UserRole.ADMIN])

    if not current_user.company_id:
        raise HTTPException(
            status_code=400, detail="User is not associated with a company"
        )

    requests = await plan_change_request_crud.get_by_company_id(
        db, company_id=current_user.company_id
    )

    return requests


@router.get(
    API_ROUTES.SUBSCRIPTIONS.ALL_PLAN_CHANGE_REQUESTS, response_model=list[PlanChangeRequestWithDetails]
)
async def get_all_plan_change_requests(
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get all plan change requests (System Admin only).
    Can filter by status: pending, approved, rejected.
    """
    require_roles(current_user, [UserRole.SYSTEM_ADMIN])

    if status:
        try:
            status_enum = PlanChangeRequestStatus(status)
            requests = await plan_change_request_crud.get_by_status(
                db, status=status_enum
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status value")
    else:
        # Get pending by default
        requests = await plan_change_request_crud.get_pending_requests(db)

    # Build response with details
    results = []
    for req in requests:
        results.append(
            PlanChangeRequestWithDetails(
                **req.__dict__,
                current_plan=req.current_plan,
                requested_plan=req.requested_plan,
                company_name=req.company.name if req.company else None,
                requester_name=req.requester.full_name if req.requester else None,
                reviewer_name=req.reviewer.full_name if req.reviewer else None,
            )
        )

    return results


@router.post(
    API_ROUTES.SUBSCRIPTIONS.REVIEW_PLAN_CHANGE,
    response_model=PlanChangeRequestWithDetails,
)
async def review_plan_change_request(
    request_id: int,
    review_data: PlanChangeRequestReview,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Approve or reject a plan change request (System Admin only).
    If approved, the plan change takes effect immediately.
    """
    require_roles(current_user, [UserRole.SYSTEM_ADMIN])

    reviewed_request = await subscription_service.review_plan_change_request(
        db,
        request_id=request_id,
        reviewer=current_user,
        status=review_data.status,
        review_message=review_data.review_message,
    )

    return PlanChangeRequestWithDetails(
        **reviewed_request.__dict__,
        current_plan=reviewed_request.current_plan,
        requested_plan=reviewed_request.requested_plan,
        company_name=(
            reviewed_request.company.name if reviewed_request.company else None
        ),
        requester_name=(
            reviewed_request.requester.full_name
            if reviewed_request.requester
            else None
        ),
        reviewer_name=(
            reviewed_request.reviewer.full_name if reviewed_request.reviewer else None
        ),
    )
