/**
 * Topic Sidebar Component
 * Obsidian-style topic organization for Manager AI Chat
 */

import React, { useState } from 'react'
import { useTopicStore, Topic, TopicViewMode } from '../store/topicStore'
import { TopicGraphView } from './TopicGraphView'
import { TopicTreeView } from './TopicTreeView'
import {
  Plus, Search, X, Edit2, Trash2, Upload, Download,
  FolderTree, Network as NetworkIcon, Tag, TrendingUp, Target,
  GitBranch, ChevronRight, ChevronDown
} from 'lucide-react'

interface TopicSidebarProps {
  onExport?: () => void
  onImport?: () => void
}

export const TopicSidebar: React.FC<TopicSidebarProps> = ({ onExport, onImport }) => {
  const {
    topics,
    activeTopicId,
    viewMode,
    searchQuery: topicSearchQuery,
    selectedTags,
    selectedGoalId,
    createTopic,
    updateTopic,
    deleteTopic,
    setActiveTopic,
    setViewMode,
    setSearchQuery: setTopicSearchQuery,
    setSelectedTags,
    setSelectedGoalId,
    getTopicById,
    getTopicsByParent,
    getRelatedTopics,
    calculateActivityScore
  } = useTopicStore()
  
  const [editingTopicId, setEditingTopicId] = useState<string | null>(null)
  const [expandedTopics, setExpandedTopics] = useState<Set<string>>(new Set())
  const [localSearchQuery, setLocalSearchQuery] = useState('')
  
  // Filter topics based on view mode
  const filteredTopics = React.useMemo(() => {
    let filtered = topics
    
    // Apply search query
    if (localSearchQuery.trim()) {
      const query = localSearchQuery.toLowerCase()
      filtered = filtered.filter(topic =>
        topic.name.toLowerCase().includes(query) ||
        topic.description?.toLowerCase().includes(query) ||
        topic.tags.some(tag => tag.value.toLowerCase().includes(query)) ||
        topic.hhni_path.some(path => path.toLowerCase().includes(query))
      )
    }
    
    // Apply tag filter
    if (selectedTags.length > 0) {
      filtered = filtered.filter(topic =>
        selectedTags.some(tag => topic.tags.some(t => `${t.key}:${t.value}` === tag))
      )
    }
    
    // Apply goal filter
    if (selectedGoalId) {
      filtered = filtered.filter(topic =>
        topic.linked_goals.some(g => g.goal_id === selectedGoalId)
      )
    }
    
    // Apply view mode filtering
    switch (viewMode) {
      case 'recent':
        filtered = [...filtered].sort((a, b) => {
          const scoreA = calculateActivityScore(a)
          const scoreB = calculateActivityScore(b)
          return scoreB - scoreA
        })
        break
      case 'tree':
        filtered = filtered.filter(t => !t.parent_topic_id)
        break
      case 'linked':
        if (activeTopicId) {
          const related = getRelatedTopics(activeTopicId)
          filtered = related
        }
        break
      case 'tags':
        filtered = filtered.filter(t => t.tags.length > 0)
        break
      case 'goals':
        filtered = filtered.filter(t => t.linked_goals.length > 0)
        break
      case 'graph':
        // Show all topics (graph view handles visualization)
        break
    }
    
    return filtered
  }, [topics, localSearchQuery, selectedTags, selectedGoalId, viewMode, activeTopicId, getRelatedTopics, calculateActivityScore])
  
  const handleCreateTopic = () => {
    const topicId = createTopic()
    setActiveTopic(topicId)
    setEditingTopicId(topicId)
  }
  
  const handleRenameTopic = (topicId: string, newName: string) => {
    if (!newName.trim()) return
    updateTopic(topicId, { name: newName.trim() })
    setEditingTopicId(null)
  }
  
  const handleDeleteTopic = (topicId: string) => {
    if (window.confirm('Are you sure you want to delete this topic? This cannot be undone.')) {
      deleteTopic(topicId)
      if (activeTopicId === topicId) {
        setActiveTopic(null)
      }
    }
  }
  
  const toggleTopicExpansion = (topicId: string) => {
    setExpandedTopics(prev => {
      const next = new Set(prev)
      if (next.has(topicId)) {
        next.delete(topicId)
      } else {
        next.add(topicId)
      }
      return next
    })
  }
  
  const renderTopicTree = (parentId: string | null, level: number = 0): React.ReactNode => {
    const children = getTopicsByParent(parentId)
    if (children.length === 0) return null
    
    return (
      <div className={`ml-${level * 4}`}>
        {children.map(topic => {
          const hasChildren = topic.child_topic_ids.length > 0
          const isExpanded = expandedTopics.has(topic.id)
          const isActive = activeTopicId === topic.id
          
          return (
            <div key={topic.id}>
              <div
                className={`group relative rounded text-sm transition-colors ${
                  isActive
                    ? 'bg-blue-600 text-white'
                    : 'hover:bg-gray-700 text-gray-300'
                }`}
              >
                <div className="flex items-center">
                  {hasChildren && (
                    <button
                      onClick={() => toggleTopicExpansion(topic.id)}
                      className="p-1 hover:bg-gray-600 rounded"
                    >
                      {isExpanded ? (
                        <ChevronDown className="w-3 h-3" />
                      ) : (
                        <ChevronRight className="w-3 h-3" />
                      )}
                    </button>
                  )}
                  {!hasChildren && <div className="w-5" />}
                  
                  <button
                    onClick={() => setActiveTopic(topic.id)}
                    className="flex-1 text-left p-2 pr-8"
                  >
                    {editingTopicId === topic.id ? (
                      <input
                        type="text"
                        defaultValue={topic.name}
                        onBlur={(e) => handleRenameTopic(topic.id, e.target.value)}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') {
                            e.preventDefault()
                            handleRenameTopic(topic.id, (e.target as HTMLInputElement).value)
                          } else if (e.key === 'Escape') {
                            e.preventDefault()
                            setEditingTopicId(null)
                          }
                        }}
                        autoFocus
                        className="w-full bg-gray-800 border border-gray-600 rounded px-2 py-1 text-sm text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        onClick={(e) => e.stopPropagation()}
                      />
                    ) : (
                      <>
                        <div className="font-medium truncate">{topic.name}</div>
                        <div className="text-xs opacity-75 mt-0.5">
                          {topic.messageCount} messages • {new Date(topic.lastActivity).toLocaleDateString()}
                        </div>
                      </>
                    )}
                  </button>
                  
                  {editingTopicId !== topic.id && (
                    <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          setEditingTopicId(topic.id)
                        }}
                        className="p-1 hover:bg-gray-600 rounded text-gray-400 hover:text-gray-200 transition-colors"
                        title="Rename"
                      >
                        <Edit2 className="w-3 h-3" />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleDeleteTopic(topic.id)
                        }}
                        className="p-1 hover:bg-red-600 rounded text-gray-400 hover:text-white transition-colors"
                        title="Delete"
                      >
                        <Trash2 className="w-3 h-3" />
                      </button>
                    </div>
                  )}
                </div>
              </div>
              
              {hasChildren && isExpanded && (
                <div className="ml-4">
                  {renderTopicTree(topic.id, level + 1)}
                </div>
              )}
            </div>
          )
        })}
      </div>
    )
  }
  
  const viewModeButtons: Array<{ mode: TopicViewMode; icon: React.ReactNode; label: string }> = [
    { mode: 'recent', icon: <TrendingUp className="w-4 h-4" />, label: 'Recent' },
    { mode: 'tree', icon: <FolderTree className="w-4 h-4" />, label: 'Tree' },
    { mode: 'graph', icon: <NetworkIcon className="w-4 h-4" />, label: 'Graph' },
    { mode: 'linked', icon: <GitBranch className="w-4 h-4" />, label: 'Linked' },
    { mode: 'tags', icon: <Tag className="w-4 h-4" />, label: 'Tags' },
    { mode: 'goals', icon: <Target className="w-4 h-4" />, label: 'Goals' }
  ]
  
  return (
    <div className="w-64 border-r border-gray-700 bg-gray-800 flex flex-col">
      {/* Header */}
      <div className="p-3 border-b border-gray-700 flex items-center justify-between">
        <h3 className="text-sm font-medium text-gray-300">Topics</h3>
        <div className="flex items-center gap-1">
          {onImport && (
            <button
              onClick={onImport}
              className="p-1.5 hover:bg-gray-700 rounded text-gray-400 hover:text-gray-200 transition-colors"
              title="Import"
              aria-label="Import"
            >
              <Upload className="w-4 h-4" />
            </button>
          )}
          <button
            onClick={handleCreateTopic}
            className="p-1.5 hover:bg-gray-700 rounded text-gray-400 hover:text-gray-200 transition-colors"
            title="New Topic (Ctrl+N)"
            aria-label="New topic"
          >
            <Plus className="w-4 h-4" />
          </button>
        </div>
      </div>
      
      {/* View Mode Selector */}
      <div className="px-3 py-2 border-b border-gray-700">
        <div className="grid grid-cols-3 gap-1">
          {viewModeButtons.map(({ mode, icon, label }) => (
            <button
              key={mode}
              onClick={() => setViewMode(mode)}
              className={`flex flex-col items-center gap-1 p-2 rounded text-xs transition-colors ${
                viewMode === mode
                  ? 'bg-blue-600 text-white'
                  : 'hover:bg-gray-700 text-gray-400 hover:text-gray-200'
              }`}
              title={label}
            >
              {icon}
              <span>{label}</span>
            </button>
          ))}
        </div>
      </div>
      
      {/* Search */}
      <div className="px-3 py-2 border-b border-gray-700">
        <div className="relative">
          <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 w-3 h-3 text-gray-400" />
          <input
            type="text"
            value={localSearchQuery}
            onChange={(e) => {
              setLocalSearchQuery(e.target.value)
              setTopicSearchQuery(e.target.value)
            }}
            placeholder="Search topics..."
            className="w-full bg-gray-900 border border-gray-600 rounded px-7 py-1.5 text-xs text-gray-100 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          {localSearchQuery && (
            <button
              onClick={() => {
                setLocalSearchQuery('')
                setTopicSearchQuery('')
              }}
              className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-200"
            >
              <X className="w-3 h-3" />
            </button>
          )}
        </div>
      </div>
      
      {/* Topic List or Visualization */}
      <div className="flex-1 overflow-hidden">
        {viewMode === 'graph' ? (
          // Graph visualization
          <div className="h-full w-full relative">
            <TopicGraphView />
          </div>
        ) : viewMode === 'tree' ? (
          // Tree visualization
          <TopicTreeView />
        ) : (
          // List views (recent, linked, tags, goals)
          <div className="flex-1 overflow-y-auto p-2 space-y-1">
            {filteredTopics.map(topic => {
              const isActive = activeTopicId === topic.id
              const activityScore = calculateActivityScore(topic)
              
              return (
              <div
                key={topic.id}
                className={`group relative rounded text-sm transition-colors ${
                  isActive
                    ? 'bg-blue-600 text-white'
                    : 'hover:bg-gray-700 text-gray-300'
                }`}
              >
                <button
                  onClick={() => setActiveTopic(topic.id)}
                  className="w-full text-left p-2 pr-8"
                >
                  {editingTopicId === topic.id ? (
                    <input
                      type="text"
                      defaultValue={topic.name}
                      onBlur={(e) => handleRenameTopic(topic.id, e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                          e.preventDefault()
                          handleRenameTopic(topic.id, (e.target as HTMLInputElement).value)
                        } else if (e.key === 'Escape') {
                          e.preventDefault()
                          setEditingTopicId(null)
                        }
                      }}
                      autoFocus
                      className="w-full bg-gray-800 border border-gray-600 rounded px-2 py-1 text-sm text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      onClick={(e) => e.stopPropagation()}
                    />
                  ) : (
                    <>
                      <div className="font-medium truncate">{topic.name}</div>
                      <div className="text-xs opacity-75 mt-0.5 flex items-center gap-2">
                        <span>{topic.messageCount} messages</span>
                        {viewMode === 'recent' && (
                          <span className="text-blue-400">{(activityScore * 100).toFixed(0)}% active</span>
                        )}
                        {topic.tags.length > 0 && (
                          <span className="flex items-center gap-1">
                            <Tag className="w-3 h-3" />
                            {topic.tags.length}
                          </span>
                        )}
                        {topic.linked_goals.length > 0 && (
                          <span className="flex items-center gap-1">
                            <Target className="w-3 h-3" />
                            {topic.linked_goals.length}
                          </span>
                        )}
                      </div>
                      {topic.description && (
                        <div className="text-xs opacity-60 mt-1 truncate">{topic.description}</div>
                      )}
                    </>
                  )}
                </button>
                
                {editingTopicId !== topic.id && (
                  <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        setEditingTopicId(topic.id)
                      }}
                      className="p-1 hover:bg-gray-600 rounded text-gray-400 hover:text-gray-200 transition-colors"
                      title="Rename"
                    >
                      <Edit2 className="w-3 h-3" />
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        handleDeleteTopic(topic.id)
                      }}
                      className="p-1 hover:bg-red-600 rounded text-gray-400 hover:text-white transition-colors"
                      title="Delete"
                    >
                      <Trash2 className="w-3 h-3" />
                    </button>
                  </div>
                )}
              </div>
            )
          })}
          
          {filteredTopics.length === 0 && topics.length > 0 && (
            <div className="text-center text-gray-500 text-sm py-4">
              <p>No topics match your search</p>
            </div>
          )}
          
          {topics.length === 0 && (
            <div className="text-center text-gray-500 text-sm py-8">
              <NetworkIcon className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p>No topics yet</p>
              <p className="text-xs mt-1">Start a conversation to create topics</p>
            </div>
          )}
        </div>
        )}
      </div>
    </div>
  )
}

