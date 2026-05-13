/**
 * Performance Benchmarks: SearchOrchestrator
 * 
 * Benchmarks for search orchestration performance
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { SearchOrchestrator, UnifiedSearchRequest } from '@services/lucid-chat/search/SearchOrchestrator'
import { createMockCommandServer } from '../../__mocks__/mockCommandServer'

describe('SearchOrchestrator Performance Benchmarks', () => {
  let orchestrator: SearchOrchestrator
  let mockServer: ReturnType<typeof createMockCommandServer>

  beforeEach(() => {
    mockServer = createMockCommandServer()
    global.fetch = mockServer.mockFetch as any
    orchestrator = new SearchOrchestrator('http://localhost:5001')
  })

  describe('single provider search', () => {
    it('should execute single provider search in <500ms', async () => {
      mockServer.setResponse('deepsearch', {
        success: true,
        data: {
          results: [
            { url: 'http://example.com', title: 'Example', summary: 'Test' }
          ]
        }
      })

      const request: UnifiedSearchRequest = {
        query: 'test query',
        providers: ['deepsearch']
      }

      const startTime = performance.now()
      const result = await orchestrator.search(request)
      const endTime = performance.now()
      const duration = endTime - startTime

      expect(result.query).toBe('test query')
      expect(duration).toBeLessThan(500) // <500ms
      console.log(`[Benchmark] SearchOrchestrator single provider: ${duration.toFixed(3)}ms`)
    })
  })

  describe('multi-provider search', () => {
    it('should execute multi-provider search (3 providers) in <2000ms', async () => {
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

      mockServer.setResponse('perplexity', {
        success: true,
        data: {
          results: [
            { url: 'http://example2.com', title: 'Example 2', summary: 'Test 2' }
          ]
        }
      })

      const request: UnifiedSearchRequest = {
        query: 'test query',
        providers: ['deepsearch', 'icip', 'perplexity']
      }

      const startTime = performance.now()
      const result = await orchestrator.search(request)
      const endTime = performance.now()
      const duration = endTime - startTime

      expect(result.query).toBe('test query')
      expect(result.metadata.providersUsed.length).toBe(3)
      expect(duration).toBeLessThan(2000) // <2000ms (parallel execution)
      console.log(`[Benchmark] SearchOrchestrator multi-provider (3): ${duration.toFixed(3)}ms`)
    })
  })

  describe('result merging', () => {
    it('should merge 100 results in <100ms', async () => {
      mockServer.setResponse('deepsearch', {
        success: true,
        data: {
          results: Array.from({ length: 100 }, (_, i) => ({
            url: `http://example${i}.com`,
            title: `Example ${i}`,
            summary: `Test ${i}`,
            relevance: Math.random()
          }))
        }
      })

      const request: UnifiedSearchRequest = {
        query: 'test query',
        providers: ['deepsearch']
      }

      const startTime = performance.now()
      const result = await orchestrator.search(request)
      const endTime = performance.now()
      const duration = endTime - startTime

      expect(result.aggregated.length).toBe(100)
      expect(duration).toBeLessThan(100) // <100ms (including network, but merging should be fast)
      console.log(`[Benchmark] SearchOrchestrator result merging (100 results): ${duration.toFixed(3)}ms`)
    })
  })
})

