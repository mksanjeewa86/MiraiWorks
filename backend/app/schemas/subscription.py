from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.utils.constants import PlanChangeRequestStatus, PlanChangeRequestType

# ============================================================================
# Feature Schemas (with hierarchical support)
# ============================================================================


class FeatureBase(BaseModel):
    """Base feature schema."""

    name: str
    display_name: str
    description: str | None = None
    category: str | None = None
    parent_feature_id: int | None = None
    permission_key: str | None = None


class FeatureCreate(FeatureBase):
    """Schema for creating a feature."""

    is_active: bool = True


class FeatureUpdate(BaseModel):
    """Schema for updating a feature."""

    display_name: str | None = None
    description: str | None = None
    category: str | None = None
    parent_feature_id: int | None = None
    permission_key: str | None = None
    is_active: bool | None = None


class FeatureInfo(FeatureBase):
    """Feature information with all details."""

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FeatureWithChildren(FeatureInfo):
    """Feature information with child features (for hierarchical display)."""

    children: list["FeatureWithChildren"] = []

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Subscription Plan Schemas
# ============================================================================


class SubscriptionPlanBase(BaseModel):
    """Base subscription plan schema."""

    name: str
    display_name: str
    description: str | None = None
    price_monthly: Decimal
    price_yearly: Decimal | None = None
    currency: str = "JPY"
    max_users: int | None = None
    max_exams: int | None = None
    max_workflows: int | None = None
    max_storage_gb: int | None = None


class SubscriptionPlanCreate(SubscriptionPlanBase):
    """Schema for creating a subscription plan."""

    is_active: bool = True
    is_public: bool = True
    display_order: int = 0


class SubscriptionPlanUpdate(BaseModel):
    """Schema for updating a subscription plan."""

    display_name: str | None = None
    description: str | None = None
    price_monthly: Decimal | None = None
    price_yearly: Decimal | None = None
    currency: str | None = None
    max_users: int | None = None
    max_exams: int | None = None
    max_workflows: int | None = None
    max_storage_gb: int | None = None
    is_active: bool | None = None
    is_public: bool | None = None
    display_order: int | None = None


class SubscriptionPlanInfo(SubscriptionPlanBase):
    """Subscription plan information with all details."""

    id: int
    is_active: bool
    is_public: bool
    display_order: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SubscriptionPlanWithFeatures(SubscriptionPlanInfo):
    """Subscription plan with its features (hierarchical)."""

    features: list[FeatureWithChildren] = []

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Plan Feature Schemas (Junction)
# ============================================================================


class PlanFeatureAdd(BaseModel):
    """Schema for adding a feature to a plan."""

    feature_id: int


class PlanFeatureInfo(BaseModel):
    """Plan feature information."""

    id: int
    plan_id: int
    feature_id: int
    added_by: int | None = None
    added_at: datetime
    feature: FeatureInfo
    plan: SubscriptionPlanInfo

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Company Subscription Schemas
# ============================================================================


class CompanySubscriptionBase(BaseModel):
    """Base company subscription schema."""

    plan_id: int
    billing_cycle: str = "monthly"  # 'monthly' or 'yearly'
    auto_renew: bool = True


class CompanySubscriptionCreate(CompanySubscriptionBase):
    """Schema for creating a company subscription."""

    company_id: int
    is_trial: bool = False
    trial_end_date: datetime | None = None


class CompanySubscriptionUpdate(BaseModel):
    """Schema for updating a company subscription."""

    plan_id: int | None = None
    billing_cycle: str | None = None
    auto_renew: bool | None = None
    is_active: bool | None = None


class CompanySubscriptionInfo(CompanySubscriptionBase):
    """Company subscription information with all details."""

    id: int
    company_id: int
    is_active: bool
    is_trial: bool
    start_date: datetime
    end_date: datetime | None = None
    trial_end_date: datetime | None = None
    next_billing_date: datetime | None = None
    cancelled_at: datetime | None = None
    cancellation_reason: str | None = None
    created_at: datetime
    updated_at: datetime
    plan: SubscriptionPlanInfo

    model_config = ConfigDict(from_attributes=True)


class CompanySubscriptionWithFeatures(CompanySubscriptionInfo):
    """Company subscription with plan features.

    Note: The plan field will contain SubscriptionPlanWithFeatures data
    but inherits the type from CompanySubscriptionInfo to avoid type conflicts.
    """

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Plan Change Request Schemas
# ============================================================================


class PlanChangeRequestCreate(BaseModel):
    """Schema for creating a plan change request."""

    requested_plan_id: int
    request_message: str | None = None


class PlanChangeRequestReview(BaseModel):
    """Schema for reviewing a plan change request."""

    status: PlanChangeRequestStatus  # 'approved' or 'rejected'
    review_message: str | None = None


class PlanChangeRequestInfo(BaseModel):
    """Plan change request information."""

    id: int
    company_id: int
    subscription_id: int
    current_plan_id: int
    requested_plan_id: int
    request_type: PlanChangeRequestType
    requested_by: int
    request_message: str | None = None
    status: PlanChangeRequestStatus
    reviewed_by: int | None = None
    review_message: str | None = None
    reviewed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PlanChangeRequestWithDetails(PlanChangeRequestInfo):
    """Plan change request with full plan details."""

    current_plan: SubscriptionPlanInfo
    requested_plan: SubscriptionPlanInfo
    company_name: str | None = None
    requester_name: str | None = None
    reviewer_name: str | None = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Permission Check Schemas
# ============================================================================


class FeatureAccessCheck(BaseModel):
    """Schema for checking feature access."""

    has_access: bool
    message: str | None = None
    feature_name: str
    plan_name: str | None = None


class BulkFeatureAccessCheck(BaseModel):
    """Schema for checking multiple features at once."""

    features: dict[str, bool]  # feature_name -> has_access
    plan_name: str | None = None
    subscription_active: bool
