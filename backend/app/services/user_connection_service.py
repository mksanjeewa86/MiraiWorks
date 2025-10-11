"""Simple user connection service."""


from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.user_connection import UserConnection


class UserConnectionService:
    """Simple service for managing user connections."""

    async def connect_users(
        self,
        db: AsyncSession,
        user_id: int,
        connected_user_id: int,
        creation_type: str = "manual",
        created_by: int | None = None,
    ) -> UserConnection:
        """Create a connection between two users.

        Args:
            db: Database session
            user_id: ID of the first user
            connected_user_id: ID of the second user
            creation_type: Type of creation ('automatic' or 'manual')
            created_by: ID of the user who created this connection (None for automatic)
        """

        # Check if connection already exists
        existing = await self._get_connection(db, user_id, connected_user_id)
        if existing:
            # Reactivate if exists but inactive
            if not existing.is_active:
                existing.is_active = True
                await db.commit()
            return existing

        # Create new connection
        connection = UserConnection(
            user_id=user_id,
            connected_user_id=connected_user_id,
            is_active=True,
            creation_type=creation_type,
            created_by=created_by,
        )

        db.add(connection)
        await db.commit()
        await db.refresh(connection)
        return connection

    async def get_connected_users(self, db: AsyncSession, user_id: int) -> list[User]:
        """Get all users connected to this user."""
        from sqlalchemy.orm import selectinload
        from app.models.role import UserRole

        # Get all active connections where user is involved
        query = select(UserConnection).where(
            and_(
                or_(
                    UserConnection.user_id == user_id,
                    UserConnection.connected_user_id == user_id,
                ),
                UserConnection.is_active == True,
            )
        )

        result = await db.execute(query)
        connections = result.scalars().all()

        # Extract connected user IDs
        connected_user_ids = []
        for conn in connections:
            if conn.user_id == user_id:
                connected_user_ids.append(conn.connected_user_id)
            else:
                connected_user_ids.append(conn.user_id)

        if not connected_user_ids:
            return []

        # Get user objects with company and roles relationships
        # IMPORTANT: Load nested relationships to avoid lazy loading errors
        users_query = (
            select(User)
            .options(
                selectinload(User.company),
                selectinload(User.user_roles).selectinload(UserRole.role)
            )
            .where(
                and_(
                    User.id.in_(connected_user_ids),
                    User.is_active == True,
                    User.is_deleted == False,
                )
            )
        )

        result = await db.execute(users_query)
        return list(result.scalars().all())

    async def disconnect_users(
        self, db: AsyncSession, user_id: int, connected_user_id: int
    ) -> bool:
        """Disconnect two users."""

        connection = await self._get_connection(db, user_id, connected_user_id)
        if connection:
            connection.is_active = False
            await db.commit()
            return True
        return False

    async def _get_connection(
        self, db: AsyncSession, user_id: int, connected_user_id: int
    ) -> UserConnection:
        """Get connection between two users (either direction)."""

        query = select(UserConnection).where(
            or_(
                and_(
                    UserConnection.user_id == user_id,
                    UserConnection.connected_user_id == connected_user_id,
                ),
                and_(
                    UserConnection.user_id == connected_user_id,
                    UserConnection.connected_user_id == user_id,
                ),
            )
        )

        result = await db.execute(query)
        return result.scalars().first()


# Singleton instance
user_connection_service = UserConnectionService()
