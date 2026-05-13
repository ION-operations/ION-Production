import React from 'react'

interface LoadingPanelProps {
  panelId?: string
  message?: string
}

/**
 * Loading Panel Component
 * 
 * Displays a loading state while panels are initializing or loading data
 */
export const LoadingPanel: React.FC<LoadingPanelProps> = ({ 
  panelId, 
  message = 'Loading...' 
}) => {
  return (
    <div className="h-full flex flex-col items-center justify-center p-4 bg-gray-800 text-gray-300">
      <div className="text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400 mx-auto mb-4"></div>
        <div className="text-sm text-gray-400">
          {panelId && (
            <div className="mb-2">
              Loading: <span className="font-mono text-blue-400">{panelId}</span>
            </div>
          )}
          <div>{message}</div>
        </div>
      </div>
    </div>
  )
}

/**
 * Suspense wrapper for panels
 * Shows loading state while panel components are loading
 */
export const PanelSuspense: React.FC<{
  children: React.ReactNode
  fallback?: React.ReactNode
  panelId?: string
}> = ({ children, fallback, panelId }) => {
  return (
    <React.Suspense fallback={fallback || <LoadingPanel panelId={panelId} />}>
      {children}
    </React.Suspense>
  )
}

