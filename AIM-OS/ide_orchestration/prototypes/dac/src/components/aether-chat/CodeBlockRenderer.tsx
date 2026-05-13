/**
 * Code Block Renderer Component
 * Displays generated code with syntax highlighting and actions
 * Created by Sage - Frontend Integration Specialist
 */

import React, { useState } from 'react'
import { Copy, Check, Play, Download, FileCode, Shield } from 'lucide-react'
import { ConfidenceBadge } from '../shared'

export interface CodeGenerationResult {
  generated_code: string
  explanation: string
  confidence: number
  language: string
  framework?: string
  dependencies?: string[]
  test_cases?: string[]
  documentation?: string
}

export interface CodeBlockRendererProps {
  result: CodeGenerationResult
  onExecute?: () => void
  onCopy?: (code: string) => void
  showConfidence?: boolean
  showActions?: boolean
  className?: string
}

export const CodeBlockRenderer: React.FC<CodeBlockRendererProps> = ({
  result,
  onExecute,
  onCopy,
  showConfidence = true,
  showActions = true,
  className = '',
}) => {
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(result.generated_code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
    onCopy?.(result.generated_code)
  }

  // Simple syntax highlighting (can be enhanced with Prism.js or highlight.js)
  const getLanguageClass = (language: string) => {
    const langMap: Record<string, string> = {
      typescript: 'language-typescript',
      javascript: 'language-javascript',
      python: 'language-python',
      rust: 'language-rust',
      go: 'language-go',
      java: 'language-java',
      cpp: 'language-cpp',
    }
    return langMap[language.toLowerCase()] || 'language-text'
  }

  return (
    <div className={`flex flex-col gap-3 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <FileCode className="w-4 h-4 text-blue-400" />
          <span className="text-sm font-medium text-gray-300">
            {result.language.charAt(0).toUpperCase() + result.language.slice(1)}
            {result.framework && ` • ${result.framework}`}
          </span>
          {showConfidence && (
            <ConfidenceBadge confidence={result.confidence} size="sm" />
          )}
        </div>
        {showActions && (
          <div className="flex items-center gap-2">
            <button
              onClick={handleCopy}
              className="p-1.5 rounded text-gray-400 hover:text-gray-200 hover:bg-gray-700 transition-colors"
              title="Copy code"
            >
              {copied ? (
                <Check className="w-4 h-4 text-green-400" />
              ) : (
                <Copy className="w-4 h-4" />
              )}
            </button>
            {onExecute && (
              <button
                onClick={onExecute}
                className="p-1.5 rounded text-gray-400 hover:text-green-400 hover:bg-gray-700 transition-colors"
                title="Execute code"
              >
                <Play className="w-4 h-4" />
              </button>
            )}
            <button
              onClick={() => {
                const blob = new Blob([result.generated_code], { type: 'text/plain' })
                const url = URL.createObjectURL(blob)
                const a = document.createElement('a')
                a.href = url
                a.download = `generated.${result.language}`
                a.click()
                URL.revokeObjectURL(url)
              }}
              className="p-1.5 rounded text-gray-400 hover:text-gray-200 hover:bg-gray-700 transition-colors"
              title="Download code"
            >
              <Download className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>

      {/* Code Block */}
      <div className="relative">
        <pre className="bg-gray-900 rounded-lg p-4 overflow-x-auto border border-gray-700">
          <code className={`${getLanguageClass(result.language)} text-sm text-gray-200`}>
            {result.generated_code}
          </code>
        </pre>
      </div>

      {/* Explanation */}
      {result.explanation && (
        <div className="bg-blue-900/20 border border-blue-700/50 rounded-lg p-3">
          <p className="text-sm text-gray-300">{result.explanation}</p>
        </div>
      )}

      {/* Metadata */}
      <div className="flex flex-wrap gap-4 text-xs text-gray-400">
        {result.dependencies && result.dependencies.length > 0 && (
          <div className="flex items-center gap-1">
            <span className="font-medium">Dependencies:</span>
            <span>{result.dependencies.join(', ')}</span>
          </div>
        )}
        {result.test_cases && result.test_cases.length > 0 && (
          <div className="flex items-center gap-1">
            <span className="font-medium">Test Cases:</span>
            <span>{result.test_cases.length}</span>
          </div>
        )}
        {result.documentation && (
          <div className="flex items-center gap-1">
            <Shield className="w-3 h-3" />
            <span>Documentation included</span>
          </div>
        )}
      </div>
    </div>
  )
}

