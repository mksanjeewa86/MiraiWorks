"""Todo permission service for role-based access control."""


from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.todo_viewer import todo_viewer
from app.models.role import Role, UserRole
from app.models.todo import Todo
from app.models.todo_extension_request import TodoExtensionRequest
from app.models.user import User
from app.utils.constants import TodoStatus, TodoVisibility
from app.utils.constants import UserRole as UserRoleEnum


class TodoPermissionService:
    """Service to handle todo assignment and permission logic."""

    @staticmethod
    async def get_user_roles(db: AsyncSession, user_id: int) -> list[str]:
        """Get all roles for a user."""
        query = (
            select(Role.name)
            .join(UserRole, Role.id == UserRole.role_id)
            .where(UserRole.user_id == user_id)
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def is_employer(db: AsyncSession, user_id: int) -> bool:
        """Check if user has member role (formerly employer)."""
        roles = await TodoPermissionService.get_user_roles(db, user_id)
        return UserRoleEnum.MEMBER.value in roles

    @staticmethod
    async def is_candidate(db: AsyncSession, user_id: int) -> bool:
        """Check if user has candidate role."""
        roles = await TodoPermissionService.get_user_roles(db, user_id)
        return UserRoleEnum.CANDIDATE.value in roles

    @staticmethod
    async def is_recruiter(db: AsyncSession, user_id: int) -> bool:
        """Check if user has member role (formerly recruiter)."""
        roles = await TodoPermissionService.get_user_roles(db, user_id)
        return UserRoleEnum.MEMBER.value in roles

    @staticmethod
    async def can_create_todo(db: AsyncSession, user_id: int) -> bool:
        """Check if user can create todos."""
        # Any user can create todos (they become the creator/owner)
        return True

    @staticmethod
    async def can_assign_todo(db: AsyncSession, user_id: int, todo: Todo) -> bool:
        """Check if user can assign/reassign a todo."""
        # Only the creator (owner) can assign todos
        return todo.owner_id == user_id

    @staticmethod
    async def can_view_todo(db: AsyncSession, user_id: int, todo: Todo) -> bool:
        """Check if user can view a todo."""
        # Creator (owner) can always view
        if todo.owner_id == user_id:
            return True

        # Assigned user can view if visibility allows (PUBLIC or VIEWER)
        if todo.assigned_user_id == user_id:
            return todo.visibility in [TodoVisibility.PUBLIC.value, TodoVisibility.VIEWER.value]

        # Check if user is in viewers list
        if await todo_viewer.is_viewer(db, todo_id=todo.id, user_id=user_id):
            return True

        return False

    @staticmethod
    async def can_edit_todo(db: AsyncSession, user_id: int, todo: Todo) -> bool:
        """Check if user can edit a todo."""
        # Creator (owner) can always edit
        if todo.owner_id == user_id:
            return True

        # Assignee can edit if visibility is PUBLIC (not VIEWER)
        if todo.assigned_user_id == user_id and todo.visibility == TodoVisibility.PUBLIC.value:
            return True

        return False

    @staticmethod
    async def can_delete_todo(db: AsyncSession, user_id: int, todo: Todo) -> bool:
        """Check if user can delete a todo."""
        # Only the creator (owner) can delete todos
        return todo.owner_id == user_id

    @staticmethod
    async def can_change_status(db: AsyncSession, user_id: int, todo: Todo) -> bool:
        """Check if user can change todo status."""
        # Creator (owner) can always change status
        if todo.owner_id == user_id:
            return True

        # Assignee can change status if visibility is PUBLIC (not VIEWER)
        if todo.assigned_user_id == user_id and todo.visibility == TodoVisibility.PUBLIC.value:
            return True

        return False

    @staticmethod
    async def can_add_attachments(db: AsyncSession, user_id: int, todo: Todo) -> bool:
        """Check if user can add attachments to a todo."""
        # Creator (owner) can always add attachments
        if todo.owner_id == user_id:
            return True

        # Assignee can add attachments if visibility is PUBLIC (not VIEWER)
        if todo.assigned_user_id == user_id and todo.visibility == TodoVisibility.PUBLIC.value:
            return True

        return False

    @staticmethod
    async def can_assign_to_user(db: AsyncSession, assigner_id: int, assignee_id: int) -> bool:
        """Check if assigner can assign todos to assignee."""
        # Any creator can assign to any active user
        query = select(User).where(
            User.id == assignee_id,
            User.is_active is True,
            User.is_deleted is False
        )
        result = await db.execute(query)
        user = result.scalars().first()
        return user is not None

    @staticmethod
    async def get_assignable_users(db: AsyncSession, assigner_id: int) -> list[User]:
        """Get list of users that can be assigned todos by the assigner."""
        # Import here to avoid circular import
        from app.services.user_connection_service import user_connection_service

        # Use simple connection service to get connected users
        try:
            connected_users = await user_connection_service.get_connected_users(db, assigner_id)

            # If no connections exist, fall back to including the user themselves
            # This provides a smooth transition and allows self-assignment for testing
            if not connected_users:
                query = select(User).where(
                    User.id == assigner_id,
                    User.is_active is True,
                    User.is_deleted is False
                )
                result = await db.execute(query)
                self_user = result.scalars().first()
                return [self_user] if self_user else []

            return connected_users

        except Exception as e:
            # Fallback to original behavior if connection service fails
            print(f"Connection service error, falling back: {e}")
            query = (
                select(User)
                .where(
                    User.is_active is True,
                    User.is_deleted is False,
                    User.id != assigner_id  # Don't include the assigner themselves
                )
            )

            result = await db.execute(query)
            return list(result.scalars().all())

    @staticmethod
    async def filter_todos_by_permission(
        db: AsyncSession,
        user_id: int,
        todos: list[Todo]
    ) -> list[Todo]:
        """Filter todos based on user permissions."""
        filtered_todos = []

        for todo in todos:
            if await TodoPermissionService.can_view_todo(db, user_id, todo):
                filtered_todos.append(todo)

        return filtered_todos

    # Extension request permissions
    @staticmethod
    async def can_request_extension(db: AsyncSession, user_id: int, todo: Todo) -> bool:
        """Check if user can request due date extension for a todo."""
        # Must be assigned user
        if todo.assigned_user_id != user_id:
            return False

        # Todo must have a due date
        if not todo.due_date:
            return False

        # Todo must not be completed or deleted
        if todo.status == TodoStatus.COMPLETED.value or todo.is_deleted:
            return False

        # Must have PUBLIC visibility (not just VIEWER)
        if todo.visibility != TodoVisibility.PUBLIC.value:
            return False

        return True

    @staticmethod
    async def can_respond_to_extension(db: AsyncSession, user_id: int, extension_request: TodoExtensionRequest) -> bool:
        """Check if user can respond to an extension request."""
        # Only the creator (owner) can respond to extension requests
        return extension_request.creator_id == user_id

    @staticmethod
    async def can_view_extension_request(db: AsyncSession, user_id: int, extension_request: TodoExtensionRequest) -> bool:
        """Check if user can view an extension request."""
        # Creator can always view
        if extension_request.creator_id == user_id:
            return True

        # Requester can view their own requests
        if extension_request.requested_by_id == user_id:
            return True

        # Check if user is a viewer of the todo
        if await todo_viewer.is_viewer(db, todo_id=extension_request.todo_id, user_id=user_id):
            return True

        return False
