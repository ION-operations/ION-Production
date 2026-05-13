/**
 * Citation Pill Component
 * Displays citation markers in markdown with VIF badges and hover interactions
 * 
 * Phase 2 Week 10: Evidence Inspector UI
 * Day 3-4: Citation System
 */

import React, { useState, useRef } from 'react'
import { FileText, Code, MessageSquare, TestTube, Link2, ChevronRight } from 'lucide-react'
import { ProvenancePopover, type EvidenceAnchor } from './ProvenancePopover'
import type { EvidenceItem, ConfidenceScore } from '../../types/aetherChatTypes'

export interface CitationMarker {
  id: string // Citation ID (e.g., "[1]", "[E1]")
  evidenceId: string // Evidence item ID
  position: number // Character position in text
  length: number // Length of citation marker
}

export interface CitationPillProps {
  marker: CitationMarker
  evidenceItem: EvidenceItem
  confidence: ConfidenceScore
  claim?: string // Optional claim text for provenance
  sourcePreview?: string // Optional source preview
  witnessHash?: string // Optional VIF witness hash
  onViewSource?: (sourceId: string) => void
  className?: string
}

export const CitationPill: React.FC<CitationPillProps> = ({
  marker,
  evidenceItem,
  confidence,
  claim,
  sourcePreview,
  witnessHash,
  onViewSource,
  className = ''
}) => {
  const [isHovered, setIsHovered] = useState(false)
  const [showPopover, setShowPopover] = useState(false)
  const pillRef = useRef<HTMLSpanElement>(null)

  const getIcon = () => {
    switch (evidenceItem.kind) {
      case 'file_snippet':
        return <Code className="w-3 h-3" />
      case 'doc_snippet':
        return <FileText className="w-3 h-3" />
      case 'prior_msg':
        return <MessageSquare className="w-3 h-3" />
      case 'test_output':
        return <TestTube className="w-3 h-3" />
      default:
        return <Link2 className="w-3 h-3" />
    }
  }

  const getTrustColor = (trust: number) => {
    if (trust >= 0.8) return 'border-green-500 bg-green-500/10 text-green-400'
    if (trust >= 0.6) return 'border-yellow-500 bg-yellow-500/10 text-yellow-400'
    return 'border-red-500 bg-red-500/10 text-red-400'
  }

  const handleClick = () => {
    setShowPopover(true)
  }

  const handleClosePopover = () => {
    setShowPopover(false)
  }

  // Build evidence anchor for popover
  const evidenceAnchor: EvidenceAnchor | null = claim
    ? {
        claim,
        sourceId: evidenceItem.sourceId,
        sourcePreview: sourcePreview || evidenceItem.excerpt,
        witnessHash,
        evidenceItem,
        confidence
      }
    : null

  return (
    <>
      <span
        ref={pillRef}
        className={`inline-flex items-center gap-1 px-2 py-0.5 rounded border cursor-pointer transition-all ${getTrustColor(evidenceItem.trust)} ${isHovered ? 'scale-105 shadow-lg' : ''} ${className}`}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        onClick={handleClick}
        title={`${evidenceItem.kind}: ${evidenceItem.excerpt.substring(0, 50)}...`}
      >
        {getIcon()}
        <span className="text-xs font-medium">{marker.id}</span>
        <ChevronRight className="w-3 h-3 opacity-50" />
      </span>

      {/* Popover */}
      {showPopover && evidenceAnchor && (
        <ProvenancePopover
          anchor={evidenceAnchor}
          onClose={handleClosePopover}
          onViewSource={onViewSource}
        />
      )}
    </>
  )
}

/**
 * Citation Parser
 * Parses markdown text for citation markers and creates CitationMarker objects
 */
export function parseCitations(text: string): CitationMarker[] {
  const citations: CitationMarker[] = []
  
  // Pattern: [1], [E1], [citation:evidenceId], etc.
  const patterns = [
    /\[(\d+)\]/g, // [1], [2], etc.
    /\[E(\d+)\]/g, // [E1], [E2], etc.
    /\[citation:([a-zA-Z0-9_-]+)\]/g // [citation:evidenceId]
  ]

  patterns.forEach((pattern) => {
    let match
    while ((match = pattern.exec(text)) !== null) {
      citations.push({
        id: match[0],
        evidenceId: match[1] || match[2] || '', // Extract ID from capture group
        position: match.index,
        length: match[0].length
      })
    }
  })

  // Sort by position
  citations.sort((a, b) => a.position - b.position)

  return citations
}

/**
 * Render text with citation pills
 */
export interface RenderTextWithCitationsProps {
  text: string
  citations: CitationMarker[]
  evidenceItems: Map<string, EvidenceItem>
  confidenceMap?: Map<string, ConfidenceScore>
  onViewSource?: (sourceId: string) => void
  className?: string
}

export const RenderTextWithCitations: React.FC<RenderTextWithCitationsProps> = ({
  text,
  citations,
  evidenceItems,
  confidenceMap = new Map(),
  onViewSource,
  className = ''
}) => {
  if (citations.length === 0) {
    return <span className={className}>{text}</span>
  }

  const parts: Array<{ text: string; isCitation: boolean; citation?: CitationMarker }> = []
  let lastIndex = 0

  citations.forEach((citation) => {
    // Add text before citation
    if (citation.position > lastIndex) {
      parts.push({
        text: text.substring(lastIndex, citation.position),
        isCitation: false
      })
    }

    // Add citation
    parts.push({
      text: text.substring(citation.position, citation.position + citation.length),
      isCitation: true,
      citation
    })

    lastIndex = citation.position + citation.length
  })

  // Add remaining text
  if (lastIndex < text.length) {
    parts.push({
      text: text.substring(lastIndex),
      isCitation: false
    })
  }

  return (
    <span className={className}>
      {parts.map((part, index) => {
        if (part.isCitation && part.citation) {
          const evidenceItem = evidenceItems.get(part.citation.evidenceId)
          const confidence = confidenceMap.get(part.citation.evidenceId) || {
            value: evidenceItem?.trust || 0.7,
            band: 'B' as const,
            reasoning: 'Default confidence'
          }

          if (!evidenceItem) {
            return <span key={index}>{part.text}</span>
          }

          return (
            <CitationPill
              key={index}
              marker={part.citation}
              evidenceItem={evidenceItem}
              confidence={confidence}
              onViewSource={onViewSource}
            />
          )
        }
        return <span key={index}>{part.text}</span>
      })}
    </span>
  )
}

