/**
 * Simple messaging functionality E2E tests
 * Tests basic functionality using actual UI elements
 */

import { test, expect } from '../fixtures/auth-fixture';

test.describe('Simple Messaging Tests', () => {
  test('should navigate to messages page', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();
    
    // Navigate to messages page
    await page.goto('/messages');
    await page.waitForLoadState('networkidle');

    // Check that we're on the messages page
    await expect(page).toHaveURL('/messages');
    
    // Look for common messaging UI elements
    const hasMessagesTitle = await page.locator('h1, h2, h3').filter({ hasText: /messages/i }).first().isVisible();
    const hasConversationArea = await page.locator('div').filter({ hasText: /conversation/i }).first().isVisible(); 
    const hasMessageInput = await page.locator('input[type="text"], textarea').first().isVisible();
    
    // At least one of these should be visible to indicate we're on a messaging page
    expect(hasMessagesTitle || hasConversationArea || hasMessageInput).toBe(true);
  });

  test('should show messages page layout', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();
    
    await page.goto('/messages');
    await page.waitForLoadState('networkidle');

    // Check for basic page structure without relying on specific test IDs
    const pageContent = await page.locator('body').isVisible();
    expect(pageContent).toBe(true);
    
    // Check that page doesn't show error message
    const hasError = await page.locator('text=/error|Error|ERROR/').isVisible();
    expect(hasError).toBe(false);
  });

  test('should handle page load without crashing', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();
    
    // Listen for console errors
    const errors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });

    // Listen for uncaught exceptions
    page.on('pageerror', error => {
      errors.push(error.message);
    });

    await page.goto('/messages');
    await page.waitForLoadState('networkidle');

    // Wait a bit for any async operations to complete
    await page.waitForTimeout(2000);

    // Check that no critical errors occurred
    const criticalErrors = errors.filter(error => 
      !error.includes('favicon') && 
      !error.includes('404') &&
      !error.includes('chrome-extension') &&
      !error.includes('websocket') // WebSocket errors are expected in test environment
    );
    
    expect(criticalErrors).toHaveLength(0);
  });

  test('should be responsive to different viewport sizes', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();

    // Test desktop viewport
    await page.setViewportSize({ width: 1200, height: 800 });
    await page.goto('/messages');
    await page.waitForLoadState('networkidle');
    
    let pageVisible = await page.locator('body').isVisible();
    expect(pageVisible).toBe(true);

    // Test tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.waitForTimeout(1000);
    
    pageVisible = await page.locator('body').isVisible();
    expect(pageVisible).toBe(true);

    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForTimeout(1000);
    
    pageVisible = await page.locator('body').isVisible();
    expect(pageVisible).toBe(true);
  });

  test('should handle authentication correctly', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();

    // Go to messages page
    await page.goto('/messages');
    await page.waitForLoadState('networkidle');

    // Should not redirect to login page
    const currentUrl = page.url();
    expect(currentUrl).not.toContain('/auth/login');
    expect(currentUrl).toContain('/messages');

    // Should not show "unauthorized" or "login required" messages
    const hasUnauthorized = await page.locator('text=/unauthorized|login required|please log in/i').isVisible();
    expect(hasUnauthorized).toBe(false);
  });

  test('should load without infinite loading states', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();

    await page.goto('/messages');
    
    // Wait for initial load
    await page.waitForLoadState('networkidle');
    
    // Wait a reasonable time for any loading indicators to disappear
    await page.waitForTimeout(5000);
    
    // Check that we don't have infinite loading spinners
    const loadingSpinners = page.locator('[class*="loading"], [class*="spinner"], text=/loading/i');
    const spinnerCount = await loadingSpinners.count();
    
    // It's okay to have some loading indicators, but not too many (which might indicate stuck loading)
    expect(spinnerCount).toBeLessThan(5);
  });

  test('should render basic UI elements', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();

    await page.goto('/messages');
    await page.waitForLoadState('networkidle');

    // Look for common messaging UI patterns without specific test IDs
    const commonElements = [
      page.locator('input').first(), // Some kind of input field
      page.locator('button').first(), // Some kind of button
      page.locator('div').first(), // Basic page structure
    ];

    for (const element of commonElements) {
      const isVisible = await element.isVisible();
      expect(isVisible).toBe(true);
    }
  });

  test('should handle navigation back to dashboard', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();

    await page.goto('/messages');
    await page.waitForLoadState('networkidle');

    // Try to navigate back to dashboard
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');

    // Should successfully navigate to dashboard
    expect(page.url()).toContain('/dashboard');

    // Navigate back to messages
    await page.goto('/messages');
    await page.waitForLoadState('networkidle');

    // Should successfully return to messages
    expect(page.url()).toContain('/messages');
  });
});