"""CRUD operations for TodoViewer."""

from typing import List
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.todo_viewer import TodoViewer
from app.models.user import User


class CRUDTodoViewer:
    """CRUD operations for todo viewers."""

    async def add_viewers(
        self, 
        db: AsyncSession, 
        *, 
        todo_id: int, 
        viewer_ids: List[int], 
        added_by: int
    ) -> List[TodoViewer]:
        """Add multiple viewers to a todo."""
        # Remove existing viewers first
        await self.remove_all_viewers(db, todo_id=todo_id)
        
        # Add new viewers
        viewers = []
        for user_id in viewer_ids:
            viewer = TodoViewer(
                todo_id=todo_id,
                user_id=user_id,
                added_by=added_by
            )
            db.add(viewer)
            viewers.append(viewer)
        
        await db.commit()
        
        # Refresh to get relationships
        for viewer in viewers:
            await db.refresh(viewer)
        
        return viewers

    async def get_viewers(
        self, 
        db: AsyncSession, 
        *, 
        todo_id: int
    ) -> List[TodoViewer]:
        """Get all viewers for a todo."""
        result = await db.execute(
            select(TodoViewer)
            .options(selectinload(TodoViewer.user))
            .where(TodoViewer.todo_id == todo_id)
            .order_by(TodoViewer.added_at.asc())
        )
        return list(result.scalars().all())

    async def remove_viewer(
        self, 
        db: AsyncSession, 
        *, 
        todo_id: int, 
        user_id: int
    ) -> bool:
        """Remove a specific viewer from a todo."""
        result = await db.execute(
            delete(TodoViewer).where(
                TodoViewer.todo_id == todo_id,
                TodoViewer.user_id == user_id
            )
        )
        await db.commit()
        return result.rowcount > 0

    async def remove_all_viewers(
        self, 
        db: AsyncSession, 
        *, 
        todo_id: int
    ) -> None:
        """Remove all viewers from a todo."""
        await db.execute(
            delete(TodoViewer).where(TodoViewer.todo_id == todo_id)
        )
        await db.commit()

    async def is_viewer(
        self, 
        db: AsyncSession, 
        *, 
        todo_id: int, 
        user_id: int
    ) -> bool:
        """Check if user is a viewer of the todo."""
        result = await db.execute(
            select(TodoViewer).where(
                TodoViewer.todo_id == todo_id,
                TodoViewer.user_id == user_id
            )
        )
        return result.scalars().first() is not None

    async def get_user_viewed_todos(
        self, 
        db: AsyncSession, 
        *, 
        user_id: int
    ) -> List[int]:
        """Get list of todo IDs that user is a viewer of."""
        result = await db.execute(
            select(TodoViewer.todo_id).where(TodoViewer.user_id == user_id)
        )
        return list(result.scalars().all())


todo_viewer = CRUDTodoViewer()