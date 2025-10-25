"""Service for managing todo viewers with permission enforcement."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.todo import todo as todo_crud
from app.crud.todo_viewer import todo_viewer as todo_viewer_crud
from app.models.todo import Todo
from app.models.todo_viewer import TodoViewer
from app.schemas.todo_viewer import TodoViewerListResponse, TodoViewerWithUser


class TodoViewerService:
    """Service to handle todo viewer operations with permission checks."""

    @staticmethod
    async def can_manage_viewers(db: AsyncSession, user_id: int, todo: Todo) -> bool:
        """Check if user can manage (add/remove) viewers for a todo.

        Only the creator (owner) can manage viewers.
        """
        return todo.owner_id == user_id or todo.created_by == user_id

    @staticmethod
    async def can_view_viewers_list(db: AsyncSession, user_id: int, todo: Todo) -> bool:
        """Check if user can view the list of viewers.

        Only the creator can see the viewers list.
        Viewers and assignees cannot see other viewers.
        """
        return todo.owner_id == user_id or todo.created_by == user_id

    @staticmethod
    async def is_viewer(db: AsyncSession, user_id: int, todo_id: int) -> bool:
        """Check if user is a viewer of the todo."""
        return await todo_viewer_crud.is_viewer(db, todo_id=todo_id, user_id=user_id)

    @staticmethod
    async def can_view_as_viewer(db: AsyncSession, user_id: int, todo: Todo) -> bool:
        """Check if user can view todo as a viewer.

        Viewers can only view if:
        - They are in the viewers list
        - Todo is published
        - Todo is not deleted
        """
        if todo.is_deleted or todo.publish_status != "published":
            return False

        return await TodoViewerService.is_viewer(db, user_id, todo.id)

    @staticmethod
    async def add_viewer(
        db: AsyncSession, *, current_user_id: int, todo_id: int, viewer_user_id: int
    ) -> TodoViewer:
        """Add a viewer to a todo.

        Args:
            current_user_id: ID of the user adding the viewer (must be creator)
            todo_id: ID of the todo
            viewer_user_id: ID of the user to add as viewer

        Raises:
            ValueError: If user doesn't have permission or viewer is invalid
        """
        # Get todo
        todo = await todo_crud.get(db, todo_id)
        if not todo:
            raise ValueError("Todo not found")

        # Check permission
        if not await TodoViewerService.can_manage_viewers(db, current_user_id, todo):
            raise ValueError("Only the creator can manage viewers")

        # Cannot add owner/creator as viewer
        if viewer_user_id == todo.owner_id or viewer_user_id == todo.created_by:
            raise ValueError("Creator cannot be added as a viewer")

        # Add viewer
        viewer = await todo_viewer_crud.add_viewer(
            db, todo_id=todo_id, user_id=viewer_user_id, added_by=current_user_id
        )
        return viewer

    @staticmethod
    async def remove_viewer(
        db: AsyncSession, *, current_user_id: int, todo_id: int, viewer_user_id: int
    ) -> bool:
        """Remove a viewer from a todo.

        Args:
            current_user_id: ID of the user removing the viewer (must be creator)
            todo_id: ID of the todo
            viewer_user_id: ID of the viewer to remove

        Raises:
            ValueError: If user doesn't have permission
        """
        # Get todo
        todo = await todo_crud.get(db, todo_id)
        if not todo:
            raise ValueError("Todo not found")

        # Check permission
        if not await TodoViewerService.can_manage_viewers(db, current_user_id, todo):
            raise ValueError("Only the creator can manage viewers")

        # Remove viewer
        return await todo_viewer_crud.remove_viewer(
            db, todo_id=todo_id, user_id=viewer_user_id
        )

    @staticmethod
    async def get_viewers(
        db: AsyncSession, *, current_user_id: int, todo_id: int
    ) -> TodoViewerListResponse:
        """Get list of viewers for a todo.

        Only the creator can see the viewers list.

        Args:
            current_user_id: ID of the user requesting the list
            todo_id: ID of the todo

        Raises:
            ValueError: If user doesn't have permission
        """
        # Get todo
        todo = await todo_crud.get(db, todo_id)
        if not todo:
            raise ValueError("Todo not found")

        # Check permission
        if not await TodoViewerService.can_view_viewers_list(db, current_user_id, todo):
            raise ValueError("Only the creator can view the viewers list")

        # Get viewers with user info
        viewers = await todo_viewer_crud.get_viewers_for_todo(db, todo_id=todo_id)

        # Convert to response schema
        viewer_items = [TodoViewerWithUser.model_validate(viewer) for viewer in viewers]

        return TodoViewerListResponse(items=viewer_items, total=len(viewer_items))

    @staticmethod
    async def get_viewable_todos_for_user(db: AsyncSession, user_id: int) -> list[Todo]:
        """Get all todos that a user can view as a viewer."""
        viewer_records = await todo_viewer_crud.get_todos_for_viewer(
            db, user_id=user_id
        )

        # Filter out deleted and draft todos
        todos = [
            vr.todo
            for vr in viewer_records
            if not vr.todo.is_deleted and vr.todo.publish_status == "published"
        ]

        return todos


todo_viewer_service = TodoViewerService()
