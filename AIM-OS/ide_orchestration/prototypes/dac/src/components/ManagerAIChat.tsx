/**
 * Manager AI Chat Component
 * Main AI chat interface with Manager AI (Aether) that coordinates AIM-OS systems
 */

import React, { useState, useRef, useEffect, useCallback, useMemo } from 'react'
import { useCanvasStore } from '../store/canvasStore'
import { usePanelStore } from '../store/panelStore'
import { useTopicStore, Topic, TopicViewMode } from '../store/topicStore'
import { useCMC, useVIF, useSEG, useAPOE, useCAS, useTCS } from '../hooks/useAIMOS'
import { llmService } from '../services/LLMService'
import { aiCollaborationService, DelegationStatus } from '../services/AICollaborationService'
import { apoeService, PlanExecutionStatus } from '../services/APOEService'
import { TopicDetectionService } from '../services/TopicDetectionService'
import { SystemStatusSidebar } from './SystemStatusSidebar'
import { TopicSidebar } from './TopicSidebar'
import {
  Send, Bot, User, Sparkles, Brain, Settings,
  Plus, FileText, ExternalLink, CheckCircle, AlertCircle,
  Zap, Target, Database, Shield, Network, Clock,
  Search, Filter, Download, MessageSquare, X, Edit2, Trash2, Upload,
  GitBranch, Tag, FolderTree, Network as NetworkIcon, TrendingUp
} from 'lucide-react'

interface ManagerAIMessage {
  id: string
  role: 'user' | 'manager' | 'system' | 'delegated'
  content: string
  timestamp: Date
  topicId?: string // Topic ID (replaces threadId)
  topicTags?: string[] // All topics mentioned in this message
  confidence?: number
  evidence?: Evidence[]
  workReferences?: WorkReference
  evidenceTrail?: EvidenceTrail
  goalAlignment?: GoalAlignment
  delegatedTo?: string
  delegationStatus?: DelegationStatus
  planId?: string
  planStatus?: PlanExecutionStatus
  systemActions?: SystemAction[]
  canvasActions?: {
    createCanvas?: boolean
    addToCanvas?: string
    canvasReference?: string
  }
}

interface SystemAction {
  system: 'CMC' | 'HHNI' | 'VIF' | 'SEG' | 'APOE' | 'CAS' | 'TCS'
  action: string
  result?: any
  timestamp: Date
}

interface Evidence {
  id: string
  type: 'cmc_atom' | 'vif_witness' | 'file' | 'memory' | 'knowledge_graph'
  source: string
  relevance: number
  summary?: string
}

interface WorkReference {
  files?: Array<{
    path: string
    operation: 'created' | 'modified' | 'deleted'
    lines?: number[]
    commit_hash?: string
  }>
  cmc_atoms?: string[]
  vif_witnesses?: string[]
  goals?: string[]
  timeline_entries?: string[]
  git_commits?: string[]
}

interface EvidenceTrail {
  cmc_atom_id?: string
  vif_witness_id?: string
  supporting_files?: Array<{
    path: string
    lines: number[]
    relevance: number
  }>
}

interface GoalAlignment {
  objective?: string
  key_result?: string
  progress?: number
}

export const ManagerAIChat: React.FC = () => {
  const [allMessages, setAllMessages] = useState<ManagerAIMessage[]>([]) // Store all messages (infinite chat)
  const [input, setInput] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [showSearch, setShowSearch] = useState(false)
  const [filterRole, setFilterRole] = useState<'all' | 'user' | 'manager' | 'system'>('all')
  const [topicSearchQuery, setTopicSearchQuery] = useState('')
  const [debouncedSearchQuery, setDebouncedSearchQuery] = useState('')
  const [debouncedTopicSearchQuery, setDebouncedTopicSearchQuery] = useState('')
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' | 'info' } | null>(null)
  const [retryableErrors, setRetryableErrors] = useState<Map<string, { error: Error; retryFn: () => void; originalInput: string }>>(new Map())
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const delegationMonitors = useRef<Map<string, NodeJS.Timeout>>(new Map())
  const planMonitors = useRef<Map<string, NodeJS.Timeout>>(new Map())
  
  // Topic store
  const {
    topics,
    activeTopicId,
    viewMode,
    searchQuery: topicSearchQueryStore,
    selectedTags,
    selectedGoalId,
    createTopic,
    updateTopic,
    deleteTopic,
    setActiveTopic,
    linkTopics,
    setViewMode,
    setSearchQuery: setTopicSearchQueryStore,
    setSelectedTags,
    setSelectedGoalId,
    getTopicById,
    getTopicsByParent,
    getTopicsByTag,
    getTopicsByGoal,
    getRelatedTopics,
    calculateActivityScore
  } = useTopicStore()
  
  // Get messages for active topic (or all if no topic selected)
  const messages = useMemo(() => {
    if (activeTopicId) {
      return allMessages.filter(m => m.topicId === activeTopicId || m.topicTags?.includes(activeTopicId))
    }
    return allMessages
  }, [allMessages, activeTopicId])
  
  // AIM-OS hooks
  const { retrieveAtoms, createAtom } = useCMC()
  const { trackConfidence } = useVIF()
  const { synthesizeKnowledge, entities, relations } = useSEG()
  const { createPlan } = useAPOE()
  const { getMetrics } = useCAS()
  const { addEntry } = useTCS()
  
  // Canvas integration
  const createCanvas = useCanvasStore((state) => state.createCanvas)
  const addMessageToCanvas = useCanvasStore((state) => state.addMessageToCanvas)
  const linkCanvasToMessage = useCanvasStore((state) => state.linkCanvasToMessage)
  const updateCanvas = useCanvasStore((state) => state.updateCanvas)
  const addSection = useCanvasStore((state) => state.addSection)
  const setActiveCanvas = useCanvasStore((state) => state.setActiveCanvas)
  const canvases = useCanvasStore((state) => state.canvases)
  
  // Panel navigation
  const setMainView = usePanelStore((state) => state.setMainView)
  
  // Cleanup monitors on unmount
  useEffect(() => {
    return () => {
      delegationMonitors.current.forEach(interval => clearInterval(interval))
      delegationMonitors.current.clear()
      planMonitors.current.forEach(interval => clearInterval(interval))
      planMonitors.current.clear()
    }
  }, [])
  
  // Monitor plan execution progress
  const monitorPlanProgress = useCallback(async (planId: string) => {
    // Check if already monitoring
    if (planMonitors.current.has(planId)) {
      return
    }

    // Start monitoring interval (check every 3 seconds)
    const interval = setInterval(async () => {
      const status = await apoeService.monitorPlanExecution(planId, (updatedStatus) => {
        // Update message with plan status
        setAllMessages(prev => prev.map(msg => {
          if (msg.planId === planId) {
            return {
              ...msg,
              planStatus: updatedStatus,
              content: updatedStatus.status === 'completed'
                ? `${msg.content}\n\n✅ Plan execution completed (${updatedStatus.completed_steps}/${updatedStatus.total_steps} steps)`
                : updatedStatus.status === 'failed'
                ? `${msg.content}\n\n❌ Plan execution failed: ${updatedStatus.error}`
                : `${msg.content.split('\n\n')[0]}\n\n📊 Plan Progress: ${updatedStatus.completed_steps}/${updatedStatus.total_steps} steps (${Math.round(updatedStatus.progress)}%)`
            }
          }
          return msg
        }))
      })

      // Stop monitoring if completed or failed
      if (status.status === 'completed' || status.status === 'failed' || status.status === 'cancelled') {
        clearInterval(interval)
        planMonitors.current.delete(planId)
      }
    }, 3000)

    planMonitors.current.set(planId, interval)
  }, [])
  
  // Monitor delegation progress
  const monitorDelegationProgress = useCallback(async (threadId: string, fromAI: string, toAI: string) => {
    // Check if already monitoring
    if (delegationMonitors.current.has(threadId)) {
      return
    }

    // Start monitoring interval (check every 5 seconds)
    const interval = setInterval(async () => {
      const status = await aiCollaborationService.monitorDelegation(threadId, fromAI, toAI)
      
      // Update message with delegation status
      setAllMessages(prev => prev.map(msg => {
        if (msg.delegatedTo === toAI && msg.delegationStatus?.thread_id === threadId) {
          return {
            ...msg,
            delegationStatus: status
          }
        }
        return msg
      }))

      // Stop monitoring if completed or failed
      if (status.status === 'completed' || status.status === 'failed') {
        clearInterval(interval)
        delegationMonitors.current.delete(threadId)
        
        // Update message with final result
        if (status.status === 'completed' && status.result) {
          setAllMessages(prev => prev.map(msg => {
            if (msg.delegatedTo === toAI && msg.delegationStatus?.thread_id === threadId) {
              return {
                ...msg,
                content: `${msg.content}\n\n✅ Task completed by ${toAI}:\n${status.result}`,
                delegationStatus: status
              }
            }
            return msg
          }))
        } else if (status.status === 'failed' && status.error) {
          setAllMessages(prev => prev.map(msg => {
            if (msg.delegatedTo === toAI && msg.delegationStatus?.thread_id === threadId) {
              return {
                ...msg,
                content: `${msg.content}\n\n❌ Task failed: ${status.error}`,
                delegationStatus: status
              }
            }
            return msg
          }))
        }
      }
    }, 5000)

    delegationMonitors.current.set(threadId, interval)
  }, [])
  
  // Toast notification helper
  const showToast = (message: string, type: 'success' | 'error' | 'info' = 'info') => {
    setToast({ message, type })
    setTimeout(() => setToast(null), 5000)
  }
  
  // Topic management functions (defined early for keyboard shortcuts)
  const handleCreateNewTopic = useCallback((name?: string, description?: string, parentId?: string) => {
    const topicName = name || `Topic ${topics.length + 1}`
    const topicId = createTopic(topicName, description, parentId)
    setActiveTopic(topicId)
    return topicId
  }, [topics.length, createTopic, setActiveTopic])
  
  // Auto-detect topics from message content (LLM-based)
  const detectTopicsFromMessage = useCallback(async (content: string): Promise<string[]> => {
    // Use enhanced topic detection service
    const detectionResult = await TopicDetectionService.detectTopicsFromContent(
      content,
      topics.map(t => ({
        id: t.id,
        name: t.name,
        tags: t.tags
      })),
      entities
    )
    
    const detectedTopicIds: string[] = []
    
    // Process detected topics
    for (const topic of detectionResult.topics) {
      if (topic.topicId) {
        // Existing topic
        detectedTopicIds.push(topic.topicId)
      } else {
        // New topic - create it
        const newTopicId = createTopic(topic.name, undefined, undefined)
        detectedTopicIds.push(newTopicId)
        
        // Link to related topics if specified
        if (topic.relatedTopics && topic.relatedTopics.length > 0) {
          topic.relatedTopics.forEach(relatedName => {
            const relatedTopic = topics.find(t => t.name.toLowerCase() === relatedName.toLowerCase())
            if (relatedTopic) {
              linkTopics(newTopicId, relatedTopic.id, 'related', [])
            }
          })
        }
      }
    }
    
    // Create SEG entities from detected topics
    if (detectionResult.entities.length > 0) {
      // This would integrate with SEG to create entities
      // For now, we'll just log it
      console.log('Detected SEG entities:', detectionResult.entities)
    }
    
    return [...new Set(detectedTopicIds)] // Remove duplicates
  }, [topics, entities, createTopic, linkTopics])
  
  // Assign topic to message and update topic activity
  const assignTopicToMessage = useCallback((messageId: string, topicId: string) => {
    setAllMessages(prev => prev.map(msg => {
      if (msg.id === messageId) {
        const topicTags = [...(msg.topicTags || []), topicId]
        return {
          ...msg,
          topicId,
          topicTags: [...new Set(topicTags)]
        }
      }
      return msg
    }))
    
    // Update topic activity
    const topic = getTopicById(topicId)
    if (topic) {
      updateTopic(topicId, {
        lastActivity: new Date(),
        messageCount: topic.messageCount + 1,
        activity_score: calculateActivityScore({
          ...topic,
          messageCount: topic.messageCount + 1,
          lastActivity: new Date()
        })
      })
    }
  }, [getTopicById, updateTopic, calculateActivityScore])
  
  const exportConversation = useCallback(() => {
    const activeTopic = activeTopicId ? getTopicById(activeTopicId) : null
    const exportData = {
      topicId: activeTopicId,
      topicName: activeTopic?.name || 'All Messages',
      exportedAt: new Date().toISOString(),
      messageCount: messages.length,
      messages: messages.map(msg => ({
        id: msg.id,
        role: msg.role,
        content: msg.content,
        timestamp: msg.timestamp.toISOString(),
        topicId: msg.topicId,
        topicTags: msg.topicTags,
        confidence: msg.confidence,
        delegatedTo: msg.delegatedTo,
        planId: msg.planId,
        systemActions: msg.systemActions
      }))
    }
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `manager-ai-chat-${activeTopicId || 'export'}-${Date.now()}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }, [activeTopicId, getTopicById, messages])
  
  const importConversation = useCallback(() => {
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = 'application/json'
    input.onchange = async (e) => {
      const file = (e.target as HTMLInputElement).files?.[0]
      if (!file) return
      
      try {
        const text = await file.text()
        const importData = JSON.parse(text)
        
        if (!importData.messages || !Array.isArray(importData.messages)) {
          alert('Invalid import file format')
          return
        }
        
        // Create topic if specified or create default
        let topicId = importData.topicId
        if (topicId && !getTopicById(topicId)) {
          // Topic doesn't exist, create it
          const topicName = importData.topicName || `Imported ${new Date().toLocaleDateString()}`
          topicId = createTopic(topicName, `Imported conversation from ${importData.exportedAt}`)
        } else if (!topicId) {
          // No topic specified, create default
          topicId = createTopic(`Imported ${new Date().toLocaleDateString()}`, `Imported conversation`)
        }
        
        // Import messages
        const importedMessages: ManagerAIMessage[] = importData.messages.map((msg: any) => ({
          id: msg.id || `msg-${Date.now()}-${Math.random()}`,
          role: msg.role || 'user',
          content: msg.content || '',
          timestamp: msg.timestamp ? new Date(msg.timestamp) : new Date(),
          topicId: msg.topicId || topicId,
          topicTags: msg.topicTags || [topicId],
          confidence: msg.confidence,
          delegatedTo: msg.delegatedTo,
          planId: msg.planId,
          systemActions: msg.systemActions
        }))
        
        setAllMessages(prev => [...prev, ...importedMessages])
        setActiveTopic(topicId)
        
        // Update topic with imported messages
        importedMessages.forEach(msg => {
          if (msg.topicId) {
            assignTopicToMessage(msg.id, msg.topicId)
          }
        })
        
        showToast(`Successfully imported ${importedMessages.length} messages`, 'success')
      } catch (error) {
        console.error('Import error:', error)
        showToast(`Failed to import: ${error instanceof Error ? error.message : 'Unknown error'}`, 'error')
      }
    }
    input.click()
  }, [getTopicById, createTopic, setActiveTopic, assignTopicToMessage, showToast])
  
  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])
  
  // Debounce search queries
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearchQuery(searchQuery)
    }, 300)
    return () => clearTimeout(timer)
  }, [searchQuery])
  
  // Debounce topic search query
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedTopicSearchQuery(topicSearchQuery)
      setTopicSearchQueryStore(topicSearchQuery)
    }, 300)
    return () => clearTimeout(timer)
  }, [topicSearchQuery, setTopicSearchQueryStore])
  
  // Auto-dismiss toast
  useEffect(() => {
    if (toast) {
      const timer = setTimeout(() => setToast(null), 5000)
      return () => clearTimeout(timer)
    }
  }, [toast])
  
  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl/Cmd + K: Toggle search
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault()
        setShowSearch(prev => !prev)
        return
      }
      
      // Ctrl/Cmd + N: New topic
      if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
        e.preventDefault()
        handleCreateNewTopic()
        return
      }
      
      // Ctrl/Cmd + E: Export conversation
      if ((e.ctrlKey || e.metaKey) && e.key === 'e' && messages.length > 0) {
        e.preventDefault()
        exportConversation()
        return
      }
      
      // Ctrl/Cmd + I: Import conversation
      if ((e.ctrlKey || e.metaKey) && e.key === 'i') {
        e.preventDefault()
        importConversation()
        return
      }
      
      // Escape: Close search or clear input
      if (e.key === 'Escape') {
        if (showSearch) {
          setShowSearch(false)
          setSearchQuery('')
          setFilterRole('all')
        } else if (input.trim()) {
          setInput('')
        }
        return
      }
    }
    
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [showSearch, messages.length, input, handleCreateNewTopic, exportConversation, importConversation])
  
  const handleSend = useCallback(async () => {
    if (!input.trim() || isProcessing) return
    
    const currentInput = input.trim()
    setInput('')
    setIsProcessing(true)
    
    // Detect topics from user message
    const detectedTopicIds = await detectTopicsFromMessage(currentInput)
    let assignedTopicId = activeTopicId || detectedTopicIds[0]
    
    // Create new topic if no topic detected and none active
    if (!assignedTopicId) {
      assignedTopicId = handleCreateNewTopic(currentInput.substring(0, 50))
    }
    
    const userMessage: ManagerAIMessage = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content: currentInput,
      timestamp: new Date(),
      topicId: assignedTopicId,
      topicTags: detectedTopicIds.length > 0 ? detectedTopicIds : (assignedTopicId ? [assignedTopicId] : [])
    }
    
    // Assign topic to message
    if (assignedTopicId) {
      assignTopicToMessage(userMessage.id, assignedTopicId)
    }
    
    setAllMessages(prev => [...prev, userMessage])
    
    try {
      // Process request and get response structure
      const managerResponse = await processManagerAIRequest(currentInput)
      
      // Assign topic to manager response
      managerResponse.topicId = assignedTopicId
      managerResponse.topicTags = detectedTopicIds.length > 0 ? detectedTopicIds : (assignedTopicId ? [assignedTopicId] : [])
      
      // Assign topic to response message
      if (assignedTopicId) {
        assignTopicToMessage(managerResponse.id, assignedTopicId)
      }
      
      // If it's a direct response, we can stream it
      // Otherwise, add the complete response
      if (managerResponse.systemActions?.some(a => a.system === 'CMC' && a.action.includes('Retrieved context'))) {
        // Stream the response for direct queries
        const streamingMessageId = `msg-streaming-${Date.now()}`
        const streamingMessage: ManagerAIMessage = {
          ...managerResponse,
          id: streamingMessageId,
          content: '' // Start empty for streaming
        }
        setAllMessages(prev => [...prev, streamingMessage])
        
        // Stream response
        let streamedContent = ''
        const contextStrings = managerResponse.evidence?.map(e => e.summary || '').filter(Boolean) || []
        
        try {
          for await (const chunk of llmService.stream({
            prompt: currentInput,
            context: contextStrings,
            systemPrompt: 'You are Aether, the Manager AI for AIM-OS. Coordinate systems and provide helpful responses.',
            stream: true
          })) {
            streamedContent += chunk.content
            setAllMessages(prev => prev.map(m => 
              m.id === streamingMessageId 
                ? { ...m, content: streamedContent }
                : m
            ))
            
            if (chunk.done) break
          }
        } catch (streamError) {
          // Fallback to non-streaming if streaming fails
          console.warn('Streaming failed, using non-streaming response:', streamError)
          setAllMessages(prev => prev.map(m => 
            m.id === streamingMessageId 
              ? { ...m, content: managerResponse.content }
              : m
          ))
          showToast('Streaming failed, showing complete response', 'info')
        }
      } else {
        // Non-streaming response (delegation, planning, etc.)
        setAllMessages(prev => [...prev, managerResponse])
      }
    } catch (error) {
      console.error('Error processing request:', error)
      const errorMessage: ManagerAIMessage = {
        id: `msg-error-${Date.now()}`,
        role: 'system',
        content: `❌ Error: ${error instanceof Error ? error.message : 'Unknown error occurred. Please try again.'}`,
        timestamp: new Date(),
        topicId: assignedTopicId,
        topicTags: userMessage.topicTags
      }
      setAllMessages(prev => [...prev, errorMessage])
      
      // Store retryable error
      const retryFn = () => {
        setInput(currentInput)
        setTimeout(() => handleSend(), 100)
      }
      setRetryableErrors(prev => {
        const newMap = new Map(prev)
        newMap.set(errorMessage.id, { 
          error: error instanceof Error ? error : new Error('Unknown error'), 
          retryFn,
          originalInput: currentInput
        })
        return newMap
      })
      
      showToast(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`, 'error')
    } finally {
      setIsProcessing(false)
    }
  }, [input, isProcessing, retrieveAtoms, trackConfidence, synthesizeKnowledge, createAtom, addEntry, activeTopicId, detectTopicsFromMessage, handleCreateNewTopic, assignTopicToMessage])
  
  const processManagerAIRequest = async (request: string): Promise<ManagerAIMessage> => {
    // Step 1: Retrieve context from CMC/HHNI
    const context = await retrieveAtoms(request, 5)
    
    // Step 2: Analyze request and decide action (LLM-based)
    const analysis = await analyzeRequest(request, context)
    
    // Step 3: Track confidence (use analysis confidence if available, otherwise estimate)
    const estimatedConfidence = analysis.estimatedConfidence || (context.length > 0 ? 0.85 : 0.70)
    const confidenceResult = await trackConfidence(
      request,
      estimatedConfidence,
      context.map(c => c.content.inline || ''),
      'Analyzing user request and coordinating AIM-OS systems'
    )
    
    // Step 4: Execute action
    const systemActions: SystemAction[] = []
    let response = ''
    let delegatedTo: string | undefined
    
    if (analysis.actionType === 'direct') {
      // Direct response via LLM
      response = await generateDirectResponse(request, context, { confidence: estimatedConfidence })
      systemActions.push({
        system: 'CMC',
        action: 'Retrieved context for direct response',
        timestamp: new Date()
      })
      systemActions.push({
        system: 'VIF',
        action: 'Tracked confidence',
        timestamp: new Date()
      })
    } else if (analysis.actionType === 'delegate') {
      // Delegate to specialized AI
      delegatedTo = analysis.delegateTo
      
      // Hand off task via AI Collaboration Service
      const handoffResult = await aiCollaborationService.handoffTaskToAI(
        'manager-ai',
        delegatedTo || 'unknown',
        request,
        {
          context: context.map(c => c.content.inline || '').filter(Boolean),
          original_request: request
        },
        'high'
      )
      
      if (handoffResult.success) {
        response = `I've delegated this task to ${delegatedTo}. Thread ID: ${handoffResult.thread_id}. They're working on it now. I'll monitor their progress and report back.`
        
        // Start monitoring delegation progress
        if (handoffResult.thread_id) {
          monitorDelegationProgress(handoffResult.thread_id, 'manager-ai', delegatedTo || 'unknown')
        }
      } else {
        response = `Failed to delegate task to ${delegatedTo}: ${handoffResult.error || 'Unknown error'}. I'll handle this request directly instead.`
        showToast(`Delegation failed: ${handoffResult.error || 'Unknown error'}`, 'error')
      }
      
      systemActions.push({
        system: 'APOE',
        action: `Delegated to ${delegatedTo}`,
        result: handoffResult,
        timestamp: new Date()
      })
    } else if (analysis.actionType === 'plan') {
      // Create plan via APOE Service
      const planResult = await apoeService.createPlan(
        request,
        context.map(c => c.content.inline || '').join('\n'),
        'medium'
      )
      
      if (planResult.success && planResult.plan) {
        const plan = planResult.plan
        response = `Created execution plan: ${plan.plan_id}\n\nGoal: ${plan.goal}\n\nSteps: ${plan.steps.length}\n\nI'll coordinate the necessary systems and specialized AIs to accomplish this.`
        
        systemActions.push({
          system: 'APOE',
          action: `Created plan ${plan.plan_id}`,
          result: plan,
          timestamp: new Date()
        })
        
        // Execute plan (async, non-blocking)
        apoeService.executePlan(plan.plan_id, {}, {
          original_request: request,
          context: context.map(c => c.content.inline || '')
        }).then(execResult => {
          if (execResult.success && execResult.execution_id) {
            // Start monitoring plan execution
            monitorPlanProgress(plan.plan_id)
          }
        })
      } else {
        response = `Failed to create plan: ${planResult.error || 'Unknown error'}. I'll handle this request directly instead.`
        showToast(`Plan creation failed: ${planResult.error || 'Unknown error'}`, 'error')
      }
    } else if (analysis.actionType === 'coordinate') {
      // Coordinate multiple systems
      response = await coordinateSystems(analysis.systems || [], request)
      systemActions.push({
        system: 'APOE',
        action: 'Coordinated multiple systems',
        timestamp: new Date()
      })
    }
    
    // Step 5: Synthesize knowledge
    await synthesizeKnowledge({
      topics: [request],
      depth: 'medium'
    })
    
    // Step 6: Create message
    const managerMessage: ManagerAIMessage = {
      id: `msg-${Date.now()}`,
      role: 'manager',
      content: response,
      timestamp: new Date(),
      confidence: estimatedConfidence,
      evidence: context.map(c => ({
        id: c.id,
        type: 'cmc_atom' as const,
        source: c.id,
        relevance: 0.8,
        summary: (c.content.inline || '').substring(0, 100)
      })),
      workReferences: {
        cmc_atoms: context.map(c => c.id)
      },
      delegatedTo,
      delegationStatus: analysis.actionType === 'delegate' && systemActions.find(a => a.system === 'APOE' && a.result?.thread_id)
        ? {
            thread_id: systemActions.find(a => a.system === 'APOE' && a.result?.thread_id)?.result?.thread_id || '',
            from_ai: 'manager-ai',
            to_ai: delegatedTo || '',
            task_description: request,
            status: 'pending' as const,
            last_update: new Date().toISOString()
          }
        : undefined,
      planId: analysis.actionType === 'plan' && systemActions.find(a => a.system === 'APOE' && a.result?.plan_id)
        ? systemActions.find(a => a.system === 'APOE' && a.result?.plan_id)?.result?.plan_id
        : undefined,
      planStatus: analysis.actionType === 'plan' && systemActions.find(a => a.system === 'APOE' && a.result?.plan_id)
        ? {
            plan_id: systemActions.find(a => a.system === 'APOE' && a.result?.plan_id)?.result?.plan_id || '',
            status: 'running' as const,
            progress: 0,
            completed_steps: 0,
            total_steps: systemActions.find(a => a.system === 'APOE' && a.result?.steps)?.result?.steps?.length || 0,
            started_at: new Date().toISOString()
          }
        : undefined,
      systemActions,
      canvasActions: {
        createCanvas: analysis.shouldCreateCanvas,
        addToCanvas: analysis.canvasId
      }
    }
    
    // Step 7: Store in CMC
    await createAtom(`User: ${request}\nManager AI: ${response}`, 'text')
    
    // Step 8: Add to timeline
    await addEntry(
      managerMessage.id,
      request,
      {
        confidence: estimatedConfidence,
        systems: systemActions.map(a => a.system)
      }
    )
    
    return managerMessage
  }
  
  const analyzeRequest = async (request: string, context: any[]): Promise<{
    actionType: 'direct' | 'delegate' | 'plan' | 'coordinate'
    delegateTo?: string
    systems?: string[]
    shouldCreateCanvas?: boolean
    canvasId?: string
    complexity?: 'simple' | 'moderate' | 'complex' | 'very_complex'
    estimatedConfidence?: number
  }> => {
    // Use LLM to analyze request intent
    const analysisPrompt = `Analyze this user request and determine the best action type.

User Request: "${request}"

Available Context: ${context.length} relevant memories retrieved

Available Specialized AIs:
- codex: Code generation, refactoring, debugging
- lexicon: Documentation, writing, explanation
- audit: Code review, quality assurance, validation
- architect: System design, architecture planning
- researcher: Research, investigation, analysis

Action Types:
- direct: Simple query that can be answered directly (confidence ≥0.90)
- delegate: Task that should be delegated to a specialized AI (confidence 0.70-0.89)
- plan: Complex task requiring multi-step execution plan (confidence <0.70)
- coordinate: Task requiring multiple AIM-OS systems working together

Canvas Creation:
- shouldCreateCanvas: true if this is documentation, planning, or needs persistent editing
- canvasId: ID of existing canvas if adding to one

Respond with JSON only:
{
  "actionType": "direct" | "delegate" | "plan" | "coordinate",
  "delegateTo": "codex" | "lexicon" | "audit" | "architect" | "researcher" | null,
  "systems": ["CMC", "HHNI", "VIF", "SEG", "APOE", "CAS", "TCS"],
  "shouldCreateCanvas": boolean,
  "canvasId": string | null,
  "complexity": "simple" | "moderate" | "complex" | "very_complex",
  "estimatedConfidence": 0.0-1.0,
  "reasoning": "brief explanation"
}`

    try {
      // Use LLM to analyze request
      const analysisResponse = await llmService.generate({
        prompt: analysisPrompt,
        context: context.map(c => c.content.inline || '').filter(Boolean),
        systemPrompt: 'You are an expert at analyzing user requests and determining optimal action routing. Respond with valid JSON only.',
        model: 'gpt-4-turbo',
        temperature: 0.3, // Lower temperature for more consistent analysis
        maxTokens: 500
      })

      // Parse JSON response
      const jsonMatch = analysisResponse.content.match(/\{[\s\S]*\}/)
      if (jsonMatch) {
        const analysis = JSON.parse(jsonMatch[0])
        
        // Validate and return analysis
        return {
          actionType: analysis.actionType || 'direct',
          delegateTo: analysis.delegateTo || undefined,
          systems: analysis.systems || undefined,
          shouldCreateCanvas: analysis.shouldCreateCanvas || false,
          canvasId: analysis.canvasId || undefined,
          complexity: analysis.complexity || 'moderate',
          estimatedConfidence: analysis.estimatedConfidence || 0.75
        }
      }
    } catch (error) {
      console.warn('LLM-based analysis failed, falling back to keyword matching:', error)
      showToast('Using fallback analysis method', 'info')
    }

    // Fallback to keyword-based analysis
    const lowerRequest = request.toLowerCase()
    
    if (lowerRequest.includes('build') || lowerRequest.includes('create') || lowerRequest.includes('implement')) {
      return {
        actionType: 'plan',
        shouldCreateCanvas: true,
        complexity: 'complex',
        estimatedConfidence: 0.75
      }
    }
    
    if (lowerRequest.includes('code') || lowerRequest.includes('function') || lowerRequest.includes('class')) {
      return {
        actionType: 'delegate',
        delegateTo: 'codex',
        complexity: 'moderate',
        estimatedConfidence: 0.80
      }
    }
    
    if (lowerRequest.includes('document') || lowerRequest.includes('write') || lowerRequest.includes('explain')) {
      return {
        actionType: 'delegate',
        delegateTo: 'lexicon',
        shouldCreateCanvas: true,
        complexity: 'moderate',
        estimatedConfidence: 0.85
      }
    }
    
    return {
      actionType: 'direct',
      complexity: 'simple',
      estimatedConfidence: 0.90
    }
  }
  
  const generateDirectResponse = async (request: string, context: any[], confidence: any): Promise<string> => {
    // Build system prompt with AIM-OS context
    const systemPrompt = `You are Aether, the Manager AI for AIM-OS. You coordinate all AIM-OS systems (CMC, HHNI, VIF, SEG, APOE, CAS, TCS) and specialized AI agents.

Your role:
- Analyze user requests and coordinate appropriate AIM-OS systems
- Delegate tasks to specialized AIs when needed
- Create execution plans for complex tasks
- Synthesize knowledge from multiple sources
- Maintain confidence thresholds (≥0.70 required)
- Provide clear, helpful responses with evidence trails

Current confidence level: ${Math.round(confidence.confidence * 100)}%
Available context: ${context.length} relevant memories retrieved

Respond naturally and helpfully, leveraging AIM-OS capabilities.`

    // Prepare context strings
    const contextStrings = context.map(c => c.content.inline || '').filter(Boolean)

    // Generate response via LLM service
    const llmResponse = await llmService.generate({
      prompt: request,
      context: contextStrings,
      systemPrompt,
      model: 'gpt-4-turbo',
      temperature: 0.7,
      maxTokens: 2000
    })

    return llmResponse.content
  }
  
  const delegateToSpecializedAI = async (aiId: string, request: string, context: any[]): Promise<string> => {
    // Mock delegation (will be replaced with actual AI coordination)
    return `I've delegated this task to ${aiId}. They're working on: "${request}". I'll monitor their progress and report back.`
  }
  
  const coordinateSystems = async (systems: string[], request: string): Promise<string> => {
    // Mock coordination (will be replaced with actual system coordination)
    return `I'm coordinating ${systems.join(', ')} to handle: "${request}". This is a complex operation that requires multiple systems working together.`
  }
  
  const handleCreateCanvas = (messageId: string) => {
    const message = messages.find(m => m.id === messageId)
    if (!message) return
    
    const canvasId = createCanvas({
      title: `Canvas from ${new Date().toLocaleDateString()}`,
      initialContent: message.content,
      aimos: {
        confidence: message.confidence,
        evidence: message.evidence || [],
        workReferences: message.workReferences,
        evidenceTrail: message.evidenceTrail,
        goalAlignment: message.goalAlignment
      }
    })
    
    linkCanvasToMessage(canvasId, messageId)
    
    // Update message with canvas reference
    setAllMessages(prev => prev.map(m => 
      m.id === messageId 
        ? { ...m, canvasActions: { ...m.canvasActions, canvasReference: canvasId } }
        : m
    ))
    
    // Navigate to Canvas view
    setActiveCanvas(canvasId)
    setMainView('canvas')
  }
  
  const handleViewCanvas = (canvasId: string) => {
    setActiveCanvas(canvasId)
    setMainView('canvas')
  }
  
  const handleAddToCanvas = (messageId: string, canvasId: string) => {
    const message = messages.find(m => m.id === messageId)
    if (!message) return
    
    const canvas = canvases.find(c => c.id === canvasId)
    if (!canvas) return
    
    // Add message content as a new section to the canvas
    addSection(canvasId, {
      type: 'text',
      content: message.content,
      order: canvas.sections.length,
      aimosMetadata: {
        confidence: message.confidence,
        evidence_trail: message.evidence || [],
        work_references: message.workReferences,
        actor: 'ai',
        actorName: 'Manager AI',
        timestamp: new Date().toISOString()
      },
      linkedChatMessages: [messageId]
    })
    
    // Navigate to Canvas view to show the update
    setActiveCanvas(canvasId)
    setMainView('canvas')
  }
  
  // Filter topics based on view mode and search (memoized)
  const filteredTopics = useMemo(() => {
    let filtered = topics
    
    // Apply search query
    if (debouncedTopicSearchQuery.trim()) {
      const query = debouncedTopicSearchQuery.toLowerCase()
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
        // Sort by activity score (most recent first)
        filtered = [...filtered].sort((a, b) => {
          const scoreA = calculateActivityScore(a)
          const scoreB = calculateActivityScore(b)
          return scoreB - scoreA
        })
        break
      case 'tree':
        // Show only root topics (no parent)
        filtered = filtered.filter(t => !t.parent_topic_id)
        break
      case 'linked':
        // Show topics related to active topic
        if (activeTopicId) {
          const related = getRelatedTopics(activeTopicId)
          filtered = related
        }
        break
      case 'tags':
        // Show topics with tags
        filtered = filtered.filter(t => t.tags.length > 0)
        break
      case 'goals':
        // Show topics linked to goals
        filtered = filtered.filter(t => t.linked_goals.length > 0)
        break
      case 'graph':
        // Show all topics (graph view handles visualization)
        break
    }
    
    return filtered
  }, [topics, debouncedTopicSearchQuery, selectedTags, selectedGoalId, viewMode, activeTopicId, getRelatedTopics, calculateActivityScore])
  
  // Search and filter messages (memoized)
  const filteredMessages = useMemo(() => {
    return messages.filter(msg => {
      // Role filter
      if (filterRole !== 'all' && msg.role !== filterRole) {
        return false
      }
      
      // Search query
      if (debouncedSearchQuery.trim()) {
        const query = debouncedSearchQuery.toLowerCase()
        return (
          msg.content.toLowerCase().includes(query) ||
          msg.delegatedTo?.toLowerCase().includes(query) ||
          msg.systemActions?.some(a => a.action.toLowerCase().includes(query)) ||
          false
        )
      }
      
      return true
    })
  }, [messages, filterRole, debouncedSearchQuery])
  
  
  return (
    <div className="h-full flex bg-gray-900 text-gray-100">
      {/* Topic Sidebar */}
      <TopicSidebar
        onExport={exportConversation}
        onImport={importConversation}
      />
      
      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="h-12 px-4 border-b border-gray-700 bg-gray-800 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Brain className="w-5 h-5 text-blue-400" />
            <div>
              <div className="text-sm font-medium text-white">Manager AI (Aether)</div>
              <div className="text-xs text-gray-400">Coordinating AIM-OS systems</div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowSearch(!showSearch)}
              className="p-1.5 hover:bg-gray-700 rounded text-gray-400 hover:text-gray-200 transition-colors"
              title="Search (Ctrl+K)"
              aria-label="Toggle search"
            >
              <Search className="w-4 h-4" />
            </button>
            <button
              onClick={exportConversation}
              className="p-1.5 hover:bg-gray-700 rounded text-gray-400 hover:text-gray-200 transition-colors"
              title="Export Conversation (Ctrl+E)"
              disabled={messages.length === 0}
              aria-label="Export conversation"
            >
              <Download className="w-4 h-4" />
            </button>
            <div className="flex items-center gap-1 px-2 py-1 bg-green-900/30 border border-green-700 rounded text-xs">
              <CheckCircle className="w-3 h-3 text-green-400" />
              <span className="text-green-300">Active</span>
            </div>
          </div>
        </div>
        
        {/* Search Bar */}
        {showSearch && (
          <div className="px-4 py-2 border-b border-gray-700 bg-gray-800 flex items-center gap-2">
            <Search className="w-4 h-4 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search messages..."
              className="flex-1 bg-gray-900 border border-gray-600 rounded px-3 py-1.5 text-sm text-gray-100 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <select
              value={filterRole}
              onChange={(e) => setFilterRole(e.target.value as any)}
              className="bg-gray-900 border border-gray-600 rounded px-2 py-1.5 text-sm text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Roles</option>
              <option value="user">User</option>
              <option value="manager">Manager AI</option>
              <option value="system">System</option>
            </select>
            <button
              onClick={() => {
                setSearchQuery('')
                setFilterRole('all')
                setShowSearch(false)
              }}
              className="p-1.5 hover:bg-gray-700 rounded text-gray-400 hover:text-gray-200 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        )}
        
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {filteredMessages.length === 0 ? (
            <div className="h-full flex items-center justify-center">
              <div className="text-center text-gray-500">
                <Brain className="w-16 h-16 mx-auto mb-4 opacity-50" />
                <p className="text-lg mb-2">
                  {debouncedSearchQuery || filterRole !== 'all' ? 'No messages match your filters' : 'Start a conversation with Manager AI'}
                </p>
                <p className="text-sm">
                  {debouncedSearchQuery || filterRole !== 'all' ? 'Try adjusting your search or filters' : 'I coordinate all AIM-OS systems and specialized AIs'}
                </p>
              </div>
            </div>
          ) : (
            filteredMessages.map((message) => (
              <MessageBubble
                key={message.id}
                message={message}
                onCreateCanvas={() => handleCreateCanvas(message.id)}
                onViewCanvas={(canvasId) => handleViewCanvas(canvasId)}
                onAddToCanvas={(canvasId) => handleAddToCanvas(message.id, canvasId)}
                onRetry={(messageId) => {
                  const retryError = retryableErrors.get(messageId)
                  if (retryError) {
                    setInput(retryError.originalInput)
                    setTimeout(() => {
                      retryError.retryFn()
                      setRetryableErrors(prev => {
                        const newMap = new Map(prev)
                        newMap.delete(messageId)
                        return newMap
                      })
                    }, 100)
                  }
                }}
              />
            ))
          )}
          {isProcessing && (
            <div className="flex items-center gap-2 text-gray-400">
              <Bot className="w-5 h-5 animate-pulse" />
              <span>Manager AI is thinking...</span>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        
        {/* Input */}
        <div className="h-16 px-4 border-t border-gray-700 bg-gray-800 flex items-center gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
              onKeyDown={(e) => {
                // Shift+Enter for new line
                if (e.key === 'Enter' && e.shiftKey) {
                  return // Allow default behavior (new line)
                }
              }}
              placeholder="Ask Manager AI anything... (Enter to send, Shift+Enter for new line)"
              className="flex-1 bg-gray-900 border border-gray-600 rounded-lg px-4 py-2 text-gray-100 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isProcessing}
              aria-label="Message input"
            />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isProcessing}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:text-gray-500 text-white rounded-lg flex items-center gap-2 transition-colors"
          >
            <Send className="w-4 h-4" />
            <span>Send</span>
          </button>
        </div>
      </div>
      
      {/* System Status Sidebar */}
      <SystemStatusSidebar isOpen={true} />
      
      {/* Toast Notification */}
      {toast && (
        <div className={`fixed bottom-4 right-4 z-50 px-4 py-3 rounded-lg shadow-lg flex items-center gap-3 min-w-[300px] max-w-[500px] animate-in slide-in-from-bottom-5 ${
          toast.type === 'success' ? 'bg-green-900 border border-green-700 text-green-100' :
          toast.type === 'error' ? 'bg-red-900 border border-red-700 text-red-100' :
          'bg-blue-900 border border-blue-700 text-blue-100'
        }`}>
          <div className="flex-1">
            <div className="font-medium text-sm">{toast.message}</div>
          </div>
          <button
            onClick={() => setToast(null)}
            className="text-gray-400 hover:text-gray-200 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}
    </div>
  )
}

interface MessageBubbleProps {
  message: ManagerAIMessage
  onCreateCanvas: () => void
  onViewCanvas: (canvasId: string) => void
  onAddToCanvas: (canvasId: string) => void
  onRetry?: (messageId: string) => void
}

const MessageBubble: React.FC<MessageBubbleProps> = React.memo(({ message, onCreateCanvas, onViewCanvas, onAddToCanvas, onRetry }) => {
  const isUser = message.role === 'user'
  const isManager = message.role === 'manager'
  const isSystem = message.role === 'system'
  const isError = isSystem && message.content.includes('❌ Error:')
  const [showMetadata, setShowMetadata] = useState(false)
  const [showEvidence, setShowEvidence] = useState(false)
  
  return (
    <div className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0">
          <Bot className="w-5 h-5 text-white" />
        </div>
      )}
      <div className={`flex-1 max-w-3xl ${isUser ? 'order-2' : ''}`}>
        <div className={`rounded-lg p-4 ${
          isUser 
            ? 'bg-blue-600 text-white' 
            : isManager 
            ? 'bg-gray-800 border border-gray-700' 
            : isError
            ? 'bg-red-900/30 border border-red-700'
            : 'bg-gray-800/50'
        }`}>
          <div className="prose prose-invert prose-sm max-w-none">
            <p className="whitespace-pre-wrap">{message.content}</p>
          </div>
          
          {/* Retry Button for Errors */}
          {isError && onRetry && (
            <div className="mt-3 pt-3 border-t border-red-700">
              <button
                onClick={() => onRetry(message.id)}
                className="px-3 py-1.5 text-xs bg-red-600 hover:bg-red-700 text-white rounded flex items-center gap-2 transition-colors"
              >
                <AlertCircle className="w-3 h-3" />
                <span>Retry</span>
              </button>
            </div>
          )}
          
          {/* Delegation Status */}
          {message.delegationStatus && (
            <div className="mt-3 pt-3 border-t border-gray-700">
              <div className="flex items-center gap-2 mb-2">
                <Network className="w-4 h-4 text-blue-400" />
                <span className="text-xs font-medium text-gray-300">Delegated to {message.delegationStatus.to_ai}</span>
              </div>
              <div className="flex items-center gap-2 text-xs">
                <div className={`px-2 py-1 rounded ${
                  message.delegationStatus.status === 'completed' ? 'bg-green-900/30 text-green-300' :
                  message.delegationStatus.status === 'failed' ? 'bg-red-900/30 text-red-300' :
                  message.delegationStatus.status === 'in_progress' ? 'bg-yellow-900/30 text-yellow-300' :
                  'bg-gray-700/30 text-gray-300'
                }`}>
                  {message.delegationStatus.status === 'completed' && '✅ Completed'}
                  {message.delegationStatus.status === 'failed' && '❌ Failed'}
                  {message.delegationStatus.status === 'in_progress' && '⏳ In Progress'}
                  {message.delegationStatus.status === 'pending' && '⏳ Pending'}
                </div>
                {message.delegationStatus.progress !== undefined && (
                  <div className="flex-1 h-1.5 bg-gray-700 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${
                        message.delegationStatus.status === 'completed' ? 'bg-green-500' :
                        message.delegationStatus.status === 'failed' ? 'bg-red-500' :
                        'bg-yellow-500'
                      } transition-all duration-300`}
                      style={{ width: `${message.delegationStatus.progress}%` }}
                    />
                  </div>
                )}
              </div>
              {message.delegationStatus.error && (
                <div className="mt-2 text-xs text-red-400">{message.delegationStatus.error}</div>
              )}
            </div>
          )}
          
          {/* Plan Status */}
          {message.planStatus && (
            <div className="mt-3 pt-3 border-t border-gray-700">
              <div className="flex items-center gap-2 mb-2">
                <Target className="w-4 h-4 text-purple-400" />
                <span className="text-xs font-medium text-gray-300">Plan: {message.planId}</span>
              </div>
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-xs">
                  <div className={`px-2 py-1 rounded ${
                    message.planStatus.status === 'completed' ? 'bg-green-900/30 text-green-300' :
                    message.planStatus.status === 'failed' ? 'bg-red-900/30 text-red-300' :
                    message.planStatus.status === 'running' ? 'bg-blue-900/30 text-blue-300' :
                    'bg-gray-700/30 text-gray-300'
                  }`}>
                    {message.planStatus.status === 'completed' && '✅ Completed'}
                    {message.planStatus.status === 'failed' && '❌ Failed'}
                    {message.planStatus.status === 'running' && '⏳ Running'}
                    {message.planStatus.status === 'pending' && '⏳ Pending'}
                  </div>
                  <span className="text-gray-400">
                    {message.planStatus.completed_steps}/{message.planStatus.total_steps} steps
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="flex-1 h-1.5 bg-gray-700 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${
                        message.planStatus.status === 'completed' ? 'bg-green-500' :
                        message.planStatus.status === 'failed' ? 'bg-red-500' :
                        'bg-blue-500'
                      } transition-all duration-300`}
                      style={{ width: `${message.planStatus.progress}%` }}
                    />
                  </div>
                  <span className="text-xs text-gray-400">{Math.round(message.planStatus.progress)}%</span>
                </div>
                {message.planStatus.current_step && (
                  <div className="text-xs text-gray-400">Current: {message.planStatus.current_step}</div>
                )}
              </div>
            </div>
          )}
          
          {/* AIM-OS Metadata */}
          {isManager && (
            <div className="mt-3 pt-3 border-t border-gray-700 space-y-2">
              {/* Confidence Badge */}
              {message.confidence !== undefined && (
                <div className="flex items-center gap-2 text-xs">
                  <Shield className="w-3 h-3 text-blue-400" />
                  <span className="text-gray-400">Confidence: </span>
                  <span className={`font-medium px-2 py-0.5 rounded ${
                    message.confidence >= 0.9 ? 'bg-green-900/30 text-green-300' :
                    message.confidence >= 0.7 ? 'bg-yellow-900/30 text-yellow-300' :
                    'bg-red-900/30 text-red-300'
                  }`}>
                    {Math.round(message.confidence * 100)}%
                  </span>
                </div>
              )}
              
              {/* System Actions */}
              {message.systemActions && message.systemActions.length > 0 && (
                <div className="space-y-1">
                  <button
                    onClick={() => setShowMetadata(!showMetadata)}
                    className="flex items-center gap-2 text-xs text-gray-400 hover:text-gray-300 transition-colors"
                  >
                    <Zap className="w-3 h-3" />
                    <span>Systems used ({message.systemActions.length})</span>
                    {showMetadata ? <span>▼</span> : <span>▶</span>}
                  </button>
                  {showMetadata && (
                    <div className="ml-5 space-y-1 pl-3 border-l border-gray-700">
                      {message.systemActions.map((action, index) => (
                        <div key={index} className="text-xs text-gray-400">
                          <span className="font-medium text-gray-300">{action.system}:</span> {action.action}
                          {action.timestamp && (
                            <span className="ml-2 text-gray-500">
                              {new Date(action.timestamp).toLocaleTimeString()}
                            </span>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
              
              {/* Evidence Trail */}
              {message.evidence && message.evidence.length > 0 && (
                <div className="space-y-1">
                  <button
                    onClick={() => setShowEvidence(!showEvidence)}
                    className="flex items-center gap-2 text-xs text-gray-400 hover:text-gray-300 transition-colors"
                  >
                    <Database className="w-3 h-3" />
                    <span>Evidence ({message.evidence.length})</span>
                    {showEvidence ? <span>▼</span> : <span>▶</span>}
                  </button>
                  {showEvidence && (
                    <div className="ml-5 space-y-1 pl-3 border-l border-gray-700">
                      {message.evidence.map((evidence, index) => (
                        <div key={index} className="text-xs">
                          <div className="flex items-center gap-2 text-gray-300">
                            <span className="font-medium">{evidence.type.replace('_', ' ')}</span>
                            <span className="text-gray-500">•</span>
                            <span className="text-gray-400">Relevance: {Math.round(evidence.relevance * 100)}%</span>
                          </div>
                          {evidence.summary && (
                            <div className="text-gray-500 mt-0.5 ml-2">{evidence.summary}</div>
                          )}
                          <button
                            onClick={() => {/* View evidence source */}}
                            className="text-blue-400 hover:text-blue-300 text-xs mt-1 ml-2"
                          >
                            View source →
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
              
              {/* Work References */}
              {message.workReferences && (
                <div className="text-xs text-gray-400">
                  {message.workReferences.cmc_atoms && message.workReferences.cmc_atoms.length > 0 && (
                    <div className="flex items-center gap-2">
                      <Database className="w-3 h-3" />
                      <span>{message.workReferences.cmc_atoms.length} CMC atoms</span>
                    </div>
                  )}
                  {message.workReferences.files && message.workReferences.files.length > 0 && (
                    <div className="flex items-center gap-2 mt-1">
                      <FileText className="w-3 h-3" />
                      <span>{message.workReferences.files.length} files</span>
                    </div>
                  )}
                  {message.workReferences.goals && message.workReferences.goals.length > 0 && (
                    <div className="flex items-center gap-2 mt-1">
                      <Target className="w-3 h-3" />
                      <span>{message.workReferences.goals.length} goals</span>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
          
          {/* Canvas Actions */}
          {isManager && message.canvasActions && (
            <div className="mt-3 pt-3 border-t border-gray-700 flex items-center gap-2 flex-wrap">
              {message.canvasActions.createCanvas && (
                <button
                  onClick={onCreateCanvas}
                  className="px-2 py-1 text-xs bg-blue-600 hover:bg-blue-700 text-white rounded flex items-center gap-1.5 transition-colors"
                >
                  <Plus className="w-3 h-3" />
                  <span>Create Canvas</span>
                </button>
              )}
              {message.canvasActions.canvasReference && (
                <button
                  onClick={() => onViewCanvas(message.canvasActions.canvasReference!)}
                  className="px-2 py-1 text-xs bg-gray-700 hover:bg-gray-600 text-gray-300 rounded flex items-center gap-1.5 transition-colors"
                >
                  <ExternalLink className="w-3 h-3" />
                  <span>View Canvas</span>
                </button>
              )}
              {message.canvasActions.addToCanvas && (
                <button
                  onClick={() => onAddToCanvas(message.canvasActions.addToCanvas!)}
                  className="px-2 py-1 text-xs bg-gray-700 hover:bg-gray-600 text-gray-300 rounded flex items-center gap-1.5 transition-colors"
                >
                  <FileText className="w-3 h-3" />
                  <span>Add to Canvas</span>
                </button>
              )}
            </div>
          )}
        </div>
        <div className={`text-xs text-gray-500 mt-1 flex items-center gap-2 ${isUser ? 'justify-end' : 'justify-start'}`}>
          <span>{new Date(message.timestamp).toLocaleTimeString()}</span>
          {isManager && message.confidence !== undefined && (
            <>
              <span>•</span>
              <span className={`${
                message.confidence >= 0.9 ? 'text-green-400' :
                message.confidence >= 0.7 ? 'text-yellow-400' :
                'text-red-400'
              }`}>
                {Math.round(message.confidence * 100)}% confidence
              </span>
            </>
          )}
        </div>
      </div>
      {isUser && (
        <div className="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center flex-shrink-0 order-1">
          <User className="w-5 h-5 text-gray-300" />
        </div>
      )}
    </div>
  )
})

MessageBubble.displayName = 'MessageBubble'

