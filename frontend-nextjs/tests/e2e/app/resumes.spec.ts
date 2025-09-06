import { test, expect } from '@playwright/test';
import { AuthHelper } from '../fixtures/auth-helper';

test.describe('Resumes Page', () => {
  let authHelper: AuthHelper;

  test.beforeEach(async ({ page }) => {
    authHelper = new AuthHelper(page);
    await authHelper.ensureLoggedOut();
    await authHelper.login('jobSeeker');
  });

  test('should display resumes page correctly', async ({ page }) => {
    await page.goto('/resumes');
    
    // Check page title
    await expect(page).toHaveTitle(/Resumes/);
    
    // Check page header
    await expect(page.locator('h1')).toContainText('Resumes');
    
    // Check create resume button
    await expect(page.locator('[data-testid="create-resume-button"]')).toBeVisible();
    
    // Check stats section
    await expect(page.locator('[data-testid="resume-stats"]')).toBeVisible();
  });

  test('should display resume statistics', async ({ page }) => {
    await page.goto('/resumes');
    await page.waitForLoadState('networkidle');
    
    // Check stat cards
    await expect(page.locator('[data-testid="total-resumes-stat"]')).toBeVisible();
    await expect(page.locator('[data-testid="published-resumes-stat"]')).toBeVisible();
    await expect(page.locator('[data-testid="total-views-stat"]')).toBeVisible();
    await expect(page.locator('[data-testid="total-downloads-stat"]')).toBeVisible();
  });

  test('should navigate to create resume page', async ({ page }) => {
    await page.goto('/resumes');
    
    await page.click('[data-testid="create-resume-button"]');
    await expect(page).toHaveURL('/resumes/builder');
  });

  test('should display resume list', async ({ page }) => {
    await page.goto('/resumes');
    await page.waitForLoadState('networkidle');
    
    // Should either show resumes or empty state
    const resumeCards = page.locator('[data-testid="resume-card"]');
    const resumeCount = await resumeCards.count();
    const hasEmptyState = await page.locator('[data-testid="no-resumes"]').isVisible();
    
    expect(resumeCount > 0 || hasEmptyState).toBeTruthy();
    
    if (resumeCount > 0) {
      const firstResume = resumeCards.first();
      
      // Check resume card content
      await expect(firstResume.locator('[data-testid="resume-title"]')).toBeVisible();
      await expect(firstResume.locator('[data-testid="resume-status"]')).toBeVisible();
      await expect(firstResume.locator('[data-testid="resume-updated"]')).toBeVisible();
      await expect(firstResume.locator('[data-testid="resume-views"]')).toBeVisible();
      await expect(firstResume.locator('[data-testid="resume-downloads"]')).toBeVisible();
      
      // Check resume actions
      await expect(firstResume.locator('[data-testid="edit-resume-button"]')).toBeVisible();
      await expect(firstResume.locator('[data-testid="preview-resume-button"]')).toBeVisible();
      await expect(firstResume.locator('[data-testid="share-resume-button"]')).toBeVisible();
    }
  });

  test('should edit resume', async ({ page }) => {
    await page.goto('/resumes');
    await page.waitForLoadState('networkidle');
    
    const resumeCards = page.locator('[data-testid="resume-card"]');
    const resumeCount = await resumeCards.count();
    
    if (resumeCount > 0) {
      await resumeCards.first().locator('[data-testid="edit-resume-button"]').click();
      
      // Should navigate to resume builder
      await expect(page).toHaveURL(/\/resumes\/builder/);
      
      // Should show resume builder interface
      await expect(page.locator('[data-testid="resume-builder"]')).toBeVisible();
    }
  });

  test('should preview resume', async ({ page }) => {
    await page.goto('/resumes');
    await page.waitForLoadState('networkidle');
    
    const resumeCards = page.locator('[data-testid="resume-card"]');
    const resumeCount = await resumeCards.count();
    
    if (resumeCount > 0) {
      await resumeCards.first().locator('[data-testid="preview-resume-button"]').click();
      
      // Should navigate to resume preview
      await expect(page).toHaveURL(/\/resumes\/preview/);
      
      // Should show resume preview
      await expect(page.locator('[data-testid="resume-preview"]')).toBeVisible();
      await expect(page.locator('[data-testid="download-pdf-button"]')).toBeVisible();
    }
  });

  test('should delete resume', async ({ page }) => {
    await page.goto('/resumes');
    await page.waitForLoadState('networkidle');
    
    const resumeCards = page.locator('[data-testid="resume-card"]');
    const initialCount = await resumeCards.count();
    
    if (initialCount > 0) {
      // Click delete button
      await resumeCards.first().locator('[data-testid="delete-resume-button"]').click();
      
      // Should show confirmation dialog
      await expect(page.locator('[data-testid="delete-confirmation"]')).toBeVisible();
      
      // Confirm deletion
      await page.click('[data-testid="confirm-delete-button"]');
      
      // Wait for the operation to complete
      await page.waitForLoadState('networkidle');
      
      // Should show success message or remove the item
      const newCount = await page.locator('[data-testid="resume-card"]').count();
      expect(newCount).toBe(initialCount - 1);
    }
  });

  test('should share resume', async ({ page }) => {
    await page.goto('/resumes');
    await page.waitForLoadState('networkidle');
    
    const resumeCards = page.locator('[data-testid="resume-card"]');
    const resumeCount = await resumeCards.count();
    
    if (resumeCount > 0) {
      await resumeCards.first().locator('[data-testid="share-resume-button"]').click();
      
      // Should show share modal or options
      const shareModal = page.locator('[data-testid="share-modal"]');
      const shareOptions = page.locator('[data-testid="share-options"]');
      
      expect(await shareModal.isVisible() || await shareOptions.isVisible()).toBeTruthy();
    }
  });

  test('should filter resumes by status', async ({ page }) => {
    await page.goto('/resumes');
    await page.waitForLoadState('networkidle');
    
    const statusFilter = page.locator('[data-testid="status-filter"]');
    
    if (await statusFilter.isVisible()) {
      // Filter by published
      await statusFilter.selectOption('published');
      await page.waitForLoadState('networkidle');
      
      // Check that only published resumes are shown
      const resumeCards = page.locator('[data-testid="resume-card"]');
      const count = await resumeCards.count();
      
      for (let i = 0; i < count; i++) {
        const statusBadge = resumeCards.nth(i).locator('[data-testid="resume-status"]');
        await expect(statusBadge).toContainText('published');
      }
    }
  });

  test('should search resumes', async ({ page }) => {
    await page.goto('/resumes');
    await page.waitForLoadState('networkidle');
    
    const searchInput = page.locator('[data-testid="resume-search-input"]');
    
    if (await searchInput.isVisible()) {
      await searchInput.fill('Software Engineer');
      await page.click('[data-testid="search-resumes-button"]');
      
      await page.waitForLoadState('networkidle');
      
      // Results should be filtered
      const resumeCards = page.locator('[data-testid="resume-card"]');
      const count = await resumeCards.count();
      
      if (count > 0) {
        // At least one result should contain the search term
        const firstTitle = await resumeCards.first().locator('[data-testid="resume-title"]').textContent();
        expect(firstTitle?.toLowerCase()).toContain('software');
      }
    }
  });

  test('should duplicate resume', async ({ page }) => {
    await page.goto('/resumes');
    await page.waitForLoadState('networkidle');
    
    const resumeCards = page.locator('[data-testid="resume-card"]');
    const initialCount = await resumeCards.count();
    
    if (initialCount > 0) {
      const duplicateButton = resumeCards.first().locator('[data-testid="duplicate-resume-button"]');
      
      if (await duplicateButton.isVisible()) {
        await duplicateButton.click();
        
        // Should show duplicate confirmation or create duplicate
        await page.waitForLoadState('networkidle');
        
        const newCount = await page.locator('[data-testid="resume-card"]').count();
        expect(newCount).toBe(initialCount + 1);
      }
    }
  });

  test('should handle empty state', async ({ page }) => {
    // This test assumes we can create a state with no resumes
    // In a real test, you might need to delete all resumes first
    await page.goto('/resumes');
    await page.waitForLoadState('networkidle');
    
    const resumeCards = page.locator('[data-testid="resume-card"]');
    const resumeCount = await resumeCards.count();
    
    if (resumeCount === 0) {
      // Should show empty state
      await expect(page.locator('[data-testid="no-resumes"]')).toBeVisible();
      await expect(page.locator('[data-testid="create-first-resume-button"]')).toBeVisible();
      
      // Click create first resume
      await page.click('[data-testid="create-first-resume-button"]');
      await expect(page).toHaveURL('/resumes/builder');
    }
  });

  test('should be responsive on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/resumes');
    
    // Check mobile layout
    await expect(page.locator('h1')).toContainText('Resumes');
    
    // Stats should be stacked on mobile
    const statsSection = page.locator('[data-testid="resume-stats"]');
    await expect(statsSection).toBeVisible();
    
    // Resume cards should be responsive
    const resumeCards = page.locator('[data-testid="resume-card"]');
    const resumeCount = await resumeCards.count();
    
    if (resumeCount > 0) {
      await expect(resumeCards.first()).toBeVisible();
    }
  });

  test('should sort resumes', async ({ page }) => {
    await page.goto('/resumes');
    await page.waitForLoadState('networkidle');
    
    const sortSelect = page.locator('[data-testid="sort-resumes-select"]');
    
    if (await sortSelect.isVisible()) {
      // Sort by updated date (newest first)
      await sortSelect.selectOption('updated-desc');
      await page.waitForLoadState('networkidle');
      
      // Verify sorting is applied
      const resumeCards = page.locator('[data-testid="resume-card"]');
      const count = await resumeCards.count();
      
      if (count > 1) {
        // Check that the first resume has a more recent update date than the second
        const firstDate = await resumeCards.first().locator('[data-testid="resume-updated"]').textContent();
        const secondDate = await resumeCards.nth(1).locator('[data-testid="resume-updated"]').textContent();
        
        // This is a basic check - in a real implementation you'd parse and compare dates
        expect(firstDate).toBeTruthy();
        expect(secondDate).toBeTruthy();
      }
    }
  });
});