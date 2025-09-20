# Frontend Tests

This directory contains all frontend tests organized by category.

## Directory Structure

```
frontend/src/tests/
├── api/                    # API function tests
│   └── calendar.test.ts    # Calendar API tests
├── calendar/               # Calendar component tests
│   └── calendarEventCreation.test.tsx  # Event creation tests
├── pages/                  # Page component tests
│   └── activation.test.tsx # Account activation page tests
├── file-download-scenario.test.tsx     # File download integration tests
└── README.md              # This file
```

## Test Categories

### API Tests (`api/`)
Tests for API layer functions that interact with the backend.

### Calendar Tests (`calendar/`)
Tests for calendar-related components and functionality.

### Page Tests (`pages/`)
Tests for Next.js page components.

### Integration Tests (root level)
End-to-end and integration tests that span multiple components.

## Running Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run with coverage
npm run test:coverage

# Run specific test file
npm test -- calendar.test.ts

# Run tests in specific directory
npm test -- tests/api
```

## Test Standards

- All test files should follow the `*.test.ts` or `*.test.tsx` pattern
- Use descriptive test names and organize with `describe` blocks
- Mock external dependencies and API calls
- Test both success and error scenarios
- Maintain good test coverage for critical paths

## File Naming Convention

- API tests: `[module].test.ts`
- Component tests: `[componentName].test.tsx`
- Page tests: `[pageName].test.tsx`
- Integration tests: `[feature]-scenario.test.tsx`