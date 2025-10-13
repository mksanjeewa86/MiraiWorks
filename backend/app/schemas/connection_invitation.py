"""Connection invitation schemas and enums."""

from enum import Enum


class InvitationStatus(str, Enum):
    """Status of connection invitations."""

    PENDING = "pending"  # Invitation sent, awaiting response
    ACCEPTED = "accepted"  # Invitation accepted (should create connection)
    REJECTED = "rejected"  # Invitation declined
    CANCELLED = "cancelled"  # Sender cancelled the invitation
