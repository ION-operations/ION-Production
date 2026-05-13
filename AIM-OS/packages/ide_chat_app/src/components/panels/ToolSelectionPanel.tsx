/**
 * Tool Selection Panel Component
 * 
 * Phase 2.2: Right Drawer Panels
 * 
 * MCP tool selection and management.
 * Features:
 * - Tool browser
 * - Tool search/filter
 * - Tool usage statistics
 * - Tool quality metrics
 * - AIM-OS integration (MCP Tools, Tool Quality Dashboard, VIF confidence)
 */

import React, { useState, useCallback, useMemo, useEffect } from 'react'
import { Wrench, Search, Zap, CheckCircle2, AlertCircle, TrendingUp, Filter, Database, Brain, Shield, BarChart3, Clock, Activity, RefreshCw, X, ExternalLink, ChevronRight, ChevronDown } from 'lucide-react'
import { getAllMCPMetrics, getMCPToolMetrics } from '../../services/mcpToolService'
import { useAIMOS } from '../../hooks/useAIMOS'
import { useDebounce } from '../../hooks/useDebounce'
import { ErrorBoundary } from '../ErrorBoundary'
import { LoadingState } from '../LoadingState'

interface MCPTool {
  id: string
  name: string
  description: string
  category: 'core' | 'memory' | 'timeline' | 'goal' | 'autonomous' | 'collaboration' | 'observability'
  status: 'working' | 'broken' | 'placeholder'
  usageCount: number
  successRate: number
  avgLatency: number
  confidence: number
  tags: string[]
  recentCalls?: number[] // Last 10 call latencies
  errorBreakdown?: Array<{
    type: string
    count: number
    percentage: number
  }>
  lastUsed?: string
  documentation?: string
  cmcAtomId?: string // CMC integration
}

const mockTools: MCPTool[] = [
  {
    id: 'store_memory',
    name: 'store_memory',
    description: 'Store information in AIM-OS persistent memory',
    category: 'memory',
    status: 'working',
    usageCount: 245,
    successRate: 0.98,
    avgLatency: 120,
    confidence: 0.95,
    tags: ['CMC', 'memory', 'persistence'],
    recentCalls: [115, 125, 118, 122, 130, 115, 120, 125, 118, 122],
    errorBreakdown: [
      { type: 'Timeout', count: 3, percentage: 60.0 },
      { type: 'Validation Error', count: 2, percentage: 40.0 },
    ],
    lastUsed: '2025-11-07T10:30:00Z',
    documentation: '/docs/mcp-tools/store_memory',
    cmcAtomId: 'cmc-tool-001',
  },
  {
    id: 'retrieve_memory',
    name: 'retrieve_memory',
    description: 'Retrieve insights from HHNI',
    category: 'memory',
    status: 'working',
    usageCount: 189,
    successRate: 0.97,
    avgLatency: 85,
    confidence: 0.94,
    tags: ['HHNI', 'memory', 'retrieval'],
    recentCalls: [80, 90, 85, 88, 82, 90, 85, 88, 82, 85],
    errorBreakdown: [
      { type: 'Not Found', count: 4, percentage: 80.0 },
      { type: 'Timeout', count: 1, percentage: 20.0 },
    ],
    lastUsed: '2025-11-07T10:29:00Z',
    documentation: '/docs/mcp-tools/retrieve_memory',
    cmcAtomId: 'cmc-tool-002',
  },
  {
    id: 'track_confidence',
    name: 'track_confidence',
    description: 'Track VIF confidence',
    category: 'core',
    status: 'working',
    usageCount: 156,
    successRate: 0.99,
    avgLatency: 45,
    confidence: 0.98,
    tags: ['VIF', 'confidence', 'quality'],
    recentCalls: [42, 48, 45, 43, 46, 44, 47, 45, 43, 46],
    lastUsed: '2025-11-07T10:31:00Z',
    documentation: '/docs/mcp-tools/track_confidence',
    cmcAtomId: 'cmc-tool-003',
  },
  {
    id: 'run_cognitive_audit',
    name: 'run_cognitive_audit',
    description: 'Run full cognitive analysis audit using CAS',
    category: 'observability',
    status: 'broken',
    usageCount: 12,
    successRate: 0.0,
    avgLatency: 0,
    confidence: 0.0,
    tags: ['CAS', 'audit', 'cognitive'],
    errorBreakdown: [
      { type: 'Method Signature Mismatch', count: 12, percentage: 100.0 },
    ],
    lastUsed: '2025-11-07T09:00:00Z',
    documentation: '/docs/mcp-tools/run_cognitive_audit',
  },
  {
    id: 'get_nl_tags',
    name: 'get_nl_tags',
    description: 'Get natural language tags for a code file',
    category: 'core',
    status: 'broken',
    usageCount: 8,
    successRate: 0.0,
    avgLatency: 0,
    confidence: 0.0,
    tags: ['NL', 'tags', 'code'],
    errorBreakdown: [
      { type: 'Syntax Error', count: 8, percentage: 100.0 },
    ],
    lastUsed: '2025-11-07T08:30:00Z',
    documentation: '/docs/mcp-tools/get_nl_tags',
  },
  {
    id: 'compute_intuition',
    name: 'compute_intuition',
    description: 'Compute AI intuition score using IIS',
    category: 'core',
    status: 'placeholder',
    usageCount: 0,
    successRate: 0.0,
    avgLatency: 0,
    confidence: 0.0,
    tags: ['IIS', 'intuition', 'placeholder'],
    documentation: '/docs/mcp-tools/compute_intuition',
  },
]

export const ToolSelectionPanel: React.FC = () => {
  const [tools, setTools] = useState<MCPTool[]>(mockTools)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<'all' | MCPTool['category']>('all')
  const [selectedStatus, setSelectedStatus] = useState<'all' | MCPTool['status']>('all')
  const [selectedTool, setSelectedTool] = useState<MCPTool | null>(null)
  const [expandedTool, setExpandedTool] = useState<string | null>(null)
  const [viewMode, setViewMode] = useState<'list' | 'metrics'>('list')
  const [isLoading, setIsLoading] = useState(false)

  // Debounce search query for performance
  const debouncedSearchQuery = useDebounce(searchQuery, 300)

  // AIM-OS integration
  const { vif, isConnected, useMockData } = useAIMOS()

  // Load real MCP tool metrics
  useEffect(() => {
    const loadMetrics = () => {
      setIsLoading(true)
      try {
        const metrics = getAllMCPMetrics()
        if (metrics.length > 0) {
          // Update tools with real metrics
          setTools(prevTools => prevTools.map(tool => {
            const metric = metrics.find(m => m.tool === tool.id)
            if (metric) {
              return {
                ...tool,
                usageCount: metric.callCount,
                successRate: metric.successCount / metric.callCount || 0,
                avgLatency: metric.avgLatency,
                confidence: metric.confidence || tool.confidence,
                lastUsed: metric.lastCallTime,
                recentCalls: metric.recentCalls,
                errorBreakdown: metric.errorBreakdown,
              }
            }
            return tool
          }))
        }
      } catch (error) {
        console.warn('Failed to load MCP tool metrics:', error)
      } finally {
        setIsLoading(false)
      }
    }
    
    loadMetrics()
    // Refresh every 5 seconds
    const interval = setInterval(loadMetrics, 5000)
    return () => clearInterval(interval)
  }, [])

  const categories = ['all', ...Array.from(new Set(tools.map((tool) => tool.category)))]

  // Calculate overall statistics
  const overallStats = useMemo(() => {
    const working = tools.filter(t => t.status === 'working').length
    const broken = tools.filter(t => t.status === 'broken').length
    const placeholder = tools.filter(t => t.status === 'placeholder').length
    const avgSuccessRate = tools.reduce((sum, t) => sum + t.successRate, 0) / tools.length
    const avgLatency = tools.reduce((sum, t) => sum + t.avgLatency, 0) / tools.length
    const avgConfidence = tools.reduce((sum, t) => sum + t.confidence, 0) / tools.length
    const totalUsage = tools.reduce((sum, t) => sum + t.usageCount, 0)
    return { working, broken, placeholder, avgSuccessRate, avgLatency, avgConfidence, totalUsage }
  }, [tools])

  const renderLatencyChart = (recentCalls?: number[]) => {
    if (!recentCalls || recentCalls.length === 0) return null
    
    const maxLatency = Math.max(...recentCalls, 1)
    const minHeight = 4
    const maxHeight = 30

    return (
      <div className="flex items-end gap-0.5 h-8">
        {recentCalls.map((latency, idx) => {
          const height = minHeight + ((latency / maxLatency) * (maxHeight - minHeight))
          const color = latency < 50 ? 'bg-green-500' : latency < 100 ? 'bg-yellow-500' : 'bg-red-500'
          return (
            <div
              key={idx}
              className={`${color} rounded-t transition-all`}
              style={{ width: '6px', height: `${height}px` }}
              title={`${latency}ms`}
            />
          )
        })}
      </div>
    )
  }

  const filteredTools = useMemo(() => {
    return tools.filter((tool) => {
      const matchesSearch =
        tool.name.toLowerCase().includes(debouncedSearchQuery.toLowerCase()) ||
        tool.description.toLowerCase().includes(debouncedSearchQuery.toLowerCase()) ||
        tool.tags.some((tag) => tag.toLowerCase().includes(debouncedSearchQuery.toLowerCase()))
      const matchesCategory = selectedCategory === 'all' || tool.category === selectedCategory
      const matchesStatus = selectedStatus === 'all' || tool.status === selectedStatus
      return matchesSearch && matchesCategory && matchesStatus
    })
  }, [tools, debouncedSearchQuery, selectedCategory, selectedStatus])

  const getCategoryIcon = (category: MCPTool['category']) => {
    switch (category) {
      case 'core':
        return <Zap className="w-4 h-4 text-blue-400" />
      case 'memory':
        return <Database className="w-4 h-4 text-green-400" />
      case 'timeline':
        return <TrendingUp className="w-4 h-4 text-purple-400" />
      case 'goal':
        return <TrendingUp className="w-4 h-4 text-yellow-400" />
      case 'autonomous':
        return <Brain className="w-4 h-4 text-orange-400" />
      case 'collaboration':
        return <Brain className="w-4 h-4 text-pink-400" />
      case 'observability':
        return <Shield className="w-4 h-4 text-red-400" />
      default:
        return <Wrench className="w-4 h-4 text-gray-400" />
    }
  }

  const getStatusIcon = (status: MCPTool['status']) => {
    switch (status) {
      case 'working':
        return <CheckCircle2 className="w-4 h-4 text-green-400" />
      case 'broken':
        return <AlertCircle className="w-4 h-4 text-red-400" />
      case 'placeholder':
        return <AlertCircle className="w-4 h-4 text-yellow-400" />
      default:
        return <Wrench className="w-4 h-4 text-gray-400" />
    }
  }

  return (
    <ErrorBoundary>
      <div className="h-full flex flex-col bg-gray-800" role="complementary" aria-label="Tool Selection Panel">
        {isLoading ? (
          <LoadingState message="Loading tool metrics..." />
        ) : (
          <>
      {/* Header */}
      <div className="h-10 bg-gray-900 border-b border-gray-700 flex items-center justify-between px-3 shrink-0">
        <div className="flex items-center">
          <Wrench className="w-4 h-4 mr-2 text-gray-400" />
          <span className="text-sm font-semibold text-gray-300">Tool Selection</span>
          <span className="ml-2 px-2 py-0.5 bg-gray-700 text-gray-400 text-xs rounded">
            {filteredTools.length} {filteredTools.length === 1 ? 'tool' : 'tools'}
          </span>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={() => setViewMode(viewMode === 'list' ? 'metrics' : 'list')}
            className="p-1 text-gray-400 hover:text-gray-300 transition-colors"
            title={viewMode === 'list' ? 'Show Metrics' : 'Show List'}
          >
            {viewMode === 'list' ? <BarChart3 className="w-4 h-4" /> : <Wrench className="w-4 h-4" />}
          </button>
          <button
            className="p-1 text-gray-400 hover:text-gray-300 transition-colors"
            title="Refresh tools"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="p-2 border-b border-gray-700 space-y-2 shrink-0">
        <div className="relative">
          <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search tools..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-8 pr-2 py-1.5 bg-gray-900 border border-gray-700 rounded text-sm text-gray-300 placeholder-gray-500 focus:outline-none focus:border-blue-500"
            aria-label="Search tools"
          />
        </div>
        <div className="flex gap-1 overflow-x-auto">
          {categories.map((category) => (
            <button
              key={category}
              onClick={() => setSelectedCategory(category as any)}
              className={`px-2 py-1 text-xs rounded whitespace-nowrap ${
                selectedCategory === category
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {category}
            </button>
          ))}
        </div>
        <div className="flex gap-1 overflow-x-auto">
          {['all', 'working', 'broken', 'placeholder'].map((status) => (
            <button
              key={status}
              onClick={() => setSelectedStatus(status as any)}
              className={`px-2 py-1 text-xs rounded whitespace-nowrap ${
                selectedStatus === status
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {status}
            </button>
          ))}
        </div>
      </div>

      {/* Tools List */}
      <div className="flex-1 overflow-y-auto p-2">
        {viewMode === 'metrics' ? (
          <div className="space-y-4">
            {/* Overall Statistics */}
            <div className="bg-gray-700/50 rounded p-3 border border-gray-700">
              <h3 className="text-sm font-semibold text-gray-300 mb-3">Overall Statistics</h3>
              <div className="grid grid-cols-2 gap-3 text-xs">
                <div>
                  <div className="text-gray-400 mb-1">Total Tools</div>
                  <div className="text-2xl font-bold text-gray-300">{tools.length}</div>
                </div>
                <div>
                  <div className="text-gray-400 mb-1">Working</div>
                  <div className="text-2xl font-bold text-green-400">{overallStats.working}</div>
                </div>
                <div>
                  <div className="text-gray-400 mb-1">Broken</div>
                  <div className="text-2xl font-bold text-red-400">{overallStats.broken}</div>
                </div>
                <div>
                  <div className="text-gray-400 mb-1">Placeholder</div>
                  <div className="text-2xl font-bold text-yellow-400">{overallStats.placeholder}</div>
                </div>
                <div>
                  <div className="text-gray-400 mb-1">Avg Success Rate</div>
                  <div className="text-2xl font-bold text-blue-400">
                    {(overallStats.avgSuccessRate * 100).toFixed(1)}%
                  </div>
                </div>
                <div>
                  <div className="text-gray-400 mb-1">Avg Latency</div>
                  <div className="text-2xl font-bold text-purple-400">
                    {Math.round(overallStats.avgLatency)}ms
                  </div>
                </div>
                <div>
                  <div className="text-gray-400 mb-1">Total Usage</div>
                  <div className="text-2xl font-bold text-gray-300">{overallStats.totalUsage}</div>
                </div>
                <div>
                  <div className="text-gray-400 mb-1">Avg Confidence</div>
                  <div className="text-2xl font-bold text-green-400">
                    {(overallStats.avgConfidence * 100).toFixed(1)}%
                  </div>
                </div>
              </div>
            </div>

            {/* By Category */}
            <div className="bg-gray-700/50 rounded p-3 border border-gray-700">
              <h3 className="text-sm font-semibold text-gray-300 mb-3">Tools by Category</h3>
              <div className="space-y-2">
                {categories.slice(1).map(category => {
                  const categoryTools = tools.filter(t => t.category === category)
                  const working = categoryTools.filter(t => t.status === 'working').length
                  return (
                    <div key={category}>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm font-medium text-gray-300 capitalize">{category}</span>
                        <span className="text-xs text-gray-400">
                          {working}/{categoryTools.length} working
                        </span>
                      </div>
                      <div className="w-full bg-gray-700 rounded-full h-2">
                        <div
                          className="bg-green-500 h-2 rounded-full"
                          style={{ width: `${(working / categoryTools.length) * 100}%` }}
                        />
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
        ) : filteredTools.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500 text-sm">
            <Wrench className="w-8 h-8 mb-2 opacity-50" />
            <p>No tools found</p>
            {(searchQuery || selectedCategory !== 'all' || selectedStatus !== 'all') && (
              <button
                onClick={() => {
                  setSearchQuery('')
                  setSelectedCategory('all')
                  setSelectedStatus('all')
                }}
                className="mt-2 px-3 py-1 text-xs bg-blue-600 hover:bg-blue-700 rounded text-white"
              >
                Clear Filters
              </button>
            )}
          </div>
        ) : (
          <div className="space-y-1">
            {filteredTools.map((tool) => {
              const isExpanded = expandedTool === tool.id
              return (
                <div
                  key={tool.id}
                  className={`rounded cursor-pointer transition-colors border ${
                    selectedTool?.id === tool.id
                      ? 'bg-blue-600/20 border-blue-500'
                      : 'bg-gray-700 hover:bg-gray-600 border-transparent'
                  }`}
                >
                  <div
                    className="p-2"
                    onClick={() => setSelectedTool(tool)}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      {getCategoryIcon(tool.category)}
                      <span className="text-sm font-mono text-gray-300 flex-1">{tool.name}</span>
                      {getStatusIcon(tool.status)}
                      <span className="text-xs text-gray-500">{tool.usageCount} uses</span>
                      {tool.cmcAtomId && (
                        <span className="text-xs text-purple-400 flex items-center gap-0.5" title="CMC Atom ID">
                          <Brain className="w-3 h-3" />
                          CMC
                        </span>
                      )}
                      {tool.recentCalls && tool.recentCalls.length > 0 && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            setExpandedTool(isExpanded ? null : tool.id)
                          }}
                          className="p-0.5 hover:bg-gray-600 rounded"
                        >
                          {isExpanded ? (
                            <ChevronDown className="w-3 h-3 text-gray-400" />
                          ) : (
                            <ChevronRight className="w-3 h-3 text-gray-400" />
                          )}
                        </button>
                      )}
                    </div>
                    <div className="text-xs text-gray-400 mb-1 line-clamp-1">{tool.description}</div>
                    <div className="flex items-center gap-2 text-xs">
                      <span className={`${
                        tool.successRate >= 0.95 ? 'text-green-400' :
                        tool.successRate >= 0.90 ? 'text-yellow-400' :
                        'text-red-400'
                      }`}>
                        {Math.round(tool.successRate * 100)}% success
                      </span>
                      <span className="text-gray-500">•</span>
                      <span className="text-gray-500">{tool.avgLatency}ms</span>
                      <span className="text-gray-500">•</span>
                      <span className="text-blue-400">{Math.round(tool.confidence * 100)}% conf</span>
                    </div>
                    {tool.tags.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-1">
                        {tool.tags.slice(0, 3).map(tag => (
                          <span key={tag} className="px-1 py-0.5 bg-gray-800 text-xs text-gray-500 rounded">
                            {tag}
                          </span>
                        ))}
                        {tool.tags.length > 3 && (
                          <span className="text-xs text-gray-500">+{tool.tags.length - 3}</span>
                        )}
                      </div>
                    )}
                  </div>
                  {isExpanded && tool.recentCalls && (
                    <div className="px-2 pb-2 border-t border-gray-700">
                      <div className="text-xs text-gray-400 mb-1">Recent Latencies</div>
                      {renderLatencyChart(tool.recentCalls)}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* Tool Detail */}
      {selectedTool && (
        <div className="p-3 border-t border-gray-700 bg-gray-900 shrink-0 max-h-96 overflow-y-auto">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              {getCategoryIcon(selectedTool.category)}
              <span className="text-sm font-mono text-white">{selectedTool.name}</span>
              {getStatusIcon(selectedTool.status)}
            </div>
            <div className="flex items-center gap-1">
              {selectedTool.documentation && (
                <a
                  href={selectedTool.documentation}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-1 text-gray-400 hover:text-gray-300 hover:bg-gray-800 rounded"
                  title="View documentation"
                >
                  <ExternalLink className="w-3 h-3" />
                </a>
              )}
              <button
                onClick={() => setSelectedTool(null)}
                className="text-gray-400 hover:text-gray-300"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>
          <p className="text-xs text-gray-400 mb-2">{selectedTool.description}</p>
          <div className="space-y-1 text-xs text-gray-400">
            <div className="flex justify-between">
              <span>Category:</span>
              <span className="text-gray-300 capitalize">{selectedTool.category}</span>
            </div>
            <div className="flex justify-between">
              <span>Status:</span>
              <span className={selectedTool.status === 'working' ? 'text-green-400' : selectedTool.status === 'broken' ? 'text-red-400' : 'text-yellow-400'}>
                {selectedTool.status}
              </span>
            </div>
            <div className="flex justify-between">
              <span>Usage Count:</span>
              <span className="text-gray-300">{selectedTool.usageCount}</span>
            </div>
            <div className="flex justify-between">
              <span>Success Rate:</span>
              <span className={`${
                selectedTool.successRate >= 0.95 ? 'text-green-400' :
                selectedTool.successRate >= 0.90 ? 'text-yellow-400' :
                'text-red-400'
              }`}>
                {Math.round(selectedTool.successRate * 100)}%
              </span>
            </div>
            <div className="flex justify-between">
              <span>Avg Latency:</span>
              <span className="text-gray-300">{selectedTool.avgLatency}ms</span>
            </div>
            <div className="flex justify-between">
              <span>Confidence:</span>
              <span className="text-blue-400">{Math.round(selectedTool.confidence * 100)}%</span>
            </div>
            {selectedTool.lastUsed && (
              <div className="flex justify-between">
                <span>Last Used:</span>
                <span className="text-gray-300">{new Date(selectedTool.lastUsed).toLocaleDateString()}</span>
              </div>
            )}
            {selectedTool.cmcAtomId && (
              <div className="flex justify-between">
                <span>CMC Atom:</span>
                <span className="text-purple-400 font-mono text-xs">{selectedTool.cmcAtomId.substring(0, 12)}...</span>
              </div>
            )}
            {selectedTool.recentCalls && selectedTool.recentCalls.length > 0 && (
              <div className="mt-2 pt-2 border-t border-gray-700">
                <div className="text-gray-400 mb-1 flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  Recent Latencies
                </div>
                {renderLatencyChart(selectedTool.recentCalls)}
              </div>
            )}
            {selectedTool.errorBreakdown && selectedTool.errorBreakdown.length > 0 && (
              <div className="mt-2 pt-2 border-t border-gray-700">
                <div className="font-semibold mb-1 text-red-400 flex items-center gap-1">
                  <AlertCircle className="w-3 h-3" />
                  Error Breakdown
                </div>
                <div className="space-y-1">
                  {selectedTool.errorBreakdown.map((error, idx) => (
                    <div key={idx} className="flex items-center justify-between text-xs">
                      <span className="text-gray-300">{error.type}</span>
                      <div className="flex items-center gap-2">
                        <div className="w-24 bg-gray-700 rounded-full h-1.5">
                          <div
                            className="bg-red-500 h-1.5 rounded-full"
                            style={{ width: `${error.percentage}%` }}
                          />
                        </div>
                        <span className="text-gray-400 w-12 text-right">
                          {error.count} ({error.percentage.toFixed(1)}%)
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            {selectedTool.tags.length > 0 && (
              <div className="mt-2 pt-2 border-t border-gray-700">
                <div className="font-semibold mb-1">Tags:</div>
                <div className="flex flex-wrap gap-1">
                  {selectedTool.tags.map((tag) => (
                    <span key={tag} className="px-2 py-0.5 bg-blue-600/20 text-blue-300 rounded text-xs">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
          </>
        )}
      </div>
    </ErrorBoundary>
  )
}

