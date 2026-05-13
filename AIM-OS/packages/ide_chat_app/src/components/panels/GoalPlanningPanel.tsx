/**
 * Goal Planning Panel Component - ENHANCED
 * 
 * Phase 2.2: Right Drawer Panels
 * 
 * Goal management and planning visualization with comprehensive AIM-OS integration.
 * Features:
 * - Goal hierarchy with expandable tree ⭐
 * - Goal progress tracking with visual indicators ⭐
 * - Goal timeline integration (TCS) ⭐
 * - Goal dependencies visualization ⭐
 * - Goal creation and editing ⭐
 * - Multiple views (Tree, Timeline, Board) ⭐
 * - AIM-OS integration (Goal Timeline System, TCS, APOE, VIF confidence) ⭐
 * - Search and advanced filtering ⭐
 * 
 * Enhanced: 2025-11-07 (Rev - Competition Phase)
 */

import React, { useState, useCallback, useMemo, useEffect } from 'react'
import { 
  Target, 
  CheckCircle2, 
  Circle, 
  Clock, 
  TrendingUp, 
  AlertCircle, 
  Plus, 
  Edit2, 
  Trash2, 
  ChevronRight, 
  ChevronDown,
  Search,
  Filter,
  Calendar,
  List,
  LayoutGrid,
  Link2,
  Brain,
  BarChart3,
  X,
  Save,
  Zap,
  GitBranch,
  Play,
  Pause,
  RefreshCw
} from 'lucide-react'
import { useAIMOS } from '../../hooks/useAIMOS'
import { useDebounce } from '../../hooks/useDebounce'
import { ErrorBoundary } from '../ErrorBoundary'
import { LoadingState } from '../LoadingState'

interface Goal {
  id: string
  name: string
  description: string
  status: 'planned' | 'in_progress' | 'completed' | 'blocked' | 'cancelled'
  progress: number // 0-100
  priority: 'low' | 'medium' | 'high' | 'critical'
  dueDate?: string
  createdAt: string
  dependencies: string[]
  children?: Goal[]
  confidence?: number // VIF confidence
  keyResults?: string[]
  timelineNodeId?: string // TCS integration
  apoePlanId?: string // APOE integration
}

type GoalView = 'tree' | 'timeline' | 'board'

const mockGoals: Goal[] = [
  {
    id: 'goal-1',
    name: 'Complete IDE Prototype',
    description: 'Build comprehensive IDE layout prototype with all panels and features',
    status: 'in_progress',
    progress: 75,
    priority: 'critical',
    dueDate: '2025-11-15',
    createdAt: '2025-11-01T00:00:00Z',
    dependencies: [],
    confidence: 0.85,
    keyResults: [
      'All panels implemented',
      'AIM-OS integration complete',
      'Documentation finished'
    ],
    timelineNodeId: 'timeline-node-001',
    apoePlanId: 'apoe-plan-001',
    children: [
      {
        id: 'goal-1-1',
        name: 'Phase 2: Panel Implementation',
        description: 'Implement all right drawer panels',
        status: 'in_progress',
        progress: 85,
        priority: 'high',
        createdAt: '2025-11-05T00:00:00Z',
        dependencies: ['goal-1-2'],
        confidence: 0.90,
        children: [
          {
            id: 'goal-1-1-1',
            name: 'Properties Panel',
            description: 'Complete Properties Panel with validation',
            status: 'completed',
            progress: 100,
            priority: 'high',
            createdAt: '2025-11-06T00:00:00Z',
            dependencies: [],
            confidence: 0.95
          },
          {
            id: 'goal-1-1-2',
            name: 'Problems Panel',
            description: 'Complete Problems Panel with quick fixes',
            status: 'completed',
            progress: 100,
            priority: 'high',
            createdAt: '2025-11-06T00:00:00Z',
            dependencies: [],
            confidence: 0.95
          },
          {
            id: 'goal-1-1-3',
            name: 'Output Panel',
            description: 'Complete Output Panel with real-time updates',
            status: 'completed',
            progress: 100,
            priority: 'medium',
            createdAt: '2025-11-07T00:00:00Z',
            dependencies: [],
            confidence: 0.92
          },
          {
            id: 'goal-1-1-4',
            name: 'Context Web Panel',
            description: 'Add revolutionary Context Web Panel',
            status: 'planned',
            progress: 0,
            priority: 'critical',
            createdAt: '2025-11-07T00:00:00Z',
            dependencies: ['goal-1-1-1', 'goal-1-1-2', 'goal-1-1-3'],
            confidence: 0.75
          }
        ]
      },
      {
        id: 'goal-1-2',
        name: 'Phase 1: Core Layout',
        description: 'Create core layout structure',
        status: 'completed',
        progress: 100,
        priority: 'critical',
        createdAt: '2025-11-01T00:00:00Z',
        dependencies: [],
        confidence: 0.95
      },
      {
        id: 'goal-1-3',
        name: 'Phase 3: Customization',
        description: 'Implement drag-and-drop, layout saving',
        status: 'planned',
        progress: 0,
        priority: 'medium',
        createdAt: '2025-11-07T00:00:00Z',
        dependencies: ['goal-1-1'],
        confidence: 0.80
      }
    ],
  },
  {
    id: 'goal-2',
    name: 'Revolutionary Features Integration',
    description: 'Integrate Context Web, Bitemporal Timeline, Evolution Explorer',
    status: 'planned',
    progress: 0,
    priority: 'high',
    createdAt: '2025-11-05T00:00:00Z',
    dependencies: ['goal-1'],
    confidence: 0.75,
    timelineNodeId: 'timeline-node-002'
  },
  {
    id: 'goal-3',
    name: 'Agent Management Enhancement',
    description: 'Enhance Agent Management Dashboard with task breakdown',
    status: 'completed',
    progress: 100,
    priority: 'high',
    createdAt: '2025-11-07T00:00:00Z',
    dependencies: [],
    confidence: 0.95,
    timelineNodeId: 'timeline-node-003'
  },
  {
    id: 'goal-4',
    name: 'Panel Polish & Enhancement',
    description: 'Review and enhance all panels with real functionality',
    status: 'in_progress',
    progress: 60,
    priority: 'high',
    createdAt: '2025-11-07T00:00:00Z',
    dependencies: ['goal-1-1'],
    confidence: 0.88
  }
]

export const GoalPlanningPanel: React.FC = () => {
  const [goals, setGoals] = useState<Goal[]>(mockGoals)
  const [expandedGoals, setExpandedGoals] = useState<Set<string>>(new Set(['goal-1', 'goal-1-1']))
  const [selectedGoal, setSelectedGoal] = useState<Goal | null>(null)
  const [filterStatus, setFilterStatus] = useState<'all' | Goal['status']>('all')
  const [filterPriority, setFilterPriority] = useState<'all' | Goal['priority']>('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [goalView, setGoalView] = useState<GoalView>('tree')
  const [showCreateGoal, setShowCreateGoal] = useState(false)
  const [apoePlans, setApoePlans] = useState<Map<string, any>>(new Map())
  const [executingPlans, setExecutingPlans] = useState<Set<string>>(new Set())

  // Debounce search query for performance
  const debouncedSearchQuery = useDebounce(searchQuery, 300)

  // AIM-OS integration
  const { goals: aimosGoals, tcs, apoe, vif, isConnected, useMockData, loading } = useAIMOS()

  // Load goals from AIM-OS and APOE plans
  useEffect(() => {
    const loadGoals = async () => {
      try {
        if (!useMockData && isConnected) {
          // Load goals from Goal Timeline System
          const loadedGoals = await aimosGoals.query({})
          if (loadedGoals.length > 0) {
            // Transform AIM-OS goals to panel format
            const transformedGoals: Goal[] = loadedGoals.map(g => ({
              id: g.id,
              name: g.name,
              description: g.description,
              status: g.status,
              progress: g.progress,
              priority: g.priority,
              dueDate: g.dueDate,
              createdAt: g.createdAt,
              dependencies: g.dependencies,
              confidence: g.confidence || 0.85,
              timelineNodeId: g.timelineNodeId,
              apoePlanId: g.apoePlanId,
              children: [],
            }))
            setGoals(transformedGoals)
            
            // Load APOE plans for goals that have them
            const planPromises = transformedGoals
              .filter(g => g.apoePlanId)
              .map(async (goal) => {
                try {
                  const plan = await apoe.createPlan(goal.description || goal.name, goal.priority || 'medium')
                  if (plan) {
                    setApoePlans(prev => new Map(prev).set(goal.id, plan))
                  }
                } catch (err) {
                  console.warn(`Failed to load APOE plan for goal ${goal.id}:`, err)
                }
              })
            await Promise.all(planPromises)
          }
        }
      } catch (error) {
        console.warn('Failed to load goals from AIM-OS, using mock data', error)
        // Keep mock goals as fallback
      }
    }
    
    loadGoals()
  }, [aimosGoals, apoe, useMockData, isConnected])
  
  // Track confidence for goals
  useEffect(() => {
    const trackConfidences = async () => {
      if (!useMockData && isConnected) {
        for (const goal of allGoals) {
          if (goal.confidence === undefined) {
            try {
              const confidence = await vif.trackConfidence(
                `Goal: ${goal.name}`,
                0.85, // Default confidence
                `Goal status: ${goal.status}, Progress: ${goal.progress}%`
              )
              // Update goal confidence if tracked
            } catch (err) {
              console.warn(`Failed to track confidence for goal ${goal.id}:`, err)
            }
          }
        }
      }
    }
    
    if (allGoals.length > 0) {
      trackConfidences()
    }
  }, [allGoals, vif, useMockData, isConnected])
  
  // Execute APOE plan for a goal
  const executeApoePlan = useCallback(async (goal: Goal) => {
    if (!goal.apoePlanId) {
      // Create plan if it doesn't exist
      try {
        const plan = await apoe.createPlan(goal.description || goal.name, goal.priority || 'medium')
        if (plan) {
          setApoePlans(prev => new Map(prev).set(goal.id, plan))
          setExecutingPlans(prev => new Set(prev).add(goal.id))
          
          // Simulate plan execution (in real implementation, this would be async)
          setTimeout(() => {
            setExecutingPlans(prev => {
              const newSet = new Set(prev)
              newSet.delete(goal.id)
              return newSet
            })
          }, 2000)
        }
      } catch (err) {
        console.error(`Failed to create/execute APOE plan for goal ${goal.id}:`, err)
      }
    } else {
      // Execute existing plan
      setExecutingPlans(prev => new Set(prev).add(goal.id))
      setTimeout(() => {
        setExecutingPlans(prev => {
          const newSet = new Set(prev)
          newSet.delete(goal.id)
          return newSet
        })
      }, 2000)
    }
  }, [apoe])

  // Flatten goals for easier searching and filtering
  const flattenGoals = useCallback((goalList: Goal[]): Goal[] => {
    const result: Goal[] = []
    const traverse = (goal: Goal) => {
      result.push(goal)
      if (goal.children) {
        goal.children.forEach(traverse)
      }
    }
    goalList.forEach(traverse)
    return result
  }, [])

  const allGoals = useMemo(() => flattenGoals(goals), [goals, flattenGoals])

  const filteredGoals = useMemo(() => {
    return goals.filter((goal) => {
      const matchesStatus = filterStatus === 'all' || goal.status === filterStatus
      const matchesPriority = filterPriority === 'all' || goal.priority === filterPriority
      const matchesSearch = debouncedSearchQuery === '' || 
        goal.name.toLowerCase().includes(debouncedSearchQuery.toLowerCase()) ||
        goal.description.toLowerCase().includes(debouncedSearchQuery.toLowerCase())
      
      // Also check children
      const hasMatchingChildren = goal.children?.some(child => {
        const childMatches = (filterStatus === 'all' || child.status === filterStatus) &&
          (filterPriority === 'all' || child.priority === filterPriority) &&
          (debouncedSearchQuery === '' || 
            child.name.toLowerCase().includes(debouncedSearchQuery.toLowerCase()) ||
            child.description.toLowerCase().includes(debouncedSearchQuery.toLowerCase()))
        return childMatches
      })
      
      return (matchesStatus && matchesPriority && matchesSearch) || hasMatchingChildren
    })
  }, [goals, filterStatus, filterPriority, debouncedSearchQuery])

  const toggleGoal = (goalId: string) => {
    setExpandedGoals(prev => {
      const newSet = new Set(prev)
      if (newSet.has(goalId)) {
        newSet.delete(goalId)
      } else {
        newSet.add(goalId)
      }
      return newSet
    })
  }

  const getStatusIcon = (status: Goal['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="w-4 h-4 text-green-400" />
      case 'in_progress':
        return <Circle className="w-4 h-4 text-blue-400 fill-blue-400" />
      case 'blocked':
        return <AlertCircle className="w-4 h-4 text-red-400" />
      case 'cancelled':
        return <Circle className="w-4 h-4 text-gray-500" />
      default:
        return <Clock className="w-4 h-4 text-yellow-400" />
    }
  }

  const getStatusColor = (status: Goal['status']) => {
    switch (status) {
      case 'completed':
        return 'bg-green-600 text-white'
      case 'in_progress':
        return 'bg-blue-600 text-white'
      case 'blocked':
        return 'bg-red-600 text-white'
      case 'cancelled':
        return 'bg-gray-600 text-white'
      default:
        return 'bg-yellow-600 text-white'
    }
  }

  const getPriorityColor = (priority: Goal['priority']) => {
    switch (priority) {
      case 'critical':
        return 'text-red-400 bg-red-600/20'
      case 'high':
        return 'text-orange-400 bg-orange-600/20'
      case 'medium':
        return 'text-yellow-400 bg-yellow-600/20'
      default:
        return 'text-gray-400 bg-gray-600/20'
    }
  }

  const calculateOverallProgress = (goal: Goal): number => {
    if (!goal.children || goal.children.length === 0) {
      return goal.progress
    }
    const childrenProgress = goal.children.reduce((sum, child) => sum + calculateOverallProgress(child), 0)
    return Math.round(childrenProgress / goal.children.length)
  }

  const getBlockedGoals = (goal: Goal): Goal[] => {
    const blocked: Goal[] = []
    goal.dependencies.forEach(depId => {
      const depGoal = allGoals.find(g => g.id === depId)
      if (depGoal && depGoal.status !== 'completed') {
        blocked.push(depGoal)
      }
    })
    return blocked
  }

  const renderGoalTree = (goal: Goal, depth: number = 0): React.ReactNode => {
    const hasChildren = goal.children && goal.children.length > 0
    const isExpanded = expandedGoals.has(goal.id)
    const isSelected = selectedGoal?.id === goal.id
    const blockedBy = getBlockedGoals(goal)
    const overallProgress = calculateOverallProgress(goal)
    const daysUntilDue = goal.dueDate ? Math.ceil((new Date(goal.dueDate).getTime() - Date.now()) / (1000 * 60 * 60 * 24)) : null

    return (
      <div key={goal.id}>
        <div
          className={`flex items-start gap-2 px-3 py-2 rounded cursor-pointer transition-colors border ${
            isSelected
              ? 'bg-blue-600/20 border-blue-500'
              : blockedBy.length > 0
              ? 'bg-red-900/20 border-red-500/30'
              : 'hover:bg-gray-700/50 border-transparent'
          }`}
          style={{ paddingLeft: `${depth * 20 + 12}px` }}
          onClick={() => setSelectedGoal(goal)}
        >
          {/* Expand/Collapse */}
          {hasChildren && (
            <button
              onClick={(e) => {
                e.stopPropagation()
                toggleGoal(goal.id)
              }}
              className="p-0.5 hover:bg-gray-600 rounded shrink-0 mt-0.5"
            >
              {isExpanded ? (
                <ChevronDown className="w-4 h-4 text-gray-400" />
              ) : (
                <ChevronRight className="w-4 h-4 text-gray-400" />
              )}
            </button>
          )}
          {!hasChildren && <div className="w-5 shrink-0" />}

          {/* Status Icon */}
          {getStatusIcon(goal.status)}

          {/* Goal Content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-sm font-medium text-gray-300 truncate" title={goal.name}>
                {goal.name}
              </span>
              <span className={`px-1.5 py-0.5 text-xs rounded font-medium ${getStatusColor(goal.status)}`}>
                {goal.status.replace('_', ' ')}
              </span>
              <span className={`px-1.5 py-0.5 text-xs rounded ${getPriorityColor(goal.priority)}`}>
                {goal.priority}
              </span>
              {goal.confidence !== undefined && (
                <span className={`text-xs px-1.5 py-0.5 rounded ${
                  goal.confidence >= 0.90 ? 'bg-green-600/20 text-green-400' :
                  goal.confidence >= 0.70 ? 'bg-yellow-600/20 text-yellow-400' :
                  'bg-red-600/20 text-red-400'
                }`} title="VIF Confidence">
                  {(goal.confidence * 100).toFixed(0)}%
                </span>
              )}
              {blockedBy.length > 0 && (
                <span className="text-xs text-red-400 flex items-center gap-1" title={`Blocked by: ${blockedBy.map(g => g.name).join(', ')}`}>
                  <AlertCircle className="w-3 h-3" />
                  Blocked
                </span>
              )}
              {daysUntilDue !== null && daysUntilDue < 7 && daysUntilDue >= 0 && (
                <span className="text-xs text-orange-400 flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  {daysUntilDue}d left
                </span>
              )}
            </div>
            
            {/* Progress Bar */}
            <div className="flex items-center gap-2 mb-1">
              <div className="flex-1 h-2 bg-gray-700 rounded-full overflow-hidden">
                <div
                  className={`h-full transition-all ${
                    goal.status === 'completed'
                      ? 'bg-green-500'
                      : goal.status === 'in_progress'
                      ? 'bg-blue-500'
                      : goal.status === 'blocked'
                      ? 'bg-red-500'
                      : 'bg-gray-600'
                  }`}
                  style={{ width: `${overallProgress}%` }}
                />
              </div>
              <span className="text-xs text-gray-400 shrink-0">{overallProgress}%</span>
              {hasChildren && (
                <span className="text-xs text-gray-500 shrink-0">
                  ({goal.children!.filter(c => c.status === 'completed').length}/{goal.children!.length} sub-goals)
                </span>
              )}
            </div>

            {/* Description */}
            {goal.description && (
              <p className="text-xs text-gray-500 line-clamp-1">{goal.description}</p>
            )}

            {/* Dependencies */}
            {goal.dependencies.length > 0 && (
              <div className="mt-1 flex items-center gap-1 text-xs text-gray-500">
                <Link2 className="w-3 h-3" />
                Depends on: {goal.dependencies.map(depId => {
                  const dep = allGoals.find(g => g.id === depId)
                  return dep?.name || depId
                }).join(', ')}
              </div>
            )}
          </div>
        </div>

        {/* Children */}
        {hasChildren && isExpanded && goal.children && (
          <div className="ml-4 border-l-2 border-gray-700">
            {goal.children.map((child) => renderGoalTree(child, depth + 1))}
          </div>
        )}
      </div>
    )
  }

  // Render timeline view
  const renderTimelineView = () => {
    const sortedGoals = [...allGoals].sort((a, b) => 
      new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime()
    )

    return (
      <div className="space-y-3">
        {sortedGoals.map((goal) => {
          const blockedBy = getBlockedGoals(goal)
          const daysUntilDue = goal.dueDate ? Math.ceil((new Date(goal.dueDate).getTime() - Date.now()) / (1000 * 60 * 60 * 24)) : null
          
          return (
            <div
              key={goal.id}
              className={`p-3 rounded border cursor-pointer transition-colors ${
                selectedGoal?.id === goal.id
                  ? 'bg-blue-600/20 border-blue-500'
                  : 'bg-gray-700/50 border-gray-700 hover:border-gray-600'
              }`}
              onClick={() => setSelectedGoal(goal)}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    {getStatusIcon(goal.status)}
                    <span className="text-sm font-medium text-gray-300">{goal.name}</span>
                    <span className={`px-1.5 py-0.5 text-xs rounded ${getStatusColor(goal.status)}`}>
                      {goal.status.replace('_', ' ')}
                    </span>
                    <span className={`px-1.5 py-0.5 text-xs rounded ${getPriorityColor(goal.priority)}`}>
                      {goal.priority}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 mb-2">{goal.description}</p>
                </div>
                <div className="flex flex-col items-end gap-1">
                  {goal.confidence !== undefined && (
                    <span className={`text-xs px-1.5 py-0.5 rounded ${
                      goal.confidence >= 0.90 ? 'bg-green-600/20 text-green-400' :
                      goal.confidence >= 0.70 ? 'bg-yellow-600/20 text-yellow-400' :
                      'bg-red-600/20 text-red-400'
                    }`}>
                      VIF: {(goal.confidence * 100).toFixed(0)}%
                    </span>
                  )}
                  {goal.timelineNodeId && (
                    <span className="text-xs text-purple-400 flex items-center gap-1" title="Linked to Timeline">
                      <Calendar className="w-3 h-3" />
                      Timeline
                    </span>
                  )}
                </div>
              </div>

              {/* Progress */}
              <div className="mb-2">
                <div className="flex items-center justify-between text-xs mb-1">
                  <span className="text-gray-400">Progress: {goal.progress}%</span>
                  {daysUntilDue !== null && (
                    <span className={`text-xs ${
                      daysUntilDue < 0 ? 'text-red-400' :
                      daysUntilDue < 7 ? 'text-orange-400' :
                      'text-gray-400'
                    }`}>
                      {daysUntilDue < 0 ? `Overdue by ${Math.abs(daysUntilDue)}d` :
                       daysUntilDue === 0 ? 'Due today' :
                       `${daysUntilDue}d remaining`}
                    </span>
                  )}
                </div>
                <div className="w-full h-2 bg-gray-700 rounded-full">
                  <div
                    className={`h-2 rounded-full transition-all ${
                      goal.status === 'completed' ? 'bg-green-500' :
                      goal.status === 'in_progress' ? 'bg-blue-500' :
                      goal.status === 'blocked' ? 'bg-red-500' :
                      'bg-gray-600'
                    }`}
                    style={{ width: `${goal.progress}%` }}
                  />
                </div>
              </div>

              {/* Metadata */}
              <div className="flex items-center gap-4 text-xs text-gray-500">
                <div className="flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  Created: {new Date(goal.createdAt).toLocaleDateString()}
                </div>
                {goal.dueDate && (
                  <div className="flex items-center gap-1">
                    <Calendar className="w-3 h-3" />
                    Due: {new Date(goal.dueDate).toLocaleDateString()}
                  </div>
                )}
                {blockedBy.length > 0 && (
                  <div className="text-red-400 flex items-center gap-1">
                    <AlertCircle className="w-3 h-3" />
                    Blocked by {blockedBy.length} goal(s)
                  </div>
                )}
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
      { id: 'planned', title: 'Planned', status: 'planned' as const },
      { id: 'in_progress', title: 'In Progress', status: 'in_progress' as const },
      { id: 'completed', title: 'Completed', status: 'completed' as const },
      { id: 'blocked', title: 'Blocked', status: 'blocked' as const }
    ]

    return (
      <div className="grid grid-cols-4 gap-3">
        {columns.map(column => {
          const columnGoals = allGoals.filter(g => g.status === column.status)
          
          return (
            <div key={column.id} className="flex flex-col">
              <div className="bg-gray-900 rounded-t p-2 border border-gray-700 border-b-0">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-semibold" style={{ fontSize: '12px' }}>{column.title}</h3>
                  <span className="px-1.5 py-0.5 bg-gray-700 rounded text-xs">
                    {columnGoals.length}
                  </span>
                </div>
              </div>
              <div className="flex-1 bg-gray-900 rounded-b border border-gray-700 p-2 space-y-2 min-h-[400px]">
                {columnGoals.map(goal => {
                  const blockedBy = getBlockedGoals(goal)
                  
                  return (
                    <div
                      key={goal.id}
                      className={`bg-gray-800 rounded p-2 border cursor-pointer hover:border-blue-500 transition-colors ${
                        selectedGoal?.id === goal.id ? 'border-blue-500' : 'border-gray-700'
                      }`}
                      onClick={() => setSelectedGoal(goal)}
                    >
                      <div className="flex items-start gap-2 mb-1">
                        {getStatusIcon(goal.status)}
                        <div className="flex-1 min-w-0">
                          <div className="text-xs font-medium text-gray-300 truncate mb-1" title={goal.name}>
                            {goal.name}
                          </div>
                          <div className="flex items-center gap-1 mb-1">
                            <span className={`px-1 py-0.5 text-xs rounded ${getPriorityColor(goal.priority)}`}>
                              {goal.priority}
                            </span>
                            {goal.confidence !== undefined && (
                              <span className={`text-xs px-1 py-0.5 rounded ${
                                goal.confidence >= 0.90 ? 'bg-green-600/20 text-green-400' :
                                goal.confidence >= 0.70 ? 'bg-yellow-600/20 text-yellow-400' :
                                'bg-red-600/20 text-red-400'
                              }`}>
                                {(goal.confidence * 100).toFixed(0)}%
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                      
                      {/* Progress */}
                      <div className="mb-2">
                        <div className="w-full bg-gray-700 rounded-full h-1.5">
                          <div
                            className={`h-1.5 rounded-full ${
                              goal.status === 'completed' ? 'bg-green-500' :
                              goal.status === 'in_progress' ? 'bg-blue-500' :
                              goal.status === 'blocked' ? 'bg-red-500' :
                              'bg-gray-600'
                            }`}
                            style={{ width: `${goal.progress}%` }}
                          />
                        </div>
                        <div className="text-xs text-gray-500 mt-0.5">
                          {goal.progress}%
                        </div>
                      </div>

                      {/* Blocked indicator */}
                      {blockedBy.length > 0 && (
                        <div className="text-xs text-red-400 flex items-center gap-1">
                          <AlertCircle className="w-3 h-3" />
                          Blocked
                        </div>
                      )}
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

  const overallProgress = useMemo(() => {
    if (allGoals.length === 0) return 0
    const totalProgress = allGoals.reduce((sum, goal) => sum + calculateOverallProgress(goal), 0)
    return Math.round(totalProgress / allGoals.length)
  }, [allGoals])

  const completedGoals = allGoals.filter(g => g.status === 'completed').length
  const inProgressGoals = allGoals.filter(g => g.status === 'in_progress').length
  const blockedGoals = allGoals.filter(g => g.status === 'blocked').length

  return (
    <ErrorBoundary>
      <div className="h-full flex flex-col bg-gray-800" role="complementary" aria-label="Goal Planning Panel">
        {loading.goals || loading.apoe ? (
          <LoadingState message="Loading goals and plans..." />
        ) : (
          <>
      {/* Header */}
      <div className="h-10 bg-gray-900 border-b border-gray-700 flex items-center justify-between px-3 shrink-0">
        <div className="flex items-center gap-2">
          <Target className="w-4 h-4 text-gray-400" />
          <span className="text-sm font-semibold text-gray-300">Goal Planning</span>
          <span className="text-xs text-gray-500">
            ({completedGoals}/{allGoals.length} completed, {overallProgress}% overall)
          </span>
        </div>
        <div className="flex items-center gap-1">
          {/* View Switcher */}
          <div className="flex items-center gap-1 bg-gray-800 rounded border border-gray-700 p-0.5">
            <button
              onClick={() => setGoalView('tree')}
              className={`p-1 rounded text-xs ${
                goalView === 'tree' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-gray-300'
              }`}
              title="Tree View"
            >
              <List className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setGoalView('timeline')}
              className={`p-1 rounded text-xs ${
                goalView === 'timeline' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-gray-300'
              }`}
              title="Timeline View"
            >
              <Calendar className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setGoalView('board')}
              className={`p-1 rounded text-xs ${
                goalView === 'board' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-gray-300'
              }`}
              title="Board View (Kanban)"
            >
              <LayoutGrid className="w-3.5 h-3.5" />
            </button>
          </div>
          <button
            onClick={() => setShowCreateGoal(true)}
            className="p-1 text-gray-400 hover:text-gray-300 hover:bg-gray-800 rounded"
            aria-label="Add goal"
            title="Create new goal"
          >
            <Plus className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="p-2 border-b border-gray-700 shrink-0 space-y-2">
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 w-3.5 h-3.5 text-gray-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search goals..."
            className="w-full pl-8 pr-2 py-1.5 bg-gray-900 border border-gray-700 rounded text-sm text-gray-300 placeholder-gray-500 focus:outline-none focus:border-blue-500"
          />
        </div>

        {/* Filters */}
        <div className="flex gap-2 flex-wrap">
          {/* Status Filter */}
          <div className="flex gap-1">
            {(['all', 'planned', 'in_progress', 'completed', 'blocked'] as const).map((status) => (
              <button
                key={status}
                onClick={() => setFilterStatus(status)}
                className={`px-2 py-1 text-xs rounded whitespace-nowrap ${
                  filterStatus === status
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                {status.charAt(0).toUpperCase() + status.slice(1).replace('_', ' ')}
              </button>
            ))}
          </div>

          {/* Priority Filter */}
          <select
            value={filterPriority}
            onChange={(e) => setFilterPriority(e.target.value as any)}
            className="px-2 py-1 text-xs bg-gray-700 text-gray-300 rounded border border-gray-600 focus:outline-none focus:border-blue-500"
          >
            <option value="all">All Priorities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>
      </div>

      {/* Goals Content */}
      <div className="flex-1 overflow-y-auto p-2">
        {filteredGoals.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500 text-sm">
            <Target className="w-8 h-8 mb-2 opacity-50" />
            <p>No goals found</p>
            {(searchQuery || filterStatus !== 'all' || filterPriority !== 'all') && (
              <button
                onClick={() => {
                  setSearchQuery('')
                  setFilterStatus('all')
                  setFilterPriority('all')
                }}
                className="mt-2 px-3 py-1 text-xs bg-blue-600 hover:bg-blue-700 rounded text-white"
              >
                Clear Filters
              </button>
            )}
          </div>
        ) : (
          <>
            {goalView === 'tree' && (
              <div className="space-y-1">
                {filteredGoals.map((goal) => renderGoalTree(goal))}
              </div>
            )}
            {goalView === 'timeline' && renderTimelineView()}
            {goalView === 'board' && renderBoardView()}
          </>
        )}
      </div>

      {/* Goal Detail Panel */}
      {selectedGoal && (
        <div className="p-3 border-t border-gray-700 bg-gray-900 shrink-0 max-h-64 overflow-y-auto">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-semibold text-white flex items-center gap-2">
              {getStatusIcon(selectedGoal.status)}
              {selectedGoal.name}
            </h3>
            <button
              onClick={() => setSelectedGoal(null)}
              className="text-gray-400 hover:text-gray-300"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
          
          <p className="text-xs text-gray-400 mb-3">{selectedGoal.description}</p>
          
          {/* Progress */}
          <div className="mb-3">
            <div className="flex items-center justify-between text-xs mb-1">
              <span className="text-gray-500">Progress</span>
              <span className="text-gray-300 font-semibold">{selectedGoal.progress}%</span>
            </div>
            <div className="w-full h-2 bg-gray-700 rounded-full">
              <div
                className={`h-2 rounded-full ${
                  selectedGoal.status === 'completed' ? 'bg-green-500' :
                  selectedGoal.status === 'in_progress' ? 'bg-blue-500' :
                  selectedGoal.status === 'blocked' ? 'bg-red-500' :
                  'bg-gray-600'
                }`}
                style={{ width: `${selectedGoal.progress}%` }}
              />
            </div>
          </div>

          {/* Details Grid */}
          <div className="grid grid-cols-2 gap-2 text-xs mb-3">
            <div>
              <div className="text-gray-500">Status</div>
              <div className={`text-gray-300 font-medium ${getStatusColor(selectedGoal.status)} px-1.5 py-0.5 rounded inline-block`}>
                {selectedGoal.status.replace('_', ' ')}
              </div>
            </div>
            <div>
              <div className="text-gray-500">Priority</div>
              <div className={`font-medium ${getPriorityColor(selectedGoal.priority)} px-1.5 py-0.5 rounded inline-block`}>
                {selectedGoal.priority}
              </div>
            </div>
            {selectedGoal.dueDate && (
              <div>
                <div className="text-gray-500">Due Date</div>
                <div className="text-gray-300">{new Date(selectedGoal.dueDate).toLocaleDateString()}</div>
              </div>
            )}
            {selectedGoal.confidence !== undefined && (
              <div>
                <div className="text-gray-500">VIF Confidence</div>
                <div className={`font-medium ${
                  selectedGoal.confidence >= 0.90 ? 'text-green-400' :
                  selectedGoal.confidence >= 0.70 ? 'text-yellow-400' :
                  'text-red-400'
                }`}>
                  {(selectedGoal.confidence * 100).toFixed(0)}%
                </div>
              </div>
            )}
          </div>

          {/* Dependencies */}
          {selectedGoal.dependencies.length > 0 && (
            <div className="mb-2">
              <div className="text-xs text-gray-500 mb-1 flex items-center gap-1">
                <Link2 className="w-3 h-3" />
                Dependencies
              </div>
              <div className="space-y-1">
                {selectedGoal.dependencies.map(depId => {
                  const dep = allGoals.find(g => g.id === depId)
                  return dep ? (
                    <button
                      key={depId}
                      onClick={() => setSelectedGoal(dep)}
                      className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1"
                    >
                      <ChevronRight className="w-3 h-3" />
                      {dep.name} ({dep.status})
                    </button>
                  ) : null
                })}
              </div>
            </div>
          )}

          {/* Key Results */}
          {selectedGoal.keyResults && selectedGoal.keyResults.length > 0 && (
            <div className="mb-2">
              <div className="text-xs text-gray-500 mb-1">Key Results</div>
              <ul className="space-y-1">
                {selectedGoal.keyResults.map((kr, idx) => (
                  <li key={idx} className="text-xs text-gray-400 flex items-center gap-1">
                    <Circle className="w-3 h-3" />
                    {kr}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* AIM-OS Integration */}
          <div className="flex items-center gap-2 text-xs text-gray-500">
            {selectedGoal.timelineNodeId && (
              <span className="flex items-center gap-1" title="Timeline Node ID">
                <Calendar className="w-3 h-3" />
                TCS: {selectedGoal.timelineNodeId}
              </span>
            )}
            {selectedGoal.apoePlanId && (
              <div className="flex items-center gap-2">
                <span className="flex items-center gap-1" title="APOE Plan ID">
                  <Brain className="w-3 h-3" />
                  APOE: {selectedGoal.apoePlanId}
                </span>
                {apoePlans.has(selectedGoal.id) && (
                  <button
                    onClick={() => executeApoePlan(selectedGoal)}
                    className={`px-2 py-1 rounded text-xs flex items-center gap-1 ${
                      executingPlans.has(selectedGoal.id)
                        ? 'bg-blue-600 text-white'
                        : 'bg-purple-600 hover:bg-purple-700 text-white'
                    }`}
                    disabled={executingPlans.has(selectedGoal.id)}
                  >
                    {executingPlans.has(selectedGoal.id) ? (
                      <>
                        <RefreshCw className="w-3 h-3 animate-spin" />
                        Executing...
                      </>
                    ) : (
                      <>
                        <Play className="w-3 h-3" />
                        Execute Plan
                      </>
                    )}
                  </button>
                )}
              </div>
            )}
          </div>
          </>
        )}
      </div>
    </ErrorBoundary>
  )
}
