/**
 * Lucid Daemon Service
 * Provides WebSocket communication with the Lucid Orchestrator daemon
 */

export interface SpecBlock {
  node_id: string
  responsibility: string
  must_never: string[]
  inputs: string[]
  outputs: string[]
  side_effects: string[]
  security_level: string
  perf_budget_ms: number
  status: string
  drift_reason?: string
  governance?: any
}

export interface BlueprintNode {
  node_id: string
  name: string
  kind: string
  status: string
  security_level?: string
}

export interface BlueprintEdge {
  node_id: string
  name: string
  kind: string
  status: string
  edge_type: string
  security_level?: string
}

export interface BlueprintSlice {
  center: BlueprintNode
  incoming: BlueprintEdge[]
  outgoing: BlueprintEdge[]
  blast_radius: {
    direct: number
    indirect: number
    risk_score: number
  }
}

export interface TimelineRun {
  timestamp: number
  duration_ms: number
  thread: string
  status: string
  violations: string[]
}

export interface TimelineCascade {
  symbol: string
  action: string
  duration_ms: number
  thread?: string
}

export interface TimelineSummary {
  node_id: string
  recent_runs: TimelineRun[]
  worst_run_cascade: TimelineCascade[]
}

export interface ChangeProposal {
  node_id: string
  blast_radius_summary: any
  affected_specs: any[]
  high_security_nodes: string[]
  risk_factors: string[]
  required_mitigations: string[]
  governance_template: any
}

class LucidDaemonService {
  private baseUrl: string
  private isConnected: boolean = false

  constructor(baseUrl: string = 'http://localhost:5000') {
    this.baseUrl = baseUrl
    this.checkConnection()
  }

  private connect() {
    try {
      this.ws = new WebSocket(this.url)
      
      this.ws.onopen = () => {
        console.log('Connected to Lucid Daemon')
        this.reconnectAttempts = 0
        this.processMessageQueue()
      }

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        this.handleReconnect()
      }

      this.ws.onclose = () => {
        console.log('Disconnected from Lucid Daemon')
        this.handleReconnect()
      }

      this.ws.onmessage = (event) => {
        try {
          const response = JSON.parse(event.data)
          this.handleResponse(response)
        } catch (error) {
          console.error('Failed to parse daemon response:', error)
        }
      }

    } catch (error) {
      console.error('Failed to connect to daemon:', error)
      this.handleReconnect()
    }
  }

  private handleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`)
      
      setTimeout(() => {
        this.connect()
      }, this.reconnectDelay * this.reconnectAttempts)
    } else {
      console.error('Max reconnection attempts reached')
    }
  }

  private processMessageQueue() {
    while (this.messageQueue.length > 0) {
      const { resolve, reject, request } = this.messageQueue.shift()!
      this.sendRequest(request).then(resolve).catch(reject)
    }
  }

  private handleResponse(response: any) {
    // Find the corresponding promise in the queue
    const messageIndex = this.messageQueue.findIndex(
      item => item.request.id === response.id
    )
    
    if (messageIndex !== -1) {
      const { resolve, reject } = this.messageQueue[messageIndex]
      this.messageQueue.splice(messageIndex, 1)
      
      if (response.error) {
        reject(new Error(response.error.message || 'Unknown error'))
      } else {
        resolve(response.result)
      }
    }
  }

  private async sendRequest(method: string, params: any = {}): Promise<any> {
    return new Promise((resolve, reject) => {
      if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
        // Queue the request if not connected
        const request = {
          jsonrpc: '2.0',
          id: Math.random().toString(36).substr(2, 9),
          method,
          params
        }
        this.messageQueue.push({ resolve, reject, request })
        return
      }

      const requestId = Math.random().toString(36).substr(2, 9)
      const request = {
        jsonrpc: '2.0',
        id: requestId,
        method: method,
        params: params
      }

      const timeout = setTimeout(() => {
        reject(new Error('Request timeout'))
      }, 10000)

      const messageHandler = (event: MessageEvent) => {
        try {
          const response = JSON.parse(event.data)
          if (response.id === requestId) {
            clearTimeout(timeout)
            this.ws?.removeEventListener('message', messageHandler)
            
            if (response.error) {
              reject(new Error(response.error.message || 'Unknown error'))
            } else {
              resolve(response.result)
            }
          }
        } catch (error) {
          // Ignore non-JSON messages
        }
      }

      this.ws.addEventListener('message', messageHandler)
      this.ws.send(JSON.stringify(request))
    })
  }

  // Mock data for development when daemon is not available
  private getMockSpecBlock(nodeId: string): SpecBlock {
    return {
      node_id: nodeId,
      responsibility: `Mock responsibility for ${nodeId}`,
      must_never: [
        'Mock constraint 1',
        'Mock constraint 2'
      ],
      inputs: ['input1', 'input2'],
      outputs: ['output1'],
      side_effects: ['side_effect1'],
      security_level: 'high',
      perf_budget_ms: 100,
      status: 'clean'
    }
  }

  private getMockBlueprintSlice(nodeId: string): BlueprintSlice {
    return {
      center: {
        node_id: nodeId,
        name: nodeId.split(':')[1] || 'unknown',
        kind: 'function',
        status: 'clean'
      },
      incoming: [],
      outgoing: [],
      blast_radius: {
        direct: 0,
        indirect: 0,
        risk_score: 0.0
      }
    }
  }

  private getMockTimelineSummary(nodeId: string): TimelineSummary {
    return {
      node_id: nodeId,
      recent_runs: [],
      worst_run_cascade: []
    }
  }

  private getMockChangeProposal(nodeId: string): ChangeProposal {
    return {
      node_id: nodeId,
      blast_radius_summary: { risk_score: 0.5 },
      affected_specs: [],
      high_security_nodes: [],
      risk_factors: [],
      required_mitigations: [],
      governance_template: {}
    }
  }

  async getSpecBlock(nodeId: string): Promise<SpecBlock> {
    try {
      return await this.sendRequest('getSpecBlock', { nodeId })
    } catch (error) {
      console.warn('Daemon unavailable, using mock data:', error)
      return this.getMockSpecBlock(nodeId)
    }
  }

  async getBlueprintSlice(nodeId: string, depth: number = 1): Promise<BlueprintSlice> {
    try {
      return await this.sendRequest('getBlueprintSlice', { nodeId, depth })
    } catch (error) {
      console.warn('Daemon unavailable, using mock data:', error)
      return this.getMockBlueprintSlice(nodeId)
    }
  }

  async getTimelineSummary(nodeId: string, limit: number = 10): Promise<TimelineSummary> {
    try {
      return await this.sendRequest('getTimelineSummary', { nodeId, limit })
    } catch (error) {
      console.warn('Daemon unavailable, using mock data:', error)
      return this.getMockTimelineSummary(nodeId)
    }
  }

  async proposeChange(nodeId: string): Promise<ChangeProposal> {
    try {
      return await this.sendRequest('proposeChange', { nodeId })
    } catch (error) {
      console.warn('Daemon unavailable, using mock data:', error)
      return this.getMockChangeProposal(nodeId)
    }
  }

  async focusNode(nodeId: string): Promise<any> {
    try {
      return await this.sendRequest('focusNode', { nodeId })
    } catch (error) {
      console.warn('Daemon unavailable, using mock data:', error)
      return { success: true, focused_node: nodeId }
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }
}

// Export singleton instance
export const lucidDaemonService = new LucidDaemonService()
export default LucidDaemonService
