# useICIP Hook Design

**Author:** Nova (Code Generation Specialist)  
**Date:** 2025-01-27  
**Status:** Design Phase  
**Collaborating With:** Alex (Backend), Sage (Frontend), Aether (Coordinator)

---

## 🎯 **DESIGN OVERVIEW**

### **Objective**
Create a React hook (`useICIP`) that provides code generation capabilities to Aether Chat frontend components.

### **File:** `ide_orchestration/prototypes/dac/src/hooks/useICIP.ts`

---

## 📋 **HOOK INTERFACE DESIGN**

```typescript
/**
 * useICIP Hook
 * React hook for ICIP code generation, transformation, and validation
 */

import { useState, useCallback } from 'react'
import { icipService, CodeGenerationRequest, CodeGenerationResult, CodeTransformationRequest, CodeTransformationResult, CodeValidationResult } from '../services/ICIPService'

export interface UseICIPOptions {
  autoValidate?: boolean  // Auto-validate generated code
  storeInCMC?: boolean    // Auto-store in CMC
  trackConfidence?: boolean  // Auto-track via VIF
  trackInTimeline?: boolean  // Auto-track via TCS
}

export interface UseICIPReturn {
  // State
  generating: boolean
  transforming: boolean
  validating: boolean
  error: string | null
  lastResult: CodeGenerationResult | null
  lastTransformation: CodeTransformationResult | null
  lastValidation: CodeValidationResult | null

  // Generation methods
  generateCode: (request: CodeGenerationRequest) => Promise<CodeGenerationResult | null>
  generateFunction: (description: string, language: string, framework?: string) => Promise<CodeGenerationResult | null>
  generateClass: (description: string, language: string, framework?: string) => Promise<CodeGenerationResult | null>
  generateTest: (description: string, language: string, framework?: string) => Promise<CodeGenerationResult | null>
  generateDocumentation: (code: string, language: string) => Promise<CodeGenerationResult | null>
  completeCode: (code: string, language: string, context?: string) => Promise<CodeGenerationResult | null>
  refactorCode: (code: string, language: string, refactoringType?: string) => Promise<CodeGenerationResult | null>

  // Transformation methods
  transformCode: (request: CodeTransformationRequest) => Promise<CodeTransformationResult | null>

  // Validation methods
  validateCode: (code: string, language: string) => Promise<CodeValidationResult | null>

  // Utility methods
  clearError: () => void
  clearResults: () => void
}

/**
 * useICIP Hook
 * Provides code generation, transformation, and validation capabilities
 */
export function useICIP(options: UseICIPOptions = {}): UseICIPReturn {
  const {
    autoValidate = true,
    storeInCMC = true,
    trackConfidence = true,
    trackInTimeline = true
  } = options

  // State
  const [generating, setGenerating] = useState(false)
  const [transforming, setTransforming] = useState(false)
  const [validating, setValidating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [lastResult, setLastResult] = useState<CodeGenerationResult | null>(null)
  const [lastTransformation, setLastTransformation] = useState<CodeTransformationResult | null>(null)
  const [lastValidation, setLastValidation] = useState<CodeValidationResult | null>(null)

  /**
   * Generic code generation
   */
  const generateCode = useCallback(async (
    request: CodeGenerationRequest
  ): Promise<CodeGenerationResult | null> => {
    setGenerating(true)
    setError(null)

    try {
      const response = await icipService.generateCode(request)

      if (response.success && response.result) {
        const result = response.result
        setLastResult(result)

        // Auto-validate if enabled
        if (autoValidate) {
          await validateCode(result.generated_code, result.language)
        }

        return result
      } else {
        const errorMsg = response.error || 'Failed to generate code'
        setError(errorMsg)
        return null
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error'
      setError(errorMsg)
      return null
    } finally {
      setGenerating(false)
    }
  }, [autoValidate])

  /**
   * Generate function
   */
  const generateFunction = useCallback(async (
    description: string,
    language: string = 'typescript',
    framework?: string
  ): Promise<CodeGenerationResult | null> => {
    return generateCode({
      generation_type: 'function',
      description,
      language,
      framework
    })
  }, [generateCode])

  /**
   * Generate class
   */
  const generateClass = useCallback(async (
    description: string,
    language: string = 'typescript',
    framework?: string
  ): Promise<CodeGenerationResult | null> => {
    return generateCode({
      generation_type: 'class',
      description,
      language,
      framework
    })
  }, [generateCode])

  /**
   * Generate test
   */
  const generateTest = useCallback(async (
    description: string,
    language: string = 'typescript',
    framework?: string
  ): Promise<CodeGenerationResult | null> => {
    return generateCode({
      generation_type: 'test',
      description,
      language,
      framework
    })
  }, [generateCode])

  /**
   * Generate documentation
   */
  const generateDocumentation = useCallback(async (
    code: string,
    language: string = 'typescript'
  ): Promise<CodeGenerationResult | null> => {
    return generateCode({
      generation_type: 'documentation',
      description: `Generate documentation for this ${language} code:\n\n${code}`,
      language
    })
  }, [generateCode])

  /**
   * Complete code
   */
  const completeCode = useCallback(async (
    code: string,
    language: string = 'typescript',
    context?: string
  ): Promise<CodeGenerationResult | null> => {
    return generateCode({
      generation_type: 'completion',
      description: context 
        ? `Complete this ${language} code with context: ${context}\n\n${code}`
        : `Complete this ${language} code:\n\n${code}`,
      language,
      context: context ? { context } : undefined
    })
  }, [generateCode])

  /**
   * Refactor code
   */
  const refactorCode = useCallback(async (
    code: string,
    language: string = 'typescript',
    refactoringType?: string
  ): Promise<CodeGenerationResult | null> => {
    return generateCode({
      generation_type: 'refactoring',
      description: refactoringType
        ? `Refactor this ${language} code using ${refactoringType}:\n\n${code}`
        : `Refactor this ${language} code:\n\n${code}`,
      language
    })
  }, [generateCode])

  /**
   * Transform code
   */
  const transformCode = useCallback(async (
    request: CodeTransformationRequest
  ): Promise<CodeTransformationResult | null> => {
    setTransforming(true)
    setError(null)

    try {
      const response = await icipService.transformCode(request)

      if (response.success && response.result) {
        const result = response.result
        setLastTransformation(result)
        return result
      } else {
        const errorMsg = response.error || 'Failed to transform code'
        setError(errorMsg)
        return null
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error'
      setError(errorMsg)
      return null
    } finally {
      setTransforming(false)
    }
  }, [])

  /**
   * Validate code
   */
  const validateCode = useCallback(async (
    code: string,
    language: string
  ): Promise<CodeValidationResult | null> => {
    setValidating(true)
    setError(null)

    try {
      const response = await icipService.validateCode(code, language)

      if (response.success && response.result) {
        const result = response.result
        setLastValidation(result)
        return result
      } else {
        const errorMsg = response.error || 'Failed to validate code'
        setError(errorMsg)
        return null
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error'
      setError(errorMsg)
      return null
    } finally {
      setValidating(false)
    }
  }, [])

  /**
   * Clear error
   */
  const clearError = useCallback(() => {
    setError(null)
  }, [])

  /**
   * Clear results
   */
  const clearResults = useCallback(() => {
    setLastResult(null)
    setLastTransformation(null)
    setLastValidation(null)
    setError(null)
  }, [])

  return {
    // State
    generating,
    transforming,
    validating,
    error,
    lastResult,
    lastTransformation,
    lastValidation,

    // Generation methods
    generateCode,
    generateFunction,
    generateClass,
    generateTest,
    generateDocumentation,
    completeCode,
    refactorCode,

    // Transformation methods
    transformCode,

    // Validation methods
    validateCode,

    // Utility methods
    clearError,
    clearResults
  }
}

