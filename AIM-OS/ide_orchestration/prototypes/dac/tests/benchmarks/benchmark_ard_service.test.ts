/**
 * Performance Benchmarks: ARDService
 * 
 * Benchmarks for autonomous research performance
 */

import { describe, it, expect, beforeEach } from 'vitest'
import { ARDService } from '@services/lucid-chat/research/ARDService'
import { createMockCommandServer } from '../../__mocks__/mockCommandServer'

describe('ARDService Performance Benchmarks', () => {
  let ardService: ARDService
  let mockServer: ReturnType<typeof createMockCommandServer>

  beforeEach(() => {
    mockServer = createMockCommandServer()
    global.fetch = mockServer.mockFetch as any
    ardService = new ARDService('http://localhost:5001')
  })

  describe('basic research', () => {
    it('should conduct basic research in <5000ms', async () => {
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

      mockServer.setResponse('call_api', {
        success: true,
        data: {
          content: JSON.stringify([
            {
              insights: ['Insight 1'],
              recommendations: ['Recommendation 1'],
              relevance: 0.8
            }
          ])
        }
      })

      const topic = {
        id: 'topic-1',
        topic: 'Test topic',
        depth: 'basic'
      }

      const startTime = performance.now()
      const result = await ardService.conductResearch(topic)
      const endTime = performance.now()
      const duration = endTime - startTime

      expect(result.success).toBe(true)
      expect(duration).toBeLessThan(5000) // <5000ms
      console.log(`[Benchmark] ARDService basic research: ${duration.toFixed(3)}ms`)
    })
  })

  describe('recursive research', () => {
    it('should conduct recursive research (depth 2) in <15000ms', async () => {
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

      mockServer.setResponse('call_api', {
        success: true,
        data: {
          content: JSON.stringify([
            {
              insights: ['Insight 1'],
              recommendations: ['Recommendation 1'],
              relevance: 0.8
            }
          ])
        }
      })

      const topic = {
        id: 'topic-1',
        topic: 'Test topic',
        depth: 'comprehensive'
      }

      const startTime = performance.now()
      const result = await ardService.recursiveResearch(topic, { maxDepth: 2 })
      const endTime = performance.now()
      const duration = endTime - startTime

      expect(result.success).toBe(true)
      expect(duration).toBeLessThan(15000) // <15000ms
      console.log(`[Benchmark] ARDService recursive research (depth 2): ${duration.toFixed(3)}ms`)
    })
  })
})

