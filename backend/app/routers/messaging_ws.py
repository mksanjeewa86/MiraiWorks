import json
import logging
from datetime import datetime
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from starlette.websockets import WebSocketState
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.user import User
from app.schemas.message import WSError, WSMessage, WSTyping
from app.services.auth_service import auth_service
from app.services.messaging_service import messaging_service

router = APIRouter()
logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manage WebSocket connections for real-time messaging."""

    def __init__(self):
        # Active connections: {user_id: {websocket, conversations: Set[int]}}
        self.connections: dict[int, dict] = {}
        # Conversation subscribers: {conversation_id: Set[user_id]}
        self.conversation_subscribers: dict[int, set[int]] = {}
        # Typing indicators: {conversation_id: {user_id: timestamp}}
        self.typing_indicators: dict[int, dict[int, datetime]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        """Connect user to WebSocket."""
        await websocket.accept()

        if user_id in self.connections:
            # Close existing connection
            try:
                await self.connections[user_id]["websocket"].close()
            except:
                pass

        self.connections[user_id] = {
            "websocket": websocket,
            "conversations": set(),
            "last_seen": datetime.utcnow(),
        }

        logger.info(f"User {user_id} connected to WebSocket")

        # Send connection confirmation
        await self.send_to_user(
            user_id,
            WSMessage(
                type="connected",
                data={"user_id": user_id, "message": "Connected successfully"},
            ),
        )

    async def disconnect(self, user_id: int):
        """Disconnect user from WebSocket."""
        if user_id not in self.connections:
            return

        user_data = self.connections[user_id]

        # Remove from conversation subscriptions
        for conv_id in user_data["conversations"].copy():
            await self.leave_conversation(user_id, conv_id)

        # Remove connection
        del self.connections[user_id]
        logger.info(f"User {user_id} disconnected from WebSocket")

    async def join_conversation(self, user_id: int, conversation_id: int):
        """Subscribe user to conversation updates."""
        if user_id not in self.connections:
            return False

        # Add to conversation subscribers
        if conversation_id not in self.conversation_subscribers:
            self.conversation_subscribers[conversation_id] = set()

        self.conversation_subscribers[conversation_id].add(user_id)
        self.connections[user_id]["conversations"].add(conversation_id)

        logger.info(f"User {user_id} joined conversation {conversation_id}")

        # Notify other participants
        await self.broadcast_to_conversation(
            conversation_id,
            WSMessage(
                type="user_joined",
                data={"user_id": user_id, "conversation_id": conversation_id},
            ),
            exclude_user=user_id,
        )

        return True

    async def leave_conversation(self, user_id: int, conversation_id: int):
        """Unsubscribe user from conversation updates."""
        if user_id not in self.connections:
            return

        # Remove from subscribers
        if conversation_id in self.conversation_subscribers:
            self.conversation_subscribers[conversation_id].discard(user_id)
            if not self.conversation_subscribers[conversation_id]:
                del self.conversation_subscribers[conversation_id]

        self.connections[user_id]["conversations"].discard(conversation_id)

        # Clear typing indicator
        if conversation_id in self.typing_indicators:
            self.typing_indicators[conversation_id].pop(user_id, None)
            if not self.typing_indicators[conversation_id]:
                del self.typing_indicators[conversation_id]

        logger.info(f"User {user_id} left conversation {conversation_id}")

        # Notify other participants
        await self.broadcast_to_conversation(
            conversation_id,
            WSMessage(
                type="user_left",
                data={"user_id": user_id, "conversation_id": conversation_id},
            ),
            exclude_user=user_id,
        )

    async def send_to_user(self, user_id: int, message: WSMessage):
        """Send message to specific user."""
        if user_id not in self.connections:
            return False

        try:
            websocket = self.connections[user_id]["websocket"]
            await websocket.send_text(message.model_dump_json())
            return True
        except Exception as e:
            logger.error(f"Failed to send message to user {user_id}: {e}")
            # Remove broken connection
            await self.disconnect(user_id)
            return False

    async def broadcast_to_conversation(
        self,
        conversation_id,
        message,
        exclude_user: Optional[int] = None,
    ):
        """Broadcast message to all conversation participants."""
        if conversation_id not in self.conversation_subscribers:
            return

        subscribers = self.conversation_subscribers[conversation_id].copy()
        if exclude_user:
            subscribers.discard(exclude_user)

        # Send to all subscribers
        failed_users = []
        for user_id in subscribers:
            success = await self.send_to_user(user_id, message)
            if not success:
                failed_users.append(user_id)

        # Clean up failed connections
        for user_id in failed_users:
            await self.disconnect(user_id)

    async def set_typing_indicator(
        self, user_id: int, conversation_id: int, is_typing: bool, user_name: str
    ):
        """Set/clear typing indicator for user in conversation."""
        if conversation_id not in self.typing_indicators:
            self.typing_indicators[conversation_id] = {}

        if is_typing:
            self.typing_indicators[conversation_id][user_id] = datetime.utcnow()
        else:
            self.typing_indicators[conversation_id].pop(user_id, None)
            if not self.typing_indicators[conversation_id]:
                del self.typing_indicators[conversation_id]

        # Broadcast typing indicator
        await self.broadcast_to_conversation(
            conversation_id,
            WSTyping(
                type="typing",
                data={
                    "user_id": user_id,
                    "user_name": user_name,
                    "conversation_id": conversation_id,
                    "is_typing": is_typing,
                },
            ),
            exclude_user=user_id,
        )

    def get_online_users(self) -> list[int]:
        """Get list of currently connected user IDs."""
        return list(self.connections.keys())

    def is_user_online(self, user_id: int) -> bool:
        """Check if user is currently online."""
        return user_id in self.connections


# Global connection manager
connection_manager = ConnectionManager()


async def get_current_user_ws(token: str, db: AsyncSession = Depends(get_db)) -> User:
    """Get current user from WebSocket token."""
    try:
        if not token:
            logger.warning("No token provided for WebSocket")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token required"
            )

        # Verify JWT token
        clean_token = token.replace("Bearer ", "").replace("Bearer%20", "")
        payload = auth_service.verify_token(clean_token, "access")
        if payload is None:
            logger.warning(f"Invalid token for WebSocket: {clean_token[:20]}...")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

        user_id = int(payload.get("sub"))
        logger.info(f"WebSocket authentication successful for user {user_id}")

        # Get user from database
        from app.models.role import UserRole, Role
        result = await db.execute(
            select(User)
            .options(selectinload(User.user_roles).selectinload(UserRole.role))
            .where(User.id == user_id, User.is_active == True)
        )

        user = result.scalar_one_or_none()
        if user is None:
            logger.warning(f"User {user_id} not found in database")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
            )

        return user
    except Exception as e:
        logger.error(f"WebSocket authentication failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)
        )


@router.websocket("/conversations/{conversation_id}")
async def websocket_conversation(
    websocket: WebSocket,
    conversation_id: int,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """WebSocket endpoint for real-time conversation updates."""
    try:
        # Authenticate user
        user = await get_current_user_ws(token, db)

        # Check conversation access
        logger.info(f"Checking conversation access for user {user.id} to conversation {conversation_id}")
        (
            can_access,
            reason,
        ) = await messaging_service.rules_service.can_access_conversation(
            db, user.id, conversation_id
        )
        if not can_access:
            logger.warning(f"WebSocket access denied for user {user.id} to conversation {conversation_id}: {reason}")
            await websocket.close(code=4003, reason=reason)
            return

        # Connect user
        await connection_manager.connect(websocket, user.id)

        # Join conversation
        await connection_manager.join_conversation(user.id, conversation_id)

        # WebSocket message loop
        while True:
            try:
                # Receive message
                data = await websocket.receive_text()
                message_data = json.loads(data)

                message_type = message_data.get("type")
                payload = message_data.get("data", {})

                if message_type == "typing":
                    # Handle typing indicator
                    is_typing = payload.get("is_typing", False)
                    await connection_manager.set_typing_indicator(
                        user.id, conversation_id, is_typing, user.full_name
                    )

                elif message_type == "message_read":
                    # Handle message read receipt
                    message_id = payload.get("message_id")
                    if message_id:
                        # Mark message as read
                        await messaging_service.mark_messages_as_read(
                            db, conversation_id, user.id, message_id
                        )

                        # Broadcast read receipt
                        await connection_manager.broadcast_to_conversation(
                            conversation_id,
                            WSMessage(
                                type="message_read",
                                data={
                                    "user_id": user.id,
                                    "user_name": user.full_name,
                                    "message_id": message_id,
                                    "read_at": datetime.utcnow().isoformat(),
                                },
                            ),
                            exclude_user=user.id,
                        )

                elif message_type == "ping":
                    # Handle ping/keepalive
                    await connection_manager.send_to_user(
                        user.id,
                        WSMessage(
                            type="pong",
                            data={"timestamp": datetime.utcnow().isoformat()},
                        ),
                    )

                else:
                    # Unknown message type
                    await connection_manager.send_to_user(
                        user.id,
                        WSError(
                            type="error",
                            data={
                                "error_code": "unknown_message_type",
                                "message": f"Unknown message type: {message_type}",
                            },
                        ),
                    )

            except json.JSONDecodeError:
                await connection_manager.send_to_user(
                    user.id,
                    WSError(
                        type="error",
                        data={
                            "error_code": "invalid_json",
                            "message": "Invalid JSON format",
                        },
                    ),
                )

            except Exception as e:
                logger.error(f"Error processing WebSocket message: {e}")
                await connection_manager.send_to_user(
                    user.id,
                    WSError(
                        type="error",
                        data={
                            "error_code": "processing_error",
                            "message": "Error processing message",
                        },
                    ),
                )

    except WebSocketDisconnect:
        logger.info(
            f"WebSocket disconnected for user {user.id if 'user' in locals() else 'unknown'}"
        )

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.close(code=4000, reason="Internal error")
        except:
            pass

    finally:
        # Clean up
        if "user" in locals():
            await connection_manager.disconnect(user.id)


@router.websocket("/direct/{other_user_id}")
async def websocket_direct_message(
    websocket: WebSocket,
    other_user_id: int,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """WebSocket endpoint for direct messaging with another user."""
    try:
        # Authenticate user
        user = await get_current_user_ws(token, db)
        
        logger.info(f"Direct message WebSocket connection attempt: user {user.id} with user {other_user_id}")

        # Verify the other user exists and is active
        other_user_result = await db.execute(
            select(User).where(User.id == other_user_id, User.is_active == True)
        )
        other_user = other_user_result.scalar_one_or_none()
        if not other_user:
            logger.warning(f"User {other_user_id} not found or inactive")
            await websocket.close(code=4004, reason="User not found")
            return

        # For direct messaging, allow all connections (no role restrictions)
        # Users can message anyone for now - we'll add restrictions later if needed
        logger.info(f"Direct messaging connection established between users {user.id} and {other_user_id}")

        # Connect user for direct messaging (use deterministic conversation ID)
        conversation_id = f"direct_{min(user.id, other_user_id)}_{max(user.id, other_user_id)}"
        await connection_manager.connect(websocket, user.id)
        await connection_manager.join_conversation(user.id, conversation_id)

        # WebSocket message loop
        while True:
            try:
                # Check if connection is still active
                if websocket.client_state == WebSocketState.DISCONNECTED:
                    break
                    
                data = await websocket.receive_text()
                message_data = json.loads(data)

                message_type = message_data.get("type")
                payload = message_data.get("data", {})

                if message_type == "typing":
                    is_typing = payload.get("is_typing", False)
                    await connection_manager.set_typing_indicator(
                        user.id, conversation_id, is_typing, user.full_name
                    )

                elif message_type == "message_read":
                    message_id = payload.get("message_id")
                    if message_id:
                        # For direct messages, we'll implement read receipts differently
                        logger.info(f"Message read receipt for message {message_id}")

                        await connection_manager.broadcast_to_conversation(
                            conversation_id,
                            WSMessage(
                                type="message_read",
                                data={
                                    "user_id": user.id,
                                    "user_name": user.full_name,
                                    "message_id": message_id,
                                    "read_at": datetime.utcnow().isoformat(),
                                },
                            ),
                            exclude_user=user.id,
                        )

                elif message_type == "ping":
                    await connection_manager.send_to_user(
                        user.id,
                        WSMessage(
                            type="pong",
                            data={"timestamp": datetime.utcnow().isoformat()},
                        ),
                    )

                else:
                    await connection_manager.send_to_user(
                        user.id,
                        WSError(
                            type="error",
                            data={
                                "error_code": "unknown_message_type",
                                "message": f"Unknown message type: {message_type}",
                            },
                        ),
                    )

            except json.JSONDecodeError:
                await connection_manager.send_to_user(
                    user.id,
                    WSError(
                        type="error",
                        data={
                            "error_code": "invalid_json",
                            "message": "Invalid JSON format",
                        },
                    ),
                )

            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected during message processing for user {user.id}")
                break
                
            except Exception as e:
                logger.error(f"Error processing direct message WebSocket: {e}")
                # Only try to send error if connection is still open
                try:
                    if websocket.client_state == WebSocketState.CONNECTED:
                        await connection_manager.send_to_user(
                            user.id,
                            WSError(
                                type="error",
                                data={
                                    "error_code": "processing_error",
                                    "message": "Error processing message",
                                },
                            ),
                        )
                except:
                    # Connection might be closed, just log and continue
                    logger.warning(f"Could not send error message to user {user.id}, connection closed")

    except WebSocketDisconnect:
        logger.info(f"Direct message WebSocket disconnected for user {user.id if 'user' in locals() else 'unknown'}")

    except Exception as e:
        logger.error(f"Direct message WebSocket error: {e}")
        try:
            await websocket.close(code=4000, reason="Internal error")
        except:
            pass

    finally:
        if "user" in locals():
            await connection_manager.disconnect(user.id)


@router.websocket("/status")
async def websocket_status(
    websocket: WebSocket, token: str = Query(...), db: AsyncSession = Depends(get_db)
):
    """WebSocket endpoint for general status updates (online status, notifications, etc.)."""
    try:
        # Authenticate user
        user = await get_current_user_ws(token, db)

        # Connect user (without joining specific conversation)
        await connection_manager.connect(websocket, user.id)

        # Send initial status
        await connection_manager.send_to_user(
            user.id,
            WSMessage(
                type="status",
                data={
                    "online_users": connection_manager.get_online_users(),
                    "user_id": user.id,
                },
            ),
        )

        # Status update loop
        while True:
            try:
                data = await websocket.receive_text()
                message_data = json.loads(data)

                message_type = message_data.get("type")

                if message_type == "ping":
                    await connection_manager.send_to_user(
                        user.id,
                        WSMessage(
                            type="pong",
                            data={"timestamp": datetime.utcnow().isoformat()},
                        ),
                    )

                elif message_type == "get_online_users":
                    await connection_manager.send_to_user(
                        user.id,
                        WSMessage(
                            type="online_users",
                            data={"users": connection_manager.get_online_users()},
                        ),
                    )

            except json.JSONDecodeError:
                await connection_manager.send_to_user(
                    user.id,
                    WSError(
                        type="error",
                        data={
                            "error_code": "invalid_json",
                            "message": "Invalid JSON format",
                        },
                    ),
                )

    except WebSocketDisconnect:
        logger.info(
            f"Status WebSocket disconnected for user {user.id if 'user' in locals() else 'unknown'}"
        )

    except Exception as e:
        logger.error(f"Status WebSocket error: {e}")
        try:
            await websocket.close(code=4000, reason="Internal error")
        except:
            pass

    finally:
        if "user" in locals():
            await connection_manager.disconnect(user.id)


# Function to broadcast new messages (called from REST API)
async def broadcast_new_message(conversation_id: int, message_info: dict):
    """Broadcast new message to conversation participants."""
    await connection_manager.broadcast_to_conversation(
        conversation_id, WSMessage(type="new_message", data=message_info)
    )


# Function to broadcast message updates
async def broadcast_message_update(conversation_id: int, message_info: dict):
    """Broadcast message updates to conversation participants."""
    await connection_manager.broadcast_to_conversation(
        conversation_id, WSMessage(type="message_updated", data=message_info)
    )


# Function to check if user is online
def is_user_online(user_id: int) -> bool:
    """Check if user is currently online."""
    return connection_manager.is_user_online(user_id)
