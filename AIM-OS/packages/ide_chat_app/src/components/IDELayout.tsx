import React, { useState } from 'react'
import { MonacoEditor } from './MonacoEditor'
import { LucidMonacoEditor } from './LucidMonacoEditor'
import { ConsciousnessAwareEditor } from './ConsciousnessAwareEditor'
import { TemporalNavigationBar } from './TemporalNavigationBar'
import { LucidOrchestratorPanel } from './LucidOrchestratorPanel'
import * as sampleCodeModule from '../sampleCode'
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
import { DebugConsole } from './DebugConsole'
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
  Zap,
  Bug
} from 'lucide-react'

interface IDELayoutProps {
  theme?: string
}

type LeftPanelType = 'explorer' | 'memory' | 'monitor' | 'dashboard' | 'aimos' | 'status' | 'consciousness' | 'tool-quality' | 'lucid-intelligence' | null
type RightPanelType = 'outline' | 'search' | 'context' | 'coding' | 'planning' | 'workflows' | 'coordination' | null
type MainPageType = 'code' | 'preview' | 'ui' | 'backend' | 'orchestration' | 'code-docs' | 'three-panel' | 'lucid-orchestrator' | 'consciousness-aware'
type BottomDrawerType = 'terminal' | 'timeline' | 'lucid-timeline' | 'problems' | 'debug' | null

export const IDELayout: React.FC<IDELayoutProps> = () => {
  const { activeTabId, tabs, updateTabContent } = useEditorStore()
  
  // Main page state
  const [mainPage, setMainPage] = useState<MainPageType>('code-docs')
  
  // Left side split panels
  const [leftTopPanel, setLeftTopPanel] = useState<LeftPanelType>('explorer')
  const [leftBottomPanel, setLeftBottomPanel] = useState<LeftPanelType>(null)
  
  // Right side split panels (both AI chats here)
  const [rightTopPanel, setRightTopPanel] = useState<RightPanelType>('planning')
  const [rightBottomPanel, setRightBottomPanel] = useState<RightPanelType>('coding')
  
  // Bottom drawer state
  const [bottomDrawerOpen, setBottomDrawerOpen] = useState(true)
  const [bottomDrawerPage, setBottomDrawerPage] = useState<BottomDrawerType>('terminal')
  
  // Hover state for split buttons
  const [hoveredIcon, setHoveredIcon] = useState<string | null>(null)

  const activeTab = tabs.find(t => t.id === activeTabId)

  const sampleCode = `// Welcome to AIM-OS IDE! ðŸš€
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
}`

  // Render panel content
  const renderPanelContent = (panel: LeftPanelType | RightPanelType, side: 'left' | 'right') => {
    if (side === 'left') {
      switch (panel) {
        case 'explorer': return <FileTree />
        case 'memory': return <MemoryBrowserEnhanced />
        case 'monitor': return <SystemMonitor />
        case 'dashboard': return <div className="h-full bg-gray-800 p-4 text-gray-400 text-sm">ðŸš§ AIM-OS Dashboard Coming Soon</div>
        case 'aimos': return <AIMOSIntegration />
        case 'lucid-intelligence': return <LucidOrchestratorPanel />
        case 'status': return <SystemStatusDashboard />
        case 'consciousness': return <ConsciousnessExplorer />
        case 'tool-quality': return <ToolQualityDashboard />
        default: return <div className="h-full bg-gray-800 flex items-center justify-center text-gray-500">No panel selected</div>
      }
    } else {
      switch (panel) {
        case 'outline': return <div className="h-full bg-gray-800 p-4 text-gray-400 text-sm">ðŸš§ Outline Coming Soon</div>
        case 'search': return <div className="h-full bg-gray-800 p-4 text-gray-400 text-sm">ðŸš§ Search Coming Soon</div>
        case 'context': return <ContextExplorer />
        case 'coding': return <ChatInterfaceCoding />
        case 'planning': return <ChatInterfacePlanning />
        case 'workflows': return <WorkflowManager />
        case 'coordination': return <AIAgentCoordination />
        default: return <div className="h-full bg-gray-800 flex items-center justify-center text-gray-500">No panel selected</div>
      }
    }
  }

  // Render main content
  const renderMainContent = () => {
    if (mainPage === 'code') {
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
              <LucidMonacoEditor
                value={sampleCodeModule.sampleCode}
                language="typescript"
                fileName="HttpLucidDaemonService.ts"
                onChange={() => {}}
                theme="vs-dark"
                enableLucidFolds={true}
              />
            )}
          </div>
        </div>
      )
    } else if (mainPage === 'consciousness-aware') {
      return (
        <div className="h-full flex flex-col bg-gray-900">
          {tabs.length > 0 && <EditorTabs />}
          <div className="flex-1 overflow-hidden flex flex-col">
            {activeTab ? (
              <>
                <ConsciousnessAwareEditor
                  filePath={activeTab.fileName}
                  content={activeTab.content}
                  language={activeTab.language}
                  onContentChange={(value) => updateTabContent(activeTab.id, value)}
                />
                <TemporalNavigationBar
                  filePath={activeTab.fileName}
                  currentSequence={50}
                  totalSequences={100}
                  onNavigate={(seq) => console.log('Navigate to:', seq)}
                  onPlay={() => console.log('Play')}
                  onPause={() => console.log('Pause')}
                  onReset={() => console.log('Reset')}
                  playbackSpeed={1}
                  onSpeedChange={(speed) => console.log('Speed:', speed)}
                />
              </>
            ) : (
              <>
                <ConsciousnessAwareEditor
                  filePath="HttpLucidDaemonService.ts"
                  content={sampleCodeModule.sampleCode}
                  language="typescript"
                  onContentChange={() => {}}
                />
                <TemporalNavigationBar
                  filePath="HttpLucidDaemonService.ts"
                  currentSequence={50}
                  totalSequences={100}
                  onNavigate={(seq) => console.log('Navigate to:', seq)}
                  onPlay={() => console.log('Play')}
                  onPause={() => console.log('Pause')}
                  onReset={() => console.log('Reset')}
                  playbackSpeed={1}
                  onSpeedChange={(speed) => console.log('Speed:', speed)}
                />
              </>
            )}
          </div>
        </div>
      )
    } else if (mainPage === 'code-docs') {
      return <CodeDocsViewer />
    } else if (mainPage === 'orchestration') {
      return <AIMOSOrchestration />
    } else if (mainPage === 'three-panel') {
      return <ThreePanelCodeViewer />
    } else if (mainPage === 'lucid-orchestrator') {
      return <LucidOrchestratorMain />
    } else {
      return (
        <div className="h-full flex flex-col bg-gray-900">
          <div className="flex-1 overflow-hidden">
            <LucidMonacoEditor
              value={sampleCodeModule.sampleCode}
              language="typescript"
              fileName="HttpLucidDaemonService.ts"
              onChange={() => {}}
              theme="vs-dark"
              enableLucidFolds={true}
            />
          </div>
        </div>
      )
    }
  }

  return (
    <CodingAgentProvider>
      <PlanningAgentProvider>
        <div className="flex flex-col h-screen bg-gray-900">
          <ChatBridgeIndicator
            planningActive={rightTopPanel === "planning" || rightBottomPanel === "planning"}
            codingActive={rightTopPanel === "coding" || rightBottomPanel === "coding"}
          />
      {/* Top Bar */}
      <div className="h-12 bg-gray-800 border-b border-gray-700 flex items-center px-4 gap-2">
        <span className="text-lg font-bold text-blue-400">[SAM]</span>
        <button onClick={() => setMainPage('code')} className={`flex items-center gap-2 px-4 py-2 text-sm rounded ${mainPage === 'code' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white hover:bg-gray-700'}`}>
          <Code className="w-4 h-4" />Code Editor
        </button>
        <button onClick={() => setMainPage('code-docs')} className={`flex items-center gap-2 px-4 py-2 text-sm rounded ${mainPage === 'code-docs' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white hover:bg-gray-700'}`}>
          <BookOpen className="w-4 h-4" />Code + Docs
        </button>
        <button onClick={() => setMainPage('preview')} className={`flex items-center gap-2 px-4 py-2 text-sm rounded ${mainPage === 'preview' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white hover:bg-gray-700'}`}>
          <Eye className="w-4 h-4" />Preview
        </button>
        <button onClick={() => setMainPage('orchestration')} className={`flex items-center gap-2 px-4 py-2 text-sm rounded ${mainPage === 'orchestration' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white hover:bg-gray-700'}`}>
          <GitBranch className="w-4 h-4" />Orchestration
        </button>
        <button onClick={() => setMainPage('three-panel')} className={`flex items-center gap-2 px-4 py-2 text-sm rounded ${mainPage === 'three-panel' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white hover:bg-gray-700'}`}>
          <Layers className="w-4 h-4" />Three-Panel
        </button>
        <button onClick={() => setMainPage('lucid-orchestrator')} className={`flex items-center gap-2 px-4 py-2 text-sm rounded ${mainPage === 'lucid-orchestrator' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white hover:bg-gray-700'}`}>
          <Brain className="w-4 h-4" />Lucid Orchestrator
        </button>
        <button onClick={() => setMainPage('consciousness-aware')} className={`flex items-center gap-2 px-4 py-2 text-sm rounded ${mainPage === 'consciousness-aware' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white hover:bg-gray-700'}`}>
          <Brain className="w-4 h-4" />Consciousness Editor
        </button>
      </div>

      {/* Main Layout */}
      <PanelGroup direction="vertical" className="flex-1">
        <Panel defaultSize={bottomDrawerOpen ? 85 : 100} minSize={50}>
          <div className="flex h-full overflow-hidden">
            {/* Left Icon Bar */}
            <div className="w-10 bg-gray-800 border-r border-gray-700 flex flex-col items-center py-2 gap-2">
          <button
            onMouseEnter={() => setHoveredIcon('left-explorer')}
            onMouseLeave={() => setHoveredIcon(null)}
            className="relative w-8 h-8 flex items-center justify-center text-gray-400 hover:text-white hover:bg-gray-700 rounded"
          >
            <FolderOpen className="w-5 h-5" />
            {hoveredIcon === 'left-explorer' && (
              <div className="absolute left-full ml-2 flex gap-1 z-50 bg-gray-900 border border-gray-700 rounded shadow-lg">
                <button onClick={() => {setLeftTopPanel('explorer'); setLeftBottomPanel(null)}} className="w-8 h-8 flex items-center justify-center hover:bg-gray-700">â«</button>
                <div className="w-0.5 bg-gray-700 my-1" />
                <button onClick={() => {setLeftTopPanel('explorer')}} className="w-8 h-8 flex items-center justify-center hover:bg-gray-700">â¬†ï¸</button>
                <button onClick={() => {setLeftBottomPanel('explorer')}} className="w-8 h-8 flex items-center justify-center hover:bg-gray-700">â¬‡ï¸</button>
              </div>
            )}
          </button>
          <button
            onMouseEnter={() => setHoveredIcon('left-memory')}
            onMouseLeave={() => setHoveredIcon(null)}
            className="relative w-8 h-8 flex items-center justify-center text-gray-400 hover:text-white hover:bg-gray-700 rounded"
          >
            <Database className="w-5 h-5" />
            {hoveredIcon === 'left-memory' && (
              <div className="absolute left-full ml-2 flex gap-1 z-50 bg-gray-900 border border-gray-700 rounded shadow-lg">
                <button onClick={() => {setLeftTopPanel('memory'); setLeftBottomPanel(null)}} className="w-8 h-8 flex items-center justify-center hover:bg-gray-700">â«</button>
                <div className="w-0.5 bg-gray-700 my-1" />
                <button onClick={() => {setLeftTopPanel('memory')}} className="w-8 h-8 flex items-center justify-center hover:bg-gray-700">â¬†ï¸</button>
                <button onClick={() => {setLeftBottomPanel('memory')}} className="w-8 h-8 flex items-center justify-center hover:bg-gray-700">â¬‡ï¸</button>
              </div>
            )}
          </button>
          <button
            onMouseEnter={() => setHoveredIcon('left-monitor')}
            onMouseLeave={() => setHoveredIcon(null)}
            className="relative w-8 h-8 flex items-center justify-center text-gray-400 hover:text-white hover:bg-gray-700 rounded"
          >
            <Monitor className="w-5 h-5" />
            {hoveredIcon === 'left-monitor' && (
              <div className="absolute left-full ml-2 flex gap-1 z-50 bg-gray-900 border border-gray-700 rounded shadow-lg">
                <button onClick={() => {setLeftTopPanel('monitor'); setLeftBottomPanel(null)}} className="w-8 h-8 flex items-center justify-center hover:bg-gray-700">â«</button>
                <div className="w-0.5 bg-gray-700 my-1" />
                <button onClick={() => {setLeftTopPanel('monitor')}} className="w-8 h-8 flex items-center justify-center hover:bg-gray-700">â¬†ï¸</button>
                <button onClick={() => {setLeftBottomPanel('monitor')}} className="w-8 h-8 flex items-center justify-center hover:bg-gray-700">â¬‡ï¸</button>
              </div>
            )}
          </button>
          <button
            onMouseEnter={() => setHoveredIcon('left-dashboard')}
            onMouseLeave={() => setHoveredIcon(null)}
            className="relative w-8 h-8 flex items-center justify-center text-gray-400 hover:text-white hover:bg-gray-700 rounded"
          >
            <BarChart3 className="w-5 h-5" />
            {hoveredIcon === 'left-dashboard' && (
              <div className="absolute left-full ml-2 flex gap-1 z-50 bg-gray-900 border border-gray-700 rounded shadow-lg">
                <button onClick={() => {setLeftTopPanel('dashboard'); setLeftBottomPanel(null)}} className="w-8 h-8 flex items-center justify-center hover:bg-gray-700">â«</button>
                <div className="w-0.5 bg-gray-700 my-1" />
                <button onClick={() => {setLeftTopPanel('dashboard')}} className="w-8 h-8 flex items-center justify-center hover:bg-gray-700">â¬†ï¸</button>
                <button onClick={() => {setLeftBottomPanel('dashboard')}} className="w-8 h-8 flex items-center justify-center hover:bg-gray-700">â¬‡ï¸</button>
              </div>
            )}
          </button>
          <button
            onMouseEnter={() => setHoveredIcon('left-aimos')}
            onMouseLeave={() => setHoveredIcon(null)}
            className="relative w-8 h-8 flex items-center justify-center text-gray-400 hover:text-white hover:bg-gray-700 rounded"
          >
            <Brain className="w-5 h-5" />
            {hoveredIcon === 'left-aimos' && (
              <div className="absolute left-full ml-2 flex gap-1 z-50 bg-gray-900 border border-gray-700 rounded shadow-lg">
                <button onClick={() => {setLeftTopPanel('aimos'); setLeftBottomPanel(null)}} className="w-8 h-8 flex items-center justify-center hover:bg-gray-700">â«</button>
                <div className="w-0.5 bg-gray-700 my-1" />
                <button onClick={() => {setLeftTopPanel('aimos')}} className="w-8 h-8 flex items-center justify-center hover:bg-gray-700">â¬†ï¸</button>
                <button onClick={() => {setLeftBottomPanel('aimos')}} className="w-8 h-8 flex items-center justify-center hover:bg-gray-700">â¬‡ï¸</button>
              </div>
            )}
          </button>
          <button
            onMouseEnter={() => setHoveredIcon('left-lucid')}
            onMouseLeave={() => setHoveredIcon(null)}
            className="relative w-8 h-8 flex items-center justify-center text-gray-400 hover:text-white hover:bg-gray-700 rounded"
          >
            <Zap className="w-5 h-5" />
            {hoveredIcon === 'left-lucid' && (
              <div className="absolute left-full ml-2 flex gap-1 z-50 bg-gray-900 border border-gray-700 rounded shadow-lg">
                <button onClick={() => {setLeftTopPanel('lucid-intelligence'); setLeftBottomPanel(null)}} className="w-8 h-8 flex items-center justify-center hover:bg-gray-700">⚡</button>
                <div className="w-0.5 bg-gray-700 my-1" />
                <button onClick={() => {setLeftTopPanel('lucid-intelligence')}} className="w-8 h-8 flex items-center justify-center hover:bg-gray-700">⬆️</button>
                <button onClick={() => {setLeftBottomPanel('lucid-intelligence')}} className="w-8 h-8 flex items-center justify-center hover:bg-gray-700">⬇️</button>
              </div>
            )}
          </button>
          <button
            onMouseEnter={() => setHoveredIcon('left-status')}
            onMouseLeave={() => setHoveredIcon(null)}
            className="relative w-8 h-8 flex items-center justify-center text-gray-400 hover:text-white hover:bg-gray-700 rounded"
          >
            <Activity className="w-5 h-5" />
            {hoveredIcon === 'left-status' && (
              <div className="absolute left-full ml-2 flex gap-1 z-50 bg-gray-900 border border-gray-700 rounded shadow-lg">
                <button onClick={() => {setLeftTopPanel('status'); setLeftBottomPanel(null)}} className="w-8 h-8 flex items-center justify-center hover:bg-gray-700">â«</button>
                <div className="w-0.5 bg-gray-700 my-1" />
                <button onClick={() => {setLeftTopPanel('status')}} className="w-8 h-8 flex items-center justify-center hover:bg-gray-700">â¬†ï¸</button>
                <button onClick={() => {setLeftBottomPanel('status')}} className="w-8 h-8 flex items-center justify-center hover:bg-gray-700">â¬‡ï¸</button>
              </div>
            )}
          </button>
          <button
            onMouseEnter={() => setHoveredIcon('left-consciousness')}
            onMouseLeave={() => setHoveredIcon(null)}
            className="relative w-8 h-8 flex items-center justify-center text-gray-400 hover:text-white hover:bg-gray-700 rounded"
          >
            <Brain className="w-5 h-5" />
            {hoveredIcon === 'left-consciousness' && (
              <div className="absolute left-full ml-2 flex gap-1 z-50 bg-gray-900 border border-gray-700 rounded shadow-lg">
                <button onClick={() => {setLeftTopPanel('consciousness'); setLeftBottomPanel(null)}} className="w-8 h-8 flex items-center justify-center hover:bg-gray-700">↖</button>
                <div className="w-0.5 bg-gray-700 my-1" />
                <button onClick={() => {setLeftTopPanel('consciousness')}} className="w-8 h-8 flex items-center justify-center hover:bg-gray-700">⬆️</button>
                <button onClick={() => {setLeftBottomPanel('consciousness')}} className="w-8 h-8 flex items-center justify-center hover:bg-gray-700">⬇️</button>
              </div>
            )}
          </button>
          <button
            onMouseEnter={() => setHoveredIcon('left-tool-quality')}
            onMouseLeave={() => setHoveredIcon(null)}
            className="relative w-8 h-8 flex items-center justify-center text-gray-400 hover:text-white hover:bg-gray-700 rounded"
          >
            <BarChart3 className="w-5 h-5" />
            {hoveredIcon === 'left-tool-quality' && (
              <div className="absolute left-full ml-2 flex gap-1 z-50 bg-gray-900 border border-gray-700 rounded shadow-lg">
                <button onClick={() => {setLeftTopPanel('tool-quality'); setLeftBottomPanel(null)}} className="w-8 h-8 flex items-center justify-center hover:bg-gray-700">↖</button>
                <div className="w-0.5 bg-gray-700 my-1" />
                <button onClick={() => {setLeftTopPanel('tool-quality')}} className="w-8 h-8 flex items-center justify-center hover:bg-gray-700">⬆️</button>
                <button onClick={() => {setLeftBottomPanel('tool-quality')}} className="w-8 h-8 flex items-center justify-center hover:bg-gray-700">⬇️</button>
              </div>
            )}
          </button>
        </div>

        {/* Left Side - Split Panels */}
        <PanelGroup direction="vertical" className="w-64 min-w-64 max-w-96 bg-gray-800 border-r border-gray-700">
          <Panel defaultSize={50} minSize={20}>
            <div className="h-full border-b border-gray-700">
              {renderPanelContent(leftTopPanel, 'left')}
            </div>
          </Panel>
          {leftBottomPanel && (
            <>
              <PanelResizeHandle className="h-1 bg-gray-700" />
              <Panel defaultSize={50} minSize={20}>
                {renderPanelContent(leftBottomPanel, 'left')}
              </Panel>
            </>
          )}
        </PanelGroup>

        {/* Central Main Area */}
        <div className="flex-1 min-w-0 overflow-hidden bg-gray-900">
          {renderMainContent()}
        </div>

        {/* Right Side - Split Panels */}
        <PanelGroup direction="vertical" className="w-64 min-w-64 max-w-96 bg-gray-800 border-l border-gray-700">
          <Panel defaultSize={50} minSize={20}>
            <div className="h-full border-b border-gray-700">
              {renderPanelContent(rightTopPanel, 'right')}
            </div>
          </Panel>
          {rightBottomPanel && (
            <>
              <PanelResizeHandle className="h-1 bg-gray-700" />
              <Panel defaultSize={50} minSize={20}>
                {renderPanelContent(rightBottomPanel, 'right')}
              </Panel>
            </>
          )}
        </PanelGroup>

        {/* Right Icon Bar */}
        <div className="w-10 bg-gray-800 border-l border-gray-700 flex flex-col items-center py-2 gap-2">
          <button
            onMouseEnter={() => setHoveredIcon('right-planning')}
            onMouseLeave={() => setHoveredIcon(null)}
            className="relative w-8 h-8 flex items-center justify-center text-gray-400 hover:text-white hover:bg-gray-700 rounded"
          >
            <Sparkles className="w-5 h-5" />
            {hoveredIcon === 'right-planning' && (
              <div className="absolute right-full mr-2 flex flex-col gap-1 z-50 bg-gray-900 border border-gray-700 rounded shadow-lg">
                <button onClick={() => {setRightTopPanel('planning'); setRightBottomPanel(null)}} className="w-8 h-8 flex items-center justify-center hover:bg-gray-700">â«</button>
                <div className="h-0.5 w-full bg-gray-700" />
                <button onClick={() => setRightTopPanel('planning')} className="w-8 h-8 flex items-center justify-center hover:bg-gray-700">â¬†ï¸</button>
                <button onClick={() => setRightBottomPanel('planning')} className="w-8 h-8 flex items-center justify-center hover:bg-gray-700">â¬‡ï¸</button>
              </div>
            )}
          </button>
          <button
            onMouseEnter={() => setHoveredIcon('right-coding')}
            onMouseLeave={() => setHoveredIcon(null)}
            className="relative w-8 h-8 flex items-center justify-center text-gray-400 hover:text-white hover:bg-gray-700 rounded"
          >
            <Code className="w-5 h-5" />
            {hoveredIcon === 'right-coding' && (
              <div className="absolute right-full mr-2 flex flex-col gap-1 z-50 bg-gray-900 border border-gray-700 rounded shadow-lg">
                <button onClick={() => {setRightTopPanel('coding'); setRightBottomPanel(null)}} className="w-8 h-8 flex items-center justify-center hover:bg-gray-700">â«</button>
                <div className="h-0.5 w-full bg-gray-700" />
                <button onClick={() => setRightTopPanel('coding')} className="w-8 h-8 flex items-center justify-center hover:bg-gray-700">â¬†ï¸</button>
                <button onClick={() => setRightBottomPanel('coding')} className="w-8 h-8 flex items-center justify-center hover:bg-gray-700">â¬‡ï¸</button>
              </div>
            )}
          </button>
                 <button
                   onMouseEnter={() => setHoveredIcon('right-context')}
                   onMouseLeave={() => setHoveredIcon(null)}
                   className="relative w-8 h-8 flex items-center justify-center text-gray-400 hover:text-white hover:bg-gray-700 rounded"
                 >
                   <Network className="w-5 h-5" />
                   {hoveredIcon === 'right-context' && (
                     <div className="absolute right-full mr-2 flex flex-col gap-1 z-50 bg-gray-900 border border-gray-700 rounded shadow-lg">
                       <button onClick={() => {setRightTopPanel('context'); setRightBottomPanel(null)}} className="w-8 h-8 flex items-center justify-center hover:bg-gray-700">â«</button>
                       <div className="h-0.5 w-full bg-gray-700" />
                       <button onClick={() => setRightTopPanel('context')} className="w-8 h-8 flex items-center justify-center hover:bg-gray-700">â¬†ï¸</button>
                       <button onClick={() => setRightBottomPanel('context')} className="w-8 h-8 flex items-center justify-center hover:bg-gray-700">â¬‡ï¸</button>
                     </div>
                   )}
                 </button>
                 <button
                   onMouseEnter={() => setHoveredIcon('right-workflows')}
                   onMouseLeave={() => setHoveredIcon(null)}
                   className="relative w-8 h-8 flex items-center justify-center text-gray-400 hover:text-white hover:bg-gray-700 rounded"
                 >
                   <Workflow className="w-5 h-5" />
                   {hoveredIcon === 'right-workflows' && (
                     <div className="absolute right-full mr-2 flex flex-col gap-1 z-50 bg-gray-900 border border-gray-700 rounded shadow-lg">
                       <button onClick={() => {setRightTopPanel('workflows'); setRightBottomPanel(null)}} className="w-8 h-8 flex items-center justify-center hover:bg-gray-700">â«</button>
                       <div className="h-0.5 w-full bg-gray-700" />
                       <button onClick={() => setRightTopPanel('workflows')} className="w-8 h-8 flex items-center justify-center hover:bg-gray-700">â¬†ï¸</button>
                       <button onClick={() => setRightBottomPanel('workflows')} className="w-8 h-8 flex items-center justify-center hover:bg-gray-700">â¬‡ï¸</button>
                     </div>
                   )}
                 </button>
                 <button
                   onMouseEnter={() => setHoveredIcon('right-coordination')}
                   onMouseLeave={() => setHoveredIcon(null)}
                   className="relative w-8 h-8 flex items-center justify-center text-gray-400 hover:text-white hover:bg-gray-700 rounded"
                 >
                   <Users className="w-5 h-5" />
                   {hoveredIcon === 'right-coordination' && (
                     <div className="absolute right-full mr-2 flex flex-col gap-1 z-50 bg-gray-900 border border-gray-700 rounded shadow-lg">
                       <button onClick={() => {setRightTopPanel('coordination'); setRightBottomPanel(null)}} className="w-8 h-8 flex items-center justify-center hover:bg-gray-700">â«</button>
                       <div className="h-0.5 w-full bg-gray-700" />
                       <button onClick={() => setRightTopPanel('coordination')} className="w-8 h-8 flex items-center justify-center hover:bg-gray-700">â¬†ï¸</button>
                       <button onClick={() => setRightBottomPanel('coordination')} className="w-8 h-8 flex items-center justify-center hover:bg-gray-700">â¬‡ï¸</button>
                     </div>
                   )}
                 </button>
         </div>
          </div>
        </Panel>

        {/* Bottom Drawer */}
        {bottomDrawerOpen && (
          <>
            <PanelResizeHandle className="h-1 bg-gray-700 hover:bg-gray-600 transition-colors" />
            <Panel defaultSize={15} minSize={10} maxSize={50}>
              <div className="h-full flex flex-col bg-gray-800 border-t border-gray-700">
                {/* Bottom Bar - Bottom Drawer Pages */}
                <div className="h-10 bg-gray-800 border-b border-gray-700 flex items-center px-4 gap-4">
         <button
           onClick={() => {setBottomDrawerOpen(!bottomDrawerOpen); setBottomDrawerPage('terminal')}}
           className={`px-3 py-1 rounded text-sm font-medium ${
             bottomDrawerOpen && bottomDrawerPage === 'terminal' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'
           }`}
         >
           <Terminal className="w-4 h-4 inline mr-2" />
           Terminal
         </button>
         <button
           onClick={() => {setBottomDrawerOpen(!bottomDrawerOpen); setBottomDrawerPage('timeline')}}
           className={`px-3 py-1 rounded text-sm font-medium ${
             bottomDrawerOpen && bottomDrawerPage === 'timeline' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'
           }`}
         >
           <Calendar className="w-4 h-4 inline mr-2" />
           Timeline
         </button>
         <button
           onClick={() => {setBottomDrawerOpen(!bottomDrawerOpen); setBottomDrawerPage('lucid-timeline')}}
           className={`px-3 py-1 rounded text-sm font-medium ${
             bottomDrawerOpen && bottomDrawerPage === 'lucid-timeline' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'
           }`}
         >
           <Clock className="w-4 h-4 inline mr-2" />
           Lucid Timeline
         </button>
        <button
          onClick={() => {setBottomDrawerOpen(!bottomDrawerOpen); setBottomDrawerPage('problems')}}
          className={`px-3 py-1 rounded text-sm font-medium ${
            bottomDrawerOpen && bottomDrawerPage === 'problems' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'
          }`}
        >
          <AlertTriangle className="w-4 h-4 inline mr-2" />
          Problems
        </button>
        <button
          onClick={() => {setBottomDrawerOpen(!bottomDrawerOpen); setBottomDrawerPage('debug')}}
          className={`px-3 py-1 rounded text-sm font-medium ${
            bottomDrawerOpen && bottomDrawerPage === 'debug' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'
          }`}
        >
          <Bug className="w-4 h-4 inline mr-2" />
          Debug
        </button>
                </div>
                
                {/* Bottom Drawer Content */}
                <div className="flex-1 overflow-auto">
                  {bottomDrawerPage === 'terminal' && <TerminalPanel isOpen={true} onClose={() => setBottomDrawerOpen(false)} />}
                  {bottomDrawerPage === 'timeline' && <TimelineVisualization isOpen={true} onClose={() => setBottomDrawerPage(null)} />}
                  {bottomDrawerPage === 'lucid-timeline' && <LucidTimelineDrawer />}
                  {bottomDrawerPage === 'problems' && (
                    <div className="h-full p-4">
                      <h3 className="text-white text-lg font-semibold mb-4">Problems</h3>
                      <div className="text-gray-400">No problems found</div>
                    </div>
                  )}
                  {bottomDrawerPage === 'debug' && <DebugConsole />}
                </div>
              </div>
            </Panel>
          </>
        )}
      </PanelGroup>
        </div>
      </PlanningAgentProvider>
    </CodingAgentProvider>
  )
}






