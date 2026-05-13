/**
 * FilePreviewView - Main View Wrapper for FilePreview
 * 
 * Wraps FilePreview component for use as a main view in DAC v2 IDE.
 * Manages file content access and provides integration with IDE state.
 */

import React, { useState, useEffect } from 'react'
import { FilePreview } from '../components/FilePreview'
import { FileText, Code, Eye, Edit3, Loader2 } from 'lucide-react'

export interface FilePreviewViewProps {
  // Optional: If content is provided directly
  content?: string
  // Optional: File path to load content from
  filePath?: string
}

const DEMO_CONTENT = `# File Preview - Cursor IDE Style

Welcome to the **File Preview** view! This demonstrates Cursor IDE-style markdown rendering with syntax-highlighted code blocks, professional icons, and image support.

## Features

- ✅ **Markdown Rendering** - Full markdown support
- ✅ **Syntax Highlighting** - Monaco Editor code blocks
- ✅ **Math Support** - LaTeX math rendering
- ✅ **Copy Buttons** - One-click code copying
- ✅ **Line Numbers** - Optional line numbers
- ✅ **Professional Icons** - High-grade icon replacements for emojis
- ✅ **Image Support** - Beautiful image rendering with captions

## Image Examples

Here's an example of an embedded image:

![AIM-OS Architecture](https://via.placeholder.com/800x400/1a1a1a/60a5fa?text=AIM-OS+Architecture+Diagram "System Architecture")

Images are rendered with professional styling, including:
- Elegant borders and shadows
- Smooth hover effects
- Loading states
- Error handling
- Caption support

## Code Examples

### TypeScript

\`\`\`typescript
interface User {
  id: string
  name: string
  email: string
}

function greetUser(user: User): string {
  return \`Hello, \${user.name}!\`
}

const user: User = {
  id: '1',
  name: 'Alice',
  email: 'alice@example.com'
}

console.log(greetUser(user))
\`\`\`

### Python

\`\`\`python
def fibonacci(n: int) -> list[int]:
    """Generate Fibonacci sequence up to n terms."""
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    elif n == 2:
        return [0, 1]
    
    sequence = [0, 1]
    for i in range(2, n):
        sequence.append(sequence[i-1] + sequence[i-2])
    return sequence

# Example usage
result = fibonacci(10)
print(f"Fibonacci sequence: {result}")
\`\`\`

### JavaScript

\`\`\`javascript
// Async/await example
async function fetchUserData(userId) {
  try {
    const response = await fetch(\`/api/users/\${userId}\`)
    if (!response.ok) {
      throw new Error(\`HTTP error! status: \${response.status}\`)
    }
    const data = await response.json()
    return data
  } catch (error) {
    console.error('Error fetching user:', error)
    throw error
  }
}

// Usage
fetchUserData('123')
  .then(user => console.log('User:', user))
  .catch(error => console.error('Failed:', error))
\`\`\`

## Math Examples

### Inline Math

Einstein's famous equation: $E = mc^2$

The quadratic formula: $x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$

### Block Math

The Gaussian integral:
$$
\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}
$$

Fourier transform:
$$
\\hat{f}(\\xi) = \\int_{-\\infty}^{\\infty} f(x) e^{-2\\pi i \\xi x} dx
$$

## Professional Icons

Instead of standard emojis, we use professional icons:

- ✅ Check marks → CheckCircle icon
- ❌ Cross marks → XCircle icon
- ⚠️ Warnings → AlertCircle icon
- ⭐ Stars → Star icon
- ⚡ Energy → Zap icon
- 🚀 Rockets → Rocket icon
- 💡 Ideas → Lightbulb icon
- 🎯 Targets → Target icon
- 🛡️ Protection → Shield icon
- 🏆 Achievements → Trophy icon

## Lists

### Unordered List

- First item
- Second item
  - Nested item
  - Another nested item
- Third item

### Ordered List

1. First step
2. Second step
3. Third step

## Blockquotes

> This is a blockquote. It can contain multiple paragraphs.
>
> And here's another paragraph in the same blockquote.

## Inline Code

Use \`console.log()\` for debugging, or \`const x = 42\` for variables.

## Links

Visit [AIM-OS Documentation](https://github.com/aimos) for more information.

---

**Note:** This is demo content. In production, FilePreview will load actual file content from your workspace.
`

export const FilePreviewView: React.FC<FilePreviewViewProps> = ({
  content: providedContent,
  filePath,
}) => {
  const [content, setContent] = useState<string>(providedContent || DEMO_CONTENT)
  const [loading, setLoading] = useState(false)
  const [showEditor, setShowEditor] = useState(false)
  const [editContent, setEditContent] = useState<string>(content)

  // Load content from file if filePath is provided
  useEffect(() => {
    if (filePath && !providedContent) {
      loadFileContent(filePath)
    } else if (providedContent) {
      setContent(providedContent)
      setEditContent(providedContent)
    } else {
      // Use demo content if nothing provided
      setContent(DEMO_CONTENT)
      setEditContent(DEMO_CONTENT)
    }
  }, [filePath, providedContent])

  const loadFileContent = async (path: string) => {
    setLoading(true)
    try {
      // Try localStorage first
      const storedContent = localStorage.getItem(`file-content-${path}`)
      if (storedContent) {
        setContent(storedContent)
        setEditContent(storedContent)
      } else {
        // Use demo content as fallback
        setContent(DEMO_CONTENT)
        setEditContent(DEMO_CONTENT)
      }
    } catch (error) {
      console.error('Error loading file:', error)
      setContent('# Error\n\nFailed to load file content.')
    } finally {
      setLoading(false)
    }
  }

  const handleSave = () => {
    setContent(editContent)
    setShowEditor(false)
    if (filePath) {
      localStorage.setItem(`file-content-${filePath}`, editContent)
    }
  }

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center bg-gray-900">
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="w-8 h-8 animate-spin text-blue-400" />
          <span className="text-gray-400 text-sm">Loading file...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col bg-gray-900">
      {/* Header Bar */}
      <div className="h-10 px-4 border-b border-gray-700 bg-gray-800 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <FileText className="w-4 h-4 text-blue-400" />
          <span className="text-sm text-gray-300 font-mono">
            {filePath || 'preview.md'}
          </span>
          <span className="text-xs text-gray-500 px-2 py-0.5 bg-gray-700 rounded">
            {showEditor ? 'Edit Mode' : 'Preview Mode'}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => {
              if (showEditor) {
                handleSave()
              } else {
                setShowEditor(true)
              }
            }}
            className={`px-2 py-1 rounded text-xs flex items-center gap-1.5 transition-colors ${
              showEditor
                ? 'bg-green-900/50 text-green-300 hover:bg-green-900/70'
                : 'text-gray-400 hover:bg-gray-700 hover:text-gray-200'
            }`}
            title={showEditor ? 'Save and preview' : 'Edit content'}
          >
            {showEditor ? (
              <>
                <Eye className="w-3 h-3" />
                <span>Preview</span>
              </>
            ) : (
              <>
                <Edit3 className="w-3 h-3" />
                <span>Edit</span>
              </>
            )}
          </button>
          <div className="h-4 w-px bg-gray-700" />
          <div className="flex items-center gap-2 text-xs text-gray-500">
            <Eye className="w-3 h-3" />
            <span>File Preview</span>
          </div>
        </div>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-hidden">
        {showEditor ? (
          <div className="h-full flex flex-col">
            <div className="px-4 py-2 bg-gray-800 border-b border-gray-700 flex items-center justify-between">
              <span className="text-xs text-gray-400">Edit Markdown Content</span>
              <button
                onClick={handleSave}
                className="px-2 py-1 text-xs bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors"
              >
                Save & Preview
              </button>
            </div>
            <textarea
              value={editContent}
              onChange={(e) => setEditContent(e.target.value)}
              className="flex-1 w-full p-4 bg-gray-950 text-gray-100 font-mono text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter markdown content here..."
            />
          </div>
        ) : (
          <FilePreview
            content={content}
            theme="vs-dark"
            showLineNumbers={true}
          />
        )}
      </div>
    </div>
  )
}

export default FilePreviewView

