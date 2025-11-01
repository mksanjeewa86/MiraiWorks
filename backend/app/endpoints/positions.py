from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.endpoints import API_ROUTES
from app.crud.position import position as position_crud
from app.database import get_db
from app.dependencies import get_current_active_user, get_optional_current_user
from app.models.user import User
from app.schemas.position import (
    PositionBulkStatusUpdateRequest,
    PositionCreate,
    PositionInfo,
    PositionListResponse,
    PositionStatsResponse,
    PositionStatusUpdateRequest,
    PositionUpdate,
)

router = APIRouter()


def _add_legacy_position_keys(model: BaseModel) -> dict[str, Any]:
    payload = model.model_dump() if isinstance(model, BaseModel) else dict(model)
    if "positions" in payload and "jobs" not in payload:
        payload["jobs"] = payload["positions"]
    return payload


@router.post(
    API_ROUTES.POSITIONS.BASE,
    response_model=PositionInfo,
    status_code=status.HTTP_201_CREATED,
)
@router.post(
    API_ROUTES.POSITIONS.BASE_SLASH,
    response_model=PositionInfo,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
async def create_position(
    *,
    db: AsyncSession = Depends(get_db),
    position_in: PositionCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create new position posting.
    """
    # Check if user can create positions
    if not current_user.is_admin and not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to create position postings",
        )

    # If user is not admin, ensure they can only create positions for their company
    if (
        not current_user.is_admin
        and current_user.company_id
        and position_in.company_id != current_user.company_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only create positions for your own company",
        )

    # Add posted_by field from current user
    position_data = position_in.model_dump()
    position_data["posted_by"] = current_user.id

    position = await position_crud.create_with_slug(
        db=db, obj_in=PositionCreate(**position_data)
    )
    return position


@router.get(API_ROUTES.POSITIONS.BASE, response_model=PositionListResponse)
@router.get(
    API_ROUTES.POSITIONS.BASE_SLASH,
    response_model=PositionListResponse,
    include_in_schema=False,
)
async def list_positions(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of positions to skip"),
    limit: int = Query(100, ge=1, le=500, description="Number of positions to return"),
    location: str | None = Query(None, description="Filter by location"),
    job_type: str | None = Query(None, description="Filter by job type"),
    salary_min: int | None = Query(None, ge=0, description="Minimum salary filter"),
    salary_max: int | None = Query(None, ge=0, description="Maximum salary filter"),
    company_id: int | None = Query(None, description="Filter by company"),
    search: str | None = Query(
        None, description="Search in title, description, requirements"
    ),
    days_since_posted: int | None = Query(
        None, ge=1, description="Filter positions posted within last N days"
    ),
    status: str | None = Query("published", description="Position status filter"),
    current_user: User | None = Depends(get_optional_current_user),
) -> Any:
    """Retrieve positions with optional filtering, adjusting visibility based on the caller."""
    is_admin_access = bool(
        current_user and (current_user.is_admin or current_user.company_id)
    )

    if not is_admin_access:
        positions, total_count = await position_crud.get_published_positions_with_count(
            db=db,
            skip=skip,
            limit=limit,
            location=location,
            job_type=job_type,
            salary_min=salary_min,
            salary_max=salary_max,
            company_id=company_id,
            search=search,
            days_since_posted=days_since_posted,
        )

        sanitized: list[PositionInfo] = []
        for pos in positions:
            info = PositionInfo.model_validate(pos, from_attributes=True)
            updates = {
                "application_count": 0,
                "view_count": 0,
                "company_name": pos.company.name if pos.company else None,
            }
            if not pos.show_salary:
                updates.update(
                    salary_min=None,
                    salary_max=None,
                    salary_type=None,
                    salary_currency=None,
                )
            sanitized.append(info.model_copy(update=updates))

        has_more = len(sanitized) == limit
        return PositionListResponse(
            positions=sanitized,
            total=total_count,
            skip=skip,
            limit=limit,
            has_more=has_more,
        )

    if current_user and not current_user.is_admin and current_user.company_id:
        company_id = current_user.company_id

    if status == "published":
        positions = await position_crud.get_published_positions(
            db=db,
            skip=skip,
            limit=limit,
            location=location,
            job_type=job_type,
            salary_min=salary_min,
            salary_max=salary_max,
            company_id=company_id,
            search=search,
        )
    else:
        positions = await position_crud.get_positions_by_status(
            db=db,
            status=status or "open",
            skip=skip,
            limit=limit,
        )

    # Convert positions to PositionInfo with company names
    position_infos: list[PositionInfo] = []
    for pos in positions:
        info = PositionInfo.model_validate(pos, from_attributes=True)
        # Populate company_name from relationship
        if hasattr(pos, "company") and pos.company:
            info = info.model_copy(update={"company_name": pos.company.name})
        position_infos.append(info)

    has_more = len(positions) == limit

    return PositionListResponse(
        positions=position_infos,
        total=len(positions),
        skip=skip,
        limit=limit,
        has_more=has_more,
    )


# Search functionality is now integrated into the main list_positions endpoint
# Use the main endpoint with search parameter instead


@router.get(API_ROUTES.POSITIONS.POPULAR, response_model=list[PositionInfo])
async def get_popular_positions(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(
        10, ge=1, le=50, description="Number of popular positions to return"
    ),
) -> Any:
    """
    Get most popular positions by view count.
    """
    positions = await position_crud.get_popular_positions(db=db, limit=limit)
    return positions


@router.get(API_ROUTES.POSITIONS.RECENT, response_model=list[PositionInfo])
async def get_recent_positions(
    db: AsyncSession = Depends(get_db),
    days: int = Query(
        7, ge=1, le=30, description="Positions posted in the last N days"
    ),
    limit: int = Query(100, ge=1, le=500),
) -> Any:
    """
    Get recently posted positions.
    """
    positions = await position_crud.get_recent_positions(db=db, days=days, limit=limit)
    return positions


@router.get(API_ROUTES.POSITIONS.EXPIRING, response_model=list[PositionInfo])
async def get_expiring_positions(
    db: AsyncSession = Depends(get_db),
    days: int = Query(
        7, ge=1, le=30, description="Positions expiring in the next N days"
    ),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get positions expiring soon (admin/employer only).
    """
    if not current_user.is_admin and not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view expiring positions",
        )

    positions = await position_crud.get_positions_expiring_soon(
        db=db, days=days, limit=limit
    )
    return positions


@router.get(API_ROUTES.POSITIONS.STATISTICS, response_model=PositionStatsResponse)
async def get_position_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get position posting statistics (admin only).
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )

    stats = await position_crud.get_position_statistics(db=db)
    return PositionStatsResponse(**stats)


@router.get(API_ROUTES.POSITIONS.COMPANY, response_model=list[PositionInfo])
async def get_company_positions(
    *,
    db: AsyncSession = Depends(get_db),
    company_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get positions for a specific company.
    """
    # Employers can only see their own company's positions
    if not current_user.is_admin and current_user.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only view positions for your own company",
        )

    positions = await position_crud.get_by_company(
        db=db, company_id=company_id, skip=skip, limit=limit
    )
    return positions


@router.get(API_ROUTES.POSITIONS.BY_ID, response_model=PositionInfo)
async def get_position(*, db: AsyncSession = Depends(get_db), position_id: int) -> Any:
    """
    Get position by ID and increment view count.
    """
    position = await position_crud.get(db=db, id=position_id)
    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Position not found"
        )

    # Increment view count for published positions
    if position.status == "published":
        position = await position_crud.increment_position_view_count(
            db=db, position_id=position_id
        )

    return position


@router.get(API_ROUTES.POSITIONS.BY_SLUG, response_model=PositionInfo)
async def get_position_by_slug(*, db: AsyncSession = Depends(get_db), slug: str) -> Any:
    """
    Get position by slug and increment view count.
    """
    position = await position_crud.get_by_slug(db=db, slug=slug)
    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Position not found"
        )

    # Increment view count for published positions
    if position.status == "published":
        position = await position_crud.increment_position_view_count(
            db=db, position_id=position.id
        )

    return position


@router.put(API_ROUTES.POSITIONS.BY_ID, response_model=PositionInfo)
async def update_position(
    *,
    db: AsyncSession = Depends(get_db),
    position_id: int,
    position_in: PositionUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update position posting.
    """
    position = await position_crud.get(db=db, id=position_id)
    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Position not found"
        )

    # Check permissions
    if not current_user.is_admin and current_user.company_id != position.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only update positions for your own company",
        )

    if (
        position_in.salary_min is not None
        and position_in.salary_max is not None
        and position_in.salary_max <= position_in.salary_min
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="salary_max must be greater than salary_min",
        )

    position = await position_crud.update(db=db, db_obj=position, obj_in=position_in)
    return position


@router.patch(API_ROUTES.POSITIONS.BULK_STATUS, response_model=list[PositionInfo])
async def bulk_update_position_status(
    *,
    db: AsyncSession = Depends(get_db),
    payload: PositionBulkStatusUpdateRequest,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Bulk update position statuses."""
    if not current_user.is_admin and not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update position postings",
        )

    new_status = (
        payload.status.value if hasattr(payload.status, "value") else payload.status
    )
    positions = await position_crud.bulk_update_position_status(
        db=db, position_ids=payload.position_ids, status=new_status
    )

    if not positions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Positions not found"
        )

    if not current_user.is_admin:
        unauthorized = [
            position
            for position in positions
            if getattr(position, "company_id", None) != current_user.company_id
        ]
        if unauthorized:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only update positions for your own company",
            )

    return positions


@router.patch(API_ROUTES.POSITIONS.STATUS, response_model=PositionInfo)
async def update_position_status(
    *,
    db: AsyncSession = Depends(get_db),
    position_id: int,
    status_in: PositionStatusUpdateRequest,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Update the status of an existing position posting."""
    position = await position_crud.get(db=db, id=position_id)
    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Position not found"
        )

    if not current_user.is_admin and current_user.company_id != position.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only update positions for your own company",
        )

    new_status = (
        status_in.status.value
        if hasattr(status_in.status, "value")
        else status_in.status
    )
    updated_position = await position_crud.update(
        db=db, db_obj=position, obj_in={"status": new_status}
    )
    return updated_position


@router.delete(API_ROUTES.POSITIONS.BY_ID, status_code=status.HTTP_204_NO_CONTENT)
async def delete_position(
    *,
    db: AsyncSession = Depends(get_db),
    position_id: int,
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete position posting (admin only).
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete position postings",
        )

    position = await position_crud.get(db=db, id=position_id)
    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Position not found"
        )

    await position_crud.remove(db=db, id=position_id)
