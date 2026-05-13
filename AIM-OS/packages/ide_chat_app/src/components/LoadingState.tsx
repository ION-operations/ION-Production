/**
 * Loading State Component
 * 
 * Phase 1.2: Error Handling & Loading States
 * 
 * Provides consistent loading states for panels
 */

import React from 'react'
import { Loader2 } from 'lucide-react'

interface LoadingStateProps {
  message?: string
  fullHeight?: boolean
  size?: 'sm' | 'md' | 'lg'
}

export const LoadingState: React.FC<LoadingStateProps> = ({ 
  message = 'Loading...', 
  fullHeight = true,
  size = 'md'
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
  }

  return (
    <div className={`flex flex-col items-center justify-center gap-2 text-gray-400 ${
      fullHeight ? 'h-full' : 'py-8'
    }`}>
      <Loader2 className={`${sizeClasses[size]} animate-spin`} />
      <p className="text-sm">{message}</p>
    </div>
  )
}

interface LoadingOverlayProps {
  isLoading: boolean
  message?: string
  children: React.ReactNode
}

export const LoadingOverlay: React.FC<LoadingOverlayProps> = ({ 
  isLoading, 
  message = 'Loading...',
  children 
}) => {
  if (!isLoading) {
    return <>{children}</>
  }

  return (
    <div className="relative h-full">
      <div className="absolute inset-0 bg-gray-800 bg-opacity-75 flex items-center justify-center z-10">
        <LoadingState message={message} fullHeight={false} />
      </div>
      <div className="h-full opacity-50 pointer-events-none">
        {children}
      </div>
    </div>
  )
}

