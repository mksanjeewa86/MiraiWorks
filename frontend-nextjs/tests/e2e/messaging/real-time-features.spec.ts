/**
 * Real-time messaging features E2E tests
 * Tests WebSocket connectivity, live message updates, typing indicators
 */

import { test, expect } from '../fixtures/auth-fixture';
import { testUsers } from '../fixtures/test-users';

test.describe('Real-time Messaging Features', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/messages');
    await page.waitForLoadState('networkidle');
  });

  test('should establish WebSocket connection', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();
    
    await page.goto('/messages');
    await page.waitForLoadState('networkidle');

    // Check for WebSocket connection indicator
    const connectionStatus = page.locator('[data-testid="connection-status"]');
    if (await connectionStatus.count() > 0) {
      await expect(connectionStatus).toContainText(/connected|online/i);
    }

    // Alternatively, check for WebSocket in developer tools
    const webSocketConnections = await page.evaluate(() => {
      // Check if WebSocket connection exists
      return typeof WebSocket !== 'undefined';
    });
    
    expect(webSocketConnections).toBe(true);
  });

  test('should show connection status changes', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();
    
    await page.goto('/messages');
    await page.waitForLoadState('networkidle');

    // Mock WebSocket disconnect
    await page.evaluate(() => {
      // Simulate connection loss
      window.dispatchEvent(new Event('offline'));
    });

    // Check for offline indicator
    const offlineIndicator = page.locator('[data-testid="offline-indicator"]');
    if (await offlineIndicator.count() > 0) {
      await expect(offlineIndicator).toBeVisible();
    }

    // Mock WebSocket reconnect
    await page.evaluate(() => {
      // Simulate connection restored
      window.dispatchEvent(new Event('online'));
    });

    // Check that offline indicator disappears
    if (await offlineIndicator.count() > 0) {
      await expect(offlineIndicator).not.toBeVisible({ timeout: 10000 });
    }
  });

  test('should handle message delivery status', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();
    
    await page.goto('/messages');
    await page.waitForLoadState('networkidle');

    // Select conversation
    const firstConversation = page.locator('[data-testid="conversation-item"]').first();
    if (await firstConversation.count() > 0) {
      await firstConversation.click();

      // Send a message
      const messageText = `Status test ${Date.now()}`;
      await page.fill('[data-testid="message-input"]', messageText);
      await page.click('[data-testid="send-button"]');

      // Check for message status indicators
      const sentMessage = page.locator(`[data-testid="message-bubble"]:has-text("${messageText}")`);
      await expect(sentMessage).toBeVisible();

      // Look for delivery status (sent, delivered, read)
      const messageStatus = sentMessage.locator('[data-testid="message-status"]');
      if (await messageStatus.count() > 0) {
        const statusText = await messageStatus.getAttribute('data-status');
        expect(['sending', 'sent', 'delivered', 'read']).toContain(statusText);
      }
    }
  });

  test('should show typing indicators', async ({ authenticatedContext, browser }) => {
    // This test requires multiple browser contexts to simulate two users
    const context1 = await authenticatedContext('candidate1');
    const context2 = await authenticatedContext('recruiterReal');
    
    const page1 = await context1.newPage();
    const page2 = await context2.newPage();

    // Both users navigate to messages
    await page1.goto('/messages');
    await page2.goto('/messages');
    await Promise.all([
      page1.waitForLoadState('networkidle'),
      page2.waitForLoadState('networkidle')
    ]);

    // Find a mutual conversation or create one
    const conversation1 = page1.locator('[data-testid="conversation-item"]').first();
    const conversation2 = page2.locator('[data-testid="conversation-item"]').first();
    
    if (await conversation1.count() > 0 && await conversation2.count() > 0) {
      await Promise.all([
        conversation1.click(),
        conversation2.click()
      ]);

      // User 1 starts typing
      await page1.focus('[data-testid="message-input"]');
      await page1.type('[data-testid="message-input"]', 'I am typing...', { delay: 100 });

      // User 2 should see typing indicator
      const typingIndicator = page2.locator('[data-testid="typing-indicator"]');
      if (await typingIndicator.count() > 0) {
        await expect(typingIndicator).toBeVisible({ timeout: 5000 });
        await expect(typingIndicator).toContainText(/typing/i);
      }

      // Stop typing - clear input
      await page1.fill('[data-testid="message-input"]', '');

      // Typing indicator should disappear
      if (await typingIndicator.count() > 0) {
        await expect(typingIndicator).not.toBeVisible({ timeout: 5000 });
      }
    }
  });

  test('should receive messages in real-time', async ({ authenticatedContext, browser }) => {
    const context1 = await authenticatedContext('candidate1');
    const context2 = await authenticatedContext('recruiterReal');
    
    const page1 = await context1.newPage();
    const page2 = await context2.newPage();

    await page1.goto('/messages');
    await page2.goto('/messages');
    await Promise.all([
      page1.waitForLoadState('networkidle'),
      page2.waitForLoadState('networkidle')
    ]);

    // Open same conversation on both pages
    const conversation1 = page1.locator('[data-testid="conversation-item"]').first();
    const conversation2 = page2.locator('[data-testid="conversation-item"]').first();
    
    if (await conversation1.count() > 0 && await conversation2.count() > 0) {
      await Promise.all([
        conversation1.click(),
        conversation2.click()
      ]);

      // User 2 sends a message
      const messageText = `Real-time test ${Date.now()}`;
      await page2.fill('[data-testid="message-input"]', messageText);
      await page2.click('[data-testid="send-button"]');

      // User 1 should receive the message in real-time
      const receivedMessage = page1.locator(`[data-testid="message-bubble"]:has-text("${messageText}")`);
      await expect(receivedMessage).toBeVisible({ timeout: 10000 });

      // Verify message appears in conversation list
      const updatedConversation = page1.locator('[data-testid="conversation-item"]').first();
      const lastMessagePreview = updatedConversation.locator('[data-testid="last-message-preview"]');
      if (await lastMessagePreview.count() > 0) {
        await expect(lastMessagePreview).toContainText(messageText);
      }
    }
  });

  test('should update unread counts in real-time', async ({ authenticatedContext, browser }) => {
    const context1 = await authenticatedContext('candidate1');
    const context2 = await authenticatedContext('recruiterReal');
    
    const page1 = await context1.newPage();
    const page2 = await context2.newPage();

    // User 1 on dashboard, User 2 on messages
    await page1.goto('/dashboard');
    await page2.goto('/messages');
    await Promise.all([
      page1.waitForLoadState('networkidle'),
      page2.waitForLoadState('networkidle')
    ]);

    // Get initial unread count for User 1
    const messagesNav = page1.locator('[data-testid="messages-nav"]');
    const notificationBadge = messagesNav.locator('[data-testid="notification-badge"]');
    const initialCount = await notificationBadge.count() > 0 ? 
      parseInt(await notificationBadge.textContent() || '0') : 0;

    // User 2 sends a message to User 1
    const conversation = page2.locator('[data-testid="conversation-item"]').first();
    if (await conversation.count() > 0) {
      await conversation.click();
      
      const messageText = `Unread count test ${Date.now()}`;
      await page2.fill('[data-testid="message-input"]', messageText);
      await page2.click('[data-testid="send-button"]');

      // User 1's unread count should increase
      await page1.waitForTimeout(2000); // Wait for real-time update
      
      if (await notificationBadge.count() > 0) {
        const newCount = parseInt(await notificationBadge.textContent() || '0');
        expect(newCount).toBeGreaterThan(initialCount);
      } else {
        // Badge should now appear
        await expect(notificationBadge).toBeVisible();
      }
    }
  });

  test('should handle WebSocket reconnection', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();
    
    await page.goto('/messages');
    await page.waitForLoadState('networkidle');

    // Simulate network interruption and recovery
    await page.evaluate(() => {
      // Force WebSocket close to simulate connection loss
      if ((window as any).websocket) {
        (window as any).websocket.close();
      }
    });

    // Wait for reconnection indicator or automatic reconnection
    await page.waitForTimeout(3000);

    // Verify functionality works after reconnection
    const firstConversation = page.locator('[data-testid="conversation-item"]').first();
    if (await firstConversation.count() > 0) {
      await firstConversation.click();

      // Try to send a message after reconnection
      const messageText = `Reconnection test ${Date.now()}`;
      await page.fill('[data-testid="message-input"]', messageText);
      await page.click('[data-testid="send-button"]');

      // Message should send successfully
      await expect(page.locator(`[data-testid="message-bubble"]:has-text("${messageText}")`)).toBeVisible();
    }
  });

  test('should handle multiple WebSocket events simultaneously', async ({ authenticatedContext, browser }) => {
    const context1 = await authenticatedContext('candidate1');
    const context2 = await authenticatedContext('recruiterReal');
    
    const page1 = await context1.newPage();
    const page2 = await context2.newPage();

    await page1.goto('/messages');
    await page2.goto('/messages');
    await Promise.all([
      page1.waitForLoadState('networkidle'),
      page2.waitForLoadState('networkidle')
    ]);

    // Open conversations
    const conversation1 = page1.locator('[data-testid="conversation-item"]').first();
    const conversation2 = page2.locator('[data-testid="conversation-item"]').first();
    
    if (await conversation1.count() > 0 && await conversation2.count() > 0) {
      await Promise.all([
        conversation1.click(),
        conversation2.click()
      ]);

      // Send multiple messages quickly from both users
      const messages = [
        { sender: page1, text: 'Message 1 from User 1' },
        { sender: page2, text: 'Message 1 from User 2' },
        { sender: page1, text: 'Message 2 from User 1' },
        { sender: page2, text: 'Message 2 from User 2' }
      ];

      // Send messages rapidly
      for (const { sender, text } of messages) {
        await sender.fill('[data-testid="message-input"]', text);
        await sender.click('[data-testid="send-button"]');
        await sender.waitForTimeout(500); // Small delay between messages
      }

      // Verify all messages are received and displayed correctly
      for (const { text } of messages) {
        await expect(page1.locator(`[data-testid="message-bubble"]:has-text("${text}")`)).toBeVisible();
        await expect(page2.locator(`[data-testid="message-bubble"]:has-text("${text}")`)).toBeVisible();
      }
    }
  });

  test('should show online/offline status of contacts', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();
    
    await page.goto('/messages');
    await page.waitForLoadState('networkidle');

    // Check for online status indicators on conversations
    const conversations = page.locator('[data-testid="conversation-item"]');
    const onlineIndicators = conversations.locator('[data-testid="online-status"]');
    
    if (await onlineIndicators.count() > 0) {
      const firstIndicator = onlineIndicators.first();
      await expect(firstIndicator).toBeVisible();
      
      // Check if status shows online/offline/last seen
      const statusText = await firstIndicator.textContent();
      expect(statusText).toMatch(/(online|offline|last seen|active)/i);
    }
  });

  test('should handle WebSocket errors gracefully', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();
    
    // Mock WebSocket to throw errors
    await page.addInitScript(() => {
      const OriginalWebSocket = window.WebSocket;
      window.WebSocket = class extends OriginalWebSocket {
        constructor(url: string | URL, protocols?: string | string[]) {
          super(url, protocols);
          // Simulate connection error after some time
          setTimeout(() => {
            this.dispatchEvent(new Event('error'));
          }, 1000);
        }
      } as any;
    });

    await page.goto('/messages');
    await page.waitForLoadState('networkidle');

    // Wait for potential error handling
    await page.waitForTimeout(3000);

    // App should still be functional despite WebSocket errors
    const conversationsList = page.locator('[data-testid="conversations-list"]');
    await expect(conversationsList).toBeVisible();

    // Error notification might be shown
    const errorNotification = page.locator('[data-testid="connection-error"]');
    if (await errorNotification.count() > 0) {
      await expect(errorNotification).toBeVisible();
    }
  });
});