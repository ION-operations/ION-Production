/**
 * Hook-Specific Loading States
 * Loading indicators for AIM-OS hooks and operations
 * Created by Sage - Frontend Integration Specialist
 */

import React from 'react'
import { LoadingSpinner } from '../shared'
import { Database, Search, Shield, Network, Brain, Clock, Zap } from 'lucide-react'

export type HookType = 
  | 'cmc'      // Context Memory Core
  | 'hhni'     // Hierarchical Hypergraph Neural Index
  | 'vif'      // Verifiable Intelligence Framework
  | 'seg'      // Shared Evidence Graph
  | 'apoe'     // AI-Powered Orchestration Engine
  | 'cas'      // Cognitive Analysis System
  | 'tcs'      // Timeline Context System
  | 'icip'     // Intelligent Code Integration Platform
  | 'execution' // Code execution
  | 'generic'  // Generic loading

export interface HookLoadingStateProps {
  hookType: HookType
  operation?: string
  message?: string
  size?: 'sm' | 'md' | 'lg'
  fullScreen?: boolean
  className?: string
}

const hookConfig = {
  cmc: {
    icon: Database,
    name: 'CMC',
    defaultMessage: 'Storing memory...',
    color: 'text-blue-400'
  },
  hhni: {
    icon: Search,
    name: 'HHNI',
    defaultMessage: 'Searching knowledge...',
    color: 'text-purple-400'
  },
  vif: {
    icon: Shield,
    name: 'VIF',
    defaultMessage: 'Tracking confidence...',
    color: 'text-green-400'
  },
  seg: {
    icon: Network,
    name: 'SEG',
    defaultMessage: 'Synthesizing knowledge...',
    color: 'text-yellow-400'
  },
  apoe: {
    icon: Zap,
    name: 'APOE',
    defaultMessage: 'Executing plan...',
    color: 'text-orange-400'
  },
  cas: {
    icon: Brain,
    name: 'CAS',
    defaultMessage: 'Analyzing cognition...',
    color: 'text-pink-400'
  },
  tcs: {
    icon: Clock,
    name: 'TCS',
    defaultMessage: 'Updating timeline...',
    color: 'text-cyan-400'
  },
  icip: {
    icon: Zap,
    name: 'ICIP',
    defaultMessage: 'Generating code...',
    color: 'text-blue-400'
  },
  execution: {
    icon: Zap,
    name: 'Execution',
    defaultMessage: 'Executing code...',
    color: 'text-green-400'
  },
  generic: {
    icon: Clock,
    name: 'Loading',
    defaultMessage: 'Loading...',
    color: 'text-gray-400'
  }
}

export const HookLoadingState: React.FC<HookLoadingStateProps> = ({
  hookType,
  operation,
  message,
  size = 'md',
  fullScreen = false,
  className = '',
}) => {
  const config = hookConfig[hookType]
  const Icon = config.icon
  const displayMessage = message || operation || config.defaultMessage

  return (
    <div className={`flex flex-col items-center justify-center gap-3 ${fullScreen ? 'h-full' : ''} ${className}`}>
      <div className="flex flex-col items-center gap-3">
        <div className="relative">
          <LoadingSpinner size={size} />
          <div className="absolute inset-0 flex items-center justify-center">
            <Icon className={`w-4 h-4 ${config.color} ${size === 'lg' ? 'w-6 h-6' : size === 'sm' ? 'w-3 h-3' : ''}`} />
          </div>
        </div>
        <div className="flex flex-col items-center gap-1">
          <span className={`text-sm font-medium ${config.color}`}>
            {config.name}
          </span>
          {displayMessage && (
            <span className="text-xs text-gray-400 text-center max-w-xs">
              {displayMessage}
            </span>
          )}
        </div>
      </div>
    </div>
  )
}

/**
 * Convenience components for specific hooks
 */
export const CMCLoadingState: React.FC<Omit<HookLoadingStateProps, 'hookType'>> = (props) => (
  <HookLoadingState hookType="cmc" {...props} />
)

export const HHNILoadingState: React.FC<Omit<HookLoadingStateProps, 'hookType'>> = (props) => (
  <HookLoadingState hookType="hhni" {...props} />
)

export const VIFLoadingState: React.FC<Omit<HookLoadingStateProps, 'hookType'>> = (props) => (
  <HookLoadingState hookType="vif" {...props} />
)

export const SEGLoadingState: React.FC<Omit<HookLoadingStateProps, 'hookType'>> = (props) => (
  <HookLoadingState hookType="seg" {...props} />
)

export const APOELoadingState: React.FC<Omit<HookLoadingStateProps, 'hookType'>> = (props) => (
  <HookLoadingState hookType="apoe" {...props} />
)

export const CASLoadingState: React.FC<Omit<HookLoadingStateProps, 'hookType'>> = (props) => (
  <HookLoadingState hookType="cas" {...props} />
)

export const TCSLoadingState: React.FC<Omit<HookLoadingStateProps, 'hookType'>> = (props) => (
  <HookLoadingState hookType="tcs" {...props} />
)

export const ICIPLoadingState: React.FC<Omit<HookLoadingStateProps, 'hookType'>> = (props) => (
  <HookLoadingState hookType="icip" {...props} />
)

export const CodeExecutionLoadingState: React.FC<Omit<HookLoadingStateProps, 'hookType'>> = (props) => (
  <HookLoadingState hookType="execution" {...props} />
)

