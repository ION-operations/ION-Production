// Error Tracking Service
// Comprehensive error tracking for IDE
// V2 Enhancement - Week 2 Integration

import { DebugError } from '../components/DebugConsole'

export interface ErrorContext {
  componentStack?: string
  errorBoundary?: string
  userAction?: string
  state?: any
  props?: any
  url?: string
  userAgent?: string
  timestamp: Date
}

export class ErrorTrackingService {
  private errors: DebugError[] = []
  private errorCallbacks: Array<(error: DebugError) => void> = []
  private maxErrors = 1000

  constructor() {
    this.setupGlobalErrorHandlers()
  }

  /**
   * Setup global error handlers
   */
  private setupGlobalErrorHandlers(): void {
    // Window error handler
    window.addEventListener('error', (event) => {
      this.trackError({
        id: `error-${Date.now()}-${Math.random()}`,
        message: event.message || 'Unknown error',
        stack: event.error?.stack,
        timestamp: new Date(),
        severity: 'error',
        source: 'window',
        context: {
          filename: event.filename,
          lineno: event.lineno,
          colno: event.colno,
          error: event.error
        }
      })
    })

    // Unhandled promise rejection handler
    window.addEventListener('unhandledrejection', (event) => {
      const error = event.reason instanceof Error 
        ? event.reason 
        : new Error(String(event.reason))
      
      this.trackError({
        id: `promise-${Date.now()}-${Math.random()}`,
        message: `Unhandled Promise Rejection: ${error.message}`,
        stack: error.stack,
        timestamp: new Date(),
        severity: 'error',
        source: 'promise',
        context: {
          reason: event.reason,
          promise: event.promise
        }
      })
    })

    // React Error Boundary integration (via window events)
    window.addEventListener('react-error', ((event: CustomEvent) => {
      this.trackError({
        id: `react-${Date.now()}-${Math.random()}`,
        message: event.detail.error?.message || 'React component error',
        stack: event.detail.error?.stack,
        timestamp: new Date(),
        severity: 'error',
        source: 'react',
        context: {
          componentStack: event.detail.componentStack,
          errorInfo: event.detail.errorInfo,
          errorBoundary: event.detail.errorBoundary
        }
      })
    }) as EventListener)
  }

  /**
   * Track an error
   */
  trackError(error: DebugError): void {
    // Add error context
    const enhancedError: DebugError = {
      ...error,
      context: {
        ...error.context,
        url: window.location.href,
        userAgent: navigator.userAgent,
        timestamp: new Date()
      }
    }

    // Add to errors array
    this.errors = [...this.errors.slice(-this.maxErrors + 1), enhancedError]

    // Notify callbacks
    this.errorCallbacks.forEach(callback => {
      try {
        callback(enhancedError)
      } catch (err) {
        console.error('[ErrorTracking] Callback error:', err)
      }
    })
  }

  /**
   * Subscribe to errors
   */
  subscribe(callback: (error: DebugError) => void): () => void {
    this.errorCallbacks.push(callback)
    
    // Return unsubscribe function
    return () => {
      const index = this.errorCallbacks.indexOf(callback)
      if (index > -1) {
        this.errorCallbacks.splice(index, 1)
      }
    }
  }

  /**
   * Get all errors
   */
  getErrors(): DebugError[] {
    return [...this.errors]
  }

  /**
   * Get errors by severity
   */
  getErrorsBySeverity(severity: DebugError['severity']): DebugError[] {
    return this.errors.filter(e => e.severity === severity)
  }

  /**
   * Get errors by source
   */
  getErrorsBySource(source: string): DebugError[] {
    return this.errors.filter(e => e.source === source)
  }

  /**
   * Clear errors
   */
  clearErrors(): void {
    this.errors = []
  }

  /**
   * Get error statistics
   */
  getErrorStats(): {
    total: number
    bySeverity: Record<string, number>
    bySource: Record<string, number>
    recent: number
  } {
    const bySeverity: Record<string, number> = {}
    const bySource: Record<string, number> = {}
    const oneHourAgo = Date.now() - 60 * 60 * 1000

    this.errors.forEach(error => {
      bySeverity[error.severity] = (bySeverity[error.severity] || 0) + 1
      bySource[error.source] = (bySource[error.source] || 0) + 1
    })

    const recent = this.errors.filter(
      e => e.timestamp.getTime() > oneHourAgo
    ).length

    return {
      total: this.errors.length,
      bySeverity,
      bySource,
      recent
    }
  }

  /**
   * Group similar errors
   */
  groupErrors(): Map<string, DebugError[]> {
    const groups = new Map<string, DebugError[]>()

    this.errors.forEach(error => {
      // Create group key from message and source
      const key = `${error.source}:${error.message.substring(0, 50)}`
      
      if (!groups.has(key)) {
        groups.set(key, [])
      }
      groups.get(key)!.push(error)
    })

    return groups
  }
}

// Singleton instance
let errorTrackingServiceInstance: ErrorTrackingService | null = null

export function getErrorTrackingService(): ErrorTrackingService {
  if (!errorTrackingServiceInstance) {
    errorTrackingServiceInstance = new ErrorTrackingService()
  }
  return errorTrackingServiceInstance
}

