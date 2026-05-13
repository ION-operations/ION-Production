/**
 * Unit Tests: BranchReasoningService
 * 
 * Tests for multi-path reasoning
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { BranchReasoningService } from '@services/lucid-chat'
import { createMockLLMService, mockLLMResponses } from '../../__mocks__/mockLLMService'
import { createMockCommandServer, mockMCPResponses } from '../../__mocks__/mockCommandServer'

describe('BranchReasoningService', () => {
  let service: BranchReasoningService
  let mockLLM: ReturnType<typeof createMockLLMService>
  let mockServer: ReturnType<typeof createMockCommandServer>

  beforeEach(() => {
    mockLLM = createMockLLMService()
    mockServer = createMockCommandServer()
    global.fetch = mockServer.mockFetch as any

    service = new BranchReasoningService(mockLLM as any)

    // Setup default responses
    mockLLM.complete.mockResolvedValue(mockLLMResponses.simple)
    mockServer.setResponse('store_memory', mockMCPResponses.store_memory)
  })

  describe('reasonWithBranches', () => {
    it('should generate multiple branches', async () => {
      // Arrange
      mockLLM.complete
        .mockResolvedValueOnce(mockLLMResponses.hypotheses)  // Hypothesis generation
        .mockResolvedValueOnce(mockLLMResponses.reasoning)   // Branch 1
        .mockResolvedValueOnce(mockLLMResponses.reasoning)   // Branch 2
        .mockResolvedValueOnce(mockLLMResponses.reasoning)   // Branch 3
        .mockResolvedValueOnce(mockLLMResponses.simple)      // Evaluation

      // Act
      const result = await service.reasonWithBranches({
        problem: 'Test problem',
        numBranches: 3,
      })

      // Assert
      expect(result.success).toBe(true)
      expect(result.data?.allBranches).toHaveLength(3)
      expect(result.data?.bestBranch).toBeDefined()
      expect(result.data?.finalAnswer).toBeDefined()
    })

    it('should prune low-confidence branches', async () => {
      // Arrange: Set up branches with varying confidence
      const lowConfidence = {
        ...mockLLMResponses.reasoning,
        data: { ...mockLLMResponses.reasoning.data, confidence: 0.5 },
      }
      const highConfidence = {
        ...mockLLMResponses.reasoning,
        data: { ...mockLLMResponses.reasoning.data, confidence: 0.9 },
      }

      mockLLM.complete
        .mockResolvedValueOnce(mockLLMResponses.hypotheses)
        .mockResolvedValueOnce(lowConfidence)   // Branch 1: low confidence
        .mockResolvedValueOnce(highConfidence)  // Branch 2: high confidence
        .mockResolvedValueOnce(highConfidence)  // Branch 3: high confidence
        .mockResolvedValueOnce(mockLLMResponses.simple)

      // Act
      const result = await service.reasonWithBranches({
        problem: 'Test problem',
        pruneThreshold: 0.70,
      })

      // Assert
      expect(result.data?.metadata.branchesPruned).toBeGreaterThan(0)
      expect(result.data?.prunedBranches.every(b => b.confidence >= 0.70)).toBe(true)
    })

    it('should select best branch by quality score', async () => {
      // Test best selection logic
      mockLLM.complete
        .mockResolvedValueOnce(mockLLMResponses.hypotheses)
        .mockResolvedValueOnce(mockLLMResponses.reasoning)
        .mockResolvedValueOnce(mockLLMResponses.reasoning)
        .mockResolvedValueOnce(mockLLMResponses.reasoning)
        .mockResolvedValueOnce(mockLLMResponses.simple)

      const result = await service.reasonWithBranches({
        problem: 'Test problem',
      })

      expect(result.data?.bestBranch).toBeDefined()
      expect(result.data?.bestBranch.qualityScore).toBeGreaterThanOrEqual(0.70)
    })

    it('should store branches in CMC', async () => {
      mockLLM.complete
        .mockResolvedValueOnce(mockLLMResponses.hypotheses)
        .mockResolvedValueOnce(mockLLMResponses.reasoning)
        .mockResolvedValueOnce(mockLLMResponses.reasoning)
        .mockResolvedValueOnce(mockLLMResponses.reasoning)
        .mockResolvedValueOnce(mockLLMResponses.simple)

      await service.reasonWithBranches({ problem: 'Test' })

      // Verify CMC storage called
      expect(mockServer.mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/mcp/execute'),
        expect.objectContaining({
          body: expect.stringContaining('store_memory'),
        })
      )
    })
  })
})

