import { test, expect } from '@playwright/test';
import { AuthHelper } from '../fixtures/auth-helper';

test.describe('Admin Authentication & 2FA', () => {
  let authHelper: AuthHelper;

  test.beforeEach(async ({ page }) => {
    authHelper = new AuthHelper(page);
    await authHelper.ensureLoggedOut();
  });

  test('should require 2FA for super admin login', async ({ page }) => {
    await page.goto('/auth/login');

    // Try to login with super admin credentials (the fixed user)
    await page.fill('[data-testid="email-input"]', 'admin@miraiworks.com');
    await page.fill('[data-testid="password-input"]', 'password');
    await page.click('[data-testid="login-button"]');

    // Should be redirected to 2FA page or see 2FA prompt
    await page.waitForLoadState('networkidle');
    
    // Check for 2FA indicators (either redirect to 2FA page or 2FA form appears)
    const has2FAPage = await page.locator('h1:has-text("Two-Factor Authentication")').isVisible();
    const has2FAInput = await page.locator('[data-testid="2fa-code-input"]').isVisible();
    const has2FAPrompt = await page.locator('[data-testid="2fa-prompt"]').isVisible();
    
    // At least one 2FA indicator should be present
    expect(has2FAPage || has2FAInput || has2FAPrompt).toBe(true);

    // Should not be logged in yet (no access to dashboard)
    if (await page.url().includes('/dashboard')) {
      // If redirected to dashboard, user menu should not be accessible yet
      const userMenuVisible = await page.locator('[data-testid="user-menu"]').isVisible().catch(() => false);
      expect(userMenuVisible).toBe(false);
    }
  });

  test('should handle admin authentication without SQLAlchemy errors', async ({ page }) => {
    await page.goto('/auth/login');

    // Test with company admin credentials
    await page.fill('[data-testid="email-input"]', 'admin@techcorp.com');
    await page.fill('[data-testid="password-input"]', 'password');
    
    // Monitor network requests for any 500 errors (internal server errors)
    const serverErrors: string[] = [];
    page.on('response', response => {
      if (response.status() === 500) {
        serverErrors.push(`500 error on ${response.url()}`);
      }
    });

    await page.click('[data-testid="login-button"]');
    
    // Wait for the request to complete
    await page.waitForLoadState('networkidle');

    // Should not have any server errors (no SQLAlchemy MissingGreenlet errors)
    expect(serverErrors).toHaveLength(0);

    // Should get a proper response (either 2FA required or successful login)
    const currentUrl = page.url();
    expect(currentUrl).not.toContain('error');
  });

  test('should handle bcrypt password verification correctly', async ({ page }) => {
    await page.goto('/auth/login');

    // Test with the specific user that had bcrypt issues
    await page.fill('[data-testid="email-input"]', 'admin@miraiworks.com');
    await page.fill('[data-testid="password-input"]', 'password');

    // Monitor for authentication-related errors
    let authError = '';
    page.on('response', response => {
      if (response.url().includes('/api/auth/login') && response.status() === 500) {
        response.text().then(text => {
          if (text.includes('hash could not be identified')) {
            authError = 'bcrypt hash error detected';
          }
        });
      }
    });

    await page.click('[data-testid="login-button"]');
    await page.waitForLoadState('networkidle');

    // Should not have bcrypt hash errors
    expect(authError).toBe('');

    // Should either proceed to 2FA or show proper auth error (but not 500 error)
    const hasServerError = await page.locator('[data-testid="server-error"]').isVisible().catch(() => false);
    expect(hasServerError).toBe(false);
  });

  test('should differentiate between regular users and admin users', async ({ page }) => {
    // Test regular user first (should not require 2FA)
    await page.goto('/auth/login');
    
    // Try with candidate credentials (should exist from sample data)
    await page.fill('[data-testid="email-input"]', 'jane.candidate@email.com');
    await page.fill('[data-testid="password-input"]', 'password');
    await page.click('[data-testid="login-button"]');
    
    await page.waitForLoadState('networkidle');
    
    // Regular user might go straight to dashboard (no 2FA)
    const regularUserUrl = page.url();
    const regular2FARequired = regularUserUrl.includes('2fa') || regularUserUrl.includes('two-factor');
    
    // Now test admin user (should require 2FA)
    await authHelper.ensureLoggedOut();
    await page.goto('/auth/login');
    
    await page.fill('[data-testid="email-input"]', 'admin@miraiworks.com');
    await page.fill('[data-testid="password-input"]', 'password');
    await page.click('[data-testid="login-button"]');
    
    await page.waitForLoadState('networkidle');
    
    const adminUrl = page.url();
    const admin2FARequired = adminUrl.includes('2fa') || adminUrl.includes('two-factor') ||
                            await page.locator('[data-testid="2fa-code-input"]').isVisible().catch(() => false) ||
                            await page.locator('[data-testid="2fa-prompt"]').isVisible().catch(() => false);

    // Admin should have different behavior than regular user regarding 2FA
    if (!regular2FARequired) {
      expect(admin2FARequired).toBe(true);
    }
  });

  test('should handle role-based authentication with proper async loading', async ({ page }) => {
    // This test ensures that the role checking works without async issues
    const users = [
      { email: 'admin@miraiworks.com', role: 'super admin' },
      { email: 'admin@techcorp.com', role: 'company admin' },
      { email: 'jane.candidate@email.com', role: 'candidate' }
    ];

    for (const user of users) {
      await authHelper.ensureLoggedOut();
      await page.goto('/auth/login');

      await page.fill('[data-testid="email-input"]', user.email);
      await page.fill('[data-testid="password-input"]', 'password');

      // Monitor for async-related errors
      const asyncErrors: string[] = [];
      page.on('pageerror', error => {
        if (error.message.includes('MissingGreenlet') || 
            error.message.includes('greenlet_spawn') ||
            error.message.includes('await_only')) {
          asyncErrors.push(error.message);
        }
      });

      page.on('response', response => {
        if (response.status() === 500) {
          response.text().then(text => {
            if (text.includes('MissingGreenlet') || text.includes('greenlet_spawn')) {
              asyncErrors.push(`SQLAlchemy async error for ${user.role}`);
            }
          });
        }
      });

      await page.click('[data-testid="login-button"]');
      await page.waitForLoadState('networkidle');

      // Should not have any async-related errors
      expect(asyncErrors).toHaveLength(0);
    }
  });

  test('should handle authentication state properly after backend fixes', async ({ page }) => {
    await page.goto('/auth/login');

    // Test the fixed authentication flow
    await page.fill('[data-testid="email-input"]', 'admin@miraiworks.com');
    await page.fill('[data-testid="password-input"]', 'password');

    // Capture the login response
    let loginResponse: any = null;
    page.on('response', response => {
      if (response.url().includes('/api/auth/login')) {
        response.json().then(data => {
          loginResponse = data;
        });
      }
    });

    await page.click('[data-testid="login-button"]');
    await page.waitForLoadState('networkidle');

    // Wait a bit for the response to be captured
    await page.waitForTimeout(1000);

    // The response should have the expected structure based on our backend fix
    // (either successful login with tokens or 2FA required response)
    if (loginResponse) {
      expect(loginResponse).toHaveProperty('require_2fa');
      expect(typeof loginResponse.require_2fa).toBe('boolean');
      
      if (loginResponse.require_2fa) {
        // If 2FA is required, tokens should be empty
        expect(loginResponse.access_token).toBe('');
        expect(loginResponse.refresh_token).toBe('');
        expect(loginResponse.user).toBeNull();
      }
    }
  });
});