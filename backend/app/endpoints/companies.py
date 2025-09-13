import secrets
import string
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import company as company_crud
from app.crud import user_settings as user_settings_crud
from app.database import get_db
from app.dependencies import require_super_admin
from app.models import Company, Role, User, UserRole, UserSettings
from app.services.auth_service import auth_service
from app.services.email_service import email_service
from app.utils.constants import CompanyType
from app.utils.constants import UserRole as UserRoleEnum

router = APIRouter()


class CompanyCreate(BaseModel):
    name: str
    type: CompanyType
    email: str
    phone: str
    website: Optional[str] = None
    postal_code: Optional[str] = None
    prefecture: Optional[str] = None
    city: Optional[str] = None
    description: Optional[str] = None
    is_demo: Optional[bool] = False
    demo_days: Optional[int] = 30  # Default 30 days demo period


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[CompanyType] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    postal_code: Optional[str] = None
    prefecture: Optional[str] = None
    city: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class CompanyResponse(BaseModel):
    id: int
    name: str
    type: CompanyType
    email: str
    phone: Optional[str]
    website: Optional[str]
    postal_code: Optional[str]
    prefecture: Optional[str]
    city: Optional[str]
    description: Optional[str]
    is_active: bool
    is_demo: bool
    demo_end_date: Optional[str]
    user_count: int
    job_count: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class CompanyListResponse(BaseModel):
    companies: list[CompanyResponse]
    total: int
    page: int
    size: int
    pages: int


@router.get("/companies", response_model=CompanyListResponse)
async def get_companies(
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    company_type: Optional[CompanyType] = Query(None),
    is_active: Optional[bool] = Query(None),
):
    """Get companies with filtering, pagination and search."""
    companies, total = await company_crud.get_companies(
        db=db,
        page=page,
        size=size,
        search=search,
        company_type=company_type,
        is_active=is_active,
    )

    # Convert to response format (simplified for now - can be enhanced with user/job counts later)
    company_responses = [
        CompanyResponse(
            id=company.id,
            name=company.name,
            type=company.type,
            email=company.email,
            phone=company.phone,
            website=company.website,
            postal_code=company.postal_code,
            prefecture=company.prefecture,
            city=company.city,
            description=company.description,
            is_active=company.is_active,
            is_demo=company.is_demo or False,
            demo_end_date=company.demo_end_date.isoformat()
            if company.demo_end_date
            else None,
            user_count=0,  # TODO: Add user count from CRUD
            job_count=0,  # TODO: Add job count from CRUD
            created_at=company.created_at.isoformat(),
            updated_at=company.updated_at.isoformat(),
        )
        for company in companies
    ]

    pages = (total + size - 1) // size if total > 0 else 1

    return CompanyListResponse(
        companies=company_responses,
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get("/companies/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: int,
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific company by ID."""
    # Get company with user and job counts
    query = (
        select(
            Company,
            func.count(User.id).label("user_count"),
            func.coalesce(func.count(Company.jobs), 0).label("job_count"),
        )
        .outerjoin(User, Company.id == User.company_id)
        .outerjoin(Company.jobs)
        .where(Company.id == company_id)
        .group_by(Company.id)
    )

    result = await db.execute(query)
    company_data = result.first()

    if not company_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Company not found"
        )

    company, user_count, job_count = company_data

    return CompanyResponse(
        id=company.id,
        name=company.name,
        type=company.type,
        email=company.email,
        phone=company.phone,
        website=company.website,
        postal_code=company.postal_code,
        prefecture=company.prefecture,
        city=company.city,
        description=company.description,
        is_active=company.is_active == "1",
        is_demo=company.is_demo or False,
        demo_end_date=company.demo_end_date.isoformat()
        if company.demo_end_date
        else None,
        user_count=user_count or 0,
        job_count=job_count or 0,
        created_at=company.created_at.isoformat(),
        updated_at=company.updated_at.isoformat(),
    )


@router.post("/companies", response_model=CompanyResponse)
async def create_company(
    company_data: CompanyCreate,
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    """Create a new company and associated admin user."""
    # Check if email already exists as a user
    existing_user_query = select(User).where(User.email == company_data.email)
    existing_user_result = await db.execute(existing_user_query)
    if existing_user_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    # Calculate demo end date if this is a demo account
    demo_end_date = None
    if company_data.is_demo and company_data.demo_days:
        demo_end_date = datetime.utcnow() + timedelta(days=company_data.demo_days)

    # Create company (inactive until admin activates)
    company = Company(
        name=company_data.name,
        type=company_data.type,
        email=company_data.email,
        phone=company_data.phone,
        website=company_data.website,
        postal_code=company_data.postal_code,
        prefecture=company_data.prefecture,
        city=company_data.city,
        description=company_data.description,
        is_active="0",  # Company inactive until admin activates account
        is_demo=company_data.is_demo or False,
        demo_end_date=demo_end_date,
    )

    db.add(company)
    await db.flush()  # Get company ID without committing

    # Generate a random temporary password
    def generate_password(length=12):
        characters = string.ascii_letters + string.digits + "!@#$%^&*"
        return "".join(secrets.choice(characters) for _ in range(length))

    temp_password = generate_password()

    # Create admin user for the company with default profile data
    hashed_password = auth_service.get_password_hash(temp_password)
    admin_user = User(
        email=company_data.email,
        hashed_password=hashed_password,
        first_name="Company",
        last_name="Administrator",
        phone=company_data.phone,  # Use company phone as user's default phone
        is_active=False,  # Inactive until they activate their account
        is_admin=True,  # First user is admin
        require_2fa=True,  # All admin accounts require 2FA by default
        company_id=company.id,
    )

    db.add(admin_user)
    await db.flush()  # Get user ID

    # Get company admin role
    role_query = select(Role).where(Role.name == UserRoleEnum.COMPANY_ADMIN)
    role_result = await db.execute(role_query)
    admin_role = role_result.scalar_one_or_none()

    if not admin_role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Admin role not found in system",
        )

    # Assign admin role to user
    user_role = UserRole(user_id=admin_user.id, role_id=admin_role.id)
    db.add(user_role)

    # Create default user settings
    default_settings = UserSettings(
        user_id=admin_user.id,
        # Profile settings with defaults
        job_title="Company Administrator",
        bio=f"Administrator of {company_data.name}",
        # Notification preferences (already have defaults in model)
        email_notifications=True,
        push_notifications=True,
        sms_notifications=False,
        interview_reminders=True,
        application_updates=True,
        message_notifications=True,
        # UI preferences (already have defaults in model)
        language="en",
        timezone="America/New_York",
        date_format="MM/DD/YYYY",
    )
    db.add(default_settings)

    # Commit all changes
    await db.commit()
    await db.refresh(company)
    await db.refresh(admin_user)

    # Send activation email
    try:
        await email_service.send_company_activation_email(
            email=company_data.email,
            company_name=company_data.name,
            temporary_password=temp_password,
            user_id=admin_user.id,
        )
    except Exception as e:
        # Log email error but don't fail the company creation
        print(f"Failed to send activation email: {e}")

    return CompanyResponse(
        id=company.id,
        name=company.name,
        type=company.type,
        email=company.email,
        phone=company.phone,
        website=company.website,
        postal_code=company.postal_code,
        prefecture=company.prefecture,
        city=company.city,
        description=company.description,
        is_active=company.is_active == "1",
        is_demo=company.is_demo or False,
        demo_end_date=company.demo_end_date.isoformat()
        if company.demo_end_date
        else None,
        user_count=1,  # We just created the admin user
        job_count=0,
        created_at=company.created_at.isoformat(),
        updated_at=company.updated_at.isoformat(),
    )


@router.put("/companies/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: int,
    company_data: CompanyUpdate,
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    """Update a company."""
    # Get existing company
    query = select(Company).where(Company.id == company_id)
    result = await db.execute(query)
    company = result.scalar_one_or_none()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Company not found"
        )

    # Update fields
    update_data = company_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "is_active":
            setattr(company, field, "1" if value else "0")
        else:
            setattr(company, field, value)

    await db.commit()
    await db.refresh(company)

    # Get updated company with counts
    count_query = (
        select(
            Company,
            func.count(User.id).label("user_count"),
            func.coalesce(func.count(Company.jobs), 0).label("job_count"),
        )
        .outerjoin(User, Company.id == User.company_id)
        .outerjoin(Company.jobs)
        .where(Company.id == company_id)
        .group_by(Company.id)
    )

    count_result = await db.execute(count_query)
    company_data_with_counts = count_result.first()

    if company_data_with_counts:
        company, user_count, job_count = company_data_with_counts
    else:
        user_count = job_count = 0

    return CompanyResponse(
        id=company.id,
        name=company.name,
        type=company.type,
        email=company.email,
        phone=company.phone,
        website=company.website,
        postal_code=company.postal_code,
        prefecture=company.prefecture,
        city=company.city,
        description=company.description,
        is_active=company.is_active == "1",
        is_demo=company.is_demo or False,
        demo_end_date=company.demo_end_date.isoformat()
        if company.demo_end_date
        else None,
        user_count=user_count or 0,
        job_count=job_count or 0,
        created_at=company.created_at.isoformat(),
        updated_at=company.updated_at.isoformat(),
    )


@router.delete("/companies/{company_id}")
async def delete_company(
    company_id: int,
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    """Delete a company."""
    # Get existing company
    query = select(Company).where(Company.id == company_id)
    result = await db.execute(query)
    company = result.scalar_one_or_none()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Company not found"
        )

    # Check if company has users
    users_query = select(func.count(User.id)).where(User.company_id == company_id)
    users_result = await db.execute(users_query)
    user_count = users_result.scalar()

    if user_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete company with {user_count} associated users. Please reassign or delete users first.",
        )

    await db.delete(company)
    await db.commit()

    return {"message": "Company deleted successfully"}
