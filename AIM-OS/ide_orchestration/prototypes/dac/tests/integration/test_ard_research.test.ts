/**
 * Integration Tests: ARD Research
 * 
 * Tests for autonomous research workflow
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { ARDService } from '@services/lucid-chat/research/ARDService'
import { createMockCommandServer } from '../../__mocks__/mockCommandServer'

describe('ARD Research Integration', () => {
  let ardService: ARDService
  let mockServer: ReturnType<typeof createMockCommandServer>

  beforeEach(() => {
    mockServer = createMockCommandServer()
    global.fetch = mockServer.mockFetch as any
    ardService = new ARDService('http://localhost:5001')
  })

  describe('basic research workflow', () => {
    it('should conduct research on topic', async () => {
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

      const result = await ardService.conductResearch(topic)

      expect(result.success).toBe(true)
      expect(result.findings.length).toBeGreaterThan(0)
      expect(result.topic).toBe('Test topic')
    })

    it('should integrate with DEEPSEARCH', async () => {
      mockServer.setResponse('deepsearch', {
        success: true,
        data: {
          results: [
            { url: 'http://example.com', title: 'Example', summary: 'Test' }
          ]
        }
      })

      const topic = {
        id: 'topic-1',
        topic: 'Test topic',
        depth: 'basic'
      }

      const result = await ardService.conductResearch(topic)

      expect(result.findings.some(f => f.source === 'deepsearch')).toBe(true)
    })

    it('should integrate with ICIP', async () => {
      mockServer.setResponse('icip_search', {
        success: true,
        data: {
          results: [
            { file: 'test.py', line: 10, code: 'def test(): pass' }
          ]
        }
      })

      const topic = {
        id: 'topic-1',
        topic: 'Test topic',
        depth: 'basic'
      }

      const result = await ardService.conductResearch(topic)

      expect(result.findings.some(f => f.source === 'icip')).toBe(true)
    })
  })

  describe('recursive research', () => {
    it('should conduct recursive research', async () => {
      mockServer.setResponse('deepsearch', {
        success: true,
        data: {
          results: [
            { url: 'http://example.com', title: 'Example', summary: 'Test' }
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

      const result = await ardService.recursiveResearch(topic, { maxDepth: 2 })

      expect(result.success).toBe(true)
      expect(result.depth).toBeGreaterThan(0)
    })
  })

  describe('finding analysis', () => {
    it('should analyze findings with LLM', async () => {
      mockServer.setResponse('call_api', {
        success: true,
        data: {
          content: JSON.stringify([
            {
              insights: ['Key insight 1', 'Key insight 2'],
              recommendations: ['Recommendation 1'],
              relevance: 0.9
            }
          ])
        }
      })

      const findings = [
        {
          id: 'finding-1',
          title: 'Finding 1',
          summary: 'Test finding',
          source: 'deepsearch',
          url: 'http://example.com',
          relevance: 0.8,
          confidence: 0.7,
          insights: [],
          recommendations: []
        }
      ]

      const topic = {
        id: 'topic-1',
        topic: 'Test topic',
        depth: 'basic'
      }

      const analyzed = await (ardService as any).analyzeFindings(findings, topic)

      expect(analyzed.length).toBeGreaterThan(0)
      expect(analyzed[0].insights.length).toBeGreaterThan(0)
    })
  })

  describe('improvement generation', () => {
    it('should generate improvements from findings', async () => {
      mockServer.setResponse('call_api', {
        success: true,
        data: {
          content: JSON.stringify([
            {
              area: 'performance',
              hypothesis: 'Improvement hypothesis',
              reasoning: ['Reason 1'],
              magnitude: 'high',
              effort: 'medium',
              risk: 'low',
              confidence: 0.8
            }
          ])
        }
      })

      const findings = [
        {
          id: 'finding-1',
          title: 'Finding 1',
          summary: 'Test finding',
          source: 'deepsearch',
          url: 'http://example.com',
          relevance: 0.8,
          confidence: 0.7,
          insights: ['Insight 1'],
          recommendations: []
        }
      ]

      const topic = {
        id: 'topic-1',
        topic: 'Test topic',
        depth: 'basic'
      }

      const improvements = await (ardService as any).generateImprovements(findings, topic)

      expect(improvements.length).toBeGreaterThan(0)
      expect(improvements[0].hypothesis).toBeDefined()
      expect(improvements[0].confidence).toBeGreaterThan(0)
    })
  })
})

