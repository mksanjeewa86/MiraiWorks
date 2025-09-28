from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.todo import todo as todo_crud
from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.todo import Todo
from app.models.user import User
from app.schemas.todo import (
    AssignableUser,
    AssignmentReview,
    AssignmentSubmission,
    AssignmentWorkflowResponse,
    TodoAssignmentUpdate,
    TodoCreate,
    TodoListResponse,
    TodoPublishUpdate,
    TodoRead,
    TodoUpdate,
    TodoViewersUpdate,
    TodoWithAssignedUser,
)
from app.services.todo_permissions import TodoPermissionService
from app.utils.constants import TodoStatus

router = APIRouter()


async def _get_todo_or_404(
    db: AsyncSession, *, todo_id: int, current_user: User, allow_deleted: bool = True
) -> Todo:
    todo_obj = await todo_crud.get_with_assigned_user(db, todo_id=todo_id)
    if not todo_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found"
        )

    # Check if user can view this todo
    if not await TodoPermissionService.can_view_todo(db, current_user.id, todo_obj):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found"
        )

    if not allow_deleted and todo_obj.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found"
        )
    return todo_obj


@router.get("", response_model=TodoListResponse)
async def list_todos(
    include_completed: bool = Query(True, description="Include completed todos"),
    include_deleted: bool = Query(False, description="Include deleted todos"),
    status_filter: str | None = Query(None, alias="status"),
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List todos for the current user."""
    if status_filter is not None and status_filter not in {
        status.value for status in TodoStatus
    }:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status filter",
        )

    todos, total = await todo_crud.list_for_user(
        db,
        user_id=current_user.id,
        status=status_filter,
        include_completed=include_completed,
        include_deleted=include_deleted,
        limit=limit,
        offset=offset,
    )
    return TodoListResponse(items=todos, total=total)


@router.put("/{todo_id}/viewers", response_model=TodoRead)
async def update_todo_viewers(
    todo_id: int,
    viewers_data: TodoViewersUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update viewers for a todo."""
    todo_obj = await _get_todo_or_404(db, todo_id=todo_id, current_user=current_user, allow_deleted=False)

    # Check if user can assign this todo (only creator can manage viewers)
    if not await TodoPermissionService.can_assign_todo(db, current_user.id, todo_obj):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to manage viewers for this todo"
        )

    # Validate viewer user IDs exist and are valid
    for user_id in viewers_data.viewer_ids:
        if not await TodoPermissionService.can_assign_to_user(db, current_user.id, user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot add user {user_id} as viewer"
            )

    todo_obj = await todo_crud.update_viewers(
        db, todo=todo_obj, viewers_data=viewers_data, updated_by=current_user.id
    )
    return todo_obj


@router.get("/recent", response_model=list[TodoRead])
async def get_recent_todos(
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Return the most recently updated todos for the current user."""
    todos = await todo_crud.list_recent(db, owner_id=current_user.id, limit=limit)
    return todos


@router.post("", response_model=TodoRead, status_code=status.HTTP_201_CREATED)
async def create_todo(
    todo_in: TodoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new todo for the current user."""
    # Use create_with_viewers to handle viewer_ids
    todo_obj = await todo_crud.create_with_viewers(
        db, owner_id=current_user.id, created_by=current_user.id, obj_in=todo_in
    )
    return todo_obj


@router.put("/{todo_id}", response_model=TodoRead)
async def update_todo(
    todo_id: int,
    todo_in: TodoUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update an existing todo."""
    todo_obj = await _get_todo_or_404(db, todo_id=todo_id, current_user=current_user, allow_deleted=False)

    # Check if user can edit this todo
    if not await TodoPermissionService.can_edit_todo(db, current_user.id, todo_obj):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to edit this todo"
        )

    todo_obj = await todo_crud.update_todo(
        db, db_obj=todo_obj, obj_in=todo_in, updated_by=current_user.id
    )
    return todo_obj


@router.post("/{todo_id}/complete", response_model=TodoRead)
async def complete_todo(
    todo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Mark a todo as completed."""
    todo_obj = await _get_todo_or_404(db, todo_id=todo_id, current_user=current_user, allow_deleted=False)

    # Check if user can change status
    if not await TodoPermissionService.can_change_status(db, current_user.id, todo_obj):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to change this todo's status"
        )

    if todo_obj.status == TodoStatus.COMPLETED.value:
        return todo_obj
    todo_obj = await todo_crud.mark_complete(
        db, todo=todo_obj, completed_by=current_user.id
    )
    return todo_obj


@router.post("/{todo_id}/reopen", response_model=TodoRead)
async def reopen_todo(
    todo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Reopen a completed or expired todo."""
    todo_obj = await _get_todo_or_404(db, todo_id=todo_id, current_user=current_user, allow_deleted=False)

    # Check if user can change status
    if not await TodoPermissionService.can_change_status(db, current_user.id, todo_obj):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to change this todo's status"
        )

    if todo_obj.status == TodoStatus.PENDING.value:
        return todo_obj
    todo_obj = await todo_crud.reopen(db, todo=todo_obj, reopened_by=current_user.id)
    return todo_obj


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def soft_delete_todo(
    todo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Soft delete a todo."""
    todo_obj = await _get_todo_or_404(db, todo_id=todo_id, current_user=current_user, allow_deleted=False)

    # Check if user can delete this todo
    if not await TodoPermissionService.can_delete_todo(db, current_user.id, todo_obj):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this todo"
        )

    if not todo_obj.is_deleted:
        await todo_crud.soft_delete(db, todo=todo_obj, deleted_by=current_user.id)


@router.post("/{todo_id}/restore", response_model=TodoRead)
async def restore_todo(
    todo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Restore a soft deleted todo."""
    todo_obj = await _get_todo_or_404(db, todo_id=todo_id, current_user=current_user, allow_deleted=True)
    if not todo_obj.is_deleted:
        return todo_obj
    todo_obj = await todo_crud.restore(db, todo=todo_obj, restored_by=current_user.id)
    return todo_obj


# Assignment-related endpoints
@router.get("/assignable-users", response_model=list[AssignableUser])
async def get_assignable_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get list of users that can be assigned todos by the current user."""
    users = await todo_crud.get_assignable_users(db, assigner_id=current_user.id)
    return users


@router.get("/{todo_id}/details", response_model=TodoWithAssignedUser)
async def get_todo_with_assigned_user(
    todo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get todo details including assigned user information."""
    todo_obj = await _get_todo_or_404(db, todo_id=todo_id, current_user=current_user, allow_deleted=False)
    return todo_obj


@router.put("/{todo_id}/assign", response_model=TodoRead)
async def assign_todo(
    todo_id: int,
    assignment_data: TodoAssignmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Assign a todo to a user with visibility settings."""
    todo_obj = await _get_todo_or_404(db, todo_id=todo_id, current_user=current_user, allow_deleted=False)

    # Check if user can assign this todo
    if not await TodoPermissionService.can_assign_todo(db, current_user.id, todo_obj):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to assign this todo"
        )

    # If assigning to someone, validate they can be assigned
    if assignment_data.assigned_user_id:
        if not await TodoPermissionService.can_assign_to_user(
            db, current_user.id, assignment_data.assigned_user_id
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot assign todo to this user"
            )

    todo_obj = await todo_crud.assign_todo(
        db, todo=todo_obj, assignment_data=assignment_data, assigned_by=current_user.id
    )
    return todo_obj


@router.get("/assigned", response_model=TodoListResponse)
async def list_assigned_todos(
    include_completed: bool = Query(True, description="Include completed todos"),
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List todos assigned to the current user."""
    todos, total = await todo_crud.list_assigned_todos(
        db,
        assigned_user_id=current_user.id,
        include_completed=include_completed,
        limit=limit,
        offset=offset,
    )
    return TodoListResponse(items=todos, total=total)
