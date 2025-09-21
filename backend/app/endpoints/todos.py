from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

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
from app.utils.constants import TodoStatus

router = APIRouter()


async def _get_todo_or_404(
    db: AsyncSession, *, todo_id: int, current_user: User, allow_deleted: bool = True
) -> Todo:
    todo_obj = await todo_crud.get(db, todo_id)
    if not todo_obj or todo_obj.owner_id != current_user.id:
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
        owner_id=current_user.id,
        status=status_filter,
        include_completed=include_completed,
        include_deleted=include_deleted,
        limit=limit,
        offset=offset,
    )
    return TodoListResponse(items=todos, total=total)


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
    todo_obj = await todo_crud.create_for_user(
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
    if todo_obj.status == TodoStatus.PENDING.value:
        return todo_obj
    todo_obj = await todo_crud.reopen(db, todo=todo_obj, reopened_by=current_user.id)
    return todo_obj


@router.delete("/{todo_id}", response_model=TodoRead)
async def soft_delete_todo(
    todo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Soft delete a todo."""
    todo_obj = await _get_todo_or_404(db, todo_id=todo_id, current_user=current_user, allow_deleted=False)
    if todo_obj.is_deleted:
        return todo_obj
    todo_obj = await todo_crud.soft_delete(db, todo=todo_obj, deleted_by=current_user.id)
    return todo_obj


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
