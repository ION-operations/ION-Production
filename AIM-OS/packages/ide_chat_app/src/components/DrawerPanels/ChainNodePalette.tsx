/**
 * Chain Node Palette Panel
 * Displays all available node types for adding to prompt chains
 */

import React, { useState, useMemo } from 'react'
import {
  Database, // CMC
  Search, // HHNI
  Shield, // VIF
  GitBranch, // APOE
  Network, // SEG
  CheckCircle, // SDF-CVF
  MessageSquare, // Prompt
  Code, // Code
  FileText, // Document
  Zap, // Action
  GitMerge, // Merge
  Repeat, // Loop
  Play, // Start
  Square, // End
  AlertTriangle, // Error
  Search as SearchIcon,
  Filter,
  Layers,
} from 'lucide-react'
import { NODE_TYPES_LIBRARY } from '../AgentManagementDashboard/PromptChainEditor'

interface ChainNodePaletteProps {
  onNodeSelect?: (nodeType: string, nodeConfig: any) => void
}

export const ChainNodePalette: React.FC<ChainNodePaletteProps> = ({
  onNodeSelect
}) => {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)

  // Categories for node types
  const categories = [
    { id: 'all', label: 'All Nodes', icon: Layers },
    { id: 'control', label: 'Control Flow', icon: GitMerge },
    { id: 'system', label: 'AIM-OS Systems', icon: Database },
    { id: 'prompt', label: 'Prompts & Actions', icon: MessageSquare },
    { id: 'quality', label: 'Quality Gates', icon: CheckCircle },
    { id: 'custom', label: 'Custom', icon: Code },
  ]

  // Filter nodes based on search and category
  const filteredNodes = useMemo(() => {
    return Object.entries(NODE_TYPES_LIBRARY).filter(([key, nodeConfig]) => {
      const matchesSearch = searchQuery === '' || 
                           nodeConfig.label.toLowerCase().includes(searchQuery.toLowerCase()) ||
                           nodeConfig.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
                           key.toLowerCase().includes(searchQuery.toLowerCase())
      
      const matchesCategory = selectedCategory === 'all' || selectedCategory === null || 
                              nodeConfig.category === selectedCategory
      
      return matchesSearch && matchesCategory
    })
  }, [searchQuery, selectedCategory])

  const handleNodeClick = (nodeType: string, nodeConfig: any) => {
    if (onNodeSelect) {
      onNodeSelect(nodeType, nodeConfig)
    }
    // Emit event for diagram editor to listen
    window.dispatchEvent(new CustomEvent('chain-node-selected', {
      detail: { nodeType, nodeConfig }
    }))
  }

  return (
    <div className="h-full flex flex-col bg-cursor-sidebar text-cursor-text" style={{ backgroundColor: '#252526' }}>
      {/* Header */}
      <div className="p-2 border-b border-cursor-border">
        <div className="flex items-center gap-1.5 mb-1.5">
          <Layers className="w-3.5 h-3.5 text-cursor-text-secondary" />
          <div className="text-xs font-semibold text-cursor-text" style={{ fontSize: '12px' }}>
            Node Palette
          </div>
        </div>
        <div className="relative mb-2">
          <SearchIcon className="absolute left-2 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-cursor-text-muted" />
          <input
            type="text"
            placeholder="Search nodes..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-cursor-input-bg text-cursor-text px-7 py-1 rounded border border-cursor-border focus:outline-none focus:border-cursor-status-bar cursor-input"
            style={{ fontSize: '11px' }}
          />
        </div>
        {/* Categories Filter */}
        <div className="flex flex-wrap gap-1">
          {categories.map(cat => {
            const Icon = cat.icon
            const isActive = selectedCategory === cat.id || (selectedCategory === null && cat.id === 'all')
            return (
              <button
                key={cat.id}
                onClick={() => setSelectedCategory(cat.id === 'all' ? null : cat.id)}
                className={`flex items-center gap-1 px-2 py-1 rounded transition-colors text-xs cursor-button ${
                  isActive 
                    ? 'bg-cursor-status-bar text-white' 
                    : 'bg-cursor-input-bg text-cursor-text-secondary hover:bg-cursor-hover'
                }`}
                style={{ fontSize: '10px' }}
              >
                <Icon className="w-3 h-3" />
                {cat.label}
              </button>
            )
          })}
        </div>
      </div>

      {/* Nodes List */}
      <div className="flex-1 overflow-y-auto p-2 cursor-scrollbar">
        {filteredNodes.length === 0 && (
          <div className="flex flex-col items-center justify-center p-8 text-center">
            <Layers className="w-12 h-12 text-cursor-text-secondary mb-2 opacity-50" />
            <p className="text-sm text-cursor-text-secondary mb-1">No nodes found</p>
            <p className="text-xs text-cursor-text-muted">
              Try adjusting your search or filters.
            </p>
          </div>
        )}
        <div className="space-y-1.5">
          {filteredNodes.map(([nodeType, nodeConfig]) => {
            const Icon = nodeConfig.icon
            return (
              <button
                key={nodeType}
                onClick={() => handleNodeClick(nodeType, nodeConfig)}
                className="w-full bg-cursor-input-bg hover:bg-cursor-hover rounded p-2 border border-cursor-border transition-all cursor-pointer cursor-list-item flex items-start gap-2 text-left"
                style={{ fontSize: '11px' }}
                title={nodeConfig.description}
              >
                {/* Node Icon */}
                <div 
                  className="w-6 h-6 rounded flex items-center justify-center shrink-0 flex-shrink-0"
                  style={{ backgroundColor: `${nodeConfig.color}20`, color: nodeConfig.color }}
                >
                  <Icon className="w-3.5 h-3.5" />
                </div>
                
                {/* Node Info */}
                <div className="flex-1 min-w-0">
                  <div className="font-semibold text-cursor-text" style={{ fontSize: '12px' }}>
                    {nodeConfig.label}
                  </div>
                  {nodeConfig.description && (
                    <div className="text-xs text-cursor-text-secondary mt-0.5 line-clamp-1">
                      {nodeConfig.description}
                    </div>
                  )}
                  {nodeConfig.operations && Array.isArray(nodeConfig.operations) && (
                    <div className="flex flex-wrap gap-1 mt-1">
                      {nodeConfig.operations.slice(0, 3).map((op: string) => (
                        <span
                          key={op}
                          className="px-1.5 py-0.5 text-[10px] rounded bg-cursor-bg text-cursor-text-secondary"
                          style={{ fontSize: '9px' }}
                        >
                          {op}
                        </span>
                      ))}
                      {nodeConfig.operations.length > 3 && (
                        <span className="text-xs text-cursor-text-muted" style={{ fontSize: '9px' }}>
                          +{nodeConfig.operations.length - 3}
                        </span>
                      )}
                    </div>
                  )}
                </div>
              </button>
            )
          })}
        </div>
      </div>

      {/* Footer */}
      <div className="p-2 border-t border-cursor-border">
        <div className="text-xs text-cursor-text-secondary text-center" style={{ fontSize: '10px' }}>
          {filteredNodes.length} node{filteredNodes.length !== 1 ? 's' : ''} available
        </div>
        <div className="text-xs text-cursor-text-muted text-center mt-1" style={{ fontSize: '9px' }}>
          Click to add to diagram
        </div>
      </div>
    </div>
  )
}

