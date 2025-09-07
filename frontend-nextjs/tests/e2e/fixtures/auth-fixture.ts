import { test as base, BrowserContext } from '@playwright/test';
import path from 'path';
import { testUsers } from './test-users';

type UserType = keyof typeof testUsers;

export const test = base.extend<{
  authenticatedContext: (userType: UserType) => Promise<BrowserContext>;
}>({
  authenticatedContext: async ({ browser }, use) => {
    const contextCreator = async (userType: UserType) => {
      // In CI, use pre-authenticated state files
      if (process.env.CI) {
        const authFile = path.join(__dirname, '..', '..', 'auth-states', `${userType}.json`);
        return await browser.newContext({ storageState: authFile });
      }
      
      // In local development, do quick login
      const context = await browser.newContext();
      const page = await context.newPage();
      const user = testUsers[userType];
      
      await page.goto('/auth/login', { waitUntil: 'domcontentloaded' });
      await page.fill('[data-testid="email-input"]', user.email);
      await page.fill('[data-testid="password-input"]', user.password);
      
      await Promise.all([
        page.waitForResponse(response => response.url().includes('/api/auth/login')),
        page.click('[data-testid="login-button"]')
      ]);
      
      await page.waitForURL('**/dashboard');
      await page.close();
      
      return context;
    };
    
    await use(contextCreator);
  },
});

export { expect } from '@playwright/test';