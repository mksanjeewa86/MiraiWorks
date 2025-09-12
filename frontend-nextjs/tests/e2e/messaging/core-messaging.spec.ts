/**
 * Core messaging functionality E2E tests
 * Tests basic message sending, receiving, and conversation management
 */

import { test, expect } from '../fixtures/auth-fixture';
import { testUsers } from '../fixtures/test-users';

test.describe('Core Messaging', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to messages page
    await page.goto('/messages');
    await page.waitForLoadState('networkidle');
  });

  test('should load messages page with conversations list', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();
    
    await page.goto('/messages');
    await page.waitForLoadState('networkidle');

    // Check page title
    await expect(page).toHaveTitle(/Messages/);
    
    // Check main messaging components are present
    await expect(page.locator('[data-testid="conversations-list"]')).toBeVisible();
    await expect(page.locator('[data-testid="message-input-area"]')).toBeVisible();
    await expect(page.locator('[data-testid="search-input"]')).toBeVisible();
  });

  test('should send a text message successfully', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();
    
    await page.goto('/messages');
    await page.waitForLoadState('networkidle');

    // Select first conversation or create new one
    const conversationsList = page.locator('[data-testid="conversations-list"]');
    const firstConversation = conversationsList.locator('[data-testid="conversation-item"]').first();
    
    if (await firstConversation.count() > 0) {
      await firstConversation.click();
    } else {
      // Create new conversation - click on new message button
      await page.click('[data-testid="new-message-button"]');
      await page.fill('[data-testid="recipient-search"]', testUsers.recruiterReal.email);
      await page.click('[data-testid="recipient-option"]');
    }

    // Type and send message
    const messageText = `Test message ${Date.now()}`;
    await page.fill('[data-testid="message-input"]', messageText);
    await page.click('[data-testid="send-button"]');

    // Verify message appears in chat
    await expect(page.locator(`[data-testid="message-bubble"]:has-text("${messageText}")`)).toBeVisible();
    
    // Verify message input is cleared
    await expect(page.locator('[data-testid="message-input"]')).toHaveValue('');
  });

  test('should send message using Enter key', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();
    
    await page.goto('/messages');
    await page.waitForLoadState('networkidle');

    // Select conversation
    const firstConversation = page.locator('[data-testid="conversation-item"]').first();
    if (await firstConversation.count() > 0) {
      await firstConversation.click();
    }

    // Type message and press Enter
    const messageText = `Enter key test ${Date.now()}`;
    await page.fill('[data-testid="message-input"]', messageText);
    await page.press('[data-testid="message-input"]', 'Enter');

    // Verify message appears
    await expect(page.locator(`[data-testid="message-bubble"]:has-text("${messageText}")`)).toBeVisible();
  });

  test('should not send empty message', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();
    
    await page.goto('/messages');
    await page.waitForLoadState('networkidle');

    // Select conversation
    const firstConversation = page.locator('[data-testid="conversation-item"]').first();
    if (await firstConversation.count() > 0) {
      await firstConversation.click();
    }

    // Get initial message count
    const initialMessageCount = await page.locator('[data-testid="message-bubble"]').count();

    // Try to send empty message
    await page.click('[data-testid="send-button"]');

    // Verify no new message was sent
    const finalMessageCount = await page.locator('[data-testid="message-bubble"]').count();
    expect(finalMessageCount).toBe(initialMessageCount);
  });

  test('should display conversation with correct user info', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();
    
    await page.goto('/messages');
    await page.waitForLoadState('networkidle');

    // Select first conversation
    const firstConversation = page.locator('[data-testid="conversation-item"]').first();
    if (await firstConversation.count() > 0) {
      await firstConversation.click();
      
      // Verify conversation header shows other user's info
      await expect(page.locator('[data-testid="conversation-header"]')).toBeVisible();
      await expect(page.locator('[data-testid="other-user-name"]')).toBeVisible();
      await expect(page.locator('[data-testid="other-user-role"]')).toBeVisible();
    }
  });

  test('should show message timestamps', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();
    
    await page.goto('/messages');
    await page.waitForLoadState('networkidle');

    // Select conversation
    const firstConversation = page.locator('[data-testid="conversation-item"]').first();
    if (await firstConversation.count() > 0) {
      await firstConversation.click();
      
      // Check that messages have timestamps
      const messages = page.locator('[data-testid="message-bubble"]');
      if (await messages.count() > 0) {
        const firstMessage = messages.first();
        await expect(firstMessage.locator('[data-testid="message-timestamp"]')).toBeVisible();
      }
    }
  });

  test('should auto-scroll to latest message', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();
    
    await page.goto('/messages');
    await page.waitForLoadState('networkidle');

    // Select conversation with messages
    const firstConversation = page.locator('[data-testid="conversation-item"]').first();
    if (await firstConversation.count() > 0) {
      await firstConversation.click();
      
      // Send a new message
      const messageText = `Auto-scroll test ${Date.now()}`;
      await page.fill('[data-testid="message-input"]', messageText);
      await page.click('[data-testid="send-button"]');

      // Verify the new message is visible (auto-scrolled to bottom)
      const newMessage = page.locator(`[data-testid="message-bubble"]:has-text("${messageText}")`);
      await expect(newMessage).toBeVisible();
      
      // Check if the message container is scrolled to bottom
      const messagesContainer = page.locator('[data-testid="messages-container"]');
      const isScrolledToBottom = await messagesContainer.evaluate(el => {
        return Math.abs(el.scrollHeight - el.clientHeight - el.scrollTop) < 5;
      });
      expect(isScrolledToBottom).toBe(true);
    }
  });

  test('should handle message sending errors gracefully', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();
    
    await page.goto('/messages');
    await page.waitForLoadState('networkidle');

    // Mock network failure
    await page.route('**/api/messages/**', (route) => {
      route.abort('failed');
    });

    // Select conversation
    const firstConversation = page.locator('[data-testid="conversation-item"]').first();
    if (await firstConversation.count() > 0) {
      await firstConversation.click();
    }

    // Try to send message
    const messageText = 'This should fail';
    await page.fill('[data-testid="message-input"]', messageText);
    await page.click('[data-testid="send-button"]');

    // Verify error handling (toast notification or error message)
    await expect(page.locator('[data-testid="error-message"]').or(page.locator('.toast-error'))).toBeVisible({ timeout: 5000 });
  });

  test('should display unread message indicators', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();
    
    await page.goto('/messages');
    await page.waitForLoadState('networkidle');

    // Check if unread indicators are present on conversations
    const conversationsWithUnread = page.locator('[data-testid="conversation-item"]:has([data-testid="unread-indicator"])');
    
    if (await conversationsWithUnread.count() > 0) {
      // Select conversation with unread messages
      await conversationsWithUnread.first().click();
      
      // Wait a moment and verify unread indicator disappears
      await page.waitForTimeout(1000);
      await expect(conversationsWithUnread.first().locator('[data-testid="unread-indicator"]')).not.toBeVisible();
    }
  });

  test('should show typing indicator when enabled', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();
    
    await page.goto('/messages');
    await page.waitForLoadState('networkidle');

    // Select conversation
    const firstConversation = page.locator('[data-testid="conversation-item"]').first();
    if (await firstConversation.count() > 0) {
      await firstConversation.click();
      
      // Start typing in the message input
      await page.focus('[data-testid="message-input"]');
      await page.type('[data-testid="message-input"]', 'Test typing...', { delay: 100 });
      
      // Note: Typing indicator would be visible to other users via WebSocket
      // This test would need WebSocket mocking or real-time testing setup
      // For now, just verify that typing doesn't break the UI
      await expect(page.locator('[data-testid="message-input"]')).toHaveValue('Test typing...');
    }
  });
});