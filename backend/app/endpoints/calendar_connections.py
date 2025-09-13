from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import structlog

from app.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.models.calendar_connection import CalendarConnection
from app.schemas.calendar_connection import (
    CalendarConnectionCreate,
    CalendarConnectionUpdate,
    CalendarConnectionPublic,
    CalendarListResponse,
    CalendarConnectionResponse,
    GoogleCalendarAuth,
    OutlookCalendarAuth,
)
from app.services.calendar_service import CalendarService

logger = structlog.get_logger()

router = APIRouter()
calendar_service = CalendarService()


@router.get("/calendar-connections", response_model=CalendarListResponse)
async def get_calendar_connections(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all calendar connections for the current user"""
    try:
        connections = (
            db.query(CalendarConnection)
            .filter(CalendarConnection.user_id == current_user.id)
            .all()
        )
        
        return CalendarListResponse(
            connections=[CalendarConnectionPublic.from_orm(conn) for conn in connections]
        )
    except Exception as e:
        logger.error("Failed to get calendar connections", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve calendar connections",
        )


@router.get("/calendar-connections/{connection_id}", response_model=CalendarConnectionPublic)
async def get_calendar_connection(
    connection_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific calendar connection"""
    connection = (
        db.query(CalendarConnection)
        .filter(
            CalendarConnection.id == connection_id,
            CalendarConnection.user_id == current_user.id,
        )
        .first()
    )
    
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar connection not found",
        )
    
    return CalendarConnectionPublic.from_orm(connection)


@router.put("/calendar-connections/{connection_id}", response_model=CalendarConnectionResponse)
async def update_calendar_connection(
    connection_id: int,
    connection_update: CalendarConnectionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update calendar connection settings"""
    try:
        connection = (
            db.query(CalendarConnection)
            .filter(
                CalendarConnection.id == connection_id,
                CalendarConnection.user_id == current_user.id,
            )
            .first()
        )
        
        if not connection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Calendar connection not found",
            )
        
        # Update connection with provided fields
        update_data = connection_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(connection, field, value)
        
        db.commit()
        db.refresh(connection)
        
        logger.info("Calendar connection updated", connection_id=connection_id, user_id=current_user.id)
        
        return CalendarConnectionResponse(
            message="Calendar connection updated successfully",
            connection=CalendarConnectionPublic.from_orm(connection)
        )
    except Exception as e:
        db.rollback()
        logger.error("Failed to update calendar connection", error=str(e), connection_id=connection_id, user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update calendar connection",
        )


@router.delete("/calendar-connections/{connection_id}")
async def delete_calendar_connection(
    connection_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a calendar connection"""
    try:
        connection = (
            db.query(CalendarConnection)
            .filter(
                CalendarConnection.id == connection_id,
                CalendarConnection.user_id == current_user.id,
            )
            .first()
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
            logger.warning("Failed to revoke tokens during deletion", error=str(e), connection_id=connection_id)
        
        db.delete(connection)
        db.commit()
        
        logger.info("Calendar connection deleted", connection_id=connection_id, user_id=current_user.id)
        
        return {"message": "Calendar connection deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.error("Failed to delete calendar connection", error=str(e), connection_id=connection_id, user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete calendar connection",
        )


@router.get("/calendar-connections/auth/google/url")
async def get_google_auth_url(
    current_user: User = Depends(get_current_user),
):
    """Get Google Calendar OAuth authorization URL"""
    try:
        auth_url = await calendar_service.get_google_auth_url(current_user.id)
        return {"auth_url": auth_url}
    except Exception as e:
        logger.error("Failed to generate Google auth URL", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate authorization URL",
        )


@router.post("/calendar-connections/auth/google/callback", response_model=CalendarConnectionResponse)
async def google_auth_callback(
    auth_data: GoogleCalendarAuth,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Handle Google Calendar OAuth callback"""
    try:
        connection = await calendar_service.create_google_connection(
            auth_data.code, current_user.id, db
        )
        
        logger.info("Google calendar connection created", connection_id=connection.id, user_id=current_user.id)
        
        return CalendarConnectionResponse(
            message="Google Calendar connected successfully",
            connection=CalendarConnectionPublic.from_orm(connection)
        )
    except Exception as e:
        logger.error("Failed to create Google calendar connection", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to connect Google Calendar",
        )


@router.get("/calendar-connections/auth/outlook/url")
async def get_outlook_auth_url(
    current_user: User = Depends(get_current_user),
):
    """Get Outlook Calendar OAuth authorization URL"""
    try:
        auth_url = await calendar_service.get_outlook_auth_url(current_user.id)
        return {"auth_url": auth_url}
    except Exception as e:
        logger.error("Failed to generate Outlook auth URL", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate authorization URL",
        )


@router.post("/calendar-connections/auth/outlook/callback", response_model=CalendarConnectionResponse)
async def outlook_auth_callback(
    auth_data: OutlookCalendarAuth,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Handle Outlook Calendar OAuth callback"""
    try:
        connection = await calendar_service.create_outlook_connection(
            auth_data.code, current_user.id, db
        )
        
        logger.info("Outlook calendar connection created", connection_id=connection.id, user_id=current_user.id)
        
        return CalendarConnectionResponse(
            message="Outlook Calendar connected successfully",
            connection=CalendarConnectionPublic.from_orm(connection)
        )
    except Exception as e:
        logger.error("Failed to create Outlook calendar connection", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to connect Outlook Calendar",
        )


@router.post("/calendar-connections/{connection_id}/sync")
async def sync_calendar_connection(
    connection_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Manually trigger calendar sync"""
    try:
        connection = (
            db.query(CalendarConnection)
            .filter(
                CalendarConnection.id == connection_id,
                CalendarConnection.user_id == current_user.id,
            )
            .first()
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
        
        logger.info("Calendar sync triggered", connection_id=connection_id, user_id=current_user.id)
        
        return {"message": "Calendar sync initiated", "result": sync_result}
    except Exception as e:
        logger.error("Failed to sync calendar", error=str(e), connection_id=connection_id, user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to sync calendar",
        )