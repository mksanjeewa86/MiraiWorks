import { test, expect } from '@playwright/test';
import { AuthHelper } from '../fixtures/auth-helper';

test.describe('Dashboard Page', () => {
  let authHelper: AuthHelper;

  test.beforeEach(async ({ page }) => {
    authHelper = new AuthHelper(page);
    await authHelper.ensureLoggedOut();
    await authHelper.login('jobSeeker');
  });

  test('should display dashboard correctly for job seekers', async ({ page }) => {
    await expect(page).toHaveURL('/dashboard');
    
    // Check page title
    await expect(page).toHaveTitle(/Dashboard/);
    
    // Check dashboard header
    await expect(page.locator('h1')).toContainText('Dashboard');
    
    // Check navigation is visible
    await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();
    
    // Check main dashboard sections are present
    await expect(page.locator('[data-testid="stats-section"]')).toBeVisible();
    await expect(page.locator('[data-testid="recent-applications"]')).toBeVisible();
    await expect(page.locator('[data-testid="recommended-jobs"]')).toBeVisible();
  });

  test('should display user stats correctly', async ({ page }) => {
    // Check that stats cards are present
    const statsCards = page.locator('[data-testid="stat-card"]');
    await expect(statsCards).toHaveCount(4); // Applications, Interviews, Profile Views, Saved Jobs
    
    // Check individual stat cards
    await expect(page.locator('[data-testid="applications-stat"]')).toBeVisible();
    await expect(page.locator('[data-testid="interviews-stat"]')).toBeVisible();
    await expect(page.locator('[data-testid="profile-views-stat"]')).toBeVisible();
    await expect(page.locator('[data-testid="saved-jobs-stat"]')).toBeVisible();
  });

  test('should navigate to different sections from dashboard', async ({ page }) => {
    // Test navigation to Jobs page
    await page.click('[data-testid="browse-jobs-button"]');
    await expect(page).toHaveURL('/jobs');
    
    // Go back to dashboard
    await page.goto('/dashboard');
    
    // Test navigation to Profile page
    await page.click('[data-testid="view-profile-button"]');
    await expect(page).toHaveURL('/profile');
    
    // Go back to dashboard
    await page.goto('/dashboard');
    
    // Test navigation to Resumes page
    await page.click('[data-testid="manage-resumes-button"]');
    await expect(page).toHaveURL('/resumes');
  });

  test('should display recent applications section', async ({ page }) => {
    const recentApplications = page.locator('[data-testid="recent-applications"]');
    await expect(recentApplications).toBeVisible();
    
    // Should have a heading
    await expect(recentApplications.locator('h2')).toContainText('Recent Applications');
    
    // Should either show applications or empty state
    const hasApplications = await page.locator('[data-testid="application-item"]').count();
    const hasEmptyState = await page.locator('[data-testid="no-applications"]').isVisible();
    
    expect(hasApplications > 0 || hasEmptyState).toBeTruthy();
  });

  test('should display recommended jobs section', async ({ page }) => {
    const recommendedJobs = page.locator('[data-testid="recommended-jobs"]');
    await expect(recommendedJobs).toBeVisible();
    
    // Should have a heading
    await expect(recommendedJobs.locator('h2')).toContainText('Recommended Jobs');
    
    // Should either show jobs or empty state
    const hasJobs = await page.locator('[data-testid="job-card"]').count();
    const hasEmptyState = await page.locator('[data-testid="no-jobs"]').isVisible();
    
    expect(hasJobs > 0 || hasEmptyState).toBeTruthy();
  });

  test('should handle quick actions', async ({ page }) => {
    // Test quick action buttons
    const quickActions = page.locator('[data-testid="quick-actions"]');
    await expect(quickActions).toBeVisible();
    
    // Check that quick action buttons are present
    await expect(page.locator('[data-testid="create-resume-action"]')).toBeVisible();
    await expect(page.locator('[data-testid="search-jobs-action"]')).toBeVisible();
    await expect(page.locator('[data-testid="view-interviews-action"]')).toBeVisible();
  });

  test('should display activity feed', async ({ page }) => {
    const activityFeed = page.locator('[data-testid="activity-feed"]');
    
    if (await activityFeed.isVisible()) {
      // Should have a heading
      await expect(activityFeed.locator('h3')).toContainText('Recent Activity');
      
      // Should either show activities or empty state
      const hasActivities = await page.locator('[data-testid="activity-item"]').count();
      const hasEmptyState = await page.locator('[data-testid="no-activity"]').isVisible();
      
      expect(hasActivities > 0 || hasEmptyState).toBeTruthy();
    }
  });

  test('should be responsive on mobile devices', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Check that page is still functional
    await expect(page.locator('h1')).toContainText('Dashboard');
    
    // Check that mobile navigation works
    const mobileMenu = page.locator('[data-testid="mobile-menu-toggle"]');
    if (await mobileMenu.isVisible()) {
      await mobileMenu.click();
      await expect(page.locator('[data-testid="mobile-nav"]')).toBeVisible();
    }
  });

  test('should load data progressively', async ({ page }) => {
    // Check for loading states
    await page.goto('/dashboard');
    
    // Should show loading indicators initially (if present)
    const loadingIndicators = page.locator('[data-testid="loading"]');
    const loadingCount = await loadingIndicators.count();
    
    if (loadingCount > 0) {
      // Wait for loading to complete
      await expect(loadingIndicators.first()).not.toBeVisible({ timeout: 10000 });
    }
    
    // Content should be loaded
    await expect(page.locator('[data-testid="stats-section"]')).toBeVisible();
  });
});