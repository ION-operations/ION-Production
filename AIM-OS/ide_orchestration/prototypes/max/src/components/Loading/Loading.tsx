// Loading Components for Max V2
// Provides skeleton loaders, progress indicators, and loading states

import React from 'react'
import './Loading.css'

interface SkeletonProps {
  width?: string | number
  height?: string | number
  className?: string
  rounded?: boolean
}

export const Skeleton: React.FC<SkeletonProps> = ({
  width = '100%',
  height = '1rem',
  className = '',
  rounded = false,
}) => {
  return (
    <div
      className={`skeleton ${rounded ? 'skeleton-rounded' : ''} ${className}`}
      style={{ width, height }}
      aria-label="Loading"
      role="status"
    >
      <span className="sr-only">Loading...</span>
    </div>
  )
}

interface SkeletonTextProps {
  lines?: number
  className?: string
}

export const SkeletonText: React.FC<SkeletonTextProps> = ({
  lines = 3,
  className = '',
}) => {
  return (
    <div className={`skeleton-text ${className}`} aria-label="Loading text" role="status">
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton
          key={i}
          height="1rem"
          width={i === lines - 1 ? '80%' : '100%'}
          className="skeleton-text-line"
        />
      ))}
      <span className="sr-only">Loading text...</span>
    </div>
  )
}

interface ProgressIndicatorProps {
  progress?: number
  indeterminate?: boolean
  label?: string
  className?: string
}

export const ProgressIndicator: React.FC<ProgressIndicatorProps> = ({
  progress = 0,
  indeterminate = false,
  label,
  className = '',
}) => {
  return (
    <div className={`progress-indicator ${className}`} role="progressbar" aria-valuenow={indeterminate ? undefined : progress} aria-valuemin={0} aria-valuemax={100} aria-label={label || 'Loading'}>
      <div
        className={`progress-bar ${indeterminate ? 'progress-bar-indeterminate' : ''}`}
        style={indeterminate ? {} : { width: `${progress}%` }}
      />
      {label && <span className="progress-label">{label}</span>}
    </div>
  )
}

interface LoadingSpinnerProps {
  size?: 'small' | 'medium' | 'large'
  className?: string
  label?: string
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'medium',
  className = '',
  label = 'Loading',
}) => {
  return (
    <div
      className={`loading-spinner loading-spinner-${size} ${className}`}
      role="status"
      aria-label={label}
    >
      <div className="spinner" />
      <span className="sr-only">{label}</span>
    </div>
  )
}

interface PanelLoadingProps {
  message?: string
}

export const PanelLoading: React.FC<PanelLoadingProps> = ({
  message = 'Loading panel...',
}) => {
  return (
    <div className="panel-loading" role="status" aria-live="polite">
      <LoadingSpinner size="medium" label={message} />
      <p className="panel-loading-message">{message}</p>
    </div>
  )
}

// Screen reader only text
export const SrOnly: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return <span className="sr-only">{children}</span>
}

