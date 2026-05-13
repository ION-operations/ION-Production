/**
 * Topic Info Panel Component
 * Shows detailed information about a selected topic including connections, tags, goals, etc.
 */

import React from 'react'
import { Topic } from '../store/topicStore'
import { useTopicStore } from '../store/topicStore'
import { X, Tag, Target, FileText, Link2, MessageSquare, Calendar, TrendingUp, FolderTree } from 'lucide-react'

interface TopicInfoPanelProps {
  topic: Topic | null
  onClose: () => void
  onTopicClick?: (topicId: string) => void
}

export const TopicInfoPanel: React.FC<TopicInfoPanelProps> = ({ topic, onClose, onTopicClick }) => {
  const { topics, getRelatedTopics, getTopicHierarchy } = useTopicStore()
  
  if (!topic) return null
  
  const relatedTopics = getRelatedTopics(topic.id)
  const hierarchy = getTopicHierarchy(topic.id)
  const parentTopic = topic.parent_topic_id ? topics.find(t => t.id === topic.parent_topic_id) : null
  const childTopics = topics.filter(t => t.parent_topic_id === topic.id)
  
  return (
    <div className="absolute top-0 right-0 w-80 h-full bg-gray-800 border-l border-gray-700 shadow-xl z-20 overflow-y-auto">
      <div className="sticky top-0 bg-gray-800 border-b border-gray-700 p-4 flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-100">Topic Details</h3>
        <button
          onClick={onClose}
          className="p-1 hover:bg-gray-700 rounded text-gray-400 hover:text-gray-200 transition-colors"
          aria-label="Close panel"
        >
          <X className="w-5 h-5" />
        </button>
      </div>
      
      <div className="p-4 space-y-6">
        {/* Topic Header */}
        <div>
          <h2 className="text-xl font-bold text-gray-100 mb-2">{topic.name}</h2>
          {topic.description && (
            <p className="text-sm text-gray-400">{topic.description}</p>
          )}
        </div>
        
        {/* Metadata */}
        <div className="space-y-3">
          <div className="flex items-center gap-2 text-sm text-gray-400">
            <MessageSquare className="w-4 h-4" />
            <span>{topic.messageCount} messages</span>
          </div>
          <div className="flex items-center gap-2 text-sm text-gray-400">
            <Calendar className="w-4 h-4" />
            <span>Created {new Date(topic.createdAt).toLocaleDateString()}</span>
          </div>
          <div className="flex items-center gap-2 text-sm text-gray-400">
            <TrendingUp className="w-4 h-4" />
            <span>Activity: {(topic.activity_score * 100).toFixed(0)}%</span>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <span className="px-2 py-1 bg-blue-600/20 text-blue-400 rounded text-xs font-medium">
              {topic.level}
            </span>
          </div>
        </div>
        
        {/* Hierarchy */}
        {hierarchy.length > 1 && (
          <div>
            <h4 className="text-sm font-semibold text-gray-300 mb-2 flex items-center gap-2">
              <FolderTree className="w-4 h-4" />
              Hierarchy
            </h4>
            <div className="space-y-1">
              {hierarchy.map((t, idx) => (
                <div key={t.id} className="flex items-center gap-2 text-sm text-gray-400">
                  {idx > 0 && <span className="text-gray-600">→</span>}
                  {idx === hierarchy.length - 1 ? (
                    <span className="text-gray-200 font-medium">{t.name}</span>
                  ) : (
                    <button
                      onClick={() => onTopicClick?.(t.id)}
                      className="hover:text-blue-400 transition-colors"
                    >
                      {t.name}
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
        
        {/* Parent Topic */}
        {parentTopic && (
          <div>
            <h4 className="text-sm font-semibold text-gray-300 mb-2">Parent Topic</h4>
            <button
              onClick={() => onTopicClick?.(parentTopic.id)}
              className="text-sm text-blue-400 hover:text-blue-300 transition-colors"
            >
              {parentTopic.name}
            </button>
          </div>
        )}
        
        {/* Child Topics */}
        {childTopics.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-gray-300 mb-2">Child Topics ({childTopics.length})</h4>
            <div className="space-y-1">
              {childTopics.map(child => (
                <button
                  key={child.id}
                  onClick={() => onTopicClick?.(child.id)}
                  className="block w-full text-left text-sm text-blue-400 hover:text-blue-300 transition-colors py-1"
                >
                  {child.name}
                </button>
              ))}
            </div>
          </div>
        )}
        
        {/* Related Topics */}
        {relatedTopics.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-gray-300 mb-2 flex items-center gap-2">
              <Link2 className="w-4 h-4" />
              Related Topics ({relatedTopics.length})
            </h4>
            <div className="space-y-2">
              {topic.related_topics.map(rel => {
                const relatedTopic = topics.find(t => t.id === rel.topic_id)
                if (!relatedTopic) return null
                
                return (
                  <div key={rel.topic_id} className="flex items-center justify-between">
                    <button
                      onClick={() => onTopicClick?.(rel.topic_id)}
                      className="text-sm text-blue-400 hover:text-blue-300 transition-colors flex-1 text-left"
                    >
                      {relatedTopic.name}
                    </button>
                    <span className="text-xs text-gray-500 px-2 py-0.5 bg-gray-700 rounded">
                      {rel.relation_type}
                    </span>
                  </div>
                )
              })}
            </div>
          </div>
        )}
        
        {/* Tags */}
        {topic.tags.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-gray-300 mb-2 flex items-center gap-2">
              <Tag className="w-4 h-4" />
              Tags ({topic.tags.length})
            </h4>
            <div className="flex flex-wrap gap-2">
              {topic.tags.map((tag, idx) => (
                <span
                  key={idx}
                  className="px-2 py-1 bg-gray-700 text-gray-300 rounded text-xs"
                >
                  {tag.key}: {tag.value}
                </span>
              ))}
            </div>
          </div>
        )}
        
        {/* Linked Goals */}
        {topic.linked_goals.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-gray-300 mb-2 flex items-center gap-2">
              <Target className="w-4 h-4" />
              Linked Goals ({topic.linked_goals.length})
            </h4>
            <div className="space-y-1">
              {topic.linked_goals.map((goal, idx) => (
                <div key={idx} className="text-sm text-gray-400">
                  <span className="text-blue-400">{goal.goal_id}</span>
                  {goal.objective_id && (
                    <span className="text-gray-600"> → {goal.objective_id}</span>
                  )}
                  <span className="text-gray-600 ml-2">({goal.relationship})</span>
                </div>
              ))}
            </div>
          </div>
        )}
        
        {/* Linked Files */}
        {topic.linked_files.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-gray-300 mb-2 flex items-center gap-2">
              <FileText className="w-4 h-4" />
              Linked Files ({topic.linked_files.length})
            </h4>
            <div className="space-y-1">
              {topic.linked_files.map((file, idx) => (
                <div key={idx} className="text-sm text-gray-400 truncate">
                  {file.path}
                </div>
              ))}
            </div>
          </div>
        )}
        
        {/* HHNI Path */}
        {topic.hhni_path.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-gray-300 mb-2">HHNI Path</h4>
            <div className="text-xs text-gray-500 font-mono">
              {topic.hhni_path.join(' / ')}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

