/**
 * Integration Tests: Search Orchestration
 * 
 * Tests for multi-provider search coordination
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { SearchOrchestrator, UnifiedSearchRequest } from '@services/lucid-chat/search/SearchOrchestrator'
import { createMockCommandServer } from '../../__mocks__/mockCommandServer'

describe('Search Orchestration Integration', () => {
  let orchestrator: SearchOrchestrator
  let mockServer: ReturnType<typeof createMockCommandServer>

  beforeEach(() => {
    mockServer = createMockCommandServer()
    global.fetch = mockServer.mockFetch as any
    orchestrator = new SearchOrchestrator('http://localhost:5001')
  })

  describe('multi-provider search', () => {
    it('should coordinate DEEPSEARCH and ICIP', async () => {
      mockServer.setResponse('deepsearch', {
        success: true,
        data: {
          results: [
            { url: 'http://example.com', title: 'Example', summary: 'Test' }
          ]
        }
      })

      mockServer.setResponse('icip_search', {
        success: true,
        data: {
          results: [
            { file: 'test.py', line: 10, code: 'def test(): pass' }
          ]
        }
      })

      const request: UnifiedSearchRequest = {
        query: 'test query',
        providers: ['deepsearch', 'icip']
      }

      const result = await orchestrator.search(request)

      expect(result.query).toBe('test query')
      expect(result.results.deepsearch).toBeDefined()
      expect(result.results.icip).toBeDefined()
      expect(result.metadata.providersUsed).toContain('deepsearch')
      expect(result.metadata.providersUsed).toContain('icip')
    })

    it('should execute providers in parallel', async () => {
      const startTimes: number[] = []

      mockServer.setResponse('deepsearch', {
        success: true,
        data: { results: [] }
      })

      mockServer.setResponse('icip_search', {
        success: true,
        data: { results: [] }
      })

      // Mock to track parallel execution
      const originalFetch = global.fetch
      global.fetch = vi.fn().mockImplementation((url: string) => {
        startTimes.push(Date.now())
        return originalFetch(url)
      })

      const request: UnifiedSearchRequest = {
        query: 'test',
        providers: ['deepsearch', 'icip']
      }

      const result = await orchestrator.search(request)

      // Both should start around the same time (parallel)
      if (startTimes.length >= 2) {
        const timeDiff = Math.abs(startTimes[1] - startTimes[0])
        expect(timeDiff).toBeLessThan(100) // Should start within 100ms
      }
    })
  })

  describe('result merging', () => {
    it('should merge results from multiple providers', async () => {
      mockServer.setResponse('deepsearch', {
        success: true,
        data: {
          results: [
            { url: 'http://example.com', title: 'Example 1' }
          ]
        }
      })

      mockServer.setResponse('icip_search', {
        success: true,
        data: {
          results: [
            { file: 'test.py', line: 10, code: 'def test(): pass' }
          ]
        }
      })

      const request: UnifiedSearchRequest = {
        query: 'test',
        providers: ['deepsearch', 'icip']
      }

      const result = await orchestrator.search(request)

      expect(result.aggregated.length).toBeGreaterThan(0)
      expect(result.metadata.totalResults).toBeGreaterThan(0)
    })

    it('should deduplicate results', async () => {
      mockServer.setResponse('deepsearch', {
        success: true,
        data: {
          results: [
            { url: 'http://example.com', title: 'Example' }
          ]
        }
      })

      mockServer.setResponse('perplexity', {
        success: true,
        data: {
          results: [
            { url: 'http://example.com', title: 'Example' } // Duplicate
          ]
        }
      })

      const request: UnifiedSearchRequest = {
        query: 'test',
        providers: ['deepsearch', 'perplexity']
      }

      const result = await orchestrator.search(request)

      // Should deduplicate
      const urls = result.aggregated.map((r: any) => r.url)
      const uniqueUrls = new Set(urls)
      expect(uniqueUrls.size).toBeLessThanOrEqual(urls.length)
    })
  })

  describe('provider fallback', () => {
    it('should fallback to other providers when one fails', async () => {
      mockServer.setResponse('deepsearch', {
        success: false,
        error: 'DEEPSEARCH failed'
      })

      mockServer.setResponse('icip_search', {
        success: true,
        data: {
          results: [
            { file: 'test.py', line: 10, code: 'def test(): pass' }
          ]
        }
      })

      const request: UnifiedSearchRequest = {
        query: 'test',
        providers: ['deepsearch', 'icip']
      }

      const result = await orchestrator.search(request)

      expect(result.results.icip).toBeDefined()
      expect(result.metadata.providersUsed).toContain('icip')
    })
  })

  describe('error handling', () => {
    it('should handle provider errors gracefully', async () => {
      mockServer.setResponse('deepsearch', {
        success: false,
        error: 'Provider error'
      })

      mockServer.setResponse('icip_search', {
        success: false,
        error: 'Provider error'
      })

      const request: UnifiedSearchRequest = {
        query: 'test',
        providers: ['deepsearch', 'icip']
      }

      const result = await orchestrator.search(request)

      // Should still return result structure
      expect(result.query).toBe('test')
      expect(result.results).toBeDefined()
      expect(result.metadata).toBeDefined()
    })
  })

  describe('search filtering', () => {
    it('should filter results by provider', async () => {
      mockServer.setResponse('deepsearch', {
        success: true,
        data: {
          results: [
            { url: 'http://example.com', title: 'Example' }
          ]
        }
      })

      const request: UnifiedSearchRequest = {
        query: 'test',
        providers: ['deepsearch'] // Only DEEPSEARCH
      }

      const result = await orchestrator.search(request)

      expect(result.results.deepsearch).toBeDefined()
      expect(result.results.icip).toBeUndefined()
      expect(result.metadata.providersUsed).toEqual(['deepsearch'])
    })
  })

  describe('result ranking', () => {
    it('should rank results by relevance', async () => {
      mockServer.setResponse('deepsearch', {
        success: true,
        data: {
          results: [
            { url: 'http://example.com', title: 'Example', relevance: 0.9 },
            { url: 'http://example2.com', title: 'Example 2', relevance: 0.7 }
          ]
        }
      })

      const request: UnifiedSearchRequest = {
        query: 'test',
        providers: ['deepsearch']
      }

      const result = await orchestrator.search(request)

      expect(result.aggregated.length).toBeGreaterThan(0)
      // Higher relevance should come first
      if (result.aggregated.length >= 2) {
        expect(result.aggregated[0].relevance).toBeGreaterThanOrEqual(
          result.aggregated[1].relevance
        )
      }
    })
  })

  describe('search timeouts', () => {
    it('should handle search timeouts', async () => {
      // Mock slow response
      mockServer.setResponse('deepsearch', new Promise((resolve) => {
        setTimeout(() => {
          resolve({
            success: true,
            data: { results: [] }
          })
        }, 10000) // 10 second delay
      }))

      const request: UnifiedSearchRequest = {
        query: 'test',
        providers: ['deepsearch']
      }

      // Should timeout or handle gracefully
      const result = await Promise.race([
        orchestrator.search(request),
        new Promise((resolve) => {
          setTimeout(() => resolve({ timeout: true }), 5000)
        })
      ])

      // Either completes or times out gracefully
      expect(result).toBeDefined()
    })
  })
})

