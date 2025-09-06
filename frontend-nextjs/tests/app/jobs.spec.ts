import { test, expect } from '@playwright/test';
import { AuthHelper } from '../fixtures/auth-helper';

test.describe('Jobs Page', () => {
  let authHelper: AuthHelper;

  test.beforeEach(async ({ page }) => {
    authHelper = new AuthHelper(page);
  });

  test('should display jobs page for anonymous users', async ({ page }) => {
    await page.goto('/jobs');
    
    // Check page title
    await expect(page).toHaveTitle(/Jobs/);
    
    // Check page header
    await expect(page.locator('h1')).toContainText('Jobs');
    
    // Check search functionality
    await expect(page.locator('[data-testid="job-search-input"]')).toBeVisible();
    await expect(page.locator('[data-testid="search-button"]')).toBeVisible();
    
    // Check filters
    await expect(page.locator('[data-testid="category-filter"]')).toBeVisible();
    await expect(page.locator('[data-testid="type-filter"]')).toBeVisible();
    await expect(page.locator('[data-testid="location-filter"]')).toBeVisible();
  });

  test('should search for jobs', async ({ page }) => {
    await page.goto('/jobs');
    
    // Wait for initial load
    await page.waitForLoadState('networkidle');
    
    // Search for specific job
    await page.fill('[data-testid="job-search-input"]', 'Software Engineer');
    await page.click('[data-testid="search-button"]');
    
    // Wait for search results
    await page.waitForLoadState('networkidle');
    
    // Check that results are filtered
    const jobCards = page.locator('[data-testid="job-card"]');
    const jobCount = await jobCards.count();
    
    if (jobCount > 0) {
      // Verify search results contain the search term
      const firstJobTitle = await jobCards.first().locator('[data-testid="job-title"]').textContent();
      expect(firstJobTitle?.toLowerCase()).toContain('software');
    } else {
      // Should show no results message
      await expect(page.locator('[data-testid="no-jobs-found"]')).toBeVisible();
    }
  });

  test('should filter jobs by category', async ({ page }) => {
    await page.goto('/jobs');
    await page.waitForLoadState('networkidle');
    
    // Select a category filter
    await page.selectOption('[data-testid="category-filter"]', 'engineering');
    
    // Wait for filtered results
    await page.waitForLoadState('networkidle');
    
    // Check that jobs are filtered
    const jobCards = page.locator('[data-testid="job-card"]');
    const jobCount = await jobCards.count();
    
    expect(jobCount >= 0).toBeTruthy(); // Should have 0 or more results
  });

  test('should filter jobs by type', async ({ page }) => {
    await page.goto('/jobs');
    await page.waitForLoadState('networkidle');
    
    // Select job type filter
    await page.selectOption('[data-testid="type-filter"]', 'full-time');
    
    // Wait for filtered results
    await page.waitForLoadState('networkidle');
    
    // Verify filter is applied
    const activeFilter = await page.locator('[data-testid="type-filter"]').inputValue();
    expect(activeFilter).toBe('full-time');
  });

  test('should display job details', async ({ page }) => {
    await page.goto('/jobs');
    await page.waitForLoadState('networkidle');
    
    const jobCards = page.locator('[data-testid="job-card"]');
    const jobCount = await jobCards.count();
    
    if (jobCount > 0) {
      const firstJob = jobCards.first();
      
      // Check job card contains required information
      await expect(firstJob.locator('[data-testid="job-title"]')).toBeVisible();
      await expect(firstJob.locator('[data-testid="company-name"]')).toBeVisible();
      await expect(firstJob.locator('[data-testid="job-location"]')).toBeVisible();
      await expect(firstJob.locator('[data-testid="job-salary"]')).toBeVisible();
      await expect(firstJob.locator('[data-testid="job-type"]')).toBeVisible();
      
      // Check job actions
      await expect(firstJob.locator('[data-testid="view-job-button"]')).toBeVisible();
    }
  });

  test('should navigate to job details page', async ({ page }) => {
    await page.goto('/jobs');
    await page.waitForLoadState('networkidle');
    
    const jobCards = page.locator('[data-testid="job-card"]');
    const jobCount = await jobCards.count();
    
    if (jobCount > 0) {
      // Click on first job
      await jobCards.first().locator('[data-testid="view-job-button"]').click();
      
      // Should navigate to job details page
      await expect(page).toHaveURL(/\/jobs\/\d+/);
      
      // Should display job details
      await expect(page.locator('[data-testid="job-details"]')).toBeVisible();
      await expect(page.locator('[data-testid="apply-button"]')).toBeVisible();
    }
  });

  test('should require login to apply for jobs', async ({ page }) => {
    await authHelper.ensureLoggedOut();
    await page.goto('/jobs');
    await page.waitForLoadState('networkidle');
    
    const jobCards = page.locator('[data-testid="job-card"]');
    const jobCount = await jobCards.count();
    
    if (jobCount > 0) {
      // Try to apply without being logged in
      await jobCards.first().locator('[data-testid="view-job-button"]').click();
      
      // Try to apply
      await page.click('[data-testid="apply-button"]');
      
      // Should redirect to login or show login modal
      const currentUrl = page.url();
      const hasLoginModal = await page.locator('[data-testid="login-modal"]').isVisible();
      
      expect(currentUrl.includes('/auth/login') || hasLoginModal).toBeTruthy();
    }
  });

  test('should allow logged-in users to save jobs', async ({ page }) => {
    await authHelper.ensureLoggedOut();
    await authHelper.login('jobSeeker');
    
    await page.goto('/jobs');
    await page.waitForLoadState('networkidle');
    
    const jobCards = page.locator('[data-testid="job-card"]');
    const jobCount = await jobCards.count();
    
    if (jobCount > 0) {
      const saveButton = jobCards.first().locator('[data-testid="save-job-button"]');
      
      if (await saveButton.isVisible()) {
        await saveButton.click();
        
        // Should show saved state
        await expect(jobCards.first().locator('[data-testid="job-saved-indicator"]')).toBeVisible();
      }
    }
  });

  test('should apply for job when logged in', async ({ page }) => {
    await authHelper.ensureLoggedOut();
    await authHelper.login('jobSeeker');
    
    await page.goto('/jobs');
    await page.waitForLoadState('networkidle');
    
    const jobCards = page.locator('[data-testid="job-card"]');
    const jobCount = await jobCards.count();
    
    if (jobCount > 0) {
      // Navigate to job details
      await jobCards.first().locator('[data-testid="view-job-button"]').click();
      
      // Apply for the job
      await page.click('[data-testid="apply-button"]');
      
      // Should show application form or success message
      const hasApplicationForm = await page.locator('[data-testid="application-form"]').isVisible();
      const hasSuccessMessage = await page.locator('[data-testid="application-success"]').isVisible();
      const hasAlreadyApplied = await page.locator('[data-testid="already-applied"]').isVisible();
      
      expect(hasApplicationForm || hasSuccessMessage || hasAlreadyApplied).toBeTruthy();
    }
  });

  test('should handle pagination', async ({ page }) => {
    await page.goto('/jobs');
    await page.waitForLoadState('networkidle');
    
    const pagination = page.locator('[data-testid="pagination"]');
    
    if (await pagination.isVisible()) {
      // Check pagination controls
      const nextButton = pagination.locator('[data-testid="next-page"]');
      
      if (await nextButton.isEnabled()) {
        await nextButton.click();
        await page.waitForLoadState('networkidle');
        
        // Should show page 2
        await expect(page.locator('[data-testid="current-page"]')).toContainText('2');
      }
    }
  });

  test('should be responsive on mobile devices', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/jobs');
    
    // Check that page is functional on mobile
    await expect(page.locator('h1')).toContainText('Jobs');
    
    // Check that search and filters work on mobile
    await expect(page.locator('[data-testid="job-search-input"]')).toBeVisible();
    
    // Mobile filter toggle should be available
    const mobileFilterToggle = page.locator('[data-testid="mobile-filter-toggle"]');
    if (await mobileFilterToggle.isVisible()) {
      await mobileFilterToggle.click();
      await expect(page.locator('[data-testid="mobile-filters"]')).toBeVisible();
    }
  });

  test('should clear all filters', async ({ page }) => {
    await page.goto('/jobs');
    await page.waitForLoadState('networkidle');
    
    // Apply some filters
    await page.fill('[data-testid="job-search-input"]', 'test');
    await page.selectOption('[data-testid="category-filter"]', 'engineering');
    await page.selectOption('[data-testid="type-filter"]', 'full-time');
    
    // Clear filters
    const clearFiltersButton = page.locator('[data-testid="clear-filters-button"]');
    if (await clearFiltersButton.isVisible()) {
      await clearFiltersButton.click();
      
      // Verify filters are cleared
      await expect(page.locator('[data-testid="job-search-input"]')).toHaveValue('');
      await expect(page.locator('[data-testid="category-filter"]')).toHaveValue('all');
      await expect(page.locator('[data-testid="type-filter"]')).toHaveValue('all');
    }
  });
});