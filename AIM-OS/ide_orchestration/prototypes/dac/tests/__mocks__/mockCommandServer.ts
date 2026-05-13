/**
 * Mock Command Server
 * 
 * Mocks MCP tool execution via Command Server
 */

import { vi } from 'vitest'

export interface MockMCPResponse {
  success: boolean
  data?: any
  result?: any
  error?: string
}

/**
 * Create mock Command Server
 */
export function createMockCommandServer() {
  const mockResponses = new Map<string, MockMCPResponse>()

  return {
    /**
     * Set response for specific tool
     */
    setResponse(tool: string, response: MockMCPResponse) {
      mockResponses.set(tool, response)
    },

    /**
     * Mock fetch implementation
     */
    mockFetch: vi.fn((url: string, options?: any) => {
      if (!url.includes('/mcp/execute')) {
        return Promise.reject(new Error('Not mocked'))
      }

      const body = JSON.parse(options?.body || '{}')
      const tool = body.tool

      const response = mockResponses.get(tool) || {
        success: true,
        data: {},
      }

      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve(response),
      })
    }),

    /**
     * Clear all responses
     */
    clear() {
      mockResponses.clear()
    },
  }
}

/**
 * Common mock responses
 */
export const mockMCPResponses = {
  store_memory: {
    success: true,
    data: {
      atom_id: 'test_atom_123',
    },
  },

  retrieve_memory: {
    success: true,
    data: {
      results: [
        {
          content: JSON.stringify({ test: 'data' }),
          metadata: { timestamp: new Date().toISOString() },
        },
      ],
    },
  },

  track_confidence: {
    success: true,
    data: {
      witness_id: 'test_witness_123',
    },
  },

  synthesize_knowledge: {
    success: true,
    data: {
      summary: 'Test synthesis',
      insights: ['Insight 1', 'Insight 2'],
    },
  },

  icip_search: {
    success: true,
    data: {
      results: [
        {
          file: 'test.ts',
          line: 10,
          code: 'function test() {}',
          language: 'typescript',
          relevance: 0.9,
          confidence: 0.85,
        },
      ],
      metadata: {
        query: 'test',
        total_results: 1,
      },
    },
  },

  deepsearch: {
    success: true,
    data: {
      results: [
        {
          url: 'https://example.com',
          title: 'Test Result',
          content: 'Test content',
          trustScore: 0.8,
        },
      ],
      metadata: {
        total_results: 1,
        search_time: 0.5,
      },
    },
  },
}

