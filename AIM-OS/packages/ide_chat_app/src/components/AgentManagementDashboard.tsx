/**
 * Agent Management Dashboard Component - ENHANCED
 * PRIMARY TAB - Core mission: Automating Cursor operations and managing Cursor AI agents
 * 
 * Features:
 * - Agent cards with status, model, current task, controls
 * - Cursor model management (change models dynamically)
 * - Continue prompt automation (auto-prompt agents to continue)
 * - **ENHANCED: Detailed task breakdown with subtasks, progress tracking, dependencies**
 * - **ENHANCED: Timeline view, board view, list view**
 * - **ENHANCED: Agent assignment visualization and workload balancing**
 * - Agent communication (send messages, broadcast, coordinate)
 * 
 * Created: 2025-10-31
 * Enhanced: 2025-11-07 (Rev - Competition Phase)
 * Agent: Lexicon (original), Rev (enhancements)
 * Based on: Aether's UI Design Vision Enhancement
 */

import React, { useState, useEffect, useMemo } from 'react'
import {
  Users,
  Bot,
  Zap,
  Play,
  Pause,
  Square,
  RefreshCw,
  MessageSquare,
  Send,
  Settings,
  CheckCircle,
  XCircle,
  AlertCircle,
  Activity,
  Clock,
  Target,
  Brain,
  Code,
  Sparkles,
  Network,
  Plus,
  Edit,
  Trash2,
  Copy,
  Bell,
  BellOff,
  ChevronDown,
  ChevronRight,
  List,
  Calendar,
  LayoutGrid,
  TrendingUp,
  Link2,
  BarChart3,
  Filter,
  Search,
  MoreVertical,
  CheckCircle2,
  Circle,
  ArrowRight,
  GitBranch
} from 'lucide-react'
import { AgentQuestionPanel } from './AgentManagementDashboard/AgentQuestionPanel'
import { AgentManagementTimeline } from './AgentManagementDashboard/AgentManagementTimeline'
import { useAgents } from '../hooks/useAgents'

interface Agent {
  id: string
  name: string
  role: string
  status: 'active' | 'idle' | 'busy' | 'error' | 'offline'
  model: string
  currentTask?: string
  progress?: number
  lastActivity: string
  messages: number
  tasksCompleted: number
  autoContinue: boolean
  confidence?: number
}

interface Subtask {
  id: string
  title: string
  status: 'pending' | 'in_progress' | 'completed' | 'failed'
  assignedTo?: string
  progress: number
  estimatedTime?: number // minutes
  actualTime?: number // minutes
  dependencies?: string[] // IDs of subtasks this depends on
}

interface Task {
  id: string
  title: string
  description: string
  assignedTo?: string
  status: 'pending' | 'in_progress' | 'completed' | 'failed' | 'blocked'
  priority: 'low' | 'medium' | 'high' | 'critical'
  createdAt: string
  deadline?: string
  progress: number // 0-100
  subtasks: Subtask[]
  dependencies?: string[] // IDs of other tasks this depends on
  estimatedTime?: number // hours
  actualTime?: number // hours
  tags?: string[]
  notes?: string[]
}

type TaskView = 'list' | 'timeline' | 'board' | 'breakdown' | 'agent-timeline'

export const AgentManagementDashboard: React.FC = () => {
  const { agents, loading, lastUpdate, fetchConfidenceHistory, trackConfidence, updateAgent } = useAgents()

  const [tasks, setTasks] = useState<Task[]>([
    {
      id: 'task-1',
      title: 'Enhance Agent Management Dashboard',
      description: 'Add detailed task breakdown, progress tracking, dependencies, and timeline view',
      assignedTo: 'rev',
      status: 'in_progress',
      priority: 'high',
      createdAt: '2025-11-07T10:00:00Z',
      progress: 75,
      subtasks: [
        {
          id: 'subtask-1-1',
          title: 'Add subtask support to Task interface',
          status: 'completed',
          assignedTo: 'rev',
          progress: 100,
          estimatedTime: 15,
          actualTime: 12
        },
        {
          id: 'subtask-1-2',
          title: 'Implement progress tracking per task',
          status: 'completed',
          assignedTo: 'rev',
          progress: 100,
          estimatedTime: 20,
          actualTime: 18
        },
        {
          id: 'subtask-1-3',
          title: 'Add task dependencies visualization',
          status: 'in_progress',
          assignedTo: 'rev',
          progress: 60,
          estimatedTime: 30,
          dependencies: ['subtask-1-1', 'subtask-1-2']
        },
        {
          id: 'subtask-1-4',
          title: 'Create timeline view for tasks',
          status: 'pending',
          assignedTo: 'rev',
          progress: 0,
          estimatedTime: 45,
          dependencies: ['subtask-1-3']
        },
        {
          id: 'subtask-1-5',
          title: 'Add board view (Kanban-style)',
          status: 'pending',
          assignedTo: 'rev',
          progress: 0,
          estimatedTime: 40,
          dependencies: ['subtask-1-3']
        }
      ],
      estimatedTime: 10,
      actualTime: 7.5,
      tags: ['ui', 'dashboard', 'enhancement'],
      notes: ['This is a critical enhancement for the competition']
    },
    {
      id: 'task-2',
      title: 'Complete Properties Panel',
      description: 'Add full editing, validation, and relationships support',
      assignedTo: 'rev',
      status: 'pending',
      priority: 'medium',
      createdAt: '2025-11-07T10:15:00Z',
      progress: 0,
      subtasks: [
        {
          id: 'subtask-2-1',
          title: 'Implement property validation (VIF)',
          status: 'pending',
          progress: 0,
          estimatedTime: 25
        },
        {
          id: 'subtask-2-2',
          title: 'Add property relationships (SEG)',
          status: 'pending',
          progress: 0,
          estimatedTime: 30
        },
        {
          id: 'subtask-2-3',
          title: 'Create property history view',
          status: 'pending',
          progress: 0,
          estimatedTime: 20
        }
      ],
      estimatedTime: 3,
      tags: ['panel', 'properties'],
      dependencies: ['task-1']
    },
    {
      id: 'task-3',
      title: 'Complete Problems Panel',
      description: 'Add quick fixes, navigation, and AIM-OS integration',
      status: 'pending',
      priority: 'high',
      createdAt: '2025-11-07T10:30:00Z',
      progress: 0,
      subtasks: [
        {
          id: 'subtask-3-1',
          title: 'Implement quick fix suggestions',
          status: 'pending',
          progress: 0,
          estimatedTime: 35
        },
        {
          id: 'subtask-3-2',
          title: 'Add file navigation on click',
          status: 'pending',
          progress: 0,
          estimatedTime: 15
        },
        {
          id: 'subtask-3-3',
          title: 'Integrate SDF-CVF quartet violations',
          status: 'pending',
          progress: 0,
          estimatedTime: 40
        }
      ],
      estimatedTime: 4,
      tags: ['panel', 'debugging']
    },
    {
      id: 'task-4',
      title: 'Complete Output Panel',
      description: 'Add filtering, export, and real-time updates',
      status: 'pending',
      priority: 'medium',
      createdAt: '2025-11-07T10:45:00Z',
      progress: 0,
      subtasks: [
        {
          id: 'subtask-4-1',
          title: 'Add log level filtering',
          status: 'pending',
          progress: 0,
          estimatedTime: 20
        },
        {
          id: 'subtask-4-2',
          title: 'Implement export functionality',
          status: 'pending',
          progress: 0,
          estimatedTime: 25
        },
        {
          id: 'subtask-4-3',
          title: 'Add real-time log streaming',
          status: 'pending',
          progress: 0,
          estimatedTime: 30
        }
      ],
      estimatedTime: 3,
      tags: ['panel', 'output']
    },
    {
      id: 'task-5',
      title: 'Add Context Web Panel',
      description: 'Revolutionary feature with HHNI integration for context visualization',
      status: 'pending',
      priority: 'critical',
      createdAt: '2025-11-07T11:00:00Z',
      progress: 0,
      subtasks: [
        {
          id: 'subtask-5-1',
          title: 'Design context web visualization',
          status: 'pending',
          progress: 0,
          estimatedTime: 60,
          dependencies: []
        },
        {
          id: 'subtask-5-2',
          title: 'Integrate HHNI for context retrieval',
          status: 'pending',
          progress: 0,
          estimatedTime: 45,
          dependencies: ['subtask-5-1']
        },
        {
          id: 'subtask-5-3',
          title: 'Add SEG relationship visualization',
          status: 'pending',
          progress: 0,
          estimatedTime: 50,
          dependencies: ['subtask-5-2']
        }
      ],
      estimatedTime: 8,
      tags: ['revolutionary', 'context', 'hhni'],
      notes: ['This is a unique AIM-OS feature']
    }
  ])

  const [selectedAgent, setSelectedAgent] = useState<string | null>(null)
  const [showModelSelector, setShowModelSelector] = useState<string | null>(null)
  const [showTaskAssigner, setShowTaskAssigner] = useState(false)
  const [messageText, setMessageText] = useState('')
  const [broadcastMessage, setBroadcastMessage] = useState('')
  const [showQuestionPanel, setShowQuestionPanel] = useState<{agentId: string, agentName: string} | null>(null)
  const [taskView, setTaskView] = useState<TaskView>('breakdown')
  const [expandedTasks, setExpandedTasks] = useState<Set<string>>(new Set(['task-1']))
  const [selectedTask, setSelectedTask] = useState<string | null>(null)
  const [taskFilter, setTaskFilter] = useState<'all' | 'pending' | 'in_progress' | 'completed' | 'failed'>('all')
  const [searchQuery, setSearchQuery] = useState('')

  const availableModels = [
    'gpt-4',
    'gpt-4-turbo',
    'gpt-3.5-turbo',
    'claude-sonnet-4',
    'claude-opus-4',
    'claude-haiku-4',
    'gemini-pro',
    'gemini-ultra'
  ]

  // Calculate task progress from subtasks
  const calculateTaskProgress = (task: Task): number => {
    if (task.subtasks.length === 0) return task.progress
    const completedSubtasks = task.subtasks.filter(st => st.status === 'completed').length
    return Math.round((completedSubtasks / task.subtasks.length) * 100)
  }

  // Update task progress when subtasks change
  useEffect(() => {
    setTasks(prevTasks => prevTasks.map(task => ({
      ...task,
      progress: calculateTaskProgress(task)
    })))
  }, [])

  // Filter and search tasks
  const filteredTasks = useMemo(() => {
    return tasks.filter(task => {
      const matchesFilter = taskFilter === 'all' || task.status === taskFilter
      const matchesSearch = searchQuery === '' || 
        task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        task.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        task.tags?.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
      return matchesFilter && matchesSearch
    })
  }, [tasks, taskFilter, searchQuery])

  // Get agent workload (number of assigned tasks)
  const getAgentWorkload = (agentId: string): number => {
    return tasks.filter(t => t.assignedTo === agentId && t.status !== 'completed').length
  }

  // Get agent's assigned tasks
  const getAgentTasks = (agentId: string): Task[] => {
    return tasks.filter(t => t.assignedTo === agentId)
  }

  // Calculate overall project progress
  const overallProgress = useMemo(() => {
    if (tasks.length === 0) return 0
    const totalProgress = tasks.reduce((sum, task) => sum + task.progress, 0)
    return Math.round(totalProgress / tasks.length)
  }, [tasks])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-500'
      case 'idle':
        return 'bg-yellow-500'
      case 'busy':
        return 'bg-blue-500'
      case 'error':
        return 'bg-red-500'
      default:
        return 'bg-gray-500'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="w-4 h-4 text-green-400" />
      case 'idle':
        return <Clock className="w-4 h-4 text-yellow-400" />
      case 'busy':
        return <Activity className="w-4 h-4 text-blue-400" />
      case 'error':
        return <XCircle className="w-4 h-4 text-red-400" />
      default:
        return <AlertCircle className="w-4 h-4 text-gray-400" />
    }
  }

  const getTaskStatusColor = (status: Task['status']) => {
    switch (status) {
      case 'completed':
        return 'bg-green-600 text-white'
      case 'in_progress':
        return 'bg-blue-600 text-white'
      case 'failed':
        return 'bg-red-600 text-white'
      case 'blocked':
        return 'bg-orange-600 text-white'
      default:
        return 'bg-gray-600 text-white'
    }
  }

  const getPriorityColor = (priority: Task['priority']) => {
    switch (priority) {
      case 'critical':
        return 'bg-red-600 text-white'
      case 'high':
        return 'bg-orange-600 text-white'
      case 'medium':
        return 'bg-yellow-600 text-white'
      default:
        return 'bg-gray-600 text-white'
    }
  }

  const toggleTaskExpansion = (taskId: string) => {
    setExpandedTasks(prev => {
      const newSet = new Set(prev)
      if (newSet.has(taskId)) {
        newSet.delete(taskId)
      } else {
        newSet.add(taskId)
      }
      return newSet
    })
  }

  const handleToggleAutoContinue = (agentId: string) => {
    updateAgent(agentId, { autoContinue: !agents.find(a => a.id === agentId)?.autoContinue })
  }

  const handleChangeModel = (agentId: string, newModel: string) => {
    updateAgent(agentId, { model: newModel })
    setShowModelSelector(null)
  }

  const handleSendMessage = (agentId: string) => {
    if (!messageText.trim()) return
    console.log(`Sending message to ${agentId}:`, messageText)
    setMessageText('')
    updateAgent(agentId, {
      messages: (agents.find(a => a.id === agentId)?.messages || 0) + 1,
      lastActivity: 'just now'
    })
  }

  const handleBroadcast = () => {
    if (!broadcastMessage.trim()) return
    console.log('Broadcasting:', broadcastMessage)
    setBroadcastMessage('')
    agents.forEach(agent => {
      updateAgent(agent.id, {
        messages: agent.messages + 1,
        lastActivity: 'just now'
      })
    })
  }

  const handleAssignTask = (taskId: string, agentId: string) => {
    setTasks(tasks.map(task =>
      task.id === taskId
        ? { ...task, assignedTo: agentId, status: 'in_progress' as const }
        : task
    ))
  }

  const handleUpdateSubtask = (taskId: string, subtaskId: string, updates: Partial<Subtask>) => {
    setTasks(tasks.map(task =>
      task.id === taskId
        ? {
            ...task,
            subtasks: task.subtasks.map(st =>
              st.id === subtaskId ? { ...st, ...updates } : st
            )
          }
        : task
    ))
  }

  // Render task breakdown view (detailed with subtasks)
  const renderTaskBreakdownView = () => {
    return (
      <div className="space-y-2">
        {filteredTasks.map((task) => {
          const isExpanded = expandedTasks.has(task.id)
          const agent = task.assignedTo ? agents.find(a => a.id === task.assignedTo) : null
          const completedSubtasks = task.subtasks.filter(st => st.status === 'completed').length
          const totalSubtasks = task.subtasks.length
          
          return (
            <div
              key={task.id}
              className={`bg-cursor-sidebar rounded border transition-all ${
                selectedTask === task.id ? 'border-cursor-status-bar border-2' : 'border-cursor-border'
              }`}
            >
              {/* Task Header */}
              <div
                className="p-3 cursor-pointer"
                onClick={() => toggleTaskExpansion(task.id)}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      {isExpanded ? (
                        <ChevronDown className="w-4 h-4 text-cursor-text-secondary" />
                      ) : (
                        <ChevronRight className="w-4 h-4 text-cursor-text-secondary" />
                      )}
                      <div className="font-semibold text-sm" style={{ fontSize: '13px' }}>{task.title}</div>
                      {task.tags && task.tags.length > 0 && (
                        <div className="flex gap-1">
                          {task.tags.map(tag => (
                            <span key={tag} className="px-1.5 py-0.5 bg-cursor-input-bg text-xs rounded">
                              {tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                    <div className="text-xs text-cursor-text-secondary ml-6">{task.description}</div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-1 text-xs rounded font-medium ${getTaskStatusColor(task.status)}`}>
                      {task.status.replace('_', ' ')}
                    </span>
                    <span className={`px-2 py-1 text-xs rounded font-medium ${getPriorityColor(task.priority)}`}>
                      {task.priority}
                    </span>
                  </div>
                </div>

                {/* Task Progress Bar */}
                <div className="ml-6 mb-2">
                  <div className="flex items-center justify-between text-xs mb-1">
                    <span className="text-cursor-text-secondary">
                      Progress: {completedSubtasks}/{totalSubtasks} subtasks ({task.progress}%)
                    </span>
                    {agent && (
                      <span className="text-cursor-text-secondary">
                        Assigned to: <span className="font-medium">{agent.name}</span>
                      </span>
                    )}
                  </div>
                  <div className="w-full bg-cursor-input-bg rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all ${
                        task.progress === 100 ? 'bg-green-500' :
                        task.progress >= 50 ? 'bg-blue-500' :
                        'bg-yellow-500'
                      }`}
                      style={{ width: `${task.progress}%` }}
                    />
                  </div>
                </div>

                {/* Task Metadata */}
                <div className="ml-6 flex items-center gap-4 text-xs text-cursor-text-secondary">
                  <div className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    Created: {new Date(task.createdAt).toLocaleDateString()}
                  </div>
                  {task.deadline && (
                    <div className="flex items-center gap-1">
                      <Target className="w-3 h-3" />
                      Deadline: {new Date(task.deadline).toLocaleDateString()}
                    </div>
                  )}
                  {task.estimatedTime && (
                    <div className="flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      Est: {task.estimatedTime}h
                    </div>
                  )}
                  {task.actualTime && (
                    <div className="flex items-center gap-1">
                      <Activity className="w-3 h-3" />
                      Actual: {task.actualTime}h
                    </div>
                  )}
                </div>

                {/* Dependencies */}
                {task.dependencies && task.dependencies.length > 0 && (
                  <div className="ml-6 mt-2 flex items-center gap-2 text-xs">
                    <Link2 className="w-3 h-3 text-cursor-text-secondary" />
                    <span className="text-cursor-text-secondary">Depends on:</span>
                    {task.dependencies.map(depId => {
                      const depTask = tasks.find(t => t.id === depId)
                      return depTask ? (
                        <span key={depId} className="px-1.5 py-0.5 bg-cursor-input-bg rounded">
                          {depTask.title}
                        </span>
                      ) : null
                    })}
                  </div>
                )}
              </div>

              {/* Subtasks (Expanded) */}
              {isExpanded && (
                <div className="border-t border-cursor-border p-3 bg-cursor-input-bg/30">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="text-xs font-semibold text-cursor-text-secondary">
                      Subtasks ({completedSubtasks}/{totalSubtasks} completed)
                    </h4>
                    {!task.assignedTo && (
                      <select
                        onChange={(e) => handleAssignTask(task.id, e.target.value)}
                        onClick={(e) => e.stopPropagation()}
                        className="text-xs bg-cursor-input-bg text-cursor-text px-2 py-1 rounded border border-cursor-border cursor-input"
                        style={{ fontSize: '11px' }}
                      >
                        <option value="">Assign to...</option>
                        {agents.map(agent => (
                          <option key={agent.id} value={agent.id}>{agent.name}</option>
                        ))}
                      </select>
                    )}
                  </div>
                  <div className="space-y-2">
                    {task.subtasks.map((subtask) => {
                      const subtaskAgent = subtask.assignedTo ? agents.find(a => a.id === subtask.assignedTo) : null
                      const blockedBy = subtask.dependencies?.filter(depId => {
                        const depSubtask = task.subtasks.find(st => st.id === depId)
                        return depSubtask && depSubtask.status !== 'completed'
                      })
                      
                      return (
                        <div
                          key={subtask.id}
                          className={`p-2 rounded border ${
                            subtask.status === 'completed' ? 'bg-green-900/20 border-green-600/30' :
                            subtask.status === 'failed' ? 'bg-red-900/20 border-red-600/30' :
                            subtask.status === 'in_progress' ? 'bg-blue-900/20 border-blue-600/30' :
                            blockedBy && blockedBy.length > 0 ? 'bg-orange-900/20 border-orange-600/30' :
                            'bg-cursor-sidebar border-cursor-border'
                          }`}
                        >
                          <div className="flex items-start justify-between mb-1">
                            <div className="flex-1">
                              <div className="flex items-center gap-2">
                                {subtask.status === 'completed' ? (
                                  <CheckCircle2 className="w-4 h-4 text-green-400" />
                                ) : subtask.status === 'in_progress' ? (
                                  <Circle className="w-4 h-4 text-blue-400 fill-blue-400" />
                                ) : blockedBy && blockedBy.length > 0 ? (
                                  <AlertCircle className="w-4 h-4 text-orange-400" />
                                ) : (
                                  <Circle className="w-4 h-4 text-gray-400" />
                                )}
                                <span className="text-xs font-medium" style={{ fontSize: '12px' }}>
                                  {subtask.title}
                                </span>
                              </div>
                              {blockedBy && blockedBy.length > 0 && (
                                <div className="ml-6 text-xs text-orange-400 mt-1">
                                  ⚠️ Blocked by: {blockedBy.map(id => {
                                    const dep = task.subtasks.find(st => st.id === id)
                                    return dep?.title
                                  }).filter(Boolean).join(', ')}
                                </div>
                              )}
                            </div>
                            <div className="flex items-center gap-2">
                              <span className={`px-1.5 py-0.5 text-xs rounded ${getTaskStatusColor(subtask.status)}`}>
                                {subtask.status.replace('_', ' ')}
                              </span>
                              {subtaskAgent && (
                                <span className="text-xs text-cursor-text-secondary">
                                  {subtaskAgent.name}
                                </span>
                              )}
                            </div>
                          </div>
                          
                          {/* Subtask Progress */}
                          <div className="ml-6 mt-2">
                            <div className="flex items-center justify-between text-xs mb-1">
                              <span className="text-cursor-text-secondary">Progress: {subtask.progress}%</span>
                              {subtask.estimatedTime && (
                                <span className="text-cursor-text-secondary">
                                  Est: {subtask.estimatedTime}m
                                  {subtask.actualTime && ` / Actual: ${subtask.actualTime}m`}
                                </span>
                              )}
                            </div>
                            <div className="w-full bg-cursor-input-bg rounded-full h-1.5">
                              <div
                                className={`h-1.5 rounded-full transition-all ${
                                  subtask.progress === 100 ? 'bg-green-500' :
                                  subtask.progress >= 50 ? 'bg-blue-500' :
                                  'bg-yellow-500'
                                }`}
                                style={{ width: `${subtask.progress}%` }}
                              />
                            </div>
                          </div>

                          {/* Subtask Controls */}
                          <div className="ml-6 mt-2 flex items-center gap-2">
                            {subtask.status !== 'completed' && (
                              <>
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation()
                                    handleUpdateSubtask(task.id, subtask.id, { status: 'in_progress', progress: Math.min(subtask.progress + 25, 100) })
                                  }}
                                  className="px-2 py-0.5 bg-blue-600 hover:bg-blue-700 rounded text-xs cursor-button"
                                  style={{ fontSize: '10px' }}
                                >
                                  Start
                                </button>
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation()
                                    handleUpdateSubtask(task.id, subtask.id, { status: 'completed', progress: 100 })
                                  }}
                                  className="px-2 py-0.5 bg-green-600 hover:bg-green-700 rounded text-xs cursor-button"
                                  style={{ fontSize: '10px' }}
                                >
                                  Complete
                                </button>
                              </>
                            )}
                            {!subtask.assignedTo && (
                              <select
                                onChange={(e) => {
                                  if (e.target.value) {
                                    handleUpdateSubtask(task.id, subtask.id, { assignedTo: e.target.value })
                                  }
                                }}
                                onClick={(e) => e.stopPropagation()}
                                className="text-xs bg-cursor-input-bg text-cursor-text px-1.5 py-0.5 rounded border border-cursor-border cursor-input"
                                style={{ fontSize: '10px' }}
                              >
                                <option value="">Assign...</option>
                                {agents.map(agent => (
                                  <option key={agent.id} value={agent.id}>{agent.name}</option>
                                ))}
                              </select>
                            )}
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </div>
              )}
            </div>
          )
        })}
      </div>
    )
  }

  // Render timeline view
  const renderTimelineView = () => {
    const sortedTasks = [...filteredTasks].sort((a, b) => 
      new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime()
    )

    return (
      <div className="space-y-4">
        {sortedTasks.map((task) => {
          const agent = task.assignedTo ? agents.find(a => a.id === task.assignedTo) : null
          const startDate = new Date(task.createdAt)
          const endDate = task.deadline ? new Date(task.deadline) : new Date(startDate.getTime() + (task.estimatedTime || 1) * 60 * 60 * 1000)
          
          return (
            <div key={task.id} className="flex items-start gap-4">
              {/* Timeline Line */}
              <div className="flex flex-col items-center">
                <div className={`w-3 h-3 rounded-full ${
                  task.status === 'completed' ? 'bg-green-500' :
                  task.status === 'in_progress' ? 'bg-blue-500' :
                  task.status === 'failed' ? 'bg-red-500' :
                  'bg-gray-500'
                }`} />
                <div className="w-0.5 h-full bg-cursor-border mt-1" />
              </div>

              {/* Task Content */}
              <div className="flex-1 bg-cursor-sidebar rounded p-3 border border-cursor-border">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <div className="font-semibold text-sm mb-1" style={{ fontSize: '13px' }}>{task.title}</div>
                    <div className="text-xs text-cursor-text-secondary mb-2">{task.description}</div>
                    {agent && (
                      <div className="flex items-center gap-2 text-xs text-cursor-text-secondary">
                        <Bot className="w-3 h-3" />
                        Assigned to: <span className="font-medium">{agent.name}</span>
                      </div>
                    )}
                  </div>
                  <div className="flex flex-col items-end gap-1">
                    <span className={`px-2 py-1 text-xs rounded font-medium ${getTaskStatusColor(task.status)}`}>
                      {task.status.replace('_', ' ')}
                    </span>
                    <span className={`px-2 py-1 text-xs rounded font-medium ${getPriorityColor(task.priority)}`}>
                      {task.priority}
                    </span>
                  </div>
                </div>

                {/* Progress */}
                <div className="mb-2">
                  <div className="flex items-center justify-between text-xs mb-1">
                    <span className="text-cursor-text-secondary">Progress: {task.progress}%</span>
                    <span className="text-cursor-text-secondary">
                      {task.subtasks.filter(st => st.status === 'completed').length}/{task.subtasks.length} subtasks
                    </span>
                  </div>
                  <div className="w-full bg-cursor-input-bg rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all ${
                        task.progress === 100 ? 'bg-green-500' :
                        task.progress >= 50 ? 'bg-blue-500' :
                        'bg-yellow-500'
                      }`}
                      style={{ width: `${task.progress}%` }}
                    />
                  </div>
                </div>

                {/* Timeline Dates */}
                <div className="flex items-center gap-4 text-xs text-cursor-text-secondary">
                  <div>Start: {startDate.toLocaleDateString()}</div>
                  {task.deadline && (
                    <div>Deadline: {endDate.toLocaleDateString()}</div>
                  )}
                  {task.estimatedTime && (
                    <div>Est: {task.estimatedTime}h</div>
                  )}
                </div>
              </div>
            </div>
          )
        })}
      </div>
    )
  }

  // Render board view (Kanban-style)
  const renderBoardView = () => {
    const columns = [
      { id: 'pending', title: 'Pending', status: 'pending' as const },
      { id: 'in_progress', title: 'In Progress', status: 'in_progress' as const },
      { id: 'completed', title: 'Completed', status: 'completed' as const },
      { id: 'failed', title: 'Failed', status: 'failed' as const }
    ]

    return (
      <div className="grid grid-cols-4 gap-3">
        {columns.map(column => {
          const columnTasks = filteredTasks.filter(t => t.status === column.status)
          
          return (
            <div key={column.id} className="flex flex-col">
              <div className="bg-cursor-sidebar rounded-t p-2 border border-cursor-border border-b-0">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-semibold" style={{ fontSize: '12px' }}>{column.title}</h3>
                  <span className="px-1.5 py-0.5 bg-cursor-input-bg rounded text-xs">
                    {columnTasks.length}
                  </span>
                </div>
              </div>
              <div className="flex-1 bg-cursor-sidebar rounded-b border border-cursor-border p-2 space-y-2 min-h-[400px]">
                {columnTasks.map(task => {
                  const agent = task.assignedTo ? agents.find(a => a.id === task.assignedTo) : null
                  
                  return (
                    <div
                      key={task.id}
                      className="bg-cursor-input-bg rounded p-2 border border-cursor-border cursor-pointer hover:border-cursor-status-bar transition-colors"
                      onClick={() => setSelectedTask(task.id)}
                    >
                      <div className="font-semibold text-xs mb-1" style={{ fontSize: '12px' }}>{task.title}</div>
                      <div className="text-xs text-cursor-text-secondary mb-2 line-clamp-2">{task.description}</div>
                      
                      {/* Progress */}
                      <div className="mb-2">
                        <div className="w-full bg-cursor-sidebar rounded-full h-1.5">
                          <div
                            className={`h-1.5 rounded-full transition-all ${
                              task.progress === 100 ? 'bg-green-500' :
                              task.progress >= 50 ? 'bg-blue-500' :
                              'bg-yellow-500'
                            }`}
                            style={{ width: `${task.progress}%` }}
                          />
                        </div>
                        <div className="text-xs text-cursor-text-secondary mt-1">
                          {task.progress}% • {task.subtasks.filter(st => st.status === 'completed').length}/{task.subtasks.length} subtasks
                        </div>
                      </div>

                      {/* Agent & Priority */}
                      <div className="flex items-center justify-between">
                        {agent && (
                          <div className="flex items-center gap-1 text-xs">
                            <Bot className="w-3 h-3 text-cursor-text-secondary" />
                            <span className="text-cursor-text-secondary">{agent.name}</span>
                          </div>
                        )}
                        <span className={`px-1.5 py-0.5 text-xs rounded ${getPriorityColor(task.priority)}`}>
                          {task.priority}
                        </span>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          )
        })}
      </div>
    )
  }

  // Render list view (compact)
  const renderListView = () => {
    return (
      <div className="space-y-1">
        {filteredTasks.map((task) => {
          const agent = task.assignedTo ? agents.find(a => a.id === task.assignedTo) : null
          
          return (
            <div
              key={task.id}
              className={`bg-cursor-sidebar rounded p-2 border cursor-pointer transition-colors ${
                selectedTask === task.id ? 'border-cursor-status-bar' : 'border-cursor-border'
              }`}
              onClick={() => setSelectedTask(task.id === selectedTask ? null : task.id)}
            >
              <div className="flex items-center justify-between">
                <div className="flex-1 flex items-center gap-2">
                  <div className="flex items-center gap-2 flex-1">
                    <span className={`px-2 py-0.5 text-xs rounded font-medium ${getTaskStatusColor(task.status)}`}>
                      {task.status.replace('_', ' ')}
                    </span>
                    <span className="font-semibold text-xs" style={{ fontSize: '12px' }}>{task.title}</span>
                    {agent && (
                      <span className="text-xs text-cursor-text-secondary">
                        → {agent.name}
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-24 bg-cursor-input-bg rounded-full h-1.5">
                      <div
                        className={`h-1.5 rounded-full ${
                          task.progress === 100 ? 'bg-green-500' :
                          task.progress >= 50 ? 'bg-blue-500' :
                          'bg-yellow-500'
                        }`}
                        style={{ width: `${task.progress}%` }}
                      />
                    </div>
                    <span className="text-xs text-cursor-text-secondary w-10 text-right">
                      {task.progress}%
                    </span>
                    <span className={`px-1.5 py-0.5 text-xs rounded ${getPriorityColor(task.priority)}`}>
                      {task.priority}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col bg-cursor-bg text-cursor-text">
      {/* Header */}
      <div className="p-2 border-b border-cursor-border">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <Bot className="w-5 h-5 text-cursor-status-bar" />
            <div>
              <h1 className="text-base font-semibold" style={{ fontSize: '15px' }}>Agent Management Dashboard</h1>
              <p className="text-xs text-cursor-text-secondary">Automate Cursor operations and manage AI agents</p>
            </div>
          </div>
          <div className="flex items-center gap-1.5">
            <button
              onClick={() => setShowTaskAssigner(!showTaskAssigner)}
              className="px-2 py-1 bg-cursor-status-bar hover:bg-cursor-status-bar/80 rounded flex items-center gap-1.5 text-xs cursor-button"
              style={{ fontSize: '12px' }}
            >
              <Plus className="w-3 h-3" />
              New Task
            </button>
            <button className="p-1.5 bg-cursor-hover hover:bg-cursor-active rounded cursor-button">
              <Settings className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-5 gap-2">
          <div className="bg-cursor-sidebar p-2 rounded cursor-list-item">
            <div className="text-xs text-cursor-text-secondary">Active Agents</div>
            <div className="text-lg font-bold" style={{ fontSize: '18px' }}>{agents.filter(a => a.status === 'active').length}</div>
          </div>
          <div className="bg-cursor-sidebar p-2 rounded cursor-list-item">
            <div className="text-xs text-cursor-text-secondary">Total Tasks</div>
            <div className="text-lg font-bold" style={{ fontSize: '18px' }}>{tasks.length}</div>
          </div>
          <div className="bg-cursor-sidebar p-2 rounded cursor-list-item">
            <div className="text-xs text-cursor-text-secondary">Completed</div>
            <div className="text-lg font-bold" style={{ fontSize: '18px' }}>{tasks.filter(t => t.status === 'completed').length}</div>
          </div>
          <div className="bg-cursor-sidebar p-2 rounded cursor-list-item">
            <div className="text-xs text-cursor-text-secondary">In Progress</div>
            <div className="text-lg font-bold" style={{ fontSize: '18px' }}>{tasks.filter(t => t.status === 'in_progress').length}</div>
          </div>
          <div className="bg-cursor-sidebar p-2 rounded cursor-list-item">
            <div className="text-xs text-cursor-text-secondary">Overall Progress</div>
            <div className="text-lg font-bold flex items-center gap-1" style={{ fontSize: '18px' }}>
              <TrendingUp className="w-4 h-4" />
              {overallProgress}%
            </div>
          </div>
        </div>
        
        {/* Confidence Metrics Dashboard */}
        <div className="mt-2 p-2 bg-cursor-sidebar rounded border border-cursor-border">
          <h3 className="text-sm font-semibold mb-2 flex items-center gap-1.5" style={{ fontSize: '13px' }}>
            <Brain className="w-4 h-4" />
            Confidence Metrics
          </h3>
          
          {/* Overall Confidence */}
          <div className="mb-2">
            <div className="text-xs text-cursor-text-secondary mb-1">Overall Confidence</div>
            <div className="text-lg font-bold" style={{ fontSize: '18px' }}>
              {(() => {
                const agentsWithConfidence = agents.filter(a => a.confidence !== undefined)
                if (agentsWithConfidence.length === 0) return 'N/A'
                const avgConfidence = agentsWithConfidence.reduce((sum, a) => sum + (a.confidence || 0), 0) / agentsWithConfidence.length
                const band = avgConfidence >= 0.90 ? '🟢 A-Band' : 
                             avgConfidence >= 0.70 ? '🟡 B-Band' : 
                             '🔴 C-Band'
                return `${(avgConfidence * 100).toFixed(0)}% ${band}`
              })()}
            </div>
          </div>

          {/* Confidence Distribution */}
          <div className="mb-2">
            <div className="text-xs text-cursor-text-secondary mb-1">Confidence Distribution</div>
            <div className="space-y-1">
              <div className="flex items-center justify-between text-xs">
                <span className="text-green-400">🟢 A-Band (≥0.90)</span>
                <span>{agents.filter(a => a.confidence !== undefined && a.confidence >= 0.90).length}</span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-yellow-400">🟡 B-Band (0.70-0.89)</span>
                <span>{agents.filter(a => a.confidence !== undefined && a.confidence >= 0.70 && a.confidence < 0.90).length}</span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-red-400">🔴 C-Band (&lt;0.70)</span>
                <span>{agents.filter(a => a.confidence !== undefined && a.confidence < 0.70).length}</span>
              </div>
            </div>
          </div>

          {/* Confusion Alerts */}
          {agents.filter(a => a.confidence !== undefined && a.confidence < 0.70).length > 0 && (
            <div className="mb-2 p-2 bg-red-900/30 border border-red-500 rounded">
              <div className="text-xs font-semibold text-red-400 mb-1">⚠️ Confusion Alerts</div>
              <div className="space-y-0.5">
                {agents
                  .filter(a => a.confidence !== undefined && a.confidence < 0.70)
                  .map(agent => (
                    <div key={agent.id} className="text-xs">
                      {agent.name} needs assistance (confidence: {(agent.confidence! * 100).toFixed(0)}%)
                    </div>
                  ))}
              </div>
            </div>
          )}

          {/* Kappa-Gate Status */}
          <div>
            <div className="text-xs text-cursor-text-secondary mb-1">κ-Gate Status</div>
            <div className="space-y-0.5 text-xs">
              <div className="flex items-center justify-between">
                <span>Prompt Continue</span>
                <span className="text-green-400">
                  {agents.filter(a => a.confidence !== undefined && a.confidence >= 0.70).length}/{agents.length} agents
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span>Task Assignment</span>
                <span className="text-green-400">
                  {agents.filter(a => a.confidence !== undefined && a.confidence >= 0.70).length}/{agents.length} agents
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto p-2 cursor-scrollbar">
        <div className="grid grid-cols-3 gap-2 mb-2">
          {/* Agent Cards */}
          <div className="space-y-2">
            <h2 className="text-sm font-semibold flex items-center gap-1.5" style={{ fontSize: '13px' }}>
              <Users className="w-4 h-4" />
              Agents ({agents.length})
            </h2>
            {agents.map((agent) => {
              const agentTasks = getAgentTasks(agent.id)
              const workload = getAgentWorkload(agent.id)
              
              return (
                <div
                  key={agent.id}
                  className={`bg-cursor-sidebar rounded p-2 border transition-all cursor-pointer cursor-list-item ${
                    selectedAgent === agent.id ? 'border-cursor-status-bar' : 'border-cursor-border'
                  }`}
                  onClick={() => setSelectedAgent(agent.id === selectedAgent ? null : agent.id)}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <div className={`w-2 h-2 rounded-full ${getStatusColor(agent.status)}`} />
                      <div>
                        <div className="font-semibold text-sm" style={{ fontSize: '13px' }}>{agent.name}</div>
                        <div className="text-xs text-cursor-text-secondary">{agent.role}</div>
                      </div>
                    </div>
                    {getStatusIcon(agent.status)}
                  </div>

                  {/* Workload Indicator */}
                  <div className="mb-2 p-1.5 bg-cursor-input-bg rounded">
                    <div className="flex items-center justify-between text-xs mb-1">
                      <span className="text-cursor-text-secondary">Workload</span>
                      <span className="font-semibold">{workload} tasks</span>
                    </div>
                    <div className="space-y-1">
                      {agentTasks.slice(0, 3).map(task => (
                        <div key={task.id} className="text-xs text-cursor-text-secondary truncate">
                          • {task.title}
                        </div>
                      ))}
                      {agentTasks.length > 3 && (
                        <div className="text-xs text-cursor-text-secondary">
                          +{agentTasks.length - 3} more
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Model Selection */}
                  <div className="mb-2">
                    <div className="flex items-center justify-between mb-0.5">
                      <span className="text-xs text-cursor-text-secondary">Model</span>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          setShowModelSelector(showModelSelector === agent.id ? null : agent.id)
                        }}
                        className="text-xs text-cursor-status-bar hover:text-cursor-status-bar/80 cursor-button"
                      >
                        Change
                      </button>
                    </div>
                    {showModelSelector === agent.id ? (
                      <select
                        value={agent.model}
                        onChange={(e) => handleChangeModel(agent.id, e.target.value)}
                        onClick={(e) => e.stopPropagation()}
                        className="w-full bg-cursor-input-bg text-cursor-text text-xs px-1.5 py-0.5 rounded border border-cursor-border cursor-input"
                        style={{ fontSize: '12px' }}
                      >
                        {availableModels.map(model => (
                          <option key={model} value={model}>{model}</option>
                        ))}
                      </select>
                    ) : (
                      <div className="text-xs font-medium" style={{ fontSize: '12px' }}>{agent.model}</div>
                    )}
                  </div>

                  {/* Current Task */}
                  {agent.currentTask && (
                    <div className="mb-2">
                      <div className="text-xs text-cursor-text-secondary mb-0.5">Current Task</div>
                      <div className="text-xs" style={{ fontSize: '12px' }}>{agent.currentTask}</div>
                      {agent.progress !== undefined && (
                        <div className="mt-1">
                          <div className="flex items-center justify-between text-xs mb-0.5">
                            <span>Progress</span>
                            <span>{agent.progress}%</span>
                          </div>
                          <div className="w-full bg-cursor-input-bg rounded-full h-1.5">
                            <div
                              className="bg-cursor-status-bar h-1.5 rounded-full transition-all"
                              style={{ width: `${agent.progress}%` }}
                            />
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Stats */}
                  <div className="grid grid-cols-3 gap-1.5 mb-2 text-xs">
                    <div>
                      <div className="text-cursor-text-secondary">Messages</div>
                      <div className="font-semibold">{agent.messages}</div>
                    </div>
                    <div>
                      <div className="text-cursor-text-secondary">Completed</div>
                      <div className="font-semibold">{agent.tasksCompleted}</div>
                    </div>
                    <div>
                      <div className="text-cursor-text-secondary">Confidence</div>
                      <div className={`font-semibold flex items-center gap-1 ${
                        agent.confidence !== undefined && agent.confidence >= 0.90 ? 'text-green-400' :
                        agent.confidence !== undefined && agent.confidence >= 0.70 ? 'text-yellow-400' :
                        agent.confidence !== undefined ? 'text-red-400' :
                        'text-gray-400'
                      }`}>
                        {agent.confidence !== undefined ? (
                          <>
                            {agent.confidence >= 0.90 ? '🟢' : agent.confidence >= 0.70 ? '🟡' : '🔴'}
                            {(agent.confidence * 100).toFixed(0)}%
                            {agent.confidence >= 0.90 ? ' (A)' : 
                             agent.confidence >= 0.70 ? ' (B)' : 
                             ' (C) ⚠️'}
                          </>
                        ) : 'N/A'}
                      </div>
                      {agent.confidence !== undefined && agent.confidence < 0.70 && (
                        <div className="text-xs text-red-400 mt-1">⚠️ Needs Assistance</div>
                      )}
                      {agent.confidence !== undefined && (
                        <div className="text-xs mt-1">
                          {agent.confidence >= 0.70 ? (
                            <span className="text-green-400">✅ κ-Gate: PASSED</span>
                          ) : (
                            <span className="text-red-400">❌ κ-Gate: BLOCKED</span>
                          )}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Controls */}
                  <div className="flex flex-col gap-1.5 pt-2 border-t border-cursor-border">
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        handleToggleAutoContinue(agent.id)
                      }}
                      className={`w-full px-2 py-1 rounded text-xs flex items-center justify-center gap-1 cursor-button ${
                        agent.autoContinue
                          ? 'bg-green-600 hover:bg-green-700'
                          : 'bg-cursor-hover hover:bg-cursor-active'
                      }`}
                      style={{ fontSize: '11px' }}
                      title="Auto-continue prompts"
                    >
                      {agent.autoContinue ? (
                        <>
                          <Bell className="w-3 h-3" />
                          Auto-On
                        </>
                      ) : (
                        <>
                          <BellOff className="w-3 h-3" />
                          Auto-Off
                        </>
                      )}
                    </button>
                    
                    <div className="flex items-center gap-1.5">
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          console.log(`Prompting ${agent.id} to continue`)
                        }}
                        disabled={agent.confidence !== undefined && agent.confidence < 0.70}
                        className={`flex-1 px-2 py-1 rounded text-xs flex items-center justify-center gap-1 cursor-button ${
                          agent.confidence !== undefined && agent.confidence < 0.70
                            ? 'bg-cursor-input-bg text-cursor-text-muted cursor-not-allowed'
                            : 'bg-cursor-status-bar hover:bg-cursor-status-bar/80'
                        }`}
                        style={{ fontSize: '11px' }}
                        title={agent.confidence !== undefined && agent.confidence < 0.70 
                          ? 'Confidence too low (requires ≥0.70)' 
                          : 'Prompt agent to continue'}
                      >
                        <RefreshCw className="w-3 h-3" />
                        Continue
                      </button>
                      
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          if ((window as any).handleChatWithAgent) {
                            ;(window as any).handleChatWithAgent(agent.name)
                          } else {
                            setSelectedAgent(agent.id)
                          }
                        }}
                        className="px-2 py-1 bg-cursor-status-bar hover:bg-cursor-status-bar/80 rounded text-xs flex items-center gap-1 cursor-button"
                        style={{ fontSize: '11px' }}
                        title={`Chat with ${agent.name}`}
                      >
                        <MessageSquare className="w-3 h-3" />
                        Chat
                      </button>
                    </div>
                    
                    {agent.confidence !== undefined && agent.confidence < 0.70 && (
                      <div className="flex items-center gap-1.5">
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            setShowQuestionPanel({ agentId: agent.id, agentName: agent.name })
                          }}
                          className="flex-1 px-2 py-1 bg-yellow-600 hover:bg-yellow-700 rounded text-xs flex items-center justify-center gap-1 cursor-button"
                          style={{ fontSize: '11px' }}
                          title="Agent needs assistance - ask question"
                        >
                          <AlertCircle className="w-3 h-3" />
                          Ask Question
                        </button>
                        
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            console.log(`Providing context to ${agent.id}`)
                          }}
                          className="flex-1 px-2 py-1 bg-purple-600 hover:bg-purple-700 rounded text-xs flex items-center justify-center gap-1 cursor-button"
                          style={{ fontSize: '11px' }}
                          title="Provide context to improve confidence"
                        >
                          <Brain className="w-3 h-3" />
                          Provide Context
                        </button>
                      </div>
                    )}
                  </div>

                  <div className="mt-1 text-xs text-cursor-text-secondary">
                    Last activity: {agent.lastActivity}
                  </div>
                </div>
              )
            })}
          </div>

          {/* Task Management Area */}
          <div className="col-span-2 space-y-2">
            {/* Task View Controls */}
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-sm font-semibold flex items-center gap-1.5" style={{ fontSize: '13px' }}>
                <Target className="w-4 h-4" />
                Tasks ({filteredTasks.length}/{tasks.length})
              </h2>
              <div className="flex items-center gap-2">
                {/* Search */}
                <div className="relative">
                  <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 w-3.5 h-3.5 text-cursor-text-secondary" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search tasks..."
                    className="pl-8 pr-2 py-1 bg-cursor-input-bg text-cursor-text text-xs rounded border border-cursor-border focus:outline-none focus:border-cursor-status-bar cursor-input"
                    style={{ fontSize: '11px', width: '150px' }}
                  />
                </div>
                
                {/* Filter */}
                <select
                  value={taskFilter}
                  onChange={(e) => setTaskFilter(e.target.value as any)}
                  className="px-2 py-1 bg-cursor-input-bg text-cursor-text text-xs rounded border border-cursor-border cursor-input"
                  style={{ fontSize: '11px' }}
                >
                  <option value="all">All</option>
                  <option value="pending">Pending</option>
                  <option value="in_progress">In Progress</option>
                  <option value="completed">Completed</option>
                  <option value="failed">Failed</option>
                </select>

                {/* View Switcher */}
                <div className="flex items-center gap-1 bg-cursor-sidebar rounded border border-cursor-border p-0.5">
                  <button
                    onClick={() => setTaskView('breakdown')}
                    className={`px-2 py-1 rounded text-xs cursor-button ${
                      taskView === 'breakdown' ? 'bg-cursor-status-bar' : 'bg-transparent'
                    }`}
                    style={{ fontSize: '11px' }}
                    title="Detailed Breakdown View"
                  >
                    <BarChart3 className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={() => setTaskView('list')}
                    className={`px-2 py-1 rounded text-xs cursor-button ${
                      taskView === 'list' ? 'bg-cursor-status-bar' : 'bg-transparent'
                    }`}
                    style={{ fontSize: '11px' }}
                    title="List View"
                  >
                    <List className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={() => setTaskView('timeline')}
                    className={`px-2 py-1 rounded text-xs cursor-button ${
                      taskView === 'timeline' ? 'bg-cursor-status-bar' : 'bg-transparent'
                    }`}
                    style={{ fontSize: '11px' }}
                    title="Timeline View"
                  >
                    <Calendar className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={() => setTaskView('board')}
                    className={`px-2 py-1 rounded text-xs cursor-button ${
                      taskView === 'board' ? 'bg-cursor-status-bar' : 'bg-transparent'
                    }`}
                    style={{ fontSize: '11px' }}
                    title="Board View (Kanban)"
                  >
                    <LayoutGrid className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={() => setTaskView('agent-timeline')}
                    className={`px-2 py-1 rounded text-xs cursor-button ${
                      taskView === 'agent-timeline' ? 'bg-cursor-status-bar' : 'bg-transparent'
                    }`}
                    style={{ fontSize: '11px' }}
                    title="Agent Management Timeline ⭐"
                  >
                    <Network className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>

            {/* Task View Content */}
            <div className="bg-cursor-sidebar rounded border border-cursor-border p-3">
              {taskView === 'breakdown' && renderTaskBreakdownView()}
              {taskView === 'list' && renderListView()}
              {taskView === 'timeline' && renderTimelineView()}
              {taskView === 'board' && renderBoardView()}
              {taskView === 'agent-timeline' && (
                <div className="h-[600px]">
                  <AgentManagementTimeline />
                </div>
              )}
            </div>

            {/* Agent Communication */}
            {selectedAgent && (
              <div className="bg-cursor-sidebar rounded p-2 border border-cursor-border">
                <h3 className="font-semibold mb-2 flex items-center gap-1.5 text-xs" style={{ fontSize: '12px' }}>
                  <MessageSquare className="w-3.5 h-3.5" />
                  Message {agents.find(a => a.id === selectedAgent)?.name}
                </h3>
                <div className="flex gap-1.5">
                  <input
                    type="text"
                    value={messageText}
                    onChange={(e) => setMessageText(e.target.value)}
                    placeholder="Type message..."
                    className="flex-1 bg-cursor-input-bg text-cursor-text px-2 py-1 rounded border border-cursor-border focus:outline-none focus:border-cursor-status-bar cursor-input"
                    style={{ fontSize: '12px' }}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        handleSendMessage(selectedAgent)
                      }
                    }}
                  />
                  <button
                    onClick={() => handleSendMessage(selectedAgent)}
                    className="px-2 py-1 bg-cursor-status-bar hover:bg-cursor-status-bar/80 rounded flex items-center gap-1.5 cursor-button"
                    style={{ fontSize: '12px' }}
                  >
                    <Send className="w-3.5 h-3.5" />
                    Send
                  </button>
                </div>
              </div>
            )}

            {/* Broadcast */}
            <div className="bg-cursor-sidebar rounded p-2 border border-cursor-border">
              <h3 className="font-semibold mb-2 flex items-center gap-1.5 text-xs" style={{ fontSize: '12px' }}>
                <Network className="w-3.5 h-3.5" />
                Broadcast to All Agents
              </h3>
              <div className="flex gap-1.5">
                <input
                  type="text"
                  value={broadcastMessage}
                  onChange={(e) => setBroadcastMessage(e.target.value)}
                  placeholder="Broadcast message..."
                  className="flex-1 bg-cursor-input-bg text-cursor-text px-2 py-1 rounded border border-cursor-border focus:outline-none focus:border-cursor-status-bar cursor-input"
                  style={{ fontSize: '12px' }}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      handleBroadcast()
                    }
                  }}
                />
                <button
                  onClick={handleBroadcast}
                  className="px-2 py-1 bg-purple-600 hover:bg-purple-700 rounded flex items-center gap-1.5 cursor-button"
                  style={{ fontSize: '12px' }}
                >
                  <Send className="w-3.5 h-3.5" />
                  Broadcast
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Agent Question Panel */}
      {showQuestionPanel && (() => {
        const agent = agents.find(a => a.id === showQuestionPanel.agentId)
        return agent ? (
          <AgentQuestionPanel
            agentId={agent.id}
            agentName={agent.name}
            currentConfidence={agent.confidence || 0}
            onClose={() => setShowQuestionPanel(null)}
            onAnswer={(question, answer) => {
              console.log(`Answering ${agent.name}:`, answer)
              setShowQuestionPanel(null)
            }}
            onProvideContext={() => {
              console.log(`Providing context to ${agent.name}`)
            }}
          />
        ) : null
      })()}
    </div>
  )
}

export default AgentManagementDashboard
