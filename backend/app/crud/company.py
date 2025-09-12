from typing import List, Optional
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Company
from app.utils.constants import CompanyType


async def get_companies(
    db: AsyncSession,
    page: int = 1,
    size: int = 20,
    search: Optional[str] = None,
    company_type: Optional[CompanyType] = None,
    is_active: Optional[bool] = None,
):
    """Get companies with filtering, pagination and search."""
    offset = (page - 1) * size
    
    # Build query conditions
    conditions = []
    if search:
        search_term = f"%{search}%"
        conditions.append(
            or_(
                Company.name.ilike(search_term),
                Company.email.ilike(search_term),
            )
        )
    if company_type:
        conditions.append(Company.type == company_type)
    if is_active is not None:
        conditions.append(Company.is_active == is_active)
    
    # Build query
    query = select(Company)
    if conditions:
        query = query.where(*conditions)
    
    # Get total count
    count_query = select(func.count(Company.id))
    if conditions:
        count_query = count_query.where(*conditions)
    
    total = (await db.execute(count_query)).scalar()
    
    # Get paginated results
    query = query.offset(offset).limit(size).order_by(Company.created_at.desc())
    result = await db.execute(query)
    companies = result.scalars().all()
    
    return companies, total


async def get_company_by_id(db: AsyncSession, company_id: int) -> Optional[Company]:
    """Get company by ID."""
    result = await db.execute(select(Company).where(Company.id == company_id))
    return result.scalar_one_or_none()


async def create_company(db: AsyncSession, company_data: dict) -> Company:
    """Create a new company."""
    company = Company(**company_data)
    db.add(company)
    await db.commit()
    await db.refresh(company)
    return company


async def update_company(db: AsyncSession, company: Company, update_data: dict) -> Company:
    """Update company information."""
    for field, value in update_data.items():
        if value is not None:
            setattr(company, field, value)
    
    await db.commit()
    await db.refresh(company)
    return company


async def delete_company(db: AsyncSession, company: Company) -> bool:
    """Delete company (soft delete by setting is_active to False)."""
    company.is_active = False
    await db.commit()
    return True


async def get_company_by_email(db: AsyncSession, email: str) -> Optional[Company]:
    """Get company by email."""
    result = await db.execute(select(Company).where(Company.email == email))
    return result.scalar_one_or_none()