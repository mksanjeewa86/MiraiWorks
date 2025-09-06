import { test, expect } from '@playwright/test';
import { AuthHelper } from '../fixtures/auth-helper';

test.describe('User Authentication - Register', () => {
  let authHelper: AuthHelper;

  test.beforeEach(async ({ page }) => {
    authHelper = new AuthHelper(page);
    await authHelper.ensureLoggedOut();
  });

  test('should display register page correctly', async ({ page }) => {
    await page.goto('/auth/register');

    // Check page title and heading
    await expect(page).toHaveTitle(/Register/);
    await expect(page.locator('h1')).toContainText('Create Account');

    // Check form elements are present
    await expect(page.locator('[data-testid="fullname-input"]')).toBeVisible();
    await expect(page.locator('[data-testid="email-input"]')).toBeVisible();
    await expect(page.locator('[data-testid="password-input"]')).toBeVisible();
    await expect(page.locator('[data-testid="confirm-password-input"]')).toBeVisible();
    await expect(page.locator('[data-testid="role-select"]')).toBeVisible();
    await expect(page.locator('[data-testid="terms-checkbox"]')).toBeVisible();
    await expect(page.locator('[data-testid="register-button"]')).toBeVisible();

    // Check login link
    await expect(page.locator('a[href="/auth/login"]')).toBeVisible();
  });

  test('should register successfully with valid data', async ({ page }) => {
    await page.goto('/auth/register');

    // Fill registration form
    await page.fill('[data-testid="fullname-input"]', 'New User');
    await page.fill('[data-testid="email-input"]', `newuser${Date.now()}@test.com`);
    await page.fill('[data-testid="password-input"]', 'Password123!');
    await page.fill('[data-testid="confirm-password-input"]', 'Password123!');
    await page.selectOption('[data-testid="role-select"]', 'job_seeker');
    await page.check('[data-testid="terms-checkbox"]');

    // Submit form
    await page.click('[data-testid="register-button"]');

    // Should show success message or redirect
    await page.waitForLoadState('networkidle');
    
    // Check for success indicator (could be redirect or success message)
    const currentUrl = page.url();
    const hasSuccessMessage = await page.locator('[data-testid="success-message"]').isVisible().catch(() => false);
    
    expect(currentUrl.includes('/auth/login') || currentUrl.includes('/dashboard') || hasSuccessMessage).toBeTruthy();
  });

  test('should show error for duplicate email', async ({ page }) => {
    await page.goto('/auth/register');

    // Try to register with existing email
    await page.fill('[data-testid="fullname-input"]', 'Test User');
    await page.fill('[data-testid="email-input"]', 'jobseeker@test.com'); // Existing email
    await page.fill('[data-testid="password-input"]', 'Password123!');
    await page.fill('[data-testid="confirm-password-input"]', 'Password123!');
    await page.selectOption('[data-testid="role-select"]', 'job_seeker');
    await page.check('[data-testid="terms-checkbox"]');

    await page.click('[data-testid="register-button"]');

    // Should show error message
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
  });

  test('should show validation errors for invalid input', async ({ page }) => {
    await page.goto('/auth/register');

    // Fill invalid data
    await page.fill('[data-testid="fullname-input"]', ''); // Empty name
    await page.fill('[data-testid="email-input"]', 'invalid-email'); // Invalid email
    await page.fill('[data-testid="password-input"]', '123'); // Weak password
    await page.fill('[data-testid="confirm-password-input"]', '456'); // Different password

    await page.click('[data-testid="register-button"]');

    // Should show validation errors
    await expect(page.locator('[data-testid="fullname-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="email-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="password-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="confirm-password-error"]')).toBeVisible();
  });

  test('should show error when passwords do not match', async ({ page }) => {
    await page.goto('/auth/register');

    await page.fill('[data-testid="password-input"]', 'Password123!');
    await page.fill('[data-testid="confirm-password-input"]', 'DifferentPassword123!');

    // Trigger validation by clicking elsewhere or submitting
    await page.click('[data-testid="register-button"]');

    await expect(page.locator('[data-testid="confirm-password-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="confirm-password-error"]')).toContainText('match');
  });

  test('should require terms acceptance', async ({ page }) => {
    await page.goto('/auth/register');

    // Fill valid data but don't check terms
    await page.fill('[data-testid="fullname-input"]', 'Test User');
    await page.fill('[data-testid="email-input"]', 'test@test.com');
    await page.fill('[data-testid="password-input"]', 'Password123!');
    await page.fill('[data-testid="confirm-password-input"]', 'Password123!');
    await page.selectOption('[data-testid="role-select"]', 'job_seeker');

    await page.click('[data-testid="register-button"]');

    // Should show error about terms
    await expect(page.locator('[data-testid="terms-error"]')).toBeVisible();
  });

  test('should navigate to login page', async ({ page }) => {
    await page.goto('/auth/register');

    await page.click('a[href="/auth/login"]');
    await expect(page).toHaveURL('/auth/login');
  });

  test('should validate password strength requirements', async ({ page }) => {
    await page.goto('/auth/register');

    const weakPasswords = ['123', 'password', 'abc123', 'PASSWORD'];
    
    for (const password of weakPasswords) {
      await page.fill('[data-testid="password-input"]', password);
      await page.click('[data-testid="fullname-input"]'); // Trigger validation
      
      // Should show password strength indicator or error
      const hasError = await page.locator('[data-testid="password-error"]').isVisible();
      const hasWeakIndicator = await page.locator('[data-testid="password-strength"]').isVisible();
      
      expect(hasError || hasWeakIndicator).toBeTruthy();
      
      // Clear field for next test
      await page.fill('[data-testid="password-input"]', '');
    }
  });
});