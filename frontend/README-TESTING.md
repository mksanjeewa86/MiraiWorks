# E2E Testing with Playwright

This project uses Playwright for end-to-end testing to ensure the MiraiWorks application works correctly from a user's perspective.

## Setup

### Prerequisites
- Node.js 18 or higher
- Backend server running on http://localhost:8000
- Frontend server running on http://localhost:3000

### Installation
```bash
# Install Playwright
npm install @playwright/test

# Install browsers
npx playwright install
```

## Running Tests

### Basic Commands
```bash
# Run all tests
npm run test

# Run tests in headed mode (see browser)
npm run test:headed

# Run tests with UI mode (interactive)
npm run test:ui

# Run specific test file
npx playwright test tests/auth/login.spec.ts

# Run tests in specific browser
npx playwright test --project=chromium

# Debug mode (step through tests)
npm run test:debug
```

### Test Reports
```bash
# Show HTML report
npm run test:report

# Generate and show report after test run
npx playwright test --reporter=html
```

## Test Structure

```
tests/
├── fixtures/           # Test helpers and utilities
│   ├── test-users.ts   # Test user data
│   └── auth-helper.ts  # Authentication helper functions
├── auth/               # Authentication-related tests
│   ├── login.spec.ts
│   └── register.spec.ts
├── app/                # Main application tests
│   ├── dashboard.spec.ts
│   ├── jobs.spec.ts
│   └── resumes.spec.ts
└── example.spec.ts     # Basic smoke tests
```

## Test Data

The tests use predefined test users defined in `tests/fixtures/test-users.ts`:
- `jobSeeker` - Regular job seeker account
- `recruiter` - Recruiter account  
- `employer` - Employer account
- `admin` - Admin account

## Writing Tests

### Basic Test Structure
```typescript
import { test, expect } from '@playwright/test';
import { AuthHelper } from '../fixtures/auth-helper';

test.describe('Feature Name', () => {
  let authHelper: AuthHelper;

  test.beforeEach(async ({ page }) => {
    authHelper = new AuthHelper(page);
    // Setup before each test
  });

  test('should do something', async ({ page }) => {
    // Test implementation
    await page.goto('/some-page');
    await expect(page.locator('h1')).toBeVisible();
  });
});
```

### Test Data Attributes
Use `data-testid` attributes in your components for reliable element selection:

```tsx
// In React component
<button data-testid="login-button">Login</button>

// In test
await page.click('[data-testid="login-button"]');
```

### Authentication Helper
Use the `AuthHelper` class for authentication-related operations:

```typescript
// Login as job seeker
await authHelper.login('jobSeeker');

// Logout
await authHelper.logout();

// Ensure user is logged out
await authHelper.ensureLoggedOut();

// Check if user is logged in
const isLoggedIn = await authHelper.isLoggedIn();
```

## Configuration

The Playwright configuration is in `playwright.config.ts`:

- **Base URL**: http://localhost:3000
- **Browsers**: Chromium, Firefox, WebKit, Mobile Chrome, Mobile Safari
- **Reporters**: HTML report
- **Screenshots**: Only on failure
- **Videos**: Retained on failure
- **Traces**: On first retry

## CI/CD Integration

Tests run automatically in GitHub Actions:
- On push to `main` or `develop` branches
- On pull requests to `main`
- Full stack setup with MySQL database
- Artifacts uploaded for test results and reports

## Best Practices

### 1. Use Data Test IDs
```tsx
// Good
<button data-testid="submit-button">Submit</button>

// Avoid
<button className="btn btn-primary">Submit</button>
```

### 2. Wait for Elements
```typescript
// Good - explicitly wait
await expect(page.locator('[data-testid="content"]')).toBeVisible();

// Good - wait for network
await page.waitForLoadState('networkidle');

// Avoid - arbitrary waits
await page.waitForTimeout(5000);
```

### 3. Test User Flows, Not Implementation
```typescript
// Good - test user behavior
test('should allow user to create a resume', async ({ page }) => {
  await page.goto('/resumes');
  await page.click('[data-testid="create-resume"]');
  await expect(page).toHaveURL('/resumes/builder');
});

// Avoid - testing implementation details
test('should call createResume API', async ({ page }) => {
  // Don't test API calls directly in E2E tests
});
```

### 4. Keep Tests Independent
Each test should be able to run independently and in any order.

### 5. Use Page Object Model for Complex Flows
```typescript
class ResumePage {
  constructor(private page: Page) {}
  
  async createResume(title: string) {
    await this.page.click('[data-testid="create-resume"]');
    await this.page.fill('[data-testid="title-input"]', title);
    await this.page.click('[data-testid="save-button"]');
  }
}
```

## Troubleshooting

### Common Issues

1. **Test timeouts**: Increase timeout in `playwright.config.ts` or use `test.setTimeout()`
2. **Element not found**: Use `data-testid` attributes instead of CSS selectors
3. **Flaky tests**: Add proper waits with `waitForLoadState()` or `expect().toBeVisible()`
4. **Authentication issues**: Use `AuthHelper` and ensure proper cleanup

### Debugging
```bash
# Run with debug mode
npx playwright test --debug

# Run with browser visible
npx playwright test --headed --slowMo=1000

# Generate trace
npx playwright test --trace=on
```

### Environment Issues
- Ensure backend is running on port 8000
- Ensure frontend is running on port 3000
- Check database connectivity
- Verify environment variables

## Coverage

Tests cover:
- ✅ User authentication (login, register, logout)
- ✅ Dashboard functionality
- ✅ Job searching and application
- ✅ Resume management
- ✅ Navigation and routing
- ✅ Mobile responsiveness
- ✅ Error handling
- ✅ Form validation

## Future Improvements

- Add visual regression testing
- Implement API testing alongside E2E
- Add performance testing
- Expand mobile device testing
- Add accessibility testing