// Backend Design View - Ultimate Visual Backend Builder
// Combines Lucidchart's beautiful design with n8n's workflow power

import React, { useState, useCallback, useMemo, useRef, useEffect } from 'react'
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  Node,
  Edge,
  NodeTypes,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  Panel as FlowPanel,
  useReactFlow,
  ReactFlowProvider,
  BackgroundVariant,
  MarkerType,
} from 'reactflow'
import 'reactflow/dist/style.css'
import {
  Server, Code, Zap, Cloud, ChevronLeft, ChevronRight, 
  Download, Upload, Save, Undo2, Redo2, ZoomIn, ZoomOut, 
  Maximize2, Grid3X3, Package, Sparkles, Play, Settings,
  FileText, Keyboard, Command, Wand2, Eye, Layout
} from 'lucide-react'
import { TemplateNode } from './TemplateNode'
import { TemplateLibrary } from './TemplateLibrary'
import { PropertiesPanel } from './PropertiesPanel'
import { CodePreviewModal } from './CodePreviewModal'
import { DeploymentModal } from './DeploymentModal'
import { Template, TemplateNodeData, TemplateCategory, GeneratedCode, DeploymentConfig, TemplateStatus } from './types'
import { TEMPLATES, CATEGORIES, getCategoryConfig } from './templates'

// Custom node types
const nodeTypes: NodeTypes = {
  template: TemplateNode as any,
}

// Custom edge styles
const defaultEdgeOptions = {
  type: 'smoothstep',
  animated: true,
  style: { stroke: '#6366f1', strokeWidth: 2 },
  markerEnd: { type: MarkerType.ArrowClosed, color: '#6366f1' },
}

// Beautiful preset flow diagram
const PRESET_NODES: Node<TemplateNodeData>[] = [
  // API Gateway (Entry Point)
  {
    id: 'api-gateway-1',
    type: 'template',
    position: { x: 100, y: 250 },
    data: {
      id: 'api_gateway',
      type: 'infrastructure',
      name: 'API Gateway',
      description: 'Main entry point',
      icon: 'Globe',
      status: 'configured',
      config: { port: 3000, cors: true },
      inputs: [],
      outputs: ['http'],
      version: '1.0.0',
      author: 'System',
      tags: ['entry'],
    },
  },
  // Auth Middleware
  {
    id: 'auth-jwt-1',
    type: 'template',
    position: { x: 350, y: 150 },
    data: {
      id: 'auth_jwt',
      type: 'auth',
      name: 'JWT Auth',
      description: 'Token authentication',
      icon: 'Shield',
      status: 'configured',
      config: { secret: 'your-secret', expiresIn: '24h' },
      inputs: ['http'],
      outputs: ['authenticated'],
      version: '1.0.0',
      author: 'System',
      tags: ['security'],
    },
  },
  // REST API
  {
    id: 'api-rest-1',
    type: 'template',
    position: { x: 350, y: 350 },
    data: {
      id: 'api_rest',
      type: 'api',
      name: 'REST API',
      description: 'RESTful endpoints',
      icon: 'Code',
      status: 'configured',
      config: { basePath: '/api', version: 'v1' },
      inputs: ['http'],
      outputs: ['data'],
      version: '1.0.0',
      author: 'System',
      tags: ['api'],
    },
  },
  // Database
  {
    id: 'db-postgres-1',
    type: 'template',
    position: { x: 650, y: 250 },
    data: {
      id: 'db_postgres',
      type: 'database',
      name: 'PostgreSQL',
      description: 'Relational database',
      icon: 'Database',
      status: 'configured',
      config: { host: 'localhost', port: 5432 },
      inputs: ['query'],
      outputs: ['data'],
      version: '1.0.0',
      author: 'System',
      tags: ['storage'],
    },
  },
  // Cache
  {
    id: 'cache-redis-1',
    type: 'template',
    position: { x: 650, y: 100 },
    data: {
      id: 'cache_redis',
      type: 'cache',
      name: 'Redis Cache',
      description: 'In-memory cache',
      icon: 'Zap',
      status: 'configured',
      config: { host: 'localhost', port: 6379 },
      inputs: ['key'],
      outputs: ['value'],
      version: '1.0.0',
      author: 'System',
      tags: ['performance'],
    },
  },
  // Message Queue
  {
    id: 'queue-rabbitmq-1',
    type: 'template',
    position: { x: 650, y: 400 },
    data: {
      id: 'queue_rabbitmq',
      type: 'messaging',
      name: 'RabbitMQ',
      description: 'Message queue',
      icon: 'Inbox',
      status: 'configured',
      config: { host: 'localhost', port: 5672 },
      inputs: ['message'],
      outputs: ['event'],
      version: '1.0.0',
      author: 'System',
      tags: ['async'],
    },
  },
]

const PRESET_EDGES: Edge[] = [
  // Gateway → Auth
  { id: 'e1', source: 'api-gateway-1', target: 'auth-jwt-1', ...defaultEdgeOptions },
  // Gateway → REST API
  { id: 'e2', source: 'api-gateway-1', target: 'api-rest-1', ...defaultEdgeOptions },
  // Auth → Cache
  { id: 'e3', source: 'auth-jwt-1', target: 'cache-redis-1', ...defaultEdgeOptions, style: { stroke: '#10b981', strokeWidth: 2 } },
  // REST API → Database
  { id: 'e4', source: 'api-rest-1', target: 'db-postgres-1', ...defaultEdgeOptions },
  // REST API → Queue
  { id: 'e5', source: 'api-rest-1', target: 'queue-rabbitmq-1', ...defaultEdgeOptions, style: { stroke: '#f59e0b', strokeWidth: 2 } },
]

const BackendDesignViewInner: React.FC = () => {
  const reactFlowWrapper = useRef<HTMLDivElement>(null)
  const { fitView, zoomIn, zoomOut, setCenter, getNodes, getEdges } = useReactFlow()
  
  // Canvas state with beautiful preset
  const [nodes, setNodes, onNodesChange] = useNodesState<TemplateNodeData>(PRESET_NODES)
  const [edges, setEdges, onEdgesChange] = useEdgesState(PRESET_EDGES)
  
  // UI state
  const [isDrawerOpen, setIsDrawerOpen] = useState(true)
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null)
  const [activeCategory, setActiveCategory] = useState<TemplateCategory | 'all'>('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [showGrid, setShowGrid] = useState(true)
  const [showMinimap, setShowMinimap] = useState(true)
  
  // Modal state
  const [showCodePreview, setShowCodePreview] = useState(false)
  const [showDeployment, setShowDeployment] = useState(false)
  const [generatedCode, setGeneratedCode] = useState<GeneratedCode | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  
  // History state for undo/redo
  const [history, setHistory] = useState<{ nodes: Node<TemplateNodeData>[], edges: Edge[] }[]>([])
  const [historyIndex, setHistoryIndex] = useState(-1)
  
  // Selected node
  const selectedNode = useMemo(() => 
    nodes.find(n => n.id === selectedNodeId) || null,
    [nodes, selectedNodeId]
  )

  // Save to history
  const saveToHistory = useCallback(() => {
    const newHistory = history.slice(0, historyIndex + 1)
    newHistory.push({ nodes: [...nodes], edges: [...edges] })
    setHistory(newHistory)
    setHistoryIndex(newHistory.length - 1)
  }, [nodes, edges, history, historyIndex])

  // Undo
  const handleUndo = useCallback(() => {
    if (historyIndex > 0) {
      const prevState = history[historyIndex - 1]
      setNodes(prevState.nodes)
      setEdges(prevState.edges)
      setHistoryIndex(historyIndex - 1)
    }
  }, [history, historyIndex, setNodes, setEdges])

  // Redo
  const handleRedo = useCallback(() => {
    if (historyIndex < history.length - 1) {
      const nextState = history[historyIndex + 1]
      setNodes(nextState.nodes)
      setEdges(nextState.edges)
      setHistoryIndex(historyIndex + 1)
    }
  }, [history, historyIndex, setNodes, setEdges])

  // Auto-fit preset on mount
  useEffect(() => {
    if (nodes.length > 0) {
      setTimeout(() => fitView({ padding: 0.2, duration: 800 }), 100)
    }
  }, []) // Run only once on mount
  
  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.metaKey || e.ctrlKey) {
        switch (e.key) {
          case 'z':
            e.preventDefault()
            if (e.shiftKey) handleRedo()
            else handleUndo()
            break
          case 's':
            e.preventDefault()
            handleSaveWorkflow()
            break
          case 'g':
            e.preventDefault()
            handleGenerate()
            break
          case '=':
          case '+':
            e.preventDefault()
            zoomIn()
            break
          case '-':
            e.preventDefault()
            zoomOut()
            break
          case '0':
            e.preventDefault()
            fitView({ padding: 0.2 })
            break
        }
      }
      
      if (e.key === 'Delete' || e.key === 'Backspace') {
        if (selectedNodeId) {
          handleDeleteNode(selectedNodeId)
        }
      }
    }
    
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [handleUndo, handleRedo, selectedNodeId, zoomIn, zoomOut, fitView])

  // Handle connections
  const onConnect = useCallback((params: Connection) => {
    setEdges((eds) => addEdge({
      ...params,
      ...defaultEdgeOptions,
    }, eds))
    saveToHistory()
  }, [setEdges, saveToHistory])

  // Handle node selection
  const onNodeClick = useCallback((_: React.MouseEvent, node: Node) => {
    setSelectedNodeId(node.id)
  }, [])

  // Handle canvas click (deselect)
  const onPaneClick = useCallback(() => {
    setSelectedNodeId(null)
  }, [])

  // Handle template drag start
  const onTemplateDragStart = useCallback((e: React.DragEvent, template: Template) => {
    e.dataTransfer.setData('application/reactflow', JSON.stringify(template))
    e.dataTransfer.effectAllowed = 'move'
  }, [])

  // Handle drop on canvas
  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    
    const templateData = e.dataTransfer.getData('application/reactflow')
    if (!templateData) return
    
    const template: Template = JSON.parse(templateData)
    
    // Get drop position
    const bounds = reactFlowWrapper.current?.getBoundingClientRect()
    if (!bounds) return
    
    const position = {
      x: e.clientX - bounds.left - 88,
      y: e.clientY - bounds.top - 50,
    }
    
    const newNode: Node<TemplateNodeData> = {
      id: `${template.id}-${Date.now()}`,
      type: 'template',
      position,
      data: {
        id: template.id,
        type: template.type,
        name: template.name,
        description: template.description,
        icon: template.icon,
        status: 'incomplete' as TemplateStatus,
        config: Object.fromEntries(
          Object.entries(template.defaultConfig).map(([k, v]) => [k, v.value])
        ),
        inputs: template.inputs,
        outputs: template.outputs,
        version: template.version,
        author: template.author,
        tags: template.tags,
      },
    }
    
    setNodes((nds) => [...nds, newNode])
    setSelectedNodeId(newNode.id)
    saveToHistory()
  }, [setNodes, saveToHistory])

  // Handle drag over
  const onDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.dataTransfer.dropEffect = 'move'
  }, [])

  // Handle config change
  const onConfigChange = useCallback((nodeId: string, config: Record<string, any>) => {
    setNodes((nds) => nds.map(node => {
      if (node.id === nodeId) {
        return {
          ...node,
          data: {
            ...node.data,
            config,
            status: 'configured' as TemplateStatus,
          },
        }
      }
      return node
    }))
    saveToHistory()
  }, [setNodes, saveToHistory])

  // Handle node deletion
  const handleDeleteNode = useCallback((nodeId: string) => {
    setNodes((nds) => nds.filter(n => n.id !== nodeId))
    setEdges((eds) => eds.filter(e => e.source !== nodeId && e.target !== nodeId))
    if (selectedNodeId === nodeId) {
      setSelectedNodeId(null)
    }
    saveToHistory()
  }, [setNodes, setEdges, selectedNodeId, saveToHistory])

  // Handle node duplication
  const handleDuplicateNode = useCallback((nodeId: string) => {
    const node = nodes.find(n => n.id === nodeId)
    if (!node) return
    
    const newNode: Node<TemplateNodeData> = {
      ...node,
      id: `${node.data.id}-${Date.now()}`,
      position: {
        x: node.position.x + 50,
        y: node.position.y + 50,
      },
    }
    
    setNodes((nds) => [...nds, newNode])
    setSelectedNodeId(newNode.id)
    saveToHistory()
  }, [nodes, setNodes, saveToHistory])

  // Generate code
  const handleGenerate = useCallback(async () => {
    setIsGenerating(true)
    setShowCodePreview(true)
    
    // Simulate code generation
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // Generate mock code based on nodes
    const files = nodes.map(node => ({
      path: `src/${node.data.type}/${node.data.id}.ts`,
      content: generateMockCode(node.data),
      language: 'typescript',
      template: node.data.id,
    }))
    
    // Add index files
    const types = [...new Set(nodes.map(n => n.data.type))]
    types.forEach(type => {
      files.push({
        path: `src/${type}/index.ts`,
        content: `// Auto-generated index for ${type}\n${nodes.filter(n => n.data.type === type).map(n => `export * from './${n.data.id}'`).join('\n')}`,
        language: 'typescript',
        template: 'index',
      })
    })
    
    // Build file tree
    const structure = buildFileTree(files.map(f => f.path))
    
    setGeneratedCode({
      files,
      structure,
      stats: {
        totalFiles: files.length,
        totalLines: files.reduce((sum, f) => sum + f.content.split('\n').length, 0),
        languages: { typescript: files.length },
        templates: nodes.map(n => n.data.id),
        duration: 2000,
        testFiles: Math.floor(files.length * 0.3),
        testCoverage: 94,
      },
      warnings: [],
      errors: [],
    })
    
    setIsGenerating(false)
  }, [nodes])

  // Handle deployment
  const handleDeploy = useCallback(async (config: DeploymentConfig) => {
    console.log('Deploying with config:', config)
    await new Promise(resolve => setTimeout(resolve, 3000))
  }, [])

  // Save workflow
  const handleSaveWorkflow = useCallback(() => {
    const workflow = {
      nodes,
      edges,
      timestamp: new Date().toISOString(),
    }
    localStorage.setItem('backend-design-workflow', JSON.stringify(workflow))
    console.log('Workflow saved')
  }, [nodes, edges])

  // Load workflow
  const handleLoadWorkflow = useCallback(() => {
    const saved = localStorage.getItem('backend-design-workflow')
    if (saved) {
      const workflow = JSON.parse(saved)
      setNodes(workflow.nodes)
      setEdges(workflow.edges)
    }
  }, [setNodes, setEdges])

  // Auto-layout
  const handleAutoLayout = useCallback(() => {
    const layoutedNodes = autoLayoutNodes(nodes, edges)
    setNodes(layoutedNodes)
    setTimeout(() => fitView({ padding: 0.2 }), 50)
    saveToHistory()
  }, [nodes, edges, setNodes, fitView, saveToHistory])

  return (
    <div className="h-full flex flex-col bg-gray-950">
      {/* Top Toolbar */}
      <div className="h-12 bg-gray-900 border-b border-gray-800 flex items-center px-4 gap-2">
        {/* Logo/Title */}
        <div className="flex items-center gap-2 mr-4">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
            <Server className="w-4 h-4 text-white" />
          </div>
          <span className="text-sm font-semibold text-gray-200">Backend Designer</span>
        </div>
        
        <div className="w-px h-6 bg-gray-700" />
        
        {/* Category Pills */}
        <div className="flex items-center gap-1 overflow-x-auto flex-1">
          <button
            onClick={() => setActiveCategory('all')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-all flex items-center gap-1.5 ${
              activeCategory === 'all'
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/30'
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}
          >
            <Package className="w-3.5 h-3.5" />
            All
          </button>
          {CATEGORIES.map(cat => {
            const Icon = cat.icon
            return (
              <button
                key={cat.id}
                onClick={() => setActiveCategory(cat.id)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-all flex items-center gap-1.5 ${
                  activeCategory === cat.id
                    ? 'text-white shadow-lg'
                    : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                }`}
                style={{
                  backgroundColor: activeCategory === cat.id ? cat.accentColor : undefined,
                  boxShadow: activeCategory === cat.id ? `0 4px 15px ${cat.accentColor}40` : undefined,
                }}
              >
                <Icon className="w-3.5 h-3.5" />
                {cat.name}
              </button>
            )
          })}
        </div>
        
        <div className="w-px h-6 bg-gray-700" />
        
        {/* Actions */}
        <div className="flex items-center gap-1">
          <button
            onClick={handleUndo}
            disabled={historyIndex <= 0}
            className="p-2 hover:bg-gray-800 rounded-lg text-gray-400 hover:text-gray-200 disabled:opacity-30 transition-colors"
            title="Undo (⌘Z)"
          >
            <Undo2 className="w-4 h-4" />
          </button>
          <button
            onClick={handleRedo}
            disabled={historyIndex >= history.length - 1}
            className="p-2 hover:bg-gray-800 rounded-lg text-gray-400 hover:text-gray-200 disabled:opacity-30 transition-colors"
            title="Redo (⌘⇧Z)"
          >
            <Redo2 className="w-4 h-4" />
          </button>
          
          <div className="w-px h-6 bg-gray-700 mx-1" />
          
          <button
            onClick={() => setShowGrid(!showGrid)}
            className={`p-2 rounded-lg transition-colors ${showGrid ? 'bg-gray-800 text-gray-200' : 'text-gray-400 hover:bg-gray-800'}`}
            title="Toggle Grid"
          >
            <Grid3X3 className="w-4 h-4" />
          </button>
          <button
            onClick={() => setShowMinimap(!showMinimap)}
            className={`p-2 rounded-lg transition-colors ${showMinimap ? 'bg-gray-800 text-gray-200' : 'text-gray-400 hover:bg-gray-800'}`}
            title="Toggle Minimap"
          >
            <Eye className="w-4 h-4" />
          </button>
          <button
            onClick={handleAutoLayout}
            className="p-2 hover:bg-gray-800 rounded-lg text-gray-400 hover:text-gray-200 transition-colors"
            title="Auto Layout"
          >
            <Layout className="w-4 h-4" />
          </button>
          
          <div className="w-px h-6 bg-gray-700 mx-1" />
          
          <button
            onClick={handleSaveWorkflow}
            className="p-2 hover:bg-gray-800 rounded-lg text-gray-400 hover:text-gray-200 transition-colors"
            title="Save (⌘S)"
          >
            <Save className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 relative overflow-hidden">
        {/* Template Library Drawer */}
        <div 
          className={`absolute left-0 top-0 bottom-0 w-72 z-20 transition-transform duration-300 ${
            isDrawerOpen ? 'translate-x-0' : '-translate-x-full'
          }`}
        >
          <TemplateLibrary
            onDragStart={onTemplateDragStart}
            searchQuery={searchQuery}
            onSearchChange={setSearchQuery}
            selectedCategory={activeCategory}
            onCategoryChange={setActiveCategory}
          />
        </div>

        {/* Drawer Toggle */}
        <button
          onClick={() => setIsDrawerOpen(!isDrawerOpen)}
          className={`absolute z-30 top-4 p-2 bg-gray-800 hover:bg-gray-700 rounded-r-lg border border-l-0 border-gray-700 text-gray-400 hover:text-gray-200 transition-all ${
            isDrawerOpen ? 'left-72' : 'left-0'
          }`}
        >
          {isDrawerOpen ? <ChevronLeft className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
        </button>

        {/* Canvas */}
        <div 
          ref={reactFlowWrapper}
          className={`h-full transition-all duration-300 ${isDrawerOpen ? 'pl-72' : ''}`}
          onDrop={onDrop}
          onDragOver={onDragOver}
        >
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={onNodeClick}
            onPaneClick={onPaneClick}
            nodeTypes={nodeTypes}
            defaultEdgeOptions={defaultEdgeOptions}
            fitView
            className="bg-gray-950"
            snapToGrid
            snapGrid={[20, 20]}
          >
            {showGrid && (
              <Background 
                variant={BackgroundVariant.Dots} 
                color="#374151" 
                gap={20} 
                size={1} 
              />
            )}
            
            <Controls 
              className="bg-gray-800 border border-gray-700 rounded-lg [&>button]:bg-gray-800 [&>button]:border-gray-700 [&>button]:text-gray-400 [&>button:hover]:bg-gray-700 [&>button:hover]:text-gray-200"
              showZoom={true}
              showFitView={true}
              showInteractive={false}
            />
            
            {showMinimap && (
              <MiniMap 
                className="bg-gray-800 border border-gray-700 rounded-lg"
                nodeColor={(node) => {
                  const category = getCategoryConfig((node.data as TemplateNodeData)?.type)
                  return category?.accentColor || '#6b7280'
                }}
                maskColor="rgba(17, 24, 39, 0.9)"
                pannable
                zoomable
              />
            )}
            
            {/* Empty State */}
            {nodes.length === 0 && (
              <FlowPanel position="top-center" className="mt-32">
                <div className="text-center p-8 bg-gray-900/90 rounded-2xl border border-gray-800 backdrop-blur-xl shadow-2xl max-w-lg">
                  <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center mx-auto mb-6 shadow-lg shadow-blue-500/30">
                    <Wand2 className="w-10 h-10 text-white" />
                  </div>
                  <h3 className="text-xl font-bold text-gray-100 mb-3">Design Your Backend</h3>
                  <p className="text-sm text-gray-400 mb-6 leading-relaxed">
                    Drag templates from the left panel to create your backend architecture.
                    Connect components to define data flow and dependencies.
                  </p>
                  <div className="grid grid-cols-3 gap-3 mb-6">
                    <div className="p-3 rounded-lg bg-gray-800/50 border border-gray-700">
                      <div className="w-6 h-6 rounded-full bg-green-500/20 flex items-center justify-center mx-auto mb-2">
                        <div className="w-2 h-2 rounded-full bg-green-500" />
                      </div>
                      <div className="text-[10px] text-gray-400">Configured</div>
                    </div>
                    <div className="p-3 rounded-lg bg-gray-800/50 border border-gray-700">
                      <div className="w-6 h-6 rounded-full bg-yellow-500/20 flex items-center justify-center mx-auto mb-2">
                        <div className="w-2 h-2 rounded-full bg-yellow-500" />
                      </div>
                      <div className="text-[10px] text-gray-400">Incomplete</div>
                    </div>
                    <div className="p-3 rounded-lg bg-gray-800/50 border border-gray-700">
                      <div className="w-6 h-6 rounded-full bg-blue-500/20 flex items-center justify-center mx-auto mb-2">
                        <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
                      </div>
                      <div className="text-[10px] text-gray-400">Running</div>
                    </div>
                  </div>
                  <div className="flex items-center justify-center gap-2 text-xs text-gray-500">
                    <Keyboard className="w-4 h-4" />
                    <span>Press</span>
                    <kbd className="px-1.5 py-0.5 rounded bg-gray-800 border border-gray-700">⌘</kbd>
                    <span>+</span>
                    <kbd className="px-1.5 py-0.5 rounded bg-gray-800 border border-gray-700">G</kbd>
                    <span>to generate</span>
                  </div>
                </div>
              </FlowPanel>
            )}
          </ReactFlow>
        </div>

        {/* Floating Action Bar */}
        {nodes.length > 0 && (
          <div className="absolute bottom-6 right-6 flex items-center gap-3 z-10">
            <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-gray-800/90 backdrop-blur-sm border border-gray-700 shadow-xl">
              <div className="text-xs text-gray-400">
                {nodes.length} templates • {edges.length} connections
              </div>
              <div className="w-px h-4 bg-gray-700" />
              <div className={`w-2 h-2 rounded-full ${
                nodes.every(n => n.data.status === 'configured') ? 'bg-green-500' :
                nodes.some(n => n.data.status === 'error') ? 'bg-red-500' : 'bg-yellow-500'
              }`} />
            </div>
            
            <button
              onClick={() => setShowCodePreview(true)}
              className="px-4 py-2.5 rounded-xl bg-gray-800 hover:bg-gray-700 border border-gray-700 text-gray-200 text-sm font-medium flex items-center gap-2 transition-all shadow-xl hover:shadow-2xl"
            >
              <Code className="w-4 h-4" />
              Preview
            </button>
            
            <button
              onClick={handleGenerate}
              disabled={isGenerating}
              className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 text-white text-sm font-medium flex items-center gap-2 transition-all shadow-xl shadow-blue-500/30 hover:shadow-blue-500/50 disabled:opacity-50"
            >
              {isGenerating ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Zap className="w-4 h-4" />
                  Generate
                </>
              )}
            </button>
            
            <button
              onClick={() => setShowDeployment(true)}
              className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-green-600 to-emerald-500 hover:from-green-500 hover:to-emerald-400 text-white text-sm font-medium flex items-center gap-2 transition-all shadow-xl shadow-green-500/30 hover:shadow-green-500/50"
            >
              <Cloud className="w-4 h-4" />
              Deploy
            </button>
          </div>
        )}
      </div>

      {/* Properties Panel */}
      <PropertiesPanel
        selectedNode={selectedNode}
        onConfigChange={onConfigChange}
        onDuplicate={handleDuplicateNode}
        onDelete={handleDeleteNode}
        onViewCode={() => setShowCodePreview(true)}
      />

      {/* Modals */}
      <CodePreviewModal
        isOpen={showCodePreview}
        onClose={() => setShowCodePreview(false)}
        generatedCode={generatedCode}
        isGenerating={isGenerating}
      />
      
      <DeploymentModal
        isOpen={showDeployment}
        onClose={() => setShowDeployment(false)}
        onDeploy={handleDeploy}
      />
    </div>
  )
}

// Wrap with ReactFlowProvider
export const BackendDesignView: React.FC = () => (
  <ReactFlowProvider>
    <BackendDesignViewInner />
  </ReactFlowProvider>
)

// Helper: Generate mock code for a template
function generateMockCode(data: TemplateNodeData): string {
  return `// Auto-generated: ${data.name}
// Template: ${data.id}
// Generated by AIM-OS Backend Designer

import { Injectable } from '@nestjs/common'

/**
 * ${data.description}
 * @version ${data.version}
 */
@Injectable()
export class ${toPascalCase(data.id)}Service {
  constructor() {
    // Configuration: ${JSON.stringify(data.config, null, 2)}
  }

  async initialize(): Promise<void> {
    console.log('Initializing ${data.name}...')
    // TODO: Implement initialization logic
  }

  async execute(input: unknown): Promise<unknown> {
    // TODO: Implement main logic
    return { success: true }
  }
}

export default ${toPascalCase(data.id)}Service
`
}

// Helper: Convert to PascalCase
function toPascalCase(str: string): string {
  return str.split(/[-_]/).map(word => 
    word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
  ).join('')
}

// Helper: Build file tree from paths
function buildFileTree(paths: string[]): any[] {
  const root: any[] = []
  
  paths.forEach(path => {
    const parts = path.split('/')
    let current = root
    
    parts.forEach((part, index) => {
      const isFile = index === parts.length - 1
      let node = current.find(n => n.name === part)
      
      if (!node) {
        node = {
          name: part,
          path: parts.slice(0, index + 1).join('/'),
          type: isFile ? 'file' : 'directory',
          children: isFile ? undefined : [],
        }
        current.push(node)
      }
      
      if (!isFile) {
        current = node.children
      }
    })
  })
  
  return root
}

// Helper: Auto-layout nodes
function autoLayoutNodes(nodes: Node<TemplateNodeData>[], edges: Edge[]): Node<TemplateNodeData>[] {
  const nodeMap = new Map(nodes.map(n => [n.id, n]))
  const inDegree = new Map<string, number>()
  const outNodes = new Map<string, string[]>()
  
  // Initialize
  nodes.forEach(n => {
    inDegree.set(n.id, 0)
    outNodes.set(n.id, [])
  })
  
  // Build graph
  edges.forEach(e => {
    inDegree.set(e.target, (inDegree.get(e.target) || 0) + 1)
    outNodes.get(e.source)?.push(e.target)
  })
  
  // Topological sort with levels
  const levels: string[][] = []
  const queue = nodes.filter(n => inDegree.get(n.id) === 0).map(n => n.id)
  const visited = new Set<string>()
  
  while (queue.length > 0) {
    const level: string[] = []
    const nextQueue: string[] = []
    
    queue.forEach(id => {
      if (visited.has(id)) return
      visited.add(id)
      level.push(id)
      
      outNodes.get(id)?.forEach(target => {
        const newDegree = (inDegree.get(target) || 1) - 1
        inDegree.set(target, newDegree)
        if (newDegree === 0) {
          nextQueue.push(target)
        }
      })
    })
    
    if (level.length > 0) {
      levels.push(level)
    }
    queue.length = 0
    queue.push(...nextQueue)
  }
  
  // Add any remaining nodes
  nodes.forEach(n => {
    if (!visited.has(n.id)) {
      if (levels.length === 0) levels.push([])
      levels[levels.length - 1].push(n.id)
    }
  })
  
  // Position nodes
  const xGap = 250
  const yGap = 150
  
  return nodes.map(node => {
    let levelIndex = levels.findIndex(level => level.includes(node.id))
    if (levelIndex === -1) levelIndex = 0
    
    const level = levels[levelIndex]
    const indexInLevel = level.indexOf(node.id)
    const levelHeight = level.length * yGap
    
    return {
      ...node,
      position: {
        x: levelIndex * xGap + 50,
        y: indexInLevel * yGap - levelHeight / 2 + 200,
      },
    }
  })
}

export default BackendDesignView

