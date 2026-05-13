/**
 * Integration Tests: Budget Integration
 * 
 * Tests for budget tracking in workflows
 */

import { describe, it, expect, beforeEach } from 'vitest'
import { WorkflowExecutor, WorkflowConfig } from '@services/lucid-chat/orchestration'
import { LLMService } from '@services/lucid-chat/llm/LLMService'
import { BudgetTracker } from '@services/lucid-chat/orchestration'
import { createMockCommandServer } from '../../__mocks__/mockCommandServer'

describe('Budget Integration', () => {
  let workflowExecutor: WorkflowExecutor
  let llmService: LLMService
  let mockServer: ReturnType<typeof createMockCommandServer>

  beforeEach(() => {
    mockServer = createMockCommandServer()
    global.fetch = mockServer.mockFetch as any
    llmService = new LLMService('http://localhost:5001')
    workflowExecutor = new WorkflowExecutor(llmService, 'http://localhost:5001')
  })

  describe('budget tracking in workflow', () => {
    it('should track tokens during workflow', async () => {
      mockServer.setResponse('call_api', {
        success: true,
        data: {
          content: 'Test response',
          model: 'gpt-3.5-turbo'
        }
      })

      const config: WorkflowConfig = {
        id: 'workflow-1',
        goal: 'Budget tracking',
        plan: {
          steps: [
            {
              id: 'step-1',
              role: 'reasoner',
              task: 'Test task',
              dependencies: []
            }
          ]
        },
        budget: {
          tokens: 1000
        },
        parallelExecution: false
      }

      const result = await workflowExecutor.execute(config)

      expect(result.budget_status).toBeDefined()
      expect(result.budget_status.usage.tokens).toBeGreaterThan(0)
      expect(result.total_tokens).toBeGreaterThan(0)
    })

    it('should track cost during workflow', async () => {
      mockServer.setResponse('call_api', {
        success: true,
        data: {
          content: 'Test response',
          model: 'gpt-3.5-turbo'
        }
      })

      const config: WorkflowConfig = {
        id: 'workflow-2',
        goal: 'Cost tracking',
        plan: {
          steps: [
            {
              id: 'step-1',
              role: 'reasoner',
              task: 'Test task',
              dependencies: []
            }
          ]
        },
        budget: {
          cost: 1.0
        },
        parallelExecution: false
      }

      const result = await workflowExecutor.execute(config)

      expect(result.budget_status).toBeDefined()
      expect(result.budget_status.usage.cost).toBeGreaterThan(0)
      expect(result.total_cost).toBeGreaterThan(0)
    })

    it('should track time during workflow', async () => {
      mockServer.setResponse('call_api', {
        success: true,
        data: {
          content: 'Test response',
          model: 'gpt-3.5-turbo'
        }
      })

      const config: WorkflowConfig = {
        id: 'workflow-3',
        goal: 'Time tracking',
        plan: {
          steps: [
            {
              id: 'step-1',
              role: 'reasoner',
              task: 'Test task',
              dependencies: []
            }
          ]
        },
        budget: {
          time: 60
        },
        parallelExecution: false
      }

      const result = await workflowExecutor.execute(config)

      expect(result.budget_status).toBeDefined()
      expect(result.budget_status.usage.time).toBeGreaterThan(0)
      expect(result.total_time).toBeGreaterThan(0)
    })
  })

  describe('budget exceeded handling', () => {
    it('should stop workflow when token budget exceeded', async () => {
      mockServer.setResponse('call_api', {
        success: true,
        data: {
          content: 'Test response',
          model: 'gpt-3.5-turbo'
        }
      })

      const config: WorkflowConfig = {
        id: 'workflow-4',
        goal: 'Budget exceeded',
        plan: {
          steps: [
            {
              id: 'step-1',
              role: 'reasoner',
              task: 'Test task',
              dependencies: []
            }
          ]
        },
        budget: {
          tokens: 0 // Zero budget
        },
        parallelExecution: false
      }

      const result = await workflowExecutor.execute(config)

      expect(result.success).toBe(false)
      expect(result.error).toContain('Budget exceeded')
    })
  })

  describe('warning generation', () => {
    it('should generate warnings at 80% threshold', async () => {
      mockServer.setResponse('call_api', {
        success: true,
        data: {
          content: 'Test response',
          model: 'gpt-3.5-turbo'
        }
      })

      const budgetTracker = new BudgetTracker({ tokens: 100 })

      // Mock step with high token usage
      const step = {
        success: true,
        confidence: 0.8,
        tokensUsed: 85, // 85% of 100
        latencyMs: 1000,
        model: 'gpt-3.5-turbo'
      } as any

      budgetTracker.trackStep(step)
      const status = budgetTracker.getStatus()

      expect(status.warnings.length).toBeGreaterThan(0)
      expect(status.warnings.some(w => w.includes('80'))).toBe(true)
    })
  })

  describe('budget reset', () => {
    it('should reset budget tracker', async () => {
      const budgetTracker = new BudgetTracker({ tokens: 1000 })

      const step = {
        success: true,
        confidence: 0.8,
        tokensUsed: 500,
        latencyMs: 1000,
        model: 'gpt-3.5-turbo'
      } as any

      budgetTracker.trackStep(step)
      expect(budgetTracker.getStatus().usage.tokens).toBe(500)

      budgetTracker.reset()
      expect(budgetTracker.getStatus().usage.tokens).toBe(0)
    })
  })
})

