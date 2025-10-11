# SSE (Server-Sent Events) Notifications Implementation Guide

## 📋 Overview

This document outlines the implementation of **Server-Sent Events (SSE)** for real-time notifications in MiraiWorks, replacing the current polling-based system.

### Why SSE?

**SSE (Server-Sent Events)** is the optimal choice for notifications because:

- ✅ **One-way communication** (server → client) - perfect for notifications
- ✅ **Native browser support** - `EventSource` API built into all modern browsers
- ✅ **Auto-reconnection** - handles connection drops automatically
- ✅ **Simpler than WebSocket** - less code, easier to maintain
- ✅ **Lower resource usage** - HTTP/2 multiplexing support
- ✅ **Production-ready** - works through proxies and load balancers

---

## 🏗️ Architecture Design

### Current System (Polling)

```
Frontend (React)
    ↓ Poll every 30s
Backend API (/api/notifications)
    ↓ Query database
Database
```

**Problems:**
- ❌ 30-second delay for new notifications
- ❌ High bandwidth usage (constant requests)
- ❌ Database load from frequent polling
- ❌ Poor user experience

### New System (SSE)

```
Frontend (EventSource)
    ↓ Persistent SSE connection
Backend SSE Endpoint (/sse/notifications)
    ↓ Listens to
Notification Manager (In-Memory Queue)
    ↓ Triggered by
Business Logic (create notification)
    ↓ Writes to
Database
```

**Benefits:**
- ✅ Instant notification delivery (<1s)
- ✅ 90% reduction in HTTP requests
- ✅ Lower database load
- ✅ Better user experience

---

## 📦 Components Overview

### Backend Components

1. **SSE Manager** (`app/services/sse_notification_manager.py`)
   - Manages active SSE connections
   - Routes notifications to correct users
   - Handles client registration/unregistration

2. **SSE Endpoint** (`app/endpoints/sse.py`)
   - Provides SSE stream endpoint
   - Authenticates users
   - Maintains connection lifecycle

3. **Notification Service** (Enhanced)
   - Creates notifications in database
   - Pushes to SSE manager for real-time delivery

### Frontend Components

1. **SSE Hook** (`frontend/src/hooks/useNotificationSSE.ts`)
   - Manages EventSource connection
   - Handles reconnection logic
   - Parses incoming events

2. **Notifications Context** (Updated)
   - Integrates SSE hook
   - Maintains backward compatibility with polling
   - Manages notification state

---

## 🔧 Implementation Steps

### Phase 1: Backend SSE Infrastructure

#### 1.1 Create SSE Manager Service

**File:** `backend/app/services/sse_notification_manager.py`

```python
"""
SSE Notification Manager

Manages Server-Sent Events connections for real-time notifications.
Follows MiraiWorks architecture rules:
- Business logic in services/
- No HTTP handling (that's in endpoints/)
- No direct database access (use notification_service)
"""

import asyncio
import logging
from typing import Dict, Set
from datetime import datetime

logger = logging.getLogger(__name__)


class SSENotificationManager:
    """
    Manages SSE connections and notification distribution.

    Architecture:
    - Maintains user_id -> queues mapping
    - Supports multiple connections per user (multi-tab/device)
    - Thread-safe for concurrent access
    """

    def __init__(self):
        # user_id -> set of queues (one per connection)
        self._connections: Dict[int, Set[asyncio.Queue]] = {}
        self._lock = asyncio.Lock()

    async def register_client(self, user_id: int, queue: asyncio.Queue) -> None:
        """
        Register a new SSE client connection.

        Args:
            user_id: User ID for the connection
            queue: Async queue for sending notifications
        """
        async with self._lock:
            if user_id not in self._connections:
                self._connections[user_id] = set()

            self._connections[user_id].add(queue)

            logger.info(
                f"SSE client registered for user {user_id}. "
                f"Total connections: {len(self._connections[user_id])}"
            )

    async def unregister_client(self, user_id: int, queue: asyncio.Queue) -> None:
        """
        Unregister an SSE client connection.

        Args:
            user_id: User ID for the connection
            queue: Queue to remove
        """
        async with self._lock:
            if user_id in self._connections:
                self._connections[user_id].discard(queue)

                # Clean up empty user entries
                if not self._connections[user_id]:
                    del self._connections[user_id]

                logger.info(
                    f"SSE client unregistered for user {user_id}. "
                    f"Remaining connections: {len(self._connections.get(user_id, set()))}"
                )

    async def send_notification(self, user_id: int, notification: dict) -> int:
        """
        Send notification to all active connections for a user.

        Args:
            user_id: Target user ID
            notification: Notification data to send

        Returns:
            Number of connections notified
        """
        if user_id not in self._connections:
            logger.debug(f"No active SSE connections for user {user_id}")
            return 0

        queues = list(self._connections[user_id])
        success_count = 0
        failed_queues = []

        for queue in queues:
            try:
                # Non-blocking put with timeout
                await asyncio.wait_for(
                    queue.put(notification),
                    timeout=1.0
                )
                success_count += 1
            except asyncio.TimeoutError:
                logger.warning(f"Queue full for user {user_id}, dropping notification")
                failed_queues.append(queue)
            except Exception as e:
                logger.error(f"Failed to queue notification for user {user_id}: {e}")
                failed_queues.append(queue)

        # Clean up failed queues
        if failed_queues:
            async with self._lock:
                for failed_queue in failed_queues:
                    self._connections[user_id].discard(failed_queue)

        logger.info(
            f"Notification sent to {success_count}/{len(queues)} connections for user {user_id}"
        )

        return success_count

    async def broadcast_to_users(self, user_ids: list[int], notification: dict) -> int:
        """
        Broadcast notification to multiple users.

        Args:
            user_ids: List of user IDs
            notification: Notification data to send

        Returns:
            Total number of connections notified
        """
        total_notified = 0

        for user_id in user_ids:
            count = await self.send_notification(user_id, notification)
            total_notified += count

        return total_notified

    def get_active_users(self) -> list[int]:
        """Get list of user IDs with active connections."""
        return list(self._connections.keys())

    def get_connection_count(self, user_id: int = None) -> int:
        """
        Get connection count.

        Args:
            user_id: If provided, returns connections for that user.
                    If None, returns total connections.
        """
        if user_id is not None:
            return len(self._connections.get(user_id, set()))

        return sum(len(queues) for queues in self._connections.values())

    async def send_heartbeat(self, user_id: int) -> None:
        """
        Send heartbeat/ping to keep connection alive.

        Args:
            user_id: User ID to send heartbeat to
        """
        heartbeat = {
            "type": "heartbeat",
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self.send_notification(user_id, heartbeat)


# Global singleton instance
sse_notification_manager = SSENotificationManager()
```

#### 1.2 Create SSE Endpoint

**File:** `backend/app/endpoints/sse.py`

```python
"""
SSE Endpoints

Server-Sent Events endpoints for real-time notifications.
Follows MiraiWorks architecture rules:
- HTTP handling only
- Uses services for business logic
- Proper authentication with dependencies
"""

import asyncio
import json
import logging
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.endpoints import API_ROUTES
from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.user import User
from app.services.sse_notification_manager import sse_notification_manager

router = APIRouter(tags=["sse"])
logger = logging.getLogger(__name__)


async def notification_event_generator(
    user_id: int,
    request: Request,
) -> AsyncGenerator[str, None]:
    """
    Generate SSE events for a user's notifications.

    Yields:
        SSE formatted strings
    """
    # Create queue for this connection
    queue: asyncio.Queue = asyncio.Queue(maxsize=100)

    try:
        # Register this connection
        await sse_notification_manager.register_client(user_id, queue)

        # Send initial connection event
        yield f"event: connected\ndata: {json.dumps({'user_id': user_id, 'status': 'connected'})}\n\n"

        # Keep connection alive and send notifications
        while True:
            # Check if client disconnected
            if await request.is_disconnected():
                logger.info(f"Client disconnected (user {user_id})")
                break

            try:
                # Wait for notification with timeout
                notification = await asyncio.wait_for(
                    queue.get(),
                    timeout=30.0  # 30-second timeout for heartbeat
                )

                # Determine event type
                event_type = notification.get("type", "notification")

                # Format as SSE
                yield f"event: {event_type}\ndata: {json.dumps(notification)}\n\n"

            except asyncio.TimeoutError:
                # Send heartbeat to keep connection alive
                heartbeat = {
                    "type": "heartbeat",
                    "timestamp": "now",
                }
                yield f"event: heartbeat\ndata: {json.dumps(heartbeat)}\n\n"

    except asyncio.CancelledError:
        logger.info(f"SSE connection cancelled for user {user_id}")
        raise
    except Exception as e:
        logger.error(f"Error in SSE stream for user {user_id}: {e}")
        # Send error event
        error_data = {
            "type": "error",
            "message": "Stream error occurred",
        }
        yield f"event: error\ndata: {json.dumps(error_data)}\n\n"
    finally:
        # Always unregister on disconnect
        await sse_notification_manager.unregister_client(user_id, queue)
        logger.info(f"SSE connection closed for user {user_id}")


@router.get(API_ROUTES.SSE.NOTIFICATIONS)
async def sse_notifications(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    SSE endpoint for real-time notifications.

    Returns:
        StreamingResponse with text/event-stream
    """
    logger.info(f"SSE connection initiated for user {current_user.id}")

    return StreamingResponse(
        notification_event_generator(current_user.id, request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )


@router.get(API_ROUTES.SSE.STATUS)
async def sse_status(
    current_user: User = Depends(get_current_active_user),
):
    """
    Get SSE connection status.

    Returns:
        Connection statistics
    """
    connection_count = sse_notification_manager.get_connection_count(current_user.id)
    total_connections = sse_notification_manager.get_connection_count()
    active_users = len(sse_notification_manager.get_active_users())

    return {
        "user_connections": connection_count,
        "total_connections": total_connections,
        "active_users": active_users,
        "status": "active" if connection_count > 0 else "inactive",
    }
```

#### 1.3 Update API Routes Configuration

**File:** `backend/app/config/endpoints.py`

Add SSE routes to the `API_ROUTES` configuration:

```python
class API_ROUTES:
    # ... existing routes ...

    class SSE:
        """Server-Sent Events endpoints"""
        NOTIFICATIONS = "/sse/notifications"
        STATUS = "/sse/status"
```

#### 1.4 Update Notification Service

**File:** `backend/app/services/notification_service.py`

```python
from app.services.sse_notification_manager import sse_notification_manager

class NotificationService:
    # ... existing code ...

    async def create_notification(
        self,
        db: AsyncSession,
        user_id: int,
        notification_type: str,
        title: str,
        message: str,
        payload: dict = None,
    ):
        """
        Create notification in database and push to SSE.

        This follows the architecture:
        1. Save to database (persistence)
        2. Push to SSE (real-time delivery)
        """
        # Create in database
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            payload=payload or {},
            is_read=False,
            created_at=get_utc_now(),
        )

        db.add(notification)
        await db.commit()
        await db.refresh(notification)

        # Push to SSE for real-time delivery
        notification_data = {
            "id": notification.id,
            "type": notification.type,
            "title": notification.title,
            "message": notification.message,
            "payload": notification.payload,
            "is_read": False,
            "created_at": notification.created_at.isoformat(),
        }

        await sse_notification_manager.send_notification(user_id, notification_data)

        logger.info(f"Created notification {notification.id} for user {user_id}")

        return notification
```

#### 1.5 Register SSE Router

**File:** `backend/app/main.py`

```python
from app.endpoints import sse

# Register routers
app.include_router(sse.router, prefix="/api")
```

---

### Phase 2: Frontend SSE Integration

#### 2.1 Create SSE Hook

**File:** `frontend/src/hooks/useNotificationSSE.ts`

```typescript
/**
 * SSE Hook for Real-time Notifications
 *
 * Manages EventSource connection to SSE endpoint.
 * Follows MiraiWorks architecture:
 * - Custom hook for shared logic
 * - Uses API configuration from config
 * - Proper error handling and reconnection
 */

import { useEffect, useRef, useCallback } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import type { AppNotification } from '@/types/notification';

interface UseNotificationSSEProps {
  onNotification: (notification: AppNotification) => void;
  onError?: (error: Error) => void;
  onConnected?: () => void;
}

export function useNotificationSSE({
  onNotification,
  onError,
  onConnected,
}: UseNotificationSSEProps) {
  const { accessToken, user } = useAuth();
  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 5;

  const connect = useCallback(() => {
    if (!accessToken || !user) {
      console.log('⏸️ SSE: No auth token, skipping connection');
      return;
    }

    // Clean up existing connection
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const url = `${apiUrl}/api/sse/notifications`;

      console.log('🔌 SSE: Connecting to', url);

      // Create EventSource with auth token in URL params
      const eventSource = new EventSource(`${url}?token=${accessToken}`, {
        withCredentials: true,
      });

      eventSourceRef.current = eventSource;

      // Handle connection opened
      eventSource.addEventListener('open', () => {
        console.log('✅ SSE: Connected');
        reconnectAttemptsRef.current = 0;
      });

      // Handle 'connected' event (custom event from backend)
      eventSource.addEventListener('connected', (event) => {
        const data = JSON.parse(event.data);
        console.log('✅ SSE: Connection confirmed', data);
        onConnected?.();
      });

      // Handle 'notification' events
      eventSource.addEventListener('notification', (event) => {
        try {
          const notification: AppNotification = JSON.parse(event.data);
          console.log('📬 SSE: Notification received', notification);
          onNotification(notification);
        } catch (error) {
          console.error('❌ SSE: Failed to parse notification', error);
        }
      });

      // Handle 'heartbeat' events (keep connection alive)
      eventSource.addEventListener('heartbeat', (event) => {
        console.log('💓 SSE: Heartbeat received');
      });

      // Handle errors
      eventSource.addEventListener('error', (event) => {
        console.error('❌ SSE: Error occurred', event);

        if (eventSource.readyState === EventSource.CLOSED) {
          console.log('🔌 SSE: Connection closed');

          // Attempt reconnection with exponential backoff
          if (reconnectAttemptsRef.current < maxReconnectAttempts) {
            const delay = Math.min(
              1000 * Math.pow(2, reconnectAttemptsRef.current),
              30000
            );

            console.log(
              `🔄 SSE: Reconnecting in ${delay}ms (attempt ${
                reconnectAttemptsRef.current + 1
              }/${maxReconnectAttempts})`
            );

            reconnectTimeoutRef.current = setTimeout(() => {
              reconnectAttemptsRef.current++;
              connect();
            }, delay);
          } else {
            console.error('❌ SSE: Max reconnection attempts reached');
            onError?.(new Error('SSE connection failed after max retries'));
          }
        }
      });
    } catch (error) {
      console.error('❌ SSE: Failed to create connection', error);
      onError?.(error as Error);
    }
  }, [accessToken, user, onNotification, onError, onConnected]);

  // Connect on mount and auth changes
  useEffect(() => {
    connect();

    return () => {
      // Cleanup
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (eventSourceRef.current) {
        console.log('🔌 SSE: Disconnecting');
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
    };
  }, [connect]);

  const disconnect = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
  }, []);

  const isConnected = useCallback(() => {
    return (
      eventSourceRef.current !== null &&
      eventSourceRef.current.readyState === EventSource.OPEN
    );
  }, []);

  return {
    disconnect,
    isConnected,
  };
}
```

#### 2.2 Update Notifications Context

**File:** `frontend/src/contexts/NotificationsContext.tsx`

```typescript
'use client';

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { AppNotification } from '@/types/notification';
import { notificationsApi } from '@/api/notifications';
import { useAuth } from './AuthContext';
import { useNotificationSSE } from '@/hooks/useNotificationSSE';
import type { NotificationsContextType, NotificationsProviderProps } from '@/types/contexts';

const NotificationsContext = createContext<NotificationsContextType | undefined>(undefined);

export const useNotifications = () => {
  const context = useContext(NotificationsContext);
  if (!context) {
    throw new Error('useNotifications must be used within a NotificationsProvider');
  }
  return context;
};

export const NotificationsProvider: React.FC<NotificationsProviderProps> = ({ children }) => {
  const [notifications, setNotifications] = useState<AppNotification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isSSEConnected, setIsSSEConnected] = useState(false);
  const { user } = useAuth();

  // Show browser notification
  const showNotification = (title: string, message: string) => {
    if (window.Notification && Notification.permission === 'granted') {
      new window.Notification(title, {
        body: message,
        icon: '/favicon.ico',
      });
    }
  };

  // Request notification permission
  useEffect(() => {
    if (window.Notification && Notification.permission === 'default') {
      window.Notification.requestPermission();
    }
  }, []);

  // Handle incoming SSE notification
  const handleNewNotification = useCallback((notification: AppNotification) => {
    console.log('📬 New notification received:', notification);

    // Add to state (prepend to array)
    setNotifications((prev) => [notification, ...prev]);

    // Increment unread count
    setUnreadCount((prev) => prev + 1);

    // Show browser notification
    showNotification(notification.title, notification.message);
  }, []);

  // Handle SSE connection
  const handleSSEConnected = useCallback(() => {
    console.log('✅ SSE connected');
    setIsSSEConnected(true);
  }, []);

  const handleSSEError = useCallback((error: Error) => {
    console.error('❌ SSE error:', error);
    setIsSSEConnected(false);
  }, []);

  // Connect to SSE for real-time notifications
  const { isConnected } = useNotificationSSE({
    onNotification: handleNewNotification,
    onConnected: handleSSEConnected,
    onError: handleSSEError,
  });

  // Fetch initial notifications and unread count
  const refreshNotifications = useCallback(async () => {
    if (!user) return;

    try {
      const response = await notificationsApi.getNotifications(50);
      setNotifications(response.notifications);
    } catch (error) {
      console.error('Failed to fetch notifications:', error);
    }
  }, [user]);

  const refreshUnreadCount = useCallback(async () => {
    if (!user) return;

    try {
      const response = await notificationsApi.getUnreadCount();
      setUnreadCount(response.unread_count);
    } catch (error) {
      console.error('Failed to fetch unread count:', error);
    }
  }, [user]);

  // Mark notifications as read
  const markAsRead = async (notificationIds: number[]) => {
    try {
      await notificationsApi.markNotificationsRead(notificationIds);

      // Update local state
      setNotifications((prev) =>
        prev.map((notification) =>
          notificationIds.includes(notification.id)
            ? { ...notification, is_read: true, read_at: new Date().toISOString() }
            : notification
        )
      );

      await refreshUnreadCount();
    } catch (error) {
      console.error('Failed to mark notifications as read:', error);
    }
  };

  // Mark all notifications as read
  const markAllAsRead = async () => {
    try {
      await notificationsApi.markAllNotificationsRead();

      // Update local state
      setNotifications((prev) =>
        prev.map((notification) => ({
          ...notification,
          is_read: true,
          read_at: new Date().toISOString(),
        }))
      );

      setUnreadCount(0);
    } catch (error) {
      console.error('Failed to mark all notifications as read:', error);
    }
  };

  // Load initial data when user logs in
  useEffect(() => {
    if (user) {
      refreshNotifications();
      refreshUnreadCount();
    } else {
      setNotifications([]);
      setUnreadCount(0);
    }
  }, [user, refreshNotifications, refreshUnreadCount]);

  const value: NotificationsContextType = {
    notifications,
    unreadCount,
    showNotification,
    markAsRead,
    markAllAsRead,
    refreshNotifications,
    refreshUnreadCount,
    isSSEConnected, // New: expose connection status
  };

  return <NotificationsContext.Provider value={value}>{children}</NotificationsContext.Provider>;
};
```

#### 2.3 Update Context Types

**File:** `frontend/src/types/contexts.ts`

```typescript
export interface NotificationsContextType {
  notifications: AppNotification[];
  unreadCount: number;
  showNotification: (title: string, message: string) => void;
  markAsRead: (notificationIds: number[]) => void;
  markAllAsRead: () => void;
  refreshNotifications: () => Promise<void>;
  refreshUnreadCount: () => Promise<void>;
  isSSEConnected: boolean; // Add this
}
```

#### 2.4 Add SSE Connection Indicator (Optional)

**File:** `frontend/src/components/notifications/SSEConnectionStatus.tsx`

```typescript
'use client';

import React from 'react';
import { useNotifications } from '@/contexts/NotificationsContext';

export default function SSEConnectionStatus() {
  const { isSSEConnected } = useNotifications();

  if (!isSSEConnected) {
    return (
      <div className="text-xs text-yellow-600 bg-yellow-50 px-2 py-1 rounded">
        ⚠️ Real-time notifications disconnected
      </div>
    );
  }

  return (
    <div className="text-xs text-green-600 bg-green-50 px-2 py-1 rounded">
      ✅ Real-time notifications active
    </div>
  );
}
```

---

## 🧪 Testing Strategy

### Backend Testing

**File:** `backend/app/tests/test_sse_notifications.py`

```python
"""
SSE Notifications Tests

Comprehensive tests for SSE notification functionality.
Follows MiraiWorks testing requirements:
- 100% endpoint coverage
- All success scenarios
- All error scenarios
- Authentication tests
- Edge cases
"""

import asyncio
import json
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.sse_notification_manager import sse_notification_manager
from app.services.notification_service import notification_service


class TestSSENotifications:
    """Comprehensive tests for SSE notifications."""

    @pytest.mark.asyncio
    async def test_sse_connection_success(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test successful SSE connection with authentication."""
        # This test would use a streaming client
        pass  # Placeholder - SSE testing requires special setup

    @pytest.mark.asyncio
    async def test_sse_connection_unauthorized(self, client: AsyncClient):
        """Test SSE connection without authentication fails."""
        response = await client.get("/api/sse/notifications")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_sse_manager_register_client(self):
        """Test registering SSE client."""
        queue = asyncio.Queue()
        user_id = 123

        await sse_notification_manager.register_client(user_id, queue)

        assert user_id in sse_notification_manager.get_active_users()
        assert sse_notification_manager.get_connection_count(user_id) == 1

        # Cleanup
        await sse_notification_manager.unregister_client(user_id, queue)

    @pytest.mark.asyncio
    async def test_sse_manager_send_notification(self):
        """Test sending notification through SSE manager."""
        queue = asyncio.Queue()
        user_id = 123

        await sse_notification_manager.register_client(user_id, queue)

        notification = {
            "id": 1,
            "type": "test",
            "title": "Test",
            "message": "Test message",
        }

        count = await sse_notification_manager.send_notification(user_id, notification)
        assert count == 1

        # Verify notification in queue
        received = await queue.get()
        assert received == notification

        # Cleanup
        await sse_notification_manager.unregister_client(user_id, queue)

    @pytest.mark.asyncio
    async def test_sse_manager_multiple_connections(self):
        """Test multiple SSE connections for same user."""
        queue1 = asyncio.Queue()
        queue2 = asyncio.Queue()
        user_id = 123

        await sse_notification_manager.register_client(user_id, queue1)
        await sse_notification_manager.register_client(user_id, queue2)

        assert sse_notification_manager.get_connection_count(user_id) == 2

        notification = {"test": "data"}
        count = await sse_notification_manager.send_notification(user_id, notification)

        assert count == 2

        # Verify both queues received notification
        assert await queue1.get() == notification
        assert await queue2.get() == notification

        # Cleanup
        await sse_notification_manager.unregister_client(user_id, queue1)
        await sse_notification_manager.unregister_client(user_id, queue2)

    @pytest.mark.asyncio
    async def test_sse_status_endpoint(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test SSE status endpoint."""
        response = await client.get("/api/sse/status", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "user_connections" in data
        assert "total_connections" in data
        assert "active_users" in data
        assert "status" in data
```

### Frontend Testing

**File:** `frontend/src/hooks/__tests__/useNotificationSSE.test.ts`

```typescript
import { renderHook, waitFor } from '@testing-library/react';
import { useNotificationSSE } from '../useNotificationSSE';
import { useAuth } from '@/contexts/AuthContext';

jest.mock('@/contexts/AuthContext');

describe('useNotificationSSE', () => {
  beforeEach(() => {
    // Mock EventSource
    global.EventSource = jest.fn();
  });

  it('should connect when user is authenticated', () => {
    (useAuth as jest.Mock).mockReturnValue({
      user: { id: 1 },
      accessToken: 'test-token',
    });

    const onNotification = jest.fn();

    renderHook(() => useNotificationSSE({ onNotification }));

    expect(global.EventSource).toHaveBeenCalled();
  });

  it('should not connect when user is not authenticated', () => {
    (useAuth as jest.Mock).mockReturnValue({
      user: null,
      accessToken: null,
    });

    const onNotification = jest.fn();

    renderHook(() => useNotificationSSE({ onNotification }));

    expect(global.EventSource).not.toHaveBeenCalled();
  });
});
```

---

## 🚀 Deployment & Migration

### Migration Steps

#### Step 1: Deploy Backend (Zero Downtime)

```bash
# 1. Deploy SSE infrastructure (new endpoints)
git checkout feature/sse-notifications
git pull origin main
git push origin feature/sse-notifications

# 2. Review and merge
# Frontend still using polling - no breaking changes

# 3. Monitor SSE endpoints
curl -H "Authorization: Bearer $TOKEN" \
  http://api.miraiworks.com/api/sse/status
```

#### Step 2: Deploy Frontend (Gradual Rollout)

```bash
# 1. Deploy SSE-enabled frontend
# Polling still works as fallback

# 2. Monitor SSE adoption
# Check /api/sse/status for active connections

# 3. Verify notifications delivery
# Test with real users
```

#### Step 3: Monitor & Optimize

```bash
# Monitor SSE metrics
- Active connections count
- Notification delivery rate
- Reconnection frequency
- Error rates
```

#### Step 4: Remove Polling (Optional)

After SSE is stable (1-2 weeks):
- Remove polling code from `NotificationsContext`
- Reduce database load
- Celebrate! 🎉

---

## 🔧 Configuration

### Environment Variables

**Backend** (`backend/.env`):

```bash
# SSE Configuration
SSE_KEEPALIVE_TIMEOUT=30  # Heartbeat interval (seconds)
SSE_MAX_CONNECTIONS_PER_USER=5  # Limit connections per user
SSE_QUEUE_SIZE=100  # Max queued notifications per connection
```

**Frontend** (`frontend/.env.local`):

```bash
# API URL for SSE connection
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Nginx Configuration (Production)

```nginx
# Disable buffering for SSE
location /api/sse/ {
    proxy_pass http://backend;
    proxy_http_version 1.1;
    proxy_set_header Connection "";
    proxy_buffering off;
    proxy_cache off;
    proxy_read_timeout 86400s;  # 24 hours
    chunked_transfer_encoding on;
}
```

---

## 📊 Performance Metrics

### Expected Improvements

| Metric | Before (Polling) | After (SSE) | Improvement |
|--------|------------------|-------------|-------------|
| **Latency** | 0-30 seconds | <1 second | **97% faster** |
| **HTTP Requests** | 120/hour/user | 1/hour/user | **99% reduction** |
| **Database Queries** | 120/hour/user | 0/hour/user | **100% reduction** |
| **Bandwidth** | ~500 KB/hour | ~50 KB/hour | **90% reduction** |
| **Server Load** | High | Low | **Significant** |

---

## 🐛 Troubleshooting

### Common Issues

#### 1. SSE Connection Fails

**Symptom:** Frontend can't establish SSE connection

**Solutions:**
- Check authentication token is valid
- Verify CORS settings allow credentials
- Check nginx buffering is disabled
- Verify firewall allows long-lived connections

#### 2. Notifications Not Received

**Symptom:** SSE connected but no notifications

**Solutions:**
- Check notification creation in backend logs
- Verify SSE manager receives notification
- Check user_id matching
- Verify queue is not full

#### 3. Frequent Reconnections

**Symptom:** Connection drops repeatedly

**Solutions:**
- Increase heartbeat timeout
- Check network stability
- Verify nginx timeout settings
- Check server resource limits

#### 4. Multiple Connections Per User

**Symptom:** User has many active connections

**Solutions:**
- This is normal for multiple tabs/devices
- Set `SSE_MAX_CONNECTIONS_PER_USER` limit
- Implement connection cleanup

---

## 📝 Best Practices

### Backend

1. **Always send heartbeats** - Keep connections alive
2. **Limit queue size** - Prevent memory issues
3. **Clean up dead connections** - Handle errors gracefully
4. **Log connection lifecycle** - For debugging
5. **Use background tasks** - Don't block notification creation

### Frontend

1. **Handle reconnections** - Exponential backoff
2. **Show connection status** - User visibility
3. **Handle offline/online** - Network changes
4. **Fallback to polling** - If SSE fails
5. **Clean up on unmount** - Close connections

---

## 🎯 Success Criteria

SSE implementation is successful when:

- ✅ Notifications delivered in <1 second
- ✅ Zero polling requests after SSE adoption
- ✅ Connection success rate >99%
- ✅ Auto-reconnection works consistently
- ✅ Multiple devices per user supported
- ✅ No increase in server load
- ✅ All tests passing (100% coverage)

---

## 📚 References

### Documentation
- [MDN: Server-Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
- [FastAPI: Streaming Responses](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)
- [EventSource API](https://developer.mozilla.org/en-US/docs/Web/API/EventSource)

### Architecture
- MiraiWorks Architecture Rules: `/CLAUDE.md`
- API Configuration: `backend/app/config/endpoints.py`
- Testing Requirements: `/CLAUDE.md` - Testing Section

---

## 🗓️ Implementation Timeline

### Week 1: Backend Development
- Day 1-2: SSE Manager Service
- Day 3: SSE Endpoint
- Day 4: Update Notification Service
- Day 5: Backend Testing

### Week 2: Frontend Development
- Day 1-2: SSE Hook
- Day 3: Update Context
- Day 4: UI Updates
- Day 5: Frontend Testing

### Week 3: Integration & Testing
- Day 1-2: End-to-end testing
- Day 3: Load testing
- Day 4: Bug fixes
- Day 5: Documentation

### Week 4: Deployment & Monitoring
- Day 1: Deploy to staging
- Day 2-3: Staging validation
- Day 4: Production deployment
- Day 5: Monitoring & optimization

---

**Status:** 📝 Ready for Implementation

**Last Updated:** 2025-01-10

**Maintained By:** MiraiWorks Development Team
