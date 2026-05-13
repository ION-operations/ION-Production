// Core IDE Layout Component - V2 Enhanced with Zustand
// 5-Zone Layout System with Comprehensive AIM-OS Integration
// Performance Optimized: Memoization, lazy loading, error boundaries

import React, { useState, useEffect, useMemo, useCallback, memo, useRef } from 'react'
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels'
import { ErrorBoundary } from './ErrorBoundary'
import { OptimizedPanel, LazyPanelWrapper } from '../utils/performance'
import {
  LazyFileTree,
  LazyMemoryBrowser,
  LazySystemStatus,
  LazyContextWeb,
  LazyTimelineView,
  LazyCodeEditor,
  LazyTerminalPanel,
  LazyOutlinePanel,
  LazyProblemsPanel,
  LazyDebugConsolePanel,
  LazySuperIndexPanel,
  LazyMasterIndexPanel,
  LazySystemMapPanel,
  LazyNLTagsExplorerPanel,
  LazyDocumentationExplorerPanel,
  LazyEvolutionExplorer,
  LazyConsciousnessVisualization,
  LazyAIMOSOrchestration,
  LazyAppPreview,
  LazyAppPreviewControls,
  LazyAIChatManagement,
  LazyRouterPanel,
  LazyLogSentinelsSummaries,
  LazyLogSentinelsAnomalies,
  LazyToolQualityDashboard,
  LazyDocumentEditor,
  LazyLogAnalysisDashboard,
  LazyChatHeatmapPanel,
  LazyContextLedger,
} from '../utils/performance'
import { TopBar } from './TopBar'
import { useCMC, useVIF, useCAS } from '../hooks/useAIMOS'
import { usePanelStore } from '../store/panelStore'
import { usePanelInitialization } from '../hooks/usePanelManagement'
import {
  FolderOpen,
  Code,
  Terminal,
  Clock,
  Brain,
  Network,
  Activity,
  Bug,
  Maximize2,
  Minimize2,
  Database,
  Shield,
  GitBranch,
  AlertCircle,
  ChevronDown,
  Globe,
  ChevronUp,
  ChevronLeft,
  ChevronRight,
  FileText,
  Zap,
  BarChart3,
  AlertTriangle,
} from 'lucide-react'

type LeftPanelType = 'explorer' | 'memory' | 'status' | 'app-preview-controls' | 'debug-console' | null
type RightPanelType = 'context-web' | 'timeline' | 'outline' | 'ai-chat' | 'router' | 'debug-console' | null
type BottomPanelType = 'terminal' | 'problems' | 'timeline' | 'debug-console' | 'log-sentinels-summaries' | 'log-sentinels-anomalies' | 'tool-quality' | 'log-analysis' | 'context-ledger' | 'heatmap' | null
type MainViewType = 'code' | 'evolution' | 'consciousness' | 'orchestration' | 'app-preview' | 'document-editor'

// Unified zone system for cross-zone dragging
type ZoneType = 'left' | 'right' | 'bottom' | 'main'
type SectionType = 'top' | 'bottom' | 'left' | 'right' // top/bottom for left/right zones, left/right for bottom zone

// Unified button type for cross-zone dragging
type UnifiedPanelType = LeftPanelType | RightPanelType | BottomPanelType | MainViewType

// Button configuration for left toolbar
interface LeftToolbarButton {
  id: LeftPanelType
  icon: React.ComponentType<{ className?: string }>
  title: string
  section: 'top' | 'bottom' // Which section it belongs to
  toolbar: 'left' // Which toolbar it belongs to
}

// Button configuration for right toolbar
interface RightToolbarButton {
  id: RightPanelType
  icon: React.ComponentType<{ className?: string }>
  title: string
  section: 'top' | 'bottom' // Which section it belongs to
  toolbar: 'right' // Which toolbar it belongs to
}

// Button configuration for bottom toolbar
interface BottomToolbarButton {
  id: BottomPanelType
  icon: React.ComponentType<{ className?: string }>
  title: string
  section: 'left' | 'right' // Which section it belongs to (left/right instead of top/bottom)
  toolbar: 'bottom' // Which toolbar it belongs to
}

// Button configuration for main view toolbar
interface MainToolbarButton {
  id: MainViewType
  icon: React.ComponentType<{ className?: string }>
  title: string
  section: 'left' | 'right' // Which section it belongs to (left/right instead of top/bottom)
  toolbar: 'main' // Which toolbar it belongs to
}

// Unified button type for cross-zone operations
type UnifiedToolbarButton = LeftToolbarButton | RightToolbarButton | BottomToolbarButton | MainToolbarButton

const LEFT_TOOLBAR_BUTTONS: LeftToolbarButton[] = [
  { id: 'explorer', icon: FolderOpen, title: 'File Explorer\nCMC-backed file operations with HHNI hierarchical paths', section: 'top', toolbar: 'left' },
  { id: 'memory', icon: Brain, title: 'AI Memory Browser\nCMC memory exploration with HHNI semantic search', section: 'top', toolbar: 'left' },
  { id: 'app-preview-controls', icon: Globe, title: 'App Preview Controls\nBrowser console, port info, terminal, and cache management', section: 'top', toolbar: 'left' },
  { id: 'status', icon: Activity, title: 'System Status\nReal-time AIM-OS system health monitoring', section: 'bottom', toolbar: 'left' },
]

const RIGHT_TOOLBAR_BUTTONS: RightToolbarButton[] = [
  { id: 'context-web', icon: Network, title: 'Context Web\nInteractive SEG knowledge graph visualization with HHNI integration and topic evolution tracking', section: 'top', toolbar: 'right' },
  { id: 'timeline', icon: Clock, title: 'Timeline View\nTCS timeline with playback controls and bitemporal tracking', section: 'top', toolbar: 'right' },
  { id: 'router', icon: Zap, title: 'Tool Selection\nRouter tool proposals with probabilities and preconditions', section: 'top', toolbar: 'right' },
  { id: 'outline', icon: Code, title: 'Outline\nSymbol navigation with HHNI hierarchical structure', section: 'bottom', toolbar: 'right' },
  { id: 'ai-chat', icon: Brain, title: 'AI Chat & Management\nAI agent communication, task management, and collaboration', section: 'top', toolbar: 'right' },
]

const BOTTOM_TOOLBAR_BUTTONS: BottomToolbarButton[] = [
  { id: 'terminal', icon: Terminal, title: 'Terminal\nCommand execution with CMC atom storage and VIF witness tracking', section: 'left', toolbar: 'bottom' },
  { id: 'problems', icon: AlertCircle, title: 'Problems\nError tracking with VIF confidence bands and SEG contradictions', section: 'left', toolbar: 'bottom' },
  { id: 'log-sentinels-anomalies', icon: AlertTriangle, title: 'Anomalies\nLog-Sentinels Forensics reports with root causes and fixes', section: 'left', toolbar: 'bottom' },
  { id: 'context-ledger', icon: Database, title: 'Context Ledger\nBudget, token usage, and context selection details', section: 'left', toolbar: 'bottom' },
  { id: 'timeline', icon: Clock, title: 'Timeline\nTCS timeline with playback controls and bitemporal tracking', section: 'right', toolbar: 'bottom' },
  { id: 'log-sentinels-summaries', icon: Brain, title: 'AI Summaries\nLog-Sentinels Scout reports with summaries and tool suggestions', section: 'right', toolbar: 'bottom' },
  { id: 'debug-console', icon: Bug, title: 'Debug Console\nReal-time log viewing, system breakdown, infrastructure status, and analysis insights', section: 'right', toolbar: 'bottom' },
  { id: 'tool-quality', icon: Activity, title: 'Tool Quality\nRouter telemetry dashboard with latency, success rate, and cost metrics', section: 'right', toolbar: 'bottom' },
  { id: 'log-analysis', icon: BarChart3, title: 'Log Analysis\nLog-Sentinels telemetry dashboard with statistics and timeline', section: 'right', toolbar: 'bottom' },
  { id: 'heatmap', icon: Zap, title: 'Context Heatmap\nGrid visualization of context usage across turns and agents', section: 'right', toolbar: 'bottom' },
]

const MAIN_TOOLBAR_BUTTONS: MainToolbarButton[] = [
  { id: 'code', icon: Code, title: 'Code Editor\nMonaco editor with VIF κ-gating, confidence tracking, and SEG contradiction detection', section: 'left', toolbar: 'main' },
  { id: 'document-editor', icon: FileText, title: 'Document Editor\nLUCID editor with LaTeX math, rich text, section management, and AIM-OS integration', section: 'left', toolbar: 'main' },
  { id: 'evolution', icon: GitBranch, title: 'Evolution Explorer\nVisualize connections between Timeline, Chains, and Goals', section: 'left', toolbar: 'main' },
  { id: 'consciousness', icon: Brain, title: 'Consciousness Visualization\nReal-time AI consciousness state via CAS AttentionMetrics', section: 'right', toolbar: 'main' },
  { id: 'app-preview', icon: Globe, title: 'App Preview\nBrowser preview with port info and process management', section: 'right', toolbar: 'main' },
]

export const IDELayout: React.FC = () => {
  const { getStats } = useCMC()
  const { getMetrics } = useCAS()
  
  // Initialize default panels
  usePanelInitialization()
  
  // Zustand store for panel and layout state
  const {
    mainView,
    setMainView,
    getPanelsByZone,
    getPanelById,
    updatePanel,
    togglePanelVisibility,
  } = usePanelStore()
  
  // Track left panel right edge position for dividers
  const [leftPanelRightEdge, setLeftPanelRightEdge] = useState<number>(48) // Default: left toolbar width (w-8 = 32px) + some padding
  const leftPanelRef = useRef<HTMLDivElement>(null)
  const leftToolbarRef = useRef<HTMLDivElement>(null)
  const bottomStatusDataRef = useRef<HTMLDivElement>(null)
  const [bottomStatusDataRightEdge, setBottomStatusDataRightEdge] = useState<number>(200) // Minimum position for bottom divider
  
  // Track right panel left edge positions for bottom bar dividers
  const [rightPanelLeftEdge, setRightPanelLeftEdge] = useState<number>(window.innerWidth - 300) // Default: near right edge
  const rightPanelRef = useRef<HTMLDivElement>(null)
  const [bottomRightPanelLeftEdge, setBottomRightPanelLeftEdge] = useState<number>(window.innerWidth - 300) // Default: near right edge
  const bottomRightPanelRef = useRef<HTMLDivElement>(null)
  
  // Track panel status information for bottom bar display
  const [bottomLeftPanelStatus, setBottomLeftPanelStatus] = useState<string | null>(null)
  const [bottomRightPanelStatus, setBottomRightPanelStatus] = useState<string | null>(null)
  
  // Local panel selection state (mapped to Zustand panels)
  const [leftTopPanel, setLeftTopPanel] = useState<LeftPanelType>('explorer') // Top section panel
  const [leftBottomPanel, setLeftBottomPanel] = useState<LeftPanelType | null>('status') // Bottom section panel - default to status
  const [leftToolbarButtons, setLeftToolbarButtons] = useState<LeftToolbarButton[]>(LEFT_TOOLBAR_BUTTONS)
  const [draggedButtonId, setDraggedButtonId] = useState<UnifiedPanelType | null>(null)
  const [draggedFromToolbar, setDraggedFromToolbar] = useState<ZoneType | null>(null)
  const [dragOverSection, setDragOverSection] = useState<SectionType | null>(null)
  const [dragOverToolbar, setDragOverToolbar] = useState<ZoneType | null>(null)
  
  const [rightTopPanel, setRightTopPanel] = useState<RightPanelType>('context-web') // Top section panel
  const [rightBottomPanel, setRightBottomPanel] = useState<RightPanelType | null>('outline') // Bottom section panel - default to outline
  const [rightToolbarButtons, setRightToolbarButtons] = useState<RightToolbarButton[]>(RIGHT_TOOLBAR_BUTTONS)
  const [bottomPanel, setBottomPanel] = useState<BottomPanelType>('terminal')
  const [bottomLeftPanel, setBottomLeftPanel] = useState<BottomPanelType>('terminal') // Left section panel
  const [bottomRightPanel, setBottomRightPanel] = useState<BottomPanelType | null>('debug-console') // Right section panel
  const [bottomToolbarButtons, setBottomToolbarButtons] = useState<BottomToolbarButton[]>(BOTTOM_TOOLBAR_BUTTONS)
  const [mainToolbarButtons, setMainToolbarButtons] = useState<MainToolbarButton[]>(MAIN_TOOLBAR_BUTTONS)
  const [bottomDrawerOpen, setBottomDrawerOpen] = useState(true)
  
  // Panel visibility states
  const [leftPanelOpen, setLeftPanelOpen] = useState(true) // Left panel visibility (toolbar always visible)
  const [rightPanelOpen, setRightPanelOpen] = useState(true) // Right panel visibility (toolbar always visible)
  const [topPanelOpen, setTopPanelOpen] = useState(true) // Top panel visibility (hides panel + toolbar)
  const [bottomPanelOpen, setBottomPanelOpen] = useState(true) // Bottom panel visibility (hides panel + toolbar)
  
  // Track bottom status data right edge for minimum divider position
  useEffect(() => {
    const updateBottomStatusEdge = () => {
      if (bottomStatusDataRef.current) {
        const rect = bottomStatusDataRef.current.getBoundingClientRect()
        setBottomStatusDataRightEdge(rect.right + 12) // Add some padding
      }
    }
    
    updateBottomStatusEdge()
    const resizeObserver = new ResizeObserver(updateBottomStatusEdge)
    if (bottomStatusDataRef.current) {
      resizeObserver.observe(bottomStatusDataRef.current)
    }
    
    return () => resizeObserver.disconnect()
  }, []) // ResizeObserver handles updates automatically
  
  // Track left panel right edge position
  useEffect(() => {
    const updateLeftPanelEdge = () => {
      if (!leftToolbarRef.current) {
        // Fallback: just toolbar width
        setLeftPanelRightEdge(32)
        return
      }
      
      const toolbarRect = leftToolbarRef.current.getBoundingClientRect()
      let edgePosition = toolbarRect.right
      
      // If panel is open, get its right edge
      if (leftPanelOpen && leftPanelRef.current) {
        const panelRect = leftPanelRef.current.getBoundingClientRect()
        // Validate panel rect - ensure it's reasonable
        if (panelRect.right > toolbarRect.right && 
            panelRect.right < window.innerWidth &&
            panelRect.width < window.innerWidth * 0.5) { // Panel shouldn't be > 50% of screen
          edgePosition = panelRect.right
        }
        // If panel rect seems invalid, fall back to toolbar
      }
      
      // CRITICAL: Clamp to reasonable values - should never exceed screen width
      // This prevents the top bar from becoming wider than the screen
      const screenWidth = window.innerWidth
      const clampedPosition = Math.max(32, Math.min(edgePosition, screenWidth - 100))
      
      setLeftPanelRightEdge(clampedPosition)
    }
    
    updateLeftPanelEdge()
    
    // Use ResizeObserver to track panel size changes
    const resizeObserver = new ResizeObserver(updateLeftPanelEdge)
    if (leftToolbarRef.current) {
      resizeObserver.observe(leftToolbarRef.current)
    }
    if (leftPanelRef.current) {
      resizeObserver.observe(leftPanelRef.current)
    }
    
    // Also update on panel open/close and window resize
    const interval = setInterval(updateLeftPanelEdge, 50)
    window.addEventListener('resize', updateLeftPanelEdge)
    
    return () => {
      resizeObserver.disconnect()
      clearInterval(interval)
      window.removeEventListener('resize', updateLeftPanelEdge)
    }
  }, [leftPanelOpen])
  
  // Track right panel left edge position for bottom bar divider
  useEffect(() => {
    const updateRightPanelEdge = () => {
      if (!rightPanelRef.current || !rightPanelOpen) {
        // If panel is closed, set to screen width (no divider needed)
        setRightPanelLeftEdge(window.innerWidth)
        return
      }
      
      const panelRect = rightPanelRef.current.getBoundingClientRect()
      const screenWidth = window.innerWidth
      
      // Get left edge of right panel
      const leftEdge = panelRect.left
      
      // Clamp to reasonable values
      const clampedPosition = Math.max(100, Math.min(leftEdge, screenWidth - 100))
      
      setRightPanelLeftEdge(clampedPosition)
    }
    
    updateRightPanelEdge()
    
    const resizeObserver = new ResizeObserver(updateRightPanelEdge)
    if (rightPanelRef.current) {
      resizeObserver.observe(rightPanelRef.current)
    }
    
    const interval = setInterval(updateRightPanelEdge, 50)
    window.addEventListener('resize', updateRightPanelEdge)
    
    return () => {
      resizeObserver.disconnect()
      clearInterval(interval)
      window.removeEventListener('resize', updateRightPanelEdge)
    }
  }, [rightPanelOpen])
  
  // Track bottom right panel left edge position for bottom bar divider
  useEffect(() => {
    const updateBottomRightPanelEdge = () => {
      if (!bottomRightPanelRef.current || !bottomRightPanel || !bottomPanelOpen) {
        // If panel is closed, set to screen width (no divider needed)
        setBottomRightPanelLeftEdge(window.innerWidth)
        return
      }
      
      const panelRect = bottomRightPanelRef.current.getBoundingClientRect()
      const screenWidth = window.innerWidth
      
      // Get left edge of bottom right panel
      const leftEdge = panelRect.left
      
      // Clamp to reasonable values
      const clampedPosition = Math.max(100, Math.min(leftEdge, screenWidth - 100))
      
      setBottomRightPanelLeftEdge(clampedPosition)
    }
    
    updateBottomRightPanelEdge()
    
    const resizeObserver = new ResizeObserver(updateBottomRightPanelEdge)
    if (bottomRightPanelRef.current) {
      resizeObserver.observe(bottomRightPanelRef.current)
    }
    
    const interval = setInterval(updateBottomRightPanelEdge, 50)
    window.addEventListener('resize', updateBottomRightPanelEdge)
    
    return () => {
      resizeObserver.disconnect()
      clearInterval(interval)
      window.removeEventListener('resize', updateBottomRightPanelEdge)
    }
  }, [bottomRightPanel, bottomPanelOpen])
  
  // Tab management for code editor
  interface OpenFile {
    id: string
    path: string
    name: string
    openedAt: Date
  }
  const [openFiles, setOpenFiles] = useState<OpenFile[]>([
    { id: '1', path: 'src/components/IDELayout.tsx', name: 'IDELayout.tsx', openedAt: new Date(Date.now() - 300000) },
    { id: '2', path: 'src/panels/CodeEditor.tsx', name: 'CodeEditor.tsx', openedAt: new Date(Date.now() - 180000) },
    { id: '3', path: 'src/components/TopBar.tsx', name: 'TopBar.tsx', openedAt: new Date(Date.now() - 60000) },
  ])
  const [activeFileId, setActiveFileId] = useState<string>('1')
  const [showFileDropdown, setShowFileDropdown] = useState(false)
  
  const handleFileOpen = useCallback((file: OpenFile) => {
    setOpenFiles(prev => {
      const exists = prev.find(f => f.id === file.id)
      if (exists) return prev
      return [...prev, file].sort((a, b) => a.openedAt.getTime() - b.openedAt.getTime())
    })
    setActiveFileId(file.id)
  }, [])
  
  const handleFileClose = useCallback((fileId: string, e: React.MouseEvent) => {
    e.stopPropagation()
    setOpenFiles(prev => {
      const filtered = prev.filter(f => f.id !== fileId)
      if (activeFileId === fileId && filtered.length > 0) {
        setActiveFileId(filtered[filtered.length - 1].id)
      } else if (filtered.length === 0) {
        setActiveFileId('')
      }
      return filtered
    })
  }, [activeFileId])
  
  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (showFileDropdown && !(e.target as Element).closest('.file-dropdown-container')) {
        setShowFileDropdown(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [showFileDropdown])
  
  // AIM-OS state (not panel-related, keep as local state)
  const [cmcStats, setCmcStats] = useState<any>(null)
  const [casMetrics, setCasMetrics] = useState<any>(null)
  
  // Get panels from Zustand store
  const leftPanels = useMemo(() => getPanelsByZone('left'), [getPanelsByZone])
  const rightPanels = useMemo(() => getPanelsByZone('right'), [getPanelsByZone])
  const bottomPanels = useMemo(() => getPanelsByZone('bottom'), [getPanelsByZone])
  
  // Memoized event handlers for performance
  const [appPreviewControlsGlow, setAppPreviewControlsGlow] = useState(false)
  const [previousMainView, setPreviousMainView] = useState<MainViewType>(mainView)

  // Handle glow animation separately to avoid interfering with view state
  useEffect(() => {
    if (mainView === 'app-preview' && previousMainView !== 'app-preview') {
      // App preview just opened - trigger glow
      setAppPreviewControlsGlow(true)
      const timer = setTimeout(() => {
        setAppPreviewControlsGlow(false)
      }, 2000) // 2 second glow
      return () => clearTimeout(timer)
    }
    setPreviousMainView(mainView)
  }, [mainView, previousMainView])

  const handleMainViewChange = useCallback((view: 'code' | 'evolution' | 'consciousness' | 'orchestration' | 'app-preview' | 'document-editor') => {
    // Toggle: if clicking the same view, close it (set to 'code' as default)
    if (mainView === view) {
      setMainView('code')
    } else {
    setMainView(view)
    }
  }, [mainView, setMainView])
  
  const handleLeftPanelChange = useCallback((panel: LeftPanelType, section: 'top' | 'bottom') => {
    if (section === 'top') {
      // If clicking a top panel button while a top panel is already open, switch to it
      // If clicking the same button, toggle it off
      if (leftTopPanel === panel) {
        setLeftTopPanel(null)
      } else {
        setLeftTopPanel(panel)
      }
    } else {
      // If clicking a bottom panel button while a bottom panel is already open, switch to it
      // If clicking the same button, toggle it off
      if (leftBottomPanel === panel) {
        setLeftBottomPanel(null)
      } else {
        setLeftBottomPanel(panel)
      }
    }
  }, [leftTopPanel, leftBottomPanel])
  
  // Handle drag and drop for toolbar buttons (unified for cross-zone dragging)
  const handleDragStart = useCallback((e: React.DragEvent, buttonId: UnifiedPanelType, toolbar: ZoneType) => {
    setDraggedButtonId(buttonId)
    setDraggedFromToolbar(toolbar)
    e.dataTransfer.effectAllowed = 'move'
    e.dataTransfer.setData('text/plain', buttonId || '')
    e.dataTransfer.setData('toolbar', toolbar)
  }, [])
  
  const handleDragOver = useCallback((e: React.DragEvent, section: SectionType, toolbar: ZoneType) => {
    e.preventDefault()
    e.dataTransfer.dropEffect = 'move'
    setDragOverSection(section)
    setDragOverToolbar(toolbar)
  }, [])
  
  const handleDragLeave = useCallback(() => {
    setDragOverSection(null)
    setDragOverToolbar(null)
  }, [])
  
  const handleDrop = useCallback((e: React.DragEvent, targetSection: SectionType, targetToolbar: ZoneType) => {
    e.preventDefault()
    if (!draggedButtonId || !draggedFromToolbar) return
    
    const sourceToolbar = draggedFromToolbar
    const sourceButtonId = draggedButtonId
    
    // Helper to find button in any toolbar
    const findButton = (toolbar: ZoneType, id: UnifiedPanelType): UnifiedToolbarButton | null => {
      if (toolbar === 'left') return leftToolbarButtons.find(btn => btn.id === id) || null
      if (toolbar === 'right') return rightToolbarButtons.find(btn => btn.id === id) || null
      if (toolbar === 'bottom') return bottomToolbarButtons.find(btn => btn.id === id) || null
      if (toolbar === 'main') return mainToolbarButtons.find(btn => btn.id === id) || null
      return null
    }
    
    // Helper to remove button from toolbar
    const removeButton = (toolbar: ZoneType, id: UnifiedPanelType) => {
      if (toolbar === 'left') {
        setLeftToolbarButtons(prev => prev.filter(btn => btn.id !== id))
        if (leftTopPanel === id) setLeftTopPanel(null)
        if (leftBottomPanel === id) setLeftBottomPanel(null)
      } else if (toolbar === 'right') {
        setRightToolbarButtons(prev => prev.filter(btn => btn.id !== id))
        if (rightTopPanel === id) setRightTopPanel(null)
        if (rightBottomPanel === id) setRightBottomPanel(null)
      } else if (toolbar === 'bottom') {
        setBottomToolbarButtons(prev => prev.filter(btn => btn.id !== id))
        if (bottomLeftPanel === id) setBottomLeftPanel(null)
        if (bottomRightPanel === id) setBottomRightPanel(null)
        if (bottomPanel === id) setBottomPanel('terminal') // Fallback
      } else if (toolbar === 'main') {
        setMainToolbarButtons(prev => prev.filter(btn => btn.id !== id))
        // Main view buttons don't have panel state, they control mainView directly
      }
    }
    
    // Find source button
    const sourceButton = findButton(sourceToolbar, sourceButtonId)
    if (!sourceButton) return
    
    // If dropping in the same toolbar, just move between sections
    if (sourceToolbar === targetToolbar) {
      if (targetToolbar === 'left') {
        setLeftToolbarButtons(prev => prev.map(btn => 
          btn.id === sourceButtonId ? { ...btn, section: targetSection as 'top' | 'bottom' } : btn
        ))
        if (targetSection === 'top') {
          if (leftBottomPanel === sourceButtonId) setLeftBottomPanel(null)
        } else {
          if (leftTopPanel === sourceButtonId) setLeftTopPanel(null)
        }
      } else if (targetToolbar === 'right') {
        setRightToolbarButtons(prev => prev.map(btn => 
          btn.id === sourceButtonId ? { ...btn, section: targetSection as 'top' | 'bottom' } : btn
        ))
        if (targetSection === 'top') {
          if (rightBottomPanel === sourceButtonId) setRightBottomPanel(null)
        } else {
          if (rightTopPanel === sourceButtonId) setRightTopPanel(null)
        }
      } else if (targetToolbar === 'bottom') {
        setBottomToolbarButtons(prev => prev.map(btn => 
          btn.id === sourceButtonId ? { ...btn, section: targetSection as 'left' | 'right' } : btn
        ))
        if (targetSection === 'left') {
          if (bottomRightPanel === sourceButtonId) setBottomRightPanel(null)
        } else {
          if (bottomLeftPanel === sourceButtonId) setBottomLeftPanel(null)
        }
      } else if (targetToolbar === 'main') {
        setMainToolbarButtons(prev => prev.map(btn => 
          btn.id === sourceButtonId ? { ...btn, section: targetSection as 'left' | 'right' } : btn
        ))
      }
    } else {
      // Cross-zone drag: move button from one zone to another
      removeButton(sourceToolbar, sourceButtonId)
      
      // Add to target toolbar with appropriate type conversion
      if (targetToolbar === 'left') {
        const convertedButton: LeftToolbarButton = {
          id: sourceButtonId as LeftPanelType,
          icon: sourceButton.icon,
          title: sourceButton.title,
          section: targetSection as 'top' | 'bottom',
          toolbar: 'left'
        }
        setLeftToolbarButtons(prev => [...prev, convertedButton])
      } else if (targetToolbar === 'right') {
        const convertedButton: RightToolbarButton = {
          id: sourceButtonId as RightPanelType,
          icon: sourceButton.icon,
          title: sourceButton.title,
          section: targetSection as 'top' | 'bottom',
          toolbar: 'right'
        }
        setRightToolbarButtons(prev => [...prev, convertedButton])
      } else if (targetToolbar === 'bottom') {
        const convertedButton: BottomToolbarButton = {
          id: sourceButtonId as BottomPanelType,
          icon: sourceButton.icon,
          title: sourceButton.title,
          section: targetSection as 'left' | 'right',
          toolbar: 'bottom'
        }
        setBottomToolbarButtons(prev => [...prev, convertedButton])
      } else if (targetToolbar === 'main') {
        const convertedButton: MainToolbarButton = {
          id: sourceButtonId as MainViewType,
          icon: sourceButton.icon,
          title: sourceButton.title,
          section: targetSection as 'left' | 'right',
          toolbar: 'main'
        }
        setMainToolbarButtons(prev => [...prev, convertedButton])
      }
    }
    
    setDraggedButtonId(null)
    setDraggedFromToolbar(null)
    setDragOverSection(null)
    setDragOverToolbar(null)
  }, [draggedButtonId, draggedFromToolbar, leftTopPanel, leftBottomPanel, rightTopPanel, rightBottomPanel, bottomLeftPanel, bottomRightPanel, bottomPanel, leftToolbarButtons, rightToolbarButtons, bottomToolbarButtons, mainToolbarButtons])
  
  const handleDragEnd = useCallback(() => {
    setDraggedButtonId(null)
    setDraggedFromToolbar(null)
    setDragOverSection(null)
    setDragOverToolbar(null)
  }, [])
  
  const handleRightPanelChange = useCallback((panel: RightPanelType, section: 'top' | 'bottom') => {
    if (section === 'top') {
      // If clicking a top panel button while a top panel is already open, switch to it
      // If clicking the same button, toggle it off
      if (rightTopPanel === panel) {
        setRightTopPanel(null)
      } else {
        setRightTopPanel(panel)
      }
    } else {
      // If clicking a bottom panel button while a bottom panel is already open, switch to it
      // If clicking the same button, toggle it off
      if (rightBottomPanel === panel) {
        setRightBottomPanel(null)
      } else {
        setRightBottomPanel(panel)
      }
    }
  }, [rightTopPanel, rightBottomPanel])
  
  const handleBottomDrawerToggle = useCallback(() => {
    setBottomPanelOpen(prev => !prev)
  }, [])
  
  const handleLeftPanelToggle = useCallback(() => {
    setLeftPanelOpen(prev => !prev)
  }, [])
  
  const handleRightPanelToggle = useCallback(() => {
    setRightPanelOpen(prev => !prev)
  }, [])
  
  const handleTopPanelToggle = useCallback(() => {
    setTopPanelOpen(prev => !prev)
  }, [])
  
  // Bottom panel button handlers with toggle logic
  const handleBottomLeftPanelChange = useCallback((panel: BottomPanelType) => {
    // Toggle: if clicking the same panel, close it
    if (bottomLeftPanel === panel) {
      setBottomLeftPanel(null)
      // If this was the only bottom panel, also clear bottomPanel
      if (!bottomRightPanel) {
        setBottomPanel('terminal') // Fallback to default
      }
    } else {
      setBottomLeftPanel(panel)
      setBottomPanel(panel)
    }
  }, [bottomLeftPanel, bottomRightPanel])
  
  const handleBottomRightPanelChange = useCallback((panel: BottomPanelType) => {
    // Toggle: if clicking the same panel, close it
    if (bottomRightPanel === panel) {
      setBottomRightPanel(null)
      // If this was the only bottom panel, also clear bottomPanel
      if (!bottomLeftPanel) {
        setBottomPanel('terminal') // Fallback to default
      }
    } else {
      setBottomRightPanel(panel)
      setBottomPanel(panel)
    }
  }, [bottomRightPanel, bottomLeftPanel])
  
  // Auto-close panels when no panel is selected
  useEffect(() => {
    // Close left panel if both top and bottom are null
    if (!leftTopPanel && !leftBottomPanel && leftPanelOpen) {
      setLeftPanelOpen(false)
    } else if ((leftTopPanel || leftBottomPanel) && !leftPanelOpen) {
      setLeftPanelOpen(true)
    }
  }, [leftTopPanel, leftBottomPanel, leftPanelOpen])
  
  useEffect(() => {
    // Close right panel if both top and bottom are null
    if (!rightTopPanel && !rightBottomPanel && rightPanelOpen) {
      setRightPanelOpen(false)
    } else if ((rightTopPanel || rightBottomPanel) && !rightPanelOpen) {
      setRightPanelOpen(true)
    }
  }, [rightTopPanel, rightBottomPanel, rightPanelOpen])
  
  useEffect(() => {
    // Close bottom panel if both left and right are null
    if (!bottomLeftPanel && !bottomRightPanel && bottomPanelOpen) {
      setBottomPanelOpen(false)
    } else if ((bottomLeftPanel || bottomRightPanel) && !bottomPanelOpen) {
      setBottomPanelOpen(true)
    }
  }, [bottomLeftPanel, bottomRightPanel, bottomPanelOpen])
  
  // Load AIM-OS stats on mount (memoized)
  useEffect(() => {
    const loadStats = async () => {
      const stats = await getStats()
      const metrics = await getMetrics()
      setCmcStats(stats)
      setCasMetrics(metrics)
    }
    loadStats()
  }, [getStats, getMetrics])
  
  // Memoized helper function
  const getPanelIdByType = useCallback((type: string, zone: 'left' | 'right' | 'bottom'): string | null => {
    const panels = zone === 'left' ? leftPanels : zone === 'right' ? rightPanels : bottomPanels
    const panel = panels.find(p => p.type === type)
    return panel?.id || null
  }, [leftPanels, rightPanels, bottomPanels])
  
  return (
    <div className="flex flex-col h-screen bg-gray-950 text-gray-100">
      {/* Top Bar */}
      <TopBar 
        cmcStats={cmcStats}
        casMetrics={casMetrics}
        topPanelOpen={topPanelOpen}
        onTopPanelToggle={handleTopPanelToggle}
        mainView={mainView}
        openFiles={openFiles}
        activeFileId={activeFileId}
        onFileSelect={setActiveFileId}
        onFileClose={handleFileClose}
        showFileDropdown={showFileDropdown}
        onFileDropdownToggle={() => setShowFileDropdown(!showFileDropdown)}
        leftPanelOpen={leftPanelOpen}
        leftPanelRightEdge={leftPanelRightEdge}
      />
      
      {/* Main Layout */}
      <PanelGroup direction="vertical" className="flex-1">
        <Panel defaultSize={bottomPanelOpen ? 75 : 100} minSize={50}>
          <div className="flex-1 flex overflow-hidden h-full">
            {/* Left Vertical Toolbar with Top/Bottom Sections - Always Visible */}
            <div ref={leftToolbarRef} className="w-8 bg-gray-950 border-r border-gray-800 flex flex-col h-full">
              {/* Top Section */}
              <div 
                className={`flex flex-col items-center py-2 gap-1 ${
                  dragOverSection === 'top' && dragOverToolbar === 'left' ? 'bg-gray-800/30' : ''
                }`}
                onDragOver={(e) => handleDragOver(e, 'top', 'left')}
                onDragLeave={handleDragLeave}
                onDrop={(e) => handleDrop(e, 'top', 'left')}
              >
                {leftToolbarButtons
                  .filter(btn => btn.section === 'top')
                  .map(btn => {
                    const Icon = btn.icon
                    const isActive = leftTopPanel === btn.id
                    const isGlowing = appPreviewControlsGlow && btn.id === 'app-preview-controls'
                    return (
                <button
                        key={btn.id}
                        draggable
                        onDragStart={(e) => handleDragStart(e, btn.id, 'left')}
                        onDragEnd={handleDragEnd}
                        onClick={() => handleLeftPanelChange(btn.id, 'top')}
                        className={`w-8 h-8 rounded flex items-center justify-center transition-all duration-300 ${
                          isActive
                            ? 'bg-gray-800 text-gray-100 border border-gray-700' 
                            : 'text-gray-400 hover:bg-gray-900 hover:text-gray-200 border border-transparent'
                        } ${draggedButtonId === btn.id && draggedFromToolbar === 'left' ? 'opacity-50' : ''} ${
                          isGlowing ? 'animate-pulse ring-2 ring-blue-500 ring-opacity-75 shadow-lg shadow-blue-500/50' : ''
                        }`}
                        title={btn.title.replace('\n', '&#10;')}
                      >
                        <Icon className="w-3 h-3" />
                </button>
                    )
                  })}
                
                {/* Drop Zone - Button-sized space above divider */}
                <div 
                  className={`w-full h-10 flex items-center justify-center transition-colors ${
                    (dragOverSection === 'top' || dragOverSection === 'bottom') && dragOverToolbar === 'left' ? 'bg-gray-800/40' : ''
                  }`}
                  onDragOver={(e) => {
                    e.preventDefault()
                    e.dataTransfer.dropEffect = 'move'
                    const rect = e.currentTarget.getBoundingClientRect()
                    const y = e.clientY - rect.top
                    if (y < rect.height / 2) {
                      handleDragOver(e, 'top', 'left')
                    } else {
                      handleDragOver(e, 'bottom', 'left')
                    }
                  }}
                  onDragLeave={handleDragLeave}
                  onDrop={(e) => {
                    e.preventDefault()
                    const rect = e.currentTarget.getBoundingClientRect()
                    const y = e.clientY - rect.top
                    handleDrop(e, y < rect.height / 2 ? 'top' : 'bottom', 'left')
                  }}
                />
                
                {/* Prominent Separator - Below drop zone */}
                <div className="w-full flex flex-col items-center mb-2">
                  <div className="w-10 h-0.5 bg-gray-700 border-t border-b border-gray-800 flex items-center justify-center relative">
                    <ChevronUp className="w-2 h-2 text-gray-600 absolute -top-1" />
                    <ChevronDown className="w-2 h-2 text-gray-600 absolute -bottom-1" />
                  </div>
                </div>
              </div>
              
              {/* Bottom Section */}
              <div 
                className={`flex-1 flex flex-col items-center py-2 gap-1 ${
                  dragOverSection === 'bottom' && dragOverToolbar === 'left' ? 'bg-gray-800/30' : ''
                }`}
                onDragOver={(e) => handleDragOver(e, 'bottom', 'left')}
                onDragLeave={handleDragLeave}
                onDrop={(e) => handleDrop(e, 'bottom', 'left')}
              >
                {leftToolbarButtons
                  .filter(btn => btn.section === 'bottom')
                  .map(btn => {
                    const Icon = btn.icon
                    const isActive = leftBottomPanel === btn.id
                    return (
                <button
                        key={btn.id}
                        draggable
                        onDragStart={(e) => handleDragStart(e, btn.id, 'left')}
                        onDragEnd={handleDragEnd}
                        onClick={() => handleLeftPanelChange(btn.id, 'bottom')}
                        className={`w-8 h-8 rounded flex items-center justify-center transition-colors ${
                          isActive
                            ? 'bg-gray-800 text-gray-100 border border-gray-700' 
                            : 'text-gray-400 hover:bg-gray-900 hover:text-gray-200 border border-transparent'
                        } ${draggedButtonId === btn.id && draggedFromToolbar === 'left' ? 'opacity-50' : ''}`}
                        title={btn.title.replace('\n', '&#10;')}
                >
                        <Icon className="w-3 h-3" />
                </button>
                    )
                  })}
              </div>
              
              {/* Separator */}
              <div className="w-8 h-px bg-gray-800 my-1" />
              
              {/* Left Panel Toggle Button */}
                <button
                onClick={handleLeftPanelToggle}
                className={`w-8 h-8 rounded flex items-center justify-center transition-colors border ${
                  leftPanelOpen
                    ? 'bg-gray-800 text-gray-100 border-gray-700' 
                    : 'text-gray-400 hover:bg-gray-900 hover:text-gray-200 border-transparent'
                  }`}
                title={leftPanelOpen ? "Hide Left Panel" : "Show Left Panel"}
                >
                {leftPanelOpen ? (
                  <ChevronLeft className="w-3 h-3" />
                ) : (
                  <ChevronRight className="w-3 h-3" />
                )}
                </button>
              </div>
              
            <PanelGroup direction="horizontal">
              {/* Left Drawer - Supports Top/Bottom Split */}
              {leftPanelOpen && (
                <Panel 
                  defaultSize={20} 
                  minSize={15} 
                  maxSize={35} 
                  className="bg-gray-950 border-r border-gray-800"
                >
                  <div ref={leftPanelRef} className="h-full flex flex-col">
                    {leftTopPanel && leftBottomPanel ? (
                      // Both panels open - split top/bottom
                      <PanelGroup direction="vertical" className="flex-1">
                        <Panel defaultSize={50} minSize={20}>
                          <div className="h-full overflow-auto">
                            <ErrorBoundary panelName="Left Top Panel">
                              {leftTopPanel === 'explorer' && (
                                <LazyPanelWrapper>
                                  <LazyFileTree />
                                </LazyPanelWrapper>
                              )}
                              {leftTopPanel === 'memory' && (
                                <LazyPanelWrapper>
                                  <LazyMemoryBrowser />
                                </LazyPanelWrapper>
                              )}
                              {leftTopPanel === 'status' && (
                                <LazyPanelWrapper>
                                  <LazySystemStatus metrics={casMetrics} />
                                </LazyPanelWrapper>
                              )}
                              {leftTopPanel === 'app-preview-controls' && (
                                <LazyPanelWrapper>
                                  <LazyAppPreviewControls />
                                </LazyPanelWrapper>
                              )}
                              {leftTopPanel === 'debug-console' && (
                                <LazyPanelWrapper>
                                  <LazyDebugConsolePanel />
                                </LazyPanelWrapper>
                              )}
                            </ErrorBoundary>
                          </div>
                        </Panel>
                        <PanelResizeHandle className="h-1 bg-gray-800 hover:bg-gray-700 transition-colors cursor-row-resize" />
                        <Panel defaultSize={50} minSize={20}>
                          <div className="h-full overflow-auto">
                            <ErrorBoundary panelName="Left Bottom Panel">
                              {leftBottomPanel === 'explorer' && (
                                <LazyPanelWrapper>
                                  <LazyFileTree />
                                </LazyPanelWrapper>
                              )}
                              {leftBottomPanel === 'memory' && (
                                <LazyPanelWrapper>
                                  <LazyMemoryBrowser />
                                </LazyPanelWrapper>
                              )}
                              {leftBottomPanel === 'status' && (
                                <LazyPanelWrapper>
                                  <LazySystemStatus metrics={casMetrics} />
                                </LazyPanelWrapper>
                              )}
                              {leftBottomPanel === 'app-preview-controls' && (
                                <LazyPanelWrapper>
                                  <LazyAppPreviewControls />
                                </LazyPanelWrapper>
                              )}
                              {leftBottomPanel === 'debug-console' && (
                                <LazyPanelWrapper>
                                  <LazyDebugConsolePanel />
                                </LazyPanelWrapper>
                              )}
                            </ErrorBoundary>
                          </div>
                        </Panel>
                      </PanelGroup>
                    ) : (
                      // Single panel or no panel
              <div className="flex-1 overflow-auto">
                <ErrorBoundary panelName="Left Panel">
                          {(leftTopPanel || leftBottomPanel) === 'explorer' && (
                    <LazyPanelWrapper>
                      <LazyFileTree />
                    </LazyPanelWrapper>
                  )}
                          {(leftTopPanel || leftBottomPanel) === 'memory' && (
                    <LazyPanelWrapper>
                      <LazyMemoryBrowser />
                    </LazyPanelWrapper>
                  )}
                          {(leftTopPanel || leftBottomPanel) === 'status' && (
                    <LazyPanelWrapper>
                      <LazySystemStatus metrics={casMetrics} />
                    </LazyPanelWrapper>
                  )}
                          {(leftTopPanel || leftBottomPanel) === 'app-preview-controls' && (
                    <LazyPanelWrapper>
                      <LazyAppPreviewControls />
                    </LazyPanelWrapper>
                  )}
                          {(leftTopPanel || leftBottomPanel) === 'debug-console' && (
                    <LazyPanelWrapper>
                      <LazyDebugConsolePanel />
                    </LazyPanelWrapper>
                  )}
                          {!leftTopPanel && !leftBottomPanel && (
                    <div className="p-4 text-gray-500 text-center">
                      No panel selected
                    </div>
                  )}
                </ErrorBoundary>
              </div>
                    )}
            </div>
          </Panel>
              )}
          
              {leftPanelOpen && (
                <PanelResizeHandle className="w-1 bg-gray-800 hover:bg-gray-700 transition-colors" />
              )}
          
          {/* Main Content Area */}
          <Panel defaultSize={50} minSize={30} data-main-content-area>
            <PanelGroup direction="vertical" className="h-full">
                {/* Top Panel - Only shown if topPanelOpen */}
                {topPanelOpen && (
                  <Panel defaultSize={bottomPanelOpen ? 75 : 100} minSize={50}>
                    <div className="h-full flex">
                      {/* Main View Vertical Toolbar with Left/Right Sections */}
                      <div className="w-8 bg-gray-950 border-r border-gray-800 flex flex-col h-full">
                        {/* Left Section */}
                        <div 
                          className={`flex flex-col items-center py-2 gap-1 ${
                            dragOverSection === 'left' && dragOverToolbar === 'main' ? 'bg-gray-800/30' : ''
                          }`}
                          onDragOver={(e) => handleDragOver(e, 'left', 'main')}
                          onDragLeave={handleDragLeave}
                          onDrop={(e) => handleDrop(e, 'left', 'main')}
                        >
                          {mainToolbarButtons
                            .filter(btn => btn.section === 'left')
                            .map(btn => {
                              const Icon = btn.icon
                              const isActive = mainView === btn.id
                              return (
                                <button
                                  key={btn.id}
                                  draggable
                                  onDragStart={(e) => handleDragStart(e, btn.id, 'main')}
                                  onDragEnd={handleDragEnd}
                                  onClick={() => handleMainViewChange(btn.id)}
                                  className={`w-8 h-8 rounded flex items-center justify-center transition-colors ${
                                    isActive
                                      ? 'bg-gray-800 text-gray-100 border border-gray-700' 
                                      : 'text-gray-400 hover:bg-gray-900 hover:text-gray-200 border border-transparent'
                                  } ${draggedButtonId === btn.id && draggedFromToolbar === 'main' ? 'opacity-50' : ''}`}
                                  title={btn.title.replace('\n', '&#10;')}
                                >
                                  <Icon className="w-3 h-3" />
                                </button>
                              )
                            })}
                          
                          {/* Drop Zone - Button-sized space above diagonal divider */}
                          <div 
                            className={`w-full h-10 flex items-center justify-center transition-colors ${
                              (dragOverSection === 'left' || dragOverSection === 'right') && dragOverToolbar === 'main' ? 'bg-gray-800/40' : ''
                            }`}
                            onDragOver={(e) => {
                              e.preventDefault()
                              e.dataTransfer.dropEffect = 'move'
                              // Determine which section based on mouse position
                              const rect = e.currentTarget.getBoundingClientRect()
                              const y = e.clientY - rect.top
                              if (y < rect.height / 2) {
                                handleDragOver(e, 'left', 'main')
                              } else {
                                handleDragOver(e, 'right', 'main')
                              }
                            }}
                            onDragLeave={handleDragLeave}
                            onDrop={(e) => {
                              e.preventDefault()
                              const rect = e.currentTarget.getBoundingClientRect()
                              const y = e.clientY - rect.top
                              handleDrop(e, y < rect.height / 2 ? 'left' : 'right', 'main')
                            }}
                          />
                          
                          {/* Diagonal Separator - 25 degree angle (right side up, left down) */}
                          <div className="w-full flex flex-col items-center mb-2">
                            <div className="relative w-10 h-0.5 flex items-center justify-center">
                              <div 
                                className="absolute w-full h-0.5 bg-gray-700 border-t border-b border-gray-800"
                                style={{
                                  transform: 'rotate(25deg)',
                                  transformOrigin: 'center'
                                }}
                              />
                              <ChevronUp className="w-2 h-2 text-gray-600 absolute -top-1 right-0" />
                              <ChevronDown className="w-2 h-2 text-gray-600 absolute -bottom-1 left-0" />
                            </div>
                          </div>
                        </div>
                        
                        {/* Right Section */}
                        <div 
                          className={`flex flex-col items-center py-2 gap-1 ${
                            dragOverSection === 'right' && dragOverToolbar === 'main' ? 'bg-gray-800/30' : ''
                          }`}
                          onDragOver={(e) => handleDragOver(e, 'right', 'main')}
                          onDragLeave={handleDragLeave}
                          onDrop={(e) => handleDrop(e, 'right', 'main')}
                        >
                          {mainToolbarButtons
                            .filter(btn => btn.section === 'right')
                            .map(btn => {
                              const Icon = btn.icon
                              const isActive = mainView === btn.id
                              return (
                                <button
                                  key={btn.id}
                                  draggable
                                  onDragStart={(e) => handleDragStart(e, btn.id, 'main')}
                                  onDragEnd={handleDragEnd}
                                  onClick={() => handleMainViewChange(btn.id)}
                                  className={`w-8 h-8 rounded flex items-center justify-center transition-colors ${
                                    isActive
                                      ? 'bg-gray-800 text-gray-100 border border-gray-700' 
                                      : 'text-gray-400 hover:bg-gray-900 hover:text-gray-200 border border-transparent'
                                  } ${draggedButtonId === btn.id && draggedFromToolbar === 'main' ? 'opacity-50' : ''}`}
                                  title={btn.title.replace('\n', '&#10;')}
                                >
                                  <Icon className="w-3 h-3" />
                                </button>
                              )
                            })}
                        </div>
                      </div>
                      
                      {/* Main Content Area */}
                      <div className="flex-1 bg-gray-950 flex flex-col" style={{ minHeight: 0 }}>
              <ErrorBoundary panelName="Main View">
                {mainView === 'code' && (
                  <LazyPanelWrapper>
                    <LazyCodeEditor />
                  </LazyPanelWrapper>
                )}
                {mainView === 'evolution' && (
                  <LazyPanelWrapper>
                    <LazyEvolutionExplorer />
                  </LazyPanelWrapper>
                )}
                {mainView === 'consciousness' && (
                  <LazyPanelWrapper>
                    <LazyConsciousnessVisualization />
                  </LazyPanelWrapper>
                )}
                {mainView === 'orchestration' && (
                  <LazyPanelWrapper>
                    <LazyAIMOSOrchestration />
                  </LazyPanelWrapper>
                )}
                          {mainView === 'app-preview' && (
                            <LazyPanelWrapper>
                              <LazyAppPreview onClose={() => handleMainViewChange('code')} />
                  </LazyPanelWrapper>
                )}
                {mainView === 'document-editor' && (
                  <LazyPanelWrapper>
                    <LazyDocumentEditor />
                  </LazyPanelWrapper>
                )}
              </ErrorBoundary>
                      </div>
            </div>
          </Panel>
                )}
                    
                    {/* PanelResizeHandle between top and bottom panels */}
                    {topPanelOpen && bottomPanelOpen && (
                      <PanelResizeHandle className="h-1 bg-gray-800 hover:bg-gray-700 transition-colors cursor-row-resize" />
                    )}
          
                    {/* Bottom Panel - Inset Between Left and Right Panels */}
                    {bottomPanelOpen && !topPanelOpen && (
                      <PanelResizeHandle className="h-1 bg-gray-800 hover:bg-gray-700 transition-colors cursor-row-resize" />
                    )}
                    
                    {bottomPanelOpen && (
                      <Panel 
                        defaultSize={topPanelOpen ? 25 : 100} 
                        minSize={10} 
                        maxSize={50} 
                        className="bg-gray-950 border-t border-gray-800"
                      >
                        <div className="h-full flex">
                          {/* Bottom Panel Vertical Toolbar with Left/Right Sections */}
                          <div className="w-8 bg-gray-950 border-r border-gray-800 flex flex-col h-full">
                            {/* Left Section */}
                            <div 
                              className={`flex flex-col items-center py-2 gap-1 ${
                                dragOverSection === 'left' && dragOverToolbar === 'bottom' ? 'bg-gray-800/30' : ''
                              }`}
                              onDragOver={(e) => handleDragOver(e, 'left', 'bottom')}
                              onDragLeave={handleDragLeave}
                              onDrop={(e) => handleDrop(e, 'left', 'bottom')}
                            >
                              {bottomToolbarButtons
                                .filter(btn => btn.section === 'left')
                                .map(btn => {
                                  const Icon = btn.icon
                                  const isActive = bottomLeftPanel === btn.id || (bottomPanel === btn.id && !bottomRightPanel)
                                  return (
                <button
                                      key={btn.id}
                                      draggable
                                      onDragStart={(e) => handleDragStart(e, btn.id, 'bottom')}
                                      onDragEnd={handleDragEnd}
                                      onClick={() => handleBottomLeftPanelChange(btn.id)}
                                      className={`w-8 h-8 rounded flex items-center justify-center transition-colors ${
                                        isActive
                                          ? 'bg-gray-800 text-gray-100 border border-gray-700' 
                                          : 'text-gray-400 hover:bg-gray-950 hover:text-gray-200 border border-transparent'
                                      } ${draggedButtonId === btn.id && draggedFromToolbar === 'bottom' ? 'opacity-50' : ''}`}
                                      title={btn.title.replace('\n', '&#10;')}
                >
                                      <Icon className="w-3 h-3" />
                </button>
                                  )
                                })}
                              
                              {/* Drop Zone - Button-sized space above diagonal divider */}
                              <div 
                                className={`w-full h-10 flex items-center justify-center transition-colors ${
                                  (dragOverSection === 'left' || dragOverSection === 'right') && dragOverToolbar === 'bottom' ? 'bg-gray-800/40' : ''
                                }`}
                                onDragOver={(e) => {
                                  e.preventDefault()
                                  e.dataTransfer.dropEffect = 'move'
                                  // Determine which section based on mouse position
                                  const rect = e.currentTarget.getBoundingClientRect()
                                  const x = e.clientX - rect.left
                                  if (x < rect.width / 2) {
                                    handleDragOver(e, 'left', 'bottom')
                                  } else {
                                    handleDragOver(e, 'right', 'bottom')
                                  }
                                }}
                                onDragLeave={handleDragLeave}
                                onDrop={(e) => {
                                  e.preventDefault()
                                  const rect = e.currentTarget.getBoundingClientRect()
                                  const x = e.clientX - rect.left
                                  handleDrop(e, x < rect.width / 2 ? 'left' : 'right', 'bottom')
                                }}
                              />
                              
                              {/* Diagonal Separator - 25 degree angle (right side up, left down) */}
                              <div className="w-full flex flex-col items-center mb-2">
                                <div className="relative w-10 h-0.5 flex items-center justify-center">
                                  <div 
                                    className="absolute w-full h-0.5 bg-gray-700 border-t border-b border-gray-800"
                                    style={{
                                      transform: 'rotate(25deg)',
                                      transformOrigin: 'center'
                                    }}
                                  />
                                  <ChevronUp className="w-2 h-2 text-gray-600 absolute -top-1 right-0" />
                                  <ChevronDown className="w-2 h-2 text-gray-600 absolute -bottom-1 left-0" />
                                </div>
                              </div>
                            </div>
                            
                            {/* Right Section */}
                            <div 
                              className={`flex-1 flex flex-col items-center py-2 gap-1 ${
                                dragOverSection === 'right' && dragOverToolbar === 'bottom' ? 'bg-gray-800/30' : ''
                              }`}
                              onDragOver={(e) => handleDragOver(e, 'right', 'bottom')}
                              onDragLeave={handleDragLeave}
                              onDrop={(e) => handleDrop(e, 'right', 'bottom')}
                            >
                              {bottomToolbarButtons
                                .filter(btn => btn.section === 'right')
                                .map(btn => {
                                  const Icon = btn.icon
                                  const isActive = bottomRightPanel === btn.id || (bottomPanel === btn.id && !bottomLeftPanel)
                                  return (
                                    <button
                                      key={btn.id}
                                      draggable
                                      onDragStart={(e) => handleDragStart(e, btn.id, 'bottom')}
                                      onDragEnd={handleDragEnd}
                                      onClick={() => handleBottomRightPanelChange(btn.id)}
                                      className={`w-8 h-8 rounded flex items-center justify-center transition-colors ${
                                        isActive
                                          ? 'bg-gray-800 text-gray-100 border border-gray-700' 
                                          : 'text-gray-400 hover:bg-gray-950 hover:text-gray-200 border border-transparent'
                                      } ${draggedButtonId === btn.id && draggedFromToolbar === 'bottom' ? 'opacity-50' : ''}`}
                                      title={btn.title.replace('\n', '&#10;')}
                >
                                      <Icon className="w-3 h-3" />
                </button>
                                  )
                                })}
              </div>
              
                            {/* Separator */}
                            <div className="w-8 h-px bg-gray-800 my-1" />
                          </div>
                          
                          {/* Bottom Panel Content - Supports Left/Right Split */}
              <div className="flex-1 overflow-auto">
                            {bottomLeftPanel && bottomRightPanel ? (
                              // Both panels open - split left/right
                              <PanelGroup direction="horizontal" className="h-full">
                                <Panel defaultSize={50} minSize={20}>
                                  <div className="h-full overflow-auto">
                                    <ErrorBoundary panelName="Bottom Left Panel">
                                      {bottomLeftPanel === 'terminal' && (
                    <LazyPanelWrapper>
                                          <LazyTerminalPanel />
                    </LazyPanelWrapper>
                  )}
                                      {bottomLeftPanel === 'problems' && (
                                        <LazyPanelWrapper>
                                          <LazyProblemsPanel />
                                        </LazyPanelWrapper>
                                      )}
                                      {bottomLeftPanel === 'timeline' && (
                    <LazyPanelWrapper>
                      <LazyTimelineView />
                    </LazyPanelWrapper>
                  )}
                                      {bottomLeftPanel === 'debug-console' && (
                    <LazyPanelWrapper>
                                          <LazyDebugConsolePanel onStatusChange={setBottomLeftPanelStatus} />
                    </LazyPanelWrapper>
                  )}
                                      {bottomLeftPanel === 'log-sentinels-anomalies' && (
                                        <LazyPanelWrapper>
                                          <LazyLogSentinelsAnomalies />
                                        </LazyPanelWrapper>
                                      )}
                                    </ErrorBoundary>
                    </div>
                                </Panel>
                                <PanelResizeHandle className="w-1 bg-gray-800 hover:bg-gray-700 transition-colors cursor-col-resize" />
                                <Panel defaultSize={50} minSize={20}>
                                  <div ref={bottomRightPanelRef} className="h-full overflow-auto">
                                    <ErrorBoundary panelName="Bottom Right Panel">
                                      {bottomRightPanel === 'terminal' && (
                                        <LazyPanelWrapper>
                                          <LazyTerminalPanel />
                                        </LazyPanelWrapper>
                                      )}
                                      {bottomRightPanel === 'problems' && (
                                        <LazyPanelWrapper>
                                          <LazyProblemsPanel />
                                        </LazyPanelWrapper>
                                      )}
                                      {bottomRightPanel === 'timeline' && (
                                        <LazyPanelWrapper>
                                          <LazyTimelineView />
                                        </LazyPanelWrapper>
                                      )}
                                      {bottomRightPanel === 'debug-console' && (
                                        <LazyPanelWrapper>
                                          <LazyDebugConsolePanel onStatusChange={setBottomRightPanelStatus} />
                                        </LazyPanelWrapper>
                                      )}
                                      {bottomRightPanel === 'log-sentinels-summaries' && (
                                        <LazyPanelWrapper>
                                          <LazyLogSentinelsSummaries />
                                        </LazyPanelWrapper>
                                      )}
                                      {bottomRightPanel === 'tool-quality' && (
                                        <LazyPanelWrapper>
                                          <LazyToolQualityDashboard />
                                        </LazyPanelWrapper>
                                      )}
                                      {bottomRightPanel === 'log-analysis' && (
                                        <LazyPanelWrapper>
                                          <LazyLogAnalysisDashboard />
                                        </LazyPanelWrapper>
                  )}
                </ErrorBoundary>
            </div>
          </Panel>
        </PanelGroup>
                            ) : (
                              // Single panel or no panel
                              <ErrorBoundary panelName="Bottom Panel">
                                {(bottomLeftPanel || bottomRightPanel || bottomPanel) === 'terminal' && (
                                  <LazyPanelWrapper>
                                    <LazyTerminalPanel />
                                  </LazyPanelWrapper>
                                )}
                                {(bottomLeftPanel || bottomRightPanel || bottomPanel) === 'problems' && (
                                  <LazyPanelWrapper>
                                    <LazyProblemsPanel />
                                  </LazyPanelWrapper>
                                )}
                                {(bottomLeftPanel || bottomRightPanel || bottomPanel) === 'timeline' && (
                                  <LazyPanelWrapper>
                                    <LazyTimelineView />
                                  </LazyPanelWrapper>
                                )}
                                {(bottomLeftPanel || bottomRightPanel || bottomPanel) === 'debug-console' && (
                                  <LazyPanelWrapper>
                                    <LazyDebugConsolePanel onStatusChange={(status) => {
                                      if (bottomLeftPanel === 'debug-console') setBottomLeftPanelStatus(status)
                                      if (bottomRightPanel === 'debug-console') setBottomRightPanelStatus(status)
                                    }} />
                                  </LazyPanelWrapper>
                                )}
                                {(bottomLeftPanel || bottomRightPanel || bottomPanel) === 'log-sentinels-anomalies' && (
                                  <LazyPanelWrapper>
                                    <LazyLogSentinelsAnomalies />
                                  </LazyPanelWrapper>
                                )}
                                {(bottomLeftPanel || bottomRightPanel || bottomPanel) === 'log-sentinels-summaries' && (
                                  <LazyPanelWrapper>
                                    <LazyLogSentinelsSummaries />
                                  </LazyPanelWrapper>
                                )}
                                {(bottomLeftPanel || bottomRightPanel || bottomPanel) === 'tool-quality' && (
                                  <LazyPanelWrapper>
                                    <LazyToolQualityDashboard />
                                  </LazyPanelWrapper>
                                )}
                                {(bottomLeftPanel || bottomRightPanel || bottomPanel) === 'log-analysis' && (
                                  <LazyPanelWrapper>
                                    <LazyLogAnalysisDashboard />
                                  </LazyPanelWrapper>
                                )}
                                {(bottomLeftPanel || bottomRightPanel || bottomPanel) === 'context-ledger' && (
                                  <LazyPanelWrapper>
                                    <LazyContextLedger
                                      assembledContext={null}
                                      contextInfo={{}}
                                      channelId=""
                                      budget={12000}
                                    />
                                  </LazyPanelWrapper>
                                )}
                                {(bottomLeftPanel || bottomRightPanel || bottomPanel) === 'heatmap' && (
                                  <LazyPanelWrapper>
                                    <LazyChatHeatmapPanel
                                      messages={[]}
                                      contextInfo={{}}
                                      assembledContext={null}
                                      channelId=""
                                    />
                                  </LazyPanelWrapper>
                                )}
                              </ErrorBoundary>
                            )}
      </div>
                        </div>
                      </Panel>
                    )}
                  </PanelGroup>
              </Panel>
                
                {/* Right Drawer - Supports Top/Bottom Split */}
                {rightPanelOpen && (
                  <PanelResizeHandle className="w-1 bg-gray-800 hover:bg-gray-700 transition-colors" />
                )}
                
                {rightPanelOpen && (
                  <Panel defaultSize={30} minSize={20} maxSize={45} className="bg-gray-950 border-l border-gray-800">
                    <div ref={rightPanelRef} className="h-full flex flex-col">
                      {rightTopPanel && rightBottomPanel ? (
                        // Both panels open - split top/bottom
                        <PanelGroup direction="vertical" className="flex-1">
                          <Panel defaultSize={50} minSize={20}>
                            <div className="h-full overflow-auto">
                              <ErrorBoundary panelName="Right Top Panel">
                                {rightTopPanel === 'context-web' && (
                <LazyPanelWrapper>
                                    <LazyContextWeb />
                </LazyPanelWrapper>
              )}
                                {rightTopPanel === 'timeline' && (
                <LazyPanelWrapper>
                                    <LazyTimelineView />
                </LazyPanelWrapper>
              )}
                                {rightTopPanel === 'outline' && (
                                  <LazyPanelWrapper>
                                    <LazyOutlinePanel />
                                  </LazyPanelWrapper>
                                )}
                                {rightTopPanel === 'ai-chat' && (
                                  <LazyPanelWrapper>
                                    <LazyAIChatManagement />
                                  </LazyPanelWrapper>
                                )}
                                {rightTopPanel === 'router' && (
                                  <LazyPanelWrapper>
                                    <LazyRouterPanel />
                                  </LazyPanelWrapper>
                                )}
                                {rightTopPanel === 'debug-console' && (
                                  <LazyPanelWrapper>
                                    <LazyDebugConsolePanel />
                                  </LazyPanelWrapper>
                                )}
                              </ErrorBoundary>
                            </div>
                          </Panel>
                          <PanelResizeHandle className="h-1 bg-gray-800 hover:bg-gray-700 transition-colors cursor-row-resize" />
                          <Panel defaultSize={50} minSize={20}>
                            <div className="h-full overflow-auto">
                              <ErrorBoundary panelName="Right Bottom Panel">
                                {rightBottomPanel === 'context-web' && (
                                  <LazyPanelWrapper>
                                    <LazyContextWeb />
                                  </LazyPanelWrapper>
                                )}
                                {rightBottomPanel === 'timeline' && (
                 <LazyPanelWrapper>
                   <LazyTimelineView />
                 </LazyPanelWrapper>
               )}
                                {rightBottomPanel === 'outline' && (
                                  <LazyPanelWrapper>
                                    <LazyOutlinePanel />
                                  </LazyPanelWrapper>
                                )}
                                {rightBottomPanel === 'ai-chat' && (
                                  <LazyPanelWrapper>
                                    <LazyAIChatManagement />
                                  </LazyPanelWrapper>
                                )}
                                {rightBottomPanel === 'router' && (
                                  <LazyPanelWrapper>
                                    <LazyRouterPanel />
                                  </LazyPanelWrapper>
                                )}
                                {rightBottomPanel === 'debug-console' && (
                                  <LazyPanelWrapper>
                                    <LazyDebugConsolePanel />
                                  </LazyPanelWrapper>
                                )}
                              </ErrorBoundary>
                            </div>
                          </Panel>
                        </PanelGroup>
                      ) : (
                        // Single panel or no panel
              <div className="flex-1 overflow-auto">
                <ErrorBoundary panelName="Right Panel">
                            {(rightTopPanel || rightBottomPanel) === 'context-web' && (
                    <LazyPanelWrapper>
                      <LazyContextWeb />
                    </LazyPanelWrapper>
                  )}
                            {(rightTopPanel || rightBottomPanel) === 'timeline' && (
                    <LazyPanelWrapper>
                      <LazyTimelineView />
                    </LazyPanelWrapper>
                  )}
                            {(rightTopPanel || rightBottomPanel) === 'outline' && (
                    <LazyPanelWrapper>
                      <LazyOutlinePanel />
                    </LazyPanelWrapper>
                  )}
                            {(rightTopPanel || rightBottomPanel) === 'ai-chat' && (
                              <LazyPanelWrapper>
                                <LazyAIChatManagement />
                              </LazyPanelWrapper>
                            )}
                            {(rightTopPanel || rightBottomPanel) === 'router' && (
                              <LazyPanelWrapper>
                                <LazyRouterPanel />
                              </LazyPanelWrapper>
                            )}
                            {(rightTopPanel || rightBottomPanel) === 'debug-console' && (
                              <LazyPanelWrapper>
                                <LazyDebugConsolePanel />
                              </LazyPanelWrapper>
                            )}
                            {!rightTopPanel && !rightBottomPanel && (
                    <div className="p-4 text-gray-500 text-center">
                      No panel selected
                    </div>
                  )}
                </ErrorBoundary>
              </div>
                      )}
            </div>
          </Panel>
                )}
                
                {/* Right Vertical Toolbar with Top/Bottom Sections - Always Visible */}
                <div className="w-8 bg-gray-950 border-r border-gray-800 flex flex-col h-full">
                  {/* Top Section */}
                  <div 
                    className={`flex flex-col items-center py-2 gap-1 ${
                      dragOverSection === 'top' && dragOverToolbar === 'right' ? 'bg-gray-800/30' : ''
                    }`}
                    onDragOver={(e) => handleDragOver(e, 'top', 'right')}
                    onDragLeave={handleDragLeave}
                    onDrop={(e) => handleDrop(e, 'top', 'right')}
                  >
                    {rightToolbarButtons
                      .filter(btn => btn.section === 'top')
                      .map(btn => {
                        const Icon = btn.icon
                        const isActive = rightTopPanel === btn.id
                        return (
            <button
                            key={btn.id}
                            draggable
                            onDragStart={(e) => handleDragStart(e, btn.id, 'right')}
                            onDragEnd={handleDragEnd}
                            onClick={() => handleRightPanelChange(btn.id, 'top')}
                            className={`w-8 h-8 rounded flex items-center justify-center transition-colors ${
                              isActive
                                ? 'bg-gray-800 text-gray-100 border border-gray-700' 
                                : 'text-gray-400 hover:bg-gray-900 hover:text-gray-200 border border-transparent'
                            } ${draggedButtonId === btn.id && draggedFromToolbar === 'right' ? 'opacity-50' : ''}`}
                            title={btn.title.replace('\n', '&#10;')}
                          >
                            <Icon className="w-3 h-3" />
            </button>
                        )
                      })}
                    
                    {/* Drop Zone - Button-sized space above divider */}
                    <div 
                      className={`w-full h-10 flex items-center justify-center transition-colors ${
                        (dragOverSection === 'top' || dragOverSection === 'bottom') && dragOverToolbar === 'right' ? 'bg-gray-800/40' : ''
                      }`}
                      onDragOver={(e) => {
                        e.preventDefault()
                        e.dataTransfer.dropEffect = 'move'
                        const rect = e.currentTarget.getBoundingClientRect()
                        const y = e.clientY - rect.top
                        if (y < rect.height / 2) {
                          handleDragOver(e, 'top', 'right')
                        } else {
                          handleDragOver(e, 'bottom', 'right')
                        }
                      }}
                      onDragLeave={handleDragLeave}
                      onDrop={(e) => {
                        e.preventDefault()
                        const rect = e.currentTarget.getBoundingClientRect()
                        const y = e.clientY - rect.top
                        handleDrop(e, y < rect.height / 2 ? 'top' : 'bottom', 'right')
                      }}
                    />
                    
                    {/* Prominent Separator - Below drop zone */}
                    <div className="w-full flex flex-col items-center mb-2">
                      <div className="w-10 h-0.5 bg-gray-700 border-t border-b border-gray-800 flex items-center justify-center relative">
                        <ChevronUp className="w-2 h-2 text-gray-600 absolute -top-1" />
                        <ChevronDown className="w-2 h-2 text-gray-600 absolute -bottom-1" />
                      </div>
                    </div>
                  </div>
                  
                  {/* Bottom Section */}
                  <div 
                    className={`flex-1 flex flex-col items-center py-2 gap-1 ${
                      dragOverSection === 'bottom' && dragOverToolbar === 'right' ? 'bg-gray-800/30' : ''
              }`}
                    onDragOver={(e) => handleDragOver(e, 'bottom', 'right')}
                    onDragLeave={handleDragLeave}
                    onDrop={(e) => handleDrop(e, 'bottom', 'right')}
                  >
                    {rightToolbarButtons
                      .filter(btn => btn.section === 'bottom')
                      .map(btn => {
                        const Icon = btn.icon
                        const isActive = rightBottomPanel === btn.id
                        return (
            <button
                            key={btn.id}
                            draggable
                            onDragStart={(e) => handleDragStart(e, btn.id, 'right')}
                            onDragEnd={handleDragEnd}
                            onClick={() => handleRightPanelChange(btn.id, 'bottom')}
                            className={`w-8 h-8 rounded flex items-center justify-center transition-colors ${
                              isActive
                                ? 'bg-gray-800 text-gray-100 border border-gray-700' 
                                : 'text-gray-400 hover:bg-gray-900 hover:text-gray-200 border border-transparent'
                            } ${draggedButtonId === btn.id && draggedFromToolbar === 'right' ? 'opacity-50' : ''}`}
                            title={btn.title.replace('\n', '&#10;')}
            >
                            <Icon className="w-3 h-3" />
            </button>
                        )
                      })}
          </div>
          
                  {/* Separator */}
                  <div className="w-8 h-px bg-gray-800 my-1" />
                  
                  {/* Right Panel Toggle Button */}
            <button
                    onClick={handleRightPanelToggle}
                    className={`w-8 h-8 rounded flex items-center justify-center transition-colors border ${
                      rightPanelOpen
                        ? 'bg-gray-800 text-gray-100 border-gray-700' 
                        : 'text-gray-400 hover:bg-gray-900 hover:text-gray-200 border-transparent'
                    }`}
                    title={rightPanelOpen ? "Hide Right Panel" : "Show Right Panel"}
                  >
                    {rightPanelOpen ? (
                      <ChevronRight className="w-3 h-3" />
                    ) : (
                      <ChevronLeft className="w-3 h-3" />
              )}
            </button>
          </div>
              </PanelGroup>
        </div>
        </Panel>
      </PanelGroup>
      
      {/* Bottom Status Bar - Full Width */}
      <div className="h-8 bg-gray-950 border-t border-gray-800 flex items-center relative">
        {/* CMC + VIF Integration Status */}
        <div 
          ref={bottomStatusDataRef}
          className="flex items-center gap-3 text-xs text-gray-300 ml-3"
        >
          {cmcStats && (
            <div className="flex items-center gap-1.5">
              <Database className="w-3 h-3" />
              <span>CMC: {cmcStats?.total_atoms || 0}</span>
        </div>
      )}
          <div className="flex items-center gap-1.5 text-gray-200">
            <Shield className="w-3 h-3" />
            <span>VIF + SEG Active</span>
          </div>
        </div>
        
        {/* Divider - Aligns with left panel right edge, minimum at status data */}
        <div 
          className="absolute top-0 bottom-0 w-px bg-gray-800 transition-all duration-200"
          style={{
            left: `${Math.max(leftPanelRightEdge, bottomStatusDataRightEdge)}px`
          }}
        />
        
        {/* Divider - Aligns with right panel left edge */}
        {rightPanelOpen && (
          <div 
            className="absolute top-0 bottom-0 w-px bg-gray-800 transition-all duration-200"
            style={{
              left: `${Math.max(leftPanelRightEdge, Math.min(rightPanelLeftEdge, window.innerWidth - 50))}px`
            }}
          />
        )}
        
        {/* Divider - Aligns with bottom right panel left edge (only if 2 panels open in bottom) */}
        {bottomLeftPanel && bottomRightPanel && bottomPanelOpen && (
          <div 
            className="absolute top-0 bottom-0 w-px bg-gray-800 transition-all duration-200"
            style={{
              left: `${Math.max(leftPanelRightEdge, Math.min(bottomRightPanelLeftEdge, window.innerWidth - 50))}px`
            }}
          />
        )}
        
        {/* Panel Status Display - Between dividers */}
        {bottomPanelOpen && (
          <>
            {/* Left Panel Status - Between left divider and next divider/right edge */}
            {bottomLeftPanelStatus && (
              <div 
                className="absolute top-0 bottom-0 flex items-center text-xs text-gray-400 px-3 overflow-hidden"
                style={{
                  left: `${Math.max(leftPanelRightEdge, bottomStatusDataRightEdge) + 4}px`,
                  right: bottomLeftPanel && bottomRightPanel && bottomPanelOpen
                    ? `${window.innerWidth - Math.min(bottomRightPanelLeftEdge, window.innerWidth - 50) + 4}px`
                    : rightPanelOpen
                      ? `${window.innerWidth - Math.min(rightPanelLeftEdge, window.innerWidth - 50) + 4}px`
                      : '50px'
                }}
              >
                <span className="truncate">{bottomLeftPanelStatus}</span>
              </div>
            )}
            
            {/* Right Panel Status - Between bottom right panel divider and right edge (only if 2 panels open) */}
            {bottomRightPanelStatus && bottomLeftPanel && bottomRightPanel && (
              <div 
                className="absolute top-0 bottom-0 flex items-center text-xs text-gray-400 px-3 overflow-hidden"
                style={{
                  left: `${Math.min(bottomRightPanelLeftEdge, window.innerWidth - 50) + 4}px`,
                  right: '50px'
                }}
              >
                <span className="truncate">{bottomRightPanelStatus}</span>
              </div>
            )}
          </>
        )}
        
        {/* Bottom Panel Toggle Button - Anchored to right side of divider */}
        <button
          onClick={handleBottomDrawerToggle}
          className={`absolute w-6 h-6 rounded flex items-center justify-center transition-colors ${
            bottomPanelOpen
              ? 'bg-gray-800 text-gray-100' 
              : 'text-gray-400 hover:bg-gray-800 hover:text-gray-200'
          }`}
          style={{
            left: `${Math.max(leftPanelRightEdge, bottomStatusDataRightEdge) + 4}px`
          }}
          title={bottomPanelOpen ? "Hide Bottom Panel" : "Show Bottom Panel"}
        >
          {bottomPanelOpen ? (
            <ChevronDown className="w-4 h-4" />
          ) : (
            <ChevronUp className="w-4 h-4" />
          )}
        </button>
        
        <div className="flex-1" />
        
        {/* DAC-V2 Label */}
        <div className="text-xs text-gray-400 font-medium mr-3">
          DAC-V2
        </div>
      </div>
    </div>
  )
}
