// Error Boundary Component for Panels
import React, { Component, ReactNode, ErrorInfo } from 'react'
import { AlertCircle } from 'lucide-react'

interface ErrorBoundaryProps {
  children: ReactNode
  panelId?: string
  fallback?: ReactNode
}

interface ErrorBoundaryState {
  hasError: boolean
  error: Error | null
  errorInfo: ErrorInfo | null
}

export class PanelErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    }
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return {
      hasError: true,
      error,
    }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error(`[PanelErrorBoundary] Error in panel ${this.props.panelId}:`, error, errorInfo)
    this.setState({
      error,
      errorInfo,
    })
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      return (
        <div
          style={{
            padding: '20px',
            backgroundColor: '#1F2937',
            color: '#F9FAFB',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            height: '100%',
            gap: '12px',
          }}
        >
          <AlertCircle size={32} style={{ color: '#EF4444' }} />
          <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#EF4444' }}>Panel Error</div>
          <div style={{ fontSize: '12px', color: '#9CA3AF', textAlign: 'center', maxWidth: '400px' }}>
            {this.state.error?.message || 'An unexpected error occurred'}
          </div>
          {process.env.NODE_ENV === 'development' && this.state.error && (
            <details style={{ fontSize: '11px', color: '#6B7280', maxWidth: '400px', overflow: 'auto' }}>
              <summary style={{ cursor: 'pointer', marginBottom: '8px' }}>Error Details</summary>
              <pre style={{ backgroundColor: '#111827', padding: '8px', borderRadius: '4px', overflow: 'auto' }}>
                {this.state.error.stack}
              </pre>
            </details>
          )}
          <button
            onClick={() => {
              this.setState({ hasError: false, error: null, errorInfo: null })
              window.location.reload()
            }}
            style={{
              padding: '8px 16px',
              backgroundColor: '#3B82F6',
              border: 'none',
              borderRadius: '4px',
              color: '#F9FAFB',
              cursor: 'pointer',
              fontSize: '12px',
            }}
          >
            Reload Panel
          </button>
        </div>
      )
    }

    return this.props.children
  }
}

