/**
 * Utility Type Definitions
 * Types for utility functions and classes
 */

/**
 * Rate limiter configuration
 */
export interface RateLimitConfig {
  maxRequests: number;
  timeWindowMs: number;
}

/**
 * Request record for tracking rate limit state
 */
export interface RequestRecord {
  timestamps: number[];
  blocked: boolean;
  blockedUntil?: number;
}
