# Todo Timezone Fix

## 🐛 The Problem

**Issue**: When creating a todo with due date `2025-10-30 22:00:00`, it displays as `2025-10-30 13:00:00` (9 hours earlier).

**Example**:
- ✍️ **You enter**: 2025-10-30 22:00:00
- 💾 **Backend stores**: 2025-10-30 22:00:00 UTC
- 👀 **You see**: 2025-10-30 13:00:00 (JST = UTC+9)

**Root Cause**: The backend was treating timezone-naive dates as UTC, but not properly serializing them back with timezone information for the frontend.

## 🔍 Technical Analysis

### How Dates Were Being Handled (BEFORE):

1. **Frontend sends** (no timezone):
   ```json
   {
     "due_date": "2025-10-30T22:00:00"
   }
   ```

2. **Backend receives** (todo.py:36-48):
   ```python
   @field_validator("due_date", mode="before")
   def ensure_timezone(cls, value):
       if value.tzinfo is None:
           return value.replace(tzinfo=UTC)  # Assumes UTC!
       return value.astimezone(UTC)
   ```
   Result: `2025-10-30 22:00:00+00:00` (UTC)

3. **Backend serializes** (MISSING step - this was the bug!):
   ```python
   # No field_serializer for due_date!
   # Pydantic just returns: "2025-10-30T22:00:00" (no timezone)
   ```

4. **Frontend receives**:
   ```json
   {
     "due_date": "2025-10-30T22:00:00"  // No timezone info!
   }
   ```

5. **Browser interprets as local timezone**:
   ```javascript
   new Date("2025-10-30T22:00:00")
   // Browser thinks: "This is 22:00 in UTC"
   // Displays as: "2025-10-30 13:00:00" (UTC+9)
   ```

### How Dates Are Handled (AFTER FIX):

1. **Frontend sends** (same):
   ```json
   {
     "due_date": "2025-10-30T22:00:00"
   }
   ```

2. **Backend receives** (same):
   ```python
   # Still converts to UTC
   value.replace(tzinfo=UTC)
   ```
   Result: `2025-10-30 22:00:00+00:00`

3. **Backend serializes** (NEW - this is the fix!):
   ```python
   @field_serializer('due_date', ...)
   def serialize_datetime(self, dt, _info):
       if dt.tzinfo is None:
           dt = dt.replace(tzinfo=timezone.utc)
       return dt.isoformat()  # Returns with timezone!
   ```

4. **Frontend receives** (NOW WITH TIMEZONE):
   ```json
   {
     "due_date": "2025-10-30T22:00:00+00:00"  // Includes +00:00!
   }
   ```

5. **Browser interprets correctly**:
   ```javascript
   new Date("2025-10-30T22:00:00+00:00")
   // Browser knows: "This is 22:00 UTC"
   // Displays as: "2025-10-31 07:00:00" (22:00 UTC + 9 hours = 07:00 JST next day)
   ```

Wait... that's still wrong! The issue is that the **frontend is sending the wrong value**!

## 🎯 The Real Problem

The frontend needs to send the **local time with timezone information**, not a naive datetime!

### Correct Flow Should Be:

1. **User enters in browser**: "2025-10-30 22:00" (JST)
2. **Frontend should send**: `"2025-10-30T22:00:00+09:00"` (with JST timezone)
3. **Backend converts to UTC**: `2025-10-30 13:00:00+00:00`
4. **Backend serializes**: `"2025-10-30T13:00:00+00:00"`
5. **Frontend displays**: "2025-10-30 22:00" (converts back to JST)

## ✅ Solution Applied

### Backend Fix (DONE):

Added `@field_serializer` to ensure all datetime fields are returned with timezone information:

```python
# backend/app/schemas/todo.py

class TodoRead(BaseModel):
    # ... fields ...

    @field_serializer('due_date', 'completed_at', 'expired_at', 'deleted_at',
                      'created_at', 'updated_at', 'submitted_at', 'reviewed_at')
    def serialize_datetime(self, dt: Optional[datetime], _info) -> Optional[str]:
        """Ensure datetime fields are serialized with UTC timezone information."""
        if dt is None:
            return None
        # If datetime is naive, assume it's UTC and add timezone
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        # Serialize to ISO format with timezone
        return dt.isoformat()
```

Also applied to:
- `TodoViewer.added_at`
- `TodoExtensionValidation.max_allowed_due_date`

### Frontend Fix (NEEDED):

The frontend needs to properly handle timezones. Check if there's a utility function like `formatDateTimeForAPI` used in calendar events:

**Location to check**:
- `frontend/src/components/todos/TaskModal.tsx`
- `frontend/src/components/todos/TaskModalWithAttachments.tsx`
- Look for datetime input handling

**What to fix**:
```typescript
// BEFORE (wrong)
const dueDate = formData.dueDate; // "2025-10-30T22:00:00"

// AFTER (correct)
const dueDate = new Date(formData.dueDate).toISOString(); // "2025-10-30T13:00:00.000Z"
// Or better: keep local timezone
const dueDate = formData.dueDate + getTimezoneOffset(); // "2025-10-30T22:00:00+09:00"
```

## 📝 Files Modified

### Backend:
1. ✅ `backend/app/schemas/todo.py`
   - Added `field_serializer` import
   - Added `timezone` import from datetime
   - Added `@field_serializer` to `TodoRead` class
   - Added `@field_serializer` to `TodoViewer` class
   - Added `@field_serializer` to `TodoExtensionValidation` class

### Frontend (NEEDS REVIEW):
These files likely need updates:
- `frontend/src/components/todos/TaskModal.tsx`
- `frontend/src/components/todos/TaskModalWithAttachments.tsx`
- `frontend/src/api/todos.ts` (if API formatting is done there)

## 🧪 Testing

### Test Case 1: Create Todo with Due Date

**Input (Frontend)**:
```json
{
  "title": "Test Todo",
  "due_date": "2025-10-30T22:00:00"
}
```

**Expected (Backend Response - AFTER FIX)**:
```json
{
  "id": 1,
  "title": "Test Todo",
  "due_date": "2025-10-30T22:00:00+00:00",  // Now includes timezone!
  "created_at": "2025-10-18T12:00:00+00:00",
  "updated_at": "2025-10-18T12:00:00+00:00"
}
```

### Test Case 2: Display Todo in Frontend

**Backend Returns**:
```json
{
  "due_date": "2025-10-30T13:00:00+00:00"  // UTC time
}
```

**Frontend Should Display** (in JST):
```
Due Date: 2025-10-30 22:00 JST
```

## 🚨 Important Notes

1. **Calendar Events Already Fixed**: This same pattern was already applied to calendar events in `backend/app/schemas/calendar_event.py` (lines 117-126)

2. **Consistency**: Now todos and calendar events handle timezones the same way

3. **Database Storage**: Database still stores in UTC (this is correct!)

4. **Frontend Responsibility**: The frontend should:
   - Send datetimes with timezone information
   - Display datetimes in user's local timezone
   - Use ISO format with timezone offset (e.g., `+09:00`)

## 🔄 Next Steps

1. ✅ **Backend fix applied** - All datetime fields now serialize with timezone
2. ⏳ **Frontend fix needed** - Need to check how todos send datetime to API
3. ⏳ **Test thoroughly** - Create/edit todos and verify dates display correctly
4. ⏳ **Check calendar integration** - Todos on calendar should show correct times

## 📚 Related Files to Review

Calendar events (already fixed):
- `backend/app/schemas/calendar_event.py:117-126` - field_serializer reference
- `CALENDAR_TIMEZONE_FIX.md` - Previous timezone fix documentation

Todo extension requests:
- `backend/app/schemas/todo_extension.py` - May also need timezone fix
- Check for datetime fields: `requested_at`, `responded_at`, `new_due_date`

## ⚙️ Configuration

User timezone preference:
- Should be stored in user settings
- Default to browser timezone if not set
- Use for display conversion in frontend

---

**Status**: ✅ Backend Fixed | ⏳ Frontend Needs Review
**Date**: 2025-10-18
**Related Issue**: Todo due dates showing 9 hours earlier than expected
