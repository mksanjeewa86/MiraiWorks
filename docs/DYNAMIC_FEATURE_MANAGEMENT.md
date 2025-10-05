# Dynamic Plan Feature Management System

## 📋 Overview

This system allows **System Admins** to dynamically configure which features are available in each subscription plan through a frontend interface.

### **Key Capabilities**
- ✅ Add features to any plan
- ✅ Remove features from any plan
- ✅ Real-time effect on user permissions
- ✅ Feature availability automatically enforced
- ✅ No code changes needed to modify plan features

---

## 🎯 Use Cases

### **Example 1: Add Workflows to Premium**
```
System Admin:
1. Goes to Admin > Plan Management > Premium
2. Clicks "Add Feature"
3. Selects "Workflows"
4. Saves

Result:
- Premium users can now access workflows
- Basic users still cannot access workflows (if not in Basic plan)
```

### **Example 2: Remove Exams from Basic**
```
System Admin:
1. Goes to Admin > Plan Management > Basic
2. Finds "Exams" in feature list
3. Clicks "Remove"
4. Confirms

Result:
- Basic users immediately lose access to exam library
- Premium users still have access (if Exams in Premium)
```

### **Example 3: Add Custom Feature**
```
System Admin:
1. Goes to Admin > Feature Catalog
2. Clicks "Add New Feature"
3. Enters:
   - Name: "api_access"
   - Display Name: "API Access"
   - Description: "Access to REST API"
   - Category: "integrations"
4. Saves

Then:
5. Goes to Premium plan
6. Adds "api_access" feature

Result:
- Only Premium users can access API
```

---

## 🗄️ Database Schema

### **1. Create `features` Table (Master Feature Catalog)**

```sql
CREATE TABLE features (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,           -- 'workflows', 'exams', 'api_access'
    display_name VARCHAR(100) NOT NULL,         -- 'Workflow Management'
    description TEXT,
    category VARCHAR(50),                       -- 'core', 'premium', 'integrations'
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_features_name ON features(name);
CREATE INDEX idx_features_is_active ON features(is_active);

-- Seed initial features
INSERT INTO features (name, display_name, description, category) VALUES
('interviews', 'Interviews', 'Schedule and manage interviews', 'core'),
('positions', 'Positions', 'Job position management', 'core'),
('messages', 'Messages', 'Internal messaging system', 'core'),
('candidates', 'Candidates', 'Candidate management', 'core'),
('calendar', 'Calendar', 'Calendar and scheduling', 'core'),
('users', 'Users', 'User management', 'core'),
('workflows', 'Workflows', 'Recruitment workflow automation', 'premium'),
('exam_library', 'Exam Library', 'View and browse exam library', 'premium'),
('admin_exams', 'Exam Administration', 'Create and manage exams', 'premium'),
('question_banks', 'Question Banks', 'Manage exam question banks', 'premium'),
('api_access', 'API Access', 'REST API access', 'integrations'),
('advanced_analytics', 'Advanced Analytics', 'Advanced reporting and analytics', 'premium');
```

### **2. Create `plan_features` Table (Junction Table)**

```sql
CREATE TABLE plan_features (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL,
    feature_id INTEGER NOT NULL,
    added_by INTEGER,                           -- System admin who added
    added_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (plan_id) REFERENCES subscription_plans(id) ON DELETE CASCADE,
    FOREIGN KEY (feature_id) REFERENCES features(id) ON DELETE CASCADE,
    FOREIGN KEY (added_by) REFERENCES users(id) ON DELETE SET NULL,

    UNIQUE(plan_id, feature_id)  -- Prevent duplicate features in same plan
);

CREATE INDEX idx_plan_features_plan_id ON plan_features(plan_id);
CREATE INDEX idx_plan_features_feature_id ON plan_features(feature_id);

-- Seed Basic Plan features
INSERT INTO plan_features (plan_id, feature_id)
SELECT 1, id FROM features
WHERE name IN ('interviews', 'positions', 'messages', 'candidates', 'calendar', 'users', 'workflows');

-- Seed Premium Plan features
INSERT INTO plan_features (plan_id, feature_id)
SELECT 2, id FROM features
WHERE name IN ('interviews', 'positions', 'messages', 'candidates', 'calendar', 'users',
               'workflows', 'exam_library', 'admin_exams', 'question_banks', 'api_access');
```

### **3. Update `subscription_plans` Table**

```sql
-- Remove the JSON features column (if exists) and use plan_features junction table instead
ALTER TABLE subscription_plans DROP COLUMN features;
```

---

## 🔧 Backend Implementation

### **1. Models**

#### **1.1 Create `feature.py`**

```python
# backend/app/models/feature.py
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func
from app.database import Base


class Feature(Base):
    __tablename__ = "features"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    name: Mapped[str] = Column(String(50), nullable=False, unique=True, index=True)
    display_name: Mapped[str] = Column(String(100), nullable=False)
    description: Mapped[str] = Column(Text, nullable=True)
    category: Mapped[str] = Column(String(50), nullable=True)
    is_active: Mapped[bool] = Column(Boolean, nullable=False, default=True, index=True)
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    plan_features: Mapped[list["PlanFeature"]] = relationship(
        "PlanFeature",
        back_populates="feature",
        cascade="all, delete-orphan"
    )
```

#### **1.2 Create `plan_feature.py`**

```python
# backend/app/models/plan_feature.py
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func
from app.database import Base


class PlanFeature(Base):
    __tablename__ = "plan_features"
    __table_args__ = (
        UniqueConstraint('plan_id', 'feature_id', name='uq_plan_feature'),
    )

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    plan_id: Mapped[int] = Column(Integer, ForeignKey("subscription_plans.id", ondelete="CASCADE"), nullable=False, index=True)
    feature_id: Mapped[int] = Column(Integer, ForeignKey("features.id", ondelete="CASCADE"), nullable=False, index=True)
    added_by: Mapped[int] = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    added_at: Mapped[datetime] = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    plan: Mapped["SubscriptionPlan"] = relationship("SubscriptionPlan", back_populates="plan_features")
    feature: Mapped["Feature"] = relationship("Feature", back_populates="plan_features")
    admin: Mapped["User"] = relationship("User", foreign_keys=[added_by])
```

#### **1.3 Update `subscription_plan.py`**

```python
# backend/app/models/subscription_plan.py

# Add relationship
plan_features: Mapped[list["PlanFeature"]] = relationship(
    "PlanFeature",
    back_populates="plan",
    cascade="all, delete-orphan"
)

def has_feature(self, feature_name: str) -> bool:
    """Check if plan includes a specific feature by name."""
    return any(pf.feature.name == feature_name for pf in self.plan_features if pf.feature.is_active)

def get_feature_names(self) -> list[str]:
    """Get list of all feature names in this plan."""
    return [pf.feature.name for pf in self.plan_features if pf.feature.is_active]
```

---

### **2. Schemas**

```python
# backend/app/schemas/feature.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# Feature Schemas
class FeatureBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    display_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=50)


class FeatureCreate(FeatureBase):
    pass


class FeatureUpdate(BaseModel):
    display_name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None


class FeatureInfo(FeatureBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Plan Feature Schemas
class PlanFeatureAdd(BaseModel):
    feature_id: int


class PlanFeatureInfo(BaseModel):
    id: int
    plan_id: int
    feature_id: int
    added_by: Optional[int]
    added_at: datetime

    # Related data
    feature: FeatureInfo

    class Config:
        from_attributes = True


# Plan with Features
class SubscriptionPlanWithFeatures(BaseModel):
    id: int
    name: str
    display_name: str
    description: Optional[str]
    price_monthly: Optional[float]
    price_yearly: Optional[float]
    is_active: bool
    features: list[FeatureInfo]  # List of features in this plan

    class Config:
        from_attributes = True
```

---

### **3. CRUD Operations**

```python
# backend/app/crud/feature.py
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.base import CRUDBase
from app.models.feature import Feature
from app.schemas.feature import FeatureCreate, FeatureUpdate


class CRUDFeature(CRUDBase[Feature, FeatureCreate, FeatureUpdate]):
    async def get_by_name(self, db: AsyncSession, *, name: str) -> Optional[Feature]:
        """Get feature by name."""
        result = await db.execute(
            select(Feature).where(Feature.name == name)
        )
        return result.scalar_one_or_none()

    async def get_active_features(self, db: AsyncSession) -> list[Feature]:
        """Get all active features."""
        result = await db.execute(
            select(Feature)
            .where(Feature.is_active == True)
            .order_by(Feature.category, Feature.display_name)
        )
        return list(result.scalars().all())


feature = CRUDFeature(Feature)
```

```python
# backend/app/crud/plan_feature.py
from typing import Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.plan_feature import PlanFeature
from app.models.feature import Feature


class CRUDPlanFeature:
    async def add_feature_to_plan(
        self,
        db: AsyncSession,
        *,
        plan_id: int,
        feature_id: int,
        added_by: int
    ) -> PlanFeature:
        """Add a feature to a plan."""
        plan_feature = PlanFeature(
            plan_id=plan_id,
            feature_id=feature_id,
            added_by=added_by
        )
        db.add(plan_feature)
        await db.commit()
        await db.refresh(plan_feature)
        return plan_feature

    async def remove_feature_from_plan(
        self,
        db: AsyncSession,
        *,
        plan_id: int,
        feature_id: int
    ) -> bool:
        """Remove a feature from a plan."""
        result = await db.execute(
            delete(PlanFeature)
            .where(PlanFeature.plan_id == plan_id)
            .where(PlanFeature.feature_id == feature_id)
        )
        await db.commit()
        return result.rowcount > 0

    async def get_plan_features(
        self,
        db: AsyncSession,
        *,
        plan_id: int
    ) -> list[PlanFeature]:
        """Get all features for a plan."""
        result = await db.execute(
            select(PlanFeature)
            .where(PlanFeature.plan_id == plan_id)
            .options(selectinload(PlanFeature.feature))
        )
        return list(result.scalars().all())

    async def plan_has_feature(
        self,
        db: AsyncSession,
        *,
        plan_id: int,
        feature_name: str
    ) -> bool:
        """Check if a plan has a specific feature."""
        result = await db.execute(
            select(PlanFeature)
            .join(Feature)
            .where(PlanFeature.plan_id == plan_id)
            .where(Feature.name == feature_name)
            .where(Feature.is_active == True)
        )
        return result.scalar_one_or_none() is not None


plan_feature = CRUDPlanFeature()
```

---

### **4. Endpoints**

```python
# backend/app/endpoints/feature_management.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.config.endpoints import get_current_active_user
from app.crud.feature import feature as feature_crud
from app.crud.plan_feature import plan_feature as plan_feature_crud
from app.crud.subscription_plan import subscription_plan as plan_crud
from app.models.user import User
from app.schemas.feature import (
    FeatureInfo,
    FeatureCreate,
    FeatureUpdate,
    PlanFeatureAdd,
    PlanFeatureInfo,
    SubscriptionPlanWithFeatures
)
from app.utils.auth import require_roles
from app.utils.constants import UserRole

router = APIRouter()


# ============================================
# FEATURE CATALOG MANAGEMENT (System Admin)
# ============================================

@router.get("/features", response_model=list[FeatureInfo])
async def get_all_features(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get all features in the catalog (System Admin only)."""
    require_roles(current_user, [UserRole.SYSTEM_ADMIN])

    features = await feature_crud.get_active_features(db)
    return features


@router.post("/features", response_model=FeatureInfo)
async def create_feature(
    feature_data: FeatureCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new feature (System Admin only)."""
    require_roles(current_user, [UserRole.SYSTEM_ADMIN])

    # Check if feature already exists
    existing = await feature_crud.get_by_name(db, name=feature_data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Feature '{feature_data.name}' already exists"
        )

    feature = await feature_crud.create(db, obj_in=feature_data)
    return feature


@router.put("/features/{feature_id}", response_model=FeatureInfo)
async def update_feature(
    feature_id: int,
    feature_data: FeatureUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update a feature (System Admin only)."""
    require_roles(current_user, [UserRole.SYSTEM_ADMIN])

    feature = await feature_crud.get(db, id=feature_id)
    if not feature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feature not found"
        )

    updated = await feature_crud.update(db, db_obj=feature, obj_in=feature_data)
    return updated


# ============================================
# PLAN FEATURE MANAGEMENT (System Admin)
# ============================================

@router.get("/plans/{plan_id}/features", response_model=SubscriptionPlanWithFeatures)
async def get_plan_with_features(
    plan_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get plan with all its features (System Admin only)."""
    require_roles(current_user, [UserRole.SYSTEM_ADMIN])

    plan = await plan_crud.get(db, id=plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )

    # Get plan features
    plan_features = await plan_feature_crud.get_plan_features(db, plan_id=plan_id)

    return {
        "id": plan.id,
        "name": plan.name,
        "display_name": plan.display_name,
        "description": plan.description,
        "price_monthly": plan.price_monthly,
        "price_yearly": plan.price_yearly,
        "is_active": plan.is_active,
        "features": [pf.feature for pf in plan_features if pf.feature.is_active]
    }


@router.post("/plans/{plan_id}/features", response_model=PlanFeatureInfo)
async def add_feature_to_plan(
    plan_id: int,
    data: PlanFeatureAdd,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Add a feature to a plan (System Admin only).

    This will immediately grant the feature to all users on this plan.
    """
    require_roles(current_user, [UserRole.SYSTEM_ADMIN])

    # Verify plan exists
    plan = await plan_crud.get(db, id=plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )

    # Verify feature exists
    feature = await feature_crud.get(db, id=data.feature_id)
    if not feature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feature not found"
        )

    # Add feature to plan
    try:
        plan_feature = await plan_feature_crud.add_feature_to_plan(
            db,
            plan_id=plan_id,
            feature_id=data.feature_id,
            added_by=current_user.id
        )
        return plan_feature
    except Exception as e:
        # Handle duplicate feature error
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Feature already exists in this plan or: {str(e)}"
        )


@router.delete("/plans/{plan_id}/features/{feature_id}")
async def remove_feature_from_plan(
    plan_id: int,
    feature_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Remove a feature from a plan (System Admin only).

    This will immediately revoke the feature from all users on this plan.
    """
    require_roles(current_user, [UserRole.SYSTEM_ADMIN])

    success = await plan_feature_crud.remove_feature_from_plan(
        db,
        plan_id=plan_id,
        feature_id=feature_id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feature not found in this plan"
        )

    return {"message": "Feature removed from plan successfully"}
```

---

### **5. Update Permission Checks**

```python
# backend/app/services/subscription_service.py

async def can_access_feature(
    self,
    db: AsyncSession,
    *,
    company_id: int,
    feature_name: str
) -> tuple[bool, Optional[str]]:
    """Check if company can access a specific feature."""
    subscription = await subscription_crud.get_by_company_id(db, company_id=company_id)
    if not subscription or not subscription.is_active:
        return False, "No active subscription"

    # Check if plan has this feature
    has_feature = await plan_feature_crud.plan_has_feature(
        db,
        plan_id=subscription.plan_id,
        feature_name=feature_name
    )

    if not has_feature:
        return False, f"This feature requires a plan that includes '{feature_name}'"

    return True, None


# Specific feature checks
async def can_view_exam_library(self, db: AsyncSession, *, company_id: int) -> tuple[bool, Optional[str]]:
    """Check if company can view exam library."""
    return await self.can_access_feature(db, company_id=company_id, feature_name="exam_library")


async def can_admin_exams(self, db: AsyncSession, *, company_id: int) -> tuple[bool, Optional[str]]:
    """Check if company can admin exams."""
    return await self.can_access_feature(db, company_id=company_id, feature_name="admin_exams")


async def can_manage_workflows(self, db: AsyncSession, *, company_id: int) -> tuple[bool, Optional[str]]:
    """Check if company can manage workflows."""
    return await self.can_access_feature(db, company_id=company_id, feature_name="workflows")
```

---

## 🎨 Frontend Implementation

### **System Admin UI - Manage Plan Features**

```typescript
// frontend/src/app/admin/plans/[planId]/features/page.tsx
'use client';

import { use, useEffect, useState } from 'react';
import { featureApi } from '@/api/features';
import type { Feature, PlanWithFeatures } from '@/types/feature';

export default function ManagePlanFeaturesPage({ params }: { params: Promise<{ planId: string }> }) {
  const { planId } = use(params);
  const [plan, setPlan] = useState<PlanWithFeatures | null>(null);
  const [allFeatures, setAllFeatures] = useState<Feature[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadData();
  }, [planId]);

  const loadData = async () => {
    setLoading(true);
    try {
      // Load plan with current features
      const planResponse = await featureApi.getPlanWithFeatures(Number(planId));
      setPlan(planResponse.data);

      // Load all available features
      const featuresResponse = await featureApi.getAllFeatures();
      setAllFeatures(featuresResponse.data || []);
    } catch (error) {
      console.error('Failed to load data', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddFeature = async (featureId: number) => {
    if (!plan) return;

    try {
      await featureApi.addFeatureToPlan(plan.id, featureId);
      await loadData();  // Reload
      alert('Feature added successfully!');
    } catch (error: any) {
      alert(`Failed to add feature: ${error.response?.data?.detail || 'Unknown error'}`);
    }
  };

  const handleRemoveFeature = async (featureId: number) => {
    if (!plan) return;

    if (!confirm('Are you sure? This will immediately revoke this feature from all users on this plan.')) {
      return;
    }

    try {
      await featureApi.removeFeatureFromPlan(plan.id, featureId);
      await loadData();  // Reload
      alert('Feature removed successfully!');
    } catch (error: any) {
      alert(`Failed to remove feature: ${error.response?.data?.detail || 'Unknown error'}`);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (!plan) return <div>Plan not found</div>;

  const planFeatureIds = new Set(plan.features.map(f => f.id));
  const availableFeatures = allFeatures.filter(f => !planFeatureIds.has(f.id));

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">
        Manage Features: {plan.display_name}
      </h1>

      {/* Current Features */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-4">Current Features</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {plan.features.map(feature => (
            <div key={feature.id} className="border rounded p-4 bg-green-50">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-semibold">{feature.display_name}</h3>
                  <p className="text-sm text-gray-600">{feature.description}</p>
                  <span className="text-xs text-gray-500">{feature.category}</span>
                </div>
                <button
                  onClick={() => handleRemoveFeature(feature.id)}
                  className="text-red-600 hover:text-red-800"
                  title="Remove feature"
                >
                  ✕
                </button>
              </div>
            </div>
          ))}
        </div>
        {plan.features.length === 0 && (
          <p className="text-gray-500">No features added yet</p>
        )}
      </div>

      {/* Available Features to Add */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Available Features</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {availableFeatures.map(feature => (
            <div key={feature.id} className="border rounded p-4">
              <div className="mb-2">
                <h3 className="font-semibold">{feature.display_name}</h3>
                <p className="text-sm text-gray-600">{feature.description}</p>
                <span className="text-xs text-gray-500">{feature.category}</span>
              </div>
              <button
                onClick={() => handleAddFeature(feature.id)}
                className="mt-2 bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700"
              >
                Add to Plan
              </button>
            </div>
          ))}
        </div>
        {availableFeatures.length === 0 && (
          <p className="text-gray-500">All features are already in this plan</p>
        )}
      </div>
    </div>
  );
}
```

### **Feature Catalog Management**

```typescript
// frontend/src/app/admin/features/page.tsx
'use client';

import { useEffect, useState } from 'react';
import { featureApi } from '@/api/features';
import type { Feature, FeatureCreate } from '@/types/feature';

export default function FeatureCatalogPage() {
  const [features, setFeatures] = useState<Feature[]>([]);
  const [showCreateModal, setShowCreateModal] = useState(false);

  useEffect(() => {
    loadFeatures();
  }, []);

  const loadFeatures = async () => {
    const response = await featureApi.getAllFeatures();
    setFeatures(response.data || []);
  };

  const handleCreateFeature = async (data: FeatureCreate) => {
    try {
      await featureApi.createFeature(data);
      await loadFeatures();
      setShowCreateModal(false);
      alert('Feature created successfully!');
    } catch (error: any) {
      alert(`Failed to create feature: ${error.response?.data?.detail || 'Unknown error'}`);
    }
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Feature Catalog</h1>
        <button
          onClick={() => setShowCreateModal(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded"
        >
          Add New Feature
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {features.map(feature => (
          <div key={feature.id} className="border rounded p-4">
            <h3 className="font-semibold">{feature.display_name}</h3>
            <p className="text-sm text-gray-600">{feature.description}</p>
            <div className="mt-2">
              <span className="text-xs bg-gray-200 px-2 py-1 rounded">{feature.category}</span>
              <span className="text-xs text-gray-500 ml-2">({feature.name})</span>
            </div>
          </div>
        ))}
      </div>

      {/* Create Modal would go here */}
    </div>
  );
}
```

---

## 📡 Frontend API Client

```typescript
// frontend/src/api/features.ts
import { apiClient } from './apiClient';
import type { ApiResponse } from '@/types';
import type {
  Feature,
  FeatureCreate,
  FeatureUpdate,
  PlanWithFeatures,
  PlanFeatureAdd
} from '@/types/feature';

export const featureApi = {
  // Feature Catalog
  async getAllFeatures(): Promise<ApiResponse<Feature[]>> {
    const response = await apiClient.get<Feature[]>('/api/feature-management/features');
    return { data: response.data, success: true };
  },

  async createFeature(data: FeatureCreate): Promise<ApiResponse<Feature>> {
    const response = await apiClient.post<Feature>('/api/feature-management/features', data);
    return { data: response.data, success: true };
  },

  async updateFeature(id: number, data: FeatureUpdate): Promise<ApiResponse<Feature>> {
    const response = await apiClient.put<Feature>(`/api/feature-management/features/${id}`, data);
    return { data: response.data, success: true };
  },

  // Plan Features
  async getPlanWithFeatures(planId: number): Promise<ApiResponse<PlanWithFeatures>> {
    const response = await apiClient.get<PlanWithFeatures>(`/api/feature-management/plans/${planId}/features`);
    return { data: response.data, success: true };
  },

  async addFeatureToPlan(planId: number, featureId: number): Promise<ApiResponse<any>> {
    const response = await apiClient.post(`/api/feature-management/plans/${planId}/features`, {
      feature_id: featureId
    });
    return { data: response.data, success: true };
  },

  async removeFeatureFromPlan(planId: number, featureId: number): Promise<ApiResponse<any>> {
    const response = await apiClient.delete(`/api/feature-management/plans/${planId}/features/${featureId}`);
    return { data: response.data, success: true };
  },
};
```

---

## 🎯 Example Scenario

### **Scenario: System Admin Adds Workflows to Premium**

```
1. System Admin logs in
2. Goes to: Admin > Plans > Premium > Features
3. Sees current features:
   ✅ Interviews
   ✅ Positions
   ✅ Messages
   ✅ Exam Library
   ✅ Exam Administration

4. Clicks "Add Feature"
5. Selects "Workflows" from dropdown
6. Clicks "Add to Plan"

7. System immediately:
   - Adds workflows to premium plan_features table
   - All Premium users can now access workflows
   - Basic users still cannot (workflows not in Basic)

8. To add to Basic:
   - Go to: Admin > Plans > Basic > Features
   - Click "Add Feature"
   - Select "Workflows"
   - Now both plans have workflows
```

---

## ✅ Benefits

| Benefit | Description |
|---------|-------------|
| **Flexibility** | Change features without code deployment |
| **Real-time** | Changes take effect immediately |
| **Granular Control** | Different features for different plans |
| **Easy Management** | Visual UI for system admins |
| **Audit Trail** | Track who added/removed features |
| **Scalable** | Easy to add new features |

---

## 🌳 Hierarchical Feature System (Main Functions & Sub-Functions)

### **Overview**

The system supports **hierarchical features** where main features can have sub-features. This enables granular permission control at the function level.

### **Example Use Case**

**Main Feature**: User Management
**Sub-features**:
- View Users (all plans)
- Deactivate User (Premium only)
- Suspend User (Premium only)
- Delete User (Premium only)

**Main Feature**: Exam Management
**Sub-features**:
- View Exams (Premium only)
- Create Exams (Premium only)
- Edit Exams (Premium only)
- Delete Exams (Premium only)
- Assign Exams (Premium only)

### **Database Schema Updates**

#### **Update `features` Table to Support Hierarchy**

```sql
-- Add parent-child relationship columns
ALTER TABLE features ADD COLUMN parent_feature_id INTEGER REFERENCES features(id) ON DELETE CASCADE;
ALTER TABLE features ADD COLUMN permission_key VARCHAR(100);  -- e.g., 'user_management.deactivate'

CREATE INDEX idx_features_parent_feature_id ON features(parent_feature_id);
CREATE INDEX idx_features_permission_key ON features(permission_key);

-- Seed hierarchical features example
-- Main feature: User Management
INSERT INTO features (name, display_name, description, category, parent_feature_id, permission_key)
VALUES ('user_management', 'User Management', 'User management system', 'core', NULL, 'user_management');

-- Sub-features of User Management
INSERT INTO features (name, display_name, description, category, parent_feature_id, permission_key)
VALUES
('view_users', 'View Users', 'View user list and details', 'core',
 (SELECT id FROM features WHERE name = 'user_management'), 'user_management.view'),

('deactivate_user', 'Deactivate User', 'Deactivate user accounts', 'premium',
 (SELECT id FROM features WHERE name = 'user_management'), 'user_management.deactivate'),

('suspend_user', 'Suspend User', 'Suspend user accounts temporarily', 'premium',
 (SELECT id FROM features WHERE name = 'user_management'), 'user_management.suspend'),

('delete_user', 'Delete User', 'Permanently delete user accounts', 'premium',
 (SELECT id FROM features WHERE name = 'user_management'), 'user_management.delete');

-- Main feature: Exam Management
INSERT INTO features (name, display_name, description, category, parent_feature_id, permission_key)
VALUES ('exam_management', 'Exam Management', 'Exam management system', 'premium', NULL, 'exam_management');

-- Sub-features of Exam Management
INSERT INTO features (name, display_name, description, category, parent_feature_id, permission_key)
VALUES
('view_exams', 'View Exams', 'View exam library', 'premium',
 (SELECT id FROM features WHERE name = 'exam_management'), 'exam_management.view'),

('create_exams', 'Create Exams', 'Create new exams', 'premium',
 (SELECT id FROM features WHERE name = 'exam_management'), 'exam_management.create'),

('edit_exams', 'Edit Exams', 'Edit existing exams', 'premium',
 (SELECT id FROM features WHERE name = 'exam_management'), 'exam_management.edit'),

('delete_exams', 'Delete Exams', 'Delete exams', 'premium',
 (SELECT id FROM features WHERE name = 'exam_management'), 'exam_management.delete'),

('assign_exams', 'Assign Exams', 'Assign exams to candidates', 'premium',
 (SELECT id FROM features WHERE name = 'exam_management'), 'exam_management.assign');
```

### **Updated Feature Model**

```python
# backend/app/models/feature.py
class Feature(Base):
    __tablename__ = "features"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True, index=True)
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    # Hierarchical support
    parent_feature_id = Column(Integer, ForeignKey("features.id"), nullable=True, index=True)
    permission_key = Column(String(100), nullable=True, index=True)  # e.g., 'user_management.deactivate'

    category = Column(String(50), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    parent = relationship(
        "Feature",
        remote_side=[id],
        back_populates="children",
        foreign_keys=[parent_feature_id]
    )
    children = relationship(
        "Feature",
        back_populates="parent",
        cascade="all, delete-orphan",
        foreign_keys=[parent_feature_id]
    )
    plan_features = relationship("PlanFeature", back_populates="feature", cascade="all, delete-orphan")
```

### **Permission Checking with Hierarchical Features**

#### **Check Permission by Key**

```python
# backend/app/utils/permissions.py
async def check_permission(
    db: AsyncSession,
    company_id: int,
    permission_key: str
) -> tuple[bool, Optional[str]]:
    """
    Check if company has permission based on hierarchical permission key.

    Examples:
    - permission_key = 'user_management.deactivate'
    - permission_key = 'exam_management.create'
    """
    # Get company subscription
    subscription = await subscription_crud.get_by_company_id(db, company_id=company_id)
    if not subscription or not subscription.is_active:
        return False, "No active subscription"

    # Check if plan has feature with this permission key
    result = await db.execute(
        select(PlanFeature)
        .join(Feature)
        .where(PlanFeature.plan_id == subscription.plan_id)
        .where(Feature.permission_key == permission_key)
        .where(Feature.is_active == True)
    )

    if result.scalar_one_or_none():
        return True, None

    return False, f"Permission '{permission_key}' not available in your plan"
```

#### **Usage in Endpoints**

```python
# backend/app/endpoints/user.py
@router.delete("/users/{user_id}")
async def deactivate_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Deactivate a user (Premium feature - user_management.deactivate)."""

    # Check permission
    has_permission, error_msg = await check_permission(
        db,
        company_id=current_user.company_id,
        permission_key="user_management.deactivate"
    )

    if not has_permission:
        raise HTTPException(status_code=403, detail=error_msg)

    # Proceed with deactivation
    return await user_crud.deactivate(db, user_id=user_id)
```

### **Frontend: Hierarchical Feature Display**

#### **Feature Tree Component**

```typescript
// frontend/src/components/admin/FeatureTree.tsx
interface FeatureNode {
  id: number;
  name: string;
  display_name: string;
  permission_key?: string;
  children: FeatureNode[];
}

export default function FeatureTree({ features, planId }: Props) {
  const renderFeature = (feature: FeatureNode, level = 0) => (
    <div key={feature.id} style={{ marginLeft: level * 20 + 'px' }}>
      <div className="flex items-center gap-2 py-2">
        {feature.children.length > 0 && <ChevronIcon />}
        <span className="font-medium">{feature.display_name}</span>
        {feature.permission_key && (
          <code className="text-xs bg-gray-100 px-2 py-1 rounded">
            {feature.permission_key}
          </code>
        )}
        <button onClick={() => addFeatureToPlan(planId, feature.id)}>
          Add to Plan
        </button>
      </div>

      {/* Render children */}
      {feature.children.map(child => renderFeature(child, level + 1))}
    </div>
  );

  return (
    <div className="feature-tree">
      {features.map(feature => renderFeature(feature))}
    </div>
  );
}
```

### **System Admin Workflow**

#### **Scenario: Add "Deactivate User" to Premium Only**

1. **System Admin** goes to Admin > Plan Management > Premium
2. Sees hierarchical feature tree:
   ```
   📁 User Management
      ├─ ✅ View Users (already in Premium)
      ├─ ➕ Deactivate User (add this)
      ├─ ➕ Suspend User
      └─ ➕ Delete User
   ```
3. Clicks "Add" next to "Deactivate User"
4. Confirms addition
5. **Result**:
   - Premium users can now deactivate users
   - Basic users still cannot deactivate users
   - Permission check: `user_management.deactivate`

#### **Scenario: Remove Sub-feature from Plan**

1. **System Admin** goes to Basic plan features
2. Sees:
   ```
   📁 User Management
      ├─ ✅ View Users (in plan)
      ├─ ❌ Deactivate User (not in plan)
   ```
3. Can selectively add/remove sub-features
4. Changes take effect immediately

### **Benefits of Hierarchical Features**

| Benefit | Description |
|---------|-------------|
| **Granular Control** | Control permissions at the function level |
| **Easy to Understand** | Clear parent-child relationship |
| **Flexible** | Mix and match sub-features across plans |
| **Organized** | Features grouped logically |
| **Scalable** | Easy to add new sub-features |
| **Permission Keys** | Dot notation for easy permission checking |

### **Example Feature Hierarchy**

```
📁 User Management (user_management)
   ├─ View Users (user_management.view) - Basic + Premium
   ├─ Create Users (user_management.create) - Basic + Premium
   ├─ Deactivate User (user_management.deactivate) - Premium only
   ├─ Suspend User (user_management.suspend) - Premium only
   └─ Delete User (user_management.delete) - Premium only

📁 Exam Management (exam_management) - Premium only
   ├─ View Exams (exam_management.view) - Premium only
   ├─ Create Exams (exam_management.create) - Premium only
   ├─ Edit Exams (exam_management.edit) - Premium only
   ├─ Delete Exams (exam_management.delete) - Premium only
   └─ Assign Exams (exam_management.assign) - Premium only

📁 Workflow Management (workflow_management)
   ├─ View Workflows (workflow_management.view) - Basic + Premium
   ├─ Create Workflows (workflow_management.create) - Basic + Premium
   ├─ Edit Workflows (workflow_management.edit) - Basic + Premium
   └─ Delete Workflows (workflow_management.delete) - Basic + Premium

📁 Analytics (analytics)
   ├─ Basic Reports (analytics.basic) - Basic + Premium
   └─ Advanced Analytics (analytics.advanced) - Premium only
```

---

## 📋 Implementation Checklist

### **Backend**
- [ ] Create `features` table migration
- [ ] Add hierarchical columns to `features` table (parent_feature_id, permission_key)
- [ ] Create `plan_features` junction table migration
- [ ] Create `Feature` model with parent-child relationships
- [ ] Create `PlanFeature` model
- [ ] Update `SubscriptionPlan` model with relationships
- [ ] Create feature schemas with hierarchical support (FeatureWithChildren)
- [ ] Create feature CRUD operations with hierarchical queries
- [ ] Create plan-feature CRUD operations with hierarchical methods
- [ ] Create feature management endpoints (6 endpoints)
- [ ] Create permission checking utility (check_permission with permission_key)
- [ ] Update permission checks to use dynamic features
- [ ] Seed initial features (flat structure)
- [ ] Seed hierarchical features (main + sub-features)
- [ ] Add tests for hierarchical feature queries
- [ ] Add tests for permission key checking

### **Frontend**
- [ ] Create feature types with hierarchical support (FeatureNode)
- [ ] Create feature API client
- [ ] Create Feature Catalog page (System Admin)
- [ ] Create hierarchical FeatureTree component
- [ ] Create Plan Features Management page (System Admin)
- [ ] Display features in hierarchical tree structure
- [ ] Create Add Feature modal (supports adding main or sub-features)
- [ ] Create Remove Feature confirmation
- [ ] Add expand/collapse for feature tree
- [ ] Add permission key display
- [ ] Add loading states
- [ ] Add error handling
- [ ] Add success notifications

---

## 🚀 Quick Start

1. **Run migrations** to create `features` and `plan_features` tables
2. **Seed features** with initial catalog
3. **Assign features to plans** (Basic and Premium)
4. **Access feature management** at `/admin/plans/{planId}/features`
5. **Add/remove features** dynamically

The system is now fully dynamic and requires no code changes to modify plan features!

