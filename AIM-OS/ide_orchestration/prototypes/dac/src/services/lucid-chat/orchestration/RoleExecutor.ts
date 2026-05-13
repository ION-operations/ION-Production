/**
 * APOE Role Executor - Base Class
 * 
 * Provides base functionality for all 8 APOE role executors
 * Integrates with LLM services, VIF tracking, and CMC storage
 * 
 * Epic 1.1: Complete APOE Execution
 */

import { LLMService, LLMProvider, LLMMessage } from '../llm/LLMService'
import { APIResponse } from '../base/BaseAPIService'

/**
 * APOE Role Types
 */
export type APOERole =
  | 'planner'
  | 'retriever'
  | 'reasoner'
  | 'verifier'
  | 'builder'
  | 'critic'
  | 'operator'
  | 'witness'

/**
 * Role Configuration
 */
export interface RoleConfig {
  role: APOERole
  temperature: number
  maxTokens: number
  instructions: string
  capabilities: string[]
  provider?: LLMProvider
}

/**
 * Role Execution Context
 */
export interface RoleContext {
  goal: string
  previousSteps?: RoleExecutionResult[]
  workflow?: any
  budget?: {
    tokens: number
    time: number
    cost: number
  }
  metadata?: Record<string, any>
}

/**
 * Role Execution Result
 */
export interface RoleExecutionResult {
  role: APOERole
  input: any
  output: any
  success: boolean
  confidence: number
  tokensUsed: number
  latencyMs: number
  reasoning?: string
  metadata?: Record<string, any>
  error?: string
}

/**
 * Default Role Configurations
 */
export const DEFAULT_ROLE_CONFIGS: Record<APOERole, Partial<RoleConfig>> = {
  planner: {
    temperature: 0.3,
    maxTokens: 1000,
    instructions: 'Break down the goal into clear, actionable steps. Consider dependencies and optimal order.',
    capabilities: ['planning', 'decomposition', 'strategy'],
  },
  retriever: {
    temperature: 0.1,
    maxTokens: 2000,
    instructions: 'Retrieve relevant knowledge from HHNI and CMC. Provide context for the current task.',
    capabilities: ['retrieval', 'context_gathering', 'search'],
  },
  reasoner: {
    temperature: 0.2,
    maxTokens: 3000,
    instructions: 'Apply logical reasoning to solve the problem. Use formal logic, step-by-step derivation.',
    capabilities: ['reasoning', 'logic', 'inference', 'deduction'],
  },
  verifier: {
    temperature: 0.1,
    maxTokens: 1500,
    instructions: 'Verify the correctness of the solution. Check facts, validate logic, ensure quality.',
    capabilities: ['verification', 'validation', 'fact_checking'],
  },
  builder: {
    temperature: 0.5,
    maxTokens: 4000,
    instructions: 'Construct the solution. Generate code, write documentation, create artifacts.',
    capabilities: ['construction', 'generation', 'creation', 'implementation'],
  },
  critic: {
    temperature: 0.4,
    maxTokens: 2000,
    instructions: 'Critically assess the solution. Identify issues, suggest improvements, ensure quality.',
    capabilities: ['criticism', 'assessment', 'quality_review'],
  },
  operator: {
    temperature: 0.1,
    maxTokens: 1000,
    instructions: 'Execute system operations. Perform actions, run tools, manage resources.',
    capabilities: ['operations', 'execution', 'action'],
  },
  witness: {
    temperature: 0.0,
    maxTokens: 500,
    instructions: 'Create complete provenance record. Capture all details for audit trail.',
    capabilities: ['provenance', 'witnessing', 'audit'],
  },
}

/**
 * Base Role Executor
 * 
 * All role executors inherit from this base class
 */
export abstract class RoleExecutor {
  protected config: RoleConfig
  protected llmService: LLMService
  protected commandServerUrl: string

  constructor(
    config: Partial<RoleConfig>,
    llmService: LLMService,
    commandServerUrl: string = 'http://localhost:5001'
  ) {
    const defaultConfig = DEFAULT_ROLE_CONFIGS[config.role!]
    
    this.config = {
      role: config.role!,
      temperature: config.temperature ?? defaultConfig.temperature ?? 0.5,
      maxTokens: config.maxTokens ?? defaultConfig.maxTokens ?? 2000,
      instructions: config.instructions ?? defaultConfig.instructions ?? '',
      capabilities: config.capabilities ?? defaultConfig.capabilities ?? [],
      provider: config.provider ?? 'anthropic',
    }
    
    this.llmService = llmService
    this.commandServerUrl = commandServerUrl
  }

  /**
   * Execute the role with given input and context
   * Must be implemented by subclasses
   */
  abstract execute(
    input: any,
    context: RoleContext
  ): Promise<RoleExecutionResult>

  /**
   * Execute LLM with role-specific configuration
   */
  protected async executeWithRole(
    prompt: string,
    context: RoleContext
  ): Promise<{ text: string; tokensUsed: number; latencyMs: number; confidence: number }> {
    const startTime = Date.now()
    
    // Build messages with role instructions
    const messages: LLMMessage[] = [
      {
        role: 'system',
        content: this.buildSystemPrompt(context),
      },
      {
        role: 'user',
        content: prompt,
      },
    ]
    
    // Call LLM service
    const response = await this.llmService.chatCompletion({
      provider: this.config.provider!,
      messages,
      temperature: this.config.temperature,
      maxTokens: this.config.maxTokens,
    })
    
    if (!response.success || !response.data) {
      throw new Error(`LLM call failed: ${response.error}`)
    }
    
    const latencyMs = Date.now() - startTime
    
    return {
      text: response.data.text,
      tokensUsed: response.data.tokensUsed,
      latencyMs,
      confidence: response.data.confidence ?? 0.8,
    }
  }

  /**
   * Build system prompt for this role
   */
  protected buildSystemPrompt(context: RoleContext): string {
    let prompt = `You are the ${this.config.role.toUpperCase()} role in an APOE orchestration workflow.\n\n`
    
    prompt += `**Role Instructions:**\n${this.config.instructions}\n\n`
    
    prompt += `**Capabilities:**\n${this.config.capabilities.join(', ')}\n\n`
    
    prompt += `**Current Goal:**\n${context.goal}\n\n`
    
    if (context.previousSteps && context.previousSteps.length > 0) {
      prompt += `**Previous Steps:**\n`
      context.previousSteps.forEach((step, i) => {
        prompt += `${i + 1}. ${step.role}: ${JSON.stringify(step.output).slice(0, 200)}...\n`
      })
      prompt += '\n'
    }
    
    if (context.budget) {
      prompt += `**Budget Constraints:**\n`
      prompt += `- Tokens: ${context.budget.tokens}\n`
      prompt += `- Time: ${context.budget.time}s\n`
      prompt += `- Cost: $${context.budget.cost}\n\n`
    }
    
    return prompt
  }

  /**
   * Track execution with VIF
   */
  protected async trackExecution(
    result: RoleExecutionResult
  ): Promise<void> {
    try {
      await fetch(`${this.commandServerUrl}/mcp/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tool: 'track_confidence',
          arguments: {
            operation: `apoe_role_${this.config.role}`,
            confidence: result.confidence,
            metadata: {
              tokensUsed: result.tokensUsed,
              latencyMs: result.latencyMs,
              success: result.success,
            },
          },
        }),
      })
    } catch (error) {
      // Non-critical - log but don't fail
      console.warn(`Failed to track execution in VIF:`, error)
    }
  }

  /**
   * Store result in CMC
   */
  protected async storeResult(
    result: RoleExecutionResult,
    context: RoleContext
  ): Promise<void> {
    try {
      await fetch(`${this.commandServerUrl}/mcp/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tool: 'store_memory',
          arguments: {
            content: JSON.stringify(result),
            memory_type: 'apoe_role_execution',
            tags: ['apoe', this.config.role, context.goal],
            metadata: {
              role: this.config.role,
              goal: context.goal,
              confidence: result.confidence,
              timestamp: new Date().toISOString(),
            },
          },
        }),
      })
    } catch (error) {
      // Non-critical - log but don't fail
      console.warn(`Failed to store result in CMC:`, error)
    }
  }

  /**
   * Validate input for this role
   */
  protected validateInput(input: any): void {
    if (!input) {
      throw new Error(`${this.config.role} requires input`)
    }
  }

  /**
   * Validate context
   */
  protected validateContext(context: RoleContext): void {
    if (!context.goal) {
      throw new Error('Context must have a goal')
    }
  }

  /**
   * Get role name
   */
  getRoleName(): string {
    return this.config.role
  }

  /**
   * Get role capabilities
   */
  getCapabilities(): string[] {
    return this.config.capabilities
  }

  /**
   * Get role configuration
   */
  getConfig(): RoleConfig {
    return { ...this.config }
  }
}

