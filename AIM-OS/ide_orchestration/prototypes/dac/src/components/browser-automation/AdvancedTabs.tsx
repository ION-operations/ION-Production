// Advanced Tab Components for Browser Automation Panel
// Comprehensive implementations for Scripts, Recorder, Inspector, Accounts, Debug, Metrics, Library tabs

import React, { useState, useCallback, useRef, useEffect } from 'react'
import ReactFlow, { 
  Node, 
  Edge, 
  Background, 
  Controls, 
  MiniMap, 
  useNodesState, 
  useEdgesState, 
  Connection, 
  addEdge,
  MarkerType
} from 'reactflow'
import 'reactflow/dist/style.css'
import {
  Play,
  Square,
  Pause,
  Plus,
  Save,
  Trash2,
  Edit,
  Copy,
  X,
  Check,
  Search,
  Filter,
  Download,
  Upload,
  Eye,
  MousePointer,
  Keyboard,
  Target,
  Camera,
  Bug,
  SkipForward,
  SkipBack,
  PlayCircle,
  StopCircle,
  BarChart3,
  TrendingUp,
  TrendingDown,
  Clock,
  Activity,
  AlertCircle,
  CheckCircle,
  Database,
  BookOpen,
  FileText,
  Code,
  Zap,
  Layers,
  Settings,
  Wand2,
  Monitor,
  Network,
  Globe,
  User,
  Lock,
  Mail,
  Key
} from 'lucide-react'

// ===== SCRIPTS TAB - Visual Script Builder =====

interface ScriptsTabProps {
  scripts: any[]
  scriptSearchQuery: string
  setScriptSearchQuery: (query: string) => void
  selectedScript: string | null
  setSelectedScript: (id: string | null) => void
  scriptNodes: any[]
  setScriptNodes: (nodes: any[]) => void
  scriptEdges: any[]
  setScriptEdges: (edges: any[]) => void
  selectedNode: string | null
  setSelectedNode: (id: string | null) => void
  editingScript: any
  setEditingScript: (script: any) => void
  showScriptEditor: boolean
  setShowScriptEditor: (show: boolean) => void
  loadScripts: () => Promise<void>
}

export const ScriptsTab: React.FC<ScriptsTabProps> = ({
  scripts,
  scriptSearchQuery,
  setScriptSearchQuery,
  selectedScript,
  setSelectedScript,
  scriptNodes,
  setScriptNodes,
  scriptEdges,
  setScriptEdges,
  selectedNode,
  setSelectedNode,
  editingScript,
  setEditingScript,
  showScriptEditor,
  setShowScriptEditor,
  loadScripts
}) => {
  const [nodes, setNodes, onNodesChange] = useNodesState(scriptNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(scriptEdges)
  const [nodeTypes, setNodeTypes] = useState<any>({})
  const [showNodePalette, setShowNodePalette] = useState(false)
  const [viewMode, setViewMode] = useState<'visual' | 'code'>('visual')

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  )

  const nodeTypesLibrary = [
    { type: 'navigate', label: 'Navigate', icon: Globe, color: '#3b82f6' },
    { type: 'click', label: 'Click', icon: MousePointer, color: '#10b981' },
    { type: 'type', label: 'Type', icon: Keyboard, color: '#f59e0b' },
    { type: 'wait', label: 'Wait', icon: Clock, color: '#8b5cf6' },
    { type: 'extract', label: 'Extract', icon: Download, color: '#ec4899' },
    { type: 'screenshot', label: 'Screenshot', icon: Camera, color: '#06b6d4' },
    { type: 'condition', label: 'Condition', icon: Code, color: '#f97316' },
    { type: 'loop', label: 'Loop', icon: Layers, color: '#6366f1' },
    { type: 'upload', label: 'Upload', icon: Upload, color: '#14b8a6' }
  ]

  const addNode = (nodeType: string) => {
    const newNode: Node = {
      id: `node-${Date.now()}`,
      type: 'default',
      position: { x: Math.random() * 400, y: Math.random() * 400 },
      data: {
        label: nodeTypesLibrary.find(n => n.type === nodeType)?.label || nodeType,
        type: nodeType,
        config: {}
      },
      style: {
        background: nodeTypesLibrary.find(n => n.type === nodeType)?.color || '#6366f1',
        color: '#fff',
        border: '1px solid #222',
        borderRadius: '8px',
        padding: '10px',
        minWidth: '120px'
      }
    }
    setNodes((nds) => [...nds, newNode])
    setShowNodePalette(false)
  }

  return (
    <div className="flex flex-col h-full">
      {/* Toolbar */}
      <div className="flex items-center justify-between p-2 border-b border-gray-700 bg-gray-800">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setViewMode(viewMode === 'visual' ? 'code' : 'visual')}
            className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-xs flex items-center gap-1"
          >
            {viewMode === 'visual' ? <Code className="w-3 h-3" /> : <Layers className="w-3 h-3" />}
            {viewMode === 'visual' ? 'Code View' : 'Visual View'}
          </button>
          <button
            onClick={() => setShowNodePalette(!showNodePalette)}
            className="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-xs flex items-center gap-1"
          >
            <Plus className="w-3 h-3" />
            Add Node
          </button>
          <button
            onClick={() => {}}
            className="px-3 py-1 bg-green-600 hover:bg-green-700 rounded text-xs flex items-center gap-1"
          >
            <Save className="w-3 h-3" />
            Save Script
          </button>
        </div>
        <div className="flex items-center gap-2">
          <input
            type="text"
            value={scriptSearchQuery}
            onChange={(e) => setScriptSearchQuery(e.target.value)}
            placeholder="Search scripts..."
            className="px-2 py-1 bg-gray-800 border border-gray-700 rounded text-xs text-gray-300 w-48"
          />
        </div>
      </div>

      {/* Node Palette */}
      {showNodePalette && (
        <div className="absolute z-50 bg-gray-800 border border-gray-700 rounded-lg shadow-xl p-2 m-2">
          <div className="text-xs font-semibold text-gray-300 mb-2">Action Nodes</div>
          <div className="grid grid-cols-2 gap-1">
            {nodeTypesLibrary.map(nodeType => {
              const Icon = nodeType.icon
              return (
                <button
                  key={nodeType.type}
                  onClick={() => addNode(nodeType.type)}
                  className="px-2 py-1 text-xs flex items-center gap-1 hover:bg-gray-700 rounded"
                  style={{ color: nodeType.color }}
                >
                  <Icon className="w-3 h-3" />
                  {nodeType.label}
                </button>
              )
            })}
          </div>
        </div>
      )}

      {/* Visual Script Builder */}
      {viewMode === 'visual' ? (
        <div className="flex-1 relative">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={(e, node) => setSelectedNode(node.id)}
            fitView
          >
            <Background />
            <Controls />
            <MiniMap />
          </ReactFlow>
          
          {/* Node Properties Panel */}
          {selectedNode && (
            <div className="absolute top-4 right-4 w-64 bg-gray-800 border border-gray-700 rounded-lg p-3 shadow-xl">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold text-gray-300">Node Properties</span>
                <button
                  onClick={() => setSelectedNode(null)}
                  className="text-gray-400 hover:text-gray-300"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
              <div className="space-y-2">
                <div>
                  <label className="text-xs text-gray-400">Selector</label>
                  <input
                    type="text"
                    className="w-full px-2 py-1 bg-gray-900 border border-gray-700 rounded text-xs text-gray-300"
                    placeholder="CSS selector..."
                  />
                </div>
                <div>
                  <label className="text-xs text-gray-400">Value</label>
                  <input
                    type="text"
                    className="w-full px-2 py-1 bg-gray-900 border border-gray-700 rounded text-xs text-gray-300"
                    placeholder="Value..."
                  />
                </div>
                <div>
                  <label className="text-xs text-gray-400">Timeout (ms)</label>
                  <input
                    type="number"
                    className="w-full px-2 py-1 bg-gray-900 border border-gray-700 rounded text-xs text-gray-300"
                    placeholder="5000"
                  />
                </div>
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="flex-1 p-4">
          <textarea
            className="w-full h-full bg-gray-900 border border-gray-700 rounded p-3 font-mono text-xs text-gray-300"
            placeholder="// JSON Script Editor..."
            defaultValue={JSON.stringify({ actions: [] }, null, 2)}
          />
        </div>
      )}

      {/* Script List Sidebar */}
      <div className="w-64 border-l border-gray-700 bg-gray-800 p-2 overflow-y-auto">
        <div className="text-xs font-semibold text-gray-300 mb-2">Scripts ({scripts.length})</div>
        <div className="space-y-1">
          {scripts.map(script => (
            <div
              key={script.id}
              onClick={() => setSelectedScript(script.id)}
              className={`p-2 rounded cursor-pointer text-xs ${
                selectedScript === script.id
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              <div className="font-medium">{script.name}</div>
              <div className="text-[10px] opacity-75">{script.provider}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// ===== RECORDER TAB - Macro Recorder =====

interface RecorderTabProps {
  isRecording: boolean
  startRecording: () => void
  stopRecording: () => void
  recordedActions: any[]
  setRecordedActions: (actions: any[]) => void
  browserId: string | null
}

export const RecorderTab: React.FC<RecorderTabProps> = ({
  isRecording,
  startRecording,
  stopRecording,
  recordedActions,
  setRecordedActions,
  browserId
}) => {
  return (
    <div className="flex flex-col h-full p-4">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-semibold text-gray-300 mb-1">Macro Recorder</h3>
          <p className="text-xs text-gray-400">Record browser actions and convert to automation scripts</p>
        </div>
        {!isRecording ? (
          <button
            onClick={startRecording}
            disabled={!browserId}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 disabled:bg-gray-700 rounded text-sm flex items-center gap-2"
          >
            <PlayCircle className="w-4 h-4" />
            Start Recording
          </button>
        ) : (
          <button
            onClick={stopRecording}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded text-sm flex items-center gap-2 animate-pulse"
          >
            <StopCircle className="w-4 h-4" />
            Stop Recording ({recordedActions.length})
          </button>
        )}
      </div>

      {isRecording && (
        <div className="mb-4 p-3 bg-red-900/20 border border-red-700 rounded">
          <div className="flex items-center gap-2 text-red-400 text-sm">
            <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
            Recording... All browser interactions will be captured
          </div>
        </div>
      )}

      <div className="flex-1 border border-gray-700 rounded bg-gray-900 overflow-y-auto">
        {recordedActions.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-400">
            <MousePointer className="w-12 h-12 mb-2 opacity-50" />
            <p className="text-sm">No actions recorded</p>
            <p className="text-xs mt-1">Start recording to capture browser interactions</p>
          </div>
        ) : (
          <div className="p-2 space-y-2">
            {recordedActions.map((action, index) => (
              <div
                key={index}
                className="p-3 bg-gray-800 rounded border border-gray-700"
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-500">#{index + 1}</span>
                    <span className="text-xs font-medium text-gray-300">{action.type}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <button className="p-1 hover:bg-gray-700 rounded">
                      <Edit className="w-3 h-3 text-gray-400" />
                    </button>
                    <button className="p-1 hover:bg-gray-700 rounded">
                      <Trash2 className="w-3 h-3 text-gray-400" />
                    </button>
                  </div>
                </div>
                <div className="text-xs text-gray-400 font-mono">
                  {action.selector && <div>Selector: {action.selector}</div>}
                  {action.value && <div>Value: {action.value}</div>}
                  {action.url && <div>URL: {action.url}</div>}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {recordedActions.length > 0 && (
        <div className="mt-4 flex items-center gap-2">
          <button className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 rounded text-sm flex items-center justify-center gap-2">
            <Save className="w-4 h-4" />
            Save as Script
          </button>
          <button
            onClick={() => setRecordedActions([])}
            className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded text-sm flex items-center gap-2"
          >
            <Trash2 className="w-4 h-4" />
            Clear
          </button>
        </div>
      )}
    </div>
  )
}

// ===== INSPECTOR TAB - Element Inspector =====

interface InspectorTabProps {
  inspectorMode: boolean
  toggleInspector: () => void
  detectedElements: any[]
  setDetectedElements: (elements: any[]) => void
  hoveredElement: any
  setHoveredElement: (element: any) => void
  selectedElement: any
  setSelectedElement: (element: any) => void
  browserId: string | null
  detectElements: () => Promise<void>
  screenshot: string | null
}

export const InspectorTab: React.FC<InspectorTabProps> = ({
  inspectorMode,
  toggleInspector,
  detectedElements,
  setDetectedElements,
  hoveredElement,
  setHoveredElement,
  selectedElement,
  setSelectedElement,
  browserId,
  detectElements,
  screenshot
}) => {
  return (
    <div className="flex flex-col h-full">
      <div className="p-3 border-b border-gray-700 bg-gray-800">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h3 className="text-sm font-semibold text-gray-300 mb-1">Element Inspector</h3>
            <p className="text-xs text-gray-400">Detect and inspect page elements visually</p>
          </div>
          <button
            onClick={toggleInspector}
            className={`px-4 py-2 rounded text-sm flex items-center gap-2 ${
              inspectorMode
                ? 'bg-green-600 hover:bg-green-700'
                : 'bg-gray-700 hover:bg-gray-600'
            }`}
          >
            <Eye className="w-4 h-4" />
            {inspectorMode ? 'Inspector Active' : 'Enable Inspector'}
          </button>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={detectElements}
            disabled={!browserId}
            className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 rounded text-xs flex items-center gap-1"
          >
            <Target className="w-3 h-3" />
            Detect Elements
          </button>
          <button
            className="px-3 py-1.5 bg-gray-700 hover:bg-gray-600 rounded text-xs flex items-center gap-1"
          >
            <Wand2 className="w-3 h-3" />
            Smart Selector
          </button>
        </div>
      </div>

      <div className="flex-1 flex">
        {/* Screenshot View */}
        <div className="flex-1 border-r border-gray-700 p-3 overflow-auto">
          {screenshot ? (
            <div className="relative">
              <img src={screenshot} alt="Page screenshot" className="max-w-full" />
              {hoveredElement && (
                <div
                  className="absolute border-2 border-blue-500 bg-blue-500/20 pointer-events-none"
                  style={{
                    left: hoveredElement.bounds.x,
                    top: hoveredElement.bounds.y,
                    width: hoveredElement.bounds.width,
                    height: hoveredElement.bounds.height
                  }}
                />
              )}
            </div>
          ) : (
            <div className="flex items-center justify-center h-full text-gray-400">
              <div className="text-center">
                <Monitor className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p className="text-sm">No screenshot available</p>
                <p className="text-xs mt-1">Launch browser to inspect elements</p>
              </div>
            </div>
          )}
        </div>

        {/* Element List */}
        <div className="w-80 bg-gray-800 p-3 overflow-y-auto">
          <div className="text-xs font-semibold text-gray-300 mb-2">
            Detected Elements ({detectedElements.length})
          </div>
          <div className="space-y-2">
            {detectedElements.map((element, index) => (
              <div
                key={index}
                onClick={() => setSelectedElement(element)}
                onMouseEnter={() => setHoveredElement(element)}
                onMouseLeave={() => setHoveredElement(null)}
                className={`p-2 rounded cursor-pointer border ${
                  selectedElement === element
                    ? 'bg-blue-600 border-blue-500'
                    : 'bg-gray-700 border-gray-600 hover:bg-gray-600'
                }`}
              >
                <div className="text-xs font-medium text-gray-200 mb-1">
                  {element.tag.toUpperCase()}
                </div>
                <div className="text-[10px] text-gray-400 font-mono break-all">
                  {element.selector}
                </div>
                {element.text && (
                  <div className="text-[10px] text-gray-500 mt-1 truncate">
                    "{element.text}"
                  </div>
                )}
                <div className="text-[10px] text-gray-500 mt-1">
                  Confidence: {Math.round(element.confidence * 100)}%
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Element Details */}
        {selectedElement && (
          <div className="w-80 border-l border-gray-700 bg-gray-800 p-3 overflow-y-auto">
            <div className="text-xs font-semibold text-gray-300 mb-3">Element Details</div>
            <div className="space-y-3">
              <div>
                <div className="text-[10px] text-gray-400 mb-1">Selector</div>
                <div className="p-2 bg-gray-900 rounded text-xs font-mono text-gray-300 break-all">
                  {selectedElement.selector}
                </div>
              </div>
              <div>
                <div className="text-[10px] text-gray-400 mb-1">XPath</div>
                <div className="p-2 bg-gray-900 rounded text-xs font-mono text-gray-300 break-all">
                  {selectedElement.xpath}
                </div>
              </div>
              <div>
                <div className="text-[10px] text-gray-400 mb-1">Attributes</div>
                <div className="p-2 bg-gray-900 rounded text-xs font-mono text-gray-300">
                  {JSON.stringify(selectedElement.attributes, null, 2)}
                </div>
              </div>
              <div>
                <div className="text-[10px] text-gray-400 mb-1">Bounds</div>
                <div className="text-xs text-gray-300">
                  x: {selectedElement.bounds.x}, y: {selectedElement.bounds.y}
                  <br />
                  w: {selectedElement.bounds.width}, h: {selectedElement.bounds.height}
                </div>
              </div>
              <button className="w-full px-3 py-2 bg-blue-600 hover:bg-blue-700 rounded text-xs">
                Use This Selector
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

// ===== ACCOUNTS TAB - Account Manager =====

interface AccountsTabProps {
  accounts: any[]
  setAccounts: (accounts: any[]) => void
  selectedAccount: string | null
  setSelectedAccount: (id: string | null) => void
  showAccountManager: boolean
  setShowAccountManager: (show: boolean) => void
  loadAccounts: () => Promise<void>
}

export const AccountsTab: React.FC<AccountsTabProps> = ({
  accounts,
  setAccounts,
  selectedAccount,
  setSelectedAccount,
  showAccountManager,
  setShowAccountManager,
  loadAccounts
}) => {
  const [showAddAccount, setShowAddAccount] = useState(false)
  const [newAccount, setNewAccount] = useState({
    provider: 'chatgpt',
    email: '',
    displayName: '',
    password: ''
  })

  return (
    <div className="flex flex-col h-full p-4">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-semibold text-gray-300 mb-1">Account Manager</h3>
          <p className="text-xs text-gray-400">Manage saved accounts and sessions</p>
        </div>
        <button
          onClick={() => setShowAddAccount(true)}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          Add Account
        </button>
      </div>

      <div className="flex-1 border border-gray-700 rounded bg-gray-900 overflow-y-auto">
        {accounts.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-400">
            <Database className="w-12 h-12 mb-2 opacity-50" />
            <p className="text-sm">No accounts saved</p>
            <p className="text-xs mt-1">Add an account to enable session persistence</p>
          </div>
        ) : (
          <div className="p-2 space-y-2">
            {accounts.map(account => (
              <div
                key={account.id}
                onClick={() => setSelectedAccount(account.id)}
                className={`p-3 rounded cursor-pointer border ${
                  selectedAccount === account.id
                    ? 'bg-blue-600 border-blue-500'
                    : 'bg-gray-800 border-gray-700 hover:bg-gray-700'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 bg-gray-700 rounded flex items-center justify-center">
                      <User className="w-4 h-4 text-gray-400" />
                    </div>
                    <div>
                      <div className="text-sm font-medium text-gray-200">
                        {account.displayName || account.email || 'Unnamed Account'}
                      </div>
                      <div className="text-xs text-gray-400 capitalize">{account.provider}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-1">
                    {account.sessionValid && (
                      <CheckCircle className="w-4 h-4 text-green-400" />
                    )}
                    <button className="p-1 hover:bg-gray-700 rounded">
                      <Edit className="w-3 h-3 text-gray-400" />
                    </button>
                    <button className="p-1 hover:bg-gray-700 rounded">
                      <Trash2 className="w-3 h-3 text-gray-400" />
                    </button>
                  </div>
                </div>
                {account.lastUsed && (
                  <div className="text-xs text-gray-500">
                    Last used: {new Date(account.lastUsed).toLocaleString()}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Add Account Modal */}
      {showAddAccount && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-6 w-96">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-semibold text-gray-300">Add Account</h3>
              <button
                onClick={() => setShowAddAccount(false)}
                className="text-gray-400 hover:text-gray-300"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="space-y-3">
              <div>
                <label className="text-xs text-gray-400 mb-1 block">Provider</label>
                <select
                  value={newAccount.provider}
                  onChange={(e) => setNewAccount({ ...newAccount, provider: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded text-sm text-gray-300"
                >
                  <option value="chatgpt">ChatGPT</option>
                  <option value="claude">Claude</option>
                  <option value="gemini">Gemini</option>
                  <option value="custom">Custom</option>
                </select>
              </div>
              <div>
                <label className="text-xs text-gray-400 mb-1 block">Email</label>
                <input
                  type="email"
                  value={newAccount.email}
                  onChange={(e) => setNewAccount({ ...newAccount, email: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded text-sm text-gray-300"
                  placeholder="user@example.com"
                />
              </div>
              <div>
                <label className="text-xs text-gray-400 mb-1 block">Display Name</label>
                <input
                  type="text"
                  value={newAccount.displayName}
                  onChange={(e) => setNewAccount({ ...newAccount, displayName: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded text-sm text-gray-300"
                  placeholder="Optional"
                />
              </div>
              <div>
                <label className="text-xs text-gray-400 mb-1 block">Password</label>
                <input
                  type="password"
                  value={newAccount.password}
                  onChange={(e) => setNewAccount({ ...newAccount, password: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded text-sm text-gray-300"
                  placeholder="Will be encrypted"
                />
              </div>
              <div className="flex items-center gap-2 pt-2">
                <button
                  onClick={() => {
                    // TODO: Save account
                    setShowAddAccount(false)
                    loadAccounts()
                  }}
                  className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 rounded text-sm"
                >
                  Save Account
                </button>
                <button
                  onClick={() => setShowAddAccount(false)}
                  className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded text-sm"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// ===== DEBUG TAB - Debug Tools =====

interface DebugTabProps {
  breakpoints: Set<number>
  setBreakpoints: (breakpoints: Set<number>) => void
  currentStep: number | null
  setCurrentStep: (step: number | null) => void
  variables: Record<string, any>
  setVariables: (vars: Record<string, any>) => void
  stepMode: boolean
  setStepMode: (mode: boolean) => void
  automationStatus: 'idle' | 'running' | 'paused' | 'error'
  executionProgress: any
  logs: any[]
}

export const DebugTab: React.FC<DebugTabProps> = ({
  breakpoints,
  setBreakpoints,
  currentStep,
  setCurrentStep,
  variables,
  setVariables,
  stepMode,
  setStepMode,
  automationStatus,
  executionProgress,
  logs
}) => {
  const toggleBreakpoint = (step: number) => {
    const newBreakpoints = new Set(breakpoints)
    if (newBreakpoints.has(step)) {
      newBreakpoints.delete(step)
    } else {
      newBreakpoints.add(step)
    }
    setBreakpoints(newBreakpoints)
  }

  return (
    <div className="flex flex-col h-full">
      <div className="p-3 border-b border-gray-700 bg-gray-800">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h3 className="text-sm font-semibold text-gray-300 mb-1">Debug Tools</h3>
            <p className="text-xs text-gray-400">Step-through execution, breakpoints, and variable inspection</p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setStepMode(!stepMode)}
              className={`px-3 py-1.5 rounded text-xs flex items-center gap-1 ${
                stepMode ? 'bg-green-600 hover:bg-green-700' : 'bg-gray-700 hover:bg-gray-600'
              }`}
            >
              <Bug className="w-3 h-3" />
              Step Mode: {stepMode ? 'ON' : 'OFF'}
            </button>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 rounded text-xs flex items-center gap-1">
            <SkipBack className="w-3 h-3" />
            Step Back
          </button>
          <button className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 rounded text-xs flex items-center gap-1">
            <SkipForward className="w-3 h-3" />
            Step Forward
          </button>
          <button className="px-3 py-1.5 bg-gray-700 hover:bg-gray-600 rounded text-xs flex items-center gap-1">
            <Play className="w-3 h-3" />
            Continue
          </button>
        </div>
      </div>

      <div className="flex-1 flex">
        {/* Execution Steps */}
        <div className="w-80 border-r border-gray-700 bg-gray-800 p-3 overflow-y-auto">
          <div className="text-xs font-semibold text-gray-300 mb-2">Execution Steps</div>
          <div className="space-y-1">
            {executionProgress && Array.from({ length: executionProgress.totalSteps }).map((_, index) => {
              const step = index + 1
              const isBreakpoint = breakpoints.has(step)
              const isCurrent = currentStep === step
              return (
                <div
                  key={step}
                  onClick={() => toggleBreakpoint(step)}
                  className={`p-2 rounded cursor-pointer text-xs flex items-center gap-2 ${
                    isCurrent
                      ? 'bg-blue-600 text-white'
                      : isBreakpoint
                      ? 'bg-yellow-600/30 text-yellow-300 border border-yellow-500'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  {isBreakpoint && <div className="w-2 h-2 bg-red-500 rounded-full" />}
                  <span>Step {step}</span>
                  {isCurrent && <span className="ml-auto">▶</span>}
                </div>
              )
            })}
          </div>
        </div>

        {/* Variables & Call Stack */}
        <div className="flex-1 flex flex-col">
          <div className="flex-1 p-3 border-b border-gray-700">
            <div className="text-xs font-semibold text-gray-300 mb-2">Variables</div>
            <div className="space-y-1">
              {Object.entries(variables).map(([key, value]) => (
                <div key={key} className="p-2 bg-gray-800 rounded text-xs">
                  <div className="text-gray-400 font-mono">{key}</div>
                  <div className="text-gray-300 mt-1">{JSON.stringify(value)}</div>
                </div>
              ))}
            </div>
          </div>
          <div className="flex-1 p-3">
            <div className="text-xs font-semibold text-gray-300 mb-2">Call Stack</div>
            <div className="text-xs text-gray-400">No call stack available</div>
          </div>
        </div>
      </div>
    </div>
  )
}

// ===== METRICS TAB - Performance Metrics =====

interface MetricsTabProps {
  metrics: any
  logs: any[]
}

export const MetricsTab: React.FC<MetricsTabProps> = ({ metrics, logs }) => {
  return (
    <div className="flex flex-col h-full p-4">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-300 mb-1">Performance Metrics</h3>
        <p className="text-xs text-gray-400">Track automation execution performance and success rates</p>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="p-4 bg-gray-800 rounded border border-gray-700">
          <div className="text-xs text-gray-400 mb-1">Total Executions</div>
          <div className="text-2xl font-bold text-gray-200">{metrics.totalExecutions}</div>
        </div>
        <div className="p-4 bg-gray-800 rounded border border-gray-700">
          <div className="text-xs text-gray-400 mb-1">Success Rate</div>
          <div className="text-2xl font-bold text-green-400">
            {Math.round(metrics.successRate * 100)}%
          </div>
        </div>
        <div className="p-4 bg-gray-800 rounded border border-gray-700">
          <div className="text-xs text-gray-400 mb-1">Average Duration</div>
          <div className="text-2xl font-bold text-gray-200">{metrics.averageDuration}s</div>
        </div>
        <div className="p-4 bg-gray-800 rounded border border-gray-700">
          <div className="text-xs text-gray-400 mb-1">Error Count</div>
          <div className="text-2xl font-bold text-red-400">{metrics.errorCount}</div>
        </div>
      </div>

      <div className="flex-1 border border-gray-700 rounded bg-gray-900 p-4">
        <div className="text-xs font-semibold text-gray-300 mb-3">Execution History</div>
        <div className="text-xs text-gray-400">Chart visualization would go here</div>
      </div>
    </div>
  )
}

// ===== LIBRARY TAB - Script Library =====

interface LibraryTabProps {
  scripts: any[]
  loadScripts: () => Promise<void>
}

export const LibraryTab: React.FC<LibraryTabProps> = ({ scripts, loadScripts }) => {
  const [searchQuery, setSearchQuery] = useState('')
  const [filterProvider, setFilterProvider] = useState<string>('all')

  const filteredScripts = scripts.filter(script => {
    const matchesSearch = !searchQuery || script.name.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesProvider = filterProvider === 'all' || script.provider === filterProvider
    return matchesSearch && matchesProvider
  })

  return (
    <div className="flex flex-col h-full">
      <div className="p-3 border-b border-gray-700 bg-gray-800">
        <div className="flex items-center gap-2 mb-3">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search scripts..."
            className="flex-1 px-3 py-2 bg-gray-900 border border-gray-700 rounded text-sm text-gray-300"
          />
          <select
            value={filterProvider}
            onChange={(e) => setFilterProvider(e.target.value)}
            className="px-3 py-2 bg-gray-900 border border-gray-700 rounded text-sm text-gray-300"
          >
            <option value="all">All Providers</option>
            <option value="chatgpt">ChatGPT</option>
            <option value="claude">Claude</option>
            <option value="gemini">Gemini</option>
            <option value="custom">Custom</option>
          </select>
        </div>
        <div className="flex items-center gap-2">
          <button className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 rounded text-xs flex items-center gap-1">
            <Plus className="w-3 h-3" />
            Create Script
          </button>
          <button className="px-3 py-1.5 bg-gray-700 hover:bg-gray-600 rounded text-xs flex items-center gap-1">
            <Upload className="w-3 h-3" />
            Import Script
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {filteredScripts.map(script => (
            <div
              key={script.id}
              className="p-4 bg-gray-800 rounded border border-gray-700 hover:border-gray-600 cursor-pointer"
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                  <div className="text-sm font-medium text-gray-200 mb-1">{script.name}</div>
                  <div className="text-xs text-gray-400 capitalize">{script.provider}</div>
                </div>
                <div className="flex items-center gap-1">
                  <button className="p-1 hover:bg-gray-700 rounded">
                    <Edit className="w-3 h-3 text-gray-400" />
                  </button>
                  <button className="p-1 hover:bg-gray-700 rounded">
                    <Copy className="w-3 h-3 text-gray-400" />
                  </button>
                  <button className="p-1 hover:bg-gray-700 rounded">
                    <Trash2 className="w-3 h-3 text-gray-400" />
                  </button>
                </div>
              </div>
              {script.description && (
                <div className="text-xs text-gray-500 mb-2">{script.description}</div>
              )}
              <div className="text-[10px] text-gray-500">
                Created: {new Date(script.createdAt).toLocaleDateString()}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

