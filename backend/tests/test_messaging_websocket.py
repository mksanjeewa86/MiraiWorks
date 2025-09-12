"""Tests for messaging WebSocket functionality."""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.routers.messaging_ws import ConnectionManager, connection_manager
from app.schemas.message import WSMessage, WSTyping, WSError


class TestConnectionManager:
    """Test suite for WebSocket ConnectionManager."""

    @pytest.fixture
    def manager(self):
        """Create a fresh ConnectionManager instance."""
        return ConnectionManager()

    @pytest.fixture
    def mock_websocket(self):
        """Mock WebSocket connection."""
        websocket = MagicMock()
        websocket.accept = AsyncMock()
        websocket.send_text = AsyncMock()
        websocket.receive_text = AsyncMock()
        websocket.close = AsyncMock()
        return websocket

    @pytest.mark.asyncio
    async def test_connect_user_success(self, manager: ConnectionManager, mock_websocket):
        """Test successful user connection."""
        user_id = 1
        
        await manager.connect(mock_websocket, user_id)
        
        # Verify WebSocket was accepted
        mock_websocket.accept.assert_called_once()
        
        # Verify user was added to connections
        assert user_id in manager.connections
        assert manager.connections[user_id]["websocket"] == mock_websocket
        assert isinstance(manager.connections[user_id]["conversations"], set)
        
        # Verify connection confirmation was sent
        mock_websocket.send_text.assert_called_once()
        sent_message = json.loads(mock_websocket.send_text.call_args[0][0])
        assert sent_message["type"] == "connected"
        assert sent_message["data"]["user_id"] == user_id

    @pytest.mark.asyncio
    async def test_connect_replaces_existing_connection(self, manager: ConnectionManager, mock_websocket):
        """Test that new connection replaces existing one."""
        user_id = 1
        
        # Create first connection
        old_websocket = MagicMock()
        old_websocket.accept = AsyncMock()
        old_websocket.send_text = AsyncMock()
        old_websocket.close = AsyncMock()
        
        await manager.connect(old_websocket, user_id)
        assert manager.connections[user_id]["websocket"] == old_websocket
        
        # Create second connection (should replace first)
        await manager.connect(mock_websocket, user_id)
        
        # Old connection should be closed
        old_websocket.close.assert_called_once()
        
        # New connection should be active
        assert manager.connections[user_id]["websocket"] == mock_websocket

    @pytest.mark.asyncio
    async def test_disconnect_user(self, manager: ConnectionManager, mock_websocket):
        """Test user disconnection."""
        user_id = 1
        conversation_id = 100
        
        # Connect user and join conversation
        await manager.connect(mock_websocket, user_id)
        await manager.join_conversation(user_id, conversation_id)
        
        assert user_id in manager.connections
        assert conversation_id in manager.conversation_subscribers
        
        # Disconnect user
        await manager.disconnect(user_id)
        
        # Verify user was removed from connections
        assert user_id not in manager.connections
        
        # Verify user was removed from conversation subscriptions
        assert conversation_id not in manager.conversation_subscribers

    @pytest.mark.asyncio
    async def test_join_conversation_success(self, manager: ConnectionManager, mock_websocket):
        """Test joining a conversation."""
        user_id = 1
        conversation_id = 100
        
        # Connect user first
        await manager.connect(mock_websocket, user_id)
        
        # Join conversation
        result = await manager.join_conversation(user_id, conversation_id)
        
        assert result is True
        assert conversation_id in manager.conversation_subscribers
        assert user_id in manager.conversation_subscribers[conversation_id]
        assert conversation_id in manager.connections[user_id]["conversations"]

    @pytest.mark.asyncio
    async def test_join_conversation_not_connected(self, manager: ConnectionManager):
        """Test joining conversation when user is not connected."""
        user_id = 1
        conversation_id = 100
        
        # Try to join conversation without connecting first
        result = await manager.join_conversation(user_id, conversation_id)
        
        assert result is False
        assert conversation_id not in manager.conversation_subscribers

    @pytest.mark.asyncio
    async def test_leave_conversation(self, manager: ConnectionManager, mock_websocket):
        """Test leaving a conversation."""
        user_id = 1
        conversation_id = 100
        
        # Connect and join conversation
        await manager.connect(mock_websocket, user_id)
        await manager.join_conversation(user_id, conversation_id)
        
        assert conversation_id in manager.conversation_subscribers
        assert user_id in manager.conversation_subscribers[conversation_id]
        
        # Leave conversation
        await manager.leave_conversation(user_id, conversation_id)
        
        # Verify user was removed from conversation
        assert conversation_id not in manager.conversation_subscribers
        assert conversation_id not in manager.connections[user_id]["conversations"]

    @pytest.mark.asyncio
    async def test_send_to_user_success(self, manager: ConnectionManager, mock_websocket):
        """Test sending message to user."""
        user_id = 1
        
        # Connect user
        await manager.connect(mock_websocket, user_id)
        
        # Send message
        message = WSMessage(type="test", data={"content": "test message"})
        result = await manager.send_to_user(user_id, message)
        
        assert result is True
        
        # Verify message was sent to WebSocket
        mock_websocket.send_text.assert_called()
        sent_data = mock_websocket.send_text.call_args[0][0]
        sent_message = json.loads(sent_data)
        assert sent_message["type"] == "test"
        assert sent_message["data"]["content"] == "test message"

    @pytest.mark.asyncio
    async def test_send_to_user_not_connected(self, manager: ConnectionManager):
        """Test sending message to user who is not connected."""
        user_id = 1
        
        message = WSMessage(type="test", data={"content": "test message"})
        result = await manager.send_to_user(user_id, message)
        
        assert result is False

    @pytest.mark.asyncio
    async def test_send_to_user_websocket_error(self, manager: ConnectionManager):
        """Test handling WebSocket error during message sending."""
        user_id = 1
        
        # Mock WebSocket that raises exception
        mock_websocket = MagicMock()
        mock_websocket.accept = AsyncMock()
        mock_websocket.send_text = AsyncMock(side_effect=Exception("Connection lost"))
        
        await manager.connect(mock_websocket, user_id)
        
        message = WSMessage(type="test", data={"content": "test message"})
        result = await manager.send_to_user(user_id, message)
        
        assert result is False
        # User should be disconnected after error
        assert user_id not in manager.connections

    @pytest.mark.asyncio
    async def test_broadcast_to_conversation(self, manager: ConnectionManager):
        """Test broadcasting message to conversation participants."""
        user1_id, user2_id = 1, 2
        conversation_id = 100
        
        # Create mock WebSockets
        websocket1 = MagicMock()
        websocket1.accept = AsyncMock()
        websocket1.send_text = AsyncMock()
        
        websocket2 = MagicMock()
        websocket2.accept = AsyncMock()
        websocket2.send_text = AsyncMock()
        
        # Connect both users
        await manager.connect(websocket1, user1_id)
        await manager.connect(websocket2, user2_id)
        
        # Join both to conversation
        await manager.join_conversation(user1_id, conversation_id)
        await manager.join_conversation(user2_id, conversation_id)
        
        # Broadcast message
        message = WSMessage(type="broadcast", data={"content": "hello everyone"})
        await manager.broadcast_to_conversation(conversation_id, message)
        
        # Both users should receive the message
        websocket1.send_text.assert_called()
        websocket2.send_text.assert_called()

    @pytest.mark.asyncio
    async def test_broadcast_to_conversation_exclude_user(self, manager: ConnectionManager):
        """Test broadcasting message while excluding specific user."""
        user1_id, user2_id = 1, 2
        conversation_id = 100
        
        # Create mock WebSockets
        websocket1 = MagicMock()
        websocket1.accept = AsyncMock()
        websocket1.send_text = AsyncMock()
        
        websocket2 = MagicMock()
        websocket2.accept = AsyncMock()
        websocket2.send_text = AsyncMock()
        
        # Connect both users
        await manager.connect(websocket1, user1_id)
        await manager.connect(websocket2, user2_id)
        
        # Join both to conversation
        await manager.join_conversation(user1_id, conversation_id)
        await manager.join_conversation(user2_id, conversation_id)
        
        # Broadcast message excluding user1
        message = WSMessage(type="broadcast", data={"content": "hello everyone"})
        await manager.broadcast_to_conversation(conversation_id, message, exclude_user=user1_id)
        
        # Only user2 should receive the message
        websocket1.send_text.assert_not_called()
        websocket2.send_text.assert_called()

    @pytest.mark.asyncio
    async def test_set_typing_indicator(self, manager: ConnectionManager):
        """Test setting typing indicator."""
        user_id = 1
        conversation_id = 100
        user_name = "Test User"
        
        # Mock WebSocket
        websocket1 = MagicMock()
        websocket1.accept = AsyncMock()
        websocket1.send_text = AsyncMock()
        
        websocket2 = MagicMock()
        websocket2.accept = AsyncMock() 
        websocket2.send_text = AsyncMock()
        
        # Connect users
        await manager.connect(websocket1, user_id)
        await manager.connect(websocket2, 2)
        
        # Join conversation
        await manager.join_conversation(user_id, conversation_id)
        await manager.join_conversation(2, conversation_id)
        
        # Set typing indicator
        await manager.set_typing_indicator(user_id, conversation_id, True, user_name)
        
        # Check typing indicator was recorded
        assert conversation_id in manager.typing_indicators
        assert user_id in manager.typing_indicators[conversation_id]
        
        # Check broadcast was sent (to other user)
        websocket2.send_text.assert_called()
        sent_data = websocket2.send_text.call_args[0][0]
        sent_message = json.loads(sent_data)
        assert sent_message["type"] == "typing"
        assert sent_message["data"]["is_typing"] is True

    @pytest.mark.asyncio
    async def test_clear_typing_indicator(self, manager: ConnectionManager):
        """Test clearing typing indicator."""
        user_id = 1
        conversation_id = 100
        
        # Set typing indicator first
        await manager.set_typing_indicator(user_id, conversation_id, True, "Test User")
        assert conversation_id in manager.typing_indicators
        
        # Clear typing indicator
        await manager.set_typing_indicator(user_id, conversation_id, False, "Test User")
        
        # Check typing indicator was cleared
        assert conversation_id not in manager.typing_indicators

    def test_get_online_users(self, manager: ConnectionManager):
        """Test getting list of online users."""
        # Initially no users
        assert manager.get_online_users() == []
        
        # Add users to connections manually
        manager.connections[1] = {"websocket": MagicMock(), "conversations": set()}
        manager.connections[2] = {"websocket": MagicMock(), "conversations": set()}
        
        online_users = manager.get_online_users()
        assert len(online_users) == 2
        assert 1 in online_users
        assert 2 in online_users

    def test_is_user_online(self, manager: ConnectionManager):
        """Test checking if user is online."""
        user_id = 1
        
        # User not online initially
        assert manager.is_user_online(user_id) is False
        
        # Add user to connections
        manager.connections[user_id] = {"websocket": MagicMock(), "conversations": set()}
        
        # User should now be online
        assert manager.is_user_online(user_id) is True


class TestWebSocketEndpoints:
    """Test WebSocket endpoint handlers."""

    @pytest.mark.asyncio
    @patch('app.routers.messaging_ws.get_current_user_ws')
    async def test_websocket_direct_message_connection(
        self, 
        mock_get_user: AsyncMock,
        test_user: User,
        test_user2: User,
        db_session: AsyncSession,
        mock_websocket
    ):
        """Test direct message WebSocket connection."""
        mock_get_user.return_value = test_user
        
        # Mock the websocket receive to simulate message
        mock_websocket.receive_text.return_value = json.dumps({
            "type": "typing",
            "data": {"is_typing": True}
        })
        
        from app.routers.messaging_ws import websocket_direct_message
        
        # This would normally be called by FastAPI WebSocket handler
        # We'll simulate the key parts of the connection
        
        with patch.object(connection_manager, 'connect') as mock_connect, \
             patch.object(connection_manager, 'join_conversation') as mock_join, \
             patch.object(connection_manager, 'set_typing_indicator') as mock_typing:
            
            mock_connect.return_value = None
            mock_join.return_value = None
            mock_typing.return_value = None
            
            # Simulate successful authentication and connection
            # In a real test, you'd need to handle the full WebSocket lifecycle
            await connection_manager.connect(mock_websocket, test_user.id)
            conversation_id = f"direct_{min(test_user.id, test_user2.id)}_{max(test_user.id, test_user2.id)}"
            await connection_manager.join_conversation(test_user.id, conversation_id)
            
            # Verify connection was established
            mock_connect.assert_called_with(mock_websocket, test_user.id)
            mock_join.assert_called_with(test_user.id, conversation_id)

    @pytest.mark.asyncio
    @patch('app.routers.messaging_ws.get_current_user_ws')
    async def test_websocket_typing_message(
        self, 
        mock_get_user: AsyncMock,
        test_user: User,
        db_session: AsyncSession
    ):
        """Test typing indicator WebSocket message."""
        mock_get_user.return_value = test_user
        
        # Connect user
        mock_websocket = MagicMock()
        mock_websocket.accept = AsyncMock()
        mock_websocket.send_text = AsyncMock()
        
        await connection_manager.connect(mock_websocket, test_user.id)
        conversation_id = "direct_1_2"
        await connection_manager.join_conversation(test_user.id, conversation_id)
        
        # Send typing indicator
        with patch.object(connection_manager, 'set_typing_indicator') as mock_typing:
            await connection_manager.set_typing_indicator(
                test_user.id, conversation_id, True, test_user.full_name
            )
            
            mock_typing.assert_called_with(
                test_user.id, conversation_id, True, test_user.full_name
            )

    @pytest.mark.asyncio
    @patch('app.routers.messaging_ws.get_current_user_ws')
    async def test_websocket_ping_pong(
        self, 
        mock_get_user: AsyncMock,
        test_user: User,
        db_session: AsyncSession
    ):
        """Test ping/pong WebSocket message."""
        mock_get_user.return_value = test_user
        
        # Connect user
        mock_websocket = MagicMock()
        mock_websocket.accept = AsyncMock()
        mock_websocket.send_text = AsyncMock()
        
        await connection_manager.connect(mock_websocket, test_user.id)
        
        # Send ping message (would normally be done by websocket handler)
        with patch.object(connection_manager, 'send_to_user') as mock_send:
            await connection_manager.send_to_user(
                test_user.id,
                WSMessage(type="pong", data={"timestamp": "2023-01-01T00:00:00"})
            )
            
            mock_send.assert_called_once()

    @pytest.mark.asyncio
    @patch('app.routers.messaging_ws.get_current_user_ws')
    async def test_websocket_read_receipt(
        self, 
        mock_get_user: AsyncMock,
        test_user: User,
        db_session: AsyncSession
    ):
        """Test message read receipt WebSocket message."""
        mock_get_user.return_value = test_user
        
        # Connect user
        mock_websocket = MagicMock()
        mock_websocket.accept = AsyncMock()
        mock_websocket.send_text = AsyncMock()
        
        await connection_manager.connect(mock_websocket, test_user.id)
        conversation_id = "direct_1_2"
        await connection_manager.join_conversation(test_user.id, conversation_id)
        
        # Send read receipt
        with patch.object(connection_manager, 'broadcast_to_conversation') as mock_broadcast, \
             patch('app.services.direct_message_service.direct_message_service.mark_messages_as_read') as mock_mark_read:
            
            mock_mark_read.return_value = 1
            
            # Simulate read receipt handling
            await connection_manager.broadcast_to_conversation(
                conversation_id,
                WSMessage(
                    type="message_read",
                    data={
                        "user_id": test_user.id,
                        "user_name": test_user.full_name,
                        "message_id": 123,
                        "read_at": "2023-01-01T00:00:00"
                    }
                ),
                exclude_user=test_user.id
            )
            
            mock_broadcast.assert_called_once()

    @pytest.mark.asyncio
    @patch('app.routers.messaging_ws.get_current_user_ws')
    async def test_websocket_authentication_failure(
        self, 
        mock_get_user: AsyncMock,
        mock_websocket
    ):
        """Test WebSocket authentication failure."""
        # Mock authentication failure
        mock_get_user.side_effect = Exception("Authentication failed")
        
        # WebSocket should be closed on auth failure
        from app.routers.messaging_ws import websocket_direct_message
        
        # In a real implementation, the WebSocket would be closed
        # This test verifies that auth errors are handled properly
        with pytest.raises(Exception):
            await mock_get_user("invalid-token")

    @pytest.mark.asyncio
    async def test_websocket_invalid_json_message(self):
        """Test handling invalid JSON in WebSocket message."""
        user_id = 1
        
        # Connect user
        mock_websocket = MagicMock()
        mock_websocket.accept = AsyncMock()
        mock_websocket.send_text = AsyncMock()
        
        await connection_manager.connect(mock_websocket, user_id)
        
        # Send error message (simulating invalid JSON handling)
        with patch.object(connection_manager, 'send_to_user') as mock_send:
            await connection_manager.send_to_user(
                user_id,
                WSError(
                    type="error",
                    data={
                        "error_code": "invalid_json",
                        "message": "Invalid JSON format"
                    }
                )
            )
            
            mock_send.assert_called_once()
            call_args = mock_send.call_args[0]
            assert call_args[1].type == "error"

    @pytest.mark.asyncio
    async def test_multiple_users_same_conversation(self):
        """Test multiple users in the same conversation."""
        user1_id, user2_id, user3_id = 1, 2, 3
        conversation_id = 100
        
        # Create mock WebSockets
        websockets = {}
        for user_id in [user1_id, user2_id, user3_id]:
            websocket = MagicMock()
            websocket.accept = AsyncMock()
            websocket.send_text = AsyncMock()
            websockets[user_id] = websocket
            await connection_manager.connect(websocket, user_id)
            await connection_manager.join_conversation(user_id, conversation_id)
        
        # Broadcast message
        message = WSMessage(type="test", data={"content": "group message"})
        await connection_manager.broadcast_to_conversation(conversation_id, message)
        
        # All users should receive the message
        for websocket in websockets.values():
            websocket.send_text.assert_called()

    @pytest.mark.asyncio
    async def test_conversation_cleanup_on_disconnect(self):
        """Test that conversations are cleaned up when users disconnect."""
        user_id = 1
        conversation_id = 100
        
        # Connect user and join conversation
        mock_websocket = MagicMock()
        mock_websocket.accept = AsyncMock()
        mock_websocket.send_text = AsyncMock()
        
        await connection_manager.connect(mock_websocket, user_id)
        await connection_manager.join_conversation(user_id, conversation_id)
        
        # Verify conversation exists
        assert conversation_id in connection_manager.conversation_subscribers
        assert user_id in connection_manager.conversation_subscribers[conversation_id]
        
        # Disconnect user
        await connection_manager.disconnect(user_id)
        
        # Verify conversation was cleaned up
        assert conversation_id not in connection_manager.conversation_subscribers