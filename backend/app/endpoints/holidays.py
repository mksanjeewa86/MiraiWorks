from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.endpoints import API_ROUTES
from app.crud.holiday import holiday as holiday_crud
from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.holiday import (
    CountryCode,
    HolidayCreate,
    HolidayInfo,
    HolidayListResponse,
    HolidayUpdate,
)

router = APIRouter()


@router.get(API_ROUTES.HOLIDAYS.BASE, response_model=HolidayListResponse)
async def get_holidays(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    year: int | None = Query(None, description="Filter by year"),
    country: CountryCode | None = Query(
        CountryCode.JAPAN, description="Filter by country"
    ),
    month: int | None = Query(None, ge=1, le=12, description="Filter by month"),
    is_national: bool | None = Query(None, description="Filter by national holidays"),
    date_from: date | None = Query(None, description="Filter holidays from this date"),
    date_to: date | None = Query(None, description="Filter holidays to this date"),
):
    """Get holidays with optional filters"""
    # Ensure country is not None (has default value)
    assert country is not None

    # Default to current year if no filters provided
    if not any([year, date_from, date_to]):
        year = datetime.now().year

    # Get holidays based on filters
    if date_from and date_to:
        holidays = await holiday_crud.get_by_date_range(
            db, date_from=date_from, date_to=date_to, country=country.value
        )
    elif year and month:
        holidays = await holiday_crud.get_by_month(
            db, year=year, month=month, country=country.value
        )
    elif year:
        if is_national is True:
            holidays = await holiday_crud.get_national_holidays(
                db, year=year, country=country.value
            )
        else:
            holidays = await holiday_crud.get_by_year(
                db, year=year, country=country.value
            )
    else:
        holidays = await holiday_crud.get_by_year(
            db, year=datetime.now().year, country=country.value
        )

    # Filter by national if specified and not already filtered
    if is_national is not None and not (year and is_national):
        holidays = [h for h in holidays if h.is_national == is_national]

    return HolidayListResponse(
        holidays=[HolidayInfo.model_validate(h) for h in holidays],
        total=len(holidays),
        year=year,
        country=country.value,
    )


@router.get(API_ROUTES.HOLIDAYS.UPCOMING, response_model=list[HolidayInfo])
async def get_upcoming_holidays(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    limit: int = Query(
        10, ge=1, le=50, description="Number of upcoming holidays to return"
    ),
    country: CountryCode = Query(CountryCode.JAPAN, description="Country code"),
    from_date: date | None = Query(None, description="Start date (default: today)"),
):
    """Get upcoming holidays from today or specified date"""
    start_date = from_date or date.today()

    holidays = await holiday_crud.get_upcoming_holidays(
        db, from_date=start_date, limit=limit, country=country.value
    )

    return holidays


@router.get(API_ROUTES.HOLIDAYS.CHECK, response_model=dict)
async def check_holiday(
    holiday_date: date,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    country: CountryCode = Query(CountryCode.JAPAN, description="Country code"),
):
    """Check if a specific date is a holiday"""
    is_holiday = await holiday_crud.check_is_holiday(
        db, holiday_date=holiday_date, country=country.value
    )

    holiday_info = None
    if is_holiday:
        holiday_info = await holiday_crud.get_by_date(db, holiday_date=holiday_date)

    return {"date": holiday_date, "is_holiday": is_holiday, "holiday": holiday_info}


@router.get(API_ROUTES.HOLIDAYS.BY_ID, response_model=HolidayInfo)
async def get_holiday(
    holiday_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific holiday by ID"""
    holiday = await holiday_crud.get(db, id=holiday_id)
    if not holiday:
        raise HTTPException(status_code=404, detail="Holiday not found")
    return holiday


@router.post(API_ROUTES.HOLIDAYS.BASE, response_model=HolidayInfo)
async def create_holiday(
    holiday_in: HolidayCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new holiday"""
    # Check if holiday already exists for this date
    existing_holiday = await holiday_crud.get_by_date(db, holiday_date=holiday_in.date)
    if existing_holiday:
        raise HTTPException(
            status_code=400, detail=f"Holiday already exists for date {holiday_in.date}"
        )

    # Add year to holiday data
    holiday_data = holiday_in.model_dump()
    holiday_data["year"] = holiday_in.date.year

    holiday = await holiday_crud.create(db, obj_in=HolidayCreate(**holiday_data))
    return holiday


@router.post(API_ROUTES.HOLIDAYS.BULK, response_model=list[HolidayInfo])
async def create_holidays_bulk(
    holidays_in: list[HolidayCreate],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create multiple holidays at once"""
    # Check for existing holidays
    existing_dates = []
    for holiday_in in holidays_in:
        existing = await holiday_crud.get_by_date(db, holiday_date=holiday_in.date)
        if existing:
            existing_dates.append(holiday_in.date)

    if existing_dates:
        raise HTTPException(
            status_code=400,
            detail=f"Holidays already exist for dates: {existing_dates}",
        )

    holidays = await holiday_crud.create_multiple(db, holidays=holidays_in)
    return holidays


@router.put(API_ROUTES.HOLIDAYS.BY_ID, response_model=HolidayInfo)
async def update_holiday(
    holiday_id: int,
    holiday_update: HolidayUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update a holiday"""
    holiday = await holiday_crud.get(db, id=holiday_id)
    if not holiday:
        raise HTTPException(status_code=404, detail="Holiday not found")

    # Update year if date is changed
    update_data = holiday_update.dict(exclude_unset=True)
    if "date" in update_data:
        update_data["year"] = update_data["date"].year

    holiday = await holiday_crud.update(db, db_obj=holiday, obj_in=update_data)
    return holiday


@router.delete(API_ROUTES.HOLIDAYS.BY_ID)
async def delete_holiday(
    holiday_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a holiday"""
    holiday = await holiday_crud.get(db, id=holiday_id)
    if not holiday:
        raise HTTPException(status_code=404, detail="Holiday not found")

    await holiday_crud.remove(db, id=holiday_id)
    return {"message": "Holiday deleted successfully"}
