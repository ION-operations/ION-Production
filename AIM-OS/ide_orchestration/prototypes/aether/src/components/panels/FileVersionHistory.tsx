// File Version History Panel - Simple Dropdown Version Selection
// Like git but simpler - see time, edits, details, scroll through changes

import React, { useState } from 'react'
import { ChevronDown, Clock, User, GitBranch, Eye, FileText } from 'lucide-react'

export const FileVersionHistoryPanel: React.FC<{ filePath: string }> = ({ filePath }) => {
  const [selectedVersion, setSelectedVersion] = useState<number>(0)
  const [showDiff, setShowDiff] = useState(false)

  // Mock version history with AIM-OS integration
  const versionHistory = [
    {
      version: 5,
      timestamp: '2025-11-07T17:30:00Z',
      agent: 'Aether',
      confidence: 0.95,
      changes: {
        added: 45,
        removed: 12,
        modified: 8
      },
      description: 'Added AIM-OS structure panels and hierarchical code explorer',
      evidence: ['atom_500', 'atom_501'],
      cmcAtom: 'atom_500',
      vifConfidence: 0.95,
      segEvidence: ['evidence_node_10'],
      bitemporal: {
        valid_from: '2025-11-07T17:30:00Z',
        valid_to: null
      },
      diff: {
        added: ['+ SuperIndexPanel', '+ MasterIndexPanel', '+ SystemMapPanel'],
        removed: ['- Old panel system'],
        modified: ['~ Updated layout structure']
      }
    },
    {
      version: 4,
      timestamp: '2025-11-07T16:00:00Z',
      agent: 'Aether',
      confidence: 0.92,
      changes: {
        added: 23,
        removed: 5,
        modified: 3
      },
      description: 'Added debug console panel with AIM-OS integration',
      evidence: ['atom_450', 'atom_451'],
      cmcAtom: 'atom_450',
      vifConfidence: 0.92,
      segEvidence: ['evidence_node_9'],
      bitemporal: {
        valid_from: '2025-11-07T16:00:00Z',
        valid_to: '2025-11-07T17:30:00Z'
      },
      diff: {
        added: ['+ DebugConsolePanel', '+ Debug infrastructure'],
        removed: [],
        modified: ['~ Enhanced terminal panel']
      }
    },
    {
      version: 3,
      timestamp: '2025-11-07T15:00:00Z',
      agent: 'Aether',
      confidence: 0.88,
      changes: {
        added: 15,
        removed: 2,
        modified: 1
      },
      description: 'Enhanced panels with detailed implementations',
      evidence: ['atom_400'],
      cmcAtom: 'atom_400',
      vifConfidence: 0.88,
      segEvidence: ['evidence_node_8'],
      bitemporal: {
        valid_from: '2025-11-07T15:00:00Z',
        valid_to: '2025-11-07T16:00:00Z'
      },
      diff: {
        added: ['+ Enhanced panel UI', '+ Mock data integration'],
        removed: [],
        modified: ['~ Panel styling']
      }
    },
    {
      version: 2,
      timestamp: '2025-11-07T14:00:00Z',
      agent: 'Aether',
      confidence: 0.90,
      changes: {
        added: 8,
        removed: 1,
        modified: 0
      },
      description: 'Initial panel implementations',
      evidence: ['atom_350'],
      cmcAtom: 'atom_350',
      vifConfidence: 0.90,
      segEvidence: ['evidence_node_7'],
      bitemporal: {
        valid_from: '2025-11-07T14:00:00Z',
        valid_to: '2025-11-07T15:00:00Z'
      },
      diff: {
        added: ['+ FileExplorerPanel', '+ ComponentLibraryPanel'],
        removed: [],
        modified: []
      }
    },
    {
      version: 1,
      timestamp: '2025-11-07T13:00:00Z',
      agent: 'Aether',
      confidence: 0.95,
      changes: {
        added: 42,
        removed: 0,
        modified: 0
      },
      description: 'Initial file creation',
      evidence: ['atom_300'],
      cmcAtom: 'atom_300',
      vifConfidence: 0.95,
      segEvidence: ['evidence_node_6'],
      bitemporal: {
        valid_from: '2025-11-07T13:00:00Z',
        valid_to: '2025-11-07T14:00:00Z'
      },
      diff: {
        added: ['+ Created IDELayout.tsx', '+ Basic structure'],
        removed: [],
        modified: []
      }
    }
  ]

  const currentVersion = versionHistory[selectedVersion]

  return (
    <div className="h-full flex flex-col bg-gray-900">
      {/* Header */}
      <div className="p-3 border-b border-gray-700 bg-gray-800">
        <div className="flex items-center justify-between mb-2">
          <div>
            <div className="text-xs font-semibold text-blue-400 mb-1 flex items-center gap-2">
              <FileText className="w-4 h-4" />
              Version History
            </div>
            <div className="text-xs text-gray-500">{filePath}</div>
          </div>
        </div>

        {/* Version Dropdown */}
        <div className="relative">
          <select
            value={selectedVersion}
            onChange={(e) => setSelectedVersion(Number(e.target.value))}
            className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-xs text-gray-200 appearance-none cursor-pointer hover:bg-gray-600 transition-colors"
          >
            {versionHistory.map((version, idx) => (
              <option key={version.version} value={idx}>
                Version {version.version} • {new Date(version.timestamp).toLocaleString()} • {version.description}
              </option>
            ))}
          </select>
          <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
        </div>
      </div>

      {/* Version Details */}
      <div className="flex-1 overflow-auto p-3 space-y-4">
        {/* Current Version Info */}
        <div className="bg-gray-800 rounded p-3 border border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <div className="text-sm font-semibold text-gray-200">
              Version {currentVersion.version}
              {selectedVersion === 0 && (
                <span className="ml-2 text-xs px-2 py-0.5 bg-green-900 text-green-300 rounded">Current</span>
              )}
            </div>
            <div className="text-xs text-green-400">Conf: {(currentVersion.confidence * 100).toFixed(0)}%</div>
          </div>

          <div className="space-y-2 text-xs">
            <div className="flex items-center gap-2 text-gray-400">
              <Clock className="w-3 h-3" />
              <span>{new Date(currentVersion.timestamp).toLocaleString()}</span>
            </div>
            <div className="flex items-center gap-2 text-gray-400">
              <User className="w-3 h-3" />
              <span>{currentVersion.agent}</span>
            </div>
            <div className="text-gray-300 mt-2">{currentVersion.description}</div>
          </div>
        </div>

        {/* Changes Summary */}
        <div className="bg-gray-800 rounded p-3 border border-gray-700">
          <div className="text-xs font-semibold text-gray-300 mb-2">Changes</div>
          <div className="flex items-center gap-4 text-xs">
            <div className="flex items-center gap-1">
              <span className="text-green-400">+{currentVersion.changes.added}</span>
              <span className="text-gray-500">added</span>
            </div>
            <div className="flex items-center gap-1">
              <span className="text-red-400">-{currentVersion.changes.removed}</span>
              <span className="text-gray-500">removed</span>
            </div>
            <div className="flex items-center gap-1">
              <span className="text-yellow-400">~{currentVersion.changes.modified}</span>
              <span className="text-gray-500">modified</span>
            </div>
          </div>
        </div>

        {/* Diff View Toggle */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowDiff(!showDiff)}
            className={`px-3 py-1 text-xs rounded transition-colors ${
              showDiff
                ? 'bg-blue-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            <Eye className="w-3 h-3 inline mr-1" />
            {showDiff ? 'Hide' : 'Show'} Diff
          </button>
        </div>

        {/* Diff View */}
        {showDiff && (
          <div className="bg-gray-800 rounded p-3 border border-gray-700">
            <div className="text-xs font-semibold text-gray-300 mb-2">Diff View</div>
            <div className="space-y-1 font-mono text-xs">
              {currentVersion.diff.added.map((line, idx) => (
                <div key={`added-${idx}`} className="text-green-400 bg-green-900/20 px-2 py-0.5 rounded">
                  {line}
                </div>
              ))}
              {currentVersion.diff.removed.map((line, idx) => (
                <div key={`removed-${idx}`} className="text-red-400 bg-red-900/20 px-2 py-0.5 rounded">
                  {line}
                </div>
              ))}
              {currentVersion.diff.modified.map((line, idx) => (
                <div key={`modified-${idx}`} className="text-yellow-400 bg-yellow-900/20 px-2 py-0.5 rounded">
                  {line}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* AIM-OS Integration */}
        <div className="bg-gray-800 rounded p-3 border border-gray-700">
          <div className="text-xs font-semibold text-gray-300 mb-2">AIM-OS Integration</div>
          <div className="space-y-2 text-xs">
            <div className="flex items-center gap-2 text-gray-400">
              <span className="text-purple-400">CMC Atom:</span>
              <span className="text-gray-300">{currentVersion.cmcAtom}</span>
            </div>
            <div className="flex items-center gap-2 text-gray-400">
              <span className="text-blue-400">VIF Confidence:</span>
              <span className="text-gray-300">{(currentVersion.vifConfidence * 100).toFixed(0)}%</span>
            </div>
            <div className="flex items-center gap-2 text-gray-400">
              <span className="text-green-400">SEG Evidence:</span>
              <span className="text-gray-300">{currentVersion.segEvidence.join(', ')}</span>
            </div>
            <div className="flex items-center gap-2 text-gray-400">
              <span className="text-yellow-400">Bitemporal:</span>
              <span className="text-gray-300">
                {new Date(currentVersion.bitemporal.valid_from).toLocaleString()}
                {currentVersion.bitemporal.valid_to && (
                  <> → {new Date(currentVersion.bitemporal.valid_to).toLocaleString()}</>
                )}
              </span>
            </div>
          </div>
        </div>

        {/* Version Timeline */}
        <div className="bg-gray-800 rounded p-3 border border-gray-700">
          <div className="text-xs font-semibold text-gray-300 mb-2">All Versions</div>
          <div className="space-y-2">
            {versionHistory.map((version, idx) => (
              <div
                key={version.version}
                className={`p-2 rounded cursor-pointer transition-colors ${
                  idx === selectedVersion
                    ? 'bg-blue-900/30 border border-blue-700'
                    : 'bg-gray-700 hover:bg-gray-600 border border-gray-600'
                }`}
                onClick={() => setSelectedVersion(idx)}
              >
                <div className="flex items-center justify-between mb-1">
                  <div className="text-xs font-medium text-gray-200">
                    Version {version.version}
                    {idx === 0 && (
                      <span className="ml-2 text-xs px-1 py-0.5 bg-green-900 text-green-300 rounded">Current</span>
                    )}
                  </div>
                  <div className="text-xs text-gray-500">
                    {new Date(version.timestamp).toLocaleTimeString()}
                  </div>
                </div>
                <div className="text-xs text-gray-400">{version.description}</div>
                <div className="flex items-center gap-2 mt-1 text-xs text-gray-500">
                  <span>+{version.changes.added}</span>
                  <span>-{version.changes.removed}</span>
                  <span>~{version.changes.modified}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

// Enhanced version with scrollable timeline
export const FileVersionHistoryPanelV2: React.FC<{ filePath: string }> = ({ filePath }) => {
  const [selectedVersion, setSelectedVersion] = useState<number>(0)
  const [showDiff, setShowDiff] = useState(true)

  const versionHistory = [
    {
      version: 5,
      timestamp: '2025-11-07T17:30:00Z',
      agent: 'Aether',
      confidence: 0.95,
      changes: { added: 45, removed: 12, modified: 8 },
      description: 'Added AIM-OS structure panels',
      evidence: ['atom_500'],
      diff: {
        added: ['+ SuperIndexPanel', '+ MasterIndexPanel'],
        removed: ['- Old panel system'],
        modified: ['~ Updated layout']
      }
    },
    {
      version: 4,
      timestamp: '2025-11-07T16:00:00Z',
      agent: 'Aether',
      confidence: 0.92,
      changes: { added: 23, removed: 5, modified: 3 },
      description: 'Added debug console panel',
      evidence: ['atom_450'],
      diff: {
        added: ['+ DebugConsolePanel'],
        removed: [],
        modified: ['~ Enhanced terminal']
      }
    },
    {
      version: 3,
      timestamp: '2025-11-07T15:00:00Z',
      agent: 'Aether',
      confidence: 0.88,
      changes: { added: 15, removed: 2, modified: 1 },
      description: 'Enhanced panels',
      evidence: ['atom_400'],
      diff: {
        added: ['+ Enhanced UI'],
        removed: [],
        modified: ['~ Panel styling']
      }
    },
    {
      version: 2,
      timestamp: '2025-11-07T14:00:00Z',
      agent: 'Aether',
      confidence: 0.90,
      changes: { added: 8, removed: 1, modified: 0 },
      description: 'Initial panels',
      evidence: ['atom_350'],
      diff: {
        added: ['+ FileExplorerPanel'],
        removed: [],
        modified: []
      }
    },
    {
      version: 1,
      timestamp: '2025-11-07T13:00:00Z',
      agent: 'Aether',
      confidence: 0.95,
      changes: { added: 42, removed: 0, modified: 0 },
      description: 'Initial creation',
      evidence: ['atom_300'],
      diff: {
        added: ['+ Created file'],
        removed: [],
        modified: []
      }
    }
  ]

  const currentVersion = versionHistory[selectedVersion]

  return (
    <div className="h-full flex flex-col bg-gray-900">
      <div className="p-3 border-b border-gray-700 bg-gray-800">
        <div className="text-xs font-semibold text-blue-400 mb-1">Version History V2</div>
        <div className="text-xs text-gray-500">Scrollable Timeline • Simple Dropdown • AIM-OS Integrated</div>
      </div>

      <div className="flex-1 overflow-auto">
        <div className="grid grid-cols-3 gap-4 p-3">
          {/* Version Timeline (Scrollable) */}
          <div className="col-span-1">
            <div className="text-xs font-semibold text-gray-300 mb-2">Timeline</div>
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {versionHistory.map((version, idx) => (
                <div
                  key={version.version}
                  className={`p-2 rounded cursor-pointer transition-colors ${
                    idx === selectedVersion
                      ? 'bg-blue-900/30 border-2 border-blue-500'
                      : 'bg-gray-800 border border-gray-700 hover:bg-gray-700'
                  }`}
                  onClick={() => setSelectedVersion(idx)}
                >
                  <div className="flex items-center justify-between mb-1">
                    <div className="text-xs font-medium text-gray-200">v{version.version}</div>
                    {idx === 0 && (
                      <span className="text-xs px-1 py-0.5 bg-green-900 text-green-300 rounded">Current</span>
                    )}
                  </div>
                  <div className="text-xs text-gray-500 mb-1">
                    {new Date(version.timestamp).toLocaleTimeString()}
                  </div>
                  <div className="text-xs text-gray-400 line-clamp-2">{version.description}</div>
                  <div className="flex items-center gap-2 mt-1 text-xs">
                    <span className="text-green-400">+{version.changes.added}</span>
                    <span className="text-red-400">-{version.changes.removed}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Version Details */}
          <div className="col-span-2">
            <div className="bg-gray-800 rounded p-3 border border-gray-700 mb-3">
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm font-semibold text-gray-200">
                  Version {currentVersion.version}
                </div>
                <div className="text-xs text-green-400">Conf: {(currentVersion.confidence * 100).toFixed(0)}%</div>
              </div>
              <div className="space-y-1 text-xs text-gray-400">
                <div>{new Date(currentVersion.timestamp).toLocaleString()}</div>
                <div>{currentVersion.agent}</div>
                <div className="text-gray-300 mt-2">{currentVersion.description}</div>
              </div>
            </div>

            {/* Diff View */}
            <div className="bg-gray-800 rounded p-3 border border-gray-700">
              <div className="flex items-center justify-between mb-2">
                <div className="text-xs font-semibold text-gray-300">Changes</div>
                <button
                  onClick={() => setShowDiff(!showDiff)}
                  className="text-xs text-gray-400 hover:text-gray-200"
                >
                  {showDiff ? 'Hide' : 'Show'} Diff
                </button>
              </div>
              {showDiff && (
                <div className="space-y-1 font-mono text-xs">
                  {currentVersion.diff.added.map((line, idx) => (
                    <div key={`added-${idx}`} className="text-green-400 bg-green-900/20 px-2 py-0.5 rounded">
                      {line}
                    </div>
                  ))}
                  {currentVersion.diff.removed.map((line, idx) => (
                    <div key={`removed-${idx}`} className="text-red-400 bg-red-900/20 px-2 py-0.5 rounded">
                      {line}
                    </div>
                  ))}
                  {currentVersion.diff.modified.map((line, idx) => (
                    <div key={`modified-${idx}`} className="text-yellow-400 bg-yellow-900/20 px-2 py-0.5 rounded">
                      {line}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

