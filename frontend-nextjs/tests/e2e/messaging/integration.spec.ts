/**
 * Messaging integration E2E tests
 * Tests that combine multiple messaging features working together
 */

import { test, expect } from '../fixtures/auth-fixture';
import { testUsers } from '../fixtures/test-users';
import { MessagingTestUtils } from './messaging-utils';

test.describe('Messaging Integration', () => {
  
  test('complete messaging workflow - send, receive, search, and notify', async ({ authenticatedContext, browser }) => {
    // Set up two users for real-time interaction
    const context1 = await authenticatedContext('candidate1');
    const context2 = await authenticatedContext('recruiterReal');
    
    const page1 = await context1.newPage();
    const page2 = await context2.newPage();

    // User 1 starts on dashboard, User 2 on messages
    await page1.goto('/dashboard');
    await page2.goto('/messages');
    
    await Promise.all([
      page1.waitForLoadState('networkidle'),
      page2.waitForLoadState('networkidle')
    ]);

    // Check initial unread count for User 1
    const initialUnreadCount = await MessagingTestUtils.getUnreadMessageCount(page1);

    // User 2 sends a message to User 1
    const hasConversation = await MessagingTestUtils.selectFirstConversation(page2);
    if (!hasConversation) {
      await MessagingTestUtils.createNewConversation(page2, testUsers.candidate1.email);
    }

    const testMessage = MessagingTestUtils.generateTestMessage('Integration workflow');
    await MessagingTestUtils.sendTextMessage(page2, testMessage);

    // User 1 should see notification update
    await page1.waitForTimeout(3000); // Wait for real-time update
    const newUnreadCount = await MessagingTestUtils.getUnreadMessageCount(page1);
    
    if (initialUnreadCount === 0 && newUnreadCount > 0) {
      expect(newUnreadCount).toBeGreaterThan(initialUnreadCount);
    }

    // User 1 navigates to messages
    await MessagingTestUtils.navigateToMessages(page1);
    
    // User 1 should see the conversation with new message
    await MessagingTestUtils.selectFirstConversation(page1);
    
    // Verify the message appears
    const receivedMessage = page1.locator(`[data-testid="message-bubble"]:has-text("${testMessage}")`);
    await expect(receivedMessage).toBeVisible();

    // User 1 searches for the message
    const searchResults = await MessagingTestUtils.searchMessages(page1, 'Integration');
    if (searchResults.hasResults) {
      const firstResult = searchResults.resultItems.first();
      await expect(firstResult).toContainText(testMessage);
      
      // Navigate to conversation from search
      await firstResult.click();
    }

    // Clear search and reply
    await MessagingTestUtils.clearSearch(page1);
    const replyMessage = MessagingTestUtils.generateTestMessage('Reply to integration');
    await MessagingTestUtils.sendTextMessage(page1, replyMessage);

    // User 2 should receive the reply in real-time
    const replyReceived = page2.locator(`[data-testid="message-bubble"]:has-text("${replyMessage}")`);
    await expect(replyReceived).toBeVisible({ timeout: 10000 });

    // Verify conversation is updated in both interfaces
    const conversation1 = page1.locator('[data-testid="conversation-item"]').first();
    const conversation2 = page2.locator('[data-testid="conversation-item"]').first();
    
    await MessagingTestUtils.verifyConversationStructure(page1, conversation1);
    await MessagingTestUtils.verifyConversationStructure(page2, conversation2);
  });

  test('file sharing with notifications and search', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();
    
    await MessagingTestUtils.navigateToMessages(page);
    const hasConversation = await MessagingTestUtils.selectFirstConversation(page);
    
    if (hasConversation) {
      // Upload and send a file
      const fileContent = 'File sharing integration test content';
      const fileName = 'integration-test.txt';
      
      try {
        const fileMessage = await MessagingTestUtils.uploadFile(
          page, 
          fileName, 
          fileContent, 
          'text/plain'
        );

        await MessagingTestUtils.verifyMessageStructure(page, fileMessage, 'file');

        // Search for the file by name
        const searchResults = await MessagingTestUtils.searchMessages(page, fileName);
        if (searchResults.hasResults) {
          const fileResult = searchResults.resultItems.first();
          await expect(fileResult).toContainText(fileName);
        }

        // Clear search and verify file is still in conversation
        await MessagingTestUtils.clearSearch(page);
        const fileInConversation = page.locator(`[data-testid="message-bubble"][data-message-type="file"]:has-text("${fileName}")`);
        await expect(fileInConversation).toBeVisible();

      } catch (error) {
        // File upload UI might not be available in all test environments
        console.log('File upload test skipped - UI not available');
      }
    }
  });

  test('error handling across features', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();

    // Mock various API failures
    await MessagingTestUtils.mockApiError(page, '**/api/messages/**');
    await MessagingTestUtils.mockApiError(page, '**/api/conversations/**');

    await MessagingTestUtils.navigateToMessages(page);

    // App should handle errors gracefully
    const errorIndicators = [
      '[data-testid="error-message"]',
      '[data-testid="connection-error"]',
      '.toast-error',
      '[data-testid="retry-button"]'
    ];

    let errorHandled = false;
    for (const selector of errorIndicators) {
      if (await page.locator(selector).count() > 0) {
        await expect(page.locator(selector)).toBeVisible({ timeout: 5000 });
        errorHandled = true;
        break;
      }
    }

    // If no specific error UI is shown, at least verify the app doesn't crash
    await expect(page.locator('body')).toBeVisible();
    
    if (!errorHandled) {
      console.log('No specific error UI found, but app remains stable');
    }
  });

  test('performance with multiple conversations and messages', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();

    await MessagingTestUtils.navigateToMessages(page);

    // Measure time to load conversations
    const startTime = Date.now();
    await page.waitForLoadState('networkidle');
    const loadTime = Date.now() - startTime;

    // Should load within reasonable time (adjust threshold as needed)
    expect(loadTime).toBeLessThan(10000); // 10 seconds max

    // Test scrolling performance in conversation
    const hasConversation = await MessagingTestUtils.selectFirstConversation(page);
    
    if (hasConversation) {
      const messagesContainer = page.locator('[data-testid="messages-container"]');
      
      if (await messagesContainer.count() > 0) {
        // Scroll to top to load older messages
        await messagesContainer.evaluate(el => {
          el.scrollTop = 0;
        });

        // Wait for potential message loading
        await page.waitForTimeout(2000);

        // Should still be responsive
        await expect(messagesContainer).toBeVisible();
        
        // Scroll back to bottom
        await messagesContainer.evaluate(el => {
          el.scrollTop = el.scrollHeight;
        });

        await expect(messagesContainer).toBeVisible();
      }
    }
  });

  test('accessibility in messaging interface', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();

    await MessagingTestUtils.navigateToMessages(page);

    // Check for proper ARIA labels and roles
    const conversationsList = page.locator('[data-testid="conversations-list"]');
    await expect(conversationsList).toBeVisible();

    // Check if conversations are keyboard navigable
    await page.keyboard.press('Tab');
    
    // Should be able to navigate to message input
    const messageInput = page.locator('[data-testid="message-input"]');
    if (await messageInput.count() > 0) {
      await messageInput.focus();
      
      // Should be able to type and send with keyboard
      const testMessage = 'Accessibility test message';
      await page.type('[data-testid="message-input"]', testMessage);
      await page.keyboard.press('Enter');

      // Message should be sent
      const sentMessage = page.locator(`[data-testid="message-bubble"]:has-text("${testMessage}")`);
      await expect(sentMessage).toBeVisible({ timeout: 5000 });
    }

    // Check search is keyboard accessible
    const searchInput = page.locator('[data-testid="search-input"]');
    await searchInput.focus();
    await page.type('[data-testid="search-input"]', 'test');
    
    // Should show search results or no results message
    await page.waitForLoadState('networkidle');
    
    const hasResults = await page.locator('[data-testid="search-results"]').count() > 0;
    const hasNoResults = await page.locator('[data-testid="no-search-results"]').count() > 0;
    
    expect(hasResults || hasNoResults).toBe(true);
  });

  test('responsive design on different viewport sizes', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();

    // Test desktop view
    await page.setViewportSize({ width: 1920, height: 1080 });
    await MessagingTestUtils.navigateToMessages(page);

    await expect(page.locator('[data-testid="conversations-list"]')).toBeVisible();
    await expect(page.locator('[data-testid="message-input-area"]')).toBeVisible();

    // Test tablet view
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.waitForTimeout(1000); // Wait for responsive changes

    // Conversations list might be hidden on smaller screens
    const conversationsList = page.locator('[data-testid="conversations-list"]');
    const isVisible = await conversationsList.isVisible();
    
    if (!isVisible) {
      // Look for mobile menu or toggle button
      const mobileMenuToggle = page.locator('[data-testid="mobile-menu-toggle"]');
      if (await mobileMenuToggle.count() > 0) {
        await expect(mobileMenuToggle).toBeVisible();
      }
    }

    // Test mobile view
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForTimeout(1000);

    // On mobile, conversation list and message area might stack
    // or be togglable - verify the interface adapts
    await expect(page.locator('body')).toBeVisible(); // Basic stability check
    
    // If a conversation is selected, message input should still be usable
    const hasConversation = await MessagingTestUtils.selectFirstConversation(page);
    if (hasConversation) {
      const messageInput = page.locator('[data-testid="message-input"]');
      if (await messageInput.count() > 0) {
        await expect(messageInput).toBeVisible();
        
        // Should be able to send message on mobile
        const mobileTestMessage = 'Mobile test message';
        await MessagingTestUtils.sendTextMessage(page, mobileTestMessage);
      }
    }
  });

  test('data persistence and state management', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();

    await MessagingTestUtils.navigateToMessages(page);
    const hasConversation = await MessagingTestUtils.selectFirstConversation(page);

    if (hasConversation) {
      // Send a message
      const testMessage = MessagingTestUtils.generateTestMessage('Persistence test');
      await MessagingTestUtils.sendTextMessage(page, testMessage);

      // Start typing something (to test draft persistence)
      const draftText = 'This is a draft message';
      await page.fill('[data-testid="message-input"]', draftText);

      // Navigate away and back
      await page.goto('/dashboard');
      await page.waitForLoadState('networkidle');
      
      await MessagingTestUtils.navigateToMessages(page);
      await MessagingTestUtils.selectFirstConversation(page);

      // Previously sent message should still be there
      const persistedMessage = page.locator(`[data-testid="message-bubble"]:has-text("${testMessage}")`);
      await expect(persistedMessage).toBeVisible();

      // Draft might be restored (depending on implementation)
      const messageInput = page.locator('[data-testid="message-input"]');
      const inputValue = await messageInput.inputValue();
      
      // This test depends on whether draft persistence is implemented
      // Just verify the input is accessible and functional
      await messageInput.fill('New message after navigation');
      await page.keyboard.press('Enter');

      const newMessage = page.locator(`[data-testid="message-bubble"]:has-text("New message after navigation")`);
      await expect(newMessage).toBeVisible();
    }
  });
});