/**
 * Integration Tests: APOE Workflow
 * 
 * Tests for complete APOE workflow execution with all components
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { WorkflowExecutor, WorkflowConfig } from '@services/lucid-chat/orchestration'
import { LLMService } from '@services/lucid-chat/llm/LLMService'
import { createMockCommandServer, mockMCPResponses } from '../../__mocks__/mockCommandServer'

describe('APOE Workflow Integration', () => {
  let workflowExecutor: WorkflowExecutor
  let llmService: LLMService
  let mockServer: ReturnType<typeof createMockCommandServer>

  beforeEach(() => {
    mockServer = createMockCommandServer()
    global.fetch = mockServer.mockFetch as any
    llmService = new LLMService('http://localhost:5001')
    workflowExecutor = new WorkflowExecutor(llmService, 'http://localhost:5001')
  })

  describe('simple workflow execution', () => {
    it('should execute single-step workflow', async () => {
      mockServer.setResponse('call_api', {
        success: true,
        data: {
          content: 'Test response',
          model: 'gpt-3.5-turbo'
        }
      })

      const config: WorkflowConfig = {
        id: 'workflow-1',
        goal: 'Test goal',
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
        parallelExecution: false
      }

      const result = await workflowExecutor.execute(config)

      expect(result.success).toBe(true)
      expect(result.steps_executed.length).toBe(1)
      expect(result.workflow_id).toBe('workflow-1')
      expect(result.goal).toBe('Test goal')
    })

    it('should execute multi-step workflow sequentially', async () => {
      mockServer.setResponse('call_api', {
        success: true,
        data: {
          content: 'Test response',
          model: 'gpt-3.5-turbo'
        }
      })

      const config: WorkflowConfig = {
        id: 'workflow-2',
        goal: 'Multi-step goal',
        plan: {
          steps: [
            {
              id: 'step-1',
              role: 'planner',
              task: 'Plan task',
              dependencies: []
            },
            {
              id: 'step-2',
              role: 'reasoner',
              task: 'Reason task',
              dependencies: ['step-1']
            }
          ]
        },
        parallelExecution: false
      }

      const result = await workflowExecutor.execute(config)

      expect(result.success).toBe(true)
      expect(result.steps_executed.length).toBe(2)
      expect(result.steps_executed[0].role).toBe('planner')
      expect(result.steps_executed[1].role).toBe('reasoner')
    })
  })

  describe('parallel execution', () => {
    it('should execute independent steps in parallel', async () => {
      mockServer.setResponse('call_api', {
        success: true,
        data: {
          content: 'Test response',
          model: 'gpt-3.5-turbo'
        }
      })

      const config: WorkflowConfig = {
        id: 'workflow-3',
        goal: 'Parallel goal',
        plan: {
          steps: [
            {
              id: 'step-1',
              role: 'reasoner',
              task: 'Task 1',
              dependencies: []
            },
            {
              id: 'step-2',
              role: 'reasoner',
              task: 'Task 2',
              dependencies: []
            },
            {
              id: 'step-3',
              role: 'reasoner',
              task: 'Task 3',
              dependencies: []
            }
          ]
        },
        parallelExecution: true
      }

      const startTime = Date.now()
      const result = await workflowExecutor.execute(config)
      const duration = Date.now() - startTime

      expect(result.success).toBe(true)
      expect(result.steps_executed.length).toBe(3)
      // Parallel execution should be faster than sequential
      expect(duration).toBeLessThan(3000) // Should complete quickly
    })
  })

  describe('budget integration', () => {
    it('should track budget during workflow execution', async () => {
      mockServer.setResponse('call_api', {
        success: true,
        data: {
          content: 'Test response',
          model: 'gpt-3.5-turbo'
        }
      })

      const config: WorkflowConfig = {
        id: 'workflow-4',
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
          tokens: 1000,
          time: 60,
          cost: 1.0
        },
        parallelExecution: false
      }

      const result = await workflowExecutor.execute(config)

      expect(result.success).toBe(true)
      expect(result.budget_status).toBeDefined()
      expect(result.budget_status.usage).toBeDefined()
      expect(result.budget_status.usage.tokens).toBeGreaterThan(0)
      expect(result.total_cost).toBeGreaterThan(0)
    })

    it('should stop workflow when budget exceeded', async () => {
      mockServer.setResponse('call_api', {
        success: true,
        data: {
          content: 'Test response',
          model: 'gpt-3.5-turbo'
        }
      })

      const config: WorkflowConfig = {
        id: 'workflow-5',
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
          tokens: 0, // Zero budget
          time: 60,
          cost: 1.0
        },
        parallelExecution: false
      }

      const result = await workflowExecutor.execute(config)

      // Should fail or stop early
      expect(result.success).toBe(false)
      expect(result.error).toContain('Budget exceeded')
    })
  })

  describe('quality gates integration', () => {
    it('should enforce quality gates during workflow', async () => {
      mockServer.setResponse('call_api', {
        success: true,
        data: {
          content: 'Test response',
          model: 'gpt-3.5-turbo'
        }
      })

      mockServer.setResponse('synthesize_knowledge', {
        success: true,
        result: {
          contradictions: []
        }
      })

      const config: WorkflowConfig = {
        id: 'workflow-6',
        goal: 'Quality gates',
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
        qualityGates: [
          {
            type: 'confidence',
            threshold: 0.70,
            action: 'stop'
          }
        ],
        parallelExecution: false
      }

      const result = await workflowExecutor.execute(config)

      expect(result.success).toBe(true)
      expect(result.steps_executed.length).toBe(1)
    })

    it('should stop workflow when quality gate fails', async () => {
      mockServer.setResponse('call_api', {
        success: true,
        data: {
          content: 'Test response',
          model: 'gpt-3.5-turbo'
        }
      })

      const config: WorkflowConfig = {
        id: 'workflow-7',
        goal: 'Quality gate failure',
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
        qualityGates: [
          {
            type: 'confidence',
            threshold: 0.90, // High threshold
            action: 'stop'
          }
        ],
        parallelExecution: false
      }

      // Mock low confidence result
      vi.spyOn(workflowExecutor as any, 'executeStep').mockResolvedValue({
        success: true,
        confidence: 0.60, // Below threshold
        tokensUsed: 100,
        latencyMs: 1000
      })

      const result = await workflowExecutor.execute(config)

      // Should fail or stop due to quality gate
      expect(result.success).toBe(false)
    })
  })

  describe('error handling', () => {
    it('should handle step execution errors', async () => {
      mockServer.setResponse('call_api', {
        success: false,
        error: 'API error'
      })

      const config: WorkflowConfig = {
        id: 'workflow-8',
        goal: 'Error handling',
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
        parallelExecution: false
      }

      const result = await workflowExecutor.execute(config)

      expect(result.success).toBe(false)
      expect(result.error).toBeDefined()
    })
  })

  describe('step dependencies', () => {
    it('should respect step dependencies', async () => {
      mockServer.setResponse('call_api', {
        success: true,
        data: {
          content: 'Test response',
          model: 'gpt-3.5-turbo'
        }
      })

      const executionOrder: string[] = []

      const config: WorkflowConfig = {
        id: 'workflow-9',
        goal: 'Dependencies',
        plan: {
          steps: [
            {
              id: 'step-1',
              role: 'planner',
              task: 'Plan',
              dependencies: []
            },
            {
              id: 'step-2',
              role: 'reasoner',
              task: 'Reason',
              dependencies: ['step-1']
            },
            {
              id: 'step-3',
              role: 'builder',
              task: 'Build',
              dependencies: ['step-2']
            }
          ]
        },
        parallelExecution: false
      }

      // Mock to track execution order
      vi.spyOn(workflowExecutor as any, 'executeStep').mockImplementation(async (step, context) => {
        executionOrder.push(step.id)
        return {
          success: true,
          confidence: 0.80,
          tokensUsed: 100,
          latencyMs: 1000,
          role: step.role
        }
      })

      const result = await workflowExecutor.execute(config)

      expect(result.success).toBe(true)
      expect(executionOrder).toEqual(['step-1', 'step-2', 'step-3'])
    })
  })

  describe('result aggregation', () => {
    it('should aggregate results from all steps', async () => {
      mockServer.setResponse('call_api', {
        success: true,
        data: {
          content: 'Test response',
          model: 'gpt-3.5-turbo'
        }
      })

      const config: WorkflowConfig = {
        id: 'workflow-10',
        goal: 'Result aggregation',
        plan: {
          steps: [
            {
              id: 'step-1',
              role: 'reasoner',
              task: 'Task 1',
              dependencies: []
            },
            {
              id: 'step-2',
              role: 'reasoner',
              task: 'Task 2',
              dependencies: []
            }
          ]
        },
        parallelExecution: false
      }

      const result = await workflowExecutor.execute(config)

      expect(result.success).toBe(true)
      expect(result.steps_executed.length).toBe(2)
      expect(result.total_tokens).toBeGreaterThan(0)
      expect(result.total_time).toBeGreaterThan(0)
      expect(result.total_cost).toBeGreaterThan(0)
      expect(result.final_confidence).toBeGreaterThanOrEqual(0)
    })
  })
})

