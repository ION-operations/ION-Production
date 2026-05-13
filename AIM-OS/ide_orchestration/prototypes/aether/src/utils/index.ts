// Utility Functions for AIM-OS Integration
// Helper functions for common operations

import type { Memory, SearchResult, ValidationResult } from '@/hooks/types'

/**
 * Format confidence as percentage
 */
export function formatConfidence(confidence: number): string {
  return `${(confidence * 100).toFixed(0)}%`
}

/**
 * Format timestamp for display
 */
export function formatTimestamp(timestamp: string): string {
  const date = new Date(timestamp)
  return date.toLocaleString()
}

/**
 * Format relative time (e.g., "2 minutes ago")
 */
export function formatRelativeTime(timestamp: string): string {
  const date = new Date(timestamp)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`
  if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`
  if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`
  return formatTimestamp(timestamp)
}

/**
 * Get color for confidence level
 */
export function getConfidenceColor(confidence: number): string {
  if (confidence >= 0.9) return 'text-green-400'
  if (confidence >= 0.7) return 'text-yellow-400'
  if (confidence >= 0.5) return 'text-orange-400'
  return 'text-red-400'
}

/**
 * Get background color for confidence level
 */
export function getConfidenceBgColor(confidence: number): string {
  if (confidence >= 0.9) return 'bg-green-900/20 border-green-700'
  if (confidence >= 0.7) return 'bg-yellow-900/20 border-yellow-700'
  if (confidence >= 0.5) return 'bg-orange-900/20 border-orange-700'
  return 'bg-red-900/20 border-red-700'
}

/**
 * Truncate text with ellipsis
 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength - 3) + '...'
}

/**
 * Format file size
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`
}

/**
 * Debounce function
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null
  
  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout)
    timeout = setTimeout(() => func(...args), wait)
  }
}

/**
 * Throttle function
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean
  
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args)
      inThrottle = true
      setTimeout(() => (inThrottle = false), limit)
    }
  }
}

/**
 * Generate unique ID
 */
export function generateId(prefix: string = 'id'): string {
  return `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

/**
 * Check if value is empty
 */
export function isEmpty(value: any): boolean {
  if (value === null || value === undefined) return true
  if (typeof value === 'string') return value.trim().length === 0
  if (Array.isArray(value)) return value.length === 0
  if (typeof value === 'object') return Object.keys(value).length === 0
  return false
}

/**
 * Deep clone object
 */
export function deepClone<T>(obj: T): T {
  return JSON.parse(JSON.stringify(obj))
}

/**
 * Get nested value from object
 */
export function getNestedValue(obj: any, path: string): any {
  return path.split('.').reduce((current, key) => current?.[key], obj)
}

/**
 * Set nested value in object
 */
export function setNestedValue(obj: any, path: string, value: any): void {
  const keys = path.split('.')
  const lastKey = keys.pop()!
  const target = keys.reduce((current, key) => {
    if (!current[key]) current[key] = {}
    return current[key]
  }, obj)
  target[lastKey] = value
}

/**
 * Format validation result for display
 */
export function formatValidationResult(result: ValidationResult): string {
  if (result.valid) {
    return `✓ Valid (${formatConfidence(result.confidence)})`
  }
  return `✗ Invalid (${formatConfidence(result.confidence)})`
}

/**
 * Get status color for panel
 */
export function getStatusColor(status: string): string {
  switch (status) {
    case 'connected':
    case 'completed':
    case 'solved':
      return 'text-green-400'
    case 'connecting':
    case 'in_progress':
    case 'investigating':
      return 'text-yellow-400'
    case 'error':
    case 'failed':
    case 'new':
      return 'text-red-400'
    case 'disconnected':
    case 'pending':
      return 'text-gray-400'
    default:
      return 'text-gray-400'
  }
}

/**
 * Get status background color for panel
 */
export function getStatusBgColor(status: string): string {
  switch (status) {
    case 'connected':
    case 'completed':
    case 'solved':
      return 'bg-green-900/20 border-green-700'
    case 'connecting':
    case 'in_progress':
    case 'investigating':
      return 'bg-yellow-900/20 border-yellow-700'
    case 'error':
    case 'failed':
    case 'new':
      return 'bg-red-900/20 border-red-700'
    case 'disconnected':
    case 'pending':
      return 'bg-gray-900/20 border-gray-700'
    default:
      return 'bg-gray-900/20 border-gray-700'
  }
}

/**
 * Format memory for display
 */
export function formatMemory(memory: Memory): string {
  return truncateText(memory.content, 100)
}

/**
 * Format search result for display
 */
export function formatSearchResult(result: SearchResult): string {
  return `${truncateText(result.content, 80)} (${formatConfidence(result.relevance)})`
}

/**
 * Sort by confidence (highest first)
 */
export function sortByConfidence<T extends { confidence?: number }>(items: T[]): T[] {
  return [...items].sort((a, b) => (b.confidence || 0) - (a.confidence || 0))
}

/**
 * Sort by timestamp (newest first)
 */
export function sortByTimestamp<T extends { timestamp: string }>(items: T[]): T[] {
  return [...items].sort((a, b) => 
    new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  )
}

/**
 * Filter by confidence threshold
 */
export function filterByConfidence<T extends { confidence?: number }>(
  items: T[],
  threshold: number = 0.7
): T[] {
  return items.filter(item => (item.confidence || 0) >= threshold)
}

/**
 * Group by key
 */
export function groupBy<T>(items: T[], key: keyof T): Record<string, T[]> {
  return items.reduce((groups, item) => {
    const groupKey = String(item[key])
    if (!groups[groupKey]) groups[groupKey] = []
    groups[groupKey].push(item)
    return groups
  }, {} as Record<string, T[]>)
}

/**
 * Class name utility (like clsx)
 */
export function cn(...classes: (string | boolean | undefined | null)[]): string {
  return classes.filter(Boolean).join(' ')
}

/**
 * Sleep utility for async operations
 */
export function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms))
}

/**
 * Retry async operation
 */
export async function retry<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  delay: number = 1000
): Promise<T> {
  let lastError: Error
  
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn()
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error))
      if (i < maxRetries - 1) {
        await sleep(delay * (i + 1))
      }
    }
  }
  
  throw lastError!
}

/**
 * Safe JSON parse
 */
export function safeJsonParse<T>(json: string, defaultValue: T): T {
  try {
    return JSON.parse(json) as T
  } catch {
    return defaultValue
  }
}

/**
 * Safe JSON stringify
 */
export function safeJsonStringify(obj: any, defaultValue: string = '{}'): string {
  try {
    return JSON.stringify(obj)
  } catch {
    return defaultValue
  }
}

