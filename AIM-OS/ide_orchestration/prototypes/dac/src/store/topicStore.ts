/**
 * Topic Store - Zustand Store for Topic-Based Chat Organization
 * Replaces conversation threads with Obsidian-style topic organization
 * Integrates with AIM-OS systems: SEG (entities), HHNI (hierarchy), CMC (memory), TCS (timeline)
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'

// Topic Entity (SEG-based)
export interface Topic {
  id: string // SEG entity ID
  name: string
  description?: string
  createdAt: Date
  updatedAt: Date
  lastActivity: Date
  messageCount: number
  
  // HHNI Hierarchy
  hhni_path: string[] // ["system:development", "section:dac-v2", "topic:manager-chat"]
  parent_topic_id?: string
  child_topic_ids: string[]
  level: 'system' | 'section' | 'topic' | 'subtopic' // HHNI level
  
  // SEG Relations
  related_topics: Array<{
    topic_id: string
    relation_type: 'related' | 'parent' | 'child' | 'derived' | 'contradicts'
    strength: number // 0-1
    evidence: string[] // Message IDs that created this relation
  }>
  
  // CMC Tags
  tags: Array<{
    key: string
    value: string
    weight: number
  }>
  
  // Goal Links
  linked_goals: Array<{
    goal_id: string
    objective_id?: string
    relationship: 'supports' | 'blocks' | 'related'
  }>
  
  // File Links
  linked_files: Array<{
    path: string
    relevance: number
  }>
  
  // Embedding (for semantic similarity)
  embedding?: number[]
  
  // Activity metrics
  activity_score: number // Calculated from recency + message count
}

// Topic View Mode
export type TopicViewMode = 'graph' | 'tree' | 'recent' | 'linked' | 'tags' | 'goals'

export interface TopicStore {
  // Topics
  topics: Topic[]
  activeTopicId: string | null
  
  // View state
  viewMode: TopicViewMode
  searchQuery: string
  selectedTags: string[]
  selectedGoalId: string | null
  
  // Topic operations
  createTopic: (name: string, description?: string, parentId?: string) => string
  updateTopic: (topicId: string, updates: Partial<Topic>) => void
  deleteTopic: (topicId: string) => void
  setActiveTopic: (topicId: string | null) => void
  
  // Topic relationships
  linkTopics: (sourceId: string, targetId: string, relationType: Topic['related_topics'][0]['relation_type'], evidence?: string[]) => void
  unlinkTopics: (sourceId: string, targetId: string) => void
  
  // Topic hierarchy
  setParentTopic: (topicId: string, parentId: string | null) => void
  moveTopic: (topicId: string, newParentId: string | null) => void
  
  // Topic tags
  addTagToTopic: (topicId: string, tag: { key: string; value: string; weight?: number }) => void
  removeTagFromTopic: (topicId: string, tagKey: string, tagValue: string) => void
  
  // Topic goals
  linkTopicToGoal: (topicId: string, goalId: string, objectiveId?: string, relationship?: 'supports' | 'blocks' | 'related') => void
  unlinkTopicFromGoal: (topicId: string, goalId: string) => void
  
  // Topic files
  linkTopicToFile: (topicId: string, filePath: string, relevance?: number) => void
  unlinkTopicFromFile: (topicId: string, filePath: string) => void
  
  // View operations
  setViewMode: (mode: TopicViewMode) => void
  setSearchQuery: (query: string) => void
  setSelectedTags: (tags: string[]) => void
  setSelectedGoalId: (goalId: string | null) => void
  
  // Utility
  getTopicById: (topicId: string) => Topic | undefined
  getTopicsByParent: (parentId: string | null) => Topic[]
  getTopicsByTag: (tagKey: string, tagValue: string) => Topic[]
  getTopicsByGoal: (goalId: string) => Topic[]
  getRelatedTopics: (topicId: string) => Topic[]
  getTopicHierarchy: (topicId: string) => Topic[] // Returns topic + all ancestors
  calculateActivityScore: (topic: Topic) => number
}

// Initialize with demo topics if empty (exported for use in persist callback)
const initializeDemoTopics = (): Topic[] => {
        const now = new Date()
        const demoTopics: Topic[] = [
          {
            id: 'topic-demo-manager-ai',
            name: 'Manager AI Chat',
            description: 'Central AI coordination system for AIM-OS',
            createdAt: new Date(now.getTime() - 86400000),
            updatedAt: new Date(now.getTime() - 3600000),
            lastActivity: new Date(now.getTime() - 1800000),
            messageCount: 15,
            hhni_path: ['system:aimos', 'section:ide', 'topic:manager-chat'],
            parent_topic_id: undefined,
            child_topic_ids: ['topic-demo-canvas', 'topic-demo-topics'],
            level: 'system',
            related_topics: [
              {
                topic_id: 'topic-demo-canvas',
                relation_type: 'related',
                strength: 0.85,
                evidence: ['msg-001', 'msg-002']
              }
            ],
            tags: [
              { key: 'type', value: 'system', weight: 1.0 },
              { key: 'category', value: 'ai', weight: 0.9 }
            ],
            linked_goals: [],
            linked_files: [],
            activity_score: 0.75
          },
          {
            id: 'topic-demo-canvas',
            name: 'Canvas Mode',
            description: 'Editable document mode for collaborative editing',
            createdAt: new Date(now.getTime() - 7200000),
            updatedAt: new Date(now.getTime() - 1800000),
            lastActivity: new Date(now.getTime() - 900000),
            messageCount: 8,
            hhni_path: ['system:aimos', 'section:ide', 'topic:manager-chat', 'subtopic:canvas'],
            parent_topic_id: 'topic-demo-manager-ai',
            child_topic_ids: [],
            level: 'subtopic',
            related_topics: [
              {
                topic_id: 'topic-demo-manager-ai',
                relation_type: 'parent',
                strength: 1.0,
                evidence: ['msg-003']
              }
            ],
            tags: [
              { key: 'type', value: 'feature', weight: 1.0 },
              { key: 'category', value: 'document', weight: 0.85 }
            ],
            linked_goals: [],
            linked_files: [],
            activity_score: 0.65
          },
          {
            id: 'topic-demo-topics',
            name: 'Topic Organization',
            description: 'Obsidian-style topic organization system',
            createdAt: new Date(now.getTime() - 3600000),
            updatedAt: new Date(now.getTime() - 600000),
            lastActivity: new Date(now.getTime() - 300000),
            messageCount: 12,
            hhni_path: ['system:aimos', 'section:ide', 'topic:manager-chat', 'subtopic:topics'],
            parent_topic_id: 'topic-demo-manager-ai',
            child_topic_ids: [],
            level: 'subtopic',
            related_topics: [
              {
                topic_id: 'topic-demo-manager-ai',
                relation_type: 'parent',
                strength: 1.0,
                evidence: ['msg-004']
              },
              {
                topic_id: 'topic-demo-canvas',
                relation_type: 'related',
                strength: 0.7,
                evidence: ['msg-005']
              }
            ],
            tags: [
              { key: 'type', value: 'feature', weight: 1.0 },
              { key: 'category', value: 'organization', weight: 0.9 },
              { key: 'style', value: 'obsidian', weight: 0.8 }
            ],
            linked_goals: [],
            linked_files: [],
            activity_score: 0.80
          },
          {
            id: 'topic-demo-seg',
            name: 'SEG Integration',
            description: 'Shared Evidence Graph for knowledge relationships',
            createdAt: new Date(now.getTime() - 172800000),
            updatedAt: new Date(now.getTime() - 86400000),
            lastActivity: new Date(now.getTime() - 43200000),
            messageCount: 5,
            hhni_path: ['system:aimos', 'section:core', 'topic:seg'],
            parent_topic_id: undefined,
            child_topic_ids: [],
            level: 'topic',
            related_topics: [],
            tags: [
              { key: 'type', value: 'system', weight: 1.0 },
              { key: 'category', value: 'graph', weight: 0.95 }
            ],
            linked_goals: [],
            linked_files: [],
            activity_score: 0.45
          }
        ]
        return demoTopics
      }

export const useTopicStore = create<TopicStore>()(
  persist(
    (set, get) => {
      return {
        // Initial state
        topics: initializeDemoTopics(),
        activeTopicId: null,
        viewMode: 'recent',
        searchQuery: '',
        selectedTags: [],
        selectedGoalId: null,
      
        // Create topic
        createTopic: (name, description, parentId) => {
        const topicId = `topic-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
        const now = new Date()
        
        const parentTopic = parentId ? get().getTopicById(parentId) : undefined
        const hhni_path = parentTopic 
          ? [...parentTopic.hhni_path, `topic:${name.toLowerCase().replace(/\s+/g, '-')}`]
          : [`topic:${name.toLowerCase().replace(/\s+/g, '-')}`]
        
        const level: Topic['level'] = parentTopic
          ? parentTopic.level === 'system' ? 'section'
          : parentTopic.level === 'section' ? 'topic'
          : 'subtopic'
          : 'system'
        
        const newTopic: Topic = {
          id: topicId,
          name,
          description,
          createdAt: now,
          updatedAt: now,
          lastActivity: now,
          messageCount: 0,
          hhni_path,
          parent_topic_id: parentId || undefined,
          child_topic_ids: [],
          level,
          related_topics: [],
          tags: [],
          linked_goals: [],
          linked_files: [],
          activity_score: 0
        }
        
        // Update parent's child list
        if (parentId) {
          set(state => ({
            topics: state.topics.map(t => 
              t.id === parentId 
                ? { ...t, child_topic_ids: [...t.child_topic_ids, topicId] }
                : t
            )
          }))
        }
        
        set(state => ({
          topics: [...state.topics, newTopic],
          activeTopicId: topicId
        }))
        
        return topicId
      },
      
      // Update topic
      updateTopic: (topicId, updates) => {
        set(state => ({
          topics: state.topics.map(t => 
            t.id === topicId 
              ? { ...t, ...updates, updatedAt: new Date() }
              : t
          )
        }))
      },
      
      // Delete topic
      deleteTopic: (topicId) => {
        const topic = get().getTopicById(topicId)
        if (!topic) return
        
        // Remove from parent's child list
        if (topic.parent_topic_id) {
          set(state => ({
            topics: state.topics.map(t => 
              t.id === topic.parent_topic_id 
                ? { ...t, child_topic_ids: t.child_topic_ids.filter(id => id !== topicId) }
                : t
            )
          }))
        }
        
        // Remove topic and clear active if needed
        set(state => ({
          topics: state.topics.filter(t => t.id !== topicId),
          activeTopicId: state.activeTopicId === topicId ? null : state.activeTopicId
        }))
      },
      
      // Set active topic
      setActiveTopic: (topicId) => {
        set({ activeTopicId: topicId })
        
        // Update last activity
        if (topicId) {
          get().updateTopic(topicId, { lastActivity: new Date() })
        }
      },
      
      // Link topics
      linkTopics: (sourceId, targetId, relationType, evidence = []) => {
        const strength = 0.8 // Default strength, could be calculated from evidence
        
        set(state => ({
          topics: state.topics.map(t => {
            if (t.id === sourceId) {
              // Check if link already exists
              const existingLink = t.related_topics.find(r => r.topic_id === targetId)
              if (existingLink) {
                return {
                  ...t,
                  related_topics: t.related_topics.map(r =>
                    r.topic_id === targetId
                      ? { ...r, relation_type: relationType, strength, evidence: [...r.evidence, ...evidence] }
                      : r
                  )
                }
              }
              return {
                ...t,
                related_topics: [...t.related_topics, { topic_id: targetId, relation_type: relationType, strength, evidence }]
              }
            }
            return t
          })
        }))
      },
      
      // Unlink topics
      unlinkTopics: (sourceId, targetId) => {
        set(state => ({
          topics: state.topics.map(t =>
            t.id === sourceId
              ? { ...t, related_topics: t.related_topics.filter(r => r.topic_id !== targetId) }
              : t
          )
        }))
      },
      
      // Set parent topic
      setParentTopic: (topicId, parentId) => {
        const topic = get().getTopicById(topicId)
        if (!topic) return
        
        // Remove from old parent
        if (topic.parent_topic_id) {
          set(state => ({
            topics: state.topics.map(t =>
              t.id === topic.parent_topic_id
                ? { ...t, child_topic_ids: t.child_topic_ids.filter(id => id !== topicId) }
                : t
            )
          }))
        }
        
        // Add to new parent
        if (parentId) {
          set(state => ({
            topics: state.topics.map(t =>
              t.id === parentId
                ? { ...t, child_topic_ids: [...t.child_topic_ids, topicId] }
                : t
            )
          }))
        }
        
        // Update topic
        const parentTopic = parentId ? get().getTopicById(parentId) : undefined
        const hhni_path = parentTopic
          ? [...parentTopic.hhni_path, `topic:${topic.name.toLowerCase().replace(/\s+/g, '-')}`]
          : [`topic:${topic.name.toLowerCase().replace(/\s+/g, '-')}`]
        
        const level: Topic['level'] = parentTopic
          ? parentTopic.level === 'system' ? 'section'
          : parentTopic.level === 'section' ? 'topic'
          : 'subtopic'
          : 'system'
        
        get().updateTopic(topicId, {
          parent_topic_id: parentId || undefined,
          hhni_path,
          level
        })
      },
      
      // Move topic
      moveTopic: (topicId, newParentId) => {
        get().setParentTopic(topicId, newParentId)
      },
      
      // Add tag to topic
      addTagToTopic: (topicId, tag) => {
        set(state => ({
          topics: state.topics.map(t =>
            t.id === topicId
              ? {
                  ...t,
                  tags: [
                    ...t.tags.filter(tag => tag.key !== tag.key || tag.value !== tag.value),
                    { key: tag.key, value: tag.value, weight: tag.weight || 1.0 }
                  ]
                }
              : t
          )
        }))
      },
      
      // Remove tag from topic
      removeTagFromTopic: (topicId, tagKey, tagValue) => {
        set(state => ({
          topics: state.topics.map(t =>
            t.id === topicId
              ? { ...t, tags: t.tags.filter(tag => tag.key !== tagKey || tag.value !== tagValue) }
              : t
          )
        }))
      },
      
      // Link topic to goal
      linkTopicToGoal: (topicId, goalId, objectiveId, relationship = 'related') => {
        set(state => ({
          topics: state.topics.map(t =>
            t.id === topicId
              ? {
                  ...t,
                  linked_goals: [
                    ...t.linked_goals.filter(g => g.goal_id !== goalId),
                    { goal_id: goalId, objective_id: objectiveId, relationship }
                  ]
                }
              : t
          )
        }))
      },
      
      // Unlink topic from goal
      unlinkTopicFromGoal: (topicId, goalId) => {
        set(state => ({
          topics: state.topics.map(t =>
            t.id === topicId
              ? { ...t, linked_goals: t.linked_goals.filter(g => g.goal_id !== goalId) }
              : t
          )
        }))
      },
      
      // Link topic to file
      linkTopicToFile: (topicId, filePath, relevance = 0.8) => {
        set(state => ({
          topics: state.topics.map(t =>
            t.id === topicId
              ? {
                  ...t,
                  linked_files: [
                    ...t.linked_files.filter(f => f.path !== filePath),
                    { path: filePath, relevance }
                  ]
                }
              : t
          )
        }))
      },
      
      // Unlink topic from file
      unlinkTopicFromFile: (topicId, filePath) => {
        set(state => ({
          topics: state.topics.map(t =>
            t.id === topicId
              ? { ...t, linked_files: t.linked_files.filter(f => f.path !== filePath) }
              : t
          )
        }))
      },
      
      // View operations
      setViewMode: (mode) => set({ viewMode: mode }),
      setSearchQuery: (query) => set({ searchQuery: query }),
      setSelectedTags: (tags) => set({ selectedTags: tags }),
      setSelectedGoalId: (goalId) => set({ selectedGoalId: goalId }),
      
      // Utility functions
      getTopicById: (topicId) => {
        const state = get()
        return state.topics.find(t => t.id === topicId)
      },
      
      getTopicsByParent: (parentId) => {
        const state = get()
        return state.topics.filter(t => 
          parentId === null 
            ? !t.parent_topic_id
            : t.parent_topic_id === parentId
        )
      },
      
      getTopicsByTag: (tagKey, tagValue) => {
        const state = get()
        return state.topics.filter(t =>
          t.tags.some(tag => tag.key === tagKey && tag.value === tagValue)
        )
      },
      
      getTopicsByGoal: (goalId) => {
        const state = get()
        return state.topics.filter(t =>
          t.linked_goals.some(g => g.goal_id === goalId)
        )
      },
      
      getRelatedTopics: (topicId) => {
        const state = get()
        const topic = state.getTopicById(topicId)
        if (!topic) return []
        
        return topic.related_topics
          .map(rel => state.getTopicById(rel.topic_id))
          .filter((t): t is Topic => t !== undefined)
      },
      
      getTopicHierarchy: (topicId) => {
        const state = get()
        const hierarchy: Topic[] = []
        let currentTopic = state.getTopicById(topicId)
        
        while (currentTopic) {
          hierarchy.unshift(currentTopic)
          if (currentTopic.parent_topic_id) {
            currentTopic = state.getTopicById(currentTopic.parent_topic_id)
          } else {
            break
          }
        }
        
        return hierarchy
      },
      
      calculateActivityScore: (topic) => {
        // Calculate activity score based on recency and message count
        const now = Date.now()
        const lastActivity = topic.lastActivity.getTime()
        const hoursSinceActivity = (now - lastActivity) / (1000 * 60 * 60)
        
        // Recency score (decays over time)
        const recencyScore = Math.max(0, 1 - (hoursSinceActivity / 168)) // Decay over 1 week
        
        // Message count score (logarithmic)
        const messageScore = Math.min(1, Math.log10(topic.messageCount + 1) / 3)
        
        // Combined score
        return (recencyScore * 0.6) + (messageScore * 0.4)
      }
    }
    },
    {
      name: 'dac-manager-ai-topic-store',
      partialize: (state) => ({
        topics: state.topics,
        activeTopicId: state.activeTopicId,
        viewMode: state.viewMode
      }),
      // Only initialize demo topics if store is empty (first load)
      // Also restore Date objects from serialized strings
      onRehydrateStorage: () => (state) => {
        if (state && state.topics) {
          // Restore Date objects from serialized strings
          state.topics = state.topics.map(topic => ({
            ...topic,
            createdAt: topic.createdAt instanceof Date ? topic.createdAt : new Date(topic.createdAt),
            updatedAt: topic.updatedAt instanceof Date ? topic.updatedAt : new Date(topic.updatedAt),
            lastActivity: topic.lastActivity instanceof Date ? topic.lastActivity : new Date(topic.lastActivity)
          }))
        }
        if (state && (!state.topics || state.topics.length === 0)) {
          state.topics = initializeDemoTopics()
        }
      }
    }
  )
)

