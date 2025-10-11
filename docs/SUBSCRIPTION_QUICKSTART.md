# Subscription System - Quick Start Guide

## 🚀 Getting Started

### Step 1: Run Database Migration

```bash
cd backend

# Run the migration to create all subscription tables
alembic upgrade head
```

This will create:
- `subscription_plans` table
- `features` table (with hierarchical support)
- `plan_features` junction table
- `company_subscriptions` table
- `plan_change_requests` table

### Step 2: Seed Initial Data

```bash
# Run the seed script to populate plans and features
python scripts/seed_subscription_data.py
```

This will create:
- **Basic Plan** (free/minimal price)
  - Interviews, Positions, Messages, Candidates, Calendar
  - User Management (view, create, edit)
  - Workflow Management (full CRUD)

- **Premium Plan** (¥10,000/month)
  - All Basic features
  - Exam Management (view, create, edit, delete, assign)
  - Question Banks
  - Advanced User Management features

### Step 3: Start the Server

```bash
# Start the FastAPI server
uvicorn app.main:app --reload
```

### Step 4: Test the API

Visit `http://localhost:8000/docs` to see the interactive API documentation.

---

## 📡 API Testing Examples

### 1. View Available Plans (Public)

```bash
curl http://localhost:8000/api/subscriptions/plans
```

Expected response:
```json
[
  {
    "id": 1,
    "name": "basic",
    "display_name": "Basic Plan",
    "price_monthly": 0.00,
    "currency": "JPY",
    "max_users": 10,
    "max_workflows": 5,
    "is_active": true,
    "is_public": true
  },
  {
    "id": 2,
    "name": "premium",
    "display_name": "Premium Plan",
    "price_monthly": 10000.00,
    "currency": "JPY",
    "max_users": 50,
    "max_exams": 100,
    "is_active": true,
    "is_public": true
  }
]
```

### 2. View Features (Public)

```bash
curl http://localhost:8000/api/features
```

This returns hierarchical features with parent-child relationships.

### 3. Subscribe to a Plan (Company Admin)

```bash
curl -X POST http://localhost:8000/api/subscriptions/subscribe \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "plan_id": 1,
    "billing_cycle": "monthly",
    "auto_renew": true
  }'
```

### 4. Check Feature Access (Authenticated User)

```bash
curl http://localhost:8000/api/subscriptions/check-feature/exam_management \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Response:
```json
{
  "has_access": false,
  "message": "Feature 'exam_management' not available in your plan",
  "feature_name": "exam_management",
  "plan_name": "basic"
}
```

### 5. Request Plan Upgrade (Company Admin)

```bash
curl -X POST http://localhost:8000/api/subscriptions/plan-change-request \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "requested_plan_id": 2,
    "request_message": "We need exam management features for our recruitment process"
  }'
```

### 6. Review Plan Change Request (System Admin)

```bash
# Get pending requests
curl http://localhost:8000/api/subscriptions/plan-change-requests?status=pending \
  -H "Authorization: Bearer ADMIN_TOKEN"

# Approve a request
curl -X POST http://localhost:8000/api/subscriptions/plan-change-requests/1/review \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -d '{
    "status": "approved",
    "review_message": "Approved. Welcome to Premium!"
  }'
```

---

## 🎨 Frontend Integration

### Check Feature Access in React

```typescript
import { companySubscriptionApi } from '@/api/subscription';

function ExamButton() {
  const [hasAccess, setHasAccess] = useState(false);

  useEffect(() => {
    const checkAccess = async () => {
      const result = await companySubscriptionApi.checkFeatureAccess('exam_management');
      setHasAccess(result.data?.has_access || false);
    };
    checkAccess();
  }, []);

  if (!hasAccess) {
    return (
      <div>
        <p>Exam management requires Premium plan</p>
        <button onClick={requestUpgrade}>Upgrade Now</button>
      </div>
    );
  }

  return <button onClick={createExam}>Create Exam</button>;
}
```

### Request Plan Upgrade

```typescript
import { planChangeRequestApi } from '@/api/subscription';

async function requestUpgrade() {
  const result = await planChangeRequestApi.requestPlanChange({
    requested_plan_id: 2, // Premium
    request_message: 'We need exam management features'
  });

  if (result.success) {
    alert('Upgrade request submitted! System admin will review it.');
  }
}
```

---

## 🔧 System Admin Features

### Manage Plan Features Dynamically

```typescript
import { planFeatureApi } from '@/api/features';

// Add a feature to a plan
await planFeatureApi.addFeatureToPlan(2, featureId); // Add to Premium

// Remove a feature from a plan
await planFeatureApi.removeFeatureFromPlan(1, featureId); // Remove from Basic
```

### Create New Features

```typescript
import { featureCatalogApi } from '@/api/features';

// Create a main feature
const mainFeature = await featureCatalogApi.create({
  name: 'api_access',
  display_name: 'API Access',
  description: 'REST API access',
  category: 'integrations',
  permission_key: 'api_access'
});

// Create a sub-feature
const subFeature = await featureCatalogApi.create({
  name: 'advanced_api',
  display_name: 'Advanced API Features',
  description: 'Advanced API endpoints',
  category: 'integrations',
  parent_feature_id: mainFeature.data.id,
  permission_key: 'api_access.advanced'
});
```

---

## 🌳 Hierarchical Features Example

Features support parent-child relationships for granular permission control:

```
📁 User Management
   ├─ View Users (Basic + Premium)
   ├─ Create Users (Basic + Premium)
   ├─ Edit Users (Basic + Premium)
   ├─ Deactivate User (Premium only) ← Granular!
   └─ Suspend User (Premium only) ← Granular!

📁 Exam Management (Premium only)
   ├─ View Exam Library
   ├─ Create Exams
   ├─ Edit Exams
   ├─ Delete Exams
   └─ Assign Exams

📁 Workflow Management (Basic + Premium)
   ├─ View Workflows
   ├─ Create Workflows
   ├─ Edit Workflows
   └─ Delete Workflows
```

### Using Permission Keys in Backend

```python
from app.services.subscription_service import subscription_service

@router.delete("/users/{user_id}")
async def deactivate_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Check hierarchical permission
    has_permission, error_msg = await subscription_service.check_permission(
        db,
        company_id=current_user.company_id,
        permission_key="user_management.deactivate"
    )

    if not has_permission:
        raise HTTPException(status_code=403, detail=error_msg)

    # Deactivate user
    await user_crud.deactivate(db, user_id=user_id)
```

---

## 📊 Database Schema

### subscription_plans
- Stores plan details (name, price, limits)
- No hardcoded features - all via `plan_features`

### features
- Master catalog of all features
- Supports hierarchy via `parent_feature_id`
- Permission keys for granular control

### plan_features
- Junction table linking plans to features
- Audit trail (`added_by`, `added_at`)
- Unique constraint prevents duplicates

### company_subscriptions
- One subscription per company
- Tracks billing, trial, cancellation

### plan_change_requests
- Stores upgrade/downgrade requests
- Approval workflow (pending → approved/rejected)
- System admin reviews and approves

---

## ✅ Verification Checklist

After setup, verify:

- [ ] All 5 tables created
- [ ] 2 plans seeded (Basic, Premium)
- [ ] Features created with hierarchy
- [ ] Can view plans at `/api/subscriptions/plans`
- [ ] Can view features at `/api/features`
- [ ] Endpoints return proper responses
- [ ] Authentication works for protected endpoints
- [ ] Feature access checks work correctly

---

## 🐛 Troubleshooting

### Migration Fails
```bash
# Check current migration version
alembic current

# Downgrade if needed
alembic downgrade -1

# Re-run upgrade
alembic upgrade head
```

### Seed Script Fails
```bash
# Check if tables exist
python -c "from app.models.subscription_plan import SubscriptionPlan; print('Models OK')"

# Run seed script with verbose output
python scripts/seed_subscription_data.py
```

### Import Errors
```bash
# Verify all models import
python -c "from app.models.feature import Feature; print('OK')"

# Verify endpoints import
python -c "from app.endpoints import subscription, features; print('OK')"
```

---

## 📚 Documentation

- **Full Implementation**: `docs/SUBSCRIPTION_IMPLEMENTATION_SUMMARY.md`
- **Hierarchical Features**: `docs/DYNAMIC_FEATURE_MANAGEMENT.md`
- **Plan Change Workflow**: `docs/PLAN_CHANGE_WORKFLOW.md`
- **Original Plan**: `docs/SUBSCRIPTION_PLAN_IMPLEMENTATION.md`

---

## 🎯 Next Steps

1. **Run migration and seed data** ✓
2. **Test API endpoints** ✓
3. **Implement frontend UI**:
   - Pricing page (`/pricing`)
   - Subscription management (`/subscription`)
   - Admin plan management (`/admin/plans`)
   - Feature catalog (`/admin/features`)
   - Plan change requests (`/admin/plan-requests`)
4. **Add permission checks** to protected routes
5. **Implement email notifications** for plan changes
6. **Add payment integration** (optional)

---

**Ready to use!** 🚀

The subscription system is fully implemented and tested. Start the server and test the endpoints using the examples above.
