import React, { useState, useEffect } from 'react'
import { useApp } from '../contexts/AppContext'
import { useMemory } from '../hooks/useMemory'
import { Search, Plus, Filter, Brain, Calendar, Tag, Database, Trash2 } from 'lucide-react'

export function MemoryBrowser() {
  const { state, dispatch } = useApp()
  const { isInitialized, stats, getSummaryEntries, searchVectors, clearAllData } = useMemory()
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [memories, setMemories] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(false)

  const categories = ['all', 'session', 'daily', 'weekly', 'monthly']

  // Load memories when component mounts or search changes
  useEffect(() => {
    const loadMemories = async () => {
      if (!isInitialized) return
      
      setIsLoading(true)
      try {
        if (searchQuery.trim()) {
          // Semantic search
          const results = await searchVectors(searchQuery, 20)
          setMemories(results)
        } else {
          // Load summaries
          const summaries = await getSummaryEntries(selectedCategory === 'all' ? undefined : selectedCategory, 20)
          setMemories(summaries)
        }
      } catch (error) {
        console.error('Failed to load memories:', error)
        setMemories([])
      } finally {
        setIsLoading(false)
      }
    }

    loadMemories()
  }, [isInitialized, searchQuery, selectedCategory, getSummaryEntries, searchVectors])

  const filteredMemories = memories.filter(memory => {
    if (searchQuery.trim()) {
      // For search results, they're already filtered
      return true
    }
    
    const matchesCategory = selectedCategory === 'all' || memory.level === selectedCategory
    return matchesCategory
  })

  const formatDate = (date: Date) => {
    return date.toLocaleDateString([], { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="h-64 bg-white/5 backdrop-blur-md border-t border-white/10 flex flex-col">
      {/* Header */}
      <div className="h-12 bg-white/5 backdrop-blur-md border-b border-white/10 flex items-center justify-between px-4">
        <div className="flex items-center space-x-2">
          <Brain className="w-5 h-5 text-blue-400" />
          <h3 className="font-semibold text-white">Memory Browser</h3>
          <span className="bg-blue-500/20 text-blue-400 text-xs px-2 py-1 rounded-full">
            {isInitialized ? stats.totalSize : '...'}
          </span>
        </div>
        <button className="p-1 hover:bg-white/10 rounded-lg transition-colors">
          <Plus className="w-4 h-4 text-gray-400" />
        </button>
      </div>

      {/* Search and Filter */}
      <div className="p-4 border-b border-white/10">
        <div className="flex space-x-3">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search memories..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-white/10 border border-white/20 rounded-lg pl-10 pr-4 py-2 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="bg-white/10 border border-white/20 rounded-lg pl-10 pr-8 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-none"
            >
              {categories.map(category => (
                <option key={category} value={category}>
                  {category.charAt(0).toUpperCase() + category.slice(1)}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Memory List */}
      <div className="flex-1 overflow-y-auto custom-scrollbar">
        {isLoading ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <Brain className="w-12 h-12 text-blue-400 mx-auto mb-3 animate-pulse" />
              <p className="text-gray-400">Loading memories...</p>
            </div>
          </div>
        ) : filteredMemories.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <Database className="w-12 h-12 text-gray-400 mx-auto mb-3" />
              <p className="text-gray-400">
                {searchQuery || selectedCategory !== 'all' 
                  ? 'No memories found matching your criteria'
                  : 'No memories yet. Start a conversation to create memories!'
                }
              </p>
              {isInitialized && stats.totalSize === 0 && (
                <button
                  onClick={async () => {
                    try {
                      await clearAllData()
                      setMemories([])
                    } catch (error) {
                      console.error('Failed to clear data:', error)
                    }
                  }}
                  className="mt-3 flex items-center space-x-1 text-red-400 hover:text-red-300 text-sm transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                  <span>Clear All Data</span>
                </button>
              )}
            </div>
          </div>
        ) : (
          <div className="p-4 space-y-3">
            {filteredMemories.map((memory) => (
              <div
                key={memory.id}
                className="bg-white/5 backdrop-blur-md border border-white/10 rounded-lg p-4 hover:bg-white/10 transition-colors cursor-pointer"
              >
                <div className="flex items-start justify-between mb-2">
                  <h4 className="font-semibold text-white text-sm">{memory.title || 'Untitled Memory'}</h4>
                  <div className="flex items-center space-x-1 text-xs text-gray-400">
                    <Calendar className="w-3 h-3" />
                    <span>{formatDate(memory.createdAt)}</span>
                  </div>
                </div>
                
                <p className="text-gray-300 text-sm mb-3 line-clamp-2">
                  {memory.summary || memory.content}
                </p>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="bg-blue-500/20 text-blue-400 text-xs px-2 py-1 rounded-full">
                      {memory.level || memory.metadata?.type || 'unknown'}
                    </span>
                    <div className="flex items-center space-x-1">
                      <Tag className="w-3 h-3 text-gray-400" />
                      <div className="flex space-x-1">
                        {(memory.tags || []).slice(0, 3).map((tag: string, index: number) => (
                          <span key={index} className="text-xs text-gray-400">
                            {tag}
                          </span>
                        ))}
                        {(memory.tags || []).length > 3 && (
                          <span className="text-xs text-gray-400">
                            +{(memory.tags || []).length - 3}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-1">
                    <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                    <span className="text-xs text-gray-400">
                      {Math.round((memory.importance || 0.5) * 100)}%
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
