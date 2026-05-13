/**
 * Builder Role Executor
 * 
 * Specializes in code and artifact construction
 * Temperature: 0.5 (balanced creativity/precision)
 * 
 * Epic 1.1: Complete APOE Execution
 */

import { RoleExecutor, RoleContext, RoleExecutionResult } from './RoleExecutor'
import { LLMService } from '../llm/LLMService'

/**
 * Build Result Structure
 */
export interface BuildResult {
  artifact_type: 'code' | 'document' | 'config' | 'data'
  artifact: string
  language?: string
  tests?: string
  documentation?: string
  quality_score: number
}

/**
 * Builder Executor Implementation
 */
export class BuilderExecutor extends RoleExecutor {
  constructor(llmService: LLMService, commandServerUrl?: string) {
    super(
      {
        role: 'builder',
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
      // Build construction prompt
      const prompt = this.buildConstructionPrompt(input, context)

      // Execute with LLM
      const response = await this.executeWithRole(prompt, context)

      // Parse build result from response
      const buildResult = this.parseBuildResult(response.text, input.artifact_type)

      // Build result
      const result: RoleExecutionResult = {
        role: 'builder',
        input,
        output: buildResult,
        success: true,
        confidence: this.calculateBuildConfidence(buildResult, response.confidence),
        tokensUsed: response.tokensUsed,
        latencyMs: Date.now() - startTime,
        reasoning: response.text,
        metadata: {
          artifact_type: buildResult.artifact_type,
          artifact_size: buildResult.artifact.length,
          has_tests: !!buildResult.tests,
          has_docs: !!buildResult.documentation,
        },
      }

      // Track with VIF
      await this.trackExecution(result)

      // Store in CMC
      await this.storeResult(result, context)

      return result
    } catch (error: any) {
      return {
        role: 'builder',
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
   * Build construction-specific prompt
   */
  private buildConstructionPrompt(input: any, context: RoleContext): string {
    let prompt = `As the BUILDER, construct the requested artifact:\n\n`
    
    prompt += `**Task:** ${input.task || input.description}\n\n`
    
    prompt += `**Artifact Type:** ${input.artifact_type || 'code'}\n\n`
    
    if (input.language) {
      prompt += `**Language:** ${input.language}\n\n`
    }
    
    if (input.requirements) {
      prompt += `**Requirements:**\n${JSON.stringify(input.requirements, null, 2)}\n\n`
    }
    
    prompt += `**Instructions:**\n`
    prompt += `1. Build production-ready artifact\n`
    prompt += `2. Follow best practices\n`
    prompt += `3. Include comprehensive error handling\n`
    prompt += `4. Add clear comments\n`
    prompt += `5. Write tests if applicable\n`
    prompt += `6. Provide documentation\n\n`
    
    if (input.artifact_type === 'code') {
      prompt += `**Code Quality Requirements:**\n`
      prompt += `- Type safety (use TypeScript types)\n`
      prompt += `- Error handling (try/catch, validation)\n`
      prompt += `- Documentation (JSDoc comments)\n`
      prompt += `- Best practices (DRY, SOLID principles)\n\n`
    }
    
    return prompt
  }

  /**
   * Parse build result from response
   */
  private parseBuildResult(response: string, artifactType: string): BuildResult {
    // Extract code blocks
    const codeBlocks = this.extractCodeBlocks(response)
    
    // Find main artifact
    const mainArtifact = codeBlocks.find(b => b.language !== 'test') || codeBlocks[0]
    
    // Find tests
    const testBlock = codeBlocks.find(b => b.language === 'test' || b.content.includes('test('))
    
    return {
      artifact_type: artifactType as any || 'code',
      artifact: mainArtifact?.content || response,
      language: mainArtifact?.language,
      tests: testBlock?.content,
      documentation: this.extractDocumentation(response),
      quality_score: this.assessQuality(mainArtifact?.content || response),
    }
  }

  /**
   * Extract code blocks from markdown
   */
  private extractCodeBlocks(text: string): Array<{ language: string; content: string }> {
    const blocks: Array<{ language: string; content: string }> = []
    const regex = /```(\w+)?\n([\s\S]*?)```/g
    
    let match
    while ((match = regex.exec(text)) !== null) {
      blocks.push({
        language: match[1] || 'text',
        content: match[2],
      })
    }
    
    return blocks
  }

  /**
   * Extract documentation from response
   */
  private extractDocumentation(text: string): string {
    // Look for documentation sections
    const docMatch = text.match(/##?\s+Documentation\n([\s\S]*?)(?=\n##|$)/i)
    return docMatch ? docMatch[1].trim() : ''
  }

  /**
   * Assess artifact quality
   */
  private assessQuality(artifact: string): number {
    let score = 0.5 // Base score
    
    // Has error handling?
    if (artifact.includes('try') || artifact.includes('catch') || artifact.includes('throw')) {
      score += 0.1
    }
    
    // Has documentation?
    if (artifact.includes('/**') || artifact.includes('//')) {
      score += 0.1
    }
    
    // Has type annotations? (TypeScript)
    if (artifact.includes(': ') || artifact.includes('interface') || artifact.includes('type')) {
      score += 0.1
    }
    
    // Reasonable length (not too short, not too long)
    if (artifact.length > 100 && artifact.length < 5000) {
      score += 0.1
    }
    
    // Has proper structure?
    if (artifact.includes('function') || artifact.includes('class') || artifact.includes('const')) {
      score += 0.1
    }
    
    return Math.min(score, 1.0)
  }

  /**
   * Calculate build confidence
   */
  private calculateBuildConfidence(
    buildResult: BuildResult,
    baseConfidence: number
  ): number {
    // Start with base confidence
    let confidence = baseConfidence
    
    // Boost for tests
    if (buildResult.tests) {
      confidence *= 1.1
    }
    
    // Boost for documentation
    if (buildResult.documentation) {
      confidence *= 1.05
    }
    
    // Weight by quality score
    confidence *= buildResult.quality_score
    
    return Math.min(confidence, 1.0)
  }
}

