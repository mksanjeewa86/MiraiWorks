/**
 * Utility functions for messaging E2E tests
 * Common helper functions to reduce code duplication
 */

import { Page, BrowserContext, expect } from '@playwright/test';
import { testUsers } from '../fixtures/test-users';

export class MessagingTestUtils {
  
  /**
   * Navigate to messages and wait for page load
   */
  static async navigateToMessages(page: Page) {
    await page.goto('/messages');
    await page.waitForLoadState('networkidle');
    
    // Verify we're on the messages page
    await expect(page.locator('[data-testid="conversations-list"]')).toBeVisible();
  }

  /**
   * Select the first available conversation
   */
  static async selectFirstConversation(page: Page) {
    const firstConversation = page.locator('[data-testid="conversation-item"]').first();
    
    if (await firstConversation.count() > 0) {
      await firstConversation.click();
      await expect(page.locator('[data-testid="conversation-header"]')).toBeVisible();
      return true;
    }
    
    return false;
  }

  /**
   * Create a new conversation with a specific user
   */
  static async createNewConversation(page: Page, recipientEmail: string) {
    const newMessageButton = page.locator('[data-testid="new-message-button"]');
    
    if (await newMessageButton.count() > 0) {
      await newMessageButton.click();
      
      const recipientSearch = page.locator('[data-testid="recipient-search"]');
      await recipientSearch.fill(recipientEmail);
      
      const recipientOption = page.locator('[data-testid="recipient-option"]').first();
      await recipientOption.click();
      
      return true;
    }
    
    return false;
  }

  /**
   * Send a text message and verify it appears
   */
  static async sendTextMessage(page: Page, messageText: string) {
    await page.fill('[data-testid="message-input"]', messageText);
    await page.click('[data-testid="send-button"]');
    
    // Verify message appears
    const sentMessage = page.locator(`[data-testid="message-bubble"]:has-text("${messageText}")`);
    await expect(sentMessage).toBeVisible({ timeout: 10000 });
    
    // Verify input is cleared
    await expect(page.locator('[data-testid="message-input"]')).toHaveValue('');
    
    return sentMessage;
  }

  /**
   * Search for messages and return results
   */
  static async searchMessages(page: Page, query: string) {
    await page.fill('[data-testid="search-input"]', query);
    await page.waitForLoadState('networkidle');
    
    const searchResults = page.locator('[data-testid="search-results"]');
    const hasResults = await searchResults.count() > 0;
    
    return {
      hasResults,
      searchResults,
      resultItems: searchResults.locator('[data-testid="search-result-item"]')
    };
  }

  /**
   * Clear search and return to conversations list
   */
  static async clearSearch(page: Page) {
    await page.fill('[data-testid="search-input"]', '');
    await page.waitForLoadState('networkidle');
    
    await expect(page.locator('[data-testid="search-results"]')).not.toBeVisible();
    await expect(page.locator('[data-testid="conversations-list"]')).toBeVisible();
  }

  /**
   * Get unread message count from notification badge
   */
  static async getUnreadMessageCount(page: Page) {
    const messagesNav = page.locator('[data-testid="messages-nav"]');
    const notificationBadge = messagesNav.locator('[data-testid="notification-badge"]');
    
    if (await notificationBadge.count() > 0) {
      const badgeText = await notificationBadge.textContent();
      return parseInt(badgeText || '0');
    }
    
    return 0;
  }

  /**
   * Open notification dropdown and return notification items
   */
  static async openNotificationDropdown(page: Page) {
    const notificationButton = page.locator('[data-testid="notifications-button"]');
    
    if (await notificationButton.count() > 0) {
      await notificationButton.click();
      
      const dropdown = page.locator('[data-testid="notifications-dropdown"]');
      await expect(dropdown).toBeVisible();
      
      return {
        dropdown,
        items: dropdown.locator('[data-testid="notification-item"]')
      };
    }
    
    return null;
  }

  /**
   * Upload a file in the current conversation
   */
  static async uploadFile(page: Page, fileName: string, content: string | Buffer, mimeType: string) {
    const attachButton = page.locator('[data-testid="attach-file-button"]');
    
    if (await attachButton.count() > 0) {
      await attachButton.click();
      
      const fileInput = page.locator('[data-testid="file-input"]');
      if (await fileInput.count() > 0) {
        await fileInput.setInputFiles({
          name: fileName,
          mimeType: mimeType,
          buffer: Buffer.isBuffer(content) ? content : Buffer.from(content)
        });
        
        // Wait for file processing
        await page.waitForTimeout(1000);
        
        const sendButton = page.locator('[data-testid="send-file-button"]').or(
          page.locator('[data-testid="send-button"]')
        );
        
        if (await sendButton.count() > 0) {
          await sendButton.click();
          
          // Verify file message appears
          const fileMessage = page.locator('[data-testid="message-bubble"][data-message-type="file"]');
          await expect(fileMessage).toBeVisible({ timeout: 15000 });
          
          return fileMessage;
        }
      }
    }
    
    throw new Error('Could not upload file - UI elements not found');
  }

  /**
   * Wait for typing indicator to appear/disappear
   */
  static async waitForTypingIndicator(page: Page, shouldBeVisible: boolean, timeout: number = 5000) {
    const typingIndicator = page.locator('[data-testid="typing-indicator"]');
    
    if (shouldBeVisible) {
      await expect(typingIndicator).toBeVisible({ timeout });
    } else {
      await expect(typingIndicator).not.toBeVisible({ timeout });
    }
  }

  /**
   * Verify message delivery status
   */
  static async verifyMessageStatus(page: Page, messageText: string, expectedStatus: string) {
    const message = page.locator(`[data-testid="message-bubble"]:has-text("${messageText}")`);
    const messageStatus = message.locator('[data-testid="message-status"]');
    
    if (await messageStatus.count() > 0) {
      const actualStatus = await messageStatus.getAttribute('data-status');
      expect(actualStatus).toBe(expectedStatus);
    }
  }

  /**
   * Simulate WebSocket events for real-time testing
   */
  static async simulateWebSocketEvent(page: Page, eventType: string, data: any) {
    await page.evaluate(({ eventType, data }) => {
      // Dispatch custom event to simulate WebSocket message
      window.dispatchEvent(new CustomEvent(`websocket-${eventType}`, { detail: data }));
    }, { eventType, data });
  }

  /**
   * Mock API responses for testing error scenarios
   */
  static async mockApiError(page: Page, apiPattern: string, errorType: 'abort' | 'fulfill' = 'abort') {
    await page.route(apiPattern, (route) => {
      if (errorType === 'abort') {
        route.abort('failed');
      } else {
        route.fulfill({
          status: 500,
          body: JSON.stringify({ error: 'Internal Server Error' })
        });
      }
    });
  }

  /**
   * Create test data for conversations
   */
  static async createTestConversation(page: Page, otherUserEmail: string, messageCount: number = 3) {
    const messages = [];
    
    // Navigate to messages
    await this.navigateToMessages(page);
    
    // Create or select conversation
    let conversationExists = await this.selectFirstConversation(page);
    if (!conversationExists) {
      await this.createNewConversation(page, otherUserEmail);
    }
    
    // Send test messages
    for (let i = 1; i <= messageCount; i++) {
      const messageText = `Test message ${i} - ${Date.now()}`;
      const message = await this.sendTextMessage(page, messageText);
      messages.push({ text: messageText, element: message });
      
      // Small delay between messages
      await page.waitForTimeout(500);
    }
    
    return messages;
  }

  /**
   * Verify conversation list item structure
   */
  static async verifyConversationStructure(page: Page, conversationItem: any) {
    // Check required elements
    await expect(conversationItem.locator('[data-testid="other-user-name"]')).toBeVisible();
    await expect(conversationItem.locator('[data-testid="last-message-preview"]')).toBeVisible();
    await expect(conversationItem.locator('[data-testid="conversation-timestamp"]')).toBeVisible();
    
    // Optional elements
    const unreadIndicator = conversationItem.locator('[data-testid="unread-indicator"]');
    const onlineStatus = conversationItem.locator('[data-testid="online-status"]');
    
    // These might not be visible for all conversations
    if (await unreadIndicator.count() > 0) {
      await expect(unreadIndicator).toBeVisible();
    }
    
    if (await onlineStatus.count() > 0) {
      await expect(onlineStatus).toBeVisible();
    }
  }

  /**
   * Verify message bubble structure
   */
  static async verifyMessageStructure(page: Page, messageElement: any, messageType: 'text' | 'file' = 'text') {
    // Common elements for all messages
    await expect(messageElement.locator('[data-testid="message-content"]')).toBeVisible();
    await expect(messageElement.locator('[data-testid="message-timestamp"]')).toBeVisible();
    
    // Message type specific elements
    if (messageType === 'file') {
      await expect(messageElement.locator('[data-testid="file-icon"]')).toBeVisible();
      await expect(messageElement.locator('[data-testid="file-name"]')).toBeVisible();
      await expect(messageElement.locator('[data-testid="file-size"]')).toBeVisible();
    }
    
    // Optional elements
    const messageStatus = messageElement.locator('[data-testid="message-status"]');
    if (await messageStatus.count() > 0) {
      await expect(messageStatus).toBeVisible();
    }
  }

  /**
   * Test user credentials helper
   */
  static getTestUser(userType: keyof typeof testUsers) {
    return testUsers[userType];
  }

  /**
   * Generate unique test message
   */
  static generateTestMessage(prefix: string = 'Test') {
    return `${prefix} message ${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Wait for page to be in a stable state
   */
  static async waitForStableState(page: Page, timeout: number = 5000) {
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000); // Additional buffer for UI updates
  }
}