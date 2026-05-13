import React, { useState } from 'react'
import { 
  Database, 
  Search, 
  Filter, 
  Tag, 
  Clock, 
  Eye,
  ChevronRight,
  ChevronDown,
  FileText,
  Code,
  Brain,
  Play
} from 'lucide-react'

interface Memory {
  id: string
  content: string
  modality: 'language' | 'code' | 'memory' | 'plan' | 'execution'
  tags: string[]
  timestamp: string
  witnesses: number
}

export const MemoryBrowserEnhanced: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('')
  const [activeFilter, setActiveFilter] = useState<'all' | 'language' | 'code' | 'memory' | 'plan' | 'execution'>('all')
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set())
  const [selectedMemory, setSelectedMemory] = useState<Memory | null>(null)

  // Sample memories
  const [memories] = useState<Memory[]>([
    {
      id: 'mem-001',
      content: 'IDE development started with Code + Docs viewer implementation',
      modality: 'memory',
      tags: ['ide', 'development', 'feature'],
      timestamp: '2025-10-26 14:30',
      witnesses: 3
    },
    {
      id: 'mem-002',
      content: 'function calculateSum(a: number, b: number) { return a + b }',
      modality: 'code',
      tags: ['typescript', 'function'],
      timestamp: '2025-10-26 14:25',
      witnesses: 1
    },
    {
      id: 'mem-003',
      content: 'User requested dual AI chat system with cross-agent communication',
      modality: 'language',
      tags: ['user_request', 'feature', 'ai'],
      timestamp: '2025-10-26 14:20',
      witnesses: 2
    },
    {
      id: 'mem-004',
      content: 'Plan: Complete AIM-OS system visualizations',
      modality: 'plan',
      tags: ['plan', 'aimos', 'visualization'],
      timestamp: '2025-10-26 14:15',
      witnesses: 1
    },
    {
      id: 'mem-005',
      content: 'Executed: Created CodeDocsViewer component',
      modality: 'execution',
      tags: ['execution', 'component'],
      timestamp: '2025-10-26 14:10',
      witnesses: 0
    }
  ])

  const getModalityIcon = (modality: string) => {
    switch (modality) {
      case 'language': return <Brain className="w-4 h-4 text-blue-400" />
      case 'code': return <Code className="w-4 h-4 text-green-400" />
      case 'memory': return <Database className="w-4 h-4 text-purple-400" />
      case 'plan': return <Play className="w-4 h-4 text-yellow-400" />
      case 'execution': return <FileText className="w-4 h-4 text-orange-400" />
      default: return <Database className="w-4 h-4 text-gray-400" />
    }
  }

  const filteredMemories = memories.filter(mem => {
    const matchesSearch = mem.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         mem.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
    const matchesFilter = activeFilter === 'all' || mem.modality === activeFilter
    return matchesSearch && matchesFilter
  })

  const handleToggleExpand = (id: string) => {
    const newExpanded = new Set(expandedIds)
    if (newExpanded.has(id)) {
      newExpanded.delete(id)
    } else {
      newExpanded.add(id)
    }
    setExpandedIds(newExpanded)
  }

  return (
    <div className="h-full bg-gray-800 flex flex-col">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-700 flex items-center gap-2">
        <Database className="w-5 h-5 text-purple-400" />
        <div>
          <div className="text-white text-sm font-semibold">Memory Browser</div>
          <div className="text-xs text-gray-500">CMC Atomic Memories</div>
        </div>
      </div>

      {/* Search and Filter */}
      <div className="p-3 border-b border-gray-700 space-y-2">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search memories..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-gray-700 text-white text-sm px-9 py-2 rounded focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
        </div>
        
        {/* Filter Buttons */}
        <div className="flex gap-2 overflow-x-auto">
          {['all', 'memory', 'code', 'language', 'plan', 'execution'].map((filter) => (
            <button
              key={filter}
              onClick={() => setActiveFilter(filter as any)}
              className={`px-3 py-1 text-xs rounded whitespace-nowrap ${
                activeFilter === filter
                  ? 'bg-purple-500 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {filter.charAt(0).toUpperCase() + filter.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Memory List */}
      <div className="flex-1 overflow-y-auto p-2">
        {filteredMemories.length === 0 ? (
          <div className="text-center text-gray-400 text-sm py-8">
            No memories found
          </div>
        ) : (
          <div className="space-y-1">
            {filteredMemories.map((memory) => (
              <div
                key={memory.id}
                onClick={() => setSelectedMemory(memory)}
                className={`p-3 rounded-lg cursor-pointer transition-colors ${
                  selectedMemory?.id === memory.id
                    ? 'bg-purple-500/20 border border-purple-500'
                    : 'bg-gray-700/50 hover:bg-gray-700 border border-transparent'
                }`}
              >
                {/* Memory Header */}
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    {getModalityIcon(memory.modality)}
                    <span className="text-xs text-gray-400">{memory.id}</span>
                  </div>
                  <div className="flex items-center gap-1 text-xs text-gray-400">
                    <Clock className="w-3 h-3" />
                    {memory.timestamp.split(' ')[1]}
                  </div>
                </div>

                {/* Memory Content */}
                <div className="text-sm text-gray-200 mb-2 line-clamp-2">
                  {memory.content}
                </div>

                {/* Tags */}
                <div className="flex flex-wrap gap-1">
                  {memory.tags.map((tag) => (
                    <span
                      key={tag}
                      className="inline-flex items-center gap-1 px-2 py-0.5 bg-purple-500/20 text-purple-300 text-xs rounded"
                    >
                      <Tag className="w-3 h-3" />
                      {tag}
                    </span>
                  ))}
                </div>

                {/* Witnesses */}
                <div className="flex items-center gap-1 mt-2 text-xs text-gray-400">
                  <Eye className="w-3 h-3" />
                  {memory.witnesses} witnesses
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer Stats */}
      <div className="p-3 border-t border-gray-700">
        <div className="text-xs text-gray-400">
          {filteredMemories.length} of {memories.length} memories
        </div>
      </div>
    </div>
  )
}
