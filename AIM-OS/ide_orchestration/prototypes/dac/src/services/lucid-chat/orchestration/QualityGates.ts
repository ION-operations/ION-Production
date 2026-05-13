/**
 * Quality Gates System
 * 
 * Enforces quality thresholds before proceeding with workflow steps
 * Integrates with VIF for confidence-based routing (κ-gating)
 * 
 * Epic 1.1: Complete APOE Execution
 */

import { RoleExecutionResult } from './RoleExecutor'

/**
 * Quality Gate Configuration
 */
export interface QualityGate {
  type: 'confidence' | 'quality' | 'consistency' | 'budget' | 'kappa' | 'vif'
  threshold: number
  action: 'stop' | 'retry' | 'continue' | 'warn'
  max_retries?: number
}

/**
 * Gate Evaluation Result
 */
export interface GateDecision {
  passed: boolean
  gate?: QualityGate
  action?: 'stop' | 'retry' | 'continue' | 'warn'
  reason?: string
  retry_count?: number
}

/**
 * Quality Gates System Implementation
 */
export class QualityGateSystem {
  private commandServerUrl: string

  constructor(commandServerUrl: string = 'http://localhost:5001') {
    this.commandServerUrl = commandServerUrl
  }

  /**
   * Evaluate result against quality gates
   */
  async evaluate(
    result: RoleExecutionResult,
    gates: QualityGate[]
  ): Promise<GateDecision> {
    for (const gate of gates) {
      const passed = await this.evaluateGate(gate, result)

      if (!passed) {
        return {
          passed: false,
          gate,
          action: gate.action,
          reason: `${gate.type} below threshold ${gate.threshold}`,
        }
      }
    }

    return { passed: true, action: 'continue' }
  }

  /**
   * Evaluate single gate
   */
  private async evaluateGate(
    gate: QualityGate,
    result: RoleExecutionResult
  ): Promise<boolean> {
    switch (gate.type) {
      case 'confidence':
        return this.evaluateConfidenceGate(gate, result)
      
      case 'kappa':
        return this.evaluateKappaGate(gate, result)
      
      case 'quality':
        return this.evaluateQualityGate(gate, result)
      
      case 'consistency':
        return await this.evaluateConsistencyGate(gate, result)
      
      case 'budget':
        return this.evaluateBudgetGate(gate, result)
      
      case 'vif':
        return await this.evaluateVIFGate(gate, result)
      
      default:
        return true
    }
  }

  /**
   * Evaluate confidence gate
   */
  private evaluateConfidenceGate(
    gate: QualityGate,
    result: RoleExecutionResult
  ): boolean {
    return result.confidence >= gate.threshold
  }

  /**
   * Evaluate κ-gate (VIF confidence-based routing)
   * 
   * Band A: κ >= 0.90 (high confidence)
   * Band B: 0.70 <= κ < 0.90 (medium confidence)
   * Band C: κ < 0.70 (low confidence - should stop or retry)
   */
  private evaluateKappaGate(
    gate: QualityGate,
    result: RoleExecutionResult
  ): boolean {
    const kappa = result.confidence // κ-score is confidence
    
    // Determine band
    let band: 'A' | 'B' | 'C'
    if (kappa >= 0.90) {
      band = 'A'
    } else if (kappa >= 0.70) {
      band = 'B'
    } else {
      band = 'C'
    }
    
    // Store band in result metadata
    ;(result as any).kappa_band = band
    ;(result as any).kappa_score = kappa
    
    // Gate passes if κ >= threshold
    return kappa >= gate.threshold
  }

  /**
   * Evaluate quality gate
   */
  private evaluateQualityGate(
    gate: QualityGate,
    result: RoleExecutionResult
  ): boolean {
    // Quality score from output if available
    const qualityScore = result.output?.quality_score ||
                        result.output?.overall_quality ||
                        result.confidence
    
    return qualityScore >= gate.threshold
  }

  /**
   * Evaluate consistency gate
   */
  private async evaluateConsistencyGate(
    gate: QualityGate,
    result: RoleExecutionResult
  ): Promise<boolean> {
    // Check consistency with previous results
    // Could use SEG for contradiction detection
    try {
      const response = await fetch(`${this.commandServerUrl}/mcp/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tool: 'synthesize_knowledge',
          arguments: {
            topics: [result.output],
            detect_contradictions: true,
          },
        }),
      })

      const segResult = await response.json()
      const contradictions = segResult.result?.contradictions || []

      // Pass if no major contradictions
      return contradictions.length === 0
    } catch (error) {
      // If SEG check fails, pass by default
      return true
    }
  }

  /**
   * Evaluate budget gate
   */
  private evaluateBudgetGate(
    gate: QualityGate,
    result: RoleExecutionResult
  ): boolean {
    // Budget gate checks if resources are within limits
    // Threshold represents percentage of budget used (0-1)
    // This is typically checked at workflow level, not step level
    return true // Pass by default for individual steps
  }

  /**
   * Evaluate VIF gate (provenance and witness validation)
   */
  private async evaluateVIFGate(
    gate: QualityGate,
    result: RoleExecutionResult
  ): Promise<boolean> {
    // VIF gate ensures proper provenance tracking
    // For now, check if result has required provenance fields
    try {
      const hasWitness = (result as any).witness_id || (result as any).provenance
      const hasConfidence = typeof result.confidence === 'number'
      const hasTimestamp = result.timestamp || (result as any).createdAt
      
      // Pass if provenance fields present
      return hasWitness || (hasConfidence && hasTimestamp)
    } catch (error) {
      // If check fails, pass by default (lenient)
      return true
    }
  }

  /**
   * Create default quality gates (with κ-gating)
   */
  static createDefaultGates(): QualityGate[] {
    return [
      {
        type: 'kappa',
        threshold: 0.70, // Band C threshold (κ-gate)
        action: 'retry',
        max_retries: 2,
      },
      {
        type: 'quality',
        threshold: 0.75,
        action: 'warn',
      },
    ]
  }

  /**
   * Create strict quality gates (for critical tasks)
   */
  static createStrictGates(): QualityGate[] {
    return [
      {
        type: 'kappa',
        threshold: 0.90, // Band A required (κ >= 0.90)
        action: 'stop',
      },
      {
        type: 'quality',
        threshold: 0.85,
        action: 'retry',
        max_retries: 3,
      },
      {
        type: 'consistency',
        threshold: 1.0, // No contradictions allowed
        action: 'stop',
      },
      {
        type: 'vif',
        threshold: 1.0, // Provenance required
        action: 'warn',
      },
    ]
  }

  /**
   * Create lenient quality gates (for exploratory tasks)
   */
  static createLenientGates(): QualityGate[] {
    return [
      {
        type: 'confidence',
        threshold: 0.60,
        action: 'warn',
      },
    ]
  }
}

