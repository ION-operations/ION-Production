/**
 * Evidence Panel Component
 * Comprehensive evidence display with filtering, sorting, and chain visualization
 * 
 * Phase 5 Week 21: Evidence Panel Integration
 */

import React, { useState, useMemo, useCallback } from 'react'
import { FileText, MessageSquare, TestTube, Link2, Filter, ArrowUpDown, ChevronDown, ChevronUp, Network, Eye, EyeOff, X } from 'lucide-react'
import { ProvenancePopover, type EvidenceAnchor } from './ProvenancePopover'
import type { EvidenceItem, EvidencePack, EvidenceChain } from '../../types/aetherChatTypes'

export interface EvidencePanelProps {
  evidencePack: EvidencePack
  evidenceChain?: EvidenceChain
  onItemClick?: (item: EvidenceItem) => void
  onViewSource?: (sourceId: string) => void
  showXRayMode?: boolean
  onToggleXRay?: () => void
  className?: string
  isExpanded?: boolean
  onToggleExpand?: () => void
}

type SortOption = 'trust' | 'recency' | 'kind' | 'relevance'
type FilterOption = 'all' | 'file_snippet' | 'doc_snippet' | 'prior_msg' | 'test_output' | 'other'

export const EvidencePanel: React.FC<EvidencePanelProps> = ({
  evidencePack,
  evidenceChain,
  onItemClick,
  onViewSource,
  showXRayMode = false,
  onToggleXRay,
  className = '',
  isExpanded = true,
  onToggleExpand
}) => {
  const [sortBy, setSortBy] = useState<SortOption>('trust')
  const [filterBy, setFilterBy] = useState<FilterOption>('all')
  const [selectedItem, setSelectedItem] = useState<EvidenceItem | null>(null)
  const [showProvenance, setShowProvenance] = useState(false)
  const [selectedAnchor, setSelectedAnchor] = useState<EvidenceAnchor | null>(null)

  // Filter and sort evidence items
  const filteredAndSortedItems = useMemo(() => {
    let items = [...evidencePack.items]

    // Filter by kind
    if (filterBy !== 'all') {
      items = items.filter(item => item.kind === filterBy)
    }

    // Sort
    items.sort((a, b) => {
      switch (sortBy) {
        case 'trust':
          return b.trust - a.trust
        case 'recency':
          const aTime = a.timestamp ? new Date(a.timestamp).getTime() : 0
          const bTime = b.timestamp ? new Date(b.timestamp).getTime() : 0
          return bTime - aTime
        case 'kind':
          return a.kind.localeCompare(b.kind)
        case 'relevance':
          // Use trust as proxy for relevance if not available
          return b.trust - a.trust
        default:
          return 0
      }
    })

    return items
  }, [evidencePack.items, sortBy, filterBy])

  // Get icon for evidence kind
  const getIcon = useCallback((kind: EvidenceItem['kind']) => {
    switch (kind) {
      case 'file_snippet':
        return <FileText className="w-4 h-4 text-blue-400" />
      case 'doc_snippet':
        return <FileText className="w-4 h-4 text-green-400" />
      case 'prior_msg':
        return <MessageSquare className="w-4 h-4 text-yellow-400" />
      case 'test_output':
        return <TestTube className="w-4 h-4 text-purple-400" />
      default:
        return <Link2 className="w-4 h-4 text-gray-400" />
    }
  }, [])

  // Get trust badge color
  const getTrustBadgeColor = useCallback((trust: number) => {
    if (trust >= 0.8) return 'bg-green-900/30 text-green-400'
    if (trust >= 0.6) return 'bg-yellow-900/30 text-yellow-400'
    return 'bg-red-900/30 text-red-400'
  }, [])

  // Handle item click
  const handleItemClick = useCallback((item: EvidenceItem) => {
    setSelectedItem(item)
    if (onItemClick) {
      onItemClick(item)
    }
  }, [onItemClick])

  // Handle provenance view
  const handleViewProvenance = useCallback((item: EvidenceItem, event: React.MouseEvent) => {
    event.stopPropagation()
    
    // Create evidence anchor for provenance popover
    const anchor: EvidenceAnchor = {
      claim: evidenceChain?.claims.find(c => c.evidenceIds.includes(item.id))?.text || 'Unknown claim',
      sourceId: item.sourceId,
      sourcePreview: item.excerpt,
      witnessHash: item.location, // Use location as witness hash proxy
      evidenceItem: item,
      confidence: {
        value: item.trust,
        band: item.trust >= 0.8 ? 'A' : item.trust >= 0.6 ? 'B' : 'C',
        sources: 1,
        reasoning: 'Evidence trust score'
      }
    }
    
    setSelectedAnchor(anchor)
    setShowProvenance(true)
  }, [evidenceChain])

  // Statistics
  const stats = useMemo(() => {
    const total = evidencePack.items.length
    const byKind = evidencePack.items.reduce((acc, item) => {
      acc[item.kind] = (acc[item.kind] || 0) + 1
      return acc
    }, {} as Record<string, number>)
    const avgTrust = total > 0
      ? evidencePack.items.reduce((sum, item) => sum + item.trust, 0) / total
      : 0
    const highTrust = evidencePack.items.filter(item => item.trust >= 0.8).length

    return { total, byKind, avgTrust, highTrust }
  }, [evidencePack.items])

  return (
    <div className={`evidence-panel ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between p-3 border-b border-gray-700">
        <div className="flex items-center gap-2">
          <FileText className="w-4 h-4 text-gray-400" />
          <span className="text-sm font-medium text-gray-300">
            Evidence ({stats.total})
          </span>
          {evidencePack.totalTrust !== undefined && (
            <span className={`text-xs px-1.5 py-0.5 rounded ${getTrustBadgeColor(evidencePack.totalTrust)}`}>
              {(evidencePack.totalTrust * 100).toFixed(0)}% overall
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {onToggleXRay && (
            <button
              onClick={onToggleXRay}
              className={`p-1 rounded hover:bg-gray-700 ${showXRayMode ? 'text-blue-400' : 'text-gray-400'}`}
              title="Toggle X-Ray Mode"
            >
              {showXRayMode ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
            </button>
          )}
          {onToggleExpand && (
            <button
              onClick={onToggleExpand}
              className="p-1 rounded hover:bg-gray-700 text-gray-400"
            >
              {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>
          )}
        </div>
      </div>

      {isExpanded && (
        <>
          {/* Controls */}
          <div className="p-3 border-b border-gray-700 space-y-2">
            {/* Filter */}
            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-gray-400" />
              <div className="flex gap-1 flex-wrap">
                {(['all', 'file_snippet', 'doc_snippet', 'prior_msg', 'test_output'] as FilterOption[]).map(option => (
                  <button
                    key={option}
                    onClick={() => setFilterBy(option)}
                    className={`px-2 py-0.5 rounded text-xs ${
                      filterBy === option
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                    }`}
                  >
                    {option === 'all' ? 'All' : option.replace('_', ' ')}
                    {option !== 'all' && stats.byKind[option] && (
                      <span className="ml-1">({stats.byKind[option]})</span>
                    )}
                  </button>
                ))}
              </div>
            </div>

            {/* Sort */}
            <div className="flex items-center gap-2">
              <ArrowUpDown className="w-4 h-4 text-gray-400" />
              <span className="text-xs text-gray-400">Sort by:</span>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as SortOption)}
                className="px-2 py-0.5 rounded text-xs bg-gray-700 text-gray-300 border border-gray-600"
              >
                <option value="trust">Trust Score</option>
                <option value="recency">Most Recent</option>
                <option value="kind">Kind</option>
                <option value="relevance">Relevance</option>
              </select>
            </div>

            {/* Stats */}
            <div className="flex items-center gap-4 text-xs text-gray-400">
              <span>Avg Trust: {(stats.avgTrust * 100).toFixed(0)}%</span>
              <span>High Trust: {stats.highTrust}</span>
              {evidencePack.completeness && (
                <span>Completeness: {(evidencePack.completeness.completenessScore * 100).toFixed(0)}%</span>
              )}
            </div>
          </div>

          {/* Evidence Items */}
          <div className="p-3 space-y-2 max-h-96 overflow-y-auto">
            {filteredAndSortedItems.length === 0 ? (
              <div className="text-center text-sm text-gray-500 py-8">
                No evidence items match the current filter
              </div>
            ) : (
              filteredAndSortedItems.map((item) => (
                <div
                  key={item.id}
                  onClick={() => handleItemClick(item)}
                  className={`bg-gray-900 rounded p-3 border border-gray-700 cursor-pointer hover:border-blue-500 transition-colors ${
                    selectedItem?.id === item.id ? 'border-blue-500 bg-gray-800' : ''
                  }`}
                >
                  <div className="flex items-start gap-2 mb-2">
                    {getIcon(item.kind)}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-medium text-gray-300 truncate">
                          {item.sourceId}
                        </span>
                        <div className="flex items-center gap-2">
                          <span className={`text-xs px-1.5 py-0.5 rounded ${getTrustBadgeColor(item.trust)}`}>
                            {(item.trust * 100).toFixed(0)}%
                          </span>
                          <button
                            onClick={(e) => handleViewProvenance(item, e)}
                            className="p-1 rounded hover:bg-gray-700 text-gray-400"
                            title="View Provenance"
                          >
                            <Network className="w-3 h-3" />
                          </button>
                        </div>
                      </div>
                      <p className="text-xs text-gray-400 line-clamp-3 mb-1">
                        {item.excerpt}
                      </p>
                      {item.location && (
                        <span className="text-xs text-gray-500">
                          Location: {item.location}
                        </span>
                      )}
                      {item.timestamp && (
                        <span className="text-xs text-gray-500 ml-2">
                          {new Date(item.timestamp).toLocaleString()}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Evidence Chain Visualization */}
          {evidenceChain && evidenceChain.claims.length > 0 && (
            <div className="p-3 border-t border-gray-700">
              <div className="flex items-center gap-2 mb-2">
                <Network className="w-4 h-4 text-gray-400" />
                <span className="text-sm font-medium text-gray-300">Evidence Chain</span>
              </div>
              <div className="space-y-2">
                {evidenceChain.claims.map((claim, index) => (
                  <div key={index} className="bg-gray-900 rounded p-2 border border-gray-700">
                    <div className="text-xs font-medium text-gray-300 mb-1">
                      Claim {index + 1}: {claim.text}
                    </div>
                    <div className="text-xs text-gray-400">
                      Supported by {claim.evidenceIds.length} evidence item(s)
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}

      {/* Provenance Popover */}
      {showProvenance && selectedAnchor && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="relative">
            <ProvenancePopover
              anchor={selectedAnchor}
              onClose={() => {
                setShowProvenance(false)
                setSelectedAnchor(null)
              }}
              onViewSource={onViewSource}
            />
          </div>
        </div>
      )}
    </div>
  )
}

