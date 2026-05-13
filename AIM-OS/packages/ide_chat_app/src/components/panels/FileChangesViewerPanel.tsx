/**
 * File Changes Viewer Panel Component
 * 
 * Phase 2.3: Bottom Drawer Panels
 * 
 * Git-style file changes viewer with diff visualization.
 * Features:
 * - File change list
 * - Diff viewer
 * - Change staging
 * - File comparison
 * - AIM-OS integration (CMC bitemporal, VIF validation)
 */

import React, { useState, useCallback, useEffect } from 'react'
import { FileDiff, Plus, Minus, FileText, GitBranch, CheckCircle2, Circle, X, Eye, Code, Clock, User, Brain, Shield, Link2, History } from 'lucide-react'
import { useAIMOS } from '../../hooks/useAIMOS'
import { LoadingState } from '../LoadingState'
import { ErrorBoundary } from '../ErrorBoundary'

interface FileChange {
  id: string
  filePath: string
  status: 'added' | 'modified' | 'deleted' | 'renamed'
  additions: number
  deletions: number
  staged: boolean
  diff?: string
  agent?: string // Agent who made the change
  timestamp?: string // When change was made
  cmcAtomId?: string // CMC bitemporal atom ID
  vifConfidence?: number // VIF confidence for change
  relatedChanges?: string[] // Related change IDs
  bitemporalHistory?: Array<{
    validFrom: string
    validTo?: string
    content: string
    agent?: string
  }>
}

const mockChanges: FileChange[] = [
  {
    id: 'change-1',
    filePath: 'packages/ide_chat_app/src/components/panels/LayersPanel.tsx',
    status: 'added',
    additions: 245,
    deletions: 0,
    staged: false,
    agent: 'Rev',
    timestamp: '2025-11-07T10:00:00Z',
    cmcAtomId: 'cmc-atom-001',
    vifConfidence: 0.95,
    diff: `+/**
+ * Layers Panel Component
+ * 
+ * Phase 2.2: Right Drawer Panels
+ * 
+ * Visual layer management (like Photoshop/Figma).
+ * Features:
+ * - Layer hierarchy
+ * - Layer visibility toggle
+ * - Layer locking
+ * - Layer reordering
+ * - Layer grouping
+ * - AIM-OS integration (CMC storage, VIF confidence, SEG relationships)
+ */
+
+import React, { useState, useMemo } from 'react'
+import { Layers, Eye, EyeOff, Lock, Unlock, Folder, FolderOpen, Search, Plus, Trash2, Edit2 } from 'lucide-react'
+...`,
+    bitemporalHistory: [
      {
        validFrom: '2025-11-07T10:00:00Z',
        content: 'File created',
        agent: 'Rev',
      },
    ],
  },
  {
    id: 'change-2',
    filePath: 'packages/ide_chat_app/src/components/RevIDELayout.tsx',
    status: 'modified',
    additions: 12,
    deletions: 8,
    staged: true,
    agent: 'Rev',
    timestamp: '2025-11-07T10:15:00Z',
    cmcAtomId: 'cmc-atom-002',
    vifConfidence: 0.98,
    diff: `-        return (
-          <div className="h-full bg-gray-800 p-4 text-gray-400 text-sm">
-            <div className="flex items-center gap-2 mb-4">
-              <Layers className="w-5 h-5" />
-              <span className="font-semibold">Layers</span>
-            </div>
-            <p>Layers Panel - Coming Soon</p>
-          </div>
-        )
+        return <LayersPanel />`,
+    bitemporalHistory: [
      {
        validFrom: '2025-11-07T09:00:00Z',
        validTo: '2025-11-07T10:15:00Z',
        content: 'Placeholder implementation',
        agent: 'Aether',
      },
      {
        validFrom: '2025-11-07T10:15:00Z',
        content: 'Integrated LayersPanel component',
        agent: 'Rev',
      },
    ],
  },
  {
    id: 'change-3',
    filePath: 'packages/ide_chat_app/src/components/panels/OldPanel.tsx',
    status: 'deleted',
    additions: 0,
    deletions: 156,
    staged: false,
  },
  {
    id: 'change-4',
    filePath: 'packages/ide_chat_app/src/components/panels/AssetsPanel.tsx',
    status: 'added',
    additions: 198,
    deletions: 0,
    staged: false,
  },
]

export const FileChangesViewerPanel: React.FC = () => {
  const [changes, setChanges] = useState<FileChange[]>(mockChanges)
  const [selectedChange, setSelectedChange] = useState<FileChange | null>(null)
  const [showDiff, setShowDiff] = useState(false)
  const [showBitemporal, setShowBitemporal] = useState(false)
  const [filterStatus, setFilterStatus] = useState<'all' | FileChange['status']>('all')
  const [showStagedOnly, setShowStagedOnly] = useState(false)

  // AIM-OS integration
  const { cmc, vif, tcs, isConnected, useMockData, loading } = useAIMOS()

  // Load file changes from AIM-OS (CMC bitemporal, VIF confidence, TCS timeline)
  useEffect(() => {
    const loadFileChanges = async () => {
      if (!useMockData && isConnected) {
        try {
          // Load recent CMC atoms with file change modality
          const changeAtoms = await cmc.retrieve('file change modification diff', 50)
          
          // Get TCS timeline entries for change history
          const timelineEntries = await tcs.getLogs(50)
          
          // Transform CMC atoms to FileChange format
          const loadedChanges: FileChange[] = changeAtoms
            .filter(atom => atom.modality === 'event' || atom.metadata?.type === 'file_change')
            .map((atom, index) => ({
              id: atom.id,
              filePath: atom.metadata?.filePath || `file-${index}`,
              status: atom.metadata?.status || 'modified',
              additions: atom.metadata?.additions || 0,
              deletions: atom.metadata?.deletions || 0,
              staged: atom.metadata?.staged || false,
              diff: atom.content.inline,
              agent: atom.metadata?.agent,
              timestamp: atom.created_at,
              cmcAtomId: atom.id,
              vifConfidence: atom.witness.uncertainty_band === 'green' ? 0.9 : 
                           atom.witness.uncertainty_band === 'yellow' ? 0.7 : 0.5,
              relatedChanges: atom.metadata?.relatedChanges,
              bitemporalHistory: atom.metadata?.bitemporalHistory || [],
            }))
          
          if (loadedChanges.length > 0) {
            setChanges(loadedChanges)
          }
        } catch (error) {
          console.warn('Failed to load file changes from AIM-OS, using mock data', error)
          // Keep mock changes as fallback
        }
      }
    }
    
    loadFileChanges()
  }, [cmc, vif, tcs, isConnected, useMockData])

  const toggleStage = useCallback((changeId: string) => {
    setChanges((prev) =>
      prev.map((change) =>
        change.id === changeId ? { ...change, staged: !change.staged } : change
      )
    )
  }, [])

  const getStatusIcon = (status: FileChange['status']) => {
    switch (status) {
      case 'added':
        return <Plus className="w-4 h-4 text-green-400" />
      case 'modified':
        return <FileDiff className="w-4 h-4 text-blue-400" />
      case 'deleted':
        return <Minus className="w-4 h-4 text-red-400" />
      case 'renamed':
        return <FileText className="w-4 h-4 text-yellow-400" />
      default:
        return <FileText className="w-4 h-4 text-gray-400" />
    }
  }

  const getStatusColor = (status: FileChange['status']) => {
    switch (status) {
      case 'added':
        return 'text-green-400'
      case 'modified':
        return 'text-blue-400'
      case 'deleted':
        return 'text-red-400'
      case 'renamed':
        return 'text-yellow-400'
      default:
        return 'text-gray-400'
    }
  }

  const stagedCount = changes.filter((c) => c.staged).length
  const totalAdditions = changes.reduce((sum, c) => sum + c.additions, 0)
  const totalDeletions = changes.reduce((sum, c) => sum + c.deletions, 0)

  const filteredChanges = changes.filter(change => {
    const matchesStatus = filterStatus === 'all' || change.status === filterStatus
    const matchesStaged = !showStagedOnly || change.staged
    return matchesStatus && matchesStaged
  })

  const renderDiffLine = (line: string, index: number) => {
    if (line.startsWith('+')) {
      return (
        <div key={index} className="bg-green-900/30 text-green-300 px-2 py-0.5 flex items-start">
          <span className="text-green-500 mr-2 select-none">+</span>
          <span className="font-mono text-xs">{line.substring(1)}</span>
        </div>
      )
    } else if (line.startsWith('-')) {
      return (
        <div key={index} className="bg-red-900/30 text-red-300 px-2 py-0.5 flex items-start">
          <span className="text-red-500 mr-2 select-none">-</span>
          <span className="font-mono text-xs">{line.substring(1)}</span>
        </div>
      )
    } else {
      return (
        <div key={index} className="text-gray-400 px-2 py-0.5 flex items-start">
          <span className="text-gray-600 mr-2 select-none"> </span>
          <span className="font-mono text-xs">{line}</span>
        </div>
      )
    }
  }

  return (
    <ErrorBoundary>
      <div className="h-full flex flex-col bg-gray-800" role="complementary" aria-label="File Changes Viewer Panel">
        {loading.cmc || loading.tcs ? (
          <LoadingState message="Loading file changes..." />
        ) : (
          <>
      {/* Header */}
      <div className="h-10 bg-gray-900 border-b border-gray-700 flex items-center justify-between px-3 shrink-0">
        <div className="flex items-center gap-2">
          <FileDiff className="w-4 h-4 text-gray-400" />
          <span className="text-sm font-semibold text-gray-300">File Changes</span>
          <span className="px-2 py-0.5 bg-gray-700 text-gray-400 text-xs rounded">
            {filteredChanges.length} {filteredChanges.length === 1 ? 'file' : 'files'}
          </span>
        </div>
        <div className="flex items-center gap-2 text-xs text-gray-400">
          <span className="text-green-400">+{totalAdditions}</span>
          <span className="text-red-400">-{totalDeletions}</span>
        </div>
      </div>

      {/* Filters */}
      <div className="px-2 py-2 border-b border-gray-700 shrink-0 flex items-center gap-2">
        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value as any)}
          className="px-2 py-1 text-xs bg-gray-700 text-gray-300 rounded border border-gray-600 focus:outline-none focus:border-blue-500"
        >
          <option value="all">All Status</option>
          <option value="added">Added</option>
          <option value="modified">Modified</option>
          <option value="deleted">Deleted</option>
          <option value="renamed">Renamed</option>
        </select>
        <button
          onClick={() => setShowStagedOnly(!showStagedOnly)}
          className={`px-2 py-1 text-xs rounded flex items-center gap-1 ${
            showStagedOnly
              ? 'bg-green-600 text-white'
              : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
          }`}
        >
          <CheckCircle2 className="w-3 h-3" />
          Staged Only
        </button>
      </div>

      {/* Changes List */}
      <div className="flex-1 overflow-y-auto">
        {filteredChanges.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500 text-sm">
            <FileDiff className="w-8 h-8 mb-2 opacity-50" />
            <p>No file changes</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-700">
            {filteredChanges.map((change) => (
              <div
                key={change.id}
                className={`p-3 cursor-pointer transition-colors ${
                  selectedChange?.id === change.id
                    ? 'bg-blue-600/20 border-l-2 border-blue-500'
                    : 'hover:bg-gray-700 border-l-2 border-transparent'
                }`}
                onClick={() => setSelectedChange(change)}
              >
                <div className="flex items-center gap-2 mb-1">
                  {getStatusIcon(change.status)}
                  <span className={`text-sm font-medium ${getStatusColor(change.status)}`}>
                    {change.status}
                  </span>
                  {change.agent && (
                    <span className="text-xs text-gray-500 flex items-center gap-1">
                      <User className="w-3 h-3" />
                      {change.agent}
                    </span>
                  )}
                  {change.timestamp && (
                    <span className="text-xs text-gray-500 flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {new Date(change.timestamp).toLocaleTimeString()}
                    </span>
                  )}
                  {change.vifConfidence !== undefined && (
                    <span className={`text-xs px-1.5 py-0.5 rounded ${
                      change.vifConfidence >= 0.95 ? 'bg-green-600/20 text-green-400' :
                      change.vifConfidence >= 0.90 ? 'bg-yellow-600/20 text-yellow-400' :
                      'bg-red-600/20 text-red-400'
                    }`} title="VIF Confidence">
                      <Shield className="w-3 h-3 inline mr-1" />
                      {(change.vifConfidence * 100).toFixed(0)}%
                    </span>
                  )}
                  <span className="text-xs text-gray-500 ml-auto">
                    {change.additions > 0 && <span className="text-green-400">+{change.additions}</span>}
                    {change.deletions > 0 && <span className="text-red-400"> -{change.deletions}</span>}
                  </span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      toggleStage(change.id)
                    }}
                    className={`p-1 rounded transition-colors ${
                      change.staged
                        ? 'bg-green-600/20 text-green-400'
                        : 'text-gray-400 hover:text-gray-300 hover:bg-gray-600'
                    }`}
                    aria-label={change.staged ? 'Unstage file' : 'Stage file'}
                  >
                    {change.staged ? (
                      <CheckCircle2 className="w-4 h-4" />
                    ) : (
                      <Circle className="w-4 h-4" />
                    )}
                  </button>
                </div>
                <div className="text-sm text-gray-300 font-mono truncate" title={change.filePath}>
                  {change.filePath}
                </div>
                {change.cmcAtomId && (
                  <div className="text-xs text-gray-500 mt-1 flex items-center gap-1">
                    <Brain className="w-3 h-3" />
                    CMC: {change.cmcAtomId.substring(0, 12)}...
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Diff Viewer */}
      {selectedChange && showDiff && selectedChange.diff && (
        <div className="border-t border-gray-700 bg-gray-900 shrink-0" style={{ maxHeight: '40%' }}>
          <div className="h-8 bg-gray-800 border-b border-gray-700 flex items-center justify-between px-3">
            <div className="flex items-center gap-2">
              <Code className="w-4 h-4 text-gray-400" />
              <span className="text-xs text-gray-400">Diff</span>
              {selectedChange.vifConfidence !== undefined && (
                <span className={`text-xs px-1.5 py-0.5 rounded ${
                  selectedChange.vifConfidence >= 0.95 ? 'bg-green-600/20 text-green-400' :
                  selectedChange.vifConfidence >= 0.90 ? 'bg-yellow-600/20 text-yellow-400' :
                  'bg-red-600/20 text-red-400'
                }`}>
                  VIF: {(selectedChange.vifConfidence * 100).toFixed(0)}%
                </span>
              )}
            </div>
            <button
              onClick={() => setShowDiff(false)}
              className="text-gray-400 hover:text-gray-300"
              aria-label="Close diff"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
          <div className="p-3 overflow-y-auto font-mono text-xs max-h-64">
            {selectedChange.diff?.split('\n').map((line, idx) => renderDiffLine(line, idx))}
          </div>
        </div>
      )}

      {/* Bitemporal History Viewer */}
      {selectedChange && showBitemporal && selectedChange.bitemporalHistory && (
        <div className="border-t border-gray-700 bg-gray-900 shrink-0" style={{ maxHeight: '40%' }}>
          <div className="h-8 bg-gray-800 border-b border-gray-700 flex items-center justify-between px-3">
            <div className="flex items-center gap-2">
              <History className="w-4 h-4 text-gray-400" />
              <span className="text-xs text-gray-400">Bitemporal History</span>
              {selectedChange.cmcAtomId && (
                <span className="text-xs text-gray-500 font-mono">
                  {selectedChange.cmcAtomId.substring(0, 12)}...
                </span>
              )}
            </div>
            <button
              onClick={() => setShowBitemporal(false)}
              className="text-gray-400 hover:text-gray-300"
              aria-label="Close history"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
          <div className="p-3 overflow-y-auto text-xs max-h-64 space-y-2">
            {selectedChange.bitemporalHistory.map((entry, idx) => (
              <div key={idx} className="p-2 bg-gray-800 rounded border border-gray-700">
                <div className="flex items-center gap-2 mb-1">
                  <Clock className="w-3 h-3 text-gray-400" />
                  <span className="text-gray-300">
                    {new Date(entry.validFrom).toLocaleString()}
                  </span>
                  {entry.validTo && (
                    <>
                      <span className="text-gray-500">→</span>
                      <span className="text-gray-400">
                        {new Date(entry.validTo).toLocaleString()}
                      </span>
                    </>
                  )}
                  {!entry.validTo && (
                    <span className="text-green-400 text-xs">(Current)</span>
                  )}
                </div>
                {entry.agent && (
                  <div className="flex items-center gap-1 text-gray-400 mb-1">
                    <User className="w-3 h-3" />
                    <span>{entry.agent}</span>
                  </div>
                )}
                <div className="text-gray-300">{entry.content}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="h-10 bg-gray-900 border-t border-gray-700 flex items-center justify-between px-3 shrink-0">
        <div className="flex items-center gap-2">
          {selectedChange && (
            <>
              <button
                onClick={() => setShowDiff(!showDiff)}
                className="flex items-center gap-1 px-2 py-1 text-xs text-gray-400 hover:text-gray-300 hover:bg-gray-800 rounded transition-colors"
              >
                <Eye className="w-3 h-3" />
                {showDiff ? 'Hide' : 'Show'} Diff
              </button>
              {selectedChange.bitemporalHistory && (
                <button
                  onClick={() => setShowBitemporal(!showBitemporal)}
                  className="flex items-center gap-1 px-2 py-1 text-xs text-gray-400 hover:text-gray-300 hover:bg-gray-800 rounded transition-colors"
                >
                  <History className="w-3 h-3" />
                  {showBitemporal ? 'Hide' : 'Show'} History
                </button>
              )}
            </>
          )}
        </div>
        <div className="flex items-center gap-2 text-xs text-gray-400">
          <span>
            {stagedCount} {stagedCount === 1 ? 'file' : 'files'} staged
          </span>
        </div>
      </div>
          </>
        )}
      </div>
    </ErrorBoundary>
  )
}

