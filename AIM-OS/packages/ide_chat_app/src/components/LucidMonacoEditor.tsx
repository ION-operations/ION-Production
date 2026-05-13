import React, { useRef, useEffect, useState } from 'react'
import Editor from '@monaco-editor/react'
import { Code, FileText, Eye, GitBranch, Clock } from 'lucide-react'
import { httpLucidDaemonService, SpecBlock, BlueprintSlice, TimelineSummary } from '../services/HttpLucidDaemonService'

interface LucidMonacoEditorProps {
  value: string
  language?: string
  onChange?: (value: string | undefined) => void
  fileName?: string
  readOnly?: boolean
  theme?: string
  enableLucidFolds?: boolean
}

interface CodeSymbol {
  name: string
  kind: string
  range: { startLineNumber: number; endLineNumber: number }
  nodeId: string
}

export const LucidMonacoEditor: React.FC<LucidMonacoEditorProps> = ({
  value,
  language = 'typescript',
  onChange,
  fileName,
  readOnly = false,
  theme = 'vs-dark',
  enableLucidFolds = true
}) => {
  const editorRef = useRef<any>(null)
  const monacoRef = useRef<any>(null)
  const [symbols, setSymbols] = useState<CodeSymbol[]>([])
  const [activeFolds, setActiveFolds] = useState<Set<string>>(new Set())
  const [specData, setSpecData] = useState<Map<string, SpecBlock>>(new Map())
  const [blueprintData, setBlueprintData] = useState<Map<string, BlueprintSlice>>(new Map())
  const [timelineData, setTimelineData] = useState<Map<string, TimelineSummary>>(new Map())
  const [loading, setLoading] = useState<Set<string>>(new Set())

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
      glyphMargin: true, // Enable glyph margin for gutter icons
    })

    // Add keyboard shortcuts
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
      console.log('Save triggered')
      // Handle save
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

  const loadSpecData = async (nodeId: string) => {
    if (specData.has(nodeId) || loading.has(nodeId)) return
    
    setLoading(prev => new Set(prev).add(nodeId))
    try {
      const data = await httpLucidDaemonService.getSpecBlock(nodeId)
      setSpecData(prev => new Map(prev).set(nodeId, data))
    } catch (error) {
      console.error('Failed to load spec data:', error)
    } finally {
      setLoading(prev => {
        const newSet = new Set(prev)
        newSet.delete(nodeId)
        return newSet
      })
    }
  }

  const loadBlueprintData = async (nodeId: string) => {
    if (blueprintData.has(nodeId) || loading.has(nodeId)) return
    
    setLoading(prev => new Set(prev).add(nodeId))
    try {
      const data = await httpLucidDaemonService.getBlueprintSlice(nodeId)
      setBlueprintData(prev => new Map(prev).set(nodeId, data))
    } catch (error) {
      console.error('Failed to load blueprint data:', error)
    } finally {
      setLoading(prev => {
        const newSet = new Set(prev)
        newSet.delete(nodeId)
        return newSet
      })
    }
  }

  const loadTimelineData = async (nodeId: string) => {
    if (timelineData.has(nodeId) || loading.has(nodeId)) return
    
    setLoading(prev => new Set(prev).add(nodeId))
    try {
      const data = await httpLucidDaemonService.getTimelineSummary(nodeId)
      setTimelineData(prev => new Map(prev).set(nodeId, data))
    } catch (error) {
      console.error('Failed to load timeline data:', error)
    } finally {
      setLoading(prev => {
        const newSet = new Set(prev)
        newSet.delete(nodeId)
        return newSet
      })
    }
  }

  const isReactComponent = (name: string): boolean => {
    return /^[A-Z][a-zA-Z0-9]*$/.test(name)
  }

  const handleGutterClick = async (symbol: CodeSymbol, foldType: 'spec' | 'blueprint' | 'timeline') => {
    const foldId = `${symbol.nodeId}-${foldType}`
    
    if (activeFolds.has(foldId)) {
      // Remove fold
      setActiveFolds(prev => {
        const newSet = new Set(prev)
        newSet.delete(foldId)
        return newSet
      })
    } else {
      // Add fold and load data
      setActiveFolds(prev => new Set(prev).add(foldId))
      
      // Load the appropriate data
      switch (foldType) {
        case 'spec':
          await loadSpecData(symbol.nodeId)
          break
        case 'blueprint':
          await loadBlueprintData(symbol.nodeId)
          break
        case 'timeline':
          await loadTimelineData(symbol.nodeId)
          break
      }
    }
  }

  const renderGutterIcons = () => {
    if (!enableLucidFolds || !editorRef.current) return null

    return symbols.map((symbol, index) => (
      <div key={index} className="absolute left-0 z-10" style={{ top: `${(symbol.range.startLineNumber - 1) * 20}px` }}>
        <div className="flex gap-1 bg-gray-800 rounded px-1 py-0.5 text-xs">
          <button
            onClick={() => handleGutterClick(symbol, 'spec')}
            className="px-1 py-0.5 bg-blue-600 hover:bg-blue-500 rounded text-white"
            title="Show Spec"
          >
            SPEC
          </button>
          <button
            onClick={() => handleGutterClick(symbol, 'blueprint')}
            className="px-1 py-0.5 bg-green-600 hover:bg-green-500 rounded text-white"
            title="Show Blueprint"
          >
            BLUEPRINT
          </button>
          <button
            onClick={() => handleGutterClick(symbol, 'timeline')}
            className="px-1 py-0.5 bg-orange-600 hover:bg-orange-500 rounded text-white"
            title="Show Timeline"
          >
            TIMELINE
          </button>
        </div>
      </div>
    ))
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
                {loading.has(symbol.nodeId) && (
                  <div className="animate-spin w-4 h-4 border-2 border-blue-400 border-t-transparent rounded-full" />
                )}
              </div>
              {specData.has(symbol.nodeId) ? (
                <div className="text-sm text-gray-300 space-y-2">
                  <div>
                    <strong>Responsibility:</strong> {specData.get(symbol.nodeId)?.responsibility || 'No description'}
                  </div>
                  <div>
                    <strong>Must Never:</strong>
                    <ul className="list-disc list-inside ml-4 text-red-300">
                      {(specData.get(symbol.nodeId)?.must_never || []).map((constraint, idx) => (
                        <li key={idx}>{constraint}</li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <strong>Security Level:</strong> 
                    <span className={`ml-1 ${
                      specData.get(symbol.nodeId)?.security_level === 'critical' ? 'text-red-400' :
                      specData.get(symbol.nodeId)?.security_level === 'high' ? 'text-orange-400' :
                      specData.get(symbol.nodeId)?.security_level === 'medium' ? 'text-yellow-400' :
                      'text-green-400'
                    }`}>
                      {specData.get(symbol.nodeId)?.security_level || 'low'}
                    </span>
                  </div>
                  <div>
                    <strong>Performance Budget:</strong> {specData.get(symbol.nodeId)?.perf_budget_ms || 'N/A'}ms
                  </div>
                  <div>
                    <strong>Status:</strong> 
                    <span className={`ml-1 ${
                      specData.get(symbol.nodeId)?.status === 'clean' ? 'text-green-400' :
                      specData.get(symbol.nodeId)?.status === 'drift' ? 'text-yellow-400' :
                      specData.get(symbol.nodeId)?.status === 'violation' ? 'text-red-400' :
                      'text-gray-400'
                    }`}>
                      {specData.get(symbol.nodeId)?.status || 'unknown'}
                    </span>
                  </div>
                  {specData.get(symbol.nodeId)?.drift_reason && (
                    <div className="text-yellow-300">
                      <strong>Drift Reason:</strong> {specData.get(symbol.nodeId)?.drift_reason}
                    </div>
                  )}
                  <button className="mt-2 px-3 py-1 bg-blue-600 hover:bg-blue-500 rounded text-white text-xs">
                    Propose Change
                  </button>
                </div>
              ) : (
                <div className="text-sm text-gray-400">
                  {loading.has(symbol.nodeId) ? 'Loading spec data...' : 'No spec data available'}
                </div>
              )}
            </div>
          )}

          {/* BLUEPRINT Fold */}
          {activeFolds.has(blueprintFoldId) && (
            <div className="bg-green-900/20 border-l-4 border-green-500 p-4 m-2 rounded">
              <div className="flex items-center gap-2 mb-2">
                <GitBranch className="w-4 h-4 text-green-400" />
                <span className="font-semibold text-green-300">BLUEPRINT: {symbol.name}</span>
                {loading.has(symbol.nodeId) && (
                  <div className="animate-spin w-4 h-4 border-2 border-green-400 border-t-transparent rounded-full" />
                )}
              </div>
              {blueprintData.has(symbol.nodeId) ? (
                <div className="text-sm text-gray-300 space-y-2">
                  <div>
                    <strong>Center Node:</strong> {blueprintData.get(symbol.nodeId)?.center?.name || symbol.name} ({blueprintData.get(symbol.nodeId)?.center?.kind || symbol.kind})
                  </div>
                  <div>
                    <strong>Incoming Dependencies:</strong> {blueprintData.get(symbol.nodeId)?.incoming?.length || 0} nodes
                    {blueprintData.get(symbol.nodeId)?.incoming && blueprintData.get(symbol.nodeId)!.incoming.length > 0 && (
                      <ul className="list-disc list-inside ml-4 text-xs">
                        {blueprintData.get(symbol.nodeId)!.incoming.slice(0, 3).map((dep, idx) => (
                          <li key={idx} className="text-blue-300 hover:text-blue-200 cursor-pointer">
                            {dep.name} ({dep.edgeType})
                          </li>
                        ))}
                        {blueprintData.get(symbol.nodeId)!.incoming.length > 3 && (
                          <li className="text-gray-400">... and {blueprintData.get(symbol.nodeId)!.incoming.length - 3} more</li>
                        )}
                      </ul>
                    )}
                  </div>
                  <div>
                    <strong>Outgoing Dependencies:</strong> {blueprintData.get(symbol.nodeId)?.outgoing?.length || 0} nodes
                    {blueprintData.get(symbol.nodeId)?.outgoing && blueprintData.get(symbol.nodeId)!.outgoing.length > 0 && (
                      <ul className="list-disc list-inside ml-4 text-xs">
                        {blueprintData.get(symbol.nodeId)!.outgoing.slice(0, 3).map((dep, idx) => (
                          <li key={idx} className="text-green-300 hover:text-green-200 cursor-pointer">
                            {dep.name} ({dep.edgeType})
                          </li>
                        ))}
                        {blueprintData.get(symbol.nodeId)!.outgoing.length > 3 && (
                          <li className="text-gray-400">... and {blueprintData.get(symbol.nodeId)!.outgoing.length - 3} more</li>
                        )}
                      </ul>
                    )}
                  </div>
                  <div>
                    <strong>Blast Radius:</strong> Direct: {blueprintData.get(symbol.nodeId)?.blastRadius?.direct || 0}, Indirect: {blueprintData.get(symbol.nodeId)?.blastRadius?.indirect || 0}
                  </div>
                  <div>
                    <strong>Risk Score:</strong> 
                    <span className={`ml-1 ${
                      (blueprintData.get(symbol.nodeId)?.blastRadius?.riskScore || 0) > 0.8 ? 'text-red-400' :
                      (blueprintData.get(symbol.nodeId)?.blastRadius?.riskScore || 0) > 0.5 ? 'text-yellow-400' :
                      'text-green-400'
                    }`}>
                      {((blueprintData.get(symbol.nodeId)?.blastRadius?.riskScore || 0) * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="text-xs text-gray-400">
                    Click on node names to navigate
                  </div>
                </div>
              ) : (
                <div className="text-sm text-gray-400">
                  {loading.has(symbol.nodeId) ? 'Loading blueprint data...' : 'No blueprint data available'}
                </div>
              )}
            </div>
          )}

          {/* TIMELINE Fold */}
          {activeFolds.has(timelineFoldId) && (
            <div className="bg-orange-900/20 border-l-4 border-orange-500 p-4 m-2 rounded">
              <div className="flex items-center gap-2 mb-2">
                <Clock className="w-4 h-4 text-orange-400" />
                <span className="font-semibold text-orange-300">TIMELINE: {symbol.name}</span>
                {loading.has(symbol.nodeId) && (
                  <div className="animate-spin w-4 h-4 border-2 border-orange-400 border-t-transparent rounded-full" />
                )}
              </div>
              {timelineData.has(symbol.nodeId) ? (
                <div className="text-sm text-gray-300 space-y-2">
                  <div>
                    <strong>Recent Executions:</strong> {timelineData.get(symbol.nodeId)?.recentRuns?.length || 0} runs
                    {timelineData.get(symbol.nodeId)?.recentRuns && timelineData.get(symbol.nodeId)!.recentRuns.length > 0 && (
                      <ul className="list-disc list-inside ml-4 text-xs">
                        {timelineData.get(symbol.nodeId)!.recentRuns.slice(0, 3).map((run, idx) => (
                          <li key={idx} className={`${
                            run.status === 'slow' ? 'text-yellow-300' :
                            run.status === 'ok' ? 'text-green-300' :
                            'text-red-300'
                          }`}>
                            {new Date(run.timestamp).toLocaleTimeString()} - {run.durationMs}ms ({run.status})
                            {run.violations && run.violations.length > 0 && (
                              <span className="text-red-400 ml-1">⚠️ {run.violations.join(', ')}</span>
                            )}
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                  <div>
                    <strong>Average Duration:</strong> {
                      timelineData.get(symbol.nodeId)?.recentRuns && timelineData.get(symbol.nodeId)!.recentRuns.length > 0
                        ? (timelineData.get(symbol.nodeId)!.recentRuns.reduce((sum, run) => sum + run.durationMs, 0) / timelineData.get(symbol.nodeId)!.recentRuns.length).toFixed(1)
                        : 'N/A'
                    }ms
                  </div>
                  <div>
                    <strong>Performance Status:</strong> 
                    <span className={`ml-1 ${
                      timelineData.get(symbol.nodeId)?.recentRuns?.some(run => run.status === 'slow') ? 'text-yellow-400' :
                      timelineData.get(symbol.nodeId)?.recentRuns?.some(run => run.violations && run.violations.length > 0) ? 'text-red-400' :
                      'text-green-400'
                    }`}>
                      {timelineData.get(symbol.nodeId)?.recentRuns?.some(run => run.status === 'slow') ? 'SLOW' :
                       timelineData.get(symbol.nodeId)?.recentRuns?.some(run => run.violations && run.violations.length > 0) ? 'VIOLATIONS' :
                       'NORMAL'}
                    </span>
                  </div>
                  <div>
                    <strong>Violations:</strong> {
                      timelineData.get(symbol.nodeId)?.recentRuns?.reduce((sum, run) => sum + (run.violations?.length || 0), 0) || 0
                    }
                  </div>
                  {timelineData.get(symbol.nodeId)?.worstRunCascade && timelineData.get(symbol.nodeId)!.worstRunCascade.length > 0 && (
                    <div>
                      <strong>Worst Run Cascade:</strong>
                      <div className="text-xs text-gray-400 ml-2">
                        {timelineData.get(symbol.nodeId)!.worstRunCascade.map((step, idx) => (
                          <div key={idx} className="flex items-center gap-1">
                            <span>{step.symbol}</span>
                            <span className="text-gray-500">→</span>
                            <span className="text-orange-300">{step.action}</span>
                            <span className="text-gray-500">({step.durationMs}ms)</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  <div className="text-xs text-gray-400">
                    Last run: {timelineData.get(symbol.nodeId)?.recentRuns && timelineData.get(symbol.nodeId)!.recentRuns.length > 0
                      ? new Date(timelineData.get(symbol.nodeId)!.recentRuns[0].timestamp).toLocaleString()
                      : 'Never'}
                  </div>
                </div>
              ) : (
                <div className="text-sm text-gray-400">
                  {loading.has(symbol.nodeId) ? 'Loading timeline data...' : 'No timeline data available'}
                </div>
              )}
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
