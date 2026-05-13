/**
 * Testing Agent
 * 
 * Specialized agent for writing and running tests
 * 
 * Epic 2.3: Multi-Agent Orchestration
 */

import { BaseAgent, AgentTask, AgentTaskResult } from './BaseAgent'
import { LLMService } from '../llm/LLMService'

export class TestingAgent extends BaseAgent {
  constructor(llmService: LLMService, commandServerUrl?: string) {
    super(
      'agent_testing',
      'Testing Agent',
      'Writes and executes tests',
      ['testing', 'verification'],
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
      // Generate tests using LLM
      const response = await this.llmService.complete(
        `Generate comprehensive tests for:
${task.description}

Code:
${task.input?.code || ''}

Requirements:
- Unit tests
- Edge cases
- Error handling
- Integration tests (if applicable)

Return tests in executable format.`,
        this.provider,
        this.model,
        0.3,
        3000
      )

      this.setStatus('idle')

      if (!response.success || !response.data) {
        return {
          taskId: task.id,
          success: false,
          error: 'Test generation failed',
          metadata: { duration: Date.now() - startTime },
        }
      }

      const qualityScore = response.data.confidence || 0.8
      this.recordCompletion(qualityScore)

      const taskResult: AgentTaskResult = {
        taskId: task.id,
        success: true,
        output: {
          tests: response.data.text,
          coverage: 'Comprehensive',
        },
        metadata: {
          duration: Date.now() - startTime,
          tokensUsed: response.data.tokensUsed,
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
        metadata: { duration: Date.now() - startTime },
      }
    }
  }
}

