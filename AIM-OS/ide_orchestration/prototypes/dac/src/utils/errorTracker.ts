// Error Tracker - Comprehensive error tracking and diagnostics system
// Tracks all panel errors, provides diagnostics, and enables one-click error reporting

import React from 'react'

export interface PanelError {
  id: string
  panelId: string
  panelName: string
  error: Error
  errorInfo?: React.ErrorInfo
  timestamp: Date
  componentStack?: string
  userActions?: string[] // Actions user took before error
  context?: Record<string, any> // Additional context
  resolved: boolean
  resolvedAt?: Date
}

export interface PanelDiagnostics {
  panelId: string
  panelName: string
  status: 'healthy' | 'error' | 'warning' | 'loading'
  errors: PanelError[]
  lastError?: PanelError
  mountCount: number
  renderCount: number
  loadTime?: number
  memoryUsage?: number
  performanceMetrics?: {
    averageRenderTime?: number
    slowestRender?: number
    renderCount: number
  }
  networkRequests?: Array<{
    url: string
    method: string
    status?: number
    duration?: number
    timestamp: Date
    error?: string
  }>
  consoleErrors?: Array<{
    message: string
    source?: string
    line?: number
    column?: number
    timestamp: Date
  }>
}

class ErrorTracker {
  private errors: Map<string, PanelError[]> = new Map() // panelId -> errors[]
  private diagnostics: Map<string, PanelDiagnostics> = new Map()
  private maxErrorsPerPanel = 50 // Keep last 50 errors per panel
  private listeners: Set<(panelId: string, error: PanelError) => void> = new Set()
  
  constructor() {
    this.setupGlobalErrorHandlers()
  }
  
  private setupGlobalErrorHandlers() {
    // Track unhandled errors
    window.addEventListener('error', (event) => {
      this.trackConsoleError({
        message: event.message,
        source: event.filename,
        line: event.lineno,
        column: event.colno,
        timestamp: new Date()
      })
    })
    
    // Track unhandled promise rejections
    window.addEventListener('unhandledrejection', (event) => {
      const error = event.reason instanceof Error ? event.reason : new Error(String(event.reason))
      this.trackConsoleError({
        message: `Unhandled Promise Rejection: ${error.message}`,
        timestamp: new Date()
      })
    })
  }
  
  trackError(
    panelId: string,
    panelName: string,
    error: Error,
    errorInfo?: React.ErrorInfo,
    context?: Record<string, any>
  ): string {
    const errorId = `${panelId}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    
    const panelError: PanelError = {
      id: errorId,
      panelId,
      panelName,
      error,
      errorInfo,
      timestamp: new Date(),
      componentStack: errorInfo?.componentStack,
      context,
      resolved: false
    }
    
    // Add to errors list
    if (!this.errors.has(panelId)) {
      this.errors.set(panelId, [])
    }
    const errors = this.errors.get(panelId)!
    errors.push(panelError)
    
    // Keep only last N errors
    if (errors.length > this.maxErrorsPerPanel) {
      errors.shift()
    }
    
    // Update diagnostics
    this.updateDiagnostics(panelId, panelName, panelError)
    
    // Notify listeners
    this.listeners.forEach(listener => listener(panelId, panelError))
    
    return errorId
  }
  
  trackConsoleError(error: { message: string; source?: string; line?: number; column?: number; timestamp: Date }) {
    // Try to associate with a panel (heuristic)
    const activePanelId = this.getActivePanelId()
    if (activePanelId) {
      const diagnostics = this.diagnostics.get(activePanelId)
      if (diagnostics) {
        if (!diagnostics.consoleErrors) {
          diagnostics.consoleErrors = []
        }
        diagnostics.consoleErrors.push(error)
        
        // Keep only last 20 console errors
        if (diagnostics.consoleErrors.length > 20) {
          diagnostics.consoleErrors.shift()
        }
      }
    }
  }
  
  trackNetworkRequest(
    panelId: string,
    url: string,
    method: string,
    status?: number,
    duration?: number,
    error?: string
  ) {
    const diagnostics = this.getOrCreateDiagnostics(panelId, 'Unknown Panel')
    if (!diagnostics.networkRequests) {
      diagnostics.networkRequests = []
    }
    diagnostics.networkRequests.push({
      url,
      method,
      status,
      duration,
      timestamp: new Date(),
      error
    })
    
    // Keep only last 50 requests
    if (diagnostics.networkRequests.length > 50) {
      diagnostics.networkRequests.shift()
    }
  }
  
  private getActivePanelId(): string | null {
    // Heuristic: try to find active panel from DOM or React tree
    // This is a simplified version - in production you'd want more sophisticated tracking
    return null
  }
  
  private updateDiagnostics(panelId: string, panelName: string, error: PanelError) {
    const diagnostics = this.getOrCreateDiagnostics(panelId, panelName)
    diagnostics.errors.push(error)
    diagnostics.lastError = error
    diagnostics.status = 'error'
    
    // Keep only last N errors in diagnostics
    if (diagnostics.errors.length > this.maxErrorsPerPanel) {
      diagnostics.errors.shift()
    }
  }
  
  getOrCreateDiagnostics(panelId: string, panelName: string): PanelDiagnostics {
    if (!this.diagnostics.has(panelId)) {
      this.diagnostics.set(panelId, {
        panelId,
        panelName,
        status: 'healthy',
        errors: [],
        mountCount: 0,
        renderCount: 0
      })
    }
    return this.diagnostics.get(panelId)!
  }
  
  updatePanelMetrics(
    panelId: string,
    panelName: string,
    metrics: {
      mountCount?: number
      renderCount?: number
      loadTime?: number
      memoryUsage?: number
      averageRenderTime?: number
      slowestRender?: number
    }
  ) {
    const diagnostics = this.getOrCreateDiagnostics(panelId, panelName)
    if (metrics.mountCount !== undefined) diagnostics.mountCount = metrics.mountCount
    if (metrics.renderCount !== undefined) diagnostics.renderCount = metrics.renderCount
    if (metrics.loadTime !== undefined) diagnostics.loadTime = metrics.loadTime
    if (metrics.memoryUsage !== undefined) diagnostics.memoryUsage = metrics.memoryUsage
    
    if (!diagnostics.performanceMetrics) {
      diagnostics.performanceMetrics = { renderCount: 0 }
    }
    if (metrics.averageRenderTime !== undefined) {
      diagnostics.performanceMetrics.averageRenderTime = metrics.averageRenderTime
    }
    if (metrics.slowestRender !== undefined) {
      diagnostics.performanceMetrics.slowestRender = metrics.slowestRender
    }
    diagnostics.performanceMetrics.renderCount = diagnostics.renderCount
  }
  
  markErrorResolved(panelId: string, errorId: string) {
    const errors = this.errors.get(panelId)
    if (errors) {
      const error = errors.find(e => e.id === errorId)
      if (error) {
        error.resolved = true
        error.resolvedAt = new Date()
        
        // Update diagnostics status if all errors resolved
        const diagnostics = this.diagnostics.get(panelId)
        if (diagnostics) {
          const hasUnresolvedErrors = diagnostics.errors.some(e => !e.resolved)
          if (!hasUnresolvedErrors) {
            diagnostics.status = 'healthy'
          }
        }
      }
    }
  }
  
  getPanelErrors(panelId: string): PanelError[] {
    return this.errors.get(panelId) || []
  }
  
  getPanelDiagnostics(panelId: string): PanelDiagnostics | undefined {
    return this.diagnostics.get(panelId)
  }
  
  getAllDiagnostics(): PanelDiagnostics[] {
    return Array.from(this.diagnostics.values())
  }
  
  getErrorCount(): number {
    return Array.from(this.errors.values()).reduce((total, errors) => total + errors.length, 0)
  }
  
  getUnresolvedErrorCount(): number {
    return Array.from(this.errors.values()).reduce((total, errors) => {
      return total + errors.filter(e => !e.resolved).length
    }, 0)
  }
  
  generateDiagnosticsReport(panelId?: string): string {
    const diagnostics = panelId 
      ? (this.diagnostics.get(panelId) ? [this.diagnostics.get(panelId)!] : [])
      : this.getAllDiagnostics()
    
    const report: any = {
      timestamp: new Date().toISOString(),
      summary: {
        totalPanels: diagnostics.length,
        panelsWithErrors: diagnostics.filter(d => d.errors.length > 0).length,
        totalErrors: diagnostics.reduce((sum, d) => sum + d.errors.length, 0),
        unresolvedErrors: diagnostics.reduce((sum, d) => sum + d.errors.filter(e => !e.resolved).length, 0)
      },
      panels: diagnostics.map(d => ({
        panelId: d.panelId,
        panelName: d.panelName,
        status: d.status,
        errorCount: d.errors.length,
        lastError: d.lastError ? {
          message: d.lastError.error.message,
          timestamp: d.lastError.timestamp.toISOString(),
          componentStack: d.lastError.componentStack
        } : null,
        performance: {
          mountCount: d.mountCount,
          renderCount: d.renderCount,
          loadTime: d.loadTime,
          memoryUsage: d.memoryUsage,
          averageRenderTime: d.performanceMetrics?.averageRenderTime,
          slowestRender: d.performanceMetrics?.slowestRender
        },
        networkRequests: d.networkRequests?.length || 0,
        consoleErrors: d.consoleErrors?.length || 0
      })),
      fullErrors: diagnostics.flatMap(d => d.errors.map(e => ({
        panelId: e.panelId,
        panelName: e.panelName,
        errorId: e.id,
        message: e.error.message,
        stack: e.error.stack,
        componentStack: e.componentStack,
        timestamp: e.timestamp.toISOString(),
        resolved: e.resolved,
        context: e.context
      })))
    }
    
    return JSON.stringify(report, null, 2)
  }
  
  generateMarkdownReport(panelId?: string): string {
    const diagnostics = panelId 
      ? (this.diagnostics.get(panelId) ? [this.diagnostics.get(panelId)!] : [])
      : this.getAllDiagnostics()
    
    const panelsWithErrors = diagnostics.filter(d => d.errors.length > 0)
    const totalErrors = diagnostics.reduce((sum, d) => sum + d.errors.length, 0)
    const unresolvedErrors = diagnostics.reduce((sum, d) => sum + d.errors.filter(e => !e.resolved).length, 0)
    
    let markdown = `# Panel Diagnostics Report\n\n`
    markdown += `**Generated:** ${new Date().toISOString()}\n\n`
    markdown += `## Summary\n\n`
    markdown += `- **Total Panels:** ${diagnostics.length}\n`
    markdown += `- **Panels with Errors:** ${panelsWithErrors.length}\n`
    markdown += `- **Total Errors:** ${totalErrors}\n`
    markdown += `- **Unresolved Errors:** ${unresolvedErrors}\n\n`
    
    if (panelsWithErrors.length > 0) {
      markdown += `## Panels with Errors\n\n`
      panelsWithErrors.forEach(d => {
        markdown += `### ${d.panelName} (${d.panelId})\n\n`
        markdown += `**Status:** ${d.status}\n`
        markdown += `**Error Count:** ${d.errors.length}\n\n`
        
        if (d.lastError) {
          markdown += `#### Last Error\n\n`
          markdown += `**Message:** ${d.lastError.error.message}\n\n`
          markdown += `**Timestamp:** ${d.lastError.timestamp.toISOString()}\n\n`
          if (d.lastError.componentStack) {
            markdown += `**Component Stack:**\n\`\`\`\n${d.lastError.componentStack}\n\`\`\`\n\n`
          }
          if (d.lastError.error.stack) {
            markdown += `**Stack Trace:**\n\`\`\`\n${d.lastError.error.stack}\n\`\`\`\n\n`
          }
        }
        
        if (d.errors.length > 1) {
          markdown += `#### All Errors (${d.errors.length})\n\n`
          d.errors.forEach((error, idx) => {
            markdown += `${idx + 1}. **${error.error.message}** (${error.timestamp.toISOString()}) ${error.resolved ? '✅ Resolved' : '❌ Unresolved'}\n`
          })
          markdown += `\n`
        }
      })
    }
    
    markdown += `## Performance Metrics\n\n`
    diagnostics.forEach(d => {
      if (d.performanceMetrics || d.loadTime) {
        markdown += `### ${d.panelName}\n\n`
        markdown += `- Mount Count: ${d.mountCount}\n`
        markdown += `- Render Count: ${d.renderCount}\n`
        if (d.loadTime) markdown += `- Load Time: ${d.loadTime}ms\n`
        if (d.performanceMetrics?.averageRenderTime) {
          markdown += `- Average Render Time: ${d.performanceMetrics.averageRenderTime.toFixed(2)}ms\n`
        }
        if (d.performanceMetrics?.slowestRender) {
          markdown += `- Slowest Render: ${d.performanceMetrics.slowestRender}ms\n`
        }
        markdown += `\n`
      }
    })
    
    return markdown
  }
  
  subscribe(listener: (panelId: string, error: PanelError) => void): () => void {
    this.listeners.add(listener)
    return () => this.listeners.delete(listener)
  }
  
  clearPanelErrors(panelId: string) {
    this.errors.delete(panelId)
    const diagnostics = this.diagnostics.get(panelId)
    if (diagnostics) {
      diagnostics.errors = []
      diagnostics.lastError = undefined
      diagnostics.status = 'healthy'
    }
  }
  
  clearAllErrors() {
    this.errors.clear()
    this.diagnostics.forEach(d => {
      d.errors = []
      d.lastError = undefined
      d.status = 'healthy'
    })
  }
}

// Singleton instance
export const errorTracker = new ErrorTracker()

