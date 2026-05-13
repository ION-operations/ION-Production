/**
 * AIM-OS Orchestration Visualization
 * Dynamic visualization of AIM-OS systems, prompt chains, and agent coordination
 */

import React, { useState, useEffect } from 'react'
import { 
  GitBranch, 
  Network, 
  Zap, 
  Brain, 
  Database, 
  Monitor, 
  Activity,
  Play,
  Pause,
  RotateCcw,
  Settings,
  Eye,
  EyeOff
} from 'lucide-react'

interface SystemNode {
  id: string
  name: string
  type: 'cmc' | 'hhni' | 'vif' | 'seg' | 'apoe' | 'sdfcvf' | 'agent' | 'prompt'
  status: 'active' | 'inactive' | 'processing' | 'error'
  position: { x: number; y: number }
  connections: string[]
  metadata: Record<string, any>
}

interface PromptChain {
  id: string
  name: string
  steps: PromptStep[]
  status: 'running' | 'paused' | 'completed' | 'error'
  currentStep: number
  createdAt: Date
  completedAt?: Date
}

interface PromptStep {
  id: string
  name: string
  type: 'input' | 'processing' | 'output' | 'decision'
  agentId?: string
  systemId?: string
  input: string
  output?: string
  status: 'pending' | 'running' | 'completed' | 'error'
  duration?: number
}

export const AIMOSOrchestration: React.FC = () => {
  const [systems, setSystems] = useState<SystemNode[]>([])
  const [promptChains, setPromptChains] = useState<PromptChain[]>([])
  const [isPlaying, setIsPlaying] = useState(false)
  const [showConnections, setShowConnections] = useState(true)
  const [selectedNode, setSelectedNode] = useState<string | null>(null)
  const [viewMode, setViewMode] = useState<'systems' | 'chains' | 'agents'>('systems')

  useEffect(() => {
    initializeSystems()
    initializePromptChains()
  }, [])

  const initializeSystems = () => {
    const systemNodes: SystemNode[] = [
      {
        id: 'cmc',
        name: 'Context Memory Core',
        type: 'cmc',
        status: 'active',
        position: { x: 100, y: 100 },
        connections: ['hhni', 'vif'],
        metadata: {
          memoryCount: 1247,
          lastAccess: new Date(),
          health: 0.95
        }
      },
      {
        id: 'hhni',
        name: 'Hierarchical Hypergraph Neural Index',
        type: 'hhni',
        status: 'active',
        position: { x: 300, y: 100 },
        connections: ['cmc', 'seg'],
        metadata: {
          nodeCount: 5432,
          connections: 12847,
          health: 0.92
        }
      },
      {
        id: 'vif',
        name: 'Verifiable Intelligence Framework',
        type: 'vif',
        status: 'active',
        position: { x: 100, y: 250 },
        connections: ['cmc', 'apoe'],
        metadata: {
          confidenceScore: 0.87,
          verifications: 342,
          health: 0.89
        }
      },
      {
        id: 'seg',
        name: 'Shared Evidence Graph',
        type: 'seg',
        status: 'processing',
        position: { x: 500, y: 100 },
        connections: ['hhni', 'apoe'],
        metadata: {
          evidenceCount: 892,
          synthesisRate: 0.76,
          health: 0.78
        }
      },
      {
        id: 'apoe',
        name: 'AI-Powered Orchestration Engine',
        type: 'apoe',
        status: 'active',
        position: { x: 300, y: 250 },
        connections: ['vif', 'seg', 'sdfcvf'],
        metadata: {
          activePlans: 12,
          completedTasks: 156,
          health: 0.91
        }
      },
      {
        id: 'sdfcvf',
        name: 'Atomic Evolution Framework',
        type: 'sdfcvf',
        status: 'active',
        position: { x: 500, y: 250 },
        connections: ['apoe'],
        metadata: {
          atomicOperations: 2341,
          evolutionCycles: 45,
          health: 0.94
        }
      },
      {
        id: 'coding-agent',
        name: 'CodeMaster',
        type: 'agent',
        status: 'active',
        position: { x: 100, y: 400 },
        connections: ['apoe'],
        metadata: {
          provider: 'gemini',
          messagesProcessed: 89,
          confidence: 0.85
        }
      },
      {
        id: 'planning-agent',
        name: 'StrategyMind',
        type: 'agent',
        status: 'active',
        position: { x: 300, y: 400 },
        connections: ['apoe'],
        metadata: {
          provider: 'cerebras',
          messagesProcessed: 67,
          confidence: 0.92
        }
      }
    ]

    setSystems(systemNodes)
  }

  const initializePromptChains = () => {
    const chains: PromptChain[] = [
      {
        id: 'chain-1',
        name: 'Code Review & Optimization',
        status: 'running',
        currentStep: 2,
        createdAt: new Date(Date.now() - 300000),
        steps: [
          {
            id: 'step-1',
            name: 'Code Analysis',
            type: 'input',
            agentId: 'coding-agent',
            input: 'Review this React component for performance issues',
            status: 'completed',
            duration: 1200
          },
          {
            id: 'step-2',
            name: 'Pattern Recognition',
            type: 'processing',
            systemId: 'hhni',
            input: 'Identify optimization patterns',
            status: 'running'
          },
          {
            id: 'step-3',
            name: 'Optimization Suggestions',
            type: 'output',
            agentId: 'coding-agent',
            input: 'Generate optimization recommendations',
            status: 'pending'
          }
        ]
      },
      {
        id: 'chain-2',
        name: 'Architecture Planning',
        status: 'paused',
        currentStep: 1,
        createdAt: new Date(Date.now() - 600000),
        steps: [
          {
            id: 'step-1',
            name: 'Requirements Analysis',
            type: 'input',
            agentId: 'planning-agent',
            input: 'Analyze project requirements',
            status: 'completed',
            duration: 2100
          },
          {
            id: 'step-2',
            name: 'Architecture Design',
            type: 'processing',
            systemId: 'apoe',
            input: 'Generate architecture recommendations',
            status: 'pending'
          }
        ]
      }
    ]

    setPromptChains(chains)
  }

  const getNodeIcon = (node: SystemNode) => {
    switch (node.type) {
      case 'cmc': return <Database className="w-5 h-5" />
      case 'hhni': return <Network className="w-5 h-5" />
      case 'vif': return <Monitor className="w-5 h-5" />
      case 'seg': return <Brain className="w-5 h-5" />
      case 'apoe': return <GitBranch className="w-5 h-5" />
      case 'sdfcvf': return <Activity className="w-5 h-5" />
      case 'agent': return <Zap className="w-5 h-5" />
      default: return <Activity className="w-5 h-5" />
    }
  }

  const getNodeColor = (node: SystemNode) => {
    switch (node.status) {
      case 'active': return 'bg-green-600'
      case 'processing': return 'bg-yellow-600'
      case 'inactive': return 'bg-gray-600'
      case 'error': return 'bg-red-600'
      default: return 'bg-gray-600'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'text-green-400'
      case 'paused': return 'text-yellow-400'
      case 'completed': return 'text-blue-400'
      case 'error': return 'text-red-400'
      default: return 'text-gray-400'
    }
  }

  const togglePlayPause = () => {
    setIsPlaying(!isPlaying)
    // Simulate system activity
    if (!isPlaying) {
      // Start simulation
    } else {
      // Pause simulation
    }
  }

  const resetSimulation = () => {
    setIsPlaying(false)
    initializeSystems()
    initializePromptChains()
  }

  return (
    <div className="h-full bg-gray-900 flex flex-col">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-700 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <GitBranch className="w-5 h-5 text-blue-400" />
          <div>
            <h2 className="text-white text-lg font-semibold">AIM-OS Orchestration</h2>
            <p className="text-gray-400 text-sm">Real-time system coordination and prompt chains</p>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          {/* View Mode Toggle */}
          <div className="flex bg-gray-800 rounded-lg p-1">
            <button
              onClick={() => setViewMode('systems')}
              className={`px-3 py-1 text-xs rounded ${
                viewMode === 'systems' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'
              }`}
            >
              Systems
            </button>
            <button
              onClick={() => setViewMode('chains')}
              className={`px-3 py-1 text-xs rounded ${
                viewMode === 'chains' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'
              }`}
            >
              Chains
            </button>
            <button
              onClick={() => setViewMode('agents')}
              className={`px-3 py-1 text-xs rounded ${
                viewMode === 'agents' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'
              }`}
            >
              Agents
            </button>
          </div>

          {/* Controls */}
          <div className="flex items-center gap-1">
            <button
              onClick={togglePlayPause}
              className="p-2 bg-gray-800 hover:bg-gray-700 rounded text-gray-400 hover:text-white"
              title={isPlaying ? 'Pause' : 'Play'}
            >
              {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
            </button>
            <button
              onClick={resetSimulation}
              className="p-2 bg-gray-800 hover:bg-gray-700 rounded text-gray-400 hover:text-white"
              title="Reset"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
            <button
              onClick={() => setShowConnections(!showConnections)}
              className={`p-2 rounded ${
                showConnections ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-400 hover:text-white'
              }`}
              title="Toggle connections"
            >
              {showConnections ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
            </button>
            <button className="p-2 bg-gray-800 hover:bg-gray-700 rounded text-gray-400 hover:text-white">
              <Settings className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-hidden">
        {viewMode === 'systems' && (
          <div className="h-full relative">
            {/* System Nodes */}
            <svg className="w-full h-full">
              {/* Connections */}
              {showConnections && systems.map(system => 
                system.connections.map(connectionId => {
                  const target = systems.find(s => s.id === connectionId)
                  if (!target) return null
                  
                  return (
                    <line
                      key={`${system.id}-${connectionId}`}
                      x1={system.position.x + 25}
                      y1={system.position.y + 25}
                      x2={target.position.x + 25}
                      y2={target.position.y + 25}
                      stroke="#374151"
                      strokeWidth="2"
                      className="animate-pulse"
                    />
                  )
                })
              )}
            </svg>

            {/* System Nodes */}
            {systems.map(system => (
              <div
                key={system.id}
                className={`absolute w-12 h-12 rounded-lg ${getNodeColor(system)} flex items-center justify-center cursor-pointer transform transition-all hover:scale-110 ${
                  selectedNode === system.id ? 'ring-2 ring-blue-400' : ''
                }`}
                style={{
                  left: system.position.x,
                  top: system.position.y
                }}
                onClick={() => setSelectedNode(selectedNode === system.id ? null : system.id)}
              >
                <div className="text-white">
                  {getNodeIcon(system)}
                </div>
              </div>
            ))}

            {/* System Labels */}
            {systems.map(system => (
              <div
                key={`label-${system.id}`}
                className="absolute text-xs text-gray-300 pointer-events-none"
                style={{
                  left: system.position.x + 60,
                  top: system.position.y + 15
                }}
              >
                {system.name}
                <div className="text-gray-500">
                  {system.metadata.health && `${Math.round(system.metadata.health * 100)}% health`}
                </div>
              </div>
            ))}
          </div>
        )}

        {viewMode === 'chains' && (
          <div className="h-full overflow-y-auto p-4 space-y-4">
            {promptChains.map(chain => (
              <div key={chain.id} className="bg-gray-800 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <h3 className="text-white font-semibold">{chain.name}</h3>
                    <div className="flex items-center gap-2 text-sm text-gray-400">
                      <span className={getStatusColor(chain.status)}>
                        {chain.status.toUpperCase()}
                      </span>
                      <span>•</span>
                      <span>Step {chain.currentStep} of {chain.steps.length}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                    <span className="text-xs text-gray-400">
                      {Math.round((Date.now() - chain.createdAt.getTime()) / 1000)}s ago
                    </span>
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="w-full bg-gray-700 rounded-full h-2 mb-4">
                  <div 
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${(chain.currentStep / chain.steps.length) * 100}%` }}
                  ></div>
                </div>

                {/* Steps */}
                <div className="space-y-2">
                  {chain.steps.map((step, index) => (
                    <div
                      key={step.id}
                      className={`flex items-center gap-3 p-2 rounded ${
                        index < chain.currentStep ? 'bg-green-900' :
                        index === chain.currentStep ? 'bg-yellow-900' :
                        'bg-gray-700'
                      }`}
                    >
                      <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs ${
                        step.status === 'completed' ? 'bg-green-600 text-white' :
                        step.status === 'running' ? 'bg-yellow-600 text-white' :
                        'bg-gray-600 text-gray-400'
                      }`}>
                        {index + 1}
                      </div>
                      <div className="flex-1">
                        <div className="text-sm text-white">{step.name}</div>
                        <div className="text-xs text-gray-400">{step.input}</div>
                        {step.duration && (
                          <div className="text-xs text-gray-500">
                            Completed in {step.duration}ms
                          </div>
                        )}
                      </div>
                      <div className={`text-xs ${
                        step.status === 'completed' ? 'text-green-400' :
                        step.status === 'running' ? 'text-yellow-400' :
                        'text-gray-500'
                      }`}>
                        {step.status.toUpperCase()}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}

        {viewMode === 'agents' && (
          <div className="h-full overflow-y-auto p-4">
            <div className="grid grid-cols-2 gap-4">
              {systems.filter(s => s.type === 'agent').map(agent => (
                <div key={agent.id} className="bg-gray-800 rounded-lg p-4">
                  <div className="flex items-center gap-3 mb-3">
                    <div className={`w-8 h-8 rounded-lg ${getNodeColor(agent)} flex items-center justify-center`}>
                      {getNodeIcon(agent)}
                    </div>
                    <div>
                      <h3 className="text-white font-semibold">{agent.name}</h3>
                      <div className="text-sm text-gray-400">
                        {agent.metadata.provider === 'gemini' ? '🤖 Gemini' : '⚡ Cerebras'}
                      </div>
                    </div>
                  </div>
                  
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Status:</span>
                      <span className={getStatusColor(agent.status)}>{agent.status}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Messages:</span>
                      <span className="text-white">{agent.metadata.messagesProcessed}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Confidence:</span>
                      <span className="text-white">{Math.round(agent.metadata.confidence * 100)}%</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Selected Node Details */}
      {selectedNode && (
        <div className="border-t border-gray-700 p-4 bg-gray-800">
          {(() => {
            const node = systems.find(s => s.id === selectedNode)
            if (!node) return null
            
            return (
              <div>
                <h3 className="text-white font-semibold mb-2">{node.name}</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-400">Type:</span>
                    <span className="text-white ml-2">{node.type.toUpperCase()}</span>
                  </div>
                  <div>
                    <span className="text-gray-400">Status:</span>
                    <span className={`ml-2 ${getStatusColor(node.status)}`}>{node.status}</span>
                  </div>
                  {Object.entries(node.metadata).map(([key, value]) => (
                    <div key={key}>
                      <span className="text-gray-400">{key}:</span>
                      <span className="text-white ml-2">{value}</span>
                    </div>
                  ))}
                </div>
              </div>
            )
          })()}
        </div>
      )}
    </div>
  )
}
