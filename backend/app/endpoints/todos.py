from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.endpoints import API_ROUTES
from app.crud.todo import todo as todo_crud
from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.todo import Todo
from app.models.user import User
from app.schemas.todo import (
    TodoCreate,
    TodoListResponse,
    TodoRead,
    TodoUpdate,
)
from app.schemas.todo_viewer import (
    TodoViewerCreate,
    TodoViewerListResponse,
    TodoViewerRead,
)
from app.services.todo_permissions import TodoPermissionService
from app.services.todo_viewer_service import todo_viewer_service
from app.utils.constants import TodoStatus

router = APIRouter()


async def _get_todo_or_404(
    db: AsyncSession, *, todo_id: int, current_user: User, allow_deleted: bool = True
) -> Todo:
    todo_obj = await todo_crud.get(db, id=todo_id)
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


@router.get(API_ROUTES.TODOS.BASE, response_model=TodoListResponse)
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


@router.get(API_ROUTES.TODOS.RECENT, response_model=list[TodoRead])
async def get_recent_todos(
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Return the most recently updated todos for the current user."""
    todos = await todo_crud.list_recent(db, owner_id=current_user.id, limit=limit)
    return todos


@router.post(
    API_ROUTES.TODOS.BASE, response_model=TodoRead, status_code=status.HTTP_201_CREATED
)
async def create_todo(
    todo_in: TodoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new todo for the current user."""
    todo_obj = await todo_crud.create_for_user(
        db, owner_id=current_user.id, created_by=current_user.id, obj_in=todo_in
    )
    return todo_obj


@router.put(API_ROUTES.TODOS.BY_ID, response_model=TodoRead)
async def update_todo(
    todo_id: int,
    todo_in: TodoUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update an existing todo."""
    todo_obj = await _get_todo_or_404(
        db, todo_id=todo_id, current_user=current_user, allow_deleted=False
    )

    # Check if user can edit this todo
    if not await TodoPermissionService.can_edit_todo(db, current_user.id, todo_obj):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to edit this todo",
        )

    todo_obj = await todo_crud.update_todo(
        db, db_obj=todo_obj, obj_in=todo_in, updated_by=current_user.id
    )
    return todo_obj


@router.post(API_ROUTES.TODOS.COMPLETE, response_model=TodoRead)
async def complete_todo(
    todo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Mark a todo as completed."""
    todo_obj = await _get_todo_or_404(
        db, todo_id=todo_id, current_user=current_user, allow_deleted=False
    )

    # Check if user can change status
    if not await TodoPermissionService.can_change_status(db, current_user.id, todo_obj):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to change this todo's status",
        )

    if todo_obj.status == TodoStatus.COMPLETED.value:
        return todo_obj
    todo_obj = await todo_crud.mark_complete(
        db, todo=todo_obj, completed_by=current_user.id
    )
    return todo_obj


@router.post(API_ROUTES.TODOS.REOPEN, response_model=TodoRead)
async def reopen_todo(
    todo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Reopen a completed or expired todo."""
    todo_obj = await _get_todo_or_404(
        db, todo_id=todo_id, current_user=current_user, allow_deleted=False
    )

    # Check if user can change status
    if not await TodoPermissionService.can_change_status(db, current_user.id, todo_obj):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to change this todo's status",
        )

    if todo_obj.status == TodoStatus.PENDING.value:
        return todo_obj
    todo_obj = await todo_crud.reopen(db, todo=todo_obj, reopened_by=current_user.id)
    return todo_obj


@router.delete(API_ROUTES.TODOS.BY_ID, status_code=status.HTTP_204_NO_CONTENT)
async def soft_delete_todo(
    todo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Soft delete a todo."""
    todo_obj = await _get_todo_or_404(
        db, todo_id=todo_id, current_user=current_user, allow_deleted=False
    )

    # Check if user can delete this todo
    if not await TodoPermissionService.can_delete_todo(db, current_user.id, todo_obj):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this todo",
        )

    if not todo_obj.is_deleted:
        await todo_crud.soft_delete(db, todo=todo_obj, deleted_by=current_user.id)


@router.post(API_ROUTES.TODOS.RESTORE, response_model=TodoRead)
async def restore_todo(
    todo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Restore a soft deleted todo."""
    todo_obj = await _get_todo_or_404(
        db, todo_id=todo_id, current_user=current_user, allow_deleted=True
    )
    if not todo_obj.is_deleted:
        return todo_obj
    todo_obj = await todo_crud.restore(db, todo=todo_obj, restored_by=current_user.id)
    return todo_obj


@router.get(API_ROUTES.TODOS.ASSIGNED, response_model=TodoListResponse)
async def list_assigned_todos(
    include_completed: bool = Query(True, description="Include completed todos"),
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List todos assigned to the current user (where user is assignee)."""
    todos, total = await todo_crud.get_user_assignments(
        db,
        user_id=current_user.id,
        limit=limit,
        offset=offset,
    )

    # Filter by include_completed
    if not include_completed:
        todos = [t for t in todos if t.status != TodoStatus.COMPLETED.value]
        total = len(todos)

    return TodoListResponse(items=todos, total=total)


# =============================================================================
# Viewer Management Endpoints
# =============================================================================


@router.get(API_ROUTES.TODOS.VIEWABLE_TODOS, response_model=TodoListResponse)
async def list_viewable_todos(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List all todos that the current user can view as a viewer."""
    todos = await todo_viewer_service.get_viewable_todos_for_user(db, current_user.id)
    return TodoListResponse(items=todos, total=len(todos))


@router.get(API_ROUTES.TODOS.VIEWER_LIST, response_model=TodoViewerListResponse)
async def get_todo_viewers(
    todo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get list of viewers for a todo (creator only)."""
    try:
        viewers = await todo_viewer_service.get_viewers(
            db, current_user_id=current_user.id, todo_id=todo_id
        )
        return viewers
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(e)
        ) from e


@router.post(
    API_ROUTES.TODOS.VIEWER_ADD,
    response_model=TodoViewerRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_viewer_to_todo(
    todo_id: int,
    viewer_in: TodoViewerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Add a viewer to a todo (creator only)."""
    try:
        viewer = await todo_viewer_service.add_viewer(
            db,
            current_user_id=current_user.id,
            todo_id=todo_id,
            viewer_user_id=viewer_in.user_id,
        )
        return viewer
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
            ) from e
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(e)
        ) from e


@router.delete(API_ROUTES.TODOS.VIEWER_REMOVE, status_code=status.HTTP_204_NO_CONTENT)
async def remove_viewer_from_todo(
    todo_id: int,
    viewer_user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Remove a viewer from a todo (creator only)."""
    try:
        success = await todo_viewer_service.remove_viewer(
            db,
            current_user_id=current_user.id,
            todo_id=todo_id,
            viewer_user_id=viewer_user_id,
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Viewer not found"
            )
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
            ) from e
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(e)
        ) from e
