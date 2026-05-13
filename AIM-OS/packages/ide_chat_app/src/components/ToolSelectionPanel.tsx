/**
 * Tool Selection Component
 * Displays intelligent tool selection results from daemon RAG system
 */

import React, { useState } from 'react'
import { Search, Zap, Brain, Filter, RefreshCw, CheckCircle } from 'lucide-react'
import { useDaemon } from '../hooks/useDaemon'

export const ToolSelectionPanel: React.FC = () => {
  const { processRequest, isLoading } = useDaemon()
  const [userInput, setUserInput] = useState('')
  const [selectedTools, setSelectedTools] = useState<string[]>([])
  const [contextProfile, setContextProfile] = useState<any>(null)
  const [performanceMetrics, setPerformanceMetrics] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  const handleProcessRequest = async () => {
    if (!userInput.trim()) return

    try {
      setError(null)
      const result = await processRequest(userInput, {}, 40, 'BALANCED')
      
      if (result.success) {
        setSelectedTools(result.selected_tools || [])
        setContextProfile(result.context_profile)
        setPerformanceMetrics(result.performance_metrics)
      } else {
        setError('Failed to process request')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to process request')
    }
  }

  return (
    <div className="tool-selection-panel p-4 space-y-4">
      {/* Header */}
      <div className="flex items-center gap-2">
        <Brain className="w-5 h-5" />
        <h2 className="text-lg font-semibold">Intelligent Tool Selection</h2>
      </div>

      {/* Input Area */}
      <div className="space-y-2">
        <div className="flex gap-2">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
            <input
              type="text"
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleProcessRequest()}
              placeholder="Describe what you want to do..."
              className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-blue-500"
            />
          </div>
          <button
            onClick={handleProcessRequest}
            disabled={isLoading || !userInput.trim()}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed rounded-lg flex items-center gap-2"
          >
            {isLoading ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Zap className="w-4 h-4" />
            )}
            Select Tools
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="p-3 bg-red-500/10 border border-red-500 rounded-lg text-sm text-red-400">
          {error}
        </div>
      )}

      {/* Context Profile */}
      {contextProfile && (
        <div className="p-4 bg-gray-800 rounded-lg">
          <h3 className="text-sm font-semibold mb-2 flex items-center gap-2">
            <Filter className="w-4 h-4" />
            Context Profile
          </h3>
          <div className="space-y-1 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-400">Type:</span>
              <span>{contextProfile.context_type || 'Unknown'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Complexity:</span>
              <span>{contextProfile.complexity || 'Unknown'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Confidence:</span>
              <span>{(contextProfile.confidence_score * 100).toFixed(1)}%</span>
            </div>
          </div>
        </div>
      )}

      {/* Selected Tools */}
      {selectedTools.length > 0 && (
        <div className="p-4 bg-gray-800 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-semibold flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-green-500" />
              Selected Tools ({selectedTools.length})
            </h3>
          </div>
          <div className="space-y-1 max-h-64 overflow-y-auto">
            {selectedTools.map((tool, index) => (
              <div
                key={index}
                className="p-2 bg-gray-700 rounded text-sm hover:bg-gray-600 cursor-pointer"
              >
                {tool}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Performance Metrics */}
      {performanceMetrics && (
        <div className="p-4 bg-gray-800 rounded-lg">
          <h3 className="text-sm font-semibold mb-2">Performance</h3>
          <div className="space-y-1 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-400">Total Time:</span>
              <span>{performanceMetrics.total_time_ms?.toFixed(1) || 0}ms</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Context Analysis:</span>
              <span>{performanceMetrics.context_analysis_time_ms?.toFixed(1) || 0}ms</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Tool Selection:</span>
              <span>{performanceMetrics.tool_selection_time_ms?.toFixed(1) || 0}ms</span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ToolSelectionPanel

