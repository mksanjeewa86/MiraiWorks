from datetime import date, datetime
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.holiday import holiday as holiday_crud
from app.models.holiday import Holiday
from app.schemas.holiday import HolidayCreate


class HolidayService:
    """Service for holiday-related business logic"""

    async def get_holidays_for_calendar(
        self,
        db: AsyncSession,
        start_date: date,
        end_date: date,
        country: str = "JP"
    ) -> List[Holiday]:
        """Get holidays for calendar view within date range"""
        return await holiday_crud.get_by_date_range(
            db, date_from=start_date, date_to=end_date, country=country
        )

    async def is_holiday_date(
        self,
        db: AsyncSession,
        check_date: date,
        country: str = "JP"
    ) -> bool:
        """Check if a specific date is a holiday"""
        return await holiday_crud.check_is_holiday(
            db, holiday_date=check_date, country=country
        )

    async def get_holiday_info(
        self,
        db: AsyncSession,
        check_date: date,
        country: str = "JP"
    ) -> Optional[Holiday]:
        """Get holiday information for a specific date"""
        return await holiday_crud.get_by_date(db, holiday_date=check_date)

    async def get_next_holiday(
        self,
        db: AsyncSession,
        from_date: Optional[date] = None,
        country: str = "JP"
    ) -> Optional[Holiday]:
        """Get the next upcoming holiday"""
        start_date = from_date or date.today()
        holidays = await holiday_crud.get_upcoming_holidays(
            db, from_date=start_date, limit=1, country=country
        )
        return holidays[0] if holidays else None

    async def setup_japan_holidays_2025(self, db: AsyncSession) -> List[Holiday]:
        """Setup Japan national holidays for 2025"""
        japan_holidays_2025 = [
            {
                "name": "元日",
                "name_en": "New Year's Day",
                "date": date(2025, 1, 1),
                "description": "新年を祝う日",
                "description_en": "The first day of the year"
            },
            {
                "name": "成人の日",
                "name_en": "Coming of Age Day",
                "date": date(2025, 1, 13),
                "description": "大人になったことを祝う日",
                "description_en": "Day to celebrate becoming an adult"
            },
            {
                "name": "建国記念の日",
                "name_en": "National Foundation Day",
                "date": date(2025, 2, 11),
                "description": "日本の建国を記念する日",
                "description_en": "Day to commemorate the founding of Japan"
            },
            {
                "name": "天皇誕生日",
                "name_en": "The Emperor's Birthday",
                "date": date(2025, 2, 23),
                "description": "天皇陛下の誕生日を祝う日",
                "description_en": "Day to celebrate the Emperor's birthday"
            },
            {
                "name": "春分の日",
                "name_en": "Spring Equinox Day",
                "date": date(2025, 3, 20),
                "description": "春の彼岸の中日",
                "description_en": "Vernal equinox day"
            },
            {
                "name": "昭和の日",
                "name_en": "Showa Day",
                "date": date(2025, 4, 29),
                "description": "昭和天皇の誕生日",
                "description_en": "Emperor Showa's birthday"
            },
            {
                "name": "憲法記念日",
                "name_en": "Constitution Memorial Day",
                "date": date(2025, 5, 3),
                "description": "日本国憲法の施行を記念する日",
                "description_en": "Day to commemorate the Japanese Constitution"
            },
            {
                "name": "みどりの日",
                "name_en": "Greenery Day",
                "date": date(2025, 5, 4),
                "description": "自然に親しむとともにその恩恵に感謝し、豊かな心をはぐくむ日",
                "description_en": "Day to commune with nature and be grateful for its blessings"
            },
            {
                "name": "こどもの日",
                "name_en": "Children's Day",
                "date": date(2025, 5, 5),
                "description": "こどもの人格を重んじ、こどもの幸福をはかるとともに、母に感謝する日",
                "description_en": "Day to respect children's personalities and promote their happiness"
            },
            {
                "name": "海の日",
                "name_en": "Marine Day",
                "date": date(2025, 7, 21),
                "description": "海の恩恵に感謝するとともに、海洋国日本の繁栄を願う日",
                "description_en": "Day to give thanks for the ocean's bounty and pray for Japan's prosperity"
            },
            {
                "name": "山の日",
                "name_en": "Mountain Day",
                "date": date(2025, 8, 11),
                "description": "山に親しむ機会を得て、山の恩恵に感謝する日",
                "description_en": "Day to become familiar with mountains and appreciate their benefits"
            },
            {
                "name": "敬老の日",
                "name_en": "Respect for the Aged Day",
                "date": date(2025, 9, 15),
                "description": "多年にわたり社会につくしてきた老人を敬愛し、長寿を祝う日",
                "description_en": "Day to honor elderly people and celebrate their longevity"
            },
            {
                "name": "秋分の日",
                "name_en": "Autumn Equinox Day",
                "date": date(2025, 9, 23),
                "description": "祖先をうやまい、なくなった人々をしのぶ日",
                "description_en": "Day to honor ancestors and remember deceased family members"
            },
            {
                "name": "スポーツの日",
                "name_en": "Sports Day",
                "date": date(2025, 10, 13),
                "description": "スポーツにしたしみ、健康な心身をつちかう日",
                "description_en": "Day to enjoy sports and develop a healthy mind and body"
            },
            {
                "name": "文化の日",
                "name_en": "Culture Day",
                "date": date(2025, 11, 3),
                "description": "自由と平和を愛し、文化をすすめる日",
                "description_en": "Day to promote culture and love freedom and peace"
            },
            {
                "name": "勤労感謝の日",
                "name_en": "Labor Thanksgiving Day",
                "date": date(2025, 11, 23),
                "description": "勤労をたっとび、生産を祝い、国民たがいに感謝しあう日",
                "description_en": "Day to honor labor, celebrate production, and give thanks to each other"
            }
        ]

        holiday_objects = []
        for holiday_data in japan_holidays_2025:
            holiday_create = HolidayCreate(
                name=holiday_data["name"],
                name_en=holiday_data["name_en"],
                date=holiday_data["date"],
                country="JP",
                is_national=True,
                is_recurring=True,
                description=holiday_data["description"],
                description_en=holiday_data["description_en"]
            )
            holiday_objects.append(holiday_create)

        # Check if holidays already exist for 2025
        existing_holidays = await holiday_crud.get_by_year(db, year=2025, country="JP")
        if existing_holidays:
            return existing_holidays

        # Create holidays
        created_holidays = await holiday_crud.create_multiple(db, holidays=holiday_objects)
        return created_holidays

    def format_holiday_for_calendar(self, holiday: Holiday) -> dict:
        """Format holiday data for calendar display"""
        return {
            "id": f"holiday-{holiday.id}",
            "title": holiday.name_en or holiday.name,
            "start": holiday.date.isoformat(),
            "end": holiday.date.isoformat(),
            "allDay": True,
            "backgroundColor": "#dc2626",  # Red color for holidays
            "borderColor": "#b91c1c",
            "textColor": "#ffffff",
            "extendedProps": {
                "type": "holiday",
                "isHoliday": True,
                "holidayName": holiday.name,
                "holidayNameEn": holiday.name_en,
                "description": holiday.description,
                "descriptionEn": holiday.description_en,
                "country": holiday.country,
                "isNational": holiday.is_national
            }
        }


holiday_service = HolidayService()