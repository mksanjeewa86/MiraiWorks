# Test Transaction Isolation Issue - CRITICAL BUG

## 🚨 **Root Cause:**
The account activation tests are failing because of **database session isolation**:

1. **Test session**: Uses `db_session` fixture
2. **API endpoint**: Uses separate session from `get_db()` dependency
3. **Result**: Changes in API session are not visible to test session

## 🔍 **Evidence:**
- API logs: `"User account activated successfully"` ✅
- Response JSON: `"is_active": true` ✅
- Database query: `is_active=False` ❌

## 💡 **Solution Options:**

### **Option 1: Override Database Dependency (Recommended)**
```python
# In test file, override the get_db dependency to use same session
from app.database import get_db

async def override_get_db_with_test_session(db_session):
    yield db_session

# Apply override in test
app.dependency_overrides[get_db] = lambda: override_get_db_with_test_session(db_session)
```

### **Option 2: Manual Transaction Management**
```python
# Force commit and fresh query
await db_session.commit()
await db_session.begin()  # Start new transaction
result = await db_session.execute(select(User).where(User.id == user.id))
updated_user = result.scalar_one()
```

### **Option 3: Database-Level Query (Bypass Session)**
```python
# Direct database query
from app.database import test_engine
async with test_engine.begin() as conn:
    result = await conn.execute(select(User).where(User.id == user.id))
    updated_user = result.fetchone()
```

## 🎯 **Recommended Fix:**
Use **shared session approach** for activation tests.