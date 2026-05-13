import React, { useRef, useEffect, useState } from 'react'
import Editor from '@monaco-editor/react'
import { Code, FileText, Eye, GitBranch, Clock, Users, User } from 'lucide-react'
import { lucidCollaborationService, CollaborationUser } from '../services/LucidCollaborationService'

interface CollaborativeLucidMonacoEditorProps {
  value: string
  language?: string
  onChange?: (value: string | undefined) => void
  fileName?: string
  readOnly?: boolean
  theme?: string
  enableLucidFolds?: boolean
  enableCollaboration?: boolean
}

interface CodeSymbol {
  name: string
  kind: string
  range: { startLineNumber: number; endLineNumber: number }
  nodeId: string
}

export const CollaborativeLucidMonacoEditor: React.FC<CollaborativeLucidMonacoEditorProps> = ({
  value,
  language = 'typescript',
  onChange,
  fileName,
  readOnly = false,
  theme = 'vs-dark',
  enableLucidFolds = true,
  enableCollaboration = true
}) => {
  const editorRef = useRef<any>(null)
  const monacoRef = useRef<any>(null)
  const [symbols, setSymbols] = useState<CodeSymbol[]>([])
  const [activeFolds, setActiveFolds] = useState<Set<string>>(new Set())
  const [collaborationUsers, setCollaborationUsers] = useState<CollaborationUser[]>([])
  const [focusedNode, setFocusedNode] = useState<string | undefined>()
  const [showCollaborationPanel, setShowCollaborationPanel] = useState(false)

  useEffect(() => {
    if (enableCollaboration) {
      // Set up collaboration event listeners
      const handleUserJoined = (user: CollaborationUser) => {
        setCollaborationUsers(prev => [...prev.filter(u => u.id !== user.id), user])
      }

      const handleUserLeft = (userId: string) => {
        setCollaborationUsers(prev => prev.filter(u => u.id !== userId))
      }

      const handleNodeFocused = ({ nodeId }: { nodeId: string }) => {
        setFocusedNode(nodeId)
      }

      const handleFoldToggled = ({ nodeId, foldType, active }: { nodeId: string; foldType: string; active: boolean }) => {
        const foldId = `${nodeId}-${foldType}`
        setActiveFolds(prev => {
          const newSet = new Set(prev)
          if (active) {
            newSet.add(foldId)
          } else {
            newSet.delete(foldId)
          }
          return newSet
        })
      }

      lucidCollaborationService.on('user_joined', handleUserJoined)
      lucidCollaborationService.on('user_left', handleUserLeft)
      lucidCollaborationService.on('node_focused', handleNodeFocused)
      lucidCollaborationService.on('fold_toggled', handleFoldToggled)

      // Initialize users
      setCollaborationUsers(lucidCollaborationService.getUsers())

      return () => {
        lucidCollaborationService.off('user_joined', handleUserJoined)
        lucidCollaborationService.off('user_left', handleUserLeft)
        lucidCollaborationService.off('node_focused', handleNodeFocused)
        lucidCollaborationService.off('fold_toggled', handleFoldToggled)
      }
    }
  }, [enableCollaboration])

  const handleEditorDidMount = (editor: any, monaco: any) => {
    editorRef.current = editor
    monacoRef.current = monaco

    // Configure editor options
    editor.updateOptions({
      minimap: { enabled: true },
      fontSize: 14,
      lineNumbers: 'on',
      roundedSelection: false,
      scrollBeyondLastLine: false,
      readOnly,
      wordWrap: 'on',
      automaticLayout: true,
      glyphMargin: true,
    })

    // Add keyboard shortcuts
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
      console.log('Save triggered')
    })

    // Configure TypeScript/JavaScript language
    if (language === 'typescript' || language === 'javascript') {
      monaco.languages.typescript.typescriptDefaults.setCompilerOptions({
        target: monaco.languages.typescript.ScriptTarget.ES2020,
        allowNonTsExtensions: true,
        moduleResolution: monaco.languages.typescript.ModuleResolutionKind.NodeJs,
        module: monaco.languages.typescript.ModuleKind.CommonJS,
        noEmit: true,
        esModuleInterop: true,
        jsx: monaco.languages.typescript.JsxEmit.React,
        reactNamespace: 'React',
        allowJs: true,
        typeRoots: ['node_modules/@types']
      })
    }

    // Extract symbols when content changes
    if (enableLucidFolds) {
      extractSymbols(editor, monaco)
    }

    // Set up collaboration cursor tracking
    if (enableCollaboration) {
      editor.onDidChangeCursorPosition((e: any) => {
        lucidCollaborationService.updateUserCursor(
          lucidCollaborationService['userId'],
          { line: e.position.lineNumber, column: e.position.column }
        )
      })

      editor.onDidChangeCursorSelection((e: any) => {
        const selection = e.selection
        lucidCollaborationService.updateUserSelection(
          lucidCollaborationService['userId'],
          {
            startLine: selection.startLineNumber,
            endLine: selection.endLineNumber,
            startColumn: selection.startColumn,
            endColumn: selection.endColumn
          }
        )
      })
    }
  }

  const extractSymbols = (editor: any, monaco: any) => {
    const model = editor.getModel()
    if (!model) return

    const text = model.getValue()
    const lines = text.split('\n')
    const newSymbols: CodeSymbol[] = []

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i]
      const trimmedLine = line.trim()

      // Detect function declarations
      const functionMatch = trimmedLine.match(/^(export\s+)?(async\s+)?function\s+(\w+)/)
      if (functionMatch) {
        const name = functionMatch[3]
        const nodeId = generateNodeId(fileName || 'unknown', name, 'function')
        newSymbols.push({
          name,
          kind: 'function',
          range: { startLineNumber: i + 1, endLineNumber: i + 1 },
          nodeId
        })
      }

      // Detect arrow functions
      const arrowFunctionMatch = trimmedLine.match(/^(export\s+)?const\s+(\w+)\s*=\s*(async\s+)?\(/)
      if (arrowFunctionMatch) {
        const name = arrowFunctionMatch[2]
        const nodeId = generateNodeId(fileName || 'unknown', name, 'function')
        newSymbols.push({
          name,
          kind: 'function',
          range: { startLineNumber: i + 1, endLineNumber: i + 1 },
          nodeId
        })
      }

      // Detect React components
      const componentMatch = trimmedLine.match(/^(export\s+)?(const|function)\s+(\w+)\s*[=\(]/)
      if (componentMatch && isReactComponent(componentMatch[3])) {
        const name = componentMatch[3]
        const nodeId = generateNodeId(fileName || 'unknown', name, 'reactComponent')
        newSymbols.push({
          name,
          kind: 'reactComponent',
          range: { startLineNumber: i + 1, endLineNumber: i + 1 },
          nodeId
        })
      }

      // Detect class declarations
      const classMatch = trimmedLine.match(/^(export\s+)?class\s+(\w+)/)
      if (classMatch) {
        const name = classMatch[2]
        const nodeId = generateNodeId(fileName || 'unknown', name, 'class')
        newSymbols.push({
          name,
          kind: 'class',
          range: { startLineNumber: i + 1, endLineNumber: i + 1 },
          nodeId
        })
      }
    }

    setSymbols(newSymbols)
  }

  const generateNodeId = (fileName: string, name: string, kind: string): string => {
    const module = fileName.split('/').pop()?.replace(/\.(ts|tsx|js|jsx)$/, '') || 'unknown'
    return `${module}:${name}`
  }

  const isReactComponent = (name: string): boolean => {
    return /^[A-Z][a-zA-Z0-9]*$/.test(name)
  }

  const handleGutterClick = (symbol: CodeSymbol, foldType: 'spec' | 'blueprint' | 'timeline') => {
    const foldId = `${symbol.nodeId}-${foldType}`
    
    if (activeFolds.has(foldId)) {
      // Remove fold
      setActiveFolds(prev => {
        const newSet = new Set(prev)
        newSet.delete(foldId)
        return newSet
      })
    } else {
      // Add fold
      setActiveFolds(prev => new Set(prev).add(foldId))
    }

    // Notify collaboration service
    if (enableCollaboration) {
      lucidCollaborationService.toggleFold(symbol.nodeId, foldType)
      lucidCollaborationService.focusNode(symbol.nodeId)
    }
  }

  const renderGutterIcons = () => {
    if (!enableLucidFolds || !editorRef.current) return null

    return symbols.map((symbol, index) => (
      <div key={index} className="absolute left-0 z-10" style={{ top: `${(symbol.range.startLineNumber - 1) * 20}px` }}>
        <div className="flex gap-1 bg-gray-800 rounded px-1 py-0.5 text-xs">
          <button
            onClick={() => handleGutterClick(symbol, 'spec')}
            className={`px-1 py-0.5 rounded text-white transition-colors ${
              focusedNode === symbol.nodeId ? 'bg-blue-500' : 'bg-blue-600 hover:bg-blue-500'
            }`}
            title="Show Spec"
          >
            SPEC
          </button>
          <button
            onClick={() => handleGutterClick(symbol, 'blueprint')}
            className={`px-1 py-0.5 rounded text-white transition-colors ${
              focusedNode === symbol.nodeId ? 'bg-green-500' : 'bg-green-600 hover:bg-green-500'
            }`}
            title="Show Blueprint"
          >
            BLUEPRINT
          </button>
          <button
            onClick={() => handleGutterClick(symbol, 'timeline')}
            className={`px-1 py-0.5 rounded text-white transition-colors ${
              focusedNode === symbol.nodeId ? 'bg-orange-500' : 'bg-orange-600 hover:bg-orange-500'
            }`}
            title="Show Timeline"
          >
            TIMELINE
          </button>
        </div>
      </div>
    ))
  }

  const renderCollaborationIndicators = () => {
    if (!enableCollaboration || collaborationUsers.length <= 1) return null

    return (
      <div className="absolute top-2 right-2 z-20">
        <div className="flex items-center gap-2 bg-gray-800 rounded px-2 py-1 text-xs">
          <Users className="w-3 h-3 text-blue-400" />
          <span className="text-gray-300">{collaborationUsers.length} users</span>
          <button
            onClick={() => setShowCollaborationPanel(!showCollaborationPanel)}
            className="text-blue-400 hover:text-blue-300"
          >
            View
          </button>
        </div>
      </div>
    )
  }

  const renderCollaborationPanel = () => {
    if (!showCollaborationPanel || !enableCollaboration) return null

    return (
      <div className="absolute top-12 right-2 z-30 w-64 bg-gray-800 rounded border border-gray-700 p-3">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-semibold text-white">Collaboration</h3>
          <button
            onClick={() => setShowCollaborationPanel(false)}
            className="text-gray-400 hover:text-white"
          >
            ×
          </button>
        </div>
        
        <div className="space-y-2">
          {collaborationUsers.map((user) => (
            <div key={user.id} className="flex items-center gap-2">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: user.color }}
              />
              <span className="text-sm text-gray-300">{user.name}</span>
              {user.cursor && (
                <span className="text-xs text-gray-400">
                  L{user.cursor.line}:C{user.cursor.column}
                </span>
              )}
            </div>
          ))}
        </div>

        {focusedNode && (
          <div className="mt-3 pt-2 border-t border-gray-700">
            <div className="text-xs text-gray-400">
              Focused: <span className="text-blue-400">{focusedNode}</span>
            </div>
          </div>
        )}
      </div>
    )
  }

  const renderInlineFolds = () => {
    if (!enableLucidFolds) return null

    return symbols.map((symbol, index) => {
      const specFoldId = `${symbol.nodeId}-spec`
      const blueprintFoldId = `${symbol.nodeId}-blueprint`
      const timelineFoldId = `${symbol.nodeId}-timeline`

      return (
        <div key={index}>
          {/* SPEC Fold */}
          {activeFolds.has(specFoldId) && (
            <div className="bg-blue-900/20 border-l-4 border-blue-500 p-4 m-2 rounded">
              <div className="flex items-center gap-2 mb-2">
                <Eye className="w-4 h-4 text-blue-400" />
                <span className="font-semibold text-blue-300">SPEC: {symbol.name}</span>
                {focusedNode === symbol.nodeId && (
                  <span className="text-xs bg-blue-600 text-white px-2 py-0.5 rounded">
                    FOCUSED
                  </span>
                )}
              </div>
              <div className="text-sm text-gray-300 space-y-2">
                <div>
                  <strong>Responsibility:</strong> Mock responsibility for {symbol.name}
                </div>
                <div>
                  <strong>Must Never:</strong>
                  <ul className="list-disc list-inside ml-4 text-red-300">
                    <li>Mock constraint 1</li>
                    <li>Mock constraint 2</li>
                  </ul>
                </div>
                <div>
                  <strong>Security Level:</strong> <span className="text-yellow-400">HIGH</span>
                </div>
                <div>
                  <strong>Status:</strong> <span className="text-green-400">CLEAN</span>
                </div>
                <button className="mt-2 px-3 py-1 bg-blue-600 hover:bg-blue-500 rounded text-white text-xs">
                  Propose Change
                </button>
              </div>
            </div>
          )}

          {/* BLUEPRINT Fold */}
          {activeFolds.has(blueprintFoldId) && (
            <div className="bg-green-900/20 border-l-4 border-green-500 p-4 m-2 rounded">
              <div className="flex items-center gap-2 mb-2">
                <GitBranch className="w-4 h-4 text-green-400" />
                <span className="font-semibold text-green-300">BLUEPRINT: {symbol.name}</span>
                {focusedNode === symbol.nodeId && (
                  <span className="text-xs bg-green-600 text-white px-2 py-0.5 rounded">
                    FOCUSED
                  </span>
                )}
              </div>
              <div className="text-sm text-gray-300 space-y-2">
                <div>
                  <strong>Center Node:</strong> {symbol.name} ({symbol.kind})
                </div>
                <div>
                  <strong>Incoming Dependencies:</strong> 2 nodes
                </div>
                <div>
                  <strong>Outgoing Dependencies:</strong> 3 nodes
                </div>
                <div>
                  <strong>Blast Radius:</strong> Direct: 2, Indirect: 5
                </div>
                <div className="text-xs text-gray-400">
                  Click on node names to navigate
                </div>
              </div>
            </div>
          )}

          {/* TIMELINE Fold */}
          {activeFolds.has(timelineFoldId) && (
            <div className="bg-orange-900/20 border-l-4 border-orange-500 p-4 m-2 rounded">
              <div className="flex items-center gap-2 mb-2">
                <Clock className="w-4 h-4 text-orange-400" />
                <span className="font-semibold text-orange-300">TIMELINE: {symbol.name}</span>
                {focusedNode === symbol.nodeId && (
                  <span className="text-xs bg-orange-600 text-white px-2 py-0.5 rounded">
                    FOCUSED
                  </span>
                )}
              </div>
              <div className="text-sm text-gray-300 space-y-2">
                <div>
                  <strong>Recent Executions:</strong> 5 runs
                </div>
                <div>
                  <strong>Average Duration:</strong> 12ms
                </div>
                <div>
                  <strong>Performance Status:</strong> <span className="text-green-400">NORMAL</span>
                </div>
                <div>
                  <strong>Violations:</strong> 0
                </div>
                <div className="text-xs text-gray-400">
                  Last run: 2 minutes ago
                </div>
              </div>
            </div>
          )}
        </div>
      )
    })
  }

  // Determine language from file name if not provided
  const detectedLanguage = language || (() => {
    if (!fileName) return 'typescript'
    const ext = fileName.split('.').pop()?.toLowerCase()
    const languageMap: Record<string, string> = {
      'ts': 'typescript',
      'tsx': 'typescript',
      'js': 'javascript',
      'jsx': 'javascript',
      'py': 'python',
      'json': 'json',
      'css': 'css',
      'html': 'html',
      'md': 'markdown',
      'yaml': 'yaml',
      'yml': 'yaml',
      'xml': 'xml',
      'sql': 'sql',
      'sh': 'shell',
      'bash': 'shell',
      'go': 'go',
      'rs': 'rust',
      'java': 'java',
      'cpp': 'cpp',
      'c': 'c',
    }
    return languageMap[ext || ''] || 'typescript'
  })()

  return (
    <div className="flex flex-col h-full relative">
      {/* Header */}
      <div className="flex items-center gap-2 px-4 py-2 bg-gray-800 border-b border-gray-700">
        {fileName ? (
          <>
            <FileText className="w-4 h-4 text-blue-400" />
            <span className="text-sm font-medium text-gray-200">{fileName}</span>
            {enableLucidFolds && (
              <span className="ml-auto text-xs text-gray-400">
                Lucid Folds: {symbols.length} symbols
              </span>
            )}
          </>
        ) : (
          <>
            <Code className="w-4 h-4 text-blue-400" />
            <span className="text-sm font-medium text-gray-200">Editor</span>
          </>
        )}
      </div>

      {/* Editor Container */}
      <div className="flex-1 relative">
        <Editor
          height="100%"
          language={detectedLanguage}
          value={value}
          onChange={onChange}
          onMount={handleEditorDidMount}
          theme={theme}
          options={{
            minimap: { enabled: true },
            fontSize: 14,
            lineNumbers: 'on',
            roundedSelection: false,
            scrollBeyondLastLine: false,
            readOnly,
            wordWrap: 'on',
            automaticLayout: true,
            glyphMargin: true,
          }}
        />
        
        {/* Gutter Icons Overlay */}
        {enableLucidFolds && (
          <div className="absolute left-0 top-0 w-32 pointer-events-none">
            {renderGutterIcons()}
          </div>
        )}

        {/* Collaboration Indicators */}
        {renderCollaborationIndicators()}
        {renderCollaborationPanel()}
      </div>

      {/* Inline Folds */}
      {enableLucidFolds && (
        <div className="max-h-64 overflow-y-auto">
          {renderInlineFolds()}
        </div>
      )}
    </div>
  )
}
