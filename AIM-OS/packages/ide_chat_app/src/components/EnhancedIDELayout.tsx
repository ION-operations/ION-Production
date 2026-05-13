import React, { useState } from 'react'
import { LucidMonacoEditor } from './LucidMonacoEditor'
import { LucidOrchestratorPanel } from './LucidOrchestratorPanel'
import { EditorTabs } from './EditorTabs'
import { FileTree } from './FileTree'
import { ContextExplorer } from './ContextExplorer'
import { AIAgentChat } from './AIAgentChat'
import { EnhancedAIChat } from './EnhancedAIChat'
import { AIMOSOrchestration } from './AIMOSOrchestration'
import { WorkflowManager } from './WorkflowManager'
import { TerminalPanel } from './TerminalPanel'
import { CodeDocsViewer } from './CodeDocsViewer'
import { ThreePanelCodeViewer } from './ThreePanelCodeViewer'
import { SystemMonitor } from './SystemMonitor'
import { MemoryBrowserEnhanced } from './MemoryBrowserEnhanced'
import { TimelineVisualization } from './TimelineVisualization'
import { CommandPalette } from './CommandPalette'
import { AIMOSIntegration } from './AIMOSIntegration'
import { SystemStatusDashboard } from './SystemStatusDashboard'
import { AIAgentCoordination } from './AIAgentCoordination'
import { ConsciousnessExplorer } from './ConsciousnessExplorer'
import { ToolQualityDashboard } from './ToolQualityDashboard'
import { LucidOrchestratorMain } from './LucidOrchestratorMain'
import { LucidTimelineDrawer } from './LucidTimelineDrawer'
import { ChatInterfaceCoding } from './chats/ChatInterfaceCoding'
import { ChatInterfacePlanning } from './chats/ChatInterfacePlanning'
import { CodingAgentProvider } from '../contexts/CodingAgentContext'
import { PlanningAgentProvider } from '../contexts/PlanningAgentContext'
import { useEditorStore } from '../store/editorStore'
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels'
import { ChatBridgeIndicator } from './ChatBridgeIndicator'
import {
  FolderOpen,
  Code,
  Eye,
  GitBranch,
  Sparkles,
  BookOpen,
  Database,
  Monitor,
  Network,
  Workflow,
  BarChart3,
  Terminal,
  Calendar,
  Clock,
  AlertTriangle,
  Layers,
  Brain,
  Activity,
  Users,
  Zap
} from 'lucide-react'

interface EnhancedIDELayoutProps {
  theme?: string
}

type LeftPanelType = 'explorer' | 'memory' | 'monitor' | 'dashboard' | 'aimos' | 'status' | 'consciousness' | 'tool-quality' | 'lucid-intelligence' | null
type RightPanelType = 'outline' | 'search' | 'context' | 'coding' | 'planning' | 'workflows' | 'coordination' | null
type MainPageType = 'code' | 'preview' | 'ui' | 'backend' | 'orchestration' | 'code-docs' | 'three-panel' | 'lucid-orchestrator'
type BottomDrawerType = 'terminal' | 'timeline' | 'lucid-timeline' | 'problems' | null

export const EnhancedIDELayout: React.FC<EnhancedIDELayoutProps> = () => {
  const { activeTabId, tabs, updateTabContent } = useEditorStore()
  
  // Main page state
  const [mainPage, setMainPage] = useState<MainPageType>('code-docs')
  
  // Left side split panels
  const [leftTopPanel, setLeftTopPanel] = useState<LeftPanelType>('explorer')
  const [leftBottomPanel, setLeftBottomPanel] = useState<LeftPanelType>('lucid-intelligence')
  
  // Right side split panels (both AI chats here)
  const [rightTopPanel, setRightTopPanel] = useState<RightPanelType>('planning')
  const [rightBottomPanel, setRightBottomPanel] = useState<RightPanelType>('coding')
  
  // Bottom drawer state
  const [bottomDrawerOpen, setBottomDrawerOpen] = useState(false)
  const [bottomDrawerPage, setBottomDrawerPage] = useState<BottomDrawerType>('terminal')
  
  // Hover state for split buttons
  const [hoveredIcon, setHoveredIcon] = useState<string | null>(null)
  
  // Lucid Orchestrator state
  const [selectedNodeId, setSelectedNodeId] = useState<string | undefined>()

  const activeTab = tabs.find(t => t.id === activeTabId)

  const sampleCode = `// Welcome to AIM-OS IDE with Lucid Orchestrator! 🚀
import { useState, useEffect } from 'react'

export const Example: React.FC = () => {
  const [count, setCount] = useState(0)
  
  useEffect(() => {
    console.log('Component mounted')
  }, [])
  
  return (
    <div className="example">
      <h1>Count: {count}</h1>
      <button onClick={() => setCount(count + 1)}>
        Increment
      </button>
    </div>
  )
}

// This function will show Lucid intelligence
export async function fetchUserData(userId: string) {
  const response = await fetch(\`/api/users/\${userId}\`)
  return response.json()
}

// React component with intelligence
export const UserProfile: React.FC<{ userId: string }> = ({ userId }) => {
  const [user, setUser] = useState(null)
  
  useEffect(() => {
    fetchUserData(userId).then(setUser)
  }, [userId])
  
  return (
    <div>
      {user ? <h2>{user.name}</h2> : <div>Loading...</div>}
    </div>
  )
}`

  const handleNodeSelect = (nodeId: string) => {
    setSelectedNodeId(nodeId)
  }

  const renderMainContent = () => {
    switch (mainPage) {
      case 'code':
        return (
          <LucidMonacoEditor
            value={activeTab?.content || sampleCode}
            language="typescript"
            fileName={activeTab?.name || 'example.tsx'}
            enableLucidFolds={true}
            onChange={(value) => {
              if (activeTabId) {
                updateTabContent(activeTabId, value || '')
              }
            }}
          />
        )
      case 'lucid-orchestrator':
        return <LucidOrchestratorMain />
      case 'code-docs':
        return <CodeDocsViewer />
      case 'three-panel':
        return <ThreePanelCodeViewer />
      default:
        return (
          <LucidMonacoEditor
            value={activeTab?.content || sampleCode}
            language="typescript"
            fileName={activeTab?.name || 'example.tsx'}
            enableLucidFolds={true}
            onChange={(value) => {
              if (activeTabId) {
                updateTabContent(activeTabId, value || '')
              }
            }}
          />
        )
    }
  }

  const renderLeftPanel = (panelType: LeftPanelType) => {
    switch (panelType) {
      case 'explorer':
        return <FileTree />
      case 'memory':
        return <MemoryBrowserEnhanced />
      case 'monitor':
        return <SystemMonitor />
      case 'dashboard':
        return <SystemStatusDashboard />
      case 'aimos':
        return <AIMOSIntegration />
      case 'status':
        return <SystemStatusDashboard />
      case 'consciousness':
        return <ConsciousnessExplorer />
      case 'tool-quality':
        return <ToolQualityDashboard />
      case 'lucid-intelligence':
        return (
          <LucidOrchestratorPanel
            nodeId={selectedNodeId}
            onNodeFocus={handleNodeSelect}
          />
        )
      default:
        return null
    }
  }

  const renderRightPanel = (panelType: RightPanelType) => {
    switch (panelType) {
      case 'outline':
        return <ContextExplorer />
      case 'search':
        return <ContextExplorer />
      case 'context':
        return <ContextExplorer />
      case 'coding':
        return (
          <CodingAgentProvider>
                            <ChatInterfaceCoding />
                          </CodingAgentProvider>
                        )
      case 'planning':
        return (
          <PlanningAgentProvider>
                            <ChatInterfacePlanning />
                          </PlanningAgentProvider>
                        )
      case 'workflows':
        return <WorkflowManager />
      case 'coordination':
        return <AIAgentCoordination />
      default:
        return null
    }
  }

  const renderBottomDrawer = () => {
    if (!bottomDrawerOpen) return null

    switch (bottomDrawerPage) {
      case 'terminal':
        return <TerminalPanel />
      case 'timeline':
        return <TimelineVisualization />
      case 'lucid-timeline':
        return <LucidTimelineDrawer />
      case 'problems':
        return <div className="p-4 text-gray-400">Problems panel</div>
      default:
        return null
    }
  }

  const leftPanelButtons = [
    { id: 'explorer', icon: FolderOpen, label: 'Explorer' },
    { id: 'memory', icon: Database, label: 'Memory' },
    { id: 'monitor', icon: Monitor, label: 'Monitor' },
    { id: 'dashboard', icon: BarChart3, label: 'Dashboard' },
    { id: 'aimos', icon: Brain, label: 'AIMOS' },
    { id: 'status', icon: Activity, label: 'Status' },
    { id: 'consciousness', icon: Layers, label: 'Consciousness' },
    { id: 'tool-quality', icon: AlertTriangle, label: 'Tool Quality' },
    { id: 'lucid-intelligence', icon: Zap, label: 'Lucid Intelligence' }
  ]

  const rightPanelButtons = [
    { id: 'outline', icon: BookOpen, label: 'Outline' },
    { id: 'search', icon: Code, label: 'Search' },
    { id: 'context', icon: Eye, label: 'Context' },
    { id: 'coding', icon: Code, label: 'Coding' },
    { id: 'planning', icon: Calendar, label: 'Planning' },
    { id: 'workflows', icon: Workflow, label: 'Workflows' },
    { id: 'coordination', icon: Users, label: 'Coordination' }
  ]

  const mainPageButtons = [
    { id: 'code', icon: Code, label: 'Code' },
    { id: 'preview', icon: Eye, label: 'Preview' },
    { id: 'ui', icon: Sparkles, label: 'UI' },
    { id: 'backend', icon: Database, label: 'Backend' },
    { id: 'orchestration', icon: Workflow, label: 'Orchestration' },
    { id: 'code-docs', icon: BookOpen, label: 'Code Docs' },
    { id: 'three-panel', icon: Layers, label: 'Three Panel' },
    { id: 'lucid-orchestrator', icon: Zap, label: 'Lucid Orchestrator' }
  ]

  const bottomDrawerButtons = [
    { id: 'terminal', icon: Terminal, label: 'Terminal' },
    { id: 'timeline', icon: Clock, label: 'Timeline' },
    { id: 'lucid-timeline', icon: GitBranch, label: 'Lucid Timeline' },
    { id: 'problems', icon: AlertTriangle, label: 'Problems' }
  ]

  return (
    <div className="h-screen bg-gray-900 text-white flex flex-col">
      {/* Top Navigation */}
      <div className="flex items-center justify-between px-4 py-2 bg-gray-800 border-b border-gray-700">
        <div className="flex items-center gap-4">
          <h1 className="text-lg font-semibold">AIM-OS IDE with Lucid Orchestrator</h1>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-green-400 rounded-full" />
            <span className="text-xs text-gray-400">Lucid Intelligence Active</span>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <ChatBridgeIndicator />
          <CommandPalette />
        </div>
      </div>

      {/* Main Layout */}
      <div className="flex-1 flex">
        {/* Left Sidebar */}
        <div className="w-12 bg-gray-800 border-r border-gray-700 flex flex-col">
          <div className="flex-1 py-2 space-y-1">
            {leftPanelButtons.map(({ id, icon: Icon, label }) => (
              <button
                key={id}
                onClick={() => {
                  if (leftTopPanel === id) {
                    setLeftTopPanel(null)
                  } else {
                    setLeftTopPanel(id as LeftPanelType)
                  }
                }}
                onMouseEnter={() => setHoveredIcon(id)}
                onMouseLeave={() => setHoveredIcon(null)}
                className={`w-10 h-10 flex items-center justify-center rounded transition-colors ${
                  leftTopPanel === id
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-400 hover:text-white hover:bg-gray-700'
                }`}
                title={label}
              >
                <Icon className="w-5 h-5" />
              </button>
            ))}
          </div>
        </div>

        {/* Main Content Area */}
        <PanelGroup direction="horizontal" className="flex-1">
          {/* Left Panel */}
          {leftTopPanel && (
            <>
              <Panel defaultSize={25} minSize={20} maxSize={40}>
                <div className="h-full bg-gray-800 border-r border-gray-700">
                  {renderLeftPanel(leftTopPanel)}
                </div>
              </Panel>
              <PanelResizeHandle className="w-1 bg-gray-600 hover:bg-gray-500" />
            </>
          )}

          {/* Center Content */}
          <Panel defaultSize={leftTopPanel ? 50 : 75} minSize={30}>
            <div className="h-full flex flex-col">
              {/* Editor Tabs */}
              <EditorTabs />
              
              {/* Main Content */}
              <div className="flex-1">
                {renderMainContent()}
              </div>
            </div>
          </Panel>

          {/* Right Panel */}
          {rightTopPanel && (
            <>
              <PanelResizeHandle className="w-1 bg-gray-600 hover:bg-gray-500" />
              <Panel defaultSize={25} minSize={20} maxSize={40}>
                <div className="h-full bg-gray-800 border-l border-gray-700">
                  {renderRightPanel(rightTopPanel)}
                </div>
              </Panel>
            </>
          )}
        </PanelGroup>

        {/* Right Sidebar */}
        <div className="w-12 bg-gray-800 border-l border-gray-700 flex flex-col">
          <div className="flex-1 py-2 space-y-1">
            {rightPanelButtons.map(({ id, icon: Icon, label }) => (
              <button
                key={id}
                onClick={() => {
                  if (rightTopPanel === id) {
                    setRightTopPanel(null)
                  } else {
                    setRightTopPanel(id as RightPanelType)
                  }
                }}
                onMouseEnter={() => setHoveredIcon(id)}
                onMouseLeave={() => setHoveredIcon(null)}
                className={`w-10 h-10 flex items-center justify-center rounded transition-colors ${
                  rightTopPanel === id
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-400 hover:text-white hover:bg-gray-700'
                }`}
                title={label}
              >
                <Icon className="w-5 h-5" />
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Bottom Drawer */}
      {bottomDrawerOpen && (
        <div className="h-64 bg-gray-800 border-t border-gray-700">
          {renderBottomDrawer()}
        </div>
      )}

      {/* Bottom Toolbar */}
      <div className="flex items-center justify-between px-4 py-2 bg-gray-800 border-t border-gray-700">
        <div className="flex items-center gap-4">
          {mainPageButtons.map(({ id, icon: Icon, label }) => (
            <button
              key={id}
              onClick={() => setMainPage(id as MainPageType)}
              className={`px-3 py-1 rounded text-sm transition-colors ${
                mainPage === id
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-400 hover:text-white hover:bg-gray-700'
              }`}
            >
              <Icon className="w-4 h-4 inline mr-1" />
              {label}
            </button>
          ))}
        </div>
        
        <div className="flex items-center gap-2">
          {bottomDrawerButtons.map(({ id, icon: Icon, label }) => (
            <button
              key={id}
              onClick={() => {
                if (bottomDrawerOpen && bottomDrawerPage === id) {
                  setBottomDrawerOpen(false)
                } else {
                  setBottomDrawerOpen(true)
                  setBottomDrawerPage(id as BottomDrawerType)
                }
              }}
              className={`px-3 py-1 rounded text-sm transition-colors ${
                bottomDrawerOpen && bottomDrawerPage === id
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-400 hover:text-white hover:bg-gray-700'
              }`}
            >
              <Icon className="w-4 h-4 inline mr-1" />
              {label}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
