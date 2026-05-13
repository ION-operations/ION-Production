/**
 * Verifier Role Executor
 * 
 * Specializes in validation and fact-checking
 * Temperature: 0.1 (maximum precision)
 * 
 * Epic 1.1: Complete APOE Execution
 */

import { RoleExecutor, RoleContext, RoleExecutionResult } from './RoleExecutor'
import { LLMService } from '../llm/LLMService'

/**
 * Verification Result Structure
 */
export interface VerificationResult {
  verified: boolean
  confidence: number
  issues: Array<{
    type: 'error' | 'warning' | 'info'
    description: string
    severity: number
    location?: string
  }>
  checks_performed: string[]
  facts_verified: number
  facts_failed: number
  recommendations: string[]
}

/**
 * Verifier Executor Implementation
 */
export class VerifierExecutor extends RoleExecutor {
  constructor(llmService: LLMService, commandServerUrl?: string) {
    super(
      {
        role: 'verifier',
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
      // Build verification prompt
      const prompt = this.buildVerificationPrompt(input, context)

      // Execute with LLM
      const response = await this.executeWithRole(prompt, context)

      // Parse verification from response
      const verification = this.parseVerification(response.text)

      // Build result
      const result: RoleExecutionResult = {
        role: 'verifier',
        input,
        output: verification,
        success: verification.verified,
        confidence: verification.confidence,
        tokensUsed: response.tokensUsed,
        latencyMs: Date.now() - startTime,
        reasoning: response.text,
        metadata: {
          issues_found: verification.issues.length,
          facts_verified: verification.facts_verified,
          facts_failed: verification.facts_failed,
          verification_pass: verification.verified,
        },
      }

      // Track with VIF
      await this.trackExecution(result)

      // Store in CMC
      await this.storeResult(result, context)

      return result
    } catch (error: any) {
      return {
        role: 'verifier',
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
   * Build verification-specific prompt
   */
  private buildVerificationPrompt(input: any, context: RoleContext): string {
    let prompt = `As the VERIFIER, validate the correctness and quality of this work:\n\n`
    
    prompt += `**Artifact to Verify:**\n${JSON.stringify(input.artifact, null, 2)}\n\n`
    
    if (input.requirements) {
      prompt += `**Requirements to Check:**\n${JSON.stringify(input.requirements, null, 2)}\n\n`
    }
    
    prompt += `**Verification Checklist:**\n`
    prompt += `1. **Correctness:** Is the logic/implementation correct?\n`
    prompt += `2. **Completeness:** Does it meet all requirements?\n`
    prompt += `3. **Quality:** Does it follow best practices?\n`
    prompt += `4. **Safety:** Are there security issues?\n`
    prompt += `5. **Performance:** Are there efficiency concerns?\n`
    prompt += `6. **Facts:** Are all claims accurate?\n\n`
    
    prompt += `For each check, provide:\n`
    prompt += `- Pass/Fail status\n`
    prompt += `- Issues found (if any)\n`
    prompt += `- Severity (0-10)\n`
    prompt += `- Recommendations\n\n`
    
    prompt += `Format your verification as JSON:\n`
    prompt += `{\n`
    prompt += `  "verified": true/false,\n`
    prompt += `  "confidence": 0.95,\n`
    prompt += `  "issues": [\n`
    prompt += `    {\n`
    prompt += `      "type": "error",\n`
    prompt += `      "description": "...",\n`
    prompt += `      "severity": 8,\n`
    prompt += `      "location": "line 42"\n`
    prompt += `    }\n`
    prompt += `  ],\n`
    prompt += `  "checks_performed": ["correctness", "completeness", ...],\n`
    prompt += `  "facts_verified": 10,\n`
    prompt += `  "facts_failed": 0,\n`
    prompt += `  "recommendations": ["..."]\n`
    prompt += `}\n`
    
    return prompt
  }

  /**
   * Parse verification from response
   */
  private parseVerification(response: string): VerificationResult {
    try {
      // Extract JSON
      const jsonMatch = response.match(/```json\n([\s\S]*?)\n```/) ||
                       response.match(/```\n([\s\S]*?)\n```/) ||
                       [null, response]
      
      const jsonStr = jsonMatch[1] || response
      const parsed = JSON.parse(jsonStr)
      
      return {
        verified: parsed.verified ?? true,
        confidence: parsed.confidence ?? 0.8,
        issues: parsed.issues || [],
        checks_performed: parsed.checks_performed || [],
        facts_verified: parsed.facts_verified ?? 0,
        facts_failed: parsed.facts_failed ?? 0,
        recommendations: parsed.recommendations || [],
      }
    } catch (error) {
      // Fallback: Simple verification
      return this.extractSimpleVerification(response)
    }
  }

  /**
   * Extract simple verification if JSON parsing fails
   */
  private extractSimpleVerification(response: string): VerificationResult {
    const verified = !response.toLowerCase().includes('error') &&
                    !response.toLowerCase().includes('fail') &&
                    !response.toLowerCase().includes('incorrect')
    
    return {
      verified,
      confidence: verified ? 0.7 : 0.3,
      issues: [],
      checks_performed: ['basic'],
      facts_verified: 0,
      facts_failed: 0,
      recommendations: [],
    }
  }
}

