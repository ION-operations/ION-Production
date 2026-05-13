/**
 * Planner Role Executor
 * 
 * Specializes in strategic planning and task decomposition
 * Temperature: 0.3 (focused planning)
 * 
 * Epic 1.1: Complete APOE Execution
 */

import { RoleExecutor, RoleContext, RoleExecutionResult } from './RoleExecutor'
import { LLMService } from '../llm/LLMService'

/**
 * Plan Structure
 */
export interface Plan {
  steps: PlanStep[]
  dependencies: Map<string, string[]> // step_id -> [dependency_ids]
  estimatedTime: number
  estimatedTokens: number
  estimatedCost: number
  risks: string[]
}

/**
 * Plan Step
 */
export interface PlanStep {
  id: string
  description: string
  role: string // Which APOE role should handle this
  inputs: string[]
  outputs: string[]
  dependencies: string[]
  parallel: boolean // Can be executed in parallel with others
}

/**
 * Planner Executor Implementation
 */
export class PlannerExecutor extends RoleExecutor {
  constructor(llmService: LLMService, commandServerUrl?: string) {
    super(
      {
        role: 'planner',
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
      // Build planning prompt
      const prompt = this.buildPlanningPrompt(input, context)

      // Execute with LLM
      const response = await this.executeWithRole(prompt, context)

      // Parse plan from response
      const plan = this.parsePlan(response.text)

      // Build result
      const result: RoleExecutionResult = {
        role: 'planner',
        input,
        output: plan,
        success: true,
        confidence: response.confidence,
        tokensUsed: response.tokensUsed,
        latencyMs: Date.now() - startTime,
        reasoning: response.text,
        metadata: {
          stepsGenerated: plan.steps.length,
          parallelizable: plan.steps.filter(s => s.parallel).length,
        },
      }

      // Track with VIF
      await this.trackExecution(result)

      // Store in CMC
      await this.storeResult(result, context)

      return result
    } catch (error: any) {
      return {
        role: 'planner',
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
   * Build planning-specific prompt
   */
  private buildPlanningPrompt(input: any, context: RoleContext): string {
    let prompt = `As the PLANNER, decompose this goal into a clear, actionable plan:\n\n`
    
    prompt += `**Goal:** ${input.goal || context.goal}\n\n`
    
    if (input.constraints) {
      prompt += `**Constraints:**\n${JSON.stringify(input.constraints, null, 2)}\n\n`
    }
    
    prompt += `**Requirements:**\n`
    prompt += `1. Break down into 3-8 steps\n`
    prompt += `2. For each step, specify:\n`
    prompt += `   - Clear description\n`
    prompt += `   - Which APOE role should handle it (planner/retriever/reasoner/verifier/builder/critic/operator/witness)\n`
    prompt += `   - Input requirements\n`
    prompt += `   - Expected outputs\n`
    prompt += `   - Dependencies on other steps\n`
    prompt += `   - Whether it can run in parallel\n`
    prompt += `3. Identify dependencies and execution order\n`
    prompt += `4. Estimate time, tokens, and cost\n`
    prompt += `5. Identify potential risks\n\n`
    
    prompt += `Provide your plan in this JSON format:\n`
    prompt += `{\n`
    prompt += `  "steps": [\n`
    prompt += `    {\n`
    prompt += `      "id": "step1",\n`
    prompt += `      "description": "...",\n`
    prompt += `      "role": "retriever",\n`
    prompt += `      "inputs": ["..."],\n`
    prompt += `      "outputs": ["..."],\n`
    prompt += `      "dependencies": [],\n`
    prompt += `      "parallel": false\n`
    prompt += `    }\n`
    prompt += `  ],\n`
    prompt += `  "estimatedTime": 60,\n`
    prompt += `  "estimatedTokens": 10000,\n`
    prompt += `  "estimatedCost": 0.05,\n`
    prompt += `  "risks": ["..."]\n`
    prompt += `}\n`
    
    return prompt
  }

  /**
   * Parse plan from LLM response
   */
  private parsePlan(response: string): Plan {
    try {
      // Extract JSON from response (might be wrapped in markdown)
      const jsonMatch = response.match(/```json\n([\s\S]*?)\n```/) ||
                       response.match(/```\n([\s\S]*?)\n```/) ||
                       [null, response]
      
      const jsonStr = jsonMatch[1] || response
      const parsed = JSON.parse(jsonStr)
      
      // Build dependency map
      const dependencies = new Map<string, string[]>()
      parsed.steps.forEach((step: PlanStep) => {
        dependencies.set(step.id, step.dependencies || [])
      })
      
      return {
        steps: parsed.steps,
        dependencies,
        estimatedTime: parsed.estimatedTime || 0,
        estimatedTokens: parsed.estimatedTokens || 0,
        estimatedCost: parsed.estimatedCost || 0,
        risks: parsed.risks || [],
      }
    } catch (error) {
      // Fallback: Try to extract a simple plan
      return this.extractSimplePlan(response)
    }
  }

  /**
   * Extract simple plan if JSON parsing fails
   */
  private extractSimplePlan(response: string): Plan {
    const steps: PlanStep[] = []
    
    // Look for numbered steps
    const stepMatches = response.match(/(\d+)\.\s+([^\n]+)/g)
    
    if (stepMatches) {
      stepMatches.forEach((match, i) => {
        const description = match.replace(/^\d+\.\s+/, '')
        steps.push({
          id: `step${i + 1}`,
          description,
          role: 'builder', // Default role
          inputs: [],
          outputs: [],
          dependencies: i > 0 ? [`step${i}`] : [],
          parallel: false,
        })
      })
    }
    
    return {
      steps,
      dependencies: new Map(steps.map(s => [s.id, s.dependencies])),
      estimatedTime: steps.length * 30,
      estimatedTokens: steps.length * 2000,
      estimatedCost: steps.length * 0.01,
      risks: [],
    }
  }
}

