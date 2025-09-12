# MiraiWorks Testing Guide

This document provides comprehensive information about the testing setup and procedures for the MiraiWorks messaging system.

## Test Structure Overview

```
MiraiWorks/
├── backend/
│   ├── tests/                      # Backend Python tests
│   │   ├── conftest.py            # Test fixtures and configuration
│   │   ├── test_direct_message_service.py
│   │   ├── test_notification_service.py
│   │   ├── test_direct_messages_api.py
│   │   └── test_messaging_websocket.py
│   └── scripts/
│       └── setup_test_data.py     # E2E test data setup
├── frontend-nextjs/
│   ├── tests/
│   │   ├── e2e/                   # End-to-end tests
│   │   │   ├── messaging/         # Messaging E2E tests
│   │   │   ├── fixtures/          # Test fixtures and helpers
│   │   │   └── test-files/        # Test files for upload tests
│   │   └── unit/                  # Unit tests (if any)
│   ├── jest.setup.js              # Jest configuration
│   └── playwright.config.ts       # Playwright configuration
├── .github/
│   └── workflows/
│       └── test.yml               # CI/CD pipeline
├── docker-compose.test.yml        # Docker test environment
└── scripts/
    └── run-tests.sh               # Test runner script
```

## Test Types

### 1. Backend Tests (Python/pytest)

**Location**: `backend/tests/`

**Coverage**: 
- Direct message service functionality
- Notification service
- WebSocket connections
- API endpoints
- Database operations

**Run Commands**:
```bash
cd backend
pytest tests/ -v                           # Run all tests
pytest tests/ -v --cov=app                # With coverage
pytest tests/test_direct_message_service.py # Single test file
```

### 2. Frontend E2E Tests (Playwright)

**Location**: `frontend-nextjs/tests/e2e/messaging/`

**Test Files**:
- `core-messaging.spec.ts` - Basic messaging functionality
- `search-functionality.spec.ts` - Message search and filtering
- `notifications.spec.ts` - Notification system
- `real-time-features.spec.ts` - WebSocket real-time features
- `file-sharing.spec.ts` - File upload/download
- `integration.spec.ts` - Cross-feature integration tests

**Run Commands**:
```bash
cd frontend-nextjs
npm run test                    # Run all E2E tests
npm run test:headed            # Run with browser UI
npm run test:debug             # Debug mode
npm run test:ui                # Playwright UI mode
npm run test:ci                # CI mode (chromium only)
```

### 3. Security Tests

**Tools**: 
- Bandit (Python security)
- npm audit (Node.js security)

**Run Commands**:
```bash
# Python security scan
cd backend && bandit -r app/

# Node.js security scan  
cd frontend-nextjs && npm audit
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL (for local testing)

### Run All Tests (Recommended)

```bash
# Make script executable (Linux/Mac)
chmod +x scripts/run-tests.sh

# Run complete test suite
./scripts/run-tests.sh

# Run with Docker (isolated environment)
./scripts/run-tests.sh --docker

# Run specific test suites
./scripts/run-tests.sh --backend-only
./scripts/run-tests.sh --frontend-only
./scripts/run-tests.sh --e2e-only
```

### Manual Setup

#### Backend Tests
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-cov httpx
pytest tests/ -v --cov=app
```

#### Frontend E2E Tests
```bash
cd frontend-nextjs
npm ci
npx playwright install chromium
npm run test
```

## CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/test.yml`) runs:

1. **Backend Tests** - Python unit and integration tests
2. **Frontend Tests** - Unit tests, linting, build verification
3. **E2E Tests** - Full application testing with real database
4. **Security Scans** - Vulnerability detection
5. **Performance Tests** - Lighthouse audits (main branch only)

**Triggers**:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`

## Test Data

### Backend Test Fixtures

**File**: `backend/tests/conftest.py`

**Provides**:
- Test database session
- Test companies
- Test users with different roles
- Test messages and conversations
- Mock services (email, notifications, WebSocket)

### E2E Test Data

**Setup Script**: `backend/scripts/setup_test_data.py`

**Creates**:
- Test companies and users
- Sample conversations
- Message history for search testing
- Various user roles (candidate, recruiter, admin)

**Test Users**:
```python
{
  "jane.candidate@email.com": "candidate",
  "john.candidate@email.com": "candidate", 
  "recruiter@globalrecruiters.com": "recruiter",
  "admin@testcompany.com": "company_admin",
  "admin@miraiworks.com": "super_admin"
}
# Password for all test users: "password"
```

## Docker Testing

### Test Environment

**File**: `docker-compose.test.yml`

**Services**:
- `test-db` - PostgreSQL test database
- `backend-test` - Backend test runner
- `frontend-test` - Frontend unit test runner
- `e2e-test` - E2E test runner with Playwright
- `backend-test-server` - Backend server for E2E tests
- `test-results` - Test results collector

### Run with Docker

```bash
# Full test suite
docker-compose -f docker-compose.test.yml up --build

# Individual services
docker-compose -f docker-compose.test.yml up backend-test
docker-compose -f docker-compose.test.yml up e2e-test

# View results
docker-compose -f docker-compose.test.yml up test-results
```

## Test Configuration

### Backend Configuration

**File**: `backend/tests/conftest.py`

**Key Settings**:
- SQLite in-memory database for speed
- Async test session management
- Mock services for external dependencies
- Test data factories

### E2E Configuration

**File**: `frontend-nextjs/playwright.config.ts`

**Key Settings**:
- Multiple browser testing (local) vs Chromium only (CI)
- Automatic test data setup
- Screenshot and video capture on failure
- Optimized CI settings

### Environment Variables

**Backend Tests**:
```bash
DATABASE_URL=sqlite+aiosqlite:///./test_messaging.db
ENVIRONMENT=test
SECRET_KEY=test_secret
EMAIL_HOST=smtp.test.com
```

**E2E Tests**:
```bash
CI=true
BACKEND_URL=http://localhost:8000
NODE_ENV=test
```

## Writing Tests

### Backend Test Example

```python
@pytest.mark.asyncio
async def test_send_message(db_session: AsyncSession, test_user: User, test_user2: User):
    message_data = DirectMessageCreate(
        recipient_id=test_user2.id,
        content="Test message",
        type=MessageType.TEXT
    )
    
    result = await direct_message_service.send_message(
        db_session, test_user.id, message_data
    )
    
    assert result.content == "Test message"
    assert result.sender_id == test_user.id
```

### E2E Test Example

```typescript
test('should send a text message', async ({ authenticatedContext }) => {
  const context = await authenticatedContext('candidate1');
  const page = await context.newPage();
  
  await page.goto('/messages');
  await MessagingTestUtils.selectFirstConversation(page);
  
  const messageText = 'Test E2E message';
  await MessagingTestUtils.sendTextMessage(page, messageText);
  
  await expect(page.locator(`[data-testid="message-bubble"]:has-text("${messageText}")`))
    .toBeVisible();
});
```

## Debugging Tests

### Backend Debugging

```bash
# Run single test with verbose output
pytest tests/test_direct_message_service.py::test_send_message -v -s

# Debug with pdb
pytest tests/test_direct_message_service.py::test_send_message --pdb

# Coverage report
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

### E2E Debugging

```bash
# Run in headed mode
npm run test:headed

# Debug specific test
npx playwright test messaging/core-messaging.spec.ts --debug

# View test report
npm run test:report

# Screenshot debugging
npx playwright test --trace=on
```

## Test Reports

### Backend Coverage

- **HTML Report**: `backend/htmlcov/index.html`
- **XML Report**: `backend/coverage.xml`
- **Terminal**: Coverage summary in console

### E2E Reports

- **HTML Report**: `frontend-nextjs/tests/reports/playwright-report/index.html`
- **Screenshots**: `frontend-nextjs/tests/results/`
- **Videos**: `frontend-nextjs/tests/results/` (on failure)

### Security Reports

- **Bandit**: `test-results/bandit-report.json`
- **npm audit**: `test-results/npm-audit.json`

## Best Practices

### Test Organization

1. **Arrange-Act-Assert** pattern
2. **Descriptive test names** that explain the scenario
3. **Independent tests** that don't rely on execution order
4. **Proper cleanup** in teardown methods
5. **Realistic test data** that mimics production scenarios

### Performance

1. **Use SQLite** for fast backend tests
2. **Parallel execution** where possible
3. **Mock external services** to avoid network delays
4. **Selective browser testing** (Chromium only in CI)
5. **Efficient test data setup**

### Maintenance

1. **Regular dependency updates**
2. **Test data cleanup** after each test
3. **Flaky test identification** and resolution
4. **Coverage monitoring** and improvement
5. **Documentation updates** with code changes

## Troubleshooting

### Common Issues

**Database Connection Errors**:
```bash
# Ensure test database is running
docker-compose -f docker-compose.test.yml up test-db

# Check connection
psql -h localhost -p 5433 -U test_user -d test_miraiworks
```

**E2E Test Failures**:
```bash
# Install browsers
npx playwright install

# Check backend server
curl http://localhost:8000/health

# Run with debugging
npm run test:debug
```

**Permission Issues**:
```bash
# Make scripts executable
chmod +x scripts/run-tests.sh

# Fix node_modules permissions
sudo chown -R $(whoami) node_modules/
```

### Getting Help

1. **Check logs**: Test output usually contains helpful error messages
2. **View screenshots**: E2E test failures include screenshots
3. **Use debug mode**: Both pytest and Playwright have debug options
4. **Check CI logs**: GitHub Actions provides detailed logs
5. **Review test data**: Ensure test setup is correct

## Integration with Development Workflow

### Pre-commit Hooks

Consider adding pre-commit hooks to run tests automatically:

```bash
# Install pre-commit
pip install pre-commit

# Setup hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### IDE Integration

**VS Code Extensions**:
- Python Test Explorer
- Playwright Test for VS Code
- Coverage Gutters

**PyCharm/IntelliJ**:
- Built-in pytest runner
- Coverage visualization
- Playwright plugin

This comprehensive testing setup ensures the MiraiWorks messaging system is thoroughly validated across all layers and scenarios.