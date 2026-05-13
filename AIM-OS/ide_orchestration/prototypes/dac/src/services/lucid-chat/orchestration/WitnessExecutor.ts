/**
 * Witness Role Executor
 * 
 * Specializes in provenance capture and audit trail creation
 * Temperature: 0.0 (deterministic witnessing)
 * 
 * Epic 1.1: Complete APOE Execution
 */

import { RoleExecutor, RoleContext, RoleExecutionResult } from './RoleExecutor'
import { LLMService } from '../llm/LLMService'

/**
 * Witness Record Structure (VIF Compatible)
 */
export interface WitnessRecord {
  witness_id: string
  timestamp: string
  workflow_id: string
  goal: string
  steps_executed: Array<{
    role: string
    input: any
    output: any
    confidence: number
    tokens_used: number
    latency_ms: number
  }>
  total_tokens: number
  total_time: number
  total_cost: number
  final_confidence: number
  provenance: {
    models_used: string[]
    providers_used: string[]
    tools_used: string[]
    data_sources: string[]
  }
  audit_trail: string
}

/**
 * Witness Executor Implementation
 */
export class WitnessExecutor extends RoleExecutor {
  constructor(llmService: LLMService, commandServerUrl?: string) {
    super(
      {
        role: 'witness',
      },
      llmService,
      commandServerUrl
    )
  }

  async execute(
    input: any,
    context: RoleContext
  ): Promise<RoleExecutionResult> {
    this.validateInput(input)
    this.validateContext(context)

    const startTime = Date.now()

    try {
      // Create witness record
      const witnessRecord = this.createWitnessRecord(input, context)

      // Store witness in VIF
      await this.storeWitness(witnessRecord)

      // Build result
      const result: RoleExecutionResult = {
        role: 'witness',
        input,
        output: witnessRecord,
        success: true,
        confidence: 1.0, // Witnessing is always certain
        tokensUsed: 0, // Witnessing doesn't use LLM tokens
        latencyMs: Date.now() - startTime,
        reasoning: 'Created complete provenance record',
        metadata: {
          witness_id: witnessRecord.witness_id,
          steps_witnessed: witnessRecord.steps_executed.length,
        },
      }

      // Track with VIF
      await this.trackExecution(result)

      // Store in CMC
      await this.storeResult(result, context)

      return result
    } catch (error: any) {
      return {
        role: 'witness',
        input,
        output: null,
        success: false,
        confidence: 0,
        tokensUsed: 0,
        latencyMs: Date.now() - startTime,
        error: error.message,
      }
    }
  }

  /**
   * Create witness record from workflow execution
   */
  private createWitnessRecord(
    input: any,
    context: RoleContext
  ): WitnessRecord {
    const workflowExecution = input.workflow_execution
    const steps = context.previousSteps || []

    // Calculate totals
    const totalTokens = steps.reduce((sum, s) => sum + s.tokensUsed, 0)
    const totalTime = steps.reduce((sum, s) => sum + s.latencyMs, 0)
    const totalCost = this.calculateTotalCost(steps)
    const finalConfidence = this.calculateFinalConfidence(steps)

    // Extract provenance info
    const modelsUsed = new Set(steps.map(s => s.metadata?.model).filter(Boolean))
    const providersUsed = new Set(steps.map(s => s.metadata?.provider).filter(Boolean))
    const toolsUsed = new Set(steps.map(s => s.metadata?.tool).filter(Boolean))

    // Build audit trail
    const auditTrail = this.buildAuditTrail(steps, context)

    return {
      witness_id: `witness_${Date.now()}_${Math.random().toString(36).slice(2)}`,
      timestamp: new Date().toISOString(),
      workflow_id: workflowExecution?.id || 'unknown',
      goal: context.goal,
      steps_executed: steps.map(s => ({
        role: s.role,
        input: s.input,
        output: s.output,
        confidence: s.confidence,
        tokens_used: s.tokensUsed,
        latency_ms: s.latencyMs,
      })),
      total_tokens: totalTokens,
      total_time: totalTime,
      total_cost: totalCost,
      final_confidence: finalConfidence,
      provenance: {
        models_used: Array.from(modelsUsed),
        providers_used: Array.from(providersUsed),
        tools_used: Array.from(toolsUsed),
        data_sources: ['CMC', 'HHNI', 'LLM'],
      },
      audit_trail: auditTrail,
    }
  }

  /**
   * Calculate total cost
   */
  private calculateTotalCost(steps: RoleExecutionResult[]): number {
    // Rough estimation: $0.01 per 1000 tokens
    const totalTokens = steps.reduce((sum, s) => sum + s.tokensUsed, 0)
    return (totalTokens / 1000) * 0.01
  }

  /**
   * Calculate final confidence
   */
  private calculateFinalConfidence(steps: RoleExecutionResult[]): number {
    if (steps.length === 0) return 0.5
    
    // Weighted average (later steps weighted more)
    let weightedSum = 0
    let totalWeight = 0
    
    steps.forEach((step, i) => {
      const weight = i + 1 // Later steps get more weight
      weightedSum += step.confidence * weight
      totalWeight += weight
    })
    
    return weightedSum / totalWeight
  }

  /**
   * Build audit trail
   */
  private buildAuditTrail(
    steps: RoleExecutionResult[],
    context: RoleContext
  ): string {
    let trail = `APOE Workflow Execution Audit Trail\n`
    trail += `=====================================\n\n`
    trail += `Goal: ${context.goal}\n`
    trail += `Timestamp: ${new Date().toISOString()}\n\n`
    
    trail += `Steps Executed:\n`
    steps.forEach((step, i) => {
      trail += `\n${i + 1}. ${step.role.toUpperCase()}\n`
      trail += `   Input: ${JSON.stringify(step.input).slice(0, 100)}...\n`
      trail += `   Output: ${JSON.stringify(step.output).slice(0, 100)}...\n`
      trail += `   Confidence: ${step.confidence.toFixed(2)}\n`
      trail += `   Tokens: ${step.tokensUsed}\n`
      trail += `   Time: ${step.latencyMs}ms\n`
      trail += `   Success: ${step.success ? 'YES' : 'NO'}\n`
    })
    
    return trail
  }

  /**
   * Store witness in VIF
   */
  private async storeWitness(witness: WitnessRecord): Promise<void> {
    try {
      await fetch(`${this.commandServerUrl}/mcp/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tool: 'track_confidence',
          arguments: {
            operation: 'apoe_workflow',
            confidence: witness.final_confidence,
            metadata: {
              witness_id: witness.witness_id,
              workflow_id: witness.workflow_id,
              total_tokens: witness.total_tokens,
              total_time: witness.total_time,
              total_cost: witness.total_cost,
              steps_count: witness.steps_executed.length,
            },
          },
        }),
      })
    } catch (error) {
      console.warn('Failed to store witness in VIF:', error)
    }
  }
}

