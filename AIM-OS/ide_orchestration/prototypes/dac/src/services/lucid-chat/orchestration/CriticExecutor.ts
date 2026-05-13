/**
 * Critic Role Executor
 * 
 * Specializes in quality assessment and improvement suggestions
 * Temperature: 0.4 (balanced criticism)
 * 
 * Epic 1.1: Complete APOE Execution
 */

import { RoleExecutor, RoleContext, RoleExecutionResult } from './RoleExecutor'
import { LLMService } from '../llm/LLMService'

/**
 * Critique Result Structure
 */
export interface CritiqueResult {
  overall_quality: number // 0-1
  strengths: string[]
  weaknesses: string[]
  improvements: Array<{
    category: string
    description: string
    priority: 'high' | 'medium' | 'low'
    effort: 'small' | 'medium' | 'large'
  }>
  risk_assessment: {
    risks: string[]
    severity: 'low' | 'medium' | 'high' | 'critical'
  }
  recommendation: 'approve' | 'revise' | 'reject'
}

/**
 * Critic Executor Implementation
 */
export class CriticExecutor extends RoleExecutor {
  constructor(llmService: LLMService, commandServerUrl?: string) {
    super(
      {
        role: 'critic',
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
      // Build critique prompt
      const prompt = this.buildCritiquePrompt(input, context)

      // Execute with LLM
      const response = await this.executeWithRole(prompt, context)

      // Parse critique from response
      const critique = this.parseCritique(response.text)

      // Build result
      const result: RoleExecutionResult = {
        role: 'critic',
        input,
        output: critique,
        success: true,
        confidence: response.confidence,
        tokensUsed: response.tokensUsed,
        latencyMs: Date.now() - startTime,
        reasoning: response.text,
        metadata: {
          overall_quality: critique.overall_quality,
          improvements_suggested: critique.improvements.length,
          recommendation: critique.recommendation,
        },
      }

      // Track with VIF
      await this.trackExecution(result)

      // Store in CMC
      await this.storeResult(result, context)

      return result
    } catch (error: any) {
      return {
        role: 'critic',
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
   * Build critique-specific prompt
   */
  private buildCritiquePrompt(input: any, context: RoleContext): string {
    let prompt = `As the CRITIC, assess the quality of this work and suggest improvements:\n\n`
    
    prompt += `**Work to Critique:**\n${JSON.stringify(input.artifact || input, null, 2)}\n\n`
    
    prompt += `**Assessment Criteria:**\n`
    prompt += `1. **Quality:** Overall quality (0-1 score)\n`
    prompt += `2. **Strengths:** What is done well?\n`
    prompt += `3. **Weaknesses:** What needs improvement?\n`
    prompt += `4. **Improvements:** Specific actionable suggestions\n`
    prompt += `5. **Risks:** Potential issues or concerns\n`
    prompt += `6. **Recommendation:** Approve, revise, or reject?\n\n`
    
    prompt += `For improvements, prioritize by:\n`
    prompt += `- Priority: high/medium/low\n`
    prompt += `- Effort: small/medium/large\n\n`
    
    prompt += `Format as JSON:\n`
    prompt += `{\n`
    prompt += `  "overall_quality": 0.85,\n`
    prompt += `  "strengths": ["...", "..."],\n`
    prompt += `  "weaknesses": ["...", "..."],\n`
    prompt += `  "improvements": [\n`
    prompt += `    {\n`
    prompt += `      "category": "error_handling",\n`
    prompt += `      "description": "...",\n`
    prompt += `      "priority": "high",\n`
    prompt += `      "effort": "medium"\n`
    prompt += `    }\n`
    prompt += `  ],\n`
    prompt += `  "risk_assessment": {\n`
    prompt += `    "risks": ["..."],\n`
    prompt += `    "severity": "medium"\n`
    prompt += `  },\n`
    prompt += `  "recommendation": "approve"\n`
    prompt += `}\n`
    
    return prompt
  }

  /**
   * Parse critique from response
   */
  private parseCritique(response: string): CritiqueResult {
    try {
      // Extract JSON
      const jsonMatch = response.match(/```json\n([\s\S]*?)\n```/) ||
                       response.match(/```\n([\s\S]*?)\n```/) ||
                       [null, response]
      
      const jsonStr = jsonMatch[1] || response
      const parsed = JSON.parse(jsonStr)
      
      return {
        overall_quality: parsed.overall_quality ?? 0.7,
        strengths: parsed.strengths || [],
        weaknesses: parsed.weaknesses || [],
        improvements: parsed.improvements || [],
        risk_assessment: parsed.risk_assessment || { risks: [], severity: 'low' },
        recommendation: parsed.recommendation || 'approve',
      }
    } catch (error) {
      // Fallback: Extract from text
      return this.extractSimpleCritique(response)
    }
  }

  /**
   * Extract simple critique if JSON parsing fails
   */
  private extractSimpleCritique(response: string): CritiqueResult {
    const hasIssues = response.toLowerCase().includes('issue') ||
                     response.toLowerCase().includes('problem') ||
                     response.toLowerCase().includes('concern')
    
    return {
      overall_quality: hasIssues ? 0.6 : 0.8,
      strengths: [],
      weaknesses: [],
      improvements: [],
      risk_assessment: { risks: [], severity: 'low' },
      recommendation: hasIssues ? 'revise' : 'approve',
    }
  }
}

