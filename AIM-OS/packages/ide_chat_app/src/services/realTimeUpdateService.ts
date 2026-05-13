// Real-Time Updates Service
// WebSocket integration for live AIM-OS updates
// V2 Enhancement - Week 1 Foundation

import { useState, useEffect } from 'react'
import { getMCPAPI } from './mcpApi'

export interface RealTimeUpdate {
  type: 'consciousness' | 'timeline' | 'goals' | 'memory' | 'performance' | 'evidence' | 'confidence'
  data: any
  timestamp: Date
}

type UpdateCallback = (update: RealTimeUpdate) => void

export class RealTimeUpdateService {
  private ws: WebSocket | null = null
  private callbacks: Map<string, UpdateCallback[]> = new Map()
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 5000
  private pollingInterval: number | null = null
  private usePolling = false

  constructor() {
    // Try WebSocket first, fallback to polling
    this.connect()
  }

  /**
   * Connect to WebSocket or start polling
   */
  private connect(): void {
    try {
      // Try WebSocket connection
      const wsUrl = 'ws://localhost:5001/updates'
      this.ws = new WebSocket(wsUrl)

      this.ws.onopen = () => {
        console.log('[RealTimeUpdates] WebSocket connected')
        this.reconnectAttempts = 0
        this.usePolling = false
        if (this.pollingInterval) {
          clearInterval(this.pollingInterval)
          this.pollingInterval = null
        }
      }

      this.ws.onmessage = (event) => {
        try {
          const update: RealTimeUpdate = JSON.parse(event.data)
          this.notifyCallbacks(update.type, update)
        } catch (error) {
          console.error('[RealTimeUpdates] Failed to parse WebSocket message:', error)
        }
      }

      this.ws.onerror = (error) => {
        console.warn('[RealTimeUpdates] WebSocket error, falling back to polling:', error)
        this.usePolling = true
        this.startPolling()
      }

      this.ws.onclose = () => {
        console.log('[RealTimeUpdates] WebSocket closed')
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectAttempts++
          setTimeout(() => this.connect(), this.reconnectDelay)
        } else {
          console.warn('[RealTimeUpdates] Max reconnect attempts reached, using polling')
          this.usePolling = true
          this.startPolling()
        }
      }
    } catch (error) {
      console.warn('[RealTimeUpdates] WebSocket not available, using polling:', error)
      this.usePolling = true
      this.startPolling()
    }
  }

  /**
   * Start polling as fallback
   */
  private startPolling(): void {
    if (this.pollingInterval) return

    this.pollingInterval = window.setInterval(async () => {
      try {
        const mcpApi = getMCPAPI()
        
        // Poll consciousness metrics
        const consciousnessResponse = await mcpApi.executeTool('get_consciousness_metrics', {})
        if (consciousnessResponse.success) {
          this.notifyCallbacks('consciousness', {
            type: 'consciousness',
            data: consciousnessResponse.result,
            timestamp: new Date()
          })
        }

        // Poll timeline entries
        const timelineResponse = await mcpApi.executeTool('get_timeline_entries', { limit: 5 })
        if (timelineResponse.success) {
          this.notifyCallbacks('timeline', {
            type: 'timeline',
            data: timelineResponse.result,
            timestamp: new Date()
          })
        }

        // Poll goals
        const goalsResponse = await mcpApi.executeTool('query_goal_timeline', { status: 'in_progress', limit: 5 })
        if (goalsResponse.success) {
          this.notifyCallbacks('goals', {
            type: 'goals',
            data: goalsResponse.result,
            timestamp: new Date()
          })
        }

        // Poll memory stats
        const memoryResponse = await mcpApi.executeTool('get_memory_stats', {})
        if (memoryResponse.success) {
          this.notifyCallbacks('memory', {
            type: 'memory',
            data: memoryResponse.result,
            timestamp: new Date()
          })
        }

        // Poll performance metrics (if available)
        if (typeof performance !== 'undefined' && (performance as any).memory) {
          const perfData = {
            memoryUsage: (performance as any).memory.usedJSHeapSize / 1024 / 1024,
            memoryLimit: (performance as any).memory.jsHeapSizeLimit / 1024 / 1024,
            timestamp: new Date()
          }
          this.notifyCallbacks('performance', {
            type: 'performance',
            data: perfData,
            timestamp: new Date()
          })
        }
      } catch (error) {
        console.error('[RealTimeUpdates] Polling error:', error)
      }
    }, 5000) // Poll every 5 seconds
  }

  /**
   * Subscribe to updates
   */
  subscribe(type: RealTimeUpdate['type'], callback: UpdateCallback): () => void {
    if (!this.callbacks.has(type)) {
      this.callbacks.set(type, [])
    }
    this.callbacks.get(type)!.push(callback)

    // Return unsubscribe function
    return () => {
      const callbacks = this.callbacks.get(type)
      if (callbacks) {
        const index = callbacks.indexOf(callback)
        if (index > -1) {
          callbacks.splice(index, 1)
        }
      }
    }
  }

  /**
   * Notify all callbacks for a type
   */
  private notifyCallbacks(type: RealTimeUpdate['type'], update: RealTimeUpdate): void {
    const callbacks = this.callbacks.get(type) || []
    callbacks.forEach(callback => {
      try {
        callback(update)
      } catch (error) {
        console.error('[RealTimeUpdates] Callback error:', error)
      }
    })
  }

  /**
   * Check connection status
   */
  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN || this.usePolling
  }

  /**
   * Disconnect
   */
  disconnect(): void {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval)
      this.pollingInterval = null
    }
    this.callbacks.clear()
  }
}

// Singleton instance
let realTimeUpdateServiceInstance: RealTimeUpdateService | null = null

export function getRealTimeUpdateService(): RealTimeUpdateService {
  if (!realTimeUpdateServiceInstance) {
    realTimeUpdateServiceInstance = new RealTimeUpdateService()
  }
  return realTimeUpdateServiceInstance
}

// React hook for real-time updates
export function useRealTimeUpdates(type: RealTimeUpdate['type']) {
  const [update, setUpdate] = useState<RealTimeUpdate | null>(null)
  const [connected, setConnected] = useState(false)

  useEffect(() => {
    const service = getRealTimeUpdateService()
    setConnected(service.isConnected())

    const unsubscribe = service.subscribe(type, (update) => {
      setUpdate(update)
    })

    return () => {
      unsubscribe()
    }
  }, [type])

  return { update, connected }
}

