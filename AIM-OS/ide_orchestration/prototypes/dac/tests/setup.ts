/**
 * Test Setup File
 * 
 * Global setup for all tests
 */

import { beforeAll, afterAll, afterEach, vi } from 'vitest'

// Mock environment variables
process.env.COMMAND_SERVER_URL = 'http://localhost:5001'
process.env.NODE_ENV = 'test'

// Global mocks
beforeAll(() => {
  // Mock fetch globally
  global.fetch = vi.fn()
})

afterEach(() => {
  // Clear all mocks after each test
  vi.clearAllMocks()
})

afterAll(() => {
  // Cleanup
  vi.restoreAllMocks()
})

