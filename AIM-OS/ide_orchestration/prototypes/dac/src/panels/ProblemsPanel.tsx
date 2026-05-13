// Problems Panel - V2 Refactored with BasePanel
// Error tracking with VIF confidence bands, κ-gating, and SEG contradictions

import React, { useState } from 'react'
import { AlertTriangle, XCircle, Info, Shield, Brain, CheckCircle, Ban } from 'lucide-react'
import type { VIFWitness, SEGContradiction } from '../hooks/useAIMOS'

interface Problem {
  id: string
  type: 'error' | 'warning' | 'info' | 'vif_gate_failed' | 'seg_contradiction'
  severity: 'critical' | 'high' | 'medium' | 'low'
  message: string
  file: string
  line: number
  column?: number
  
  // VIF Integration
  vif_witness?: VIFWitness
  confidence_band?: 'A' | 'B' | 'C'
  kappa_gate_passed?: boolean
  kappa_threshold?: number
  task_criticality?: 'critical' | 'important' | 'routine' | 'low_stakes'
  
  // SEG Integration
  seg_contradiction?: SEGContradiction
  contradiction_score?: number
  
  // Metadata
  source: 'typescript' | 'vif' | 'seg' | 'cas'
  timestamp: string
}

const mockProblems: Problem[] = [
  {
    id: '1',
    type: 'error',
    severity: 'high',
    message: 'Type mismatch: expected string, got number',
    file: 'src/components/IDELayout.tsx',
    line: 42,
    column: 15,
    source: 'typescript',
    timestamp: new Date(Date.now() - 300000).toISOString(),
    vif_witness: {
      id: 'witness_1',
      model_id: 'gpt-4-turbo',
      prompt_hash: 'hash_abc123',
      prompt_tokens: 150,
      confidence_score: 0.95,
      confidence_band: 'A',
      task_criticality: 'routine',
      kappa_threshold: 0.70,
      kappa_gate_passed: true,
      created_at: new Date(Date.now() - 300000).toISOString()
    },
    confidence_band: 'A',
    kappa_gate_passed: true
  },
  {
    id: '2',
    type: 'warning',
    severity: 'low',
    message: 'Unused variable: unusedVar',
    file: 'src/hooks/useAIMOS.ts',
    line: 15,
    column: 8,
    source: 'typescript',
    timestamp: new Date(Date.now() - 600000).toISOString(),
    vif_witness: {
      id: 'witness_2',
      model_id: 'gpt-4-turbo',
      prompt_hash: 'hash_def456',
      prompt_tokens: 200,
      confidence_score: 0.85,
      confidence_band: 'B',
      task_criticality: 'routine',
      kappa_threshold: 0.70,
      kappa_gate_passed: true,
      created_at: new Date(Date.now() - 600000).toISOString()
    },
    confidence_band: 'B',
    kappa_gate_passed: true
  },
  {
    id: '3',
    type: 'seg_contradiction',
    severity: 'high',
    message: 'SEG Contradiction detected: conflicting information found',
    file: 'src/components/FileTree.tsx',
    line: 78,
    source: 'seg',
    timestamp: new Date(Date.now() - 900000).toISOString(),
    seg_contradiction: {
      id: 'contradiction_1',
      entity1_id: 'atom_123',
      entity2_id: 'atom_456',
      contradiction_type: 'logical_conflict',
      similarity: 0.85,
      confidence: 0.90,
      explanation: 'Conflicting information found between two atoms',
      resolved: false,
      detected_at: new Date(Date.now() - 900000).toISOString(),
      tags: ['logical', 'conflict']
    },
    contradiction_score: 0.90,
    vif_witness: {
      id: 'witness_3',
      model_id: 'gpt-4-turbo',
      prompt_hash: 'hash_ghi789',
      prompt_tokens: 180,
      confidence_score: 0.90,
      confidence_band: 'A',
      task_criticality: 'important',
      kappa_threshold: 0.85,
      kappa_gate_passed: true,
      created_at: new Date(Date.now() - 900000).toISOString()
    },
    confidence_band: 'A'
  },
  {
    id: '4',
    type: 'vif_gate_failed',
    severity: 'medium',
    message: 'VIF κ-gate failed: Confidence 0.65 below threshold 0.70 for routine task',
    file: 'src/panels/ContextWeb.tsx',
    line: 120,
    source: 'vif',
    timestamp: new Date(Date.now() - 1200000).toISOString(),
    vif_witness: {
      id: 'witness_4',
      model_id: 'gpt-4-turbo',
      prompt_hash: 'hash_jkl012',
      prompt_tokens: 220,
      confidence_score: 0.65,
      confidence_band: 'C',
      task_criticality: 'routine',
      kappa_threshold: 0.70,
      kappa_gate_passed: false,
      created_at: new Date(Date.now() - 1200000).toISOString()
    },
    confidence_band: 'C',
    kappa_gate_passed: false,
    kappa_threshold: 0.70,
    task_criticality: 'routine'
  },
  {
    id: '5',
    type: 'error',
    severity: 'critical',
    message: 'VIF κ-gate failed: Confidence 0.60 below threshold 0.95 for critical task',
    file: 'src/components/TopBar.tsx',
    line: 45,
    source: 'vif',
    timestamp: new Date(Date.now() - 1800000).toISOString(),
    vif_witness: {
      id: 'witness_5',
      model_id: 'gpt-4-turbo',
      prompt_hash: 'hash_mno345',
      prompt_tokens: 300,
      confidence_score: 0.60,
      confidence_band: 'C',
      task_criticality: 'critical',
      kappa_threshold: 0.95,
      kappa_gate_passed: false,
      created_at: new Date(Date.now() - 1800000).toISOString()
    },
    confidence_band: 'C',
    kappa_gate_passed: false,
    kappa_threshold: 0.95,
    task_criticality: 'critical'
  }
]

export const ProblemsPanel: React.FC = () => {
  const [filter, setFilter] = useState<'all' | 'error' | 'warning' | 'info' | 'vif_gate_failed' | 'seg_contradiction'>('all')
  const [sortBy, setSortBy] = useState<'severity' | 'recent' | 'confidence'>('severity')
  const [expandedProblemId, setExpandedProblemId] = useState<string | null>(null)
  
  const filteredProblems = filter === 'all' 
    ? mockProblems 
    : mockProblems.filter(p => p.type === filter)
  
  // Sort problems
  const sortedProblems = [...filteredProblems].sort((a, b) => {
    switch (sortBy) {
      case 'severity':
        const severityOrder = { critical: 4, high: 3, medium: 2, low: 1 }
        return severityOrder[b.severity] - severityOrder[a.severity]
      case 'recent':
        return new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
      case 'confidence':
        const aConf = a.vif_witness?.confidence_score || 0
        const bConf = b.vif_witness?.confidence_score || 0
        return bConf - aConf
      default:
        return 0
    }
  })
  
  const toggleExpand = (problemId: string) => {
    setExpandedProblemId(expandedProblemId === problemId ? null : problemId)
  }
  
  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'error': return <XCircle className="w-4 h-4 text-red-400" />
      case 'warning': return <AlertTriangle className="w-4 h-4 text-yellow-400" />
      case 'info': return <Info className="w-4 h-4 text-blue-400" />
      case 'vif_gate_failed': return <Shield className="w-4 h-4 text-orange-400" />
      case 'seg_contradiction': return <Brain className="w-4 h-4 text-purple-400" />
      default: return <CheckCircle className="w-4 h-4 text-green-400" />
    }
  }
  
  const getTypeColor = (type: string) => {
    switch (type) {
      case 'error': return 'text-red-400 border-red-500 bg-red-900/20'
      case 'warning': return 'text-yellow-400 border-yellow-500 bg-yellow-900/20'
      case 'info': return 'text-blue-400 border-blue-500 bg-blue-900/20'
      case 'vif_gate_failed': return 'text-orange-400 border-orange-500 bg-orange-900/20'
      case 'seg_contradiction': return 'text-purple-400 border-purple-500 bg-purple-900/20'
      default: return 'text-gray-400 border-gray-500 bg-gray-900/20'
    }
  }
  
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-500 bg-red-900/30 border-red-700'
      case 'high': return 'text-orange-400 bg-orange-900/30 border-orange-700'
      case 'medium': return 'text-yellow-400 bg-yellow-900/30 border-yellow-700'
      case 'low': return 'text-blue-400 bg-blue-900/30 border-blue-700'
      default: return 'text-gray-400 bg-gray-900/30 border-gray-700'
    }
  }
  
  const getConfidenceBandColor = (band?: string) => {
    switch (band) {
      case 'A': return 'text-green-400 bg-green-900/30 border-green-700'
      case 'B': return 'text-yellow-400 bg-yellow-900/30 border-yellow-700'
      case 'C': return 'text-red-400 bg-red-900/30 border-red-700'
      default: return 'text-gray-400 bg-gray-900/30 border-gray-700'
    }
  }
  
  const getConfidenceBandLabel = (band?: string) => {
    switch (band) {
      case 'A': return 'Band A (0.90-1.00)'
      case 'B': return 'Band B (0.70-0.89)'
      case 'C': return 'Band C (<0.70)'
      default: return 'Unknown'
    }
  }
  
  const renderProblemCompact = (problem: Problem) => {
    const isExpanded = expandedProblemId === problem.id
    const typeColor = getTypeColor(problem.type)
    const severityColor = getSeverityColor(problem.severity)
    
    return (
      <div
        key={problem.id}
        onClick={() => toggleExpand(problem.id)}
        className={`rounded border transition-all cursor-pointer ${
          isExpanded 
            ? `p-3 ${typeColor.split(' ')[1]} ${typeColor.split(' ')[2]}` 
            : `p-1.5 border-l-2 ${typeColor.split(' ')[1]} hover:bg-gray-800/50`
        }`}
      >
        {!isExpanded ? (
          // Compact View - Color coded by severity via icon only
          <div className="flex items-center gap-2 text-xs">
            {getTypeIcon(problem.type)}
            <span className={`flex-1 truncate ${typeColor.split(' ')[0]}`}>
              {problem.message}
            </span>
            <span className="text-gray-500 text-[10px] flex-shrink-0">
              {problem.file.split('/').pop()}:{problem.line}
            </span>
          </div>
        ) : (
          // Expanded View
          <>
            {/* Header Row */}
            <div className="flex items-start gap-2 mb-2">
              {getTypeIcon(problem.type)}
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-2 mb-1">
                  <div className="text-sm text-gray-200 flex-1">
                    {problem.message}
                  </div>
                  <span className={`px-2 py-0.5 rounded text-xs capitalize flex-shrink-0 ${severityColor}`}>
                    {problem.severity}
                  </span>
                </div>
                <div className="text-xs text-gray-400">
                  {problem.file}:{problem.line}
                  {problem.column && `:${problem.column}`}
                </div>
              </div>
            </div>
            
            {/* VIF Witness Info */}
            {problem.vif_witness && (
              <div className="mt-2 pt-2 border-t border-gray-700">
                <div className="flex items-center gap-2 mb-2">
                  <Shield className="w-4 h-4 text-blue-400" />
                  <span className="text-xs font-semibold text-gray-300">VIF Witness</span>
                </div>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div>
                    <span className="text-gray-500">Confidence Band:</span>
                    <span className={`ml-2 px-1.5 py-0.5 rounded ${getConfidenceBandColor(problem.confidence_band).split(' ')[0]} ${getConfidenceBandColor(problem.confidence_band).split(' ')[1]} border ${getConfidenceBandColor(problem.confidence_band).split(' ')[2]}`}>
                      {getConfidenceBandLabel(problem.confidence_band)}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-500">Confidence Score:</span>
                    <span className={`ml-2 ${
                      problem.vif_witness.confidence_score >= 0.85 ? 'text-green-400' :
                      problem.vif_witness.confidence_score >= 0.70 ? 'text-yellow-400' : 'text-red-400'
                    }`}>
                      {(problem.vif_witness.confidence_score * 100).toFixed(0)}%
                    </span>
                  </div>
                  {problem.kappa_threshold !== undefined && (
                    <>
                      <div>
                        <span className="text-gray-500">κ Threshold:</span>
                        <span className="ml-2 text-gray-300">
                          {(problem.kappa_threshold * 100).toFixed(0)}% ({problem.task_criticality})
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-500">κ-Gate:</span>
                        <span className={`ml-2 flex items-center gap-1 ${
                          problem.kappa_gate_passed ? 'text-green-400' : 'text-red-400'
                        }`}>
                          {problem.kappa_gate_passed ? (
                            <>
                              <CheckCircle className="w-3 h-3" />
                              Passed
                            </>
                          ) : (
                            <>
                              <Ban className="w-3 h-3" />
                              Failed
                            </>
                          )}
                        </span>
                      </div>
                    </>
                  )}
                  {problem.vif_witness.ece_score !== undefined && (
                    <div className="col-span-2">
                      <span className="text-gray-500">ECE Score:</span>
                      <span className={`ml-2 ${
                        problem.vif_witness.ece_score < 0.1 ? 'text-green-400' :
                        problem.vif_witness.ece_score < 0.2 ? 'text-yellow-400' : 'text-red-400'
                      }`}>
                        {(problem.vif_witness.ece_score * 100).toFixed(2)}%
                      </span>
                    </div>
                  )}
                </div>
              </div>
            )}
            
            {/* SEG Contradiction Info */}
            {problem.seg_contradiction && (
              <div className="mt-2 pt-2 border-t border-gray-700">
                <div className="flex items-center gap-2 mb-2">
                  <Brain className="w-4 h-4 text-purple-400" />
                  <span className="text-xs font-semibold text-gray-300">SEG Contradiction</span>
                </div>
                <div className="text-xs space-y-1">
                  <div>
                    <span className="text-gray-500">Entity 1:</span>
                    <span className="ml-2 text-gray-300 font-mono">{problem.seg_contradiction.entity1_id}</span>
                  </div>
                  <div>
                    <span className="text-gray-500">Entity 2:</span>
                    <span className="ml-2 text-gray-300 font-mono">{problem.seg_contradiction.entity2_id}</span>
                  </div>
                  <div className="flex items-center gap-4">
                    <div>
                      <span className="text-gray-500">Similarity:</span>
                      <span className="ml-2 text-gray-300">{(problem.seg_contradiction.similarity * 100).toFixed(0)}%</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Confidence:</span>
                      <span className={`ml-2 ${
                        problem.seg_contradiction.confidence > 0.8 ? 'text-red-400' :
                        problem.seg_contradiction.confidence > 0.6 ? 'text-yellow-400' : 'text-gray-400'
                      }`}>
                        {(problem.seg_contradiction.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            {/* Footer */}
            <div className="mt-2 pt-2 border-t border-gray-700 flex items-center justify-between text-xs text-gray-500">
              <span className="capitalize">Source: {problem.source}</span>
              <span>{new Date(problem.timestamp).toLocaleTimeString()}</span>
            </div>
          </>
        )}
      </div>
    )
  }
  
  return (
    <div className="h-full flex flex-col bg-gray-950">
      {/* Filters & Sort - Same Row, Wrap When Needed */}
      <div className="p-2 border-b border-gray-700">
        <div className="flex items-center gap-2 flex-wrap">
          {/* Filter Buttons */}
          <button
            onClick={() => setFilter('all')}
            className={`px-2 py-1 rounded text-xs ${
              filter === 'all' 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            All ({mockProblems.length})
          </button>
          <button
            onClick={() => setFilter('error')}
            className={`px-2 py-1 rounded text-xs ${
              filter === 'error' 
                ? 'bg-red-600 text-white' 
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            Errors ({mockProblems.filter(p => p.type === 'error').length})
          </button>
          <button
            onClick={() => setFilter('warning')}
            className={`px-2 py-1 rounded text-xs ${
              filter === 'warning' 
                ? 'bg-yellow-600 text-white' 
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            Warnings ({mockProblems.filter(p => p.type === 'warning').length})
          </button>
          <button
            onClick={() => setFilter('vif_gate_failed')}
            className={`px-2 py-1 rounded text-xs flex items-center gap-1 ${
              filter === 'vif_gate_failed' 
                ? 'bg-orange-600 text-white' 
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            <Shield className="w-3 h-3" />
            κ-Gate ({mockProblems.filter(p => p.type === 'vif_gate_failed').length})
          </button>
          <button
            onClick={() => setFilter('seg_contradiction')}
            className={`px-2 py-1 rounded text-xs flex items-center gap-1 ${
              filter === 'seg_contradiction' 
                ? 'bg-purple-600 text-white' 
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            <Brain className="w-3 h-3" />
            SEG ({mockProblems.filter(p => p.type === 'seg_contradiction').length})
          </button>
          
          {/* Sort Dropdown - Inline */}
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as any)}
            className="px-2 py-1 rounded text-xs bg-gray-700 text-gray-300 border border-gray-600 ml-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <option value="severity">Sort by Severity</option>
            <option value="recent">Sort by Recent</option>
            <option value="confidence">Sort by Confidence</option>
          </select>
        </div>
      </div>
      
      {/* Problems List - Organized by Columns by Type */}
      <div className="flex-1 overflow-auto p-2">
        {sortedProblems.length === 0 ? (
          <div className="h-full flex items-center justify-center text-gray-500 text-sm">
            No problems found - all systems operational
          </div>
        ) : (
          <div className="grid grid-cols-5 gap-2 h-full">
            {/* Errors Column */}
            {sortedProblems.filter(p => p.type === 'error').length > 0 && (
              <div className="flex flex-col overflow-hidden">
                <div className="text-xs font-semibold text-red-400 mb-1 px-1 flex items-center gap-1 flex-shrink-0">
                  <XCircle className="w-3 h-3" />
                  Errors ({sortedProblems.filter(p => p.type === 'error').length})
                </div>
                <div className="flex-1 overflow-y-auto space-y-1">
                  {sortedProblems.filter(p => p.type === 'error').map(problem => renderProblemCompact(problem))}
                </div>
              </div>
            )}
            
            {/* Warnings Column */}
            {sortedProblems.filter(p => p.type === 'warning').length > 0 && (
              <div className="flex flex-col overflow-hidden">
                <div className="text-xs font-semibold text-yellow-400 mb-1 px-1 flex items-center gap-1 flex-shrink-0">
                  <AlertTriangle className="w-3 h-3" />
                  Warnings ({sortedProblems.filter(p => p.type === 'warning').length})
                </div>
                <div className="flex-1 overflow-y-auto space-y-1">
                  {sortedProblems.filter(p => p.type === 'warning').map(problem => renderProblemCompact(problem))}
                </div>
              </div>
            )}
            
            {/* Info Column */}
            {sortedProblems.filter(p => p.type === 'info').length > 0 && (
              <div className="flex flex-col overflow-hidden">
                <div className="text-xs font-semibold text-blue-400 mb-1 px-1 flex items-center gap-1 flex-shrink-0">
                  <Info className="w-3 h-3" />
                  Info ({sortedProblems.filter(p => p.type === 'info').length})
                </div>
                <div className="flex-1 overflow-y-auto space-y-1">
                  {sortedProblems.filter(p => p.type === 'info').map(problem => renderProblemCompact(problem))}
                </div>
              </div>
            )}
            
            {/* κ-Gate Column */}
            {sortedProblems.filter(p => p.type === 'vif_gate_failed').length > 0 && (
              <div className="flex flex-col overflow-hidden">
                <div className="text-xs font-semibold text-orange-400 mb-1 px-1 flex items-center gap-1 flex-shrink-0">
                  <Shield className="w-3 h-3" />
                  κ-Gate ({sortedProblems.filter(p => p.type === 'vif_gate_failed').length})
                </div>
                <div className="flex-1 overflow-y-auto space-y-1">
                  {sortedProblems.filter(p => p.type === 'vif_gate_failed').map(problem => renderProblemCompact(problem))}
                </div>
              </div>
            )}
            
            {/* SEG Column */}
            {sortedProblems.filter(p => p.type === 'seg_contradiction').length > 0 && (
              <div className="flex flex-col overflow-hidden">
                <div className="text-xs font-semibold text-purple-400 mb-1 px-1 flex items-center gap-1 flex-shrink-0">
                  <Brain className="w-3 h-3" />
                  SEG ({sortedProblems.filter(p => p.type === 'seg_contradiction').length})
                </div>
                <div className="flex-1 overflow-y-auto space-y-1">
                  {sortedProblems.filter(p => p.type === 'seg_contradiction').map(problem => renderProblemCompact(problem))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
