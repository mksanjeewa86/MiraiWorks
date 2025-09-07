import json
import logging
from datetime import datetime
from typing import Any, Optional

import redis.asyncio as redis

from app.config import settings
from app.schemas.message import WSMessage

logger = logging.getLogger(__name__)


class RealtimeService:
    """Redis pub/sub service for horizontal scaling of real-time features."""

    def __init__(self):
        self.redis_url = settings.redis_url
        self.publisher: Optional[redis.Redis] = None
        self.subscriber: Optional[redis.Redis] = None
        self.pubsub = None
        self.channels = {
            "messages": "miraiworks:messages",
            "typing": "miraiworks:typing",
            "user_status": "miraiworks:user_status",
            "notifications": "miraiworks:notifications",
        }

    async def connect(self):
        """Initialize Redis connections for pub/sub."""
        try:
            self.publisher = redis.from_url(self.redis_url)
            self.subscriber = redis.from_url(self.redis_url)
            self.pubsub = self.subscriber.pubsub()

            # Subscribe to all channels
            await self.pubsub.subscribe(*self.channels.values())

            logger.info("Connected to Redis pub/sub")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to Redis pub/sub: {e}")
            return False

    async def disconnect(self):
        """Close Redis connections."""
        try:
            if self.pubsub:
                await self.pubsub.unsubscribe()
                await self.pubsub.aclose()

            if self.publisher:
                await self.publisher.aclose()

            if self.subscriber:
                await self.subscriber.aclose()

            logger.info("Disconnected from Redis pub/sub")

        except Exception as e:
            logger.error(f"Error disconnecting from Redis: {e}")

    async def publish_message(self, conversation_id: int, message_data: dict[str, Any]):
        """Publish new message to all server instances."""
        if not self.publisher:
            logger.warning("Redis publisher not connected")
            return False

        try:
            payload = {
                "type": "new_message",
                "conversation_id": conversation_id,
                "data": message_data,
                "timestamp": datetime.utcnow().isoformat(),
                "server_id": self._get_server_id(),
            }

            await self.publisher.publish(self.channels["messages"], json.dumps(payload))

            logger.debug(f"Published message for conversation {conversation_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to publish message: {e}")
            return False

    async def publish_typing_indicator(
        self, conversation_id: int, user_id: int, user_name: str, is_typing: bool
    ):
        """Publish typing indicator to all server instances."""
        if not self.publisher:
            logger.warning("Redis publisher not connected")
            return False

        try:
            payload = {
                "type": "typing",
                "conversation_id": conversation_id,
                "user_id": user_id,
                "user_name": user_name,
                "is_typing": is_typing,
                "timestamp": datetime.utcnow().isoformat(),
                "server_id": self._get_server_id(),
            }

            await self.publisher.publish(self.channels["typing"], json.dumps(payload))

            return True

        except Exception as e:
            logger.error(f"Failed to publish typing indicator: {e}")
            return False

    async def publish_user_status(
        self,
        user_id: int,
        status: str,
        additional_data: Optional[dict[str, Any]] = None,
    ):
        """Publish user status change to all server instances."""
        if not self.publisher:
            logger.warning("Redis publisher not connected")
            return False

        try:
            payload = {
                "type": "user_status",
                "user_id": user_id,
                "status": status,  # online, offline, away, etc.
                "data": additional_data or {},
                "timestamp": datetime.utcnow().isoformat(),
                "server_id": self._get_server_id(),
            }

            await self.publisher.publish(
                self.channels["user_status"], json.dumps(payload)
            )

            return True

        except Exception as e:
            logger.error(f"Failed to publish user status: {e}")
            return False

    async def publish_notification(
        self, user_ids: list[int], notification_data: dict[str, Any]
    ):
        """Publish notification to specific users across all server instances."""
        if not self.publisher:
            logger.warning("Redis publisher not connected")
            return False

        try:
            payload = {
                "type": "notification",
                "target_users": user_ids,
                "data": notification_data,
                "timestamp": datetime.utcnow().isoformat(),
                "server_id": self._get_server_id(),
            }

            await self.publisher.publish(
                self.channels["notifications"], json.dumps(payload)
            )

            return True

        except Exception as e:
            logger.error(f"Failed to publish notification: {e}")
            return False

    async def listen_for_messages(self, message_handler):
        """Listen for Redis pub/sub messages and handle them."""
        if not self.pubsub:
            logger.error("Redis pubsub not initialized")
            return

        logger.info("Starting Redis message listener")

        try:
            async for message in self.pubsub.listen():
                if message["type"] == "message":
                    try:
                        # Parse message data
                        payload = json.loads(message["data"])
                        channel = message["channel"].decode()

                        # Skip messages from this server instance
                        if payload.get("server_id") == self._get_server_id():
                            continue

                        # Handle different message types
                        await self._handle_redis_message(
                            channel, payload, message_handler
                        )

                    except json.JSONDecodeError as e:
                        logger.error(f"Invalid JSON in Redis message: {e}")
                    except Exception as e:
                        logger.error(f"Error processing Redis message: {e}")

        except Exception as e:
            logger.error(f"Redis listener error: {e}")

    async def _handle_redis_message(
        self, channel: str, payload: dict[str, Any], handler
    ):
        """Handle different types of Redis messages."""
        try:
            message_type = payload.get("type")

            if channel == self.channels["messages"]:
                if message_type == "new_message":
                    await handler.handle_new_message(
                        payload["conversation_id"], payload["data"]
                    )

            elif channel == self.channels["typing"]:
                if message_type == "typing":
                    await handler.handle_typing_indicator(
                        payload["conversation_id"],
                        payload["user_id"],
                        payload["user_name"],
                        payload["is_typing"],
                    )

            elif channel == self.channels["user_status"]:
                if message_type == "user_status":
                    await handler.handle_user_status_change(
                        payload["user_id"], payload["status"], payload.get("data", {})
                    )

            elif channel == self.channels["notifications"]:
                if message_type == "notification":
                    await handler.handle_notification(
                        payload["target_users"], payload["data"]
                    )

        except Exception as e:
            logger.error(f"Error handling Redis message: {e}")

    def _get_server_id(self) -> str:
        """Get unique server identifier."""
        import os
        import socket

        hostname = socket.gethostname()
        pid = os.getpid()
        return f"{hostname}:{pid}"

    async def set_user_online_status(
        self, user_id: int, is_online: bool, ttl: int = 300
    ):
        """Set user online status in Redis with TTL."""
        if not self.publisher:
            return False

        try:
            key = f"user_online:{user_id}"
            if is_online:
                await self.publisher.setex(key, ttl, "1")
            else:
                await self.publisher.delete(key)

            return True

        except Exception as e:
            logger.error(f"Failed to set user online status: {e}")
            return False

    async def is_user_online(self, user_id: int) -> bool:
        """Check if user is online across all server instances."""
        if not self.publisher:
            return False

        try:
            key = f"user_online:{user_id}"
            result = await self.publisher.get(key)
            return result is not None

        except Exception as e:
            logger.error(f"Failed to check user online status: {e}")
            return False

    async def get_online_users(self) -> list[int]:
        """Get list of all online users across server instances."""
        if not self.publisher:
            return []

        try:
            pattern = "user_online:*"
            keys = await self.publisher.keys(pattern)

            user_ids = []
            for key in keys:
                key_str = key.decode() if isinstance(key, bytes) else key
                user_id_str = key_str.split(":")[-1]
                try:
                    user_ids.append(int(user_id_str))
                except ValueError:
                    continue

            return user_ids

        except Exception as e:
            logger.error(f"Failed to get online users: {e}")
            return []

    async def store_conversation_state(
        self, conversation_id: int, state_data: dict[str, Any], ttl: int = 3600
    ):
        """Store conversation state (typing indicators, etc.) in Redis."""
        if not self.publisher:
            return False

        try:
            key = f"conversation_state:{conversation_id}"
            await self.publisher.setex(key, ttl, json.dumps(state_data))
            return True

        except Exception as e:
            logger.error(f"Failed to store conversation state: {e}")
            return False

    async def get_conversation_state(
        self, conversation_id: int
    ) -> Optional[dict[str, Any]]:
        """Get conversation state from Redis."""
        if not self.publisher:
            return None

        try:
            key = f"conversation_state:{conversation_id}"
            data = await self.publisher.get(key)

            if data:
                return json.loads(data)
            return None

        except Exception as e:
            logger.error(f"Failed to get conversation state: {e}")
            return None


class RedisMessageHandler:
    """Handler for Redis pub/sub messages in WebSocket connection manager."""

    def __init__(self, connection_manager):
        self.connection_manager = connection_manager

    async def handle_new_message(
        self, conversation_id: int, message_data: dict[str, Any]
    ):
        """Handle new message broadcast from Redis."""
        try:
            ws_message = WSMessage(type="new_message", data=message_data)

            await self.connection_manager.broadcast_to_conversation(
                conversation_id, ws_message
            )

        except Exception as e:
            logger.error(f"Error handling new message broadcast: {e}")

    async def handle_typing_indicator(
        self, conversation_id: int, user_id: int, user_name: str, is_typing: bool
    ):
        """Handle typing indicator broadcast from Redis."""
        try:
            ws_message = WSMessage(
                type="typing",
                data={
                    "user_id": user_id,
                    "user_name": user_name,
                    "conversation_id": conversation_id,
                    "is_typing": is_typing,
                },
            )

            await self.connection_manager.broadcast_to_conversation(
                conversation_id, ws_message, exclude_user=user_id
            )

        except Exception as e:
            logger.error(f"Error handling typing indicator broadcast: {e}")

    async def handle_user_status_change(
        self, user_id: int, status: str, additional_data: dict[str, Any]
    ):
        """Handle user status change broadcast from Redis."""
        try:
            ws_message = WSMessage(
                type="user_status",
                data={"user_id": user_id, "status": status, **additional_data},
            )

            # Broadcast to all connected users (could be optimized to only interested users)
            for connected_user_id in self.connection_manager.get_online_users():
                await self.connection_manager.send_to_user(
                    connected_user_id, ws_message
                )

        except Exception as e:
            logger.error(f"Error handling user status change broadcast: {e}")

    async def handle_notification(
        self, target_users: list[int], notification_data: dict[str, Any]
    ):
        """Handle notification broadcast from Redis."""
        try:
            ws_message = WSMessage(type="notification", data=notification_data)

            for user_id in target_users:
                await self.connection_manager.send_to_user(user_id, ws_message)

        except Exception as e:
            logger.error(f"Error handling notification broadcast: {e}")


# Global instance
realtime_service = RealtimeService()
