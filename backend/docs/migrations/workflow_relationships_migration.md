# Workflow Relationships Migration Guide

## Migration: `e936f1f184f8_add_workflow_relationships_to_interviews_and_todos`

**Date**: 2025-10-02
**Revision ID**: `e936f1f184f8`
**Previous Revision**: `3caefaa119d8`

---

## 📋 Overview

This migration establishes database relationships between workflows (recruitment_processes) and their related interviews and todos. It also implements cascading soft delete functionality to ensure data integrity.

### Purpose

- Link interviews to workflows via foreign key
- Link todos to workflows via foreign key
- Enable automatic cascading soft delete when a workflow is deleted
- Maintain data integrity and traceability

---

## 🗄️ Database Changes

### 1. Interviews Table

#### Added Columns

| Column Name | Type | Nullable | Default | Index | Foreign Key |
|-------------|------|----------|---------|-------|-------------|
| `workflow_id` | INTEGER | YES | NULL | YES | `recruitment_processes.id` |

#### Added Indexes

- `ix_interviews_workflow_id` on `workflow_id` column

#### Added Foreign Keys

- **Name**: `fk_interviews_workflow_id`
- **References**: `recruitment_processes(id)`
- **On Delete**: `SET NULL`

### 2. Todos Table

#### Added Columns

| Column Name | Type | Nullable | Default | Index | Foreign Key |
|-------------|------|----------|---------|-------|-------------|
| `workflow_id` | INTEGER | YES | NULL | YES | `recruitment_processes.id` |

#### Added Indexes

- `ix_todos_workflow_id` on `workflow_id` column

#### Added Foreign Keys

- **Name**: `fk_todos_workflow_id`
- **References**: `recruitment_processes(id)`
- **On Delete**: `SET NULL`

---

## 🔄 Schema Diagram

```
┌─────────────────────────────┐
│   recruitment_processes     │
│        (workflows)          │
├─────────────────────────────┤
│ • id (PK)                   │
│ • name                      │
│ • description               │
│ • status                    │
│ • is_deleted                │
│ • deleted_at                │
│ • ...                       │
└─────────────────────────────┘
         ▲           ▲
         │           │
         │           │ FK: workflow_id
         │           │ (SET NULL on delete)
         │           │
    ┌────┴────┐ ┌───┴─────┐
    │         │ │         │
┌───────────────┐   ┌──────────────┐
│  interviews   │   │    todos     │
├───────────────┤   ├──────────────┤
│ • id (PK)     │   │ • id (PK)    │
│ • workflow_id │   │ • workflow_id│
│ • title       │   │ • title      │
│ • is_deleted  │   │ • is_deleted │
│ • deleted_at  │   │ • deleted_at │
│ • ...         │   │ • ...        │
└───────────────┘   └──────────────┘
```

---

## 🚀 Applying the Migration

### Forward Migration (Upgrade)

```bash
cd backend
python -m alembic upgrade head
```

#### What happens:

1. Adds `workflow_id` column to `interviews` table
2. Creates index on `interviews.workflow_id`
3. Creates foreign key constraint from `interviews.workflow_id` to `recruitment_processes.id`
4. Adds `workflow_id` column to `todos` table
5. Creates index on `todos.workflow_id`
6. Creates foreign key constraint from `todos.workflow_id` to `recruitment_processes.id`

### Backward Migration (Downgrade)

```bash
cd backend
python -m alembic downgrade -1
```

#### What happens:

1. Drops foreign key `fk_todos_workflow_id` from `todos` table
2. Drops index `ix_todos_workflow_id` from `todos` table
3. Drops column `workflow_id` from `todos` table
4. Drops foreign key `fk_interviews_workflow_id` from `interviews` table
5. Drops index `ix_interviews_workflow_id` from `interviews` table
6. Drops column `workflow_id` from `interviews` table

---

## 💾 Model Changes

### Interview Model (`app/models/interview.py`)

#### Added Fields

```python
# Workflow relationship
workflow_id = Column(
    Integer,
    ForeignKey("recruitment_processes.id", ondelete="SET NULL"),
    nullable=True,
    index=True,
)
```

#### Added Relationships

```python
# Workflow relationship
workflow = relationship("RecruitmentProcess", foreign_keys=[workflow_id], lazy="noload")
```

### Todo Model (`app/models/todo.py`)

#### Added Fields

```python
# Workflow relationship
workflow_id: Mapped[int | None] = mapped_column(
    Integer, ForeignKey("recruitment_processes.id", ondelete="SET NULL"), nullable=True, index=True
)
```

#### Added Relationships

```python
workflow: Mapped["RecruitmentProcess"] | None = relationship(
    "RecruitmentProcess", foreign_keys=[workflow_id]
)
```

### RecruitmentProcess Model (`app/models/recruitment_process.py`)

#### Added Relationships

```python
interviews: Mapped[list[Interview]] = relationship(
    "Interview", foreign_keys="Interview.workflow_id", back_populates="workflow"
)
todos: Mapped[list[Todo]] = relationship(
    "Todo", foreign_keys="Todo.workflow_id", back_populates="workflow"
)
```

---

## 🔧 CRUD Changes

### Cascading Soft Delete Implementation

File: `backend/app/crud/recruitment_workflow/recruitment_process.py`

#### New Method: `soft_delete()`

```python
async def soft_delete(self, db: AsyncSession, *, id: int) -> RecruitmentProcess:
    """
    Soft delete workflow and cascade to related interviews and todos.

    When a workflow is soft deleted, all associated interviews and todos
    are automatically soft deleted as well.
    """
    # Get the workflow
    workflow = await self.get(db, id)
    if not workflow:
        return None

    # Soft delete the workflow
    workflow.is_deleted = True
    workflow.deleted_at = datetime.utcnow()
    db.add(workflow)

    # Cascade soft delete to related interviews
    await db.execute(
        update(Interview)
        .where(
            Interview.workflow_id == id,
            Interview.is_deleted == False
        )
        .values(
            is_deleted=True,
            deleted_at=datetime.utcnow()
        )
    )

    # Cascade soft delete to related todos
    await db.execute(
        update(Todo)
        .where(
            Todo.workflow_id == id,
            Todo.is_deleted == False
        )
        .values(
            is_deleted=True,
            deleted_at=datetime.utcnow()
        )
    )

    await db.commit()
    await db.refresh(workflow)
    return workflow
```

---

## 📝 Usage Examples

### Creating an Interview Linked to a Workflow

```python
from app.models.interview import Interview

# Create interview with workflow relationship
interview = Interview(
    title="Technical Interview",
    workflow_id=123,  # Link to workflow
    candidate_id=456,
    recruiter_id=789,
    # ... other fields
)
db.add(interview)
await db.commit()
```

### Creating a Todo Linked to a Workflow

```python
from app.models.todo import Todo

# Create todo with workflow relationship
todo = Todo(
    title="Review Resume",
    workflow_id=123,  # Link to workflow
    owner_id=456,
    # ... other fields
)
db.add(todo)
await db.commit()
```

### Querying Workflow with Related Data

```python
from app.crud.recruitment_workflow.recruitment_process import recruitment_process

# Get workflow with related interviews and todos
workflow = await recruitment_process.get_with_nodes(db, id=123)

# Access related interviews
print(f"Workflow has {len(workflow.interviews)} interviews")
for interview in workflow.interviews:
    print(f"  - {interview.title}")

# Access related todos
print(f"Workflow has {len(workflow.todos)} todos")
for todo in workflow.todos:
    print(f"  - {todo.title}")
```

### Soft Deleting a Workflow (Cascades Automatically)

```python
from app.crud.recruitment_workflow.recruitment_process import recruitment_process

# Soft delete workflow - automatically cascades to interviews and todos
deleted_workflow = await recruitment_process.soft_delete(db, id=123)

# All related interviews and todos are now soft deleted
# They have is_deleted=True and deleted_at set
```

---

## ⚠️ Important Notes

### Data Safety

- **Non-destructive**: All data is preserved even when soft deleted
- **Nullable**: `workflow_id` is nullable, so existing records are not affected
- **SET NULL on delete**: If a workflow is hard deleted from DB, related records' `workflow_id` becomes NULL (not deleted)

### Performance Considerations

- **Indexes created**: Both `workflow_id` columns are indexed for query performance
- **Cascade operations**: Soft delete cascades are executed in a single transaction
- **Query filtering**: All CRUD `get()` methods automatically filter `is_deleted == False`

### Breaking Changes

- **None**: This migration is backward compatible
- Existing interviews and todos without `workflow_id` continue to work
- New code can check `workflow_id is not None` to determine if record is part of a workflow

---

## 🧪 Testing the Migration

### Manual Testing Steps

1. **Apply the migration**:
   ```bash
   cd backend
   python -m alembic upgrade head
   ```

2. **Verify schema changes**:
   ```bash
   # Connect to your database
   mysql -u your_user -p your_database

   # Check interviews table
   DESCRIBE interviews;
   # Should show workflow_id column

   # Check todos table
   DESCRIBE todos;
   # Should show workflow_id column

   # Check foreign keys
   SHOW CREATE TABLE interviews;
   SHOW CREATE TABLE todos;
   ```

3. **Test cascading soft delete**:
   ```python
   # Create a workflow with interviews and todos
   workflow = await recruitment_process.create(db, obj_in={...}, created_by=1)

   # Create linked interview
   interview = Interview(workflow_id=workflow.id, ...)
   db.add(interview)

   # Create linked todo
   todo = Todo(workflow_id=workflow.id, ...)
   db.add(todo)
   await db.commit()

   # Soft delete the workflow
   await recruitment_process.soft_delete(db, id=workflow.id)

   # Verify cascade
   assert workflow.is_deleted == True
   assert interview.is_deleted == True
   assert todo.is_deleted == True
   ```

4. **Test rollback** (optional):
   ```bash
   # Rollback migration
   cd backend
   python -m alembic downgrade -1

   # Verify columns are removed
   mysql -u your_user -p your_database
   DESCRIBE interviews;  # workflow_id should not exist
   DESCRIBE todos;       # workflow_id should not exist

   # Re-apply if needed
   python -m alembic upgrade head
   ```

---

## 🔍 Troubleshooting

### Issue: Migration fails with foreign key constraint error

**Possible causes**:
- Orphaned records in interviews or todos tables
- Database user lacks ALTER TABLE permissions

**Solution**:
```sql
-- Check for orphaned records
SELECT COUNT(*) FROM interviews WHERE workflow_id IS NOT NULL
  AND workflow_id NOT IN (SELECT id FROM recruitment_processes);

SELECT COUNT(*) FROM todos WHERE workflow_id IS NOT NULL
  AND workflow_id NOT IN (SELECT id FROM recruitment_processes);

-- If orphaned records exist, clean them up
UPDATE interviews SET workflow_id = NULL WHERE workflow_id NOT IN (SELECT id FROM recruitment_processes);
UPDATE todos SET workflow_id = NULL WHERE workflow_id NOT IN (SELECT id FROM recruitment_processes);

-- Retry migration
```

### Issue: Query performance slow after migration

**Solution**:
```sql
-- Verify indexes were created
SHOW INDEX FROM interviews WHERE Key_name = 'ix_interviews_workflow_id';
SHOW INDEX FROM todos WHERE Key_name = 'ix_todos_workflow_id';

-- If missing, create manually
CREATE INDEX ix_interviews_workflow_id ON interviews(workflow_id);
CREATE INDEX ix_todos_workflow_id ON todos(workflow_id);

-- Analyze tables for query optimizer
ANALYZE TABLE interviews;
ANALYZE TABLE todos;
```

### Issue: Cascading soft delete not working

**Verification**:
```python
# Check if override method is being called
import logging
logging.basicConfig(level=logging.DEBUG)

# Soft delete should log the cascade operations
await recruitment_process.soft_delete(db, id=workflow_id)

# Manually verify
interview_count = await db.execute(
    select(func.count()).where(
        Interview.workflow_id == workflow_id,
        Interview.is_deleted == True
    )
)
print(f"Soft deleted interviews: {interview_count.scalar()}")
```

---

## 📚 Related Documentation

- [Soft Delete Implementation Guide](./soft_delete_implementation.md)
- [RecruitmentProcess Model Reference](../models/recruitment_process.md)
- [Interview Model Reference](../models/interview.md)
- [Todo Model Reference](../models/todo.md)
- [Alembic Migration Guide](./alembic_guide.md)

---

## ✅ Checklist

- [x] Migration file created
- [x] Database schema updated
- [x] Models updated with relationships
- [x] CRUD methods updated
- [x] Cascading soft delete implemented
- [x] Indexes created for performance
- [x] Foreign key constraints added
- [x] Documentation written
- [x] Integration tests added
- [x] Backend schemas updated
- [ ] pytest-asyncio compatibility issue fixed (requires upgrade to 0.23+)
- [ ] Frontend updated to use workflow_id

---

## 👥 Authors

**Migration created by**: Claude Code Assistant
**Date**: October 2, 2025
**Project**: MiraiWorks Recruitment System

---

## 📄 License

This migration is part of the MiraiWorks project. See the main project LICENSE file for details.
