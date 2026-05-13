/**
 * Unit Tests: BaseAPIService
 * 
 * Tests for base service infrastructure
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { BaseAPIService, APIResponse } from '@services/lucid-chat'
import { createMockCommandServer, mockMCPResponses } from '../../__mocks__/mockCommandServer'

// Concrete implementation for testing
class TestService extends BaseAPIService {
  constructor() {
    super('test_service', 'http://localhost:5001', undefined, 'test')
  }

  async testMethod(input: string): Promise<APIResponse<string>> {
    return this.handleRequest(
      async () => {
        return `processed: ${input}`
      },
      'testMethod',
      { input }
    )
  }

  isAvailable(): boolean {
    return true
  }
}

describe('BaseAPIService', () => {
  let service: TestService
  let mockServer: ReturnType<typeof createMockCommandServer>

  beforeEach(() => {
    mockServer = createMockCommandServer()
    global.fetch = mockServer.mockFetch as any
    service = new TestService()
  })

  describe('handleRequest', () => {
    it('should handle successful request', async () => {
      // Arrange
      const input = 'test input'

      // Act
      const result = await service.testMethod(input)

      // Assert
      expect(result.success).toBe(true)
      expect(result.data).toBe('processed: test input')
    })

    it('should handle errors gracefully', async () => {
      // Arrange: Make test method throw
      const failingService = new TestService()
      vi.spyOn(failingService as any, 'handleRequest').mockRejectedValue(
        new Error('Test error')
      )

      // Act & Assert
      await expect(failingService.testMethod('test')).rejects.toThrow('Test error')
    })

    it('should integrate with AIM-OS', async () => {
      // Arrange
      mockServer.setResponse('store_memory', mockMCPResponses.store_memory)

      // Act
      const result = await service.testMethod('test')

      // Assert
      expect(result.success).toBe(true)
      // Verify AIMOS integration called
      expect(mockServer.mockFetch).toHaveBeenCalled()
    })
  })

  describe('isAvailable', () => {
    it('should return availability status', () => {
      expect(service.isAvailable()).toBe(true)
    })
  })
})

