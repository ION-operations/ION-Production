/**
 * Unit Tests: LLMService
 * 
 * Tests for LLM service functionality
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { LLMService } from '@services/lucid-chat'
import { createMockCommandServer } from '../../__mocks__/mockCommandServer'

describe('LLMService', () => {
  let service: LLMService
  let mockServer: ReturnType<typeof createMockCommandServer>

  beforeEach(() => {
    mockServer = createMockCommandServer()
    global.fetch = mockServer.mockFetch as any
    service = new LLMService()
  })

  describe('chatCompletion', () => {
    it('should complete chat request successfully', async () => {
      // Arrange
      mockServer.setResponse('call_api', {
        success: true,
        data: {
          content: 'Hello! How can I help?',
          model: 'claude-3-5-sonnet-20241022',
        },
      })

      // Act
      const result = await service.chatCompletion({
        provider: 'anthropic',
        messages: [{ role: 'user', content: 'Hello' }],
      })

      // Assert
      expect(result.success).toBe(true)
      expect(result.data?.text).toBeDefined()
      expect(mockServer.mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/mcp/execute'),
        expect.objectContaining({
          method: 'POST',
        })
      )
    })

    it('should handle different providers', async () => {
      // Test anthropic
      const anthropic = await service.chatCompletion({
        provider: 'anthropic',
        messages: [{ role: 'user', content: 'Test' }],
      })
      expect(mockServer.mockFetch).toHaveBeenCalled()

      // Test openai
      const openai = await service.chatCompletion({
        provider: 'openai',
        messages: [{ role: 'user', content: 'Test' }],
      })
      expect(mockServer.mockFetch).toHaveBeenCalled()
    })

    it('should handle temperature parameter', async () => {
      await service.chatCompletion({
        provider: 'anthropic',
        messages: [{ role: 'user', content: 'Test' }],
        temperature: 0.8,
      })

      // Verify temperature was passed
      const calls = mockServer.mockFetch.mock.calls
      const lastCall = calls[calls.length - 1]
      const body = JSON.parse(lastCall[1].body)
      expect(body.arguments.data.temperature).toBe(0.8)
    })

    it('should handle errors from API', async () => {
      // Arrange: Mock error response
      mockServer.setResponse('call_api', {
        success: false,
        error: 'API error',
      })

      // Act
      const result = await service.chatCompletion({
        provider: 'anthropic',
        messages: [{ role: 'user', content: 'Test' }],
      })

      // Assert
      expect(result.success).toBe(false)
      expect(result.error).toBeDefined()
    })
  })

  describe('complete', () => {
    it('should complete text prompt', async () => {
      mockServer.setResponse('call_api', {
        success: true,
        data: { content: 'Completion result' },
      })

      const result = await service.complete(
        'Test prompt',
        'anthropic',
        undefined,
        0.7,
        1000
      )

      expect(result.success).toBe(true)
      expect(result.data?.text).toBeDefined()
    })
  })

  describe('isAvailable', () => {
    it('should return true (always available)', () => {
      expect(service.isAvailable()).toBe(true)
    })
  })
})

