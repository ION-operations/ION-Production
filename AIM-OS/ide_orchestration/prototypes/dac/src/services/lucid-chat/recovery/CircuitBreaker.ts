/**
 * Circuit Breaker
 * 
 * Prevents cascading failures by opening circuit after threshold failures
 */

export interface CircuitBreakerOptions {
  failureThreshold?: number
  recoveryTimeout?: number
  halfOpenMaxAttempts?: number
}

export type CircuitState = 'closed' | 'open' | 'half-open'

export class CircuitBreaker {
  private state: CircuitState = 'closed'
  private failures: number = 0
  private lastFailureTime: number = 0
  private halfOpenAttempts: number = 0

  constructor(
    private options: CircuitBreakerOptions = {}
  ) {
    this.options = {
      failureThreshold: 5,
      recoveryTimeout: 60000, // 1 minute
      halfOpenMaxAttempts: 3,
      ...options,
    }
  }

  /**
   * Execute function with circuit breaker protection
   */
  async execute<T>(fn: () => Promise<T>): Promise<T> {
    // Check circuit state
    if (this.state === 'open') {
      // Check if recovery timeout has passed
      const timeSinceLastFailure = Date.now() - this.lastFailureTime
      if (timeSinceLastFailure >= this.options.recoveryTimeout!) {
        // Transition to half-open
        this.state = 'half-open'
        this.halfOpenAttempts = 0
      } else {
        throw new Error('Circuit breaker is open - service unavailable')
      }
    }

    try {
      const result = await fn()

      // Success - reset failures
      if (this.state === 'half-open') {
        this.halfOpenAttempts++
        if (this.halfOpenAttempts >= this.options.halfOpenMaxAttempts!) {
          // Transition to closed
          this.state = 'closed'
          this.failures = 0
          this.halfOpenAttempts = 0
        }
      } else {
        // Closed state - reset failures on success
        this.failures = 0
      }

      return result
    } catch (error) {
      this.failures++
      this.lastFailureTime = Date.now()

      // Check if threshold exceeded
      if (this.failures >= this.options.failureThreshold!) {
        this.state = 'open'
      } else if (this.state === 'half-open') {
        // Half-open failure - back to open
        this.state = 'open'
        this.halfOpenAttempts = 0
      }

      throw error
    }
  }

  /**
   * Get current circuit state
   */
  getState(): CircuitState {
    return this.state
  }

  /**
   * Reset circuit breaker
   */
  reset(): void {
    this.state = 'closed'
    this.failures = 0
    this.lastFailureTime = 0
    this.halfOpenAttempts = 0
  }

  /**
   * Get failure count
   */
  getFailureCount(): number {
    return this.failures
  }

  /**
   * Check if circuit is open
   */
  isOpen(): boolean {
    return this.state === 'open'
  }
}

