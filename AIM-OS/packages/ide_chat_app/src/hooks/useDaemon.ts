/**
 * Daemon Connection Hook
 * React hook for connecting to Solo's daemon API with real-time updates
 */

import { useState, useEffect, useCallback, useRef } from 'react'
import { httpLucidDaemonService } from '../services/HttpLucidDaemonService'

export interface DaemonStatus {
  status: string
  timestamp?: string
  daemon_status?: string
  version?: string
  metrics?: {
    total_requests: number
    successful_requests: number
    failed_requests: number
    average_response_time_ms: number
  }
  server_status?: {
    total_servers: number
    running_servers: number
    available_servers: number
  }
  resource_usage?: {
    memory_usage_mb: number
    cpu_usage_percent: number
  }
  configuration?: {
    max_tools: number
    learning_enabled: boolean
    performance_monitoring_enabled: boolean
  }
}

export interface DaemonTools {
  total_tools: number
  tools: Array<{
    tool_id: string
    name: string
    category: string
    capabilities: string[]
    description: string
  }>
}

export interface RAGStatistics {
  total_patterns: number
  patterns_by_type: {
    SUCCESS: number
    FAILURE: number
  }
  learning_stats: {
    total_learning_events: number
    successful_learning: number
  }
}

export function useDaemon() {
  const [isConnected, setIsConnected] = useState(false)
  const [status, setStatus] = useState<DaemonStatus | null>(null)
  const [tools, setTools] = useState<DaemonTools | null>(null)
  const [ragStats, setRagStats] = useState<RAGStatistics | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const eventSourceRef = useRef<EventSource | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)

  /**
   * Check connection and update status
   */
  const checkConnection = useCallback(async () => {
    try {
      setIsLoading(true)
      setError(null)
      
      const health = await httpLucidDaemonService.healthCheck()
      setIsConnected(health.status === 'healthy')
      
      if (health.status === 'healthy') {
        // Get full status
        const fullStatus = await httpLucidDaemonService.getStatus()
        setStatus({
          ...health,
          ...fullStatus
        })
      } else {
        setStatus(health as DaemonStatus)
      }
    } catch (err) {
      setIsConnected(false)
      setError(err instanceof Error ? err.message : 'Failed to connect to daemon')
      setStatus(null)
    } finally {
      setIsLoading(false)
    }
  }, [])

  /**
   * Load tools list
   */
  const loadTools = useCallback(async () => {
    try {
      setIsLoading(true)
      setError(null)
      const toolsData = await httpLucidDaemonService.getTools()
      setTools(toolsData)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load tools')
    } finally {
      setIsLoading(false)
    }
  }, [])

  /**
   * Load RAG statistics
   */
  const loadRAGStats = useCallback(async () => {
    try {
      setIsLoading(true)
      setError(null)
      const stats = await httpLucidDaemonService.getRAGStatistics()
      setRagStats(stats)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load RAG statistics')
    } finally {
      setIsLoading(false)
    }
  }, [])

  /**
   * Process request via daemon
   */
  const processRequest = useCallback(async (
    userInput: string,
    environment?: any,
    maxTools?: number,
    strategy?: string
  ) => {
    try {
      setIsLoading(true)
      setError(null)
      return await httpLucidDaemonService.processRequest(userInput, environment, maxTools, strategy)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to process request')
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [])

  /**
   * Start real-time updates via SSE
   */
  const startRealTimeUpdates = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
    }

    const eventSource = httpLucidDaemonService.createEventSource()
    if (!eventSource) {
      console.warn('EventSource not available')
      return
    }

    eventSourceRef.current = eventSource

    eventSource.onmessage = (event) => {
      try {
        const statusUpdate = JSON.parse(event.data)
        setStatus(statusUpdate)
        setIsConnected(statusUpdate.status === 'healthy' || statusUpdate.status === 'running')
      } catch (err) {
        console.error('Failed to parse SSE message:', err)
      }
    }

    eventSource.onerror = (error) => {
      console.error('SSE connection error:', error)
      setIsConnected(false)
      eventSource.close()
      
      // Attempt to reconnect after 5 seconds
      reconnectTimeoutRef.current = setTimeout(() => {
        if (isConnected) {
          startRealTimeUpdates()
        }
      }, 5000)
    }
  }, [isConnected])

  /**
   * Stop real-time updates
   */
  const stopRealTimeUpdates = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
      eventSourceRef.current = null
    }
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }
  }, [])

  /**
   * Reconnect to daemon
   */
  const reconnect = useCallback(async () => {
    await httpLucidDaemonService.reconnect()
    await checkConnection()
    if (isConnected) {
      startRealTimeUpdates()
    }
  }, [isConnected, checkConnection, startRealTimeUpdates])

  // Initialize connection on mount
  useEffect(() => {
    checkConnection()
    loadTools()
    loadRAGStats()
  }, [checkConnection, loadTools, loadRAGStats])

  // Start real-time updates when connected
  useEffect(() => {
    if (isConnected) {
      startRealTimeUpdates()
    }
    
    return () => {
      stopRealTimeUpdates()
    }
  }, [isConnected, startRealTimeUpdates, stopRealTimeUpdates])

  return {
    isConnected,
    status,
    tools,
    ragStats,
    isLoading,
    error,
    checkConnection,
    loadTools,
    loadRAGStats,
    processRequest,
    startRealTimeUpdates,
    stopRealTimeUpdates,
    reconnect
  }
}

