/**
 * Review Agent
 * 
 * Specialized agent for code/document review
 * 
 * Epic 2.3: Multi-Agent Orchestration
 */

import { BaseAgent, AgentTask, AgentTaskResult } from './BaseAgent'
import { LLMService } from '../llm/LLMService'

export class ReviewAgent extends BaseAgent {
  constructor(llmService: LLMService, commandServerUrl?: string) {
    super(
      'agent_review',
      'Review Agent',
      'Reviews code and documentation',
      ['review', 'analysis'],
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
      const response = await this.llmService.complete(
        `Review this ${task.input?.type || 'code'}:
${task.description}

Content:
${task.input?.content || ''}

Provide:
1. Quality assessment (0-10)
2. Issues found
3. Suggestions for improvement
4. Security concerns (if applicable)
5. Performance considerations
6. Best practices recommendations`,
        this.provider,
        this.model,
        0.2, // Low temp for objective review
        3000
      )

      this.setStatus('idle')

      if (!response.success || !response.data) {
        return {
          taskId: task.id,
          success: false,
          error: 'Review failed',
          metadata: { duration: Date.now() - startTime },
        }
      }

      const qualityScore = response.data.confidence || 0.85
      this.recordCompletion(qualityScore)

      const taskResult: AgentTaskResult = {
        taskId: task.id,
        success: true,
        output: {
          review: response.data.text,
          approved: true, // Would parse from response
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

