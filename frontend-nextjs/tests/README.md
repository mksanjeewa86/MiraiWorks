# Testing Framework

This directory contains all test-related files for the MiraiWorks frontend application, organized for better maintainability and clarity.

## Directory Structure

```
tests/
├── config/                 # Test configuration files
│   └── playwright.config.ts    # Playwright test configuration
├── e2e/                    # End-to-end tests
│   ├── app/                    # Application flow tests
│   │   ├── dashboard.spec.ts
│   │   ├── jobs.spec.ts
│   │   └── resumes.spec.ts
│   ├── auth/                   # Authentication tests
│   │   ├── login.spec.ts
│   │   └── register.spec.ts
│   ├── fixtures/               # Test helpers and data
│   │   ├── auth-helper.ts
│   │   └── test-users.ts
│   └── example.spec.ts         # Basic smoke tests
├── reports/                # Test reports and artifacts
│   └── playwright-report/     # HTML reports from test runs
├── results/                # Test execution results
│   └── [test-run-folders]/    # Screenshots, videos, traces
└── utils/                  # Test utilities and tools
    └── test-sidebar/          # Debug page for sidebar testing
        └── page.tsx
```

## Test Types

### 🔧 **E2E Tests** (`tests/e2e/`)
End-to-end tests using Playwright that simulate real user interactions:

- **Authentication**: Login, register, logout flows
- **Dashboard**: User stats, navigation, responsive design
- **Jobs**: Search, filtering, application process
- **Resumes**: CRUD operations, preview, sharing

### ⚙️ **Configuration** (`tests/config/`)
Test environment and tool configurations:

- **Playwright Config**: Browser settings, test directories, reporting

### 📊 **Reports** (`tests/reports/`)
Generated test reports and documentation:

- **HTML Reports**: Interactive test results with screenshots/videos
- **Coverage Reports**: Code coverage analysis (if enabled)

### 📁 **Results** (`tests/results/`)
Test execution artifacts:

- **Screenshots**: Failure screenshots for debugging
- **Videos**: Test execution recordings
- **Traces**: Detailed execution traces for debugging

### 🛠️ **Utils** (`tests/utils/`)
Testing utilities and debug tools:

- **Debug Pages**: Special pages for testing specific features
- **Helper Functions**: Reusable test utilities
- **Mock Data**: Test data generators

## Running Tests

### Basic Commands
```bash
# Run all tests
npm run test

# Run tests with browser visible
npm run test:headed

# Run tests with interactive UI
npm run test:ui

# Debug tests step by step
npm run test:debug

# Show HTML report
npm run test:report
```

### Specific Test Categories
```bash
# Run only authentication tests
npx playwright test tests/e2e/auth/

# Run only dashboard tests
npx playwright test tests/e2e/app/dashboard.spec.ts

# Run tests in specific browser
npx playwright test --project=chromium
```

## Test Development

### Creating New Tests
1. Place new test files in appropriate `tests/e2e/` subdirectory
2. Use existing fixtures and helpers from `tests/e2e/fixtures/`
3. Follow naming convention: `*.spec.ts`

### Test Data
- **User Data**: Use `tests/e2e/fixtures/test-users.ts` for test accounts
- **Auth Helper**: Use `tests/e2e/fixtures/auth-helper.ts` for login/logout
- **Mock Data**: Add reusable test data to fixtures

### Debug Tools
- **Sidebar Debug**: Visit `/test-sidebar` page (in development)
- **Element Inspector**: Use browser dev tools with `data-testid` attributes
- **Trace Viewer**: Use `npx playwright show-trace` for detailed debugging

## Best Practices

### 1. Use Data Test IDs
```tsx
// Good - reliable selectors
<button data-testid="login-button">Login</button>

// Avoid - brittle selectors
<button className="btn btn-primary">Login</button>
```

### 2. Page Object Pattern
```typescript
// Good - reusable page objects
class LoginPage {
  constructor(private page: Page) {}
  
  async login(email: string, password: string) {
    await this.page.fill('[data-testid="email-input"]', email);
    await this.page.fill('[data-testid="password-input"]', password);
    await this.page.click('[data-testid="login-button"]');
  }
}
```

### 3. Proper Waits
```typescript
// Good - wait for elements
await expect(page.locator('[data-testid="content"]')).toBeVisible();

// Good - wait for network
await page.waitForLoadState('networkidle');

// Avoid - arbitrary waits
await page.waitForTimeout(5000);
```

### 4. Independent Tests
- Each test should be able to run independently
- Use `beforeEach` for setup and cleanup
- Don't rely on test execution order

## CI/CD Integration

Tests run automatically in GitHub Actions:
- **Triggers**: Push to `main`/`develop`, Pull Requests
- **Environment**: Full stack with MySQL database
- **Artifacts**: Test reports and failure screenshots uploaded
- **Browsers**: Chrome, Firefox, Safari, Mobile

## Troubleshooting

### Common Issues
1. **Element not found**: Check `data-testid` attributes exist
2. **Test timeouts**: Increase timeout or add proper waits
3. **Flaky tests**: Add `waitForLoadState()` or element visibility checks
4. **Permission errors**: Ensure test files have proper permissions

### Debug Commands
```bash
# Run single test in debug mode
npx playwright test auth/login.spec.ts --debug

# Run with trace recording
npx playwright test --trace=on

# Show trace for failed test
npx playwright show-trace tests/results/[test-name]/trace.zip
```

## Configuration

### Environment Variables
- `CI`: Set to enable CI-specific behavior
- `PLAYWRIGHT_BROWSERS_PATH`: Custom browser installation path
- `DEBUG`: Enable debug logging

### Browser Configuration
Tests run on multiple browsers and devices:
- Desktop: Chrome, Firefox, Safari
- Mobile: Chrome (Pixel 5), Safari (iPhone 12)

### Reporting
- **Format**: HTML with interactive timeline
- **Location**: `tests/reports/playwright-report/`
- **Includes**: Screenshots, videos, traces on failure

## Maintenance

### Regular Tasks
1. **Update Dependencies**: Keep Playwright version current
2. **Clean Reports**: Periodically clean old test reports/results
3. **Review Tests**: Update tests when features change
4. **Monitor CI**: Watch for flaky tests in CI pipeline

### File Cleanup
```bash
# Clean test results and reports
npm run test:clean

# Or manually
rm -rf tests/results/* tests/reports/*
```

This organized structure makes testing more maintainable, discoverable, and professional. All test-related concerns are now centralized and properly categorized.