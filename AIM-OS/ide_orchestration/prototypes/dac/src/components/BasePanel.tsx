// Base Panel Component - V2 Foundation Enhancement
// Shared panel functionality: header, content, footer, loading/error states, AIM-OS integration

import React, { ReactNode } from 'react'
import { 
  AlertTriangle, 
  CheckCircle, 
  X, 
  Settings, 
  Loader2,
  Shield,
  Brain
} from 'lucide-react'

// ===== TYPE DEFINITIONS =====

export interface BasePanelProps {
  // Identity
  id: string
  title: string
  icon?: React.ElementType
  description?: string
  
  // Content
  children: ReactNode
  
  // States
  loading?: boolean
  error?: string | null
  empty?: boolean
  emptyMessage?: string
  
  // AIM-OS Integration
  confidence?: number
  confidenceBand?: 'A' | 'B' | 'C' | 'green' | 'yellow' | 'red'
  contradictionCount?: number
  atomCount?: number
  
  // Actions
  onClose?: () => void
  onSettings?: () => void
  actions?: ReactNode
  
  // Customization
  className?: string
  headerClassName?: string
  headerContent?: ReactNode
  contentClassName?: string
  footerClassName?: string
  
  // Footer
  showFooter?: boolean
  footerContent?: ReactNode
  
  // Header
  showHeader?: boolean
}

// ===== CONFIDENCE HELPERS =====

const getConfidenceColor = (band?: 'A' | 'B' | 'C' | 'green' | 'yellow' | 'red'): string => {
  if (!band) return 'text-gray-400'
  
  switch (band) {
    case 'A':
    case 'green':
      return 'text-green-400'
    case 'B':
    case 'yellow':
      return 'text-yellow-400'
    case 'C':
    case 'red':
      return 'text-red-400'
    default:
      return 'text-gray-400'
  }
}

const getConfidenceBadge = (band?: 'A' | 'B' | 'C' | 'green' | 'yellow' | 'red'): string => {
  if (!band) return 'bg-gray-700'
  
  switch (band) {
    case 'A':
    case 'green':
      return 'bg-green-900/30 border-green-700'
    case 'B':
    case 'yellow':
      return 'bg-yellow-900/30 border-yellow-700'
    case 'C':
    case 'red':
      return 'bg-red-900/30 border-red-700'
    default:
      return 'bg-gray-700'
  }
}

const formatConfidence = (confidence?: number): string => {
  if (confidence === undefined || confidence === null) return 'N/A'
  return `${(confidence * 100).toFixed(0)}%`
}

// ===== BASE PANEL COMPONENT =====

export const BasePanel: React.FC<BasePanelProps> = ({
  id,
  title,
  icon: Icon,
  description,
  children,
  loading = false,
  error = null,
  empty = false,
  emptyMessage = 'No data available',
  confidence,
  confidenceBand,
  contradictionCount = 0,
  atomCount,
  onClose,
  onSettings,
  actions,
  className = '',
  headerClassName = '',
  headerContent,
  contentClassName = '',
  footerClassName = '',
  showFooter = false,
  footerContent,
  showHeader = false,
}) => {
  return (
    <div 
      id={id}
      className={`h-full flex flex-col bg-gray-900 ${className}`}
    >
      {/* Header */}
      {showHeader && (
      <div className={`px-3 py-2 border-b border-gray-700 ${headerClassName}`}>
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2" title={description || undefined}>
            {Icon && <Icon className="w-4 h-4 text-blue-400" />}
            <h2 className="text-sm font-semibold text-gray-200">{title}</h2>
            
            {/* Confidence Badge */}
            {confidenceBand && (
              <span className={`text-xs px-1.5 py-0.5 rounded border ${getConfidenceBadge(confidenceBand)} ${getConfidenceColor(confidenceBand)}`}>
                {confidenceBand === 'A' || confidenceBand === 'green' ? '🟢' : confidenceBand === 'B' || confidenceBand === 'yellow' ? '🟡' : '🔴'} {confidenceBand}
              </span>
            )}
          </div>
          
          {/* Actions */}
          <div className="flex items-center gap-2">
            {actions}
            {onSettings && (
              <button
                onClick={onSettings}
                className="p-1 rounded text-gray-400 hover:text-gray-200 hover:bg-gray-700 transition-colors"
                title="Settings"
              >
                <Settings className="w-4 h-4" />
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
        
        {/* Custom Header Content */}
        {headerContent && (
          <div className="mt-2">
            {headerContent}
          </div>
        )}
      </div>
      )}
      
      {/* Content */}
      <div className={`flex-1 overflow-auto ${contentClassName}`}>
        {/* Loading State */}
        {loading && (
          <div className="h-full flex items-center justify-center">
            <div className="flex flex-col items-center gap-3 text-gray-400">
              <Loader2 className="w-8 h-8 animate-spin" />
              <span className="text-sm">Loading...</span>
            </div>
          </div>
        )}
        
        {/* Error State */}
        {!loading && error && (
          <div className="h-full flex items-center justify-center p-4">
            <div className="flex flex-col items-center gap-3 text-red-400 max-w-md text-center">
              <AlertTriangle className="w-8 h-8" />
              <span className="text-sm font-semibold">Error</span>
              <span className="text-xs text-gray-400">{error}</span>
            </div>
          </div>
        )}
        
        {/* Empty State */}
        {!loading && !error && empty && (
          <div className="h-full flex items-center justify-center p-4">
            <div className="flex flex-col items-center gap-3 text-gray-500 max-w-md text-center">
              <div className="w-12 h-12 rounded-full bg-gray-800 flex items-center justify-center">
                {Icon ? <Icon className="w-6 h-6" /> : <Brain className="w-6 h-6" />}
              </div>
              <span className="text-sm">{emptyMessage}</span>
            </div>
          </div>
        )}
        
        {/* Content */}
        {!loading && !error && !empty && children}
      </div>
      
      {/* Footer */}
      {showFooter && (
        <div className={`p-3 border-t border-gray-700 bg-gray-800/50 ${footerClassName}`}>
          {footerContent ? (
            footerContent
          ) : (
            <div className="flex items-center justify-between text-xs text-gray-400">
              {/* Left: Status Indicators */}
              <div className="flex items-center gap-4">
                {/* Confidence */}
                {confidence !== undefined && (
                  <div className="flex items-center gap-1">
                    <Shield className={`w-3 h-3 ${getConfidenceColor(confidenceBand)}`} />
                    <span className={getConfidenceColor(confidenceBand)}>
                      {formatConfidence(confidence)}
                    </span>
                  </div>
                )}
                
                {/* Contradictions */}
                {contradictionCount > 0 && (
                  <div className="flex items-center gap-1 text-yellow-400">
                    <AlertTriangle className="w-3 h-3" />
                    <span>{contradictionCount} contradiction{contradictionCount !== 1 ? 's' : ''}</span>
                  </div>
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
              <div className="flex items-center gap-2">
                {!error && !loading && (
                  <div className="flex items-center gap-1 text-green-400">
                    <CheckCircle className="w-3 h-3" />
                    <span>Ready</span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// ===== PANEL VARIANTS =====

// Simple Panel (no footer, minimal header)
export const SimplePanel: React.FC<Omit<BasePanelProps, 'showFooter'>> = (props) => {
  return <BasePanel {...props} showFooter={false} />
}

// Status Panel (emphasizes footer with status)
export const StatusPanel: React.FC<BasePanelProps> = (props) => {
  return (
    <BasePanel
      {...props}
      showFooter={true}
      footerClassName="bg-gray-800"
    />
  )
}

// Loading Panel Wrapper
export const LoadingPanel: React.FC<{ title: string; icon?: React.ElementType }> = ({ title, icon: Icon }) => {
  return (
    <BasePanel
      id={`loading-${title.toLowerCase().replace(/\s+/g, '-')}`}
      title={title}
      icon={Icon}
      loading={true}
      showFooter={false}
    >
      <></>
    </BasePanel>
  )
}

// Error Panel Wrapper
export const ErrorPanel: React.FC<{ 
  title: string; 
  error: string; 
  icon?: React.ElementType;
  onRetry?: () => void;
}> = ({ title, error, icon: Icon, onRetry }) => {
  return (
    <BasePanel
      id={`error-${title.toLowerCase().replace(/\s+/g, '-')}`}
      title={title}
      icon={Icon}
      error={error}
      showFooter={false}
      actions={
        onRetry ? (
          <button
            onClick={onRetry}
            className="px-3 py-1 rounded text-sm bg-blue-600 text-white hover:bg-blue-700 transition-colors"
          >
            Retry
          </button>
        ) : undefined
      }
    >
      <></>
    </BasePanel>
  )
}

// Empty Panel Wrapper
export const EmptyPanel: React.FC<{ 
  title: string; 
  message?: string; 
  icon?: React.ElementType;
}> = ({ title, message = 'No data available', icon: Icon }) => {
  return (
    <BasePanel
      id={`empty-${title.toLowerCase().replace(/\s+/g, '-')}`}
      title={title}
      icon={Icon}
      empty={true}
      emptyMessage={message}
      showFooter={false}
    >
      <></>
    </BasePanel>
  )
}

