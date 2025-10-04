import json
import logging

from app.config.endpoints import API_ROUTES
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.database import get_db

# Remove the complex auth dependency for now

logger = logging.getLogger(__name__)

router = APIRouter()


# Connection manager for video call rooms
class VideoCallConnectionManager:
    def __init__(self):
        # Store active connections: room_id -> {user_id: websocket}
        self.active_connections: dict[str, dict[int, WebSocket]] = {}
        # Store user rooms: user_id -> room_id
        self.user_rooms: dict[int, str] = {}

    async def connect(self, websocket: WebSocket, room_id: str, user_id: int):
        """Connect a user to a video call room."""
        await websocket.accept()

        if room_id not in self.active_connections:
            self.active_connections[room_id] = {}

        self.active_connections[room_id][user_id] = websocket
        self.user_rooms[user_id] = room_id

        logger.info(f"User {user_id} connected to video call room {room_id}")

        # Notify other participants that a new user joined
        await self.broadcast_to_room(
            room_id,
            {"type": "user_joined", "user_id": user_id, "room_id": room_id},
            exclude_user=user_id,
        )

    async def disconnect(self, user_id: int):
        """Disconnect a user from their video call room."""
        if user_id in self.user_rooms:
            room_id = self.user_rooms[user_id]

            # Remove from active connections
            if (
                room_id in self.active_connections
                and user_id in self.active_connections[room_id]
            ):
                del self.active_connections[room_id][user_id]

                # Clean up empty rooms
                if not self.active_connections[room_id]:
                    del self.active_connections[room_id]

            del self.user_rooms[user_id]

            logger.info(f"User {user_id} disconnected from video call room {room_id}")

            # Notify other participants that user left
            await self.broadcast_to_room(
                room_id,
                {"type": "user_left", "user_id": user_id, "room_id": room_id},
                exclude_user=user_id,
            )

    async def send_personal_message(self, message: dict, user_id: int):
        """Send a message to a specific user."""
        if user_id in self.user_rooms:
            room_id = self.user_rooms[user_id]
            if (
                room_id in self.active_connections
                and user_id in self.active_connections[room_id]
            ):
                websocket = self.active_connections[room_id][user_id]
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Failed to send message to user {user_id}: {e}")

    async def broadcast_to_room(
        self, room_id: str, message: dict, exclude_user: int = None
    ):
        """Broadcast a message to all users in a room."""
        if room_id in self.active_connections:
            for user_id, websocket in self.active_connections[room_id].items():
                if exclude_user and user_id == exclude_user:
                    continue
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(
                        f"Failed to broadcast to user {user_id} in room {room_id}: {e}"
                    )

    async def forward_signaling_message(
        self, room_id: str, sender_id: int, message: dict
    ):
        """Forward WebRTC signaling messages between participants."""
        target_user_id = message.get("target_user_id")

        if target_user_id:
            # Send to specific user
            await self.send_personal_message(
                {**message, "sender_id": sender_id}, target_user_id
            )
        else:
            # Broadcast to all other users in room
            await self.broadcast_to_room(
                room_id, {**message, "sender_id": sender_id}, exclude_user=sender_id
            )


# Global connection manager instance
manager = VideoCallConnectionManager()


@router.websocket(API_ROUTES.WEBSOCKET_VIDEO.WS_VIDEO)
async def websocket_video_endpoint(
    websocket: WebSocket, room_id: str, db: AsyncSession = Depends(get_db)
):
    """WebSocket endpoint for video call signaling."""
    user_id = None

    try:
        # For simplicity, we'll extract user info from query params
        # In production, you'd want proper WebSocket authentication
        query_params = dict(websocket.query_params)
        user_id = query_params.get("user_id")

        if not user_id:
            await websocket.close(code=4000, reason="Missing user_id parameter")
            return

        user_id = int(user_id)

        # Verify the video call exists and user has permission
        video_call = await crud.video_call.get_by_room_id(db, room_id=room_id)
        if not video_call:
            await websocket.close(code=4004, reason="Video call not found")
            return

        # Check if user is participant
        if video_call.interviewer_id != user_id and video_call.candidate_id != user_id:
            await websocket.close(code=4003, reason="Access denied")
            return

        # Connect to the room
        await manager.connect(websocket, room_id, user_id)

        # Send initial room state
        room_participants = list(manager.active_connections.get(room_id, {}).keys())
        await manager.send_personal_message(
            {
                "type": "room_state",
                "room_id": room_id,
                "participants": room_participants,
                "your_user_id": user_id,
            },
            user_id,
        )

        # Handle incoming messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)

                # Handle different message types
                message_type = message.get("type")

                if message_type in ["offer", "answer", "ice_candidate"]:
                    # Forward WebRTC signaling messages
                    await manager.forward_signaling_message(room_id, user_id, message)

                elif message_type == "chat_message":
                    # Forward chat messages
                    await manager.broadcast_to_room(
                        room_id,
                        {
                            "type": "chat_message",
                            "sender_id": user_id,
                            "message": message.get("message", ""),
                            "timestamp": message.get("timestamp"),
                        },
                        exclude_user=user_id,
                    )

                elif message_type == "media_state":
                    # Forward media state changes (mute/unmute, video on/off)
                    await manager.broadcast_to_room(
                        room_id,
                        {
                            "type": "participant_media_state",
                            "user_id": user_id,
                            "is_muted": message.get("is_muted"),
                            "is_video_on": message.get("is_video_on"),
                            "is_screen_sharing": message.get("is_screen_sharing"),
                        },
                        exclude_user=user_id,
                    )

                else:
                    logger.warning(f"Unknown message type: {message_type}")

            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON received from user {user_id}")
            except Exception as e:
                logger.error(f"Error handling message from user {user_id}: {e}")

    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
    finally:
        if user_id:
            await manager.disconnect(user_id)
