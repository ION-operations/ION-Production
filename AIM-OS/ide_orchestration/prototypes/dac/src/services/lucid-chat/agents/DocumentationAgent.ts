/**
 * Documentation Agent
 * 
 * Specialized agent for writing documentation
 * 
 * Epic 2.3: Multi-Agent Orchestration
 */

import { BaseAgent, AgentTask, AgentTaskResult } from './BaseAgent'
import { LLMService } from '../llm/LLMService'

export class DocumentationAgent extends BaseAgent {
  constructor(llmService: LLMService, commandServerUrl?: string) {
    super(
      'agent_documentation',
      'Documentation Agent',
      'Writes comprehensive documentation',
      ['documentation', 'implementation'],
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
        `Write comprehensive documentation for:
${task.description}

${task.input?.code ? `Code:\n${task.input.code}\n\n` : ''}
${task.input?.context ? `Context:\n${task.input.context}\n\n` : ''}

Include:
1. Overview
2. Usage examples
3. API reference
4. Best practices
5. Common pitfalls
6. Related resources`,
        this.provider,
        this.model,
        0.4,
        4000
      )

      this.setStatus('idle')

      if (!response.success || !response.data) {
        return {
          taskId: task.id,
          success: false,
          error: 'Documentation generation failed',
          metadata: { duration: Date.now() - startTime },
        }
      }

      const qualityScore = response.data.confidence || 0.8
      this.recordCompletion(qualityScore)

      const taskResult: AgentTaskResult = {
        taskId: task.id,
        success: true,
        output: {
          documentation: response.data.text,
          format: 'markdown',
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

