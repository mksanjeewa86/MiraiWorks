import { defineConfig, devices } from '@playwright/test';

/**
 * @see https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  testDir: './tests/e2e',
  /* Output directory for test results */
  outputDir: './tests/results',
  /* Global setup for authentication */
  globalSetup: process.env.CI ? './tests/e2e/fixtures/global-setup.ts' : undefined,
  /* Run tests in files in parallel */
  fullyParallel: true,
  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env.CI,
  /* Retry on CI only */
  retries: process.env.CI ? 1 : 0,
  /* Use multiple workers for faster CI execution */
  workers: process.env.CI ? 4 : undefined,
  /* Global timeout for each test */
  timeout: process.env.CI ? 60 * 1000 : 30 * 1000,
  /* Reporter to use. See https://playwright.dev/docs/test-reporters */
  reporter: process.env.CI 
    ? [['github'], ['html', { outputFolder: './tests/reports/playwright-report', open: 'never' }]]
    : [['html', { outputFolder: './tests/reports/playwright-report' }]],
  /* Shared settings for all the projects below. See https://playwright.dev/docs/api/class-testoptions. */
  use: {
    /* Base URL to use in actions like `await page.goto('/')`. */
    baseURL: 'http://localhost:3000',

    /* Collect trace when retrying the failed test. See https://playwright.dev/docs/trace-viewer */
    trace: process.env.CI ? 'on-first-retry' : 'retain-on-failure',

    /* Take screenshot on failure */
    screenshot: 'only-on-failure',

    /* Record video on failure - only in CI to save time locally */
    video: process.env.CI ? 'retain-on-failure' : 'off',

    /* Timeout for each action (e.g. click, fill, etc.) */
    actionTimeout: process.env.CI ? 10 * 1000 : 15 * 1000,

    /* Timeout for each navigation action */
    navigationTimeout: process.env.CI ? 20 * 1000 : 30 * 1000,

    /* Ignore HTTPS errors in CI */
    ignoreHTTPSErrors: process.env.CI ? true : false,

    /* Disable animations for faster tests */
    launchOptions: {
      args: process.env.CI ? [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-background-timer-throttling',
        '--disable-backgrounding-occluded-windows',
        '--disable-renderer-backgrounding',
        '--disable-features=TranslateUI',
        '--disable-ipc-flooding-protection'
      ] : []
    }
  },

  /* Configure projects for major browsers */
  projects: process.env.CI ? [
    // In CI, focus only on Chromium for maximum speed
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
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
    timeout: process.env.CI ? 180 * 1000 : 120 * 1000,
    stderr: 'pipe',
    stdout: 'pipe',
  },
});