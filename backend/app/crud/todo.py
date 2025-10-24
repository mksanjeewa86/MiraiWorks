from __future__ import annotations

from sqlalchemy import Select, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.todo import Todo
from app.models.todo_viewer_memo import TodoViewerMemo
from app.models.user import User
from app.schemas.todo import (
    TodoCreate,
    TodoUpdate,
)
from app.services.todo_permissions import TodoPermissionService
from app.utils.constants import (
    TodoPublishStatus,
    TodoStatus,
)
from app.utils.datetime_utils import get_utc_now


class CRUDTodo(CRUDBase[Todo, TodoCreate, TodoUpdate]):
    """CRUD operations for Todo items."""

    async def get(self, db: AsyncSession, id: int) -> Todo | None:
        """Get todo by id, excluding soft-deleted records."""
        result = await db.execute(
            select(Todo).where(Todo.id == id, Todo.is_deleted == False)
        )
        return result.scalar_one_or_none()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> list[Todo]:
        """Get multiple todos, excluding soft-deleted records."""
        result = await db.execute(
            select(Todo).where(Todo.is_deleted == False).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def auto_mark_expired(self, db: AsyncSession, owner_id: int) -> None:
        """Automatically mark overdue todos as expired.

        NOTE: With separate due_date and due_time fields, expiration checking
        is now handled by the Todo model's is_expired property which properly
        combines date and time. This method will be deprecated in favor of
        checking is_expired property when loading todos.

        IMPORTANT: This method does NOT commit the changes. The calling code
        is responsible for committing the transaction.
        """
        # Load todos and check expiration via the model property
        result = await db.execute(
            select(Todo).where(
                Todo.owner_id == owner_id,
                Todo.due_datetime.isnot(None),
                Todo.status.notin_(
                    [TodoStatus.COMPLETED.value, TodoStatus.EXPIRED.value]
                ),
                Todo.is_deleted == False,
            )
        )
        todos = result.scalars().all()

        now = get_utc_now()
        for todo in todos:
            if todo.is_expired:  # Uses model property
                todo.status = TodoStatus.EXPIRED.value
                todo.expired_at = now
                db.add(todo)

        # Flush changes to database but don't commit
        # This allows the changes to be visible in the same transaction
        await db.flush()

    async def list_for_user(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        status: str | None = None,
        include_completed: bool = True,
        include_deleted: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[Todo], int]:
        # Build query to include todos where user is owner
        query: Select = select(Todo).where(Todo.owner_id == user_id)

        # Filter by deleted status
        if not include_deleted:
            # Only show non-deleted todos
            query = query.where(Todo.is_deleted == False)

        if status:
            query = query.where(Todo.status == status)
        elif not include_completed:
            query = query.where(Todo.status != TodoStatus.COMPLETED.value)

        total_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(total_query)
        total = total_result.scalar() or 0

        query = query.order_by(
            Todo.due_datetime.is_(None), Todo.due_datetime.asc(), Todo.created_at.desc()
        )
        query = query.offset(offset).limit(limit)

        result = await db.execute(query)
        all_todos = result.scalars().all()

        # Filter based on permissions
        filtered_todos = await TodoPermissionService.filter_todos_by_permission(
            db, user_id, all_todos
        )

        return filtered_todos, len(filtered_todos)

    async def list_recent(
        self, db: AsyncSession, *, owner_id: int, limit: int = 5
    ) -> list[Todo]:
        result = await db.execute(
            select(Todo)
            .where(Todo.owner_id == owner_id, Todo.is_deleted == False)
            .order_by(Todo.updated_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def create_for_user(
        self, db: AsyncSession, *, owner_id: int, created_by: int, obj_in: TodoCreate
    ) -> Todo:
        data = obj_in.model_dump(exclude_unset=True)
        data.setdefault("status", TodoStatus.PENDING.value)
        data["owner_id"] = owner_id
        data["created_by"] = created_by
        data["last_updated_by"] = created_by

        # For assignment type todos, if assignee_id is not specified, assign to owner
        if data.get("todo_type") == "assignment" and not data.get("assignee_id"):
            data["assignee_id"] = owner_id

        # Check if todo is expired (due_date is in the past)
        if data.get("due_date"):
            from datetime import UTC, datetime as dt_module, time as time_type

            # Combine due_date and due_time (or use end of day if no time)
            due_time = data.get("due_time") or time_type(23, 59, 59)
            due_datetime = dt_module.combine(data["due_date"], due_time)
            if due_datetime.tzinfo is None:
                due_datetime = due_datetime.replace(tzinfo=UTC)

            if due_datetime < get_utc_now():
                data["status"] = TodoStatus.EXPIRED.value
                data["expired_at"] = get_utc_now()

        db_obj = Todo(**data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update_todo(
        self,
        db: AsyncSession,
        *,
        db_obj: Todo,
        obj_in: TodoUpdate,
        updated_by: int,
    ) -> Todo:
        update_data = obj_in.model_dump(exclude_unset=True)

        # Field-level permission checks
        # description can only be edited by creator
        if 'description' in update_data:
            if db_obj.created_by != updated_by:
                update_data.pop('description')

        # assignee_memo can only be edited by assignee
        if 'assignee_memo' in update_data:
            if db_obj.assignee_id != updated_by:
                update_data.pop('assignee_memo')

        if update_data.get("status") == TodoStatus.COMPLETED.value:
            update_data.setdefault("completed_at", get_utc_now())
            update_data.pop("expired_at", None)
        elif update_data.get("status") == TodoStatus.PENDING.value:
            update_data.setdefault("completed_at", None)
            update_data.setdefault("expired_at", None)

        update_data["last_updated_by"] = updated_by

        return await super().update(db, db_obj=db_obj, obj_in=update_data)

    async def mark_complete(
        self, db: AsyncSession, *, todo: Todo, completed_by: int
    ) -> Todo:
        todo.mark_completed()
        todo.last_updated_by = completed_by
        db.add(todo)
        await db.commit()
        await db.refresh(todo)
        return todo

    async def reopen(self, db: AsyncSession, *, todo: Todo, reopened_by: int) -> Todo:
        todo.mark_pending()
        todo.last_updated_by = reopened_by
        db.add(todo)
        await db.commit()
        await db.refresh(todo)
        return todo

    async def soft_delete(
        self, db: AsyncSession, *, todo: Todo, deleted_by: int
    ) -> Todo:
        todo.soft_delete()
        todo.last_updated_by = deleted_by
        db.add(todo)
        await db.commit()
        await db.refresh(todo)
        return todo

    async def restore(self, db: AsyncSession, *, todo: Todo, restored_by: int) -> Todo:
        todo.restore()
        todo.last_updated_by = restored_by
        db.add(todo)
        await db.commit()
        await db.refresh(todo)
        return todo

    async def get_assignable_users(
        self, db: AsyncSession, *, assigner_id: int
    ) -> list[User]:
        """Get users that can be assigned todos by the assigner."""
        return await TodoPermissionService.get_assignable_users(db, assigner_id)

    async def create_with_owner(
        self, db: AsyncSession, *, owner_id: int, obj_in: TodoCreate
    ) -> Todo:
        """Create a todo with owner - alias for create_for_user."""
        return await self.create_for_user(
            db, owner_id=owner_id, created_by=owner_id, obj_in=obj_in
        )

    # Assignment workflow methods
    async def publish_assignment(
        self, db: AsyncSession, *, todo: Todo, published_by: int
    ) -> Todo:
        """Publish an assignment (make it visible to assignee and viewers)."""
        if todo.is_assignment:
            todo.publish()
            todo.last_updated_by = published_by
            db.add(todo)
            await db.commit()
            await db.refresh(todo)
        return todo

    async def make_draft(
        self, db: AsyncSession, *, todo: Todo, updated_by: int
    ) -> Todo:
        """Make assignment a draft (hide from assignee and viewers)."""
        if todo.is_assignment:
            todo.make_draft()
            todo.last_updated_by = updated_by
            db.add(todo)
            await db.commit()
            await db.refresh(todo)
        return todo

    async def submit_assignment(
        self, db: AsyncSession, *, todo: Todo, submitted_by: int, assignee_memo: str = None
    ) -> Todo:
        """Submit assignment for review."""
        if todo.is_assignment and todo.assignee_id == submitted_by:
            todo.submit_assignment()
            todo.last_updated_by = submitted_by
            if assignee_memo:
                # Update assignee memo
                todo.assignee_memo = assignee_memo
            db.add(todo)
            await db.commit()
            await db.refresh(todo)
        return todo

    async def start_assignment_review(
        self, db: AsyncSession, *, todo: Todo, reviewer_id: int
    ) -> Todo:
        """Start review process for assignment."""
        if todo.is_assignment and todo.owner_id == reviewer_id:
            todo.start_review()
            todo.last_updated_by = reviewer_id
            db.add(todo)
            await db.commit()
            await db.refresh(todo)
        return todo

    async def review_assignment(
        self,
        db: AsyncSession,
        *,
        todo: Todo,
        reviewer_id: int,
        approved: bool,
        assessment: str = None,
        score: int = None,
    ) -> Todo:
        """Review and assess an assignment."""
        if todo.is_assignment and todo.owner_id == reviewer_id:
            if approved:
                todo.approve_assignment(reviewer_id, assessment, score)
            else:
                todo.reject_assignment(reviewer_id, assessment, score)

            todo.last_updated_by = reviewer_id
            db.add(todo)
            await db.commit()
            await db.refresh(todo)
        return todo

    async def get_assignments_for_review(
        self, db: AsyncSession, *, reviewer_id: int
    ) -> list[Todo]:
        """Get assignments that need review by the reviewer."""
        result = await db.execute(
            select(Todo)
            .where(
                Todo.owner_id == reviewer_id,
                Todo.todo_type == "assignment",
                Todo.submitted_at.isnot(None),
                Todo.reviewed_at.is_(None),  # Not yet reviewed
                Todo.is_deleted == False,
            )
            .order_by(Todo.submitted_at.asc())
        )
        return result.scalars().all()

    async def get_user_assignments(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        visibility_status: str = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[Todo], int]:
        """Get assignments for a user (where user is assignee)."""
        # Get assignments where user is assignee
        query: Select = (
            select(Todo)
            .options(selectinload(Todo.owner))
            .where(
                Todo.todo_type == "assignment",
                Todo.publish_status == TodoPublishStatus.PUBLISHED.value,
                Todo.is_deleted == False,
                Todo.assignee_id == user_id,
            )
        )

        if visibility_status:
            query = query.where(Todo.visibility_status == visibility_status)

        total_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(total_query)
        total = total_result.scalar() or 0

        query = query.order_by(
            Todo.due_datetime.is_(None), Todo.due_datetime.asc(), Todo.created_at.desc()
        )
        query = query.offset(offset).limit(limit)

        result = await db.execute(query)
        assignments = result.scalars().all()
        return assignments, total

    async def attach_viewer_memo(
        self, db: AsyncSession, *, todo: Todo, user_id: int
    ) -> Todo:
        """Attach viewer memo for the current user to the todo object."""
        # Query for viewer memo
        result = await db.execute(
            select(TodoViewerMemo).where(
                TodoViewerMemo.todo_id == todo.id,
                TodoViewerMemo.user_id == user_id
            )
        )
        viewer_memo_obj = result.scalar_one_or_none()

        # Attach as a temporary attribute (not persisted to DB)
        if viewer_memo_obj:
            todo.viewer_memo = viewer_memo_obj.memo
        else:
            todo.viewer_memo = None

        return todo


todo = CRUDTodo(Todo)
