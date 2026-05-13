/**
 * Operator Role Executor
 * 
 * Specializes in system operations and tool execution
 * Temperature: 0.1 (maximum precision for operations)
 * 
 * Epic 1.1: Complete APOE Execution
 */

import { RoleExecutor, RoleContext, RoleExecutionResult } from './RoleExecutor'
import { LLMService } from '../llm/LLMService'

/**
 * Operation Result Structure
 */
export interface OperationResult {
  operation: string
  command?: string
  tool?: string
  parameters?: Record<string, any>
  result: any
  success: boolean
  error?: string
  side_effects: string[]
}

/**
 * Operator Executor Implementation
 */
export class OperatorExecutor extends RoleExecutor {
  constructor(llmService: LLMService, commandServerUrl?: string) {
    super(
      {
        role: 'operator',
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
      // Determine operation type
      const operationType = input.operation_type || 'tool_call'

      let operationResult: OperationResult

      if (operationType === 'tool_call') {
        operationResult = await this.executeTool(input)
      } else if (operationType === 'api_call') {
        operationResult = await this.executeAPICall(input)
      } else {
        operationResult = await this.executeGenericOperation(input, context)
      }

      // Build result
      const result: RoleExecutionResult = {
        role: 'operator',
        input,
        output: operationResult,
        success: operationResult.success,
        confidence: operationResult.success ? 0.95 : 0.5,
        tokensUsed: 100, // Operators use minimal tokens
        latencyMs: Date.now() - startTime,
        reasoning: `Executed ${operationResult.operation}`,
        metadata: {
          operation: operationResult.operation,
          side_effects: operationResult.side_effects,
        },
      }

      // Track with VIF
      await this.trackExecution(result)

      // Store in CMC
      await this.storeResult(result, context)

      return result
    } catch (error: any) {
      return {
        role: 'operator',
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
   * Execute MCP tool
   */
  private async executeTool(input: any): Promise<OperationResult> {
    try {
      const response = await fetch(`${this.commandServerUrl}/mcp/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tool: input.tool,
          arguments: input.arguments || {},
        }),
      })

      const result = await response.json()

      return {
        operation: 'tool_call',
        tool: input.tool,
        parameters: input.arguments,
        result: result.result,
        success: result.success ?? true,
        side_effects: input.tool === 'store_memory' ? ['CMC updated'] : [],
      }
    } catch (error: any) {
      return {
        operation: 'tool_call',
        tool: input.tool,
        parameters: input.arguments,
        result: null,
        success: false,
        error: error.message,
        side_effects: [],
      }
    }
  }

  /**
   * Execute API call
   */
  private async executeAPICall(input: any): Promise<OperationResult> {
    try {
      const response = await fetch(`${this.commandServerUrl}/mcp/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tool: 'call_api',
          arguments: {
            provider: input.provider,
            endpoint: input.endpoint,
            method: input.method || 'POST',
            data: input.data,
          },
        }),
      })

      const result = await response.json()

      return {
        operation: 'api_call',
        parameters: {
          provider: input.provider,
          endpoint: input.endpoint,
        },
        result: result.result,
        success: result.success ?? true,
        side_effects: [],
      }
    } catch (error: any) {
      return {
        operation: 'api_call',
        result: null,
        success: false,
        error: error.message,
        side_effects: [],
      }
    }
  }

  /**
   * Execute generic operation
   */
  private async executeGenericOperation(
    input: any,
    context: RoleContext
  ): Promise<OperationResult> {
    // For generic operations, use LLM to determine what to do
    const prompt = `Determine how to execute this operation: ${JSON.stringify(input)}`
    const response = await this.executeWithRole(prompt, context)

    return {
      operation: 'generic',
      result: response.text,
      success: true,
      side_effects: [],
    }
  }
}

