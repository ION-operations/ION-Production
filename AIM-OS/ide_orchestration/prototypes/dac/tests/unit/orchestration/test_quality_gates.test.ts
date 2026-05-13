/**
 * Unit Tests: QualityGates
 * 
 * Tests for quality gate evaluation and enforcement
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { QualityGateSystem, QualityGate } from '@services/lucid-chat/orchestration'
import { RoleExecutionResult } from '@services/lucid-chat/orchestration'

describe('QualityGateSystem', () => {
  let gateSystem: QualityGateSystem
  let mockFetch: any

  beforeEach(() => {
    gateSystem = new QualityGateSystem('http://localhost:5001')
    mockFetch = vi.fn()
    global.fetch = mockFetch
  })

  describe('evaluate - confidence gate', () => {
    it('should pass when confidence meets threshold', async () => {
      const result: RoleExecutionResult = {
        success: true,
        confidence: 0.80,
        tokensUsed: 100
      }

      const gates: QualityGate[] = [
        { type: 'confidence', threshold: 0.70, action: 'stop' }
      ]

      const decision = await gateSystem.evaluate(result, gates)
      expect(decision.passed).toBe(true)
      expect(decision.action).toBe('continue')
    })

    it('should fail when confidence below threshold', async () => {
      const result: RoleExecutionResult = {
        success: true,
        confidence: 0.60,
        tokensUsed: 100
      }

      const gates: QualityGate[] = [
        { type: 'confidence', threshold: 0.70, action: 'stop' }
      ]

      const decision = await gateSystem.evaluate(result, gates)
      expect(decision.passed).toBe(false)
      expect(decision.action).toBe('stop')
      expect(decision.reason).toContain('confidence')
    })
  })

  describe('evaluate - kappa gate', () => {
    it('should classify Band A (κ >= 0.90)', async () => {
      const result: RoleExecutionResult = {
        success: true,
        confidence: 0.95, // Band A
        tokensUsed: 100
      } as any

      const gates: QualityGate[] = [
        { type: 'kappa', threshold: 0.90, action: 'continue' }
      ]

      const decision = await gateSystem.evaluate(result, gates)
      expect(decision.passed).toBe(true)
      expect((result as any).kappa_band).toBe('A')
      expect((result as any).kappa_score).toBe(0.95)
    })

    it('should classify Band B (0.70 <= κ < 0.90)', async () => {
      const result: RoleExecutionResult = {
        success: true,
        confidence: 0.80, // Band B
        tokensUsed: 100
      } as any

      const gates: QualityGate[] = [
        { type: 'kappa', threshold: 0.70, action: 'continue' }
      ]

      const decision = await gateSystem.evaluate(result, gates)
      expect(decision.passed).toBe(true)
      expect((result as any).kappa_band).toBe('B')
    })

    it('should classify Band C (κ < 0.70)', async () => {
      const result: RoleExecutionResult = {
        success: true,
        confidence: 0.60, // Band C
        tokensUsed: 100
      } as any

      const gates: QualityGate[] = [
        { type: 'kappa', threshold: 0.70, action: 'retry' }
      ]

      const decision = await gateSystem.evaluate(result, gates)
      expect(decision.passed).toBe(false)
      expect((result as any).kappa_band).toBe('C')
      expect(decision.action).toBe('retry')
    })
  })

  describe('evaluate - quality gate', () => {
    it('should pass when quality score meets threshold', async () => {
      const result: RoleExecutionResult = {
        success: true,
        confidence: 0.80,
        tokensUsed: 100,
        output: { quality_score: 0.85 }
      } as any

      const gates: QualityGate[] = [
        { type: 'quality', threshold: 0.75, action: 'continue' }
      ]

      const decision = await gateSystem.evaluate(result, gates)
      expect(decision.passed).toBe(true)
    })

    it('should use confidence as fallback for quality', async () => {
      const result: RoleExecutionResult = {
        success: true,
        confidence: 0.80,
        tokensUsed: 100,
        output: {} // No quality_score
      } as any

      const gates: QualityGate[] = [
        { type: 'quality', threshold: 0.75, action: 'continue' }
      ]

      const decision = await gateSystem.evaluate(result, gates)
      expect(decision.passed).toBe(true) // Uses confidence 0.80
    })
  })

  describe('evaluate - consistency gate', () => {
    it('should pass when SEG finds no contradictions', async () => {
      mockFetch.mockResolvedValueOnce({
        json: async () => ({
          result: { contradictions: [] }
        })
      })

      const result: RoleExecutionResult = {
        success: true,
        confidence: 0.80,
        tokensUsed: 100,
        output: { content: 'test' }
      } as any

      const gates: QualityGate[] = [
        { type: 'consistency', threshold: 1.0, action: 'stop' }
      ]

      const decision = await gateSystem.evaluate(result, gates)
      expect(decision.passed).toBe(true)
    })

    it('should fail when SEG finds contradictions', async () => {
      mockFetch.mockResolvedValueOnce({
        json: async () => ({
          result: { contradictions: ['contradiction1'] }
        })
      })

      const result: RoleExecutionResult = {
        success: true,
        confidence: 0.80,
        tokensUsed: 100,
        output: { content: 'test' }
      } as any

      const gates: QualityGate[] = [
        { type: 'consistency', threshold: 1.0, action: 'stop' }
      ]

      const decision = await gateSystem.evaluate(result, gates)
      expect(decision.passed).toBe(false)
    })

    it('should pass by default if SEG check fails', async () => {
      mockFetch.mockRejectedValueOnce(new Error('SEG unavailable'))

      const result: RoleExecutionResult = {
        success: true,
        confidence: 0.80,
        tokensUsed: 100
      } as any

      const gates: QualityGate[] = [
        { type: 'consistency', threshold: 1.0, action: 'stop' }
      ]

      const decision = await gateSystem.evaluate(result, gates)
      expect(decision.passed).toBe(true) // Lenient fallback
    })
  })

  describe('evaluate - VIF gate', () => {
    it('should pass when provenance fields present', async () => {
      const result: RoleExecutionResult = {
        success: true,
        confidence: 0.80,
        tokensUsed: 100,
        timestamp: Date.now(),
        witness_id: 'witness-123'
      } as any

      const gates: QualityGate[] = [
        { type: 'vif', threshold: 1.0, action: 'warn' }
      ]

      const decision = await gateSystem.evaluate(result, gates)
      expect(decision.passed).toBe(true)
    })

    it('should pass when confidence and timestamp present', async () => {
      const result: RoleExecutionResult = {
        success: true,
        confidence: 0.80,
        tokensUsed: 100,
        timestamp: Date.now()
      } as any

      const gates: QualityGate[] = [
        { type: 'vif', threshold: 1.0, action: 'warn' }
      ]

      const decision = await gateSystem.evaluate(result, gates)
      expect(decision.passed).toBe(true)
    })

    it('should pass by default (lenient)', async () => {
      const result: RoleExecutionResult = {
        success: true,
        tokensUsed: 100
      } as any

      const gates: QualityGate[] = [
        { type: 'vif', threshold: 1.0, action: 'warn' }
      ]

      const decision = await gateSystem.evaluate(result, gates)
      expect(decision.passed).toBe(true) // Lenient fallback
    })
  })

  describe('evaluate - multiple gates', () => {
    it('should pass when all gates pass', async () => {
      const result: RoleExecutionResult = {
        success: true,
        confidence: 0.85,
        tokensUsed: 100,
        output: { quality_score: 0.90 }
      } as any

      const gates: QualityGate[] = [
        { type: 'confidence', threshold: 0.70, action: 'stop' },
        { type: 'quality', threshold: 0.75, action: 'stop' }
      ]

      const decision = await gateSystem.evaluate(result, gates)
      expect(decision.passed).toBe(true)
    })

    it('should fail on first failing gate', async () => {
      const result: RoleExecutionResult = {
        success: true,
        confidence: 0.60, // Fails first gate
        tokensUsed: 100,
        output: { quality_score: 0.90 } // Would pass second gate
      } as any

      const gates: QualityGate[] = [
        { type: 'confidence', threshold: 0.70, action: 'stop' },
        { type: 'quality', threshold: 0.75, action: 'stop' }
      ]

      const decision = await gateSystem.evaluate(result, gates)
      expect(decision.passed).toBe(false)
      expect(decision.gate?.type).toBe('confidence')
    })
  })

  describe('createDefaultGates', () => {
    it('should create gates with κ-gate', () => {
      const gates = QualityGateSystem.createDefaultGates()
      expect(gates.length).toBeGreaterThan(0)
      expect(gates.some(g => g.type === 'kappa')).toBe(true)
    })
  })

  describe('createStrictGates', () => {
    it('should create strict gates with Band A requirement', () => {
      const gates = QualityGateSystem.createStrictGates()
      const kappaGate = gates.find(g => g.type === 'kappa')
      expect(kappaGate?.threshold).toBe(0.90) // Band A
      expect(kappaGate?.action).toBe('stop')
    })

    it('should include VIF gate', () => {
      const gates = QualityGateSystem.createStrictGates()
      expect(gates.some(g => g.type === 'vif')).toBe(true)
    })
  })

  describe('createLenientGates', () => {
    it('should create lenient gates with lower threshold', () => {
      const gates = QualityGateSystem.createLenientGates()
      expect(gates.length).toBeGreaterThan(0)
      const confidenceGate = gates.find(g => g.type === 'confidence')
      expect(confidenceGate?.threshold).toBe(0.60) // Lower threshold
    })
  })
})

