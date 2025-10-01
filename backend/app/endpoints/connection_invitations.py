"""Connection invitation API endpoints."""


from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.connection_invitation import InvitationStatus
from app.models.user import User
from app.services.connection_invitation_service import connection_invitation_service

router = APIRouter()


class InvitationCreate(BaseModel):
    """Schema for creating invitations."""
    message: str | None = None


class InvitationResponse(BaseModel):
    """Schema for invitation response."""
    accept: bool


@router.post("/send/{user_id}")
async def send_invitation(
    user_id: int,
    invitation_data: InvitationCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Send a connection invitation to another user."""

    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot send invitation to yourself"
        )

    try:
        invitation = await connection_invitation_service.send_invitation(
            db=db,
            sender_id=current_user.id,
            receiver_id=user_id,
            message=invitation_data.message
        )

        return {
            "message": "Invitation sent successfully",
            "invitation_id": invitation.id,
            "sent_to_user_id": user_id
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/respond/{invitation_id}")
async def respond_to_invitation(
    invitation_id: int,
    response_data: InvitationResponse,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Respond to a connection invitation (accept or reject)."""

    try:
        result = await connection_invitation_service.respond_to_invitation(
            db=db,
            invitation_id=invitation_id,
            receiver_id=current_user.id,
            accept=response_data.accept
        )

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/cancel/{invitation_id}")
async def cancel_invitation(
    invitation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Cancel a sent invitation."""

    try:
        success = await connection_invitation_service.cancel_invitation(
            db=db,
            invitation_id=invitation_id,
            sender_id=current_user.id
        )

        if success:
            return {"message": "Invitation cancelled successfully"}

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/sent")
async def get_sent_invitations(
    status_filter: str | None = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get invitations sent by current user."""

    invitation_status = None
    if status_filter:
        try:
            invitation_status = InvitationStatus(status_filter)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status_filter}"
            )

    invitations = await connection_invitation_service.get_sent_invitations(
        db=db,
        sender_id=current_user.id,
        status=invitation_status
    )

    return {
        "invitations": invitations,
        "total": len(invitations)
    }


@router.get("/received")
async def get_received_invitations(
    status_filter: str | None = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get invitations received by current user."""

    invitation_status = None
    if status_filter:
        try:
            invitation_status = InvitationStatus(status_filter)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status_filter}"
            )

    invitations = await connection_invitation_service.get_received_invitations(
        db=db,
        receiver_id=current_user.id,
        status=invitation_status
    )

    return {
        "invitations": invitations,
        "total": len(invitations)
    }


@router.get("/pending")
async def get_pending_invitations(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all pending invitations for current user (sent and received)."""

    pending_invitations = await connection_invitation_service.get_pending_invitations(
        db=db,
        user_id=current_user.id
    )

    return pending_invitations
