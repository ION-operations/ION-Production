/**
 * Rate Limiter
 * 
 * Token bucket rate limiting
 */

export interface RateLimitConfig {
  limit: number // Max requests
  window: number // Time window in milliseconds
  burst?: number // Burst allowance
}

export interface RateLimitStatus {
  allowed: boolean
  remaining: number
  resetAt: number
  limit: number
}

export class RateLimiter {
  private buckets: Map<string, {
    tokens: number
    lastRefill: number
    limit: number
    window: number
    burst: number
  }> = new Map()

  /**
   * Check if request is allowed
   */
  checkLimit(key: string, config: RateLimitConfig): RateLimitStatus {
    const { limit, window, burst = limit } = config
    const now = Date.now()

    // Get or create bucket
    let bucket = this.buckets.get(key)
    if (!bucket) {
      bucket = {
        tokens: limit,
        lastRefill: now,
        limit,
        window,
        burst,
      }
      this.buckets.set(key, bucket)
    }

    // Refill tokens
    const timeSinceRefill = now - bucket.lastRefill
    const tokensToAdd = Math.floor((timeSinceRefill / window) * limit)
    
    if (tokensToAdd > 0) {
      bucket.tokens = Math.min(bucket.limit + bucket.burst, bucket.tokens + tokensToAdd)
      bucket.lastRefill = now
    }

    // Check if request allowed
    const allowed = bucket.tokens >= 1
    const remaining = Math.max(0, bucket.tokens - 1)
    const resetAt = now + window

    if (allowed) {
      bucket.tokens--
    }

    return {
      allowed,
      remaining,
      resetAt,
      limit: bucket.limit,
    }
  }

  /**
   * Consume tokens
   */
  consume(key: string, tokens: number, config: RateLimitConfig): boolean {
    const status = this.checkLimit(key, config)
    
    if (status.allowed && status.remaining >= tokens - 1) {
      const bucket = this.buckets.get(key)!
      bucket.tokens -= tokens
      return true
    }

    return false
  }

  /**
   * Get remaining tokens
   */
  getRemaining(key: string, config: RateLimitConfig): number {
    const status = this.checkLimit(key, config)
    return status.remaining
  }

  /**
   * Reset rate limit for key
   */
  reset(key: string): void {
    this.buckets.delete(key)
  }

  /**
   * Reset all rate limits
   */
  resetAll(): void {
    this.buckets.clear()
  }

  /**
   * Get rate limit status
   */
  getStatus(key: string, config: RateLimitConfig): RateLimitStatus {
    return this.checkLimit(key, config)
  }

  /**
   * Clean old buckets (optional cleanup)
   */
  cleanOldBuckets(maxAge: number = 3600000): number {
    const now = Date.now()
    let count = 0

    for (const [key, bucket] of this.buckets.entries()) {
      const age = now - bucket.lastRefill
      if (age > maxAge) {
        this.buckets.delete(key)
        count++
      }
    }

    return count
  }
}

