/**
 * Planning Agent Context
 * State management for the AI Planning/Strategy Agent
 */

import React, { createContext, useContext, useReducer, ReactNode } from 'react'
import { ChatMessage } from '../components/chats/ChatMessage'

export interface Goal {
  id: string
  title: string
  description: string
  priority: 'low' | 'medium' | 'high' | 'critical'
  status: 'planned' | 'in_progress' | 'completed' | 'blocked' | 'cancelled'
  dueDate?: Date
  dependencies: string[]
  progress: number // 0-100
}

export interface Milestone {
  id: string
  title: string
  description: string
  dueDate: Date
  status: 'upcoming' | 'in_progress' | 'completed' | 'overdue'
  goals: string[] // Goal IDs
}

export interface ArchitectureState {
  patterns: string[]
  technologies: string[]
  decisions: {
    id: string
    decision: string
    rationale: string
    alternatives: string[]
    impact: 'low' | 'medium' | 'high'
    date: Date
  }[]
  constraints: string[]
  risks: {
    id: string
    risk: string
    probability: 'low' | 'medium' | 'high'
    impact: 'low' | 'medium' | 'high'
    mitigation: string
  }[]
}

export interface Sprint {
  id: string
  name: string
  startDate: Date
  endDate: Date
  goals: string[] // Goal IDs
  status: 'planning' | 'active' | 'completed' | 'cancelled'
  velocity: number
  capacity: number
}

export interface PlanningAgentState {
  messages: ChatMessage[]
  projectGoals: Goal[]
  milestones: Milestone[]
  architecture: ArchitectureState
  currentSprint?: Sprint
  isTyping: boolean
  lastActivity: Date
  context: {
    projectName: string
    teamSize: number
    budget?: number
    timeline: {
      startDate: Date
      endDate?: Date
      phases: string[]
    }
    stakeholders: string[]
    requirements: string[]
  }
}

export type PlanningAgentAction =
  | { type: 'ADD_MESSAGE'; payload: ChatMessage }
  | { type: 'ADD_GOAL'; payload: Goal }
  | { type: 'UPDATE_GOAL'; payload: { id: string; updates: Partial<Goal> } }
  | { type: 'REMOVE_GOAL'; payload: string }
  | { type: 'ADD_MILESTONE'; payload: Milestone }
  | { type: 'UPDATE_MILESTONE'; payload: { id: string; updates: Partial<Milestone> } }
  | { type: 'REMOVE_MILESTONE'; payload: string }
  | { type: 'UPDATE_ARCHITECTURE'; payload: Partial<ArchitectureState> }
  | { type: 'ADD_ARCHITECTURE_DECISION'; payload: ArchitectureState['decisions'][0] }
  | { type: 'ADD_RISK'; payload: ArchitectureState['risks'][0] }
  | { type: 'SET_CURRENT_SPRINT'; payload: Sprint }
  | { type: 'UPDATE_SPRINT'; payload: { id: string; updates: Partial<Sprint> } }
  | { type: 'SET_TYPING'; payload: boolean }
  | { type: 'UPDATE_LAST_ACTIVITY' }
  | { type: 'UPDATE_CONTEXT'; payload: Partial<PlanningAgentState['context']> }
  | { type: 'CLEAR_MESSAGES' }
  | { type: 'RESET_STATE' }

const initialState: PlanningAgentState = {
  messages: [],
  projectGoals: [],
  milestones: [],
  architecture: {
    patterns: [],
    technologies: [],
    decisions: [],
    constraints: [],
    risks: []
  },
  isTyping: false,
  lastActivity: new Date(),
  context: {
    projectName: '',
    teamSize: 1,
    timeline: {
      startDate: new Date(),
      phases: []
    },
    stakeholders: [],
    requirements: []
  }
}

function planningAgentReducer(state: PlanningAgentState, action: PlanningAgentAction): PlanningAgentState {
  switch (action.type) {
    case 'ADD_MESSAGE':
      return {
        ...state,
        messages: [...state.messages, action.payload],
        lastActivity: new Date()
      }

    case 'ADD_GOAL':
      return {
        ...state,
        projectGoals: [...state.projectGoals, action.payload],
        lastActivity: new Date()
      }

    case 'UPDATE_GOAL':
      return {
        ...state,
        projectGoals: state.projectGoals.map(goal =>
          goal.id === action.payload.id
            ? { ...goal, ...action.payload.updates }
            : goal
        ),
        lastActivity: new Date()
      }

    case 'REMOVE_GOAL':
      return {
        ...state,
        projectGoals: state.projectGoals.filter(goal => goal.id !== action.payload),
        lastActivity: new Date()
      }

    case 'ADD_MILESTONE':
      return {
        ...state,
        milestones: [...state.milestones, action.payload],
        lastActivity: new Date()
      }

    case 'UPDATE_MILESTONE':
      return {
        ...state,
        milestones: state.milestones.map(milestone =>
          milestone.id === action.payload.id
            ? { ...milestone, ...action.payload.updates }
            : milestone
        ),
        lastActivity: new Date()
      }

    case 'REMOVE_MILESTONE':
      return {
        ...state,
        milestones: state.milestones.filter(milestone => milestone.id !== action.payload),
        lastActivity: new Date()
      }

    case 'UPDATE_ARCHITECTURE':
      return {
        ...state,
        architecture: {
          ...state.architecture,
          ...action.payload
        },
        lastActivity: new Date()
      }

    case 'ADD_ARCHITECTURE_DECISION':
      return {
        ...state,
        architecture: {
          ...state.architecture,
          decisions: [...state.architecture.decisions, action.payload]
        },
        lastActivity: new Date()
      }

    case 'ADD_RISK':
      return {
        ...state,
        architecture: {
          ...state.architecture,
          risks: [...state.architecture.risks, action.payload]
        },
        lastActivity: new Date()
      }

    case 'SET_CURRENT_SPRINT':
      return {
        ...state,
        currentSprint: action.payload,
        lastActivity: new Date()
      }

    case 'UPDATE_SPRINT':
      return {
        ...state,
        currentSprint: state.currentSprint?.id === action.payload.id
          ? { ...state.currentSprint, ...action.payload.updates }
          : state.currentSprint,
        lastActivity: new Date()
      }

    case 'SET_TYPING':
      return {
        ...state,
        isTyping: action.payload
      }

    case 'UPDATE_LAST_ACTIVITY':
      return {
        ...state,
        lastActivity: new Date()
      }

    case 'UPDATE_CONTEXT':
      return {
        ...state,
        context: {
          ...state.context,
          ...action.payload
        },
        lastActivity: new Date()
      }

    case 'CLEAR_MESSAGES':
      return {
        ...state,
        messages: [],
        lastActivity: new Date()
      }

    case 'RESET_STATE':
      return {
        ...initialState,
        lastActivity: new Date()
      }

    default:
      return state
  }
}

interface PlanningAgentContextType {
  state: PlanningAgentState
  dispatch: React.Dispatch<PlanningAgentAction>
  // Helper functions
  addMessage: (message: Omit<ChatMessage, 'id' | 'timestamp'>) => void
  addGoal: (goal: Omit<Goal, 'id'>) => void
  updateGoal: (id: string, updates: Partial<Goal>) => void
  removeGoal: (id: string) => void
  addMilestone: (milestone: Omit<Milestone, 'id'>) => void
  updateMilestone: (id: string, updates: Partial<Milestone>) => void
  removeMilestone: (id: string) => void
  updateArchitecture: (updates: Partial<ArchitectureState>) => void
  addArchitectureDecision: (decision: Omit<ArchitectureState['decisions'][0], 'id'>) => void
  addRisk: (risk: Omit<ArchitectureState['risks'][0], 'id'>) => void
  setCurrentSprint: (sprint: Sprint) => void
  updateSprint: (id: string, updates: Partial<Sprint>) => void
  setTyping: (isTyping: boolean) => void
  updateContext: (context: Partial<PlanningAgentState['context']>) => void
  clearMessages: () => void
  resetState: () => void
  // Computed values
  getActiveGoals: () => Goal[]
  getCompletedGoals: () => Goal[]
  getUpcomingMilestones: () => Milestone[]
  getOverdueMilestones: () => Milestone[]
  getHighPriorityGoals: () => Goal[]
  getProjectProgress: () => number
}

const PlanningAgentContext = createContext<PlanningAgentContextType | undefined>(undefined)

interface PlanningAgentProviderProps {
  children: ReactNode
}

export const PlanningAgentProvider: React.FC<PlanningAgentProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(planningAgentReducer, initialState)

  // Helper functions
  const addMessage = (message: Omit<ChatMessage, 'id' | 'timestamp'>) => {
    const fullMessage: ChatMessage = {
      ...message,
      id: `planning-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date()
    }
    dispatch({ type: 'ADD_MESSAGE', payload: fullMessage })
  }

  const addGoal = (goal: Omit<Goal, 'id'>) => {
    const fullGoal: Goal = {
      ...goal,
      id: `goal-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    }
    dispatch({ type: 'ADD_GOAL', payload: fullGoal })
  }

  const updateGoal = (id: string, updates: Partial<Goal>) => {
    dispatch({ type: 'UPDATE_GOAL', payload: { id, updates } })
  }

  const removeGoal = (id: string) => {
    dispatch({ type: 'REMOVE_GOAL', payload: id })
  }

  const addMilestone = (milestone: Omit<Milestone, 'id'>) => {
    const fullMilestone: Milestone = {
      ...milestone,
      id: `milestone-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    }
    dispatch({ type: 'ADD_MILESTONE', payload: fullMilestone })
  }

  const updateMilestone = (id: string, updates: Partial<Milestone>) => {
    dispatch({ type: 'UPDATE_MILESTONE', payload: { id, updates } })
  }

  const removeMilestone = (id: string) => {
    dispatch({ type: 'REMOVE_MILESTONE', payload: id })
  }

  const updateArchitecture = (updates: Partial<ArchitectureState>) => {
    dispatch({ type: 'UPDATE_ARCHITECTURE', payload: updates })
  }

  const addArchitectureDecision = (decision: Omit<ArchitectureState['decisions'][0], 'id'>) => {
    const fullDecision: ArchitectureState['decisions'][0] = {
      ...decision,
      id: `decision-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    }
    dispatch({ type: 'ADD_ARCHITECTURE_DECISION', payload: fullDecision })
  }

  const addRisk = (risk: Omit<ArchitectureState['risks'][0], 'id'>) => {
    const fullRisk: ArchitectureState['risks'][0] = {
      ...risk,
      id: `risk-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    }
    dispatch({ type: 'ADD_RISK', payload: fullRisk })
  }

  const setCurrentSprint = (sprint: Sprint) => {
    dispatch({ type: 'SET_CURRENT_SPRINT', payload: sprint })
  }

  const updateSprint = (id: string, updates: Partial<Sprint>) => {
    dispatch({ type: 'UPDATE_SPRINT', payload: { id, updates } })
  }

  const setTyping = (isTyping: boolean) => {
    dispatch({ type: 'SET_TYPING', payload: isTyping })
  }

  const updateContext = (context: Partial<PlanningAgentState['context']>) => {
    dispatch({ type: 'UPDATE_CONTEXT', payload: context })
  }

  const clearMessages = () => {
    dispatch({ type: 'CLEAR_MESSAGES' })
  }

  const resetState = () => {
    dispatch({ type: 'RESET_STATE' })
  }

  // Computed values
  const getActiveGoals = (): Goal[] => {
    return state.projectGoals.filter(goal => goal.status === 'in_progress')
  }

  const getCompletedGoals = (): Goal[] => {
    return state.projectGoals.filter(goal => goal.status === 'completed')
  }

  const getUpcomingMilestones = (): Milestone[] => {
    const now = new Date()
    return state.milestones
      .filter(milestone => milestone.dueDate > now && milestone.status === 'upcoming')
      .sort((a, b) => a.dueDate.getTime() - b.dueDate.getTime())
  }

  const getOverdueMilestones = (): Milestone[] => {
    const now = new Date()
    return state.milestones
      .filter(milestone => milestone.dueDate < now && milestone.status !== 'completed')
      .sort((a, b) => a.dueDate.getTime() - b.dueDate.getTime())
  }

  const getHighPriorityGoals = (): Goal[] => {
    return state.projectGoals
      .filter(goal => goal.priority === 'high' || goal.priority === 'critical')
      .sort((a, b) => {
        const priorityOrder = { critical: 4, high: 3, medium: 2, low: 1 }
        return priorityOrder[b.priority] - priorityOrder[a.priority]
      })
  }

  const getProjectProgress = (): number => {
    if (state.projectGoals.length === 0) return 0
    const totalProgress = state.projectGoals.reduce((sum, goal) => sum + goal.progress, 0)
    return Math.round(totalProgress / state.projectGoals.length)
  }

  const value: PlanningAgentContextType = {
    state,
    dispatch,
    addMessage,
    addGoal,
    updateGoal,
    removeGoal,
    addMilestone,
    updateMilestone,
    removeMilestone,
    updateArchitecture,
    addArchitectureDecision,
    addRisk,
    setCurrentSprint,
    updateSprint,
    setTyping,
    updateContext,
    clearMessages,
    resetState,
    getActiveGoals,
    getCompletedGoals,
    getUpcomingMilestones,
    getOverdueMilestones,
    getHighPriorityGoals,
    getProjectProgress
  }

  return (
    <PlanningAgentContext.Provider value={value}>
      {children}
    </PlanningAgentContext.Provider>
  )
}

export const usePlanningAgent = (): PlanningAgentContextType => {
  const context = useContext(PlanningAgentContext)
  if (context === undefined) {
    throw new Error('usePlanningAgent must be used within a PlanningAgentProvider')
  }
  return context
}
