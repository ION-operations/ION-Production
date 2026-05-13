/**
 * Provenance Popover Component
 * Displays evidence anchor with claim, source, witness hash, and VIF confidence
 * 
 * Phase 2 Week 10: Evidence Inspector UI
 * Day 1-2: Provenance Popover Component
 */

import React from 'react'
import { X, FileText, Code, MessageSquare, TestTube, Link2, Shield, ExternalLink } from 'lucide-react'
import { ConfidenceDisplay } from './ConfidenceDisplay'
import type { EvidenceItem, ConfidenceScore } from '../../types/aetherChatTypes'

export interface EvidenceAnchor {
  claim: string // The claim being made
  sourceId: string // CMC atom ID or file path
  sourcePreview: string // Preview of source content
  witnessHash?: string // VIF witness hash for verification
  evidenceItem: EvidenceItem
  confidence: ConfidenceScore
}

export interface ProvenancePopoverProps {
  anchor: EvidenceAnchor
  onClose: () => void
  onViewSource?: (sourceId: string) => void
  className?: string
}

export const ProvenancePopover: React.FC<ProvenancePopoverProps> = ({
  anchor,
  onClose,
  onViewSource,
  className = ''
}) => {
  const { claim, sourceId, sourcePreview, witnessHash, evidenceItem, confidence } = anchor

  const getIcon = () => {
    switch (evidenceItem.kind) {
      case 'file_snippet':
        return <Code className="w-4 h-4" />
      case 'doc_snippet':
        return <FileText className="w-4 h-4" />
      case 'prior_msg':
        return <MessageSquare className="w-4 h-4" />
      case 'test_output':
        return <TestTube className="w-4 h-4" />
      default:
        return <Link2 className="w-4 h-4" />
    }
  }

  const getKindLabel = () => {
    switch (evidenceItem.kind) {
      case 'file_snippet':
        return 'Code Snippet'
      case 'doc_snippet':
        return 'Documentation'
      case 'prior_msg':
        return 'Prior Message'
      case 'test_output':
        return 'Test Output'
      default:
        return 'Evidence'
    }
  }

  const getTrustColor = (trust: number) => {
    if (trust >= 0.8) return 'text-green-400'
    if (trust >= 0.6) return 'text-yellow-400'
    return 'text-red-400'
  }

  return (
    <div
      className={`fixed inset-0 z-50 flex items-center justify-center bg-black/50 ${className}`}
      onClick={onClose}
    >
      <div
        className="bg-gray-900 border border-gray-700 rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[80vh] overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-700">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-600/20 rounded-lg">
              {getIcon()}
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-200">Evidence Provenance</h3>
              <p className="text-sm text-gray-400">{getKindLabel()}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded hover:bg-gray-700 transition-colors"
            aria-label="Close"
          >
            <X className="w-5 h-5 text-gray-400" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {/* Claim */}
          <div>
            <h4 className="text-sm font-medium text-gray-400 mb-2">Claim</h4>
            <p className="text-gray-200 bg-gray-800 p-3 rounded border border-gray-700">
              {claim}
            </p>
          </div>

          {/* Confidence & Trust */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <h4 className="text-sm font-medium text-gray-400 mb-2">VIF Confidence</h4>
              <ConfidenceDisplay
                confidence={confidence.value}
                confidenceBand={confidence.band === 'S' ? 'A' : confidence.band}
                size="sm"
              />
            </div>
            <div>
              <h4 className="text-sm font-medium text-gray-400 mb-2">Trust Score</h4>
              <div className="flex items-center gap-2">
                <span className={`text-lg font-semibold ${getTrustColor(evidenceItem.trust)}`}>
                  {(evidenceItem.trust * 100).toFixed(0)}%
                </span>
                <Shield className={`w-4 h-4 ${getTrustColor(evidenceItem.trust)}`} />
              </div>
            </div>
          </div>

          {/* Source Preview */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-medium text-gray-400">Source Preview</h4>
              {onViewSource && (
                <button
                  onClick={() => onViewSource(sourceId)}
                  className="flex items-center gap-1 text-sm text-blue-400 hover:text-blue-300 transition-colors"
                >
                  <ExternalLink className="w-3 h-3" />
                  View Full Source
                </button>
              )}
            </div>
            <div className="bg-gray-800 border border-gray-700 rounded p-3">
              {evidenceItem.kind === 'file_snippet' ? (
                <pre className="text-sm text-gray-300 font-mono overflow-x-auto">
                  <code>{sourcePreview}</code>
                </pre>
              ) : (
                <p className="text-sm text-gray-300 whitespace-pre-wrap">{sourcePreview}</p>
              )}
            </div>
            {evidenceItem.location && (
              <p className="text-xs text-gray-500 mt-1">
                Location: {evidenceItem.location}
              </p>
            )}
            {evidenceItem.timestamp && (
              <p className="text-xs text-gray-500">
                Timestamp: {new Date(evidenceItem.timestamp).toLocaleString()}
              </p>
            )}
          </div>

          {/* Witness Hash (VIF Verification) */}
          {witnessHash && (
            <div>
              <h4 className="text-sm font-medium text-gray-400 mb-2">VIF Witness Hash</h4>
              <div className="bg-gray-800 border border-gray-700 rounded p-3">
                <code className="text-xs text-gray-400 font-mono break-all">
                  {witnessHash}
                </code>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Cryptographic hash for deterministic replay verification
              </p>
            </div>
          )}

          {/* Evidence Item Details */}
          <div>
            <h4 className="text-sm font-medium text-gray-400 mb-2">Evidence Details</h4>
            <div className="bg-gray-800 border border-gray-700 rounded p-3 space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Evidence ID:</span>
                <code className="text-gray-300 font-mono text-xs">{evidenceItem.id}</code>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Source ID:</span>
                <code className="text-gray-300 font-mono text-xs">{sourceId}</code>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Type:</span>
                <span className="text-gray-300">{getKindLabel()}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="border-t border-gray-700 p-4 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-gray-200 rounded transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}

