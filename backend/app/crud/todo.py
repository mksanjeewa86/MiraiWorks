from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import Select, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.crud.todo_viewer import todo_viewer
from app.models.todo import Todo
from app.models.todo_viewer import TodoViewer
from app.models.user import User
from app.schemas.todo import (
    TodoAssignmentUpdate,
    TodoCreate,
    TodoUpdate,
    TodoViewersUpdate,
)
from app.services.todo_permissions import TodoPermissionService
from app.utils.constants import (
    AssignmentStatus,
    TodoPublishStatus,
    TodoStatus,
    TodoVisibility,
)


class CRUDTodo(CRUDBase[Todo, TodoCreate, TodoUpdate]):
    """CRUD operations for Todo items."""

    async def get(self, db: AsyncSession, id: int) -> Todo | None:
        """Get todo by id, excluding soft-deleted records."""
        result = await db.execute(
            select(Todo).where(
                Todo.id == id,
                Todo.is_deleted == False
            )
        )
        return result.scalar_one_or_none()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> list[Todo]:
        """Get multiple todos, excluding soft-deleted records."""
        result = await db.execute(
            select(Todo)
            .where(Todo.is_deleted == False)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def auto_mark_expired(self, db: AsyncSession, owner_id: int) -> None:
        """Automatically mark overdue todos as expired."""
        now = datetime.now(UTC)
        await db.execute(
            update(Todo)
            .where(
                Todo.owner_id == owner_id,
                Todo.due_date.isnot(None),
                Todo.status.notin_(
                    [TodoStatus.COMPLETED.value, TodoStatus.EXPIRED.value]
                ),
                Todo.due_date < now,
            )
            .values(status=TodoStatus.EXPIRED.value, expired_at=now)
        )
        await db.commit()

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
        await self.auto_mark_expired(db, user_id)

        # Build query to include todos where user is owner OR assigned
        # BUT exclude draft assignments if user is not the owner
        query: Select = (
            select(Todo)
            .options(selectinload(Todo.assigned_user))
            .where(
                (Todo.owner_id == user_id) |
                (
                    (Todo.assigned_user_id == user_id) &
                    (Todo.publish_status == TodoPublishStatus.PUBLISHED.value)
                )
            )
        )

        # Filter by deleted status
        if include_deleted:
            query = query.where(Todo.is_deleted is True)
        else:
            query = query.where(Todo.is_deleted is False)

        if status:
            query = query.where(Todo.status == status)
        elif not include_completed:
            query = query.where(Todo.status != TodoStatus.COMPLETED.value)

        total_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(total_query)
        total_result.scalar() or 0

        query = query.order_by(
            Todo.due_date.is_(None), Todo.due_date.asc(), Todo.created_at.desc()
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
        await self.auto_mark_expired(db, owner_id)
        result = await db.execute(
            select(Todo)
            .where(Todo.owner_id == owner_id, Todo.is_deleted is False)
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

        if data.get("due_date") and data["due_date"] < datetime.now(UTC):
            data["status"] = TodoStatus.EXPIRED.value
            data["expired_at"] = datetime.now(UTC)

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
        if update_data.get("status") == TodoStatus.COMPLETED.value:
            update_data.setdefault("completed_at", datetime.now(UTC))
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

    async def soft_delete(self, db: AsyncSession, *, todo: Todo, deleted_by: int) -> Todo:
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

    async def get_with_assigned_user(
        self, db: AsyncSession, *, todo_id: int
    ) -> Todo | None:
        """Get todo with assigned user and viewers information, excluding soft-deleted."""
        result = await db.execute(
            select(Todo)
            .options(
                selectinload(Todo.assigned_user),
                selectinload(Todo.viewers).selectinload(TodoViewer.user)
            )
            .where(
                Todo.id == todo_id,
                Todo.is_deleted == False
            )
        )
        return result.scalars().first()

    async def assign_todo(
        self,
        db: AsyncSession,
        *,
        todo: Todo,
        assignment_data: TodoAssignmentUpdate,
        assigned_by: int,
    ) -> Todo:
        """Assign a todo to a user with visibility settings."""
        update_data = assignment_data.model_dump(exclude_unset=True)
        update_data["last_updated_by"] = assigned_by

        # If assigning to someone, set default visibility to PUBLIC
        if update_data.get("assigned_user_id") and not update_data.get("visibility"):
            update_data["visibility"] = TodoVisibility.PUBLIC.value

        # If unassigning, set visibility to PRIVATE
        if update_data.get("assigned_user_id") is None:
            update_data["visibility"] = TodoVisibility.PRIVATE.value

        return await super().update(db, db_obj=todo, obj_in=update_data)

    async def get_assignable_users(self, db: AsyncSession, *, assigner_id: int) -> list[User]:
        """Get users that can be assigned todos by the assigner."""
        return await TodoPermissionService.get_assignable_users(db, assigner_id)

    async def list_assigned_todos(
        self,
        db: AsyncSession,
        *,
        assigned_user_id: int,
        include_completed: bool = True,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[Todo], int]:
        """List todos assigned to a specific user."""
        query: Select = (
            select(Todo)
            .options(selectinload(Todo.owner), selectinload(Todo.assigned_user))
            .where(
                Todo.assigned_user_id == assigned_user_id,
                Todo.is_deleted is False,
                Todo.visibility.in_([TodoVisibility.PUBLIC.value, TodoVisibility.VIEWER.value])
            )
        )

        if not include_completed:
            query = query.where(Todo.status != TodoStatus.COMPLETED.value)

        total_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(total_query)
        total = total_result.scalar() or 0

        query = query.order_by(
            Todo.due_date.is_(None), Todo.due_date.asc(), Todo.created_at.desc()
        )
        query = query.offset(offset).limit(limit)

        result = await db.execute(query)
        todos = result.scalars().all()
        return todos, total

    async def update_viewers(
        self,
        db: AsyncSession,
        *,
        todo: Todo,
        viewers_data: TodoViewersUpdate,
        updated_by: int,
    ) -> Todo:
        """Update viewers for a todo."""
        # Update viewers
        await todo_viewer.add_viewers(
            db,
            todo_id=todo.id,
            viewer_ids=viewers_data.viewer_ids,
            added_by=updated_by
        )

        # Update last_updated_by
        todo.last_updated_by = updated_by
        db.add(todo)
        await db.commit()
        await db.refresh(todo)

        return todo

    async def create_with_viewers(
        self,
        db: AsyncSession,
        *,
        owner_id: int,
        created_by: int,
        obj_in: TodoCreate
    ) -> Todo:
        """Create a todo with viewers."""
        # Extract viewer_ids from the input
        viewer_ids = obj_in.viewer_ids or []
        obj_data = obj_in.model_dump(exclude={'viewer_ids'})

        # Create the todo first
        obj_data.setdefault("status", TodoStatus.PENDING.value)
        obj_data["owner_id"] = owner_id
        obj_data["created_by"] = created_by
        obj_data["last_updated_by"] = created_by

        if obj_data.get("due_date") and obj_data["due_date"] < datetime.now(UTC):
            obj_data["status"] = TodoStatus.EXPIRED.value
            obj_data["expired_at"] = datetime.now(UTC)

        db_obj = Todo(**obj_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)

        # Add viewers if any
        if viewer_ids:
            await todo_viewer.add_viewers(
                db,
                todo_id=db_obj.id,
                viewer_ids=viewer_ids,
                added_by=created_by
            )
            # Refresh to get viewers
            await db.refresh(db_obj)

        return db_obj

    async def create_with_owner(
        self, db: AsyncSession, *, owner_id: int, obj_in: TodoCreate
    ) -> Todo:
        """Create a todo with owner - alias for create_for_user."""
        return await self.create_for_user(db, owner_id=owner_id, created_by=owner_id, obj_in=obj_in)

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
        self, db: AsyncSession, *, todo: Todo, submitted_by: int, notes: str = None
    ) -> Todo:
        """Submit assignment for review."""
        if todo.is_assignment and todo.assigned_user_id == submitted_by:
            todo.submit_assignment()
            todo.last_updated_by = submitted_by
            if notes:
                # Add notes to existing notes if any
                if todo.notes:
                    todo.notes = f"{todo.notes}\n\n**Submission Notes:**\n{notes}"
                else:
                    todo.notes = f"**Submission Notes:**\n{notes}"
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
        assignment_status: str,
        assessment: str = None,
        score: int = None
    ) -> Todo:
        """Review and assess an assignment."""
        if todo.is_assignment and todo.owner_id == reviewer_id:
            if assignment_status == AssignmentStatus.APPROVED.value:
                todo.approve_assignment(reviewer_id, assessment, score)
            elif assignment_status == AssignmentStatus.REJECTED.value:
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
            .options(selectinload(Todo.assigned_user))
            .where(
                Todo.owner_id == reviewer_id,
                Todo.todo_type == "assignment",
                Todo.assignment_status.in_([
                    AssignmentStatus.SUBMITTED.value,
                    AssignmentStatus.UNDER_REVIEW.value
                ]),
                Todo.is_deleted is False
            )
            .order_by(Todo.submitted_at.asc())
        )
        return result.scalars().all()

    async def get_user_assignments(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        assignment_status: str = None,
        limit: int = 100,
        offset: int = 0
    ) -> tuple[list[Todo], int]:
        """Get assignments for a user (either as assignee or viewer)."""
        # Get assignments where user is assigned or is a viewer
        query: Select = (
            select(Todo)
            .options(
                selectinload(Todo.owner),
                selectinload(Todo.assigned_user),
                selectinload(Todo.viewers).selectinload(TodoViewer.user)
            )
            .where(
                Todo.todo_type == "assignment",
                Todo.publish_status == TodoPublishStatus.PUBLISHED.value,
                Todo.is_deleted is False,
                (
                    (Todo.assigned_user_id == user_id) |
                    (Todo.viewers.any(TodoViewer.user_id == user_id))
                )
            )
        )

        if assignment_status:
            query = query.where(Todo.assignment_status == assignment_status)

        total_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(total_query)
        total = total_result.scalar() or 0

        query = query.order_by(
            Todo.due_date.is_(None), Todo.due_date.asc(), Todo.created_at.desc()
        )
        query = query.offset(offset).limit(limit)

        result = await db.execute(query)
        assignments = result.scalars().all()
        return assignments, total


todo = CRUDTodo(Todo)
