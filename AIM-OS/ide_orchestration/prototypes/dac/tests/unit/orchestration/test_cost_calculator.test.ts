/**
 * Unit Tests: CostCalculator
 * 
 * Tests for cost calculation functionality
 */

import { describe, it, expect } from 'vitest'
import { CostCalculator } from '@services/lucid-chat/orchestration'

describe('CostCalculator', () => {
  describe('calculateCost', () => {
    it('should calculate cost for GPT-4', () => {
      // GPT-4: $30/1M input, $60/1M output
      // 1000 input + 1000 output = $0.09
      const cost = CostCalculator.calculateCost('gpt-4', 1000, 1000)
      expect(cost).toBeCloseTo(0.09, 4)
    })

    it('should calculate cost for Claude 3.5', () => {
      // Claude 3.5: $3/1M input, $15/1M output
      // 1000 input + 1000 output = $0.018
      const cost = CostCalculator.calculateCost('claude-3-5-sonnet-20241022', 1000, 1000)
      expect(cost).toBeCloseTo(0.018, 4)
    })

    it('should calculate cost for GPT-3.5', () => {
      // GPT-3.5: $0.50/1M input, $1.50/1M output
      // 1000 input + 1000 output = $0.002
      const cost = CostCalculator.calculateCost('gpt-3.5-turbo', 1000, 1000)
      expect(cost).toBeCloseTo(0.002, 4)
    })

    it('should return 0 for Cerebras (free)', () => {
      const cost = CostCalculator.calculateCost('llama-3.3-70b', 1000, 1000)
      expect(cost).toBe(0)
    })

    it('should handle zero tokens', () => {
      const cost = CostCalculator.calculateCost('gpt-4', 0, 0)
      expect(cost).toBe(0)
    })

    it('should handle large token counts', () => {
      // 1M tokens for GPT-4
      const cost = CostCalculator.calculateCost('gpt-4', 1_000_000, 0)
      expect(cost).toBe(30) // $30 per 1M input
    })

    it('should use fallback for unknown model', () => {
      // Unknown model should use GPT-3.5 pricing
      const cost = CostCalculator.calculateCost('unknown-model-xyz', 1000, 1000)
      expect(cost).toBeCloseTo(0.002, 4) // GPT-3.5 pricing
    })

    it('should handle fuzzy model matching', () => {
      // "gpt-4-0125-preview" should match "gpt-4"
      const cost = CostCalculator.calculateCost('gpt-4-0125-preview', 1000, 1000)
      expect(cost).toBeCloseTo(0.09, 4) // GPT-4 pricing
    })
  })

  describe('estimateCost', () => {
    it('should estimate cost before execution', () => {
      const cost = CostCalculator.estimateCost('gpt-4', 1000, 500)
      expect(cost).toBeGreaterThan(0)
    })

    it('should match calculateCost for same inputs', () => {
      const estimate = CostCalculator.estimateCost('gpt-4', 1000, 1000)
      const actual = CostCalculator.calculateCost('gpt-4', 1000, 1000)
      expect(estimate).toBe(actual)
    })
  })

  describe('formatCost', () => {
    it('should format small costs as cents', () => {
      const formatted = CostCalculator.formatCost(0.005)
      expect(formatted).toBe('$0.5000¢')
    })

    it('should format larger costs as dollars', () => {
      const formatted = CostCalculator.formatCost(1.5)
      expect(formatted).toBe('$1.5000')
    })

    it('should format zero cost', () => {
      const formatted = CostCalculator.formatCost(0)
      expect(formatted).toBe('$0.0000')
    })
  })

  describe('getAllPricing', () => {
    it('should return all pricing data', () => {
      const pricing = CostCalculator.getAllPricing()
      expect(Object.keys(pricing).length).toBeGreaterThan(10)
    })

    it('should include known models', () => {
      const pricing = CostCalculator.getAllPricing()
      expect(pricing).toHaveProperty('gpt-4')
      expect(pricing).toHaveProperty('claude-3-5-sonnet-20241022')
      expect(pricing).toHaveProperty('gemini-1.5-pro')
    })
  })

  describe('addPricing', () => {
    it('should add custom pricing', () => {
      CostCalculator.addPricing('custom-model', {
        inputPer1M: 5,
        outputPer1M: 10
      })
      
      const cost = CostCalculator.calculateCost('custom-model', 1000, 1000)
      expect(cost).toBeCloseTo(0.015, 4)
    })
  })
})

