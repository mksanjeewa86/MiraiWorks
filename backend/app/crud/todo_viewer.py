"""CRUD operations for TodoViewer model."""

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.todo_viewer import TodoViewer
from app.schemas.todo_viewer import TodoViewerCreate


class CRUDTodoViewer(CRUDBase[TodoViewer, TodoViewerCreate, TodoViewerCreate]):
    """CRUD operations for TodoViewer."""

    async def get_by_todo_and_user(
        self, db: AsyncSession, *, todo_id: int, user_id: int
    ) -> TodoViewer | None:
        """Get viewer by todo_id and user_id."""
        result = await db.execute(
            select(TodoViewer).where(
                and_(TodoViewer.todo_id == todo_id, TodoViewer.user_id == user_id)
            )
        )
        return result.scalar_one_or_none()

    async def get_viewers_for_todo(
        self, db: AsyncSession, *, todo_id: int
    ) -> list[TodoViewer]:
        """Get all viewers for a todo with user information."""
        result = await db.execute(
            select(TodoViewer)
            .where(TodoViewer.todo_id == todo_id)
            .options(selectinload(TodoViewer.user))
        )
        return list(result.scalars().all())

    async def get_todos_for_viewer(
        self, db: AsyncSession, *, user_id: int
    ) -> list[TodoViewer]:
        """Get all todos that a user is viewing."""
        result = await db.execute(
            select(TodoViewer)
            .where(TodoViewer.user_id == user_id)
            .options(selectinload(TodoViewer.todo))
        )
        return list(result.scalars().all())

    async def is_viewer(
        self, db: AsyncSession, *, todo_id: int, user_id: int
    ) -> bool:
        """Check if user is a viewer of the todo."""
        viewer = await self.get_by_todo_and_user(db, todo_id=todo_id, user_id=user_id)
        return viewer is not None

    async def add_viewer(
        self, db: AsyncSession, *, todo_id: int, user_id: int, added_by: int
    ) -> TodoViewer:
        """Add a viewer to a todo."""
        # Check if viewer already exists
        existing = await self.get_by_todo_and_user(db, todo_id=todo_id, user_id=user_id)
        if existing:
            return existing

        # Create new viewer
        viewer = TodoViewer(todo_id=todo_id, user_id=user_id, added_by=added_by)
        db.add(viewer)
        await db.commit()
        await db.refresh(viewer)
        return viewer

    async def remove_viewer(
        self, db: AsyncSession, *, todo_id: int, user_id: int
    ) -> bool:
        """Remove a viewer from a todo."""
        viewer = await self.get_by_todo_and_user(db, todo_id=todo_id, user_id=user_id)
        if not viewer:
            return False

        await db.delete(viewer)
        await db.commit()
        return True

    async def remove_all_viewers(self, db: AsyncSession, *, todo_id: int) -> int:
        """Remove all viewers from a todo. Returns number of viewers removed."""
        viewers = await self.get_viewers_for_todo(db, todo_id=todo_id)
        count = len(viewers)
        for viewer in viewers:
            await db.delete(viewer)
        await db.commit()
        return count


todo_viewer = CRUDTodoViewer(TodoViewer)
