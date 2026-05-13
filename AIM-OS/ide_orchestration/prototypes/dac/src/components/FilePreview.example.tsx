/**
 * FilePreview Usage Example
 * 
 * This file demonstrates how to use the FilePreview component
 */

import React, { useState } from 'react'
import { FilePreview } from './FilePreview'
import { Eye, Code } from 'lucide-react'

// Example usage in a component
export const FilePreviewExample: React.FC = () => {
  const [previewMode, setPreviewMode] = useState(false)
  const [content, setContent] = useState(`# Example Markdown File

This is a **markdown** file with various features.

## Code Blocks

Here's a TypeScript code block:

\`\`\`typescript
function greet(name: string): string {
  return \`Hello, \${name}!\`
}

const message = greet('World')
console.log(message)
\`\`\`

## Math Support

Inline math: $E = mc^2$

Block math:
$$
\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}
$$

## Lists

- Item 1
- Item 2
- Item 3

## Inline Code

Use \`console.log()\` for debugging.

## Blockquotes

> This is a blockquote
> with multiple lines
`)

  return (
    <div className="h-full flex flex-col">
      {/* Toolbar */}
      <div className="px-4 py-2 border-b border-gray-700 bg-gray-800 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Code className="w-4 h-4 text-gray-400" />
          <span className="text-sm text-gray-300">example.md</span>
        </div>
        <button
          onClick={() => setPreviewMode(!previewMode)}
          className={`px-3 py-1.5 rounded text-xs flex items-center gap-2 transition-colors ${
            previewMode
              ? 'bg-blue-900/50 text-blue-300'
              : 'text-gray-400 hover:bg-gray-700'
          }`}
        >
          <Eye className="w-4 h-4" />
          {previewMode ? 'Edit' : 'Preview'}
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-hidden">
        {previewMode ? (
          <FilePreview
            content={content}
            theme="vs-dark"
            showLineNumbers={true}
          />
        ) : (
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            className="w-full h-full p-4 bg-gray-950 text-gray-100 font-mono text-sm resize-none focus:outline-none"
          />
        )}
      </div>
    </div>
  )
}

