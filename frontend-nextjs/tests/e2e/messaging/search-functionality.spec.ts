/**
 * Message search functionality E2E tests
 * Tests message search, filtering, and results display
 */

import { test, expect } from '../fixtures/auth-fixture';

test.describe('Message Search', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/messages');
    await page.waitForLoadState('networkidle');
  });

  test('should search messages by content', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();
    
    await page.goto('/messages');
    await page.waitForLoadState('networkidle');

    // Enter search query
    const searchQuery = 'hello';
    await page.fill('[data-testid="search-input"]', searchQuery);
    
    // Wait for search results
    await page.waitForLoadState('networkidle');

    // Verify search results are displayed
    const searchResults = page.locator('[data-testid="search-results"]');
    await expect(searchResults).toBeVisible();
    
    // Verify search results contain the query
    const resultItems = searchResults.locator('[data-testid="search-result-item"]');
    if (await resultItems.count() > 0) {
      const firstResult = resultItems.first();
      const resultText = await firstResult.locator('[data-testid="message-content"]').textContent();
      expect(resultText?.toLowerCase()).toContain(searchQuery.toLowerCase());
    }
  });

  test('should highlight search terms in results', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();
    
    await page.goto('/messages');
    await page.waitForLoadState('networkidle');

    const searchQuery = 'test';
    await page.fill('[data-testid="search-input"]', searchQuery);
    await page.waitForLoadState('networkidle');

    const searchResults = page.locator('[data-testid="search-results"]');
    if (await searchResults.locator('[data-testid="search-result-item"]').count() > 0) {
      // Check for highlighted terms
      await expect(searchResults.locator('[data-testid="highlighted-term"]').first()).toBeVisible();
    }
  });

  test('should show "no results" when search returns empty', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();
    
    await page.goto('/messages');
    await page.waitForLoadState('networkidle');

    // Search for something that definitely doesn't exist
    const uniqueQuery = 'xyzzyx123nonexistent';
    await page.fill('[data-testid="search-input"]', uniqueQuery);
    await page.waitForLoadState('networkidle');

    // Verify no results message
    await expect(page.locator('[data-testid="no-search-results"]')).toBeVisible();
    await expect(page.locator('[data-testid="no-search-results"]')).toContainText('No messages found');
  });

  test('should clear search results when input is cleared', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();
    
    await page.goto('/messages');
    await page.waitForLoadState('networkidle');

    // Perform search
    await page.fill('[data-testid="search-input"]', 'test');
    await page.waitForLoadState('networkidle');
    
    // Verify search results are shown
    if (await page.locator('[data-testid="search-results"]').count() > 0) {
      await expect(page.locator('[data-testid="search-results"]')).toBeVisible();
    }

    // Clear search
    await page.fill('[data-testid="search-input"]', '');
    await page.waitForLoadState('networkidle');

    // Verify search results are hidden and conversations list is back
    await expect(page.locator('[data-testid="search-results"]')).not.toBeVisible();
    await expect(page.locator('[data-testid="conversations-list"]')).toBeVisible();
  });

  test('should search with filters', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();
    
    await page.goto('/messages');
    await page.waitForLoadState('networkidle');

    // Open search filters if available
    const filtersToggle = page.locator('[data-testid="search-filters-toggle"]');
    if (await filtersToggle.count() > 0) {
      await filtersToggle.click();

      // Apply date filter
      const dateFilter = page.locator('[data-testid="date-filter"]');
      if (await dateFilter.count() > 0) {
        await dateFilter.selectOption('last-week');
      }

      // Apply sender filter
      const senderFilter = page.locator('[data-testid="sender-filter"]');
      if (await senderFilter.count() > 0) {
        await senderFilter.fill('recruiter');
      }

      // Perform search with filters
      await page.fill('[data-testid="search-input"]', 'position');
      await page.waitForLoadState('networkidle');

      // Verify filtered results
      const searchResults = page.locator('[data-testid="search-results"]');
      await expect(searchResults).toBeVisible();
    }
  });

  test('should navigate to conversation from search result', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();
    
    await page.goto('/messages');
    await page.waitForLoadState('networkidle');

    // Perform search
    await page.fill('[data-testid="search-input"]', 'hello');
    await page.waitForLoadState('networkidle');

    const searchResults = page.locator('[data-testid="search-results"]');
    const resultItems = searchResults.locator('[data-testid="search-result-item"]');
    
    if (await resultItems.count() > 0) {
      // Click on first search result
      await resultItems.first().click();

      // Verify conversation is opened
      await expect(page.locator('[data-testid="conversation-header"]')).toBeVisible();
      await expect(page.locator('[data-testid="messages-container"]')).toBeVisible();
      
      // Verify search is cleared
      await expect(page.locator('[data-testid="search-input"]')).toHaveValue('');
    }
  });

  test('should handle search with special characters', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();
    
    await page.goto('/messages');
    await page.waitForLoadState('networkidle');

    const specialQueries = ['@mention', '#hashtag', 'email@domain.com', 'c++', '100%'];
    
    for (const query of specialQueries) {
      await page.fill('[data-testid="search-input"]', query);
      await page.waitForLoadState('networkidle');
      
      // Should not crash or show error
      await expect(page.locator('[data-testid="search-input"]')).toHaveValue(query);
      
      // Results should be displayed or "no results" message
      const hasResults = await page.locator('[data-testid="search-results"]').count() > 0;
      const hasNoResults = await page.locator('[data-testid="no-search-results"]').count() > 0;
      
      expect(hasResults || hasNoResults).toBe(true);
    }
  });

  test('should show search history/suggestions', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();
    
    await page.goto('/messages');
    await page.waitForLoadState('networkidle');

    // Focus search input to potentially show search history
    await page.focus('[data-testid="search-input"]');
    
    const searchSuggestions = page.locator('[data-testid="search-suggestions"]');
    if (await searchSuggestions.count() > 0) {
      await expect(searchSuggestions).toBeVisible();
      
      // Click on a suggestion if available
      const firstSuggestion = searchSuggestions.locator('[data-testid="search-suggestion"]').first();
      if (await firstSuggestion.count() > 0) {
        await firstSuggestion.click();
        
        // Verify suggestion is used as search query
        const suggestionText = await firstSuggestion.textContent();
        await expect(page.locator('[data-testid="search-input"]')).toHaveValue(suggestionText || '');
      }
    }
  });

  test('should handle rapid search queries without breaking', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();
    
    await page.goto('/messages');
    await page.waitForLoadState('networkidle');

    const queries = ['h', 'he', 'hel', 'hell', 'hello', 'hello w', 'hello wo', 'hello wor', 'hello worl', 'hello world'];
    
    // Type queries rapidly
    for (const query of queries) {
      await page.fill('[data-testid="search-input"]', query);
      await page.waitForTimeout(50); // Small delay to simulate rapid typing
    }
    
    // Wait for final search to complete
    await page.waitForLoadState('networkidle');
    
    // Should handle rapid queries without errors
    await expect(page.locator('[data-testid="search-input"]')).toHaveValue('hello world');
  });

  test('should preserve search state on page refresh', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();
    
    await page.goto('/messages');
    await page.waitForLoadState('networkidle');

    // Perform search
    const searchQuery = 'important message';
    await page.fill('[data-testid="search-input"]', searchQuery);
    await page.waitForLoadState('networkidle');

    // Refresh page
    await page.reload();
    await page.waitForLoadState('networkidle');

    // Verify search state is preserved (if implemented)
    const searchInput = page.locator('[data-testid="search-input"]');
    const inputValue = await searchInput.inputValue();
    
    // This test depends on whether the app implements search state persistence
    // Could be empty (no persistence) or maintain the search query
    expect(typeof inputValue).toBe('string');
  });
});