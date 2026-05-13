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
  LazyResourceMonitor,
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
  LazySystemIndexBrowserPanel,
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
  LazyBrowserAutomationPanel,
  LazyFilePreviewView,
  LazyCanvasView,
  LazyManagerAIChat,
  LazyBackendDesign,
} from '../utils/performance'
import { LucidChatPanel } from './lucid-chat/LucidChatPanel'
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
  Eye,
  MessageSquare,
  PanelLeftClose,
  PanelLeftOpen,
  PanelRightClose,
  PanelRightOpen,
  PanelBottomClose,
  PanelBottomOpen,
  Layers,
  Server,
} from 'lucide-react'

type LeftPanelType = 'explorer' | 'memory' | 'status' | 'resource-monitor' | 'app-preview-controls' | 'debug-console' | null
type RightPanelType = 'context-web' | 'timeline' | 'outline' | 'ai-chat' | 'router' | 'debug-console' | 'browser-automation' | 'lucid-chat' | 'system-index-browser' | 'system-map' | null
type BottomPanelType = 'terminal' | 'problems' | 'timeline' | 'debug-console' | 'log-sentinels-summaries' | 'log-sentinels-anomalies' | 'tool-quality' | 'log-analysis' | 'context-ledger' | 'heatmap' | null
type MainViewType = 'code' | 'evolution' | 'consciousness' | 'orchestration' | 'app-preview' | 'document-editor' | 'file-preview' | 'canvas' | 'manager-ai-chat' | 'backend-design'

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
  { id: 'resource-monitor', icon: Database, title: 'Resource Monitor\nTrack panel memory usage and loading states', section: 'bottom', toolbar: 'left' },
]

const RIGHT_TOOLBAR_BUTTONS: RightToolbarButton[] = [
  { id: 'context-web', icon: Network, title: 'Context Web\nInteractive SEG knowledge graph visualization with HHNI integration and topic evolution tracking', section: 'top', toolbar: 'right' },
  { id: 'timeline', icon: Clock, title: 'Timeline View\nTCS timeline with playback controls and bitemporal tracking', section: 'top', toolbar: 'right' },
  { id: 'router', icon: Zap, title: 'Tool Selection\nRouter tool proposals with probabilities and preconditions', section: 'top', toolbar: 'right' },
  { id: 'browser-automation', icon: Globe, title: 'Browser Automation\nAutomate AI chat pages (ChatGPT, Claude) with script execution and session management', section: 'top', toolbar: 'right' },
  { id: 'lucid-chat', icon: MessageSquare, title: 'Lucid Chat\nAI-driven visual communication with 3D models, audio, and diverse outputs', section: 'top', toolbar: 'right' },
  { id: 'outline', icon: Code, title: 'Outline\nSymbol navigation with HHNI hierarchical structure', section: 'bottom', toolbar: 'right' },
  { id: 'ai-chat', icon: Brain, title: 'AI Chat & Management\nAI agent communication, task management, and collaboration', section: 'top', toolbar: 'right' },
  { id: 'system-index-browser', icon: Layers, title: 'System Index Browser\nBrowse all system indexes with intent, architecture, integrations, and status', section: 'bottom', toolbar: 'right' },
  { id: 'system-map', icon: Network, title: 'System Map\nVisual system map showing AIM-OS system relationships and dependencies', section: 'bottom', toolbar: 'right' },
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
  { id: 'file-preview', icon: Eye, title: 'File Preview\nCursor-style markdown preview with syntax-highlighted code blocks', section: 'left', toolbar: 'main' },
  { id: 'canvas', icon: FileText, title: 'Canvas\nLiving document editor - grows and evolves with AI collaboration', section: 'left', toolbar: 'main' },
  { id: 'manager-ai-chat', icon: MessageSquare, title: 'Manager AI Chat\nAdvanced AI chat with Manager AI (Aether) coordinating AIM-OS systems', section: 'left', toolbar: 'main' },
  { id: 'document-editor', icon: FileText, title: 'Document Editor\nLUCID editor with LaTeX math, rich text, section management, and AIM-OS integration', section: 'left', toolbar: 'main' },
  { id: 'evolution', icon: GitBranch, title: 'Evolution Explorer\nVisualize connections between Timeline, Chains, and Goals', section: 'left', toolbar: 'main' },
  { id: 'consciousness', icon: Brain, title: 'Consciousness Visualization\nReal-time AI consciousness state via CAS AttentionMetrics', section: 'right', toolbar: 'main' },
  { id: 'app-preview', icon: Globe, title: 'App Preview\nBrowser preview with port info and process management', section: 'right', toolbar: 'main' },
  { id: 'backend-design', icon: Server, title: 'Backend Design\nVisual backend architecture design with template composition', section: 'right', toolbar: 'main' },
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
    saveLayoutForView,
    loadLayoutForView,
    lockLayoutToView,
    unlockLayoutFromView,
    getLayoutForView,
    updateCurrentPanelConfiguration,
  } = usePanelStore()
  
  // Track left panel right edge position for dividers
  const [leftPanelRightEdge, setLeftPanelRightEdge] = useState<number>(48) // Default: left toolbar width (w-8 = 32px) + some padding
  const leftPanelRef = useRef<HTMLDivElement>(null)
  const leftToolbarRef = useRef<HTMLDivElement>(null)
  const leftTopPanelRef = useRef<HTMLDivElement>(null) // Track top panel for divider position
  const rightTopPanelRef = useRef<HTMLDivElement>(null) // Track top panel for divider position
  const [leftDividerPosition, setLeftDividerPosition] = useState<number>(50) // Percentage from top
  const [rightDividerPosition, setRightDividerPosition] = useState<number>(50) // Percentage from top
  const bottomStatusDataRef = useRef<HTMLDivElement>(null)
  const bottomBarRef = useRef<HTMLDivElement>(null)
  const bottomLeftButtonsRef = useRef<HTMLDivElement>(null)
  const bottomRightButtonsRef = useRef<HTMLDivElement>(null)
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
  
  // Panel visibility states with localStorage persistence
  const [leftPanelOpen, setLeftPanelOpen] = useState(() => {
    const saved = localStorage.getItem('dac-ide-left-panel-open')
    return saved !== null ? JSON.parse(saved) : true
  })
  const [rightPanelOpen, setRightPanelOpen] = useState(() => {
    const saved = localStorage.getItem('dac-ide-right-panel-open')
    return saved !== null ? JSON.parse(saved) : true
  })
  const [topPanelOpen, setTopPanelOpen] = useState(true) // Top panel visibility (hides panel + toolbar)
  const [bottomPanelOpen, setBottomPanelOpen] = useState(() => {
    const saved = localStorage.getItem('dac-ide-bottom-panel-open')
    return saved !== null ? JSON.parse(saved) : true
  })
  
  // Panel sizes with localStorage persistence
  const [leftPanelSize, setLeftPanelSize] = useState(() => {
    const saved = localStorage.getItem('dac-ide-left-panel-size')
    return saved !== null ? JSON.parse(saved) : 20
  })
  const [rightPanelSize, setRightPanelSize] = useState(() => {
    const saved = localStorage.getItem('dac-ide-right-panel-size')
    return saved !== null ? JSON.parse(saved) : 30
  })
  const [bottomPanelSize, setBottomPanelSize] = useState(() => {
    const saved = localStorage.getItem('dac-ide-bottom-panel-size')
    return saved !== null ? JSON.parse(saved) : 25
  })
  
  // Save panel visibility to localStorage
  useEffect(() => {
    localStorage.setItem('dac-ide-left-panel-open', JSON.stringify(leftPanelOpen))
  }, [leftPanelOpen])
  
  useEffect(() => {
    localStorage.setItem('dac-ide-right-panel-open', JSON.stringify(rightPanelOpen))
  }, [rightPanelOpen])
  
  useEffect(() => {
    localStorage.setItem('dac-ide-bottom-panel-open', JSON.stringify(bottomPanelOpen))
  }, [bottomPanelOpen])
  
  // Save panel sizes to localStorage
  useEffect(() => {
    localStorage.setItem('dac-ide-left-panel-size', JSON.stringify(leftPanelSize))
  }, [leftPanelSize])
  
  useEffect(() => {
    localStorage.setItem('dac-ide-right-panel-size', JSON.stringify(rightPanelSize))
  }, [rightPanelSize])
  
  useEffect(() => {
    localStorage.setItem('dac-ide-bottom-panel-size', JSON.stringify(bottomPanelSize))
  }, [bottomPanelSize])
  
  // Sync panel configuration to store for ResourceMonitor visualization
  useEffect(() => {
    updateCurrentPanelConfiguration({
      leftTopPanel,
      leftBottomPanel,
      rightTopPanel,
      rightBottomPanel,
      bottomLeftPanel,
      bottomRightPanel,
      leftPanelOpen,
      rightPanelOpen,
      bottomPanelOpen,
    })
  }, [
    leftTopPanel,
    leftBottomPanel,
    rightTopPanel,
    rightBottomPanel,
    bottomLeftPanel,
    bottomRightPanel,
    leftPanelOpen,
    rightPanelOpen,
    bottomPanelOpen,
    updateCurrentPanelConfiguration,
  ])
  
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
  
  // Track left panel divider position (top/bottom split)
  useEffect(() => {
    const updateLeftDividerPosition = () => {
      if (!leftToolbarRef.current || !leftPanelRef.current) return
      
      if (leftTopPanel && leftBottomPanel && leftTopPanelRef.current) {
        // Both panels open - track top panel height
        const toolbarRect = leftToolbarRef.current.getBoundingClientRect()
        const topPanelRect = leftTopPanelRef.current.getBoundingClientRect()
        const relativeTop = topPanelRect.top - toolbarRect.top
        const relativeBottom = topPanelRect.bottom - toolbarRect.top
        const topPanelHeight = relativeBottom - relativeTop
        const toolbarHeight = toolbarRect.height
        const percentage = (topPanelHeight / toolbarHeight) * 100
        setLeftDividerPosition(Math.max(10, Math.min(90, percentage)))
      } else {
        // Only one panel open - center
        setLeftDividerPosition(50)
      }
    }
    
    updateLeftDividerPosition()
    const resizeObserver = new ResizeObserver(updateLeftDividerPosition)
    if (leftPanelRef.current) {
      resizeObserver.observe(leftPanelRef.current)
    }
    if (leftTopPanelRef.current) {
      resizeObserver.observe(leftTopPanelRef.current)
    }
    
    window.addEventListener('resize', updateLeftDividerPosition)
    return () => {
      resizeObserver.disconnect()
      window.removeEventListener('resize', updateLeftDividerPosition)
    }
  }, [leftTopPanel, leftBottomPanel])
  
  // Track right panel divider position (top/bottom split)
  useEffect(() => {
    const updateRightDividerPosition = () => {
      if (!rightPanelRef.current) return
      
      if (rightTopPanel && rightBottomPanel && rightTopPanelRef.current) {
        // Both panels open - track top panel height
        const panelRect = rightPanelRef.current.getBoundingClientRect()
        const topPanelRect = rightTopPanelRef.current.getBoundingClientRect()
        const relativeTop = topPanelRect.top - panelRect.top
        const relativeBottom = topPanelRect.bottom - panelRect.top
        const topPanelHeight = relativeBottom - relativeTop
        const panelHeight = panelRect.height
        const percentage = (topPanelHeight / panelHeight) * 100
        setRightDividerPosition(Math.max(10, Math.min(90, percentage)))
      } else {
        // Only one panel open - center
        setRightDividerPosition(50)
      }
    }
    
    updateRightDividerPosition()
    const resizeObserver = new ResizeObserver(updateRightDividerPosition)
    if (rightPanelRef.current) {
      resizeObserver.observe(rightPanelRef.current)
    }
    if (rightTopPanelRef.current) {
      resizeObserver.observe(rightTopPanelRef.current)
    }
    
    window.addEventListener('resize', updateRightDividerPosition)
    return () => {
      resizeObserver.disconnect()
      window.removeEventListener('resize', updateRightDividerPosition)
    }
  }, [rightTopPanel, rightBottomPanel])
  
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
    commit?: string
    isGitVersion?: boolean
  }
  const [openFiles, setOpenFiles] = useState<OpenFile[]>([
    { id: '1', path: 'src/components/IDELayout.tsx', name: 'IDELayout.tsx', openedAt: new Date(Date.now() - 300000) },
    { id: '2', path: 'src/panels/CodeEditor.tsx', name: 'CodeEditor.tsx', openedAt: new Date(Date.now() - 180000) },
    { id: '3', path: 'src/components/TopBar.tsx', name: 'TopBar.tsx', openedAt: new Date(Date.now() - 60000) },
  ])
  const [activeFileId, setActiveFileId] = useState<string>('1')
  
  const handleFileOpen = useCallback((file: OpenFile) => {
    setOpenFiles(prev => {
      const exists = prev.find(f => f.id === file.id)
      if (exists) return prev
      return [...prev, file].sort((a, b) => a.openedAt.getTime() - b.openedAt.getTime())
    })
    setActiveFileId(file.id)
  }, [])
  
  const handleFileOpenFromCodeEditor = useCallback((file: { id: string; path: string; name: string; commit?: string; isGitVersion?: boolean }) => {
    setOpenFiles(prev => {
      const exists = prev.find(f => f.id === file.id)
      if (exists) {
        setActiveFileId(file.id)
        return prev
      }
      const newFile: OpenFile = {
        id: file.id,
        path: file.path,
        name: file.name,
        openedAt: new Date(),
        commit: file.commit,
        isGitVersion: file.isGitVersion
      }
      setActiveFileId(file.id)
      return [...prev, newFile].sort((a, b) => a.openedAt.getTime() - b.openedAt.getTime())
    })
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
  
  // AIM-OS state (not panel-related, keep as local state)
  const [cmcStats, setCmcStats] = useState<any>(null)
  const [casMetrics, setCasMetrics] = useState<any>(null)
  
  // Language selector state
  const [selectedLanguage, setSelectedLanguage] = useState<string>('typescript')
  
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

  // Helper function to restore panel state from layout
  const restorePanelState = useCallback((panelState: {
    panelVisibility?: { leftPanelOpen: boolean; rightPanelOpen: boolean; bottomPanelOpen: boolean }
    panelSizes?: { leftPanelSize: number; rightPanelSize: number; bottomPanelSize: number }
    panelConfiguration?: {
      leftTopPanel: string | null
      leftBottomPanel: string | null
      rightTopPanel: string | null
      rightBottomPanel: string | null
      bottomLeftPanel: string | null
      bottomRightPanel: string | null
    }
  }) => {
    if (panelState.panelVisibility) {
      setLeftPanelOpen(panelState.panelVisibility.leftPanelOpen)
      setRightPanelOpen(panelState.panelVisibility.rightPanelOpen)
      setBottomPanelOpen(panelState.panelVisibility.bottomPanelOpen)
    }
    if (panelState.panelSizes) {
      setLeftPanelSize(panelState.panelSizes.leftPanelSize)
      setRightPanelSize(panelState.panelSizes.rightPanelSize)
      setBottomPanelSize(panelState.panelSizes.bottomPanelSize)
    }
    if (panelState.panelConfiguration) {
      setLeftTopPanel(panelState.panelConfiguration.leftTopPanel as LeftPanelType)
      setLeftBottomPanel(panelState.panelConfiguration.leftBottomPanel as LeftPanelType)
      setRightTopPanel(panelState.panelConfiguration.rightTopPanel as RightPanelType)
      setRightBottomPanel(panelState.panelConfiguration.rightBottomPanel as RightPanelType)
      setBottomLeftPanel(panelState.panelConfiguration.bottomLeftPanel as BottomPanelType)
      setBottomRightPanel(panelState.panelConfiguration.bottomRightPanel as BottomPanelType)
    }
  }, [])

  const handleMainViewChange = useCallback((view: 'code' | 'evolution' | 'consciousness' | 'orchestration' | 'app-preview' | 'document-editor' | 'file-preview' | 'canvas' | 'manager-ai-chat') => {
    // Toggle: if clicking the same view, close it (set to 'code' as default)
    if (mainView === view) {
      setMainView('code')
      // Load layout for code view if locked
      const layoutData = loadLayoutForView('code')
      if (layoutData?.panelState) {
        restorePanelState(layoutData.panelState)
      }
    } else {
      setMainView(view)
      // Load layout for the new view if locked
      const layoutData = loadLayoutForView(view)
      if (layoutData?.panelState) {
        restorePanelState(layoutData.panelState)
      }
    }
  }, [mainView, setMainView, loadLayoutForView, restorePanelState])
  
  // Save current layout state
  const handleSaveLayout = useCallback((viewName?: string) => {
    saveLayoutForView(mainView, viewName, {
      panelVisibility: {
        leftPanelOpen,
        rightPanelOpen,
        bottomPanelOpen,
      },
      panelSizes: {
        leftPanelSize,
        rightPanelSize,
        bottomPanelSize,
      },
      panelConfiguration: {
        leftTopPanel: leftTopPanel || null,
        leftBottomPanel: leftBottomPanel || null,
        rightTopPanel: rightTopPanel || null,
        rightBottomPanel: rightBottomPanel || null,
        bottomLeftPanel: bottomLeftPanel || null,
        bottomRightPanel: bottomRightPanel || null,
      },
    })
  }, [mainView, leftPanelOpen, rightPanelOpen, bottomPanelOpen, leftPanelSize, rightPanelSize, bottomPanelSize, leftTopPanel, leftBottomPanel, rightTopPanel, rightBottomPanel, bottomLeftPanel, bottomRightPanel, saveLayoutForView])
  
  // Lock current layout to view
  const handleLockLayout = useCallback(() => {
    const layout = getLayoutForView(mainView)
    if (layout) {
      lockLayoutToView(mainView, layout.id)
    } else {
      // Save layout first, then lock it
      handleSaveLayout()
      const newLayout = getLayoutForView(mainView)
      if (newLayout) {
        lockLayoutToView(mainView, newLayout.id)
      }
    }
  }, [mainView, getLayoutForView, lockLayoutToView, handleSaveLayout])
  
  // Unlock layout from view
  const handleUnlockLayout = useCallback(() => {
    unlockLayoutFromView(mainView)
  }, [mainView, unlockLayoutFromView])
  
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
        onMainViewChange={handleMainViewChange}
        openFiles={openFiles}
        activeFileId={activeFileId}
        onFileSelect={setActiveFileId}
        onFileClose={handleFileClose}
        leftPanelRightEdge={leftPanelRightEdge}
        rightPanelLeftEdge={rightPanelLeftEdge}
        rightPanelOpen={rightPanelOpen}
        onSaveLayout={handleSaveLayout}
        onRestoreLayout={restorePanelState}
        leftPanelOpen={leftPanelOpen}
        rightPanelOpen={rightPanelOpen}
        bottomPanelOpen={bottomPanelOpen}
        onLeftPanelToggle={handleLeftPanelToggle}
        onRightPanelToggle={handleRightPanelToggle}
        onBottomPanelToggle={handleBottomDrawerToggle}
        onAccountClick={() => console.log('Account clicked')}
        onSignOut={() => console.log('Sign out clicked')}
        userName="User"
      />
      
      {/* Main Layout */}
      <PanelGroup direction="vertical" className="flex-1">
        <Panel defaultSize={bottomPanelOpen ? 75 : 100} minSize={50}>
          <div className="flex-1 flex overflow-hidden h-full">
            {/* Left Vertical Toolbar with Top/Bottom Sections - Always Visible */}
            <div ref={leftToolbarRef} className="w-8 bg-gray-950 border-r border-gray-800 flex flex-col h-full relative">
              {/* Top Section - Above divider */}
              <div 
                className={`flex flex-col items-center py-2 gap-1 ${
                  dragOverSection === 'top' && dragOverToolbar === 'left' ? 'bg-gray-800/30' : ''
                }`}
                style={{
                  flex: `0 0 ${leftDividerPosition}%`
                }}
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
              </div>
              
              {/* Divider - Tracks top/bottom panel split */}
              <div 
                className="w-full h-px bg-gray-800 transition-all duration-200 flex-shrink-0"
              />
              
              {/* Bottom Section - Below divider */}
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
              </div>
              
            <PanelGroup direction="horizontal" onLayout={(sizes) => {
              // Track left panel size (first panel in horizontal group)
              if (leftPanelOpen && sizes.length > 0) {
                setLeftPanelSize(sizes[0])
              }
              // Track right panel size (last panel in horizontal group)
              if (rightPanelOpen && sizes.length > 1) {
                setRightPanelSize(sizes[sizes.length - 1])
              }
            }}>
              {/* Left Drawer - Supports Top/Bottom Split */}
              {leftPanelOpen && (
                <Panel 
                  defaultSize={leftPanelSize} 
                  minSize={15} 
                  maxSize={35} 
                  className="bg-gray-950 border-r border-gray-800"
                >
                  <div ref={leftPanelRef} className="h-full flex flex-col">
                    {leftTopPanel && leftBottomPanel ? (
                      // Both panels open - split top/bottom
                      <PanelGroup direction="vertical" className="flex-1">
                        <Panel defaultSize={50} minSize={20}>
                          <div ref={leftTopPanelRef} className="h-full overflow-auto">
                            <ErrorBoundary panelName="Left Top Panel">
                              {leftTopPanel === 'explorer' && (
                                <LazyPanelWrapper panelId="explorer" panelName="File Explorer">
                                  <LazyFileTree />
                                </LazyPanelWrapper>
                              )}
                              {leftTopPanel === 'memory' && (
                                <LazyPanelWrapper panelId="memory" panelName="Memory Browser">
                                  <LazyMemoryBrowser />
                                </LazyPanelWrapper>
                              )}
                              {leftTopPanel === 'status' && (
                                <LazyPanelWrapper panelId="status" panelName="System Status">
                                  <LazySystemStatus metrics={casMetrics} />
                                </LazyPanelWrapper>
                              )}
                              {leftTopPanel === 'app-preview-controls' && (
                                <LazyPanelWrapper panelId="app-preview-controls" panelName="App Preview Controls">
                                  <LazyAppPreviewControls />
                                </LazyPanelWrapper>
                              )}
                              {leftTopPanel === 'debug-console' && (
                                <LazyPanelWrapper panelId="debug-console" panelName="Debug Console">
                                  <LazyDebugConsolePanel />
                                </LazyPanelWrapper>
                              )}
                            </ErrorBoundary>
                          </div>
                        </Panel>
                        <PanelResizeHandle className="group h-1 cursor-row-resize relative bg-transparent">
                          <div className="absolute inset-0 flex items-center justify-center">
                            <div 
                              className="w-full bg-gray-800 transition-all duration-200 group-hover:bg-gray-700 resize-handle-line resize-handle-horizontal"
                            />
                          </div>
                        </PanelResizeHandle>
                        <Panel defaultSize={50} minSize={20}>
                          <div className="h-full overflow-auto">
                            <ErrorBoundary panelName="Left Bottom Panel">
                              {leftBottomPanel === 'explorer' && (
                                <LazyPanelWrapper panelId="explorer" panelName="File Explorer">
                                  <LazyFileTree />
                                </LazyPanelWrapper>
                              )}
                              {leftBottomPanel === 'memory' && (
                                <LazyPanelWrapper panelId="memory" panelName="Memory Browser">
                                  <LazyMemoryBrowser />
                                </LazyPanelWrapper>
                              )}
                              {leftBottomPanel === 'status' && (
                                <LazyPanelWrapper panelId="status" panelName="System Status">
                                  <LazySystemStatus metrics={casMetrics} />
                                </LazyPanelWrapper>
                              )}
                              {leftBottomPanel === 'resource-monitor' && (
                                <LazyPanelWrapper panelId="resource-monitor" panelName="Resource Monitor">
                                  <LazyResourceMonitor />
                                </LazyPanelWrapper>
                              )}
                              {leftBottomPanel === 'app-preview-controls' && (
                                <LazyPanelWrapper panelId="app-preview-controls" panelName="App Preview Controls">
                                  <LazyAppPreviewControls />
                                </LazyPanelWrapper>
                              )}
                              {leftBottomPanel === 'debug-console' && (
                                <LazyPanelWrapper panelId="debug-console" panelName="Debug Console">
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
                    <LazyPanelWrapper panelId="explorer" panelName="File Explorer">
                      <LazyFileTree />
                    </LazyPanelWrapper>
                  )}
                          {(leftTopPanel || leftBottomPanel) === 'memory' && (
                    <LazyPanelWrapper panelId="memory" panelName="Memory Browser">
                      <LazyMemoryBrowser />
                    </LazyPanelWrapper>
                  )}
                          {(leftTopPanel || leftBottomPanel) === 'status' && (
                    <LazyPanelWrapper panelId="status" panelName="System Status">
                      <LazySystemStatus metrics={casMetrics} />
                    </LazyPanelWrapper>
                  )}
                          {(leftTopPanel || leftBottomPanel) === 'app-preview-controls' && (
                    <LazyPanelWrapper panelId="app-preview-controls" panelName="App Preview Controls">
                      <LazyAppPreviewControls />
                    </LazyPanelWrapper>
                  )}
                          {(leftTopPanel || leftBottomPanel) === 'debug-console' && (
                    <LazyPanelWrapper panelId="debug-console" panelName="Debug Console">
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
                <PanelResizeHandle className="group w-1 cursor-col-resize relative bg-transparent">
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div 
                      className="h-full bg-gray-800 transition-all duration-200 group-hover:bg-gray-700 resize-handle-line resize-handle-vertical"
                    />
                  </div>
                </PanelResizeHandle>
              )}
          
          {/* Main Content Area */}
          <Panel defaultSize={50} minSize={30} data-main-content-area>
            <PanelGroup direction="vertical" className="h-full" onLayout={(sizes) => {
              // Track bottom panel size (last panel in vertical group when bottom panel is open)
              if (bottomPanelOpen && sizes.length > 1) {
                setBottomPanelSize(sizes[sizes.length - 1])
              } else if (!bottomPanelOpen && sizes.length > 0) {
                // When bottom panel is closed, the main content takes full size
                // Don't update bottomPanelSize in this case
              }
            }}>
                {/* Top Panel - Only shown if topPanelOpen */}
                {topPanelOpen && (
                  <Panel defaultSize={bottomPanelOpen ? 75 : 100} minSize={50}>
                    <div className="h-full flex">
                      {/* Main Content Area */}
                      <div className="flex-1 bg-gray-950 flex flex-col" style={{ minHeight: 0 }}>
              <ErrorBoundary panelName="Main View">
                {mainView === 'code' && (
                  <LazyPanelWrapper panelId="code" panelName="Code Editor">
                    <LazyCodeEditor 
                      onOpenFileInTabs={handleFileOpenFromCodeEditor}
                      openFiles={openFiles}
                      activeFileId={activeFileId}
                      onFileSelect={setActiveFileId}
                      selectedLanguage={selectedLanguage}
                      onLanguageChange={setSelectedLanguage}
                    />
                  </LazyPanelWrapper>
                )}
                {mainView === 'evolution' && (
                  <LazyPanelWrapper panelId="evolution" panelName="Evolution Explorer">
                    <LazyEvolutionExplorer />
                  </LazyPanelWrapper>
                )}
                {mainView === 'consciousness' && (
                  <LazyPanelWrapper panelId="consciousness" panelName="Consciousness Visualization">
                    <LazyConsciousnessVisualization />
                  </LazyPanelWrapper>
                )}
                {mainView === 'orchestration' && (
                  <LazyPanelWrapper panelId="orchestration" panelName="AIM-OS Orchestration">
                    <LazyAIMOSOrchestration />
                  </LazyPanelWrapper>
                )}
                          {mainView === 'app-preview' && (
                            <LazyPanelWrapper panelId="app-preview" panelName="App Preview">
                              <LazyAppPreview onClose={() => handleMainViewChange('code')} />
                  </LazyPanelWrapper>
                )}
                {mainView === 'document-editor' && (
                  <LazyPanelWrapper panelId="document-editor" panelName="Document Editor">
                    <LazyDocumentEditor />
                  </LazyPanelWrapper>
                )}
                {mainView === 'file-preview' && (
                  <LazyPanelWrapper panelId="file-preview" panelName="File Preview">
                    <LazyFilePreviewView />
                  </LazyPanelWrapper>
                )}
                {mainView === 'canvas' && (
                  <LazyPanelWrapper panelId="canvas" panelName="Canvas View">
                    <LazyCanvasView />
                  </LazyPanelWrapper>
                )}
                {mainView === 'manager-ai-chat' && (
                  <LazyPanelWrapper panelId="manager-ai-chat" panelName="Manager AI Chat">
                    <LazyManagerAIChat />
                  </LazyPanelWrapper>
                )}
                {mainView === 'backend-design' && (
                  <LazyPanelWrapper panelId="backend-design" panelName="Backend Design">
                    <LazyBackendDesign />
                  </LazyPanelWrapper>
                )}
              </ErrorBoundary>
                      </div>
            </div>
          </Panel>
                )}
                    
                    {/* PanelResizeHandle between top and bottom panels */}
                    {topPanelOpen && bottomPanelOpen && (
                      <PanelResizeHandle className="group h-1 cursor-row-resize relative bg-transparent">
                        <div className="absolute inset-0 flex items-center justify-center">
                          <div 
                            className="w-full bg-gray-800 transition-all duration-200 group-hover:bg-gray-700 resize-handle-line resize-handle-horizontal"
                          />
                        </div>
                      </PanelResizeHandle>
                    )}
          
                    {/* Bottom Panel - Inset Between Left and Right Panels */}
                    {bottomPanelOpen && !topPanelOpen && (
                      <PanelResizeHandle className="group h-1 cursor-row-resize relative bg-transparent">
                        <div className="absolute inset-0 flex items-center justify-center">
                          <div 
                            className="w-full bg-gray-800 transition-all duration-200 group-hover:bg-gray-700 resize-handle-line resize-handle-horizontal"
                          />
                        </div>
                      </PanelResizeHandle>
                    )}
                    
                    {bottomPanelOpen && (
                      <Panel 
                        defaultSize={bottomPanelSize} 
                        minSize={10} 
                        maxSize={50} 
                        className="bg-gray-950 border-t border-gray-800"
                      >
                        <div className="h-full flex">
                          {/* Bottom Panel Content - Supports Left/Right Split */}
                          <div className="flex-1 overflow-auto">
                            {bottomLeftPanel && bottomRightPanel ? (
                              // Both panels open - split left/right
                              <PanelGroup direction="horizontal" className="h-full">
                                <Panel defaultSize={50} minSize={20}>
                                  <div className="h-full overflow-auto">
                                    <ErrorBoundary panelName="Bottom Left Panel">
                                      {bottomLeftPanel === 'terminal' && (
                    <LazyPanelWrapper panelId="terminal" panelName="Terminal">
                                          <LazyTerminalPanel />
                    </LazyPanelWrapper>
                  )}
                                      {bottomLeftPanel === 'problems' && (
                                        <LazyPanelWrapper panelId="problems" panelName="Problems">
                                          <LazyProblemsPanel />
                                        </LazyPanelWrapper>
                                      )}
                                      {bottomLeftPanel === 'timeline' && (
                    <LazyPanelWrapper panelId="timeline" panelName="Timeline View">
                      <LazyTimelineView />
                    </LazyPanelWrapper>
                  )}
                                      {bottomLeftPanel === 'debug-console' && (
                    <LazyPanelWrapper panelId="debug-console" panelName="Debug Console">
                                          <LazyDebugConsolePanel onStatusChange={setBottomLeftPanelStatus} />
                    </LazyPanelWrapper>
                  )}
                                      {bottomLeftPanel === 'log-sentinels-anomalies' && (
                                        <LazyPanelWrapper panelId="log-sentinels-anomalies" panelName="Log Sentinels Anomalies">
                                          <LazyLogSentinelsAnomalies />
                                        </LazyPanelWrapper>
                                      )}
                                    </ErrorBoundary>
                    </div>
                                </Panel>
                                <Panel defaultSize={50} minSize={20}>
                                  <div ref={bottomRightPanelRef} className="h-full overflow-auto">
                                    <ErrorBoundary panelName="Bottom Right Panel">
                                      {bottomRightPanel === 'terminal' && (
                                        <LazyPanelWrapper panelId="terminal" panelName="Terminal">
                                          <LazyTerminalPanel />
                                        </LazyPanelWrapper>
                                      )}
                                      {bottomRightPanel === 'problems' && (
                                        <LazyPanelWrapper panelId="problems" panelName="Problems">
                                          <LazyProblemsPanel />
                                        </LazyPanelWrapper>
                                      )}
                                      {bottomRightPanel === 'timeline' && (
                                        <LazyPanelWrapper panelId="timeline" panelName="Timeline View">
                                          <LazyTimelineView />
                                        </LazyPanelWrapper>
                                      )}
                                      {bottomRightPanel === 'debug-console' && (
                                        <LazyPanelWrapper panelId="debug-console" panelName="Debug Console">
                                          <LazyDebugConsolePanel onStatusChange={setBottomRightPanelStatus} />
                                        </LazyPanelWrapper>
                                      )}
                                      {bottomRightPanel === 'log-sentinels-summaries' && (
                                        <LazyPanelWrapper panelId="log-sentinels-summaries" panelName="Log Sentinels Summaries">
                                          <LazyLogSentinelsSummaries />
                                        </LazyPanelWrapper>
                                      )}
                                      {bottomRightPanel === 'tool-quality' && (
                                        <LazyPanelWrapper panelId="tool-quality" panelName="Tool Quality Dashboard">
                                          <LazyToolQualityDashboard />
                                        </LazyPanelWrapper>
                                      )}
                                      {bottomRightPanel === 'log-analysis' && (
                                        <LazyPanelWrapper panelId="log-analysis" panelName="Log Analysis Dashboard">
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
                                  <LazyPanelWrapper panelId="terminal" panelName="Terminal">
                                    <LazyTerminalPanel />
                                  </LazyPanelWrapper>
                                )}
                                {(bottomLeftPanel || bottomRightPanel || bottomPanel) === 'problems' && (
                                  <LazyPanelWrapper panelId="problems" panelName="Problems">
                                    <LazyProblemsPanel />
                                  </LazyPanelWrapper>
                                )}
                                {(bottomLeftPanel || bottomRightPanel || bottomPanel) === 'timeline' && (
                                  <LazyPanelWrapper panelId="timeline" panelName="Timeline View">
                                    <LazyTimelineView />
                                  </LazyPanelWrapper>
                                )}
                                {(bottomLeftPanel || bottomRightPanel || bottomPanel) === 'debug-console' && (
                                  <LazyPanelWrapper panelId="debug-console" panelName="Debug Console">
                                    <LazyDebugConsolePanel onStatusChange={(status) => {
                                      if (bottomLeftPanel === 'debug-console') setBottomLeftPanelStatus(status)
                                      if (bottomRightPanel === 'debug-console') setBottomRightPanelStatus(status)
                                    }} />
                                  </LazyPanelWrapper>
                                )}
                                {(bottomLeftPanel || bottomRightPanel || bottomPanel) === 'log-sentinels-anomalies' && (
                                  <LazyPanelWrapper panelId="log-sentinels-anomalies" panelName="Log Sentinels Anomalies">
                                    <LazyLogSentinelsAnomalies />
                                  </LazyPanelWrapper>
                                )}
                                {(bottomLeftPanel || bottomRightPanel || bottomPanel) === 'log-sentinels-summaries' && (
                                  <LazyPanelWrapper panelId="log-sentinels-summaries" panelName="Log Sentinels Summaries">
                                    <LazyLogSentinelsSummaries />
                                  </LazyPanelWrapper>
                                )}
                                {(bottomLeftPanel || bottomRightPanel || bottomPanel) === 'tool-quality' && (
                                  <LazyPanelWrapper panelId="tool-quality" panelName="Tool Quality Dashboard">
                                    <LazyToolQualityDashboard />
                                  </LazyPanelWrapper>
                                )}
                                {(bottomLeftPanel || bottomRightPanel || bottomPanel) === 'log-analysis' && (
                                  <LazyPanelWrapper panelId="log-analysis" panelName="Log Analysis Dashboard">
                                    <LazyLogAnalysisDashboard />
                                  </LazyPanelWrapper>
                                )}
                                {(bottomLeftPanel || bottomRightPanel || bottomPanel) === 'context-ledger' && (
                                  <LazyPanelWrapper panelId="context-ledger" panelName="Context Ledger">
                                    <LazyContextLedger
                                      assembledContext={null}
                                      contextInfo={{}}
                                      channelId=""
                                      budget={12000}
                                    />
                                  </LazyPanelWrapper>
                                )}
                                {(bottomLeftPanel || bottomRightPanel || bottomPanel) === 'heatmap' && (
                                  <LazyPanelWrapper panelId="heatmap" panelName="Chat Heatmap">
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
                  <PanelResizeHandle className="group w-1 cursor-col-resize relative bg-transparent">
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div 
                        className="h-full bg-gray-800 transition-all duration-200 group-hover:bg-gray-700 resize-handle-line resize-handle-vertical"
                      />
                    </div>
                  </PanelResizeHandle>
                )}
                
                {rightPanelOpen && (
                  <Panel defaultSize={rightPanelSize} minSize={20} maxSize={45} className="bg-gray-950 border-l border-gray-800">
                    <div ref={rightPanelRef} className="h-full flex flex-col">
                      {rightTopPanel && rightBottomPanel ? (
                        // Both panels open - split top/bottom
                        <PanelGroup direction="vertical" className="flex-1">
                          <Panel defaultSize={50} minSize={20}>
                            <div ref={rightTopPanelRef} className="h-full overflow-auto">
                              <ErrorBoundary panelName="Right Top Panel">
                                {rightTopPanel === 'context-web' && (
                <LazyPanelWrapper panelId="context-web" panelName="Context Web">
                                    <LazyContextWeb />
                </LazyPanelWrapper>
              )}
                                {rightTopPanel === 'timeline' && (
                <LazyPanelWrapper panelId="timeline" panelName="Timeline View">
                                    <LazyTimelineView />
                </LazyPanelWrapper>
              )}
                                {rightTopPanel === 'outline' && (
                                  <LazyPanelWrapper panelId="outline" panelName="Code Outline">
                                    <LazyOutlinePanel />
                                  </LazyPanelWrapper>
                                )}
                                {rightTopPanel === 'ai-chat' && (
                                  <LazyPanelWrapper panelId="ai-chat" panelName="AI Chat">
                                    <LazyAIChatManagement />
                                  </LazyPanelWrapper>
                                )}
                                {rightTopPanel === 'router' && (
                                  <LazyPanelWrapper panelId="router" panelName="Router Panel">
                                    <LazyRouterPanel />
                                  </LazyPanelWrapper>
                                )}
                                {rightTopPanel === 'browser-automation' && (
                                  <LazyPanelWrapper panelId="browser-automation" panelName="Browser Automation">
                                    <LazyBrowserAutomationPanel />
                                  </LazyPanelWrapper>
                                )}
                                {rightTopPanel === 'lucid-chat' && (
                                  <LazyPanelWrapper panelId="lucid-chat" panelName="Lucid Chat">
                                    <LucidChatPanel />
                                  </LazyPanelWrapper>
                                )}
                                {rightTopPanel === 'debug-console' && (
                                  <LazyPanelWrapper panelId="debug-console" panelName="Debug Console">
                                    <LazyDebugConsolePanel />
                                  </LazyPanelWrapper>
                                )}
                                {rightTopPanel === 'system-index-browser' && (
                                  <LazyPanelWrapper panelId="system-index-browser" panelName="System Index Browser">
                                    <LazySystemIndexBrowserPanel />
                                  </LazyPanelWrapper>
                                )}
                                {rightTopPanel === 'system-map' && (
                                  <LazyPanelWrapper panelId="system-map" panelName="System Map">
                                    <LazySystemMapPanel />
                                  </LazyPanelWrapper>
                                )}
                              </ErrorBoundary>
                            </div>
                          </Panel>
                          <PanelResizeHandle className="group h-1 cursor-row-resize relative bg-transparent">
                        <div className="absolute inset-0 flex items-center justify-center">
                          <div 
                            className="w-full bg-gray-800 transition-all duration-200 group-hover:bg-gray-700 resize-handle-line resize-handle-horizontal"
                          />
                        </div>
                      </PanelResizeHandle>
                          <Panel defaultSize={50} minSize={20}>
                            <div className="h-full overflow-auto">
                              <ErrorBoundary panelName="Right Bottom Panel">
                                {rightBottomPanel === 'context-web' && (
                                  <LazyPanelWrapper panelId="context-web" panelName="Context Web">
                                    <LazyContextWeb />
                                  </LazyPanelWrapper>
                                )}
                                {rightBottomPanel === 'timeline' && (
                 <LazyPanelWrapper panelId="timeline" panelName="Timeline View">
                   <LazyTimelineView />
                 </LazyPanelWrapper>
               )}
                                {rightBottomPanel === 'outline' && (
                                  <LazyPanelWrapper panelId="outline" panelName="Code Outline">
                                    <LazyOutlinePanel />
                                  </LazyPanelWrapper>
                                )}
                                {rightBottomPanel === 'ai-chat' && (
                                  <LazyPanelWrapper panelId="ai-chat" panelName="AI Chat">
                                    <LazyAIChatManagement />
                                  </LazyPanelWrapper>
                                )}
                                {rightBottomPanel === 'router' && (
                                  <LazyPanelWrapper panelId="router" panelName="Router Panel">
                                    <LazyRouterPanel />
                                  </LazyPanelWrapper>
                                )}
                                {rightBottomPanel === 'browser-automation' && (
                                  <LazyPanelWrapper panelId="browser-automation" panelName="Browser Automation">
                                    <LazyBrowserAutomationPanel />
                                  </LazyPanelWrapper>
                                )}
                                {rightBottomPanel === 'lucid-chat' && (
                                  <LazyPanelWrapper panelId="lucid-chat" panelName="Lucid Chat">
                                    <LucidChatPanel />
                                  </LazyPanelWrapper>
                                )}
                                {rightBottomPanel === 'debug-console' && (
                                  <LazyPanelWrapper panelId="debug-console" panelName="Debug Console">
                                    <LazyDebugConsolePanel />
                                  </LazyPanelWrapper>
                                )}
                                {rightBottomPanel === 'system-index-browser' && (
                                  <LazyPanelWrapper panelId="system-index-browser" panelName="System Index Browser">
                                    <LazySystemIndexBrowserPanel />
                                  </LazyPanelWrapper>
                                )}
                                {rightBottomPanel === 'system-map' && (
                                  <LazyPanelWrapper panelId="system-map" panelName="System Map">
                                    <LazySystemMapPanel />
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
                    <LazyPanelWrapper panelId="context-web" panelName="Context Web">
                      <LazyContextWeb />
                    </LazyPanelWrapper>
                  )}
                            {(rightTopPanel || rightBottomPanel) === 'timeline' && (
                    <LazyPanelWrapper panelId="timeline" panelName="Timeline View">
                      <LazyTimelineView />
                    </LazyPanelWrapper>
                  )}
                            {(rightTopPanel || rightBottomPanel) === 'outline' && (
                    <LazyPanelWrapper panelId="outline" panelName="Code Outline">
                      <LazyOutlinePanel />
                    </LazyPanelWrapper>
                  )}
                            {(rightTopPanel || rightBottomPanel) === 'ai-chat' && (
                              <LazyPanelWrapper panelId="ai-chat" panelName="AI Chat">
                                <LazyAIChatManagement />
                              </LazyPanelWrapper>
                            )}
                            {(rightTopPanel || rightBottomPanel) === 'router' && (
                              <LazyPanelWrapper panelId="router" panelName="Router Panel">
                                <LazyRouterPanel />
                              </LazyPanelWrapper>
                            )}
                            {(rightTopPanel || rightBottomPanel) === 'debug-console' && (
                              <LazyPanelWrapper panelId="debug-console" panelName="Debug Console">
                                <LazyDebugConsolePanel />
                              </LazyPanelWrapper>
                            )}
                            {(rightTopPanel || rightBottomPanel) === 'system-index-browser' && (
                              <LazyPanelWrapper panelId="system-index-browser" panelName="System Index Browser">
                                <LazySystemIndexBrowserPanel />
                              </LazyPanelWrapper>
                            )}
                            {(rightTopPanel || rightBottomPanel) === 'system-map' && (
                              <LazyPanelWrapper panelId="system-map" panelName="System Map">
                                <LazySystemMapPanel />
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
                <div className="w-8 bg-gray-950 border-r border-gray-800 flex flex-col h-full relative">
                  {/* Top Section - Above divider */}
                  <div 
                    className={`flex flex-col items-center py-2 gap-1 ${
                      dragOverSection === 'top' && dragOverToolbar === 'right' ? 'bg-gray-800/30' : ''
                    }`}
                    style={{
                      flex: `0 0 ${rightDividerPosition}%`
                    }}
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
                  </div>
                  
                  {/* Divider - Tracks top/bottom panel split */}
                  <div 
                    className="w-full h-px bg-gray-800 transition-all duration-200 flex-shrink-0"
                  />
                  
                  {/* Bottom Section - Below divider */}
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
          </div>
              </PanelGroup>
        </div>
        </Panel>
      </PanelGroup>
      
      {/* Bottom Status Bar - Full Width */}
      <div ref={bottomBarRef} className="h-8 bg-gray-950 border-t border-gray-800 flex items-center relative">
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
          className="absolute top-0 bottom-0 w-px bg-gray-800 transition-all duration-200 z-30"
          style={{
            left: `${Math.max(leftPanelRightEdge, bottomStatusDataRightEdge)}px`
          }}
        />
        
        {/* Divider - Aligns with right panel left edge */}
        {rightPanelOpen && (
          <div 
            className="absolute top-0 bottom-0 w-px bg-gray-800 transition-all duration-200 z-30"
            style={{
              left: `${Math.max(leftPanelRightEdge, Math.min(rightPanelLeftEdge, window.innerWidth - 50))}px`
            }}
          />
        )}
        
        {/* Bottom Panel Buttons - Between toggle and right label */}
        <div className="absolute top-0 bottom-0 left-0 right-0 flex items-center justify-center z-20"
          style={{
            left: `${Math.max(leftPanelRightEdge, bottomStatusDataRightEdge) + 32}px`,
            right: rightPanelOpen ? `${window.innerWidth - rightPanelLeftEdge + 60}px` : '60px' // Space for right divider + DAC-V2 label or just label
          }}
        >
          {/* Left Section Buttons */}
          <div 
            ref={bottomLeftButtonsRef}
            className="flex items-center gap-1 px-2"
          >
            {bottomToolbarButtons
              .filter(btn => btn.section === 'left')
              .map(btn => {
                const Icon = btn.icon
                const isActive = bottomLeftPanel === btn.id || (bottomPanel === btn.id && !bottomRightPanel)
                return (
                  <button
                    key={btn.id}
                    onClick={() => handleBottomLeftPanelChange(btn.id)}
                    className={`w-6 h-6 rounded flex items-center justify-center transition-colors ${
                      isActive
                        ? 'bg-gray-800 text-gray-100' 
                        : 'text-gray-400 hover:bg-gray-900 hover:text-gray-300'
                    }`}
                    title={btn.title.split('\n')[0]}
                  >
                    <Icon className="w-3 h-3" />
                  </button>
                )
              })}
          </div>
          
          {/* Horizontal Separator with Opposing Arrows */}
          <div className="flex items-center justify-center mx-2">
            <div className="relative w-8 h-0.5 flex items-center justify-center">
              <div className="absolute w-full h-0.5 bg-gray-700 border-t border-b border-gray-800" />
              <ChevronLeft className="w-2 h-2 text-gray-600 absolute -left-1" />
              <ChevronRight className="w-2 h-2 text-gray-600 absolute -right-1" />
            </div>
          </div>
          
          {/* Right Section Buttons */}
          <div 
            ref={bottomRightButtonsRef}
            className="flex items-center gap-1 px-2"
          >
            {bottomToolbarButtons
              .filter(btn => btn.section === 'right')
              .map(btn => {
                const Icon = btn.icon
                const isActive = bottomRightPanel === btn.id || (bottomPanel === btn.id && !bottomLeftPanel)
                return (
                  <button
                    key={btn.id}
                    onClick={() => handleBottomRightPanelChange(btn.id)}
                    className={`w-6 h-6 rounded flex items-center justify-center transition-colors ${
                      isActive
                        ? 'bg-gray-800 text-gray-100' 
                        : 'text-gray-400 hover:bg-gray-900 hover:text-gray-300'
                    }`}
                    title={btn.title.split('\n')[0]}
                  >
                    <Icon className="w-3 h-3" />
                  </button>
                )
              })}
          </div>
        </div>
        
        <div className="flex-1" />
        
        {/* Status Indicators - Bottom Right */}
        <div className="flex items-center gap-3 text-xs text-gray-400 mr-3">
          {/* CMC Status */}
          {cmcStats && (
            <div className="flex items-center gap-1.5">
              <Database className="w-3 h-3" />
              <span>CMC: {cmcStats?.total_atoms || 0}</span>
            </div>
          )}
          
          {/* CAS Status */}
          {casMetrics && (
            <div className="flex items-center gap-1.5">
              <Brain className="w-3 h-3" />
              <span>CAS: {casMetrics?.health || 'unknown'}</span>
            </div>
          )}
          
          {/* Health Indicator */}
          <div className="flex items-center gap-1.5">
            <Activity className="w-3 h-3" />
            <span>{casMetrics?.health === 'good' ? '🟢' : '🟡'}</span>
          </div>
          
          {/* Port */}
          <div className="text-gray-500 font-medium">
            Port: 3002
          </div>
        </div>
        
        {/* DAC-V2 Label */}
        <div className="text-xs text-gray-400 font-medium mr-3">
          DAC-V2
        </div>
      </div>
    </div>
  )
}
