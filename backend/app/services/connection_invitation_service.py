"""Connection invitation service for managing connection requests."""

from datetime import datetime

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.connection_invitation import ConnectionInvitation, InvitationStatus
from app.services.user_connection_service import user_connection_service


class ConnectionInvitationService:
    """Service for managing connection invitations."""

    async def send_invitation(
        self,
        db: AsyncSession,
        sender_id: int,
        receiver_id: int,
        message: str | None = None,
    ) -> ConnectionInvitation:
        """Send a connection invitation to another user."""

        if sender_id == receiver_id:
            raise ValueError("Cannot send invitation to yourself")

        # Check if invitation already exists
        existing = await self._get_pending_invitation(db, sender_id, receiver_id)
        if existing:
            raise ValueError("Invitation already sent to this user")

        # Check if users are already connected
        existing_connection = await user_connection_service._get_connection(
            db, sender_id, receiver_id
        )
        if existing_connection and existing_connection.is_active:
            raise ValueError("Users are already connected")

        # Create invitation
        invitation = ConnectionInvitation(
            sender_id=sender_id,
            receiver_id=receiver_id,
            status=InvitationStatus.PENDING,
            message=message,
            sent_at=datetime.utcnow(),
        )

        db.add(invitation)
        await db.commit()
        await db.refresh(invitation)

        # TODO: Send notification to receiver
        return invitation

    async def respond_to_invitation(
        self, db: AsyncSession, invitation_id: int, receiver_id: int, accept: bool
    ) -> dict:
        """Respond to a connection invitation (accept or reject)."""

        # Get invitation
        invitation = await self._get_invitation_by_id(db, invitation_id)
        if not invitation:
            raise ValueError("Invitation not found")

        if invitation.receiver_id != receiver_id:
            raise ValueError("You can only respond to invitations sent to you")

        if invitation.status != InvitationStatus.PENDING:
            raise ValueError("Invitation has already been responded to")

        # Update invitation status
        if accept:
            invitation.status = InvitationStatus.ACCEPTED
            # Create connection
            await user_connection_service.connect_users(
                db=db,
                user_id=invitation.sender_id,
                connected_user_id=invitation.receiver_id,
            )
            result_message = "Invitation accepted and connection created"
        else:
            invitation.status = InvitationStatus.REJECTED
            result_message = "Invitation rejected"

        invitation.responded_at = datetime.utcnow()
        await db.commit()

        # TODO: Send notification to sender
        return {
            "message": result_message,
            "invitation_id": invitation.id,
            "status": invitation.status,
        }

    async def cancel_invitation(
        self, db: AsyncSession, invitation_id: int, sender_id: int
    ) -> bool:
        """Cancel a sent invitation."""

        invitation = await self._get_invitation_by_id(db, invitation_id)
        if not invitation:
            raise ValueError("Invitation not found")

        if invitation.sender_id != sender_id:
            raise ValueError("You can only cancel invitations you sent")

        if invitation.status != InvitationStatus.PENDING:
            raise ValueError("Can only cancel pending invitations")

        invitation.status = InvitationStatus.CANCELLED
        invitation.responded_at = datetime.utcnow()
        await db.commit()

        return True

    async def get_sent_invitations(
        self, db: AsyncSession, sender_id: int, status: InvitationStatus | None = None
    ) -> list[ConnectionInvitation]:
        """Get invitations sent by user."""

        query = select(ConnectionInvitation).where(
            ConnectionInvitation.sender_id == sender_id
        )

        if status:
            query = query.where(ConnectionInvitation.status == status)

        query = query.order_by(ConnectionInvitation.sent_at.desc())

        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_received_invitations(
        self, db: AsyncSession, receiver_id: int, status: InvitationStatus | None = None
    ) -> list[ConnectionInvitation]:
        """Get invitations received by user."""

        query = select(ConnectionInvitation).where(
            ConnectionInvitation.receiver_id == receiver_id
        )

        if status:
            query = query.where(ConnectionInvitation.status == status)

        query = query.order_by(ConnectionInvitation.sent_at.desc())

        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_pending_invitations(self, db: AsyncSession, user_id: int) -> dict:
        """Get all pending invitations for user (sent and received)."""

        sent = await self.get_sent_invitations(db, user_id, InvitationStatus.PENDING)
        received = await self.get_received_invitations(
            db, user_id, InvitationStatus.PENDING
        )

        return {
            "sent": sent,
            "received": received,
            "total_sent": len(sent),
            "total_received": len(received),
        }

    # Helper methods

    async def _get_pending_invitation(
        self, db: AsyncSession, sender_id: int, receiver_id: int
    ) -> ConnectionInvitation | None:
        """Check if pending invitation exists between users."""

        query = select(ConnectionInvitation).where(
            and_(
                ConnectionInvitation.sender_id == sender_id,
                ConnectionInvitation.receiver_id == receiver_id,
                ConnectionInvitation.status == InvitationStatus.PENDING,
            )
        )

        result = await db.execute(query)
        return result.scalars().first()

    async def _get_invitation_by_id(
        self, db: AsyncSession, invitation_id: int
    ) -> ConnectionInvitation | None:
        """Get invitation by ID."""

        query = select(ConnectionInvitation).where(
            ConnectionInvitation.id == invitation_id
        )

        result = await db.execute(query)
        return result.scalars().first()


# Singleton instance
connection_invitation_service = ConnectionInvitationService()
