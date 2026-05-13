// Shared UI Components - V2 Foundation Enhancement
// Reusable components for panels: LoadingSpinner, ErrorDisplay, ConfidenceBadge

import React, { ReactNode } from 'react'
import { Loader2, AlertTriangle, CheckCircle, Shield, Brain, X, Clock, RefreshCw, AlertCircle } from 'lucide-react'

// ===== LOADING SPINNER =====

export interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  message?: string
  fullScreen?: boolean
  className?: string
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  message,
  fullScreen = false,
  className = '',
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  }
  
  const containerClasses = fullScreen
    ? 'h-full flex items-center justify-center'
    : 'flex items-center justify-center'
  
  return (
    <div className={`${containerClasses} ${className}`}>
      <div className="flex flex-col items-center gap-3 text-gray-400">
        <Loader2 className={`${sizeClasses[size]} animate-spin`} />
        {message && <span className="text-sm">{message}</span>}
      </div>
    </div>
  )
}

// ===== ERROR DISPLAY =====

export type ErrorType = 
  | 'network'      // Connection issues, server unavailable
  | 'timeout'      // Request timeout, operation timeout
  | 'validation'   // Input validation, API validation
  | 'api'          // 4xx (client), 5xx (server) errors
  | 'system'       // Unexpected errors, fallback errors

export interface ErrorDisplayProps {
  error: string | Error
  title?: string
  errorType?: ErrorType
  onRetry?: () => void
  onDismiss?: () => void
  retryCount?: number
  maxRetries?: number
  className?: string
}

export const ErrorDisplay: React.FC<ErrorDisplayProps> = ({
  error,
  title,
  errorType = 'system',
  onRetry,
  onDismiss,
  retryCount,
  maxRetries = 3,
  className = '',
}) => {
  // Determine error message and title
  const errorMessage = error instanceof Error ? error.message : error
  const errorTitle = title || getErrorTitle(errorType)
  
  // Error type configuration
  const errorConfig = {
    network: {
      icon: AlertTriangle,
      color: 'text-orange-400',
      bgColor: 'bg-orange-900/20',
      borderColor: 'border-orange-700/50',
      defaultTitle: 'Network Error',
      description: 'Unable to connect to server'
    },
    timeout: {
      icon: Clock,
      color: 'text-yellow-400',
      bgColor: 'bg-yellow-900/20',
      borderColor: 'border-yellow-700/50',
      defaultTitle: 'Timeout Error',
      description: 'Request took too long to complete'
    },
    validation: {
      icon: AlertCircle,
      color: 'text-blue-400',
      bgColor: 'bg-blue-900/20',
      borderColor: 'border-blue-700/50',
      defaultTitle: 'Validation Error',
      description: 'Invalid input or data format'
    },
    api: {
      icon: AlertTriangle,
      color: 'text-red-400',
      bgColor: 'bg-red-900/20',
      borderColor: 'border-red-700/50',
      defaultTitle: 'API Error',
      description: 'Server returned an error'
    },
    system: {
      icon: AlertTriangle,
      color: 'text-red-400',
      bgColor: 'bg-red-900/20',
      borderColor: 'border-red-700/50',
      defaultTitle: 'System Error',
      description: 'An unexpected error occurred'
    }
  }
  
  const config = errorConfig[errorType]
  const Icon = config.icon
  
  // Check if retries exhausted
  const retriesExhausted = retryCount !== undefined && retryCount >= maxRetries
  
  return (
    <div className={`flex flex-col gap-3 ${config.bgColor} ${config.borderColor} border rounded-lg p-4 max-w-md ${className}`}>
      <div className="flex items-start gap-3">
        <Icon className={`w-6 h-6 ${config.color} flex-shrink-0 mt-0.5`} />
        <div className="flex-1">
          <h3 className={`text-sm font-semibold ${config.color} mb-1`}>
            {errorTitle}
          </h3>
          <p className="text-xs text-gray-400 mb-2">
            {config.description}
          </p>
          <div className="bg-gray-900/50 rounded p-2 mb-2">
            <p className="text-xs text-gray-300 font-mono break-all">
              {errorMessage}
            </p>
          </div>
          {retryCount !== undefined && (
            <p className="text-xs text-gray-500 mb-2">
              Retry attempts: {retryCount}/{maxRetries}
            </p>
          )}
        </div>
      </div>
      <div className="flex gap-2">
        {onRetry && !retriesExhausted && (
          <button
            onClick={onRetry}
            className="px-3 py-1.5 rounded text-sm bg-blue-600 text-white hover:bg-blue-700 transition-colors flex items-center gap-1"
          >
            <RefreshCw className="w-3 h-3" />
            Retry
          </button>
        )}
        {retriesExhausted && (
          <span className="text-xs text-gray-500 px-3 py-1.5">
            Max retries reached
          </span>
        )}
        {onDismiss && (
          <button
            onClick={onDismiss}
            className="px-3 py-1.5 rounded text-sm bg-gray-700 text-gray-300 hover:bg-gray-600 transition-colors"
          >
            Dismiss
          </button>
        )}
      </div>
    </div>
  )
}

function getErrorTitle(errorType: ErrorType): string {
  const titles = {
    network: 'Network Error',
    timeout: 'Timeout Error',
    validation: 'Validation Error',
    api: 'API Error',
    system: 'System Error'
  }
  return titles[errorType]
}

// ===== CONFIDENCE BADGE =====

export interface ConfidenceBadgeProps {
  confidence?: number
  band?: 'A' | 'B' | 'C' | 'green' | 'yellow' | 'red'
  showPercentage?: boolean
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

export const ConfidenceBadge: React.FC<ConfidenceBadgeProps> = ({
  confidence,
  band,
  showPercentage = true,
  size = 'md',
  className = '',
}) => {
  // Determine band from confidence if not provided
  const determinedBand: 'A' | 'B' | 'C' | 'green' | 'yellow' | 'red' = band || 
    (confidence !== undefined && confidence !== null
      ? confidence >= 0.90 ? 'A'
      : confidence >= 0.70 ? 'B'
      : 'C'
      : 'gray')
  
  const sizeClasses = {
    sm: 'text-xs px-1.5 py-0.5',
    md: 'text-xs px-2 py-1',
    lg: 'text-sm px-3 py-1.5',
  }
  
  const colorClasses = {
    A: 'bg-green-900/30 border-green-700 text-green-400',
    green: 'bg-green-900/30 border-green-700 text-green-400',
    B: 'bg-yellow-900/30 border-yellow-700 text-yellow-400',
    yellow: 'bg-yellow-900/30 border-yellow-700 text-yellow-400',
    C: 'bg-red-900/30 border-red-700 text-red-400',
    red: 'bg-red-900/30 border-red-700 text-red-400',
    gray: 'bg-gray-700 border-gray-600 text-gray-400',
  }
  
  const emoji = {
    A: '🟢',
    green: '🟢',
    B: '🟡',
    yellow: '🟡',
    C: '🔴',
    red: '🔴',
    gray: '⚪',
  }
  
  return (
    <span className={`inline-flex items-center gap-1 rounded border ${sizeClasses[size]} ${colorClasses[determinedBand]} ${className}`}>
      <span>{emoji[determinedBand]}</span>
      <span>{determinedBand === 'A' || determinedBand === 'green' ? 'A' : determinedBand === 'B' || determinedBand === 'yellow' ? 'B' : determinedBand === 'C' || determinedBand === 'red' ? 'C' : '?'}</span>
      {showPercentage && confidence !== undefined && confidence !== null && (
        <span className="ml-1">{(confidence * 100).toFixed(0)}%</span>
      )}
    </span>
  )
}

// ===== CONTRADICTION ALERT =====

export interface ContradictionAlertProps {
  count: number
  onClick?: () => void
  className?: string
}

export const ContradictionAlert: React.FC<ContradictionAlertProps> = ({
  count,
  onClick,
  className = '',
}) => {
  if (count === 0) return null
  
  return (
    <div
      onClick={onClick}
      className={`flex items-center gap-1 text-yellow-400 cursor-pointer hover:text-yellow-300 transition-colors ${className}`}
      title={`${count} contradiction${count !== 1 ? 's' : ''} detected`}
    >
      <AlertTriangle className="w-4 h-4" />
      <span className="text-xs font-semibold">{count}</span>
    </div>
  )
}

// ===== STATUS INDICATOR =====

export interface StatusIndicatorProps {
  status: 'ready' | 'loading' | 'error' | 'warning'
  message?: string
  className?: string
}

export const StatusIndicator: React.FC<StatusIndicatorProps> = ({
  status,
  message,
  className = '',
}) => {
  const statusConfig = {
    ready: {
      icon: CheckCircle,
      color: 'text-green-400',
      defaultMessage: 'Ready',
    },
    loading: {
      icon: Loader2,
      color: 'text-blue-400',
      defaultMessage: 'Loading...',
    },
    error: {
      icon: AlertTriangle,
      color: 'text-red-400',
      defaultMessage: 'Error',
    },
    warning: {
      icon: AlertTriangle,
      color: 'text-yellow-400',
      defaultMessage: 'Warning',
    },
  }
  
  const config = statusConfig[status]
  const Icon = config.icon
  
  return (
    <div className={`flex items-center gap-1 ${config.color} ${className}`}>
      <Icon className={`w-3 h-3 ${status === 'loading' ? 'animate-spin' : ''}`} />
      <span className="text-xs">{message || config.defaultMessage}</span>
    </div>
  )
}

// ===== EMPTY STATE =====

export interface EmptyStateProps {
  icon?: React.ElementType
  title?: string
  message: string
  action?: {
    label: string
    onClick: () => void
  }
  className?: string
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon: Icon,
  title,
  message,
  action,
  className = '',
}) => {
  return (
    <div className={`flex flex-col items-center gap-3 text-gray-500 max-w-md text-center p-4 ${className}`}>
      {Icon && (
        <div className="w-12 h-12 rounded-full bg-gray-800 flex items-center justify-center">
          <Icon className="w-6 h-6" />
        </div>
      )}
      {title && <span className="text-sm font-semibold">{title}</span>}
      <span className="text-sm">{message}</span>
      {action && (
        <button
          onClick={action.onClick}
          className="mt-2 px-4 py-2 rounded text-sm bg-blue-600 text-white hover:bg-blue-700 transition-colors"
        >
          {action.label}
        </button>
      )}
    </div>
  )
}

// ===== PANEL HEADER =====

export interface PanelHeaderProps {
  title: string
  icon?: React.ElementType
  description?: string
  actions?: ReactNode
  onClose?: () => void
  onSettings?: () => void
  className?: string
}

export const PanelHeader: React.FC<PanelHeaderProps> = ({
  title,
  icon: Icon,
  description,
  actions,
  onClose,
  onSettings,
  className = '',
}) => {
  return (
    <div className={`p-4 border-b border-gray-700 ${className}`}>
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          {Icon && <Icon className="w-5 h-5 text-blue-400" />}
          <h2 className="text-lg font-semibold text-gray-200">{title}</h2>
        </div>
        
        <div className="flex items-center gap-2">
          {actions}
          {onSettings && (
            <button
              onClick={onSettings}
              className="p-1 rounded text-gray-400 hover:text-gray-200 hover:bg-gray-700 transition-colors"
              title="Settings"
            >
              <Shield className="w-4 h-4" />
            </button>
          )}
          {onClose && (
            <button
              onClick={onClose}
              className="p-1 rounded text-gray-400 hover:text-gray-200 hover:bg-gray-700 transition-colors"
              title="Close"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
      
      {description && (
        <div className="text-sm text-gray-400">{description}</div>
      )}
    </div>
  )
}

// ===== PANEL FOOTER =====

export interface PanelFooterProps {
  confidence?: number
  confidenceBand?: 'A' | 'B' | 'C' | 'green' | 'yellow' | 'red'
  contradictionCount?: number
  atomCount?: number
  status?: 'ready' | 'loading' | 'error' | 'warning'
  customContent?: ReactNode
  className?: string
}

export const PanelFooter: React.FC<PanelFooterProps> = ({
  confidence,
  confidenceBand,
  contradictionCount = 0,
  atomCount,
  status = 'ready',
  customContent,
  className = '',
}) => {
  if (customContent) {
    return (
      <div className={`p-3 border-t border-gray-700 bg-gray-800/50 ${className}`}>
        {customContent}
      </div>
    )
  }
  
  return (
    <div className={`p-3 border-t border-gray-700 bg-gray-800/50 ${className}`}>
      <div className="flex items-center justify-between text-xs text-gray-400">
        {/* Left: Status Indicators */}
        <div className="flex items-center gap-4">
          {/* Confidence */}
          {confidence !== undefined && (
            <ConfidenceBadge confidence={confidence} band={confidenceBand} size="sm" />
          )}
          
          {/* Contradictions */}
          {contradictionCount > 0 && (
            <ContradictionAlert count={contradictionCount} />
          )}
          
          {/* Atom Count */}
          {atomCount !== undefined && (
            <div className="flex items-center gap-1">
              <Brain className="w-3 h-3" />
              <span>{atomCount} atom{atomCount !== 1 ? 's' : ''}</span>
            </div>
          )}
        </div>
        
        {/* Right: Status */}
        <StatusIndicator status={status} />
      </div>
    </div>
  )
}

