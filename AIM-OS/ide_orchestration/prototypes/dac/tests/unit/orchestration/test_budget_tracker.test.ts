/**
 * Unit Tests: BudgetTracker
 * 
 * Tests for budget tracking and enforcement
 */

import { describe, it, expect, beforeEach } from 'vitest'
import { BudgetTracker, Budget } from '@services/lucid-chat/orchestration'
import { RoleExecutionResult } from '@services/lucid-chat/orchestration'

describe('BudgetTracker', () => {
  let tracker: BudgetTracker
  let budget: Budget

  beforeEach(() => {
    budget = {
      tokens: 1000,
      time: 60,
      cost: 1.0
    }
    tracker = new BudgetTracker(budget)
  })

  describe('constructor', () => {
    it('should initialize with budget', () => {
      expect(tracker).toBeDefined()
      const status = tracker.getStatus()
      expect(status.budget).toEqual(budget)
      expect(status.usage.tokens).toBe(0)
      expect(status.usage.time).toBe(0)
      expect(status.usage.cost).toBe(0)
    })

    it('should handle partial budget', () => {
      const partialBudget: Budget = { tokens: 1000 }
      const partialTracker = new BudgetTracker(partialBudget)
      const status = partialTracker.getStatus()
      expect(status.budget.tokens).toBe(1000)
      expect(status.budget.time).toBeUndefined()
    })
  })

  describe('trackStep', () => {
    it('should update token usage', () => {
      const step: RoleExecutionResult = {
        success: true,
        confidence: 0.8,
        tokensUsed: 100,
        latencyMs: 1000,
        model: 'gpt-3.5-turbo'
      } as any

      tracker.trackStep(step)
      const status = tracker.getStatus()
      expect(status.usage.tokens).toBe(100)
    })

    it('should update time usage', () => {
      const step: RoleExecutionResult = {
        success: true,
        confidence: 0.8,
        tokensUsed: 0,
        latencyMs: 2000, // 2 seconds
        model: 'gpt-3.5-turbo'
      } as any

      tracker.trackStep(step)
      const status = tracker.getStatus()
      expect(status.usage.time).toBe(2)
    })

    it('should calculate cost correctly', () => {
      const step: RoleExecutionResult = {
        success: true,
        confidence: 0.8,
        tokensUsed: 1000,
        inputTokens: 400,
        outputTokens: 600,
        model: 'gpt-3.5-turbo',
        latencyMs: 1000
      } as any

      tracker.trackStep(step)
      const status = tracker.getStatus()
      expect(status.usage.cost).toBeGreaterThan(0)
    })

    it('should accumulate multiple steps', () => {
      const step1: RoleExecutionResult = {
        success: true,
        confidence: 0.8,
        tokensUsed: 100,
        latencyMs: 1000,
        model: 'gpt-3.5-turbo'
      } as any

      const step2: RoleExecutionResult = {
        success: true,
        confidence: 0.8,
        tokensUsed: 200,
        latencyMs: 2000,
        model: 'gpt-3.5-turbo'
      } as any

      tracker.trackStep(step1)
      tracker.trackStep(step2)
      const status = tracker.getStatus()
      expect(status.usage.tokens).toBe(300)
      expect(status.usage.time).toBe(3)
    })
  })

  describe('isExceeded', () => {
    it('should return false when under budget', () => {
      expect(tracker.isExceeded()).toBe(false)
    })

    it('should return true when tokens exceeded', () => {
      const step: RoleExecutionResult = {
        success: true,
        confidence: 0.8,
        tokensUsed: 1500, // Exceeds 1000 limit
        latencyMs: 1000,
        model: 'gpt-3.5-turbo'
      } as any

      tracker.trackStep(step)
      expect(tracker.isExceeded()).toBe(true)
    })

    it('should return true when time exceeded', () => {
      const step: RoleExecutionResult = {
        success: true,
        confidence: 0.8,
        tokensUsed: 0,
        latencyMs: 65000, // 65 seconds, exceeds 60 limit
        model: 'gpt-3.5-turbo'
      } as any

      tracker.trackStep(step)
      expect(tracker.isExceeded()).toBe(true)
    })

    it('should return true when cost exceeded', () => {
      const step: RoleExecutionResult = {
        success: true,
        confidence: 0.8,
        tokensUsed: 100000, // Large token count
        inputTokens: 50000,
        outputTokens: 50000,
        model: 'gpt-4', // Expensive model
        latencyMs: 1000
      } as any

      tracker.trackStep(step)
      expect(tracker.isExceeded()).toBe(true)
    })
  })

  describe('getStatus', () => {
    it('should return correct structure', () => {
      const status = tracker.getStatus()
      expect(status).toHaveProperty('exceeded')
      expect(status).toHaveProperty('remaining')
      expect(status).toHaveProperty('usage')
      expect(status).toHaveProperty('budget')
      expect(status).toHaveProperty('warnings')
      expect(status).toHaveProperty('percentage')
    })

    it('should calculate remaining correctly', () => {
      const step: RoleExecutionResult = {
        success: true,
        confidence: 0.8,
        tokensUsed: 300,
        latencyMs: 10000,
        model: 'gpt-3.5-turbo'
      } as any

      tracker.trackStep(step)
      const status = tracker.getStatus()
      expect(status.remaining.tokens).toBe(700) // 1000 - 300
      expect(status.remaining.time).toBe(50) // 60 - 10
    })

    it('should calculate percentages correctly', () => {
      const step: RoleExecutionResult = {
        success: true,
        confidence: 0.8,
        tokensUsed: 500,
        latencyMs: 30000,
        model: 'gpt-3.5-turbo'
      } as any

      tracker.trackStep(step)
      const status = tracker.getStatus()
      expect(status.percentage.tokens).toBe(50) // 500/1000 * 100
      expect(status.percentage.time).toBe(50) // 30/60 * 100
    })
  })

  describe('warnings', () => {
    it('should generate warning at 80%', () => {
      const step: RoleExecutionResult = {
        success: true,
        confidence: 0.8,
        tokensUsed: 850, // 85% of 1000
        latencyMs: 1000,
        model: 'gpt-3.5-turbo'
      } as any

      tracker.trackStep(step)
      const warnings = tracker.getWarnings()
      expect(warnings.length).toBeGreaterThan(0)
      expect(warnings.some(w => w.includes('80'))).toBe(true)
    })

    it('should generate exceeded warning', () => {
      const step: RoleExecutionResult = {
        success: true,
        confidence: 0.8,
        tokensUsed: 1500, // Exceeds limit
        latencyMs: 1000,
        model: 'gpt-3.5-turbo'
      } as any

      tracker.trackStep(step)
      const warnings = tracker.getWarnings()
      expect(warnings.some(w => w.includes('EXCEEDED'))).toBe(true)
    })
  })

  describe('reset', () => {
    it('should clear usage', () => {
      const step: RoleExecutionResult = {
        success: true,
        confidence: 0.8,
        tokensUsed: 500,
        latencyMs: 10000,
        model: 'gpt-3.5-turbo'
      } as any

      tracker.trackStep(step)
      tracker.reset()
      
      const status = tracker.getStatus()
      expect(status.usage.tokens).toBe(0)
      expect(status.usage.time).toBe(0)
      expect(status.usage.cost).toBe(0)
      expect(status.warnings.length).toBe(0)
    })
  })

  describe('getSummary', () => {
    it('should format summary correctly', () => {
      const step: RoleExecutionResult = {
        success: true,
        confidence: 0.8,
        tokensUsed: 500,
        latencyMs: 30000,
        model: 'gpt-3.5-turbo'
      } as any

      tracker.trackStep(step)
      const summary = tracker.getSummary()
      
      expect(summary).toContain('Budget Usage')
      expect(summary).toContain('Tokens')
      expect(summary).toContain('Time')
      expect(summary).toContain('Cost')
    })
  })
})

