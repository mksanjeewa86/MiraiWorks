from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Select, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.todo import Todo
from app.schemas.todo import TodoCreate, TodoUpdate
from app.utils.constants import TodoStatus


class CRUDTodo(CRUDBase[Todo, TodoCreate, TodoUpdate]):
    """CRUD operations for Todo items."""

    async def auto_mark_expired(self, db: AsyncSession, owner_id: int) -> None:
        """Automatically mark overdue todos as expired."""
        now = datetime.now(timezone.utc)
        await db.execute(
            update(Todo)
            .where(
                Todo.owner_id == owner_id,
                Todo.due_date.isnot(None),
                Todo.status.notin_([TodoStatus.COMPLETED.value, TodoStatus.EXPIRED.value]),
                Todo.due_date < now,
            )
            .values(status=TodoStatus.EXPIRED.value, expired_at=now)
        )
        await db.commit()

    async def list_for_user(
        self,
        db: AsyncSession,
        *,
        owner_id: int,
        status: str | None = None,
        include_completed: bool = True,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[Todo], int]:
        await self.auto_mark_expired(db, owner_id)

        query: Select = select(Todo).where(Todo.owner_id == owner_id)

        if status:
            query = query.where(Todo.status == status)
        elif not include_completed:
            query = query.where(Todo.status != TodoStatus.COMPLETED.value)

        total_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(total_query)
        total = total_result.scalar() or 0

        query = query.order_by(Todo.due_date.is_(None), Todo.due_date.asc(), Todo.created_at.desc())
        query = query.offset(offset).limit(limit)

        result = await db.execute(query)
        todos = result.scalars().all()
        return todos, total

    async def list_recent(self, db: AsyncSession, *, owner_id: int, limit: int = 5) -> list[Todo]:
        await self.auto_mark_expired(db, owner_id)
        result = await db.execute(
            select(Todo)
            .where(Todo.owner_id == owner_id)
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

        if data.get("due_date") and data["due_date"] < datetime.now(timezone.utc):
            data["status"] = TodoStatus.EXPIRED.value
            data["expired_at"] = datetime.now(timezone.utc)

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
            update_data.setdefault("completed_at", datetime.now(timezone.utc))
            update_data.pop("expired_at", None)
        elif update_data.get("status") == TodoStatus.PENDING.value:
            update_data.setdefault("completed_at", None)
            update_data.setdefault("expired_at", None)

        update_data["last_updated_by"] = updated_by

        return await super().update(db, db_obj=db_obj, obj_in=update_data)

    async def mark_complete(self, db: AsyncSession, *, todo: Todo, completed_by: int) -> Todo:
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


todo = CRUDTodo(Todo)
