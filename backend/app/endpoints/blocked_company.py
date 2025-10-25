"""
Blocked Company Endpoints

API endpoints for managing candidate's blocked company list.
"""


from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.endpoints import API_ROUTES
from app.crud import blocked_company as blocked_company_crud
from app.database import get_db
from app.endpoints.auth import get_current_active_user
from app.models.user import User
from app.schemas.blocked_company import (
    BlockedCompanyCreate,
    BlockedCompanyInfo,
    CompanySearchResult,
)

router = APIRouter()


@router.get(API_ROUTES.BLOCKED_COMPANIES.BASE, response_model=list[BlockedCompanyInfo])
async def get_blocked_companies(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get all blocked companies for the current user.

    Returns:
        List of blocked companies with their details
    """
    blocked_companies = await blocked_company_crud.get_user_blocked_companies(
        db, user_id=current_user.id
    )
    return blocked_companies


@router.post(
    API_ROUTES.BLOCKED_COMPANIES.BASE,
    response_model=BlockedCompanyInfo,
    status_code=status.HTTP_201_CREATED,
)
async def create_blocked_company(
    blocked_data: BlockedCompanyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Block a company.

    Args:
        blocked_data: Company information to block (either company_id or company_name required)

    Returns:
        Created blocked company entry

    Raises:
        400: If neither company_id nor company_name is provided
        409: If company is already blocked
    """
    # Validate that at least one identifier is provided
    if not blocked_data.company_id and not blocked_data.company_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either company_id or company_name must be provided",
        )

    # Check if already blocked
    is_blocked = await blocked_company_crud.check_if_company_blocked(
        db,
        user_id=current_user.id,
        company_id=blocked_data.company_id,
        company_name=blocked_data.company_name,
    )

    if is_blocked:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Company is already blocked",
        )

    # Create blocked company entry
    blocked_company = await blocked_company_crud.create_blocked_company(
        db,
        user_id=current_user.id,
        company_id=blocked_data.company_id,
        company_name=blocked_data.company_name,
        reason=blocked_data.reason,
    )

    return blocked_company


@router.delete(
    API_ROUTES.BLOCKED_COMPANIES.BY_ID,
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_blocked_company(
    blocked_company_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Unblock a company.

    Args:
        blocked_company_id: ID of the blocked company entry to remove

    Raises:
        404: If blocked company not found or doesn't belong to user
    """
    deleted = await blocked_company_crud.delete_blocked_company(
        db, blocked_company_id=blocked_company_id, user_id=current_user.id
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blocked company not found",
        )


@router.get(
    API_ROUTES.BLOCKED_COMPANIES.SEARCH,
    response_model=list[CompanySearchResult],
)
async def search_companies(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Search for companies by name (for autocomplete).

    Args:
        q: Search query string
        limit: Maximum number of results (default: 10, max: 50)

    Returns:
        List of companies matching the search query
    """
    companies = await blocked_company_crud.search_companies_for_blocking(
        db, search_query=q, limit=limit
    )
    return companies
