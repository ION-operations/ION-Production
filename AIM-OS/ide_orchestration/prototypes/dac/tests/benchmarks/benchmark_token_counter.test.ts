/**
 * Performance Benchmarks: TokenCounter
 * 
 * Benchmarks for token estimation performance
 */

import { describe, it, expect } from 'vitest'
import { TokenCounter } from '@services/lucid-chat/orchestration'

describe('TokenCounter Performance Benchmarks', () => {
  describe('estimate performance', () => {
    it('should estimate 1KB text in <1ms', () => {
      const text = 'a'.repeat(1024) // 1KB
      const iterations = 1000
      const startTime = performance.now()

      for (let i = 0; i < iterations; i++) {
        TokenCounter.estimate(text)
      }

      const endTime = performance.now()
      const avgTime = (endTime - startTime) / iterations

      expect(avgTime).toBeLessThan(1) // <1ms average
      console.log(`[Benchmark] estimate() average: ${avgTime.toFixed(3)}ms (${iterations} iterations)`)
    })

    it('should estimate 10KB text in <5ms', () => {
      const text = 'a'.repeat(10 * 1024) // 10KB
      const iterations = 100
      const startTime = performance.now()

      for (let i = 0; i < iterations; i++) {
        TokenCounter.estimate(text)
      }

      const endTime = performance.now()
      const avgTime = (endTime - startTime) / iterations

      expect(avgTime).toBeLessThan(5) // <5ms average
      console.log(`[Benchmark] estimate() 10KB average: ${avgTime.toFixed(3)}ms (${iterations} iterations)`)
    })
  })

  describe('estimateMessages performance', () => {
    it('should estimate 100 messages in <5ms', () => {
      const messages = Array.from({ length: 100 }, (_, i) => ({
        role: i % 2 === 0 ? 'user' : 'assistant',
        content: `Message ${i}: ${'a'.repeat(50)}`
      }))

      const iterations = 100
      const startTime = performance.now()

      for (let i = 0; i < iterations; i++) {
        TokenCounter.estimateMessages(messages)
      }

      const endTime = performance.now()
      const avgTime = (endTime - startTime) / iterations

      expect(avgTime).toBeLessThan(5) // <5ms average
      console.log(`[Benchmark] estimateMessages() 100 messages average: ${avgTime.toFixed(3)}ms (${iterations} iterations)`)
    })
  })

  describe('estimateRequest performance', () => {
    it('should estimate request in <2ms', () => {
      const data = {
        messages: Array.from({ length: 10 }, (_, i) => ({
          role: i % 2 === 0 ? 'user' : 'assistant',
          content: `Message ${i}: ${'a'.repeat(100)}`
        })),
        system: 'You are a helpful assistant',
        max_tokens: 500
      }

      const iterations = 500
      const startTime = performance.now()

      for (let i = 0; i < iterations; i++) {
        TokenCounter.estimateRequest(data)
      }

      const endTime = performance.now()
      const avgTime = (endTime - startTime) / iterations

      expect(avgTime).toBeLessThan(2) // <2ms average
      console.log(`[Benchmark] estimateRequest() average: ${avgTime.toFixed(3)}ms (${iterations} iterations)`)
    })
  })
})

