// Error Boundary Component - V2 Foundation Enhancement
// Isolated error handling for panels to prevent IDE crashes

import React, { Component, ErrorInfo, ReactNode } from 'react'
import { AlertTriangle, RefreshCw, X } from 'lucide-react'
import { errorTracker } from '../utils/errorTracker'

interface ErrorBoundaryProps {
  children: ReactNode
  fallback?: ReactNode
  onError?: (error: Error, errorInfo: ErrorInfo) => void
  panelName?: string
}

interface ErrorBoundaryState {
  hasError: boolean
  error: Error | null
  errorInfo: ErrorInfo | null
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    }
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    this.setState({
      error,
      errorInfo,
    })
    
    // Track error in error tracker
    const panelId = this.props.panelName?.toLowerCase().replace(/\s+/g, '-') || 'unknown-panel'
    errorTracker.trackError(
      panelId,
      this.props.panelName || 'Unknown Panel',
      error,
      errorInfo,
      {
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        url: window.location.href
      }
    )
    
    // Call optional error handler
    this.props.onError?.(error, errorInfo)
    
    // Log error in development
    if (process.env.NODE_ENV === 'development') {
      console.error('ErrorBoundary caught an error:', error, errorInfo)
    }
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    })
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      return (
        <div className="h-full flex items-center justify-center bg-gray-900 p-4">
          <div className="bg-gray-800 border border-red-500 rounded-lg p-6 max-w-md w-full">
            <div className="flex items-start gap-3 mb-4">
              <AlertTriangle className="w-6 h-6 text-red-400 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-red-400 mb-1">
                  {this.props.panelName ? `${this.props.panelName} Error` : 'Panel Error'}
                </h3>
                <p className="text-sm text-gray-400 mb-2">
                  This panel encountered an error and couldn't render.
                </p>
                {this.state.error && (
                  <div className="bg-gray-900 rounded p-2 mb-3">
                    <p className="text-xs text-red-300 font-mono break-all">
                      {this.state.error.message}
                    </p>
                  </div>
                )}
                {process.env.NODE_ENV === 'development' && this.state.errorInfo && (
                  <details className="mb-3">
                    <summary className="text-xs text-gray-500 cursor-pointer hover:text-gray-400">
                      Stack Trace
                    </summary>
                    <pre className="text-xs text-gray-600 mt-2 overflow-auto max-h-32">
                      {this.state.errorInfo.componentStack}
                    </pre>
                  </details>
                )}
              </div>
              <button
                onClick={this.handleReset}
                className="p-1 hover:bg-gray-700 rounded text-gray-400 hover:text-gray-200"
                title="Close error"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="flex gap-2">
              <button
                onClick={this.handleReset}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-white text-sm font-medium flex items-center gap-2"
              >
                <RefreshCw className="w-4 h-4" />
                Retry
              </button>
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

// HOC for wrapping panels with error boundary
export function withErrorBoundary<P extends object>(
  Component: React.ComponentType<P>,
  panelName?: string
) {
  const WrappedComponent = (props: P) => (
    <ErrorBoundary panelName={panelName}>
      <Component {...props} />
    </ErrorBoundary>
  )
  
  WrappedComponent.displayName = `withErrorBoundary(${Component.displayName || Component.name || 'Component'})`
  
  return WrappedComponent
}

