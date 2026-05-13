/**
 * AIM-OS Integration Component
 * Comprehensive integration with all AIM-OS systems and MCP tools
 */

import React, { useState, useEffect } from 'react'
import { 
  Brain, 
  Database, 
  Search, 
  Shield, 
  Network, 
  Target, 
  GitBranch,
  Activity,
  Clock,
  BarChart3,
  Zap,
  Users,
  Settings,
  Play,
  Pause,
  Square,
  RefreshCw
} from 'lucide-react'
import { mcpIntegration, MCPTool, MCPToolResult } from '../lib/mcp-integration'
import { performanceMonitor } from '../lib/performance-monitor'
import { errorHandler } from '../lib/error-handler'

interface AIMOSIntegrationProps {
  className?: string
}

export const AIMOSIntegration: React.FC<AIMOSIntegrationProps> = ({ className = '' }) => {
  const [tools, setTools] = useState<MCPTool[]>([])
  const [isInitialized, setIsInitialized] = useState(false)
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [executionResults, setExecutionResults] = useState<MCPToolResult[]>([])
  const [isExecuting, setIsExecuting] = useState(false)
  const [performanceStats, setPerformanceStats] = useState<any>(null)

  // Initialize MCP integration
  useEffect(() => {
    const initialize = async () => {
      try {
        const success = await mcpIntegration.initialize()
        setIsInitialized(success)
        
        if (success) {
          const availableTools = mcpIntegration.getAvailableTools()
          setTools(availableTools)
        }
      } catch (error) {
        console.error('Failed to initialize MCP integration:', error)
      }
    }

    initialize()
  }, [])

  // Load performance stats
  useEffect(() => {
    const loadStats = () => {
      try {
        const report = performanceMonitor.getPerformanceReport()
        setPerformanceStats(report)
      } catch (error) {
        console.error('Failed to load performance stats:', error)
      }
    }

    loadStats()
    const interval = setInterval(loadStats, 5000) // Update every 5 seconds
    return () => clearInterval(interval)
  }, [])

  // Execute MCP tool
  const executeTool = async (toolId: string, parameters: Record<string, any> = {}) => {
    setIsExecuting(true)
    
    try {
      const result = await mcpIntegration.executeTool(toolId, parameters)
      setExecutionResults(prev => [result, ...prev.slice(0, 9)]) // Keep last 10 results
      
      // Track performance
      performanceMonitor.recordAIMOSOperation(`mcp_tool_execution_${toolId}`, result.executionTime)
      
    } catch (error) {
      errorHandler.handleError(error as Error, {
        component: 'AIMOSIntegration',
        action: 'executeTool'
      })
    } finally {
      setIsExecuting(false)
    }
  }

  // Get tools by category
  const getToolsByCategory = (category: string) => {
    if (category === 'all') return tools
    return tools.filter(tool => tool.category === category)
  }

  // Get category icon
  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'Core AIM-OS': return <Brain className="w-4 h-4" />
      case 'SCOR': return <Shield className="w-4 h-4" />
      case 'Snapshot': return <Database className="w-4 h-4" />
      case 'Timeline Context': return <Clock className="w-4 h-4" />
      case 'Goal Timeline': return <Target className="w-4 h-4" />
      case 'Intuitive Intelligence': return <Zap className="w-4 h-4" />
      case 'Co-Agency': return <Users className="w-4 h-4" />
      case 'Dataset Management': return <BarChart3 className="w-4 h-4" />
      case 'Application Lifecycle': return <Settings className="w-4 h-4" />
      case 'Autonomous Protocol': return <Activity className="w-4 h-4" />
      default: return <Settings className="w-4 h-4" />
    }
  }

  // Get category color
  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'Core AIM-OS': return 'text-blue-400'
      case 'SCOR': return 'text-red-400'
      case 'Snapshot': return 'text-green-400'
      case 'Timeline Context': return 'text-yellow-400'
      case 'Goal Timeline': return 'text-purple-400'
      case 'Intuitive Intelligence': return 'text-pink-400'
      case 'Co-Agency': return 'text-cyan-400'
      case 'Dataset Management': return 'text-orange-400'
      case 'Application Lifecycle': return 'text-indigo-400'
      case 'Autonomous Protocol': return 'text-emerald-400'
      default: return 'text-gray-400'
    }
  }

  const categories = [
    'all',
    'Core AIM-OS',
    'SCOR',
    'Snapshot',
    'Timeline Context',
    'Goal Timeline',
    'Intuitive Intelligence',
    'Co-Agency',
    'Dataset Management',
    'Application Lifecycle',
    'Autonomous Protocol'
  ]

  const filteredTools = getToolsByCategory(selectedCategory)

  return (
    <div className={`h-full bg-gray-800 flex flex-col ${className}`}>
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Brain className="w-5 h-5 text-blue-400" />
            <div>
              <div className="text-white text-sm font-semibold">AIM-OS Integration</div>
              <div className="text-xs text-gray-500">
                {isInitialized ? `${tools.length} MCP tools available` : 'Initializing...'}
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${isInitialized ? 'bg-green-500' : 'bg-yellow-500'}`} />
            <span className="text-xs text-gray-400">
              {isInitialized ? 'Connected' : 'Connecting...'}
            </span>
          </div>
        </div>
      </div>

      {/* Category Filter */}
      <div className="px-4 py-2 border-b border-gray-700">
        <div className="flex gap-2 overflow-x-auto">
          {categories.map(category => (
            <button
              key={category}
              onClick={() => setSelectedCategory(category)}
              className={`flex items-center gap-1 px-3 py-1 text-xs rounded whitespace-nowrap transition-colors ${
                selectedCategory === category
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {category !== 'all' && getCategoryIcon(category)}
              <span>{category === 'all' ? 'All' : category}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Tools Grid */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {filteredTools.map(tool => (
            <div
              key={tool.id}
              className="bg-gray-700 rounded-lg p-3 hover:bg-gray-600 transition-colors"
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <div className={getCategoryColor(tool.category)}>
                    {getCategoryIcon(tool.category)}
                  </div>
                  <div>
                    <div className="text-sm font-medium text-white">{tool.name}</div>
                    <div className="text-xs text-gray-400">{tool.category}</div>
                  </div>
                </div>
                
                <div className="flex items-center gap-1 text-xs text-gray-400">
                  <span>{tool.usageCount}</span>
                  <Activity className="w-3 h-3" />
                </div>
              </div>
              
              <div className="text-xs text-gray-300 mb-3 line-clamp-2">
                {tool.description}
              </div>
              
              <button
                onClick={() => executeTool(tool.id)}
                disabled={isExecuting || !tool.isAvailable}
                className="w-full px-3 py-1 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white text-xs rounded transition-colors"
              >
                {isExecuting ? 'Executing...' : 'Execute'}
              </button>
            </div>
          ))}
        </div>
        
        {filteredTools.length === 0 && (
          <div className="text-center text-gray-400 text-sm py-8">
            <Settings className="w-12 h-12 mx-auto mb-4 text-gray-600" />
            <div>No tools available in this category</div>
          </div>
        )}
      </div>

      {/* Execution Results */}
      {executionResults.length > 0 && (
        <div className="border-t border-gray-700 p-4">
          <div className="text-sm font-medium text-white mb-2">Recent Executions</div>
          <div className="space-y-2 max-h-32 overflow-y-auto">
            {executionResults.slice(0, 5).map((result, index) => (
              <div
                key={index}
                className={`text-xs p-2 rounded ${
                  result.success
                    ? 'bg-green-900/20 text-green-300'
                    : 'bg-red-900/20 text-red-300'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium">{result.tool}</span>
                  <span>{result.executionTime}ms</span>
                </div>
                {result.success ? (
                  <div className="text-gray-400">Success</div>
                ) : (
                  <div className="text-red-400">{result.error}</div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Performance Stats */}
      {performanceStats && (
        <div className="border-t border-gray-700 p-4">
          <div className="text-sm font-medium text-white mb-2">Performance Stats</div>
          <div className="grid grid-cols-2 gap-4 text-xs">
            <div>
              <div className="text-gray-400">Avg Render Time</div>
              <div className="text-white font-medium">
                {performanceStats.summary.averageRenderTime.toFixed(1)}ms
              </div>
            </div>
            <div>
              <div className="text-gray-400">Memory Usage</div>
              <div className="text-white font-medium">
                {(performanceStats.summary.memoryUsage / 1024 / 1024).toFixed(1)}MB
              </div>
            </div>
            <div>
              <div className="text-gray-400">Interactions</div>
              <div className="text-white font-medium">
                {performanceStats.summary.interactionCount}
              </div>
            </div>
            <div>
              <div className="text-gray-400">AIM-OS Response</div>
              <div className="text-white font-medium">
                {performanceStats.summary.aimosResponseTime.toFixed(1)}ms
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
