/**
 * NL Tag Panel Component
 * Main panel for NL tag management and validation
 * 
 * Created: 2025-10-31
 * Agent: Aether (based on Sonnet's UI integration plan)
 */

import React, { useState, useEffect } from 'react'
import { Tag, FileText, RefreshCw, CheckCircle, AlertCircle, XCircle, Loader } from 'lucide-react'
import AIMOSService from '../services/AIMOSService'

const aimosService = new AIMOSService()

interface NLTag {
  id: string
  file_path: string
  line_start: number
  line_end: number
  tag_text: string
  code_block?: string
  language: string
  accuracy_score?: number
  validation_status: string
  canonical_id?: string
  syntax_ref?: string
  dependencies?: string[]
  structural_match_score?: number
  combined_score?: number
}

export const NLTagPanel: React.FC = () => {
  const [tags, setTags] = useState<NLTag[]>([])
  const [filePath, setFilePath] = useState<string>('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selectedTagId, setSelectedTagId] = useState<string | null>(null)

  // Load tags for current file
  const loadTags = async (path: string) => {
    if (!path) return
    
    setLoading(true)
    setError(null)
    
    try {
      const fetchedTags = await aimosService.getNLTags(path)
      setTags(fetchedTags as NLTag[])
    } catch (err: any) {
      setError(err.message || 'Failed to load tags')
      console.error('Failed to load NL tags:', err)
    } finally {
      setLoading(false)
    }
  }

  const getStatusIcon = (tag: NLTag) => {
    const score = tag.combined_score ?? tag.structural_match_score ?? tag.accuracy_score ?? 0
    
    if (score >= 0.95) {
      return <CheckCircle className="w-4 h-4 text-green-400" />
    } else if (score >= 0.70) {
      return <AlertCircle className="w-4 h-4 text-yellow-400" />
    } else {
      return <XCircle className="w-4 h-4 text-red-400" />
    }
  }

  const getStatusColor = (tag: NLTag) => {
    const score = tag.combined_score ?? tag.structural_match_score ?? tag.accuracy_score ?? 0
    
    if (score >= 0.95) {
      return 'border-green-500 bg-green-900/20'
    } else if (score >= 0.70) {
      return 'border-yellow-500 bg-yellow-900/20'
    } else {
      return 'border-red-500 bg-red-900/20'
    }
  }

  return (
    <div className="h-full flex flex-col bg-gray-900 text-white">
      {/* Header */}
      <div className="p-4 border-b border-gray-700">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-3">
            <Tag className="w-6 h-6 text-blue-400" />
            <div>
              <h1 className="text-xl font-bold">NL Tags</h1>
              <p className="text-sm text-gray-400">Natural language tag management and validation</p>
            </div>
          </div>
          <button
            onClick={() => filePath && loadTags(filePath)}
            disabled={!filePath || loading}
            className="p-2 bg-gray-700 hover:bg-gray-600 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>

        {/* File Selector */}
        <div className="flex items-center gap-2">
          <FileText className="w-4 h-4 text-gray-400" />
          <input
            type="text"
            value={filePath}
            onChange={(e) => setFilePath(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                loadTags(filePath)
              }
            }}
            placeholder="Enter file path (e.g., packages/vif/kappa_gate.py)"
            className="flex-1 bg-gray-700 text-white px-3 py-2 rounded-lg border border-gray-600 focus:outline-none focus:border-blue-500"
          />
          <button
            onClick={() => loadTags(filePath)}
            disabled={!filePath || loading}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg"
          >
            Load Tags
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4">
        {error && (
          <div className="mb-4 p-3 bg-red-900/30 border border-red-500 rounded-lg">
            <div className="text-red-400 font-semibold">Error</div>
            <div className="text-sm text-gray-300">{error}</div>
          </div>
        )}

        {loading && (
          <div className="flex items-center justify-center py-8">
            <Loader className="w-6 h-6 animate-spin text-blue-400" />
            <span className="ml-2 text-gray-400">Loading tags...</span>
          </div>
        )}

        {!loading && !error && tags.length === 0 && filePath && (
          <div className="flex items-center justify-center py-8 text-gray-400">
            <Tag className="w-6 h-6 mr-2" />
            <span>No tags found for this file</span>
          </div>
        )}

        {!loading && !error && tags.length === 0 && !filePath && (
          <div className="flex items-center justify-center py-8 text-gray-400">
            <div className="text-center">
              <FileText className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p>Enter a file path to load NL tags</p>
            </div>
          </div>
        )}

        {!loading && !error && tags.length > 0 && (
          <div className="space-y-3">
            <div className="text-sm text-gray-400 mb-2">
              Found {tags.length} tag{tags.length !== 1 ? 's' : ''}
            </div>
            {tags.map((tag) => (
              <div
                key={tag.id}
                onClick={() => setSelectedTagId(tag.id === selectedTagId ? null : tag.id)}
                className={`p-4 rounded-lg border cursor-pointer transition-colors ${
                  selectedTagId === tag.id
                    ? 'border-blue-500 bg-blue-900/20'
                    : getStatusColor(tag)
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      {getStatusIcon(tag)}
                      <span className="font-semibold">
                        {tag.canonical_id || tag.tag_text.split('|')[0]?.trim() || 'Untagged'}
                      </span>
                      {tag.canonical_id && (
                        <span className="text-xs text-gray-400">
                          ({tag.tag_text.split('|')[1]?.trim() || 'No description'})
                        </span>
                      )}
                    </div>
                    
                    {tag.canonical_id && (
                      <div className="text-sm text-gray-300 mb-2">
                        {tag.tag_text.split('|')[1]?.trim() || tag.tag_text}
                      </div>
                    )}

                    <div className="flex items-center gap-4 text-xs text-gray-400">
                      <span>Lines: {tag.line_start}-{tag.line_end}</span>
                      {tag.language && <span>Language: {tag.language}</span>}
                      {tag.structural_match_score !== undefined && (
                        <span>Structural: {(tag.structural_match_score * 100).toFixed(0)}%</span>
                      )}
                      {tag.combined_score !== undefined && (
                        <span className="font-semibold">
                          Combined: {(tag.combined_score * 100).toFixed(0)}%
                        </span>
                      )}
                      {tag.accuracy_score !== undefined && (
                        <span>Accuracy: {(tag.accuracy_score * 100).toFixed(0)}%</span>
                      )}
                    </div>

                    {tag.syntax_ref && (
                      <div className="mt-2 text-xs text-gray-400">
                        <span className="font-semibold">SYNTAX_REF:</span> {tag.syntax_ref}
                      </div>
                    )}

                    {tag.dependencies && tag.dependencies.length > 0 && (
                      <div className="mt-2 text-xs text-gray-400">
                        <span className="font-semibold">Dependencies:</span> {tag.dependencies.join(', ')}
                      </div>
                    )}

                    {selectedTagId === tag.id && tag.code_block && (
                      <div className="mt-3 p-2 bg-gray-800 rounded border border-gray-700">
                        <div className="text-xs text-gray-400 mb-1">Code Block:</div>
                        <pre className="text-xs text-gray-300 overflow-x-auto">
                          {tag.code_block}
                        </pre>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default NLTagPanel

