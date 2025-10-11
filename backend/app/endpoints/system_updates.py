"""
System Update Endpoints

API endpoints for managing system-wide updates.
Only system administrators can create/manage updates.
All authenticated users can view them.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.system_update import system_update as system_update_crud
from app.database import get_db
from app.endpoints.auth import get_current_active_user
from app.models.role import Role, UserRole
from app.models.user import User
from app.schemas.system_update import (
    SystemUpdateCreate,
    SystemUpdateInfo,
    SystemUpdateUpdate,
    SystemUpdateWithCreator,
)

router = APIRouter()


async def get_current_system_admin(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Dependency to verify the current user is a system administrator.

    Args:
        current_user: Currently authenticated user
        db: Database session

    Returns:
        User if they are a system admin

    Raises:
        HTTPException: If user is not a system admin
    """
    # Check if user has system_admin role using SQLAlchemy ORM
    query = (
        select(Role.name)
        .join(UserRole, Role.id == UserRole.role_id)
        .where(UserRole.user_id == current_user.id)
    )

    result = await db.execute(query)
    roles = [row[0] for row in result.all()]

    if "system_admin" not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only system administrators can perform this action",
        )

    return current_user


@router.get("", response_model=list[SystemUpdateInfo])
async def get_system_updates(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records"),
    tags: list[str] | None = Query(None, description="Filter by tags"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get all active system updates.

    All authenticated users can view system updates.
    """
    if tags:
        updates = await system_update_crud.get_by_tags(
            db, tags=tags, skip=skip, limit=limit
        )
    else:
        updates = await system_update_crud.get_all_active(db, skip=skip, limit=limit)

    return updates


@router.get("/{update_id}", response_model=SystemUpdateWithCreator)
async def get_system_update(
    update_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get a specific system update by ID with creator information.

    All authenticated users can view system updates.
    """
    update = await system_update_crud.get_with_creator(db, update_id=update_id)

    if not update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="System update not found"
        )

    # Add creator name if available
    result = SystemUpdateWithCreator.from_orm(update)
    if update.created_by:
        result.created_by_name = update.created_by.full_name

    return result


@router.post("", response_model=SystemUpdateInfo, status_code=status.HTTP_201_CREATED)
async def create_system_update(
    update_in: SystemUpdateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_system_admin),
) -> Any:
    """
    Create a new system update.

    Only system administrators can create updates.
    """
    # Convert Pydantic model to dict and handle enum serialization
    update_data = update_in.model_dump()
    update_data["tags"] = [tag.value for tag in update_in.tags]

    update = await system_update_crud.create_with_creator(
        db, obj_in=update_data, creator_id=current_user.id
    )

    await db.commit()
    await db.refresh(update)

    return update


@router.put("/{update_id}", response_model=SystemUpdateInfo)
async def update_system_update(
    update_id: int,
    update_in: SystemUpdateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_system_admin),
) -> Any:
    """
    Update an existing system update.

    Only system administrators can update.
    """
    update = await system_update_crud.get(db, id=update_id)

    if not update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="System update not found"
        )

    # Convert Pydantic model to dict and handle enum serialization
    update_data = update_in.model_dump(exclude_unset=True)
    if "tags" in update_data and update_data["tags"] is not None:
        update_data["tags"] = [tag.value for tag in update_in.tags]

    updated = await system_update_crud.update(db, db_obj=update, obj_in=update_data)

    await db.commit()
    await db.refresh(updated)

    return updated


@router.delete("/{update_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_system_update(
    update_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_system_admin),
) -> None:
    """
    Deactivate a system update (soft delete).

    Only system administrators can deactivate updates.
    """
    update = await system_update_crud.deactivate(db, update_id=update_id)

    if not update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="System update not found"
        )

    await db.commit()


@router.post("/{update_id}/activate", response_model=SystemUpdateInfo)
async def activate_system_update(
    update_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_system_admin),
) -> Any:
    """
    Activate a previously deactivated system update.

    Only system administrators can activate updates.
    """
    update = await system_update_crud.activate(db, update_id=update_id)

    if not update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="System update not found"
        )

    await db.commit()
    await db.refresh(update)

    return update
