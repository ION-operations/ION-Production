/**
 * Unit Tests: TokenCounter
 * 
 * Tests for token estimation functionality
 */

import { describe, it, expect } from 'vitest'
import { TokenCounter } from '@services/lucid-chat/orchestration'

describe('TokenCounter', () => {
  describe('estimate', () => {
    it('should return 0 for empty string', () => {
      expect(TokenCounter.estimate('')).toBe(0)
    })

    it('should return 0 for null/undefined', () => {
      expect(TokenCounter.estimate(null as any)).toBe(0)
      expect(TokenCounter.estimate(undefined as any)).toBe(0)
    })

    it('should estimate tokens for short text', () => {
      // "Hello world" = 11 chars / 4 = 3 tokens
      expect(TokenCounter.estimate('Hello world')).toBe(3)
    })

    it('should estimate tokens for long text', () => {
      // 100 chars / 4 = 25 tokens
      const text = 'a'.repeat(100)
      expect(TokenCounter.estimate(text)).toBe(25)
    })

    it('should round up for partial tokens', () => {
      // 5 chars / 4 = 1.25, rounds up to 2
      expect(TokenCounter.estimate('12345')).toBe(2)
    })

    it('should handle whitespace correctly', () => {
      const text = 'Hello   world   with   spaces'
      expect(TokenCounter.estimate(text)).toBeGreaterThan(0)
    })
  })

  describe('estimateMessages', () => {
    it('should return 0 for empty array', () => {
      expect(TokenCounter.estimateMessages([])).toBe(0)
    })

    it('should estimate single message', () => {
      const messages = [
        { role: 'user', content: 'Hello' }
      ]
      // "Hello" = 5 chars / 4 = 2 tokens + 4 overhead = 6
      expect(TokenCounter.estimateMessages(messages)).toBe(6)
    })

    it('should estimate multiple messages', () => {
      const messages = [
        { role: 'user', content: 'Hello' },
        { role: 'assistant', content: 'Hi there' }
      ]
      // Message 1: 2 + 4 = 6
      // Message 2: 3 + 4 = 7
      // Total: 13
      expect(TokenCounter.estimateMessages(messages)).toBe(13)
    })

    it('should add overhead for each message', () => {
      const messages = [
        { role: 'user', content: 'A' },
        { role: 'assistant', content: 'B' },
        { role: 'user', content: 'C' }
      ]
      // Each message adds 4 tokens overhead
      // 3 messages * 4 = 12 overhead
      // Plus content tokens
      const result = TokenCounter.estimateMessages(messages)
      expect(result).toBeGreaterThanOrEqual(12)
    })
  })

  describe('estimateRequest', () => {
    it('should estimate from messages', () => {
      const data = {
        messages: [
          { role: 'user', content: 'Hello' }
        ]
      }
      const result = TokenCounter.estimateRequest(data)
      expect(result.input).toBeGreaterThan(0)
      expect(result.estimated_output).toBe(100) // Default
    })

    it('should include system prompt', () => {
      const data = {
        messages: [{ role: 'user', content: 'Hello' }],
        system: 'You are a helpful assistant'
      }
      const result = TokenCounter.estimateRequest(data)
      expect(result.input).toBeGreaterThan(0)
    })

    it('should use max_tokens if provided', () => {
      const data = {
        messages: [{ role: 'user', content: 'Hello' }],
        max_tokens: 500
      }
      const result = TokenCounter.estimateRequest(data)
      expect(result.estimated_output).toBe(500)
    })

    it('should handle missing fields gracefully', () => {
      const result = TokenCounter.estimateRequest({})
      expect(result.input).toBe(0)
      expect(result.estimated_output).toBe(100)
    })
  })

  describe('countResponse', () => {
    it('should count tokens in response', () => {
      const content = 'This is a response'
      const tokens = TokenCounter.countResponse(content)
      expect(tokens).toBeGreaterThan(0)
    })

    it('should return 0 for empty response', () => {
      expect(TokenCounter.countResponse('')).toBe(0)
    })

    it('should match estimate for same text', () => {
      const text = 'Hello world'
      const estimate = TokenCounter.estimate(text)
      const count = TokenCounter.countResponse(text)
      expect(count).toBe(estimate)
    })
  })
})

