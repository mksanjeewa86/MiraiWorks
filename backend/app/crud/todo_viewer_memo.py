from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.todo_viewer_memo import TodoViewerMemo
from app.schemas.todo_viewer_memo import TodoViewerMemoCreate, TodoViewerMemoUpdate


class CRUDTodoViewerMemo(
    CRUDBase[TodoViewerMemo, TodoViewerMemoCreate, TodoViewerMemoUpdate]
):
    async def get_by_todo_and_user(
        self, db: AsyncSession, *, todo_id: int, user_id: int
    ) -> TodoViewerMemo | None:
        """Get viewer memo for specific todo and user."""
        result = await db.execute(
            select(TodoViewerMemo).where(
                TodoViewerMemo.todo_id == todo_id, TodoViewerMemo.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def create_or_update(
        self, db: AsyncSession, *, todo_id: int, user_id: int, memo: str | None
    ) -> TodoViewerMemo:
        """Create or update viewer memo."""
        existing = await self.get_by_todo_and_user(db, todo_id=todo_id, user_id=user_id)

        if existing:
            existing.memo = memo
            await db.commit()
            await db.refresh(existing)
            return existing
        else:
            db_obj = TodoViewerMemo(todo_id=todo_id, user_id=user_id, memo=memo)
            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
            return db_obj


todo_viewer_memo = CRUDTodoViewerMemo(TodoViewerMemo)
