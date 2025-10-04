"""User connections API endpoints."""


from app.config.endpoints import API_ROUTES
from app.config.endpoints import API_ROUTES
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.user import UserResponse
from app.services.user_connection_service import user_connection_service

router = APIRouter()


@router.post(API_ROUTES.USER_CONNECTIONS.CONNECT)
async def connect_to_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a connection with another user."""

    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot connect to yourself"
        )

    try:
        connection = await user_connection_service.connect_users(
            db=db,
            user_id=current_user.id,
            connected_user_id=user_id,
            creation_type="manual",
            created_by=current_user.id,
        )

        return {
            "message": "Connection created successfully",
            "connection_id": connection.id,
        }

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(API_ROUTES.USER_CONNECTIONS.DISCONNECT)
async def disconnect_from_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove connection with another user."""

    success = await user_connection_service.disconnect_users(
        db=db, user_id=current_user.id, connected_user_id=user_id
    )

    if success:
        return {"message": "Connection removed successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Connection not found"
        )


@router.get(
    API_ROUTES.USER_CONNECTIONS.MY_CONNECTIONS, response_model=list[UserResponse]
)
async def get_my_connections(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all users connected to current user."""

    connected_users = await user_connection_service.get_connected_users(
        db=db, user_id=current_user.id
    )

    return connected_users


@router.get(
    API_ROUTES.USER_CONNECTIONS.ASSIGNABLE_USERS, response_model=list[UserResponse]
)
async def get_assignable_users(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get users that can be assigned todos (same as connected users for now)."""

    connected_users = await user_connection_service.get_connected_users(
        db=db, user_id=current_user.id
    )

    # If no connections, return self for testing
    if not connected_users:
        return [current_user]

    return connected_users
