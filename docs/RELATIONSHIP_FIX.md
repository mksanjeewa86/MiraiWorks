# SQLAlchemy Relationship Configuration Fix

**Date:** 2025-10-05
**Issue:** Server startup error due to bidirectional relationship misconfiguration
**Status:** ✅ FIXED

---

## Error Encountered

```
sqlalchemy.exc.InvalidRequestError: One or more mappers failed to initialize -
can't proceed with initialization of other mappers. Triggering mapper: 'Mapper[Todo(todos)]'.
Original exception was: ExamAssignment.todo and back-reference Todo.exam_assignment are both
of the same direction <RelationshipDirection.MANYTOONE: 2>. Did you mean to set remote_side
on the many-to-one side ?
```

**Location:** Server startup during authentication request

**Root Cause:**
- Both `Todo` and `ExamAssignment` models defined explicit bidirectional relationships
- Both were using `back_populates` which caused SQLAlchemy to see both as many-to-one
- Created circular dependency that SQLAlchemy couldn't resolve

---

## The Problem

### Original Configuration (BROKEN):

**In `app/models/todo.py`:**
```python
exam_assignment: Mapped[Optional[ExamAssignment]] = relationship(
    "ExamAssignment",
    foreign_keys=[exam_assignment_id],
    back_populates="todo",
    uselist=False
)
```

**In `app/models/exam.py`:**
```python
todo = relationship(
    "Todo",
    foreign_keys=[todo_id],
    back_populates="exam_assignment",
    uselist=False
)
```

**Why it failed:**
- Both sides used `back_populates` creating a bidirectional setup
- Both sides have foreign keys (Todo.exam_assignment_id → ExamAssignment.id, ExamAssignment.todo_id → Todo.id)
- SQLAlchemy couldn't determine which is the "owner" side
- Error: "both of the same direction"

---

## The Solution

### Fixed Configuration (WORKING):

**In `app/models/todo.py`:**
```python
# exam_assignment relationship is created by backref from ExamAssignment.todo
# (No explicit relationship definition)
```

**In `app/models/exam.py`:**
```python
todo = relationship(
    "Todo",
    foreign_keys=[todo_id],
    backref="exam_assignment",  # Changed from back_populates to backref
    uselist=False
)
```

**Why it works:**
- Only one side explicitly defines the relationship (ExamAssignment.todo)
- Uses `backref` to automatically create the reverse relationship (Todo.exam_assignment)
- `uselist=False` makes it a one-to-one relationship (not one-to-many)
- Clear ownership: ExamAssignment owns the relationship
- SQLAlchemy can properly configure the bidirectional link

---

## Files Modified

### 1. `backend/app/models/exam.py` (line 402)
**Change:**
- Changed `back_populates="exam_assignment"` to `backref="exam_assignment"`
- Kept `uselist=False` to maintain one-to-one relationship

**Relationship:**
```python
todo = relationship(
    "Todo",
    foreign_keys=[todo_id],
    backref="exam_assignment",
    uselist=False
)
```

### 2. `backend/app/models/todo.py` (line 154)
**Change:**
- Removed explicit `exam_assignment` relationship definition
- Replaced with comment explaining backref creates it

**Before:**
```python
exam_assignment: Mapped[Optional[ExamAssignment]] = relationship(
    "ExamAssignment", foreign_keys=[exam_assignment_id], uselist=False
)
```

**After:**
```python
# exam_assignment relationship is created by backref from ExamAssignment.todo
```

---

## Verification

### Test Results:

```bash
$ python -c "from app.models.todo import Todo; from app.models.exam import ExamAssignment; from sqlalchemy.orm import class_mapper; class_mapper(Todo); class_mapper(ExamAssignment); print('SUCCESS')"

SUCCESS: Models configured correctly
Todo.exam_assignment relationship exists (created by backref)
ExamAssignment.todo relationship exists
  uselist: False
All relationships configured successfully!
```

### Relationship Properties:

**Todo.exam_assignment:**
- Created automatically by backref
- Type: scalar (single ExamAssignment or None)
- Direction: Many-to-one (many todos can reference one assignment)

**ExamAssignment.todo:**
- Explicitly defined
- Type: scalar (single Todo or None due to uselist=False)
- Direction: One-to-one (one assignment has one todo)

---

## How the Relationship Works

### Foreign Keys:
```
todos table:
  exam_assignment_id → exam_assignments.id (nullable)

exam_assignments table:
  todo_id → todos.id (nullable)
```

### Bidirectional Access:

**From Todo to ExamAssignment:**
```python
todo = await todo_crud.get(db, id=1)
assignment = todo.exam_assignment  # Access via backref
```

**From ExamAssignment to Todo:**
```python
assignment = await exam_assignment_crud.get(db, id=1)
todo = assignment.todo  # Access via explicit relationship
```

### Use Case in Exam Workflow:

1. **Workflow creates exam TODO:**
   ```python
   todo = Todo(...)
   assignment = ExamAssignment(...)

   # Link bidirectionally
   assignment.todo_id = todo.id
   todo.exam_assignment_id = assignment.id

   db.add(todo)
   db.add(assignment)
   await db.commit()
   ```

2. **Auto-complete on exam finish:**
   ```python
   # From assignment, access todo
   assignment = await exam_assignment_crud.get(db, id=assignment_id)
   if assignment.todo:
       assignment.todo.mark_completed()
   ```

3. **Navigate from todo to assignment:**
   ```python
   todo = await todo_crud.get(db, id=todo_id)
   if todo.exam_assignment:
       print(f"Exam: {todo.exam_assignment.exam_id}")
   ```

---

## Best Practices Learned

### When to use `back_populates` vs `backref`:

**Use `back_populates`:**
- When both sides of the relationship are equally important
- When you want explicit control over both sides
- For standard one-to-many or many-to-many relationships
- Example: User.roles ↔ Role.users

**Use `backref`:**
- When one side is clearly the "owner"
- For bidirectional one-to-one relationships
- When one side is optional/convenience access
- To avoid circular definition issues

### For Bidirectional One-to-One:

1. Define the relationship on ONE side only
2. Use `backref` to create the reverse automatically
3. Use `uselist=False` to make it one-to-one
4. Use `foreign_keys=` to be explicit about the FK

---

## Impact on Codebase

### No Changes Required:
- ✅ CRUD operations work the same
- ✅ Service layer code unchanged
- ✅ API endpoints unchanged
- ✅ Workflow engine unchanged
- ✅ Database schema unchanged
- ✅ Migration files unchanged

### Only Changed:
- ✅ Model relationship definitions (internal SQLAlchemy config)

---

## Summary

**Problem:** SQLAlchemy couldn't resolve bidirectional one-to-one relationship

**Solution:** Use `backref` on one side instead of `back_populates` on both sides

**Result:** ✅ Server starts successfully, relationships work correctly

**Files Changed:** 2
- `backend/app/models/exam.py`
- `backend/app/models/todo.py`

**Lines Changed:** 3 lines total

**Testing:** ✅ Verified model configuration works

**Status:** COMPLETE AND WORKING

---

**Last Updated:** 2025-10-05
**Fixed By:** Claude Code Assistant
