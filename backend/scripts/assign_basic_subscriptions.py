"""
Assign Basic plan to all companies without an active subscription.
This script should be run once to fix existing companies.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select

from app.database import get_db, init_db
from app.models.company import Company
from app.models.company_subscription import CompanySubscription
from app.models.subscription_plan import SubscriptionPlan
from app.utils.datetime_utils import get_utc_now


async def assign_basic_subscriptions():
    """Assign Basic plan to all companies without active subscriptions."""
    await init_db()

    async for db in get_db():
        try:
            # Get Basic plan
            result = await db.execute(
                select(SubscriptionPlan).where(SubscriptionPlan.name == "basic")
            )
            basic_plan = result.scalar_one_or_none()

            if not basic_plan:
                print("[ERROR] Basic plan not found in database!")
                return

            print(f"[OK] Found Basic plan (ID: {basic_plan.id})")

            # Get all companies
            result = await db.execute(select(Company))
            companies = result.scalars().all()

            print(f"[INFO] Total companies: {len(companies)}")

            # Track results
            created_count = 0
            skipped_count = 0

            for company in companies:
                # Check if company already has an active subscription
                result = await db.execute(
                    select(CompanySubscription)
                    .where(CompanySubscription.company_id == company.id)
                    .where(CompanySubscription.is_active is True)
                )
                existing_subscription = result.scalar_one_or_none()

                if existing_subscription:
                    print(
                        f"[SKIP] {company.name} (ID: {company.id}) - already has subscription"
                    )
                    skipped_count += 1
                    continue

                # Create Basic subscription
                subscription = CompanySubscription(
                    company_id=company.id,
                    plan_id=basic_plan.id,
                    is_active=True,
                    is_trial=False,
                    start_date=get_utc_now(),
                    billing_cycle="monthly",
                    auto_renew=True,
                )

                db.add(subscription)
                print(f"[CREATED] {company.name} (ID: {company.id}) -> Basic plan")
                created_count += 1

            # Commit all subscriptions
            await db.commit()

            print("\n" + "=" * 60)
            print("Summary:")
            print(f"   - Created: {created_count} subscriptions")
            print(f"   - Skipped: {skipped_count} companies (already had subscription)")
            print(f"   - Total: {len(companies)} companies")
            print("=" * 60)

        except Exception as e:
            print(f"[ERROR] {e}")
            await db.rollback()
            raise
        finally:
            await db.close()


if __name__ == "__main__":
    print("Starting Basic subscription assignment...")
    print("-" * 60)
    asyncio.run(assign_basic_subscriptions())
    print("\nDone!")
