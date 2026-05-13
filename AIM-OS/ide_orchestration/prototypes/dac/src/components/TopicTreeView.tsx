/**
 * Topic Tree View Component
 * Hierarchical tree visualization of topics using HHNI structure
 */

import React, { useState, useMemo } from 'react'
import { useTopicStore, Topic } from '../store/topicStore'
import { useHHNI } from '../hooks/useAIMOS'
import { ChevronRight, ChevronDown, Folder, FolderOpen, FileText, Tag, Target, GitBranch } from 'lucide-react'

interface TopicTreeNodeProps {
  topic: Topic
  level: number
  isExpanded: boolean
  onToggle: () => void
  onSelect: () => void
  isActive: boolean
  children: React.ReactNode
}

const TopicTreeNode: React.FC<TopicTreeNodeProps> = ({
  topic,
  level,
  isExpanded,
  onToggle,
  onSelect,
  isActive,
  children
}) => {
  const hasChildren = topic.child_topic_ids.length > 0
  const indent = level * 20
  
  return (
    <div>
      <div
        className={`flex items-center py-1.5 px-2 rounded transition-colors cursor-pointer group ${
          isActive
            ? 'bg-blue-600 text-white'
            : 'hover:bg-gray-700 text-gray-300'
        }`}
        style={{ paddingLeft: `${indent + 8}px` }}
        onClick={onSelect}
      >
        {/* Expand/Collapse Icon */}
        <div className="w-4 h-4 flex items-center justify-center mr-1">
          {hasChildren ? (
            <button
              onClick={(e) => {
                e.stopPropagation()
                onToggle()
              }}
              className="text-gray-400 hover:text-gray-200"
            >
              {isExpanded ? (
                <ChevronDown className="w-4 h-4" />
              ) : (
                <ChevronRight className="w-4 h-4" />
              )}
            </button>
          ) : (
            <div className="w-4 h-4" />
          )}
        </div>
        
        {/* Folder/File Icon */}
        <div className="mr-2">
          {hasChildren ? (
            isExpanded ? (
              <FolderOpen className="w-4 h-4" />
            ) : (
              <Folder className="w-4 h-4" />
            )
          ) : (
            <FileText className="w-4 h-4" />
          )}
        </div>
        
        {/* Topic Name */}
        <div className="flex-1 min-w-0">
          <div className="font-medium truncate">{topic.name}</div>
          <div className="text-xs opacity-75 flex items-center gap-2 mt-0.5">
            <span>{topic.messageCount} msgs</span>
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
            {topic.related_topics.length > 0 && (
              <span className="flex items-center gap-1">
                <GitBranch className="w-3 h-3" />
                {topic.related_topics.length}
              </span>
            )}
          </div>
        </div>
        
        {/* Activity Indicator */}
        <div className="ml-2">
          <div
            className={`w-2 h-2 rounded-full ${
              topic.lastActivity.getTime() > Date.now() - 3600000
                ? 'bg-green-500'
                : topic.lastActivity.getTime() > Date.now() - 86400000
                ? 'bg-yellow-500'
                : 'bg-gray-500'
            }`}
            title={`Last activity: ${topic.lastActivity.toLocaleString()}`}
          />
        </div>
      </div>
      
      {/* Children */}
      {hasChildren && isExpanded && (
        <div className="ml-4">
          {children}
        </div>
      )}
    </div>
  )
}

interface TopicTreeViewProps {
  rootTopicId?: string | null
}

export const TopicTreeView: React.FC<TopicTreeViewProps> = ({ rootTopicId = null }) => {
  const { topics, activeTopicId, setActiveTopic, getTopicsByParent } = useTopicStore()
  const { searchNodes } = useHHNI()
  const [expandedTopics, setExpandedTopics] = useState<Set<string>>(new Set())
  
  // Build tree structure
  const treeData = useMemo(() => {
    const rootTopics = getTopicsByParent(rootTopicId)
    return rootTopics
  }, [topics, rootTopicId, getTopicsByParent])
  
  const toggleExpanded = (topicId: string) => {
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
  
  const renderTreeNode = (topic: Topic, level: number = 0): React.ReactNode => {
    const children = getTopicsByParent(topic.id)
    const isExpanded = expandedTopics.has(topic.id)
    const isActive = activeTopicId === topic.id
    
    return (
      <TopicTreeNode
        key={topic.id}
        topic={topic}
        level={level}
        isExpanded={isExpanded}
        onToggle={() => toggleExpanded(topic.id)}
        onSelect={() => setActiveTopic(topic.id)}
        isActive={isActive}
      >
        {children.map(child => renderTreeNode(child, level + 1))}
      </TopicTreeNode>
    )
  }
  
  // Get HHNI path display
  const getHHNIPath = (topic: Topic): string => {
    return topic.hhni_path.join(' → ')
  }
  
  return (
    <div className="h-full overflow-y-auto bg-gray-900 text-gray-100">
      {/* Header */}
      <div className="sticky top-0 bg-gray-800 border-b border-gray-700 px-4 py-2 z-10">
        <div className="flex items-center justify-between">
          <div className="text-sm font-medium text-gray-300">
            Topic Hierarchy
            {rootTopicId && (
              <span className="ml-2 text-xs text-gray-500">
                ({getTopicsByParent(rootTopicId).length} topics)
              </span>
            )}
          </div>
          <button
            onClick={() => {
              // Expand all
              const allTopicIds = new Set(topics.map(t => t.id))
              setExpandedTopics(allTopicIds)
            }}
            className="text-xs text-gray-400 hover:text-gray-200"
          >
            Expand All
          </button>
        </div>
      </div>
      
      {/* Tree */}
      <div className="p-2">
        {treeData.length === 0 ? (
          <div className="text-center text-gray-500 text-sm py-8">
            <Folder className="w-8 h-8 mx-auto mb-2 opacity-50" />
            <p>No topics found</p>
            {rootTopicId && (
              <p className="text-xs mt-1">This topic has no subtopics</p>
            )}
          </div>
        ) : (
          treeData.map(topic => renderTreeNode(topic, 0))
        )}
      </div>
      
      {/* HHNI Path Display */}
      {activeTopicId && (
        <div className="sticky bottom-0 bg-gray-800 border-t border-gray-700 px-4 py-2">
          <div className="text-xs text-gray-400">
            <span className="font-medium">HHNI Path:</span>{' '}
            {getHHNIPath(topics.find(t => t.id === activeTopicId)!)}
          </div>
        </div>
      )}
    </div>
  )
}

