/**
 * YAML/JSON Renderer
 * Formatted YAML/JSON with syntax highlighting and collapsible sections
 */

import React, { useState } from 'react'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { Copy, Check, ChevronDown, ChevronRight } from 'lucide-react'
import yaml from 'js-yaml'

interface YAMLJSONRendererProps {
  content: string
  format: 'yaml' | 'json'
}

export const YAMLJSONRenderer: React.FC<YAMLJSONRendererProps> = ({
  content,
  format,
}) => {
  const [copied, setCopied] = useState(false)
  const [collapsed, setCollapsed] = useState(false)
  const [validationError, setValidationError] = useState<string | null>(null)

  // Validate content
  React.useEffect(() => {
    try {
      if (format === 'json') {
        JSON.parse(content)
      } else {
        yaml.load(content)
      }
      setValidationError(null)
    } catch (error: any) {
      setValidationError(error.message)
    }
  }, [content, format])

  const handleCopy = async () => {
    await navigator.clipboard.writeText(content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="relative border border-gray-700 rounded-lg overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2 bg-gray-800 border-b border-gray-700">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="p-1 text-gray-400 hover:text-gray-300"
          >
            {collapsed ? (
              <ChevronRight className="w-4 h-4" />
            ) : (
              <ChevronDown className="w-4 h-4" />
            )}
          </button>
          <span className="text-xs font-mono text-gray-400 uppercase">
            {format}
          </span>
          {validationError && (
            <span className="text-xs text-red-400 ml-2">
              Invalid {format.toUpperCase()}
            </span>
          )}
        </div>
        <button
          onClick={handleCopy}
          className="p-1 text-gray-400 hover:text-gray-300"
          title="Copy"
        >
          {copied ? (
            <Check className="w-4 h-4 text-green-400" />
          ) : (
            <Copy className="w-4 h-4" />
          )}
        </button>
      </div>

      {/* Content */}
      {!collapsed && (
        <div className="relative">
          <SyntaxHighlighter
            style={vscDarkPlus}
            language={format}
            PreTag="div"
            customStyle={{
              margin: 0,
              padding: '1rem',
              background: '#1e1e1e',
            }}
          >
            {content}
          </SyntaxHighlighter>
        </div>
      )}
    </div>
  )
}

