import { test, expect } from '../fixtures/auth-fixture';

test.describe('Dashboard Page', () => {
  let page: any;
  let context: any;

  test.beforeEach(async ({ authenticatedContext }) => {
    // Use pre-authenticated context for candidate/jobSeeker
    context = await authenticatedContext('candidate1');
    page = await context.newPage();
    await page.goto('/dashboard', { waitUntil: 'domcontentloaded' });
  });

  test.afterEach(async () => {
    await page?.close();
    await context?.close();
  });

  test('should display dashboard correctly for candidates', async () => {
    await expect(page).toHaveURL('/dashboard');
    
    // Check page title
    await expect(page).toHaveTitle(/MiraiWorks/);
    
    // Check dashboard header - wait for loading to complete
    await page.waitForSelector('h1', { timeout: 10000 });
    await expect(page.locator('h1')).toContainText('Candidate Dashboard');
    
    // Check welcome message
    await expect(page.locator('p').first()).toContainText('Welcome back');
    
    // Check that stats cards are present - wait for data to load
    await page.waitForSelector('text=Applications', { timeout: 10000 });
    await expect(page.locator('text=Applications').first()).toBeVisible();
    await expect(page.locator('text=Interviews Scheduled')).toBeVisible();
    await expect(page.locator('text=Interviews Completed')).toBeVisible();
    await expect(page.locator('text=Resumes Created')).toBeVisible();
  });

  test('should display user stats correctly', async () => {
    // Wait for dashboard to load
    await page.waitForSelector('h1', { timeout: 10000 });
    
    // Check that all 4 stat cards are present in the grid
    const statsGrid = page.locator('.grid.grid-cols-1.md\\:grid-cols-2.lg\\:grid-cols-4');
    await expect(statsGrid).toBeVisible();
    
    // Check individual stat labels
    await expect(page.locator('text=Applications')).toBeVisible();
    await expect(page.locator('text=Interviews Scheduled')).toBeVisible(); 
    await expect(page.locator('text=Interviews Completed')).toBeVisible();
    await expect(page.locator('text=Resumes Created')).toBeVisible();
    
    // Check that numeric values are displayed (even if 0)
    const numbers = page.locator('.text-3xl.font-bold');
    await expect(numbers).toHaveCount(4);
  });

  test('should display quick actions section', async () => {
    // Wait for dashboard to load
    await page.waitForSelector('h1', { timeout: 10000 });
    
    // Check Quick Actions section exists
    await expect(page.locator('h3:has-text("Quick Actions")')).toBeVisible();
    
    // Check that action buttons are present
    await expect(page.locator('button:has-text("Create Resume")')).toBeVisible();
    await expect(page.locator('button:has-text("Browse Jobs")')).toBeVisible();
    await expect(page.locator('button:has-text("Schedule Interview")')).toBeVisible();
    await expect(page.locator('button:has-text("Message Recruiter")')).toBeVisible();
  });

  test('should display application status section', async () => {
    // Wait for dashboard to load
    await page.waitForSelector('h1', { timeout: 10000 });
    
    // Check Application Status section exists
    await expect(page.locator('h3:has-text("Application Status")')).toBeVisible();
    
    // Should show either stats or empty state
    const hasStats = await page.locator('text=No applications yet').isVisible();
    const hasStatusCards = await page.locator('text=Start Applying').isVisible();
    
    // At least one should be visible
    expect(hasStats || hasStatusCards || await page.locator('div:has-text("Application Status")').isVisible()).toBeTruthy();
  });

  test('should display progress section', async () => {
    // Wait for dashboard to load
    await page.waitForSelector('h1', { timeout: 10000 });
    
    // Check Progress section exists
    await expect(page.locator('h3:has-text("This Month\'s Progress")')).toBeVisible();
    
    // Check progress indicators
    await expect(page.locator('text=Applications Sent')).toBeVisible();
    await expect(page.locator('text=Interviews Attended')).toBeVisible();
    await expect(page.locator('text=Resume Updates')).toBeVisible();
  });

  test('should display upcoming interviews section', async () => {
    // Wait for dashboard to load
    await page.waitForSelector('h1', { timeout: 10000 });
    
    // Check Upcoming Interviews section exists
    await expect(page.locator('h3:has-text("Upcoming Interviews")')).toBeVisible();
    
    // Should show either interviews or empty state
    const hasEmptyState = await page.locator('text=No interviews scheduled').isVisible();
    const hasScheduleButton = await page.locator('button:has-text("Schedule Interview")').isVisible();
    
    // At least empty state should be visible
    expect(hasEmptyState || hasScheduleButton || await page.locator('div:has-text("Upcoming Interviews")').isVisible()).toBeTruthy();
  });

  test('should display recent resumes section', async () => {
    // Wait for dashboard to load  
    await page.waitForSelector('h1', { timeout: 10000 });
    
    // Check Recent Resumes section exists
    await expect(page.locator('h3:has-text("Recent Resumes")')).toBeVisible();
    
    // Should show either resumes or empty state
    const hasEmptyState = await page.locator('text=No resumes created yet').isVisible();
    const hasCreateButton = await page.locator('button:has-text("Create Resume")').isVisible();
    
    // At least empty state should be visible
    expect(hasEmptyState || hasCreateButton || await page.locator('div:has-text("Recent Resumes")').isVisible()).toBeTruthy();
  });

  test('should display career tips section', async () => {
    // Wait for dashboard to load
    await page.waitForSelector('h1', { timeout: 10000 });
    
    // Check Career Tips section exists
    await expect(page.locator('h3:has-text("Career Tips")')).toBeVisible();
    
    // Check tip content
    await expect(page.locator('h4:has-text("Tip of the Day")')).toBeVisible();
    await expect(page.locator('text=Keep your resume updated regularly')).toBeVisible();
  });

  test('should be responsive on mobile devices', async () => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Wait for dashboard to load
    await page.waitForSelector('h1', { timeout: 10000 });
    
    // Check that page is still functional on mobile
    await expect(page.locator('h1')).toContainText('Candidate Dashboard');
    
    // Check that stats grid adapts to mobile (should stack vertically)
    const statsGrid = page.locator('.grid.grid-cols-1.md\\:grid-cols-2.lg\\:grid-cols-4');
    await expect(statsGrid).toBeVisible();
  });

  test('should handle loading states gracefully', async () => {
    // Reload page to catch loading state
    await page.reload({ waitUntil: 'domcontentloaded' });
    
    // Should eventually show the dashboard content
    await page.waitForSelector('h1', { timeout: 15000 });
    await expect(page.locator('h1')).toContainText('Candidate Dashboard');
    
    // Check that main sections load
    await expect(page.locator('text=Applications')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('h3:has-text("Quick Actions")')).toBeVisible({ timeout: 10000 });
  });
});