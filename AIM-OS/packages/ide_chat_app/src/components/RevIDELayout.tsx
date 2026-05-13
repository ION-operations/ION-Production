/**
 * Rev's IDE Layout Prototype - Core Layout Component
 * Research-First, User-Centered, Comprehensive Integration Approach
 * 
 * Phase 1.1: Foundation - Core Layout Structure
 * 
 * Features:
 * - Three-zone layout (left drawer, main content, right drawer)
 * - Bottom drawer support
 * - Panel visibility toggle
 * - Resizable panels using react-resizable-panels
 * - Panel state management (React Context)
 * - Keyboard shortcuts support
 * - Accessibility-first design
 */

import React, { useState, useEffect, useCallback } from 'react'
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels'
import { useEditorStore } from '../store/editorStore'
import { FileTree } from './FileTree'
import { FileExplorerPanel } from './panels/FileExplorerPanel'
import { LucidMonacoEditor } from './LucidMonacoEditor'
import { EditorTabs } from './EditorTabs'
import { CommandPalette } from './CommandPalette'
import { OutlinePanel } from './panels/OutlinePanel'
import { SettingsPanel } from './panels/SettingsPanel'
import { EnhancedTerminalPanel } from './panels/EnhancedTerminalPanel'
import { ComponentLibraryPanel } from './panels/ComponentLibraryPanel'
import { AIMemoryPanel } from './panels/AIMemoryPanel'
import { GitPanel } from './panels/GitPanel'
import { TemplatesPanel } from './panels/TemplatesPanel'
import { ToolQualityDashboardPanel } from './panels/ToolQualityDashboardPanel'
import { PropertiesPanel } from './panels/PropertiesPanel'
import { ProblemsPanel } from './panels/ProblemsPanel'
import { OutputPanel } from './panels/OutputPanel'
import { LayersPanel } from './panels/LayersPanel'
import { AssetsPanel } from './panels/AssetsPanel'
import { GoalPlanningPanel } from './panels/GoalPlanningPanel'
import { ContextWebPanel } from './panels/ContextWebPanel'
import { NLTagPanel } from './panels/NLTagPanel'
import { ToolSelectionPanel } from './panels/ToolSelectionPanel'
import { DebugConsolePanel } from './panels/DebugConsolePanel'
import { FileChangesViewerPanel } from './panels/FileChangesViewerPanel'
import { BitemporalTimelinePanel } from './panels/BitemporalTimelinePanel'
import { LucidOrchestratorPanel } from './LucidOrchestratorPanel'
import { ConsciousnessExplorer } from './ConsciousnessExplorer'
import { EvolutionExplorer } from './AgentManagementDashboard/EvolutionExplorer'
import { AgentManagementDashboard } from './AgentManagementDashboard'
import ConsciousnessVisualization from './ConsciousnessVisualization'
import { LucidOrchestratorMain } from './LucidOrchestratorMain'
import { PanelManagementModal } from './PanelManagementModal'
import { EnhancedResizeHandle } from './EnhancedResizeHandle'
import { LayoutSelector } from './LayoutSelector'
import { ConnectionStatus } from './ConnectionStatus'
import { ErrorBoundary } from './ErrorBoundary'
import { useTheme } from '../hooks/useTheme'
import { SkipToMainContent, AriaLiveRegion } from '../hooks/useAccessibility'
import {
  FolderOpen,
  Code,
  Search,
  Settings,
  Terminal,
  Layers,
  Brain,
  Activity,
  Database,
  GitBranch,
  FileText,
  ChevronDown,
  ChevronUp,
  X
} from 'lucide-react'

// Panel Types
export type LeftPanelType = 
  | 'file-explorer'
  | 'component-library'
  | 'ai-memory'
  | 'git'
  | 'templates'
  | 'lucid-orchestrator'
  | 'consciousness-explorer'
  | 'tool-quality'
  | null

export type RightPanelType =
  | 'outline'
  | 'properties'
  | 'layers'
  | 'assets'
  | 'settings'
  | 'goal-planning'
  | 'context-web'
  | 'nl-tag'
  | 'tool-selection'
  | null

export type BottomPanelType =
  | 'terminal'
  | 'problems'
  | 'output'
  | 'debug-console'
  | 'timeline'
  | 'file-changes'
  | null

export type MainContentMode =
  | 'code-editor'
  | 'evolution-explorer'
  | 'agent-management'
  | 'consciousness-visualization'
  | 'lucid-orchestrator'

interface RevIDELayoutProps {
  theme?: 'dark' | 'light' | 'high-contrast'
}

/**
 * Rev's IDE Layout Component
 * 
 * Architecture:
 * - Top Bar: Mode switcher, command palette trigger
 * - Left Drawer: Vertical PanelGroup with resizable panels
 * - Main Content: Flexible area for different modes
 * - Right Drawer: Vertical PanelGroup with resizable panels
 * - Bottom Drawer: Horizontal PanelGroup (collapsible)
 * - Left Icon Bar: Panel selector icons
 * - Right Icon Bar: Panel selector icons
 */
export const RevIDELayout: React.FC<RevIDELayoutProps> = ({ theme: propTheme }) => {
  const { activeTabId, tabs, updateTabContent } = useEditorStore()
  const { theme, resolvedTheme, currentTheme, setTheme } = useTheme()
  
  // Use prop theme if provided, otherwise use hook theme
  const activeTheme = propTheme || resolvedTheme
  
  // Panel state
  const [leftTopPanel, setLeftTopPanel] = useState<LeftPanelType>('file-explorer')
  const [leftBottomPanel, setLeftBottomPanel] = useState<LeftPanelType>(null)
  const [rightTopPanel, setRightTopPanel] = useState<RightPanelType>('outline')
  const [rightBottomPanel, setRightBottomPanel] = useState<RightPanelType>(null)
  const [bottomPanel, setBottomPanel] = useState<BottomPanelType>(null)
  const [bottomDrawerOpen, setBottomDrawerOpen] = useState(false)
  
  // Main content mode
  const [mainContentMode, setMainContentMode] = useState<MainContentMode>('code-editor')
  
  // UI state
  const [hoveredIcon, setHoveredIcon] = useState<string | null>(null)
  const [isCommandPaletteOpen, setIsCommandPaletteOpen] = useState(false)
  const [isPanelManagementOpen, setIsPanelManagementOpen] = useState(false)
  
  const activeTab = tabs.find(t => t.id === activeTabId)

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Command Palette: Ctrl+K or Cmd+K
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault()
        setIsCommandPaletteOpen(true)
      }
      
      // Toggle Bottom Drawer: Ctrl+` or Cmd+`
      if ((e.ctrlKey || e.metaKey) && e.key === '`') {
        e.preventDefault()
        setBottomDrawerOpen(!bottomDrawerOpen)
      }
      
      // Panel shortcuts
      if ((e.ctrlKey || e.metaKey) && e.shiftKey) {
        switch (e.key) {
          case 'E': // File Explorer
            e.preventDefault()
            setLeftTopPanel(leftTopPanel === 'file-explorer' ? null : 'file-explorer')
            break
          case 'O': // Outline
            e.preventDefault()
            setRightTopPanel(rightTopPanel === 'outline' ? null : 'outline')
            break
          case 'M': // AI Memory
            e.preventDefault()
            setLeftTopPanel(leftTopPanel === 'ai-memory' ? null : 'ai-memory')
            break
          case 'T': // Terminal
            e.preventDefault()
            setBottomPanel(bottomPanel === 'terminal' ? null : 'terminal')
            setBottomDrawerOpen(bottomPanel === 'terminal' ? false : true)
            break
        }
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [leftTopPanel, rightTopPanel, bottomPanel, bottomDrawerOpen])

  // Render left panel content
  const renderLeftPanel = useCallback((panel: LeftPanelType) => {
    switch (panel) {
      case 'file-explorer':
        return <ErrorBoundary><FileExplorerPanel /></ErrorBoundary>
      case 'ai-memory':
        return <ErrorBoundary><AIMemoryPanel /></ErrorBoundary>
      case 'component-library':
        return <ErrorBoundary><ComponentLibraryPanel /></ErrorBoundary>
      case 'git':
        return <ErrorBoundary><GitPanel /></ErrorBoundary>
      case 'templates':
        return <ErrorBoundary><TemplatesPanel /></ErrorBoundary>
      case 'lucid-orchestrator':
        return <ErrorBoundary><LucidOrchestratorPanel /></ErrorBoundary>
      case 'consciousness-explorer':
        return <ErrorBoundary><ConsciousnessExplorer /></ErrorBoundary>
      case 'tool-quality':
        return <ErrorBoundary><ToolQualityDashboardPanel /></ErrorBoundary>
      default:
        return (
          <div className="h-full bg-gray-800 flex items-center justify-center text-gray-500 text-sm">
            No panel selected
          </div>
        )
    }
  }, [])

  // Render right panel content
  const renderRightPanel = useCallback((panel: RightPanelType) => {
    switch (panel) {
      case 'outline':
        return <ErrorBoundary><OutlinePanel /></ErrorBoundary>
      case 'properties':
        return <ErrorBoundary><PropertiesPanel /></ErrorBoundary>
      case 'layers':
        return <ErrorBoundary><LayersPanel /></ErrorBoundary>
      case 'assets':
        return <ErrorBoundary><AssetsPanel /></ErrorBoundary>
      case 'settings':
        return <ErrorBoundary><SettingsPanel /></ErrorBoundary>
      case 'goal-planning':
        return <ErrorBoundary><GoalPlanningPanel /></ErrorBoundary>
      case 'context-web':
        return <ErrorBoundary><ContextWebPanel /></ErrorBoundary>
      case 'nl-tag':
        return <ErrorBoundary><NLTagPanel /></ErrorBoundary>
      case 'tool-selection':
        return <ErrorBoundary><ToolSelectionPanel /></ErrorBoundary>
      default:
        return (
          <div className="h-full bg-gray-800 flex items-center justify-center text-gray-500 text-sm">
            No panel selected
          </div>
        )
    }
  }, [])

  // Render bottom panel content
  const renderBottomPanel = useCallback((panel: BottomPanelType) => {
    switch (panel) {
      case 'terminal':
        return <ErrorBoundary><EnhancedTerminalPanel /></ErrorBoundary>
      case 'problems':
        return <ErrorBoundary><ProblemsPanel /></ErrorBoundary>
      case 'output':
        return <ErrorBoundary><OutputPanel /></ErrorBoundary>
      case 'debug-console':
        return <ErrorBoundary><DebugConsolePanel /></ErrorBoundary>
      case 'timeline':
        return (
          <ErrorBoundary>
            <BitemporalTimelinePanel />
          </ErrorBoundary>
        )
      case 'file-changes':
        return <ErrorBoundary><FileChangesViewerPanel /></ErrorBoundary>
      default:
        return (
          <div className="h-full bg-gray-800 flex items-center justify-center text-gray-500 text-sm">
            No panel selected
          </div>
        )
    }
  }, [])

  // Render main content based on mode
  const renderMainContent = useCallback(() => {
    switch (mainContentMode) {
      case 'code-editor':
        return (
          <div className="h-full flex flex-col bg-gray-900">
            {tabs.length > 0 && <EditorTabs />}
            <div className="flex-1 overflow-hidden">
              {activeTab ? (
                <LucidMonacoEditor
                  value={activeTab.content}
                  language={activeTab.language}
                  fileName={activeTab.fileName}
                  onChange={(value) => updateTabContent(activeTab.id, value || '')}
                  theme="vs-dark"
                  readOnly={activeTab.readOnly}
                  enableLucidFolds={true}
                />
              ) : (
                <div className="h-full flex items-center justify-center text-gray-500">
                  <div className="text-center">
                    <Code className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p className="text-lg mb-2">No file open</p>
                    <p className="text-sm">Open a file from the File Explorer or create a new one</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        )
      case 'evolution-explorer':
        return (
          <ErrorBoundary>
            <div className="h-full bg-gray-900">
              <EvolutionExplorer />
            </div>
          </ErrorBoundary>
        )
      case 'agent-management':
        return (
          <ErrorBoundary>
            <div className="h-full bg-gray-900">
              <AgentManagementDashboard />
            </div>
          </ErrorBoundary>
        )
      case 'consciousness-visualization':
        return (
          <ErrorBoundary>
            <div className="h-full bg-gray-900">
              <ConsciousnessVisualization />
            </div>
          </ErrorBoundary>
        )
      case 'lucid-orchestrator':
        return (
          <ErrorBoundary>
            <div className="h-full bg-gray-900">
              <LucidOrchestratorMain />
            </div>
          </ErrorBoundary>
        )
      default:
        return (
          <div className="h-full bg-gray-900 flex items-center justify-center text-gray-500">
            Unknown mode
          </div>
        )
    }
  }, [mainContentMode, tabs, activeTab, updateTabContent])

  return (
    <div className="flex flex-col h-screen bg-gray-900 text-gray-100" data-theme={activeTheme}>
      {/* Accessibility: Skip to main content */}
      <SkipToMainContent />
      
      {/* Accessibility: ARIA live region for announcements */}
      <AriaLiveRegion priority="polite" />
      
      {/* Command Palette */}
      {isCommandPaletteOpen && (
        <CommandPalette />
      )}

      {/* Panel Management Modal */}
      <PanelManagementModal
        isOpen={isPanelManagementOpen}
        onClose={() => setIsPanelManagementOpen(false)}
        leftTopPanel={leftTopPanel || 'file-explorer'}
        leftBottomPanel={leftBottomPanel}
        rightTopPanel={rightTopPanel || 'outline'}
        rightBottomPanel={rightBottomPanel}
        bottomPanel={bottomPanel}
        onUpdatePanels={(panels) => {
          setLeftTopPanel(panels.leftTop)
          setLeftBottomPanel(panels.leftBottom)
          setRightTopPanel(panels.rightTop)
          setRightBottomPanel(panels.rightBottom)
          setBottomPanel(panels.bottom)
        }}
      />

      {/* Top Bar */}
      <div className="h-12 bg-gray-800 border-b border-gray-700 flex items-center px-4 gap-2 shrink-0">
        <button
          onClick={() => setMainContentMode('code-editor')}
          className={`flex items-center gap-2 px-4 py-2 text-sm rounded transition-colors ${
            mainContentMode === 'code-editor'
              ? 'bg-blue-600 text-white'
              : 'text-gray-400 hover:text-white hover:bg-gray-700'
          }`}
          aria-label="Code Editor Mode"
        >
          <Code className="w-4 h-4" />
          Code Editor
        </button>
        <button
          onClick={() => setMainContentMode('evolution-explorer')}
          className={`flex items-center gap-2 px-4 py-2 text-sm rounded transition-colors ${
            mainContentMode === 'evolution-explorer'
              ? 'bg-blue-600 text-white'
              : 'text-gray-400 hover:text-white hover:bg-gray-700'
          }`}
          aria-label="Evolution Explorer Mode"
        >
          <Brain className="w-4 h-4" />
          Evolution Explorer ⭐
        </button>
        <button
          onClick={() => setMainContentMode('agent-management')}
          className={`flex items-center gap-2 px-4 py-2 text-sm rounded transition-colors ${
            mainContentMode === 'agent-management'
              ? 'bg-blue-600 text-white'
              : 'text-gray-400 hover:text-white hover:bg-gray-700'
          }`}
          aria-label="Agent Management Mode"
        >
          <Activity className="w-4 h-4" />
          Agent Management
        </button>
        <button
          onClick={() => setMainContentMode('consciousness-visualization')}
          className={`flex items-center gap-2 px-4 py-2 text-sm rounded transition-colors ${
            mainContentMode === 'consciousness-visualization'
              ? 'bg-blue-600 text-white'
              : 'text-gray-400 hover:text-white hover:bg-gray-700'
          }`}
          aria-label="Consciousness Visualization Mode"
        >
          <Brain className="w-4 h-4" />
          Consciousness ⭐
        </button>
        <div className="flex-1" />
        <ConnectionStatus className="mr-2" />
        {/* Theme Selector */}
        <div className="relative mr-2">
          <button
            onClick={() => {
              const themes: Array<'dark' | 'light' | 'high-contrast' | 'auto'> = ['dark', 'light', 'high-contrast', 'auto']
              const currentIndex = themes.indexOf(theme)
              const nextIndex = (currentIndex + 1) % themes.length
              setTheme(themes[nextIndex])
            }}
            className="px-3 py-1.5 text-sm text-gray-400 hover:text-white hover:bg-gray-700 rounded flex items-center gap-1"
            aria-label={`Current theme: ${theme}. Click to change theme.`}
            title={`Theme: ${theme}`}
          >
            <Palette className="w-4 h-4" />
            <span className="text-xs">{theme}</span>
          </button>
        </div>
        <LayoutSelector
          currentConfig={{
            leftTop: leftTopPanel || 'file-explorer',
            leftBottom: leftBottomPanel,
            rightTop: rightTopPanel || 'outline',
            rightBottom: rightBottomPanel,
            bottom: bottomPanel,
            mainContentMode
          }}
          onLoadLayout={(config) => {
            setLeftTopPanel(config.leftTop)
            setLeftBottomPanel(config.leftBottom)
            setRightTopPanel(config.rightTop)
            setRightBottomPanel(config.rightBottom)
            setBottomPanel(config.bottom)
            setMainContentMode(config.mainContentMode)
          }}
        />
        <button
          onClick={() => setIsCommandPaletteOpen(true)}
          className="px-3 py-1.5 text-sm text-gray-400 hover:text-white hover:bg-gray-700 rounded"
          aria-label="Open Command Palette (Ctrl+K)"
        >
          <Search className="w-4 h-4" />
        </button>
        <button
          onClick={() => setIsPanelManagementOpen(true)}
          className="px-3 py-1.5 text-sm text-gray-400 hover:text-white hover:bg-gray-700 rounded"
          aria-label="Open Panel Management"
          title="Panel Management (Drag & Drop)"
        >
          <Layers className="w-4 h-4" />
        </button>
      </div>

      {/* Main Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Icon Bar */}
        <div className="w-10 bg-gray-800 border-r border-gray-700 flex flex-col items-center py-2 gap-2 shrink-0">
          <button
            onMouseEnter={() => setHoveredIcon('left-explorer')}
            onMouseLeave={() => setHoveredIcon(null)}
            onClick={() => setLeftTopPanel(leftTopPanel === 'file-explorer' ? null : 'file-explorer')}
            className={`relative w-8 h-8 flex items-center justify-center rounded transition-colors ${
              leftTopPanel === 'file-explorer'
                ? 'text-white bg-gray-700'
                : 'text-gray-400 hover:text-white hover:bg-gray-700'
            }`}
            aria-label="File Explorer (Ctrl+Shift+E)"
            title="File Explorer (Ctrl+Shift+E)"
          >
            <FolderOpen className="w-5 h-5" />
            {hoveredIcon === 'left-explorer' && (
              <div className="absolute left-full ml-2 flex gap-1 z-50 bg-gray-900 border border-gray-700 rounded shadow-lg">
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    setLeftTopPanel('file-explorer')
                    setLeftBottomPanel(null)
                  }}
                  className="w-8 h-8 flex items-center justify-center hover:bg-gray-700"
                  title="Show in top only"
                >
                  <ChevronUp className="w-4 h-4" />
                </button>
                <div className="w-0.5 bg-gray-700 my-1" />
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    setLeftTopPanel('file-explorer')
                    setLeftBottomPanel('file-explorer')
                  }}
                  className="w-8 h-8 flex items-center justify-center hover:bg-gray-700"
                  title="Split vertically"
                >
                  <ChevronDown className="w-4 h-4" />
                </button>
              </div>
            )}
          </button>
          <button
            onMouseEnter={() => setHoveredIcon('left-memory')}
            onMouseLeave={() => setHoveredIcon(null)}
            onClick={() => setLeftTopPanel(leftTopPanel === 'ai-memory' ? null : 'ai-memory')}
            className={`relative w-8 h-8 flex items-center justify-center rounded transition-colors ${
              leftTopPanel === 'ai-memory'
                ? 'text-white bg-gray-700'
                : 'text-gray-400 hover:text-white hover:bg-gray-700'
            }`}
            aria-label="AI Memory (Ctrl+Shift+M)"
            title="AI Memory (Ctrl+Shift+M)"
          >
            <Database className="w-5 h-5" />
          </button>
        </div>

        {/* Left Drawer - Split Panels */}
        <PanelGroup direction="vertical" className="w-64 min-w-64 max-w-96 bg-gray-800 border-r border-gray-700">
          <Panel defaultSize={leftBottomPanel ? 50 : 100} minSize={20} maxSize={leftBottomPanel ? 80 : 100}>
            <div className="h-full border-b border-gray-700">
              {renderLeftPanel(leftTopPanel)}
            </div>
          </Panel>
          {leftBottomPanel && (
            <>
              <EnhancedResizeHandle
                direction="vertical"
                snapPoints={[25, 33, 50, 67, 75]}
                minSize={20}
                maxSize={80}
                showPreview={true}
              />
              <Panel defaultSize={50} minSize={20} maxSize={80}>
                {renderLeftPanel(leftBottomPanel)}
              </Panel>
            </>
          )}
        </PanelGroup>

        {/* Main Content Area */}
        <div className="flex-1 min-w-0 overflow-hidden bg-gray-900">
          {renderMainContent()}
        </div>

        {/* Right Drawer - Split Panels */}
        <PanelGroup direction="vertical" className="w-64 min-w-64 max-w-96 bg-gray-800 border-l border-gray-700">
          <Panel defaultSize={rightBottomPanel ? 50 : 100} minSize={20} maxSize={rightBottomPanel ? 80 : 100}>
            <div className="h-full border-b border-gray-700">
              {renderRightPanel(rightTopPanel)}
            </div>
          </Panel>
          {rightBottomPanel && (
            <>
              <EnhancedResizeHandle
                direction="vertical"
                snapPoints={[25, 33, 50, 67, 75]}
                minSize={20}
                maxSize={80}
                showPreview={true}
              />
              <Panel defaultSize={50} minSize={20} maxSize={80}>
                {renderRightPanel(rightBottomPanel)}
              </Panel>
            </>
          )}
        </PanelGroup>

        {/* Right Icon Bar */}
        <div className="w-10 bg-gray-800 border-l border-gray-700 flex flex-col items-center py-2 gap-2 shrink-0">
          <button
            onMouseEnter={() => setHoveredIcon('right-outline')}
            onMouseLeave={() => setHoveredIcon(null)}
            onClick={() => setRightTopPanel(rightTopPanel === 'outline' ? null : 'outline')}
            className={`relative w-8 h-8 flex items-center justify-center rounded transition-colors ${
              rightTopPanel === 'outline'
                ? 'text-white bg-gray-700'
                : 'text-gray-400 hover:text-white hover:bg-gray-700'
            }`}
            aria-label="Outline (Ctrl+Shift+O)"
            title="Outline (Ctrl+Shift+O)"
          >
            <Layers className="w-5 h-5" />
          </button>
          <button
            onMouseEnter={() => setHoveredIcon('right-context-web')}
            onMouseLeave={() => setHoveredIcon(null)}
            onClick={() => setRightTopPanel(rightTopPanel === 'context-web' ? null : 'context-web')}
            className={`relative w-8 h-8 flex items-center justify-center rounded transition-colors ${
              rightTopPanel === 'context-web'
                ? 'text-white bg-gray-700'
                : 'text-gray-400 hover:text-white hover:bg-gray-700'
            }`}
            aria-label="Context Web ⭐"
            title="Context Web ⭐"
          >
            <Brain className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Bottom Bar */}
      <div className="h-10 bg-gray-800 border-t border-gray-700 flex items-center px-4 gap-4 shrink-0">
        <button
          onClick={() => {
            setBottomPanel('terminal')
            setBottomDrawerOpen(!bottomDrawerOpen)
          }}
          className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
            bottomDrawerOpen && bottomPanel === 'terminal'
              ? 'bg-blue-600 text-white'
              : 'text-gray-400 hover:text-white hover:bg-gray-700'
          }`}
          aria-label="Terminal (Ctrl+Shift+T)"
          title="Terminal (Ctrl+Shift+T)"
        >
          <Terminal className="w-4 h-4 inline mr-2" />
          Terminal
        </button>
        <button
          onClick={() => {
            setBottomPanel('timeline')
            setBottomDrawerOpen(!bottomDrawerOpen)
          }}
          className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
            bottomDrawerOpen && bottomPanel === 'timeline'
              ? 'bg-blue-600 text-white'
              : 'text-gray-400 hover:text-white hover:bg-gray-700'
          }`}
          aria-label="Bitemporal Timeline ⭐"
          title="Bitemporal Timeline ⭐"
        >
          <Activity className="w-4 h-4 inline mr-2" />
          Timeline ⭐
        </button>
        <button
          onClick={() => {
            setBottomPanel('problems')
            setBottomDrawerOpen(!bottomDrawerOpen)
          }}
          className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
            bottomDrawerOpen && bottomPanel === 'problems'
              ? 'bg-blue-600 text-white'
              : 'text-gray-400 hover:text-white hover:bg-gray-700'
          }`}
          aria-label="Problems"
          title="Problems"
        >
          <Activity className="w-4 h-4 inline mr-2" />
          Problems
        </button>
        {bottomDrawerOpen && (
          <button
            onClick={() => setBottomDrawerOpen(false)}
            className="ml-auto px-2 py-1 text-gray-400 hover:text-white hover:bg-gray-700 rounded"
            aria-label="Close Bottom Drawer"
            title="Close Bottom Drawer"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Bottom Drawer */}
      {bottomDrawerOpen && bottomPanel && (
        <PanelGroup direction="horizontal" className="h-64 min-h-32 max-h-96 bg-gray-800 border-t border-gray-700">
          <Panel defaultSize={100} minSize={30} maxSize={100}>
            {renderBottomPanel(bottomPanel)}
          </Panel>
        </PanelGroup>
      )}
    </div>
  )
}

