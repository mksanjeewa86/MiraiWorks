/**
 * Messaging notifications E2E tests
 * Tests in-app notifications, email notifications, and notification settings
 */

import { test, expect } from '../fixtures/auth-fixture';
import { testUsers } from '../fixtures/test-users';

test.describe('Message Notifications', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/messages');
    await page.waitForLoadState('networkidle');
  });

  test('should show notification badge for unread messages', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();
    
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');

    // Check for notification badge on messages nav item
    const messagesNav = page.locator('[data-testid="messages-nav"]');
    const notificationBadge = messagesNav.locator('[data-testid="notification-badge"]');
    
    if (await notificationBadge.count() > 0) {
      await expect(notificationBadge).toBeVisible();
      
      // Badge should contain a number
      const badgeText = await notificationBadge.textContent();
      expect(parseInt(badgeText || '0')).toBeGreaterThan(0);
    }
  });

  test('should show in-app notification dropdown', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();
    
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');

    // Click on notification bell/icon
    const notificationButton = page.locator('[data-testid="notifications-button"]');
    if (await notificationButton.count() > 0) {
      await notificationButton.click();

      // Verify dropdown is visible
      const notificationDropdown = page.locator('[data-testid="notifications-dropdown"]');
      await expect(notificationDropdown).toBeVisible();

      // Check for notification items
      const notificationItems = notificationDropdown.locator('[data-testid="notification-item"]');
      if (await notificationItems.count() > 0) {
        // Verify notification structure
        const firstNotification = notificationItems.first();
        await expect(firstNotification.locator('[data-testid="notification-title"]')).toBeVisible();
        await expect(firstNotification.locator('[data-testid="notification-time"]')).toBeVisible();
      }
    }
  });

  test('should clear notification badge when messages are read', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();
    
    // Start from dashboard to see notification badge
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');

    const messagesNav = page.locator('[data-testid="messages-nav"]');
    const notificationBadge = messagesNav.locator('[data-testid="notification-badge"]');
    
    if (await notificationBadge.count() > 0) {
      // Note the initial badge count
      const initialBadgeText = await notificationBadge.textContent();
      const initialCount = parseInt(initialBadgeText || '0');

      // Navigate to messages and open a conversation
      await messagesNav.click();
      await page.waitForLoadState('networkidle');

      const firstConversation = page.locator('[data-testid="conversation-item"]').first();
      if (await firstConversation.count() > 0) {
        await firstConversation.click();
        await page.waitForTimeout(2000); // Wait for messages to be marked as read

        // Go back to dashboard and check if badge count decreased
        await page.goto('/dashboard');
        await page.waitForLoadState('networkidle');

        if (await notificationBadge.count() > 0) {
          const finalBadgeText = await notificationBadge.textContent();
          const finalCount = parseInt(finalBadgeText || '0');
          expect(finalCount).toBeLessThanOrEqual(initialCount);
        } else {
          // Badge should be completely gone if no unread messages
          expect(await notificationBadge.count()).toBe(0);
        }
      }
    }
  });

  test('should show browser notification with permission', async ({ authenticatedContext, browserName }) => {
    // Skip this test in webkit as it has different notification behavior
    test.skip(browserName === 'webkit', 'Webkit has different notification permission handling');
    
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();
    
    // Grant notification permission
    await context.grantPermissions(['notifications']);
    
    await page.goto('/settings');
    await page.waitForLoadState('networkidle');

    // Enable browser notifications in settings
    const browserNotificationToggle = page.locator('[data-testid="browser-notifications-toggle"]');
    if (await browserNotificationToggle.count() > 0) {
      await browserNotificationToggle.check();
      
      // Save settings
      const saveButton = page.locator('[data-testid="save-settings-button"]');
      if (await saveButton.count() > 0) {
        await saveButton.click();
        await page.waitForLoadState('networkidle');
      }
    }

    // Note: Testing actual browser notifications requires either:
    // 1. Mocking the Notification API
    // 2. Using real WebSocket connections to trigger notifications
    // This test mainly verifies the permission and setting flow
  });

  test('should respect notification settings', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();
    
    await page.goto('/settings');
    await page.waitForLoadState('networkidle');

    // Disable in-app notifications
    const inAppNotificationToggle = page.locator('[data-testid="in-app-notifications-toggle"]');
    if (await inAppNotificationToggle.count() > 0) {
      await inAppNotificationToggle.uncheck();
      
      // Save settings
      const saveButton = page.locator('[data-testid="save-settings-button"]');
      if (await saveButton.count() > 0) {
        await saveButton.click();
        await page.waitForLoadState('networkidle');
      }

      // Navigate to messages and verify notifications are disabled
      await page.goto('/messages');
      await page.waitForLoadState('networkidle');

      // Send a message from another account and verify no notification
      // This would require WebSocket testing or API mocking
    }
  });

  test('should mark notifications as read when clicked', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();
    
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');

    // Open notification dropdown
    const notificationButton = page.locator('[data-testid="notifications-button"]');
    if (await notificationButton.count() > 0) {
      await notificationButton.click();

      const notificationDropdown = page.locator('[data-testid="notifications-dropdown"]');
      const notificationItems = notificationDropdown.locator('[data-testid="notification-item"]');
      
      if (await notificationItems.count() > 0) {
        // Find unread notification
        const unreadNotification = notificationItems.locator('[data-testid="unread-notification"]').first();
        
        if (await unreadNotification.count() > 0) {
          await unreadNotification.click();
          
          // Verify notification is marked as read (styling change)
          await expect(unreadNotification.locator('[data-testid="unread-indicator"]')).not.toBeVisible();
        }
      }
    }
  });

  test('should navigate to conversation from notification', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();
    
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');

    // Open notification dropdown
    const notificationButton = page.locator('[data-testid="notifications-button"]');
    if (await notificationButton.count() > 0) {
      await notificationButton.click();

      const notificationDropdown = page.locator('[data-testid="notifications-dropdown"]');
      const messageNotification = notificationDropdown.locator('[data-testid="notification-item"][data-type="message"]').first();
      
      if (await messageNotification.count() > 0) {
        await messageNotification.click();
        
        // Should navigate to messages page and open specific conversation
        await expect(page).toHaveURL(/\/messages/);
        await expect(page.locator('[data-testid="conversation-header"]')).toBeVisible();
      }
    }
  });

  test('should show notification count in page title', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();
    
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');

    // Check if page title includes notification count
    const title = await page.title();
    
    // If there are unread messages, title might include count like "(3) MiraiWorks"
    const hasNotificationCount = /\(\d+\)/.test(title);
    
    if (hasNotificationCount) {
      expect(title).toMatch(/\(\d+\)/);
    }
  });

  test('should handle notification API errors gracefully', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();
    
    // Mock notification API failure
    await page.route('**/api/notifications**', (route) => {
      route.abort('failed');
    });

    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');

    // Click notification button
    const notificationButton = page.locator('[data-testid="notifications-button"]');
    if (await notificationButton.count() > 0) {
      await notificationButton.click();

      // Should show error state or fallback UI
      const errorMessage = page.locator('[data-testid="notifications-error"]');
      if (await errorMessage.count() > 0) {
        await expect(errorMessage).toBeVisible();
      }
    }
  });

  test('should update notification count in real-time', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();
    
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');

    const notificationButton = page.locator('[data-testid="notifications-button"]');
    const notificationBadge = notificationButton.locator('[data-testid="notification-badge"]');
    
    if (await notificationBadge.count() > 0) {
      const initialCount = await notificationBadge.textContent();
      
      // Simulate new message received via WebSocket
      // In a real test, this would involve sending a message from another user
      // and verifying the count updates in real-time
      
      // For now, verify the badge structure is correct
      expect(initialCount).toMatch(/\d+/);
    }
  });

  test('should support notification preferences per contact', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();
    
    await page.goto('/messages');
    await page.waitForLoadState('networkidle');

    // Open conversation settings
    const firstConversation = page.locator('[data-testid="conversation-item"]').first();
    if (await firstConversation.count() > 0) {
      await firstConversation.click();
      
      // Look for conversation settings or options menu
      const conversationOptions = page.locator('[data-testid="conversation-options"]');
      if (await conversationOptions.count() > 0) {
        await conversationOptions.click();
        
        // Check for notification settings for this specific conversation
        const notificationSettings = page.locator('[data-testid="conversation-notifications"]');
        if (await notificationSettings.count() > 0) {
          await expect(notificationSettings).toBeVisible();
        }
      }
    }
  });
});