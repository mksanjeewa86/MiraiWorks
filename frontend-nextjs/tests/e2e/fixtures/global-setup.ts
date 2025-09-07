import { chromium, FullConfig } from '@playwright/test';
import { testUsers } from './test-users';

async function globalSetup(config: FullConfig) {
  // Create a browser instance
  const browser = await chromium.launch();
  
  // Setup authentication states for different user types
  const authStates = ['jobSeeker', 'recruiter', 'admin', 'superAdmin'] as const;
  
  for (const userType of authStates) {
    const page = await browser.newPage();
    const user = testUsers[userType];
    
    // Navigate to login page
    await page.goto('http://localhost:3000/auth/login', { waitUntil: 'domcontentloaded' });
    
    // Login
    await page.fill('[data-testid="email-input"]', user.email);
    await page.fill('[data-testid="password-input"]', user.password);
    
    const [response] = await Promise.all([
      page.waitForResponse(response => response.url().includes('/api/auth/login')),
      page.click('[data-testid="login-button"]')
    ]);
    
    // Wait for login success
    await page.waitForURL('**/dashboard');
    
    // Save authentication state
    await page.context().storageState({ 
      path: `tests/auth-states/${userType}.json` 
    });
    
    await page.close();
  }
  
  await browser.close();
}

export default globalSetup;