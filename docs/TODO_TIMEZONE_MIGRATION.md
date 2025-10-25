# TODO: Complete Timezone Migration for Todos

## Current Status

The timezone migration implementation is **95% complete** but the database migration is **stuck/slow**.

### What's Already Done ✅

1. **Backend Model Updated** (`backend/app/models/todo.py`)
   - Changed from `due_date` (Date) + `due_time` (Time) to `due_datetime` (DateTime with timezone=True)
   - Updated `is_expired` property to use timezone-aware datetime

2. **Backend Schemas Updated** (`backend/app/schemas/todo.py`)
   - All schemas now use `due_datetime` instead of separate fields
   - Added field serializer to ensure timezone info is preserved in API responses

3. **Backend CRUD Updated** (`backend/app/crud/todo_extension_request.py`)
   - Updated extension request logic to use `due_datetime`
   - Updated validation to handle timezone-aware comparisons

4. **Frontend Utilities Created** (`frontend/src/utils/dateTimeUtils.ts`)
   - `utcToLocalDateTimeParts()` - Converts UTC to local date/time for forms
   - `localDateTimePartsToUTC()` - Converts local input to UTC for API
   - `formatUTCDateTimeForDisplay()` - Displays UTC times in local timezone

5. **Frontend Types Updated** (`frontend/src/types/todo.ts`)
   - Changed from `due_date` + `due_time` to `due_datetime`
   - Added timezone documentation in comments

6. **Frontend Components Updated**
   - `frontend/src/app/[locale]/(app)/todos/page.tsx` - Todo list displays local times
   - `frontend/src/components/todos/TaskModal.tsx` - Form converts between UTC and local

7. **Frontend Build** ✅ - Passes without errors

## What's NOT Done ❌

### Database Migration is STUCK

**Problem**: The Alembic migration runs but hangs/is very slow when trying to:
1. Drop the `due_datetime` column (from previous failed attempt)
2. Add new `due_datetime` column
3. Migrate data from `due_date` + `due_time` to `due_datetime`
4. Drop old `due_date` and `due_time` columns

**Migration File**: `backend/alembic/versions/d5fb4c228327_merge_todo_due_date_time_to_due_datetime.py`

**Current State**:
- Migration revision: `e8b5e6296ba3` (not upgraded yet)
- Target revision: `d5fb4c228327`
- The `todos` table has: `due_date`, `due_time`, AND `due_datetime` (inconsistent state)

## How to Complete the Migration

### Option 1: Manual SQL Migration (Recommended - Fast)

Connect to the MySQL database and run these commands **in order**:

```sql
-- 1. Check current state
DESCRIBE todos;

-- 2. Drop due_datetime if it exists from previous failed migration
ALTER TABLE todos DROP COLUMN IF EXISTS due_datetime;

-- 3. Add new due_datetime column
ALTER TABLE todos ADD COLUMN due_datetime DATETIME NULL;

-- 4. Migrate data (combine due_date + due_time)
UPDATE todos
SET due_datetime = CASE
    -- If both date and time exist, combine them
    WHEN due_date IS NOT NULL AND due_time IS NOT NULL THEN
        CAST(CONCAT(due_date, ' ', due_time) AS DATETIME)
    -- If only date exists, use end of day (23:59:59)
    WHEN due_date IS NOT NULL AND due_time IS NULL THEN
        CAST(CONCAT(due_date, ' 23:59:59') AS DATETIME)
    -- Otherwise leave as NULL
    ELSE NULL
END;

-- 5. Verify data migration
SELECT
    id,
    due_date,
    due_time,
    due_datetime,
    CASE
        WHEN due_date IS NOT NULL THEN 'Has date'
        ELSE 'No date'
    END as status
FROM todos
LIMIT 10;

-- 6. Drop old columns
ALTER TABLE todos DROP COLUMN due_time;
ALTER TABLE todos DROP COLUMN due_date;

-- 7. Update Alembic version table to mark migration as done
UPDATE alembic_version SET version_num = 'd5fb4c228327';

-- 8. Verify final state
DESCRIBE todos;
SELECT version_num FROM alembic_version;
```

### Option 2: Fix and Re-run Alembic Migration

If you want to use Alembic properly:

1. **Kill any stuck migration processes**:
   ```bash
   docker restart miraiworks_backend
   ```

2. **Check current state**:
   ```bash
   docker exec miraiworks_backend alembic current
   ```

3. **If stuck on the old revision**, try the migration again:
   ```bash
   docker exec miraiworks_backend alembic upgrade head
   ```

   **Note**: This might hang again. If it does, use Option 1 instead.

### Option 3: Downgrade and Recreate Migration

If the migration file is corrupted:

1. **Downgrade to previous version** (if possible):
   ```bash
   docker exec miraiworks_backend alembic downgrade e8b5e6296ba3
   ```

2. **Delete the problematic migration**:
   ```bash
   rm backend/alembic/versions/d5fb4c228327_merge_todo_due_date_time_to_due_datetime.py
   ```

3. **Create a new migration**:
   ```bash
   docker exec miraiworks_backend alembic revision -m "merge_todo_due_date_time_to_due_datetime_v2"
   ```

4. **Edit the new migration file** with the same logic but different approach

## After Migration is Complete

1. **Restart the backend**:
   ```bash
   docker restart miraiworks_backend
   ```

2. **Verify the API works**:
   - Create a new todo with a due date
   - Edit an existing todo
   - Check that times display correctly in local timezone
   - Test extension requests

3. **Mark the todo item as complete** in your task tracker

## Testing Checklist

Once migration is done, test these scenarios:

- [ ] Create new todo with due date/time - should save in UTC
- [ ] View existing todos - should display in local timezone
- [ ] Edit todo due date/time - should convert correctly
- [ ] Todo expiration logic works correctly
- [ ] Extension requests work with new datetime field
- [ ] Calendar events integration (if applicable)
- [ ] Timezone conversion is correct for different user timezones

## Database Connection Info

To connect to MySQL directly (if needed):

```bash
# From host machine
docker exec -it miraiworks_db mysql -u root -p miraiworks

# Database credentials (check docker-compose.yml):
# User: miraiworks or root
# Password: (check .env or docker-compose.yml)
# Database: miraiworks
```

## Files Modified

### Backend
- `backend/app/models/todo.py` ✅
- `backend/app/schemas/todo.py` ✅
- `backend/app/crud/todo_extension_request.py` ✅
- `backend/alembic/versions/d5fb4c228327_merge_todo_due_date_time_to_due_datetime.py` ⚠️ (stuck)

### Frontend
- `frontend/src/utils/dateTimeUtils.ts` ✅ (new file)
- `frontend/src/types/todo.ts` ✅
- `frontend/src/app/[locale]/(app)/todos/page.tsx` ✅
- `frontend/src/components/todos/TaskModal.tsx` ✅

## Why This Migration is Important

**Before**:
- Separate `due_date` (Date) and `due_time` (Time) fields
- No timezone information
- Confusion when users in different timezones view the same todo

**After**:
- Single `due_datetime` field (DateTime with timezone)
- All times stored in UTC
- Displayed in user's local timezone
- Consistent behavior across timezones

## Notes

- Frontend build passes ✅
- Backend code is ready ✅
- Only the database schema needs to be updated ⚠️
- The migration hangs because the `todos` table likely has many records or there's a lock
- Manual SQL is the fastest way to complete this

---

**Created**: 2025-10-18
**Status**: Waiting for database migration to complete
**Next Step**: Run Option 1 (Manual SQL Migration) when ready
