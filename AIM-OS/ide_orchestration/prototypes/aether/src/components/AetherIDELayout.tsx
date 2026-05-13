import React, { useMemo, useCallback } from 'react'
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels'
import {
  FolderOpen,
  Code,
  Database,
  Target,
  Activity,
  Network,
  GitBranch,
  FileText,
  Settings,
  Terminal,
  AlertTriangle,
  Clock,
  Brain,
  Zap,
  Layers,
  Eye,
  Bug,
  Save
} from 'lucide-react'

// Panel Components
import {
  FileExplorerPanel,
  ComponentLibraryPanel,
  AIMemoryPanel,
  GoalPlanningPanel,
  SystemStatusPanel,
  CodeEditorPanel,
  EvolutionExplorerPanel,
  ConsciousnessVisualizationPanel,
  AgentManagementPanel,
  LucidOrchestratorPanel,
  ContextWebPanel,
  EvidenceGraphPanel,
  TimelineViewPanel,
  MCPToolsPanel,
  ConfidenceCalibrationPanel,
  NLTagsPanel,
  TerminalPanel,
  ProblemsPanel,
  TimelinePanel,
  FileChangesPanel,
  DebugConsolePanel,
  SuperIndexPanel,
  MasterIndexPanel,
  SystemMapPanel,
  NLTagsExplorerPanel,
  DocumentationExplorerPanel,
  HierarchicalCodeExplorerV1,
  HierarchicalCodeExplorerV2,
  HierarchicalCodeExplorerV3,
  FileVersionHistoryPanel,
  FileVersionHistoryPanelV2,
  AIMOSStatusPanel
} from './panels'

// Mock Data
import {
  mockFileTree,
  mockTimeline,
  mockContextWeb,
  mockAgents,
  mockGoals,
  mockCode,
  mockTerminal,
  mockMCPTools,
  mockConsciousnessState,
  mockEvidenceGraph
} from '../mockData'
import {
  mockDebugConsole,
  mockDebugLogsBySystem,
  mockDebugAnalysis,
  mockDebugInfrastructure
} from '../mockData/debugData'

// Panel Store Integration
import { usePanelStore } from '../stores/panelStore'
import { usePanelInitialization, useActivePanel, usePanelControls } from './hooks/usePanelManagement'
import { DEFAULT_PANEL_CONFIGS, PANEL_ID_MAP } from './panelMappings'
import { PanelErrorBoundary } from './ErrorBoundary'
import { PanelSuspense, LoadingPanel } from './LoadingPanel'
import type { PanelZone, PanelId } from '../stores/panelStore'

// Panel Icon Mapping
const PANEL_ICONS: Record<string, React.ReactNode> = {
  'file-explorer': <FolderOpen className="w-4 h-4 inline mr-1" />,
  'components': <Layers className="w-4 h-4 inline mr-1" />,
  'memory': <Database className="w-4 h-4 inline mr-1" />,
  'goals': <Target className="w-4 h-4 inline mr-1" />,
  'status': <Activity className="w-4 h-4 inline mr-1" />,
  'super-index': <FileText className="w-3 h-3 inline mr-1" />,
  'master-index': <FileText className="w-3 h-3 inline mr-1" />,
  'system-map': <Network className="w-3 h-3 inline mr-1" />,
  'nl-tags-explorer': <FileText className="w-3 h-3 inline mr-1" />,
  'docs-explorer': <FileText className="w-3 h-3 inline mr-1" />,
  'aimos-status': <Activity className="w-3 h-3 inline mr-1" />,
  'code-editor': <Code className="w-4 h-4 inline mr-1" />,
  'evolution-explorer': <Network className="w-4 h-4 inline mr-1" />,
  'consciousness': <Brain className="w-4 h-4 inline mr-1" />,
  'agents': <Zap className="w-4 h-4 inline mr-1" />,
  'orchestrator': <GitBranch className="w-4 h-4 inline mr-1" />,
  'hierarchical-code-v1': <Code className="w-4 h-4 inline mr-1" />,
  'hierarchical-code-v2': <Code className="w-4 h-4 inline mr-1" />,
  'hierarchical-code-v3': <Code className="w-4 h-4 inline mr-1" />,
  'context-web': <Network className="w-4 h-4 inline mr-1" />,
  'evidence': <Eye className="w-4 h-4 inline mr-1" />,
  'timeline-view': <Clock className="w-4 h-4 inline mr-1" />,
  'mcp-tools': <Zap className="w-4 h-4 inline mr-1" />,
  'confidence': <Target className="w-4 h-4 inline mr-1" />,
  'nl-tags': <FileText className="w-4 h-4 inline mr-1" />,
  'version-history': <GitBranch className="w-4 h-4 inline mr-1" />,
  'version-history-v2': <GitBranch className="w-4 h-4 inline mr-1" />,
  'terminal': <Terminal className="w-4 h-4 inline mr-1" />,
  'problems': <AlertTriangle className="w-4 h-4 inline mr-1" />,
  'timeline': <Clock className="w-4 h-4 inline mr-1" />,
  'file-changes': <GitBranch className="w-4 h-4 inline mr-1" />,
  'debug-console': <Bug className="w-4 h-4 inline mr-1" />
}

// Panel Label Mapping
const PANEL_LABELS: Record<string, string> = {
  'file-explorer': 'Files',
  'components': 'Components',
  'memory': 'Memory',
  'goals': 'Goals',
  'status': 'Status',
  'super-index': 'Super Index',
  'master-index': 'Master Index',
  'system-map': 'System Map',
  'nl-tags-explorer': 'NL Tags',
  'docs-explorer': 'Docs',
  'aimos-status': 'AIM-OS Status',
  'code-editor': 'Code Editor',
  'evolution-explorer': 'Evolution Explorer',
  'consciousness': 'Consciousness',
  'agents': 'Agents',
  'orchestrator': 'Orchestrator',
  'hierarchical-code-v1': 'Code V1',
  'hierarchical-code-v2': 'Code V2',
  'hierarchical-code-v3': 'Code V3',
  'context-web': 'Context Web',
  'evidence': 'Evidence',
  'timeline-view': 'Timeline',
  'mcp-tools': 'MCP Tools',
  'confidence': 'Confidence',
  'nl-tags': 'NL Tags',
  'version-history': 'Versions',
  'version-history-v2': 'Versions V2',
  'terminal': 'Terminal',
  'problems': 'Problems',
  'timeline': 'Timeline',
  'file-changes': 'File Changes',
  'debug-console': 'Debug Console'
}

// Render panel component based on panel ID
function renderPanel(panelId: PanelId): React.ReactNode {
  switch (panelId) {
    // Left panels
    case 'file-explorer':
      return <FileExplorerPanel data={mockFileTree} />
    case 'components':
      return <ComponentLibraryPanel />
    case 'memory':
      return <AIMemoryPanel />
    case 'goals':
      return <GoalPlanningPanel data={mockGoals} />
    case 'status':
      return <SystemStatusPanel />
    case 'super-index':
      return <SuperIndexPanel />
    case 'master-index':
      return <MasterIndexPanel />
    case 'system-map':
      return <SystemMapPanel />
    case 'nl-tags-explorer':
      return <NLTagsExplorerPanel />
    case 'docs-explorer':
      return <DocumentationExplorerPanel />
    case 'aimos-status':
      return <AIMOSStatusPanel />
    
    // Main content panels
    case 'code-editor':
      return <CodeEditorPanel code={mockCode} />
    case 'evolution-explorer':
      return <EvolutionExplorerPanel />
    case 'consciousness':
      return <ConsciousnessVisualizationPanel data={mockConsciousnessState} />
    case 'agents':
      return <AgentManagementPanel data={mockAgents} />
    case 'orchestrator':
      return <LucidOrchestratorPanel />
    case 'hierarchical-code-v1':
      return <HierarchicalCodeExplorerV1 activeFile="src/components/AetherIDELayout.tsx" activeSection="Top Bar" />
    case 'hierarchical-code-v2':
      return <HierarchicalCodeExplorerV2 />
    case 'hierarchical-code-v3':
      return <HierarchicalCodeExplorerV3 />
    
    // Right panels
    case 'context-web':
      return <ContextWebPanel data={mockContextWeb} />
    case 'evidence':
      return <EvidenceGraphPanel data={mockEvidenceGraph} />
    case 'timeline-view':
      return <TimelineViewPanel data={mockTimeline} />
    case 'mcp-tools':
      return <MCPToolsPanel data={mockMCPTools} />
    case 'confidence':
      return <ConfidenceCalibrationPanel />
    case 'nl-tags':
      return <NLTagsPanel />
    case 'version-history':
      return <FileVersionHistoryPanel filePath="IDELayout.tsx" />
    case 'version-history-v2':
      return <FileVersionHistoryPanelV2 filePath="IDELayout.tsx" />
    
    // Bottom panels
    case 'terminal':
      return <TerminalPanel data={mockTerminal} />
    case 'problems':
      return <ProblemsPanel />
    case 'timeline':
      return <TimelinePanel data={mockTimeline} />
    case 'file-changes':
      return <FileChangesPanel />
    case 'debug-console':
      return (
        <DebugConsolePanel
          console={mockDebugConsole}
          logsBySystem={mockDebugLogsBySystem}
          analysis={mockDebugAnalysis}
          infrastructure={mockDebugInfrastructure}
        />
      )
    
    default:
      return null
  }
}

export const AetherIDELayout: React.FC = () => {
  // Initialize panels
  usePanelInitialization()
  
  // Panel store
  const { panels, getPanelsByZone, layoutPresets, saveLayoutPreset, loadLayoutPreset, currentPreset, clearPersistedData } = usePanelStore()
  const { togglePanel } = usePanelControls()
  
  // Clear cache handler
  const handleClearCache = useCallback(() => {
    if (confirm('Clear all cached panel state? This will reset the layout to defaults.')) {
      clearPersistedData()
      window.location.reload()
    }
  }, [clearPersistedData])
  
  // Get active panels for each zone
  const leftPanels = getPanelsByZone('left')
  const mainPanels = getPanelsByZone('main')
  const rightPanels = getPanelsByZone('right')
  const bottomPanels = getPanelsByZone('bottom')
  
  // Fallback: If no panels, create buttons from default configs
  const leftPanelButtons = leftPanels.length > 0 ? leftPanels : Object.values(DEFAULT_PANEL_CONFIGS).filter(p => p.zone === 'left')
  const mainPanelButtons = mainPanels.length > 0 ? mainPanels : Object.values(DEFAULT_PANEL_CONFIGS).filter(p => p.zone === 'main')
  const rightPanelButtons = rightPanels.length > 0 ? rightPanels : Object.values(DEFAULT_PANEL_CONFIGS).filter(p => p.zone === 'right')
  const bottomPanelButtons = bottomPanels.length > 0 ? bottomPanels : Object.values(DEFAULT_PANEL_CONFIGS).filter(p => p.zone === 'bottom')
  
  // Debug logging
  console.log('[AETHER] Layout render - Left panels:', leftPanels.length, leftPanels.map(p => p.id))
  console.log('[AETHER] Layout render - Main panels:', mainPanels.length, mainPanels.map(p => p.id))
  console.log('[AETHER] Layout render - Right panels:', rightPanels.length, rightPanels.map(p => p.id))
  console.log('[AETHER] Layout render - Bottom panels:', bottomPanels.length, bottomPanels.map(p => p.id))
  console.log('[AETHER] Layout render - All panels:', Object.keys(panels))
  
  // Get active panel IDs (first visible panel, or first panel if none visible)
  const activeLeftPanel = useActivePanel('left')
  const activeMainPanel = useActivePanel('main')
  const activeRightPanel = useActivePanel('right')
  const activeBottomPanel = useActivePanel('bottom')
  
  // Bottom drawer visibility (check if any bottom panel is visible)
  const bottomDrawerOpen = useMemo(() => {
    return bottomPanels.some(p => p.visible)
  }, [bottomPanels])
  
  // Layout preset handlers (memoized)
  const handleSaveLayout = useCallback(() => {
    const name = prompt('Layout name:')
    if (name) {
      saveLayoutPreset(name, 'Custom layout')
    }
  }, [saveLayoutPreset])
  
  const handleLoadLayout = useCallback((presetName: string) => {
    if (presetName) {
      loadLayoutPreset(presetName)
    }
  }, [loadLayoutPreset])
  
  // Panel toggle handler (memoized)
  const handlePanelToggle = useCallback((panelId: PanelId) => {
    console.log('[AETHER] Panel toggle clicked:', panelId)
    const store = usePanelStore.getState()
    let panel = store.panels[panelId]
    
    console.log('[AETHER] Current panel state:', panel)
    
    // If panel doesn't exist, try to add it from default configs
    if (!panel) {
      console.log('[AETHER] Panel not found, trying to add from defaults')
      const defaultConfig = DEFAULT_PANEL_CONFIGS[panelId as keyof typeof DEFAULT_PANEL_CONFIGS]
      if (defaultConfig) {
        console.log('[AETHER] Adding panel from default config')
        store.addPanel(defaultConfig)
        panel = store.panels[panelId]
        console.log('[AETHER] Panel added, new state:', panel)
      } else {
        console.warn(`[AETHER] Panel ${panelId} not found and no default config available`)
        return
      }
    }
    
    // If panel is not visible, make it visible and active
    if (!panel.visible) {
      console.log('[AETHER] Making panel visible:', panelId, 'current visible:', panel.visible)
      togglePanel(panelId)
      // Make it active by updating order to 0 (brings to front)
      store.updatePanel(panelId, { order: 0 })
      
      // Verify the toggle worked
      const updatedPanel = store.panels[panelId]
      console.log('[AETHER] Panel after toggle - visible:', updatedPanel?.visible, 'order:', updatedPanel?.order)
    } else {
      // If panel is visible, make it active (bring to front by setting order to -1 to ensure it's first)
      console.log('[AETHER] Making panel active:', panelId, 'current order:', panel.order)
      // Set order to -1 to ensure it's before all others (order 0)
      const allPanelsInZone = store.getPanelsByZone(panel.zone)
      const minOrder = Math.min(...allPanelsInZone.map(p => p.order), 0)
      store.updatePanel(panelId, { order: minOrder - 1 })
      
      const updatedPanel = store.panels[panelId]
      console.log('[AETHER] Panel after order update - order:', updatedPanel?.order)
    }
  }, [panels, togglePanel])
  
  // Hide bottom drawer handler (memoized)
  const handleHideBottomDrawer = useCallback(() => {
    bottomPanels.forEach(panel => {
      if (panel.visible) {
        togglePanel(panel.id)
      }
    })
  }, [bottomPanels, togglePanel])

  return (
    <div className="h-screen w-screen flex flex-col bg-gray-900 text-gray-100">
      {/* Top Bar */}
      <div className="h-12 bg-gray-800 border-b border-gray-700 flex items-center justify-between px-4">
        <div className="flex items-center gap-4">
          <span className="text-lg font-bold text-blue-400">Aether IDE</span>
          <span className="text-xs text-gray-400">System Architecture & Deep AIM-OS Integration</span>
        </div>
        <div className="flex items-center gap-4">
          {/* Layout Preset Controls */}
          <div className="flex items-center gap-2">
            <button
              onClick={handleClearCache}
              className="text-xs bg-red-600 text-white px-2 py-1 rounded hover:bg-red-700"
              title="Clear cached state (fixes stuck panels)"
            >
              Clear Cache
            </button>
            <select
              value={currentPreset || ''}
              onChange={(e) => handleLoadLayout(e.target.value)}
              className="text-xs bg-gray-700 text-gray-300 px-2 py-1 rounded border border-gray-600 hover:border-gray-500"
            >
              <option value="">Default Layout</option>
              {Object.keys(layoutPresets).map(name => (
                <option key={name} value={name}>{name}</option>
              ))}
            </select>
            <button
              onClick={handleSaveLayout}
              className="text-xs bg-blue-600 text-white px-2 py-1 rounded hover:bg-blue-700 flex items-center gap-1"
              title="Save current layout"
            >
              <Save className="w-3 h-3" />
              Save Layout
            </button>
          </div>
          
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-green-400 rounded-full"></div>
            <span className="text-xs text-gray-400">Confidence: 0.92</span>
          </div>
          <div className="flex items-center gap-2">
            <Brain className="w-4 h-4 text-purple-400" />
            <span className="text-xs text-gray-400">Consciousness: Active</span>
          </div>
        </div>
      </div>

      {/* Main Layout */}
      <PanelGroup direction="vertical" className="flex-1">
        {/* Content Area */}
        <Panel defaultSize={bottomDrawerOpen ? 75 : 100} minSize={50}>
          <PanelGroup direction="horizontal" className="h-full">
            {/* Left Drawer */}
            <Panel defaultSize={20} minSize={15} maxSize={30}>
              <div className="h-full bg-gray-800 border-r border-gray-700 flex flex-col">
                {/* Left Drawer Header */}
                <div className="h-10 bg-gray-750 border-b border-gray-700 flex items-center px-3 gap-2">
                  <span className="text-xs font-semibold text-gray-300">SYSTEM NAVIGATION</span>
                </div>
                
                {/* Left Drawer Tabs */}
                <div className="flex border-b border-gray-700 overflow-x-auto">
                  {leftPanelButtons.slice(0, 5).map(panel => (
                    <button
                      key={panel.id}
                      onClick={(e) => {
                        e.preventDefault()
                        e.stopPropagation()
                        console.log('[AETHER] Button clicked directly:', panel.id)
                        handlePanelToggle(panel.id)
                      }}
                      onMouseDown={(e) => {
                        e.preventDefault()
                        console.log('[AETHER] Button mousedown:', panel.id)
                      }}
                      className={`flex-1 px-3 py-2 text-xs font-medium transition-colors whitespace-nowrap cursor-pointer ${
                        activeLeftPanel === panel.id && panel.visible
                          ? 'bg-gray-700 text-blue-400 border-b-2 border-blue-400'
                          : panel.visible
                          ? 'bg-gray-750 text-gray-300'
                          : 'text-gray-400 hover:text-gray-200 hover:bg-gray-750'
                      }`}
                      style={{ pointerEvents: 'auto', zIndex: 10 }}
                    >
                      {PANEL_ICONS[panel.id]}
                      {PANEL_LABELS[panel.id]}
                    </button>
                  ))}
                </div>
                
                {/* AIM-OS Structure Tabs */}
                <div className="flex flex-wrap border-b border-gray-700 bg-gray-750">
                  {leftPanelButtons.slice(5).map(panel => (
                    <button
                      key={panel.id}
                      onClick={(e) => {
                        e.preventDefault()
                        e.stopPropagation()
                        console.log('[AETHER] Button clicked directly:', panel.id)
                        handlePanelToggle(panel.id)
                      }}
                      className={`px-2 py-1 text-xs font-medium transition-colors cursor-pointer ${
                        activeLeftPanel === panel.id && panel.visible
                          ? 'bg-gray-700 text-purple-400 border-b-2 border-purple-400'
                          : 'text-gray-400 hover:text-gray-200 hover:bg-gray-700'
                      }`}
                      style={{ pointerEvents: 'auto', zIndex: 10 }}
                    >
                      {PANEL_ICONS[panel.id]}
                      {PANEL_LABELS[panel.id]}
                    </button>
                  ))}
                </div>
                
                {/* Left Panel Content */}
                <div className="flex-1 overflow-auto">
                  {(() => {
                    const activePanel = activeLeftPanel ? panels[activeLeftPanel] : null
                    console.log('[AETHER] Rendering left panel:', {
                      activeLeftPanel,
                      panel: activePanel,
                      visible: activePanel?.visible,
                      allLeftPanels: leftPanels.map(p => ({ id: p.id, visible: p.visible }))
                    })
                    
                    if (activeLeftPanel && activePanel?.visible) {
                      return (
                        <PanelErrorBoundary key={activeLeftPanel} panelId={activeLeftPanel}>
                          <PanelSuspense panelId={activeLeftPanel}>
                            {renderPanel(activeLeftPanel)}
                          </PanelSuspense>
                        </PanelErrorBoundary>
                      )
                    } else {
                      return (
                        <LoadingPanel 
                          panelId={activeLeftPanel || undefined} 
                          message={activeLeftPanel ? `Panel ${activeLeftPanel} visible=${activePanel?.visible}` : "No panel selected"} 
                        />
                      )
                    }
                  })()}
                </div>
              </div>
            </Panel>

            <PanelResizeHandle className="w-1 bg-gray-700 hover:bg-gray-600 transition-colors" />

            {/* Main Content Area */}
            <Panel defaultSize={60} minSize={40}>
              <div className="h-full bg-gray-900 flex flex-col">
                {/* Main Content Tabs */}
                <div className="h-10 bg-gray-800 border-b border-gray-700 flex items-center gap-1 px-2 overflow-x-auto">
                  {mainPanelButtons.map(panel => (
                    <button
                      key={panel.id}
                      onClick={(e) => {
                        e.preventDefault()
                        e.stopPropagation()
                        console.log('[AETHER] Button clicked directly:', panel.id)
                        handlePanelToggle(panel.id)
                      }}
                      className={`px-3 py-1 text-xs font-medium rounded-t transition-colors whitespace-nowrap cursor-pointer ${
                        activeMainPanel === panel.id && panel.visible
                          ? 'bg-gray-900 text-blue-400'
                          : panel.visible
                          ? 'bg-gray-800 text-gray-300'
                          : 'text-gray-400 hover:text-gray-200'
                      }`}
                      style={{ pointerEvents: 'auto', zIndex: 10 }}
                    >
                      {PANEL_ICONS[panel.id]}
                      {PANEL_LABELS[panel.id]}
                    </button>
                  ))}
                </div>
                
                {/* Main Content */}
                <div className="flex-1 overflow-auto">
                  {activeMainPanel && panels[activeMainPanel]?.visible ? (
                    <PanelErrorBoundary key={activeMainPanel} panelId={activeMainPanel}>
                      <PanelSuspense panelId={activeMainPanel}>
                        {renderPanel(activeMainPanel)}
                      </PanelSuspense>
                    </PanelErrorBoundary>
                  ) : (
                    <LoadingPanel panelId={activeMainPanel || undefined} message="No panel selected" />
                  )}
                </div>
              </div>
            </Panel>

            <PanelResizeHandle className="w-1 bg-gray-700 hover:bg-gray-600 transition-colors" />

            {/* Right Drawer */}
            <Panel defaultSize={20} minSize={15} maxSize={30}>
              <div className="h-full bg-gray-800 border-l border-gray-700 flex flex-col">
                {/* Right Drawer Header */}
                <div className="h-10 bg-gray-750 border-b border-gray-700 flex items-center px-3 gap-2">
                  <span className="text-xs font-semibold text-gray-300">CONTEXT & EVIDENCE</span>
                </div>
                
                {/* Right Drawer Tabs */}
                <div className="flex flex-wrap border-b border-gray-700 overflow-x-auto">
                  {rightPanelButtons.map(panel => (
                    <button
                      key={panel.id}
                      onClick={(e) => {
                        e.preventDefault()
                        e.stopPropagation()
                        console.log('[AETHER] Button clicked directly:', panel.id)
                        handlePanelToggle(panel.id)
                      }}
                      className={`px-3 py-2 text-xs font-medium transition-colors whitespace-nowrap cursor-pointer ${
                        activeRightPanel === panel.id && panel.visible
                          ? 'bg-gray-700 text-blue-400 border-b-2 border-blue-400'
                          : panel.visible
                          ? 'bg-gray-750 text-gray-300'
                          : 'text-gray-400 hover:text-gray-200 hover:bg-gray-750'
                      }`}
                      style={{ pointerEvents: 'auto', zIndex: 10 }}
                    >
                      {PANEL_ICONS[panel.id]}
                      {PANEL_LABELS[panel.id]}
                    </button>
                  ))}
                </div>
                
                {/* Right Panel Content */}
                <div className="flex-1 overflow-auto">
                  {activeRightPanel && panels[activeRightPanel]?.visible ? (
                    <PanelErrorBoundary key={activeRightPanel} panelId={activeRightPanel}>
                      <PanelSuspense panelId={activeRightPanel}>
                        {renderPanel(activeRightPanel)}
                      </PanelSuspense>
                    </PanelErrorBoundary>
                  ) : (
                    <LoadingPanel panelId={activeRightPanel || undefined} message="No panel selected" />
                  )}
                </div>
              </div>
            </Panel>
          </PanelGroup>
        </Panel>

        {/* Bottom Drawer */}
        {bottomDrawerOpen && (
          <>
            <PanelResizeHandle className="h-1 bg-gray-700 hover:bg-gray-600 transition-colors" />
            <Panel defaultSize={25} minSize={15} maxSize={50}>
              <div className="h-full bg-gray-800 border-t border-gray-700 flex flex-col">
                {/* Bottom Drawer Tabs */}
                <div className="h-10 bg-gray-750 border-b border-gray-700 flex items-center gap-1 px-2">
                  {bottomPanelButtons.map(panel => (
                    <button
                      key={panel.id}
                      onClick={(e) => {
                        e.preventDefault()
                        e.stopPropagation()
                        console.log('[AETHER] Button clicked directly:', panel.id)
                        handlePanelToggle(panel.id)
                      }}
                      className={`px-3 py-1 text-xs font-medium rounded-t transition-colors cursor-pointer ${
                        activeBottomPanel === panel.id && panel.visible
                          ? 'bg-gray-800 text-blue-400'
                          : 'text-gray-400 hover:text-gray-200'
                      }`}
                      style={{ pointerEvents: 'auto', zIndex: 10 }}
                    >
                      {PANEL_ICONS[panel.id]}
                      {PANEL_LABELS[panel.id]}
                    </button>
                  ))}
                  <button
                    onClick={(e) => {
                      e.preventDefault()
                      e.stopPropagation()
                      handleHideBottomDrawer()
                    }}
                    className="ml-auto px-2 py-1 text-xs text-gray-400 hover:text-gray-200 cursor-pointer"
                  >
                    Hide
                  </button>
                </div>
                
                {/* Bottom Panel Content */}
                <div className="flex-1 overflow-auto">
                  {activeBottomPanel && panels[activeBottomPanel]?.visible ? (
                    <PanelErrorBoundary key={activeBottomPanel} panelId={activeBottomPanel}>
                      <PanelSuspense panelId={activeBottomPanel}>
                        {renderPanel(activeBottomPanel)}
                      </PanelSuspense>
                    </PanelErrorBoundary>
                  ) : (
                    <LoadingPanel panelId={activeBottomPanel || undefined} message="No panel selected" />
                  )}
                </div>
              </div>
            </Panel>
          </>
        )}
      </PanelGroup>
    </div>
  )
}
