// Code Editor Panel - V2 Enhanced with Consciousness-Aware & Temporal Navigation
// Monaco editor with VIF κ-gating, confidence tracking, SEG contradiction detection,
// consciousness awareness, and temporal navigation

import React, { useState, useCallback, useEffect, useMemo, useRef } from 'react'
import Editor, { DiffEditor, loader, OnMount } from '@monaco-editor/react'
import type { Monaco } from '@monaco-editor/react'
import type * as monaco from 'monaco-editor'
import { useVIF, useSEG, useCMC, useTCS, useCAS } from '../hooks/useAIMOS'
import { 
  Code, CheckCircle, Shield, Brain, Ban, Zap, 
  Play, Pause, RotateCcw, ChevronLeft, ChevronRight,
  Target, FileText, Clock, ChevronUp, ChevronDown,
  GitBranch, Link2, ExternalLink, X, History, Edit, User, Bot, Columns, AlignJustify, Plus, MessageSquare, StickyNote, Eye, EyeOff, Hash, CircleDot
} from 'lucide-react'
import type { VIFWitness, SEGContradiction, TimelineEntry } from '../hooks/useAIMOS'

interface OpenFile {
  id: string
  path: string
  name: string
  openedAt: Date
  commit?: string
  isGitVersion?: boolean
}

interface FileHistoryEntry {
  id: string
  type: 'edit' | 'open'
  filePath: string
  fileName: string
  timestamp: Date
  actor: 'ai' | 'human'
  actorName: string // AI agent name or user name
  details?: string // Additional details like commit hash, edit summary, etc.
  commit?: string
  isGitVersion?: boolean
}

interface CodeLineMetadata {
  lineNumber: number
  confidence?: number
  actor?: 'ai' | 'human'
  actorName?: string
  timestamp?: Date
  evidence?: Array<{ id: string; name: string; summary: string; confidence: number }>
  witnessId?: string
}

interface CodeEditorProps {
  onOpenFileInTabs?: (file: { id: string; path: string; name: string; commit?: string; isGitVersion?: boolean }) => void
  openFiles?: OpenFile[]
  activeFileId?: string
  onFileSelect?: (fileId: string) => void
  selectedLanguage?: string
  onLanguageChange?: (language: string) => void
}

export const CodeEditor: React.FC<CodeEditorProps> = ({ 
  onOpenFileInTabs,
  openFiles = [],
  activeFileId,
  onFileSelect,
  selectedLanguage: propSelectedLanguage = 'typescript',
  onLanguageChange
}) => {
  const { trackConfidence } = useVIF()
  const { detectContradictions, entities } = useSEG()
  const { retrieveAtoms } = useCMC()
  const { getSummary } = useTCS()
  const { getMetrics } = useCAS()
  
  // Consciousness-aware state
  const [consciousnessMetrics, setConsciousnessMetrics] = useState<any>(null)
  const [relatedMemories, setRelatedMemories] = useState<any[]>([])
  const [relatedGoals, setRelatedGoals] = useState<any[]>([])
  const [evidenceTrails, setEvidenceTrails] = useState<any[]>([])
  const [showEvidencePanel, setShowEvidencePanel] = useState(false)
  
  // Connected files/docs and git history state
  const [connectedFiles, setConnectedFiles] = useState<Array<{
    path: string
    name: string
    lines: number[]
    type: 'import' | 'export' | 'reference' | 'dependency'
    nestedConnections?: Array<{
      path: string
      name: string
      lines: number[]
      type: 'import' | 'export' | 'reference' | 'dependency'
    }>
  }>>([])
  const [gitHistory, setGitHistory] = useState<Array<{
    commit: string
    author: string
    date: Date
    message: string
    content?: string // File content at this commit
  }>>([])
  const [showGitHistory, setShowGitHistory] = useState(false)
  const [showCreateBranch, setShowCreateBranch] = useState(false)
  const [newBranchName, setNewBranchName] = useState('')
  const [newBranchBase, setNewBranchBase] = useState('main')
  const [newBranchDescription, setNewBranchDescription] = useState('')
  const [showConnections, setShowConnections] = useState(false)
  const [selectedFileDetails, setSelectedFileDetails] = useState<string | null>(null)
  const [showMoreConnections, setShowMoreConnections] = useState(false)
  const [selectedGitVersion, setSelectedGitVersion] = useState<string | null>(null)
  const [showGitEditWarning, setShowGitEditWarning] = useState(false)
  const [isEditingGitVersion, setIsEditingGitVersion] = useState(false)
  const [gitVersionContent, setGitVersionContent] = useState<string | null>(null)
  const [nextVersionContent, setNextVersionContent] = useState<string | null>(null)
  const [showDiffView, setShowDiffView] = useState(false)
  const [diffSideBySide, setDiffSideBySide] = useState(true)
  const [showMemoriesDetails, setShowMemoriesDetails] = useState(false)
  const [showGoalsDetails, setShowGoalsDetails] = useState(false)
  const [showHistoryDropdown, setShowHistoryDropdown] = useState(false)
  const [fileHistory, setFileHistory] = useState<FileHistoryEntry[]>([])
  const [showTechnicalDetails, setShowTechnicalDetails] = useState(false)
  const [enableAdvancedFeatures, setEnableAdvancedFeatures] = useState(true)
  const [editorInfo, setEditorInfo] = useState({ lines: 0, characters: 0, cursorLine: 0, cursorColumn: 0 })
  const editorRef = useRef<monaco.editor.IStandaloneCodeEditor | null>(null)
  const monacoRef = useRef<Monaco | null>(null)
  const codeLensProviderRef = useRef<monaco.IDisposable | null>(null)
  const hoverProviderRef = useRef<monaco.IDisposable | null>(null)
  const [codeLineMetadata, setCodeLineMetadata] = useState<Record<number, CodeLineMetadata>>({})
  const codeLineMetadataRef = useRef<Record<number, CodeLineMetadata>>({})
  
  // Notes system - notes per line
  interface LineNote {
    id: string
    lineNumber: number
    content: string
    author: 'user' | 'ai'
    authorName: string
    timestamp: Date
  }
  const [lineNotes, setLineNotes] = useState<Record<number, LineNote[]>>({})
  const [editingNoteLine, setEditingNoteLine] = useState<number | null>(null)
  const [editingNoteContent, setEditingNoteContent] = useState<string>('')
  const [hoveredNoteLine, setHoveredNoteLine] = useState<number | null>(null)
  const notesContainerRef = useRef<HTMLDivElement>(null)
  
  // Column visibility toggles
  const [showLineNumbers, setShowLineNumbers] = useState<boolean>(true)
  const [showGlyphMargin, setShowGlyphMargin] = useState<boolean>(true)
  const [showNotesColumn, setShowNotesColumn] = useState<boolean>(true)
  const [showEditorInfo, setShowEditorInfo] = useState<boolean>(true)
  
  // Use language from props, but manage dropdown locally
  const selectedLanguage = propSelectedLanguage
  const selectedLanguageRef = useRef<string>(propSelectedLanguage)
  const showLineNumbersRef = useRef<boolean>(true)
  const showGlyphMarginRef = useRef<boolean>(true)
  const [showLanguageDropdown, setShowLanguageDropdown] = useState(false)
  
  // Supported languages for Monaco editor
  const supportedLanguages = [
    { value: 'typescript', label: 'TypeScript', icon: 'TS' },
    { value: 'javascript', label: 'JavaScript', icon: 'JS' },
    { value: 'python', label: 'Python', icon: 'PY' },
    { value: 'java', label: 'Java', icon: 'JA' },
    { value: 'csharp', label: 'C#', icon: 'C#' },
    { value: 'cpp', label: 'C++', icon: 'C++' },
    { value: 'c', label: 'C', icon: 'C' },
    { value: 'go', label: 'Go', icon: 'GO' },
    { value: 'rust', label: 'Rust', icon: 'RS' },
    { value: 'php', label: 'PHP', icon: 'PHP' },
    { value: 'ruby', label: 'Ruby', icon: 'RB' },
    { value: 'swift', label: 'Swift', icon: 'SW' },
    { value: 'kotlin', label: 'Kotlin', icon: 'KT' },
    { value: 'html', label: 'HTML', icon: 'HTML' },
    { value: 'css', label: 'CSS', icon: 'CSS' },
    { value: 'json', label: 'JSON', icon: 'JSON' },
    { value: 'yaml', label: 'YAML', icon: 'YAML' },
    { value: 'markdown', label: 'Markdown', icon: 'MD' },
    { value: 'sql', label: 'SQL', icon: 'SQL' },
    { value: 'shell', label: 'Shell', icon: 'SH' },
    { value: 'dockerfile', label: 'Dockerfile', icon: 'DOCK' },
    { value: 'plaintext', label: 'Plain Text', icon: 'TXT' },
  ]
  
  // Keep refs in sync with state
  useEffect(() => {
    codeLineMetadataRef.current = codeLineMetadata
  }, [codeLineMetadata])
  
  useEffect(() => {
    selectedLanguageRef.current = propSelectedLanguage
  }, [propSelectedLanguage])
  
  useEffect(() => {
    showLineNumbersRef.current = showLineNumbers
  }, [showLineNumbers])
  
  useEffect(() => {
    showGlyphMarginRef.current = showGlyphMargin
  }, [showGlyphMargin])
  const [fileContentCache, setFileContentCache] = useState<Record<string, {
    content: string
    nestedConnections: Array<{
      path: string
      name: string
      lines: number[]
      type: 'import' | 'export' | 'reference' | 'dependency'
    }>
  }>>({})
  
  // Temporal navigation state
  const [timelineEntries, setTimelineEntries] = useState<TimelineEntry[]>([])
  const [currentTimelineIndex, setCurrentTimelineIndex] = useState<number>(-1)
  const [isPlaying, setIsPlaying] = useState(false)
  const [playbackSpeed, setPlaybackSpeed] = useState(1)
  const [code, setCode] = useState(`// AIM-OS IDE Prototype - Perfect Integration
import React from 'react'
import { useCMC, useVIF, useSEG } from './hooks/useAIMOS'

export const Example: React.FC = () => {
  const { storeAtom } = useCMC()
  const { trackConfidence } = useVIF()
  const { detectContradictions } = useSEG()
  
  const handleAction = async () => {
    // Store in CMC with bitemporal tracking
    await storeAtom('Action performed', 'event', { type: 'user_action' })
    
    // Track confidence with VIF κ-gating
    const witness = await trackConfidence(
      'action_execution',
      0.92,
      ['atom_123'],
      'High confidence: action matches expected pattern',
      'routine'
    )
    
    // Check for SEG contradictions
    const contradictions = await detectContradictions('Action performed')
    if (contradictions.length > 0) {
      console.warn('SEG contradictions detected:', contradictions)
    }
    
    return witness
  }
  
  return <div>Example Component</div>
}`)
  const [currentWitness, setCurrentWitness] = useState<VIFWitness | null>(null)
  const [detectedContradictions, setDetectedContradictions] = useState<SEGContradiction[]>([])
  const [isValidating, setIsValidating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [validationResult, setValidationResult] = useState<{
    passed: boolean
    confidence_band: 'A' | 'B' | 'C'
    kappa_gate_passed: boolean
    message: string
  } | null>(null)
  
  // Diff view validation results
  const [diffOldValidation, setDiffOldValidation] = useState<{
    passed: boolean
    confidence_band: 'A' | 'B' | 'C'
    kappa_gate_passed: boolean
    message: string
  } | null>(null)
  const [diffNewValidation, setDiffNewValidation] = useState<{
    passed: boolean
    confidence_band: 'A' | 'B' | 'C'
    kappa_gate_passed: boolean
    message: string
  } | null>(null)
  
  // Helper function to calculate validation for a code string
  const calculateValidation = useCallback(async (codeToValidate: string): Promise<{
    passed: boolean
    confidence_band: 'A' | 'B' | 'C'
    kappa_gate_passed: boolean
    message: string
  }> => {
    // Simplified validation logic - in real implementation, this would use VIF
    const codeConfidence = Math.min(0.95, 0.60 + (codeToValidate.length / 10000) * 0.35)
    
    let confidence_band: 'A' | 'B' | 'C'
    if (codeConfidence >= 0.90) {
      confidence_band = 'A'
    } else if (codeConfidence >= 0.70) {
      confidence_band = 'B'
    } else {
      confidence_band = 'C'
    }
    
    const taskCriticality = 'important' as const
    const kappa_thresholds = {
      critical: 0.90,
      important: 0.85,
      routine: 0.70,
      low_stakes: 0.60
    }
    const kappa_threshold = kappa_thresholds[taskCriticality]
    const kappa_gate_passed = codeConfidence >= kappa_threshold
    
    return {
      passed: kappa_gate_passed,
      confidence_band,
      kappa_gate_passed,
      message: kappa_gate_passed
        ? `κ-gate passed: Confidence ${(codeConfidence * 100).toFixed(0)}% >= threshold ${(kappa_threshold * 100).toFixed(0)}%`
        : `κ-gate failed: Confidence ${(codeConfidence * 100).toFixed(0)}% < threshold ${(kappa_threshold * 100).toFixed(0)}%`
    }
  }, [])
  
  // Calculate validation for diff view versions
  useEffect(() => {
    if (showDiffView && gitVersionContent && nextVersionContent) {
      const calculateDiffValidations = async () => {
        const oldValidation = await calculateValidation(gitVersionContent)
        const newValidation = await calculateValidation(nextVersionContent)
        setDiffOldValidation(oldValidation)
        setDiffNewValidation(newValidation)
      }
      calculateDiffValidations()
    } else {
      setDiffOldValidation(null)
      setDiffNewValidation(null)
    }
  }, [showDiffView, gitVersionContent, nextVersionContent, calculateValidation])
  
  // Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (showMoreConnections && !(e.target as Element).closest('.connections-dropdown')) {
        setShowMoreConnections(false)
      }
      if (selectedFileDetails && !(e.target as Element).closest('.file-details-popup')) {
        setSelectedFileDetails(null)
      }
      if (showMemoriesDetails && !(e.target as Element).closest('.memories-details-popup')) {
        setShowMemoriesDetails(false)
      }
      if (showGoalsDetails && !(e.target as Element).closest('.goals-details-popup')) {
        setShowGoalsDetails(false)
      }
      if (showHistoryDropdown && !(e.target as Element).closest('.history-dropdown')) {
        setShowHistoryDropdown(false)
      }
      if (showEvidencePanel && !(e.target as Element).closest('.evidence-details-popup')) {
        setShowEvidencePanel(false)
      }
      if (showCreateBranch && !(e.target as Element).closest('.create-branch-panel')) {
        setShowCreateBranch(false)
      }
      if (showTechnicalDetails && !(e.target as Element).closest('.technical-details')) {
        setShowTechnicalDetails(false)
      }
      if (showLanguageDropdown && !(e.target as Element).closest('.language-selector')) {
        setShowLanguageDropdown(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [showMoreConnections, selectedFileDetails, showMemoriesDetails, showGoalsDetails, showHistoryDropdown, showEvidencePanel, showCreateBranch, showTechnicalDetails, showLanguageDropdown])
  
  // Track file history (edit and open events)
  useEffect(() => {
    // Initialize with mock history data - in real implementation, this would come from CMC/TCS
    const initialHistory: FileHistoryEntry[] = [
      {
        id: 'hist-1',
        type: 'open',
        filePath: 'src/panels/CodeEditor.tsx',
        fileName: 'CodeEditor.tsx',
        timestamp: new Date(Date.now() - 300000),
        actor: 'human',
        actorName: 'Braden'
      },
      {
        id: 'hist-2',
        type: 'edit',
        filePath: 'src/panels/CodeEditor.tsx',
        fileName: 'CodeEditor.tsx',
        timestamp: new Date(Date.now() - 240000),
        actor: 'ai',
        actorName: 'Aether',
        details: 'Added history tracking functionality'
      },
      {
        id: 'hist-3',
        type: 'open',
        filePath: 'src/components/IDELayout.tsx',
        fileName: 'IDELayout.tsx',
        timestamp: new Date(Date.now() - 180000),
        actor: 'human',
        actorName: 'Braden'
      },
      {
        id: 'hist-4',
        type: 'edit',
        filePath: 'src/components/IDELayout.tsx',
        fileName: 'IDELayout.tsx',
        timestamp: new Date(Date.now() - 120000),
        actor: 'ai',
        actorName: 'Aether',
        details: 'Updated layout state management'
      },
      {
        id: 'hist-5',
        type: 'open',
        filePath: 'src/components/TopBar.tsx',
        fileName: 'TopBar.tsx',
        timestamp: new Date(Date.now() - 60000),
        actor: 'human',
        actorName: 'Braden'
      },
      {
        id: 'hist-6',
        type: 'edit',
        filePath: 'src/panels/CodeEditor.tsx',
        fileName: 'CodeEditor.tsx',
        timestamp: new Date(Date.now() - 30000),
        actor: 'ai',
        actorName: 'Aether',
        details: 'Refactored history button implementation'
      }
    ]
    setFileHistory(initialHistory)
  }, [])
  
  // Track code edits in history
  useEffect(() => {
    if (code) {
      const editEntry: FileHistoryEntry = {
        id: `edit-${Date.now()}`,
        type: 'edit',
        filePath: 'src/panels/CodeEditor.tsx', // Current file - in real implementation, get from active file
        fileName: 'CodeEditor.tsx',
        timestamp: new Date(),
        actor: 'ai', // In real implementation, detect from context
        actorName: 'Aether',
        details: `Code edited (${code.length} chars)`
      }
      // Debounce: only add if significant change (in real implementation, use proper debouncing)
      setFileHistory(prev => {
        const recentEdit = prev.find(e => e.type === 'edit' && e.filePath === editEntry.filePath)
        if (recentEdit && Date.now() - recentEdit.timestamp.getTime() < 5000) {
          return prev // Skip if edit was less than 5 seconds ago
        }
        return [editEntry, ...prev].slice(0, 50) // Keep last 50 entries
      })
    }
  }, [code])
  
  // Setup Monaco theme to match app background (gray-950 = #030712)
  useEffect(() => {
    loader.init().then((monaco) => {
      monaco.editor.defineTheme('aimos-dark', {
        base: 'vs-dark',
        inherit: true,
        rules: [],
        colors: {
          'editor.background': '#030712', // gray-950
          'editor.foreground': '#f3f4f6', // gray-100
          'editor.selectionBackground': '#374151', // gray-700
          'editor.lineHighlightBackground': '#111827', // gray-900
          'editorCursor.foreground': '#f3f4f6',
          'editorLineNumber.foreground': '#6b7280', // gray-500
          'editorLineNumber.activeForeground': '#d1d5db', // gray-300
          'editorGutter.background': '#030712',
          'editorIndentGuide.background': '#374151',
          'editorIndentGuide.activeBackground': '#4b5563',
        }
      })
      monaco.editor.setTheme('aimos-dark')
    })
  }, [])
  
  // Load connected files and git history
  useEffect(() => {
    const loadConnections = async () => {
      // Mock connected files - in real implementation, this would analyze imports/exports/references
      const mockConnections = [
        { path: 'src/hooks/useAIMOS.ts', name: 'useAIMOS.ts', lines: [1, 2, 3, 16, 17, 18], type: 'import' as const },
        { path: 'src/components/IDELayout.tsx', name: 'IDELayout.tsx', lines: [38, 39], type: 'reference' as const },
        { path: 'src/store/panelStore.ts', name: 'panelStore.ts', lines: [45, 46], type: 'dependency' as const },
        { path: 'docs/CODE_EDITOR.md', name: 'CODE_EDITOR.md', lines: [12, 15, 20], type: 'reference' as const },
      ]
      setConnectedFiles(mockConnections)
      
      // Mock git history - in real implementation, this would fetch from git
      const mockHistory = [
        { 
          commit: 'a3f2b1c', 
          author: 'Dac', 
          date: new Date(Date.now() - 3600000), 
          message: 'Enhanced code editor with connections view',
          content: `// AIM-OS IDE Prototype - Enhanced Version
import React from 'react'
import { useCMC, useVIF, useSEG } from './hooks/useAIMOS'

export const Example: React.FC = () => {
  const { storeAtom } = useCMC()
  const { trackConfidence } = useVIF()
  const { detectContradictions } = useSEG()
  
  const handleAction = async () => {
    await storeAtom('Action performed', 'event', { type: 'user_action' })
    const witness = await trackConfidence('action_execution', 0.92, ['atom_123'], 'High confidence', 'routine')
    const contradictions = await detectContradictions('Action performed')
    return witness
  }
  
  return <div>Example Component</div>
}`
        },
        { 
          commit: 'b2e1d0f', 
          author: 'Dac', 
          date: new Date(Date.now() - 7200000), 
          message: 'Added git history dropdown',
          content: `// AIM-OS IDE Prototype - Git History Added
import React from 'react'
import { useCMC, useVIF } from './hooks/useAIMOS'

export const Example: React.FC = () => {
  const { storeAtom } = useCMC()
  const { trackConfidence } = useVIF()
  
  return <div>Example Component</div>
}`
        },
        { 
          commit: 'c1d0e9f', 
          author: 'Dac', 
          date: new Date(Date.now() - 10800000), 
          message: 'Fixed scrollbar styling',
          content: `// AIM-OS IDE Prototype - Initial
import React from 'react'

export const Example: React.FC = () => {
  return <div>Example Component</div>
}`
        },
        { 
          commit: 'd0c9e8f', 
          author: 'Dac', 
          date: new Date(Date.now() - 14400000), 
          message: 'Initial code editor implementation',
          content: `// Initial implementation
export const Example = () => {
  return <div>Example</div>
}`
        },
      ]
      setGitHistory(mockHistory)
    }
    loadConnections()
  }, [code])
  
  const handleCodeChange = useCallback(async (value: string | undefined) => {
    if (!value) return
    
    // Check if editing git version and show warning
    if (selectedGitVersion && !isEditingGitVersion && value !== code) {
      setShowGitEditWarning(true)
      return
    }
    
    setCode(value)
    setIsValidating(true)
    setError(null)
    
    try {
      // Analyze code quality and determine confidence
      const codeLength = value.length
      const hasImports = value.includes('import')
      const hasExports = value.includes('export')
      const hasTypes = value.includes(':') || value.includes('<')
      const hasComments = value.includes('//') || value.includes('/*')
      
      // Calculate confidence based on code quality indicators
      let codeConfidence = 0.70 // Base confidence
      if (codeLength > 100) codeConfidence += 0.05
      if (hasImports) codeConfidence += 0.05
      if (hasExports) codeConfidence += 0.05
      if (hasTypes) codeConfidence += 0.05
      if (hasComments) codeConfidence += 0.05
      codeConfidence = Math.min(0.95, codeConfidence)
      
      // Determine task criticality based on code content
      let taskCriticality: 'critical' | 'important' | 'routine' | 'low_stakes' = 'routine'
      if (value.includes('async') || value.includes('await')) {
        taskCriticality = 'important'
      }
      if (value.includes('error') || value.includes('throw') || value.includes('catch')) {
        taskCriticality = 'critical'
      }
      
      // Track confidence with VIF
      const result = await trackConfidence(
        'code_edit',
        codeConfidence,
        ['code_change', `length_${codeLength}`],
        `Code edit: ${codeLength} chars, ${hasImports ? 'has imports' : 'no imports'}`,
        taskCriticality
      )
      
      if (result.witness) {
        setCurrentWitness(result.witness)
        
        // Determine confidence band
        let confidence_band: 'A' | 'B' | 'C'
        if (codeConfidence >= 0.90) {
          confidence_band = 'A'
        } else if (codeConfidence >= 0.70) {
          confidence_band = 'B'
        } else {
          confidence_band = 'C'
        }
        
        // Check κ-gate
        const kappa_thresholds = {
          critical: 0.95,
          important: 0.85,
          routine: 0.70,
          low_stakes: 0.60
        }
        const kappa_threshold = kappa_thresholds[taskCriticality]
        const kappa_gate_passed = codeConfidence >= kappa_threshold
        
        setValidationResult({
          passed: kappa_gate_passed,
          confidence_band,
          kappa_gate_passed,
          message: kappa_gate_passed
            ? `κ-gate passed: Confidence ${(codeConfidence * 100).toFixed(0)}% >= threshold ${(kappa_threshold * 100).toFixed(0)}%`
            : `κ-gate failed: Confidence ${(codeConfidence * 100).toFixed(0)}% < threshold ${(kappa_threshold * 100).toFixed(0)}%`
        })
      }
      
      // Check for SEG contradictions
      const contradictions = await detectContradictions(value)
      setDetectedContradictions(contradictions)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Code validation failed')
      console.error('Code validation error:', err)
    } finally {
      setIsValidating(false)
    }
  }, [trackConfidence, detectContradictions])
  
  // Load consciousness metrics
  useEffect(() => {
    const loadConsciousnessData = async () => {
      try {
        const metrics = await getMetrics()
        setConsciousnessMetrics(metrics)
        
        // Mock related memories with real data structure
        const mockMemories = [
          { id: 'mem_001', content: 'Code editor validation patterns', confidence: 0.92, timestamp: new Date() },
          { id: 'mem_002', content: 'VIF κ-gating implementation', confidence: 0.88, timestamp: new Date() },
          { id: 'mem_003', content: 'SEG contradiction detection', confidence: 0.85, timestamp: new Date() },
          { id: 'mem_004', content: 'Monaco editor integration', confidence: 0.90, timestamp: new Date() },
          { id: 'mem_005', content: 'Temporal navigation patterns', confidence: 0.87, timestamp: new Date() },
        ]
        setRelatedMemories(mockMemories)
        
        // Mock evidence trails with real data structure
        const mockEvidence = [
          { id: 'ev_001', name: 'VIF Witness Validation', confidence: 0.95, summary: 'High confidence validation pattern detected' },
          { id: 'ev_002', name: 'SEG Entity Connection', confidence: 0.82, summary: 'Connected to related code entities' },
          { id: 'ev_003', name: 'CMC Atom Reference', confidence: 0.88, summary: 'Referenced in memory system' },
          { id: 'ev_004', name: 'TCS Timeline Entry', confidence: 0.90, summary: 'Tracked in timeline context' },
          { id: 'ev_005', name: 'CAS Metrics Correlation', confidence: 0.85, summary: 'Correlated with cognitive metrics' },
        ]
        setEvidenceTrails(mockEvidence)
        
        // Mock related goals
        const mockGoals = [
          { id: 'goal_001', name: 'OBJ-07: MCP Tools Enhancement', progress: 0.15, status: 'in_progress' },
          { id: 'goal_002', name: 'OBJ-08: RAG MCP & Daemon Upgrades', progress: 0.60, status: 'in_progress' },
          { id: 'goal_003', name: 'IDE Prototype V2 Completion', progress: 0.75, status: 'in_progress' },
        ]
        setRelatedGoals(mockGoals)
      } catch (err) {
        console.error('Failed to load consciousness data:', err)
        // Fallback to mock data
        setRelatedMemories([
          { id: 'mem_001', content: 'Code editor validation patterns', confidence: 0.92, timestamp: new Date() },
          { id: 'mem_002', content: 'VIF κ-gating implementation', confidence: 0.88, timestamp: new Date() },
        ])
        setEvidenceTrails([
          { id: 'ev_001', name: 'VIF Witness Validation', confidence: 0.95, summary: 'High confidence validation pattern detected' },
          { id: 'ev_002', name: 'SEG Entity Connection', confidence: 0.82, summary: 'Connected to related code entities' },
        ])
        setRelatedGoals([
          { id: 'goal_001', name: 'OBJ-07: MCP Tools Enhancement', progress: 0.15, status: 'in_progress' },
        ])
      }
    }
    loadConsciousnessData()
  }, [code, getMetrics, retrieveAtoms, entities])
  
  // Load timeline entries
  useEffect(() => {
    const loadTimeline = async () => {
      try {
        const entries = await getSummary(50)
        setTimelineEntries(entries)
        setCurrentTimelineIndex(entries.length - 1)
      } catch (err) {
        console.error('Failed to load timeline:', err)
      }
    }
    loadTimeline()
  }, [getSummary])
  
  // Playback control
  useEffect(() => {
    if (!isPlaying || currentTimelineIndex < 0 || currentTimelineIndex >= timelineEntries.length - 1) {
      setIsPlaying(false)
      return
    }
    
    const interval = setInterval(() => {
      setCurrentTimelineIndex(prev => {
        if (prev >= timelineEntries.length - 1) {
          setIsPlaying(false)
          return prev
        }
        return prev + 1
      })
    }, 1000 / playbackSpeed)
    
    return () => clearInterval(interval)
  }, [isPlaying, currentTimelineIndex, timelineEntries.length, playbackSpeed])
  
  // Initial validation
  useEffect(() => {
    // Trigger initial validation
    if (code) {
      handleCodeChange(code)
    }
  }, []) // Only on mount
  
  // Temporal navigation handlers
  const handlePlay = () => setIsPlaying(true)
  const handlePause = () => setIsPlaying(false)
  const handleReset = () => {
    setIsPlaying(false)
    setCurrentTimelineIndex(0)
  }
  const handlePrevious = () => setCurrentTimelineIndex(prev => Math.max(0, prev - 1))
  const handleNext = () => setCurrentTimelineIndex(prev => Math.min(timelineEntries.length - 1, prev + 1))
  
  // Calculate consciousness health (0-100)
  const consciousnessHealth = useMemo(() => {
    if (!consciousnessMetrics) return 75
    const { attention_focus = 0.8, cognitive_load = 0.5, quality_maintained = true } = consciousnessMetrics
    const health = (attention_focus * 40 + (1 - cognitive_load) * 40 + (quality_maintained ? 20 : 0))
    return Math.round(health)
  }, [consciousnessMetrics])
  
  const getConfidenceBandColor = (band?: 'A' | 'B' | 'C') => {
    switch (band) {
      case 'A': return 'text-green-400 bg-green-900/30 border-green-700'
      case 'B': return 'text-yellow-400 bg-yellow-900/30 border-yellow-700'
      case 'C': return 'text-red-400 bg-red-900/30 border-red-700'
      default: return 'text-gray-400 bg-gray-900/30 border-gray-700'
    }
  }
  
  // Add/update note
  const handleAddNote = useCallback((lineNumber: number, content: string) => {
    if (!content.trim()) return
    
    const newNote: LineNote = {
      id: `note-${Date.now()}-${Math.random()}`,
      lineNumber,
      content: content.trim(),
      author: 'user',
      authorName: 'User',
      timestamp: new Date()
    }
    
    setLineNotes(prev => ({
      ...prev,
      [lineNumber]: [...(prev[lineNumber] || []), newNote]
    }))
    
    setEditingNoteLine(null)
    setEditingNoteContent('')
  }, [])
  
  // Delete note
  const handleDeleteNote = useCallback((lineNumber: number, noteId: string) => {
    setLineNotes(prev => {
      const notes = prev[lineNumber] || []
      const updated = notes.filter(n => n.id !== noteId)
      if (updated.length === 0) {
        const { [lineNumber]: _, ...rest } = prev
        return rest
      }
      return { ...prev, [lineNumber]: updated }
    })
  }, [])
  
  // Get notes for a line
  const getNotesForLine = useCallback((lineNumber: number): LineNote[] => {
    return lineNotes[lineNumber] || []
  }, [lineNotes])
  
  // Parse code to extract line metadata (mock implementation - in real app, this would come from VIF/CMC)
  useEffect(() => {
    if (!code || !enableAdvancedFeatures) return
    
    const lines = code.split('\n')
    const metadata: Record<number, CodeLineMetadata> = {}
    
    // Mock: Parse code and assign metadata based on patterns
    lines.forEach((line, index) => {
      const lineNum = index + 1
      
      // Detect AI-generated code patterns
      if (line.includes('useCMC') || line.includes('useVIF') || line.includes('useSEG')) {
        metadata[lineNum] = {
          lineNumber: lineNum,
          confidence: 0.95,
          actor: 'ai',
          actorName: 'Aether',
          timestamp: new Date(),
          evidence: evidenceTrails.slice(0, 2),
          witnessId: currentWitness?.id
        }
      } else if (line.trim().startsWith('//') && line.includes('AIM-OS')) {
        metadata[lineNum] = {
          lineNumber: lineNum,
          confidence: 0.90,
          actor: 'ai',
          actorName: 'Aether',
          timestamp: new Date(),
          evidence: evidenceTrails.slice(0, 1)
        }
      } else if (line.trim().length > 0 && !line.trim().startsWith('//')) {
        // Assume human-written code for non-comment lines without AI patterns
        metadata[lineNum] = {
          lineNumber: lineNum,
          confidence: 1.0, // Human code is 100% confident
          actor: 'human',
          actorName: 'Braden',
          timestamp: new Date()
        }
      }
    })
    
    setCodeLineMetadata(metadata)
  }, [code, enableAdvancedFeatures, evidenceTrails, currentWitness])
  
  // Update editor info (line count, character count, cursor position)
  const updateEditorInfo = useCallback(() => {
    if (editorRef.current) {
      const model = editorRef.current.getModel()
      if (model) {
        const lines = model.getLineCount()
        const characters = model.getValue().length
        const position = editorRef.current.getPosition()
        const cursorLine = position ? position.lineNumber : 0
        const cursorColumn = position ? position.column : 0
        setEditorInfo({ lines, characters, cursorLine, cursorColumn })
      }
    }
  }, [])

  // Setup Monaco editor advanced features
  const handleEditorDidMount: OnMount = useCallback((editor: monaco.editor.IStandaloneCodeEditor, monaco: Monaco) => {
    editorRef.current = editor
    monacoRef.current = monaco
    
    // Update editor info on mount
    updateEditorInfo()
    
    // Update editor info on content change
    editor.onDidChangeModelContent(() => {
      updateEditorInfo()
    })
    
    // Update editor info on cursor position change
    editor.onDidChangeCursorPosition(() => {
      updateEditorInfo()
    })
    
    // Auto-adjust line numbers width based on total lines
    const updateLineNumbersWidth = () => {
      const model = editor.getModel()
      if (model && showLineNumbersRef.current) {
        const lineCount = model.getLineCount()
        const minChars = Math.max(3, Math.ceil(Math.log10(lineCount + 1)))
        editor.updateOptions({
          lineNumbersMinChars: minChars,
          lineNumbers: showLineNumbersRef.current ? 'on' : 'off'
        })
      } else {
        editor.updateOptions({
          lineNumbers: 'off'
        })
      }
    }
    
    // Initial update
    updateLineNumbersWidth()
    
    // Update on content changes
    const model = editor.getModel()
    if (model) {
      model.onDidChangeContent(() => {
        updateLineNumbersWidth()
      })
    }
    
    // Note: Editor options (lineNumbers, glyphMargin) are handled by useEffect
    // to avoid infinite re-render loops
    
    if (!enableAdvancedFeatures) return
    
    let decorationIds: string[] = []
    let noteDecorationIds: string[] = []
    
    // Function to update note decorations
    const updateNoteDecorations = () => {
      const decorations: monaco.editor.IModelDeltaDecoration[] = []
      
      Object.entries(lineNotes).forEach(([lineNumStr, notes]) => {
        const lineNum = parseInt(lineNumStr)
        if (notes.length > 0) {
          decorations.push({
            range: {
              startLineNumber: lineNum,
              startColumn: 1,
              endLineNumber: lineNum,
              endColumn: 1
            },
            options: {
              glyphMarginClassName: 'note-indicator',
              glyphMarginHoverMessage: {
                value: `Notes (${notes.length}): ${notes.map(n => n.content.substring(0, 50)).join('; ')}`
              },
              stickiness: monaco.editor.TrackedRangeStickiness.NeverGrowsWhenTypingAtEdges
            }
          })
        }
      })
      
      noteDecorationIds = editor.deltaDecorations(noteDecorationIds, decorations)
    }
    
    // Update note decorations
    updateNoteDecorations()
    
    // Handle glyph margin clicks for notes
    editor.onMouseDown((e) => {
      if (e.target.type === monaco.editor.MouseTargetType.GUTTER_GLYPH_MARGIN) {
        const lineNumber = e.target.position?.lineNumber
        if (lineNumber) {
          const target = e.target.element
          if (target?.classList.contains('note-indicator')) {
            // Clicked on note indicator - show notes
            setEditingNoteLine(lineNumber)
            const existingNotes = lineNotes[lineNumber] || []
            setEditingNoteContent('')
          } else {
            // Clicked on empty glyph margin - add new note
            setEditingNoteLine(lineNumber)
            setEditingNoteContent('')
          }
        }
      }
    })
    
    // Function to update decorations
    const updateDecorations = () => {
      const decorations: monaco.editor.IModelDeltaDecoration[] = []
      const metadata = codeLineMetadataRef.current
      
      Object.values(metadata).forEach((lineMetadata) => {
        if (lineMetadata.confidence !== undefined) {
          const confidence = lineMetadata.confidence
          let color = 'rgba(34, 197, 94, 0.1)' // Green for high confidence
          let borderColor = 'rgba(34, 197, 94, 0.3)'
          
          if (confidence < 0.70) {
            color = 'rgba(239, 68, 68, 0.15)' // Red for low confidence
            borderColor = 'rgba(239, 68, 68, 0.4)'
          } else if (confidence < 0.85) {
            color = 'rgba(234, 179, 8, 0.12)' // Yellow for medium confidence
            borderColor = 'rgba(234, 179, 8, 0.35)'
          }
          
          decorations.push({
            range: {
              startLineNumber: lineMetadata.lineNumber,
              startColumn: 1,
              endLineNumber: lineMetadata.lineNumber,
              endColumn: 1000
            },
            options: {
              className: 'confidence-decoration',
              inlineClassName: 'confidence-inline',
              hoverMessage: {
                value: `Confidence: ${(confidence * 100).toFixed(0)}% | ${lineMetadata.actor === 'ai' ? 'AI' : 'Human'}-generated`
              },
              glyphMarginClassName: lineMetadata.actor === 'ai' ? 'ai-line-indicator' : 'human-line-indicator',
              minimap: {
                color: confidence >= 0.85 ? '#22c55e' : confidence >= 0.70 ? '#eab308' : '#ef4444',
                position: monaco.editor.MinimapPosition.Inline
              }
            }
          })
        }
      })
      
      decorationIds = editor.deltaDecorations(decorationIds, decorations)
    }
    
    // Register Code Lens Provider for AI operations
    const currentLanguage = selectedLanguageRef.current
    
    // Dispose of previous providers if they exist
    if (codeLensProviderRef.current) {
      codeLensProviderRef.current.dispose()
      codeLensProviderRef.current = null
    }
    if (hoverProviderRef.current) {
      hoverProviderRef.current.dispose()
      hoverProviderRef.current = null
    }
    
    if (currentLanguage && enableAdvancedFeatures) {
      try {
        // Only register if codeLens is enabled in options
        codeLensProviderRef.current = monaco.languages.registerCodeLensProvider(currentLanguage, {
          provideCodeLens: (model) => {
            if (!enableAdvancedFeatures) return []
            const codeLenses: monaco.languages.CodeLens[] = []
            const lines = model.getLinesContent()
            const metadata = codeLineMetadataRef.current
            
            lines.forEach((line, index) => {
              const lineNum = index + 1
              const lineMetadata = metadata[lineNum]
              
              if (lineMetadata && lineMetadata.actor === 'ai' && lineMetadata.confidence) {
                codeLenses.push({
                  range: {
                    startLineNumber: lineNum,
                    startColumn: 1,
                    endLineNumber: lineNum,
                    endColumn: line.length + 1
                  },
                  id: `ai-lens-${lineNum}`,
                  command: {
                    id: 'show-evidence',
                    title: `🤖 Generated by ${lineMetadata.actorName} @ ${(lineMetadata.confidence * 100).toFixed(0)}% confidence`,
                    arguments: [lineMetadata]
                  }
                })
              }
            })
            
            return codeLenses
          },
          resolveCodeLens: (codeLens) => {
            return codeLens
          }
        })
        
        // Register Hover Provider for evidence trails
        hoverProviderRef.current = monaco.languages.registerHoverProvider(currentLanguage, {
          provideHover: (model, position) => {
            if (!enableAdvancedFeatures) return null
            const lineNum = position.lineNumber
            const metadata = codeLineMetadataRef.current
            const lineMetadata = metadata[lineNum]
            
            if (lineMetadata && lineMetadata.evidence && lineMetadata.evidence.length > 0) {
              const evidenceList = lineMetadata.evidence.map(e => 
                `• ${e.name}: ${e.summary} (${(e.confidence * 100).toFixed(0)}%)`
              ).join('\n')
              
              return {
                range: {
                  startLineNumber: lineNum,
                  startColumn: 1,
                  endLineNumber: lineNum,
                  endColumn: model.getLineLength(lineNum) + 1
                },
                contents: [
                  {
                    value: `**${lineMetadata.actor === 'ai' ? '🤖' : '👤'} ${lineMetadata.actorName}**\n\n` +
                           `Confidence: ${lineMetadata.confidence ? (lineMetadata.confidence * 100).toFixed(0) : 'N/A'}%\n\n` +
                           `**Evidence Trails:**\n${evidenceList}`
                  }
                ]
              }
            }
            
            return null
          }
        })
      } catch (error) {
        console.warn('Failed to register Monaco providers:', error)
      }
    }
    
    // Initial decoration update
    updateDecorations()
    
    // Handle glyph margin clicks for notes
    const mouseDownDisposable = editor.onMouseDown((e) => {
      if (e.target.type === monaco.editor.MouseTargetType.GUTTER_GLYPH_MARGIN) {
        const lineNumber = e.target.position?.lineNumber
        if (lineNumber) {
          // Check if clicking on note indicator or empty glyph margin
          const targetElement = e.target.element as HTMLElement
          if (targetElement?.classList.contains('note-indicator') || !targetElement) {
            // Open notes panel for this line
            setEditingNoteLine(lineNumber)
            setEditingNoteContent('')
          }
        }
      }
    })
    
    // Update decorations when code changes (reuse model from above)
    if (model) {
      const disposable = model.onDidChangeContent(() => {
        // Debounce decoration updates
        setTimeout(updateDecorations, 100)
        updateNoteDecorations()
      })
      
      return () => {
        disposable.dispose()
        mouseDownDisposable.dispose()
        if (codeLensProviderRef.current) {
          codeLensProviderRef.current.dispose()
          codeLensProviderRef.current = null
        }
        if (hoverProviderRef.current) {
          hoverProviderRef.current.dispose()
          hoverProviderRef.current = null
        }
        editor.deltaDecorations(decorationIds, [])
        editor.deltaDecorations(noteDecorationIds, [])
      }
    }
    
    return () => {
      mouseDownDisposable.dispose()
      if (codeLensProviderRef.current) {
        codeLensProviderRef.current.dispose()
        codeLensProviderRef.current = null
      }
      if (hoverProviderRef.current) {
        hoverProviderRef.current.dispose()
        hoverProviderRef.current = null
      }
      editor.deltaDecorations(decorationIds, [])
      editor.deltaDecorations(noteDecorationIds, [])
    }
  }, [enableAdvancedFeatures, propSelectedLanguage, lineNotes]) // Removed showLineNumbers and showGlyphMargin to prevent infinite loops
  
  // Update note decorations when lineNotes changes
  useEffect(() => {
    if (editorRef.current && enableAdvancedFeatures && showNotesColumn) {
      const editor = editorRef.current
      const decorations: monaco.editor.IModelDeltaDecoration[] = []
      
      Object.entries(lineNotes).forEach(([lineNumStr, notes]) => {
        const lineNum = parseInt(lineNumStr)
        if (notes.length > 0) {
          decorations.push({
            range: {
              startLineNumber: lineNum,
              startColumn: 1,
              endLineNumber: lineNum,
              endColumn: 1
            },
            options: {
              glyphMarginClassName: 'note-indicator',
              glyphMarginHoverMessage: {
                value: `Notes (${notes.length}): ${notes.map(n => n.content.substring(0, 50)).join('; ')}`
              },
              stickiness: monaco.editor.TrackedRangeStickiness.NeverGrowsWhenTypingAtEdges
            }
          })
        }
      })
      
      // Get existing note decorations and replace them
      const existingDecorations = editor.getModel()?.getAllDecorations() || []
      const noteDecorationIds = existingDecorations
        .filter(d => d.options.glyphMarginClassName === 'note-indicator')
        .map(d => d.id)
      
      editor.deltaDecorations(noteDecorationIds, decorations)
    } else if (editorRef.current && !showNotesColumn) {
      // Remove all note decorations when notes column is hidden
      const editor = editorRef.current
      const existingDecorations = editor.getModel()?.getAllDecorations() || []
      const noteDecorationIds = existingDecorations
        .filter(d => d.options.glyphMarginClassName === 'note-indicator')
        .map(d => d.id)
      editor.deltaDecorations(noteDecorationIds, [])
    }
  }, [lineNotes, enableAdvancedFeatures, showNotesColumn])
  
  // Update decorations when metadata changes
  useEffect(() => {
    if (editorRef.current && enableAdvancedFeatures && showGlyphMargin) {
      const editor = editorRef.current
      const decorations: monaco.editor.IModelDeltaDecoration[] = []
      
      Object.values(codeLineMetadata).forEach((lineMetadata) => {
        if (lineMetadata.confidence !== undefined) {
          const confidence = lineMetadata.confidence
          let color = 'rgba(34, 197, 94, 0.1)' // Green for high confidence
          
          if (confidence < 0.70) {
            color = 'rgba(239, 68, 68, 0.15)' // Red for low confidence
          } else if (confidence < 0.85) {
            color = 'rgba(234, 179, 8, 0.12)' // Yellow for medium confidence
          }
          
          decorations.push({
            range: {
              startLineNumber: lineMetadata.lineNumber,
              startColumn: 1,
              endLineNumber: lineMetadata.lineNumber,
              endColumn: 1000
            },
            options: {
              className: 'confidence-decoration',
              hoverMessage: {
                value: `Confidence: ${(confidence * 100).toFixed(0)}% | ${lineMetadata.actor === 'ai' ? 'AI' : 'Human'}-generated`
              },
              glyphMarginClassName: lineMetadata.actor === 'ai' ? 'ai-line-indicator' : 'human-line-indicator',
              minimap: {
                color: confidence >= 0.85 ? '#22c55e' : confidence >= 0.70 ? '#eab308' : '#ef4444',
                position: 1 // monaco.editor.MinimapPosition.Inline
              }
            }
          })
        }
      })
      
      editor.deltaDecorations([], decorations)
    } else if (editorRef.current && !showGlyphMargin) {
      // Remove all glyph margin decorations when glyph margin is hidden
      const editor = editorRef.current
      const existingDecorations = editor.getModel()?.getAllDecorations() || []
      const glyphDecorationIds = existingDecorations
        .filter(d => d.options.glyphMarginClassName && d.options.glyphMarginClassName !== 'note-indicator')
        .map(d => d.id)
      editor.deltaDecorations(glyphDecorationIds, [])
    }
  }, [codeLineMetadata, enableAdvancedFeatures, showGlyphMargin])
  
  // Update editor options when visibility toggles change
  useEffect(() => {
    if (editorRef.current) {
      const editor = editorRef.current
      const model = editor.getModel()
      
      // Update line numbers
      editor.updateOptions({
        lineNumbers: showLineNumbers ? 'on' : 'off',
        glyphMargin: showGlyphMargin
      })
      
      // Update line numbers width if showing line numbers
      if (model && showLineNumbers) {
        const lineCount = model.getLineCount()
        const minChars = Math.max(3, Math.ceil(Math.log10(lineCount + 1)))
        editor.updateOptions({
          lineNumbersMinChars: minChars
        })
      }
    }
  }, [showLineNumbers, showGlyphMargin])
  
  // Add CSS for decorations
  useEffect(() => {
    const style = document.createElement('style')
    style.textContent = `
      .confidence-decoration {
        background: rgba(34, 197, 94, 0.05) !important;
        border-left: 2px solid rgba(34, 197, 94, 0.3) !important;
      }
      .ai-line-indicator::before {
        content: '🤖';
        font-size: 10px;
        margin-right: 4px;
      }
      .human-line-indicator::before {
        content: '👤';
        font-size: 10px;
        margin-right: 4px;
      }
      .note-indicator::before {
        content: '📝';
        font-size: 12px;
        cursor: pointer;
        opacity: 0.7;
      }
      .note-indicator:hover::before {
        opacity: 1;
      }
    `
    document.head.appendChild(style)
    return () => document.head.removeChild(style)
  }, [])
  
  return (
    <div className="h-full flex flex-col bg-gray-950">
      
      {/* Connected Files & Git History Section */}
      <div className="px-4 py-2 border-b border-gray-700 bg-gray-900/50">
        <div className="flex items-center gap-3 flex-wrap">
          {/* History Dropdown */}
          <div className="relative history-dropdown">
              <button
              onClick={() => setShowHistoryDropdown(!showHistoryDropdown)}
                className={`px-2 py-1 rounded text-xs flex items-center gap-1 transition-colors ${
                showHistoryDropdown 
                    ? 'bg-purple-900/50 text-purple-300' 
                    : 'text-gray-400 hover:bg-gray-800'
                }`}
              >
              <History className="w-3 h-3" />
              History ({fileHistory.length})
              <ChevronDown className={`w-3 h-3 transition-transform ${showHistoryDropdown ? 'rotate-180' : ''}`} />
              </button>
              
            {/* History Dropdown Menu */}
            {showHistoryDropdown && (
              <div className="absolute top-full left-0 mt-1 bg-gray-900 border border-gray-700 rounded shadow-lg z-50 min-w-[500px] max-w-[700px] max-h-[500px] overflow-y-auto">
                <div className="px-3 py-2 border-b border-gray-700 flex items-center justify-between sticky top-0 bg-gray-900">
                    <div className="flex items-center gap-2">
                    <History className="w-4 h-4 text-purple-400" />
                    <span className="text-sm font-semibold text-gray-200">File History ({fileHistory.length})</span>
                    </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-500">
                      Edit: {fileHistory.filter(h => h.type === 'edit').length} • 
                      Open: {fileHistory.filter(h => h.type === 'open').length}
                    </span>
                    <button
                      onClick={() => setShowHistoryDropdown(false)}
                      className="text-gray-400 hover:text-gray-300"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                  </div>
                  <div className="p-2 space-y-1">
                  {fileHistory.length === 0 ? (
                    <div className="p-4 text-center text-gray-500 text-sm">
                      No history available
                    </div>
                  ) : (
                    fileHistory.map((entry) => {
                      const timeAgo = Math.floor((Date.now() - entry.timestamp.getTime()) / 1000)
                      const minutesAgo = Math.floor(timeAgo / 60)
                      const hoursAgo = Math.floor(minutesAgo / 60)
                      const timeDisplay = hoursAgo > 0 
                        ? `${hoursAgo}h ago` 
                        : minutesAgo > 0 
                        ? `${minutesAgo}m ago` 
                        : `${timeAgo}s ago`
                      
                      return (
                      <div
                          key={entry.id}
                        onClick={() => {
                            if (onFileSelect && entry.type === 'open') {
                              const file = openFiles.find(f => f.path === entry.filePath)
                              if (file) {
                            onFileSelect(file.id)
                          }
                            }
                            setShowHistoryDropdown(false)
                        }}
                          className={`p-3 rounded border transition-colors cursor-pointer ${
                            entry.type === 'edit'
                              ? 'bg-blue-900/20 border-blue-700/30 hover:bg-blue-900/30'
                              : 'bg-purple-900/20 border-purple-700/30 hover:bg-purple-900/30'
                        }`}
                      >
                          <div className="flex items-start justify-between gap-3">
                            <div className="flex items-start gap-2 flex-1 min-w-0">
                              {/* Type Icon */}
                              <div className={`mt-0.5 flex-shrink-0 ${
                                entry.type === 'edit' ? 'text-blue-400' : 'text-purple-400'
                              }`}>
                                {entry.type === 'edit' ? (
                                  <Edit className="w-4 h-4" />
                                ) : (
                                  <FileText className="w-4 h-4" />
                            )}
                              </div>
                              
                              {/* Content */}
                            <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2 mb-1">
                                  <span className="text-xs font-semibold text-gray-200 truncate">
                                    {entry.fileName}
                                  </span>
                                  {entry.isGitVersion && (
                                    <GitBranch className="w-3 h-3 text-green-400 flex-shrink-0" />
                                  )}
                                </div>
                                <div className="text-[10px] text-gray-500 truncate mb-1">
                                  {entry.filePath}
                                </div>
                                
                                {/* Actor Info */}
                                <div className="flex items-center gap-2 mb-1">
                                  <div className={`flex items-center gap-1 ${
                                    entry.actor === 'ai' ? 'text-blue-400' : 'text-green-400'
                                  }`}>
                                    {entry.actor === 'ai' ? (
                                      <Bot className="w-3 h-3" />
                                    ) : (
                                      <User className="w-3 h-3" />
                                    )}
                                    <span className="text-[10px] font-medium">
                                      {entry.actorName}
                                    </span>
                            </div>
                                  <span className="text-gray-600">•</span>
                                  <span className="text-[10px] text-gray-500">
                                    {timeDisplay}
                                  </span>
                                  <span className="text-gray-600">•</span>
                                  <span className="text-[10px] text-gray-500">
                                    {entry.timestamp.toLocaleTimeString()}
                                  </span>
                          </div>
                                
                                {/* Details */}
                                {entry.details && (
                                  <div className="text-[10px] text-gray-400 mt-1 italic">
                                    {entry.details}
                                  </div>
                                )}
                                
                                {/* Commit */}
                                {entry.commit && (
                                  <div className="text-[10px] text-gray-500 font-mono mt-1">
                                    {entry.commit.substring(0, 7)}
                        </div>
                                )}
                      </div>
                  </div>
                            
                            {/* Action Button */}
                            {entry.type === 'open' && (
                              <button
                                onClick={(e) => {
                                  e.stopPropagation()
                                  const file = openFiles.find(f => f.path === entry.filePath)
                                  if (file && onFileSelect) {
                                    onFileSelect(file.id)
                                  }
                                  setShowHistoryDropdown(false)
                                }}
                                className="px-2 py-1 text-[10px] bg-purple-900/50 text-purple-300 rounded hover:bg-purple-900/70 flex items-center gap-1 flex-shrink-0"
                                title="Open file"
                              >
                                <ExternalLink className="w-3 h-3" />
                                Open
                              </button>
                            )}
                </div>
                        </div>
                      )
                    })
              )}
                </div>
            </div>
          )}
          </div>
          
          {/* Git History Dropdown */}
          <div className="relative">
            <button
              onClick={() => {
                setShowGitHistory(!showGitHistory)
                if (!showGitHistory) setShowCreateBranch(false) // Close create branch when opening history
              }}
              className={`px-2 py-1 rounded text-xs flex items-center gap-1 transition-colors ${
                showGitHistory 
                  ? 'bg-green-900/50 text-green-300' 
                  : 'text-gray-400 hover:bg-gray-800'
              }`}
            >
              <GitBranch className="w-3 h-3" />
              Git History ({gitHistory.length})
              <ChevronDown className={`w-3 h-3 transition-transform ${showGitHistory ? 'rotate-180' : ''}`} />
            </button>
            
            {showGitHistory && (
              <div className="absolute top-full left-0 mt-1 bg-gray-900 border border-gray-700 rounded shadow-lg z-50 max-h-64 overflow-y-auto min-w-[400px]">
                {gitHistory.map((commit, idx) => (
                  <div
                    key={idx}
                    className="px-3 py-2 border-b border-gray-800 hover:bg-gray-800 cursor-pointer"
                    onClick={() => {
                      if (onOpenFileInTabs) {
                        const selectedCommit = gitHistory[idx]
                        const nextCommit = idx > 0 ? gitHistory[idx - 1] : null // Next newer version (idx-1 is newer)
                        
                        // Set git version content
                        if (selectedCommit.content) {
                          setGitVersionContent(selectedCommit.content)
                        }
                        
                        // Set next version content for diff (or current code if no next version)
                        if (nextCommit?.content) {
                          setNextVersionContent(nextCommit.content)
                        } else {
                          setNextVersionContent(code) // Use current code as "newer" version
                        }
                        
                        setSelectedGitVersion(selectedCommit.commit)
                        setShowDiffView(true) // Show diff view
                        setShowGitHistory(false)
                        
                        onOpenFileInTabs({
                          id: `git-${selectedCommit.commit}`,
                          path: 'src/panels/CodeEditor.tsx', // Current file path
                          name: `CodeEditor.tsx @ ${selectedCommit.commit.substring(0, 7)}`,
                          commit: selectedCommit.commit,
                          isGitVersion: true
                        })
                      }
                    }}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs font-mono text-blue-400">{commit.commit.substring(0, 7)}</span>
                      <span className="text-[10px] text-gray-500">
                        {Math.floor((Date.now() - commit.date.getTime()) / 1000 / 60)}m ago
                      </span>
                    </div>
                    <div className="text-xs text-gray-300 mb-1">{commit.message}</div>
                    <div className="text-[10px] text-gray-500">{commit.author} • {commit.date.toLocaleString()}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
          
          {/* Create Branch Button */}
          <div className="relative create-branch-panel">
            <button
              onClick={() => {
                setShowCreateBranch(!showCreateBranch)
                if (!showCreateBranch) setShowGitHistory(false) // Close git history when opening create branch
              }}
              className={`px-2 py-1 rounded text-xs flex items-center gap-1 transition-colors ${
                showCreateBranch 
                  ? 'bg-green-900/50 text-green-300' 
                  : 'text-gray-400 hover:bg-gray-800'
              }`}
              title="Create new branch"
            >
              <Plus className="w-3 h-3" />
              <GitBranch className="w-3 h-3" />
              <ChevronDown className={`w-3 h-3 transition-transform ${showCreateBranch ? 'rotate-180' : ''}`} />
            </button>
            
            {/* Create Branch Panel */}
            {showCreateBranch && (
              <div className="absolute top-full left-0 mt-1 bg-gray-900 border border-gray-700 rounded shadow-lg z-50 min-w-[450px] max-w-[600px]">
                <div className="px-4 py-3 border-b border-gray-700 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <GitBranch className="w-4 h-4 text-green-400" />
                    <span className="text-sm font-semibold text-gray-200">Create New Branch</span>
                  </div>
                  <button
                    onClick={() => setShowCreateBranch(false)}
                    className="text-gray-400 hover:text-gray-300"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
                
                <div className="p-4 space-y-4">
                  {/* Branch Name */}
                  <div>
                    <label className="block text-xs font-medium text-gray-300 mb-1.5">
                      Branch Name <span className="text-red-400">*</span>
                    </label>
                    <input
                      type="text"
                      value={newBranchName}
                      onChange={(e) => setNewBranchName(e.target.value)}
                      placeholder="feature/new-feature"
                      className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded text-sm text-gray-200 placeholder-gray-500 focus:outline-none focus:border-green-500 focus:ring-1 focus:ring-green-500"
                    />
                    <p className="text-[10px] text-gray-500 mt-1">
                      Use lowercase letters, numbers, hyphens, and underscores
                    </p>
                  </div>
                  
                  {/* Base Branch */}
                  <div>
                    <label className="block text-xs font-medium text-gray-300 mb-1.5">
                      Base Branch
                    </label>
                    <select
                      value={newBranchBase}
                      onChange={(e) => setNewBranchBase(e.target.value)}
                      className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded text-sm text-gray-200 focus:outline-none focus:border-green-500 focus:ring-1 focus:ring-green-500"
                    >
                      <option value="main">main</option>
                      <option value="develop">develop</option>
                      <option value="master">master</option>
                      {gitHistory.length > 0 && (
                        <option value={gitHistory[0].commit}>{gitHistory[0].commit.substring(0, 7)} - {gitHistory[0].message}</option>
                      )}
                    </select>
                    <p className="text-[10px] text-gray-500 mt-1">
                      Branch will be created from this base
                    </p>
                  </div>
                  
                  {/* Description */}
                  <div>
                    <label className="block text-xs font-medium text-gray-300 mb-1.5">
                      Description <span className="text-gray-500">(Optional)</span>
                    </label>
                    <textarea
                      value={newBranchDescription}
                      onChange={(e) => setNewBranchDescription(e.target.value)}
                      placeholder="Describe what this branch is for..."
                      rows={3}
                      className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded text-sm text-gray-200 placeholder-gray-500 focus:outline-none focus:border-green-500 focus:ring-1 focus:ring-green-500 resize-none"
                    />
                  </div>
                  
                  {/* Current File Info */}
                  <div className="p-2 bg-gray-800/50 rounded border border-gray-700/50">
                    <div className="text-[10px] text-gray-400 mb-1">Current File:</div>
                    <div className="text-xs text-gray-300 font-mono">src/panels/CodeEditor.tsx</div>
                    {selectedGitVersion && (
                      <div className="text-[10px] text-gray-500 mt-1">
                        Based on commit: {selectedGitVersion.substring(0, 7)}
                      </div>
                    )}
                  </div>
                  
                  {/* Actions */}
                  <div className="flex items-center gap-2 pt-2 border-t border-gray-700">
                    <button
                      onClick={() => {
                        if (newBranchName.trim()) {
                          // Mock: Create branch - in real implementation, this would call git API
                          console.log('Creating branch:', {
                            name: newBranchName,
                            base: newBranchBase,
                            description: newBranchDescription,
                            currentFile: 'src/panels/CodeEditor.tsx',
                            fromCommit: selectedGitVersion
                          })
                          // Reset form
                          setNewBranchName('')
                          setNewBranchDescription('')
                          setNewBranchBase('main')
                          setShowCreateBranch(false)
                          // In real implementation: Show success message, refresh git history, switch to new branch
                        }
                      }}
                      disabled={!newBranchName.trim()}
                      className={`px-4 py-2 rounded text-xs font-medium transition-colors flex items-center gap-2 ${
                        newBranchName.trim()
                          ? 'bg-green-900/50 text-green-300 hover:bg-green-900/70'
                          : 'bg-gray-800 text-gray-500 cursor-not-allowed'
                      }`}
                    >
                      <Plus className="w-3 h-3" />
                      Create Branch
                    </button>
                    <button
                      onClick={() => {
                        setNewBranchName('')
                        setNewBranchDescription('')
                        setNewBranchBase('main')
                        setShowCreateBranch(false)
                      }}
                      className="px-4 py-2 rounded text-xs font-medium bg-gray-800 text-gray-300 hover:bg-gray-700"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
          
          {/* Connections Dropdown */}
          <div className="relative connections-dropdown">
            <button
              onClick={() => setShowConnections(!showConnections)}
              className={`px-2 py-1 rounded text-xs flex items-center gap-1 transition-colors ${
                showConnections 
                  ? 'bg-blue-900/50 text-blue-300' 
                  : 'text-gray-400 hover:bg-gray-800'
              }`}
            >
              <Link2 className="w-3 h-3" />
              Connections ({connectedFiles.length})
              <ChevronDown className={`w-3 h-3 transition-transform ${showConnections ? 'rotate-180' : ''}`} />
            </button>
            
            {/* Connections Dropdown Menu */}
            {showConnections && connectedFiles.length > 0 && (
              <div className="absolute top-full left-0 mt-1 bg-gray-900 border border-gray-700 rounded shadow-lg z-50 min-w-[400px] max-w-[600px] max-h-[400px] overflow-y-auto">
                <div className="px-3 py-2 border-b border-gray-700 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Link2 className="w-4 h-4 text-blue-400" />
                    <span className="text-sm font-semibold text-gray-200">Connected Files ({connectedFiles.length})</span>
                  </div>
                  <button
                    onClick={() => setShowConnections(false)}
                    className="text-gray-400 hover:text-gray-300"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
                <div className="p-2 space-y-1">
                  {connectedFiles.map((file, idx) => {
                    const getTypeIcon = () => {
                      switch (file.type) {
                        case 'import': return { icon: '↓', color: 'text-blue-400 bg-blue-900/30' }
                        case 'export': return { icon: '↑', color: 'text-green-400 bg-green-900/30' }
                        case 'reference': return { icon: '↗', color: 'text-purple-400 bg-purple-900/30' }
                        case 'dependency': return { icon: '→', color: 'text-yellow-400 bg-yellow-900/30' }
                        default: return { icon: '•', color: 'text-gray-400 bg-gray-800/30' }
                      }
                    }
                    const typeInfo = getTypeIcon()
                    
                    return (
                      <div
                        key={idx}
                        className="p-2 bg-gray-800/50 rounded border border-gray-700/50 hover:bg-gray-800 transition-colors cursor-pointer"
                        onClick={() => setSelectedFileDetails(selectedFileDetails === file.path ? null : file.path)}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex items-center gap-2 flex-1">
                            <span className={`w-4 h-4 rounded flex items-center justify-center text-[10px] ${typeInfo.color}`}>
                              {typeInfo.icon}
                            </span>
                            <div className="flex-1 min-w-0">
                              <div className="text-xs font-semibold text-gray-200 truncate">{file.name}</div>
                              <div className="text-[10px] text-gray-500 truncate">{file.path}</div>
                              <div className="text-[10px] text-gray-400 mt-0.5">
                                Lines: {file.lines.join(', ')} • Type: {file.type}
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center gap-1 ml-2">
                            <button
                              onClick={(e) => {
                                e.stopPropagation()
                                if (onOpenFileInTabs) {
                                  onOpenFileInTabs({
                                    id: `file-${file.path}`,
                                    path: file.path,
                                    name: file.name
                                  })
                                }
                              }}
                              className="px-2 py-1 text-[10px] bg-blue-900/50 text-blue-300 rounded hover:bg-blue-900/70 flex items-center gap-1"
                              title="Open in tabs"
                            >
                              <ExternalLink className="w-3 h-3" />
                              Open
                            </button>
                          </div>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            )}
          </div>
          
          {/* Memory Awareness - Clickable button with dropdown */}
          <div className="relative memories-details-popup">
            <button
              onClick={() => setShowMemoriesDetails(!showMemoriesDetails)}
              className={`flex items-center gap-1 px-2 py-1 rounded text-xs transition-colors ${
                showMemoriesDetails 
                  ? 'bg-blue-900/50 text-blue-300' 
                  : 'text-gray-400 hover:bg-gray-800 hover:text-gray-300'
              }`}
              title="Related memories from AIM-OS memory system (CMC) - contextual information related to current code"
            >
              <FileText className="w-3 h-3" />
              <span>Memories ({relatedMemories.length})</span>
              <ChevronDown className={`w-3 h-3 transition-transform ${showMemoriesDetails ? 'rotate-180' : ''}`} />
            </button>
              
              {/* Memories Details Dropdown */}
              {showMemoriesDetails && (
                <div className="absolute top-full left-0 mt-1 bg-gray-900 border border-gray-700 rounded shadow-lg z-50 min-w-[400px] max-w-[600px] max-h-[400px] overflow-y-auto">
                  <div className="px-3 py-2 border-b border-gray-700 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <FileText className="w-4 h-4 text-blue-400" />
                      <span className="text-sm font-semibold text-gray-200">Related Memories ({relatedMemories.length})</span>
                    </div>
                    <button
                      onClick={() => setShowMemoriesDetails(false)}
                      className="text-gray-400 hover:text-gray-300"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                  <div className="p-2 space-y-2">
                    {relatedMemories.length === 0 ? (
                      <div className="p-4 text-center text-gray-500 text-sm">
                        No memories available yet
                      </div>
                    ) : (
                      relatedMemories.map((memory, idx) => (
                      <div key={memory.id || idx} className="p-2 bg-gray-800/50 rounded border border-gray-700/50 hover:bg-gray-800 transition-colors">
                        <div className="flex items-start justify-between mb-1">
                          <div className="flex-1">
                            <div className="text-xs font-semibold text-gray-200 mb-1">
                              {memory.content || `Memory ${idx + 1}`}
                            </div>
                            {memory.timestamp && (
                              <div className="text-[10px] text-gray-500 mb-1">
                                {new Date(memory.timestamp).toLocaleString()}
                              </div>
                            )}
                            {memory.confidence !== undefined && (
                              <div className="text-[10px] text-gray-400">
                                Confidence: {(memory.confidence * 100).toFixed(0)}%
                              </div>
                            )}
                          </div>
                          <button
                            onClick={() => {
                              // Mock: Open full memory view in CMC
                              console.log('Open memory in CMC:', memory.id)
                              // In real implementation: navigate to CMC memory browser with this memory selected
                            }}
                            className="px-2 py-1 text-[10px] bg-blue-900/50 text-blue-300 rounded hover:bg-blue-900/70 flex items-center gap-1 ml-2"
                            title="View full memory in CMC"
                          >
                            <ExternalLink className="w-3 h-3" />
                            View
                          </button>
                        </div>
                      </div>
                      ))
                    )}
                  </div>
                  {relatedMemories.length > 0 && (
                    <div className="px-3 py-2 border-t border-gray-700 bg-gray-800/30">
                      <button
                        onClick={() => {
                          // Mock: Open CMC memory browser
                          console.log('Open CMC Memory Browser')
                          // In real implementation: navigate to full CMC memory browser panel
                        }}
                        className="w-full px-3 py-1 text-xs bg-blue-900/50 text-blue-300 rounded hover:bg-blue-900/70 flex items-center justify-center gap-2"
                      >
                        <FileText className="w-3 h-3" />
                        View All Memories in CMC Browser
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          
          {/* Evidence Trails - Dropdown button */}
          <div className="relative evidence-details-popup">
            <button
              onClick={() => setShowEvidencePanel(!showEvidencePanel)}
              className={`flex items-center gap-1 px-2 py-1 rounded text-xs transition-colors ${
                showEvidencePanel 
                  ? 'bg-purple-900/50 text-purple-300' 
                  : 'text-gray-400 hover:bg-gray-800 hover:text-gray-300'
              }`}
              title="Evidence trails from AIM-OS systems - VIF witnesses, SEG connections, CMC references"
            >
              <Brain className="w-3 h-3" />
              <span>Evidence ({evidenceTrails.length})</span>
              <ChevronDown className={`w-3 h-3 transition-transform ${showEvidencePanel ? 'rotate-180' : ''}`} />
            </button>
              
              {/* Evidence Details Dropdown */}
              {showEvidencePanel && (
                <div className="absolute top-full left-0 mt-1 bg-gray-900 border border-gray-700 rounded shadow-lg z-50 min-w-[400px] max-w-[600px] max-h-[400px] overflow-y-auto">
                  <div className="px-3 py-2 border-b border-gray-700 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Brain className="w-4 h-4 text-purple-400" />
                      <span className="text-sm font-semibold text-gray-200">Evidence Trails ({evidenceTrails.length})</span>
                    </div>
                    <button
                      onClick={() => setShowEvidencePanel(false)}
                      className="text-gray-400 hover:text-gray-300"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                  <div className="p-2 space-y-2">
                    {evidenceTrails.length === 0 ? (
                      <div className="p-4 text-center text-gray-500 text-sm">
                        No evidence trails available yet
                      </div>
                    ) : (
                      evidenceTrails.map((evidence, idx) => (
                      <div key={evidence.id || idx} className="p-2 bg-gray-800/50 rounded border border-gray-700/50 hover:bg-gray-800 transition-colors">
                        <div className="flex items-start justify-between mb-1">
                          <div className="flex-1">
                            <div className="text-xs font-semibold text-purple-300 mb-1">
                              {evidence.name || `Evidence ${idx + 1}`}
                            </div>
                            <div className="text-[10px] text-purple-400 mb-1">
                              {evidence.summary || 'No summary available'}
                            </div>
                            {evidence.confidence !== undefined && (
                              <div className="text-[10px] text-gray-400">
                                Confidence: <span className="text-purple-400">{(evidence.confidence * 100).toFixed(0)}%</span>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                      ))
                    )}
                  </div>
                  {evidenceTrails.length > 0 && (
                    <div className="px-3 py-2 border-t border-gray-700 bg-gray-800/30">
                      <button
                        onClick={() => {
                          // Mock: Open full evidence view
                          console.log('Open Evidence Graph')
                          // In real implementation: navigate to evidence graph panel
                        }}
                        className="w-full px-3 py-1 text-xs bg-purple-900/50 text-purple-300 rounded hover:bg-purple-900/70 flex items-center justify-center gap-2"
                      >
                        <Brain className="w-3 h-3" />
                        View All Evidence in Evidence Graph
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          
          {/* Goal Alignment - Clickable button with dropdown */}
          <div className="relative goals-details-popup">
            <button
              onClick={() => setShowGoalsDetails(!showGoalsDetails)}
              className={`flex items-center gap-1 px-2 py-1 rounded text-xs transition-colors ${
                showGoalsDetails 
                  ? 'bg-green-900/50 text-green-300' 
                  : 'text-gray-400 hover:bg-gray-800 hover:text-gray-300'
              }`}
              title="Related goals from goal tracking system - objectives/key results this code contributes to"
            >
              <Target className="w-3 h-3" />
              <span>Goals ({relatedGoals.length})</span>
              <ChevronDown className={`w-3 h-3 transition-transform ${showGoalsDetails ? 'rotate-180' : ''}`} />
            </button>
              
              {/* Goals Details Dropdown */}
              {showGoalsDetails && (
                <div className="absolute top-full left-0 mt-1 bg-gray-900 border border-gray-700 rounded shadow-lg z-50 min-w-[400px] max-w-[600px] max-h-[400px] overflow-y-auto">
                  <div className="px-3 py-2 border-b border-gray-700 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Target className="w-4 h-4 text-green-400" />
                      <span className="text-sm font-semibold text-gray-200">Related Goals ({relatedGoals.length})</span>
                    </div>
                    <button
                      onClick={() => setShowGoalsDetails(false)}
                      className="text-gray-400 hover:text-gray-300"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                  <div className="p-2 space-y-2">
                    {relatedGoals.length === 0 ? (
                      <div className="p-4 text-center text-gray-500 text-sm">
                        No related goals available yet
                      </div>
                    ) : (
                      relatedGoals.map((goal) => (
                        <div key={goal.id} className="p-2 bg-gray-800/50 rounded border border-gray-700/50 hover:bg-gray-800 transition-colors">
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex-1">
                            <div className="text-xs font-semibold text-green-300 mb-1">
                              {goal.name || `Goal ${goal.id}`}
                            </div>
                            <div className="flex items-center gap-2 mb-1">
                              <div className="flex-1 h-1.5 bg-gray-700 rounded-full overflow-hidden">
                                <div 
                                  className="h-full bg-green-500 transition-all"
                                  style={{ width: `${(goal.progress || 0) * 100}%` }}
                                />
                              </div>
                              <span className="text-[10px] text-green-400 min-w-[35px]">
                                {((goal.progress || 0) * 100).toFixed(0)}%
                              </span>
                            </div>
                            <div className="text-[10px] text-gray-400 capitalize">
                              Status: <span className="text-green-400">{goal.status || 'unknown'}</span>
                            </div>
                            {goal.id && (
                              <div className="text-[10px] text-gray-500 mt-1 font-mono">
                                ID: {goal.id}
                              </div>
                            )}
                          </div>
                          <button
                            onClick={() => {
                              // Mock: Open full goal view
                              console.log('Open goal in goal tracker:', goal.id)
                              // In real implementation: navigate to goal timeline/GOAL_TREE with this goal selected
                            }}
                            className="px-2 py-1 text-[10px] bg-green-900/50 text-green-300 rounded hover:bg-green-900/70 flex items-center gap-1 ml-2"
                            title="View full goal details"
                          >
                            <ExternalLink className="w-3 h-3" />
                            View
                          </button>
                        </div>
                      </div>
                      ))
                    )}
                  </div>
                  {relatedGoals.length > 0 && (
                    <div className="px-3 py-2 border-t border-gray-700 bg-gray-800/30">
                      <button
                        onClick={() => {
                          // Mock: Open goal timeline/GOAL_TREE
                          console.log('Open Goal Timeline')
                          // In real implementation: navigate to goal timeline panel or GOAL_TREE.yaml viewer
                        }}
                        className="w-full px-3 py-1 text-xs bg-green-900/50 text-green-300 rounded hover:bg-green-900/70 flex items-center justify-center gap-2"
                      >
                        <Target className="w-3 h-3" />
                        View All Goals in Goal Timeline
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
        </div>
      </div>
      
      {/* File Details Popup - Shows when clicking on a connected file */}
      {selectedFileDetails && fileContentCache[selectedFileDetails] && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-gray-900 border border-gray-700 rounded-lg p-6 max-w-md">
            <h3 className="text-lg font-semibold text-gray-200 mb-2">Edit Git Version Warning</h3>
            <p className="text-sm text-gray-400 mb-4">
              You are about to edit a file from git history. This will create a new branch. Do you want to continue?
            </p>
            <div className="flex items-center gap-3">
              <button
                onClick={() => {
                  setIsEditingGitVersion(true)
                  setShowGitEditWarning(false)
                }}
                className="px-4 py-2 bg-green-900/50 text-green-300 rounded hover:bg-green-900/70"
              >
                Create Branch & Edit
              </button>
              <button
                onClick={() => {
                  setShowGitEditWarning(false)
                }}
                className="px-4 py-2 bg-gray-800 text-gray-300 rounded hover:bg-gray-700"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
      
      {/* File Details Popup - Shows when clicking on a connected file */}
      {selectedFileDetails && fileContentCache[selectedFileDetails] && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setSelectedFileDetails(null)}>
          <div className="bg-gray-900 border border-gray-700 rounded shadow-xl max-w-[90vw] max-h-[90vh] flex flex-col" onClick={(e) => e.stopPropagation()}>
            {/* Header */}
            <div className="px-4 py-3 border-b border-gray-700 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-gray-400" />
                <div>
                  <div className="text-sm text-gray-300 font-semibold">{selectedFileDetails}</div>
                  <div className="text-xs text-gray-500">
                    {connectedFiles.find(f => f.path === selectedFileDetails)?.lines.join(', ')} • Type: {connectedFiles.find(f => f.path === selectedFileDetails)?.type}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => {
                    if (onOpenFileInTabs) {
                      onOpenFileInTabs({
                        id: `file-${selectedFileDetails}`,
                        path: selectedFileDetails,
                        name: connectedFiles.find(f => f.path === selectedFileDetails)?.name || selectedFileDetails
                      })
                    }
                  }}
                  className="px-3 py-1.5 text-xs bg-blue-900/50 text-blue-300 rounded hover:bg-blue-900/70 flex items-center gap-1"
                  title="Open in tabs"
                >
                  <ExternalLink className="w-4 h-4" />
                  Open in Tabs
                </button>
                <button
                  onClick={() => setSelectedFileDetails(null)}
                  className="text-gray-400 hover:text-gray-300"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>
            
            {/* Code Editor Section */}
            <div className="flex-1 overflow-hidden flex flex-col min-h-0">
              <div className="px-4 py-2 bg-gray-800/50 border-b border-gray-700 text-xs text-gray-400">
                Code Editor - Edit related code
              </div>
              <div className="flex-1 min-h-0" style={{ height: '500px' }}>
                <Editor
                  height="100%"
                  defaultLanguage="typescript"
                  value={fileContentCache[selectedFileDetails].content}
                  onChange={(value) => {
                    setFileContentCache(prev => ({
                      ...prev,
                      [selectedFileDetails]: {
                        ...prev[selectedFileDetails],
                        content: value || ''
                      }
                    }))
                  }}
                  theme="aimos-dark"
                  options={{
                    minimap: { enabled: false },
                    fontSize: 12,
                    lineNumbers: 'on',
                    scrollBeyondLastLine: false,
                    readOnly: false,
                    automaticLayout: true,
                    wordWrap: 'on',
                    padding: { top: 8, bottom: 8 },
                    scrollbar: {
                      vertical: 'auto',
                      horizontal: 'auto',
                      verticalScrollbarSize: 4,
                      horizontalScrollbarSize: 4,
                    }
                  }}
                />
              </div>
            </div>
            
            {/* Nested Connections */}
            {fileContentCache[selectedFileDetails]?.nestedConnections && fileContentCache[selectedFileDetails].nestedConnections.length > 0 && (
              <div className="border-t border-gray-700 p-3 bg-gray-800/30">
                <div className="text-xs text-gray-400 mb-2 font-semibold">
                  Related Files ({fileContentCache[selectedFileDetails].nestedConnections.length})
                </div>
                <div className="flex flex-wrap gap-2">
                  {fileContentCache[selectedFileDetails].nestedConnections.map((nested: {
                    path: string
                    name: string
                    lines: number[]
                    type: 'import' | 'export' | 'reference' | 'dependency'
                  }, nestedIdx: number) => {
                    const getTypeIcon = () => {
                      switch (nested.type) {
                        case 'import': return { icon: '↓', color: 'text-blue-400 bg-blue-900/30' }
                        case 'export': return { icon: '↑', color: 'text-green-400 bg-green-900/30' }
                        case 'reference': return { icon: '↗', color: 'text-purple-400 bg-purple-900/30' }
                        case 'dependency': return { icon: '→', color: 'text-yellow-400 bg-yellow-900/30' }
                        default: return { icon: '•', color: 'text-gray-400 bg-gray-800/30' }
                      }
                    }
                    const typeInfo = getTypeIcon()
                    return (
                      <button
                        key={nestedIdx}
                        onClick={() => {
                          setSelectedFileDetails(nested.path)
                        }}
                        className="flex items-center gap-1 px-2 py-1 rounded text-xs bg-gray-800/50 hover:bg-gray-800 cursor-pointer"
                      >
                        <span className={`w-4 h-4 rounded flex items-center justify-center text-[10px] ${typeInfo.color}`}>
                          {typeInfo.icon}
                        </span>
                        <span className="text-gray-300">{nested.name}</span>
                        <span className="text-gray-500">:{nested.lines[0]}</span>
                      </button>
                    )
                  })}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
      
      {/* File Details Popup - Shows when clicking on a connected file */}
      {selectedFileDetails && fileContentCache[selectedFileDetails] && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setSelectedFileDetails(null)}>
          <div className="bg-gray-900 border border-gray-700 rounded shadow-xl max-w-[90vw] max-h-[90vh] flex flex-col" onClick={(e) => e.stopPropagation()}>
            {/* Header */}
            <div className="px-4 py-3 border-b border-gray-700 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-gray-400" />
                <div>
                  <div className="text-sm text-gray-300 font-semibold">{selectedFileDetails}</div>
                  <div className="text-xs text-gray-500">
                    {connectedFiles.find(f => f.path === selectedFileDetails)?.lines.join(', ')} • Type: {connectedFiles.find(f => f.path === selectedFileDetails)?.type}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => {
                    if (onOpenFileInTabs) {
                      onOpenFileInTabs({
                        id: `file-${selectedFileDetails}`,
                        path: selectedFileDetails,
                        name: connectedFiles.find(f => f.path === selectedFileDetails)?.name || selectedFileDetails
                      })
                    }
                  }}
                  className="px-3 py-1.5 text-xs bg-blue-900/50 text-blue-300 rounded hover:bg-blue-900/70 flex items-center gap-1"
                  title="Open in tabs"
                >
                  <ExternalLink className="w-4 h-4" />
                  Open in Tabs
                </button>
                <button
                  onClick={() => setSelectedFileDetails(null)}
                  className="text-gray-400 hover:text-gray-300"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>
            
            {/* Code Editor Section */}
            <div className="flex-1 overflow-hidden flex flex-col min-h-0">
              <div className="px-4 py-2 bg-gray-800/50 border-b border-gray-700 text-xs text-gray-400">
                Code Editor - Edit related code
              </div>
              <div className="flex-1 min-h-0" style={{ height: '500px' }}>
                <Editor
                  height="100%"
                  defaultLanguage="typescript"
                  value={fileContentCache[selectedFileDetails].content}
                  onChange={(value) => {
                    setFileContentCache(prev => ({
                      ...prev,
                      [selectedFileDetails]: {
                        ...prev[selectedFileDetails],
                        content: value || ''
                      }
                    }))
                  }}
                  theme="aimos-dark"
                  options={{
                    minimap: { enabled: false },
                    fontSize: 12,
                    lineNumbers: 'on',
                    scrollBeyondLastLine: false,
                    readOnly: false,
                    automaticLayout: true,
                    wordWrap: 'on',
                    padding: { top: 8, bottom: 8 },
                    scrollbar: {
                      vertical: 'auto',
                      horizontal: 'auto',
                      verticalScrollbarSize: 4,
                      horizontalScrollbarSize: 4,
                    }
                  }}
                />
              </div>
            </div>
            
            {/* Nested Connections */}
            {fileContentCache[selectedFileDetails]?.nestedConnections && fileContentCache[selectedFileDetails].nestedConnections.length > 0 && (
              <div className="border-t border-gray-700 p-3 bg-gray-800/30">
                <div className="text-xs text-gray-400 mb-2 font-semibold">
                  Related Files ({fileContentCache[selectedFileDetails].nestedConnections.length})
                </div>
                <div className="flex flex-wrap gap-2">
                  {fileContentCache[selectedFileDetails].nestedConnections.map((nested: {
                    path: string
                    name: string
                    lines: number[]
                    type: 'import' | 'export' | 'reference' | 'dependency'
                  }, nestedIdx: number) => {
                    const getTypeIcon = () => {
                      switch (nested.type) {
                        case 'import': return { icon: '↓', color: 'text-blue-400 bg-blue-900/30' }
                        case 'export': return { icon: '↑', color: 'text-green-400 bg-green-900/30' }
                        case 'reference': return { icon: '↗', color: 'text-purple-400 bg-purple-900/30' }
                        case 'dependency': return { icon: '→', color: 'text-yellow-400 bg-yellow-900/30' }
                        default: return { icon: '•', color: 'text-gray-400 bg-gray-800/30' }
                      }
                    }
                    const typeInfo = getTypeIcon()
                    return (
                      <button
                        key={nestedIdx}
                        onClick={() => {
                          setSelectedFileDetails(nested.path)
                        }}
                        className="flex items-center gap-1 px-2 py-1 rounded text-xs bg-gray-800/50 hover:bg-gray-800 cursor-pointer"
                      >
                        <span className={`w-4 h-4 rounded flex items-center justify-center text-[10px] ${typeInfo.color}`}>
                          {typeInfo.icon}
                        </span>
                        <span className="text-gray-300">{nested.name}</span>
                        <span className="text-gray-500">:{nested.lines[0]}</span>
                      </button>
                    )
                  })}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
      
      {showGitEditWarning && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-gray-900 border border-gray-700 rounded-lg p-6 max-w-md">
            <h3 className="text-lg font-semibold text-gray-200 mb-2">Edit Git Version Warning</h3>
            <p className="text-sm text-gray-400 mb-4">
              You are about to edit a file from git history. This will create a new branch. Do you want to continue?
            </p>
            <div className="flex items-center gap-3">
              <button
                onClick={() => {
                  setIsEditingGitVersion(true)
                  setShowGitEditWarning(false)
                }}
                className="px-4 py-2 bg-green-900/50 text-green-300 rounded hover:bg-green-900/70"
              >
                Create Branch & Edit
              </button>
              <button
                onClick={() => {
                  setShowGitEditWarning(false)
                }}
                className="px-4 py-2 bg-gray-800 text-gray-300 rounded hover:bg-gray-700"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
      
      
      {/* Editor - Full Height */}
      <div className="flex-1 relative flex" style={{ minHeight: 0 }}>
        {/* Notes Panel - Appears when editing a note */}
        {editingNoteLine !== null && (
          <div className="w-80 bg-gray-900 border-r border-gray-700 shadow-xl overflow-y-auto flex-shrink-0">
            <div className="p-4">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <StickyNote className="w-4 h-4 text-blue-400" />
                  <h3 className="text-sm font-semibold text-gray-200">
                    Notes for Line {editingNoteLine}
                  </h3>
                </div>
                <button
                  onClick={() => {
                    setEditingNoteLine(null)
                    setEditingNoteContent('')
                  }}
                  className="text-gray-400 hover:text-gray-200"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
              
              {/* Existing Notes */}
              {getNotesForLine(editingNoteLine).length > 0 && (
                <div className="space-y-3 mb-4">
                  {getNotesForLine(editingNoteLine).map((note) => (
                    <div key={note.id} className="p-3 bg-gray-800 rounded border border-gray-700">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-2">
                          {note.author === 'ai' ? (
                            <Bot className="w-3 h-3 text-blue-400" />
                          ) : (
                            <User className="w-3 h-3 text-green-400" />
                          )}
                          <span className="text-xs text-gray-400">{note.authorName}</span>
                          <span className="text-xs text-gray-500">
                            {note.timestamp.toLocaleTimeString()}
                          </span>
                        </div>
                        <button
                          onClick={() => handleDeleteNote(editingNoteLine, note.id)}
                          className="text-gray-500 hover:text-red-400"
                          title="Delete note"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </div>
                      <p className="text-sm text-gray-300 whitespace-pre-wrap">{note.content}</p>
                    </div>
                  ))}
                </div>
              )}
              
              {/* Add New Note */}
              <div className="border-t border-gray-700 pt-4">
                <label className="block text-xs text-gray-400 mb-2">Add Note</label>
                <textarea
                  value={editingNoteContent}
                  onChange={(e) => setEditingNoteContent(e.target.value)}
                  placeholder="Enter your note here..."
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded text-sm text-gray-200 placeholder-gray-500 focus:outline-none focus:border-blue-500 resize-none"
                  rows={4}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
                      e.preventDefault()
                      handleAddNote(editingNoteLine, editingNoteContent)
                    }
                  }}
                />
                <div className="flex items-center justify-between mt-2">
                  <span className="text-xs text-gray-500">Press Ctrl+Enter to save</span>
                  <button
                    onClick={() => handleAddNote(editingNoteLine, editingNoteContent)}
                    disabled={!editingNoteContent.trim()}
                    className="px-3 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1"
                  >
                    <Plus className="w-3 h-3" />
                    Add Note
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
        
        <div className="flex-1 relative" style={{ minHeight: 0 }}>
        {showDiffView && selectedGitVersion && gitVersionContent && nextVersionContent ? (
          <>
            {/* Diff View Header */}
            <div className="px-4 py-2 border-b border-gray-700 bg-gray-900/50 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2">
                  <GitBranch className="w-4 h-4 text-green-400" />
                  <span className="text-xs font-semibold text-gray-300">Diff View</span>
            </div>
                <span className="text-gray-600">•</span>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-400">Old Version:</span>
                  <span className="text-xs font-mono text-red-400 bg-red-900/20 px-1.5 py-0.5 rounded">
                    {selectedGitVersion.substring(0, 7)}
                </span>
                  <span className="text-[10px] text-gray-500">
                    ({gitHistory.find(c => c.commit === selectedGitVersion)?.message || 'Unknown'})
                  </span>
                </div>
                <span className="text-gray-600">→</span>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-400">New Version:</span>
                  <span className="text-xs font-mono text-green-400 bg-green-900/20 px-1.5 py-0.5 rounded">
                    {(() => {
                      const currentIdx = gitHistory.findIndex(c => c.commit === selectedGitVersion)
                      return currentIdx > 0 
                        ? gitHistory[currentIdx - 1].commit.substring(0, 7)
                        : 'Current'
                    })()}
                  </span>
                  {(() => {
                    const currentIdx = gitHistory.findIndex(c => c.commit === selectedGitVersion)
                    const nextCommit = currentIdx > 0 ? gitHistory[currentIdx - 1] : null
                    return nextCommit && (
                      <span className="text-[10px] text-gray-500">
                        ({nextCommit.message})
                      </span>
                    )
                  })()}
                </div>
            </div>
              <div className="flex items-center gap-2">
                {/* Toggle Diff View Mode - Icon-only buttons */}
                <button
                  onClick={() => setDiffSideBySide(true)}
                  className={`w-7 h-7 rounded flex items-center justify-center transition-colors ${
                    diffSideBySide
                      ? 'bg-blue-900/50 text-blue-300 hover:bg-blue-900/70 border border-blue-700'
                      : 'bg-gray-800 text-gray-400 hover:bg-gray-700 border border-gray-700'
                  }`}
                  title="Side-by-side diff view"
                >
                  <Columns className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setDiffSideBySide(false)}
                  className={`w-7 h-7 rounded flex items-center justify-center transition-colors ${
                    !diffSideBySide
                      ? 'bg-blue-900/50 text-blue-300 hover:bg-blue-900/70 border border-blue-700'
                      : 'bg-gray-800 text-gray-400 hover:bg-gray-700 border border-gray-700'
                  }`}
                  title="Inline/unified diff view"
                >
                  <AlignJustify className="w-4 h-4" />
                </button>
                <button
                  onClick={() => {
                    setShowDiffView(false)
                    setSelectedGitVersion(null)
                    setGitVersionContent(null)
                    setNextVersionContent(null)
                  }}
                  className="w-7 h-7 rounded flex items-center justify-center bg-gray-800 text-red-400 hover:bg-red-900/30 hover:text-red-300 border border-red-700/50 transition-colors"
                  title="Close Diff View"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>
            
            {/* Diff Editor */}
            <DiffEditor
              height="100%"
              language={selectedLanguage}
              original={gitVersionContent}
              modified={nextVersionContent}
              theme="aimos-dark"
              options={{
                minimap: { enabled: true },
                fontSize: 14,
                lineNumbers: showLineNumbers ? 'on' : 'off',
                readOnly: true,
                automaticLayout: true,
                renderSideBySide: diffSideBySide,
                scrollBeyondLastLine: false,
                glyphMargin: showGlyphMargin,
                scrollbar: {
                  vertical: 'auto',
                  horizontal: 'auto',
                  verticalScrollbarSize: 4,
                  horizontalScrollbarSize: 4,
                },
                // Diff-specific options
                enableSplitViewResizing: diffSideBySide,
                renderOverviewRuler: true,
                diffWordWrap: 'on',
                diffCodeLens: true,
                // Enhanced diff colors
                renderIndicators: true,
                ignoreTrimWhitespace: false,
              }}
            />
          </>
        ) : (
        <>
        <Editor
          height="100%"
          language={selectedLanguage}
          value={code}
          onChange={handleCodeChange}
          theme="aimos-dark"
          onMount={handleEditorDidMount}
          options={{
            minimap: { enabled: true },
            fontSize: 14,
            lineNumbers: showLineNumbers ? 'on' : 'off',
            lineNumbersMinChars: 3, // Will be auto-adjusted in handleEditorDidMount
            roundedSelection: false,
            scrollBeyondLastLine: false,
            readOnly: false,
            automaticLayout: true,
            wordWrap: 'on',
            formatOnPaste: true,
            formatOnType: true,
            suggestOnTriggerCharacters: true,
            quickSuggestions: true,
            codeLens: enableAdvancedFeatures,
            glyphMargin: showGlyphMargin,
            scrollbar: {
              vertical: 'auto',
              horizontal: 'auto',
              verticalScrollbarSize: 4,
              horizontalScrollbarSize: 4,
            }
          }}
        />
        
        {/* SEG Contradictions Overlay */}
        {detectedContradictions.length > 0 && (
          <div className="absolute top-4 right-4 w-64 bg-purple-900/90 border border-purple-700 rounded-lg p-3 shadow-xl z-10">
            <div className="flex items-center gap-2 mb-2">
              <Brain className="w-4 h-4 text-purple-400" />
              <h4 className="text-sm font-semibold text-purple-200">SEG Contradictions</h4>
            </div>
            <div className="space-y-2 text-xs">
              {detectedContradictions.map((cont, idx) => (
                <div key={idx} className="p-2 bg-purple-800/50 rounded border border-purple-600">
                  <div className="text-purple-300 mb-1">
                    Contradiction Confidence: {(cont.confidence * 100).toFixed(0)}%
                  </div>
                  <div className="text-purple-400 text-xs font-mono">
                    {cont.entity1_id.substring(0, 16)}... ↔ {cont.entity2_id.substring(0, 16)}...
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        </>
        )}
        </div>
      </div>
      
      {/* Validation Status Bar - Shows different content for diff view vs regular editor */}
      <div className="pl-1 pr-4 py-2 border-t border-gray-700" style={{ backgroundColor: '#030712' }}>
        {isValidating && !showDiffView && (
          <div className="flex items-center gap-2 text-xs text-gray-400">
            <Zap className="w-4 h-4 animate-pulse" />
            <span>Validating...</span>
          </div>
        )}
        
        {/* Diff View Status Bar */}
        {showDiffView && diffOldValidation && diffNewValidation ? (
          <div className="flex items-center gap-2 flex-wrap">
            {/* Column Visibility Toggles - Small Icons on Left (shared for both views) */}
            <div className="flex items-center gap-1 mr-2 border-r border-gray-800 pr-2 pl-1">
              <button
                onClick={() => setShowLineNumbers(!showLineNumbers)}
                className={`p-1 rounded transition-colors ${
                  showLineNumbers
                    ? 'bg-blue-900/50 text-blue-300'
                    : 'text-gray-500 hover:bg-gray-800 hover:text-gray-300'
                }`}
                title={showLineNumbers ? 'Hide line numbers' : 'Show line numbers'}
              >
                {showLineNumbers ? <Hash className="w-3.5 h-3.5" /> : <Hash className="w-3.5 h-3.5 opacity-50" />}
              </button>
              
              <button
                onClick={() => setShowGlyphMargin(!showGlyphMargin)}
                className={`p-1 rounded transition-colors ${
                  showGlyphMargin
                    ? 'bg-blue-900/50 text-blue-300'
                    : 'text-gray-500 hover:bg-gray-800 hover:text-gray-300'
                }`}
                title={showGlyphMargin ? 'Hide glyph margin (AI/Human indicators)' : 'Show glyph margin'}
              >
                {showGlyphMargin ? <CircleDot className="w-3.5 h-3.5" /> : <CircleDot className="w-3.5 h-3.5 opacity-50" />}
              </button>
              
              <button
                onClick={() => setShowNotesColumn(!showNotesColumn)}
                className={`p-1 rounded transition-colors ${
                  showNotesColumn
                    ? 'bg-blue-900/50 text-blue-300'
                    : 'text-gray-500 hover:bg-gray-800 hover:text-gray-300'
                }`}
                title={showNotesColumn ? 'Hide notes column' : 'Show notes column'}
              >
                {showNotesColumn ? <StickyNote className="w-3.5 h-3.5" /> : <StickyNote className="w-3.5 h-3.5 opacity-50" />}
              </button>
            </div>
            
            {/* Old Version Validation */}
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-500">Old:</span>
              <div 
                className={`px-2 py-1 rounded text-xs border flex items-center gap-1 ${getConfidenceBandColor(diffOldValidation.confidence_band)}`}
                title={`Old Version - ${diffOldValidation.message}`}
              >
                <Shield className="w-3 h-3" />
                Band {diffOldValidation.confidence_band}
              </div>
              {diffOldValidation.kappa_gate_passed ? (
                <div className="flex items-center gap-1 text-xs text-green-400">
                  <CheckCircle className="w-3 h-3" />
                  <span>κ-Gate Passed</span>
                </div>
              ) : (
                <div className="flex items-center gap-1 text-xs text-red-400">
                  <Ban className="w-3 h-3" />
                  <span>κ-Gate Failed</span>
                </div>
              )}
            </div>
            
            <span className="text-gray-500">→</span>
            
            {/* New Version Validation */}
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-500">New:</span>
              <div 
                className={`px-2 py-1 rounded text-xs border flex items-center gap-1 ${getConfidenceBandColor(diffNewValidation.confidence_band)}`}
                title={`New Version - ${diffNewValidation.message}`}
              >
                <Shield className="w-3 h-3" />
                Band {diffNewValidation.confidence_band}
              </div>
              {diffNewValidation.kappa_gate_passed ? (
                <div className="flex items-center gap-1 text-xs text-green-400">
                  <CheckCircle className="w-3 h-3" />
                  <span>κ-Gate Passed</span>
                </div>
              ) : (
                <div className="flex items-center gap-1 text-xs text-red-400">
                  <Ban className="w-3 h-3" />
                  <span>κ-Gate Failed</span>
                </div>
              )}
            </div>
            
            {/* Change Indicator */}
            {diffOldValidation.confidence_band !== diffNewValidation.confidence_band && (
              <>
                <span className="text-gray-500">•</span>
                <div className="flex items-center gap-1 text-xs text-blue-400">
                  <span>Band Changed: {diffOldValidation.confidence_band} → {diffNewValidation.confidence_band}</span>
                </div>
              </>
            )}
            
            {/* Language Selector */}
            <span className="text-gray-500">•</span>
            <div className="relative language-selector">
              <button
                onClick={() => setShowLanguageDropdown(!showLanguageDropdown)}
                className={`px-2 py-0.5 rounded text-xs flex items-center gap-1.5 transition-colors ${
                  showLanguageDropdown 
                    ? 'bg-blue-900/50 text-blue-300' 
                    : 'text-gray-300 hover:bg-gray-800 hover:text-gray-100'
                }`}
                title="Select programming language"
              >
                <Code className="w-3 h-3" />
                <span className="font-medium">
                  {supportedLanguages.find(l => l.value === selectedLanguage)?.label || selectedLanguage}
                </span>
                <ChevronDown className={`w-3 h-3 transition-transform ${showLanguageDropdown ? 'rotate-180' : ''}`} />
              </button>
              
              {/* Language Dropdown */}
              {showLanguageDropdown && (
                <div className="absolute bottom-full left-0 mb-1 bg-gray-900 border border-gray-700 rounded shadow-lg z-50 min-w-[200px] max-h-[400px] overflow-y-auto">
                  <div className="px-3 py-2 border-b border-gray-700 flex items-center justify-between sticky top-0 bg-gray-900">
                    <div className="flex items-center gap-2">
                      <Code className="w-4 h-4 text-blue-400" />
                      <span className="text-sm font-semibold text-gray-200">Language Mode</span>
                    </div>
                    <button
                      onClick={() => setShowLanguageDropdown(false)}
                      className="text-gray-400 hover:text-gray-300"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                  <div className="p-2 space-y-1">
                    {supportedLanguages.map((lang) => (
                      <button
                        key={lang.value}
                        onClick={() => {
                          if (onLanguageChange) {
                            onLanguageChange(lang.value)
                          }
                          setShowLanguageDropdown(false)
                        }}
                        className={`w-full px-3 py-2 rounded text-xs flex items-center justify-between transition-colors ${
                          selectedLanguage === lang.value
                            ? 'bg-blue-900/50 text-blue-300 border border-blue-700/50'
                            : 'text-gray-300 hover:bg-gray-800'
                        }`}
                      >
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-[10px] text-gray-500 w-8">{lang.icon}</span>
                          <span>{lang.label}</span>
                        </div>
                        {selectedLanguage === lang.value && (
                          <CheckCircle className="w-3 h-3 text-blue-400" />
                        )}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ) : (
          /* Regular Editor Status Bar - Always show, even without validation result */
          !isValidating && (
            <div className="flex items-center gap-2 flex-wrap">
            {/* Column Visibility Toggles - Small Icons on Left */}
            <div className="flex items-center gap-1 mr-2 border-r border-gray-800 pr-2 pl-1">
              <button
                onClick={() => setShowLineNumbers(!showLineNumbers)}
                className={`p-1 rounded transition-colors ${
                  showLineNumbers
                    ? 'bg-blue-900/50 text-blue-300'
                    : 'text-gray-500 hover:bg-gray-800 hover:text-gray-300'
                }`}
                title={showLineNumbers ? 'Hide line numbers' : 'Show line numbers'}
              >
                {showLineNumbers ? <Hash className="w-3.5 h-3.5" /> : <Hash className="w-3.5 h-3.5 opacity-50" />}
              </button>
              
              <button
                onClick={() => setShowGlyphMargin(!showGlyphMargin)}
                className={`p-1 rounded transition-colors ${
                  showGlyphMargin
                    ? 'bg-blue-900/50 text-blue-300'
                    : 'text-gray-500 hover:bg-gray-800 hover:text-gray-300'
                }`}
                title={showGlyphMargin ? 'Hide glyph margin (AI/Human indicators)' : 'Show glyph margin'}
              >
                {showGlyphMargin ? <CircleDot className="w-3.5 h-3.5" /> : <CircleDot className="w-3.5 h-3.5 opacity-50" />}
              </button>
              
              <button
                onClick={() => setShowNotesColumn(!showNotesColumn)}
                className={`p-1 rounded transition-colors ${
                  showNotesColumn
                    ? 'bg-blue-900/50 text-blue-300'
                    : 'text-gray-500 hover:bg-gray-800 hover:text-gray-300'
                }`}
                title={showNotesColumn ? 'Hide notes column' : 'Show notes column'}
              >
                {showNotesColumn ? <StickyNote className="w-3.5 h-3.5" /> : <StickyNote className="w-3.5 h-3.5 opacity-50" />}
              </button>
            </div>
            
            {/* Confidence Band */}
            {validationResult ? (
              <div 
                className={`px-2 py-1 rounded text-xs border flex items-center gap-1 ${getConfidenceBandColor(validationResult.confidence_band)}`}
                title={`Confidence Band ${validationResult.confidence_band}: ${validationResult.confidence_band === 'A' ? 'High trust (≥90%)' : validationResult.confidence_band === 'B' ? 'Medium trust (≥70%)' : 'Low trust (<70%)'}`}
              >
                <Shield className="w-3 h-3" />
                Band {validationResult.confidence_band}
              </div>
            ) : (
              <div 
                className="px-2 py-1 rounded text-xs border flex items-center gap-1 border-gray-700 text-gray-500 bg-gray-800/50"
                title="Validation pending - edit code to trigger validation"
              >
                <Shield className="w-3 h-3" />
                <span>Pending</span>
              </div>
            )}
            
            {/* κ-Gate Status */}
            {validationResult ? (
              validationResult.kappa_gate_passed ? (
                <div 
                  className="flex items-center gap-1 text-xs text-green-400"
                  title="κ-Gate Passed: Confidence meets safety threshold. AI can proceed."
                >
                  <CheckCircle className="w-4 h-4" />
                  <span>κ-Gate Passed</span>
                </div>
              ) : (
                <div 
                  className="flex items-center gap-1 text-xs text-red-400"
                  title="κ-Gate Failed: Confidence below safety threshold. AI should abstain."
                >
                  <Ban className="w-4 h-4" />
                  <span>κ-Gate Failed</span>
                </div>
              )
            ) : (
              <div 
                className="flex items-center gap-1 text-xs text-gray-500"
                title="Validation pending"
              >
                <CircleDot className="w-4 h-4" />
                <span>Pending</span>
              </div>
            )}
            
            {/* Confidence Score - With Label */}
            {currentWitness && (
              <>
                <span className="text-gray-500">•</span>
                <span 
                  className={`text-xs font-medium ${
                    currentWitness.confidence_score >= 0.85 ? 'text-green-400' :
                    currentWitness.confidence_score >= 0.70 ? 'text-yellow-400' : 'text-red-400'
                  }`}
                  title={`Confidence Score: ${(currentWitness.confidence_score * 100).toFixed(1)}%`}
                >
                  Confidence: {(currentWitness.confidence_score * 100).toFixed(0)}%
                </span>
              </>
            )}
            
            {/* Health - Emphasized when low */}
            {consciousnessMetrics && (
              <>
                <span className="text-gray-500">•</span>
                <div 
                  className={`flex items-center gap-1 text-xs ${
                    consciousnessHealth >= 80 ? 'text-green-400' :
                    consciousnessHealth >= 60 ? 'text-yellow-400' : 'text-red-400'
                  } ${consciousnessHealth < 70 ? 'font-semibold bg-red-900/20 px-1.5 py-0.5 rounded border border-red-700/50' : ''}`}
                  title={`System Health: ${consciousnessHealth}% - Attention: ${(consciousnessMetrics.attention_focus || 0) * 100}%, Load: ${(consciousnessMetrics.cognitive_load || 0) * 100}%, Quality: ${consciousnessMetrics.quality_maintained ? 'Good' : 'Degraded'}`}
                >
                  {consciousnessHealth < 70 && (
                    <Ban className="w-3 h-3" />
                  )}
                  <span>Health: {consciousnessHealth}%</span>
                </div>
              </>
            )}
            
            {/* AI Attribution Toggle */}
            <span className="text-gray-500">•</span>
            <button
              onClick={() => setEnableAdvancedFeatures(!enableAdvancedFeatures)}
              className={`px-2 py-0.5 rounded text-xs flex items-center gap-1 transition-colors ${
                enableAdvancedFeatures 
                  ? 'bg-purple-900/50 text-purple-300' 
                  : 'text-gray-400 hover:bg-gray-800 hover:text-gray-300'
              }`}
              title={enableAdvancedFeatures ? 'Disable AI attribution features (AI/Human indicators, confidence tracking)' : 'Enable AI attribution features'}
            >
              <Brain className="w-3 h-3" />
              <span>AI Attribution</span>
              {enableAdvancedFeatures && <CheckCircle className="w-3 h-3" />}
            </button>
            
            {/* Language Selector */}
            <span className="text-gray-500">•</span>
            <div className="relative language-selector">
              <button
                onClick={() => setShowLanguageDropdown(!showLanguageDropdown)}
                className={`px-2 py-0.5 rounded text-xs flex items-center gap-1.5 transition-colors ${
                  showLanguageDropdown 
                    ? 'bg-blue-900/50 text-blue-300' 
                    : 'text-gray-300 hover:bg-gray-800 hover:text-gray-100'
                }`}
                title="Select programming language"
              >
                <Code className="w-3 h-3" />
                <span className="font-medium">
                  {supportedLanguages.find(l => l.value === selectedLanguage)?.label || selectedLanguage}
                </span>
                <ChevronDown className={`w-3 h-3 transition-transform ${showLanguageDropdown ? 'rotate-180' : ''}`} />
              </button>
              
              {/* Language Dropdown */}
              {showLanguageDropdown && (
                <div className="absolute bottom-full left-0 mb-1 bg-gray-900 border border-gray-700 rounded shadow-lg z-50 min-w-[200px] max-h-[400px] overflow-y-auto">
                  <div className="px-3 py-2 border-b border-gray-700 flex items-center justify-between sticky top-0 bg-gray-900">
                    <div className="flex items-center gap-2">
                      <Code className="w-4 h-4 text-blue-400" />
                      <span className="text-sm font-semibold text-gray-200">Language Mode</span>
                    </div>
                    <button
                      onClick={() => setShowLanguageDropdown(false)}
                      className="text-gray-400 hover:text-gray-300"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                  <div className="p-2 space-y-1">
                    {supportedLanguages.map((lang) => (
                      <button
                        key={lang.value}
                        onClick={() => {
                          if (onLanguageChange) {
                            onLanguageChange(lang.value)
                          }
                          setShowLanguageDropdown(false)
                        }}
                        className={`w-full px-3 py-2 rounded text-xs flex items-center justify-between transition-colors ${
                          selectedLanguage === lang.value
                            ? 'bg-blue-900/50 text-blue-300 border border-blue-700/50'
                            : 'text-gray-300 hover:bg-gray-800'
                        }`}
                      >
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-[10px] text-gray-500 w-8">{lang.icon}</span>
                          <span>{lang.label}</span>
                        </div>
                        {selectedLanguage === lang.value && (
                          <CheckCircle className="w-3 h-3 text-blue-400" />
                        )}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
            
            {/* SEG Contradictions */}
            {detectedContradictions.length > 0 && (
              <>
                <span className="text-gray-500">•</span>
                <div 
                  className="flex items-center gap-1 text-xs text-purple-400"
                  title={`${detectedContradictions.length} contradiction(s) detected in knowledge graph`}
                >
                  <Brain className="w-4 h-4" />
                  <span>{detectedContradictions.length} Contradiction(s)</span>
                </div>
              </>
            )}
            
            {/* Editor Info - Line Count, Character Count, Cursor Position - Toggleable */}
            <span className="text-gray-500">•</span>
            <button
              onClick={() => setShowEditorInfo(!showEditorInfo)}
              className={`px-2 py-0.5 rounded text-xs flex items-center gap-1 transition-colors ${
                showEditorInfo 
                  ? 'bg-gray-800/50 text-gray-300' 
                  : 'text-gray-500 hover:bg-gray-800 hover:text-gray-300'
              }`}
              title={showEditorInfo ? 'Hide editor info' : 'Show editor info (lines, characters, cursor position)'}
            >
              <Hash className="w-3 h-3" />
              <span>Info</span>
            </button>
            {showEditorInfo && (
              <div className="flex items-center gap-2 text-xs text-gray-400">
                <span title="Line count">
                  Lines: {editorInfo.lines}
                </span>
                <span className="text-gray-600">•</span>
                <span title="Character count">
                  Chars: {editorInfo.characters.toLocaleString()}
                </span>
                {editorInfo.cursorLine > 0 && (
                  <>
                    <span className="text-gray-600">•</span>
                    <span title="Cursor position">
                      Ln {editorInfo.cursorLine}, Col {editorInfo.cursorColumn}
                    </span>
                  </>
                )}
              </div>
            )}
            
            {/* Technical Details - Collapsible */}
            {currentWitness && (
              <div className="relative group ml-auto technical-details">
                <button
                  onClick={() => setShowTechnicalDetails(!showTechnicalDetails)}
                  className="px-1.5 py-0.5 rounded text-[10px] text-gray-500 hover:text-gray-300 hover:bg-gray-800 transition-colors flex items-center gap-1"
                  title="Show technical details"
                >
                  <Code className="w-3 h-3" />
                  <span>Details</span>
                </button>
                
                {/* Technical Details Dropdown */}
                {showTechnicalDetails && (
                  <div className="absolute bottom-full right-0 mb-1 bg-gray-900 border border-gray-700 rounded shadow-lg z-50 min-w-[250px] p-3">
                    <div className="space-y-2 text-xs">
                      <div className="flex items-center justify-between">
                        <span className="text-gray-400">Model:</span>
                        <span className="text-gray-200 font-mono">{currentWitness.model_id}</span>
                      </div>
                      {currentWitness.kappa_threshold !== undefined && (
                        <div className="flex items-center justify-between">
                          <span className="text-gray-400">κ Threshold:</span>
                          <span className="text-gray-200">{(currentWitness.kappa_threshold * 100).toFixed(0)}%</span>
                        </div>
                      )}
                      {consciousnessMetrics && (
                        <>
                          <div className="border-t border-gray-700 pt-2 mt-2">
                            <div className="text-gray-400 mb-1.5 text-[10px] font-medium">Consciousness Metrics:</div>
                            <div className="space-y-1 text-[10px]">
                              <div className="flex items-center justify-between">
                                <span className="text-gray-500">Attention:</span>
                                <span className="text-gray-300">{((consciousnessMetrics.attention_focus || 0) * 100).toFixed(0)}%</span>
                              </div>
                              <div className="flex items-center justify-between">
                                <span className="text-gray-500">Cognitive Load:</span>
                                <span className="text-gray-300">{((consciousnessMetrics.cognitive_load || 0) * 100).toFixed(0)}%</span>
                              </div>
                              <div className="flex items-center justify-between">
                                <span className="text-gray-500">Quality:</span>
                                <span className={consciousnessMetrics.quality_maintained ? 'text-green-400' : 'text-red-400'}>
                                  {consciousnessMetrics.quality_maintained ? 'Maintained' : 'Degraded'}
                                </span>
                              </div>
                            </div>
                          </div>
                        </>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )
      )}
      </div>
    </div>
  )
}
