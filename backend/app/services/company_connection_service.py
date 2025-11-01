"""Service for company-based connections."""

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.company import Company
from app.models.company_connection import CompanyConnection
from app.models.user import User
from app.utils.datetime_utils import get_utc_now


class CompanyConnectionService:
    """Service for managing company-based connections."""

    async def can_users_interact(
        self, db: AsyncSession, user1_id: int, user2_id: int
    ) -> bool:
        """
        Check if two users can interact based on company connections.

        Users can interact if:
        0. Both users are in the same company (automatically allowed)
        1. User1's company is connected to User2's company
        2. User1 is directly connected to User2's company
        3. User2 is directly connected to User1's company

        Args:
            db: Database session
            user1_id: First user ID
            user2_id: Second user ID

        Returns:
            True if users can interact, False otherwise
        """
        # Get both users with their companies
        result = await db.execute(
            select(User)
            .where(User.id.in_([user1_id, user2_id]))
            .options(selectinload(User.company))
        )
        users = result.scalars().all()

        if len(users) != 2:
            return False

        user1 = next((u for u in users if u.id == user1_id), None)
        user2 = next((u for u in users if u.id == user2_id), None)

        if not user1 or not user2:
            return False

        # Scenario 0: Both users in same company - automatically allowed
        if (
            user1.company_id
            and user2.company_id
            and user1.company_id == user2.company_id
        ):
            return True

        # Check various connection scenarios
        conditions = []

        # Scenario 1: User1's company → User2's company (company-to-company)
        if user1.company_id and user2.company_id:
            conditions.append(
                and_(
                    CompanyConnection.source_type == "company",
                    CompanyConnection.source_company_id == user1.company_id,
                    CompanyConnection.target_company_id == user2.company_id,
                    CompanyConnection.is_active,
                    CompanyConnection.can_message,
                )
            )
            # Reverse direction
            conditions.append(
                and_(
                    CompanyConnection.source_type == "company",
                    CompanyConnection.source_company_id == user2.company_id,
                    CompanyConnection.target_company_id == user1.company_id,
                    CompanyConnection.is_active,
                    CompanyConnection.can_message,
                )
            )

        # Scenario 2: User1 → User2's company (user-to-company)
        if user2.company_id:
            conditions.append(
                and_(
                    CompanyConnection.source_type == "user",
                    CompanyConnection.source_user_id == user1_id,
                    CompanyConnection.target_company_id == user2.company_id,
                    CompanyConnection.is_active,
                    CompanyConnection.can_message,
                )
            )

        # Scenario 3: User2 → User1's company (user-to-company)
        if user1.company_id:
            conditions.append(
                and_(
                    CompanyConnection.source_type == "user",
                    CompanyConnection.source_user_id == user2_id,
                    CompanyConnection.target_company_id == user1.company_id,
                    CompanyConnection.is_active,
                    CompanyConnection.can_message,
                )
            )

        if not conditions:
            return False

        # Check if any connection exists
        result = await db.execute(
            select(CompanyConnection).where(or_(*conditions)).limit(1)
        )
        connection = result.scalar_one_or_none()

        return connection is not None

    async def connect_user_to_company(
        self,
        db: AsyncSession,
        user_id: int,
        company_id: int,
        created_by_id: int,
        connection_type: str = "standard",
        can_message: bool = True,
        can_view_profile: bool = True,
        can_assign_tasks: bool = False,
    ) -> CompanyConnection:
        """
        Create a user-to-company connection.

        Args:
            db: Database session
            user_id: User ID
            company_id: Target company ID
            created_by_id: ID of user creating this connection
            connection_type: Type of connection
            can_message: Whether messaging is allowed
            can_view_profile: Whether profile viewing is allowed
            can_assign_tasks: Whether task assignment is allowed

        Returns:
            Created CompanyConnection

        Raises:
            ValueError: If connection already exists or invalid parameters
        """
        # Check if connection already exists
        result = await db.execute(
            select(CompanyConnection).where(
                and_(
                    CompanyConnection.source_type == "user",
                    CompanyConnection.source_user_id == user_id,
                    CompanyConnection.target_company_id == company_id,
                )
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            raise ValueError(
                f"Connection already exists between user {user_id} and company {company_id}"
            )

        # Verify user and company exist
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if not user:
            raise ValueError(f"User {user_id} not found")

        company_result = await db.execute(
            select(Company).where(Company.id == company_id)
        )
        company = company_result.scalar_one_or_none()
        if not company:
            raise ValueError(f"Company {company_id} not found")

        # Create connection
        connection = CompanyConnection(
            source_type="user",
            source_user_id=user_id,
            source_company_id=None,
            target_company_id=company_id,
            is_active=True,
            connection_type=connection_type,
            can_message=can_message,
            can_view_profile=can_view_profile,
            can_assign_tasks=can_assign_tasks,
            creation_type="manual",
            created_by=created_by_id,
            created_at=get_utc_now(),
        )

        db.add(connection)
        await db.commit()
        await db.refresh(connection)

        return connection

    async def connect_companies(
        self,
        db: AsyncSession,
        source_company_id: int,
        target_company_id: int,
        created_by_id: int,
        connection_type: str = "standard",
        can_message: bool = True,
        can_view_profile: bool = True,
        can_assign_tasks: bool = False,
    ) -> CompanyConnection:
        """
        Create a company-to-company connection.

        Args:
            db: Database session
            source_company_id: Source company ID
            target_company_id: Target company ID
            created_by_id: ID of user creating this connection
            connection_type: Type of connection
            can_message: Whether messaging is allowed
            can_view_profile: Whether profile viewing is allowed
            can_assign_tasks: Whether task assignment is allowed

        Returns:
            Created CompanyConnection

        Raises:
            ValueError: If connection already exists or invalid parameters
        """
        if source_company_id == target_company_id:
            raise ValueError("Cannot connect a company to itself")

        # Check if connection already exists in either direction
        result = await db.execute(
            select(CompanyConnection).where(
                and_(
                    CompanyConnection.source_type == "company",
                    or_(
                        and_(
                            CompanyConnection.source_company_id == source_company_id,
                            CompanyConnection.target_company_id == target_company_id,
                        ),
                        and_(
                            CompanyConnection.source_company_id == target_company_id,
                            CompanyConnection.target_company_id == source_company_id,
                        ),
                    ),
                )
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            raise ValueError(
                f"Connection already exists between companies {source_company_id} and {target_company_id}"
            )

        # Verify both companies exist
        companies_result = await db.execute(
            select(Company).where(
                Company.id.in_([source_company_id, target_company_id])
            )
        )
        companies = companies_result.scalars().all()
        if len(companies) != 2:
            raise ValueError("One or both companies not found")

        # Create connection
        connection = CompanyConnection(
            source_type="company",
            source_user_id=None,
            source_company_id=source_company_id,
            target_company_id=target_company_id,
            is_active=True,
            connection_type=connection_type,
            can_message=can_message,
            can_view_profile=can_view_profile,
            can_assign_tasks=can_assign_tasks,
            creation_type="manual",
            created_by=created_by_id,
            created_at=get_utc_now(),
        )

        db.add(connection)
        await db.commit()
        await db.refresh(connection)

        return connection

    async def get_connected_users(self, db: AsyncSession, user_id: int) -> list[User]:
        """
        Get all users that the specified user can interact with.

        This includes:
        0. Users from the same company (colleagues)
        1. Users from companies connected to the user's company
        2. Users from companies the user is directly connected to
        3. Users whose company is connected to the user's company

        Args:
            db: Database session
            user_id: User ID

        Returns:
            List of users that can be interacted with
        """
        # Get the user with their company
        result = await db.execute(
            select(User).where(User.id == user_id).options(selectinload(User.company))
        )
        user = result.scalar_one_or_none()

        if not user:
            return []

        connected_company_ids = set()

        # Include user's own company (colleagues can interact)
        if user.company_id:
            connected_company_ids.add(user.company_id)

        # Scenario 1: Get companies connected via user's company (company-to-company)
        if user.company_id:
            # Companies that user's company connects to
            result = await db.execute(
                select(CompanyConnection.target_company_id).where(
                    and_(
                        CompanyConnection.source_type == "company",
                        CompanyConnection.source_company_id == user.company_id,
                        CompanyConnection.is_active,
                        CompanyConnection.can_message,
                    )
                )
            )
            connected_company_ids.update(result.scalars().all())

            # Companies that connect to user's company
            result = await db.execute(
                select(CompanyConnection.source_company_id).where(
                    and_(
                        CompanyConnection.source_type == "company",
                        CompanyConnection.target_company_id == user.company_id,
                        CompanyConnection.is_active,
                        CompanyConnection.can_message,
                    )
                )
            )
            connected_company_ids.update(result.scalars().all())

        # Scenario 2: Get companies user is directly connected to (user-to-company)
        result = await db.execute(
            select(CompanyConnection.target_company_id).where(
                and_(
                    CompanyConnection.source_type == "user",
                    CompanyConnection.source_user_id == user_id,
                    CompanyConnection.is_active,
                    CompanyConnection.can_message,
                )
            )
        )
        connected_company_ids.update(result.scalars().all())

        # Scenario 3: Get users who are directly connected to user's company
        if user.company_id:
            result = await db.execute(
                select(CompanyConnection.source_user_id).where(
                    and_(
                        CompanyConnection.source_type == "user",
                        CompanyConnection.target_company_id == user.company_id,
                        CompanyConnection.is_active,
                        CompanyConnection.can_message,
                        CompanyConnection.source_user_id.isnot(None),
                    )
                )
            )
            connected_user_ids = set(result.scalars().all())
        else:
            connected_user_ids = set()

        if not connected_company_ids and not connected_user_ids:
            return []

        # Get all users from connected companies + directly connected users
        conditions = []
        if connected_company_ids:
            conditions.append(User.company_id.in_(connected_company_ids))
        if connected_user_ids:
            conditions.append(User.id.in_(connected_user_ids))

        result = await db.execute(
            select(User)
            .where(
                and_(
                    or_(*conditions),
                    User.id != user_id,  # Exclude self
                    User.is_active,
                    ~User.is_deleted,
                )
            )
            .options(selectinload(User.company))
        )

        return list(result.scalars().all())

    async def check_connection(
        self,
        db: AsyncSession,
        source_type: str,
        source_id: int,
        target_company_id: int,
    ) -> CompanyConnection | None:
        """
        Check if a specific connection exists.

        Args:
            db: Database session
            source_type: Type of source ("user" or "company")
            source_id: Source user ID or company ID
            target_company_id: Target company ID

        Returns:
            CompanyConnection if exists, None otherwise
        """
        if source_type == "user":
            result = await db.execute(
                select(CompanyConnection).where(
                    and_(
                        CompanyConnection.source_type == "user",
                        CompanyConnection.source_user_id == source_id,
                        CompanyConnection.target_company_id == target_company_id,
                        CompanyConnection.is_active,
                    )
                )
            )
        elif source_type == "company":
            result = await db.execute(
                select(CompanyConnection).where(
                    and_(
                        CompanyConnection.source_type == "company",
                        CompanyConnection.source_company_id == source_id,
                        CompanyConnection.target_company_id == target_company_id,
                        CompanyConnection.is_active,
                    )
                )
            )
        else:
            return None

        return result.scalar_one_or_none()

    async def deactivate_connection(
        self, db: AsyncSession, connection_id: int
    ) -> CompanyConnection | None:
        """
        Deactivate a connection.

        Args:
            db: Database session
            connection_id: Connection ID to deactivate

        Returns:
            Updated CompanyConnection or None if not found
        """
        result = await db.execute(
            select(CompanyConnection).where(CompanyConnection.id == connection_id)
        )
        connection = result.scalar_one_or_none()

        if not connection:
            return None

        connection.is_active = False
        connection.updated_at = get_utc_now()

        await db.commit()
        await db.refresh(connection)

        return connection

    async def activate_connection(
        self, db: AsyncSession, connection_id: int
    ) -> CompanyConnection | None:
        """
        Activate a connection.

        Args:
            db: Database session
            connection_id: Connection ID to activate

        Returns:
            Updated CompanyConnection or None if not found
        """
        result = await db.execute(
            select(CompanyConnection).where(CompanyConnection.id == connection_id)
        )
        connection = result.scalar_one_or_none()

        if not connection:
            return None

        connection.is_active = True
        connection.updated_at = get_utc_now()

        await db.commit()
        await db.refresh(connection)

        return connection


# Singleton instance
company_connection_service = CompanyConnectionService()
