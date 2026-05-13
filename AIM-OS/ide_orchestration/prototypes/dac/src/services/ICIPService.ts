/**
 * ICIP Service
 * Handles code generation, transformation, and validation via ICIP backend
 * Uses MCPService for MCP tool execution (when available) or direct service calls
 */

import { mcpService } from './MCPService'

// Types based on ICIP L4 documentation
export type GenerationType = 
  | 'function' 
  | 'class' 
  | 'test' 
  | 'documentation' 
  | 'completion' 
  | 'refactoring'

export type TransformationType =
  | 'refactoring'
  | 'modernization'
  | 'optimization'
  | 'translation'
  | 'migration'
  | 'standardization'

export interface CodeGenerationRequest {
  generation_type: GenerationType
  description: string
  language: string
  framework?: string
  context?: Record<string, any>
  metadata?: Record<string, any>
}

export interface CodeGenerationResult {
  generated_code: string
  explanation: string
  confidence: number  // 0.0-1.0
  language: string
  framework?: string
  dependencies: string[]
  test_cases: string[]
  documentation: string
  metadata?: Record<string, any>
  atom_id?: string  // CMC atom ID if stored
  witness_id?: string  // VIF witness ID
  timeline_entry_id?: string  // TCS entry ID
}

export interface CodeTransformationRequest {
  transformation_type: TransformationType
  source_code: string
  source_language: string
  target_language?: string
  transformation_rules?: Record<string, any>
  context?: Record<string, any>
}

export interface CodeTransformationResult {
  original_code: string
  transformed_code: string
  transformation_type: string
  confidence: number
  changes: Array<{
    type: string
    description: string
    location?: { line: number; column: number }
  }>
  explanation: string
  validation_results: Record<string, any>
  metadata?: Record<string, any>
}

export interface CodeValidationResult {
  valid: boolean
  errors: Array<{
    type: 'syntax' | 'quality' | 'security' | 'other'
    message: string
    location?: { line: number; column: number }
    severity: 'low' | 'medium' | 'high' | 'critical'
  }>
  warnings: Array<{
    type: string
    message: string
    location?: { line: number; column: number }
  }>
  quality_metrics: {
    complexity?: number
    maintainability?: number
    test_coverage?: number
  }
  confidence: number
}

/**
 * ICIP Service
 * Integrates with ICIP backend via Command Server MCP tools (when available) or direct service calls
 */
export class ICIPService {
  private icipServiceUrl: string = 'http://localhost:8000' // ICIP service URL (if direct calls needed)

  /**
   * Generate code using ICIP
   * Phase 1: Try MCP tools, fallback to direct service calls
   */
  async generateCode(
    request: CodeGenerationRequest
  ): Promise<{ success: boolean; result?: CodeGenerationResult; error?: string }> {
    try {
      // Phase 1: Try MCP tool (if ICIP MCP tools exist)
      const mcpResult = await mcpService.executeTool('mcp_lucid-mcp_generate_code', {
        generation_type: request.generation_type,
        description: request.description,
        language: request.language,
        framework: request.framework,
        context: request.context || {},
        metadata: request.metadata || {}
      })

      if (mcpResult.success && mcpResult.result) {
        // MCP tool exists and succeeded
        const result = this.parseCodeGenerationResult(mcpResult.result)
        
        // Store in CMC, track VIF, track TCS
        await this.integrateWithAIMOS(result, request)
        
        return {
          success: true,
          result
        }
      }

      // Phase 2: Fallback to direct ICIP service call (if MCP tools don't exist yet)
      if (mcpResult.error?.includes('tool') || mcpResult.error?.includes('not found')) {
        return await this.generateCodeDirect(request)
      }

      // MCP tool failed for other reason
      return {
        success: false,
        error: mcpResult.error || 'Failed to generate code via MCP tool'
      }
    } catch (error) {
      console.error('ICIP generate code error:', error)
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      }
    }
  }

  /**
   * Direct ICIP service call (fallback when MCP tools don't exist)
   */
  private async generateCodeDirect(
    request: CodeGenerationRequest
  ): Promise<{ success: boolean; result?: CodeGenerationResult; error?: string }> {
    try {
      // TODO: Replace with actual ICIP service endpoint when available
      // For now, return placeholder response
      console.warn('ICIP MCP tools not available, using placeholder response')
      
      // Placeholder response (will be replaced with actual ICIP service call)
      const placeholderResult: CodeGenerationResult = {
        generated_code: `// Placeholder: ${request.generation_type} generation for ${request.language}\n// TODO: Connect to ICIP service`,
        explanation: 'ICIP service integration pending',
        confidence: 0.5,
        language: request.language,
        framework: request.framework,
        dependencies: [],
        test_cases: [],
        documentation: ''
      }

      // Store in CMC, track VIF, track TCS
      await this.integrateWithAIMOS(placeholderResult, request)

      return {
        success: true,
        result: placeholderResult
      }
    } catch (error) {
      console.error('ICIP direct service call error:', error)
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      }
    }
  }

  /**
   * Transform code using ICIP
   */
  async transformCode(
    request: CodeTransformationRequest
  ): Promise<{ success: boolean; result?: CodeTransformationResult; error?: string }> {
    try {
      // Try MCP tool first
      const mcpResult = await mcpService.executeTool('mcp_lucid-mcp_transform_code', {
        transformation_type: request.transformation_type,
        source_code: request.source_code,
        source_language: request.source_language,
        target_language: request.target_language,
        transformation_rules: request.transformation_rules || {},
        context: request.context || {}
      })

      if (mcpResult.success && mcpResult.result) {
        return {
          success: true,
          result: this.parseCodeTransformationResult(mcpResult.result)
        }
      }

      // Fallback to direct service call
      if (mcpResult.error?.includes('tool') || mcpResult.error?.includes('not found')) {
        return await this.transformCodeDirect(request)
      }

      return {
        success: false,
        error: mcpResult.error || 'Failed to transform code'
      }
    } catch (error) {
      console.error('ICIP transform code error:', error)
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      }
    }
  }

  /**
   * Direct transformation call (fallback)
   */
  private async transformCodeDirect(
    request: CodeTransformationRequest
  ): Promise<{ success: boolean; result?: CodeTransformationResult; error?: string }> {
    // TODO: Implement direct ICIP service call
    console.warn('ICIP transformation MCP tools not available, using placeholder')
    return {
      success: false,
      error: 'ICIP transformation service not yet implemented'
    }
  }

  /**
   * Validate generated code
   */
  async validateCode(
    code: string,
    language: string
  ): Promise<{ success: boolean; result?: CodeValidationResult; error?: string }> {
    try {
      // Use CodeValidationService for comprehensive validation
      const { codeValidationService } = await import('./CodeValidationService')
      
      const validationResult = await codeValidationService.validate({
        code,
        language,
        validationTypes: ['syntax', 'quality', 'security']
      })

      if (validationResult.success && validationResult.result) {
        // Convert to CodeValidationResult format
        const result: CodeValidationResult = {
          valid: validationResult.result.valid,
          errors: validationResult.result.errors,
          warnings: validationResult.result.warnings,
          quality_metrics: validationResult.result.quality_metrics,
          confidence: validationResult.result.confidence
        }

        return {
          success: true,
          result
        }
      } else {
        return {
          success: false,
          error: validationResult.error || 'Validation failed'
        }
      }
    } catch (error) {
      console.error('ICIP validate code error:', error)
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      }
    }
  }

  /**
   * Integrate with AIM-OS systems (CMC, VIF, TCS)
   */
  private async integrateWithAIMOS(
    result: CodeGenerationResult,
    request: CodeGenerationRequest
  ): Promise<void> {
    try {
      // Store in CMC
      const cmcResult = await mcpService.executeTool('mcp_lucid-mcp_store_memory', {
        content: result.generated_code,
        tags: {
          'code': 1.0,
          'generation': 1.0,
          'language': 0.9,
          [request.language]: 0.9,
          [request.generation_type]: 0.9
        },
        metadata: {
          generation_type: request.generation_type,
          language: request.language,
          framework: request.framework,
          confidence: result.confidence
        }
      })

      if (cmcResult.success && cmcResult.result) {
        result.atom_id = cmcResult.result.atom_id
      }

      // Track confidence via VIF
      const vifResult = await mcpService.executeTool('mcp_lucid-mcp_track_confidence', {
        confidence_score: result.confidence,
        task_type: 'code_generation',
        context: {
          generation_type: request.generation_type,
          language: request.language
        }
      })

      if (vifResult.success && vifResult.result) {
        result.witness_id = vifResult.result.witness_id
      }

      // Track in timeline via TCS
      const tcsResult = await mcpService.executeTool('mcp_lucid-mcp_add_timeline_entry', {
        action: 'code_generation',
        context: {
          generation_type: request.generation_type,
          language: request.language,
          confidence: result.confidence,
          atom_id: result.atom_id
        }
      })

      if (tcsResult.success && tcsResult.result) {
        result.timeline_entry_id = tcsResult.result.entry_id
      }
    } catch (error) {
      console.error('ICIP AIM-OS integration error:', error)
      // Don't fail the request if integration fails
    }
  }

  /**
   * Parse code generation result from MCP tool response
   */
  private parseCodeGenerationResult(data: any): CodeGenerationResult {
    return {
      generated_code: data.generated_code || data.code || '',
      explanation: data.explanation || '',
      confidence: data.confidence || 0.5,
      language: data.language || 'typescript',
      framework: data.framework,
      dependencies: data.dependencies || [],
      test_cases: data.test_cases || [],
      documentation: data.documentation || '',
      metadata: data.metadata || {}
    }
  }

  /**
   * Parse code transformation result from MCP tool response
   */
  private parseCodeTransformationResult(data: any): CodeTransformationResult {
    return {
      original_code: data.original_code || data.source_code || '',
      transformed_code: data.transformed_code || data.target_code || '',
      transformation_type: data.transformation_type || '',
      confidence: data.confidence || 0.5,
      changes: data.changes || [],
      explanation: data.explanation || '',
      validation_results: data.validation_results || {},
      metadata: data.metadata || {}
    }
  }
}

// Singleton instance
export const icipService = new ICIPService()

