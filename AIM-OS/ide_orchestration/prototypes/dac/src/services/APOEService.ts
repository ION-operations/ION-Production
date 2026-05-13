/**
 * APOE Service
 * Handles plan creation and execution monitoring via MCP tools
 */

const COMMAND_SERVER_URL = 'http://localhost:5001'

export interface ExecutionPlan {
  plan_id: string
  goal: string
  steps: Array<{
    id: string
    name: string
    description: string
    role: string
    dependencies?: string[]
  }>
  metadata?: Record<string, any>
}

export interface PlanExecutionStatus {
  plan_id: string
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
  progress: number // 0-100
  current_step?: string
  completed_steps: number
  total_steps: number
  started_at?: string
  completed_at?: string
  error?: string
  results?: Record<string, any>
}

/**
 * APOE Service
 * Integrates with MCP tools for plan creation and execution
 */
export class APOEService {
  private commandServerUrl: string
  private executionStatuses: Map<string, PlanExecutionStatus> = new Map()

  constructor(commandServerUrl: string = COMMAND_SERVER_URL) {
    this.commandServerUrl = commandServerUrl
  }

  /**
   * Create an execution plan via APOE
   */
  async createPlan(
    goal: string,
    context: string = '',
    priority: 'low' | 'medium' | 'high' | 'critical' = 'medium'
  ): Promise<{ success: boolean; plan?: ExecutionPlan; error?: string }> {
    try {
      const response = await fetch(`${this.commandServerUrl}/mcp/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          tool: 'mcp_lucid-mcp_create_plan',
          arguments: {
            goal,
            context,
            priority
          }
        })
      })

      if (!response.ok) {
        throw new Error(`Command Server error: ${response.status} ${response.statusText}`)
      }

      const data = await response.json()
      
      if (data.success && data.plan) {
        return {
          success: true,
          plan: {
            plan_id: data.plan.plan_id || data.plan_id || `plan_${Date.now()}`,
            goal: data.plan.goal || goal,
            steps: data.plan.steps || [],
            metadata: data.plan.metadata || {}
          }
        }
      } else {
        return {
          success: false,
          error: data.error || 'Failed to create plan'
        }
      }
    } catch (error) {
      console.error('APOE create plan error:', error)
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      }
    }
  }

  /**
   * Execute a plan (via prompt chain execution)
   */
  async executePlan(
    planId: string,
    inputs: Record<string, any> = {},
    context: Record<string, any> = {}
  ): Promise<{ success: boolean; execution_id?: string; error?: string }> {
    try {
      // Initialize execution status
      const status: PlanExecutionStatus = {
        plan_id: planId,
        status: 'running',
        progress: 0,
        completed_steps: 0,
        total_steps: 0,
        started_at: new Date().toISOString()
      }
      this.executionStatuses.set(planId, status)

      // Execute plan via prompt chain (if plan is stored as a chain)
      // For now, we'll simulate execution progress
      const response = await fetch(`${this.commandServerUrl}/mcp/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          tool: 'mcp_lucid-mcp_execute_prompt_chain',
          arguments: {
            chain_id: planId,
            inputs,
            context
          }
        })
      })

      if (!response.ok) {
        throw new Error(`Command Server error: ${response.status} ${response.statusText}`)
      }

      const data = await response.json()
      
      if (data.success) {
        status.status = 'completed'
        status.progress = 100
        status.completed_at = new Date().toISOString()
        status.results = data.results || {}
        this.executionStatuses.set(planId, status)
        
        return {
          success: true,
          execution_id: data.execution_id || data.chain_instance_id || `exec_${Date.now()}`
        }
      } else {
        status.status = 'failed'
        status.error = data.error || 'Execution failed'
        this.executionStatuses.set(planId, status)
        
        return {
          success: false,
          error: data.error || 'Execution failed'
        }
      }
    } catch (error) {
      console.error('APOE execute plan error:', error)
      const status = this.executionStatuses.get(planId)
      if (status) {
        status.status = 'failed'
        status.error = error instanceof Error ? error.message : 'Unknown error'
        this.executionStatuses.set(planId, status)
      }
      
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      }
    }
  }

  /**
   * Get plan execution status
   */
  getPlanStatus(planId: string): PlanExecutionStatus | null {
    return this.executionStatuses.get(planId) || null
  }

  /**
   * Monitor plan execution progress
   */
  async monitorPlanExecution(
    planId: string,
    onProgress?: (status: PlanExecutionStatus) => void
  ): Promise<PlanExecutionStatus> {
    const status = this.executionStatuses.get(planId)
    if (!status) {
      // Initialize status if not exists
      const newStatus: PlanExecutionStatus = {
        plan_id: planId,
        status: 'pending',
        progress: 0,
        completed_steps: 0,
        total_steps: 0
      }
      this.executionStatuses.set(planId, newStatus)
      return newStatus
    }

    // Update progress based on current status
    if (status.status === 'running') {
      // Simulate progress (in real implementation, this would query execution state)
      if (status.total_steps > 0) {
        status.progress = Math.min(100, (status.completed_steps / status.total_steps) * 100)
      } else {
        // Estimate progress if total steps unknown
        status.progress = Math.min(95, status.progress + 5)
      }
    }

    if (onProgress) {
      onProgress(status)
    }

    return status
  }

  /**
   * Update plan execution status
   */
  updatePlanStatus(planId: string, updates: Partial<PlanExecutionStatus>): void {
    const status = this.executionStatuses.get(planId)
    if (status) {
      Object.assign(status, updates)
      this.executionStatuses.set(planId, status)
    }
  }
}

// Singleton instance
export const apoeService = new APOEService()

