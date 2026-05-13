/**
 * Code Execution UI Component
 * Interface for executing code in sandbox and displaying results
 * Created by Sage - Frontend Integration Specialist
 * Integrates with Nova's code execution service
 */

import React, { useState } from 'react'
import { Play, Square, CheckCircle, XCircle, AlertTriangle, Clock } from 'lucide-react'
import { LoadingSpinner, ErrorDisplay } from '../shared'
import { CodeExecutionLoadingState } from './LoadingStates'

export interface ExecutionResult {
  success: boolean
  output?: string
  error?: string
  executionTime?: number
  memoryUsed?: number
  exitCode?: number
}

export interface CodeExecutionUIProps {
  code: string
  language: string
  onExecute: (code: string, language: string) => Promise<ExecutionResult>
  executing?: boolean
  result?: ExecutionResult
  className?: string
}

export const CodeExecutionUI: React.FC<CodeExecutionUIProps> = ({
  code,
  language,
  onExecute,
  executing = false,
  result,
  className = '',
}) => {
  const [isExecuting, setIsExecuting] = useState(false)
  const [executionResult, setExecutionResult] = useState<ExecutionResult | undefined>(result)

  const handleExecute = async () => {
    if (!code.trim() || isExecuting) return

    setIsExecuting(true)
    try {
      const result = await onExecute(code, language)
      setExecutionResult(result)
    } catch (error) {
      setExecutionResult({
        success: false,
        error: error instanceof Error ? error.message : 'Execution failed',
      })
    } finally {
      setIsExecuting(false)
    }
  }

  const isCurrentlyExecuting = executing || isExecuting

  return (
    <div className={`flex flex-col gap-4 ${className}`}>
      {/* Execute Button */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-gray-300">
            Code Execution
          </span>
          <span className="text-xs text-gray-500">
            {language.charAt(0).toUpperCase() + language.slice(1)}
          </span>
        </div>
        <button
          onClick={handleExecute}
          disabled={!code.trim() || isCurrentlyExecuting}
          className="flex items-center gap-2 px-4 py-2 rounded bg-green-600 text-white font-medium hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isCurrentlyExecuting ? (
            <>
              <LoadingSpinner size="sm" />
              <span>Executing...</span>
            </>
          ) : (
            <>
              <Play className="w-4 h-4" />
              <span>Execute</span>
            </>
          )}
        </button>
      </div>

      {/* Execution Status */}
      {isCurrentlyExecuting && (
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <CodeExecutionLoadingState
            operation="Executing code in sandbox..."
            size="md"
          />
        </div>
      )}

      {/* Execution Result */}
      {executionResult && !isCurrentlyExecuting && (
        <div className="flex flex-col gap-3">
          {executionResult.success ? (
            <div className="bg-green-900/20 border border-green-700/50 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-3">
                <CheckCircle className="w-5 h-5 text-green-400" />
                <span className="text-sm font-medium text-green-400">
                  Execution Successful
                </span>
                {executionResult.executionTime && (
                  <span className="text-xs text-gray-400 flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {executionResult.executionTime}ms
                  </span>
                )}
              </div>
              {executionResult.output && (
                <div className="bg-gray-900 rounded p-3 mt-2">
                  <pre className="text-sm text-gray-200 whitespace-pre-wrap font-mono">
                    {executionResult.output}
                  </pre>
                </div>
              )}
              {executionResult.memoryUsed && (
                <div className="text-xs text-gray-400 mt-2">
                  Memory: {executionResult.memoryUsed}MB
                </div>
              )}
            </div>
          ) : (
            <div className="bg-red-900/20 border border-red-700/50 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-3">
                <XCircle className="w-5 h-5 text-red-400" />
                <span className="text-sm font-medium text-red-400">
                  Execution Failed
                </span>
                {executionResult.exitCode !== undefined && (
                  <span className="text-xs text-gray-400">
                    Exit Code: {executionResult.exitCode}
                  </span>
                )}
              </div>
              {executionResult.error && (
                <ErrorDisplay
                  error={executionResult.error}
                  errorType="system"
                  title="Execution Error"
                />
              )}
            </div>
          )}
        </div>
      )}

      {/* Security Notice */}
      <div className="bg-yellow-900/20 border border-yellow-700/50 rounded-lg p-3">
        <div className="flex items-start gap-2">
          <AlertTriangle className="w-4 h-4 text-yellow-400 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-xs text-yellow-400 font-medium mb-1">
              Sandbox Execution
            </p>
            <p className="text-xs text-gray-400">
              Code is executed in an isolated sandbox environment with resource limits and security restrictions.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

