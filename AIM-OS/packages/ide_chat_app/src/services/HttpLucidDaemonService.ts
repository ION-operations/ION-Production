/**
 * HTTP-based Lucid Daemon Service
 * Provides HTTP communication with the Lucid Orchestrator daemon
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

class HttpLucidDaemonService {
  private baseUrl: string
  private isConnected: boolean = false

  constructor(baseUrl: string = 'http://localhost:5000') {
    this.baseUrl = baseUrl
    this.checkConnection()
  }

  private async checkConnection(): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/api/health`)
      this.isConnected = response.ok
      if (this.isConnected) {
        console.log('Connected to Lucid Daemon')
      }
    } catch (error) {
      this.isConnected = false
      console.warn('Lucid Daemon not available, using mock data')
    }
  }

  private async makeRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        },
        ...options
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.warn(`Request to ${endpoint} failed:`, error)
      throw error
    }
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
      if (!this.isConnected) {
        return this.getMockSpecBlock(nodeId)
      }
      return await this.makeRequest<SpecBlock>(`/api/spec/${encodeURIComponent(nodeId)}`)
    } catch (error) {
      console.warn('Daemon unavailable, using mock data:', error)
      return this.getMockSpecBlock(nodeId)
    }
  }

  async getBlueprintSlice(nodeId: string, depth: number = 1): Promise<BlueprintSlice> {
    try {
      if (!this.isConnected) {
        return this.getMockBlueprintSlice(nodeId)
      }
      return await this.makeRequest<BlueprintSlice>(`/api/blueprint/${encodeURIComponent(nodeId)}?depth=${depth}`)
    } catch (error) {
      console.warn('Daemon unavailable, using mock data:', error)
      return this.getMockBlueprintSlice(nodeId)
    }
  }

  async getTimelineSummary(nodeId: string, limit: number = 10): Promise<TimelineSummary> {
    try {
      if (!this.isConnected) {
        return this.getMockTimelineSummary(nodeId)
      }
      return await this.makeRequest<TimelineSummary>(`/api/timeline/${encodeURIComponent(nodeId)}?limit=${limit}`)
    } catch (error) {
      console.warn('Daemon unavailable, using mock data:', error)
      return this.getMockTimelineSummary(nodeId)
    }
  }

  async proposeChange(nodeId: string): Promise<ChangeProposal> {
    try {
      if (!this.isConnected) {
        return this.getMockChangeProposal(nodeId)
      }
      return await this.makeRequest<ChangeProposal>(`/api/propose-change/${encodeURIComponent(nodeId)}`, {
        method: 'POST'
      })
    } catch (error) {
      console.warn('Daemon unavailable, using mock data:', error)
      return this.getMockChangeProposal(nodeId)
    }
  }

  async focusNode(nodeId: string): Promise<any> {
    try {
      if (!this.isConnected) {
        return { success: true, focused_node: nodeId }
      }
      return await this.makeRequest<any>(`/api/focus/${encodeURIComponent(nodeId)}`, {
        method: 'POST'
      })
    } catch (error) {
      console.warn('Daemon unavailable, using mock data:', error)
      return { success: true, focused_node: nodeId }
    }
  }

  async listNodes(): Promise<Array<{ node_id: string; name: string; kind: string }>> {
    try {
      if (!this.isConnected) {
        return [
          { node_id: 'example:function1', name: 'function1', kind: 'function' },
          { node_id: 'example:Component1', name: 'Component1', kind: 'reactComponent' }
        ]
      }
      return await this.makeRequest<Array<{ node_id: string; name: string; kind: string }>>('/api/nodes')
    } catch (error) {
      console.warn('Daemon unavailable, using mock data:', error)
      return [
        { node_id: 'example:function1', name: 'function1', kind: 'function' },
        { node_id: 'example:Component1', name: 'Component1', kind: 'reactComponent' }
      ]
    }
  }

  async healthCheck(): Promise<{ status: string; timestamp: string; focused_node?: string }> {
    try {
      return await this.makeRequest<{ status: string; timestamp: string; focused_node?: string }>('/api/health')
    } catch (error) {
      return {
        status: 'unavailable',
        timestamp: new Date().toISOString()
      }
    }
  }

  isDaemonConnected(): boolean {
    return this.isConnected
  }

  async reconnect(): Promise<void> {
    await this.checkConnection()
  }
}

// Export singleton instance
export const httpLucidDaemonService = new HttpLucidDaemonService()
export default HttpLucidDaemonService
