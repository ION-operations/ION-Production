/**
 * Multi-Agent Orchestrator
 * 
 * Coordinates multiple AI agents working together
 * 
 * Epic 2.3: Multi-Agent Orchestration
 */

import { BaseAgent, AgentTask, AgentTaskResult } from './BaseAgent'
import { AgentRegistry, getAgentRegistry } from './AgentRegistry'
import { APIResponse } from '../base/BaseAPIService'

/**
 * Collaboration Strategy
 */
export type CollaborationStrategy = 'parallel' | 'sequential' | 'pipeline' | 'voting'

/**
 * Multi-Agent Task
 */
export interface MultiAgentTask {
  id: string
  description: string
  subtasks: AgentTask[]
  strategy: CollaborationStrategy
  timeout?: number
}

/**
 * Multi-Agent Result
 */
export interface MultiAgentResult {
  taskId: string
  success: boolean
  results: AgentTaskResult[]
  synthesis?: any
  metadata: {
    duration: number
    agentsUsed: number
    totalTokens: number
  }
}

/**
 * Multi-Agent Orchestrator Implementation
 */
export class MultiAgentOrchestrator {
  private registry: AgentRegistry
  private commandServerUrl: string

  constructor(commandServerUrl: string = 'http://localhost:5001') {
    this.registry = getAgentRegistry()
    this.commandServerUrl = commandServerUrl
  }

  /**
   * Execute multi-agent task
   */
  async execute(task: MultiAgentTask): Promise<APIResponse<MultiAgentResult>> {
    const startTime = Date.now()

    try {
      let results: AgentTaskResult[]

      switch (task.strategy) {
        case 'parallel':
          results = await this.executeParallel(task.subtasks)
          break
        case 'sequential':
          results = await this.executeSequential(task.subtasks)
          break
        case 'pipeline':
          results = await this.executePipeline(task.subtasks)
          break
        case 'voting':
          results = await this.executeVoting(task.subtasks)
          break
        default:
          throw new Error(`Unknown strategy: ${task.strategy}`)
      }

      // Synthesize results if needed
      const synthesis = await this.synthesizeResults(results)

      const result: MultiAgentResult = {
        taskId: task.id,
        success: results.every(r => r.success),
        results,
        synthesis,
        metadata: {
          duration: Date.now() - startTime,
          agentsUsed: results.length,
          totalTokens: results.reduce(
            (sum, r) => sum + (r.metadata?.tokensUsed || 0),
            0
          ),
        },
      }

      return {
        success: true,
        data: result,
      }
    } catch (error: any) {
      return {
        success: false,
        error: error.message,
      }
    }
  }

  /**
   * Execute tasks in parallel
   */
  private async executeParallel(tasks: AgentTask[]): Promise<AgentTaskResult[]> {
    const promises = tasks.map(task => {
      const agent = this.registry.findBestAgent(task)
      if (!agent) {
        return Promise.resolve({
          taskId: task.id,
          success: false,
          error: 'No suitable agent found',
        } as AgentTaskResult)
      }
      return agent.executeTask(task)
    })

    return Promise.all(promises)
  }

  /**
   * Execute tasks sequentially
   */
  private async executeSequential(tasks: AgentTask[]): Promise<AgentTaskResult[]> {
    const results: AgentTaskResult[] = []

    for (const task of tasks) {
      const agent = this.registry.findBestAgent(task)
      if (!agent) {
        results.push({
          taskId: task.id,
          success: false,
          error: 'No suitable agent found',
        } as AgentTaskResult)
        continue
      }

      const result = await agent.executeTask(task)
      results.push(result)

      // Stop if task failed
      if (!result.success) {
        break
      }
    }

    return results
  }

  /**
   * Execute tasks as pipeline (output of one feeds next)
   */
  private async executePipeline(tasks: AgentTask[]): Promise<AgentTaskResult[]> {
    const results: AgentTaskResult[] = []
    let previousOutput: any = null

    for (const task of tasks) {
      // Feed previous output as input
      if (previousOutput) {
        task.input = { ...task.input, previousOutput }
      }

      const agent = this.registry.findBestAgent(task)
      if (!agent) {
        results.push({
          taskId: task.id,
          success: false,
          error: 'No suitable agent found',
        } as AgentTaskResult)
        break
      }

      const result = await agent.executeTask(task)
      results.push(result)

      if (!result.success) {
        break
      }

      previousOutput = result.output
    }

    return results
  }

  /**
   * Execute same task with multiple agents and vote on best result
   */
  private async executeVoting(tasks: AgentTask[]): Promise<AgentTaskResult[]> {
    // All tasks should be the same for voting
    const task = tasks[0]

    // Execute with multiple agents
    const agents = this.registry.getAllAgents().slice(0, 3) // Use up to 3 agents

    const results = await Promise.all(
      agents.map(agent => agent.executeTask(task))
    )

    // Vote on best result (highest confidence)
    const bestResult = results.reduce((best, current) => {
      const bestConf = best.metadata?.confidence || 0
      const currentConf = current.metadata?.confidence || 0
      return currentConf > bestConf ? current : best
    })

    return [bestResult]
  }

  /**
   * Synthesize results from multiple agents
   */
  private async synthesizeResults(results: AgentTaskResult[]): Promise<any> {
    try {
      const response = await fetch(`${this.commandServerUrl}/mcp/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tool: 'synthesize_knowledge',
          arguments: {
            topics: results.map(r => JSON.stringify(r.output)).slice(0, 5),
            depth: 'medium',
            format: 'summary',
          },
        }),
      })

      const result = await response.json()
      if (result.success && result.data) {
        return result.data
      }
    } catch (error) {
      console.warn('[MultiAgent] Synthesis failed:', error)
    }

    return {
      summary: `Completed ${results.length} tasks`,
      successRate: results.filter(r => r.success).length / results.length,
    }
  }

  /**
   * Get orchestrator statistics
   */
  getStats(): any {
    return {
      registry: this.registry.getStats(),
      strategies: ['parallel', 'sequential', 'pipeline', 'voting'],
    }
  }
}

// Singleton instance
let orchestratorInstance: MultiAgentOrchestrator | null = null

export function getMultiAgentOrchestrator(
  commandServerUrl?: string
): MultiAgentOrchestrator {
  if (!orchestratorInstance) {
    orchestratorInstance = new MultiAgentOrchestrator(commandServerUrl)
  }
  return orchestratorInstance
}

