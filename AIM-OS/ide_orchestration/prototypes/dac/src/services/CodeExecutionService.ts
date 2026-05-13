/**
 * Code Execution Service
 * Orchestrates code execution with validation, storage, and tracking
 */

import { sandboxService, SandboxConfig, ExecutionResult } from './SandboxService'
import { mcpService } from './MCPService'
import {
  IntegrationTagContext,
  resolveIntegrationContext
} from '../utils/integrationTags'

export interface CodeExecutionRequest {
  code: string
  language: string
  context?: Record<string, any>
  input?: string
  timeout?: number
  memory?: number
  cpu?: number
  integrationContext?: IntegrationTagContext
}

export interface CodeExecutionResult extends ExecutionResult {
  output: string
  validated: boolean
  confidence?: number
  atom_id?: string  // CMC atom ID if stored
  witness_id?: string  // VIF witness ID
  timeline_entry_id?: string  // TCS entry ID
}

/**
 * Code Execution Service
 * Orchestrates secure code execution with AIM-OS integration
 */
export class CodeExecutionService {
  /**
   * Execute code in secure sandbox
   */
  async execute(
    request: CodeExecutionRequest
  ): Promise<{ success: boolean; result?: CodeExecutionResult; error?: string }> {
    try {
      // Validate code (basic security check)
      const validation = await this.validateCode(request.code, request.language)
      if (!validation.valid) {
        return {
          success: false,
          error: `Code validation failed: ${validation.error}`
        }
      }

      // Execute code in sandbox
      const sandboxConfig: SandboxConfig = {
        language: request.language,
        code: request.code,
        timeout: request.timeout || 30000,
        memory: request.memory || 512,
        cpu: request.cpu || 0.5,
        network: 'none', // No network by default (per Aether's security requirements)
        context: request.context
      }

      const executionResult = await sandboxService.executeCode(sandboxConfig)

      if (!executionResult.success || !executionResult.result) {
        return {
          success: false,
          error: executionResult.error || 'Code execution failed'
        }
      }

      const result = executionResult.result

      // Create execution result
      const codeExecutionResult: CodeExecutionResult = {
        ...result,
        output: result.stdout || '',
        validated: validation.valid,
        confidence: this.calculateConfidence(result, validation)
      }

      // Store result in CMC
      const cmcResult = await this.storeResult(codeExecutionResult, request)
      codeExecutionResult.atom_id = cmcResult.atom_id

      // Track confidence via VIF
      if (codeExecutionResult.confidence !== undefined) {
        const vifResult = await this.trackConfidence(
          codeExecutionResult.confidence,
          {
            task: 'code_execution',
            language: request.language,
            success: result.success
          },
          request.integrationContext
        )
        codeExecutionResult.witness_id = vifResult.witness_id
      }

      // Track in timeline via TCS
      const tcsResult = await this.trackInTimeline(
        {
          action: 'code_execution',
          language: request.language,
          success: result.success,
          executionTime: result.executionTime
        },
        request.integrationContext
      )
      codeExecutionResult.timeline_entry_id = tcsResult.entry_id

      return {
        success: true,
        result: codeExecutionResult
      }
    } catch (error) {
      console.error('Code execution error:', error)
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      }
    }
  }

  /**
   * Validate code (basic security check)
   */
  async validateCode(
    code: string,
    language: string
  ): Promise<{ valid: boolean; error?: string }> {
    try {
      // Basic validation checks
      // TODO: Implement comprehensive security validation

      // Check for dangerous patterns (basic)
      const dangerousPatterns = [
        /eval\s*\(/,
        /Function\s*\(/,
        /require\s*\(['"]fs['"]/,
        /import\s+.*fs/,
        /process\.exit/,
        /child_process/,
        /exec\s*\(/,
        /spawn\s*\(/
      ]

      for (const pattern of dangerousPatterns) {
        if (pattern.test(code)) {
          return {
            valid: false,
            error: `Potentially dangerous code detected: ${pattern}`
          }
        }
      }

      return { valid: true }
    } catch (error) {
      return {
        valid: false,
        error: error instanceof Error ? error.message : 'Validation error'
      }
    }
  }

  /**
   * Calculate confidence based on execution result
   */
  private calculateConfidence(
    result: ExecutionResult,
    validation: { valid: boolean }
  ): number {
    let confidence = 0.5 // Base confidence

    // Success increases confidence
    if (result.success && result.exitCode === 0) {
      confidence += 0.3
    }

    // No errors increases confidence
    if (!result.stderr && !result.error) {
      confidence += 0.2
    }

    // Validation passed increases confidence
    if (validation.valid) {
      confidence += 0.1
    }

    // Errors decrease confidence
    if (result.stderr || result.error) {
      confidence -= 0.3
    }

    // Timeout or resource issues decrease confidence
    if (result.error?.includes('timeout')) {
      confidence -= 0.2
    }

    return Math.max(0, Math.min(1, confidence))
  }

  /**
   * Store execution result in CMC
   */
  private async storeResult(
    result: CodeExecutionResult,
    request: CodeExecutionRequest
  ): Promise<{ atom_id?: string }> {
    try {
      const integrationContext = resolveIntegrationContext(request.integrationContext, {
        system: { name: 'cmc', priority: 'p0' },
        integrationType: 'memory_operation',
        connection: 'chat->cmc',
        modality: `code:${request.language}`,
        action: 'code_execution',
        mode: (request.context as any)?.thinkingMode,
        agent: 'coding',
        extras: ['code_execution']
      })

      const cmcResult = await mcpService.executeTool('mcp_lucid-mcp_store_memory', {
        content: result.output || result.stdout || '',
        tags: {
          'code': 1.0,
          'execution': 1.0,
          'language': 0.9,
          [request.language]: 0.9,
          'result': result.success ? 0.9 : 0.5
        },
        metadata: {
          language: request.language,
          success: result.success,
          exitCode: result.exitCode,
          executionTime: result.executionTime,
          confidence: result.confidence
        }
      }, integrationContext ? { integrationContext } : undefined)

      return { atom_id: cmcResult.result?.atom_id }
    } catch (error) {
      console.error('CMC storage error:', error)
      return {}
    }
  }

  /**
   * Track confidence via VIF
   */
  private async trackConfidence(
    confidence: number,
    context: Record<string, any>,
    integrationContext?: IntegrationTagContext
  ): Promise<{ witness_id?: string }> {
    try {
      const resolvedContext = resolveIntegrationContext(integrationContext, {
        system: { name: 'vif', priority: 'critical' },
        integrationType: 'witness',
        connection: 'chat->vif',
        modality: 'witness',
        action: 'code_execution',
        extras: ['code_execution', 'confidence_tracking']
      })

      const vifResult = await mcpService.executeTool('mcp_lucid-mcp_track_confidence', {
        confidence_score: confidence,
        task_type: 'code_execution',
        context: context
      }, resolvedContext ? { integrationContext: resolvedContext } : undefined)

      return { witness_id: vifResult.result?.witness_id }
    } catch (error) {
      console.error('VIF tracking error:', error)
      return {}
    }
  }

  /**
   * Track in timeline via TCS
   */
  private async trackInTimeline(
    entry: Record<string, any>,
    integrationContext?: IntegrationTagContext
  ): Promise<{ entry_id?: string }> {
    try {
      const resolvedContext = resolveIntegrationContext(integrationContext, {
        system: { name: 'tcs', priority: 'p0' },
        integrationType: 'timeline_event',
        connection: 'chat->tcs',
        modality: 'timeline',
        action: entry.action || 'code_execution',
        extras: ['code_execution']
      })

      const tcsResult = await mcpService.executeTool('mcp_lucid-mcp_add_timeline_entry', {
        action: entry.action,
        context: entry
      }, resolvedContext ? { integrationContext: resolvedContext } : undefined)

      return { entry_id: tcsResult.result?.entry_id }
    } catch (error) {
      console.error('TCS tracking error:', error)
      return {}
    }
  }
}

// Singleton instance
export const codeExecutionService = new CodeExecutionService()

