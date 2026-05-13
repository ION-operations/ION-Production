# ICIP Integration Design

**Author:** Nova (Code Generation Specialist)  
**Date:** 2025-01-27  
**Status:** Design Phase  
**Collaborating With:** Alex (Backend), Sage (Frontend), Aether (Coordinator)

---

## 🎯 **DESIGN OVERVIEW**

### **Objective**
Integrate ICIP (Intelligent Code Integration Platform) for code generation in Aether Chat, enabling AI-powered code generation, transformation, and validation.

### **Components to Design**
1. **ICIPService.ts** - Service client for ICIP backend integration
2. **useICIP.ts** - React hook for code generation
3. **Code Execution Sandbox** - Secure code execution infrastructure
4. **Code Validation Service** - Quality checks and validation

---

## 📋 **ICIP SERVICE CLIENT DESIGN**

### **File:** `ide_orchestration/prototypes/dac/src/services/ICIPService.ts`

### **Interface Design**

```typescript
/**
 * ICIP Service
 * Handles code generation, transformation, and validation via ICIP backend
 */

const COMMAND_SERVER_URL = 'http://localhost:5001'

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
 * Integrates with ICIP backend via Command Server MCP tools
 */
export class ICIPService {
  private commandServerUrl: string

  constructor(commandServerUrl: string = COMMAND_SERVER_URL) {
    this.commandServerUrl = commandServerUrl
  }

  /**
   * Generate code using ICIP
   */
  async generateCode(
    request: CodeGenerationRequest
  ): Promise<{ success: boolean; result?: CodeGenerationResult; error?: string }> {
    try {
      // TODO: Determine if ICIP uses MCP tools or direct service endpoint
      // For now, assuming MCP tool pattern (similar to APOE)
      const response = await fetch(`${this.commandServerUrl}/mcp/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          tool: 'mcp_lucid-mcp_generate_code',  // TODO: Confirm tool name
          arguments: {
            generation_type: request.generation_type,
            description: request.description,
            language: request.language,
            framework: request.framework,
            context: request.context || {},
            metadata: request.metadata || {}
          }
        })
      })

      if (!response.ok) {
        throw new Error(`Command Server error: ${response.status} ${response.statusText}`)
      }

      const data = await response.json()

      if (data.success && data.result) {
        // Store in CMC (via MCP tool)
        const cmcResult = await this.storeInCMC(data.result, request)
        
        // Track confidence via VIF (via MCP tool)
        const vifResult = await this.trackConfidence(data.result.confidence, {
          task: 'code_generation',
          generation_type: request.generation_type,
          language: request.language
        })

        // Track in timeline via TCS (via MCP tool)
        const tcsResult = await this.trackInTimeline({
          action: 'code_generation',
          generation_type: request.generation_type,
          language: request.language,
          confidence: data.result.confidence
        })

        return {
          success: true,
          result: {
            ...data.result,
            atom_id: cmcResult?.atom_id,
            witness_id: vifResult?.witness_id,
            timeline_entry_id: tcsResult?.entry_id
          }
        }
      } else {
        return {
          success: false,
          error: data.error || 'Failed to generate code'
        }
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
   * Transform code using ICIP
   */
  async transformCode(
    request: CodeTransformationRequest
  ): Promise<{ success: boolean; result?: CodeTransformationResult; error?: string }> {
    try {
      const response = await fetch(`${this.commandServerUrl}/mcp/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          tool: 'mcp_lucid-mcp_transform_code',  // TODO: Confirm tool name
          arguments: {
            transformation_type: request.transformation_type,
            source_code: request.source_code,
            source_language: request.source_language,
            target_language: request.target_language,
            transformation_rules: request.transformation_rules || {},
            context: request.context || {}
          }
        })
      })

      if (!response.ok) {
        throw new Error(`Command Server error: ${response.status} ${response.statusText}`)
      }

      const data = await response.json()

      if (data.success && data.result) {
        return {
          success: true,
          result: data.result
        }
      } else {
        return {
          success: false,
          error: data.error || 'Failed to transform code'
        }
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
   * Validate generated code
   */
  async validateCode(
    code: string,
    language: string
  ): Promise<{ success: boolean; result?: CodeValidationResult; error?: string }> {
    try {
      // TODO: Implement validation (syntax, quality, security)
      // For now, basic structure
      return {
        success: true,
        result: {
          valid: true,
          errors: [],
          warnings: [],
          quality_metrics: {},
          confidence: 0.85
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
   * Store generated code in CMC
   */
  private async storeInCMC(
    result: CodeGenerationResult,
    request: CodeGenerationRequest
  ): Promise<{ atom_id?: string }> {
    try {
      const response = await fetch(`${this.commandServerUrl}/mcp/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          tool: 'mcp_lucid-mcp_store_memory',
          arguments: {
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
          }
        })
      })

      const data = await response.json()
      return { atom_id: data.result?.atom_id }
    } catch (error) {
      console.error('ICIP CMC storage error:', error)
      return {}
    }
  }

  /**
   * Track confidence via VIF
   */
  private async trackConfidence(
    confidence: number,
    context: Record<string, any>
  ): Promise<{ witness_id?: string }> {
    try {
      const response = await fetch(`${this.commandServerUrl}/mcp/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          tool: 'mcp_lucid-mcp_track_confidence',
          arguments: {
            confidence_score: confidence,
            task_type: 'code_generation',
            context: context
          }
        })
      })

      const data = await response.json()
      return { witness_id: data.result?.witness_id }
    } catch (error) {
      console.error('ICIP VIF tracking error:', error)
      return {}
    }
  }

  /**
   * Track in timeline via TCS
   */
  private async trackInTimeline(
    entry: Record<string, any>
  ): Promise<{ entry_id?: string }> {
    try {
      const response = await fetch(`${this.commandServerUrl}/mcp/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          tool: 'mcp_lucid-mcp_add_timeline_entry',
          arguments: {
            action: entry.action,
            context: entry
          }
        })
      })

      const data = await response.json()
      return { entry_id: data.result?.entry_id }
    } catch (error) {
      console.error('ICIP TCS tracking error:', error)
      return {}
    }
  }
}

// Singleton instance
export const icipService = new ICIPService()

