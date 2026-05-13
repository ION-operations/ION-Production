/**
 * Main Dashboard Component with Multi-Tab Structure
 * Wraps AgentManagementDashboard and other tabs
 * 
 * Created: 2025-10-31
 * Agent: Aether (taking over from Lexicon)
 */

import React, { useState, useEffect, useMemo } from 'react'
import { Bot, MessageSquare, Link, Wrench, Calendar, Tag, Zap, Terminal, Server, GitBranch, Activity, AlertTriangle, Heart, Users, Settings, BookOpen, FileText, Code, Database, Layers } from 'lucide-react'
import { LandingPage } from './LandingPage'
import { ErrorBoundary } from './ErrorBoundary'
import { AgentManagementDashboard } from './AgentManagementDashboard'
import { ChatInterfaceTab } from './AgentManagementDashboard/ChatInterfaceTab'
import PromptChainsTab from './AgentManagementDashboard/PromptChainsTab'
import MCPToolsTab from './AgentManagementDashboard/MCPToolsTab'
import TimelineTab from './AgentManagementDashboard/TimelineTab'
import NLTagPanel from './NLTagPanel'
import { NotificationSystem } from './NotificationSystem'
import { AutonomousOperationPanel } from './AutonomousOperationPanel'
import { LogViewer } from './DevTools/LogViewer'
import { DaemonDashboard } from './DaemonIntegration/DaemonDashboard'
import { FileChangesViewer } from './FileChanges/FileChangesViewer'
import { SystemTools } from './SystemTools/SystemTools'
import { ErrorDetector } from './Telemetry/ErrorDetector'
import { AgentChatsPanel } from './DrawerPanels/AgentChatsPanel'
import { AIChatDrawer } from './DrawerPanels/AIChatDrawer'
import { PromptChainTemplatesPanel } from './DrawerPanels/PromptChainTemplatesPanel'
import { ChainNodePalette } from './DrawerPanels/ChainNodePalette'
import { CaptureResult } from './CaptureResult'

export type TabId = 'agents' | 'chat' | 'chains' | 'tools' | 'timeline' | 'nl-tags' | 'autonomous' | 'devtools' | 'daemon' | 'file-changes' | 'system-tools' | 'error-detector'

interface Tab {
  id: TabId
  label: string
  icon: React.ComponentType<{ className?: string }>
}

const tabs: Tab[] = [
  { id: 'agents', label: 'Agents', icon: Bot },
  { id: 'chat', label: 'Chat', icon: MessageSquare },
  { id: 'chains', label: 'Chains', icon: Link },
  { id: 'tools', label: 'Tools', icon: Wrench },
  { id: 'timeline', label: 'Timeline', icon: Calendar },
  { id: 'nl-tags', label: 'NL Tags', icon: Tag },
  { id: 'autonomous', label: 'Autonomous', icon: Zap },
  { id: 'devtools', label: 'Dev Tools', icon: Terminal },
  { id: 'error-detector', label: 'Error Detection', icon: AlertTriangle },
  { id: 'daemon', label: 'Daemon', icon: Server },
  { id: 'file-changes', label: 'File Changes', icon: GitBranch },
  { id: 'system-tools', label: 'System Tools', icon: Activity }
]

interface MainDashboardProps {
  leftDrawerPanel?: string | null
  rightDrawerPanel?: string | null
  onLeftDrawerChange?: (panelId: string | null) => void
  onRightDrawerChange?: (panelId: string | null) => void
}

export const MainDashboard: React.FC<MainDashboardProps> = ({
  leftDrawerPanel,
  rightDrawerPanel,
  onLeftDrawerChange,
  onRightDrawerChange
}) => {
  // Skip landing page in Electron mode (show tabs immediately)
  const [showLanding, setShowLanding] = useState(true)
  const [activeTab, setActiveTab] = useState<TabId>('agents')
  const [chatWithAgent, setChatWithAgent] = useState<string | null>(null)
  const [previousMessageCount, setPreviousMessageCount] = useState(0)
  const [currentMessages, setCurrentMessages] = useState<any[]>([])
  const [systemStatus, setSystemStatus] = useState({
    extensionLoaded: false,
    reactUILoaded: true,
    mcpToolsAvailable: false,
    daemonConnected: false,
    extensionCommandServer: false
  })

  // Template capture state
  const [captureResult, setCaptureResult] = useState<{
    thumbnail: string
    rectangle: { x: number; y: number; width: number; height: number }
  } | null>(null)

  // Listen for capture result
  useEffect(() => {
    const handleCaptureResult = (event: CustomEvent) => {
      const data = event.detail
      setCaptureResult({
        thumbnail: data.thumbnail,
        rectangle: data.rectangle
      })
    }

    window.addEventListener('capture-result', handleCaptureResult as EventListener)
    return () => {
      window.removeEventListener('capture-result', handleCaptureResult as EventListener)
    }
  }, [])

  // Handle template save
  const handleTemplateSave = async (metadata: { name: string; theme: 'light' | 'dark' | 'hover' }) => {
    if (!captureResult) return

    const win = window as any
    if (win.electronAPI) {
      try {
        const result = await win.electronAPI.invoke('template:save', {
          templateData: {
            croppedRegion: captureResult.thumbnail, // Base64 string
            rectangle: captureResult.rectangle
          },
          metadata
        })

        if (result.success) {
          alert(`Template saved: ${result.templateId}`)
          setCaptureResult(null)
        } else {
          alert(`Failed to save template: ${result.error}`)
        }
      } catch (error) {
        console.error('Failed to save template:', error)
        alert('Failed to save template')
      }
    }
  }

  // Track messages for notifications (reduced polling to prevent excessive API calls)
  useEffect(() => {
    let mounted = true
    
    // This will be updated when ChatInterfaceTab provides messages
    // For now, we'll fetch messages separately for notifications
    const fetchMessagesForNotifications = async () => {
      if (!mounted) return
      
      try {
        const { getServiceBridge } = await import('../services/serviceBridge')
        const serviceBridge = getServiceBridge()
        const messages = await serviceBridge.getAIMessages(undefined, undefined)
        if (mounted) {
          setCurrentMessages(messages)
        }
      } catch (error) {
        // Silently fail - backend not available is expected
        if (mounted && process.env.NODE_ENV === 'development') {
          console.log('[MainDashboard] Failed to fetch messages for notifications:', error)
        }
      }
    }
    
    // Increased polling interval: 30 seconds instead of 15 seconds to reduce API calls
    const interval = setInterval(fetchMessagesForNotifications, 30000)
    fetchMessagesForNotifications() // Initial fetch
    
    return () => {
      mounted = false
      clearInterval(interval)
    }
  }, [])

  // Update previous message count when messages change
  useEffect(() => {
    if (currentMessages.length > previousMessageCount) {
      // Notification system will handle showing notifications
      // We'll update count after notifications are shown
    }
  }, [currentMessages.length, previousMessageCount])

  // Get context-aware drawer panels based on active tab
  const leftDrawerPanels = useMemo(() => {
    if (activeTab === 'chat') {
      return [
        {
          id: 'agent-chats',
          icon: Users,
          label: 'Agent Chats',
          content: (
            <AgentChatsPanel
              onSelectAgent={(agent) => {
                setChatWithAgent(agent)
                setActiveTab('chat')
              }}
              onSelectThread={(threadId) => {
                // Handle thread selection if needed
                console.log('Thread selected:', threadId)
              }}
            />
          )
        }
      ]
    }
    
    if (activeTab === 'chains') {
      return [
        {
          id: 'chain-nodes',
          icon: Layers,
          label: 'Node Palette',
          content: (
            <ChainNodePalette
              onNodeSelect={(nodeType, nodeConfig) => {
                console.log('Node selected:', nodeType, nodeConfig)
                // Emit event for chain editor to handle
                window.dispatchEvent(new CustomEvent('chain-node-selected', {
                  detail: { nodeType, nodeConfig }
                }))
              }}
            />
          )
        },
        {
          id: 'chain-templates',
          icon: FileText,
          label: 'Chain Templates',
          content: (
            <PromptChainTemplatesPanel
              onSelectTemplate={(template) => {
                console.log('Template selected:', template)
                // Emit event for chain editor to load template
                window.dispatchEvent(new CustomEvent('chain-template-loaded', {
                  detail: { template }
                }))
              }}
              onUseTemplate={(template) => {
                console.log('Using template:', template)
                // Emit event for chain editor to instantiate template
                window.dispatchEvent(new CustomEvent('chain-template-use', {
                  detail: { template }
                }))
              }}
            />
          )
        }
      ]
    }
    
    // Add more context-aware panels here for other tabs
    return []
  }, [activeTab])

  const rightDrawerPanels = useMemo(() => {
    // Right drawer panels - AI Chat always available
    return [
      {
        id: 'ai-chat',
        icon: MessageSquare,
        label: 'AI Chat',
        content: (
          <AIChatDrawer
            selectedAgent={chatWithAgent}
            onAgentChange={(agent) => {
              setChatWithAgent(agent)
              // Optionally switch to chat tab when agent selected
              if (agent) {
                setActiveTab('chat')
              }
            }}
          />
        )
      }
    ]
  }, [chatWithAgent])

  // Expose drawer panels to parent (App.tsx) via window
  useEffect(() => {
    ;(window as any).leftDrawerPanels = leftDrawerPanels
    ;(window as any).rightDrawerPanels = rightDrawerPanels
    
    // Expose tab navigation to App.tsx
    ;(window as any).tabNavigation = (
      <>
        {/* Back to Landing Button */}
        <button
          onClick={() => setShowLanding(true)}
          className="px-2 py-1 text-cursor-text-secondary hover:text-cursor-text hover:bg-cursor-hover transition-colors cursor-button"
          title="Back to landing page"
        >
          ←
        </button>
        
        {tabs.map((tab) => {
          const Icon = tab.icon
          const isActive = activeTab === tab.id
          return (
            <button
              key={tab.id}
              onClick={() => {
                setActiveTab(tab.id)
                // Clear chat agent selection when switching away from chat
                if (tab.id !== 'chat') {
                  setChatWithAgent(null)
                }
              }}
              className={`flex items-center gap-1.5 px-3 py-1 transition-colors ${
                isActive
                  ? 'bg-cursor-tab-active text-cursor-text border-b-2 border-cursor-status-bar'
                  : 'bg-cursor-tab-inactive text-cursor-text-secondary hover:text-cursor-text hover:bg-cursor-hover'
              }`}
              style={{
                fontSize: '13px',
                height: '32px',
                lineHeight: '1.4'
              }}
            >
              <Icon className="w-3.5 h-3.5" />
              <span className="font-normal">{tab.label}</span>
            </button>
          )
        })}
      </>
    )
    
    return () => {
      delete (window as any).leftDrawerPanels
      delete (window as any).rightDrawerPanels
      delete (window as any).tabNavigation
    }
  }, [leftDrawerPanels, rightDrawerPanels, activeTab, tabs, showLanding, chatWithAgent])

  const renderTabContent = () => {
    switch (activeTab) {
      case 'agents':
        return <AgentManagementDashboard />
      case 'chat':
        return <ChatInterfaceTab initialAgent={chatWithAgent} onAgentChange={setChatWithAgent} />
      case 'chains':
        return <PromptChainsTab />
      case 'tools':
        return <MCPToolsTab />
      case 'timeline':
        return <TimelineTab />
      case 'nl-tags':
        return <NLTagPanel />
      case 'autonomous':
        return <AutonomousOperationPanel />
      case 'devtools':
        return <LogViewer />
      case 'daemon':
        return <DaemonDashboard />
      case 'file-changes':
        return <FileChangesViewer />
      case 'system-tools':
        return <SystemTools />
      case 'error-detector':
        return <ErrorDetector />
      default:
        return <AgentManagementDashboard />
    }
  }

  // Function to handle chat navigation from agent cards
  const handleChatWithAgent = (agentName: string) => {
    setChatWithAgent(agentName)
    setActiveTab('chat')
  }

  // Expose handler via context or prop (for AgentManagementDashboard)
  useEffect(() => {
    // Store handler in window for AgentManagementDashboard to access
    ;(window as any).handleChatWithAgent = handleChatWithAgent
    return () => {
      delete (window as any).handleChatWithAgent
    }
  }, [])

  // Check if running in Electron and skip landing page
  useEffect(() => {
    const checkElectron = () => {
      const isElectron = typeof window !== 'undefined' && (window as any).windowControls !== undefined
      if (isElectron) {
        setShowLanding(false) // Skip landing page in Electron
      }
    }
    
    // Check immediately and after a short delay (in case windowControls loads async)
    checkElectron()
    setTimeout(checkElectron, 100)
  }, [])

  // Check system status on mount
  useEffect(() => {
    const checkSystemStatus = async () => {
      try {
        // Check Extension command server (for MCP tools)
        try {
          const { getMCPAPI } = await import('../services/mcpApi')
          const mcpApi = getMCPAPI()
          const extensionAvailable = await mcpApi.checkExtension()
          
          setSystemStatus(prev => ({
            ...prev,
            extensionCommandServer: extensionAvailable,
            mcpToolsAvailable: extensionAvailable
          }))
          
          if (extensionAvailable) {
            // Try to list MCP tools
            const tools = await mcpApi.listTools()
            if (tools.length > 0) {
              console.log(`[AIM-OS] MCP tools available: ${tools.length} tools`)
            }
          }
        } catch (error) {
          console.log('[AIM-OS] Extension/MCP check:', error)
        }
        
        // Check if we're in webview context (legacy check)
        if (typeof (window as any).acquireVsCodeApi !== 'undefined') {
          setSystemStatus(prev => ({ ...prev, extensionLoaded: true }))
        }
      } catch (error) {
        console.log('[AIM-OS] System status check:', error)
      }
    }
    
    // Delay check to let UI render first
    setTimeout(checkSystemStatus, 500)
  }, [])

  // Show landing page first, then dashboard after user clicks "Enter Dashboard"
  if (showLanding) {
    return (
      <ErrorBoundary>
        <LandingPage
          onEnterDashboard={() => setShowLanding(false)}
          systemStatus={systemStatus}
        />
      </ErrorBoundary>
    )
  }

  return (
    <ErrorBoundary>
      <div className="flex flex-col bg-cursor-bg text-cursor-text h-full overflow-hidden cursor-scrollbar">
        {/* Tab Content - Full height (tab bar is rendered at App.tsx level) */}
        <div className="flex-1 overflow-hidden relative">
          <ErrorBoundary>
            {renderTabContent()}
          </ErrorBoundary>
          
          {/* Notification System - Always visible */}
          <NotificationSystem
            messages={currentMessages}
            previousMessageCount={previousMessageCount}
            onNotificationClick={() => {
              setActiveTab('chat')
              setPreviousMessageCount(currentMessages.length)
            }}
          />
          
          {/* Capture Result Modal */}
          {captureResult && (
            <CaptureResult
              thumbnail={captureResult.thumbnail}
              rectangle={captureResult.rectangle}
              onSave={handleTemplateSave}
              onCancel={() => setCaptureResult(null)}
            />
          )}
        </div>
      </div>
    </ErrorBoundary>
  )
}

export default MainDashboard

