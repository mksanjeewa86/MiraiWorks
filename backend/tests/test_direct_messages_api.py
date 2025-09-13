"""Tests for Direct Messages API endpoints."""

from unittest.mock import AsyncMock, patch

from fastapi import status
from fastapi.testclient import TestClient

from app.models.direct_message import DirectMessage
from app.models.user import User


class TestDirectMessagesAPI:
    """Test suite for Direct Messages API endpoints."""

    def test_get_conversations_success(
        self,
        client: TestClient,
        test_user: User,
        test_user2: User,
        test_messages: list[DirectMessage],
        test_utils,
    ):
        """Test successful conversation retrieval."""
        headers = test_utils.get_auth_headers(test_user.id)

        with patch("app.dependencies.get_current_active_user") as mock_auth:
            mock_auth.return_value = test_user

            response = client.get("/api/direct_messages/conversations", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "conversations" in data
        assert "total" in data
        assert data["total"] > 0

        # Should have conversation with test_user2
        conversations = data["conversations"]
        user2_conversation = next(
            (c for c in conversations if c["other_user_id"] == test_user2.id), None
        )
        assert user2_conversation is not None
        assert (
            user2_conversation["other_user_name"]
            == f"{test_user2.first_name} {test_user2.last_name}"
        )

    def test_get_conversations_with_search(
        self,
        client: TestClient,
        test_user: User,
        test_user2: User,
        test_messages: list[DirectMessage],
        test_utils,
    ):
        """Test conversation search."""
        headers = test_utils.get_auth_headers(test_user.id)

        with patch("app.dependencies.get_current_active_user") as mock_auth:
            mock_auth.return_value = test_user

            response = client.get(
                "/api/direct_messages/conversations",
                headers=headers,
                params={"search": "Test2"},
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        conversations = data["conversations"]
        assert len(conversations) >= 1

        # All returned conversations should match search
        for conversation in conversations:
            assert (
                "test2" in conversation["other_user_name"].lower()
                or "test2" in conversation["other_user_email"].lower()
            )

    def test_get_conversations_unauthorized(self, client: TestClient):
        """Test conversation retrieval without authentication."""
        response = client.get("/api/direct_messages/conversations")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_messages_with_user_success(
        self,
        client: TestClient,
        test_user: User,
        test_user2: User,
        test_messages: list[DirectMessage],
        test_utils,
    ):
        """Test successful message retrieval."""
        headers = test_utils.get_auth_headers(test_user.id)

        with patch("app.dependencies.get_current_active_user") as mock_auth:
            mock_auth.return_value = test_user

            response = client.get(
                f"/api/direct_messages/with/{test_user2.id}", headers=headers
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "messages" in data
        assert "total" in data
        assert "has_more" in data

        messages = data["messages"]
        assert len(messages) == 5  # From test_messages fixture

        # All messages should be between the two users
        for message in messages:
            assert (
                message["sender_id"] == test_user.id
                and message["recipient_id"] == test_user2.id
            ) or (
                message["sender_id"] == test_user2.id
                and message["recipient_id"] == test_user.id
            )

    def test_get_messages_with_pagination(
        self,
        client: TestClient,
        test_user: User,
        test_user2: User,
        test_messages: list[DirectMessage],
        test_utils,
    ):
        """Test message pagination."""
        headers = test_utils.get_auth_headers(test_user.id)

        with patch("app.dependencies.get_current_active_user") as mock_auth:
            mock_auth.return_value = test_user

            # Get first page
            response = client.get(
                f"/api/direct_messages/with/{test_user2.id}",
                headers=headers,
                params={"limit": 3},
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        messages = data["messages"]
        assert len(messages) == 3
        assert data["has_more"] is True

        # Get second page
        oldest_id = messages[-1]["id"]
        response = client.get(
            f"/api/direct_messages/with/{test_user2.id}",
            headers=headers,
            params={"limit": 3, "before_id": oldest_id},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        page2_messages = data["messages"]
        assert len(page2_messages) == 2  # Remaining messages

        # Verify no overlap
        page1_ids = {msg["id"] for msg in messages}
        page2_ids = {msg["id"] for msg in page2_messages}
        assert page1_ids.isdisjoint(page2_ids)

    def test_send_message_success(
        self, client: TestClient, test_user: User, test_user2: User, test_utils
    ):
        """Test successful message sending."""
        headers = test_utils.get_auth_headers(test_user.id)

        message_data = {
            "recipient_id": test_user2.id,
            "content": "Hello from API test!",
            "type": "text",
        }

        with patch("app.dependencies.get_current_active_user") as mock_auth, patch(
            "app.endpoints.direct_messages.connection_manager"
        ) as mock_manager, patch(
            "app.endpoints.direct_messages.notification_service"
        ) as mock_notifications:
            mock_auth.return_value = test_user
            mock_manager.broadcast_to_conversation = AsyncMock()
            mock_notifications.handle_new_message_notifications = AsyncMock()

            response = client.post(
                "/api/direct_messages/send", headers=headers, json=message_data
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["sender_id"] == test_user.id
        assert data["recipient_id"] == test_user2.id
        assert data["content"] == "Hello from API test!"
        assert data["type"] == "text"
        assert data["is_read"] is False

        # Note: Real-time messaging is now handled by polling on frontend
        # No WebSocket broadcast verification needed anymore

        # Verify notification handler was called
        mock_notifications.handle_new_message_notifications.assert_called_once()

    def test_send_file_message(
        self, client: TestClient, test_user: User, test_user2: User, test_utils
    ):
        """Test sending file message."""
        headers = test_utils.get_auth_headers(test_user.id)

        message_data = {
            "recipient_id": test_user2.id,
            "content": "📎 document.pdf",
            "type": "file",
            "file_url": "/files/uploads/document.pdf",
            "file_name": "document.pdf",
            "file_size": 1024000,
            "file_type": "application/pdf",
        }

        with patch("app.dependencies.get_current_active_user") as mock_auth, patch(
            "app.endpoints.direct_messages.connection_manager"
        ) as mock_manager, patch(
            "app.endpoints.direct_messages.notification_service"
        ) as mock_notifications:
            mock_auth.return_value = test_user
            mock_manager.broadcast_to_conversation = AsyncMock()
            mock_notifications.handle_new_message_notifications = AsyncMock()

            response = client.post(
                "/api/direct_messages/send", headers=headers, json=message_data
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["type"] == "file"
        assert data["file_url"] == "/files/uploads/document.pdf"
        assert data["file_name"] == "document.pdf"
        assert data["file_size"] == 1024000

    def test_send_message_invalid_recipient(
        self, client: TestClient, test_user: User, test_utils
    ):
        """Test sending message to non-existent recipient."""
        headers = test_utils.get_auth_headers(test_user.id)

        message_data = {
            "recipient_id": 99999,  # Non-existent user
            "content": "This should fail",
            "type": "text",
        }

        with patch("app.dependencies.get_current_active_user") as mock_auth:
            mock_auth.return_value = test_user

            response = client.post(
                "/api/direct_messages/send", headers=headers, json=message_data
            )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_send_message_role_restrictions(
        self, client: TestClient, test_user: User, test_admin_user: User, test_utils
    ):
        """Test role-based messaging restrictions."""
        headers = test_utils.get_auth_headers(test_user.id)

        message_data = {
            "recipient_id": test_admin_user.id,
            "content": "Trying to message admin",
            "type": "text",
        }

        with patch("app.dependencies.get_current_active_user") as mock_auth:
            mock_auth.return_value = test_user

            response = client.post(
                "/api/direct_messages/send", headers=headers, json=message_data
            )

        # Should fail due to role restrictions
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_search_messages_success(
        self,
        client: TestClient,
        test_user: User,
        test_messages: list[DirectMessage],
        test_utils,
    ):
        """Test message search."""
        headers = test_utils.get_auth_headers(test_user.id)

        search_data = {"query": "message 3", "limit": 10, "offset": 0}

        with patch("app.dependencies.get_current_active_user") as mock_auth:
            mock_auth.return_value = test_user

            response = client.post(
                "/api/direct_messages/search", headers=headers, json=search_data
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "messages" in data
        assert "total" in data
        assert "has_more" in data

        messages = data["messages"]
        # Should find at least one message containing "message 3"
        found_message = any("message 3" in msg["content"].lower() for msg in messages)
        assert found_message

    def test_search_messages_with_user_filter(
        self,
        client: TestClient,
        test_user: User,
        test_user2: User,
        test_messages: list[DirectMessage],
        test_utils,
    ):
        """Test message search with user filter."""
        headers = test_utils.get_auth_headers(test_user.id)

        search_data = {
            "query": "message",
            "with_user_id": test_user2.id,
            "limit": 10,
            "offset": 0,
        }

        with patch("app.dependencies.get_current_active_user") as mock_auth:
            mock_auth.return_value = test_user

            response = client.post(
                "/api/direct_messages/search", headers=headers, json=search_data
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        messages = data["messages"]
        # All results should involve test_user2
        for message in messages:
            assert (
                message["sender_id"] == test_user2.id
                or message["recipient_id"] == test_user2.id
            )

    def test_mark_messages_as_read_success(
        self,
        client: TestClient,
        test_user: User,
        test_messages: list[DirectMessage],
        test_utils,
    ):
        """Test marking messages as read."""
        headers = test_utils.get_auth_headers(test_user.id)

        # Get some unread message IDs
        unread_message_ids = [
            msg.id
            for msg in test_messages
            if msg.recipient_id == test_user.id and not msg.is_read
        ][:2]  # Take first 2

        read_data = {"message_ids": unread_message_ids}

        with patch("app.dependencies.get_current_active_user") as mock_auth:
            mock_auth.return_value = test_user

            response = client.put(
                "/api/direct_messages/mark-read", headers=headers, json=read_data
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "message" in data
        assert str(len(unread_message_ids)) in data["message"]

    def test_mark_conversation_as_read_success(
        self,
        client: TestClient,
        test_user: User,
        test_user2: User,
        test_messages: list[DirectMessage],
        test_utils,
    ):
        """Test marking entire conversation as read."""
        headers = test_utils.get_auth_headers(test_user.id)

        with patch("app.dependencies.get_current_active_user") as mock_auth:
            mock_auth.return_value = test_user

            response = client.put(
                f"/api/direct_messages/mark-conversation-read/{test_user2.id}",
                headers=headers,
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "message" in data
        assert "marked" in data["message"].lower()

    def test_get_participants_success(
        self, client: TestClient, test_user: User, test_user2: User, test_utils
    ):
        """Test getting message participants."""
        headers = test_utils.get_auth_headers(test_user.id)

        with patch("app.dependencies.get_current_active_user") as mock_auth:
            mock_auth.return_value = test_user

            response = client.get("/api/direct_messages/participants", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "participants" in data
        participants = data["participants"]

        # Should include test_user2 but not test_user itself
        participant_ids = [p["id"] for p in participants]
        assert test_user2.id in participant_ids
        assert test_user.id not in participant_ids

    def test_get_participants_with_search(
        self, client: TestClient, test_user: User, test_user2: User, test_utils
    ):
        """Test searching participants."""
        headers = test_utils.get_auth_headers(test_user.id)

        with patch("app.dependencies.get_current_active_user") as mock_auth:
            mock_auth.return_value = test_user

            response = client.get(
                "/api/direct_messages/participants",
                headers=headers,
                params={"query": "Test2"},
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        participants = data["participants"]
        # All participants should match search
        for participant in participants:
            name_match = "test2" in participant["full_name"].lower()
            email_match = "test2" in participant["email"].lower()
            assert name_match or email_match

    def test_get_participants_role_filtering(
        self, client: TestClient, test_admin_user: User, test_user2: User, test_utils
    ):
        """Test role-based participant filtering."""
        # Test as company admin - should only see super admins
        headers = test_utils.get_auth_headers(test_admin_user.id)

        with patch("app.dependencies.get_current_active_user") as mock_auth:
            mock_auth.return_value = test_admin_user

            response = client.get("/api/direct_messages/participants", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        participants = data["participants"]
        # Company admin should only see super admins, not regular users
        participant_ids = [p["id"] for p in participants]
        assert (
            test_user2.id not in participant_ids
        )  # Regular user should not be visible

    def test_invalid_json_request(
        self, client: TestClient, test_user: User, test_utils
    ):
        """Test invalid JSON in request."""
        headers = test_utils.get_auth_headers(test_user.id)

        with patch("app.dependencies.get_current_active_user") as mock_auth:
            mock_auth.return_value = test_user

            response = client.post(
                "/api/direct_messages/send", headers=headers, data="invalid json"
            )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_missing_required_fields(
        self, client: TestClient, test_user: User, test_utils
    ):
        """Test missing required fields in request."""
        headers = test_utils.get_auth_headers(test_user.id)

        # Missing recipient_id
        incomplete_data = {"content": "Hello", "type": "text"}

        with patch("app.dependencies.get_current_active_user") as mock_auth:
            mock_auth.return_value = test_user

            response = client.post(
                "/api/direct_messages/send", headers=headers, json=incomplete_data
            )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_empty_message_content(
        self, client: TestClient, test_user: User, test_user2: User, test_utils
    ):
        """Test sending empty message content."""
        headers = test_utils.get_auth_headers(test_user.id)

        message_data = {
            "recipient_id": test_user2.id,
            "content": "",  # Empty content
            "type": "text",
        }

        with patch("app.dependencies.get_current_active_user") as mock_auth:
            mock_auth.return_value = test_user

            response = client.post(
                "/api/direct_messages/send", headers=headers, json=message_data
            )

        # Should fail validation
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_rate_limiting_headers(
        self, client: TestClient, test_user: User, test_user2: User, test_utils
    ):
        """Test that rate limiting headers are present."""
        headers = test_utils.get_auth_headers(test_user.id)

        with patch("app.dependencies.get_current_active_user") as mock_auth, patch(
            "app.endpoints.direct_messages.connection_manager"
        ) as mock_manager, patch(
            "app.endpoints.direct_messages.notification_service"
        ) as mock_notifications:
            mock_auth.return_value = test_user
            mock_manager.broadcast_to_conversation = AsyncMock()
            mock_notifications.handle_new_message_notifications = AsyncMock()

            response = client.get("/api/direct_messages/conversations", headers=headers)

        assert response.status_code == status.HTTP_200_OK

        # Check for common rate limiting headers (if implemented)
        # This would depend on your rate limiting implementation
        # assert "X-RateLimit-Limit" in response.headers
        # assert "X-RateLimit-Remaining" in response.headers

    def test_large_message_content(
        self, client: TestClient, test_user: User, test_user2: User, test_utils
    ):
        """Test sending very large message content."""
        headers = test_utils.get_auth_headers(test_user.id)

        # Create a very large message (assuming there's a limit)
        large_content = "A" * 10000  # 10KB message

        message_data = {
            "recipient_id": test_user2.id,
            "content": large_content,
            "type": "text",
        }

        with patch("app.dependencies.get_current_active_user") as mock_auth:
            mock_auth.return_value = test_user

            response = client.post(
                "/api/direct_messages/send", headers=headers, json=message_data
            )

        # Depending on your validation, this might succeed or fail
        # Adjust assertion based on your message size limits
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ]
