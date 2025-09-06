import { test, expect } from '@playwright/test';
import { AuthHelper } from '../fixtures/auth-helper';

test.describe('User Authentication - Login', () => {
  let authHelper: AuthHelper;

  test.beforeEach(async ({ page }) => {
    authHelper = new AuthHelper(page);
    await authHelper.ensureLoggedOut();
  });

  test('should display login page correctly', async ({ page }) => {
    await page.goto('/auth/login');

    // Check page title and heading
    await expect(page).toHaveTitle(/Login/);
    await expect(page.locator('h1')).toContainText('Sign In');

    // Check form elements are present
    await expect(page.locator('[data-testid="email-input"]')).toBeVisible();
    await expect(page.locator('[data-testid="password-input"]')).toBeVisible();
    await expect(page.locator('[data-testid="login-button"]')).toBeVisible();

    // Check links
    await expect(page.locator('a[href="/auth/register"]')).toBeVisible();
    await expect(page.locator('a[href="/auth/forgot-password"]')).toBeVisible();
  });

  test('should login successfully with valid credentials', async ({ page }) => {
    await authHelper.login('jobSeeker');

    // Should be redirected to dashboard
    await expect(page).toHaveURL('/dashboard');
    
    // Should see user menu indicating successful login
    await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();
  });

  test('should show error with invalid email', async ({ page }) => {
    await page.goto('/auth/login');

    await page.fill('[data-testid="email-input"]', 'invalid@test.com');
    await page.fill('[data-testid="password-input"]', 'Password123!');
    await page.click('[data-testid="login-button"]');

    // Should show error message
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
    await expect(page.locator('[data-testid="error-message"]')).toContainText('Invalid credentials');
  });

  test('should show error with invalid password', async ({ page }) => {
    await page.goto('/auth/login');

    await page.fill('[data-testid="email-input"]', 'jobseeker@test.com');
    await page.fill('[data-testid="password-input"]', 'wrongpassword');
    await page.click('[data-testid="login-button"]');

    // Should show error message
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
  });

  test('should show validation error for empty fields', async ({ page }) => {
    await page.goto('/auth/login');

    // Try to submit without filling fields
    await page.click('[data-testid="login-button"]');

    // Should show validation errors
    await expect(page.locator('[data-testid="email-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="password-error"]')).toBeVisible();
  });

  test('should navigate to register page', async ({ page }) => {
    await page.goto('/auth/login');

    await page.click('a[href="/auth/register"]');
    await expect(page).toHaveURL('/auth/register');
  });

  test('should navigate to forgot password page', async ({ page }) => {
    await page.goto('/auth/login');

    await page.click('a[href="/auth/forgot-password"]');
    await expect(page).toHaveURL('/auth/forgot-password');
  });

  test('should logout successfully', async ({ page }) => {
    // Login first
    await authHelper.login('jobSeeker');
    
    // Then logout
    await authHelper.logout();
    
    // Should be redirected to home or login page
    await expect(page).toHaveURL(/\/(|auth\/login)$/);
  });
});