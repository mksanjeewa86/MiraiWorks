import { Page, expect } from '@playwright/test';
import { testUsers } from './test-users';

export class AuthHelper {
  constructor(private page: Page) {}

  async login(userType: keyof typeof testUsers) {
    const user = testUsers[userType];
    
    // Navigate to login page with faster loading
    await this.page.goto('/auth/login', { waitUntil: 'domcontentloaded' });
    
    // Fill login form
    await this.page.fill('[data-testid="email-input"]', user.email);
    await this.page.fill('[data-testid="password-input"]', user.password);
    
    // Submit form and wait for navigation
    const [response] = await Promise.all([
      this.page.waitForResponse(response => response.url().includes('/api/auth/login')),
      this.page.click('[data-testid="login-button"]')
    ]);
    
    // Wait for successful login redirect with timeout
    await expect(this.page).toHaveURL('/dashboard', { timeout: 10000 });
    
    // Verify user is logged in by checking for user menu or profile info
    await expect(this.page.locator('[data-testid="user-menu"]')).toBeVisible({ timeout: 5000 });
  }

  async logout() {
    // Click user menu to open dropdown
    await this.page.click('[data-testid="user-menu"]');
    
    // Click logout button
    await this.page.click('[data-testid="logout-button"]');
    
    // Verify redirect to home or login page
    await expect(this.page).toHaveURL(/\/(|auth\/login)$/);
  }

  async register(userType: keyof typeof testUsers) {
    const user = testUsers[userType];
    
    // Navigate to register page
    await this.page.goto('/auth/register');
    
    // Fill registration form
    await this.page.fill('[data-testid="fullname-input"]', user.fullName);
    await this.page.fill('[data-testid="email-input"]', user.email);
    await this.page.fill('[data-testid="password-input"]', user.password);
    await this.page.fill('[data-testid="confirm-password-input"]', user.password);
    
    // Select user role
    await this.page.selectOption('[data-testid="role-select"]', user.role);
    
    // Accept terms
    await this.page.check('[data-testid="terms-checkbox"]');
    
    // Submit form
    await this.page.click('[data-testid="register-button"]');
    
    // Wait for successful registration redirect or confirmation
    await this.page.waitForLoadState('networkidle');
  }

  async ensureLoggedOut() {
    try {
      // Clear all storage first for faster logout
      await this.page.context().clearCookies();
      await this.page.evaluate(() => {
        localStorage.clear();
        sessionStorage.clear();
      });
      
      // Check if still logged in after clearing storage
      await this.page.goto('/dashboard', { timeout: 3000, waitUntil: 'domcontentloaded' });
      
      // If we can still access dashboard, do proper logout
      if (await this.page.locator('[data-testid="user-menu"]').isVisible({ timeout: 2000 })) {
        await this.logout();
      }
    } catch {
      // User is already logged out or page doesn't exist
      // This is expected when clearing storage works
    }
  }

  async isLoggedIn(): Promise<boolean> {
    try {
      await this.page.goto('/dashboard', { timeout: 5000 });
      return await this.page.locator('[data-testid="user-menu"]').isVisible();
    } catch {
      return false;
    }
  }
}