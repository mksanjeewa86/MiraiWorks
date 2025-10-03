from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.utils.constants import UserRole


class PermissionService:
    """Service for handling user permissions and access control."""

    async def can_schedule_interview(
        self, db: AsyncSession, user: User, candidate_id: int
    ) -> bool:
        """
        Check if a user can schedule interviews with a specific candidate.
        """
        # Super admins can schedule interviews with anyone
        if await self._is_super_admin(user):
            return True

        # Recruiters and employers can typically schedule interviews
        # You might want to add more specific business logic here
        user_roles = await self._get_user_roles(db, user)

        return any(
            role in [UserRole.MEMBER, UserRole.MEMBER, UserRole.ADMIN]
            for role in user_roles
        )

    async def can_access_video_call(
        self, db: AsyncSession, user: User, video_call
    ) -> bool:
        """
        Check if a user can access a specific video call.
        """
        # Super admins can access any video call
        if await self._is_super_admin(user):
            return True

        # Participants can access their own video calls
        return (
            video_call.interviewer_id == user.id or
            video_call.candidate_id == user.id
        )

    async def can_end_video_call(
        self, db: AsyncSession, user: User, video_call
    ) -> bool:
        """
        Check if a user can end a video call.
        """
        # Super admins can end any video call
        if await self._is_super_admin(user):
            return True

        # Only the interviewer can end the call
        return video_call.interviewer_id == user.id

    async def _is_super_admin(self, user: User) -> bool:
        """Check if user is a super admin."""
        # TODO: Implement actual role checking logic
        # This should check the user's roles in the database
        return False  # Placeholder

    async def _get_user_roles(self, db: AsyncSession, user: User) -> list[UserRole]:
        """Get all roles for a user."""
        # TODO: Implement actual role fetching from database
        # This should query the user_roles table
        return [UserRole.MEMBER]  # Placeholder


permission_service = PermissionService()
