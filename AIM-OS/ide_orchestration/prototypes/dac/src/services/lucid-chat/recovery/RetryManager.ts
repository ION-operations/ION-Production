/**
 * Retry Manager
 * 
 * Handles retry logic with exponential backoff
 */

export interface RetryOptions {
  maxRetries?: number
  backoff?: 'exponential' | 'linear' | 'fixed'
  initialDelay?: number
  maxDelay?: number
  retryable?: (error: Error) => boolean
}

export class RetryManager {
  /**
   * Retry function with backoff
   */
  static async retry<T>(
    fn: () => Promise<T>,
    options: RetryOptions = {}
  ): Promise<T> {
    const {
      maxRetries = 3,
      backoff = 'exponential',
      initialDelay = 1000,
      maxDelay = 30000,
      retryable = (error: Error) => {
        // Default: retry on network errors, timeouts, 5xx errors
        const message = error.message.toLowerCase()
        return (
          message.includes('network') ||
          message.includes('timeout') ||
          message.includes('econnrefused') ||
          message.includes('500') ||
          message.includes('502') ||
          message.includes('503') ||
          message.includes('504')
        )
      },
    } = options

    let lastError: Error
    let attempt = 0

    while (attempt <= maxRetries) {
      try {
        return await fn()
      } catch (error) {
        lastError = error instanceof Error ? error : new Error(String(error))

        // Check if error is retryable
        if (!retryable(lastError)) {
          throw lastError
        }

        // Check if we've exhausted retries
        if (attempt >= maxRetries) {
          throw lastError
        }

        // Calculate delay
        const delay = this.calculateDelay(attempt, backoff, initialDelay, maxDelay)

        // Wait before retry
        await this.sleep(delay)

        attempt++
      }
    }

    throw lastError!
  }

  /**
   * Calculate delay based on backoff strategy
   */
  private static calculateDelay(
    attempt: number,
    strategy: 'exponential' | 'linear' | 'fixed',
    initialDelay: number,
    maxDelay: number
  ): number {
    let delay: number

    switch (strategy) {
      case 'exponential':
        delay = initialDelay * Math.pow(2, attempt)
        break
      case 'linear':
        delay = initialDelay * (attempt + 1)
        break
      case 'fixed':
        delay = initialDelay
        break
      default:
        delay = initialDelay
    }

    return Math.min(delay, maxDelay)
  }

  /**
   * Sleep for specified milliseconds
   */
  private static sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms))
  }

  /**
   * Check if error is retryable
   */
  static isRetryableError(error: Error): boolean {
    const message = error.message.toLowerCase()
    return (
      message.includes('network') ||
      message.includes('timeout') ||
      message.includes('econnrefused') ||
      message.includes('500') ||
      message.includes('502') ||
      message.includes('503') ||
      message.includes('504')
    )
  }
}

