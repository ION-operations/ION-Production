/**
 * useCodeExecution Hook
 * React hook for secure code execution in sandbox
 */

import { useState, useCallback } from 'react'
import {
  codeExecutionService,
  CodeExecutionRequest,
  CodeExecutionResult
} from '../services/CodeExecutionService'
import { getActiveIntegrationContext } from '../utils/integrationTags'

export interface UseCodeExecutionOptions {
  autoValidate?: boolean  // Auto-validate code before execution
  storeInCMC?: boolean    // Auto-store results in CMC (handled by service)
  trackConfidence?: boolean  // Auto-track via VIF (handled by service)
  trackInTimeline?: boolean  // Auto-track via TCS (handled by service)
  defaultTimeout?: number  // Default timeout in milliseconds
  defaultMemory?: number   // Default memory in MB
  defaultCpu?: number      // Default CPU percentage
}

export interface UseCodeExecutionReturn {
  // State
  executing: boolean
  error: string | null
  lastResult: CodeExecutionResult | null

  // Execution methods
  executeCode: (request: CodeExecutionRequest) => Promise<CodeExecutionResult | null>
  executeCodeQuick: (code: string, language: string) => Promise<CodeExecutionResult | null>

  // Utility methods
  clearError: () => void
  clearResults: () => void
}

/**
 * useCodeExecution Hook
 * Provides secure code execution in sandbox
 */
export function useCodeExecution(
  options: UseCodeExecutionOptions = {}
): UseCodeExecutionReturn {
  const {
    autoValidate = true,
    defaultTimeout = 30000,
    defaultMemory = 512,
    defaultCpu = 0.5
  } = options

  // State
  const [executing, setExecuting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [lastResult, setLastResult] = useState<CodeExecutionResult | null>(null)

  /**
   * Execute code in secure sandbox
   */
  const executeCode = useCallback(async (
    request: CodeExecutionRequest
  ): Promise<CodeExecutionResult | null> => {
    setExecuting(true)
    setError(null)

    try {
      // Apply defaults
      const executionRequest: CodeExecutionRequest = {
        ...request,
        timeout: request.timeout || defaultTimeout,
        memory: request.memory || defaultMemory,
        cpu: request.cpu || defaultCpu,
        integrationContext: request.integrationContext || getActiveIntegrationContext() || undefined
      }

      const response = await codeExecutionService.execute(executionRequest)

      if (response.success && response.result) {
        const result = response.result
        setLastResult(result)

        return result
      } else {
        const errorMsg = response.error || 'Code execution failed'
        setError(errorMsg)
        return null
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error'
      setError(errorMsg)
      return null
    } finally {
      setExecuting(false)
    }
  }, [defaultTimeout, defaultMemory, defaultCpu])

  /**
   * Quick code execution (convenience method)
   */
  const executeCodeQuick = useCallback(async (
    code: string,
    language: string = 'typescript'
  ): Promise<CodeExecutionResult | null> => {
    return executeCode({
      code,
      language
    })
  }, [executeCode])

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
    setError(null)
  }, [])

  return {
    // State
    executing,
    error,
    lastResult,

    // Execution methods
    executeCode,
    executeCodeQuick,

    // Utility methods
    clearError,
    clearResults
  }
}

