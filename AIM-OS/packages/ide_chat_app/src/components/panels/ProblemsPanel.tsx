/**
 * Problems Panel Component - ENHANCED
 * 
 * Phase 2.3: Bottom Drawer Panels
 * 
 * Errors, warnings, and info messages with comprehensive debugging support.
 * Features:
 * - Error/warning/info categorization
 * - File location links with navigation ⭐
 * - Quick fixes with auto-apply ⭐
 * - Filter by severity, source, file
 * - Problem grouping and related problems
 * - AIM-OS integration (SDF-CVF quartet violations, VIF confidence, SEG evidence) ⭐
 * - Auto-fix suggestions
 * - Problem history tracking
 * 
 * Enhanced: 2025-11-07 (Rev - Competition Phase)
 */

import React, { useState, useMemo, useEffect, useCallback } from 'react'
import { 
  AlertTriangle, 
  Info, 
  XCircle, 
  CheckCircle, 
  Filter, 
  FileText, 
  Code, 
  ExternalLink,
  Zap,
  Search,
  RefreshCw,
  Wrench,
  ChevronRight,
  ChevronDown,
  Link2,
  Brain,
  Shield,
  Clock,
  Copy,
  Eye
} from 'lucide-react'
import { useAIMOS } from '../../hooks/useAIMOS'
import { useDebounce } from '../../hooks/useDebounce'
import { LoadingState } from '../LoadingState'
import { ErrorBoundary } from '../ErrorBoundary'

interface QuickFix {
  id: string
  title: string
  description: string
  action: () => void
  confidence?: number // VIF confidence for auto-fix
  autoApply?: boolean
}

interface ProblemLifecycle {
  status: 'active' | 'solved' | 'resolved' | 'suppressed'
  solvedAt?: string
  solvedBy?: string // Agent or user who solved it
  solvedMethod?: 'auto-fix' | 'manual-fix' | 'code-change' | 'config-change'
  resolutionDetails?: string
  verifiedAt?: string
  verifiedBy?: string
}

interface Problem {
  id: string
  severity: 'error' | 'warning' | 'info'
  message: string
  file: string
  line: number
  column: number
  source?: string
  code?: string
  related?: string[] // Related problem IDs
  quickFixes?: QuickFix[]
  quartetViolation?: {
    type: 'spec' | 'test' | 'doc' | 'code'
    description: string
  }
  vifConfidence?: number
  segEvidence?: string[] // SEG evidence links
  firstSeen?: string
  lastSeen?: string
  count?: number // How many times this problem occurred
  lifecycle?: ProblemLifecycle // Error lifecycle tracking
  history?: Array<{
    timestamp: string
    event: 'created' | 'updated' | 'solved' | 'resolved' | 'reopened' | 'suppressed'
    details?: string
    agent?: string
  }>
}

const mockProblems: Problem[] = [
  {
    id: 'err-001',
    severity: 'error',
    message: "Cannot find name 'RevIDELayout'",
    file: 'packages/ide_chat_app/src/App.tsx',
    line: 15,
    column: 5,
    source: 'TypeScript',
    code: 'TS2304',
    vifConfidence: 0.95,
    quartetViolation: {
      type: 'code',
      description: 'Missing import statement violates code-spec alignment'
    },
    quickFixes: [
      {
        id: 'fix-001',
        title: 'Add import statement',
        description: "Import RevIDELayout from './components/RevIDELayout'",
        action: () => console.log('Applying fix: Add import'),
        confidence: 0.98,
        autoApply: true
      },
      {
        id: 'fix-002',
        title: 'Check component name',
        description: 'Verify component name matches export',
        action: () => console.log('Applying fix: Check name'),
        confidence: 0.85
      }
    ],
    firstSeen: '2025-11-07T10:00:00Z',
    lastSeen: '2025-11-07T11:30:00Z',
    count: 3,
    lifecycle: {
      status: 'active'
    },
    history: [
      { timestamp: '2025-11-07T10:00:00Z', event: 'created', agent: 'TypeScript Compiler' },
      { timestamp: '2025-11-07T10:15:00Z', event: 'updated', details: 'Error persisted after code change' },
      { timestamp: '2025-11-07T11:30:00Z', event: 'updated', details: 'Still active' }
    ]
  },
  {
    id: 'err-solved-001',
    severity: 'error',
    message: "Cannot find module './components/FileExplorerPanel'",
    file: 'packages/ide_chat_app/src/components/RevIDELayout.tsx',
    line: 21,
    column: 1,
    source: 'TypeScript',
    code: 'TS2307',
    vifConfidence: 0.98,
    firstSeen: '2025-11-07T09:00:00Z',
    lastSeen: '2025-11-07T10:30:00Z',
    count: 1,
    lifecycle: {
      status: 'solved',
      solvedAt: '2025-11-07T10:30:00Z',
      solvedBy: 'Rev',
      solvedMethod: 'manual-fix',
      resolutionDetails: 'Added missing import: import { FileExplorerPanel } from "./panels/FileExplorerPanel"',
      verifiedAt: '2025-11-07T10:31:00Z',
      verifiedBy: 'TypeScript Compiler'
    },
    history: [
      { timestamp: '2025-11-07T09:00:00Z', event: 'created', agent: 'TypeScript Compiler' },
      { timestamp: '2025-11-07T10:30:00Z', event: 'solved', agent: 'Rev', details: 'Added missing import' },
      { timestamp: '2025-11-07T10:31:00Z', event: 'resolved', agent: 'TypeScript Compiler', details: 'Error no longer present' }
    ]
  },
  {
    id: 'warn-001',
    severity: 'warning',
    message: 'Unused variable: hoveredIcon',
    file: 'packages/ide_chat_app/src/components/RevIDELayout.tsx',
    line: 85,
    column: 3,
    source: 'ESLint',
    code: 'no-unused-vars',
    vifConfidence: 0.90,
    quickFixes: [
      {
        id: 'fix-003',
        title: 'Remove unused variable',
        description: 'Delete hoveredIcon declaration',
        action: () => console.log('Applying fix: Remove variable'),
        confidence: 0.95,
        autoApply: true
      },
      {
        id: 'fix-004',
        title: 'Prefix with underscore',
        description: 'Rename to _hoveredIcon to indicate intentionally unused',
        action: () => console.log('Applying fix: Rename variable'),
        confidence: 0.80
      }
    ],
    firstSeen: '2025-11-07T09:00:00Z',
    lastSeen: '2025-11-07T11:30:00Z',
    count: 1
  },
  {
    id: 'info-001',
    severity: 'info',
    message: 'Consider using React.memo for performance',
    file: 'packages/ide_chat_app/src/components/panels/OutlinePanel.tsx',
    line: 45,
    column: 1,
    source: 'React',
    vifConfidence: 0.75,
    quickFixes: [
      {
        id: 'fix-005',
        title: 'Wrap with React.memo',
        description: 'Optimize component with React.memo',
        action: () => console.log('Applying fix: Add React.memo'),
        confidence: 0.70
      }
    ],
    firstSeen: '2025-11-07T10:15:00Z',
    lastSeen: '2025-11-07T11:30:00Z',
    count: 1
  },
  {
    id: 'err-002',
    severity: 'error',
    message: "Property 'panelRegistry' does not exist",
    file: 'packages/ide_chat_app/src/components/RevIDELayout.tsx',
    line: 25,
    column: 10,
    source: 'TypeScript',
    code: 'TS2339',
    vifConfidence: 0.92,
    quartetViolation: {
      type: 'code',
      description: 'Missing panelRegistry import violates spec'
    },
    related: ['err-001'],
    quickFixes: [
      {
        id: 'fix-006',
        title: 'Import panelRegistry',
        description: "Add import: import { panelRegistry } from './panelRegistry'",
        action: () => console.log('Applying fix: Import panelRegistry'),
        confidence: 0.96,
        autoApply: true
      }
    ],
    firstSeen: '2025-11-07T10:30:00Z',
    lastSeen: '2025-11-07T11:30:00Z',
    count: 2
  },
  {
    id: 'violation-001',
    severity: 'error',
    message: 'SDF-CVF Quartet Violation: Missing test for createWitness function',
    file: 'packages/vif/src/witness.py',
    line: 42,
    column: 1,
    source: 'SDF-CVF',
    quartetViolation: {
      type: 'test',
      description: 'Code exists but test is missing (violates quartet parity)'
    },
    vifConfidence: 1.0,
    segEvidence: ['test-witness-001', 'spec-witness-001'],
    quickFixes: [
      {
        id: 'fix-007',
        title: 'Generate test template',
        description: 'Create test file with template for createWitness',
        action: () => console.log('Applying fix: Generate test'),
        confidence: 0.88
      }
    ],
    firstSeen: '2025-11-07T08:00:00Z',
    lastSeen: '2025-11-07T11:30:00Z',
    count: 5
  }
]

export const ProblemsPanel: React.FC = () => {
  const [problems, setProblems] = useState<Problem[]>(mockProblems)
  const [selectedSeverity, setSelectedSeverity] = useState<'all' | Problem['severity']>('all')
  const [selectedProblem, setSelectedProblem] = useState<Problem | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [filterSource, setFilterSource] = useState<string>('all')
  const [expandedProblems, setExpandedProblems] = useState<Set<string>>(new Set())
  const [showQuartetViolations, setShowQuartetViolations] = useState(true)
  const [autoFixEnabled, setAutoFixEnabled] = useState(false)
  const [showSolved, setShowSolved] = useState(true) // Show solved errors
  const [filterLifecycle, setFilterLifecycle] = useState<'all' | ProblemLifecycle['status']>('all')

  // Debounce search query for performance
  const debouncedSearchQuery = useDebounce(searchQuery, 300)

  // AIM-OS integration
  const { cmc, vif, seg, isConnected, useMockData, loading } = useAIMOS()

  // Load problems from AIM-OS (CMC + VIF + SEG)
  useEffect(() => {
    const loadProblems = async () => {
      if (!useMockData && isConnected) {
        try {
          // Load recent CMC atoms with error/warning modality
          const errorAtoms = await cmc.retrieve('error warning problem issue', 100)
          
          // Transform CMC atoms to Problem format
          const loadedProblems: Problem[] = errorAtoms
            .filter(atom => atom.modality === 'event' || atom.modality === 'tool')
            .map(atom => ({
              id: atom.id,
              severity: atom.metadata?.severity || 'error',
              message: atom.content.inline || '',
              file: atom.metadata?.file || 'unknown',
              line: atom.metadata?.line || 0,
              column: atom.metadata?.column || 0,
              source: atom.metadata?.source,
              code: atom.metadata?.code,
              related: atom.metadata?.related || [],
              quickFixes: atom.metadata?.quickFixes || [],
              quartetViolation: atom.metadata?.quartetViolation,
              vifConfidence: atom.witness.uncertainty_band === 'green' ? 0.9 : 
                           atom.witness.uncertainty_band === 'yellow' ? 0.7 : 0.5,
              segEvidence: atom.metadata?.segEvidence || [],
              firstSeen: atom.created_at,
              lastSeen: atom.created_at,
              count: 1,
              lifecycle: {
                status: atom.metadata?.lifecycle?.status || 'active',
                solvedAt: atom.metadata?.lifecycle?.solvedAt,
                solvedBy: atom.metadata?.lifecycle?.solvedBy,
                solvedMethod: atom.metadata?.lifecycle?.solvedMethod,
                resolutionDetails: atom.metadata?.lifecycle?.resolutionDetails,
              },
              history: atom.metadata?.history || [],
            }))
          
          setProblems(loadedProblems)
        } catch (error) {
          console.warn('Failed to load problems from AIM-OS, using mock data', error)
          // Keep mock problems as fallback
        }
      }
    }
    
    loadProblems()
    // Refresh every 5 seconds
    const interval = setInterval(loadProblems, 5000)
    return () => clearInterval(interval)
  }, [cmc, isConnected, useMockData])

  const filteredProblems = useMemo(() => {
    return problems.filter(p => {
      const matchesSeverity = selectedSeverity === 'all' || p.severity === selectedSeverity
      const matchesSearch = debouncedSearchQuery === '' || 
        p.message.toLowerCase().includes(debouncedSearchQuery.toLowerCase()) ||
        p.file.toLowerCase().includes(debouncedSearchQuery.toLowerCase()) ||
        p.code?.toLowerCase().includes(debouncedSearchQuery.toLowerCase())
      const matchesSource = filterSource === 'all' || p.source === filterSource
      const matchesQuartet = showQuartetViolations || !p.quartetViolation
      const matchesLifecycle = filterLifecycle === 'all' || p.lifecycle?.status === filterLifecycle
      const matchesSolved = showSolved || p.lifecycle?.status !== 'solved' && p.lifecycle?.status !== 'resolved'
      return matchesSeverity && matchesSearch && matchesSource && matchesQuartet && matchesLifecycle && matchesSolved
    })
  }, [problems, selectedSeverity, debouncedSearchQuery, filterSource, showQuartetViolations, filterLifecycle, showSolved])

  const getSeverityIcon = (severity: Problem['severity']) => {
    switch (severity) {
      case 'error': return <XCircle className="w-4 h-4 text-red-400" />
      case 'warning': return <AlertTriangle className="w-4 h-4 text-yellow-400" />
      case 'info': return <Info className="w-4 h-4 text-blue-400" />
    }
  }

  const getSeverityColor = (severity: Problem['severity']) => {
    switch (severity) {
      case 'error': return 'text-red-400 border-red-500/20 bg-red-500/10'
      case 'warning': return 'text-yellow-400 border-yellow-500/20 bg-yellow-500/10'
      case 'info': return 'text-blue-400 border-blue-500/20 bg-blue-500/10'
    }
  }

  const handleProblemClick = (problem: Problem) => {
    setSelectedProblem(selectedProblem?.id === problem.id ? null : problem)
    // TODO: Navigate to file location in editor (Monaco editor API)
    if ((window as any).navigateToFile) {
      ;(window as any).navigateToFile(problem.file, problem.line, problem.column)
    }
  }

  const handleQuickFix = (problem: Problem, fix: QuickFix) => {
    fix.action()
    // TODO: Apply fix via Monaco editor API
    // TODO: Update problem status via AIM-OS
    console.log(`Applied fix: ${fix.title} for problem ${problem.id}`)
  }

  const handleAutoFix = (problem: Problem) => {
    const autoFix = problem.quickFixes?.find(f => f.autoApply && f.confidence && f.confidence >= 0.90)
    if (autoFix) {
      handleQuickFix(problem, autoFix)
    }
  }

  const toggleProblemExpansion = (problemId: string) => {
    setExpandedProblems(prev => {
      const newSet = new Set(prev)
      if (newSet.has(problemId)) {
        newSet.delete(problemId)
      } else {
        newSet.add(problemId)
      }
      return newSet
    })
  }

  const errorCount = problems.filter(p => p.severity === 'error').length
  const warningCount = problems.filter(p => p.severity === 'warning').length
  const infoCount = problems.filter(p => p.severity === 'info').length
  const quartetViolationCount = problems.filter(p => p.quartetViolation).length

  const sources = Array.from(new Set(problems.map(p => p.source).filter(Boolean))) as string[]

  return (
    <ErrorBoundary>
      <div className="h-full flex flex-col bg-gray-800" role="complementary" aria-label="Problems Panel">
        {loading.cmc ? (
          <LoadingState message="Loading problems..." />
        ) : (
          <>
      {/* Header */}
      <div className="h-10 bg-gray-900 border-b border-gray-700 flex items-center px-3 shrink-0">
        <AlertTriangle className="w-4 h-4 mr-2 text-gray-400" />
        <span className="text-sm font-semibold text-gray-300">Problems</span>
        <div className="ml-auto flex items-center gap-3 text-xs">
          {errorCount > 0 && (
            <span className="text-red-400 font-semibold">{errorCount} errors</span>
          )}
          {warningCount > 0 && (
            <span className="text-yellow-400">{warningCount} warnings</span>
          )}
          {infoCount > 0 && (
            <span className="text-blue-400">{infoCount} info</span>
          )}
          {quartetViolationCount > 0 && (
            <span className="text-orange-400 flex items-center gap-1" title="SDF-CVF Quartet Violations">
              <Shield className="w-3 h-3" />
              {quartetViolationCount} violations
            </span>
          )}
        </div>
      </div>

      {/* Search and Filters */}
      <div className="px-2 py-2 border-b border-gray-700 shrink-0 space-y-2">
        <div className="relative">
          <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 w-3.5 h-3.5 text-gray-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search problems..."
            className="w-full pl-8 pr-2 py-1.5 bg-gray-900 border border-gray-700 rounded text-sm text-gray-300 placeholder-gray-500 focus:outline-none focus:border-blue-500"
          />
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          {/* Severity Filter */}
          <div className="flex gap-1">
            {(['all', 'error', 'warning', 'info'] as const).map((severity) => (
              <button
                key={severity}
                onClick={() => setSelectedSeverity(severity)}
                className={`px-2 py-1 text-xs rounded transition-colors ${
                  selectedSeverity === severity
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                {severity.charAt(0).toUpperCase() + severity.slice(1)}
              </button>
            ))}
          </div>
          
          {/* Source Filter */}
          <select
            value={filterSource}
            onChange={(e) => setFilterSource(e.target.value)}
            className="px-2 py-1 text-xs bg-gray-700 text-gray-300 rounded border border-gray-600 focus:outline-none focus:border-blue-500"
          >
            <option value="all">All Sources</option>
            {sources.map(source => (
              <option key={source} value={source}>{source}</option>
            ))}
          </select>

          {/* Lifecycle Filter */}
          <select
            value={filterLifecycle}
            onChange={(e) => setFilterLifecycle(e.target.value as any)}
            className="px-2 py-1 text-xs bg-gray-700 text-gray-300 rounded border border-gray-600 focus:outline-none focus:border-blue-500"
          >
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="solved">Solved</option>
            <option value="resolved">Resolved</option>
            <option value="suppressed">Suppressed</option>
          </select>

          {/* Show Solved Toggle */}
          <button
            onClick={() => setShowSolved(!showSolved)}
            className={`px-2 py-1 text-xs rounded flex items-center gap-1 ${
              showSolved
                ? 'bg-green-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
            title="Show/hide solved errors"
          >
            <CheckCircle className="w-3 h-3" />
            Solved
          </button>

          {/* Quartet Violations Toggle */}
          <button
            onClick={() => setShowQuartetViolations(!showQuartetViolations)}
            className={`px-2 py-1 text-xs rounded flex items-center gap-1 ${
              showQuartetViolations
                ? 'bg-orange-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
            title="Show/hide SDF-CVF quartet violations"
          >
            <Shield className="w-3 h-3" />
            Quartet
          </button>

          {/* Auto-fix Toggle */}
          <button
            onClick={() => setAutoFixEnabled(!autoFixEnabled)}
            className={`px-2 py-1 text-xs rounded flex items-center gap-1 ${
              autoFixEnabled
                ? 'bg-green-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
            title="Enable/disable auto-fix for high-confidence fixes"
          >
            <Zap className="w-3 h-3" />
            Auto-Fix
          </button>
        </div>
      </div>

      {/* Problems List */}
      <div className="flex-1 overflow-y-auto p-2">
        {filteredProblems.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500 text-sm">
            <CheckCircle className="w-8 h-8 mb-2 opacity-50 text-green-400" />
            <p>No problems found</p>
          </div>
        ) : (
          <div className="space-y-1">
            {filteredProblems.map((problem) => {
              const isExpanded = expandedProblems.has(problem.id)
              const hasQuickFixes = problem.quickFixes && problem.quickFixes.length > 0
              const autoFix = problem.quickFixes?.find(f => f.autoApply && f.confidence && f.confidence >= 0.90)
              
              return (
                <div
                  key={problem.id}
                  className={`rounded border transition-colors ${
                    selectedProblem?.id === problem.id
                      ? `${getSeverityColor(problem.severity)} border-2`
                      : 'bg-gray-700/50 hover:bg-gray-700 border-transparent'
                  }`}
                >
                  {/* Problem Header */}
                  <div
                    onClick={() => handleProblemClick(problem)}
                    className="p-3 cursor-pointer"
                    role="button"
                    tabIndex={0}
                    aria-label={`${problem.severity} ${problem.message}`}
                  >
                    <div className="flex items-start gap-2 mb-1">
                      {getSeverityIcon(problem.severity)}
                      <div className="flex-1">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="text-sm text-gray-300 mb-1 flex items-center gap-2 flex-wrap">
                              {problem.message}
                              {problem.lifecycle?.status === 'solved' && (
                                <span className="px-1.5 py-0.5 bg-green-600/20 text-green-400 text-xs rounded flex items-center gap-1" title="Solved">
                                  <CheckCircle className="w-3 h-3" />
                                  Solved
                                </span>
                              )}
                              {problem.lifecycle?.status === 'resolved' && (
                                <span className="px-1.5 py-0.5 bg-blue-600/20 text-blue-400 text-xs rounded flex items-center gap-1" title="Resolved">
                                  <CheckCircle className="w-3 h-3" />
                                  Resolved
                                </span>
                              )}
                              {problem.quartetViolation && (
                                <span className="px-1.5 py-0.5 bg-orange-600 text-white text-xs rounded flex items-center gap-1" title="SDF-CVF Quartet Violation">
                                  <Shield className="w-3 h-3" />
                                  Quartet
                                </span>
                              )}
                              {problem.vifConfidence !== undefined && (
                                <span className={`text-xs px-1.5 py-0.5 rounded ${
                                  problem.vifConfidence >= 0.90 ? 'bg-green-600/20 text-green-400' :
                                  problem.vifConfidence >= 0.70 ? 'bg-yellow-600/20 text-yellow-400' :
                                  'bg-red-600/20 text-red-400'
                                }`} title="VIF Confidence">
                                  VIF: {(problem.vifConfidence * 100).toFixed(0)}%
                                </span>
                              )}
                              {problem.count && problem.count > 1 && (
                                <span className="text-xs text-gray-500" title="Occurrence count">
                                  ({problem.count}x)
                                </span>
                              )}
                            </div>
                            <div className="flex items-center gap-2 text-xs text-gray-500">
                              <FileText className="w-3 h-3" />
                              <span className="font-mono">{problem.file.split('/').pop()}</span>
                              <span>•</span>
                              <span>Line {problem.line}, Col {problem.column}</span>
                              {problem.source && (
                                <>
                                  <span>•</span>
                                  <span>{problem.source}</span>
                                </>
                              )}
                              {problem.code && (
                                <>
                                  <span>•</span>
                                  <code className="bg-gray-900 px-1 rounded">{problem.code}</code>
                                </>
                              )}
                            </div>
                          </div>
                          <div className="flex items-center gap-1">
                            {hasQuickFixes && (
                              <button
                                onClick={(e) => {
                                  e.stopPropagation()
                                  toggleProblemExpansion(problem.id)
                                }}
                                className="p-1 text-gray-400 hover:text-gray-300"
                                title="Show quick fixes"
                              >
                                {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                              </button>
                            )}
                            {autoFix && autoFixEnabled && (
                              <button
                                onClick={(e) => {
                                  e.stopPropagation()
                                  handleAutoFix(problem)
                                }}
                                className="p-1 text-green-400 hover:text-green-300"
                                title={`Auto-fix: ${autoFix.title}`}
                              >
                                <Zap className="w-4 h-4" />
                              </button>
                            )}
                            <button
                              onClick={(e) => {
                                e.stopPropagation()
                                if ((window as any).navigateToFile) {
                                  ;(window as any).navigateToFile(problem.file, problem.line, problem.column)
                                }
                              }}
                              className="p-1 text-blue-400 hover:text-blue-300"
                              title="Go to file location"
                            >
                              <ExternalLink className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Quick Fixes (Expanded) */}
                  {isExpanded && hasQuickFixes && (
                    <div className="border-t border-gray-700 p-3 bg-gray-900/50">
                      <div className="text-xs font-semibold text-gray-400 mb-2 flex items-center gap-1">
                        <Wrench className="w-3 h-3" />
                        Quick Fixes ({problem.quickFixes!.length})
                      </div>
                      <div className="space-y-2">
                        {problem.quickFixes!.map((fix) => (
                          <div
                            key={fix.id}
                            className="p-2 bg-gray-800 rounded border border-gray-700"
                          >
                            <div className="flex items-start justify-between mb-1">
                              <div className="flex-1">
                                <div className="text-xs font-medium text-gray-300 mb-0.5">
                                  {fix.title}
                                  {fix.autoApply && (
                                    <span className="ml-2 px-1 py-0.5 bg-green-600/20 text-green-400 text-xs rounded">
                                      Auto
                                    </span>
                                  )}
                                </div>
                                <div className="text-xs text-gray-500">{fix.description}</div>
                              </div>
                              <div className="flex items-center gap-1">
                                {fix.confidence !== undefined && (
                                  <span className={`text-xs px-1.5 py-0.5 rounded ${
                                    fix.confidence >= 0.90 ? 'bg-green-600/20 text-green-400' :
                                    fix.confidence >= 0.70 ? 'bg-yellow-600/20 text-yellow-400' :
                                    'bg-red-600/20 text-red-400'
                                  }`}>
                                    {(fix.confidence * 100).toFixed(0)}%
                                  </span>
                                )}
                                <button
                                  onClick={() => handleQuickFix(problem, fix)}
                                  className="px-2 py-1 bg-blue-600 hover:bg-blue-700 text-white text-xs rounded flex items-center gap-1"
                                >
                                  <Zap className="w-3 h-3" />
                                  Apply
                                </button>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Quartet Violation Details */}
                  {problem.quartetViolation && (
                    <div className="border-t border-gray-700 p-3 bg-orange-900/10">
                      <div className="text-xs font-semibold text-orange-400 mb-1 flex items-center gap-1">
                        <Shield className="w-3 h-3" />
                        SDF-CVF Quartet Violation
                      </div>
                      <div className="text-xs text-gray-300">
                        Type: <span className="font-mono">{problem.quartetViolation.type}</span>
                      </div>
                      <div className="text-xs text-gray-400 mt-1">
                        {problem.quartetViolation.description}
                      </div>
                    </div>
                  )}

                  {/* SEG Evidence */}
                  {problem.segEvidence && problem.segEvidence.length > 0 && (
                    <div className="border-t border-gray-700 p-3 bg-gray-900/50">
                      <div className="text-xs font-semibold text-gray-400 mb-1 flex items-center gap-1">
                        <Brain className="w-3 h-3" />
                        SEG Evidence
                      </div>
                      <div className="flex flex-wrap gap-1">
                        {problem.segEvidence.map((evidence, idx) => (
                          <button
                            key={idx}
                            className="px-2 py-0.5 bg-gray-800 text-xs text-gray-300 rounded border border-gray-700 hover:border-blue-500"
                            title={`View evidence: ${evidence}`}
                          >
                            <Link2 className="w-3 h-3 inline mr-1" />
                            {evidence}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Related Problems */}
                  {problem.related && problem.related.length > 0 && (
                    <div className="border-t border-gray-700 p-3 bg-gray-900/50">
                      <div className="text-xs font-semibold text-gray-400 mb-1 flex items-center gap-1">
                        <Link2 className="w-3 h-3" />
                        Related Problems
                      </div>
                      <div className="space-y-1">
                        {problem.related.map(relatedId => {
                          const relatedProblem = mockProblems.find(p => p.id === relatedId)
                          return relatedProblem ? (
                            <button
                              key={relatedId}
                              onClick={() => handleProblemClick(relatedProblem)}
                              className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1"
                            >
                              <ChevronRight className="w-3 h-3" />
                              {relatedProblem.message}
                            </button>
                          ) : null
                        })}
                      </div>
                    </div>
                  )}

                  {/* Problem History */}
                  {(problem.firstSeen || problem.lastSeen) && (
                    <div className="border-t border-gray-700 p-2 bg-gray-900/30">
                      <div className="flex items-center gap-4 text-xs text-gray-500">
                        {problem.firstSeen && (
                          <div className="flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            First: {new Date(problem.firstSeen).toLocaleTimeString()}
                          </div>
                        )}
                        {problem.lastSeen && (
                          <div className="flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            Last: {new Date(problem.lastSeen).toLocaleTimeString()}
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* Problem Details Panel */}
      {selectedProblem && (
        <div className="h-40 bg-gray-900 border-t border-gray-700 p-3 overflow-y-auto shrink-0">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-semibold text-gray-300 flex items-center gap-2">
              {getSeverityIcon(selectedProblem.severity)}
              {selectedProblem.severity.toUpperCase()}
            </h3>
            <div className="flex items-center gap-2">
              <button
                onClick={() => {
                  navigator.clipboard.writeText(`${selectedProblem.file}:${selectedProblem.line}:${selectedProblem.column}`)
                }}
                className="p-1 text-gray-400 hover:text-gray-300"
                title="Copy location"
              >
                <Copy className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => {
                  if ((window as any).navigateToFile) {
                    ;(window as any).navigateToFile(selectedProblem.file, selectedProblem.line, selectedProblem.column)
                  }
                }}
                className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1"
              >
                <ExternalLink className="w-3.5 h-3.5" />
                Go to file
              </button>
            </div>
          </div>
          <p className="text-xs text-gray-300 mb-2">{selectedProblem.message}</p>
          <div className="text-xs text-gray-500 space-y-1">
            <div className="font-mono">{selectedProblem.file}:{selectedProblem.line}:{selectedProblem.column}</div>
            {selectedProblem.source && <div>Source: {selectedProblem.source}</div>}
            {selectedProblem.code && <div>Code: <code className="bg-gray-800 px-1 rounded">{selectedProblem.code}</code></div>}
            {selectedProblem.vifConfidence !== undefined && (
              <div>VIF Confidence: <span className="text-gray-300">{(selectedProblem.vifConfidence * 100).toFixed(0)}%</span></div>
            )}
            {selectedProblem.quartetViolation && (
              <div className="text-orange-400">
                Quartet Violation: {selectedProblem.quartetViolation.type} - {selectedProblem.quartetViolation.description}
              </div>
            )}
            {selectedProblem.lifecycle && (
              <div className="mt-3 pt-3 border-t border-gray-700">
                <div className="text-xs font-semibold text-gray-400 mb-2 flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  Lifecycle Status
                </div>
                <div className="space-y-1 text-xs">
                  <div className="flex items-center gap-2">
                    <span className="text-gray-500">Status:</span>
                    <span className={`px-2 py-0.5 rounded ${
                      selectedProblem.lifecycle.status === 'solved' ? 'bg-green-600/20 text-green-400' :
                      selectedProblem.lifecycle.status === 'resolved' ? 'bg-blue-600/20 text-blue-400' :
                      selectedProblem.lifecycle.status === 'suppressed' ? 'bg-gray-600/20 text-gray-400' :
                      'bg-red-600/20 text-red-400'
                    }`}>
                      {selectedProblem.lifecycle.status.charAt(0).toUpperCase() + selectedProblem.lifecycle.status.slice(1)}
                    </span>
                  </div>
                  {selectedProblem.lifecycle.solvedAt && (
                    <>
                      <div className="flex items-center gap-2">
                        <span className="text-gray-500">Solved At:</span>
                        <span className="text-gray-300">{new Date(selectedProblem.lifecycle.solvedAt).toLocaleString()}</span>
                      </div>
                      {selectedProblem.lifecycle.solvedBy && (
                        <div className="flex items-center gap-2">
                          <span className="text-gray-500">Solved By:</span>
                          <span className="text-gray-300">{selectedProblem.lifecycle.solvedBy}</span>
                        </div>
                      )}
                      {selectedProblem.lifecycle.solvedMethod && (
                        <div className="flex items-center gap-2">
                          <span className="text-gray-500">Method:</span>
                          <span className="text-gray-300 capitalize">{selectedProblem.lifecycle.solvedMethod.replace('-', ' ')}</span>
                        </div>
                      )}
                      {selectedProblem.lifecycle.resolutionDetails && (
                        <div className="mt-2 p-2 bg-gray-800 rounded">
                          <div className="text-gray-500 mb-1">Resolution Details:</div>
                          <div className="text-gray-300">{selectedProblem.lifecycle.resolutionDetails}</div>
                        </div>
                      )}
                      {selectedProblem.lifecycle.verifiedAt && (
                        <div className="flex items-center gap-2">
                          <span className="text-gray-500">Verified At:</span>
                          <span className="text-gray-300">{new Date(selectedProblem.lifecycle.verifiedAt).toLocaleString()}</span>
                          {selectedProblem.lifecycle.verifiedBy && (
                            <span className="text-gray-500">by {selectedProblem.lifecycle.verifiedBy}</span>
                          )}
                        </div>
                      )}
                    </>
                  )}
                </div>
              </div>
            )}
            {selectedProblem.history && selectedProblem.history.length > 0 && (
              <div className="mt-3 pt-3 border-t border-gray-700">
                <div className="text-xs font-semibold text-gray-400 mb-2 flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  History ({selectedProblem.history.length} events)
                </div>
                <div className="space-y-1 max-h-32 overflow-y-auto">
                  {selectedProblem.history.map((event, idx) => (
                    <div key={idx} className="text-xs text-gray-400 flex items-start gap-2">
                      <span className="text-gray-600">{new Date(event.timestamp).toLocaleTimeString()}</span>
                      <span className={`capitalize ${
                        event.event === 'solved' || event.event === 'resolved' ? 'text-green-400' :
                        event.event === 'created' ? 'text-blue-400' :
                        'text-gray-300'
                      }`}>
                        {event.event}
                      </span>
                      {event.agent && (
                        <span className="text-gray-500">by {event.agent}</span>
                      )}
                      {event.details && (
                        <span className="text-gray-500">- {event.details}</span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
          </>
        )}
      </div>
    </ErrorBoundary>
  )
}
