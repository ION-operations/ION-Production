/**
 * Integration Tests: Quality Gates Integration
 * 
 * Tests for quality gate enforcement in workflows
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { WorkflowExecutor, WorkflowConfig } from '@services/lucid-chat/orchestration'
import { LLMService } from '@services/lucid-chat/llm/LLMService'
import { QualityGate } from '@services/lucid-chat/orchestration'
import { createMockCommandServer } from '../../__mocks__/mockCommandServer'

describe('Quality Gates Integration', () => {
  let workflowExecutor: WorkflowExecutor
  let llmService: LLMService
  let mockServer: ReturnType<typeof createMockCommandServer>

  beforeEach(() => {
    mockServer = createMockCommandServer()
    global.fetch = mockServer.mockFetch as any
    llmService = new LLMService('http://localhost:5001')
    workflowExecutor = new WorkflowExecutor(llmService, 'http://localhost:5001')
  })

  describe('gate enforcement in workflow', () => {
    it('should enforce confidence gate', async () => {
      mockServer.setResponse('call_api', {
        success: true,
        data: {
          content: 'Test response',
          model: 'gpt-3.5-turbo'
        }
      })

      const gates: QualityGate[] = [
        {
          type: 'confidence',
          threshold: 0.70,
          action: 'stop'
        }
      ]

      const config: WorkflowConfig = {
        id: 'workflow-1',
        goal: 'Confidence gate',
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
        qualityGates: gates,
        parallelExecution: false
      }

      const result = await workflowExecutor.execute(config)

      expect(result.success).toBe(true)
      expect(result.steps_executed.length).toBe(1)
    })

    it('should enforce κ-gate (Band A/B/C)', async () => {
      mockServer.setResponse('call_api', {
        success: true,
        data: {
          content: 'Test response',
          model: 'gpt-3.5-turbo'
        }
      })

      const gates: QualityGate[] = [
        {
          type: 'kappa',
          threshold: 0.70,
          action: 'retry'
        }
      ]

      const config: WorkflowConfig = {
        id: 'workflow-2',
        goal: 'κ-gate',
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
        qualityGates: gates,
        parallelExecution: false
      }

      const result = await workflowExecutor.execute(config)

      expect(result.success).toBe(true)
      // κ-gate should classify result into Band A/B/C
      if (result.steps_executed.length > 0) {
        const step = result.steps_executed[0]
        expect((step as any).kappa_band).toBeDefined()
      }
    })

    it('should enforce consistency gate (SEG)', async () => {
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

      const gates: QualityGate[] = [
        {
          type: 'consistency',
          threshold: 1.0,
          action: 'stop'
        }
      ]

      const config: WorkflowConfig = {
        id: 'workflow-3',
        goal: 'Consistency gate',
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
        qualityGates: gates,
        parallelExecution: false
      }

      const result = await workflowExecutor.execute(config)

      expect(result.success).toBe(true)
    })

    it('should enforce VIF gate (provenance)', async () => {
      mockServer.setResponse('call_api', {
        success: true,
        data: {
          content: 'Test response',
          model: 'gpt-3.5-turbo'
        }
      })

      const gates: QualityGate[] = [
        {
          type: 'vif',
          threshold: 1.0,
          action: 'warn'
        }
      ]

      const config: WorkflowConfig = {
        id: 'workflow-4',
        goal: 'VIF gate',
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
        qualityGates: gates,
        parallelExecution: false
      }

      const result = await workflowExecutor.execute(config)

      expect(result.success).toBe(true)
    })
  })

  describe('multiple gates evaluation', () => {
    it('should evaluate multiple gates', async () => {
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

      const gates: QualityGate[] = [
        {
          type: 'confidence',
          threshold: 0.70,
          action: 'stop'
        },
        {
          type: 'consistency',
          threshold: 1.0,
          action: 'stop'
        }
      ]

      const config: WorkflowConfig = {
        id: 'workflow-5',
        goal: 'Multiple gates',
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
        qualityGates: gates,
        parallelExecution: false
      }

      const result = await workflowExecutor.execute(config)

      expect(result.success).toBe(true)
    })
  })
})

