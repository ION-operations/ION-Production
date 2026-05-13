import React, { useState, useEffect, useMemo } from 'react'
import Editor, { DiffEditor } from '@monaco-editor/react'
import { FileText, GitBranch, Clock, X, ChevronDown, ChevronUp, FilePlus, FileMinus, FileEdit } from 'lucide-react'
import { getServiceBridge } from '@/services/serviceBridge'

interface FileChange {
  id: string
  file_path: string
  operation: 'created' | 'modified' | 'deleted'
  timestamp: string
  agent: string
  message_id?: string
  old_content?: string
  new_content?: string
  diff?: string
}

interface FileChangesViewerProps {
  onClose?: () => void
}

export const FileChangesViewer: React.FC<FileChangesViewerProps> = ({ onClose }) => {
  const [fileChanges, setFileChanges] = useState<FileChange[]>([])
  const [selectedFile, setSelectedFile] = useState<FileChange | null>(null)
  const [loading, setLoading] = useState(false)
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set())

  // Fetch file changes from MCP messages
  const fetchFileChanges = async () => {
    try {
      setLoading(true)
      const serviceBridge = getServiceBridge()
      
      // Get all messages
      const messages = await serviceBridge.getAIMessages(undefined, undefined)
      
      // Filter messages with file change tags
      const changes: FileChange[] = []
      messages.forEach((msg: any) => {
        // Check if message has file_change tags
        const tags = (msg as any).tags || {}
        const content = msg.content || ''
        
        // Check for file_change tag or file change pattern in content
        if (tags.type === 'file_change' || tags.file_change || 
            content.includes('file_change') || 
            content.match(/modified|created|deleted.*file/i)) {
          
          // Extract file path from tags or content
          const filePath = tags.file_path || 
                          content.match(/file[:\s]+([^\s]+)/i)?.[1] ||
                          content.match(/`([^`]+\.(ts|tsx|js|jsx|py|md|json|yaml|yml))`/)?.[1] ||
                          'unknown'
          
          // Determine operation
          let operation: 'created' | 'modified' | 'deleted' = 'modified'
          if (tags.operation) {
            operation = tags.operation as 'created' | 'modified' | 'deleted'
          } else if (content.includes('created') || content.includes('Created')) {
            operation = 'created'
          } else if (content.includes('deleted') || content.includes('Deleted')) {
            operation = 'deleted'
          }
          
          changes.push({
            id: msg.id || `change_${Date.now()}_${Math.random()}`,
            file_path: filePath,
            operation: operation,
            timestamp: msg.timestamp || new Date().toISOString(),
            agent: msg.from_ai || 'unknown',
            message_id: msg.id,
            old_content: tags.old_content,
            new_content: tags.new_content,
            diff: tags.diff
          })
        }
      })
      
      // Sort by timestamp (newest first)
      changes.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
      
      setFileChanges(changes.slice(0, 100)) // Keep last 100 changes
    } catch (error) {
      console.error('Failed to fetch file changes:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchFileChanges()
    // Poll every 5 seconds for new changes
    const interval = setInterval(fetchFileChanges, 5000)
    return () => clearInterval(interval)
  }, [])

  // Group changes by file
  const groupedChanges = useMemo(() => {
    const groups: { [key: string]: FileChange[] } = {}
    fileChanges.forEach(change => {
      if (!groups[change.file_path]) {
        groups[change.file_path] = []
      }
      groups[change.file_path].push(change)
    })
    return groups
  }, [fileChanges])

  const toggleGroup = (filePath: string) => {
    const newExpanded = new Set(expandedItems)
    if (newExpanded.has(filePath)) {
      newExpanded.delete(filePath)
    } else {
      newExpanded.add(filePath)
    }
    setExpandedItems(newExpanded)
  }

  const getOperationIcon = (operation: string) => {
    switch (operation) {
      case 'created': return <FilePlus className="w-4 h-4 text-green-400" />
      case 'deleted': return <FileMinus className="w-4 h-4 text-red-400" />
      case 'modified': return <FileEdit className="w-4 h-4 text-blue-400" />
      default: return <FileText className="w-4 h-4 text-gray-400" />
    }
  }

  const getOperationColor = (operation: string) => {
    switch (operation) {
      case 'created': return 'bg-green-900/20 text-green-400 border-green-700/50'
      case 'deleted': return 'bg-red-900/20 text-red-400 border-red-700/50'
      case 'modified': return 'bg-blue-900/20 text-blue-400 border-blue-700/50'
      default: return 'bg-gray-800/20 text-gray-400 border-gray-700/50'
    }
  }

  // Get file content for diff view
  const getFileContent = async (filePath: string) => {
    try {
      // Try to read file via Electron IPC or HTTP
      const win = window as any
      if (win.aimosAPI) {
        // Use AIM-OS API if available
        const response = await win.aimosAPI.get(`/api/file/read?path=${encodeURIComponent(filePath)}`)
        return response.data?.content || ''
      }
      return ''
    } catch (error) {
      console.error('Failed to read file:', error)
      return ''
    }
  }

  return (
    <div className="h-full flex flex-col bg-gray-900 text-white">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-800">
        <div className="flex items-center gap-4">
          <GitBranch className="w-6 h-6 text-blue-400" />
          <h2 className="text-xl font-semibold">Recent File Changes</h2>
          <div className="text-sm text-gray-400">
            {fileChanges.length} change{fileChanges.length !== 1 ? 's' : ''}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={fetchFileChanges}
            disabled={loading}
            className="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm disabled:opacity-50"
          >
            Refresh
          </button>
          {onClose && (
            <button
              onClick={onClose}
              className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-sm"
            >
              Close
            </button>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* File List */}
        <div className="w-1/3 border-r border-gray-800 overflow-y-auto">
          {loading && fileChanges.length === 0 ? (
            <div className="p-4 text-center text-gray-400">Loading changes...</div>
          ) : fileChanges.length === 0 ? (
            <div className="p-4 text-center text-gray-400">
              <p>No file changes detected</p>
              <p className="text-xs mt-2 text-gray-500">
                Agents will notify of changes via MCP messages with file_change tags
              </p>
            </div>
          ) : (
            <div className="p-2 space-y-1">
              {Object.entries(groupedChanges).map(([filePath, changes]) => {
                const isExpanded = expandedItems.has(filePath)
                const latestChange = changes[0]
                
                return (
                  <div key={filePath} className="border border-gray-700/50 rounded-lg overflow-hidden">
                    <button
                      onClick={() => toggleGroup(filePath)}
                      className="w-full p-3 bg-gray-800/50 hover:bg-gray-800 flex items-center gap-2 text-left"
                    >
                      {isExpanded ? (
                        <ChevronDown className="w-4 h-4 text-gray-400" />
                      ) : (
                        <ChevronUp className="w-4 h-4 text-gray-400" />
                      )}
                      <FileText className="w-4 h-4 text-blue-400 flex-shrink-0" />
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium truncate">{filePath.split('/').pop()}</div>
                        <div className="text-xs text-gray-400 truncate">{filePath}</div>
                      </div>
                      <div className="flex items-center gap-2 flex-shrink-0">
                        {getOperationIcon(latestChange.operation)}
                        <span className="text-xs text-gray-400">{changes.length}</span>
                      </div>
                    </button>
                    
                    {isExpanded && (
                      <div className="border-t border-gray-700/50 bg-gray-900/50">
                        {changes.map((change) => (
                          <button
                            key={change.id}
                            onClick={() => setSelectedFile(change)}
                            className={`w-full p-2 text-left hover:bg-gray-800 border-b border-gray-700/30 last:border-b-0 ${
                              selectedFile?.id === change.id ? 'bg-blue-900/20' : ''
                            }`}
                          >
                            <div className="flex items-center gap-2 mb-1">
                              {getOperationIcon(change.operation)}
                              <span className={`text-xs px-2 py-0.5 rounded ${getOperationColor(change.operation)}`}>
                                {change.operation}
                              </span>
                              <span className="text-xs text-gray-400 ml-auto">
                                {new Date(change.timestamp).toLocaleTimeString()}
                              </span>
                            </div>
                            <div className="text-xs text-gray-400">by {change.agent}</div>
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          )}
        </div>

        {/* Diff Viewer */}
        <div className="flex-1 flex flex-col">
          {selectedFile ? (
            <>
              {/* Header */}
              <div className="p-4 border-b border-gray-800 bg-gray-800/50">
                <div className="flex items-center gap-2 mb-2">
                  <FileText className="w-5 h-5 text-blue-400" />
                  <span className="font-semibold">{selectedFile.file_path}</span>
                  <span className={`text-xs px-2 py-0.5 rounded ${getOperationColor(selectedFile.operation)}`}>
                    {selectedFile.operation}
                  </span>
                </div>
                <div className="text-sm text-gray-400 flex items-center gap-4">
                  <div className="flex items-center gap-1">
                    <Clock className="w-4 h-4" />
                    {new Date(selectedFile.timestamp).toLocaleString()}
                  </div>
                  <div>by {selectedFile.agent}</div>
                </div>
              </div>

              {/* Monaco Diff Editor */}
              <div className="flex-1">
                {selectedFile.old_content && selectedFile.new_content ? (
                  <DiffEditor
                    height="100%"
                    language={(() => {
                      const ext = selectedFile.file_path.split('.').pop()?.toLowerCase()
                      const langMap: Record<string, string> = {
                        'ts': 'typescript', 'tsx': 'typescript', 'js': 'javascript', 'jsx': 'javascript',
                        'py': 'python', 'json': 'json', 'md': 'markdown', 'yaml': 'yaml', 'yml': 'yaml',
                        'html': 'html', 'css': 'css', 'xml': 'xml', 'sql': 'sql', 'sh': 'shell',
                        'go': 'go', 'rs': 'rust', 'java': 'java', 'cpp': 'cpp', 'c': 'c'
                      }
                      return langMap[ext || ''] || 'plaintext'
                    })()}
                    theme="vs-dark"
                    original={selectedFile.old_content}
                    modified={selectedFile.new_content}
                    options={{
                      readOnly: true,
                      minimap: { enabled: true },
                      fontSize: 14,
                      lineNumbers: 'on',
                      automaticLayout: true,
                      renderSideBySide: true,
                      diffWordWrap: 'on',
                      enableSplitViewResizing: true,
                      renderOverviewRuler: true,
                    }}
                  />
                ) : selectedFile.diff ? (
                  <div className="h-full p-4 overflow-auto">
                    <pre className="text-sm font-mono whitespace-pre-wrap">{selectedFile.diff}</pre>
                  </div>
                ) : (
                  <div className="h-full flex items-center justify-center text-gray-400">
                    <div className="text-center">
                      <p>No diff content available</p>
                      <p className="text-xs mt-2 text-gray-500">
                        File change detected but content not included in message
                      </p>
                      <p className="text-xs mt-2 text-gray-400">
                        Agents should send file_change messages with old_content and new_content tags
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </>
          ) : (
            <div className="h-full flex items-center justify-center text-gray-400">
              <div className="text-center">
                <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>Select a file change to view diff</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

