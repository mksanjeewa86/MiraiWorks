# Remove user_connections Immediately (HIGH RISK)

## ⚠️ WARNING: This will break existing features!

Only do this if you:
- Don't need messaging to work right now
- Are ready to implement company_connections immediately
- Understand you can't send messages until new system is ready

---

## 🗑️ Removal Steps

### Step 1: Disable Message Validation

```python
# backend/app/endpoints/messages.py

async def validate_messaging_permission(
    db: AsyncSession, sender_id: int, recipient_id: int
):
    """Validate that sender can message recipient."""
    # TEMPORARY: Skip validation until company_connections is implemented
    # TODO: Replace with company_connection_service.can_users_interact()
    pass  # Allow all messages temporarily
```

### Step 2: Disable User Connection Endpoints

```python
# backend/app/routers.py

def include_routers(app: FastAPI) -> None:
    # ... other routers ...

    # DISABLED: user_connections endpoints
    # app.include_router(
    #     user_connections.router,
    #     prefix="/api/user/connections",
    #     tags=["user-connections"],
    # )
```

### Step 3: Drop Database Table

```sql
-- Backup first (just in case)
CREATE TABLE user_connections_backup AS SELECT * FROM user_connections;

-- Drop the table
DROP TABLE user_connections;
```

### Step 4: Remove Python Files

```bash
# Remove model
rm backend/app/models/user_connection.py

# Remove service
rm backend/app/services/user_connection_service.py

# Remove endpoints
rm backend/app/endpoints/user_connections.py

# Remove from seed data
# Edit: backend/app/seeds/users_and_companies.py
# Remove any user_connection creation
```

### Step 5: Update Frontend

```typescript
// frontend/src/api/userConnections.ts
// Comment out or remove this file temporarily

// Update messages page to not show "connect" button
// Since connections don't exist yet
```

---

## 🚨 What Won't Work:

- ❌ Sending messages between users
- ❌ Viewing connected users
- ❌ Managing user connections
- ❌ Assigning todos to connected users

---

## ✅ What to Do Next:

1. **Immediately start implementing company_connections**
2. Follow `MIGRATION_PLAN_COMPANY_CONNECTIONS.md`
3. Implement Phase 1 (schema + models) ASAP
4. Implement Phase 2 (message validation)
5. Re-enable messaging with new system

**Estimated Time to Restore Functionality:** 3-5 days minimum

---

## 🔄 Recommended Alternative:

**Keep user_connections and run BOTH systems in parallel:**

1. Create `company_connections` table (doesn't conflict)
2. Implement new system
3. Migrate data: `user_connections` → `company_connections`
4. Switch over with feature flag
5. Remove `user_connections` when 100% confident

This gives you:
- ✅ Zero downtime
- ✅ Easy rollback
- ✅ Time to test
- ✅ Gradual migration
