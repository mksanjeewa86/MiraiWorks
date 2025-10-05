# Subscription Plan System Implementation Plan

## 📋 Overview

This document outlines the complete implementation plan for a two-tier subscription system (Basic and Premium) for the MiraiWorks application.

### **🔑 Key Point: Exam Access**

**IMPORTANT**: Taking exams is **NOT** a subscription-gated feature!

- ✅ **All users** (Basic plan, Premium plan, and Candidates) can **take exams** when assigned
- ✅ Candidates (users without company affiliation) can take exams regardless of subscription
- ❌ **Only Premium** users can **view exam library** and **administer exams** (create/edit/delete)
- ❌ **Basic plan** users cannot view exam library or create/manage exams

---

## 🎯 Plan Structure

### **Plan Tiers**

| Plan | Features | Restrictions |
|------|----------|--------------|
| **Basic** | - Interviews (view, create, manage)<br>- Positions (view, create, manage)<br>- Messages (send, receive)<br>- Candidates (view, manage)<br>- Calendar (view, schedule)<br>- Users (view, manage company users)<br>- Workflows (create, manage recruitment workflows)<br>- Profile & Settings (full access) | - **Cannot** create/manage exams<br>- **Cannot** view exam library |
| **Premium** | - All Basic features<br>- Exam Administration (create, edit, delete exams)<br>- Exam Library (view all exams)<br>- Question Banks (manage exam questions) | - Full access to all features |

### **Access Rules**
- **Profile**: Available to all users (both Basic and Premium)
- **Settings**: Available to all users (both Basic and Premium)
- **Taking Exams**: Available to **ALL users** (Basic, Premium, and Candidates) when assigned an exam
- **Exam Administration**: Premium only (create, edit, delete, view library)
- **Subscription** is at **Company level** (not user level)
- Users inherit plan features from their company
- **Candidates** (users without company affiliation) can take assigned exams regardless of subscription

---

## 🗄️ Database Schema Design

### **1. Create `subscription_plans` Table**

```sql
CREATE TABLE subscription_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,  -- 'basic', 'premium'
    display_name VARCHAR(100) NOT NULL,  -- 'Basic Plan', 'Premium Plan'
    description TEXT,
    price_monthly DECIMAL(10, 2),  -- Monthly price in JPY/USD
    price_yearly DECIMAL(10, 2),   -- Yearly price (optional discount)
    max_users INTEGER,              -- NULL = unlimited
    max_exams INTEGER,              -- NULL = unlimited
    max_workflows INTEGER,          -- NULL = unlimited
    features JSON,                  -- JSON array of feature flags
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Index for quick lookups
CREATE INDEX idx_subscription_plans_name ON subscription_plans(name);
CREATE INDEX idx_subscription_plans_is_active ON subscription_plans(is_active);
```

### **2. Create `company_subscriptions` Table**

```sql
CREATE TABLE company_subscriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL UNIQUE,  -- One subscription per company
    plan_id INTEGER NOT NULL,
    billing_cycle VARCHAR(20) NOT NULL,  -- 'monthly', 'yearly'
    status VARCHAR(20) NOT NULL DEFAULT 'active',  -- 'active', 'cancelled', 'expired', 'suspended'
    trial_ends_at TIMESTAMP,             -- Trial period end date
    current_period_start TIMESTAMP NOT NULL,
    current_period_end TIMESTAMP NOT NULL,
    cancel_at_period_end BOOLEAN NOT NULL DEFAULT FALSE,
    cancelled_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    FOREIGN KEY (plan_id) REFERENCES subscription_plans(id) ON DELETE RESTRICT
);

-- Indexes
CREATE INDEX idx_company_subscriptions_company_id ON company_subscriptions(company_id);
CREATE INDEX idx_company_subscriptions_status ON company_subscriptions(status);
CREATE INDEX idx_company_subscriptions_plan_id ON company_subscriptions(plan_id);
```

### **3. Create `subscription_invoices` Table** (Optional - for billing history)

```sql
CREATE TABLE subscription_invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subscription_id INTEGER NOT NULL,
    invoice_number VARCHAR(50) NOT NULL UNIQUE,
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'JPY',
    status VARCHAR(20) NOT NULL,  -- 'pending', 'paid', 'failed', 'refunded'
    billing_period_start TIMESTAMP NOT NULL,
    billing_period_end TIMESTAMP NOT NULL,
    issued_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    paid_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (subscription_id) REFERENCES company_subscriptions(id) ON DELETE CASCADE
);

CREATE INDEX idx_subscription_invoices_subscription_id ON subscription_invoices(subscription_id);
CREATE INDEX idx_subscription_invoices_status ON subscription_invoices(status);
```

### **4. Create `plan_change_requests` Table**

```sql
CREATE TABLE plan_change_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    subscription_id INTEGER NOT NULL,
    current_plan_id INTEGER NOT NULL,
    requested_plan_id INTEGER NOT NULL,
    request_type VARCHAR(20) NOT NULL,  -- 'upgrade', 'downgrade'
    requested_by INTEGER NOT NULL,      -- User ID who requested
    request_message TEXT,               -- Message from company admin
    status VARCHAR(20) NOT NULL DEFAULT 'pending',  -- 'pending', 'approved', 'rejected'
    reviewed_by INTEGER,                -- System admin who reviewed
    review_message TEXT,                -- Message from system admin
    reviewed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    FOREIGN KEY (subscription_id) REFERENCES company_subscriptions(id) ON DELETE CASCADE,
    FOREIGN KEY (current_plan_id) REFERENCES subscription_plans(id) ON DELETE RESTRICT,
    FOREIGN KEY (requested_plan_id) REFERENCES subscription_plans(id) ON DELETE RESTRICT,
    FOREIGN KEY (requested_by) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (reviewed_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Indexes
CREATE INDEX idx_plan_change_requests_company_id ON plan_change_requests(company_id);
CREATE INDEX idx_plan_change_requests_subscription_id ON plan_change_requests(subscription_id);
CREATE INDEX idx_plan_change_requests_status ON plan_change_requests(status);
CREATE INDEX idx_plan_change_requests_requested_by ON plan_change_requests(requested_by);
```

### **5. Update `companies` Table**

Add a computed property to easily access subscription plan (no schema change needed - handled in code).

---

## 🔧 Backend Implementation

### **Phase 1: Models** (`backend/app/models/`)

#### **1.1 Create `subscription_plan.py`**
```python
# backend/app/models/subscription_plan.py
from sqlalchemy import Boolean, Column, DateTime, Integer, Numeric, String, Text, JSON
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func
from app.database import Base

class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    name: Mapped[str] = Column(String(50), nullable=False, unique=True, index=True)
    display_name: Mapped[str] = Column(String(100), nullable=False)
    description: Mapped[str] = Column(Text, nullable=True)
    price_monthly: Mapped[float] = Column(Numeric(10, 2), nullable=True)
    price_yearly: Mapped[float] = Column(Numeric(10, 2), nullable=True)
    max_users: Mapped[int] = Column(Integer, nullable=True)  # NULL = unlimited
    max_exams: Mapped[int] = Column(Integer, nullable=True)
    max_workflows: Mapped[int] = Column(Integer, nullable=True)
    features: Mapped[dict] = Column(JSON, nullable=True)  # Feature flags
    is_active: Mapped[bool] = Column(Boolean, nullable=False, default=True, index=True)
    created_at: Mapped[DateTime] = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    company_subscriptions: Mapped[list["CompanySubscription"]] = relationship(
        "CompanySubscription",
        back_populates="plan",
        cascade="all, delete-orphan"
    )

    @property
    def is_basic(self) -> bool:
        return self.name == "basic"

    @property
    def is_premium(self) -> bool:
        return self.name == "premium"

    def has_feature(self, feature: str) -> bool:
        """Check if plan includes a specific feature."""
        if not self.features:
            return False
        return feature in self.features.get("included", [])
```

#### **1.2 Create `company_subscription.py`**
```python
# backend/app/models/company_subscription.py
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func
from app.database import Base

class CompanySubscription(Base):
    __tablename__ = "company_subscriptions"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    company_id: Mapped[int] = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    plan_id: Mapped[int] = Column(Integer, ForeignKey("subscription_plans.id", ondelete="RESTRICT"), nullable=False, index=True)
    billing_cycle: Mapped[str] = Column(String(20), nullable=False)  # 'monthly', 'yearly'
    status: Mapped[str] = Column(String(20), nullable=False, default="active", index=True)
    trial_ends_at: Mapped[datetime] = Column(DateTime(timezone=True), nullable=True)
    current_period_start: Mapped[datetime] = Column(DateTime(timezone=True), nullable=False)
    current_period_end: Mapped[datetime] = Column(DateTime(timezone=True), nullable=False)
    cancel_at_period_end: Mapped[bool] = Column(Boolean, nullable=False, default=False)
    cancelled_at: Mapped[datetime] = Column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    company: Mapped["Company"] = relationship("Company", back_populates="subscription")
    plan: Mapped["SubscriptionPlan"] = relationship("SubscriptionPlan", back_populates="company_subscriptions")

    @property
    def is_active(self) -> bool:
        """Check if subscription is currently active."""
        return self.status == "active" and self.current_period_end >= datetime.now()

    @property
    def is_trial(self) -> bool:
        """Check if subscription is in trial period."""
        if not self.trial_ends_at:
            return False
        return datetime.now() <= self.trial_ends_at

    @property
    def days_remaining(self) -> int:
        """Calculate days remaining in current period."""
        delta = self.current_period_end - datetime.now()
        return max(0, delta.days)
```

#### **1.3 Update `company.py`**
```python
# Add to backend/app/models/company.py

# Add relationship
subscription: Mapped["CompanySubscription"] = relationship(
    "CompanySubscription",
    back_populates="company",
    uselist=False,
    cascade="all, delete-orphan"
)

@property
def subscription_plan(self) -> Optional["SubscriptionPlan"]:
    """Get the company's current subscription plan."""
    if not self.subscription:
        return None
    return self.subscription.plan

@property
def is_premium(self) -> bool:
    """Check if company has premium subscription."""
    plan = self.subscription_plan
    return plan and plan.is_premium

@property
def is_basic(self) -> bool:
    """Check if company has basic subscription."""
    plan = self.subscription_plan
    return plan and plan.is_basic
```

#### **1.4 Create `plan_change_request.py`**
```python
# backend/app/models/plan_change_request.py
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func
from app.database import Base


class PlanChangeRequest(Base):
    __tablename__ = "plan_change_requests"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    company_id: Mapped[int] = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    subscription_id: Mapped[int] = Column(Integer, ForeignKey("company_subscriptions.id", ondelete="CASCADE"), nullable=False, index=True)
    current_plan_id: Mapped[int] = Column(Integer, ForeignKey("subscription_plans.id", ondelete="RESTRICT"), nullable=False)
    requested_plan_id: Mapped[int] = Column(Integer, ForeignKey("subscription_plans.id", ondelete="RESTRICT"), nullable=False)
    request_type: Mapped[str] = Column(String(20), nullable=False)  # 'upgrade', 'downgrade'
    requested_by: Mapped[int] = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=False, index=True)
    request_message: Mapped[str] = Column(Text, nullable=True)
    status: Mapped[str] = Column(String(20), nullable=False, default="pending", index=True)
    reviewed_by: Mapped[int] = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    review_message: Mapped[str] = Column(Text, nullable=True)
    reviewed_at: Mapped[datetime] = Column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    company: Mapped["Company"] = relationship("Company", foreign_keys=[company_id])
    subscription: Mapped["CompanySubscription"] = relationship("CompanySubscription", foreign_keys=[subscription_id])
    current_plan: Mapped["SubscriptionPlan"] = relationship("SubscriptionPlan", foreign_keys=[current_plan_id])
    requested_plan: Mapped["SubscriptionPlan"] = relationship("SubscriptionPlan", foreign_keys=[requested_plan_id])
    requester: Mapped["User"] = relationship("User", foreign_keys=[requested_by])
    reviewer: Mapped["User"] = relationship("User", foreign_keys=[reviewed_by])

    @property
    def is_pending(self) -> bool:
        return self.status == "pending"

    @property
    def is_approved(self) -> bool:
        return self.status == "approved"

    @property
    def is_rejected(self) -> bool:
        return self.status == "rejected"
```

#### **1.5 Update `models/__init__.py`**
```python
# Add imports
from app.models.subscription_plan import SubscriptionPlan
from app.models.company_subscription import CompanySubscription
from app.models.plan_change_request import PlanChangeRequest

# Add to __all__
__all__ = [
    # ... existing exports
    "SubscriptionPlan",
    "CompanySubscription",
    "PlanChangeRequest",
]
```

---

### **Phase 2: Schemas** (`backend/app/schemas/`)

#### **2.1 Create `subscription.py`**
```python
# backend/app/schemas/subscription.py
from datetime import datetime
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field, validator


# Enums
class PlanName(str, Enum):
    BASIC = "basic"
    PREMIUM = "premium"


class BillingCycle(str, Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    TRIAL = "trial"


# Subscription Plan Schemas
class SubscriptionPlanBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    display_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    price_monthly: Optional[float] = Field(None, ge=0)
    price_yearly: Optional[float] = Field(None, ge=0)
    max_users: Optional[int] = Field(None, ge=1)
    max_exams: Optional[int] = Field(None, ge=0)
    max_workflows: Optional[int] = Field(None, ge=0)
    features: Optional[dict[str, Any]] = None


class SubscriptionPlanCreate(SubscriptionPlanBase):
    pass


class SubscriptionPlanUpdate(BaseModel):
    display_name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    price_monthly: Optional[float] = Field(None, ge=0)
    price_yearly: Optional[float] = Field(None, ge=0)
    max_users: Optional[int] = Field(None, ge=1)
    max_exams: Optional[int] = Field(None, ge=0)
    max_workflows: Optional[int] = Field(None, ge=0)
    features: Optional[dict[str, Any]] = None
    is_active: Optional[bool] = None


class SubscriptionPlanInfo(SubscriptionPlanBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Company Subscription Schemas
class CompanySubscriptionBase(BaseModel):
    billing_cycle: BillingCycle


class CompanySubscriptionCreate(CompanySubscriptionBase):
    plan_id: int
    trial_days: Optional[int] = Field(None, ge=0, le=365)


class CompanySubscriptionUpdate(BaseModel):
    plan_id: Optional[int] = None
    billing_cycle: Optional[BillingCycle] = None


class CompanySubscriptionInfo(CompanySubscriptionBase):
    id: int
    company_id: int
    plan_id: int
    status: SubscriptionStatus
    trial_ends_at: Optional[datetime]
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool
    cancelled_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    # Related data
    plan: SubscriptionPlanInfo

    class Config:
        from_attributes = True


class SubscriptionFeatures(BaseModel):
    """Features available in the subscription."""
    # Exam features (Premium only)
    can_view_exam_library: bool  # Can view exam library/list
    can_admin_exams: bool        # Can create/edit/delete exams

    # Note: Taking exams is available to ALL users (including candidates) when assigned
    # This is NOT a subscription feature - it's a universal permission

    # Workflow features (All plans)
    can_manage_workflows: bool

    # Basic features (All plans)
    can_use_interviews: bool
    can_use_positions: bool
    can_use_messages: bool
    can_use_candidates: bool
    can_use_calendar: bool
    can_manage_users: bool

    # Limits
    max_users: Optional[int]
    max_exams: Optional[int]
    max_workflows: Optional[int]


class SubscriptionUsage(BaseModel):
    """Current usage statistics."""
    users_count: int
    exams_count: int
    workflows_count: int
    max_users: Optional[int]
    max_exams: Optional[int]
    max_workflows: Optional[int]
    users_remaining: Optional[int]
    exams_remaining: Optional[int]
    workflows_remaining: Optional[int]


class SubscriptionSummary(BaseModel):
    """Complete subscription information with features and usage."""
    subscription: CompanySubscriptionInfo
    features: SubscriptionFeatures
    usage: SubscriptionUsage
    is_trial: bool
    days_remaining: int


# Plan Change Request Schemas
class PlanChangeRequestStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class PlanChangeRequestType(str, Enum):
    UPGRADE = "upgrade"
    DOWNGRADE = "downgrade"


class PlanChangeRequestCreate(BaseModel):
    requested_plan_id: int
    request_message: Optional[str] = None


class PlanChangeRequestReview(BaseModel):
    status: PlanChangeRequestStatus  # 'approved' or 'rejected'
    review_message: Optional[str] = None


class PlanChangeRequestInfo(BaseModel):
    id: int
    company_id: int
    subscription_id: int
    current_plan_id: int
    requested_plan_id: int
    request_type: PlanChangeRequestType
    requested_by: int
    request_message: Optional[str]
    status: PlanChangeRequestStatus
    reviewed_by: Optional[int]
    review_message: Optional[str]
    reviewed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    # Related data
    current_plan: SubscriptionPlanInfo
    requested_plan: SubscriptionPlanInfo

    class Config:
        from_attributes = True
```

---

### **Phase 3: CRUD** (`backend/app/crud/`)

#### **3.1 Create `subscription_plan.py`**
```python
# backend/app/crud/subscription_plan.py
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.base import CRUDBase
from app.models.subscription_plan import SubscriptionPlan
from app.schemas.subscription import SubscriptionPlanCreate, SubscriptionPlanUpdate


class CRUDSubscriptionPlan(CRUDBase[SubscriptionPlan, SubscriptionPlanCreate, SubscriptionPlanUpdate]):
    async def get_by_name(self, db: AsyncSession, *, name: str) -> Optional[SubscriptionPlan]:
        """Get subscription plan by name."""
        result = await db.execute(
            select(SubscriptionPlan).where(SubscriptionPlan.name == name)
        )
        return result.scalar_one_or_none()

    async def get_active_plans(self, db: AsyncSession) -> list[SubscriptionPlan]:
        """Get all active subscription plans."""
        result = await db.execute(
            select(SubscriptionPlan)
            .where(SubscriptionPlan.is_active == True)
            .order_by(SubscriptionPlan.price_monthly.asc())
        )
        return list(result.scalars().all())


subscription_plan = CRUDSubscriptionPlan(SubscriptionPlan)
```

#### **3.2 Create `company_subscription.py`**
```python
# backend/app/crud/company_subscription.py
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.crud.base import CRUDBase
from app.models.company_subscription import CompanySubscription
from app.schemas.subscription import CompanySubscriptionCreate, CompanySubscriptionUpdate


class CRUDCompanySubscription(CRUDBase[CompanySubscription, CompanySubscriptionCreate, CompanySubscriptionUpdate]):
    async def get_by_company_id(
        self, db: AsyncSession, *, company_id: int
    ) -> Optional[CompanySubscription]:
        """Get subscription by company ID with plan loaded."""
        result = await db.execute(
            select(CompanySubscription)
            .where(CompanySubscription.company_id == company_id)
            .options(selectinload(CompanySubscription.plan))
        )
        return result.scalar_one_or_none()

    async def create_subscription(
        self,
        db: AsyncSession,
        *,
        company_id: int,
        plan_id: int,
        billing_cycle: str,
        trial_days: Optional[int] = None
    ) -> CompanySubscription:
        """Create a new company subscription."""
        now = datetime.now()

        # Calculate period dates
        if billing_cycle == "monthly":
            period_end = now + timedelta(days=30)
        else:  # yearly
            period_end = now + timedelta(days=365)

        # Calculate trial end date
        trial_ends_at = None
        if trial_days and trial_days > 0:
            trial_ends_at = now + timedelta(days=trial_days)

        subscription = CompanySubscription(
            company_id=company_id,
            plan_id=plan_id,
            billing_cycle=billing_cycle,
            status="active",
            trial_ends_at=trial_ends_at,
            current_period_start=now,
            current_period_end=period_end,
        )

        db.add(subscription)
        await db.commit()
        await db.refresh(subscription)

        return subscription

    async def cancel_subscription(
        self,
        db: AsyncSession,
        *,
        subscription: CompanySubscription,
        cancel_at_period_end: bool = True
    ) -> CompanySubscription:
        """Cancel a subscription."""
        if cancel_at_period_end:
            subscription.cancel_at_period_end = True
        else:
            subscription.status = "cancelled"
            subscription.cancelled_at = datetime.now()

        await db.commit()
        await db.refresh(subscription)
        return subscription

    async def reactivate_subscription(
        self,
        db: AsyncSession,
        *,
        subscription: CompanySubscription
    ) -> CompanySubscription:
        """Reactivate a cancelled subscription."""
        subscription.status = "active"
        subscription.cancel_at_period_end = False
        subscription.cancelled_at = None

        await db.commit()
        await db.refresh(subscription)
        return subscription

    async def upgrade_subscription(
        self,
        db: AsyncSession,
        *,
        subscription: CompanySubscription,
        new_plan_id: int
    ) -> CompanySubscription:
        """Upgrade subscription to a higher plan (immediate effect)."""
        subscription.plan_id = new_plan_id
        # Upgrading takes effect immediately
        # Note: In production, you might want to prorate charges here

        await db.commit()
        await db.refresh(subscription)
        return subscription

    async def downgrade_subscription(
        self,
        db: AsyncSession,
        *,
        subscription: CompanySubscription,
        new_plan_id: int,
        immediate: bool = False
    ) -> CompanySubscription:
        """
        Downgrade subscription to a lower plan.

        Args:
            immediate: If True, downgrade now. If False, downgrade at period end.
        """
        if immediate:
            subscription.plan_id = new_plan_id
        else:
            # Schedule downgrade at period end
            # Store the new plan ID for later application
            # You might want to add a `pending_plan_id` field to the model
            subscription.cancel_at_period_end = True
            # In production, you'd store new_plan_id somewhere to apply at period end

        await db.commit()
        await db.refresh(subscription)
        return subscription


company_subscription = CRUDCompanySubscription(CompanySubscription)
```

---

### **Phase 4: Services** (`backend/app/services/`)

#### **4.1 Create `subscription_service.py`**
```python
# backend/app/services/subscription_service.py
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.crud.subscription_plan import subscription_plan as plan_crud
from app.crud.company_subscription import company_subscription as subscription_crud
from app.models.user import User
from app.models.exam import Exam
from app.models.workflow import Workflow
from app.schemas.subscription import (
    SubscriptionFeatures,
    SubscriptionUsage,
    SubscriptionSummary,
    PlanName
)


class SubscriptionService:
    """Service for subscription-related business logic."""

    async def get_company_subscription_summary(
        self,
        db: AsyncSession,
        *,
        company_id: int
    ) -> Optional[SubscriptionSummary]:
        """Get complete subscription summary with features and usage."""
        # Get subscription
        subscription = await subscription_crud.get_by_company_id(db, company_id=company_id)
        if not subscription:
            return None

        # Get plan
        plan = subscription.plan

        # Calculate features
        features = SubscriptionFeatures(
            can_view_exam_library=plan.is_premium,  # Premium only
            can_admin_exams=plan.is_premium,        # Premium only
            # Note: can_take_exams is NOT here - it's universally available
            can_manage_workflows=True,              # All plans
            can_use_interviews=True,                # All plans
            can_use_positions=True,                 # All plans
            can_use_messages=True,                  # All plans
            can_use_candidates=True,                # All plans
            can_use_calendar=True,                  # All plans
            can_manage_users=True,                  # All plans
            max_users=plan.max_users,
            max_exams=plan.max_exams,
            max_workflows=plan.max_workflows,
        )

        # Get usage statistics
        users_count = await db.scalar(
            select(func.count(User.id))
            .where(User.company_id == company_id)
            .where(User.is_deleted == False)
        ) or 0

        exams_count = await db.scalar(
            select(func.count(Exam.id))
            .where(Exam.company_id == company_id)
        ) or 0

        workflows_count = await db.scalar(
            select(func.count(Workflow.id))
            .where(Workflow.employer_company_id == company_id)
        ) or 0

        usage = SubscriptionUsage(
            users_count=users_count,
            exams_count=exams_count,
            workflows_count=workflows_count,
            max_users=plan.max_users,
            max_exams=plan.max_exams,
            max_workflows=plan.max_workflows,
            users_remaining=plan.max_users - users_count if plan.max_users else None,
            exams_remaining=plan.max_exams - exams_count if plan.max_exams else None,
            workflows_remaining=plan.max_workflows - workflows_count if plan.max_workflows else None,
        )

        return SubscriptionSummary(
            subscription=subscription,
            features=features,
            usage=usage,
            is_trial=subscription.is_trial,
            days_remaining=subscription.days_remaining,
        )

    async def can_view_exam_library(self, db: AsyncSession, *, company_id: int) -> tuple[bool, Optional[str]]:
        """Check if company can view exam library (Premium feature)."""
        subscription = await subscription_crud.get_by_company_id(db, company_id=company_id)
        if not subscription or not subscription.is_active:
            return False, "No active subscription"

        if not subscription.plan.is_premium:
            return False, "Viewing exam library requires Premium plan"

        return True, None

    async def can_admin_exams(self, db: AsyncSession, *, company_id: int) -> tuple[bool, Optional[str]]:
        """Check if company can admin exams (Premium feature)."""
        subscription = await subscription_crud.get_by_company_id(db, company_id=company_id)
        if not subscription or not subscription.is_active:
            return False, "No active subscription"

        if not subscription.plan.is_premium:
            return False, "Exam administration requires Premium plan"

        return True, None

    async def can_create_exam(self, db: AsyncSession, *, company_id: int) -> tuple[bool, Optional[str]]:
        """Check if company can create more exams (Premium feature with limits)."""
        # First check if they have admin rights
        can_admin, error = await self.can_admin_exams(db, company_id=company_id)
        if not can_admin:
            return False, error

        subscription = await subscription_crud.get_by_company_id(db, company_id=company_id)
        plan = subscription.plan

        if plan.max_exams is None:
            return True, None  # Unlimited

        current_count = await db.scalar(
            select(func.count(Exam.id)).where(Exam.company_id == company_id)
        ) or 0

        if current_count >= plan.max_exams:
            return False, f"Exam limit reached ({plan.max_exams} exams max)"

        return True, None

    async def can_manage_workflows(self, db: AsyncSession, *, company_id: int) -> tuple[bool, Optional[str]]:
        """Check if company can manage workflows (Available to all plans)."""
        subscription = await subscription_crud.get_by_company_id(db, company_id=company_id)
        if not subscription or not subscription.is_active:
            return False, "No active subscription"

        # Workflows available to all plans
        return True, None

    async def can_create_workflow(self, db: AsyncSession, *, company_id: int) -> tuple[bool, Optional[str]]:
        """Check if company can create more workflows."""
        subscription = await subscription_crud.get_by_company_id(db, company_id=company_id)
        if not subscription or not subscription.is_active:
            return False, "No active subscription"

        plan = subscription.plan

        if plan.max_workflows is None:
            return True, None  # Unlimited

        current_count = await db.scalar(
            select(func.count(Workflow.id)).where(Workflow.employer_company_id == company_id)
        ) or 0

        if current_count >= plan.max_workflows:
            return False, f"Workflow limit reached ({plan.max_workflows} workflows max)"

        return True, None

    async def upgrade_to_premium(
        self,
        db: AsyncSession,
        *,
        company_id: int
    ) -> tuple[bool, Optional[str]]:
        """Upgrade company subscription from Basic to Premium."""
        subscription = await subscription_crud.get_by_company_id(db, company_id=company_id)
        if not subscription:
            return False, "No subscription found"

        if not subscription.is_active:
            return False, "Subscription is not active"

        # Check if already premium
        if subscription.plan.is_premium:
            return False, "Already on Premium plan"

        # Get Premium plan
        premium_plan = await plan_crud.get_by_name(db, name="premium")
        if not premium_plan:
            return False, "Premium plan not found"

        # Upgrade (immediate effect)
        await subscription_crud.upgrade_subscription(
            db,
            subscription=subscription,
            new_plan_id=premium_plan.id
        )

        return True, None

    async def downgrade_to_basic(
        self,
        db: AsyncSession,
        *,
        company_id: int,
        immediate: bool = False
    ) -> tuple[bool, Optional[str]]:
        """Downgrade company subscription from Premium to Basic."""
        subscription = await subscription_crud.get_by_company_id(db, company_id=company_id)
        if not subscription:
            return False, "No subscription found"

        if not subscription.is_active:
            return False, "Subscription is not active"

        # Check if already basic
        if subscription.plan.is_basic:
            return False, "Already on Basic plan"

        # Get Basic plan
        basic_plan = await plan_crud.get_by_name(db, name="basic")
        if not basic_plan:
            return False, "Basic plan not found"

        # Downgrade
        await subscription_crud.downgrade_subscription(
            db,
            subscription=subscription,
            new_plan_id=basic_plan.id,
            immediate=immediate
        )

        if immediate:
            return True, "Downgraded to Basic immediately"
        else:
            return True, "Downgrade to Basic scheduled at period end"


subscription_service = SubscriptionService()
```

---

### **Phase 5: Endpoints** (`backend/app/endpoints/`)

#### **5.1 Create `subscription.py`**
```python
# backend/app/endpoints/subscription.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.config.endpoints import get_current_active_user
from app.crud.subscription_plan import subscription_plan as plan_crud
from app.crud.company_subscription import company_subscription as subscription_crud
from app.models.user import User
from app.schemas.subscription import (
    SubscriptionPlanInfo,
    CompanySubscriptionInfo,
    CompanySubscriptionCreate,
    CompanySubscriptionUpdate,
    SubscriptionSummary,
)
from app.services.subscription_service import subscription_service
from app.utils.auth import require_roles
from app.utils.constants import UserRole

router = APIRouter()


@router.get("/plans", response_model=list[SubscriptionPlanInfo])
async def get_available_plans(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get all available subscription plans."""
    plans = await plan_crud.get_active_plans(db)
    return plans


@router.get("/my-subscription", response_model=SubscriptionSummary)
async def get_my_subscription(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get current user's company subscription with features and usage."""
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not associated with a company"
        )

    summary = await subscription_service.get_company_subscription_summary(
        db, company_id=current_user.company_id
    )

    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No subscription found for company"
        )

    return summary


@router.post("/subscribe", response_model=CompanySubscriptionInfo)
async def create_subscription(
    subscription_data: CompanySubscriptionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new subscription for the company (Admin only)."""
    require_roles(current_user, [UserRole.ADMIN])

    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with a company"
        )

    # Check if subscription already exists
    existing = await subscription_crud.get_by_company_id(
        db, company_id=current_user.company_id
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company already has a subscription"
        )

    # Verify plan exists
    plan = await plan_crud.get(db, id=subscription_data.plan_id)
    if not plan or not plan.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription plan not found or inactive"
        )

    # Create subscription
    subscription = await subscription_crud.create_subscription(
        db,
        company_id=current_user.company_id,
        plan_id=subscription_data.plan_id,
        billing_cycle=subscription_data.billing_cycle,
        trial_days=subscription_data.trial_days,
    )

    return subscription


@router.put("/my-subscription", response_model=CompanySubscriptionInfo)
async def update_my_subscription(
    subscription_data: CompanySubscriptionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update company subscription (Admin only)."""
    require_roles(current_user, [UserRole.ADMIN])

    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with a company"
        )

    subscription = await subscription_crud.get_by_company_id(
        db, company_id=current_user.company_id
    )

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No subscription found for company"
        )

    # If changing plan, verify new plan exists
    if subscription_data.plan_id:
        plan = await plan_crud.get(db, id=subscription_data.plan_id)
        if not plan or not plan.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription plan not found or inactive"
            )

    updated = await subscription_crud.update(
        db, db_obj=subscription, obj_in=subscription_data
    )

    return updated


@router.post("/my-subscription/cancel", response_model=CompanySubscriptionInfo)
async def cancel_my_subscription(
    cancel_at_period_end: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Cancel company subscription (Admin only)."""
    require_roles(current_user, [UserRole.ADMIN])

    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with a company"
        )

    subscription = await subscription_crud.get_by_company_id(
        db, company_id=current_user.company_id
    )

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No subscription found for company"
        )

    cancelled = await subscription_crud.cancel_subscription(
        db, subscription=subscription, cancel_at_period_end=cancel_at_period_end
    )

    return cancelled


@router.post("/my-subscription/reactivate", response_model=CompanySubscriptionInfo)
async def reactivate_my_subscription(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Reactivate cancelled subscription (Admin only)."""
    require_roles(current_user, [UserRole.ADMIN])

    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with a company"
        )

    subscription = await subscription_crud.get_by_company_id(
        db, company_id=current_user.company_id
    )

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No subscription found for company"
        )

    reactivated = await subscription_crud.reactivate_subscription(
        db, subscription=subscription
    )

    return reactivated


@router.post("/my-subscription/upgrade", response_model=CompanySubscriptionInfo)
async def upgrade_to_premium(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Upgrade to Premium plan (Admin only)."""
    require_roles(current_user, [UserRole.ADMIN])

    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with a company"
        )

    # Use service to handle upgrade logic
    success, error = await subscription_service.upgrade_to_premium(
        db, company_id=current_user.company_id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error or "Upgrade failed"
        )

    # Get updated subscription
    subscription = await subscription_crud.get_by_company_id(
        db, company_id=current_user.company_id
    )

    return subscription


@router.post("/my-subscription/downgrade", response_model=CompanySubscriptionInfo)
async def downgrade_to_basic(
    immediate: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Downgrade to Basic plan (Admin only).

    Args:
        immediate: If True, downgrade immediately. If False (default), downgrade at period end.
    """
    require_roles(current_user, [UserRole.ADMIN])

    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with a company"
        )

    # Use service to handle downgrade logic
    success, message = await subscription_service.downgrade_to_basic(
        db, company_id=current_user.company_id, immediate=immediate
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message or "Downgrade failed"
        )

    # Get updated subscription
    subscription = await subscription_crud.get_by_company_id(
        db, company_id=current_user.company_id
    )

    return subscription
```

#### **5.2 Update `routers.py`**
```python
# backend/app/routers.py
from app.endpoints import subscription

# Add to router includes
api_router.include_router(
    subscription.router,
    prefix="/subscriptions",
    tags=["subscriptions"]
)
```

---

### **Phase 6: Permission Middleware** (`backend/app/utils/`)

#### **6.1 Update `auth.py`**
```python
# backend/app/utils/auth.py

# Add new permission functions

async def require_premium_feature(user: User, db: AsyncSession, feature: str) -> None:
    """Check if user's company has access to premium feature."""
    from app.services.subscription_service import subscription_service

    if not user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with a company"
        )

    if feature == "exam_library":
        can_access, error = await subscription_service.can_view_exam_library(
            db, company_id=user.company_id
        )
    elif feature == "exam_admin":
        can_access, error = await subscription_service.can_admin_exams(
            db, company_id=user.company_id
        )
    else:
        raise ValueError(f"Unknown feature: {feature}")

    if not can_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error or "Insufficient permissions"
        )


def can_admin_exams(user: User) -> bool:
    """Check if user can admin exams (requires premium plan)."""
    # This is a sync version - use in non-async contexts
    # For async contexts, use subscription_service.can_admin_exams()
    return has_any_role(user, [UserRole.ADMIN])
```

#### **6.2 Create `subscription_middleware.py`**
```python
# backend/app/utils/subscription_middleware.py
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.config.endpoints import get_current_active_user
from app.models.user import User
from app.services.subscription_service import subscription_service


async def require_exam_library_access(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Dependency to require exam library access (Premium feature - for viewing exam list/library)."""
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with a company"
        )

    can_access, error = await subscription_service.can_view_exam_library(
        db, company_id=current_user.company_id
    )

    if not can_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error or "Viewing exam library requires Premium plan"
        )

    return current_user


async def require_exam_admin_access(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Dependency to require exam admin access (Premium feature - for creating/editing/deleting exams)."""
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with a company"
        )

    can_access, error = await subscription_service.can_admin_exams(
        db, company_id=current_user.company_id
    )

    if not can_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error or "Exam administration requires Premium plan"
        )

    return current_user


async def require_workflow_access(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Dependency to require workflow access (Available to all plans)."""
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with a company"
        )

    can_access, error = await subscription_service.can_manage_workflows(
        db, company_id=current_user.company_id
    )

    if not can_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error or "Workflow access requires active subscription"
        )

    return current_user
```

---

### **Phase 7: Update Existing Endpoints**

#### **7.1 Update Exam Endpoints**
```python
# backend/app/endpoints/exam.py

from app.utils.subscription_middleware import require_exam_library_access, require_exam_admin_access

# Exam library viewing endpoints (Premium only)
@router.get("/", response_model=list[ExamInfo])
async def get_exams(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_exam_library_access),  # Changed - requires Premium
):
    """Get all exams in library (Premium feature)."""
    # ... existing implementation


@router.get("/{exam_id}", response_model=ExamInfo)
async def get_exam(
    exam_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_exam_library_access),  # Changed - requires Premium
):
    """Get exam details from library (Premium feature)."""
    # ... existing implementation


# Taking exam endpoint (Available to ALL users - no subscription check)
@router.post("/{exam_id}/take", response_model=ExamSessionInfo)
async def take_exam(
    exam_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),  # NO subscription check
):
    """
    Start taking an exam (Available to ALL users including candidates).

    Note: This endpoint does NOT require Premium subscription.
    Users (including candidates) can take exams when assigned to them.
    The assignment check is done within the endpoint logic.
    """
    # ... existing implementation
    # Should check if user is assigned to this exam


# Exam administration endpoints (Premium only)
@router.post("/", response_model=ExamInfo)
async def create_exam(
    exam_data: ExamCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_exam_admin_access),  # Changed - requires Premium
):
    """Create a new exam (Premium feature)."""
    # ... existing implementation


@router.put("/{exam_id}", response_model=ExamInfo)
async def update_exam(
    exam_id: int,
    exam_data: ExamUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_exam_admin_access),  # Changed - requires Premium
):
    """Update an exam (Premium feature)."""
    # ... existing implementation


@router.delete("/{exam_id}")
async def delete_exam(
    exam_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_exam_admin_access),  # Changed - requires Premium
):
    """Delete an exam (Premium feature)."""
    # ... existing implementation
```

#### **7.2 Update Workflow Endpoints**
```python
# backend/app/endpoints/workflow.py (if exists)

from app.utils.subscription_middleware import require_workflow_access

# Update all workflow endpoints (Available to all plans)
@router.get("/", response_model=list[WorkflowInfo])
async def get_workflows(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_workflow_access),  # Changed - requires active subscription
):
    """Get all workflows (Available to all plans)."""
    # ... existing implementation


@router.post("/", response_model=WorkflowInfo)
async def create_workflow(
    workflow_data: WorkflowCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_workflow_access),  # Changed - requires active subscription
):
    """Create a new workflow (Available to all plans)."""
    # ... existing implementation


@router.put("/{workflow_id}", response_model=WorkflowInfo)
async def update_workflow(
    workflow_id: int,
    workflow_data: WorkflowUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_workflow_access),  # Changed - requires active subscription
):
    """Update a workflow (Available to all plans)."""
    # ... existing implementation


@router.delete("/{workflow_id}")
async def delete_workflow(
    workflow_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_workflow_access),  # Changed - requires active subscription
):
    """Delete a workflow (Available to all plans)."""
    # ... existing implementation
```

---

## 🎨 Frontend Implementation

### **Phase 8: Types** (`frontend/src/types/`)

#### **8.1 Create `subscription.ts`**
```typescript
// frontend/src/types/subscription.ts

export enum PlanName {
  BASIC = 'basic',
  PREMIUM = 'premium',
}

export enum BillingCycle {
  MONTHLY = 'monthly',
  YEARLY = 'yearly',
}

export enum SubscriptionStatus {
  ACTIVE = 'active',
  CANCELLED = 'cancelled',
  EXPIRED = 'expired',
  SUSPENDED = 'suspended',
  TRIAL = 'trial',
}

export interface SubscriptionPlan {
  id: number;
  name: string;
  display_name: string;
  description?: string;
  price_monthly?: number;
  price_yearly?: number;
  max_users?: number;
  max_exams?: number;
  max_workflows?: number;
  features?: Record<string, any>;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CompanySubscription {
  id: number;
  company_id: number;
  plan_id: number;
  billing_cycle: BillingCycle;
  status: SubscriptionStatus;
  trial_ends_at?: string;
  current_period_start: string;
  current_period_end: string;
  cancel_at_period_end: boolean;
  cancelled_at?: string;
  created_at: string;
  updated_at: string;
  plan: SubscriptionPlan;
}

export interface SubscriptionFeatures {
  // Exam features (Premium only)
  can_view_exam_library: boolean;  // Can view exam library/list
  can_admin_exams: boolean;        // Can create/edit/delete exams

  // Note: Taking exams is available to ALL users (including candidates) when assigned
  // This is NOT a subscription feature - it's a universal permission

  // Workflow features (All plans)
  can_manage_workflows: boolean;

  // Basic features (All plans)
  can_use_interviews: boolean;
  can_use_positions: boolean;
  can_use_messages: boolean;
  can_use_candidates: boolean;
  can_use_calendar: boolean;
  can_manage_users: boolean;

  // Limits
  max_users?: number;
  max_exams?: number;
  max_workflows?: number;
}

export interface SubscriptionUsage {
  users_count: number;
  exams_count: number;
  workflows_count: number;
  max_users?: number;
  max_exams?: number;
  max_workflows?: number;
  users_remaining?: number;
  exams_remaining?: number;
  workflows_remaining?: number;
}

export interface SubscriptionSummary {
  subscription: CompanySubscription;
  features: SubscriptionFeatures;
  usage: SubscriptionUsage;
  is_trial: boolean;
  days_remaining: number;
}

export interface CreateSubscriptionData {
  plan_id: number;
  billing_cycle: BillingCycle;
  trial_days?: number;
}

export interface UpdateSubscriptionData {
  plan_id?: number;
  billing_cycle?: BillingCycle;
}
```

---

### **Phase 9: API Client** (`frontend/src/api/`)

#### **9.1 Create `subscription.ts`**
```typescript
// frontend/src/api/subscription.ts
import { apiClient } from './apiClient';
import type { ApiResponse } from '@/types';
import type {
  SubscriptionPlan,
  CompanySubscription,
  SubscriptionSummary,
  CreateSubscriptionData,
  UpdateSubscriptionData,
} from '@/types/subscription';

export const subscriptionApi = {
  async getAvailablePlans(): Promise<ApiResponse<SubscriptionPlan[]>> {
    const response = await apiClient.get<SubscriptionPlan[]>('/api/subscriptions/plans');
    return { data: response.data, success: true };
  },

  async getMySubscription(): Promise<ApiResponse<SubscriptionSummary>> {
    const response = await apiClient.get<SubscriptionSummary>('/api/subscriptions/my-subscription');
    return { data: response.data, success: true };
  },

  async subscribe(data: CreateSubscriptionData): Promise<ApiResponse<CompanySubscription>> {
    const response = await apiClient.post<CompanySubscription>('/api/subscriptions/subscribe', data);
    return { data: response.data, success: true };
  },

  async updateSubscription(data: UpdateSubscriptionData): Promise<ApiResponse<CompanySubscription>> {
    const response = await apiClient.put<CompanySubscription>('/api/subscriptions/my-subscription', data);
    return { data: response.data, success: true };
  },

  async cancelSubscription(cancelAtPeriodEnd: boolean = true): Promise<ApiResponse<CompanySubscription>> {
    const response = await apiClient.post<CompanySubscription>(
      `/api/subscriptions/my-subscription/cancel?cancel_at_period_end=${cancelAtPeriodEnd}`
    );
    return { data: response.data, success: true };
  },

  async reactivateSubscription(): Promise<ApiResponse<CompanySubscription>> {
    const response = await apiClient.post<CompanySubscription>('/api/subscriptions/my-subscription/reactivate');
    return { data: response.data, success: true };
  },
};
```

---

### **Phase 10: Hooks** (`frontend/src/hooks/`)

#### **10.1 Create `useSubscription.ts`**
```typescript
// frontend/src/hooks/useSubscription.ts
import { useState, useEffect } from 'react';
import { subscriptionApi } from '@/api/subscription';
import type {
  SubscriptionPlan,
  SubscriptionSummary,
  CreateSubscriptionData,
  UpdateSubscriptionData,
} from '@/types/subscription';

export function useSubscriptionPlans() {
  const [plans, setPlans] = useState<SubscriptionPlan[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPlans = async () => {
      setLoading(true);
      try {
        const response = await subscriptionApi.getAvailablePlans();
        setPlans(response.data || []);
      } catch (err) {
        setError('Failed to load subscription plans');
      } finally {
        setLoading(false);
      }
    };

    fetchPlans();
  }, []);

  return { plans, loading, error };
}

export function useMySubscription() {
  const [subscription, setSubscription] = useState<SubscriptionSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSubscription = async () => {
    setLoading(true);
    try {
      const response = await subscriptionApi.getMySubscription();
      setSubscription(response.data || null);
    } catch (err) {
      setError('Failed to load subscription');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSubscription();
  }, []);

  const subscribe = async (data: CreateSubscriptionData) => {
    setLoading(true);
    setError(null);
    try {
      await subscriptionApi.subscribe(data);
      await fetchSubscription();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to subscribe');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const updateSubscription = async (data: UpdateSubscriptionData) => {
    setLoading(true);
    setError(null);
    try {
      await subscriptionApi.updateSubscription(data);
      await fetchSubscription();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update subscription');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const cancelSubscription = async (cancelAtPeriodEnd: boolean = true) => {
    setLoading(true);
    setError(null);
    try {
      await subscriptionApi.cancelSubscription(cancelAtPeriodEnd);
      await fetchSubscription();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to cancel subscription');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const reactivateSubscription = async () => {
    setLoading(true);
    setError(null);
    try {
      await subscriptionApi.reactivateSubscription();
      await fetchSubscription();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to reactivate subscription');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return {
    subscription,
    loading,
    error,
    subscribe,
    updateSubscription,
    cancelSubscription,
    reactivateSubscription,
    refresh: fetchSubscription,
  };
}

// Helper hook for checking features
export function useSubscriptionFeatures() {
  const { subscription } = useMySubscription();

  return {
    // Exam features (Premium only)
    canViewExamLibrary: subscription?.features.can_view_exam_library ?? false,
    canAdminExams: subscription?.features.can_admin_exams ?? false,

    // Note: Taking exams is NOT gated by subscription
    // All users (including candidates) can take assigned exams

    // Workflow features (All plans)
    canManageWorkflows: subscription?.features.can_manage_workflows ?? true,

    // Basic features (All plans)
    canUseInterviews: subscription?.features.can_use_interviews ?? true,
    canUsePositions: subscription?.features.can_use_positions ?? true,
    canUseMessages: subscription?.features.can_use_messages ?? true,
    canUseCandidates: subscription?.features.can_use_candidates ?? true,
    canUseCalendar: subscription?.features.can_use_calendar ?? true,
    canManageUsers: subscription?.features.can_manage_users ?? true,

    // Plan info
    isPremium: subscription?.subscription.plan.name === 'premium',
    isBasic: subscription?.subscription.plan.name === 'basic',
    isTrial: subscription?.is_trial ?? false,
  };
}
```

---

### **Phase 11: Components** (`frontend/src/components/`)

#### **11.1 Create `subscription/PlanCard.tsx`**
```typescript
// frontend/src/components/subscription/PlanCard.tsx
import React from 'react';
import type { SubscriptionPlan } from '@/types/subscription';

interface PlanCardProps {
  plan: SubscriptionPlan;
  isCurrentPlan?: boolean;
  onSelect?: (plan: SubscriptionPlan) => void;
}

export default function PlanCard({ plan, isCurrentPlan, onSelect }: PlanCardProps) {
  return (
    <div className={`border rounded-lg p-6 ${isCurrentPlan ? 'border-blue-500 bg-blue-50' : 'border-gray-300'}`}>
      <div className="mb-4">
        <h3 className="text-2xl font-bold">{plan.display_name}</h3>
        {isCurrentPlan && (
          <span className="text-sm text-blue-600 font-medium">Current Plan</span>
        )}
      </div>

      {plan.description && (
        <p className="text-gray-600 mb-4">{plan.description}</p>
      )}

      <div className="mb-6">
        {plan.price_monthly && (
          <div className="text-3xl font-bold">
            ¥{plan.price_monthly.toLocaleString()}
            <span className="text-sm text-gray-600 font-normal">/month</span>
          </div>
        )}
        {plan.price_yearly && (
          <div className="text-sm text-gray-600">
            or ¥{plan.price_yearly.toLocaleString()}/year
          </div>
        )}
      </div>

      <div className="mb-6">
        <h4 className="font-semibold mb-2">Features:</h4>
        <ul className="space-y-2 text-sm">
          <li>✓ Interviews, Positions, Messages</li>
          <li>✓ Candidates Management</li>
          <li>✓ Calendar & Scheduling</li>
          <li>✓ User Management</li>
          <li>✓ Workflow Management</li>
          {plan.name === 'premium' && (
            <>
              <li className="text-blue-600 font-medium">✓ Exam Library (View)</li>
              <li className="text-blue-600 font-medium">✓ Exam Administration (Create/Edit/Delete)</li>
              <li className="text-blue-600 font-medium">✓ Question Banks</li>
            </>
          )}
        </ul>
        <div className="mt-2 text-xs text-gray-500">
          * All users can take exams when assigned
        </div>
      </div>

      {!isCurrentPlan && onSelect && (
        <button
          onClick={() => onSelect(plan)}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700"
        >
          Select Plan
        </button>
      )}
    </div>
  );
}
```

#### **11.2 Create `subscription/SubscriptionStatus.tsx`**
```typescript
// frontend/src/components/subscription/SubscriptionStatus.tsx
import React from 'react';
import type { SubscriptionSummary } from '@/types/subscription';

interface SubscriptionStatusProps {
  summary: SubscriptionSummary;
}

export default function SubscriptionStatus({ summary }: SubscriptionStatusProps) {
  const { subscription, features, usage, is_trial, days_remaining } = summary;

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold mb-2">
          {subscription.plan.display_name}
        </h2>
        {is_trial && (
          <div className="bg-yellow-100 text-yellow-800 px-3 py-1 rounded inline-block text-sm">
            Trial - {days_remaining} days remaining
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="border rounded p-4">
          <div className="text-sm text-gray-600">Users</div>
          <div className="text-2xl font-bold">
            {usage.users_count}
            {usage.max_users && ` / ${usage.max_users}`}
          </div>
        </div>

        <div className="border rounded p-4">
          <div className="text-sm text-gray-600">Exams</div>
          <div className="text-2xl font-bold">
            {usage.exams_count}
            {usage.max_exams && ` / ${usage.max_exams}`}
          </div>
        </div>

        <div className="border rounded p-4">
          <div className="text-sm text-gray-600">Workflows</div>
          <div className="text-2xl font-bold">
            {usage.workflows_count}
            {usage.max_workflows && ` / ${usage.max_workflows}`}
          </div>
        </div>
      </div>

      <div className="border-t pt-4">
        <h3 className="font-semibold mb-2">Available Features:</h3>
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div className={features.can_use_interviews ? 'text-green-600' : 'text-gray-400'}>
            {features.can_use_interviews ? '✓' : '✗'} Interviews
          </div>
          <div className={features.can_use_positions ? 'text-green-600' : 'text-gray-400'}>
            {features.can_use_positions ? '✓' : '✗'} Positions
          </div>
          <div className={features.can_manage_workflows ? 'text-green-600' : 'text-gray-400'}>
            {features.can_manage_workflows ? '✓' : '✗'} Workflows
          </div>
          <div className={features.can_view_exam_library ? 'text-green-600' : 'text-gray-400'}>
            {features.can_view_exam_library ? '✓' : '✗'} Exam Library
          </div>
          <div className={features.can_admin_exams ? 'text-green-600' : 'text-gray-400'}>
            {features.can_admin_exams ? '✓' : '✗'} Exam Admin
          </div>
        </div>
        <div className="mt-2 text-xs text-gray-500">
          * Taking exams is available to all users when assigned
        </div>
      </div>
    </div>
  );
}
```

---

### **Phase 12: Pages** (`frontend/src/app/`)

#### **12.1 Create `app/subscription/page.tsx`**
```typescript
// frontend/src/app/subscription/page.tsx
'use client';

import React from 'react';
import { useMySubscription } from '@/hooks/useSubscription';
import SubscriptionStatus from '@/components/subscription/SubscriptionStatus';

export default function SubscriptionPage() {
  const { subscription, loading, error } = useMySubscription();

  if (loading) {
    return <div className="p-8">Loading subscription...</div>;
  }

  if (error) {
    return <div className="p-8 text-red-600">Error: {error}</div>;
  }

  if (!subscription) {
    return <div className="p-8">No subscription found</div>;
  }

  return (
    <div className="container mx-auto p-8">
      <h1 className="text-3xl font-bold mb-6">Subscription Management</h1>
      <SubscriptionStatus summary={subscription} />
    </div>
  );
}
```

---

## 🗄️ Database Migration

### **Phase 13: Alembic Migration**

```bash
# Generate migration
cd backend
alembic revision --autogenerate -m "add_subscription_plans_and_company_subscriptions"

# Review and edit migration file if needed

# Run migration
alembic upgrade head
```

---

## 🌱 Seed Data

### **Phase 14: Initial Plan Data**

Create a seed script to populate initial plans:

```python
# backend/scripts/seed_subscription_plans.py
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session_maker
from app.models.subscription_plan import SubscriptionPlan


async def seed_plans():
    async with async_session_maker() as db:
        # Check if plans already exist
        existing = await db.execute(
            select(SubscriptionPlan).where(SubscriptionPlan.name.in_(["basic", "premium"]))
        )
        if existing.scalars().first():
            print("Plans already exist, skipping seed")
            return

        # Create Basic Plan
        basic_plan = SubscriptionPlan(
            name="basic",
            display_name="Basic Plan",
            description="Essential features for small teams with workflow management",
            price_monthly=9800.00,  # ¥9,800/month
            price_yearly=98000.00,  # ¥98,000/year (2 months free)
            max_users=10,
            max_exams=0,  # No exam library/admin access
            max_workflows=None,  # Unlimited workflows
            features={
                "included": [
                    "interviews",
                    "positions",
                    "messages",
                    "candidates",
                    "calendar",
                    "users",
                    "workflows",  # Workflows included in Basic
                    "profile",
                    "settings"
                ],
                "note": "Taking exams is available to all users when assigned (not plan-specific)"
            },
            is_active=True
        )

        # Create Premium Plan
        premium_plan = SubscriptionPlan(
            name="premium",
            display_name="Premium Plan",
            description="All features including exam library and administration",
            price_monthly=29800.00,  # ¥29,800/month
            price_yearly=298000.00,  # ¥298,000/year
            max_users=None,  # Unlimited
            max_exams=None,  # Unlimited exams
            max_workflows=None,  # Unlimited workflows
            features={
                "included": [
                    "interviews",
                    "positions",
                    "messages",
                    "candidates",
                    "calendar",
                    "users",
                    "workflows",
                    "exam_library",  # Can view exam library
                    "admin_exams",  # Exam administration (create/edit/delete)
                    "question_banks",
                    "profile",
                    "settings"
                ],
                "note": "Taking exams is available to all users when assigned (not plan-specific)"
            ]
            },
            is_active=True
        )

        db.add_all([basic_plan, premium_plan])
        await db.commit()
        print("Subscription plans seeded successfully!")


if __name__ == "__main__":
    asyncio.run(seed_plans())
```

Run the seed script:
```bash
cd backend
PYTHONPATH=. python scripts/seed_subscription_plans.py
```

---

## ✅ Implementation Checklist

### **Backend**
- [ ] Create `subscription_plan.py` model
- [ ] Create `company_subscription.py` model
- [ ] Update `company.py` model with subscription relationship
- [ ] Update `models/__init__.py`
- [ ] Create subscription schemas in `schemas/subscription.py`
- [ ] Create `crud/subscription_plan.py`
- [ ] Create `crud/company_subscription.py`
- [ ] Create `services/subscription_service.py`
- [ ] Create `endpoints/subscription.py`
- [ ] Create `utils/subscription_middleware.py`
- [ ] Update `utils/auth.py` with subscription helpers
- [ ] Update `routers.py` to include subscription routes
- [ ] Update exam endpoints with subscription checks
- [ ] Update workflow endpoints with subscription checks
- [ ] Create Alembic migration
- [ ] Run migration
- [ ] Create and run seed script

### **Frontend**
- [ ] Create `types/subscription.ts`
- [ ] Create `api/subscription.ts`
- [ ] Create `hooks/useSubscription.ts`
- [ ] Create `components/subscription/PlanCard.tsx`
- [ ] Create `components/subscription/SubscriptionStatus.tsx`
- [ ] Create `app/subscription/page.tsx`
- [ ] Update navigation to include subscription link
- [ ] Add subscription guards to exam library pages (Premium only)
- [ ] Add subscription guards to exam admin pages (Premium only - create, edit, delete)
- [ ] **DO NOT** add guards to "take exam" page (available to all users)
- [ ] Ensure workflow pages are accessible to all plans
- [ ] Hide exam library navigation for Basic plan users
- [ ] Show workflow navigation for all plan users
- [ ] Show "Take Exam" link for ALL users when assigned

### **Testing**
- [ ] Test subscription plan CRUD
- [ ] Test company subscription creation
- [ ] Test subscription cancellation
- [ ] Test subscription reactivation
- [ ] Test Premium exam library access (viewing exams)
- [ ] Test Premium exam admin access (create, edit, delete)
- [ ] Test taking exams works for ALL users (Basic, Premium, Candidates)
- [ ] Test Basic plan users CANNOT view exam library
- [ ] Test Basic plan users CANNOT create/edit/delete exams
- [ ] Test Basic plan users CAN take exams when assigned
- [ ] Test Candidates (no company) CAN take exams when assigned
- [ ] Test Premium feature access (question banks)
- [ ] Test workflow access (available to all plans)
- [ ] Test usage limits (users, exams, workflows)
- [ ] Test trial period functionality

---

## 🎯 Next Steps

1. **Implement backend models and migrations**
2. **Create CRUD operations**
3. **Build subscription service**
4. **Create API endpoints**
5. **Implement frontend types and API**
6. **Build UI components**
7. **Add subscription guards to protected features**
8. **Test thoroughly**
9. **Deploy**

---

*Last updated: January 2025*
