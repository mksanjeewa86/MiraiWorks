/**
 * Secure Logger Utility
 *
 * Provides secure logging that:
 * - Only logs in development mode
 * - Sanitizes sensitive data before logging
 * - Prevents accidental exposure of tokens, passwords, and PII
 */

const isDevelopment = process.env.NODE_ENV === 'development';

/**
 * Sensitive keys that should be redacted from logs
 */
const SENSITIVE_KEYS = [
  'password',
  'token',
  'accesstoken',
  'refreshtoken',
  'secret',
  'apikey',
  'authorization',
  'cookie',
  'session',
  'csrf',
  'ssn',
  'creditcard',
  'cvv',
  'pin',
];

/**
 * Check if a key contains sensitive information
 */
function isSensitiveKey(key: string): boolean {
  const lowerKey = key.toLowerCase().replace(/[_-]/g, '');
  return SENSITIVE_KEYS.some(sensitiveKey => lowerKey.includes(sensitiveKey));
}

/**
 * Sanitize an object by redacting sensitive keys
 */
function sanitizeObject(obj: any, depth: number = 0): any {
  // Prevent infinite recursion
  if (depth > 5) return '[Max Depth Reached]';

  if (obj === null || obj === undefined) return obj;

  // Handle arrays
  if (Array.isArray(obj)) {
    return obj.map(item => sanitizeObject(item, depth + 1));
  }

  // Handle objects
  if (typeof obj === 'object') {
    // Handle special objects
    if (obj instanceof Date) return obj.toISOString();
    if (obj instanceof Error) {
      return {
        name: obj.name,
        message: obj.message,
        stack: isDevelopment ? obj.stack : '[REDACTED]',
      };
    }

    const sanitized: any = {};
    for (const key of Object.keys(obj)) {
      if (isSensitiveKey(key)) {
        sanitized[key] = '[REDACTED]';
      } else {
        sanitized[key] = sanitizeObject(obj[key], depth + 1);
      }
    }
    return sanitized;
  }

  // Primitive values
  return obj;
}

/**
 * Sanitize arguments for logging
 */
function sanitizeArgs(args: unknown[]): unknown[] {
  return args.map(arg => {
    if (typeof arg === 'object' && arg !== null) {
      return sanitizeObject(arg);
    }
    return arg;
  });
}

/**
 * Secure logger instance
 */
export const logger = {
  /**
   * Log informational messages (development only)
   */
  log: (...args: unknown[]) => {
    if (isDevelopment) {
      console.log(...sanitizeArgs(args));
    }
  },

  /**
   * Log informational messages with custom label (development only)
   */
  info: (...args: unknown[]) => {
    if (isDevelopment) {
      console.info(...sanitizeArgs(args));
    }
  },

  /**
   * Log warning messages (development only)
   */
  warn: (...args: unknown[]) => {
    if (isDevelopment) {
      console.warn(...sanitizeArgs(args));
    }
  },

  /**
   * Log error messages (always logged, but sanitized)
   */
  error: (...args: unknown[]) => {
    // Always log errors, but sanitize sensitive data
    const sanitized = sanitizeArgs(args);
    console.error(...sanitized);

    // In production, you might want to send errors to an error tracking service
    // Example: if (!isDevelopment) { sendToErrorTracking(sanitized); }
  },

  /**
   * Log debug messages (development only)
   */
  debug: (...args: unknown[]) => {
    if (isDevelopment) {
      console.debug(...sanitizeArgs(args));
    }
  },

  /**
   * Create a grouped log (development only)
   */
  group: (label: string, callback: () => void) => {
    if (isDevelopment) {
      console.group(label);
      try {
        callback();
      } finally {
        console.groupEnd();
      }
    }
  },

  /**
   * Log a table (development only)
   */
  table: (data: any) => {
    if (isDevelopment) {
      console.table(sanitizeObject(data));
    }
  },

  /**
   * Time a function execution (development only)
   */
  time: (label: string) => {
    if (isDevelopment) {
      console.time(label);
    }
  },

  /**
   * End timing a function execution (development only)
   */
  timeEnd: (label: string) => {
    if (isDevelopment) {
      console.timeEnd(label);
    }
  },
};

/**
 * Example usage:
 *
 * import { logger } from '@/utils/logger';
 *
 * // Safe - only logs in development
 * logger.log('User logged in', { userId: 123 });
 *
 * // Sensitive data is automatically redacted
 * logger.log('Auth response', { accessToken: 'secret123', user: { id: 1 } });
 * // Output: Auth response { accessToken: '[REDACTED]', user: { id: 1 } }
 *
 * // Errors are always logged (but sanitized)
 * logger.error('Failed to fetch', error);
 *
 * // Grouped logs
 * logger.group('User Authentication', () => {
 *   logger.log('Step 1: Validate credentials');
 *   logger.log('Step 2: Generate token');
 *   logger.log('Step 3: Set session');
 * });
 */

export default logger;
