// Base Panel Component - Common UI and Logic for All Panels
import React, { ReactNode, memo, useCallback, KeyboardEvent } from 'react'
import { Panel } from '@/types'
import { PanelErrorBoundary } from './PanelErrorBoundary'
import { PanelLoading } from './PanelLoading'

interface BasePanelProps {
  panel: Panel
  children: ReactNode
  headerActions?: ReactNode
  className?: string
  isLoading?: boolean
  loadingMessage?: string
  error?: Error | null
}

export const BasePanel: React.FC<BasePanelProps> = memo(({
  panel,
  children,
  headerActions,
  className = '',
  isLoading = false,
  loadingMessage,
  error,
}) => {
  const handleClose = useCallback(() => {
    const event = new CustomEvent('togglePanel', { detail: { panelId: panel.id } })
    window.dispatchEvent(event)
  }, [panel.id])

  const handleKeyDown = useCallback((e: KeyboardEvent<HTMLButtonElement>) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      handleClose()
    }
  }, [handleClose])

  return (
    <PanelErrorBoundary panelId={panel.id}>
      <div
        className={`base-panel ${className}`}
        style={{
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          backgroundColor: '#1F2937',
          borderRight: '1px solid #374151',
          transition: 'background-color 0.2s ease',
        }}
        role="region"
        aria-label={`${panel.title} panel`}
      >
        {/* Panel Header */}
        <div
          className="panel-header"
          style={{
            height: '32px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '0 12px',
            borderBottom: '1px solid #374151',
            backgroundColor: '#111827',
          }}
          role="banner"
        >
          <span style={{ color: '#F9FAFB', fontSize: '13px', fontWeight: 500 }}>{panel.title}</span>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            {headerActions}
            <button
              onClick={handleClose}
              onKeyDown={handleKeyDown}
              style={{
                background: 'none',
                border: 'none',
                color: '#9CA3AF',
                cursor: 'pointer',
                padding: '4px',
                display: 'flex',
                alignItems: 'center',
                borderRadius: '4px',
                transition: 'background-color 0.2s ease, color 0.2s ease',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#374151'
                e.currentTarget.style.color = '#F9FAFB'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'transparent'
                e.currentTarget.style.color = '#9CA3AF'
              }}
              onFocus={(e) => {
                e.currentTarget.style.outline = '2px solid #3B82F6'
                e.currentTarget.style.outlineOffset = '2px'
              }}
              onBlur={(e) => {
                e.currentTarget.style.outline = 'none'
              }}
              title="Close panel"
              aria-label="Close panel"
              tabIndex={0}
            >
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                <path d="M1 1L13 13M13 1L1 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
              </svg>
            </button>
          </div>
        </div>

        {/* Panel Content */}
        <div
          className="panel-content"
          style={{
            flex: 1,
            overflow: 'auto',
            padding: '12px',
          }}
          role="main"
          aria-busy={isLoading}
          aria-live="polite"
        >
          {isLoading ? (
            <PanelLoading message={loadingMessage} />
          ) : error ? (
            <div
              role="alert"
              style={{
                padding: '20px',
                backgroundColor: '#1F2937',
                color: '#EF4444',
                fontSize: '12px',
                textAlign: 'center',
                borderRadius: '4px',
                border: '1px solid #EF4444',
              }}
            >
              <strong>Error:</strong> {error.message}
            </div>
          ) : (
            children
          )}
        </div>
      </div>
    </PanelErrorBoundary>
  )
}, (prevProps, nextProps) => {
  // Custom comparison for memoization
  return (
    prevProps.panel.id === nextProps.panel.id &&
    prevProps.isLoading === nextProps.isLoading &&
    prevProps.error?.message === nextProps.error?.message &&
    prevProps.className === nextProps.className
  )
})

BasePanel.displayName = 'BasePanel'

