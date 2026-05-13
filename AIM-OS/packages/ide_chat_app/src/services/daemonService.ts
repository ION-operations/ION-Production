/**
 * Daemon Service
 * 
 * Phase 1.3.3: Daemon Services Integration (OBJ-08)
 * 
 * Provides service layer for daemon/RAG system integration
 * 
 * Features:
 * - Health checks (GET /api/health)
 * - Status monitoring (GET /api/status)
 * - Request processing (POST /api/requests)
 * - Tool registry access (GET /api/tools)
 * - RAG statistics (GET /api/rag/statistics)
 * - Real-time updates (SSE /api/stream)
 */

const DAEMON_BASE_URL = 'http://localhost:5000'
const DAEMON_HEALTH_ENDPOINT = `${DAEMON_BASE_URL}/api/health`
const DAEMON_STATUS_ENDPOINT = `${DAEMON_BASE_URL}/api/status`
const DAEMON_REQUESTS_ENDPOINT = `${DAEMON_BASE_URL}/api/requests`
const DAEMON_TOOLS_ENDPOINT = `${DAEMON_BASE_URL}/api/tools`
const DAEMON_RAG_STATS_ENDPOINT = `${DAEMON_BASE_URL}/api/rag/statistics`
const CONNECTION_TIMEOUT = 5000 // 5 seconds

export interface DaemonHealth {
  status: 'healthy' | 'unavailable'
  timestamp: string
  daemon_status: 'running' | 'stopped' | 'starting' | 'stopping' | 'error'
  version: string
}

export interface DaemonStatus {
  status: 'running' | 'stopped' | 'starting' | 'stopping' | 'error'
  metrics: {
    total_requests: number
    successful_requests: number
    failed_requests: number
    average_response_time_ms: number
    context_analysis_time_ms: number
    tool_selection_time_ms: number
    server_management_time_ms: number
  }
  server_status: {
    total_servers: number
    running_servers: number
    available_servers: number
  }
  resource_usage: {
    memory_usage_mb: number
    cpu_usage_percent: number
  }
  configuration: {
    max_tools: number
    learning_enabled: boolean
    performance_monitoring_enabled: boolean
  }
}

export interface DaemonRequest {
  user_input: string
  environment?: string
  max_tools?: number
  strategy?: 'fast' | 'balanced' | 'thorough'
}

export interface DaemonResponse {
  selected_tools: string[]
  reasoning: string
  confidence: number
  context_analysis: {
    complexity: 'low' | 'medium' | 'high'
    context_type: string
  }
}

class DaemonService {
  private connectionStatus: 'connected' | 'disconnected' | 'checking' = 'checking'
  private lastHealthCheck: number = 0
  private healthCheckInterval: number = 10000 // 10 seconds

  /**
   * Check if daemon is available
   */
  async checkHealth(): Promise<DaemonHealth | null> {
    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), CONNECTION_TIMEOUT)
      
      const response = await fetch(DAEMON_HEALTH_ENDPOINT, {
        method: 'GET',
        signal: controller.signal,
        headers: { 'Content-Type': 'application/json' },
      })
      
      clearTimeout(timeoutId)
      
      if (response.ok) {
        const health = await response.json()
        this.connectionStatus = 'connected'
        this.lastHealthCheck = Date.now()
        return health as DaemonHealth
      } else {
        this.connectionStatus = 'disconnected'
        this.lastHealthCheck = Date.now()
        return null
      }
    } catch (error) {
      this.connectionStatus = 'disconnected'
      this.lastHealthCheck = Date.now()
      return null
    }
  }

  /**
   * Get comprehensive daemon status
   */
  async getStatus(): Promise<DaemonStatus | null> {
    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), CONNECTION_TIMEOUT)
      
      const response = await fetch(DAEMON_STATUS_ENDPOINT, {
        method: 'GET',
        signal: controller.signal,
        headers: { 'Content-Type': 'application/json' },
      })
      
      clearTimeout(timeoutId)
      
      if (response.ok) {
        const status = await response.json()
        this.connectionStatus = 'connected'
        this.lastHealthCheck = Date.now()
        return status as DaemonStatus
      } else {
        this.connectionStatus = 'disconnected'
        return null
      }
    } catch (error) {
      this.connectionStatus = 'disconnected'
      return null
    }
  }

  /**
   * Process request via daemon (intelligent tool selection)
   */
  async processRequest(request: DaemonRequest): Promise<DaemonResponse | null> {
    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), CONNECTION_TIMEOUT)
      
      const response = await fetch(DAEMON_REQUESTS_ENDPOINT, {
        method: 'POST',
        signal: controller.signal,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request),
      })
      
      clearTimeout(timeoutId)
      
      if (response.ok) {
        const result = await response.json()
        this.connectionStatus = 'connected'
        this.lastHealthCheck = Date.now()
        return result as DaemonResponse
      } else {
        this.connectionStatus = 'disconnected'
        return null
      }
    } catch (error) {
      this.connectionStatus = 'disconnected'
      return null
    }
  }

  /**
   * Get available tools from daemon
   */
  async getTools(): Promise<string[] | null> {
    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), CONNECTION_TIMEOUT)
      
      const response = await fetch(DAEMON_TOOLS_ENDPOINT, {
        method: 'GET',
        signal: controller.signal,
        headers: { 'Content-Type': 'application/json' },
      })
      
      clearTimeout(timeoutId)
      
      if (response.ok) {
        const result = await response.json()
        this.connectionStatus = 'connected'
        this.lastHealthCheck = Date.now()
        return result.tools || []
      } else {
        this.connectionStatus = 'disconnected'
        return null
      }
    } catch (error) {
      this.connectionStatus = 'disconnected'
      return null
    }
  }

  /**
   * Get RAG system statistics
   */
  async getRAGStatistics(): Promise<any | null> {
    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), CONNECTION_TIMEOUT)
      
      const response = await fetch(DAEMON_RAG_STATS_ENDPOINT, {
        method: 'GET',
        signal: controller.signal,
        headers: { 'Content-Type': 'application/json' },
      })
      
      clearTimeout(timeoutId)
      
      if (response.ok) {
        const stats = await response.json()
        this.connectionStatus = 'connected'
        this.lastHealthCheck = Date.now()
        return stats
      } else {
        this.connectionStatus = 'disconnected'
        return null
      }
    } catch (error) {
      this.connectionStatus = 'disconnected'
      return null
    }
  }

  /**
   * Get connection status
   */
  getConnectionStatus(): 'connected' | 'disconnected' | 'checking' {
    // Auto-check if stale
    const timeSinceLastCheck = Date.now() - this.lastHealthCheck
    if (timeSinceLastCheck > this.healthCheckInterval) {
      this.checkHealth() // Fire and forget
    }
    return this.connectionStatus
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
export const daemonService = new DaemonService()

// Export convenience functions
export const checkDaemonHealth = () => daemonService.checkHealth()
export const getDaemonStatus = () => daemonService.getStatus()
export const processDaemonRequest = (request: DaemonRequest) => daemonService.processRequest(request)
export const getDaemonTools = () => daemonService.getTools()
export const getDaemonRAGStatistics = () => daemonService.getRAGStatistics()
export const getDaemonConnectionStatus = () => daemonService.getConnectionStatus()
export const getDaemonConnectionHealth = () => daemonService.getConnectionHealth()

