
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.interview_note import InterviewNote
from app.schemas.interview_note import InterviewNoteCreate, InterviewNoteUpdate


class CRUDInterviewNote(CRUDBase[InterviewNote, InterviewNoteCreate, InterviewNoteUpdate]):
    """CRUD operations for interview notes."""

    async def get_by_interview_and_participant(
        self, db: AsyncSession, *, interview_id: int, participant_id: int
    ) -> InterviewNote | None:
        """Get interview note for a specific participant in an interview."""
        result = await db.execute(
            select(InterviewNote).where(
                and_(
                    InterviewNote.interview_id == interview_id,
                    InterviewNote.participant_id == participant_id
                )
            )
        )
        return result.scalar_one_or_none()

    async def create_or_update(
        self,
        db: AsyncSession,
        *,
        interview_id: int,
        participant_id: int,
        content: str | None
    ) -> InterviewNote:
        """Create a new note or update existing note for a participant."""
        # Check if note already exists
        existing_note = await self.get_by_interview_and_participant(
            db, interview_id=interview_id, participant_id=participant_id
        )

        if existing_note:
            # Update existing note
            existing_note.content = content
            await db.commit()
            await db.refresh(existing_note)
            return existing_note
        else:
            # Create new note
            note_data = InterviewNoteCreate(content=content)
            db_note = InterviewNote(
                interview_id=interview_id,
                participant_id=participant_id,
                **note_data.model_dump()
            )
            db.add(db_note)
            await db.commit()
            await db.refresh(db_note)
            return db_note

    async def delete_by_interview_and_participant(
        self, db: AsyncSession, *, interview_id: int, participant_id: int
    ) -> bool:
        """Delete interview note for a specific participant."""
        note = await self.get_by_interview_and_participant(
            db, interview_id=interview_id, participant_id=participant_id
        )
        if note:
            await db.delete(note)
            await db.commit()
            return True
        return False


interview_note = CRUDInterviewNote(InterviewNote)
