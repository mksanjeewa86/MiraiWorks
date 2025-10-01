
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import Company, User
from app.schemas.company import CompanyCreate, CompanyUpdate
from app.utils.constants import CompanyType


class CRUDCompany(CRUDBase[Company, CompanyCreate, CompanyUpdate]):
    """Company CRUD operations."""

    async def get_with_counts(self, db: AsyncSession, company_id: int):
        """Get company with user and position counts."""
        query = (
            select(
                Company,
                func.count(User.id).label("user_count"),
                func.coalesce(func.count(Company.positions), 0).label("position_count"),
            )
            .outerjoin(User, Company.id == User.company_id)
            .outerjoin(Company.positions)
            .where(Company.id == company_id)
            .group_by(Company.id)
        )
        result = await db.execute(query)
        return result.first()

    async def get_by_email(self, db: AsyncSession, email: str) -> Company | None:
        """Get company by email."""
        result = await db.execute(select(Company).where(Company.email == email))
        return result.scalar_one_or_none()

    async def get_admin_count(self, db: AsyncSession, company_id: int) -> int:
        """Get count of admin users for a company."""
        admin_query = select(func.count(User.id)).where(
            and_(
                User.company_id == company_id,
                User.is_admin is True,
                User.is_deleted is False,
            )
        )
        result = await db.execute(admin_query)
        return result.scalar() or 0


async def get_companies(
    db: AsyncSession,
    page: int = 1,
    size: int = 20,
    search: str | None = None,
    company_type: CompanyType | None = None,
    is_active: bool | None = None,
    is_demo: bool | None = None,
    include_deleted: bool = False,
):
    """Get companies with filtering, pagination and search."""
    offset = (page - 1) * size

    # Build query conditions
    conditions = []

    # Handle logical deletion
    if not include_deleted:
        conditions.append(Company.is_deleted is False)

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
        # Convert boolean to string since is_active is stored as String(1) in database
        active_value = "1" if is_active else "0"
        conditions.append(Company.is_active == active_value)
    if is_demo is not None:
        conditions.append(Company.is_demo == is_demo)

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


async def get_company_by_id(db: AsyncSession, company_id: int) -> Company | None:
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


async def update_company(
    db: AsyncSession, company: Company, update_data: dict
) -> Company:
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


async def get_company_by_email(db: AsyncSession, email: str) -> Company | None:
    """Get company by email."""
    result = await db.execute(select(Company).where(Company.email == email))
    return result.scalar_one_or_none()


# Create the CRUD instance
company = CRUDCompany(Company)
