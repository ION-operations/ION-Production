// Core Layout Component - FIXED VERSION
import React from 'react'
import { PanelGroup, Panel, PanelResizeHandle } from 'react-resizable-panels'
import { useLayoutStore } from '@/store/layoutStore'
import { FileExplorer } from '@/components/panels/FileExplorer'
import { CodeEditor } from '@/components/panels/CodeEditor'
import { CodingChat } from '@/components/panels/CodingChat'
import { Terminal } from '@/components/panels/Terminal'
import { ContextWeb } from '@/components/panels/ContextWeb'
import { MemoryBrowser } from '@/components/panels/MemoryBrowser'
import { SystemMonitor } from '@/components/panels/SystemMonitor'
import { Timeline } from '@/components/panels/Timeline'
import { PDASPanel } from '@/components/panels/PDASPanel'
import { AgentManagement } from '@/components/panels/AgentManagement'
import { ProblemsPanel } from '@/components/panels/ProblemsPanel'
import { EvolutionExplorer } from '@/components/panels/EvolutionExplorer'
import { PlanningChat } from '@/components/panels/PlanningChat'
import { SearchPanel } from '@/components/panels/SearchPanel'
import { OutlinePanel } from '@/components/panels/OutlinePanel'
import { PropertiesPanel } from '@/components/panels/PropertiesPanel'
import { GitPanel } from '@/components/panels/GitPanel'
import { ComponentLibrary } from '@/components/panels/ComponentLibrary'
import { DocumentationViewer } from '@/components/panels/DocumentationViewer'
import { UIEditor } from '@/components/panels/UIEditor'
import { LayoutManager } from '@/components/LayoutManager'
import { PanelIconBar } from '@/components/PanelIconBar'
import { PanelTabBar } from '@/components/PanelTabBar'
import { PanelType } from '@/types'

const PanelComponentMap: Record<PanelType, React.ComponentType<any>> = {
  'file-explorer': FileExplorer,
  'memory-browser': MemoryBrowser,
  'system-monitor': SystemMonitor,
  'agent-management': AgentManagement,
  'component-library': ComponentLibrary,
  'code-editor': CodeEditor,
  'context-web': ContextWeb,
  'evolution-explorer': EvolutionExplorer,
  'documentation-viewer': DocumentationViewer,
  'ui-editor': UIEditor,
  'coding-chat': CodingChat,
  'planning-chat': PlanningChat,
  'outline-panel': OutlinePanel,
  'properties-panel': PropertiesPanel,
  'search-panel': SearchPanel,
  'terminal': Terminal,
  'timeline': Timeline,
  'problems': ProblemsPanel,
  'debug-console': PDASPanel,
  'git-panel': GitPanel,
}

export const IDELayout: React.FC = () => {
  const { panels, activePanels } = useLayoutStore()

  const leftPanels = panels.filter((p) => p.zone === 'left').sort((a, b) => a.order - b.order)
  const mainPanels = panels.filter((p) => p.zone === 'main').sort((a, b) => a.order - b.order)
  const rightPanels = panels.filter((p) => p.zone === 'right').sort((a, b) => a.order - b.order)
  const bottomPanels = panels.filter((p) => p.zone === 'bottom').sort((a, b) => a.order - b.order)

  // Get active panel for each zone
  const activeLeftPanel = leftPanels.find((p) => p.id === activePanels?.left)
  const activeMainPanel = mainPanels.find((p) => p.id === activePanels?.main)
  const activeRightPanel = rightPanels.find((p) => p.id === activePanels?.right)
  const activeBottomPanel = bottomPanels.find((p) => p.id === activePanels?.bottom)

  // Fixed sizes that total exactly 100%
  const LEFT_SIZE = 20
  const RIGHT_SIZE = 20
  const MAIN_SIZE = 60

  return (
    <div style={{ width: '100vw', height: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: '#111827' }}>
      {/* Top Bar */}
      <div style={{ height: '40px', borderBottom: '1px solid #374151', display: 'flex', alignItems: 'center', padding: '0 16px', backgroundColor: '#1F2937', flexShrink: 0 }}>
        <span style={{ color: '#F9FAFB', fontWeight: 'bold', fontSize: '14px' }}>AIM-OS IDE Prototype - Lex</span>
        <span style={{ color: '#9CA3AF', fontSize: '12px', marginLeft: '16px' }}>Port: 3004</span>
      </div>

      {/* Layout Manager */}
      <LayoutManager />

      {/* Main Layout - Vertical PanelGroup */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', minHeight: 0 }}>
        <PanelGroup direction="vertical" style={{ flex: 1 }}>
          {/* Main horizontal area - WRAP IN PANEL */}
          <Panel defaultSize={bottomPanels.length > 0 ? 80 : 100} minSize={50} maxSize={100}>
            <PanelGroup direction="horizontal" style={{ width: '100%', height: '100%' }}>
              {/* Left Panel - ALWAYS RENDER */}
              <Panel defaultSize={LEFT_SIZE} minSize={15} maxSize={30} collapsible={true}>
                <div style={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'row', backgroundColor: '#1F2937' }}>
                  <PanelIconBar zone="left" panels={leftPanels} />
                  {activeLeftPanel && (
                    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', minWidth: 0 }}>
                      {(() => {
                        const Component = PanelComponentMap[activeLeftPanel.type]
                        return Component ? <Component key={activeLeftPanel.id} panel={activeLeftPanel} /> : null
                      })()}
                    </div>
                  )}
                </div>
              </Panel>
              <PanelResizeHandle style={{ width: '4px', backgroundColor: '#374151', cursor: 'col-resize' }} />

              {/* Main Panel - ALWAYS RENDER */}
              <Panel defaultSize={MAIN_SIZE} minSize={40} maxSize={80}>
                <div style={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column', backgroundColor: '#111827', overflow: 'hidden' }}>
                  <PanelTabBar zone="main" panels={mainPanels} />
                  {activeMainPanel && (
                    <div style={{ flex: 1, overflow: 'hidden', minHeight: 0 }}>
                      {(() => {
                        const Component = PanelComponentMap[activeMainPanel.type]
                        return Component ? <Component key={activeMainPanel.id} panel={activeMainPanel} /> : null
                      })()}
                    </div>
                  )}
                </div>
              </Panel>
              <PanelResizeHandle style={{ width: '4px', backgroundColor: '#374151', cursor: 'col-resize' }} />

              {/* Right Panel - ALWAYS RENDER */}
              <Panel defaultSize={RIGHT_SIZE} minSize={15} maxSize={30} collapsible={true}>
                <div style={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'row', backgroundColor: '#1F2937' }}>
                  {activeRightPanel && (
                    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', minWidth: 0 }}>
                      {(() => {
                        const Component = PanelComponentMap[activeRightPanel.type]
                        return Component ? <Component key={activeRightPanel.id} panel={activeRightPanel} /> : null
                      })()}
                    </div>
                  )}
                  <PanelIconBar zone="right" panels={rightPanels} />
                </div>
              </Panel>
            </PanelGroup>
          </Panel>

          {/* Bottom Panel - ALWAYS RENDER but can be collapsed */}
          {bottomPanels.length > 0 && (
            <>
              <PanelResizeHandle style={{ height: '4px', backgroundColor: '#374151', cursor: 'row-resize' }} />
              <Panel defaultSize={20} minSize={10} maxSize={50} collapsible={true}>
                <div style={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column', backgroundColor: '#111827', overflow: 'hidden' }}>
                  <PanelTabBar zone="bottom" panels={bottomPanels} />
                  {activeBottomPanel && (
                    <div style={{ flex: 1, overflow: 'hidden', minHeight: 0 }}>
                      {(() => {
                        const Component = PanelComponentMap[activeBottomPanel.type]
                        return Component ? <Component key={activeBottomPanel.id} panel={activeBottomPanel} /> : null
                      })()}
                    </div>
                  )}
                </div>
              </Panel>
            </>
          )}
        </PanelGroup>
      </div>
    </div>
  )
}
