// Advanced Browser Automation Panel - DAC V2 IDE
// Comprehensive automation tools: Visual Script Builder, Element Inspector, Macro Recorder, etc.

import React, { useState, useEffect, useRef, useCallback } from 'react'
import { BasePanel } from '../components/BasePanel'
import { LoadingSpinner, ErrorDisplay } from '../components/shared/shared'
import {
  ScriptsTab,
  RecorderTab,
  InspectorTab,
  AccountsTab,
  DebugTab,
  MetricsTab,
  LibraryTab
} from '../components/browser-automation/AdvancedTabs'
import {
  Globe,
  Play,
  Square,
  Pause,
  RefreshCw,
  Settings,
  Save,
  Upload,
  Download,
  Trash2,
  Plus,
  ChevronRight,
  ChevronDown,
  Search,
  Eye,
  MousePointer,
  Keyboard,
  FileText,
  Code,
  Zap,
  Layers,
  Database,
  BarChart3,
  Camera,
  Bug,
  PlayCircle,
  StopCircle,
  SkipForward,
  SkipBack,
  Copy,
  Edit,
  X,
  Check,
  AlertCircle,
  Info,
  Filter,
  Download as DownloadIcon,
  Upload as UploadIcon,
  FolderOpen,
  BookOpen,
  Wand2,
  Target,
  Monitor,
  Network,
  Clock,
  Activity
} from 'lucide-react'

// ===== TYPE DEFINITIONS =====

interface ChatAccount {
  id: string
  provider: 'chatgpt' | 'claude' | 'gemini' | 'custom'
  email?: string
  displayName?: string
  lastUsed?: string
  sessionValid?: boolean
}

interface AutomationScript {
  id: string
  name: string
  description?: string
  provider: string
  createdAt: string
  actions: any[]
  variables?: Record<string, string>
}

interface AutomationLog {
  timestamp: number
  level: 'LOG' | 'SUCCESS' | 'WARN' | 'ERROR' | 'DEBUG'
  message: string
  data?: any
  step?: number
  selector?: string
}

interface ScriptNode {
  id: string
  type: 'navigate' | 'click' | 'type' | 'wait' | 'extract' | 'screenshot' | 'condition' | 'loop' | 'upload'
  position: { x: number; y: number }
  data: {
    label: string
    config: any
  }
}

interface DetectedElement {
  selector: string
  xpath: string
  text?: string
  tag: string
  attributes: Record<string, string>
  bounds: { x: number; y: number; width: number; height: number }
  confidence: number
}

interface ExecutionMetrics {
  totalExecutions: number
  successRate: number
  averageDuration: number
  lastExecution?: Date
  errorCount: number
}

// ===== API CLIENT =====

const API_BASE_URL = 'http://localhost:5002/api'

async function apiRequest<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers
    }
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Request failed' }))
    throw new Error(error.error || `HTTP ${response.status}`)
  }

  return response.json()
}

// ===== MAIN COMPONENT =====

type TabType = 'browser' | 'scripts' | 'recorder' | 'inspector' | 'accounts' | 'debug' | 'metrics' | 'library'

export const BrowserAutomationPanel: React.FC = () => {
  // Core state
  const [activeTab, setActiveTab] = useState<TabType>('browser')
  const [browserId, setBrowserId] = useState<string | null>(null)
  const [browserUrl, setBrowserUrl] = useState<string>('https://chat.openai.com')
  const [screenshot, setScreenshot] = useState<string | null>(null)
  const [automationStatus, setAutomationStatus] = useState<'idle' | 'running' | 'paused' | 'error'>('idle')
  const [executionId, setExecutionId] = useState<string | null>(null)
  const [executionProgress, setExecutionProgress] = useState<{
    currentStep: number
    totalSteps: number
    stepName: string
    progress: number
  } | null>(null)

  // Data state
  const [logs, setLogs] = useState<AutomationLog[]>([])
  const [accounts, setAccounts] = useState<ChatAccount[]>([])
  const [scripts, setScripts] = useState<AutomationScript[]>([])
  const [selectedAccount, setSelectedAccount] = useState<string | null>(null)
  const [selectedScript, setSelectedScript] = useState<string | null>(null)
  const [scriptSearchQuery, setScriptSearchQuery] = useState('')
  const [logFilter, setLogFilter] = useState<'all' | 'LOG' | 'SUCCESS' | 'WARN' | 'ERROR' | 'DEBUG'>('all')

  // Visual Script Builder state
  const [scriptNodes, setScriptNodes] = useState<ScriptNode[]>([])
  const [scriptEdges, setScriptEdges] = useState<any[]>([])
  const [selectedNode, setSelectedNode] = useState<string | null>(null)
  const [isRecording, setIsRecording] = useState(false)
  const [recordedActions, setRecordedActions] = useState<any[]>([])

  // Element Inspector state
  const [inspectorMode, setInspectorMode] = useState(false)
  const [detectedElements, setDetectedElements] = useState<DetectedElement[]>([])
  const [hoveredElement, setHoveredElement] = useState<DetectedElement | null>(null)
  const [selectedElement, setSelectedElement] = useState<DetectedElement | null>(null)

  // Debug state
  const [breakpoints, setBreakpoints] = useState<Set<number>>(new Set())
  const [currentStep, setCurrentStep] = useState<number | null>(null)
  const [variables, setVariables] = useState<Record<string, any>>({})
  const [stepMode, setStepMode] = useState(false)

  // Metrics state
  const [metrics, setMetrics] = useState<ExecutionMetrics>({
    totalExecutions: 0,
    successRate: 0,
    averageDuration: 0,
    errorCount: 0
  })

  // UI state
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showAccountManager, setShowAccountManager] = useState(false)
  const [showScriptEditor, setShowScriptEditor] = useState(false)
  const [editingScript, setEditingScript] = useState<AutomationScript | null>(null)

  // Load data on mount
  useEffect(() => {
    loadAccounts()
    loadScripts()
    loadMetrics()
  }, [])

  // Poll execution status when running
  useEffect(() => {
    if (executionId && automationStatus === 'running') {
      const interval = setInterval(() => {
        checkExecutionStatus()
        if (browserId) {
          captureScreenshot()
        }
      }, 1000)
      return () => clearInterval(interval)
    }
  }, [executionId, automationStatus, browserId])

  // Capture screenshot periodically when browser is active
  useEffect(() => {
    if (browserId && !executionId) {
      const interval = setInterval(() => {
        captureScreenshot()
      }, 2000)
      return () => clearInterval(interval)
    }
  }, [browserId, executionId])

  const loadAccounts = async () => {
    try {
      const response = await apiRequest<{ success: boolean; accounts: ChatAccount[] }>('/connections/list')
      if (response.success) {
        setAccounts(response.accounts || [])
      }
    } catch (err) {
      console.error('Failed to load accounts:', err)
    }
  }

  const loadScripts = async () => {
    try {
      const response = await apiRequest<{ success: boolean; scripts: AutomationScript[] }>('/scripts/list')
      if (response.success) {
        setScripts(response.scripts || [])
      }
    } catch (err) {
      console.error('Failed to load scripts:', err)
    }
  }

  const loadMetrics = async () => {
    try {
      const response = await apiRequest<{ success: boolean; metrics?: ExecutionMetrics }>('/automation/metrics')
      if (response.success && response.metrics) {
        setMetrics(response.metrics)
      }
    } catch (err) {
      console.error('Failed to load metrics:', err)
      // Keep current metrics on error
    }
  }

  const captureScreenshot = async () => {
    if (!browserId) return
    try {
      const response = await fetch(`${API_BASE_URL}/browser/screenshot?browserId=${browserId}&type=png`)
      if (response.ok) {
        const blob = await response.blob()
        const url = URL.createObjectURL(blob)
        setScreenshot(url)
      }
    } catch (err) {
      console.error('Failed to capture screenshot:', err)
      addLog('WARN', 'Screenshot capture failed')
    }
  }

  const launchBrowser = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await apiRequest<{ success: boolean; browserId?: string }>('/browser/launch', {
        method: 'POST',
        body: JSON.stringify({
          headless: false,
          viewport: { width: 1280, height: 720 }
        })
      })

      if (response.success && response.browserId) {
        setBrowserId(response.browserId)
        addLog('SUCCESS', 'Browser launched successfully')
        await navigateToUrl(browserUrl)
        await captureScreenshot()
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to launch browser'
      setError(errorMessage)
      addLog('ERROR', errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const navigateToUrl = async (url: string) => {
    if (!browserId) return

    setLoading(true)
    setError(null)
    try {
      await apiRequest('/browser/navigate', {
        method: 'POST',
        body: JSON.stringify({ browserId, url })
      })
      setBrowserUrl(url)
      addLog('SUCCESS', `Navigated to ${url}`)
      await captureScreenshot()
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Navigation failed'
      setError(errorMessage)
      addLog('ERROR', errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const executeScript = async () => {
    if (!browserId || !selectedScript) {
      setError('Browser and script must be selected')
      return
    }

    setLoading(true)
    setError(null)
    setAutomationStatus('running')
    addLog('LOG', 'Starting script execution...')

    try {
      const scriptResponse = await apiRequest<{ success: boolean; script?: any }>(`/scripts/${selectedScript}`)
      if (!scriptResponse.success || !scriptResponse.script) {
        throw new Error('Failed to load script')
      }

      if (selectedAccount) {
        await apiRequest(`/connections/${selectedAccount}/load-session`, {
          method: 'POST',
          body: JSON.stringify({ browserId })
        })
        addLog('SUCCESS', 'Session loaded')
      }

      const executeResponse = await apiRequest<{ success: boolean; executionId?: string }>('/automation/execute', {
        method: 'POST',
        body: JSON.stringify({
          browserId,
          script: scriptResponse.script,
          variables: variables
        })
      })

      if (executeResponse.success && executeResponse.executionId) {
        setExecutionId(executeResponse.executionId)
        addLog('SUCCESS', 'Script execution started')
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Execution failed'
      setError(errorMessage)
      setAutomationStatus('error')
      addLog('ERROR', errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const checkExecutionStatus = async () => {
    if (!executionId) return

    try {
      const response = await apiRequest<{ success: boolean; status?: any }>(`/automation/status?executionId=${executionId}`)
      if (response.success && response.status) {
        const totalSteps = response.status.totalSteps || 0
        const currentStep = response.status.currentStep || 0
        const progress = totalSteps > 0 ? currentStep / totalSteps : 0

        setExecutionProgress({
          currentStep,
          totalSteps,
          stepName: response.status.stepName || '',
          progress
        })
        setCurrentStep(currentStep || null)

        if (response.status.status === 'completed') {
          setAutomationStatus('idle')
          setExecutionId(null)
          addLog('SUCCESS', 'Script execution completed')
          setMetrics(prev => ({
            ...prev,
            totalExecutions: prev.totalExecutions + 1,
            successRate: (prev.successRate * prev.totalExecutions + 1) / (prev.totalExecutions + 1)
          }))
        } else if (response.status.status === 'error') {
          setAutomationStatus('error')
          setExecutionId(null)
          addLog('ERROR', 'Script execution failed')
          setMetrics(prev => ({
            ...prev,
            errorCount: prev.errorCount + 1,
            successRate: (prev.successRate * prev.totalExecutions) / (prev.totalExecutions + 1)
          }))
        }
      }
    } catch (err) {
      console.error('Failed to check execution status:', err)
    }
  }

  const pauseExecution = async () => {
    if (!executionId) return
    try {
      await apiRequest('/automation/pause', {
        method: 'POST',
        body: JSON.stringify({ executionId })
      })
      setAutomationStatus('paused')
      addLog('LOG', 'Execution paused')
    } catch (err) {
      console.error('Failed to pause execution:', err)
      addLog('ERROR', 'Failed to pause execution')
    }
  }

  const resumeExecution = async () => {
    if (!executionId) return
    try {
      await apiRequest('/automation/resume', {
        method: 'POST',
        body: JSON.stringify({ executionId })
      })
      setAutomationStatus('running')
      addLog('LOG', 'Execution resumed')
    } catch (err) {
      console.error('Failed to resume execution:', err)
      addLog('ERROR', 'Failed to resume execution')
    }
  }

  const stopExecution = async () => {
    if (!executionId) return
    try {
      await apiRequest('/automation/stop', {
        method: 'POST',
        body: JSON.stringify({ executionId })
      })
      setAutomationStatus('idle')
      setExecutionId(null)
      setCurrentStep(null)
      addLog('LOG', 'Execution stopped')
    } catch (err) {
      console.error('Failed to stop execution:', err)
      addLog('ERROR', 'Failed to stop execution')
    }
  }

  const closeBrowser = async () => {
    if (!browserId) return
    setLoading(true)
    try {
      await apiRequest('/browser/close', {
        method: 'POST',
        body: JSON.stringify({ browserId })
      })
      setBrowserId(null)
      setBrowserUrl('https://chat.openai.com')
      setScreenshot(null)
      addLog('SUCCESS', 'Browser closed')
    } catch (err) {
      console.error('Failed to close browser:', err)
    } finally {
      setLoading(false)
    }
  }

  const startRecording = () => {
    setIsRecording(true)
    setRecordedActions([])
    addLog('LOG', 'Macro recording started')
  }

  const stopRecording = () => {
    setIsRecording(false)
    addLog('SUCCESS', `Macro recording stopped. ${recordedActions.length} actions recorded.`)
  }

  const toggleInspector = () => {
    setInspectorMode(!inspectorMode)
    if (!inspectorMode) {
      addLog('LOG', 'Element Inspector enabled - Click elements to inspect')
    } else {
      addLog('LOG', 'Element Inspector disabled')
    }
  }

  const detectElements = async () => {
    if (!browserId) return
    try {
      const response = await apiRequest<{ success: boolean; elements?: DetectedElement[] }>('/browser/detect-elements', {
        method: 'POST',
        body: JSON.stringify({ browserId })
      })
      if (response.success && response.elements) {
        setDetectedElements(response.elements)
        addLog('SUCCESS', `Detected ${response.elements.length} interactive elements`)
      }
    } catch (err) {
      console.error('Failed to detect elements:', err)
      addLog('ERROR', 'Element detection failed')
    }
  }

  const addLog = (level: AutomationLog['level'], message: string, data?: any, step?: number, selector?: string) => {
    setLogs(prev => [...prev.slice(-199), {
      timestamp: Date.now(),
      level,
      message,
      data,
      step,
      selector
    }])
  }

  const filteredLogs = logs.filter(log => logFilter === 'all' || log.level === logFilter)
  const filteredScripts = scripts.filter(script =>
    !scriptSearchQuery ||
    script.name.toLowerCase().includes(scriptSearchQuery.toLowerCase()) ||
    script.provider.toLowerCase().includes(scriptSearchQuery.toLowerCase())
  )

  const actions = (
    <div className="flex items-center gap-1">
      {browserId ? (
        <>
          <button
            onClick={closeBrowser}
            className="p-1 hover:bg-gray-700 rounded"
            title="Close Browser"
          >
            <Square className="w-4 h-4" />
          </button>
          <button
            onClick={() => navigateToUrl(browserUrl)}
            className="p-1 hover:bg-gray-700 rounded"
            title="Refresh"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <button
            onClick={captureScreenshot}
            className="p-1 hover:bg-gray-700 rounded"
            title="Capture Screenshot"
          >
            <Camera className="w-4 h-4" />
          </button>
        </>
      ) : (
        <button
          onClick={launchBrowser}
          disabled={loading}
          className="px-2 py-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 rounded text-xs flex items-center gap-1"
        >
          <Globe className="w-3 h-3" />
          Launch
        </button>
      )}
    </div>
  )

  return (
    <BasePanel
      id="browser-automation-panel"
      title="Browser Automation"
      icon={Globe}
      loading={loading}
      error={error}
      actions={actions}
    >
      <div className="flex flex-col h-full">
        {/* Tab Navigation - Icons Only */}
        <div className="flex border-b border-gray-700 bg-gray-800/50">
          {([
            { id: 'browser' as TabType, label: 'Browser', icon: Globe, title: 'Browser View' },
            { id: 'scripts' as TabType, label: 'Scripts', icon: Code, title: 'Scripts' },
            { id: 'recorder' as TabType, label: 'Recorder', icon: PlayCircle, title: 'Recorder' },
            { id: 'inspector' as TabType, label: 'Inspector', icon: Eye, title: 'Inspector' },
            { id: 'accounts' as TabType, label: 'Accounts', icon: Database, title: 'Accounts' },
            { id: 'debug' as TabType, label: 'Debug', icon: Bug, title: 'Debug' },
            { id: 'metrics' as TabType, label: 'Metrics', icon: BarChart3, title: 'Metrics' },
            { id: 'library' as TabType, label: 'Library', icon: BookOpen, title: 'Library' }
          ]).map(tab => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                title={tab.title}
                className={`p-2 border-b-2 transition-colors ${activeTab === tab.id
                  ? 'border-blue-500 text-blue-400 bg-gray-800'
                  : 'border-transparent text-gray-400 hover:text-gray-300 hover:bg-gray-800/50'
                  }`}
              >
                <Icon className="w-4 h-4" />
              </button>
            )
          })}
        </div>

        {/* Tab Content */}
        <div className="flex-1 overflow-auto">
          {activeTab === 'browser' && (
            <BrowserTab
              browserId={browserId}
              browserUrl={browserUrl}
              setBrowserUrl={setBrowserUrl}
              screenshot={screenshot}
              navigateToUrl={navigateToUrl}
              automationStatus={automationStatus}
              executionProgress={executionProgress}
              selectedAccount={selectedAccount}
              setSelectedAccount={setSelectedAccount}
              selectedScript={selectedScript}
              setSelectedScript={setSelectedScript}
              accounts={accounts}
              scripts={filteredScripts}
              executeScript={executeScript}
              pauseExecution={pauseExecution}
              resumeExecution={resumeExecution}
              stopExecution={stopExecution}
              logs={filteredLogs}
              logFilter={logFilter}
              setLogFilter={setLogFilter}
              addLog={addLog}
            />
          )}

          {activeTab === 'scripts' && (
            <ScriptsTab
              scripts={filteredScripts}
              scriptSearchQuery={scriptSearchQuery}
              setScriptSearchQuery={setScriptSearchQuery}
              selectedScript={selectedScript}
              setSelectedScript={setSelectedScript}
              scriptNodes={scriptNodes}
              setScriptNodes={setScriptNodes}
              scriptEdges={scriptEdges}
              setScriptEdges={setScriptEdges}
              selectedNode={selectedNode}
              setSelectedNode={setSelectedNode}
              editingScript={editingScript}
              setEditingScript={setEditingScript}
              showScriptEditor={showScriptEditor}
              setShowScriptEditor={setShowScriptEditor}
              loadScripts={loadScripts}
            />
          )}

          {activeTab === 'recorder' && (
            <RecorderTab
              isRecording={isRecording}
              startRecording={startRecording}
              stopRecording={stopRecording}
              recordedActions={recordedActions}
              setRecordedActions={setRecordedActions}
              browserId={browserId}
            />
          )}

          {activeTab === 'inspector' && (
            <InspectorTab
              inspectorMode={inspectorMode}
              toggleInspector={toggleInspector}
              detectedElements={detectedElements}
              setDetectedElements={setDetectedElements}
              hoveredElement={hoveredElement}
              setHoveredElement={setHoveredElement}
              selectedElement={selectedElement}
              setSelectedElement={setSelectedElement}
              browserId={browserId}
              detectElements={detectElements}
              screenshot={screenshot}
            />
          )}

          {activeTab === 'accounts' && (
            <AccountsTab
              accounts={accounts}
              setAccounts={setAccounts}
              selectedAccount={selectedAccount}
              setSelectedAccount={setSelectedAccount}
              showAccountManager={showAccountManager}
              setShowAccountManager={setShowAccountManager}
              loadAccounts={loadAccounts}
            />
          )}

          {activeTab === 'debug' && (
            <DebugTab
              breakpoints={breakpoints}
              setBreakpoints={setBreakpoints}
              currentStep={currentStep}
              setCurrentStep={setCurrentStep}
              variables={variables}
              setVariables={setVariables}
              stepMode={stepMode}
              setStepMode={setStepMode}
              automationStatus={automationStatus}
              executionProgress={executionProgress}
              logs={filteredLogs}
            />
          )}

          {activeTab === 'metrics' && (
            <MetricsTab
              metrics={metrics}
              logs={logs}
            />
          )}

          {activeTab === 'library' && (
            <LibraryTab
              scripts={scripts}
              loadScripts={loadScripts}
            />
          )}
        </div>
      </div>
    </BasePanel>
  )
}

// ===== TAB COMPONENTS =====

interface BrowserTabProps {
  browserId: string | null
  browserUrl: string
  setBrowserUrl: (url: string) => void
  screenshot: string | null
  navigateToUrl: (url: string) => Promise<void>
  automationStatus: 'idle' | 'running' | 'paused' | 'error'
  executionProgress: { currentStep: number; totalSteps: number; stepName: string; progress: number } | null
  selectedAccount: string | null
  setSelectedAccount: (id: string | null) => void
  selectedScript: string | null
  setSelectedScript: (id: string | null) => void
  accounts: ChatAccount[]
  scripts: AutomationScript[]
  executeScript: () => Promise<void>
  pauseExecution: () => Promise<void>
  resumeExecution: () => Promise<void>
  stopExecution: () => Promise<void>
  logs: AutomationLog[]
  logFilter: 'all' | 'LOG' | 'SUCCESS' | 'WARN' | 'ERROR' | 'DEBUG'
  setLogFilter: (filter: 'all' | 'LOG' | 'SUCCESS' | 'WARN' | 'ERROR' | 'DEBUG') => void
  addLog: (level: AutomationLog['level'], message: string, data?: any, step?: number, selector?: string) => void
}

const BrowserTab: React.FC<BrowserTabProps> = ({
  browserId,
  browserUrl,
  setBrowserUrl,
  screenshot,
  navigateToUrl,
  automationStatus,
  executionProgress,
  selectedAccount,
  setSelectedAccount,
  selectedScript,
  setSelectedScript,
  accounts,
  scripts,
  executeScript,
  pauseExecution,
  resumeExecution,
  stopExecution,
  logs,
  logFilter,
  setLogFilter,
  addLog
}) => {
  const iframeRef = useRef<HTMLIFrameElement>(null)
  const [browserViewportUrl, setBrowserViewportUrl] = useState<string | null>(null)
  const [useIframe, setUseIframe] = useState(true)
  const [iframeKey, setIframeKey] = useState(0)
  const isEmbeddableViewportUrl = (url: string | null | undefined): url is string =>
    !!url && /^https?:\/\//i.test(url)

  // Get browser viewport URL from backend
  useEffect(() => {
    if (browserId) {
      // Try to get viewport URL from backend (CDP websocket or proxy URL)
      const getViewportUrl = async () => {
        try {
          const response = await fetch(`http://localhost:5002/api/browser/viewport?browserId=${browserId}`)
          if (response.ok) {
            const data = await response.json()
            if (isEmbeddableViewportUrl(data.viewportUrl)) {
              setBrowserViewportUrl(data.viewportUrl as string)
              setUseIframe(true)
              addLog('SUCCESS', 'Using backend viewport URL')
              return
            }
          }
          // Default fallback: screenshot mode. Direct URL iframe can still be manually toggled.
          setBrowserViewportUrl(null)
          setUseIframe(false)
          addLog('LOG', 'Using screenshot mode (backend viewport not available)')
        } catch (err) {
          console.error('Failed to get viewport URL, using screenshot mode:', err)
          setBrowserViewportUrl(null)
          setUseIframe(false)
          addLog('WARN', 'Backend viewport unavailable, using screenshot mode')
        }
      }
      getViewportUrl()
    } else {
      setBrowserViewportUrl(null)
    }
  }, [browserId, addLog])

  // Update iframe URL when browserUrl changes (for direct URL mode)
  useEffect(() => {
    if (browserId && browserUrl && useIframe) {
      // If we're using direct URL mode (not backend viewport), update the iframe
      const isBackendViewport = browserViewportUrl && browserViewportUrl.startsWith('http://localhost:5002')
      if (!isBackendViewport && browserViewportUrl !== browserUrl) {
        setBrowserViewportUrl(browserUrl)
        setIframeKey(prev => prev + 1) // Force iframe reload
        addLog('LOG', `Navigating iframe to: ${browserUrl}`)
      }
    }
  }, [browserUrl, browserId, browserViewportUrl, useIframe, addLog])

  return (
    <div className="flex flex-col h-full gap-2 p-2">
      {/* Browser View - Fully Operational */}
      {browserId ? (
        <div className="flex-1 border border-gray-700 rounded bg-gray-900 min-h-[400px] relative overflow-hidden flex flex-col">
          {/* Browser Chrome - Address Bar */}
          <div className="flex items-center justify-between p-2 border-b border-gray-700 bg-gray-800 flex-shrink-0">
            <div className="flex items-center gap-2 flex-1">
              <button
                onClick={() => navigateToUrl(browserUrl)}
                className="p-1 hover:bg-gray-700 rounded transition-colors"
                title="Refresh"
              >
                <RefreshCw className="w-4 h-4 text-gray-400" />
              </button>
              <input
                type="text"
                value={browserUrl}
                onChange={(e) => setBrowserUrl(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    navigateToUrl(browserUrl)
                  }
                }}
                className="flex-1 px-3 py-1.5 bg-gray-900 border border-gray-700 rounded text-sm text-gray-300 focus:outline-none focus:border-blue-500"
                placeholder="Enter URL..."
              />
            </div>
            <div className="flex items-center gap-1 ml-2">
              <button
                onClick={() => {
                  setUseIframe(!useIframe)
                  if (!useIframe && browserUrl) {
                    // When switching to iframe, update the URL
                    setBrowserViewportUrl(browserUrl)
                    setIframeKey(prev => prev + 1)
                  }
                }}
                className={`px-2 py-1 text-xs rounded transition-colors ${useIframe
                  ? 'bg-green-900/30 text-green-400 border border-green-700/50'
                  : 'bg-gray-800 text-gray-400 hover:text-gray-300 border border-gray-700'
                  }`}
                title={useIframe ? 'Live browser view (switch to screenshot)' : 'Screenshot view (switch to live)'}
              >
                {useIframe ? (
                  <>
                    <Monitor className="w-3 h-3 inline mr-1" />
                    Live
                  </>
                ) : (
                  <>
                    <Camera className="w-3 h-3 inline mr-1" />
                    Screenshot
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Browser Content - Iframe or Screenshot */}
          <div className="flex-1 relative overflow-hidden bg-white">
            {useIframe && browserViewportUrl ? (
              <div className="w-full h-full relative">
                <iframe
                  key={iframeKey}
                  ref={iframeRef}
                  src={browserViewportUrl}
                  className="w-full h-full border-0"
                  sandbox="allow-same-origin allow-scripts allow-forms allow-popups allow-modals allow-top-navigation allow-downloads"
                  allow="clipboard-read; clipboard-write; geolocation; microphone; camera; fullscreen"
                  title="Browser Viewport"
                  style={{
                    background: 'white',
                    minHeight: '100%',
                    display: 'block'
                  }}
                  onLoad={() => {
                    addLog('SUCCESS', `Browser viewport loaded: ${browserViewportUrl}`)
                  }}
                  onError={(e) => {
                    console.error('Iframe load error:', e)
                    addLog('WARN', 'Failed to load browser viewport, falling back to screenshot')
                    setUseIframe(false)
                  }}
                />
                {/* Loading indicator */}
                {iframeKey > 0 && (
                  <div className="absolute top-2 left-2 px-2 py-1 bg-blue-900/90 border border-blue-700 rounded text-xs text-blue-300 animate-pulse">
                    Loading...
                  </div>
                )}
              </div>
            ) : screenshot ? (
              <div className="relative w-full h-full overflow-auto bg-gray-950">
                <img
                  src={screenshot}
                  alt="Browser screenshot"
                  className="w-full h-auto"
                  style={{ maxHeight: '100%', objectFit: 'contain' }}
                />
                {/* Overlay to indicate this is a screenshot */}
                <div className="absolute top-2 right-2 px-2 py-1 bg-gray-900/90 border border-gray-700 rounded text-xs text-gray-400">
                  Screenshot View
                </div>
              </div>
            ) : (
              <div className="p-4 text-center text-gray-400 text-sm h-full flex items-center justify-center">
                <div>
                  <Globe className="w-12 h-12 mx-auto mb-2 opacity-50 animate-pulse" />
                  <p>Loading browser view...</p>
                </div>
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="flex-1 border border-gray-700 rounded bg-gray-900 flex items-center justify-center min-h-[400px]">
          <div className="text-center text-gray-400">
            <Globe className="w-12 h-12 mx-auto mb-2 opacity-50" />
            <p className="text-sm">No browser instance</p>
            <p className="text-xs mt-1">Launch browser to start automation</p>
          </div>
        </div>
      )}

      {/* Automation Controls */}
      <div className="border border-gray-700 rounded p-3 bg-gray-800/50 space-y-3">
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-xs text-gray-400 mb-1 block">Account</label>
            <select
              value={selectedAccount || ''}
              onChange={(e) => setSelectedAccount(e.target.value || null)}
              className="w-full px-2 py-1.5 bg-gray-800 border border-gray-700 rounded text-sm text-gray-300"
            >
              <option value="">None</option>
              {accounts.map(acc => (
                <option key={acc.id} value={acc.id}>
                  {acc.displayName || acc.email || acc.id} ({acc.provider})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-xs text-gray-400 mb-1 block">Script</label>
            <select
              value={selectedScript || ''}
              onChange={(e) => setSelectedScript(e.target.value || null)}
              className="w-full px-2 py-1.5 bg-gray-800 border border-gray-700 rounded text-sm text-gray-300"
            >
              <option value="">Select script...</option>
              {scripts.map(script => (
                <option key={script.id} value={script.id}>
                  {script.name} ({script.provider})
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Execution Controls */}
        {browserId && (
          <div className="flex items-center gap-2 pt-2 border-t border-gray-700">
            {automationStatus === 'idle' && (
              <button
                onClick={executeScript}
                disabled={!selectedScript}
                className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-700 disabled:cursor-not-allowed rounded text-sm flex items-center justify-center gap-2 font-medium"
              >
                <Play className="w-4 h-4" />
                Execute Script
              </button>
            )}
            {automationStatus === 'running' && (
              <>
                <button
                  onClick={pauseExecution}
                  className="px-4 py-2 bg-yellow-600 hover:bg-yellow-700 rounded text-sm flex items-center gap-2"
                >
                  <Pause className="w-4 h-4" />
                  Pause
                </button>
                <button
                  onClick={stopExecution}
                  className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded text-sm flex items-center gap-2"
                >
                  <Square className="w-4 h-4" />
                  Stop
                </button>
              </>
            )}
            {automationStatus === 'paused' && (
              <>
                <button
                  onClick={resumeExecution}
                  className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 rounded text-sm flex items-center justify-center gap-2 font-medium"
                >
                  <Play className="w-4 h-4" />
                  Resume
                </button>
                <button
                  onClick={stopExecution}
                  className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded text-sm flex items-center gap-2"
                >
                  <Square className="w-4 h-4" />
                  Stop
                </button>
              </>
            )}
          </div>
        )}

        {/* Execution Progress */}
        {executionProgress && (
          <div className="pt-2 border-t border-gray-700">
            <div className="flex items-center justify-between text-xs text-gray-400 mb-2">
              <span className="font-medium">{executionProgress.stepName || 'Executing...'}</span>
              <span>{executionProgress.currentStep} / {executionProgress.totalSteps}</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all"
                style={{ width: `${executionProgress.progress * 100}%` }}
              />
            </div>
          </div>
        )}
      </div>

      {/* Advanced Logs */}
      <div className="flex-1 border border-gray-700 rounded bg-gray-900 overflow-hidden flex flex-col min-h-[150px]">
        <div className="flex items-center justify-between p-2 border-b border-gray-700 bg-gray-800">
          <h4 className="text-xs font-semibold text-gray-300 flex items-center gap-2">
            <Activity className="w-4 h-4" />
            Execution Logs
          </h4>
          <div className="flex items-center gap-2">
            <select
              value={logFilter}
              onChange={(e) => setLogFilter(e.target.value as any)}
              className="px-2 py-1 bg-gray-800 border border-gray-700 rounded text-xs text-gray-300"
            >
              <option value="all">All</option>
              <option value="LOG">Log</option>
              <option value="SUCCESS">Success</option>
              <option value="WARN">Warning</option>
              <option value="ERROR">Error</option>
              <option value="DEBUG">Debug</option>
            </select>
            <button
              onClick={() => addLog('LOG', 'Logs cleared')}
              className="text-xs text-gray-400 hover:text-gray-300"
            >
              Clear
            </button>
          </div>
        </div>
        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {logs.length === 0 ? (
            <div className="text-xs text-gray-500 text-center py-8">No logs yet</div>
          ) : (
            logs.map((log, index) => (
              <div
                key={index}
                className={`text-xs p-2 rounded border-l-2 ${log.level === 'ERROR' ? 'text-red-400 bg-red-900/20 border-red-500' :
                  log.level === 'WARN' ? 'text-yellow-400 bg-yellow-900/20 border-yellow-500' :
                    log.level === 'SUCCESS' ? 'text-green-400 bg-green-900/20 border-green-500' :
                      log.level === 'DEBUG' ? 'text-blue-400 bg-blue-900/20 border-blue-500' :
                        'text-gray-400 bg-gray-800/50 border-gray-600'
                  }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <span className="text-gray-500 text-[10px]">
                      {new Date(log.timestamp).toLocaleTimeString()}
                    </span>
                    {log.step && (
                      <span className="ml-2 text-gray-500 text-[10px]">Step {log.step}</span>
                    )}
                    <div className="mt-1 font-mono">{log.message}</div>
                    {log.selector && (
                      <div className="mt-1 text-[10px] text-gray-500">Selector: {log.selector}</div>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
