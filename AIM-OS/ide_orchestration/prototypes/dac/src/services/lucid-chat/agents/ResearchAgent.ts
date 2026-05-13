/**
 * Research Agent
 * 
 * Specialized agent for conducting research using ARD
 * 
 * Epic 2.3: Multi-Agent Orchestration
 */

import { BaseAgent, AgentTask, AgentTaskResult } from './BaseAgent'
import { LLMService } from '../llm/LLMService'
import { getARDService } from '../research/ARDService'

/**
 * Research Agent Implementation
 */
export class ResearchAgent extends BaseAgent {
  constructor(llmService: LLMService, commandServerUrl?: string) {
    super(
      'agent_research',
      'Research Agent',
      'Conducts autonomous research using ARD',
      ['research', 'analysis'],
      llmService,
      'anthropic',
      'claude-3-5-sonnet-20241022',
      commandServerUrl
    )
  }

  async executeTask(task: AgentTask): Promise<AgentTaskResult> {
    this.setStatus('busy')
    const startTime = Date.now()

    try {
      const ardService = getARDService(this.commandServerUrl)

      const result = await ardService.conductResearch({
        topic: {
          topic: task.description,
          context: task.input?.context,
          goals: task.input?.goals,
        },
        depth: task.input?.depth || 'standard',
        enableWebSearch: true,
        enableCodeSearch: true,
        enableDocumentSearch: true,
        generateImprovements: task.input?.generateImprovements ?? true,
        recursiveDepth: task.input?.recursiveDepth || 1,
      })

      this.setStatus('idle')

      if (!result.success || !result.data) {
        return {
          taskId: task.id,
          success: false,
          error: result.error || 'Research failed',
          metadata: {
            duration: Date.now() - startTime,
          },
        }
      }

      const qualityScore = result.data.metadata.trustScore
      this.recordCompletion(qualityScore)

      const taskResult: AgentTaskResult = {
        taskId: task.id,
        success: true,
        output: result.data,
        metadata: {
          duration: Date.now() - startTime,
          confidence: qualityScore,
        },
      }

      await this.storeTaskResult(task, taskResult)

      return taskResult
    } catch (error: any) {
      this.setStatus('error')
      return {
        taskId: task.id,
        success: false,
        error: error.message,
        metadata: {
          duration: Date.now() - startTime,
        },
      }
    }
  }
}

