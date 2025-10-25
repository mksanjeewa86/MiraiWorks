import logging
import secrets
import string
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.endpoints import API_ROUTES
from app.crud import company as company_crud
from app.database import get_db
from app.dependencies import get_current_active_user, require_super_admin
from app.models import Company, Role, User, UserRole, UserSettings
from app.models.company_subscription import CompanySubscription
from app.models.subscription_plan import SubscriptionPlan
from app.schemas.company import (
    CompanyAdminStatus,
    CompanyCreate,
    CompanyListResponse,
    CompanyResponse,
    CompanyUpdate,
)
from app.services.auth_service import auth_service
from app.services.email_service import email_service
from app.utils.constants import CompanyType
from app.utils.constants import UserRole as UserRoleEnum
from app.utils.datetime_utils import get_utc_now

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(API_ROUTES.COMPANIES.BASE, response_model=CompanyListResponse)
async def get_companies(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None),
    company_type: CompanyType | None = Query(None),
    is_active: bool | None = Query(None),
    include_deleted: bool = Query(False),
):
    """Get companies with filtering, pagination and search.

    - System admins can see all companies
    - Company admins can only see their own company
    """
    # Check user role
    user_roles = [user_role.role.name for user_role in current_user.user_roles]
    is_system_admin = UserRoleEnum.SYSTEM_ADMIN.value in user_roles
    is_admin = UserRoleEnum.ADMIN.value in user_roles

    # Only admins and system admins can access this endpoint
    if not (is_system_admin or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )

    # For company admins, filter to only their company
    if is_admin and not is_system_admin:
        if not current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Company admin must be associated with a company",
            )
        # Get only the user's company
        company = await company_crud.company.get(db, current_user.company_id)

        # Check if company exists and apply include_deleted filter
        if not company or (not include_deleted and company.is_deleted):
            return CompanyListResponse(
                companies=[],
                total=0,
                page=1,
                size=size,
                pages=0,
            )

        # Return single company as a list
        companies = [company]
        total = 1
    else:
        # System admin can see all companies
        companies, total = await company_crud.get_companies(
            db=db,
            page=page,
            size=size,
            search=search,
            company_type=company_type,
            is_active=is_active,
            include_deleted=include_deleted,
        )

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
            is_active=company.is_active == "1",
            user_count=0,
            job_count=0,
            is_deleted=company.is_deleted,
            deleted_at=company.deleted_at.isoformat() if company.deleted_at else None,
            deleted_by=company.deleted_by,
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


@router.get(API_ROUTES.COMPANIES.BY_ID, response_model=CompanyResponse)
async def get_company(
    company_id: int,
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific company by ID."""
    company_data = await company_crud.company.get_with_counts(db, company_id)

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
        user_count=user_count or 0,
        job_count=job_count or 0,
        is_deleted=company.is_deleted,
        deleted_at=company.deleted_at.isoformat() if company.deleted_at else None,
        deleted_by=company.deleted_by,
        created_at=company.created_at.isoformat(),
        updated_at=company.updated_at.isoformat(),
    )


@router.post(
    API_ROUTES.COMPANIES.CREATE,
    response_model=CompanyResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_company(
    company_data: CompanyCreate,
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    """Create a new company and associated admin user."""
    # Check for duplicate company email
    existing_company_query = select(Company).where(Company.email == company_data.email)
    existing_company_result = await db.execute(existing_company_query)
    if existing_company_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company with this email already exists",
        )

    # Check for duplicate user email (for the admin user that will be created)
    existing_user_query = select(User).where(User.email == company_data.email)
    existing_user_result = await db.execute(existing_user_query)
    if existing_user_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

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
        is_active="0",
    )

    db.add(company)
    await db.flush()

    def generate_password(length=12):
        characters = string.ascii_letters + string.digits + "!@#$%^&*"
        return "".join(secrets.choice(characters) for _ in range(length))

    temp_password = generate_password()
    hashed_password = auth_service.get_password_hash(temp_password)
    admin_user = User(
        email=company_data.email,
        hashed_password=hashed_password,
        first_name="Company",
        last_name="Administrator",
        phone=company_data.phone,
        is_active=False,
        is_admin=True,
        require_2fa=True,
        company_id=company.id,
    )

    db.add(admin_user)
    await db.flush()

    role_query = select(Role).where(Role.name == UserRoleEnum.ADMIN)
    role_result = await db.execute(role_query)
    admin_role = role_result.scalar_one_or_none()

    if not admin_role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Admin role not found in system",
        )

    user_role = UserRole(user_id=admin_user.id, role_id=admin_role.id)
    db.add(user_role)

    default_settings = UserSettings(
        user_id=admin_user.id,
        job_title="Company Administrator",
        bio=f"Administrator of {company_data.name}",
        email_notifications=True,
        push_notifications=True,
        sms_notifications=False,
        interview_reminders=True,
        application_updates=True,
        message_notifications=True,
        language="en",
        timezone="America/New_York",
        date_format="MM/DD/YYYY",
    )
    db.add(default_settings)

    # Create subscription based on provided options or auto-assign Basic plan
    plan_id = company_data.plan_id
    if not plan_id:
        # No plan specified - auto-assign Basic plan
        basic_plan_query = select(SubscriptionPlan).where(
            SubscriptionPlan.name == "basic"
        )
        basic_plan_result = await db.execute(basic_plan_query)
        basic_plan = basic_plan_result.scalar_one_or_none()
        if basic_plan:
            plan_id = basic_plan.id
        else:
            logger.warning(
                f"Basic plan not found - company {company.id} created without subscription"
            )

    if plan_id:
        # Calculate trial end date if trial subscription
        trial_end_date = None
        if company_data.is_trial and company_data.trial_days:
            trial_end_date = get_utc_now() + timedelta(days=company_data.trial_days)

        subscription = CompanySubscription(
            company_id=company.id,
            plan_id=plan_id,
            is_active=True,
            is_trial=company_data.is_trial or False,
            start_date=get_utc_now(),
            trial_end_date=trial_end_date,
            billing_cycle="monthly",
            auto_renew=True,
        )
        db.add(subscription)

        plan_name = "trial" if company_data.is_trial else "paid"
        logger.info(
            f"Assigned {plan_name} subscription (plan_id={plan_id}) to company {company.id} ({company_data.name})"
        )

    await db.commit()
    await db.refresh(company)
    await db.refresh(admin_user)

    try:
        await email_service.send_company_activation_email(
            email=company_data.email,
            company_name=company_data.name,
            temporary_password=temp_password,
            user_id=admin_user.id,
        )
    except Exception as e:
        logger.error(f"Error creating admin user for company {company.id}: {e}")
        # Continue with company creation even if admin user creation fails

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
        user_count=1,
        job_count=0,
        is_deleted=company.is_deleted,
        deleted_at=company.deleted_at.isoformat() if company.deleted_at else None,
        deleted_by=company.deleted_by,
        created_at=company.created_at.isoformat(),
        updated_at=company.updated_at.isoformat(),
    )


@router.put(API_ROUTES.COMPANIES.UPDATE, response_model=CompanyResponse)
async def update_company(
    company_id: int,
    company_data: CompanyUpdate,
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    """Update a company."""
    company = await company_crud.company.get(db, company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Company not found"
        )

    update_data = company_data.model_dump(exclude_unset=True)

    # Check for duplicate email if email is being updated
    if "email" in update_data and update_data["email"] != company.email:
        existing_company_query = select(Company).where(
            Company.email == update_data["email"]
        )
        existing_company_result = await db.execute(existing_company_query)
        if existing_company_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Company with this email already exists",
            )

    if "is_active" in update_data:
        update_data["is_active"] = "1" if update_data["is_active"] else "0"

    company = await company_crud.company.update(db, db_obj=company, obj_in=update_data)

    company_data_with_counts = await company_crud.company.get_with_counts(
        db, company_id
    )
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
        user_count=user_count or 0,
        job_count=job_count or 0,
        is_deleted=company.is_deleted,
        deleted_at=company.deleted_at.isoformat() if company.deleted_at else None,
        deleted_by=company.deleted_by,
        created_at=company.created_at.isoformat(),
        updated_at=company.updated_at.isoformat(),
    )


@router.delete(API_ROUTES.COMPANIES.DELETE)
async def delete_company(
    company_id: int,
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    """Delete a company."""
    company = await company_crud.company.get(db, company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Company not found"
        )

    users_query = select(func.count(User.id)).where(User.company_id == company_id)
    users_result = await db.execute(users_query)
    user_count = users_result.scalar()

    if user_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete company with {user_count} associated users. Please reassign or delete users first.",
        )

    await company_crud.company.remove(db, id=company_id)
    return {"message": "Company deleted successfully"}


@router.get(API_ROUTES.COMPANIES.ADMIN_STATUS, response_model=CompanyAdminStatus)
async def get_company_admin_status(
    company_id: int,
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    """Check if company has admin users."""
    company = await company_crud.company.get(db, company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Company not found"
        )

    admin_count = await company_crud.company.get_admin_count(db, company_id)
    return CompanyAdminStatus(
        company_id=company_id, has_active_admin=admin_count > 0, admin_count=admin_count
    )


@router.get(API_ROUTES.COMPANIES.MY_COMPANY, response_model=CompanyResponse)
async def get_my_company(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's company profile."""
    # Check if user is part of a company
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not associated with any company",
        )

    # Check if user is a company user (member or admin)
    user_roles = [user_role.role.name for user_role in current_user.user_roles]
    is_company_user = any(
        role
        in [
            UserRoleEnum.MEMBER.value,
            UserRoleEnum.ADMIN.value,
            UserRoleEnum.SYSTEM_ADMIN.value,
        ]
        for role in user_roles
    )

    if not is_company_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only company users can access company profile",
        )

    company_data = await company_crud.company.get_with_counts(
        db, current_user.company_id
    )

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
        user_count=user_count or 0,
        job_count=job_count or 0,
        is_deleted=company.is_deleted,
        deleted_at=company.deleted_at.isoformat() if company.deleted_at else None,
        deleted_by=company.deleted_by,
        created_at=company.created_at.isoformat(),
        updated_at=company.updated_at.isoformat(),
    )


@router.put(API_ROUTES.COMPANIES.UPDATE_MY_COMPANY, response_model=CompanyResponse)
async def update_my_company(
    company_data: CompanyUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update current user's company profile. Only company admins can update."""
    # Check if user is part of a company
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not associated with any company",
        )

    # Check if user is admin
    user_roles = [user_role.role.name for user_role in current_user.user_roles]
    is_admin = any(
        role in [UserRoleEnum.ADMIN.value, UserRoleEnum.SYSTEM_ADMIN.value]
        for role in user_roles
    )

    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only company admins can update company profile",
        )

    company = await company_crud.company.get(db, current_user.company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Company not found"
        )

    update_data = company_data.model_dump(exclude_unset=True)

    # Check for duplicate email if email is being updated
    if "email" in update_data and update_data["email"] != company.email:
        existing_company_query = select(Company).where(
            Company.email == update_data["email"]
        )
        existing_company_result = await db.execute(existing_company_query)
        if existing_company_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Company with this email already exists",
            )

    if "is_active" in update_data:
        update_data["is_active"] = "1" if update_data["is_active"] else "0"

    company = await company_crud.company.update(db, db_obj=company, obj_in=update_data)

    company_data_with_counts = await company_crud.company.get_with_counts(
        db, current_user.company_id
    )
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
        user_count=user_count or 0,
        job_count=job_count or 0,
        is_deleted=company.is_deleted,
        deleted_at=company.deleted_at.isoformat() if company.deleted_at else None,
        deleted_by=company.deleted_by,
        created_at=company.created_at.isoformat(),
        updated_at=company.updated_at.isoformat(),
    )
