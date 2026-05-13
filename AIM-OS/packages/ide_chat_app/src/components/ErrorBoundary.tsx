// React Error Boundary Component
// Catches React component errors and reports to ErrorTrackingService
// V2 Enhancement - Week 2 Integration

import React, { Component, ErrorInfo, ReactNode } from 'react'
import { AlertTriangle, RefreshCw } from 'lucide-react'
import { getErrorTrackingService } from '../services/errorTrackingService'

interface Props {
  children: ReactNode
  fallback?: ReactNode
  onError?: (error: Error, errorInfo: ErrorInfo) => void
}

interface State {
  hasError: boolean
  error: Error | null
  errorInfo: ErrorInfo | null
}

export class ErrorBoundary extends Component<Props, State> {
  private errorTrackingService = getErrorTrackingService()

  constructor(props: Props) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    }
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: null
    }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // Update state with error info
    this.setState({
      error,
      errorInfo
    })

    // Report to error tracking service
    const customEvent = new CustomEvent('react-error', {
      detail: {
        error,
        errorInfo,
        componentStack: errorInfo.componentStack,
        errorBoundary: this.constructor.name
      }
    })
    window.dispatchEvent(customEvent)

    // Call optional error handler
    if (this.props.onError) {
      this.props.onError(error, errorInfo)
    }
  }

  handleReset = (): void => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null
    })
  }

  render(): ReactNode {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      return (
        <div className="flex flex-col items-center justify-center h-full p-8 bg-gray-900 text-gray-100">
          <AlertTriangle className="w-16 h-16 text-red-400 mb-4" />
          <h2 className="text-xl font-semibold mb-2">Something went wrong</h2>
          <p className="text-gray-400 mb-4 text-center max-w-md">
            {this.state.error?.message || 'An unexpected error occurred'}
          </p>
          
          {this.state.errorInfo && (
            <details className="w-full max-w-2xl mb-4">
              <summary className="cursor-pointer text-sm text-gray-400 hover:text-gray-300 mb-2">
                Error Details
              </summary>
              <pre className="text-xs text-gray-500 bg-gray-800 p-4 rounded overflow-auto max-h-64">
                {this.state.errorInfo.componentStack}
              </pre>
            </details>
          )}

          <button
            onClick={this.handleReset}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded flex items-center gap-2 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            Try Again
          </button>
        </div>
      )
    }

    return this.props.children
  }
}
