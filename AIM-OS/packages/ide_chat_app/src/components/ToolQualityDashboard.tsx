import React, { useState, useEffect } from 'react'
import { 
  BarChart3, 
  TrendingUp, 
  TrendingDown, 
  CheckCircle, 
  AlertTriangle, 
  XCircle,
  RefreshCw,
  Brain,
  Shield,
  Clock,
  Target,
  Zap
} from 'lucide-react'

interface ToolQuality {
  tool_name: string
  category: string
  status: string
  quality_metrics: {
    response_relevance: number
    context_understanding: number
    system_integration: number
    learning_adaptation: number
    consciousness_focus: number
  }
  overall_score: number
  improvement_ideas: string[]
  evolution_timeline: Array<{
    date: string
    update: string
  }>
  notes: string
}

interface ToolQualityDashboardProps {
  className?: string
}

export const ToolQualityDashboard: React.FC<ToolQualityDashboardProps> = ({ className = '' }) => {
  const [tools, setTools] = useState<ToolQuality[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [selectedCategory, setSelectedCategory] = useState<string>('All')
  const [sortBy, setSortBy] = useState<'name' | 'score' | 'category'>('score')

  const categories = [
    'All', 'Core AIM-OS', 'Autonomous', 'SCOR', 'Timeline', 
    'Goal Timeline', 'IIS', 'Co-Agency', 'Dataset', 'Application', 'ARD', 'AI Collaboration'
  ]

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'working':
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'needs_review':
        return <AlertTriangle className="w-4 h-4 text-yellow-500" />
      case 'error':
        return <XCircle className="w-4 h-4 text-red-500" />
      default:
        return <Clock className="w-4 h-4 text-gray-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'working':
        return 'text-green-500'
      case 'needs_review':
        return 'text-yellow-500'
      case 'error':
        return 'text-red-500'
      default:
        return 'text-gray-500'
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'text-green-500'
    if (score >= 0.6) return 'text-yellow-500'
    return 'text-red-500'
  }

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'Core AIM-OS':
        return <Brain className="w-4 h-4" />
      case 'Autonomous':
        return <Zap className="w-4 h-4" />
      case 'SCOR':
        return <Shield className="w-4 h-4" />
      case 'Timeline':
        return <Clock className="w-4 h-4" />
      case 'Goal Timeline':
        return <Target className="w-4 h-4" />
      default:
        return <BarChart3 className="w-4 h-4" />
    }
  }

  const filteredTools = tools.filter(tool => 
    selectedCategory === 'All' || tool.category === selectedCategory
  ).sort((a, b) => {
    switch (sortBy) {
      case 'name':
        return a.tool_name.localeCompare(b.tool_name)
      case 'score':
        return b.overall_score - a.overall_score
      case 'category':
        return a.category.localeCompare(b.category)
      default:
        return 0
    }
  })

  const averageScore = tools.length > 0 
    ? tools.reduce((sum, tool) => sum + tool.overall_score, 0) / tools.length 
    : 0

  const categoryStats = categories.slice(1).map(category => {
    const categoryTools = tools.filter(tool => tool.category === category)
    const avgScore = categoryTools.length > 0
      ? categoryTools.reduce((sum, tool) => sum + tool.overall_score, 0) / categoryTools.length
      : 0
    return { category, count: categoryTools.length, avgScore }
  })

  return (
    <div className={`p-6 bg-gray-900 text-white rounded-lg shadow-lg ${className}`}>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold flex items-center">
          <BarChart3 className="w-6 h-6 mr-2" />
          Tool Quality Dashboard
        </h2>
        <div className="flex items-center space-x-4">
          <div className="text-sm text-gray-400">
            Average Score: <span className={`font-bold ${getScoreColor(averageScore)}`}>
              {(averageScore * 100).toFixed(1)}%
            </span>
          </div>
          <button
            onClick={() => setIsLoading(true)}
            className="p-2 rounded-full bg-gray-700 hover:bg-gray-600 transition-colors duration-200"
            title="Refresh Data"
          >
            <RefreshCw className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Category Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 mb-6">
        {categoryStats.map(({ category, count, avgScore }) => (
          <div key={category} className="bg-gray-800 p-3 rounded-md">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium">{category}</span>
              {getCategoryIcon(category)}
            </div>
            <div className="text-xs text-gray-400">
              {count} tools
            </div>
            <div className={`text-sm font-bold ${getScoreColor(avgScore)}`}>
              {(avgScore * 100).toFixed(1)}%
            </div>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-4 mb-6">
        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          className="px-3 py-2 bg-gray-800 border border-gray-700 rounded-md text-white"
        >
          {categories.map(category => (
            <option key={category} value={category}>{category}</option>
          ))}
        </select>
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value as 'name' | 'score' | 'category')}
          className="px-3 py-2 bg-gray-800 border border-gray-700 rounded-md text-white"
        >
          <option value="score">Sort by Score</option>
          <option value="name">Sort by Name</option>
          <option value="category">Sort by Category</option>
        </select>
      </div>

      {/* Tools List */}
      <div className="space-y-4">
        {filteredTools.map((tool) => (
          <div key={tool.tool_name} className="bg-gray-800 p-4 rounded-md">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-3">
                {getStatusIcon(tool.status)}
                <h3 className="font-semibold text-lg">{tool.tool_name}</h3>
                <span className="text-sm text-gray-400">({tool.category})</span>
              </div>
              <div className="flex items-center space-x-4">
                <span className={`text-sm font-bold ${getScoreColor(tool.overall_score)}`}>
                  {(tool.overall_score * 100).toFixed(1)}%
                </span>
                <span className={`text-sm ${getStatusColor(tool.status)}`}>
                  {tool.status.toUpperCase()}
                </span>
              </div>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-3">
              <div className="text-sm">
                <div className="text-gray-400">Relevance</div>
                <div className={`font-medium ${getScoreColor(tool.quality_metrics.response_relevance)}`}>
                  {(tool.quality_metrics.response_relevance * 100).toFixed(0)}%
                </div>
              </div>
              <div className="text-sm">
                <div className="text-gray-400">Context</div>
                <div className={`font-medium ${getScoreColor(tool.quality_metrics.context_understanding)}`}>
                  {(tool.quality_metrics.context_understanding * 100).toFixed(0)}%
                </div>
              </div>
              <div className="text-sm">
                <div className="text-gray-400">Integration</div>
                <div className={`font-medium ${getScoreColor(tool.quality_metrics.system_integration)}`}>
                  {(tool.quality_metrics.system_integration * 100).toFixed(0)}%
                </div>
              </div>
              <div className="text-sm">
                <div className="text-gray-400">Learning</div>
                <div className={`font-medium ${getScoreColor(tool.quality_metrics.learning_adaptation)}`}>
                  {(tool.quality_metrics.learning_adaptation * 100).toFixed(0)}%
                </div>
              </div>
              <div className="text-sm">
                <div className="text-gray-400">Consciousness</div>
                <div className={`font-medium ${getScoreColor(tool.quality_metrics.consciousness_focus)}`}>
                  {(tool.quality_metrics.consciousness_focus * 100).toFixed(0)}%
                </div>
              </div>
            </div>

            {tool.improvement_ideas.length > 0 && (
              <div className="mt-3">
                <div className="text-sm text-gray-400 mb-2">Improvement Ideas:</div>
                <ul className="text-sm text-gray-300 space-y-1">
                  {tool.improvement_ideas.slice(0, 3).map((idea, index) => (
                    <li key={index} className="flex items-start">
                      <span className="text-blue-400 mr-2">•</span>
                      {idea}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
