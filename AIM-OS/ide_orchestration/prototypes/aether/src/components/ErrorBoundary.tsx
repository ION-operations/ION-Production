import React, { Component, ReactNode, ErrorInfo } from 'react'

interface ErrorBoundaryProps {
  children: ReactNode
  fallback?: ReactNode
  onError?: (error: Error, errorInfo: ErrorInfo) => void
  panelId?: string
}

interface ErrorBoundaryState {
  hasError: boolean
  error: Error | null
}

/**
 * Error Boundary for Panel Components
 * 
 * Catches errors in panel rendering and displays a fallback UI
 * Prevents the entire IDE from crashing when a single panel fails
 */
export class PanelErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = {
      hasError: false,
      error: null
    }
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return {
      hasError: true,
      error
    }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log error for debugging
    console.error(`Panel Error (${this.props.panelId || 'unknown'}):`, error, errorInfo)
    
    // Call optional error handler
    if (this.props.onError) {
      this.props.onError(error, errorInfo)
    }
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null
    })
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      return (
        <div className="h-full flex flex-col items-center justify-center p-4 bg-gray-800 text-gray-300">
          <div className="text-center max-w-md">
            <div className="text-red-400 text-xl mb-2">⚠️ Panel Error</div>
            <div className="text-sm mb-4">
              {this.props.panelId && (
                <div className="mb-2">
                  Panel: <span className="font-mono text-blue-400">{this.props.panelId}</span>
                </div>
              )}
              <div className="text-gray-400 mb-4">
                {this.state.error?.message || 'An unexpected error occurred'}
              </div>
            </div>
            <button
              onClick={this.handleReset}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
            >
              Try Again
            </button>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

/**
 * Hook for creating error boundary wrapper
 */
export function useErrorBoundary() {
  const [error, setError] = React.useState<Error | null>(null)

  const resetError = React.useCallback(() => {
    setError(null)
  }, [])

  const captureError = React.useCallback((error: Error) => {
    setError(error)
  }, [])

  return {
    error,
    resetError,
    captureError
  }
}

