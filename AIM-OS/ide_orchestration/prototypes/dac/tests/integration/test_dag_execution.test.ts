/**
 * Integration Tests: DAG Execution
 * 
 * Tests for DAG execution with real components
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { WorkflowExecutor, WorkflowConfig } from '@services/lucid-chat/orchestration'
import { LLMService } from '@services/lucid-chat/llm/LLMService'
import { createMockCommandServer } from '../../__mocks__/mockCommandServer'

describe('DAG Execution Integration', () => {
  let workflowExecutor: WorkflowExecutor
  let llmService: LLMService
  let mockServer: ReturnType<typeof createMockCommandServer>

  beforeEach(() => {
    mockServer = createMockCommandServer()
    global.fetch = mockServer.mockFetch as any
    llmService = new LLMService('http://localhost:5001')
    workflowExecutor = new WorkflowExecutor(llmService, 'http://localhost:5001')
  })

  describe('simple DAG execution', () => {
    it('should execute simple DAG', async () => {
      mockServer.setResponse('call_api', {
        success: true,
        data: {
          content: 'Test response',
          model: 'gpt-3.5-turbo'
        }
      })

      const config: WorkflowConfig = {
        id: 'workflow-1',
        goal: 'Simple DAG',
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
              dependencies: ['step-1']
            }
          ]
        },
        parallelExecution: true
      }

      const result = await workflowExecutor.execute(config)

      expect(result.success).toBe(true)
      expect(result.steps_executed.length).toBe(2)
    })

    it('should execute complex DAG', async () => {
      mockServer.setResponse('call_api', {
        success: true,
        data: {
          content: 'Test response',
          model: 'gpt-3.5-turbo'
        }
      })

      const config: WorkflowConfig = {
        id: 'workflow-2',
        goal: 'Complex DAG',
        plan: {
          steps: [
            { id: 'step-1', role: 'planner', task: 'Plan', dependencies: [] },
            { id: 'step-2', role: 'reasoner', task: 'Reason 1', dependencies: ['step-1'] },
            { id: 'step-3', role: 'reasoner', task: 'Reason 2', dependencies: ['step-1'] },
            { id: 'step-4', role: 'builder', task: 'Build', dependencies: ['step-2', 'step-3'] }
          ]
        },
        parallelExecution: true
      }

      const result = await workflowExecutor.execute(config)

      expect(result.success).toBe(true)
      expect(result.steps_executed.length).toBe(4)
    })
  })

  describe('parallel execution verification', () => {
    it('should execute independent steps in parallel', async () => {
      mockServer.setResponse('call_api', {
        success: true,
        data: {
          content: 'Test response',
          model: 'gpt-3.5-turbo'
        }
      })

      const startTimes = new Map<string, number>()

      const config: WorkflowConfig = {
        id: 'workflow-3',
        goal: 'Parallel execution',
        plan: {
          steps: [
            { id: 'step-1', role: 'reasoner', task: 'Task 1', dependencies: [] },
            { id: 'step-2', role: 'reasoner', task: 'Task 2', dependencies: [] },
            { id: 'step-3', role: 'reasoner', task: 'Task 3', dependencies: [] }
          ]
        },
        parallelExecution: true
      }

      // Mock to track execution times
      vi.spyOn(workflowExecutor as any, 'executeStep').mockImplementation(async (step, context) => {
        startTimes.set(step.id, Date.now())
        await new Promise(resolve => setTimeout(resolve, 50)) // Simulate work
        return {
          success: true,
          confidence: 0.80,
          tokensUsed: 100,
          latencyMs: 50,
          role: step.role
        }
      })

      const result = await workflowExecutor.execute(config)

      expect(result.success).toBe(true)
      expect(result.steps_executed.length).toBe(3)

      // Check that steps started around the same time (parallel)
      if (startTimes.size >= 2) {
        const times = Array.from(startTimes.values())
        const maxTime = Math.max(...times)
        const minTime = Math.min(...times)
        expect(maxTime - minTime).toBeLessThan(100) // Should start within 100ms
      }
    })
  })

  describe('dependency resolution', () => {
    it('should respect dependencies in DAG', async () => {
      mockServer.setResponse('call_api', {
        success: true,
        data: {
          content: 'Test response',
          model: 'gpt-3.5-turbo'
        }
      })

      const executionOrder: string[] = []

      const config: WorkflowConfig = {
        id: 'workflow-4',
        goal: 'Dependencies',
        plan: {
          steps: [
            { id: 'step-1', role: 'planner', task: 'Plan', dependencies: [] },
            { id: 'step-2', role: 'reasoner', task: 'Reason', dependencies: ['step-1'] },
            { id: 'step-3', role: 'builder', task: 'Build', dependencies: ['step-2'] }
          ]
        },
        parallelExecution: true
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
      // step-1 must come before step-2, step-2 before step-3
      expect(executionOrder.indexOf('step-1')).toBeLessThan(executionOrder.indexOf('step-2'))
      expect(executionOrder.indexOf('step-2')).toBeLessThan(executionOrder.indexOf('step-3'))
    })
  })

  describe('error propagation', () => {
    it('should propagate errors in DAG', async () => {
      mockServer.setResponse('call_api', {
        success: false,
        error: 'API error'
      })

      const config: WorkflowConfig = {
        id: 'workflow-5',
        goal: 'Error propagation',
        plan: {
          steps: [
            { id: 'step-1', role: 'reasoner', task: 'Task 1', dependencies: [] },
            { id: 'step-2', role: 'reasoner', task: 'Task 2', dependencies: ['step-1'] }
          ]
        },
        parallelExecution: true
      }

      const result = await workflowExecutor.execute(config)

      expect(result.success).toBe(false)
      expect(result.error).toBeDefined()
    })

    it('should skip dependent steps when dependency fails', async () => {
      mockServer.setResponse('call_api', {
        success: false,
        error: 'API error'
      })

      const config: WorkflowConfig = {
        id: 'workflow-6',
        goal: 'Skip on failure',
        plan: {
          steps: [
            { id: 'step-1', role: 'reasoner', task: 'Task 1', dependencies: [] },
            { id: 'step-2', role: 'reasoner', task: 'Task 2', dependencies: ['step-1'] }
          ]
        },
        parallelExecution: true
      }

      const result = await workflowExecutor.execute(config)

      expect(result.success).toBe(false)
      // step-2 should be skipped because step-1 failed
      expect(result.steps_executed.length).toBe(0)
    })
  })

  describe('execution timing', () => {
    it('should track execution time', async () => {
      mockServer.setResponse('call_api', {
        success: true,
        data: {
          content: 'Test response',
          model: 'gpt-3.5-turbo'
        }
      })

      const config: WorkflowConfig = {
        id: 'workflow-7',
        goal: 'Timing',
        plan: {
          steps: [
            { id: 'step-1', role: 'reasoner', task: 'Task 1', dependencies: [] }
          ]
        },
        parallelExecution: true
      }

      const startTime = Date.now()
      const result = await workflowExecutor.execute(config)
      const duration = Date.now() - startTime

      expect(result.success).toBe(true)
      expect(result.total_time).toBeGreaterThan(0)
      expect(result.total_time * 1000).toBeLessThan(duration + 1000) // Allow some margin
    })
  })
})

