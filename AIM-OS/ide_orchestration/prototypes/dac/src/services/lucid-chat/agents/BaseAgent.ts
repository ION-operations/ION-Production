/**
 * Base Agent Class
 * 
 * Foundation for specialized AI agents that can collaborate
 * 
 * Epic 2.3: Multi-Agent Orchestration
 */

import { LLMService, LLMProvider } from '../llm/LLMService'
import { APIResponse } from '../base/BaseAPIService'

/**
 * Agent Capability
 */
export type AgentCapability = 
  | 'research'
  | 'testing'
  | 'review'
  | 'documentation'
  | 'implementation'
  | 'analysis'
  | 'planning'
  | 'verification'

/**
 * Agent Status
 */
export type AgentStatus = 'idle' | 'busy' | 'error' | 'offline'

/**
 * Agent Task
 */
export interface AgentTask {
  id: string
  type: string
  description: string
  input: any
  priority?: number
  deadline?: Date
  requester?: string
}

/**
 * Agent Task Result
 */
export interface AgentTaskResult {
  taskId: string
  success: boolean
  output?: any
  error?: string
  metadata?: {
    duration: number
    tokensUsed?: number
    confidence?: number
  }
}

/**
 * Agent Profile
 */
export interface AgentProfile {
  id: string
  name: string
  description: string
  capabilities: AgentCapability[]
  provider: LLMProvider
  model?: string
  status: AgentStatus
  metadata?: {
    tasksCompleted?: number
    averageQuality?: number
    specialization?: string
  }
}

/**
 * Base Agent Implementation
 */
export abstract class BaseAgent {
  protected id: string
  protected name: string
  protected description: string
  protected capabilities: AgentCapability[]
  protected provider: LLMProvider
  protected model?: string
  protected status: AgentStatus = 'idle'
  protected llmService: LLMService
  protected commandServerUrl: string
  protected tasksCompleted: number = 0
  protected qualityScores: number[] = []

  constructor(
    id: string,
    name: string,
    description: string,
    capabilities: AgentCapability[],
    llmService: LLMService,
    provider: LLMProvider = 'anthropic',
    model?: string,
    commandServerUrl: string = 'http://localhost:5001'
  ) {
    this.id = id
    this.name = name
    this.description = description
    this.capabilities = capabilities
    this.provider = provider
    this.model = model
    this.llmService = llmService
    this.commandServerUrl = commandServerUrl
  }

  /**
   * Get agent profile
   */
  getProfile(): AgentProfile {
    return {
      id: this.id,
      name: this.name,
      description: this.description,
      capabilities: this.capabilities,
      provider: this.provider,
      model: this.model,
      status: this.status,
      metadata: {
        tasksCompleted: this.tasksCompleted,
        averageQuality: this.calculateAverageQuality(),
        specialization: this.capabilities[0],
      },
    }
  }

  /**
   * Check if agent can handle task
   */
  canHandle(task: AgentTask): boolean {
    // Override in subclass for more sophisticated matching
    return this.status === 'idle' || this.status === 'busy'
  }

  /**
   * Execute task (abstract - implement in subclass)
   */
  abstract executeTask(task: AgentTask): Promise<AgentTaskResult>

  /**
   * Update agent status
   */
  protected setStatus(status: AgentStatus): void {
    this.status = status
  }

  /**
   * Record task completion
   */
  protected recordCompletion(qualityScore: number): void {
    this.tasksCompleted++
    this.qualityScores.push(qualityScore)
    
    // Keep only last 10 scores
    if (this.qualityScores.length > 10) {
      this.qualityScores.shift()
    }
  }

  /**
   * Calculate average quality
   */
  private calculateAverageQuality(): number {
    if (this.qualityScores.length === 0) return 0
    
    const sum = this.qualityScores.reduce((a, b) => a + b, 0)
    return sum / this.qualityScores.length
  }

  /**
   * Store task result in CMC
   */
  protected async storeTaskResult(task: AgentTask, result: AgentTaskResult): Promise<void> {
    try {
      await fetch(`${this.commandServerUrl}/mcp/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tool: 'store_memory',
          arguments: {
            content: JSON.stringify({
              agent: this.name,
              task: task.description,
              result: result.output,
              success: result.success,
            }),
            memory_type: 'agent_task',
            tags: ['agent', this.name, task.type],
            metadata: {
              agent_id: this.id,
              task_id: task.id,
              timestamp: new Date().toISOString(),
            },
          },
        }),
      })
    } catch (error) {
      console.warn(`[${this.name}] Failed to store task result:`, error)
    }
  }
}

