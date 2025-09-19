import secrets
from datetime import datetime
from typing import Any, Optional

from fastapi import HTTPException, status
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.interview import Interview
from app.models.meeting import (
    Meeting,
    meeting_participants,
)
from app.models.user import User
from app.schemas.meeting import (
    MeetingCreate,
    MeetingListParams,
    MeetingParticipantCreate,
    MeetingStatus,
    MeetingType,
    MeetingUpdate,
    ParticipantRole,
    ParticipantStatus,
)
from app.services.audit_service import log_action
from app.rbac import has_permission
from app.utils.permissions import check_company_access


class MeetingService:
    def __init__(self, db: Session):
        self.db = db

    def create_meeting(
        self, meeting_data: MeetingCreate, current_user: User
    ) -> Meeting:
        """Create a new meeting with RBAC validation"""

        # Validate interview access if provided
        interview = None
        if meeting_data.interview_id:
            interview = (
                self.db.query(Interview).filter_by(id=meeting_data.interview_id).first()
            )
            if not interview:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found"
                )

            # Validate interview access based on user role
            if not self._can_access_interview(current_user, interview):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to create meetings for this interview",
                )

        # Validate participants
        self._validate_and_get_participants(
            meeting_data.participants,
            meeting_data.meeting_type,
            current_user,
            interview,
        )

        # Generate unique room ID
        room_id = self._generate_room_id()

        # Create meeting
        meeting = Meeting(
            interview_id=meeting_data.interview_id,
            title=meeting_data.title,
            description=meeting_data.description,
            meeting_type=meeting_data.meeting_type,
            scheduled_start=meeting_data.scheduled_start,
            scheduled_end=meeting_data.scheduled_end,
            room_id=room_id,
            access_code=meeting_data.access_code,
            recording_enabled=meeting_data.recording_enabled,
            recording_consent_required=meeting_data.recording_consent_required,
            transcription_enabled=meeting_data.transcription_enabled,
            auto_summary=meeting_data.auto_summary,
            company_id=current_user.company_id,
            created_by=current_user.id,
        )

        self.db.add(meeting)
        self.db.flush()  # Get meeting ID

        # Add participants
        for participant_data in meeting_data.participants:
            participant_stmt = meeting_participants.insert().values(
                meeting_id=meeting.id,
                user_id=participant_data.user_id,
                role=participant_data.role,
                can_record=participant_data.can_record,
                recording_consent=participant_data.recording_consent,
            )
            self.db.execute(participant_stmt)

        self.db.commit()

        # Log action
        log_action(
            self.db,
            current_user,
            "meeting.create",
            f"Created meeting '{meeting.title}' (ID: {meeting.id})",
            {"meeting_id": meeting.id, "meeting_type": meeting_data.meeting_type},
        )

        return self.get_meeting_by_id(meeting.id, current_user)

    def get_meeting_by_id(self, meeting_id: int, current_user: User) -> Meeting:
        """Get meeting by ID with RBAC validation"""
        meeting = self.db.query(Meeting).filter_by(id=meeting_id).first()

        if not meeting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found"
            )

        # Validate access
        if not self._can_access_meeting(current_user, meeting):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this meeting",
            )

        return meeting

    def get_meeting_by_room_id(self, room_id: str, current_user: User) -> Meeting:
        """Get meeting by room ID with RBAC validation"""
        meeting = self.db.query(Meeting).filter_by(room_id=room_id).first()

        if not meeting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Meeting room not found"
            )

        if not self._can_access_meeting(current_user, meeting):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this meeting",
            )

        return meeting

    def list_meetings(
        self, params: MeetingListParams, current_user: User
    ) -> dict[str, Any]:
        """List meetings with filtering and pagination"""

        query = self.db.query(Meeting)

        # Company scoping
        query = query.filter(Meeting.company_id == current_user.company_id)

        # Role-based filtering
        if not has_permission(current_user, "meeting.view_all"):
            # Non-admin users can only see meetings they participate in
            query = query.join(meeting_participants).filter(
                meeting_participants.c.user_id == current_user.id
            )

        # Apply filters
        if params.status:
            query = query.filter(Meeting.status == params.status)

        if params.meeting_type:
            query = query.filter(Meeting.meeting_type == params.meeting_type)

        if params.start_date:
            query = query.filter(Meeting.scheduled_start >= params.start_date)

        if params.end_date:
            query = query.filter(Meeting.scheduled_start <= params.end_date)

        if params.participant_id:
            query = query.join(meeting_participants).filter(
                meeting_participants.c.user_id == params.participant_id
            )

        # Get total count
        total = query.count()

        # Apply pagination
        offset = (params.page - 1) * params.limit
        meetings = (
            query.order_by(Meeting.scheduled_start.desc())
            .offset(offset)
            .limit(params.limit)
            .all()
        )

        return {
            "meetings": meetings,
            "total": total,
            "page": params.page,
            "limit": params.limit,
            "total_pages": (total + params.limit - 1) // params.limit,
        }

    def update_meeting(
        self, meeting_id: int, update_data: MeetingUpdate, current_user: User
    ) -> Meeting:
        """Update meeting with RBAC validation"""

        meeting = self.get_meeting_by_id(meeting_id, current_user)

        # Validate permission to update
        if not self._can_modify_meeting(current_user, meeting):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to modify this meeting",
            )

        # Apply updates
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(meeting, field, value)

        meeting.updated_at = datetime.utcnow()
        self.db.commit()

        # Log action
        log_action(
            self.db,
            current_user,
            "meeting.update",
            f"Updated meeting '{meeting.title}' (ID: {meeting.id})",
            {
                "meeting_id": meeting.id,
                "updated_fields": list(update_data.dict(exclude_unset=True).keys()),
            },
        )

        return meeting

    def join_meeting(
        self, room_id: str, access_code: Optional[str], current_user: User
    ) -> dict[str, Any]:
        """Join meeting with validation"""

        meeting = self.get_meeting_by_room_id(room_id, current_user)

        # Check if meeting can be joined
        if not meeting.can_join:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Meeting cannot be joined at this time",
            )

        # Validate access code if required
        if meeting.access_code and meeting.access_code != access_code:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Invalid access code"
            )

        # Check if user is a participant
        participant = self.db.execute(
            meeting_participants.select().where(
                and_(
                    meeting_participants.c.meeting_id == meeting.id,
                    meeting_participants.c.user_id == current_user.id,
                )
            )
        ).first()

        if not participant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to join this meeting",
            )

        # Update participant status and join time
        self.db.execute(
            meeting_participants.update()
            .where(
                and_(
                    meeting_participants.c.meeting_id == meeting.id,
                    meeting_participants.c.user_id == current_user.id,
                )
            )
            .values(status=ParticipantStatus.JOINED, joined_at=datetime.utcnow())
        )

        # Update meeting status if first participant
        if meeting.status == MeetingStatus.SCHEDULED:
            meeting.status = MeetingStatus.STARTING
            meeting.actual_start = datetime.utcnow()

        self.db.commit()

        # Get TURN server configuration
        turn_servers = self._get_turn_servers()

        return {
            "success": True,
            "room_id": room_id,
            "participant_id": participant.id,
            "meeting": meeting,
            "turn_servers": turn_servers,
        }

    def leave_meeting(self, room_id: str, current_user: User) -> dict[str, Any]:
        """Leave meeting"""

        meeting = self.get_meeting_by_room_id(room_id, current_user)

        # Update participant status
        self.db.execute(
            meeting_participants.update()
            .where(
                and_(
                    meeting_participants.c.meeting_id == meeting.id,
                    meeting_participants.c.user_id == current_user.id,
                )
            )
            .values(status=ParticipantStatus.LEFT, left_at=datetime.utcnow())
        )

        # Check if all participants have left
        active_participants = self.db.execute(
            meeting_participants.select().where(
                and_(
                    meeting_participants.c.meeting_id == meeting.id,
                    meeting_participants.c.status == ParticipantStatus.JOINED,
                )
            )
        ).fetchall()

        # End meeting if no active participants
        if not active_participants and meeting.status == MeetingStatus.IN_PROGRESS:
            meeting.status = MeetingStatus.COMPLETED
            meeting.actual_end = datetime.utcnow()

        self.db.commit()

        return {"success": True}

    def _validate_and_get_participants(
        self,
        participants: list[MeetingParticipantCreate],
        meeting_type: MeetingType,
        current_user: User,
        interview: Optional[Interview] = None,
    ) -> list[User]:
        """Validate participants based on meeting type and RBAC rules"""

        participant_users = []
        user_roles = {}

        # Get all participant users
        for participant_data in participants:
            user = self.db.query(User).filter_by(id=participant_data.user_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User {participant_data.user_id} not found",
                )

            # Validate company access
            if not check_company_access(current_user, user.company_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied: insufficient company permissions for user {participant_data.user_id}",
                )

            participant_users.append(user)
            user_roles[user.id] = self._get_user_primary_role(user)

        # Validate meeting type rules
        if meeting_type == MeetingType.CASUAL:
            self._validate_casual_meeting_participants(
                participant_users, user_roles, interview
            )
        elif meeting_type == MeetingType.MAIN:
            self._validate_main_meeting_participants(
                participant_users, user_roles, interview
            )

        return participant_users

    def _validate_casual_meeting_participants(
        self,
        users: list[User],
        user_roles: dict[int, str],
        interview: Optional[Interview],
    ):
        """Validate casual meeting: Candidate ↔ Recruiter only"""

        if len(users) != 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Casual meetings must have exactly 2 participants",
            )

        roles = set(user_roles.values())

        if not (roles == {"candidate", "recruiter"}):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Casual meetings must have one candidate and one recruiter",
            )

        # If linked to interview, validate participants match
        if interview:
            participant_ids = {user.id for user in users}
            expected_ids = {interview.candidate_id, interview.recruiter_id}

            if participant_ids != expected_ids:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Meeting participants must match interview participants",
                )

    def _validate_main_meeting_participants(
        self,
        users: list[User],
        user_roles: dict[int, str],
        interview: Optional[Interview],
    ):
        """Validate main meeting: Candidate ↔ Employer (+ optional recruiter observer)"""

        if len(users) < 2 or len(users) > 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Main meetings must have 2-5 participants",
            )

        roles = list(user_roles.values())

        # Must have candidate and at least one employer
        if "candidate" not in roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Main meetings must include the candidate",
            )

        if "employer" not in roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Main meetings must include at least one employer",
            )

        # Validate against interview if provided
        if interview:
            candidate_ids = [u.id for u in users if user_roles[u.id] == "candidate"]
            if len(candidate_ids) != 1 or candidate_ids[0] != interview.candidate_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Meeting candidate must match interview candidate",
                )

    def _can_access_interview(self, user: User, interview: Interview) -> bool:
        """Check if user can access the interview"""
        user_role = self._get_user_primary_role(user)

        if user_role == "super_admin":
            return True
        elif user_role == "company_admin":
            return interview.recruiter_company_id == user.company_id
        elif user_role == "recruiter":
            return interview.recruiter_id == user.id
        elif user_role == "employer":
            return interview.employer_company_id == user.company_id
        elif user_role == "candidate":
            return interview.candidate_id == user.id

        return False

    def _can_access_meeting(self, user: User, meeting: Meeting) -> bool:
        """Check if user can access the meeting"""
        user_role = self._get_user_primary_role(user)

        # Super admin and company admin can access all meetings in their scope
        if user_role == "super_admin":
            return True
        elif user_role == "company_admin":
            return meeting.company_id == user.company_id

        # Check if user is a participant
        participant = self.db.execute(
            meeting_participants.select().where(
                and_(
                    meeting_participants.c.meeting_id == meeting.id,
                    meeting_participants.c.user_id == user.id,
                )
            )
        ).first()

        return participant is not None

    def _can_modify_meeting(self, user: User, meeting: Meeting) -> bool:
        """Check if user can modify the meeting"""
        user_role = self._get_user_primary_role(user)

        # Super admin and company admin can modify meetings
        if user_role in ["super_admin", "company_admin"]:
            return meeting.company_id == user.company_id

        # Meeting creator can modify
        if meeting.created_by == user.id:
            return True

        # Host participants can modify
        participant = self.db.execute(
            meeting_participants.select().where(
                and_(
                    meeting_participants.c.meeting_id == meeting.id,
                    meeting_participants.c.user_id == user.id,
                    meeting_participants.c.role == ParticipantRole.HOST,
                )
            )
        ).first()

        return participant is not None

    def _get_user_primary_role(self, user: User) -> str:
        """Get user's primary role for RBAC validation"""
        # This should be enhanced to properly determine user's primary role
        # For now, simple logic based on user properties
        if user.is_admin:
            return "company_admin" if user.company_id else "super_admin"

        # Check user roles (simplified)
        for user_role in user.user_roles:
            role_name = user_role.role.name.lower()
            if role_name in ["candidate", "recruiter", "employer"]:
                return role_name

        return "user"

    def _generate_room_id(self) -> str:
        """Generate unique room ID"""
        while True:
            room_id = f"room_{secrets.token_urlsafe(16)}"
            existing = self.db.query(Meeting).filter_by(room_id=room_id).first()
            if not existing:
                return room_id

    def _get_turn_servers(self) -> list[dict[str, Any]]:
        """Get TURN server configuration"""
        # This should come from environment configuration
        return [
            {"urls": "turn:localhost:3478", "username": "user", "credential": "pass"}
        ]
