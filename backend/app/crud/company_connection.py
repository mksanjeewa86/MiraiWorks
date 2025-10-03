"""CRUD operations for company connections."""

from typing import List
from sqlalchemy import and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.company_connection import CompanyConnection
from app.schemas.company_connection import (
    CompanyConnectionCreate, 
    CompanyConnectionUpdate,
    ConnectionStatus
)


class CRUDCompanyConnection(CRUDBase[CompanyConnection, CompanyConnectionCreate, CompanyConnectionUpdate]):
    """CRUD operations for company connections."""

    async def get_by_companies(
        self, 
        db: AsyncSession, 
        requesting_company_id: int, 
        target_company_id: int
    ) -> CompanyConnection | None:
        """Get a connection by requesting and target company IDs."""
        result = await db.execute(
            select(CompanyConnection).where(
                and_(
                    CompanyConnection.requesting_company_id == requesting_company_id,
                    CompanyConnection.target_company_id == target_company_id
                )
            )
        )
        return result.scalars().first()

    async def get_connection_between_companies(
        self, 
        db: AsyncSession, 
        company_id_1: int, 
        company_id_2: int
    ) -> CompanyConnection | None:
        """Get any connection between two companies (bidirectional)."""
        result = await db.execute(
            select(CompanyConnection).where(
                or_(
                    and_(
                        CompanyConnection.requesting_company_id == company_id_1,
                        CompanyConnection.target_company_id == company_id_2
                    ),
                    and_(
                        CompanyConnection.requesting_company_id == company_id_2,
                        CompanyConnection.target_company_id == company_id_1
                    )
                )
            )
        )
        return result.scalars().first()

    async def get_company_connections(
        self, 
        db: AsyncSession, 
        company_id: int, 
        status: ConnectionStatus | None = None
    ) -> List[CompanyConnection]:
        """Get all connections for a company (sent and received)."""
        query = select(CompanyConnection).options(
            selectinload(CompanyConnection.requesting_company),
            selectinload(CompanyConnection.target_company),
            selectinload(CompanyConnection.requester),
            selectinload(CompanyConnection.responder)
        ).where(
            or_(
                CompanyConnection.requesting_company_id == company_id,
                CompanyConnection.target_company_id == company_id
            )
        )
        
        if status:
            query = query.where(CompanyConnection.status == status.value)
            
        result = await db.execute(query)
        return result.scalars().all()

    async def get_sent_requests(
        self, 
        db: AsyncSession, 
        company_id: int, 
        status: ConnectionStatus | None = None
    ) -> List[CompanyConnection]:
        """Get connection requests sent by a company."""
        query = select(CompanyConnection).options(
            selectinload(CompanyConnection.target_company),
            selectinload(CompanyConnection.requester)
        ).where(CompanyConnection.requesting_company_id == company_id)
        
        if status:
            query = query.where(CompanyConnection.status == status.value)
            
        result = await db.execute(query)
        return result.scalars().all()

    async def get_received_requests(
        self, 
        db: AsyncSession, 
        company_id: int, 
        status: ConnectionStatus | None = None
    ) -> List[CompanyConnection]:
        """Get connection requests received by a company."""
        query = select(CompanyConnection).options(
            selectinload(CompanyConnection.requesting_company),
            selectinload(CompanyConnection.requester)
        ).where(CompanyConnection.target_company_id == company_id)
        
        if status:
            query = query.where(CompanyConnection.status == status.value)
            
        result = await db.execute(query)
        return result.scalars().all()

    async def create_connection_request(
        self, 
        db: AsyncSession, 
        requesting_company_id: int,
        requested_by_user_id: int,
        connection_data: CompanyConnectionCreate
    ) -> CompanyConnection:
        """Create a new connection request."""
        # Check if connection already exists
        existing = await self.get_by_companies(
            db, requesting_company_id, connection_data.target_company_id
        )
        
        if existing:
            raise ValueError("Connection request already exists between these companies")
        
        # Prevent self-connection
        if requesting_company_id == connection_data.target_company_id:
            raise ValueError("Company cannot connect to itself")
        
        db_obj = CompanyConnection(
            requesting_company_id=requesting_company_id,
            target_company_id=connection_data.target_company_id,
            requested_by=requested_by_user_id,
            **connection_data.dict(exclude={"target_company_id"})
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def approve_connection(
        self, 
        db: AsyncSession, 
        connection_id: int,
        responding_user_id: int,
        response_message: str | None = None
    ) -> CompanyConnection | None:
        """Approve a connection request."""
        connection = await self.get(db, id=connection_id)
        
        if connection and connection.status == "pending":
            connection.approve(responding_user_id, response_message)
            await db.commit()
            await db.refresh(connection)
            return connection
        return None

    async def reject_connection(
        self, 
        db: AsyncSession, 
        connection_id: int,
        responding_user_id: int,
        response_message: str | None = None
    ) -> CompanyConnection | None:
        """Reject a connection request."""
        connection = await self.get(db, id=connection_id)
        
        if connection and connection.status == "pending":
            connection.reject(responding_user_id, response_message)
            await db.commit()
            await db.refresh(connection)
            return connection
        return None

    async def block_connection(
        self, 
        db: AsyncSession, 
        connection_id: int,
        responding_user_id: int,
        response_message: str | None = None
    ) -> CompanyConnection | None:
        """Block a connection request (and future requests)."""
        connection = await self.get(db, id=connection_id)
        
        if connection:
            connection.block(responding_user_id, response_message)
            await db.commit()
            await db.refresh(connection)
            return connection
        return None

    async def get_active_connections(
        self, 
        db: AsyncSession, 
        company_id: int
    ) -> List[CompanyConnection]:
        """Get all active (approved) connections for a company."""
        return await self.get_company_connections(
            db, company_id, ConnectionStatus.APPROVED
        )

    async def are_companies_connected(
        self, 
        db: AsyncSession, 
        company_id_1: int, 
        company_id_2: int
    ) -> bool:
        """Check if two companies have an active connection."""
        connection = await self.get_connection_between_companies(
            db, company_id_1, company_id_2
        )
        return connection is not None and connection.is_active

    async def can_companies_message(
        self, 
        db: AsyncSession, 
        company_id_1: int, 
        company_id_2: int
    ) -> bool:
        """Check if companies can message each other."""
        connection = await self.get_connection_between_companies(
            db, company_id_1, company_id_2
        )
        return (
            connection is not None and 
            connection.is_active and 
            connection.allow_messaging
        )

    async def get_connection_summary(
        self, 
        db: AsyncSession, 
        company_id: int
    ) -> dict:
        """Get connection statistics for a company."""
        all_connections = await self.get_company_connections(db, company_id)
        
        return {
            "total_connections": len(all_connections),
            "active_connections": len([c for c in all_connections if c.is_active]),
            "pending_requests_sent": len([
                c for c in all_connections 
                if c.requesting_company_id == company_id and c.is_pending
            ]),
            "pending_requests_received": len([
                c for c in all_connections 
                if c.target_company_id == company_id and c.is_pending
            ]),
            "rejected_requests": len([c for c in all_connections if c.status == "rejected"]),
            "blocked_connections": len([c for c in all_connections if c.status == "blocked"])
        }


company_connection = CRUDCompanyConnection(CompanyConnection)