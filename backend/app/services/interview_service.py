import logging
from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import and_, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.models.calendar_integration import ExternalCalendarAccount, SyncedEvent
from app.models.company import Company
from app.models.interview import Interview, InterviewProposal
from app.models.role import Role
from app.models.role import UserRole as UserRoleModel
from app.models.user import User
from app.services.calendar_service import google_calendar_service
from app.services.microsoft_calendar_service import microsoft_calendar_service
from app.utils.constants import InterviewStatus, UserRole
from app.utils.permissions import is_company_admin, is_super_admin

logger = logging.getLogger(__name__)


class InterviewService:
    """Service for managing interviews and scheduling proposals."""

    async def create_interview(
        self,
        db: AsyncSession,
        candidate_id: int,
        recruiter_id: int,
        employer_company_id: int,
        title: str,
        description: str | None = None,
        position_title: str | None = None,
        interview_type: str = "video",
        created_by: int | None = None,
        status: str | None = None,
        scheduled_start: datetime | None = None,
        scheduled_end: datetime | None = None,
        timezone: str | None = "UTC",
        location: str | None = None,
        meeting_url: str | None = None,
        video_call_type: str | None = None,
        notes: str | None = None,
    ) -> Interview:
        """Create a new interview."""
        # Validate participants exist and have correct roles
        await self._validate_interview_participants(
            db, candidate_id, recruiter_id, employer_company_id
        )

        # Get recruiter's company
        recruiter_result = await db.execute(
            select(User)
            .options(selectinload(User.company))
            .where(User.id == recruiter_id)
        )
        recruiter = recruiter_result.scalar_one()
        recruiter_company_id = recruiter.company_id

        interview_status = status or InterviewStatus.PENDING_SCHEDULE.value

        # Handle automatic meeting URL generation for video interviews
        final_meeting_url = meeting_url
        if interview_type == "video" and video_call_type == "system_generated":
            # We'll generate the URL after creating the interview to get the ID
            final_meeting_url = None

        # Create interview
        interview = Interview(
            candidate_id=candidate_id,
            recruiter_id=recruiter_id,
            employer_company_id=employer_company_id,
            recruiter_company_id=recruiter_company_id,
            title=title,
            description=description,
            position_title=position_title,
            interview_type=interview_type,
            status=interview_status,
            created_by=created_by,
            scheduled_start=scheduled_start,
            scheduled_end=scheduled_end,
            timezone=timezone or "UTC",
            location=location,
            meeting_url=final_meeting_url,
            video_call_type=video_call_type,
            notes=notes,
        )

        db.add(interview)
        await db.commit()
        await db.refresh(interview)

        # Generate system meeting URL if needed
        if interview_type == "video" and video_call_type == "system_generated":
            # Get the base URL from settings or use localhost for development
            base_url = getattr(settings, "BASE_URL", "http://localhost:3000")
            system_meeting_url = f"{base_url}/video-call/{interview.id}"

            # Update the interview with the generated URL
            interview.meeting_url = system_meeting_url
            await db.commit()
            await db.refresh(interview)

        return interview

    async def create_proposal(
        self,
        db: AsyncSession,
        interview_id: int,
        proposed_by: int,
        start_datetime: datetime,
        end_datetime: datetime,
        timezone: str = "UTC",
        location: str | None = None,
        notes: str | None = None,
    ) -> InterviewProposal:
        """Create a new interview time proposal."""
        # Get interview with participants
        interview_result = await db.execute(
            select(Interview)
            .options(
                selectinload(Interview.candidate),
                selectinload(Interview.recruiter),
                selectinload(Interview.employer_company),
            )
            .where(Interview.id == interview_id)
        )

        interview = interview_result.scalar_one_or_none()
        if not interview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found"
            )

        # Determine proposer role
        proposer_role = await self._get_proposer_role(db, proposed_by, interview)

        # Validate proposal permissions
        await self._validate_proposal_permissions(
            proposer_role, interview.status, proposed_by, interview
        )

        # Check for time conflicts
        await self._check_time_conflicts(
            db, interview, start_datetime, end_datetime, proposed_by
        )

        # Create proposal
        proposal = InterviewProposal(
            interview_id=interview_id,
            proposed_by=proposed_by,
            proposer_role=proposer_role,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            timezone=timezone,
            location=location,
            notes=notes,
            expires_at=datetime.utcnow() + timedelta(days=7),  # 7-day expiration
        )

        db.add(proposal)
        await db.commit()
        await db.refresh(proposal)

        # Send notifications
        await self._send_proposal_notifications(db, proposal, interview)

        logger.info(
            f"Created proposal {proposal.id} for interview {interview_id} by user {proposed_by}"
        )

        return proposal

    async def respond_to_proposal(
        self,
        db: AsyncSession,
        proposal_id: int,
        response: str,  # "accepted" or "declined"
        responded_by: int,
        response_notes: str | None = None,
    ) -> InterviewProposal:
        """Respond to an interview proposal."""
        # Get proposal with interview
        proposal_result = await db.execute(
            select(InterviewProposal)
            .options(
                selectinload(InterviewProposal.interview).selectinload(
                    Interview.candidate
                ),
                selectinload(InterviewProposal.interview).selectinload(
                    Interview.recruiter
                ),
                selectinload(InterviewProposal.interview).selectinload(
                    Interview.employer_company
                ),
            )
            .where(InterviewProposal.id == proposal_id)
        )

        proposal = proposal_result.scalar_one_or_none()
        if not proposal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Proposal not found"
            )

        # Validate response permissions
        await self._validate_response_permissions(db, responded_by, proposal)

        # Update proposal
        proposal.status = response
        proposal.responded_by = responded_by
        proposal.responded_at = datetime.utcnow()
        proposal.response_notes = response_notes

        # If accepted, update interview and create calendar events
        if response == "accepted":
            await self._accept_proposal(db, proposal)

        await db.commit()

        # Send notifications
        await self._send_response_notifications(db, proposal)

        logger.info(f"Proposal {proposal_id} {response} by user {responded_by}")

        return proposal

    async def cancel_interview(
        self,
        db: AsyncSession,
        interview_id: int,
        cancelled_by: int,
        reason: str | None = None,
    ) -> Interview:
        """Cancel an interview."""
        interview_result = await db.execute(
            select(Interview)
            .options(
                selectinload(Interview.candidate),
                selectinload(Interview.recruiter),
                selectinload(Interview.synced_events),
            )
            .where(Interview.id == interview_id)
        )

        interview = interview_result.scalar_one_or_none()
        if not interview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found"
            )

        # Validate cancellation permissions
        await self._validate_cancellation_permissions(db, cancelled_by, interview)

        # Update interview status
        interview.status = InterviewStatus.CANCELLED.value
        interview.cancelled_by = cancelled_by
        interview.cancelled_at = datetime.utcnow()
        interview.cancellation_reason = reason

        # Cancel calendar events
        await self._cancel_calendar_events(db, interview)

        await db.commit()

        # Send notifications
        await self._send_cancellation_notifications(db, interview, reason)

        logger.info(f"Interview {interview_id} cancelled by user {cancelled_by}")

        return interview

    async def reschedule_interview(
        self,
        db: AsyncSession,
        interview_id: int,
        new_start: datetime,
        new_end: datetime,
        rescheduled_by: int,
        reason: str | None = None,
    ) -> Interview:
        """Reschedule an interview."""
        interview_result = await db.execute(
            select(Interview)
            .options(
                selectinload(Interview.candidate),
                selectinload(Interview.recruiter),
                selectinload(Interview.synced_events),
            )
            .where(Interview.id == interview_id)
        )

        interview = interview_result.scalar_one_or_none()
        if not interview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found"
            )

        # Validate reschedule permissions
        await self._validate_reschedule_permissions(db, rescheduled_by, interview)

        # Check for conflicts
        await self._check_time_conflicts(
            db, interview, new_start, new_end, rescheduled_by
        )

        # Update interview timing
        old_start = interview.scheduled_start
        interview.scheduled_start = new_start
        interview.scheduled_end = new_end

        # Update calendar events
        await self._update_calendar_events(db, interview, reason)

        await db.commit()

        # Send notifications
        await self._send_reschedule_notifications(db, interview, old_start, reason)

        logger.info(f"Interview {interview_id} rescheduled by user {rescheduled_by}")

        return interview

    async def get_user_interviews(
        self,
        db: AsyncSession,
        user_id: int,
        status_filter: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Interview]:
        """Get interviews for a user."""
        query = (
            select(Interview)
            .options(
                selectinload(Interview.candidate),
                selectinload(Interview.recruiter),
                selectinload(Interview.employer_company),
                selectinload(Interview.proposals).selectinload(
                    InterviewProposal.proposer
                ),
            )
            .where(
                or_(
                    Interview.candidate_id == user_id,
                    Interview.recruiter_id == user_id,
                    Interview.created_by == user_id,
                )
            )
        )

        # Apply filters
        if status_filter:
            query = query.where(Interview.status == status_filter)

        if start_date:
            query = query.where(Interview.scheduled_start >= start_date)

        if end_date:
            query = query.where(Interview.scheduled_start <= end_date)

        # Order and paginate
        query = (
            query.order_by(Interview.scheduled_start.desc()).offset(offset).limit(limit)
        )

        result = await db.execute(query)
        return result.scalars().all()

    # Private helper methods

    async def _validate_interview_participants(
        self,
        db: AsyncSession,
        candidate_id: int,
        recruiter_id: int,
        employer_company_id: int,
    ):
        """Validate that interview participants have correct roles."""
        # Get users
        users_result = await db.execute(
            select(User).where(User.id.in_([candidate_id, recruiter_id]))
        )
        users = {user.id: user for user in users_result.scalars().all()}

        # Get user roles with role names - use explicit join since relationship loading isn't working
        user_roles_result = await db.execute(
            select(UserRoleModel, Role)
            .join(Role, UserRoleModel.role_id == Role.id)
            .where(UserRoleModel.user_id.in_([candidate_id, recruiter_id]))
        )

        # Build user -> roles mapping
        user_role_names = {}
        for user_role, role in user_roles_result:
            if user_role.user_id not in user_role_names:
                user_role_names[user_role.user_id] = []
            user_role_names[user_role.user_id].append(role.name)

        # Validate candidate
        candidate = users.get(candidate_id)
        if not candidate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found"
            )

        candidate_roles = user_role_names.get(candidate_id, [])
        if UserRole.CANDIDATE.value not in candidate_roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Specified user is not a candidate. Roles found: {candidate_roles}, Expected: {UserRole.CANDIDATE.value}",
            )

        # Validate recruiter
        recruiter = users.get(recruiter_id)
        if not recruiter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Recruiter not found"
            )

        recruiter_roles = user_role_names.get(recruiter_id, [])
        if not (
            UserRole.MEMBER.value in recruiter_roles
            or UserRole.ADMIN.value in recruiter_roles
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Specified user is not a recruiter or company admin. Roles found: {recruiter_roles}",
            )

        # Validate employer company exists
        company_result = await db.execute(
            select(Company).where(Company.id == employer_company_id)
        )
        employer_company = company_result.scalar_one_or_none()
        if not employer_company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employer company not found",
            )

    async def _get_proposer_role(
        self, db: AsyncSession, user_id: int, interview: Interview
    ) -> str:
        """Get the role of the user making the proposal."""
        if user_id == interview.candidate_id:
            return "candidate"
        elif user_id == interview.recruiter_id:
            return "recruiter"
        else:
            # Check if user is from employer company
            user_result = await db.execute(select(User).where(User.id == user_id))
            user = user_result.scalar_one_or_none()

            if user and user.company_id == interview.employer_company_id:
                return "employer"

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not authorized to create proposals for this interview",
        )

    async def _validate_proposal_permissions(
        self,
        proposer_role: str,
        interview_status: str,
        proposed_by: int,
        interview: Interview,
    ):
        """Validate that user can create proposals."""
        if interview_status not in [
            InterviewStatus.PENDING_SCHEDULE.value,
            InterviewStatus.SCHEDULED.value,
        ]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot create proposals for interview in {interview_status} status",
            )

    async def _check_time_conflicts(
        self,
        db: AsyncSession,
        interview: Interview,
        start_time: datetime,
        end_time: datetime,
        user_id: int,
    ):
        """Check for scheduling conflicts."""
        # Check for overlapping interviews for all participants
        participant_ids = [interview.candidate_id, interview.recruiter_id]

        # Get employer users from company (simplified - could be more specific)
        employer_users = await db.execute(
            select(User.id).where(User.company_id == interview.employer_company_id)
        )
        employer_user_ids = [uid for (uid,) in employer_users.all()]
        participant_ids.extend(employer_user_ids[:5])  # Limit to avoid huge queries

        # Check for conflicts
        conflicts = await db.execute(
            select(Interview).where(
                Interview.id != interview.id,
                Interview.status.in_(
                    [InterviewStatus.CONFIRMED.value, InterviewStatus.IN_PROGRESS.value]
                ),
                or_(
                    Interview.candidate_id.in_(participant_ids),
                    Interview.recruiter_id.in_(participant_ids),
                ),
                and_(
                    Interview.scheduled_start < end_time,
                    Interview.scheduled_end > start_time,
                ),
            )
        )

        conflicting_interviews = conflicts.scalars().all()
        if conflicting_interviews:
            logger.warning(
                f"Time conflict detected for proposal: {len(conflicting_interviews)} conflicts"
            )
            # Note: In a real system, you might want to return conflicts as warnings rather than blocking

    async def _accept_proposal(self, db: AsyncSession, proposal: InterviewProposal):
        """Accept a proposal and update interview."""
        interview = proposal.interview

        # Update interview with proposed time
        interview.scheduled_start = proposal.start_datetime
        interview.scheduled_end = proposal.end_datetime
        interview.timezone = proposal.timezone
        interview.location = proposal.location
        interview.status = InterviewStatus.CONFIRMED.value
        interview.confirmed_by = proposal.responded_by
        interview.confirmed_at = datetime.utcnow()

        # Create calendar events for participants
        await self._create_calendar_events(db, interview)

        # Decline other pending proposals
        await db.execute(
            update(InterviewProposal)
            .where(
                InterviewProposal.interview_id == interview.id,
                InterviewProposal.id != proposal.id,
                InterviewProposal.status == "pending",
            )
            .values(
                status="declined",
                response_notes="Automatically declined - another proposal accepted",
            )
        )

    async def _create_calendar_events(self, db: AsyncSession, interview: Interview):
        """Create calendar events for interview participants."""
        participants = [interview.candidate, interview.recruiter]

        # Filter out None participants (in case relationships aren't loaded)
        participants = [p for p in participants if p is not None]

        for participant in participants:
            # Get participant's calendar accounts
            calendar_accounts = await db.execute(
                select(ExternalCalendarAccount).where(
                    ExternalCalendarAccount.user_id == participant.id,
                    ExternalCalendarAccount.is_active is True,
                    ExternalCalendarAccount.sync_enabled is True,
                )
            )

            for account in calendar_accounts.scalars().all():
                try:
                    await self._create_calendar_event_for_account(
                        db, interview, account
                    )
                except Exception as e:
                    logger.error(
                        f"Failed to create calendar event for user {participant.id}: {e}"
                    )

    async def _create_calendar_event_for_account(
        self,
        db: AsyncSession,
        interview: Interview,
        calendar_account: ExternalCalendarAccount,
    ):
        """Create calendar event for specific calendar account."""
        # Prepare event data
        event_data = {
            "summary": interview.title,
            "description": f"Interview: {interview.description or interview.title}\n\nPosition: {interview.position_title or 'N/A'}",
            "location": interview.location or interview.meeting_url,
            "start": {
                "dateTime": interview.scheduled_start.isoformat(),
                "timeZone": interview.timezone or "UTC",
            },
            "end": {
                "dateTime": interview.scheduled_end.isoformat(),
                "timeZone": interview.timezone or "UTC",
            },
        }

        # Add attendees
        attendees = []
        if interview.candidate.email:
            attendees.append({"email": interview.candidate.email})
        if interview.recruiter.email:
            attendees.append({"email": interview.recruiter.email})

        if calendar_account.provider == "google":
            event_data["attendees"] = attendees
            created_event = await google_calendar_service.create_event(
                calendar_account, event_data
            )
        elif calendar_account.provider == "microsoft":
            # Microsoft Graph format
            event_data["attendees"] = [
                {"emailAddress": {"address": email["email"], "name": email["email"]}}
                for email in attendees
            ]
            created_event = await microsoft_calendar_service.create_event(
                calendar_account, event_data
            )
        else:
            logger.warning(f"Unknown calendar provider: {calendar_account.provider}")
            return

        # Store synced event
        synced_event = SyncedEvent(
            calendar_account_id=calendar_account.id,
            external_event_id=created_event["id"],
            external_calendar_id=calendar_account.calendar_id or "primary",
            title=interview.title,
            description=interview.description,
            location=interview.location,
            start_datetime=interview.scheduled_start,
            end_datetime=interview.scheduled_end,
            timezone=interview.timezone,
            interview_id=interview.id,
            organizer_email=calendar_account.email,
            attendees=[att["email"] for att in attendees],
        )

        db.add(synced_event)

    async def _validate_response_permissions(
        self, db: AsyncSession, user_id: int, proposal: InterviewProposal
    ):
        """Validate user can respond to proposal."""
        interview = proposal.interview
        proposer_role = proposal.proposer_role

        # Determine who can respond based on proposer role
        allowed_responders = []

        if proposer_role == "candidate":
            # Candidate proposed, recruiter or employer can respond
            allowed_responders = [interview.recruiter_id]
            # Add employer users (simplified)
            employer_users = await db.execute(
                select(User.id).where(User.company_id == interview.employer_company_id)
            )
            allowed_responders.extend([uid for (uid,) in employer_users.all()])

        elif proposer_role == "employer":
            # Employer proposed, candidate or recruiter can respond
            allowed_responders = [interview.candidate_id, interview.recruiter_id]

        elif proposer_role == "recruiter":
            # Recruiter proposed, candidate or employer can respond
            allowed_responders = [interview.candidate_id]
            employer_users = await db.execute(
                select(User.id).where(User.company_id == interview.employer_company_id)
            )
            allowed_responders.extend([uid for (uid,) in employer_users.all()])

        if user_id not in allowed_responders:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to respond to this proposal",
            )

    async def _validate_cancellation_permissions(
        self, db: AsyncSession, user_id: int, interview: Interview
    ):
        """Validate user can cancel interview."""
        # Allow participants or admins to cancel
        allowed_users = [interview.candidate_id, interview.recruiter_id]

        # Add employer users
        employer_users = await db.execute(
            select(User.id).where(User.company_id == interview.employer_company_id)
        )
        allowed_users.extend([uid for (uid,) in employer_users.all()])

        # Check if user is admin
        user_result = await db.execute(
            select(User)
            .options(selectinload(User.user_roles).selectinload(UserRoleModel.role))
            .where(User.id == user_id)
        )
        user = user_result.scalar_one_or_none()

        if user and (is_super_admin(user) or is_company_admin(user)):
            return  # Admins can cancel any interview

        if user_id not in allowed_users:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to cancel this interview",
            )

    async def _validate_reschedule_permissions(
        self, db: AsyncSession, user_id: int, interview: Interview
    ):
        """Validate user can reschedule interview."""
        # Same as cancellation permissions
        await self._validate_cancellation_permissions(db, user_id, interview)

    async def _send_proposal_notifications(
        self, db: AsyncSession, proposal: InterviewProposal, interview: Interview
    ):
        """Send notifications about new proposal."""
        # Implementation would create notifications and send emails

    async def _send_response_notifications(
        self, db: AsyncSession, proposal: InterviewProposal
    ):
        """Send notifications about proposal response."""
        # Implementation would create notifications and send emails

    async def _send_cancellation_notifications(
        self, db: AsyncSession, interview: Interview, reason: str | None
    ):
        """Send notifications about interview cancellation."""
        # Implementation would create notifications and send emails

    async def _send_reschedule_notifications(
        self,
        db: AsyncSession,
        interview: Interview,
        old_start: datetime,
        reason: str | None,
    ):
        """Send notifications about interview reschedule."""
        # Implementation would create notifications and send emails

    async def _cancel_calendar_events(self, db: AsyncSession, interview: Interview):
        """Cancel calendar events for interview."""
        for synced_event in interview.synced_events:
            try:
                calendar_account = synced_event.calendar_account

                if calendar_account.provider == "google":
                    await google_calendar_service.delete_event(
                        calendar_account,
                        synced_event.external_event_id,
                        synced_event.external_calendar_id,
                    )
                elif calendar_account.provider == "microsoft":
                    await microsoft_calendar_service.delete_event(
                        calendar_account,
                        synced_event.external_event_id,
                        synced_event.external_calendar_id,
                    )

            except Exception as e:
                logger.error(f"Failed to cancel calendar event {synced_event.id}: {e}")

    async def _update_calendar_events(
        self, db: AsyncSession, interview: Interview, reason: str | None
    ):
        """Update calendar events for rescheduled interview."""
        for synced_event in interview.synced_events:
            try:
                calendar_account = synced_event.calendar_account

                # Prepare updated event data
                event_data = {
                    "summary": interview.title,
                    "description": f"Interview: {interview.description or interview.title}\n\nRescheduled. Reason: {reason or 'N/A'}",
                    "location": interview.location or interview.meeting_url,
                    "start": {
                        "dateTime": interview.scheduled_start.isoformat(),
                        "timeZone": interview.timezone or "UTC",
                    },
                    "end": {
                        "dateTime": interview.scheduled_end.isoformat(),
                        "timeZone": interview.timezone or "UTC",
                    },
                }

                if calendar_account.provider == "google":
                    await google_calendar_service.update_event(
                        calendar_account,
                        synced_event.external_event_id,
                        event_data,
                        synced_event.external_calendar_id,
                    )
                elif calendar_account.provider == "microsoft":
                    await microsoft_calendar_service.update_event(
                        calendar_account,
                        synced_event.external_event_id,
                        event_data,
                        synced_event.external_calendar_id,
                    )

                # Update synced event record
                synced_event.start_datetime = interview.scheduled_start
                synced_event.end_datetime = interview.scheduled_end
                synced_event.description = event_data["description"]

            except Exception as e:
                logger.error(f"Failed to update calendar event {synced_event.id}: {e}")


# Global instance
interview_service = InterviewService()
