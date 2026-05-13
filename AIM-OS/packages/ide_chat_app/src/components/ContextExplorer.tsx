import React, { useState } from 'react'
import { 
  Search, 
  Network, 
  TreePine,
  Layers,
  ArrowRight,
  Sparkles
} from 'lucide-react'

interface ContextNode {
  id: string
  type: 'root' | 'level' | 'leaf'
  label: string
  relevance: number
  children: ContextNode[]
}

export const ContextExplorer: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('')
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set(['root']))

  const [contextTree] = useState<ContextNode>({
    id: 'root',
    type: 'root',
    label: 'Knowledge Base',
    relevance: 1.0,
    children: [
      {
        id: 'l1-ide',
        type: 'level',
        label: 'IDE Development',
        relevance: 0.95,
        children: [
          { id: 'leaf-1', type: 'leaf', label: 'Code + Docs Viewer', relevance: 0.92, children: [] },
          { id: 'leaf-2', type: 'leaf', label: 'Dual AI Chat System', relevance: 0.88, children: [] },
          { id: 'leaf-3', type: 'leaf', label: 'Monaco Editor Integration', relevance: 0.85, children: [] }
        ]
      },
      {
        id: 'l1-aimos',
        type: 'level',
        label: 'AIM-OS Systems',
        relevance: 0.90,
        children: [
          { id: 'leaf-4', type: 'leaf', label: 'CMC Memory Storage', relevance: 0.93, children: [] },
          { id: 'leaf-5', type: 'leaf', label: 'HHNI Context Search', relevance: 0.87, children: [] },
          { id: 'leaf-6', type: 'leaf', label: 'VIF Confidence Tracking', relevance: 0.91, children: [] }
        ]
      },
      {
        id: 'l1-architecture',
        type: 'level',
        label: 'System Architecture',
        relevance: 0.88,
        children: [
          { id: 'leaf-7', type: 'leaf', label: 'Microservices Design', relevance: 0.86, children: [] },
          { id: 'leaf-8', type: 'leaf', label: 'API Gateway', relevance: 0.84, children: [] }
        ]
      }
    ]
  })

  const toggleNode = (nodeId: string) => {
    const newExpanded = new Set(expandedNodes)
    if (newExpanded.has(nodeId)) {
      newExpanded.delete(nodeId)
    } else {
      newExpanded.add(nodeId)
    }
    setExpandedNodes(newExpanded)
  }

  const renderNode = (node: ContextNode, level: number = 0) => {
    const isExpanded = expandedNodes.has(node.id)
    const hasChildren = node.children && node.children.length > 0
    
    return (
      <div key={node.id} className="select-none">
        {/* Node */}
        <div
          className={`flex items-center gap-2 py-1.5 px-2 hover:bg-gray-700/50 rounded cursor-pointer ${
            level === 0 ? 'font-semibold' : ''
          }`}
          onClick={() => hasChildren && toggleNode(node.id)}
          style={{ marginLeft: `${level * 16}px` }}
        >
          {/* Expand/Collapse Icon */}
          {hasChildren ? (
            <ArrowRight className={`w-3 h-3 transition-transform ${isExpanded ? 'rotate-90' : ''}`} />
          ) : (
            <div className="w-3" />
          )}
          
          {/* Node Type Icon */}
          {node.type === 'root' && <TreePine className="w-4 h-4 text-green-400" />}
          {node.type === 'level' && <Layers className="w-4 h-4 text-blue-400" />}
          {node.type === 'leaf' && <Sparkles className="w-4 h-4 text-purple-400" />}
          
          {/* Label */}
          <span className="text-sm text-gray-200 flex-1">{node.label}</span>
          
          {/* Relevance Score */}
          <span className="text-xs text-gray-400">{(node.relevance * 100).toFixed(0)}%</span>
        </div>

        {/* Children */}
        {isExpanded && hasChildren && (
          <div>
            {node.children.map(child => renderNode(child, level + 1))}
          </div>
        )}
      </div>
    )
  }

  const filteredTree = searchQuery 
    ? {
        ...contextTree,
        children: contextTree.children.filter(child => 
          child.label.toLowerCase().includes(searchQuery.toLowerCase()) ||
          child.children.some(grandchild => 
            grandchild.label.toLowerCase().includes(searchQuery.toLowerCase())
          )
        )
      }
    : contextTree

  return (
    <div className="h-full bg-gray-800 flex flex-col">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-700 flex items-center gap-2">
        <Network className="w-5 h-5 text-green-400" />
        <div>
          <div className="text-white text-sm font-semibold">Context Explorer</div>
          <div className="text-xs text-gray-500">HHNI Hierarchical Context</div>
        </div>
      </div>

      {/* Search */}
      <div className="p-3 border-b border-gray-700">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search context..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-gray-700 text-white text-sm px-9 py-2 rounded focus:outline-none focus:ring-2 focus:ring-green-500"
          />
        </div>
      </div>

      {/* Tree View */}
      <div className="flex-1 overflow-y-auto p-2">
        {renderNode(filteredTree)}
      </div>

      {/* Footer Info */}
      <div className="p-3 border-t border-gray-700">
        <div className="text-xs text-gray-400">
          Hierarchical context with semantic relationships
        </div>
      </div>
    </div>
  )
}
