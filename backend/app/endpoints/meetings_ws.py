import asyncio
import json
import logging
from datetime import datetime
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.meeting import (
    Meeting,
    MeetingStatus,
    ParticipantStatus,
    meeting_participants,
)
from app.services.meeting_service import MeetingService
from app.utils.websocket_auth import get_user_from_websocket

logger = logging.getLogger(__name__)

router = APIRouter()


# Global connection manager for WebRTC signaling
class WebRTCConnectionManager:
    def __init__(self):
        self.active_connections: dict[
            str, dict[int, WebSocket]
        ] = {}  # room_id -> {user_id: websocket}
        self.user_rooms: dict[int, str] = {}  # user_id -> room_id

    async def connect(self, websocket: WebSocket, room_id: str, user_id: int):
        """Connect user to meeting room"""
        await websocket.accept()

        if room_id not in self.active_connections:
            self.active_connections[room_id] = {}

        self.active_connections[room_id][user_id] = websocket
        self.user_rooms[user_id] = room_id

        logger.info(f"User {user_id} connected to meeting room {room_id}")

        # Notify other participants about new user
        await self.broadcast_to_room(
            room_id,
            {
                "type": "user_joined",
                "data": {"user_id": user_id, "timestamp": str(datetime.utcnow())},
            },
            exclude_user=user_id,
        )

    def disconnect(self, user_id: int):
        """Disconnect user from their current room"""
        if user_id in self.user_rooms:
            room_id = self.user_rooms[user_id]

            if (
                room_id in self.active_connections
                and user_id in self.active_connections[room_id]
            ):
                del self.active_connections[room_id][user_id]

                # Clean up empty rooms
                if not self.active_connections[room_id]:
                    del self.active_connections[room_id]

            del self.user_rooms[user_id]

            logger.info(f"User {user_id} disconnected from meeting room {room_id}")

            # Notify other participants about user leaving
            asyncio.create_task(
                self.broadcast_to_room(
                    room_id,
                    {
                        "type": "user_left",
                        "data": {
                            "user_id": user_id,
                            "timestamp": str(datetime.utcnow()),
                        },
                    },
                    exclude_user=user_id,
                )
            )

    async def send_to_user(self, user_id: int, message: dict):
        """Send message to specific user"""
        if user_id in self.user_rooms:
            room_id = self.user_rooms[user_id]
            if (
                room_id in self.active_connections
                and user_id in self.active_connections[room_id]
            ):
                try:
                    await self.active_connections[room_id][user_id].send_text(
                        json.dumps(message)
                    )
                except Exception as e:
                    logger.error(f"Error sending message to user {user_id}: {e}")
                    self.disconnect(user_id)

    async def send_to_room_user(self, room_id: str, target_user_id: int, message: dict):
        """Send message to specific user in a room"""
        if (
            room_id in self.active_connections
            and target_user_id in self.active_connections[room_id]
        ):
            try:
                await self.active_connections[room_id][target_user_id].send_text(
                    json.dumps(message)
                )
            except Exception as e:
                logger.error(
                    f"Error sending message to user {target_user_id} in room {room_id}: {e}"
                )
                self.disconnect(target_user_id)

    async def broadcast_to_room(
        self, room_id: str, message: dict, exclude_user: Optional[int] = None
    ):
        """Broadcast message to all users in a room"""
        if room_id not in self.active_connections:
            return

        disconnected_users = []

        for user_id, websocket in self.active_connections[room_id].items():
            if exclude_user and user_id == exclude_user:
                continue

            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(
                    f"Error broadcasting to user {user_id} in room {room_id}: {e}"
                )
                disconnected_users.append(user_id)

        # Clean up disconnected users
        for user_id in disconnected_users:
            self.disconnect(user_id)

    def get_room_participants(self, room_id: str) -> set[int]:
        """Get list of user IDs in a room"""
        if room_id in self.active_connections:
            return set(self.active_connections[room_id].keys())
        return set()


# Global connection manager instance
webrtc_manager = WebRTCConnectionManager()


@router.websocket("/ws/meetings/{room_id}")
async def websocket_meeting_endpoint(
    websocket: WebSocket, room_id: str, db: Session = Depends(get_db)
):
    """WebSocket endpoint for WebRTC signaling in meetings"""

    user = None
    user_id = None

    try:
        # Authenticate user from WebSocket
        user = await get_user_from_websocket(websocket, db)
        user_id = user.id

        # Validate meeting access
        meeting_service = MeetingService(db)
        meeting = meeting_service.get_meeting_by_room_id(room_id, user)

        # Check if meeting can be joined
        if not meeting.can_join:
            await websocket.close(
                code=status.WS_1008_POLICY_VIOLATION, reason="Meeting cannot be joined"
            )
            return

        # Connect user to room
        await webrtc_manager.connect(websocket, room_id, user_id)

        # Update participant status to joined
        db.execute(
            meeting_participants.update()
            .where(
                and_(
                    meeting_participants.c.meeting_id == meeting.id,
                    meeting_participants.c.user_id == user_id,
                )
            )
            .values(status=ParticipantStatus.JOINED, joined_at=datetime.utcnow())
        )

        # Update meeting status if first participant
        if meeting.status == MeetingStatus.SCHEDULED:
            meeting.status = MeetingStatus.STARTING
            meeting.actual_start = datetime.utcnow()
        elif meeting.status == MeetingStatus.STARTING:
            meeting.status = MeetingStatus.IN_PROGRESS

        db.commit()

        # Send welcome message with meeting info
        await webrtc_manager.send_to_user(
            user_id,
            {
                "type": "meeting_joined",
                "data": {
                    "room_id": room_id,
                    "meeting": {
                        "id": meeting.id,
                        "title": meeting.title,
                        "recording_enabled": meeting.recording_enabled,
                        "transcription_enabled": meeting.transcription_enabled,
                    },
                    "participants": list(webrtc_manager.get_room_participants(room_id)),
                },
            },
        )

        # Handle incoming messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)

                await handle_webrtc_message(
                    room_id=room_id,
                    sender_id=user_id,
                    message=message,
                    meeting=meeting,
                    db=db,
                )

            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON received from user {user_id}")
                await webrtc_manager.send_to_user(
                    user_id,
                    {"type": "error", "data": {"message": "Invalid message format"}},
                )
            except Exception as e:
                logger.error(
                    f"Error handling WebSocket message from user {user_id}: {e}"
                )
                await webrtc_manager.send_to_user(
                    user_id,
                    {"type": "error", "data": {"message": "Internal server error"}},
                )

    except HTTPException as e:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason=e.detail)
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
        await websocket.close(
            code=status.WS_1011_INTERNAL_ERROR, reason="Internal server error"
        )
    finally:
        # Clean up on disconnect
        if user_id:
            webrtc_manager.disconnect(user_id)

            if user and room_id:
                # Update participant status
                try:
                    meeting = db.query(Meeting).filter_by(room_id=room_id).first()
                    if meeting:
                        db.execute(
                            meeting_participants.update()
                            .where(
                                and_(
                                    meeting_participants.c.meeting_id == meeting.id,
                                    meeting_participants.c.user_id == user_id,
                                )
                            )
                            .values(
                                status=ParticipantStatus.LEFT, left_at=datetime.utcnow()
                            )
                        )

                        # Check if meeting should be ended
                        active_participants = webrtc_manager.get_room_participants(
                            room_id
                        )
                        if (
                            not active_participants
                            and meeting.status == MeetingStatus.IN_PROGRESS
                        ):
                            meeting.status = MeetingStatus.COMPLETED
                            meeting.actual_end = datetime.utcnow()

                        db.commit()
                except Exception as e:
                    logger.error(
                        f"Error updating participant status on disconnect: {e}"
                    )


async def handle_webrtc_message(
    room_id: str, sender_id: int, message: dict, meeting: Meeting, db: Session
):
    """Handle different types of WebRTC signaling messages"""

    message_type = message.get("type")
    data = message.get("data", {})
    target_user_id = message.get("target_user_id")

    logger.debug(
        f"Handling message type '{message_type}' from user {sender_id} in room {room_id}"
    )

    if message_type == "offer":
        # WebRTC offer - forward to target peer
        if target_user_id:
            await webrtc_manager.send_to_room_user(
                room_id,
                target_user_id,
                {"type": "offer", "data": data, "sender_id": sender_id},
            )

    elif message_type == "answer":
        # WebRTC answer - forward to target peer
        if target_user_id:
            await webrtc_manager.send_to_room_user(
                room_id,
                target_user_id,
                {"type": "answer", "data": data, "sender_id": sender_id},
            )

    elif message_type == "ice-candidate":
        # ICE candidate - forward to target peer
        if target_user_id:
            await webrtc_manager.send_to_room_user(
                room_id,
                target_user_id,
                {"type": "ice-candidate", "data": data, "sender_id": sender_id},
            )
        else:
            # Broadcast to all participants except sender
            await webrtc_manager.broadcast_to_room(
                room_id,
                {"type": "ice-candidate", "data": data, "sender_id": sender_id},
                exclude_user=sender_id,
            )

    elif message_type == "start_recording":
        # Handle recording start request
        await handle_recording_request(room_id, sender_id, "start", meeting, db)

    elif message_type == "stop_recording":
        # Handle recording stop request
        await handle_recording_request(room_id, sender_id, "stop", meeting, db)

    elif message_type == "chat_message":
        # In-meeting chat message
        await handle_chat_message(room_id, sender_id, data, db)

    elif message_type == "screen_share_start":
        # Screen sharing started
        await webrtc_manager.broadcast_to_room(
            room_id,
            {
                "type": "screen_share_start",
                "data": {"user_id": sender_id},
                "sender_id": sender_id,
            },
            exclude_user=sender_id,
        )

    elif message_type == "screen_share_stop":
        # Screen sharing stopped
        await webrtc_manager.broadcast_to_room(
            room_id,
            {
                "type": "screen_share_stop",
                "data": {"user_id": sender_id},
                "sender_id": sender_id,
            },
            exclude_user=sender_id,
        )

    elif message_type == "mute_audio":
        # Audio muted
        await webrtc_manager.broadcast_to_room(
            room_id,
            {
                "type": "participant_muted",
                "data": {"user_id": sender_id, "audio": True},
                "sender_id": sender_id,
            },
            exclude_user=sender_id,
        )

    elif message_type == "unmute_audio":
        # Audio unmuted
        await webrtc_manager.broadcast_to_room(
            room_id,
            {
                "type": "participant_unmuted",
                "data": {"user_id": sender_id, "audio": True},
                "sender_id": sender_id,
            },
            exclude_user=sender_id,
        )

    elif message_type == "mute_video":
        # Video muted
        await webrtc_manager.broadcast_to_room(
            room_id,
            {
                "type": "participant_muted",
                "data": {"user_id": sender_id, "video": True},
                "sender_id": sender_id,
            },
            exclude_user=sender_id,
        )

    elif message_type == "unmute_video":
        # Video unmuted
        await webrtc_manager.broadcast_to_room(
            room_id,
            {
                "type": "participant_unmuted",
                "data": {"user_id": sender_id, "video": True},
                "sender_id": sender_id,
            },
            exclude_user=sender_id,
        )

    else:
        logger.warning(f"Unknown message type '{message_type}' from user {sender_id}")


async def handle_recording_request(
    room_id: str, user_id: int, action: str, meeting: Meeting, db: Session
):
    """Handle recording start/stop requests"""

    if not meeting.recording_enabled:
        await webrtc_manager.send_to_user(
            user_id,
            {
                "type": "error",
                "data": {"message": "Recording is not enabled for this meeting"},
            },
        )
        return

    # Check if user has recording permission
    participant = db.execute(
        meeting_participants.select().where(
            and_(
                meeting_participants.c.meeting_id == meeting.id,
                meeting_participants.c.user_id == user_id,
            )
        )
    ).first()

    if not participant or not participant.can_record:
        await webrtc_manager.send_to_user(
            user_id,
            {
                "type": "error",
                "data": {"message": "You don't have permission to record this meeting"},
            },
        )
        return

    # Check consent if required
    if meeting.recording_consent_required:
        # Get all participants' consent status
        participants = db.execute(
            meeting_participants.select().where(
                meeting_participants.c.meeting_id == meeting.id
            )
        ).fetchall()

        for p in participants:
            if p.recording_consent is None:
                await webrtc_manager.send_to_user(
                    user_id,
                    {
                        "type": "error",
                        "data": {
                            "message": "Recording consent required from all participants"
                        },
                    },
                )
                return
            elif p.recording_consent is False:
                await webrtc_manager.send_to_user(
                    user_id,
                    {
                        "type": "error",
                        "data": {
                            "message": "Recording consent denied by participant(s)"
                        },
                    },
                )
                return

    if action == "start":
        # Start recording logic here
        # This would integrate with actual recording service

        await webrtc_manager.broadcast_to_room(
            room_id,
            {
                "type": "recording_started",
                "data": {"started_by": user_id, "timestamp": str(datetime.utcnow())},
            },
        )

    elif action == "stop":
        # Stop recording logic here

        await webrtc_manager.broadcast_to_room(
            room_id,
            {
                "type": "recording_stopped",
                "data": {"stopped_by": user_id, "timestamp": str(datetime.utcnow())},
            },
        )


async def handle_chat_message(room_id: str, sender_id: int, data: dict, db: Session):
    """Handle in-meeting chat messages"""

    message_content = data.get("message", "").strip()
    if not message_content:
        return

    # Broadcast chat message to all participants
    await webrtc_manager.broadcast_to_room(
        room_id,
        {
            "type": "chat_message",
            "data": {
                "sender_id": sender_id,
                "message": message_content,
                "timestamp": str(datetime.utcnow()),
            },
        },
    )

    # TODO: Save chat message to database if needed


# Export connection manager for use in other modules
__all__ = ["router", "webrtc_manager"]
