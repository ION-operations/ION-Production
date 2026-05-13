/**
 * Reasoner Role Executor
 * 
 * Specializes in logical reasoning and formal deduction
 * Temperature: 0.2 (systematic reasoning)
 * 
 * Epic 1.1: Complete APOE Execution
 */

import { RoleExecutor, RoleContext, RoleExecutionResult } from './RoleExecutor'
import { LLMService } from '../llm/LLMService'

/**
 * Reasoning Result Structure
 */
export interface ReasoningResult {
  premises: string[]
  reasoning_steps: Array<{
    step: number
    thought: string
    inference: string
    confidence: number
  }>
  conclusion: string
  reasoning_type: 'deductive' | 'inductive' | 'abductive' | 'analogical'
  validity: boolean
  soundness: boolean
}

/**
 * Reasoner Executor Implementation
 */
export class ReasonerExecutor extends RoleExecutor {
  constructor(llmService: LLMService, commandServerUrl?: string) {
    super(
      {
        role: 'reasoner',
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
      // Build reasoning prompt
      const prompt = this.buildReasoningPrompt(input, context)

      // Execute with LLM
      const response = await this.executeWithRole(prompt, context)

      // Parse reasoning from response
      const reasoning = this.parseReasoning(response.text)

      // Build result
      const result: RoleExecutionResult = {
        role: 'reasoner',
        input,
        output: reasoning,
        success: true,
        confidence: this.calculateReasoningConfidence(reasoning, response.confidence),
        tokensUsed: response.tokensUsed,
        latencyMs: Date.now() - startTime,
        reasoning: response.text,
        metadata: {
          reasoning_type: reasoning.reasoning_type,
          steps_count: reasoning.reasoning_steps.length,
          validity: reasoning.validity,
          soundness: reasoning.soundness,
        },
      }

      // Track with VIF
      await this.trackExecution(result)

      // Store in CMC
      await this.storeResult(result, context)

      return result
    } catch (error: any) {
      return {
        role: 'reasoner',
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
   * Build reasoning-specific prompt
   */
  private buildReasoningPrompt(input: any, context: RoleContext): string {
    let prompt = `As the REASONER, apply logical reasoning to solve this problem:\n\n`
    
    prompt += `**Problem:** ${input.problem || input}\n\n`
    
    if (input.reasoning_type) {
      prompt += `**Reasoning Type:** ${input.reasoning_type}\n\n`
    }
    
    prompt += `**Instructions:**\n`
    prompt += `1. Identify your premises (starting facts/assumptions)\n`
    prompt += `2. Apply systematic reasoning step-by-step\n`
    prompt += `3. For each step, show:\n`
    prompt += `   - Your thought process\n`
    prompt += `   - The inference you're making\n`
    prompt += `   - Your confidence in this step (0-1)\n`
    prompt += `4. Reach a clear conclusion\n`
    prompt += `5. Validate your reasoning (validity and soundness)\n\n`
    
    prompt += `**Reasoning Types:**\n`
    prompt += `- Deductive: General principles → Specific conclusions\n`
    prompt += `- Inductive: Specific observations → General principles\n`
    prompt += `- Abductive: Observations → Best explanation\n`
    prompt += `- Analogical: Similar cases → Conclusions\n\n`
    
    prompt += `Provide your reasoning in this format:\n`
    prompt += `{\n`
    prompt += `  "premises": ["...", "..."],\n`
    prompt += `  "reasoning_steps": [\n`
    prompt += `    {\n`
    prompt += `      "step": 1,\n`
    prompt += `      "thought": "...",\n`
    prompt += `      "inference": "...",\n`
    prompt += `      "confidence": 0.9\n`
    prompt += `    }\n`
    prompt += `  ],\n`
    prompt += `  "conclusion": "...",\n`
    prompt += `  "reasoning_type": "deductive",\n`
    prompt += `  "validity": true,\n`
    prompt += `  "soundness": true\n`
    prompt += `}\n`
    
    return prompt
  }

  /**
   * Parse reasoning from response
   */
  private parseReasoning(response: string): ReasoningResult {
    try {
      // Extract JSON
      const jsonMatch = response.match(/```json\n([\s\S]*?)\n```/) ||
                       response.match(/```\n([\s\S]*?)\n```/) ||
                       [null, response]
      
      const jsonStr = jsonMatch[1] || response
      const parsed = JSON.parse(jsonStr)
      
      return {
        premises: parsed.premises || [],
        reasoning_steps: parsed.reasoning_steps || [],
        conclusion: parsed.conclusion || '',
        reasoning_type: parsed.reasoning_type || 'deductive',
        validity: parsed.validity ?? true,
        soundness: parsed.soundness ?? true,
      }
    } catch (error) {
      // Fallback: Extract from text
      return this.extractReasoningFromText(response)
    }
  }

  /**
   * Extract reasoning from text if JSON parsing fails
   */
  private extractReasoningFromText(response: string): ReasoningResult {
    return {
      premises: [],
      reasoning_steps: [
        {
          step: 1,
          thought: response.slice(0, 500),
          inference: 'See full reasoning',
          confidence: 0.7,
        },
      ],
      conclusion: response.slice(-200),
      reasoning_type: 'deductive',
      validity: true,
      soundness: true,
    }
  }

  /**
   * Calculate reasoning confidence
   */
  private calculateReasoningConfidence(
    reasoning: ReasoningResult,
    baseConfidence: number
  ): number {
    // Average step confidences
    const stepConfidences = reasoning.reasoning_steps.map(s => s.confidence)
    const avgStepConfidence = stepConfidences.length > 0
      ? stepConfidences.reduce((a, b) => a + b, 0) / stepConfidences.length
      : 0.7
    
    // Weight by validity and soundness
    const validityWeight = reasoning.validity ? 1.0 : 0.5
    const soundnessWeight = reasoning.soundness ? 1.0 : 0.7
    
    // Combine
    return (baseConfidence + avgStepConfidence) / 2 * validityWeight * soundnessWeight
  }
}

