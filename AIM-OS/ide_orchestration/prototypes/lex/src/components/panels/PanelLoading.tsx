// Loading State Component for Panels - Enhanced with Accessibility
import React, { memo } from 'react'
import { Loader2 } from 'lucide-react'

interface PanelLoadingProps {
  message?: string
  size?: 'small' | 'medium' | 'large'
}

export const PanelLoading: React.FC<PanelLoadingProps> = memo(({ message = 'Loading...', size = 'medium' }) => {
  const iconSize = size === 'small' ? 16 : size === 'medium' ? 24 : 32

  return (
    <div
      role="status"
      aria-live="polite"
      aria-label={message}
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
      <Loader2
        size={iconSize}
        style={{
          color: '#3B82F6',
          animation: 'spin 1s linear infinite',
        }}
        aria-hidden="true"
      />
      <div style={{ fontSize: '12px', color: '#9CA3AF' }}>{message}</div>
      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  )
})

PanelLoading.displayName = 'PanelLoading'

