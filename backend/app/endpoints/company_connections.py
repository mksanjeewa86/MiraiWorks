"""Company connections API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config.endpoints import API_ROUTES
from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.company_connection import (
    CompanyConnectionInfo,
    CompanyToCompanyConnectionCreate,
    UserToCompanyConnectionCreate,
)
from app.services.company_connection_service import company_connection_service

router = APIRouter()


@router.post(
    API_ROUTES.COMPANY_CONNECTIONS.USER_TO_COMPANY, response_model=CompanyConnectionInfo
)
async def create_user_to_company_connection(
    connection_data: UserToCompanyConnectionCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a connection between current user and a company.

    This allows the user to interact with any user in the target company.
    """
    try:
        connection = await company_connection_service.connect_user_to_company(
            db=db,
            user_id=current_user.id,
            company_id=connection_data.target_company_id,
            created_by_id=current_user.id,
            connection_type=connection_data.connection_type,
            can_message=connection_data.can_message,
            can_view_profile=connection_data.can_view_profile,
            can_assign_tasks=connection_data.can_assign_tasks,
        )

        # Eager load relationships for response
        await db.refresh(
            connection,
            [
                "source_user",
                "target_company",
            ],
        )

        return CompanyConnectionInfo(
            id=connection.id,
            source_type=connection.source_type,
            source_user_id=connection.source_user_id,
            source_company_id=connection.source_company_id,
            target_company_id=connection.target_company_id,
            is_active=connection.is_active,
            connection_type=connection.connection_type,
            can_message=connection.can_message,
            can_view_profile=connection.can_view_profile,
            can_assign_tasks=connection.can_assign_tasks,
            creation_type=connection.creation_type,
            created_by=connection.created_by,
            created_at=connection.created_at,
            updated_at=connection.updated_at,
            source_display_name=connection.source_display_name,
            target_company_name=connection.target_company.name
            if connection.target_company
            else None,
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    API_ROUTES.COMPANY_CONNECTIONS.COMPANY_TO_COMPANY,
    response_model=CompanyConnectionInfo,
)
async def create_company_to_company_connection(
    connection_data: CompanyToCompanyConnectionCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a connection between two companies.

    This allows any user from source company to interact with any user from target company.
    User must belong to the source company to create this connection.
    """
    # Verify user belongs to source company
    if current_user.company_id != connection_data.source_company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create connections for your own company",
        )

    try:
        connection = await company_connection_service.connect_companies(
            db=db,
            source_company_id=connection_data.source_company_id,
            target_company_id=connection_data.target_company_id,
            created_by_id=current_user.id,
            connection_type=connection_data.connection_type,
            can_message=connection_data.can_message,
            can_view_profile=connection_data.can_view_profile,
            can_assign_tasks=connection_data.can_assign_tasks,
        )

        # Eager load relationships for response
        await db.refresh(
            connection,
            [
                "source_company",
                "target_company",
            ],
        )

        return CompanyConnectionInfo(
            id=connection.id,
            source_type=connection.source_type,
            source_user_id=connection.source_user_id,
            source_company_id=connection.source_company_id,
            target_company_id=connection.target_company_id,
            is_active=connection.is_active,
            connection_type=connection.connection_type,
            can_message=connection.can_message,
            can_view_profile=connection.can_view_profile,
            can_assign_tasks=connection.can_assign_tasks,
            creation_type=connection.creation_type,
            created_by=connection.created_by,
            created_at=connection.created_at,
            updated_at=connection.updated_at,
            source_display_name=connection.source_display_name,
            target_company_name=connection.target_company.name
            if connection.target_company
            else None,
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    API_ROUTES.COMPANY_CONNECTIONS.MY_CONNECTIONS,
    response_model=list[CompanyConnectionInfo],
)
async def get_my_connections(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all company connections for the current user.

    Returns:
    - User-to-company connections where user is the source
    - Company-to-company connections where user's company is involved
    """
    from sqlalchemy import or_, select

    from app.models.company_connection import CompanyConnection

    # Build query for user's connections
    conditions = []

    # 1. User-to-company connections (user is source)
    conditions.append(
        CompanyConnection.source_user_id == current_user.id,
    )

    # 2. Company-to-company connections (user's company is source)
    if current_user.company_id:
        conditions.append(
            CompanyConnection.source_company_id == current_user.company_id,
        )

    if not conditions:
        return []

    result = await db.execute(
        select(CompanyConnection)
        .where(or_(*conditions))
        .options(
            selectinload(CompanyConnection.source_user),
            selectinload(CompanyConnection.source_company),
            selectinload(CompanyConnection.target_company),
        )
    )

    connections = result.scalars().all()

    return [
        CompanyConnectionInfo(
            id=conn.id,
            source_type=conn.source_type,
            source_user_id=conn.source_user_id,
            source_company_id=conn.source_company_id,
            target_company_id=conn.target_company_id,
            is_active=conn.is_active,
            connection_type=conn.connection_type,
            can_message=conn.can_message,
            can_view_profile=conn.can_view_profile,
            can_assign_tasks=conn.can_assign_tasks,
            creation_type=conn.creation_type,
            created_by=conn.created_by,
            created_at=conn.created_at,
            updated_at=conn.updated_at,
            source_display_name=conn.source_display_name,
            target_company_name=conn.target_company.name
            if conn.target_company
            else None,
        )
        for conn in connections
    ]


@router.get(API_ROUTES.COMPANY_CONNECTIONS.BY_ID, response_model=CompanyConnectionInfo)
async def get_connection_by_id(
    connection_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get details of a specific company connection."""
    from sqlalchemy import select

    from app.models.company_connection import CompanyConnection

    result = await db.execute(
        select(CompanyConnection)
        .where(CompanyConnection.id == connection_id)
        .options(
            selectinload(CompanyConnection.source_user),
            selectinload(CompanyConnection.source_company),
            selectinload(CompanyConnection.target_company),
        )
    )

    connection = result.scalar_one_or_none()

    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found",
        )

    # Verify user has access to this connection
    has_access = False
    if connection.source_user_id == current_user.id:
        has_access = True
    elif connection.source_company_id == current_user.company_id:
        has_access = True
    elif connection.target_company_id == current_user.company_id:
        has_access = True

    if not has_access and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this connection",
        )

    return CompanyConnectionInfo(
        id=connection.id,
        source_type=connection.source_type,
        source_user_id=connection.source_user_id,
        source_company_id=connection.source_company_id,
        target_company_id=connection.target_company_id,
        is_active=connection.is_active,
        connection_type=connection.connection_type,
        can_message=connection.can_message,
        can_view_profile=connection.can_view_profile,
        can_assign_tasks=connection.can_assign_tasks,
        creation_type=connection.creation_type,
        created_by=connection.created_by,
        created_at=connection.created_at,
        updated_at=connection.updated_at,
        source_display_name=connection.source_display_name,
        target_company_name=connection.target_company.name
        if connection.target_company
        else None,
    )


@router.put(
    API_ROUTES.COMPANY_CONNECTIONS.DEACTIVATE, response_model=CompanyConnectionInfo
)
async def deactivate_connection(
    connection_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Deactivate a company connection."""
    from sqlalchemy import select

    from app.models.company_connection import CompanyConnection

    # Get connection and verify access
    result = await db.execute(
        select(CompanyConnection)
        .where(CompanyConnection.id == connection_id)
        .options(
            selectinload(CompanyConnection.source_user),
            selectinload(CompanyConnection.source_company),
            selectinload(CompanyConnection.target_company),
        )
    )
    connection = result.scalar_one_or_none()

    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found",
        )

    # Verify user has permission to deactivate
    has_permission = False
    if connection.source_user_id == current_user.id:
        has_permission = True
    elif connection.source_company_id == current_user.company_id:
        has_permission = True
    elif current_user.is_admin:
        has_permission = True

    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to deactivate this connection",
        )

    updated_connection = await company_connection_service.deactivate_connection(
        db=db, connection_id=connection_id
    )

    if not updated_connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found",
        )

    # Eager load for response
    await db.refresh(
        updated_connection,
        [
            "source_user",
            "source_company",
            "target_company",
        ],
    )

    return CompanyConnectionInfo(
        id=updated_connection.id,
        source_type=updated_connection.source_type,
        source_user_id=updated_connection.source_user_id,
        source_company_id=updated_connection.source_company_id,
        target_company_id=updated_connection.target_company_id,
        is_active=updated_connection.is_active,
        connection_type=updated_connection.connection_type,
        can_message=updated_connection.can_message,
        can_view_profile=updated_connection.can_view_profile,
        can_assign_tasks=updated_connection.can_assign_tasks,
        creation_type=updated_connection.creation_type,
        created_by=updated_connection.created_by,
        created_at=updated_connection.created_at,
        updated_at=updated_connection.updated_at,
        source_display_name=updated_connection.source_display_name,
        target_company_name=updated_connection.target_company.name
        if updated_connection.target_company
        else None,
    )


@router.put(
    API_ROUTES.COMPANY_CONNECTIONS.ACTIVATE, response_model=CompanyConnectionInfo
)
async def activate_connection(
    connection_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Activate a company connection."""
    from sqlalchemy import select

    from app.models.company_connection import CompanyConnection

    # Get connection and verify access
    result = await db.execute(
        select(CompanyConnection)
        .where(CompanyConnection.id == connection_id)
        .options(
            selectinload(CompanyConnection.source_user),
            selectinload(CompanyConnection.source_company),
            selectinload(CompanyConnection.target_company),
        )
    )
    connection = result.scalar_one_or_none()

    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found",
        )

    # Verify user has permission to activate
    has_permission = False
    if connection.source_user_id == current_user.id:
        has_permission = True
    elif connection.source_company_id == current_user.company_id:
        has_permission = True
    elif current_user.is_admin:
        has_permission = True

    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to activate this connection",
        )

    updated_connection = await company_connection_service.activate_connection(
        db=db, connection_id=connection_id
    )

    if not updated_connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found",
        )

    # Eager load for response
    await db.refresh(
        updated_connection,
        [
            "source_user",
            "source_company",
            "target_company",
        ],
    )

    return CompanyConnectionInfo(
        id=updated_connection.id,
        source_type=updated_connection.source_type,
        source_user_id=updated_connection.source_user_id,
        source_company_id=updated_connection.source_company_id,
        target_company_id=updated_connection.target_company_id,
        is_active=updated_connection.is_active,
        connection_type=updated_connection.connection_type,
        can_message=updated_connection.can_message,
        can_view_profile=updated_connection.can_view_profile,
        can_assign_tasks=updated_connection.can_assign_tasks,
        creation_type=updated_connection.creation_type,
        created_by=updated_connection.created_by,
        created_at=updated_connection.created_at,
        updated_at=updated_connection.updated_at,
        source_display_name=updated_connection.source_display_name,
        target_company_name=updated_connection.target_company.name
        if updated_connection.target_company
        else None,
    )
