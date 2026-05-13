/**
 * Mock LLM Service
 * 
 * Provides mock LLM responses for testing
 */

import { vi } from 'vitest'
import { LLMService, LLMResponse, APIResponse } from '@services/lucid-chat'

/**
 * Create mock LLM Service
 */
export function createMockLLMService(): jest.Mocked<LLMService> {
  return {
    chatCompletion: vi.fn(),
    complete: vi.fn(),
    getAvailableModels: vi.fn(() => Promise.resolve(['claude-3-5-sonnet-20241022'])),
    isAvailable: vi.fn(() => true),
  } as any
}

/**
 * Mock LLM responses
 */
export const mockLLMResponses = {
  simple: {
    success: true,
    data: {
      text: 'This is a test response',
      model: 'claude-3-5-sonnet-20241022',
      provider: 'anthropic',
      tokensUsed: 50,
      latencyMs: 1000,
      confidence: 0.85,
    },
  } as APIResponse<LLMResponse>,

  reasoning: {
    success: true,
    data: {
      text: `Step 1: Analyze the problem
Step 2: Consider approaches
Step 3: Select best approach
Conclusion: The optimal solution is X`,
      model: 'claude-3-5-sonnet-20241022',
      provider: 'anthropic',
      tokensUsed: 200,
      latencyMs: 2000,
      confidence: 0.90,
    },
  } as APIResponse<LLMResponse>,

  hypotheses: {
    success: true,
    data: {
      text: `["Hypothesis 1: Deductive approach from first principles", "Hypothesis 2: Inductive approach from examples", "Hypothesis 3: Analogical approach from similar cases"]`,
      model: 'claude-3-5-sonnet-20241022',
      provider: 'anthropic',
      tokensUsed: 150,
      latencyMs: 1500,
      confidence: 0.85,
    },
  } as APIResponse<LLMResponse>,

  error: {
    success: false,
    error: 'API rate limit exceeded',
  } as APIResponse<LLMResponse>,
}

/**
 * Setup mock LLM service with default responses
 */
export function setupMockLLMService(mockService: jest.Mocked<LLMService>) {
  // Default: Return simple response
  mockService.chatCompletion.mockResolvedValue(mockLLMResponses.simple)
  mockService.complete.mockResolvedValue(mockLLMResponses.simple)

  return mockService
}

