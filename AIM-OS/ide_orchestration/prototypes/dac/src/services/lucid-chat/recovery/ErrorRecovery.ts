/**
 * Error Recovery
 * 
 * Orchestrates multiple recovery strategies
 */

import { RetryManager } from './RetryManager'
import { CircuitBreaker } from './CircuitBreaker'

export interface RecoveryStrategy {
  name: string
  priority: number
  execute: <T>(fn: () => Promise<T>, error: Error) => Promise<T>
}

export interface ErrorRecoveryOptions {
  retry?: RetryManager
  circuitBreaker?: CircuitBreaker
  fallback?: <T>() => Promise<T>
  strategies?: RecoveryStrategy[]
}

export class ErrorRecovery {
  private retryManager: RetryManager
  private circuitBreaker: CircuitBreaker | null = null
  private fallback: (<T>() => Promise<T>) | null = null
  private strategies: RecoveryStrategy[] = []

  constructor(options: ErrorRecoveryOptions = {}) {
    this.retryManager = options.retry || RetryManager
    this.circuitBreaker = options.circuitBreaker || null
    this.fallback = options.fallback || null
    this.strategies = options.strategies || []
  }

  /**
   * Execute function with error recovery
   */
  async execute<T>(fn: () => Promise<T>): Promise<T> {
    try {
      // Use circuit breaker if available
      if (this.circuitBreaker) {
        return await this.circuitBreaker.execute(fn)
      }

      // Use retry manager
      return await this.retryManager.retry(fn)
    } catch (error) {
      const err = error instanceof Error ? error : new Error(String(error))

      // Try recovery strategies
      for (const strategy of this.strategies.sort((a, b) => a.priority - b.priority)) {
        try {
          return await strategy.execute(fn, err)
        } catch (strategyError) {
          // Strategy failed, try next
          continue
        }
      }

      // Try fallback if available
      if (this.fallback) {
        try {
          return await this.fallback<T>()
        } catch (fallbackError) {
          // Fallback failed, throw original error
        }
      }

      // All recovery strategies failed
      throw err
    }
  }

  /**
   * Add recovery strategy
   */
  addStrategy(strategy: RecoveryStrategy): void {
    this.strategies.push(strategy)
    this.strategies.sort((a, b) => a.priority - b.priority)
  }

  /**
   * Set fallback function
   */
  setFallback<T>(fallback: () => Promise<T>): void {
    this.fallback = fallback as <T>() => Promise<T>
  }

  /**
   * Set circuit breaker
   */
  setCircuitBreaker(circuitBreaker: CircuitBreaker): void {
    this.circuitBreaker = circuitBreaker
  }
}

