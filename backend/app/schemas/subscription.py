from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.utils.constants import PlanChangeRequestStatus, PlanChangeRequestType

# ============================================================================
# Feature Schemas (with hierarchical support)
# ============================================================================


class FeatureBase(BaseModel):
    """Base feature schema."""

    name: str
    display_name: str
    description: Optional[str] = None
    category: Optional[str] = None
    parent_feature_id: Optional[int] = None
    permission_key: Optional[str] = None


class FeatureCreate(FeatureBase):
    """Schema for creating a feature."""

    is_active: bool = True


class FeatureUpdate(BaseModel):
    """Schema for updating a feature."""

    display_name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    parent_feature_id: Optional[int] = None
    permission_key: Optional[str] = None
    is_active: Optional[bool] = None


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
    description: Optional[str] = None
    price_monthly: Decimal
    price_yearly: Optional[Decimal] = None
    currency: str = "JPY"
    max_users: Optional[int] = None
    max_exams: Optional[int] = None
    max_workflows: Optional[int] = None
    max_storage_gb: Optional[int] = None


class SubscriptionPlanCreate(SubscriptionPlanBase):
    """Schema for creating a subscription plan."""

    is_active: bool = True
    is_public: bool = True
    display_order: int = 0


class SubscriptionPlanUpdate(BaseModel):
    """Schema for updating a subscription plan."""

    display_name: Optional[str] = None
    description: Optional[str] = None
    price_monthly: Optional[Decimal] = None
    price_yearly: Optional[Decimal] = None
    currency: Optional[str] = None
    max_users: Optional[int] = None
    max_exams: Optional[int] = None
    max_workflows: Optional[int] = None
    max_storage_gb: Optional[int] = None
    is_active: Optional[bool] = None
    is_public: Optional[bool] = None
    display_order: Optional[int] = None


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
    added_by: Optional[int] = None
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
    trial_end_date: Optional[datetime] = None


class CompanySubscriptionUpdate(BaseModel):
    """Schema for updating a company subscription."""

    plan_id: Optional[int] = None
    billing_cycle: Optional[str] = None
    auto_renew: Optional[bool] = None
    is_active: Optional[bool] = None


class CompanySubscriptionInfo(CompanySubscriptionBase):
    """Company subscription information with all details."""

    id: int
    company_id: int
    is_active: bool
    is_trial: bool
    start_date: datetime
    end_date: Optional[datetime] = None
    trial_end_date: Optional[datetime] = None
    next_billing_date: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    plan: SubscriptionPlanInfo

    model_config = ConfigDict(from_attributes=True)


class CompanySubscriptionWithFeatures(CompanySubscriptionInfo):
    """Company subscription with plan features."""

    plan: SubscriptionPlanWithFeatures

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Plan Change Request Schemas
# ============================================================================


class PlanChangeRequestCreate(BaseModel):
    """Schema for creating a plan change request."""

    requested_plan_id: int
    request_message: Optional[str] = None


class PlanChangeRequestReview(BaseModel):
    """Schema for reviewing a plan change request."""

    status: PlanChangeRequestStatus  # 'approved' or 'rejected'
    review_message: Optional[str] = None


class PlanChangeRequestInfo(BaseModel):
    """Plan change request information."""

    id: int
    company_id: int
    subscription_id: int
    current_plan_id: int
    requested_plan_id: int
    request_type: PlanChangeRequestType
    requested_by: int
    request_message: Optional[str] = None
    status: PlanChangeRequestStatus
    reviewed_by: Optional[int] = None
    review_message: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PlanChangeRequestWithDetails(PlanChangeRequestInfo):
    """Plan change request with full plan details."""

    current_plan: SubscriptionPlanInfo
    requested_plan: SubscriptionPlanInfo
    company_name: Optional[str] = None
    requester_name: Optional[str] = None
    reviewer_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Permission Check Schemas
# ============================================================================


class FeatureAccessCheck(BaseModel):
    """Schema for checking feature access."""

    has_access: bool
    message: Optional[str] = None
    feature_name: str
    plan_name: Optional[str] = None


class BulkFeatureAccessCheck(BaseModel):
    """Schema for checking multiple features at once."""

    features: dict[str, bool]  # feature_name -> has_access
    plan_name: Optional[str] = None
    subscription_active: bool
