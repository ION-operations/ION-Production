/**
 * Topic Selector Component
 * UI for selecting and managing topics in Aether Chat
 * Created by Sage - Frontend Integration Specialist
 */

import React, { useState } from 'react'
import { FolderTree, Plus, Search, X, Tag } from 'lucide-react'
import { useTopicStore, Topic } from '../../store/topicStore'

export interface TopicSelectorProps {
  activeTopicId?: string
  onTopicSelect?: (topicId: string) => void
  onTopicCreate?: (name: string) => string
  showCreate?: boolean
  className?: string
}

export const TopicSelector: React.FC<TopicSelectorProps> = ({
  activeTopicId,
  onTopicSelect,
  onTopicCreate,
  showCreate = true,
  className = '',
}) => {
  const { topics, setActiveTopic, createTopic } = useTopicStore()
  const [searchQuery, setSearchQuery] = useState('')
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [newTopicName, setNewTopicName] = useState('')

  const filteredTopics = topics.filter(topic =>
    topic.name.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const handleTopicSelect = (topicId: string) => {
    setActiveTopic(topicId)
    onTopicSelect?.(topicId)
  }

  const handleCreateTopic = () => {
    if (!newTopicName.trim()) return

    const topicId = onTopicCreate
      ? onTopicCreate(newTopicName.trim())
      : createTopic(newTopicName.trim())

    setActiveTopic(topicId)
    setNewTopicName('')
    setShowCreateForm(false)
  }

  return (
    <div className={`flex flex-col gap-2 ${className}`}>
      {/* Search */}
      <div className="relative">
        <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search topics..."
          className="w-full pl-8 pr-3 py-2 rounded bg-gray-800 text-gray-200 border border-gray-700 focus:outline-none focus:border-blue-500 text-sm"
        />
      </div>

      {/* Create Topic Form */}
      {showCreate && showCreateForm && (
        <div className="flex gap-2">
          <input
            type="text"
            value={newTopicName}
            onChange={(e) => setNewTopicName(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleCreateTopic()}
            placeholder="Topic name..."
            className="flex-1 px-3 py-2 rounded bg-gray-800 text-gray-200 border border-gray-700 focus:outline-none focus:border-blue-500 text-sm"
            autoFocus
          />
          <button
            onClick={handleCreateTopic}
            className="px-3 py-2 rounded bg-blue-600 text-white hover:bg-blue-700 transition-colors text-sm"
          >
            Create
          </button>
          <button
            onClick={() => {
              setShowCreateForm(false)
              setNewTopicName('')
            }}
            className="px-3 py-2 rounded bg-gray-700 text-gray-300 hover:bg-gray-600 transition-colors text-sm"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Topic List */}
      <div className="flex flex-col gap-1 max-h-64 overflow-y-auto">
        {filteredTopics.length === 0 ? (
          <div className="text-sm text-gray-500 p-2 text-center">
            {searchQuery ? 'No topics found' : 'No topics yet'}
          </div>
        ) : (
          filteredTopics.map((topic) => (
            <button
              key={topic.id}
              onClick={() => handleTopicSelect(topic.id)}
              className={`flex items-center gap-2 px-3 py-2 rounded text-sm transition-colors ${
                activeTopicId === topic.id
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
              }`}
            >
              <FolderTree className="w-4 h-4" />
              <span className="flex-1 text-left">{topic.name}</span>
              {topic.messageCount > 0 && (
                <span className="text-xs opacity-75">
                  {topic.messageCount}
                </span>
              )}
            </button>
          ))
        )}
      </div>

      {/* Create Button */}
      {showCreate && !showCreateForm && (
        <button
          onClick={() => setShowCreateForm(true)}
          className="flex items-center gap-2 px-3 py-2 rounded bg-gray-800 text-gray-300 hover:bg-gray-700 transition-colors text-sm"
        >
          <Plus className="w-4 h-4" />
          <span>Create Topic</span>
        </button>
      )}
    </div>
  )
}

