import { defineConfig, devices } from '@playwright/test';

/**
 * @see https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  testDir: './tests/e2e',
  /* Output directory for test results */
  outputDir: './tests/results',
  /* Run tests in files in parallel */
  fullyParallel: true,
  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env.CI,
  /* Retry on CI only */
  retries: process.env.CI ? 2 : 0,
  /* Use multiple workers for faster CI execution */
  workers: process.env.CI ? '50%' : undefined,
  /* Reporter to use. See https://playwright.dev/docs/test-reporters */
  reporter: process.env.CI 
    ? [['github'], ['html', { outputFolder: './tests/reports/playwright-report', open: 'never' }]]
    : [['html', { outputFolder: './tests/reports/playwright-report' }]],
  /* Shared settings for all the projects below. See https://playwright.dev/docs/api/class-testoptions. */
  use: {
    /* Base URL to use in actions like `await page.goto('/')`. */
    baseURL: 'http://localhost:3000',

    /* Collect trace when retrying the failed test. See https://playwright.dev/docs/trace-viewer */
    trace: 'on-first-retry',

    /* Take screenshot on failure */
    screenshot: 'only-on-failure',

    /* Record video on failure - only in CI to save time locally */
    video: process.env.CI ? 'retain-on-failure' : 'off',

    /* Timeout for each action (e.g. click, fill, etc.) */
    actionTimeout: 15 * 1000,

    /* Timeout for each navigation action */
    navigationTimeout: 30 * 1000,
  },

  /* Configure projects for major browsers */
  projects: process.env.CI ? [
    // In CI, focus on Chromium for speed (most common browser)
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    // Test one mobile viewport
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
  ] : [
    // Locally, test all browsers
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },

    /* Test against branded browsers. */
    // {
    //   name: 'Microsoft Edge',
    //   use: { ...devices['Desktop Edge'], channel: 'msedge' },
    // },
    // {
    //   name: 'Google Chrome',
    //   use: { ...devices['Desktop Chrome'], channel: 'chrome' },
    // },
  ],

  /* Run your local dev server before starting the tests */
  webServer: {
    command: process.env.CI ? 'npm start' : 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
});