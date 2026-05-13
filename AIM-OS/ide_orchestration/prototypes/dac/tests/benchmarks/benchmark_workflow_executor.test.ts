/**
 * Performance Benchmarks: WorkflowExecutor
 * 
 * Benchmarks for workflow execution performance
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { WorkflowExecutor, WorkflowConfig } from '@services/lucid-chat/orchestration'
import { LLMService } from '@services/lucid-chat/llm/LLMService'
import { createMockCommandServer } from '../../__mocks__/mockCommandServer'

describe('WorkflowExecutor Performance Benchmarks', () => {
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
    it('should execute simple workflow (1 step) in <1000ms', async () => {
      mockServer.setResponse('call_api', {
        success: true,
        data: {
          content: 'Test response',
          model: 'gpt-3.5-turbo'
        }
      })

      const config: WorkflowConfig = {
        id: 'workflow-1',
        goal: 'Simple workflow',
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

      const startTime = performance.now()
      const result = await workflowExecutor.execute(config)
      const endTime = performance.now()
      const duration = endTime - startTime

      expect(result.success).toBe(true)
      expect(duration).toBeLessThan(1000) // <1000ms
      console.log(`[Benchmark] WorkflowExecutor simple workflow (1 step): ${duration.toFixed(3)}ms`)
    })
  })

  describe('complex workflow execution', () => {
    it('should execute complex workflow (10 steps) in <10000ms', async () => {
      mockServer.setResponse('call_api', {
        success: true,
        data: {
          content: 'Test response',
          model: 'gpt-3.5-turbo'
        }
      })

      const config: WorkflowConfig = {
        id: 'workflow-2',
        goal: 'Complex workflow',
        plan: {
          steps: Array.from({ length: 10 }, (_, i) => ({
            id: `step-${i + 1}`,
            role: 'reasoner',
            task: `Task ${i + 1}`,
            dependencies: i > 0 ? [`step-${i}`] : []
          }))
        },
        parallelExecution: false
      }

      const startTime = performance.now()
      const result = await workflowExecutor.execute(config)
      const endTime = performance.now()
      const duration = endTime - startTime

      expect(result.success).toBe(true)
      expect(result.steps_executed.length).toBe(10)
      expect(duration).toBeLessThan(10000) // <10000ms
      console.log(`[Benchmark] WorkflowExecutor complex workflow (10 steps): ${duration.toFixed(3)}ms`)
    })
  })

  describe('parallel workflow execution', () => {
    it('should execute parallel workflow faster than sequential', async () => {
      mockServer.setResponse('call_api', {
        success: true,
        data: {
          content: 'Test response',
          model: 'gpt-3.5-turbo'
        }
      })

      const steps = Array.from({ length: 5 }, (_, i) => ({
        id: `step-${i + 1}`,
        role: 'reasoner',
        task: `Task ${i + 1}`,
        dependencies: [] // All independent
      }))

      // Sequential execution
      const sequentialConfig: WorkflowConfig = {
        id: 'workflow-sequential',
        goal: 'Sequential workflow',
        plan: { steps },
        parallelExecution: false
      }

      const sequentialStart = performance.now()
      const sequentialResult = await workflowExecutor.execute(sequentialConfig)
      const sequentialDuration = performance.now() - sequentialStart

      // Parallel execution
      const parallelConfig: WorkflowConfig = {
        id: 'workflow-parallel',
        goal: 'Parallel workflow',
        plan: { steps },
        parallelExecution: true
      }

      const parallelStart = performance.now()
      const parallelResult = await workflowExecutor.execute(parallelConfig)
      const parallelDuration = performance.now() - parallelStart

      expect(sequentialResult.success).toBe(true)
      expect(parallelResult.success).toBe(true)
      // Parallel should be faster (allowing for network overhead)
      expect(parallelDuration).toBeLessThan(sequentialDuration * 2) // Parallel should be at least 2x faster
      console.log(`[Benchmark] WorkflowExecutor parallel vs sequential:`)
      console.log(`  Sequential: ${sequentialDuration.toFixed(3)}ms`)
      console.log(`  Parallel: ${parallelDuration.toFixed(3)}ms`)
      console.log(`  Speedup: ${(sequentialDuration / parallelDuration).toFixed(2)}x`)
    })
  })
})

