import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.endpoints import API_ROUTES
from app.crud.calendar_connection import calendar_connection
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.calendar_connection import (
    CalendarConnectionPublic,
    CalendarConnectionResponse,
    CalendarConnectionUpdate,
    CalendarListResponse,
    GoogleCalendarAuth,
    OutlookCalendarAuth,
)
from app.services.calendar_service import CalendarService

logger = structlog.get_logger()

router = APIRouter()
calendar_service = CalendarService()


@router.get(API_ROUTES.CALENDAR_CONNECTIONS.BASE, response_model=CalendarListResponse)
async def get_calendar_connections(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all calendar connections for the current user"""
    try:
        connections = await calendar_connection.get_by_user(db, current_user.id)

        return CalendarListResponse(
            connections=[
                CalendarConnectionPublic.from_orm(conn) for conn in connections
            ]
        )
    except Exception as e:
        logger.error(
            "Failed to get calendar connections", error=str(e), user_id=current_user.id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve calendar connections",
        ) from e


@router.get(
    API_ROUTES.CALENDAR_CONNECTIONS.BY_ID, response_model=CalendarConnectionPublic
)
async def get_calendar_connection(
    connection_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific calendar connection"""
    connection = await calendar_connection.get_by_user_and_id(
        db, current_user.id, connection_id
    )

    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar connection not found",
        )

    return CalendarConnectionPublic.from_orm(connection)


@router.put(
    API_ROUTES.CALENDAR_CONNECTIONS.BY_ID, response_model=CalendarConnectionResponse
)
async def update_calendar_connection(
    connection_id: int,
    connection_update: CalendarConnectionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update calendar connection settings"""
    try:
        connection = await calendar_connection.get_by_user_and_id(
            db, current_user.id, connection_id
        )

        if not connection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Calendar connection not found",
            )

        connection = await calendar_connection.update(
            db, db_obj=connection, obj_in=connection_update
        )

        logger.info(
            "Calendar connection updated",
            connection_id=connection_id,
            user_id=current_user.id,
        )

        return CalendarConnectionResponse(
            message="Calendar connection updated successfully",
            connection=CalendarConnectionPublic.from_orm(connection),
        )
    except Exception as e:
        logger.error(
            "Failed to update calendar connection",
            error=str(e),
            connection_id=connection_id,
            user_id=current_user.id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update calendar connection",
        ) from e


@router.delete(API_ROUTES.CALENDAR_CONNECTIONS.BY_ID)
async def delete_calendar_connection(
    connection_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a calendar connection"""
    try:
        connection = await calendar_connection.get_by_user_and_id(
            db, current_user.id, connection_id
        )

        if not connection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Calendar connection not found",
            )

        # Revoke tokens if possible
        try:
            await calendar_service.revoke_tokens(connection)
        except Exception as e:
            logger.warning(
                "Failed to revoke tokens during deletion",
                error=str(e),
                connection_id=connection_id,
            )

        await calendar_connection.remove(db, id=connection_id)

        logger.info(
            "Calendar connection deleted",
            connection_id=connection_id,
            user_id=current_user.id,
        )

        return {"message": "Calendar connection deleted successfully"}
    except Exception as e:
        logger.error(
            "Failed to delete calendar connection",
            error=str(e),
            connection_id=connection_id,
            user_id=current_user.id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete calendar connection",
        ) from e


@router.get(API_ROUTES.CALENDAR_CONNECTIONS.AUTH_GOOGLE_URL)
async def get_google_auth_url(
    current_user: User = Depends(get_current_user),
):
    """Get Google Calendar OAuth authorization URL"""
    try:
        auth_url = await calendar_service.get_google_auth_url(current_user.id)
        return {"auth_url": auth_url}
    except Exception as e:
        logger.error(
            "Failed to generate Google auth URL", error=str(e), user_id=current_user.id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate authorization URL",
        ) from e


@router.post(
    API_ROUTES.CALENDAR_CONNECTIONS.AUTH_GOOGLE_CALLBACK,
    response_model=CalendarConnectionResponse,
)
async def google_auth_callback(
    auth_data: GoogleCalendarAuth,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Handle Google Calendar OAuth callback"""
    try:
        connection = await calendar_service.create_google_connection(
            auth_data.code, current_user.id, db
        )

        logger.info(
            "Google calendar connection created",
            connection_id=connection.id,
            user_id=current_user.id,
        )

        return CalendarConnectionResponse(
            message="Google Calendar connected successfully",
            connection=CalendarConnectionPublic.from_orm(connection),
        )
    except Exception as e:
        logger.error(
            "Failed to create Google calendar connection",
            error=str(e),
            user_id=current_user.id,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to connect Google Calendar",
        ) from e


@router.get(API_ROUTES.CALENDAR_CONNECTIONS.AUTH_OUTLOOK_URL)
async def get_outlook_auth_url(
    current_user: User = Depends(get_current_user),
):
    """Get Outlook Calendar OAuth authorization URL"""
    try:
        auth_url = await calendar_service.get_outlook_auth_url(current_user.id)
        return {"auth_url": auth_url}
    except Exception as e:
        logger.error(
            "Failed to generate Outlook auth URL", error=str(e), user_id=current_user.id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate authorization URL",
        ) from e


@router.post(
    API_ROUTES.CALENDAR_CONNECTIONS.AUTH_OUTLOOK_CALLBACK,
    response_model=CalendarConnectionResponse,
)
async def outlook_auth_callback(
    auth_data: OutlookCalendarAuth,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Handle Outlook Calendar OAuth callback"""
    try:
        connection = await calendar_service.create_outlook_connection(
            auth_data.code, current_user.id, db
        )

        logger.info(
            "Outlook calendar connection created",
            connection_id=connection.id,
            user_id=current_user.id,
        )

        return CalendarConnectionResponse(
            message="Outlook Calendar connected successfully",
            connection=CalendarConnectionPublic.from_orm(connection),
        )
    except Exception as e:
        logger.error(
            "Failed to create Outlook calendar connection",
            error=str(e),
            user_id=current_user.id,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to connect Outlook Calendar",
        ) from e


@router.post(API_ROUTES.CALENDAR_CONNECTIONS.SYNC)
async def sync_calendar_connection(
    connection_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Manually trigger calendar sync"""
    try:
        connection = await calendar_connection.get_by_user_and_id(
            db, current_user.id, connection_id
        )

        if not connection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Calendar connection not found",
            )

        if not connection.is_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Calendar connection is disabled",
            )

        # Trigger sync
        sync_result = await calendar_service.sync_calendar(connection, db)

        logger.info(
            "Calendar sync triggered",
            connection_id=connection_id,
            user_id=current_user.id,
        )

        return {"message": "Calendar sync initiated", "result": sync_result}
    except Exception as e:
        logger.error(
            "Failed to sync calendar",
            error=str(e),
            connection_id=connection_id,
            user_id=current_user.id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to sync calendar",
        ) from e
