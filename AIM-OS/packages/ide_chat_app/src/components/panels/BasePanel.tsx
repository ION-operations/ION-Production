/**
 * Base Panel Component - Component Composition Pattern
 * 
 * Phase 4.1: Component Composition Foundation
 * 
 * Features:
 * - Consistent panel structure (header, content, footer)
 * - AIM-OS integration (confidence, VIF, CMC, contradictions)
 * - PDAS integration (pre-execution auditing, observability)
 * - Loading/error/empty states
 * - Accessibility support
 * - Panel variants (Simple, Status, Loading, Error, Empty)
 */

import React, { ReactNode, useEffect, useState } from 'react'
import { 
  AlertTriangle, 
  CheckCircle, 
  X, 
  Settings, 
  Loader2,
  Shield,
  Brain,
  Eye,
  Activity
} from 'lucide-react'
import { useAIMOS } from '../../hooks/useAIMOS'
import { ErrorBoundary } from '../ErrorBoundary'
import { LoadingState } from '../LoadingState'

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
  error?: string | Error | null
  empty?: boolean
  emptyMessage?: string
  
  // AIM-OS Integration
  confidence?: number
  confidenceBand?: 'A' | 'B' | 'C' | 'green' | 'yellow' | 'red'
  contradictionCount?: number
  atomCount?: number
  
  // PDAS Integration
  enablePDAS?: boolean
  expectedBehavior?: string
  actualBehavior?: string
  auditTrail?: Array<{ timestamp: string; action: string; result: string }>
  
  // Actions
  onClose?: () => void
  onSettings?: () => void
  actions?: ReactNode
  
  // Customization
  className?: string
  headerClassName?: string
  contentClassName?: string
  footerClassName?: string
  
  // Footer
  showFooter?: boolean
  footerContent?: ReactNode
  
  // Observability
  showObservability?: boolean
  metrics?: {
    renderTime?: number
    dataLoadTime?: number
    errorRate?: number
  }
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

// ===== PDAS AUDIT TRAIL COMPONENT =====

interface AuditTrailProps {
  auditTrail?: Array<{ timestamp: string; action: string; result: string }>
}

const AuditTrail: React.FC<AuditTrailProps> = ({ auditTrail }) => {
  if (!auditTrail || auditTrail.length === 0) return null
  
  return (
    <div className="mt-2 p-2 bg-gray-800/50 rounded text-xs">
      <div className="text-gray-500 mb-1 flex items-center gap-1">
        <Activity className="w-3 h-3" />
        Audit Trail:
      </div>
      <div className="space-y-1 max-h-32 overflow-y-auto">
        {auditTrail.map((entry, idx) => (
          <div key={idx} className="text-gray-400 font-mono">
            <span className="text-gray-600">{entry.timestamp}</span>
            {' '}
            <span className="text-blue-400">{entry.action}</span>
            {' → '}
            <span className={entry.result === 'success' ? 'text-green-400' : 'text-red-400'}>
              {entry.result}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
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
  enablePDAS = false,
  expectedBehavior,
  actualBehavior,
  auditTrail,
  onClose,
  onSettings,
  actions,
  className = '',
  headerClassName = '',
  contentClassName = '',
  footerClassName = '',
  showFooter = true,
  footerContent,
  showObservability = false,
  metrics,
}) => {
  const { vif, isConnected } = useAIMOS()
  const [renderTime, setRenderTime] = useState<number | null>(null)
  
  // Measure render time for observability
  useEffect(() => {
    if (showObservability) {
      const startTime = performance.now()
      return () => {
        const endTime = performance.now()
        setRenderTime(endTime - startTime)
      }
    }
  }, [showObservability, children])
  
  // PDAS: Pre-execution auditing
  useEffect(() => {
    if (enablePDAS && expectedBehavior && actualBehavior) {
      const matches = expectedBehavior === actualBehavior
      if (!matches && auditTrail) {
        // Log mismatch to audit trail
        console.warn(`[PDAS] Expected: ${expectedBehavior}, Actual: ${actualBehavior}`)
      }
    }
  }, [enablePDAS, expectedBehavior, actualBehavior, auditTrail])
  
  const errorMessage = error instanceof Error ? error.message : error
  
  return (
    <ErrorBoundary>
      <div 
        id={id}
        className={`h-full flex flex-col bg-gray-900 ${className}`}
        role="region"
        aria-label={`${title} panel`}
      >
        {/* Header */}
        <div className={`px-4 py-3 border-b border-gray-700 bg-gray-800/50 ${headerClassName}`}>
          <div className="flex items-center justify-between mb-1">
            <div className="flex items-center gap-2">
              {Icon && <Icon className="w-5 h-5 text-blue-400" />}
              <h2 className="text-sm font-semibold text-gray-200">{title}</h2>
              
              {/* Confidence Badge */}
              {confidenceBand && (
                <span className={`text-xs px-1.5 py-0.5 rounded border ${getConfidenceBadge(confidenceBand)} ${getConfidenceColor(confidenceBand)}`}>
                  {confidenceBand === 'A' || confidenceBand === 'green' ? '🟢' : confidenceBand === 'B' || confidenceBand === 'yellow' ? '🟡' : '🔴'} {confidenceBand}
                </span>
              )}
            </div>
            
            {/* Actions */}
            <div className="flex items-center gap-1">
              {actions}
              {onSettings && (
                <button
                  onClick={onSettings}
                  className="p-1 rounded text-gray-400 hover:text-gray-200 hover:bg-gray-700 transition-colors"
                  title="Settings"
                  aria-label="Panel settings"
                >
                  <Settings className="w-4 h-4" />
                </button>
              )}
              {onClose && (
                <button
                  onClick={onClose}
                  className="p-1 rounded text-gray-400 hover:text-gray-200 hover:bg-gray-700 transition-colors"
                  title="Close panel"
                  aria-label="Close panel"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>
          
          {/* Description */}
          {description && (
            <div className="text-xs text-gray-400 mb-1">{description}</div>
          )}
          
          {/* PDAS: Expected vs Actual */}
          {enablePDAS && expectedBehavior && actualBehavior && (
            <div className="mt-2 p-2 bg-gray-900/50 rounded text-xs">
              <div className="flex items-center gap-2 mb-1">
                <Eye className="w-3 h-3 text-blue-400" />
                <span className="text-gray-500">PDAS:</span>
              </div>
              <div className="space-y-1">
                <div className="text-gray-400">
                  <span className="text-gray-600">Expected:</span> {expectedBehavior}
                </div>
                <div className={expectedBehavior === actualBehavior ? 'text-green-400' : 'text-red-400'}>
                  <span className="text-gray-600">Actual:</span> {actualBehavior}
                </div>
              </div>
              {auditTrail && <AuditTrail auditTrail={auditTrail} />}
            </div>
          )}
        </div>
        
        {/* Content */}
        <div className={`flex-1 overflow-auto ${contentClassName}`}>
          {/* Loading State */}
          {loading && (
            <LoadingState message="Loading..." />
          )}
          
          {/* Error State */}
          {!loading && errorMessage && (
            <div className="h-full flex items-center justify-center p-4">
              <div className="flex flex-col items-center gap-3 text-red-400 max-w-md text-center">
                <AlertTriangle className="w-8 h-8" />
                <span className="text-sm font-semibold">Error</span>
                <span className="text-xs text-gray-400">{errorMessage}</span>
              </div>
            </div>
          )}
          
          {/* Empty State */}
          {!loading && !errorMessage && empty && (
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
          {!loading && !errorMessage && !empty && children}
        </div>
        
        {/* Footer */}
        {showFooter && (
          <div className={`px-3 py-2 border-t border-gray-700 bg-gray-800/50 ${footerClassName}`}>
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
                  
                  {/* Observability Metrics */}
                  {showObservability && metrics && (
                    <>
                      {metrics.renderTime && (
                        <div className="flex items-center gap-1">
                          <Activity className="w-3 h-3" />
                          <span>{metrics.renderTime.toFixed(0)}ms</span>
                        </div>
                      )}
                      {metrics.errorRate !== undefined && (
                        <div className={`flex items-center gap-1 ${metrics.errorRate > 0 ? 'text-red-400' : 'text-green-400'}`}>
                          <AlertTriangle className="w-3 h-3" />
                          <span>{metrics.errorRate.toFixed(1)}%</span>
                        </div>
                      )}
                    </>
                  )}
                </div>
                
                {/* Right: Status */}
                <div className="flex items-center gap-2">
                  {!errorMessage && !loading && (
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
    </ErrorBoundary>
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

// PDAS Panel (with pre-execution auditing)
export const PDASPanel: React.FC<BasePanelProps> = (props) => {
  return (
    <BasePanel
      {...props}
      enablePDAS={true}
      showObservability={true}
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

