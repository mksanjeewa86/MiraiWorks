// Basic Jest setup for Node environment tests

// Mock fetch globally
global.fetch = jest.fn();

// Basic console setup
global.console = {
  ...console,
  log: jest.fn(),
  error: jest.fn(),
  warn: jest.fn(),
  info: jest.fn(),
  debug: jest.fn(),
};
