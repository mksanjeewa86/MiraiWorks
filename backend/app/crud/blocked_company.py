"""
CRUD operations for Blocked Companies
"""

from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.models import BlockedCompany, Company


async def get_user_blocked_companies(
    db: AsyncSession, user_id: int
) -> List[BlockedCompany]:
    """Get all blocked companies for a user."""
    result = await db.execute(
        select(BlockedCompany)
        .where(BlockedCompany.user_id == user_id)
        .order_by(BlockedCompany.created_at.desc())
    )
    return list(result.scalars().all())


async def get_blocked_company_by_id(
    db: AsyncSession, blocked_company_id: int, user_id: int
) -> Optional[BlockedCompany]:
    """Get a specific blocked company by ID (must belong to user)."""
    result = await db.execute(
        select(BlockedCompany).where(
            and_(
                BlockedCompany.id == blocked_company_id,
                BlockedCompany.user_id == user_id,
            )
        )
    )
    return result.scalar_one_or_none()


async def check_if_company_blocked(
    db: AsyncSession, user_id: int, company_id: Optional[int] = None, company_name: Optional[str] = None
) -> bool:
    """
    Check if a company is blocked by the user.
    Can check by company_id or company_name.
    """
    conditions = [BlockedCompany.user_id == user_id]

    if company_id is not None:
        conditions.append(BlockedCompany.company_id == company_id)
    elif company_name is not None:
        conditions.append(BlockedCompany.company_name == company_name)
    else:
        return False

    result = await db.execute(
        select(BlockedCompany).where(and_(*conditions))
    )
    return result.scalar_one_or_none() is not None


async def create_blocked_company(
    db: AsyncSession,
    user_id: int,
    company_id: Optional[int] = None,
    company_name: Optional[str] = None,
    reason: Optional[str] = None,
) -> BlockedCompany:
    """
    Create a new blocked company entry.
    Either company_id or company_name must be provided.
    """
    blocked_company = BlockedCompany(
        user_id=user_id,
        company_id=company_id,
        company_name=company_name,
        reason=reason,
    )
    db.add(blocked_company)
    await db.commit()
    await db.refresh(blocked_company)
    return blocked_company


async def delete_blocked_company(
    db: AsyncSession, blocked_company_id: int, user_id: int
) -> bool:
    """
    Delete a blocked company entry.
    Returns True if deleted, False if not found.
    """
    blocked_company = await get_blocked_company_by_id(db, blocked_company_id, user_id)
    if not blocked_company:
        return False

    await db.delete(blocked_company)
    await db.commit()
    return True


async def search_companies_for_blocking(
    db: AsyncSession, search_query: str, limit: int = 10
) -> List[Company]:
    """
    Search for companies by name for the blocking interface.
    Returns companies that match the search query.
    """
    result = await db.execute(
        select(Company)
        .where(Company.name.ilike(f"%{search_query}%"))
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_blocked_company_ids_for_user(
    db: AsyncSession, user_id: int
) -> List[int]:
    """
    Get list of blocked company IDs for a user.
    This is useful for filtering search results.
    Returns only company_ids (not company_names).
    """
    result = await db.execute(
        select(BlockedCompany.company_id)
        .where(
            and_(
                BlockedCompany.user_id == user_id,
                BlockedCompany.company_id.isnot(None),
            )
        )
    )
    return [row[0] for row in result.all() if row[0] is not None]


async def get_users_who_blocked_company(
    db: AsyncSession, company_id: int
) -> List[int]:
    """
    Get list of user IDs who have blocked a specific company.
    This is useful for excluding candidates from search results.
    """
    result = await db.execute(
        select(BlockedCompany.user_id)
        .where(BlockedCompany.company_id == company_id)
    )
    return [row[0] for row in result.all()]
