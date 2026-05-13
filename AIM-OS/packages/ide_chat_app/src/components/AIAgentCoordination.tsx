/**
 * AI Agent Coordination System
 * Multi-agent collaboration and coordination interface
 */

import React, { useState, useEffect, useRef } from 'react'
import { 
  Users, 
  MessageSquare, 
  Send, 
  Bot, 
  Sparkles, 
  Code, 
  Target, 
  Brain,
  Zap,
  Activity,
  Clock,
  CheckCircle,
  AlertTriangle,
  Play,
  Pause,
  Square,
  RefreshCw,
  Settings,
  Plus,
  Trash2,
  Edit3
} from 'lucide-react'
import { enhancedAIService, AIAgent, AIResponse, AIRequest } from '../lib/ai-service-enhanced'
import { mcpIntegration } from '../lib/mcp-integration'
import { performanceMonitor } from '../lib/performance-monitor'

interface AgentMessage {
  id: string
  agentId: string
  content: string
  timestamp: Date
  type: 'message' | 'action' | 'coordination' | 'result'
  metadata?: Record<string, any>
}

interface AgentTask {
  id: string
  agentId: string
  description: string
  status: 'pending' | 'in_progress' | 'completed' | 'failed'
  priority: 'low' | 'medium' | 'high' | 'critical'
  createdAt: Date
  completedAt?: Date
  result?: any
}

interface AgentCoordination {
  id: string
  agents: string[]
  task: string
  status: 'planning' | 'executing' | 'completed' | 'failed'
  messages: AgentMessage[]
  tasks: AgentTask[]
  createdAt: Date
  completedAt?: Date
}

interface AIAgentCoordinationProps {
  className?: string
}

export const AIAgentCoordination: React.FC<AIAgentCoordinationProps> = ({ className = '' }) => {
  const [agents, setAgents] = useState<AIAgent[]>([])
  const [activeCoordination, setActiveCoordination] = useState<AgentCoordination | null>(null)
  const [coordinationHistory, setCoordinationHistory] = useState<AgentCoordination[]>([])
  const [isRunning, setIsRunning] = useState(false)
  const [newTask, setNewTask] = useState('')
  const [selectedAgents, setSelectedAgents] = useState<string[]>([])
  const [messages, setMessages] = useState<AgentMessage[]>([])
  const [isProcessing, setIsProcessing] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Initialize agents
  useEffect(() => {
    const loadAgents = () => {
      const availableAgents = enhancedAIService.getActiveAgents()
      setAgents(availableAgents)
      
      // Auto-select first two agents for coordination
      if (availableAgents.length >= 2) {
        setSelectedAgents([availableAgents[0].id, availableAgents[1].id])
      }
    }

    loadAgents()
  }, [])

  // Auto-scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Start new coordination session
  const startCoordination = async () => {
    if (!newTask.trim() || selectedAgents.length < 2) return

    setIsProcessing(true)
    
    try {
      const coordination: AgentCoordination = {
        id: `coord-${Date.now()}`,
        agents: selectedAgents,
        task: newTask,
        status: 'planning',
        messages: [],
        tasks: [],
        createdAt: new Date()
      }

      setActiveCoordination(coordination)
      setMessages([])
      setNewTask('')
      setIsRunning(true)

      // Add initial planning message
      addMessage({
        agentId: 'system',
        content: `Starting coordination between ${selectedAgents.length} agents for task: "${newTask}"`,
        type: 'coordination',
        timestamp: new Date()
      })

      // Begin coordination process
      await processCoordination(coordination)

    } catch (error) {
      console.error('Failed to start coordination:', error)
      addMessage({
        agentId: 'system',
        content: `Failed to start coordination: ${(error as Error).message}`,
        type: 'coordination',
        timestamp: new Date()
      })
    } finally {
      setIsProcessing(false)
    }
  }

  // Process coordination between agents
  const processCoordination = async (coordination: AgentCoordination) => {
    try {
      // Phase 1: Planning
      addMessage({
        agentId: 'system',
        content: 'Phase 1: Planning - Agents are discussing the task and creating a plan...',
        type: 'coordination',
        timestamp: new Date()
      })

      const planningMessages = await simulateAgentPlanning(coordination)
      setMessages(prev => [...prev, ...planningMessages])

      // Phase 2: Task Distribution
      addMessage({
        agentId: 'system',
        content: 'Phase 2: Task Distribution - Breaking down the task into subtasks...',
        type: 'coordination',
        timestamp: new Date()
      })

      const tasks = await createSubtasks(coordination)
      setActiveCoordination(prev => prev ? { ...prev, tasks } : null)

      // Phase 3: Execution
      addMessage({
        agentId: 'system',
        content: 'Phase 3: Execution - Agents are working on their assigned tasks...',
        type: 'coordination',
        timestamp: new Date()
      })

      await executeTasks(coordination, tasks)

      // Phase 4: Integration
      addMessage({
        agentId: 'system',
        content: 'Phase 4: Integration - Combining results and finalizing...',
        type: 'coordination',
        timestamp: new Date()
      })

      await integrateResults(coordination)

      // Complete coordination
      setActiveCoordination(prev => prev ? { ...prev, status: 'completed', completedAt: new Date() } : null)
      setCoordinationHistory(prev => [coordination, ...prev])
      setIsRunning(false)

      addMessage({
        agentId: 'system',
        content: 'Coordination completed successfully!',
        type: 'coordination',
        timestamp: new Date()
      })

    } catch (error) {
      console.error('Coordination failed:', error)
      setActiveCoordination(prev => prev ? { ...prev, status: 'failed' } : null)
      setIsRunning(false)
      
      addMessage({
        agentId: 'system',
        content: `Coordination failed: ${(error as Error).message}`,
        type: 'coordination',
        timestamp: new Date()
      })
    }
  }

  // Simulate agent planning phase
  const simulateAgentPlanning = async (coordination: AgentCoordination): Promise<AgentMessage[]> => {
    const planningMessages: AgentMessage[] = []
    
    for (const agentId of coordination.agents) {
      const agent = agents.find(a => a.id === agentId)
      if (!agent) continue

      // Simulate agent thinking
      await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000))

      const planningResponse = await enhancedAIService.generateAgentResponse(agentId, {
        prompt: `Plan how to approach this task: "${coordination.task}". Consider your capabilities: ${agent.capabilities.join(', ')}.`,
        provider: agentId as any
      })

      planningMessages.push({
        id: `msg-${Date.now()}-${Math.random()}`,
        agentId,
        content: planningResponse.content,
        timestamp: new Date(),
        type: 'message',
        metadata: { phase: 'planning', confidence: planningResponse.metadata.confidence }
      })
    }

    return planningMessages
  }

  // Create subtasks for agents
  const createSubtasks = async (coordination: AgentCoordination): Promise<AgentTask[]> => {
    const tasks: AgentTask[] = []
    
    for (let i = 0; i < coordination.agents.length; i++) {
      const agentId = coordination.agents[i]
      const agent = agents.find(a => a.id === agentId)
      
      tasks.push({
        id: `task-${Date.now()}-${i}`,
        agentId,
        description: `Subtask ${i + 1}: ${agent?.name} will work on a specific aspect of "${coordination.task}"`,
        status: 'pending',
        priority: i === 0 ? 'high' : 'medium',
        createdAt: new Date()
      })
    }

    return tasks
  }

  // Execute tasks
  const executeTasks = async (coordination: AgentCoordination, tasks: AgentTask[]) => {
    for (const task of tasks) {
        // Update task status
        setActiveCoordination(prev => {
          if (!prev) return null
          const updatedTasks = prev.tasks.map(t => 
            t.id === task.id ? { ...t, status: 'in_progress' as const } : t
          )
          return { ...prev, tasks: updatedTasks }
        })

      addMessage({
        agentId: task.agentId,
        content: `Starting task: ${task.description}`,
        type: 'action',
        timestamp: new Date()
      })

      // Simulate task execution
      await new Promise(resolve => setTimeout(resolve, 2000 + Math.random() * 3000))

      // Generate result
      const agent = agents.find(a => a.id === task.agentId)
      if (agent) {
        const result = await enhancedAIService.generateAgentResponse(task.agentId, {
          prompt: `Complete this task: ${task.description}. Provide a detailed result.`,
          provider: task.agentId as any
        })

        addMessage({
          agentId: task.agentId,
          content: `Task completed: ${result.content}`,
          type: 'result',
          timestamp: new Date(),
          metadata: { taskId: task.id, confidence: result.metadata.confidence }
        })

        // Update task status
        setActiveCoordination(prev => {
          if (!prev) return null
          const updatedTasks = prev.tasks.map(t => 
            t.id === task.id ? { 
              ...t, 
              status: 'completed' as const, 
              completedAt: new Date(),
              result: result.content
            } : t
          )
          return { ...prev, tasks: updatedTasks }
        })
      }
    }
  }

  // Integrate results
  const integrateResults = async (coordination: AgentCoordination) => {
    addMessage({
      agentId: 'system',
      content: 'Integrating results from all agents...',
      type: 'coordination',
      timestamp: new Date()
    })

    // Simulate integration
    await new Promise(resolve => setTimeout(resolve, 1500))

    addMessage({
      agentId: 'system',
      content: 'Results integrated successfully. All agents have contributed to the final solution.',
      type: 'coordination',
      timestamp: new Date()
    })
  }

  // Add message to coordination
  const addMessage = (message: Omit<AgentMessage, 'id'>) => {
    const newMessage: AgentMessage = {
      id: `msg-${Date.now()}-${Math.random()}`,
      ...message
    }
    setMessages(prev => [...prev, newMessage])
  }

  // Stop coordination
  const stopCoordination = () => {
    setIsRunning(false)
    setActiveCoordination(prev => prev ? { ...prev, status: 'failed' } : null)
    
    addMessage({
      agentId: 'system',
      content: 'Coordination stopped by user.',
      type: 'coordination',
      timestamp: new Date()
    })
  }

  // Get agent info
  const getAgentInfo = (agentId: string) => {
    return agents.find(a => a.id === agentId)
  }

  // Get agent icon
  const getAgentIcon = (agentId: string) => {
    switch (agentId) {
      case 'coding': return <Code className="w-4 h-4 text-blue-400" />
      case 'planning': return <Sparkles className="w-4 h-4 text-purple-400" />
      default: return <Bot className="w-4 h-4 text-gray-400" />
    }
  }

  // Get status color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-400'
      case 'in_progress': return 'text-blue-400'
      case 'failed': return 'text-red-400'
      default: return 'text-gray-400'
    }
  }

  return (
    <div className={`h-full bg-gray-800 flex flex-col ${className}`}>
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Users className="w-5 h-5 text-blue-400" />
            <div>
              <div className="text-white text-sm font-semibold">AI Agent Coordination</div>
              <div className="text-xs text-gray-500">
                {activeCoordination ? `${activeCoordination.agents.length} agents active` : 'No active coordination'}
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            {isRunning ? (
              <button
                onClick={stopCoordination}
                className="flex items-center gap-1 px-3 py-1 bg-red-600 hover:bg-red-700 text-white text-xs rounded"
              >
                <Square className="w-3 h-3" />
                Stop
              </button>
            ) : (
              <button
                onClick={startCoordination}
                disabled={!newTask.trim() || selectedAgents.length < 2 || isProcessing}
                className="flex items-center gap-1 px-3 py-1 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white text-xs rounded"
              >
                <Play className="w-3 h-3" />
                Start
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Task Input */}
      <div className="px-4 py-3 border-b border-gray-700">
        <div className="space-y-3">
          <div>
            <label className="text-xs text-gray-400 mb-1 block">Task Description</label>
            <textarea
              value={newTask}
              onChange={(e) => setNewTask(e.target.value)}
              placeholder="Describe the task for AI agents to collaborate on..."
              className="w-full bg-gray-700 text-white text-sm rounded p-2 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
              rows={2}
              disabled={isRunning}
            />
          </div>
          
          <div>
            <label className="text-xs text-gray-400 mb-1 block">Select Agents</label>
            <div className="flex gap-2 flex-wrap">
              {agents.map(agent => (
                <button
                  key={agent.id}
                  onClick={() => {
                    if (selectedAgents.includes(agent.id)) {
                      setSelectedAgents(prev => prev.filter(id => id !== agent.id))
                    } else {
                      setSelectedAgents(prev => [...prev, agent.id])
                    }
                  }}
                  disabled={isRunning}
                  className={`flex items-center gap-1 px-2 py-1 text-xs rounded ${
                    selectedAgents.includes(agent.id)
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  } disabled:opacity-50`}
                >
                  {getAgentIcon(agent.id)}
                  {agent.name}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Active Tasks */}
      {activeCoordination && activeCoordination.tasks.length > 0 && (
        <div className="px-4 py-3 border-b border-gray-700">
          <div className="text-xs text-gray-400 mb-2">Active Tasks</div>
          <div className="space-y-2">
            {activeCoordination.tasks.map(task => {
              const agent = getAgentInfo(task.agentId)
              return (
                <div key={task.id} className="flex items-center justify-between bg-gray-700 rounded p-2">
                  <div className="flex items-center gap-2">
                    {getAgentIcon(task.agentId)}
                    <div>
                      <div className="text-xs text-white">{agent?.name}</div>
                      <div className="text-xs text-gray-400">{task.description}</div>
                    </div>
                  </div>
                  <div className={`text-xs ${getStatusColor(task.status)}`}>
                    {task.status.toUpperCase()}
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="space-y-3">
          {messages.map(message => {
            const agent = getAgentInfo(message.agentId)
            return (
              <div key={message.id} className="flex gap-2">
                <div className="flex-shrink-0">
                  {message.agentId === 'system' ? (
                    <Settings className="w-4 h-4 text-gray-400 mt-1" />
                  ) : (
                    getAgentIcon(message.agentId)
                  )}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-medium text-white">
                      {message.agentId === 'system' ? 'System' : agent?.name || 'Unknown Agent'}
                    </span>
                    <span className="text-xs text-gray-400">
                      {message.timestamp.toLocaleTimeString()}
                    </span>
                    <span className={`text-xs px-1 rounded ${
                      message.type === 'coordination' ? 'bg-blue-900 text-blue-300' :
                      message.type === 'action' ? 'bg-yellow-900 text-yellow-300' :
                      message.type === 'result' ? 'bg-green-900 text-green-300' :
                      'bg-gray-900 text-gray-300'
                    }`}>
                      {message.type}
                    </span>
                  </div>
                  <div className="text-sm text-gray-300">{message.content}</div>
                  {message.metadata?.confidence && (
                    <div className="text-xs text-gray-500 mt-1">
                      Confidence: {(message.metadata.confidence * 100).toFixed(0)}%
                    </div>
                  )}
                </div>
              </div>
            )
          })}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Status */}
      {isRunning && (
        <div className="px-4 py-2 border-t border-gray-700 bg-blue-900/20">
          <div className="flex items-center gap-2 text-sm text-blue-300">
            <Activity className="w-4 h-4 animate-pulse" />
            <span>Agents are collaborating...</span>
          </div>
        </div>
      )}
    </div>
  )
}
