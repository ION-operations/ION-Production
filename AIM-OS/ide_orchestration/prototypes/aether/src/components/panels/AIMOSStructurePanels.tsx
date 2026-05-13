// AIM-OS Structure Panels - Showing AIM-OS Wide Open
// Special panels for Master Index, Super Index, System Maps, NL Tags, Docs, Code

import React, { useState } from 'react'
import { ChevronRight, File, FolderOpen } from 'lucide-react'

// Super Index Panel - Master concept index
export const SuperIndexPanel: React.FC = () => {
  const superIndex = {
    totalConcepts: 1247,
    categories: [
      { name: 'Core Systems', count: 89, concepts: ['CMC', 'HHNI', 'VIF', 'SEG', 'APOE'] },
      { name: 'Protocols', count: 156, concepts: ['L0-L4', 'A-H Protocol', 'MCP Tools'] },
      { name: 'Standards', count: 234, concepts: ['Documentation', 'Coding', 'Quality'] },
      { name: 'Architecture', count: 178, concepts: ['System Maps', 'Indexes', 'Hierarchies'] }
    ],
    recentAdditions: [
      { concept: 'Debug Infrastructure', category: 'Architecture', confidence: 0.95 },
      { concept: 'Hierarchical Code Explorer', category: 'UI/UX', confidence: 0.88 }
    ]
  }

  return (
    <div className="h-full flex flex-col">
      <div className="p-3 border-b border-gray-700">
        <div className="text-xs font-semibold text-purple-400 mb-1">Super Index</div>
        <div className="text-xs text-gray-500">Master Concept Index • 1,247 Concepts • HHNI-Powered</div>
      </div>
      <div className="flex-1 overflow-auto p-3 space-y-4">
        <div className="bg-gray-800 rounded p-3 border border-gray-700">
          <div className="text-xs font-semibold text-gray-300 mb-2">Overview</div>
          <div className="text-sm text-gray-200 mb-1">Total Concepts: {superIndex.totalConcepts}</div>
          <div className="text-xs text-gray-400">Master index of all AIM-OS concepts</div>
        </div>

        <div className="space-y-2">
          <div className="text-xs font-semibold text-gray-300">Categories</div>
          {superIndex.categories.map((cat) => (
            <div key={cat.name} className="bg-gray-800 rounded p-2 border border-gray-700">
              <div className="flex items-center justify-between mb-1">
                <div className="text-xs font-medium text-gray-200">{cat.name}</div>
                <div className="text-xs text-gray-400">{cat.count} concepts</div>
              </div>
              <div className="flex flex-wrap gap-1">
                {cat.concepts.map((concept) => (
                  <span key={concept} className="text-xs px-2 py-0.5 bg-purple-900/30 text-purple-300 rounded">
                    {concept}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className="space-y-2">
          <div className="text-xs font-semibold text-gray-300">Recent Additions</div>
          {superIndex.recentAdditions.map((item, idx) => (
            <div key={idx} className="bg-gray-800 rounded p-2 border border-gray-700">
              <div className="flex items-center justify-between">
                <div className="text-xs text-gray-200">{item.concept}</div>
                <div className="text-xs text-green-400">Conf: {(item.confidence * 100).toFixed(0)}%</div>
              </div>
              <div className="text-xs text-gray-500">{item.category}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// Master Index Panel - System-level index
export const MasterIndexPanel: React.FC = () => {
  const masterIndex = {
    systems: [
      {
        id: 'cmc',
        name: 'CMC - Context Memory Core',
        layer: 'Layer 1: Memory',
        status: 'Production',
        dependencies: [],
        components: ['Atoms', 'Snapshots', 'Bitemporal', 'Pipelines'],
        confidence: 0.95
      },
      {
        id: 'hhni',
        name: 'HHNI - Hierarchical Hypergraph Neural Index',
        layer: 'Layer 2: Indexing',
        status: 'Production',
        dependencies: ['cmc'],
        components: ['Hierarchical Index', 'Semantic Search', 'Relationship Graph'],
        confidence: 0.92
      },
      {
        id: 'vif',
        name: 'VIF - Verifiable Intelligence Framework',
        layer: 'Layer 3: Quality',
        status: 'Production',
        dependencies: ['cmc', 'hhni'],
        components: ['Confidence Tracking', 'Quality Gates', 'Witness System'],
        confidence: 0.94
      }
    ]
  }

  return (
    <div className="h-full flex flex-col">
      <div className="p-3 border-b border-gray-700">
        <div className="text-xs font-semibold text-blue-400 mb-1">Master Index</div>
        <div className="text-xs text-gray-500">System-Level Index • All AIM-OS Systems • Layer Hierarchy</div>
      </div>
      <div className="flex-1 overflow-auto p-3 space-y-3">
        {masterIndex.systems.map((system) => (
          <div key={system.id} className="bg-gray-800 rounded p-3 border border-gray-700">
            <div className="flex items-center justify-between mb-2">
              <div className="text-sm font-semibold text-gray-200">{system.name}</div>
              <div className="text-xs text-green-400">Conf: {(system.confidence * 100).toFixed(0)}%</div>
            </div>
            <div className="text-xs text-gray-400 mb-2">{system.layer}</div>
            <div className="flex items-center gap-2 mb-2">
              <span className={`text-xs px-2 py-0.5 rounded ${
                system.status === 'Production' ? 'bg-green-900 text-green-300' : 'bg-yellow-900 text-yellow-300'
              }`}>
                {system.status}
              </span>
            </div>
            <div className="mb-2">
              <div className="text-xs text-gray-500 mb-1">Components:</div>
              <div className="flex flex-wrap gap-1">
                {system.components.map((comp) => (
                  <span key={comp} className="text-xs px-2 py-0.5 bg-blue-900/30 text-blue-300 rounded">
                    {comp}
                  </span>
                ))}
              </div>
            </div>
            {system.dependencies.length > 0 && (
              <div>
                <div className="text-xs text-gray-500 mb-1">Depends on:</div>
                <div className="flex flex-wrap gap-1">
                  {system.dependencies.map((dep) => (
                    <span key={dep} className="text-xs px-2 py-0.5 bg-gray-700 text-gray-300 rounded">
                      {dep}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

// System Map Panel - Visual system relationships
export const SystemMapPanel: React.FC = () => {
  const systemMap = {
    nodes: [
      { id: 'cmc', name: 'CMC', layer: 1, x: 100, y: 100, connections: ['hhni', 'vif'] },
      { id: 'hhni', name: 'HHNI', layer: 2, x: 300, y: 100, connections: ['vif', 'seg'] },
      { id: 'vif', name: 'VIF', layer: 3, x: 200, y: 200, connections: ['seg', 'apoe'] },
      { id: 'seg', name: 'SEG', layer: 3, x: 400, y: 200, connections: ['apoe'] },
      { id: 'apoe', name: 'APOE', layer: 4, x: 300, y: 300, connections: [] }
    ],
    layers: [
      { level: 1, name: 'Memory', systems: ['CMC'] },
      { level: 2, name: 'Indexing', systems: ['HHNI'] },
      { level: 3, name: 'Quality', systems: ['VIF', 'SEG'] },
      { level: 4, name: 'Orchestration', systems: ['APOE'] }
    ]
  }

  return (
    <div className="h-full flex flex-col">
      <div className="p-3 border-b border-gray-700">
        <div className="text-xs font-semibold text-green-400 mb-1">System Map</div>
        <div className="text-xs text-gray-500">Visual System Relationships • Layer Hierarchy • Dependencies</div>
      </div>
      <div className="flex-1 overflow-auto p-3">
        <div className="mb-4">
          <div className="text-xs font-semibold text-gray-300 mb-2">Layer Hierarchy</div>
          <div className="space-y-2">
            {systemMap.layers.map((layer) => (
              <div key={layer.level} className="bg-gray-800 rounded p-2 border border-gray-700">
                <div className="text-xs font-medium text-gray-200 mb-1">
                  Layer {layer.level}: {layer.name}
                </div>
                <div className="flex flex-wrap gap-1">
                  {layer.systems.map((sys) => (
                    <span key={sys} className="text-xs px-2 py-0.5 bg-green-900/30 text-green-300 rounded">
                      {sys}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div>
          <div className="text-xs font-semibold text-gray-300 mb-2">System Connections</div>
          <div className="space-y-2">
            {systemMap.nodes.map((node) => (
              <div key={node.id} className="bg-gray-800 rounded p-2 border border-gray-700">
                <div className="text-xs font-medium text-gray-200 mb-1">{node.name}</div>
                {node.connections.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    <span className="text-xs text-gray-500">Connects to:</span>
                    {node.connections.map((conn) => (
                      <span key={conn} className="text-xs px-2 py-0.5 bg-blue-900/30 text-blue-300 rounded">
                        {conn.toUpperCase()}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

// Enhanced NL Tags Explorer Panel
export const NLTagsExplorerPanel: React.FC = () => {
  const nlTags = {
    totalTags: 1247,
    coverage: 0.87,
    bySystem: [
      { system: 'CMC', tags: 234, coverage: 0.92, validated: true },
      { system: 'HHNI', tags: 189, coverage: 0.88, validated: true },
      { system: 'VIF', tags: 156, coverage: 0.85, validated: false },
      { system: 'SEG', tags: 178, coverage: 0.90, validated: true }
    ],
    recentTags: [
      { id: 'VIF-WITNESS-001', description: 'Create VIF witness envelope', system: 'VIF', confidence: 0.95 },
      { id: 'CMC-STORE-001', description: 'Store atom in CMC', system: 'CMC', confidence: 0.98 },
      { id: 'HHNI-INDEX-001', description: 'Index document in HHNI', system: 'HHNI', confidence: 0.92 }
    ]
  }

  return (
    <div className="h-full flex flex-col">
      <div className="p-3 border-b border-gray-700">
        <div className="text-xs font-semibold text-blue-400 mb-1">NL Tags Explorer</div>
        <div className="text-xs text-gray-500">Natural Language Code Tags • Coverage: {(nlTags.coverage * 100).toFixed(0)}% • {nlTags.totalTags} Tags</div>
      </div>
      <div className="flex-1 overflow-auto p-3 space-y-4">
        <div className="bg-gray-800 rounded p-3 border border-gray-700">
          <div className="text-xs font-semibold text-gray-300 mb-2">Coverage by System</div>
          <div className="space-y-2">
            {nlTags.bySystem.map((sys) => (
              <div key={sys.system} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="text-xs text-gray-200">{sys.system}</div>
                  <div className={`text-xs px-2 py-0.5 rounded ${
                    sys.validated ? 'bg-green-900 text-green-300' : 'bg-yellow-900 text-yellow-300'
                  }`}>
                    {sys.validated ? '✓' : '⚠'}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-24 bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-blue-500 h-2 rounded-full"
                      style={{ width: `${sys.coverage * 100}%` }}
                    />
                  </div>
                  <div className="text-xs text-gray-400 w-12 text-right">{(sys.coverage * 100).toFixed(0)}%</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div>
          <div className="text-xs font-semibold text-gray-300 mb-2">Recent Tags</div>
          <div className="space-y-2">
            {nlTags.recentTags.map((tag) => (
              <div key={tag.id} className="bg-gray-800 rounded p-2 border border-gray-700">
                <div className="flex items-center justify-between mb-1">
                  <div className="text-xs font-mono text-gray-200">{tag.id}</div>
                  <div className="text-xs text-green-400">Conf: {(tag.confidence * 100).toFixed(0)}%</div>
                </div>
                <div className="text-xs text-gray-400 mb-1">{tag.description}</div>
                <div className="text-xs text-gray-500">{tag.system}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

// Documentation Explorer Panel
export const DocumentationExplorerPanel: React.FC = () => {
  const docs = {
    totalDocs: 1247,
    byLevel: [
      { level: 'L0', name: 'Executive Summary', count: 89, avgWords: 100 },
      { level: 'L1', name: 'Overview', count: 156, avgWords: 500 },
      { level: 'L2', name: 'Architecture', count: 234, avgWords: 2000 },
      { level: 'L3', name: 'Detailed', count: 178, avgWords: 10000 },
      { level: 'L4', name: 'Complete', count: 45, avgWords: 15000 }
    ],
    recentDocs: [
      { name: 'DEBUG_INFRASTRUCTURE.md', level: 'L2', system: 'Architecture', confidence: 0.95 },
      { name: 'HIERARCHICAL_CODE_EXPLORER.md', level: 'L1', system: 'UI/UX', confidence: 0.88 },
      { name: 'AIM_OS_STRUCTURE_PANELS.md', level: 'L0', system: 'Overview', confidence: 0.92 }
    ]
  }

  return (
    <div className="h-full flex flex-col">
      <div className="p-3 border-b border-gray-700">
        <div className="text-xs font-semibold text-purple-400 mb-1">Documentation Explorer</div>
        <div className="text-xs text-gray-500">L0-L4 Documentation • {docs.totalDocs} Documents • HHNI-Indexed</div>
      </div>
      <div className="flex-1 overflow-auto p-3 space-y-4">
        <div className="bg-gray-800 rounded p-3 border border-gray-700">
          <div className="text-xs font-semibold text-gray-300 mb-2">Documentation by Level</div>
          <div className="space-y-2">
            {docs.byLevel.map((level) => (
              <div key={level.level} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="text-xs font-medium text-gray-200">{level.level}</div>
                  <div className="text-xs text-gray-400">{level.name}</div>
                </div>
                <div className="flex items-center gap-4 text-xs text-gray-500">
                  <span>{level.count} docs</span>
                  <span>~{level.avgWords} words</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div>
          <div className="text-xs font-semibold text-gray-300 mb-2">Recent Documents</div>
          <div className="space-y-2">
            {docs.recentDocs.map((doc, idx) => (
              <div key={idx} className="bg-gray-800 rounded p-2 border border-gray-700">
                <div className="flex items-center justify-between mb-1">
                  <div className="text-xs font-medium text-gray-200">{doc.name}</div>
                  <div className="text-xs text-green-400">Conf: {(doc.confidence * 100).toFixed(0)}%</div>
                </div>
                <div className="flex items-center gap-2 text-xs text-gray-500">
                  <span>{doc.level}</span>
                  <span>•</span>
                  <span>{doc.system}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

