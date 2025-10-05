"""
Seed script for subscription plans and features.
Initializes the subscription system with Basic and Premium plans and their features.

Usage:
    python scripts/seed_subscription_data.py
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.feature import Feature
from app.models.plan_feature import PlanFeature
from app.models.subscription_plan import SubscriptionPlan


async def create_subscription_plans(db: AsyncSession):
    """Create Basic and Premium subscription plans."""
    print("Creating subscription plans...")

    # Check if plans already exist
    result = await db.execute(select(SubscriptionPlan))
    existing_plans = result.scalars().all()

    if existing_plans:
        print(f"  Found {len(existing_plans)} existing plans. Skipping plan creation.")
        return existing_plans

    # Create Basic Plan
    basic_plan = SubscriptionPlan(
        name="basic",
        display_name="Basic Plan",
        description="Essential features for small teams",
        price_monthly=0.00,  # Free or minimal price
        price_yearly=0.00,
        currency="JPY",
        max_users=10,
        max_workflows=5,
        is_active=True,
        is_public=True,
        display_order=1,
    )
    db.add(basic_plan)

    # Create Premium Plan
    premium_plan = SubscriptionPlan(
        name="premium",
        display_name="Premium Plan",
        description="Advanced features for growing teams",
        price_monthly=10000.00,
        price_yearly=100000.00,
        currency="JPY",
        max_users=50,
        max_exams=100,
        max_workflows=20,
        max_storage_gb=100,
        is_active=True,
        is_public=True,
        display_order=2,
    )
    db.add(premium_plan)

    await db.commit()
    await db.refresh(basic_plan)
    await db.refresh(premium_plan)

    print(f"  [OK] Created Basic Plan (ID: {basic_plan.id})")
    print(f"  [OK] Created Premium Plan (ID: {premium_plan.id})")

    return [basic_plan, premium_plan]


async def create_features(db: AsyncSession):
    """Create hierarchical features catalog."""
    print("\nCreating features catalog...")

    # Check if features already exist
    result = await db.execute(select(Feature))
    existing_features = result.scalars().all()

    if existing_features:
        print(f"  Found {len(existing_features)} existing features. Skipping feature creation.")
        return existing_features

    # Core features (available in all plans)
    core_features = [
        Feature(
            name="interviews",
            display_name="Interviews",
            description="Schedule and manage interviews",
            category="core",
            permission_key="interviews",
        ),
        Feature(
            name="positions",
            display_name="Positions",
            description="Job position management",
            category="core",
            permission_key="positions",
        ),
        Feature(
            name="messages",
            display_name="Messages",
            description="Internal messaging system",
            category="core",
            permission_key="messages",
        ),
        Feature(
            name="candidates",
            display_name="Candidates",
            description="Candidate management",
            category="core",
            permission_key="candidates",
        ),
        Feature(
            name="calendar",
            display_name="Calendar",
            description="Calendar and scheduling",
            category="core",
            permission_key="calendar",
        ),
    ]

    # User Management (hierarchical)
    user_mgmt = Feature(
        name="user_management",
        display_name="User Management",
        description="User management system",
        category="core",
        permission_key="user_management",
    )
    db.add(user_mgmt)
    await db.flush()  # Get ID for parent reference

    user_mgmt_subfeatures = [
        Feature(
            name="view_users",
            display_name="View Users",
            description="View user list and details",
            category="core",
            parent_feature_id=user_mgmt.id,
            permission_key="user_management.view",
        ),
        Feature(
            name="create_users",
            display_name="Create Users",
            description="Create new user accounts",
            category="core",
            parent_feature_id=user_mgmt.id,
            permission_key="user_management.create",
        ),
        Feature(
            name="edit_users",
            display_name="Edit Users",
            description="Edit user accounts",
            category="core",
            parent_feature_id=user_mgmt.id,
            permission_key="user_management.edit",
        ),
    ]

    # Workflow Management
    workflow_mgmt = Feature(
        name="workflow_management",
        display_name="Workflow Management",
        description="Recruitment workflow automation",
        category="core",
        permission_key="workflow_management",
    )
    db.add(workflow_mgmt)
    await db.flush()

    workflow_subfeatures = [
        Feature(
            name="view_workflows",
            display_name="View Workflows",
            description="View workflow list",
            category="core",
            parent_feature_id=workflow_mgmt.id,
            permission_key="workflow_management.view",
        ),
        Feature(
            name="create_workflows",
            display_name="Create Workflows",
            description="Create new workflows",
            category="core",
            parent_feature_id=workflow_mgmt.id,
            permission_key="workflow_management.create",
        ),
        Feature(
            name="edit_workflows",
            display_name="Edit Workflows",
            description="Edit existing workflows",
            category="core",
            parent_feature_id=workflow_mgmt.id,
            permission_key="workflow_management.edit",
        ),
        Feature(
            name="delete_workflows",
            display_name="Delete Workflows",
            description="Delete workflows",
            category="core",
            parent_feature_id=workflow_mgmt.id,
            permission_key="workflow_management.delete",
        ),
    ]

    # Exam Management (Premium)
    exam_mgmt = Feature(
        name="exam_management",
        display_name="Exam Management",
        description="Exam management system",
        category="premium",
        permission_key="exam_management",
    )
    db.add(exam_mgmt)
    await db.flush()

    exam_subfeatures = [
        Feature(
            name="view_exams",
            display_name="View Exam Library",
            description="View exam library and browse exams",
            category="premium",
            parent_feature_id=exam_mgmt.id,
            permission_key="exam_management.view",
        ),
        Feature(
            name="create_exams",
            display_name="Create Exams",
            description="Create new exams",
            category="premium",
            parent_feature_id=exam_mgmt.id,
            permission_key="exam_management.create",
        ),
        Feature(
            name="edit_exams",
            display_name="Edit Exams",
            description="Edit existing exams",
            category="premium",
            parent_feature_id=exam_mgmt.id,
            permission_key="exam_management.edit",
        ),
        Feature(
            name="delete_exams",
            display_name="Delete Exams",
            description="Delete exams",
            category="premium",
            parent_feature_id=exam_mgmt.id,
            permission_key="exam_management.delete",
        ),
        Feature(
            name="assign_exams",
            display_name="Assign Exams",
            description="Assign exams to candidates",
            category="premium",
            parent_feature_id=exam_mgmt.id,
            permission_key="exam_management.assign",
        ),
    ]

    # Question Banks (Premium)
    question_banks = Feature(
        name="question_banks",
        display_name="Question Banks",
        description="Manage exam question banks",
        category="premium",
        permission_key="question_banks",
    )

    # Add all features
    for feature in core_features:
        db.add(feature)

    for feature in user_mgmt_subfeatures:
        db.add(feature)

    for feature in workflow_subfeatures:
        db.add(feature)

    for feature in exam_subfeatures:
        db.add(feature)

    db.add(question_banks)

    await db.commit()
    print(f"  [OK] Created {len(core_features) + len(user_mgmt_subfeatures) + len(workflow_subfeatures) + len(exam_subfeatures) + 4} features")

    # Return all features
    result = await db.execute(select(Feature))
    return result.scalars().all()


async def assign_features_to_plans(
    db: AsyncSession, plans: list[SubscriptionPlan], features: list[Feature]
):
    """Assign features to plans based on plan type."""
    print("\nAssigning features to plans...")

    # Find plans
    basic_plan = next((p for p in plans if p.name == "basic"), None)
    premium_plan = next((p for p in plans if p.name == "premium"), None)

    if not basic_plan or not premium_plan:
        print("  [ERROR] Plans not found. Cannot assign features.")
        return

    # Basic Plan Features
    basic_feature_names = [
        "interviews",
        "positions",
        "messages",
        "candidates",
        "calendar",
        "user_management",
        "view_users",
        "create_users",
        "edit_users",
        "workflow_management",
        "view_workflows",
        "create_workflows",
        "edit_workflows",
        "delete_workflows",
    ]

    # Premium Plan Features (includes all Basic + exam features)
    premium_feature_names = basic_feature_names + [
        "exam_management",
        "view_exams",
        "create_exams",
        "edit_exams",
        "delete_exams",
        "assign_exams",
        "question_banks",
    ]

    # Assign to Basic Plan
    basic_count = 0
    for feature in features:
        if feature.name in basic_feature_names:
            plan_feature = PlanFeature(
                plan_id=basic_plan.id,
                feature_id=feature.id,
            )
            db.add(plan_feature)
            basic_count += 1

    # Assign to Premium Plan
    premium_count = 0
    for feature in features:
        if feature.name in premium_feature_names:
            plan_feature = PlanFeature(
                plan_id=premium_plan.id,
                feature_id=feature.id,
            )
            db.add(plan_feature)
            premium_count += 1

    await db.commit()
    print(f"  [OK] Assigned {basic_count} features to Basic Plan")
    print(f"  [OK] Assigned {premium_count} features to Premium Plan")


async def main():
    """Run seed script."""
    print("=" * 60)
    print("Subscription System Seed Data")
    print("=" * 60)

    async with AsyncSessionLocal() as db:
        try:
            # Create plans
            plans = await create_subscription_plans(db)

            # Create features
            features = await create_features(db)

            # Assign features to plans
            await assign_features_to_plans(db, plans, features)

            print("\n" + "=" * 60)
            print("[SUCCESS] Seed data completed successfully!")
            print("=" * 60)
            print("\nSummary:")
            print(f"  - Plans created: {len(plans)}")
            print(f"  - Features created: {len(features)}")
            print("\nYou can now:")
            print("  - View plans at: GET /api/subscriptions/plans")
            print("  - View features at: GET /api/features")
            print("  - Subscribe companies to plans via API")

        except Exception as e:
            print(f"\n[ERROR] Error during seed: {str(e)}")
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())
