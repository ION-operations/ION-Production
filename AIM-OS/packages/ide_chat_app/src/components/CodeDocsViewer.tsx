import React, { useRef, useState, useEffect } from 'react'
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels'
import { LucidMonacoEditor } from './LucidMonacoEditor'
import { BookOpen, Code as CodeIcon } from 'lucide-react'

interface CodeDocsViewerProps {
  codeFile?: string
  docFile?: string
  codeContent?: string
  docContent?: string
}

// Extract code elements from JSDoc comments
interface CodeElement {
  name: string
  type: 'function' | 'class' | 'method'
  startLine: number
  endLine: number
  jsdoc: string
}

function extractCodeElements(code: string): CodeElement[] {
  const elements: CodeElement[] = []
  const lines = code.split('\n')
  let currentJsdoc = ''
  let jsdocStart = -1

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]
    
    // Start of JSDoc comment
    if (line.trim().startsWith('/**')) {
      currentJsdoc = line
      jsdocStart = i
    }
    // Continuation of JSDoc comment
    else if (currentJsdoc && (line.includes('*/') || line.trim().startsWith('*'))) {
      currentJsdoc += '\n' + line
      if (line.includes('*/')) {
        // End of JSDoc, check next line for declaration
        if (i + 1 < lines.length) {
          const nextLine = lines[i + 1]
          // Match function declaration
          const functionMatch = nextLine.match(/(?:function|const|export\s+(?:function|const))\s+(\w+)/)
          const classMatch = nextLine.match(/class\s+(\w+)/)
          
          if (functionMatch || classMatch) {
            const name = functionMatch ? functionMatch[1] : classMatch![1]
            const type = classMatch ? 'class' : 'function'
            elements.push({
              name,
              type,
              startLine: jsdocStart,
              endLine: jsdocStart + currentJsdoc.split('\n').length,
              jsdoc: currentJsdoc
            })
          }
        }
        currentJsdoc = ''
        jsdocStart = -1
      }
    }
    // Reset if we hit code without JSDoc
    else if (currentJsdoc && !line.trim().startsWith('//')) {
      currentJsdoc = ''
      jsdocStart = -1
    }
  }

  return elements
}

export const CodeDocsViewer: React.FC<CodeDocsViewerProps> = ({
  codeFile,
  docFile,
  codeContent,
  docContent
}) => {
  const [selectedElement, setSelectedElement] = useState<string | null>(null)
  const [codeElements, setCodeElements] = useState<CodeElement[]>([])
  const [hoveredDocElement, setHoveredDocElement] = useState<string | null>(null)
  const codePanelRef = useRef<HTMLDivElement>(null)
  const docPanelRef = useRef<HTMLDivElement>(null)

  // Sample code with inline documentation
  const defaultCode = codeContent || `/**
 * Calculates the sum of two numbers
 * @param a - First number
 * @param b - Second number
 * @returns The sum of a and b
 */
function add(a: number, b: number): number {
  return a + b
}

/**
 * Represents a user in the system
 */
class User {
  name: string
  age: number
  
  /**
   * Creates a new User instance
   * @param name - User's name
   * @param age - User's age
   */
  constructor(name: string, age: number) {
    this.name = name
    this.age = age
  }
}

// Function without docs
const multiply = (x: number, y: number) => x * y`

  // Extract code elements on mount
  useEffect(() => {
    const elements = extractCodeElements(defaultCode)
    setCodeElements(elements)
  }, [defaultCode])

  // Sample documentation
  const defaultDoc = docContent || `# API Documentation

## Functions

### add(a, b)

Calculates the sum of two numbers.

**Parameters:**
- \`a\` (number): First number
- \`b\` (number): Second number

**Returns:**
- (number): The sum of a and b

**Example:**
\`\`\`typescript
const result = add(2, 3) // 5
\`\`\`

---

## Classes

### User

Represents a user in the system.

**Properties:**
- \`name\` (string): User's name
- \`age\` (number): User's age

**Constructor:**
\`\`\`typescript
constructor(name: string, age: number)
\`\`\`

**Parameters:**
- \`name\` (string): User's name
- \`age\` (number): User's age

---

## Notes

- All functions are type-safe with TypeScript
- Classes follow the standard object-oriented pattern`

  // Handle element selection for synchronized highlighting
  const handleCodeSelection = (element: string) => {
    setSelectedElement(element)
  }

  const handleDocSelection = (element: string) => {
    setSelectedElement(element)
  }

  const handleDocHover = (element: string | null) => {
    setHoveredDocElement(element)
  }

  // Check if an element should be highlighted
  const isHighlighted = (name: string) => {
    return selectedElement === name || hoveredDocElement === name
  }

  return (
    <div className="h-full flex flex-col bg-gray-900">
      {/* Header */}
      <div className="h-10 bg-gray-800 border-b border-gray-700 flex items-center px-4 gap-4">
        <div className="flex items-center gap-2 text-sm">
          <CodeIcon className="w-4 h-4 text-blue-400" />
          <span className="text-gray-300">{codeFile || 'code.ts'}</span>
        </div>
        <div className="h-4 w-px bg-gray-700" />
        <div className="flex items-center gap-2 text-sm">
          <BookOpen className="w-4 h-4 text-purple-400" />
          <span className="text-gray-300">{docFile || 'documentation.md'}</span>
        </div>
        {selectedElement && (
          <>
            <div className="h-4 w-px bg-gray-700" />
            <div className="text-xs text-purple-300 flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-purple-500 animate-pulse" />
              Linked: {selectedElement}
            </div>
          </>
        )}
      </div>

      {/* Split Panels */}
      <PanelGroup direction="horizontal" className="flex-1">
        {/* Code Panel */}
        <Panel defaultSize={50} minSize={30}>
          <div ref={codePanelRef} className="h-full bg-gray-950">
            <div className="h-8 bg-gray-900 border-b border-gray-800 px-4 flex items-center text-xs text-gray-400">
              CODE
              {codeElements.length > 0 && (
                <span className="ml-2 text-gray-500">
                  ({codeElements.length} elements)
                </span>
              )}
            </div>
            <div className="h-[calc(100%-2rem)] overflow-hidden">
              <LucidMonacoEditor
                value={defaultCode}
                language="typescript"
                fileName={codeFile || 'code.ts'}
                onChange={() => {}}
                theme="vs-dark"
                enableLucidFolds={true}
              />
            </div>
          </div>
        </Panel>

        {/* Resize Handle */}
        <PanelResizeHandle className="w-2 bg-gray-800 hover:bg-gray-700 transition-colors cursor-col-resize">
          <div className="w-full h-full flex items-center justify-center">
            <div className="h-12 w-0.5 bg-gray-600" />
          </div>
        </PanelResizeHandle>

        {/* Documentation Panel */}
        <Panel defaultSize={50} minSize={30}>
          <div ref={docPanelRef} className="h-full bg-gray-950 overflow-hidden">
            <div className="h-8 bg-gray-900 border-b border-gray-800 px-4 flex items-center text-xs text-gray-400">
              DOCUMENTATION
            </div>
            <div className="h-[calc(100%-2rem)] overflow-y-auto p-4">
              <div 
                className="prose prose-invert prose-sm max-w-none"
                dangerouslySetInnerHTML={{ __html: renderMarkdown(defaultDoc, handleDocSelection, handleDocHover, isHighlighted) }}
              />
            </div>
          </div>
        </Panel>
      </PanelGroup>
    </div>
  )
}

// Enhanced markdown renderer with synchronized highlighting
function renderMarkdown(
  content: string,
  onElementClick: (name: string) => void,
  onElementHover: (name: string | null) => void,
  isHighlighted: (name: string) => boolean
): string {
  let html = content
  
  // Headers with click/hover handlers
  html = html.replace(/^### (.*$)/gim, (match, text) => {
    const isHighlightedClass = isHighlighted(text) ? 'bg-purple-500/20 border-l-4 border-purple-500' : ''
    return `<h3 class="text-lg font-semibold text-white mt-6 mb-2 ${isHighlightedClass} px-3 py-2 rounded cursor-pointer transition-all hover:bg-purple-500/10" data-element="${text}">${text}</h3>`
  })
  
  html = html.replace(/^## (.*$)/gim, '<h2 class="text-xl font-bold text-white mt-8 mb-3 border-b border-gray-700 pb-2">$1</h2>')
  html = html.replace(/^# (.*$)/gim, '<h1 class="text-2xl font-bold text-white mb-4">$1</h1>')
  
  // Bold
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-white">$1</strong>')
  
  // Code blocks
  html = html.replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre class="bg-gray-800 p-3 rounded my-3 overflow-x-auto"><code class="text-green-400 text-sm">$2</code></pre>')
  
  // Inline code
  html = html.replace(/`([^`]+)`/g, '<code class="bg-gray-800 text-green-400 px-1.5 py-0.5 rounded text-sm">$1</code>')
  
  // Lists
  html = html.replace(/^\* (.*$)/gim, '<li class="ml-4 text-gray-300">$1</li>')
  html = html.replace(/^\- (.*$)/gim, '<li class="ml-4 text-gray-300">$1</li>')
  html = html.replace(/(<li.*<\/li>)/s, '<ul class="list-disc my-2 space-y-1">$1</ul>')
  
  // Paragraphs
  html = html.replace(/^(?!<[h|u|p|l|d|s])/gm, '<p class="text-gray-300 mb-3">')
  html = html.replace(/(?<!>)$/gm, '</p>')
  
  // Horizontal rule
  html = html.replace(/^---$/gm, '<hr class="border-gray-700 my-4">')
  
  return html
}
