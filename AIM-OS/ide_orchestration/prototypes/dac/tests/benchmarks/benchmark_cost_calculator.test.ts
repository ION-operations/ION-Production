/**
 * Performance Benchmarks: CostCalculator
 * 
 * Benchmarks for cost calculation performance
 */

import { describe, it, expect } from 'vitest'
import { CostCalculator } from '@services/lucid-chat/orchestration'

describe('CostCalculator Performance Benchmarks', () => {
  describe('calculateCost performance', () => {
    it('should calculate cost in <0.1ms', () => {
      const iterations = 10000
      const startTime = performance.now()

      for (let i = 0; i < iterations; i++) {
        CostCalculator.calculateCost('gpt-3.5-turbo', 1000, 1000)
      }

      const endTime = performance.now()
      const avgTime = (endTime - startTime) / iterations

      expect(avgTime).toBeLessThan(0.1) // <0.1ms average
      console.log(`[Benchmark] calculateCost() average: ${avgTime.toFixed(4)}ms (${iterations} iterations)`)
    })

    it('should handle multiple models efficiently', () => {
      const models = ['gpt-4', 'claude-3-5-sonnet-20241022', 'gemini-1.5-pro', 'gpt-3.5-turbo']
      const iterations = 1000
      const startTime = performance.now()

      for (let i = 0; i < iterations; i++) {
        const model = models[i % models.length]
        CostCalculator.calculateCost(model, 1000, 1000)
      }

      const endTime = performance.now()
      const avgTime = (endTime - startTime) / iterations

      expect(avgTime).toBeLessThan(0.2) // <0.2ms average (slightly higher due to model lookup)
      console.log(`[Benchmark] calculateCost() multiple models average: ${avgTime.toFixed(4)}ms (${iterations} iterations)`)
    })
  })

  describe('formatCost performance', () => {
    it('should format cost in <0.1ms', () => {
      const costs = [0.001, 0.01, 0.1, 1.0, 10.0, 100.0]
      const iterations = 10000
      const startTime = performance.now()

      for (let i = 0; i < iterations; i++) {
        const cost = costs[i % costs.length]
        CostCalculator.formatCost(cost)
      }

      const endTime = performance.now()
      const avgTime = (endTime - startTime) / iterations

      expect(avgTime).toBeLessThan(0.1) // <0.1ms average
      console.log(`[Benchmark] formatCost() average: ${avgTime.toFixed(4)}ms (${iterations} iterations)`)
    })
  })
})

