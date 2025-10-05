/**
 * Client-Side Rate Limiter
 *
 * Prevents abuse by limiting the number of requests within a time window.
 * Useful for protecting against accidental DDoS and reducing server load.
 */

interface RateLimitConfig {
  maxRequests: number;
  timeWindowMs: number;
}

interface RequestRecord {
  timestamps: number[];
  blocked: boolean;
  blockedUntil?: number;
}

export class RateLimiter {
  private requests: Map<string, RequestRecord> = new Map();
  private readonly config: RateLimitConfig;
  private cleanupInterval: NodeJS.Timeout | null = null;

  constructor(maxRequests: number = 100, timeWindowMs: number = 60000) {
    this.config = { maxRequests, timeWindowMs };
    this.startCleanup();
  }

  /**
   * Check if a request can be made for the given key
   * @param key - Unique identifier for the rate limit (e.g., URL or user action)
   * @returns true if request is allowed, false if rate limited
   */
  canMakeRequest(key: string): boolean {
    const now = Date.now();
    const record = this.getOrCreateRecord(key);

    // Check if currently blocked
    if (record.blocked && record.blockedUntil) {
      if (now < record.blockedUntil) {
        return false;
      }
      // Unblock if block period has expired
      record.blocked = false;
      record.blockedUntil = undefined;
    }

    // Remove old timestamps outside the time window
    record.timestamps = record.timestamps.filter(
      timestamp => now - timestamp < this.config.timeWindowMs
    );

    // Check if limit exceeded
    if (record.timestamps.length >= this.config.maxRequests) {
      // Block for the time window duration
      record.blocked = true;
      record.blockedUntil = now + this.config.timeWindowMs;
      return false;
    }

    // Add current timestamp
    record.timestamps.push(now);
    this.requests.set(key, record);
    return true;
  }

  /**
   * Get the remaining requests available for a key
   */
  getRemainingRequests(key: string): number {
    const record = this.requests.get(key);
    if (!record) return this.config.maxRequests;

    const now = Date.now();
    const validTimestamps = record.timestamps.filter(
      timestamp => now - timestamp < this.config.timeWindowMs
    );

    return Math.max(0, this.config.maxRequests - validTimestamps.length);
  }

  /**
   * Get time until rate limit resets (in milliseconds)
   */
  getResetTime(key: string): number {
    const record = this.requests.get(key);
    if (!record || record.timestamps.length === 0) return 0;

    const now = Date.now();
    const oldestTimestamp = Math.min(...record.timestamps);
    const resetTime = oldestTimestamp + this.config.timeWindowMs - now;

    return Math.max(0, resetTime);
  }

  /**
   * Check if a key is currently blocked
   */
  isBlocked(key: string): boolean {
    const record = this.requests.get(key);
    if (!record) return false;

    const now = Date.now();
    if (record.blocked && record.blockedUntil) {
      return now < record.blockedUntil;
    }

    return false;
  }

  /**
   * Manually reset rate limit for a key
   */
  reset(key: string): void {
    this.requests.delete(key);
  }

  /**
   * Clear all rate limit records
   */
  clearAll(): void {
    this.requests.clear();
  }

  /**
   * Get or create a request record for a key
   */
  private getOrCreateRecord(key: string): RequestRecord {
    const existing = this.requests.get(key);
    if (existing) return existing;

    const newRecord: RequestRecord = {
      timestamps: [],
      blocked: false,
    };
    this.requests.set(key, newRecord);
    return newRecord;
  }

  /**
   * Periodically clean up old records to prevent memory leaks
   */
  private startCleanup(): void {
    this.cleanupInterval = setInterval(() => {
      const now = Date.now();
      const keysToDelete: string[] = [];

      this.requests.forEach((record, key) => {
        // Remove timestamps outside time window
        record.timestamps = record.timestamps.filter(
          timestamp => now - timestamp < this.config.timeWindowMs
        );

        // If no recent activity and not blocked, remove the record
        if (record.timestamps.length === 0 && !record.blocked) {
          keysToDelete.push(key);
        }
      });

      keysToDelete.forEach(key => this.requests.delete(key));
    }, this.config.timeWindowMs);
  }

  /**
   * Stop the cleanup interval (call when destroying the rate limiter)
   */
  destroy(): void {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
      this.cleanupInterval = null;
    }
    this.clearAll();
  }
}

/**
 * Global API rate limiter instance
 * Limits: 100 requests per minute per endpoint
 */
export const apiRateLimiter = new RateLimiter(100, 60000);

/**
 * Rate limiter for sensitive operations (e.g., login attempts)
 * Limits: 5 requests per minute
 */
export const authRateLimiter = new RateLimiter(5, 60000);

/**
 * Rate limiter for file uploads
 * Limits: 10 uploads per minute
 */
export const uploadRateLimiter = new RateLimiter(10, 60000);

/**
 * Helper function to check rate limit and throw error if exceeded
 */
export function checkRateLimit(
  limiter: RateLimiter,
  key: string,
  errorMessage?: string
): void {
  if (!limiter.canMakeRequest(key)) {
    const resetTime = limiter.getResetTime(key);
    const resetSeconds = Math.ceil(resetTime / 1000);
    throw new Error(
      errorMessage || `Rate limit exceeded. Please try again in ${resetSeconds} seconds.`
    );
  }
}

/**
 * Example usage:
 *
 * import { apiRateLimiter, checkRateLimit } from '@/utils/rateLimiter';
 *
 * // In API client
 * export const makeRequest = async (url: string) => {
 *   checkRateLimit(apiRateLimiter, url);
 *   return fetch(url);
 * };
 *
 * // Check remaining requests
 * const remaining = apiRateLimiter.getRemainingRequests('/api/users');
 * console.log(`${remaining} requests remaining`);
 *
 * // Reset limit for a specific key
 * apiRateLimiter.reset('/api/users');
 */
