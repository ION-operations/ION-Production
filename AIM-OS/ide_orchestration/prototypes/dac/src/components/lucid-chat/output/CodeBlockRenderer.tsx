/**
 * Code Block Renderer
 * Enhanced code block rendering with syntax highlighting and copy functionality
 */

import React, { useState } from 'react'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { Copy, Check } from 'lucide-react'

interface CodeBlockRendererProps {
  code: string
  language?: string
  inline?: boolean
}

export const CodeBlockRenderer: React.FC<CodeBlockRendererProps> = ({
  code,
  language = 'text',
  inline = false,
}) => {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  if (inline) {
    return (
      <code className="px-1.5 py-0.5 bg-gray-800 rounded text-sm text-blue-300 font-mono">
        {code}
      </code>
    )
  }

  return (
    <div className="relative group">
      <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
        <button
          onClick={handleCopy}
          className="p-1.5 bg-gray-700 rounded text-xs text-gray-300 hover:bg-gray-600 transition-colors"
          title="Copy code"
        >
          {copied ? (
            <Check className="w-3.5 h-3.5 text-green-400" />
          ) : (
            <Copy className="w-3.5 h-3.5" />
          )}
        </button>
      </div>
      <SyntaxHighlighter
        style={vscDarkPlus}
        language={language}
        PreTag="div"
        className="rounded-lg"
        customStyle={{
          margin: 0,
          padding: '1rem',
          background: '#1e1e1e',
        }}
      >
        {code}
      </SyntaxHighlighter>
      {language && language !== 'text' && (
        <div className="absolute bottom-2 right-2 text-xs text-gray-500 font-mono">
          {language}
        </div>
      )}
    </div>
  )
}

