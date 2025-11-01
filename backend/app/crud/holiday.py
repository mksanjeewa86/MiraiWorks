from datetime import date

from sqlalchemy import and_, extract, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.holiday import Holiday
from app.schemas.holiday import HolidayCreate, HolidayUpdate


class CRUDHoliday(CRUDBase[Holiday, HolidayCreate, HolidayUpdate]):
    async def get_by_date(
        self, db: AsyncSession, *, holiday_date: date
    ) -> Holiday | None:
        """Get holiday by specific date"""
        result = await db.execute(select(Holiday).where(Holiday.date == holiday_date))
        return result.scalar_one_or_none()

    async def get_by_year(
        self, db: AsyncSession, *, year: int, country: str = "JP"
    ) -> list[Holiday]:
        """Get all holidays for a specific year and country"""
        result = await db.execute(
            select(Holiday)
            .where(and_(Holiday.year == year, Holiday.country == country))
            .order_by(Holiday.date)
        )
        return list(result.scalars().all())

    async def get_by_date_range(
        self, db: AsyncSession, *, date_from: date, date_to: date, country: str = "JP"
    ) -> list[Holiday]:
        """Get holidays within a date range"""
        result = await db.execute(
            select(Holiday)
            .where(
                and_(
                    Holiday.date >= date_from,
                    Holiday.date <= date_to,
                    Holiday.country == country,
                )
            )
            .order_by(Holiday.date)
        )
        return list(result.scalars().all())

    async def get_by_month(
        self, db: AsyncSession, *, year: int, month: int, country: str = "JP"
    ) -> list[Holiday]:
        """Get holidays for a specific month and year"""
        result = await db.execute(
            select(Holiday)
            .where(
                and_(
                    extract("year", Holiday.date) == year,
                    extract("month", Holiday.date) == month,
                    Holiday.country == country,
                )
            )
            .order_by(Holiday.date)
        )
        return list(result.scalars().all())

    async def get_national_holidays(
        self, db: AsyncSession, *, year: int, country: str = "JP"
    ) -> list[Holiday]:
        """Get all national holidays for a specific year and country"""
        result = await db.execute(
            select(Holiday)
            .where(
                and_(
                    Holiday.year == year,
                    Holiday.country == country,
                    Holiday.is_national,
                )
            )
            .order_by(Holiday.date)
        )
        return list(result.scalars().all())

    async def check_is_holiday(
        self, db: AsyncSession, *, holiday_date: date, country: str = "JP"
    ) -> bool:
        """Check if a specific date is a holiday"""
        result = await db.execute(
            select(Holiday).where(
                and_(Holiday.date == holiday_date, Holiday.country == country)
            )
        )
        return result.scalar_one_or_none() is not None

    async def get_upcoming_holidays(
        self, db: AsyncSession, *, from_date: date, limit: int = 10, country: str = "JP"
    ) -> list[Holiday]:
        """Get upcoming holidays from a specific date"""
        result = await db.execute(
            select(Holiday)
            .where(and_(Holiday.date >= from_date, Holiday.country == country))
            .order_by(Holiday.date)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def create_multiple(
        self, db: AsyncSession, *, holidays: list[HolidayCreate]
    ) -> list[Holiday]:
        """Create multiple holidays at once"""
        db_holidays = []
        for holiday_data in holidays:
            # Calculate year from date
            holiday_dict = holiday_data.dict()
            holiday_dict["year"] = holiday_data.date.year

            db_holiday = Holiday(**holiday_dict)
            db.add(db_holiday)
            db_holidays.append(db_holiday)

        await db.commit()
        for db_holiday in db_holidays:
            await db.refresh(db_holiday)

        return db_holidays


holiday = CRUDHoliday(Holiday)
