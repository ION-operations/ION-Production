/**
 * Prompt Chain Visual Editor Component
 * Advanced Lucidchart-style diagramming for prompt orchestration
 * 
 * Features:
 * - Visual node-based chain building
 * - Comprehensive node library (system nodes, prompt nodes, conditional nodes, etc.)
 * - Custom node creation
 * - Drag-and-drop editing
 * - Real-time chain execution preview
 */

import React, { useState, useCallback, useMemo, useEffect } from 'react'
import {
  ReactFlow,
  ReactFlowProvider,
  Node,
  Edge,
  addEdge,
  Background,
  Controls,
  MiniMap,
  Connection,
  useNodesState,
  useEdgesState,
  Panel,
  MarkerType,
  NodeTypes,
  EdgeTypes,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import {
  Database, // CMC
  Search, // HHNI
  Shield, // VIF
  GitBranch, // APOE
  Network, // SEG
  CheckCircle, // SDF-CVF
  MessageSquare, // Prompt
  Code, // Code
  FileText, // Document
  Zap, // Action
  GitMerge, // Merge
  Repeat, // Loop
  Play, // Start
  Square, // End
  AlertTriangle, // Error
  Plus,
  Save,
  X,
  Settings,
  Trash2,
} from 'lucide-react'
import { getServiceBridge } from '../../services/serviceBridge'

const serviceBridge = getServiceBridge()

// Comprehensive Node Types Library
export const NODE_TYPES_LIBRARY = {
  // Control Flow Nodes
  start: {
    type: 'start',
    label: 'Start',
    icon: Play,
    color: '#22c55e',
    description: 'Chain entry point',
    category: 'control',
  },
  end: {
    type: 'end',
    label: 'End',
    icon: Square,
    color: '#ef4444',
    description: 'Chain exit point',
    category: 'control',
  },
  conditional: {
    type: 'conditional',
    label: 'Conditional Branch',
    icon: GitMerge,
    color: '#f59e0b',
    description: 'Branch based on condition',
    category: 'control',
  },
  loop: {
    type: 'loop',
    label: 'Loop',
    icon: Repeat,
    color: '#8b5cf6',
    description: 'Repeat steps until condition met',
    category: 'control',
  },
  merge: {
    type: 'merge',
    label: 'Merge',
    icon: GitMerge,
    color: '#3b82f6',
    description: 'Merge multiple paths',
    category: 'control',
  },
  error: {
    type: 'error',
    label: 'Error Handler',
    icon: AlertTriangle,
    color: '#ef4444',
    description: 'Handle errors',
    category: 'control',
  },
  
  // AIM-OS System Nodes
  cmc: {
    type: 'system',
    systemId: 'cmc',
    label: 'CMC - Store/Retrieve',
    icon: Database,
    color: '#6366f1',
    description: 'Context Memory Core operations',
    category: 'system',
    operations: ['store', 'retrieve', 'query', 'update'],
  },
  hhni: {
    type: 'system',
    systemId: 'hhni',
    label: 'HHNI - Knowledge Retrieval',
    icon: Search,
    color: '#8b5cf6',
    description: 'Hierarchical knowledge retrieval',
    category: 'system',
    operations: ['search', 'retrieve', 'index'],
  },
  vif: {
    type: 'system',
    systemId: 'vif',
    label: 'VIF - Confidence Validation',
    icon: Shield,
    color: '#10b981',
    description: 'Verifiable Intelligence Framework',
    category: 'system',
    operations: ['validate', 'extract_confidence', 'check_band'],
  },
  apoe: {
    type: 'system',
    systemId: 'apoe',
    label: 'APOE - Planning',
    icon: GitBranch,
    color: '#f59e0b',
    description: 'AI-Powered Orchestration Engine',
    category: 'system',
    operations: ['create_plan', 'execute_plan', 'optimize'],
  },
  seg: {
    type: 'system',
    systemId: 'seg',
    label: 'SEG - Knowledge Synthesis',
    icon: Network,
    color: '#ec4899',
    description: 'Shared Evidence Graph',
    category: 'system',
    operations: ['synthesize', 'connect', 'analyze'],
  },
  sdfcvf: {
    type: 'system',
    systemId: 'sdfcvf',
    label: 'SDF-CVF - Quality Check',
    icon: CheckCircle,
    color: '#14b8a6',
    description: 'System Development Framework',
    category: 'system',
    operations: ['validate_quality', 'check_parity', 'gate'],
  },
  
  // Prompt & Content Nodes
  prompt: {
    type: 'prompt',
    label: 'Prompt',
    icon: MessageSquare,
    color: '#3b82f6',
    description: 'LLM prompt execution',
    category: 'content',
  },
  code: {
    type: 'code',
    label: 'Code Execution',
    icon: Code,
    color: '#06b6d4',
    description: 'Execute code or script',
    category: 'content',
  },
  document: {
    type: 'document',
    label: 'Document Generation',
    icon: FileText,
    color: '#84cc16',
    description: 'Generate documentation',
    category: 'content',
  },
  action: {
    type: 'action',
    label: 'Action',
    icon: Zap,
    color: '#f97316',
    description: 'Execute action',
    category: 'content',
  },
  
  // Quality Gate Nodes
  quality_gate: {
    type: 'quality_gate',
    label: 'Quality Gate',
    icon: CheckCircle,
    color: '#10b981',
    description: 'Quality validation gate',
    category: 'quality',
    gateTypes: ['document_size', 'quality_score', 'confidence', 'test_coverage', 'dependency'],
  },
  confidence_gate: {
    type: 'confidence_gate',
    label: 'Confidence Gate',
    icon: Shield,
    color: '#8b5cf6',
    description: 'Confidence threshold gate',
    category: 'quality',
  },
  
  // Agent Nodes
  agent: {
    type: 'agent',
    label: 'Agent Assignment',
    icon: MessageSquare,
    color: '#6366f1',
    description: 'Assign step to specific agent',
    category: 'orchestration',
  },
  
  // Custom Node
  custom: {
    type: 'custom',
    label: 'Custom Node',
    icon: Settings,
    color: '#64748b',
    description: 'User-defined custom node',
    category: 'custom',
  },
}

// Custom Node Components
const CustomNodeComponent = ({ data }: { data: any }) => {
  const nodeType = NODE_TYPES_LIBRARY[data.nodeType as keyof typeof NODE_TYPES_LIBRARY]
  const Icon = nodeType?.icon || Settings
  
  return (
    <div className="px-3 py-2 bg-cursor-sidebar border-2 border-cursor-border rounded shadow-lg min-w-[120px]">
      <div className="flex items-center gap-2">
        <Icon className="w-4 h-4" style={{ color: nodeType?.color || '#64748b' }} />
        <div className="text-xs font-semibold">{data.label}</div>
      </div>
      {data.description && (
        <div className="text-[10px] text-cursor-text-secondary mt-1">{data.description}</div>
      )}
    </div>
  )
}

const nodeTypes: NodeTypes = {
  custom: CustomNodeComponent,
}

interface PromptChainEditorProps {
  chainId?: string
  onSave?: (chain: any) => void
  onClose?: () => void
}

export const PromptChainEditor: React.FC<PromptChainEditorProps> = ({
  chainId,
  onSave,
  onClose,
}) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([] as Node[])
  const [edges, setEdges, onEdgesChange] = useEdgesState([] as Edge[])
  const [nodePaletteOpen, setNodePaletteOpen] = useState(false)
  const [selectedNode, setSelectedNode] = useState<Node | null>(null)
  const [chainName, setChainName] = useState('')
  const [chainDescription, setChainDescription] = useState('')
  const [saving, setSaving] = useState(false)
  const [loading, setLoading] = useState(false)

  const loadChain = useCallback(async () => {
    if (!chainId) return
    
    setLoading(true)
    try {
      const result = await serviceBridge.getPromptChain(chainId)
      if (result.success && result.chain) {
        const chain = result.chain
        setChainName(chain.name || '')
        setChainDescription(chain.description || '')
        
        // Convert chain nodes/edges to ReactFlow format
        if (chain.nodes && Array.isArray(chain.nodes)) {
          const flowNodes: Node[] = chain.nodes.map((node: any) => ({
            id: node.id,
            type: 'custom',
            position: node.position || { x: Math.random() * 400, y: Math.random() * 300 },
            data: {
              label: node.label || node.name || node.id,
              nodeType: node.type || 'prompt',
              description: node.description || node.prompt || '',
              systemId: node.systemId,
              prompt: node.prompt,
              config: node.config,
            },
          }))
          setNodes(flowNodes)
        }
        
        if (chain.edges && Array.isArray(chain.edges)) {
          const flowEdges: Edge[] = chain.edges.map((edge: any) => ({
            id: edge.id,
            source: edge.source,
            target: edge.target,
            type: edge.type || 'default',
            data: {
              condition: edge.condition,
            },
          }))
          setEdges(flowEdges)
        }
      }
    } catch (error) {
      console.error('Failed to load chain:', error)
    } finally {
      setLoading(false)
    }
  }, [chainId, setNodes, setEdges])

  // Load existing chain if chainId provided
  useEffect(() => {
    if (chainId) {
      loadChain()
    }
  }, [chainId, loadChain])

  // Listen for node selection from drawer panel
  useEffect(() => {
    const handleNodeSelected = (event: CustomEvent) => {
      const { nodeType, nodeConfig } = event.detail
      // Add node at center of viewport
      const position = { x: 400, y: 300 }
      addNode(nodeType, position)
    }

    const handleTemplateLoaded = (event: CustomEvent) => {
      const { template } = event.detail
      // Load template into editor
      if (template.nodes && Array.isArray(template.nodes)) {
        const flowNodes: Node[] = template.nodes.map((node: any) => ({
          id: node.id,
          type: 'custom',
          position: node.position || { x: Math.random() * 400 + 100, y: Math.random() * 300 + 100 },
          data: {
            label: node.label || node.name,
            nodeType: node.type || 'prompt',
            description: node.description || node.prompt || '',
            systemId: node.systemId,
            prompt: node.prompt,
            config: node.config,
          },
        }))
        setNodes(flowNodes)
      }
      
      if (template.edges && Array.isArray(template.edges)) {
        const flowEdges: Edge[] = template.edges.map((edge: any) => ({
          id: edge.id,
          source: edge.source,
          target: edge.target,
          type: edge.type || 'default',
          animated: edge.animated || false,
        }))
        setEdges(flowEdges)
      }
      
      // Update chain name and description if present
      if (template.name) setChainName(template.name)
      if (template.description) setChainDescription(template.description)
    }

    window.addEventListener('chain-node-selected', handleNodeSelected as EventListener)
    window.addEventListener('chain-template-loaded', handleTemplateLoaded as EventListener)

    return () => {
      window.removeEventListener('chain-node-selected', handleNodeSelected as EventListener)
      window.removeEventListener('chain-template-loaded', handleTemplateLoaded as EventListener)
    }
  }, [addNode, setNodes, setEdges])

  const onConnect = useCallback(
    (params: Connection) => {
      setEdges((eds) => addEdge(params, eds))
    },
    [setEdges]
  )

  const addNode = useCallback((nodeType: string, position: { x: number; y: number }) => {
    const nodeConfig = NODE_TYPES_LIBRARY[nodeType as keyof typeof NODE_TYPES_LIBRARY]
    if (!nodeConfig) return

    const newNode: Node = {
      id: `node_${Date.now()}`,
      type: 'custom',
      position,
      data: {
        label: nodeConfig.label,
        nodeType,
        description: nodeConfig.description,
        systemId: (nodeConfig as any).systemId,
        operations: (nodeConfig as any).operations,
        gateTypes: (nodeConfig as any).gateTypes,
      },
    }

    setNodes((nds) => [...nds, newNode])
    setNodePaletteOpen(false)
  }, [setNodes])

  const handleSave = useCallback(async () => {
    if (!chainName.trim()) {
      alert('Please enter a chain name')
      return
    }

    setSaving(true)
    try {
      const chainDefinition = {
        name: chainName,
        description: chainDescription,
        nodes: nodes.map((node: Node) => ({
          id: node.id,
          type: (node.data as any).nodeType,
          position: node.position,
          label: (node.data as any).label,
          systemId: (node.data as any).systemId,
          prompt: (node.data as any).prompt,
          config: (node.data as any).config,
        })),
        edges: edges.map((edge: Edge) => ({
          id: edge.id,
          source: edge.source,
          target: edge.target,
          type: edge.type || 'sequential',
          condition: (edge.data as any)?.condition,
        })),
        executionType: 'dynamic',
        entryPoint: nodes.find((n: Node) => (n.data as any).nodeType === 'start')?.id || nodes[0]?.id,
      }

      if (chainId) {
        // Update existing chain
        const result = await serviceBridge.updatePromptChain(
          chainId,
          chainDefinition,
          'Updated via visual editor',
          'user'
        )
        if (result.success && onSave) {
          onSave(chainDefinition)
        } else {
          alert(result.error || 'Failed to update chain')
        }
      } else {
        // Create new chain
        const result = await serviceBridge.createPromptChain(
          chainDefinition,
          'user'
        )
        if (result.success && onSave) {
          onSave(chainDefinition)
        } else {
          alert(result.error || 'Failed to create chain')
        }
      }
    } catch (error) {
      console.error('Failed to save chain:', error)
      alert('Failed to save chain')
    } finally {
      setSaving(false)
    }
  }, [chainName, chainDescription, nodes, edges, chainId, onSave])

  return (
    <div className="h-full flex flex-col bg-cursor-bg">
      {/* Header */}
      <div className="p-2 border-b border-cursor-border flex items-center justify-between">
        <div className="flex items-center gap-2 flex-1">
          <input
            type="text"
            placeholder="Chain Name"
            value={chainName}
            onChange={(e) => setChainName(e.target.value)}
            className="bg-cursor-input-bg text-cursor-text px-2 py-1 rounded border border-cursor-border focus:outline-none focus:border-cursor-status-bar"
            style={{ fontSize: '13px' }}
          />
          <input
            type="text"
            placeholder="Description"
            value={chainDescription}
            onChange={(e) => setChainDescription(e.target.value)}
            className="bg-cursor-input-bg text-cursor-text px-2 py-1 rounded border border-cursor-border focus:outline-none focus:border-cursor-status-bar flex-1"
            style={{ fontSize: '12px' }}
          />
        </div>
        <div className="flex items-center gap-1.5">
          <button
            onClick={() => setNodePaletteOpen(!nodePaletteOpen)}
            className="px-2 py-1 bg-cursor-status-bar hover:bg-cursor-status-bar/80 rounded flex items-center gap-1.5 text-xs cursor-button"
            style={{ fontSize: '12px' }}
          >
            <Plus className="w-3.5 h-3.5" />
            Add Node
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-2 py-1 bg-green-600 hover:bg-green-700 disabled:opacity-50 rounded flex items-center gap-1.5 text-xs cursor-button"
            style={{ fontSize: '12px' }}
          >
            <Save className="w-3.5 h-3.5" />
            {saving ? 'Saving...' : 'Save'}
          </button>
          {onClose && (
            <button
              onClick={onClose}
              className="p-1.5 bg-gray-600 hover:bg-gray-700 rounded cursor-button"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {/* Node Palette */}
      {nodePaletteOpen && (
        <div className="absolute top-12 left-2 z-50 bg-cursor-sidebar border border-cursor-border rounded shadow-xl p-2 max-h-[80vh] overflow-y-auto cursor-scrollbar" style={{ width: '300px' }}>
          <div className="text-xs font-semibold mb-2 text-cursor-text">Node Library</div>
          
          {/* Control Flow */}
          <div className="mb-3">
            <div className="text-xs font-semibold mb-1 text-cursor-text-secondary">Control Flow</div>
            <div className="grid grid-cols-2 gap-1">
              {Object.entries(NODE_TYPES_LIBRARY)
                .filter(([_, config]) => config.category === 'control')
                .map(([key, config]) => {
                  const Icon = config.icon
                  return (
                    <button
                      key={key}
                      onClick={() => addNode(key, { x: Math.random() * 400 + 100, y: Math.random() * 300 + 100 })}
                      className="p-2 bg-cursor-input-bg hover:bg-cursor-hover rounded flex items-center gap-1.5 text-xs cursor-button text-left"
                      style={{ fontSize: '11px' }}
                    >
                      <Icon className="w-3.5 h-3.5" style={{ color: config.color }} />
                      <span>{config.label}</span>
                    </button>
                  )
                })}
            </div>
          </div>

          {/* AIM-OS Systems */}
          <div className="mb-3">
            <div className="text-xs font-semibold mb-1 text-cursor-text-secondary">AIM-OS Systems</div>
            <div className="grid grid-cols-2 gap-1">
              {Object.entries(NODE_TYPES_LIBRARY)
                .filter(([_, config]) => config.category === 'system')
                .map(([key, config]) => {
                  const Icon = config.icon
                  return (
                    <button
                      key={key}
                      onClick={() => addNode(key, { x: Math.random() * 400 + 100, y: Math.random() * 300 + 100 })}
                      className="p-2 bg-cursor-input-bg hover:bg-cursor-hover rounded flex items-center gap-1.5 text-xs cursor-button text-left"
                      style={{ fontSize: '11px' }}
                    >
                      <Icon className="w-3.5 h-3.5" style={{ color: config.color }} />
                      <span>{config.label}</span>
                    </button>
                  )
                })}
            </div>
          </div>

          {/* Content Nodes */}
          <div className="mb-3">
            <div className="text-xs font-semibold mb-1 text-cursor-text-secondary">Content</div>
            <div className="grid grid-cols-2 gap-1">
              {Object.entries(NODE_TYPES_LIBRARY)
                .filter(([_, config]) => config.category === 'content')
                .map(([key, config]) => {
                  const Icon = config.icon
                  return (
                    <button
                      key={key}
                      onClick={() => addNode(key, { x: Math.random() * 400 + 100, y: Math.random() * 300 + 100 })}
                      className="p-2 bg-cursor-input-bg hover:bg-cursor-hover rounded flex items-center gap-1.5 text-xs cursor-button text-left"
                      style={{ fontSize: '11px' }}
                    >
                      <Icon className="w-3.5 h-3.5" style={{ color: config.color }} />
                      <span>{config.label}</span>
                    </button>
                  )
                })}
            </div>
          </div>

          {/* Quality Gates */}
          <div className="mb-3">
            <div className="text-xs font-semibold mb-1 text-cursor-text-secondary">Quality Gates</div>
            <div className="grid grid-cols-2 gap-1">
              {Object.entries(NODE_TYPES_LIBRARY)
                .filter(([_, config]) => config.category === 'quality')
                .map(([key, config]) => {
                  const Icon = config.icon
                  return (
                    <button
                      key={key}
                      onClick={() => addNode(key, { x: Math.random() * 400 + 100, y: Math.random() * 300 + 100 })}
                      className="p-2 bg-cursor-input-bg hover:bg-cursor-hover rounded flex items-center gap-1.5 text-xs cursor-button text-left"
                      style={{ fontSize: '11px' }}
                    >
                      <Icon className="w-3.5 h-3.5" style={{ color: config.color }} />
                      <span>{config.label}</span>
                    </button>
                  )
                })}
            </div>
          </div>

          {/* Custom Node */}
          <div>
            <button
              onClick={() => addNode('custom', { x: Math.random() * 400 + 100, y: Math.random() * 300 + 100 })}
              className="w-full p-2 bg-cursor-input-bg hover:bg-cursor-hover rounded flex items-center gap-1.5 text-xs cursor-button text-left"
              style={{ fontSize: '11px' }}
            >
              <Settings className="w-3.5 h-3.5" />
              <span>Custom Node</span>
            </button>
          </div>
        </div>
      )}

      {/* ReactFlow Canvas */}
      <div className="flex-1 relative">
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-xs text-cursor-text-secondary">Loading chain...</div>
          </div>
        ) : (
          <ReactFlowProvider>
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onConnect={onConnect}
              nodeTypes={nodeTypes}
              fitView
              className="bg-cursor-bg"
            >
              <Background />
              <Controls />
              <MiniMap />
            </ReactFlow>
          </ReactFlowProvider>
        )}
      </div>
    </div>
  )
}

