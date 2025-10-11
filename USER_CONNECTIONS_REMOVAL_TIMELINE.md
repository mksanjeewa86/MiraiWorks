# user_connections Table Removal Timeline

## 📅 Complete Removal Process

### Phase 1: Creation (Week 1-2) ✅
**Status**: Create new system while keeping old
```sql
-- Old table stays untouched
user_connections ✅ (still active)

-- New table created
CREATE TABLE company_connections ✅
```

---

### Phase 2: Migration (Week 2-3) 🔄
**Status**: Migrate data, run both systems in parallel
```python
# Migrate data from old → new
user_connections → company_connections

# Both tables exist
user_connections ✅ (legacy, read-only)
company_connections ✅ (active)
```

**Feature Flag**:
```python
USE_COMPANY_CONNECTIONS = True  # Switch to new system

# But old table still exists for rollback
```

---

### Phase 3: Testing Period (Week 4-5) 🧪
**Status**: New system active, old table as backup
```sql
user_connections ✅ (backup only, no writes)
company_connections ✅ (active system)
```

**What happens**:
- ✅ All NEW connections go to `company_connections`
- ✅ All reads from `company_connections`
- ✅ `user_connections` sits idle as backup
- ✅ Monitor for any issues

---

### Phase 4: Safety Period (Week 6-7) ⏳
**Status**: 30-day safety window
```sql
user_connections ✅ (backup, untouched)
company_connections ✅ (fully active)
```

**Purpose**:
- Allow time to catch any bugs
- Ensure no data loss
- Verify all features work
- Give time for rollback if needed

---

### Phase 5: **FINAL REMOVAL** (Week 8+) 🗑️
**Status**: Old table deleted permanently

```sql
-- Backup one last time (just in case)
CREATE TABLE user_connections_archive_2025_10_11 AS
SELECT * FROM user_connections;

-- Drop the old table
DROP TABLE user_connections; ✅ REMOVED
```

**Also remove**:
```bash
# Delete Python files
rm backend/app/models/user_connection.py
rm backend/app/services/user_connection_service.py
rm backend/app/endpoints/user_connections.py

# Remove from routers
# Edit backend/app/routers.py - remove user_connections routes

# Clean up imports
# Remove from backend/app/models/__init__.py
```

---

## 📊 Visual Timeline

```
Week 1-2: Create company_connections
          ├─ user_connections ✅ (active)
          └─ company_connections ✅ (new)

Week 3:   Migrate data
          ├─ user_connections ✅ (legacy)
          └─ company_connections ✅ (active)

Week 4-7: Testing + Safety period (30 days)
          ├─ user_connections ✅ (backup only)
          └─ company_connections ✅ (active)

Week 8+:  REMOVE old table
          ├─ user_connections ❌ DELETED
          └─ company_connections ✅ (only system)
```

---

## ✅ Final State (After Week 8)

### Database Tables:
```sql
-- REMOVED
❌ user_connections (deleted)

-- ACTIVE
✅ company_connections (only connection table)
```

### Backend Code:
```python
# REMOVED FILES
❌ app/models/user_connection.py
❌ app/services/user_connection_service.py
❌ app/endpoints/user_connections.py

# ACTIVE FILES
✅ app/models/company_connection.py
✅ app/services/company_connection_service.py
✅ app/endpoints/company_connections.py
```

---

## 🚨 Why Keep for 30 Days?

1. **Safety Net** 🛡️
   - If something goes wrong, can rollback
   - No data loss risk

2. **Bug Detection** 🐛
   - Gives time to find edge cases
   - Users report issues during normal usage

3. **Verification** ✅
   - Confirm all features work with new system
   - Ensure performance is good
   - Check no regressions

4. **Peace of Mind** 😌
   - Less stressful migration
   - Can revert if needed

---

## 🗑️ Final Removal Checklist

Before dropping `user_connections`, verify:

- [ ] ✅ company_connections has been live for 30+ days
- [ ] ✅ No bugs reported related to connections
- [ ] ✅ All messaging features working correctly
- [ ] ✅ All todo assignment features working
- [ ] ✅ Performance metrics acceptable
- [ ] ✅ Backup of old table created (archive)
- [ ] ✅ Team approval obtained
- [ ] ✅ Rollback plan no longer needed

---

## 📝 Removal Script

```python
# backend/scripts/remove_user_connections_final.py
"""
Final removal of user_connections table.
Run this after 30 days of successful company_connections usage.
"""

async def remove_user_connections_table(db: AsyncSession):
    """
    Permanently remove user_connections table.

    Prerequisites:
    - company_connections has been live for 30+ days
    - No issues reported
    - All stakeholders approve
    """

    # 1. Create final backup
    await db.execute(text("""
        CREATE TABLE user_connections_archive_final AS
        SELECT * FROM user_connections
    """))

    # 2. Drop the table
    await db.execute(text("DROP TABLE user_connections"))

    # 3. Clean up references
    # Update any remaining code references

    await db.commit()

    print("✅ user_connections table removed successfully")
    print("✅ Backup saved as: user_connections_archive_final")
```

---

## 🎯 Summary

**Question**: "Will user_connections be removed?"

**Answer**: **YES! But not immediately.**

**Timeline**:
1. **Weeks 1-3**: Both tables exist (migration period)
2. **Weeks 4-7**: Old table as backup only (30-day safety)
3. **Week 8+**: **Old table DELETED permanently**

**Final Result**: Only `company_connections` remains ✅

---

**Last Updated**: 2025-10-11
**Status**: Removal planned for Week 8+
