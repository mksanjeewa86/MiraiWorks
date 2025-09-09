import logging
from typing import Any, Optional

from fastapi import HTTPException, status
from sqlalchemy import desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.message import (
    Conversation,
    Message,
    MessageRead,
    conversation_participants,
)
from app.models.role import UserRole as UserRoleModel
from app.models.user import User
from app.utils.constants import MessageType, UserRole

logger = logging.getLogger(__name__)


class MessagingRulesService:
    """Service to enforce messaging business rules."""

    async def can_communicate(
        self, db: AsyncSession, user1_id: int, user2_id: int
    ) -> tuple[bool, str]:
        """
        Check if two users can communicate based on business rules:
        - Candidate ↔ Recruiter: allowed
        - Employer ↔ Recruiter: allowed
        - Candidate ↔ Employer: NOT allowed (must go through Recruiter)
        """
        # Get both users with their roles and companies
        result = await db.execute(
            select(User)
            .options(
                selectinload(User.user_roles).selectinload(UserRoleModel.role),
                selectinload(User.company),
            )
            .where(User.id.in_([user1_id, user2_id]))
        )
        users = result.scalars().all()

        if len(users) != 2:
            return False, "One or both users not found"

        user1, user2 = users[0], users[1]
        if user1.id == user2_id:
            user1, user2 = user2, user1

        # Get user roles
        user1_roles = [ur.role.name for ur in user1.user_roles]
        user2_roles = [ur.role.name for ur in user2.user_roles]

        # Check if users are active
        if not user1.is_active or not user2.is_active:
            return False, "One or both users are inactive"

        # Super admin can only communicate with company admins
        if UserRole.SUPER_ADMIN.value in user1_roles:
            if UserRole.COMPANY_ADMIN.value in user2_roles:
                return True, "Super admin can communicate with company admin"
            else:
                return False, "Super admin can only communicate with company admins"
        elif UserRole.SUPER_ADMIN.value in user2_roles:
            if UserRole.COMPANY_ADMIN.value in user1_roles:
                return True, "Super admin can communicate with company admin"
            else:
                return False, "Super admin can only communicate with company admins"

        # Company admins cannot communicate with each other - only with super admin
        if (UserRole.COMPANY_ADMIN.value in user1_roles and 
            UserRole.COMPANY_ADMIN.value in user2_roles):
            return False, "Company admins cannot communicate with each other"

        # Company admins can only communicate with super admin, not other users
        if UserRole.COMPANY_ADMIN.value in user1_roles:
            return False, "Company admins can only communicate with super admins"
        elif UserRole.COMPANY_ADMIN.value in user2_roles:
            return False, "Company admins can only communicate with super admins"

        # Determine primary roles (highest priority role)
        def get_primary_role(roles):
            role_priority = {
                UserRole.SUPER_ADMIN.value: 1,
                UserRole.COMPANY_ADMIN.value: 2,
                UserRole.RECRUITER.value: 3,
                UserRole.EMPLOYER.value: 4,
                UserRole.CANDIDATE.value: 5,
            }
            return min(roles, key=lambda r: role_priority.get(r, 999))

        primary_role1 = get_primary_role(user1_roles)
        primary_role2 = get_primary_role(user2_roles)

        # Apply messaging rules
        allowed_combinations = {
            (UserRole.CANDIDATE.value, UserRole.RECRUITER.value),
            (UserRole.RECRUITER.value, UserRole.CANDIDATE.value),
            (UserRole.EMPLOYER.value, UserRole.RECRUITER.value),
            (UserRole.RECRUITER.value, UserRole.EMPLOYER.value),
            (
                UserRole.RECRUITER.value,
                UserRole.RECRUITER.value,
            ),  # Recruiters can talk to each other
        }

        # Check if combination is allowed
        if (primary_role1, primary_role2) in allowed_combinations:
            return True, f"Allowed communication: {primary_role1} ↔ {primary_role2}"

        # Specifically block Candidate ↔ Employer
        if (
            primary_role1 == UserRole.CANDIDATE.value
            and primary_role2 == UserRole.EMPLOYER.value
        ) or (
            primary_role1 == UserRole.EMPLOYER.value
            and primary_role2 == UserRole.CANDIDATE.value
        ):
            return (
                False,
                "Direct communication between Candidates and Employers is not allowed. Please communicate through a Recruiter.",
            )

        return (
            False,
            f"Communication not allowed between {primary_role1} and {primary_role2}",
        )

    async def can_access_conversation(
        self, db: AsyncSession, user_id: int, conversation_id: int
    ) -> tuple[bool, str]:
        """Check if user can access a conversation."""
        result = await db.execute(
            select(Conversation)
            .options(selectinload(Conversation.participants))
            .where(Conversation.id == conversation_id)
        )

        conversation = result.scalar_one_or_none()
        if not conversation:
            return False, "Conversation not found"

        # Check if user is a participant
        participant_ids = [p.id for p in conversation.participants]
        if user_id not in participant_ids:
            return False, "User is not a participant in this conversation"

        return True, "Access allowed"

    async def get_allowed_conversation_participants(
        self, db: AsyncSession, user_id: int
    ) -> list[dict[str, Any]]:
        """Get list of users the current user can start conversations with."""
        # Get current user
        result = await db.execute(
            select(User)
            .options(
                selectinload(User.user_roles).selectinload(UserRoleModel.role),
                selectinload(User.company),
            )
            .where(User.id == user_id)
        )

        current_user = result.scalar_one_or_none()
        if not current_user:
            return []

        current_roles = [ur.role.name for ur in current_user.user_roles]
        primary_role = self._get_primary_role(current_roles)

        # Get potential participants based on role
        potential_participants = []

        if primary_role == UserRole.SUPER_ADMIN.value:
            # Super admin can only talk to company admins
            from app.models.role import Role
            result = await db.execute(
                select(User)
                .options(selectinload(User.company))
                .where(
                    User.id != user_id,
                    User.is_active == True,
                    User.user_roles.any(
                        UserRoleModel.role.has(name=UserRole.COMPANY_ADMIN.value)
                    ),
                )
            )
            potential_participants = result.scalars().all()

        elif primary_role == UserRole.COMPANY_ADMIN.value:
            # Company admin can only communicate with super admins
            from app.models.role import Role
            result = await db.execute(
                select(User)
                .options(selectinload(User.company))
                .where(
                    User.id != user_id,
                    User.is_active == True,
                    User.user_roles.any(
                        UserRoleModel.role.has(name=UserRole.SUPER_ADMIN.value)
                    ),
                )
            )
            potential_participants = result.scalars().all()

        elif primary_role == UserRole.RECRUITER.value:
            # Recruiters can talk to candidates and employers
            result = await db.execute(
                select(User)
                .join(User.user_roles)
                .join("role")
                .options(selectinload(User.company))
                .where(
                    User.id != user_id,
                    User.is_active == True,
                    # Role name is either CANDIDATE or EMPLOYER or RECRUITER
                    or_(
                        User.user_roles.any(
                            role_id=select("roles").where(
                                UserRole.CANDIDATE.value == "name"
                            )
                        ),
                        User.user_roles.any(
                            role_id=select("roles").where(
                                UserRole.EMPLOYER.value == "name"
                            )
                        ),
                        User.user_roles.any(
                            role_id=select("roles").where(
                                UserRole.RECRUITER.value == "name"
                            )
                        ),
                    ),
                )
            )
            potential_participants = result.scalars().all()

        elif primary_role == UserRole.EMPLOYER.value:
            # Employers can only talk to recruiters
            result = await db.execute(
                select(User)
                .join(User.user_roles)
                .join("role")
                .options(selectinload(User.company))
                .where(
                    User.id != user_id,
                    User.is_active == True,
                    User.user_roles.any(
                        role_id=select("roles").where(
                            UserRole.RECRUITER.value == "name"
                        )
                    ),
                )
            )
            potential_participants = result.scalars().all()

        elif primary_role == UserRole.CANDIDATE.value:
            # Candidates can only talk to recruiters
            result = await db.execute(
                select(User)
                .join(User.user_roles)
                .join("role")
                .options(selectinload(User.company))
                .where(
                    User.id != user_id,
                    User.is_active == True,
                    User.user_roles.any(
                        role_id=select("roles").where(
                            UserRole.RECRUITER.value == "name"
                        )
                    ),
                )
            )
            potential_participants = result.scalars().all()

        # Convert to response format
        participants_data = []
        for user in potential_participants:
            # Verify communication is allowed
            can_comm, _ = await self.can_communicate(db, user_id, user.id)
            if can_comm:
                participants_data.append(
                    {
                        "id": user.id,
                        "email": user.email,
                        "full_name": user.full_name,
                        "company_name": user.company.name if user.company else None,
                        "is_online": False,  # TODO: Implement online status
                    }
                )

        return participants_data

    def _get_primary_role(self, roles: list[str]) -> str:
        """Get primary role from list of roles."""
        role_priority = {
            UserRole.SUPER_ADMIN.value: 1,
            UserRole.COMPANY_ADMIN.value: 2,
            UserRole.RECRUITER.value: 3,
            UserRole.EMPLOYER.value: 4,
            UserRole.CANDIDATE.value: 5,
        }
        return min(roles, key=lambda r: role_priority.get(r, 999))


class MessagingService:
    """Main messaging service."""

    def __init__(self):
        self.rules_service = MessagingRulesService()

    async def find_or_create_conversation(
        self,
        db: AsyncSession,
        participant_ids: list[int],
        title: Optional[str] = None,
    ) -> Conversation:
        """Find existing conversation or create new one between participants."""
        if len(participant_ids) == 2:
            existing_conv = await self._find_existing_direct_conversation(
                db, participant_ids
            )
            if existing_conv:
                return existing_conv
        
        # Create new conversation - use first participant as creator
        return await self.create_conversation(
            db, participant_ids[0], participant_ids[1:], title
        )

    async def create_conversation(
        self,
        db: AsyncSession,
        current_user_id: int,
        participant_ids: list[int],
        title: Optional[str] = None,
    ) -> Conversation:
        """Create a new conversation."""
        # Validate all participants can communicate
        all_participants = [current_user_id] + [
            pid for pid in participant_ids if pid != current_user_id
        ]

        # For direct conversations (2 participants), check if they can communicate
        if len(all_participants) == 2:
            can_comm, reason = await self.rules_service.can_communicate(
                db, all_participants[0], all_participants[1]
            )
            if not can_comm:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail=reason
                )

        # Check if conversation already exists between these participants
        if len(all_participants) == 2:
            existing_conv = await self._find_existing_direct_conversation(
                db, all_participants
            )
            if existing_conv:
                return existing_conv

        # Create conversation
        conversation = Conversation(
            title=title,
            type="direct" if len(all_participants) == 2 else "group",
            created_by=current_user_id,
        )

        db.add(conversation)
        await db.flush()  # Get ID

        # Add participants
        for participant_id in all_participants:
            # Verify user exists
            user_result = await db.execute(
                select(User).where(User.id == participant_id)
            )
            user = user_result.scalar_one_or_none()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User {participant_id} not found",
                )

            conversation.participants.append(user)

        await db.commit()
        await db.refresh(conversation)

        return conversation

    async def _find_existing_direct_conversation(
        self, db: AsyncSession, participant_ids: list[int]
    ) -> Optional[Conversation]:
        """Find existing direct conversation between participants."""
        result = await db.execute(
            select(Conversation)
            .join(conversation_participants)
            .where(Conversation.type == "direct", Conversation.is_active == True)
            .group_by(Conversation.id)
            .having(
                func.count(conversation_participants.c.user_id) == len(participant_ids)
            )
        )

        conversations = result.scalars().all()

        # Check each conversation to see if it has exactly our participants
        for conv in conversations:
            conv_result = await db.execute(
                select(Conversation)
                .options(selectinload(Conversation.participants))
                .where(Conversation.id == conv.id)
            )
            conv_with_participants = conv_result.scalar_one()

            conv_participant_ids = {p.id for p in conv_with_participants.participants}
            if conv_participant_ids == set(participant_ids):
                return conv_with_participants

        return None

    async def send_message(
        self,
        db: AsyncSession,
        conversation_id: int,
        sender_id: int,
        content: str,
        message_type: MessageType = MessageType.TEXT,
        reply_to_id: Optional[int] = None,
    ) -> Message:
        """Send a message in a conversation."""
        # Check if user can access conversation
        can_access, reason = await self.rules_service.can_access_conversation(
            db, sender_id, conversation_id
        )
        if not can_access:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=reason)

        # Validate reply_to message if provided
        if reply_to_id:
            reply_result = await db.execute(
                select(Message).where(
                    Message.id == reply_to_id,
                    Message.conversation_id == conversation_id,
                    Message.is_deleted == False,
                )
            )
            reply_message = reply_result.scalar_one_or_none()
            if not reply_message:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Reply message not found",
                )

        # Create message
        message = Message(
            conversation_id=conversation_id,
            sender_id=sender_id,
            type=message_type.value,
            content=content,
            reply_to_id=reply_to_id,
        )

        db.add(message)

        # Update conversation timestamp
        await db.execute(select(Conversation).where(Conversation.id == conversation_id))

        await db.commit()
        await db.refresh(message)

        return message

    async def get_conversation_messages(
        self,
        db: AsyncSession,
        conversation_id: int,
        user_id: int,
        limit: int = 50,
        before_id: Optional[int] = None,
    ) -> list[Message]:
        """Get messages from a conversation with pagination."""
        # Check access
        can_access, reason = await self.rules_service.can_access_conversation(
            db, user_id, conversation_id
        )
        if not can_access:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=reason)

        query = (
            select(Message)
            .options(
                selectinload(Message.sender),
                selectinload(Message.attachments),
                selectinload(Message.reply_to).selectinload(Message.sender),
            )
            .where(
                Message.conversation_id == conversation_id, Message.is_deleted == False
            )
            .order_by(desc(Message.created_at))
            .limit(limit)
        )

        if before_id:
            query = query.where(Message.id < before_id)

        result = await db.execute(query)
        messages = result.scalars().all()

        return list(reversed(messages))  # Return in chronological order

    async def mark_messages_as_read(
        self,
        db: AsyncSession,
        conversation_id: int,
        user_id: int,
        up_to_message_id: int,
    ) -> int:
        """Mark messages as read up to a specific message."""
        # Check access
        can_access, reason = await self.rules_service.can_access_conversation(
            db, user_id, conversation_id
        )
        if not can_access:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=reason)

        # Get unread messages up to the specified message
        unread_messages = await db.execute(
            select(Message.id).where(
                Message.conversation_id == conversation_id,
                Message.id <= up_to_message_id,
                Message.sender_id != user_id,  # Don't mark own messages
                ~Message.message_reads.any(MessageRead.user_id == user_id),
            )
        )

        message_ids = unread_messages.scalars().all()

        # Create read records
        read_records = [
            MessageRead(message_id=msg_id, user_id=user_id) for msg_id in message_ids
        ]

        db.add_all(read_records)
        await db.commit()

        return len(read_records)


# Global instance
messaging_service = MessagingService()
