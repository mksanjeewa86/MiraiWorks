from datetime import datetime
from typing import List, Optional

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.calendar_event import CalendarEvent
from app.schemas.calendar_event import CalendarEventCreate, CalendarEventUpdate, EventType, EventStatus


class CRUDCalendarEvent(CRUDBase[CalendarEvent, CalendarEventCreate, CalendarEventUpdate]):
    async def get_by_creator(
        self,
        db: AsyncSession,
        *,
        creator_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[CalendarEvent]:
        """Get calendar events by creator"""
        result = await db.execute(
            select(CalendarEvent)
            .where(CalendarEvent.creator_id == creator_id)
            .order_by(CalendarEvent.start_datetime)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_date_range(
        self,
        db: AsyncSession,
        *,
        start_date: datetime,
        end_date: datetime,
        creator_id: Optional[int] = None,
        event_type: Optional[EventType] = None,
        status: Optional[EventStatus] = None,
        include_all_day: bool = True
    ) -> List[CalendarEvent]:
        """Get calendar events within a date range"""
        conditions = [
            or_(
                # Event starts within range
                and_(
                    CalendarEvent.start_datetime >= start_date,
                    CalendarEvent.start_datetime <= end_date
                ),
                # Event ends within range
                and_(
                    CalendarEvent.end_datetime.is_not(None),
                    CalendarEvent.end_datetime >= start_date,
                    CalendarEvent.end_datetime <= end_date
                ),
                # Event spans the entire range
                and_(
                    CalendarEvent.start_datetime <= start_date,
                    or_(
                        CalendarEvent.end_datetime >= end_date,
                        CalendarEvent.end_datetime.is_(None)
                    )
                )
            )
        ]

        if creator_id is not None:
            conditions.append(CalendarEvent.creator_id == creator_id)

        if event_type is not None:
            conditions.append(CalendarEvent.event_type == event_type.value)

        if status is not None:
            conditions.append(CalendarEvent.status == status.value)

        if not include_all_day:
            conditions.append(CalendarEvent.is_all_day == False)

        result = await db.execute(
            select(CalendarEvent)
            .where(and_(*conditions))
            .order_by(CalendarEvent.start_datetime)
        )
        return result.scalars().all()

    async def get_by_date(
        self,
        db: AsyncSession,
        *,
        target_date: datetime,
        creator_id: Optional[int] = None
    ) -> List[CalendarEvent]:
        """Get calendar events for a specific date"""
        start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)

        return await self.get_by_date_range(
            db,
            start_date=start_of_day,
            end_date=end_of_day,
            creator_id=creator_id
        )

    async def get_upcoming_events(
        self,
        db: AsyncSession,
        *,
        creator_id: Optional[int] = None,
        limit: int = 10,
        from_datetime: Optional[datetime] = None
    ) -> List[CalendarEvent]:
        """Get upcoming calendar events"""
        if from_datetime is None:
            from_datetime = datetime.utcnow()

        conditions = [
            CalendarEvent.start_datetime >= from_datetime,
            CalendarEvent.status != EventStatus.CANCELLED.value
        ]

        if creator_id is not None:
            conditions.append(CalendarEvent.creator_id == creator_id)

        result = await db.execute(
            select(CalendarEvent)
            .where(and_(*conditions))
            .order_by(CalendarEvent.start_datetime)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_type(
        self,
        db: AsyncSession,
        *,
        event_type: EventType,
        creator_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[CalendarEvent]:
        """Get calendar events by type"""
        conditions = [CalendarEvent.event_type == event_type.value]

        if creator_id is not None:
            conditions.append(CalendarEvent.creator_id == creator_id)

        result = await db.execute(
            select(CalendarEvent)
            .where(and_(*conditions))
            .order_by(CalendarEvent.start_datetime)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_status(
        self,
        db: AsyncSession,
        *,
        status: EventStatus,
        creator_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[CalendarEvent]:
        """Get calendar events by status"""
        conditions = [CalendarEvent.status == status.value]

        if creator_id is not None:
            conditions.append(CalendarEvent.creator_id == creator_id)

        result = await db.execute(
            select(CalendarEvent)
            .where(and_(*conditions))
            .order_by(CalendarEvent.start_datetime)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_recurring_events(
        self,
        db: AsyncSession,
        *,
        creator_id: Optional[int] = None,
        parent_only: bool = True
    ) -> List[CalendarEvent]:
        """Get recurring calendar events"""
        if parent_only:
            conditions = [
                CalendarEvent.recurrence_rule.is_not(None),
                CalendarEvent.parent_event_id.is_(None)
            ]
        else:
            conditions = [CalendarEvent.recurrence_rule.is_not(None)]

        if creator_id is not None:
            conditions.append(CalendarEvent.creator_id == creator_id)

        result = await db.execute(
            select(CalendarEvent)
            .where(and_(*conditions))
            .order_by(CalendarEvent.start_datetime)
        )
        return result.scalars().all()

    async def get_event_instances(
        self,
        db: AsyncSession,
        *,
        parent_event_id: int
    ) -> List[CalendarEvent]:
        """Get all instances of a recurring event"""
        result = await db.execute(
            select(CalendarEvent)
            .where(CalendarEvent.parent_event_id == parent_event_id)
            .order_by(CalendarEvent.start_datetime)
        )
        return result.scalars().all()

    async def create_with_creator(
        self,
        db: AsyncSession,
        *,
        obj_in: CalendarEventCreate,
        creator_id: int
    ) -> CalendarEvent:
        """Create calendar event with creator"""
        obj_in_data = obj_in.model_dump()
        obj_in_data['creator_id'] = creator_id

        db_obj = CalendarEvent(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def create_multiple(
        self,
        db: AsyncSession,
        *,
        events_data: List[CalendarEventCreate],
        creator_id: int
    ) -> List[CalendarEvent]:
        """Create multiple calendar events at once"""
        db_events = []
        for event_data in events_data:
            obj_data = event_data.model_dump()
            obj_data['creator_id'] = creator_id

            db_event = CalendarEvent(**obj_data)
            db.add(db_event)
            db_events.append(db_event)

        await db.commit()
        for db_event in db_events:
            await db.refresh(db_event)

        return db_events

    async def get_conflicting_events(
        self,
        db: AsyncSession,
        *,
        start_datetime: datetime,
        end_datetime: Optional[datetime] = None,
        creator_id: int,
        exclude_event_id: Optional[int] = None
    ) -> List[CalendarEvent]:
        """Get events that conflict with the given time period"""
        if end_datetime is None:
            end_datetime = start_datetime

        conditions = [
            CalendarEvent.creator_id == creator_id,
            CalendarEvent.status != EventStatus.CANCELLED.value,
            or_(
                # New event starts during existing event
                and_(
                    CalendarEvent.start_datetime <= start_datetime,
                    or_(
                        CalendarEvent.end_datetime >= start_datetime,
                        CalendarEvent.end_datetime.is_(None)
                    )
                ),
                # New event ends during existing event
                and_(
                    CalendarEvent.start_datetime <= end_datetime,
                    or_(
                        CalendarEvent.end_datetime >= end_datetime,
                        CalendarEvent.end_datetime.is_(None)
                    )
                ),
                # Existing event is within new event
                and_(
                    CalendarEvent.start_datetime >= start_datetime,
                    or_(
                        CalendarEvent.end_datetime <= end_datetime,
                        CalendarEvent.end_datetime.is_(None)
                    )
                )
            )
        ]

        if exclude_event_id is not None:
            conditions.append(CalendarEvent.id != exclude_event_id)

        result = await db.execute(
            select(CalendarEvent)
            .where(and_(*conditions))
            .order_by(CalendarEvent.start_datetime)
        )
        return result.scalars().all()

    async def search_events(
        self,
        db: AsyncSession,
        *,
        search_term: str,
        creator_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[CalendarEvent]:
        """Search calendar events by title or description"""
        search_pattern = f"%{search_term}%"
        conditions = [
            or_(
                CalendarEvent.title.ilike(search_pattern),
                CalendarEvent.description.ilike(search_pattern),
                CalendarEvent.location.ilike(search_pattern)
            )
        ]

        if creator_id is not None:
            conditions.append(CalendarEvent.creator_id == creator_id)

        result = await db.execute(
            select(CalendarEvent)
            .where(and_(*conditions))
            .order_by(CalendarEvent.start_datetime)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_with_relationships(
        self,
        db: AsyncSession,
        *,
        event_id: int
    ) -> Optional[CalendarEvent]:
        """Get calendar event with all relationships loaded"""
        result = await db.execute(
            select(CalendarEvent)
            .options(
                selectinload(CalendarEvent.creator),
                selectinload(CalendarEvent.parent_event),
                selectinload(CalendarEvent.child_events)
            )
            .where(CalendarEvent.id == event_id)
        )
        return result.scalar_one_or_none()


calendar_event = CRUDCalendarEvent(CalendarEvent)