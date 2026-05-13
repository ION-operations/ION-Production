export const sampleCode = `/**
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

export interface TimelineSummary {
  node_id: string
  recent_runs: TimelineRun[]
  worst_run_cascade: any[]
}

export interface ChangeProposal {
  node_id: string
  blast_radius: any
  risk_assessment: any
  required_mitigations: string[]
  governance_template: any
}

export class HttpLucidDaemonService {
  private baseUrl: string = 'http://localhost:5000/api'

  async getSpecBlock(nodeId: string): Promise<SpecBlock> {
    const response = await fetch(\`\${this.baseUrl}/spec/\${nodeId}\`)
    if (!response.ok) {
      throw new Error(\`Failed to fetch spec block: \${response.statusText}\`)
    }
    return response.json()
  }

  async getBlueprintSlice(nodeId: string, depth: number = 1): Promise<BlueprintSlice> {
    const response = await fetch(\`\${this.baseUrl}/blueprint/\${nodeId}?depth=\${depth}\`)
    if (!response.ok) {
      throw new Error(\`Failed to fetch blueprint slice: \${response.statusText}\`)
    }
    return response.json()
  }

  async getTimelineSummary(nodeId: string, limit: number = 10): Promise<TimelineSummary> {
    const response = await fetch(\`\${this.baseUrl}/timeline/\${nodeId}?limit=\${limit}\`)
    if (!response.ok) {
      throw new Error(\`Failed to fetch timeline summary: \${response.statusText}\`)
    }
    return response.json()
  }

  async proposeChange(nodeId: string): Promise<ChangeProposal> {
    const response = await fetch(\`\${this.baseUrl}/propose-change/\${nodeId}\`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    })
    if (!response.ok) {
      throw new Error(\`Failed to propose change: \${response.statusText}\`)
    }
    return response.json()
  }

  async focusNode(nodeId: string): Promise<void> {
    const response = await fetch(\`\${this.baseUrl}/focus/\${nodeId}\`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    })
    if (!response.ok) {
      throw new Error(\`Failed to focus node: \${response.statusText}\`)
    }
  }

  isDaemonConnected(): boolean {
    // Simple check - in production this would ping the health endpoint
    return true
  }
}

export const httpLucidDaemonService = new HttpLucidDaemonService()`