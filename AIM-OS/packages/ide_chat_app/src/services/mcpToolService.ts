/**
 * MCP Tool Service
 * 
 * Phase 1.1: Real MCP Tool Integration (OBJ-07)
 * 
 * Provides service layer for calling MCP tools via HTTP endpoint
 * 
 * Features:
 * - HTTP endpoint integration (http://localhost:5001/mcp/execute)
 * - Tool call tracking
 * - Error handling
 * - Retry logic
 * - Connection management
 * - Quality monitoring
 */

const MCP_ENDPOINT = 'http://localhost:5001/mcp/execute'
const MCP_HEALTH_ENDPOINT = 'http://localhost:5001/health'
const CONNECTION_TIMEOUT = 5000 // 5 seconds
const RETRY_ATTEMPTS = 3
const RETRY_DELAY = 1000 // 1 second

export interface MCPToolCall {
  tool: string
  arguments: Record<string, any>
}

export interface MCPToolResponse {
  success: boolean
  result?: any
  error?: string
  atom_id?: string
  timestamp?: string
}

export interface MCPToolMetrics {
  tool: string
  callCount: number
  successCount: number
  errorCount: number
  avgLatency: number
  lastCallTime?: string
  lastError?: string
  // Enhanced metrics
  successRate: number
  averageLatency: number
  recentCalls: number[] // Last 20 call latencies
  errorBreakdown: Array<{ type: string; count: number; percentage: number }>
  confidence: number // VIF confidence score
  trend: 'up' | 'down' | 'stable' // Latency trend
}

class MCPToolService {
  private metrics: Map<string, MCPToolMetrics> = new Map()
  private connectionStatus: 'connected' | 'disconnected' | 'checking' = 'checking'
  private lastHealthCheck: number = 0
  private healthCheckInterval: number = 5000 // 5 seconds
  private errorTypes: Map<string, Map<string, number>> = new Map() // tool -> errorType -> count
  private readonly MAX_RECENT_CALLS = 20

  /**
   * Check if MCP server is available
   */
  async checkConnection(): Promise<boolean> {
    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), CONNECTION_TIMEOUT)
      
      const response = await fetch(MCP_HEALTH_ENDPOINT, {
        method: 'GET',
        signal: controller.signal,
        headers: { 'Content-Type': 'application/json' },
      })
      
      clearTimeout(timeoutId)
      
      const isConnected = response.ok
      this.connectionStatus = isConnected ? 'connected' : 'disconnected'
      this.lastHealthCheck = Date.now()
      
      return isConnected
    } catch (error) {
      this.connectionStatus = 'disconnected'
      this.lastHealthCheck = Date.now()
      return false
    }
  }

  /**
   * Call MCP tool via HTTP endpoint
   */
  async callTool(tool: string, arguments_: Record<string, any>): Promise<MCPToolResponse> {
    const startTime = Date.now()
    
    // Initialize metrics if needed
    if (!this.metrics.has(tool)) {
      this.metrics.set(tool, {
        tool,
        callCount: 0,
        successCount: 0,
        errorCount: 0,
        avgLatency: 0,
        successRate: 0,
        averageLatency: 0,
        recentCalls: [],
        errorBreakdown: [],
        confidence: 0.9, // Default confidence
        trend: 'stable',
      })
      this.errorTypes.set(tool, new Map())
    }
    
    const metrics = this.metrics.get(tool)!
    metrics.callCount++
    
    // Check connection before calling
    const isConnected = await this.checkConnection()
    if (!isConnected) {
      metrics.errorCount++
      metrics.lastError = 'MCP server not available'
      return {
        success: false,
        error: 'MCP server not available. Using mock data fallback.',
      }
    }
    
    // Retry logic
    let lastError: Error | null = null
    for (let attempt = 1; attempt <= RETRY_ATTEMPTS; attempt++) {
      try {
        const controller = new AbortController()
        const timeoutId = setTimeout(() => controller.abort(), CONNECTION_TIMEOUT)
        
        const response = await fetch(MCP_ENDPOINT, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            tool,
            arguments: arguments_,
          }),
          signal: controller.signal,
        })
        
        clearTimeout(timeoutId)
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`)
        }
        
        const result = await response.json()
        const latency = Date.now() - startTime
        
        // Update metrics
        metrics.successCount++
        metrics.avgLatency = (metrics.avgLatency * (metrics.callCount - 1) + latency) / metrics.callCount
        metrics.averageLatency = metrics.avgLatency
        metrics.lastCallTime = new Date().toISOString()
        
        // Track recent call latencies
        metrics.recentCalls.push(latency)
        if (metrics.recentCalls.length > this.MAX_RECENT_CALLS) {
          metrics.recentCalls.shift()
        }
        
        // Calculate success rate
        metrics.successRate = metrics.successCount / metrics.callCount
        
        // Calculate latency trend
        if (metrics.recentCalls.length >= 2) {
          const recentAvg = metrics.recentCalls.slice(-5).reduce((a, b) => a + b, 0) / Math.min(5, metrics.recentCalls.length)
          const olderAvg = metrics.recentCalls.slice(0, -5).reduce((a, b) => a + b, 0) / Math.max(1, metrics.recentCalls.length - 5)
          if (recentAvg > olderAvg * 1.1) {
            metrics.trend = 'up'
          } else if (recentAvg < olderAvg * 0.9) {
            metrics.trend = 'down'
          } else {
            metrics.trend = 'stable'
          }
        }
        
        // Update confidence based on success rate and latency
        const latencyScore = latency < 100 ? 1.0 : latency < 200 ? 0.9 : latency < 500 ? 0.8 : 0.7
        metrics.confidence = (metrics.successRate * 0.7) + (latencyScore * 0.3)
        
        return {
          success: true,
          result: result.result || result,
          atom_id: result.atom_id,
          timestamp: new Date().toISOString(),
        }
      } catch (error) {
        lastError = error instanceof Error ? error : new Error(String(error))
        
        // Don't retry on abort (timeout)
        if (error instanceof Error && error.name === 'AbortError') {
          break
        }
        
        // Wait before retry
        if (attempt < RETRY_ATTEMPTS) {
          await new Promise(resolve => setTimeout(resolve, RETRY_DELAY * attempt))
        }
      }
    }
    
    // All retries failed
    metrics.errorCount++
    const errorMessage = lastError?.message || 'Unknown error'
    metrics.lastError = errorMessage
    
    // Track error types
    const errorType = this.categorizeError(errorMessage)
    const errorTypeMap = this.errorTypes.get(tool)!
    errorTypeMap.set(errorType, (errorTypeMap.get(errorType) || 0) + 1)
    
    // Update error breakdown
    const totalErrors = Array.from(errorTypeMap.values()).reduce((a, b) => a + b, 0)
    metrics.errorBreakdown = Array.from(errorTypeMap.entries()).map(([type, count]) => ({
      type,
      count,
      percentage: (count / totalErrors) * 100,
    }))
    
    // Update success rate and confidence
    metrics.successRate = metrics.successCount / metrics.callCount
    metrics.confidence = metrics.successRate * 0.8 // Lower confidence on errors
    
    return {
      success: false,
      error: errorMessage,
    }
  }

  /**
   * Categorize error by type
   */
  private categorizeError(error: string): string {
    const lowerError = error.toLowerCase()
    if (lowerError.includes('timeout') || lowerError.includes('abort')) {
      return 'Timeout'
    } else if (lowerError.includes('not available') || lowerError.includes('connection')) {
      return 'Connection Error'
    } else if (lowerError.includes('404') || lowerError.includes('not found')) {
      return 'Not Found'
    } else if (lowerError.includes('500') || lowerError.includes('server error')) {
      return 'Server Error'
    } else if (lowerError.includes('400') || lowerError.includes('bad request')) {
      return 'Bad Request'
    } else if (lowerError.includes('unauthorized') || lowerError.includes('403')) {
      return 'Unauthorized'
    } else {
      return 'Unknown Error'
    }
  }

  /**
   * Get tool metrics with enhanced data
   */
  getToolMetrics(tool: string): MCPToolMetrics | null {
    const metrics = this.metrics.get(tool)
    if (!metrics) return null
    
    // Ensure all enhanced fields are present
    return {
      ...metrics,
      successRate: metrics.successRate || (metrics.successCount / Math.max(1, metrics.callCount)),
      averageLatency: metrics.averageLatency || metrics.avgLatency,
      recentCalls: metrics.recentCalls || [],
      errorBreakdown: metrics.errorBreakdown || [],
      confidence: metrics.confidence || 0.9,
      trend: metrics.trend || 'stable',
    }
  }

  /**
   * Get all tool metrics with enhanced data
   */
  getAllMetrics(): MCPToolMetrics[] {
    return Array.from(this.metrics.values()).map(metrics => ({
      ...metrics,
      successRate: metrics.successRate || (metrics.successCount / Math.max(1, metrics.callCount)),
      averageLatency: metrics.averageLatency || metrics.avgLatency,
      recentCalls: metrics.recentCalls || [],
      errorBreakdown: metrics.errorBreakdown || [],
      confidence: metrics.confidence || 0.9,
      trend: metrics.trend || 'stable',
    }))
  }

  /**
   * Get connection status
   */
  getConnectionStatus(): 'connected' | 'disconnected' | 'checking' {
    // Auto-check if stale
    const timeSinceLastCheck = Date.now() - this.lastHealthCheck
    if (timeSinceLastCheck > this.healthCheckInterval) {
      this.checkConnection() // Fire and forget
    }
    return this.connectionStatus
  }

  /**
   * Reset metrics for a tool
   */
  resetMetrics(tool: string): void {
    this.metrics.delete(tool)
    this.errorTypes.delete(tool)
  }

  /**
   * Reset all metrics
   */
  resetAllMetrics(): void {
    this.metrics.clear()
    this.errorTypes.clear()
  }

  /**
   * Get connection health metrics
   */
  getConnectionHealth(): {
    status: 'connected' | 'disconnected' | 'checking'
    lastCheck: number
    uptime: number
  } {
    return {
      status: this.connectionStatus,
      lastCheck: this.lastHealthCheck,
      uptime: Date.now() - this.lastHealthCheck,
    }
  }
}

// Singleton instance
export const mcpToolService = new MCPToolService()

// Export convenience functions
export const callMCPTool = (tool: string, arguments_: Record<string, any>) => 
  mcpToolService.callTool(tool, arguments_)

export const checkMCPConnection = () => 
  mcpToolService.checkConnection()

export const getMCPConnectionStatus = () => 
  mcpToolService.getConnectionStatus()

export const getMCPToolMetrics = (tool: string) => 
  mcpToolService.getToolMetrics(tool)

export const getAllMCPMetrics = () => 
  mcpToolService.getAllMetrics()

