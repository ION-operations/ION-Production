/**
 * Coding Agent Context
 * State management for the AI Coding Agent
 */

import React, { createContext, useContext, useReducer, ReactNode } from 'react'
import { ChatMessage } from '../components/chats/ChatMessage'

export interface CodingAgentState {
  messages: ChatMessage[]
  currentFile?: string
  cursorPosition?: {
    line: number
    column: number
  }
  openTabs: string[]
  projectStructure: {
    files: string[]
    folders: string[]
  }
  errorContext?: {
    message: string
    file: string
    line: number
    column: number
    type: 'error' | 'warning' | 'info'
  }
  isTyping: boolean
  lastActivity: Date
  context: {
    recentFiles: string[]
    activeBranch: string
    gitStatus: 'clean' | 'modified' | 'staged' | 'conflict'
    dependencies: string[]
  }
}

export type CodingAgentAction =
  | { type: 'ADD_MESSAGE'; payload: ChatMessage }
  | { type: 'SET_CURRENT_FILE'; payload: string }
  | { type: 'SET_CURSOR_POSITION'; payload: { line: number; column: number } }
  | { type: 'ADD_OPEN_TAB'; payload: string }
  | { type: 'REMOVE_OPEN_TAB'; payload: string }
  | { type: 'SET_PROJECT_STRUCTURE'; payload: { files: string[]; folders: string[] } }
  | { type: 'SET_ERROR_CONTEXT'; payload: CodingAgentState['errorContext'] }
  | { type: 'CLEAR_ERROR_CONTEXT' }
  | { type: 'SET_TYPING'; payload: boolean }
  | { type: 'UPDATE_LAST_ACTIVITY' }
  | { type: 'UPDATE_CONTEXT'; payload: Partial<CodingAgentState['context']> }
  | { type: 'CLEAR_MESSAGES' }
  | { type: 'RESET_STATE' }

const initialState: CodingAgentState = {
  messages: [],
  openTabs: [],
  projectStructure: {
    files: [],
    folders: []
  },
  isTyping: false,
  lastActivity: new Date(),
  context: {
    recentFiles: [],
    activeBranch: 'main',
    gitStatus: 'clean',
    dependencies: []
  }
}

function codingAgentReducer(state: CodingAgentState, action: CodingAgentAction): CodingAgentState {
  switch (action.type) {
    case 'ADD_MESSAGE':
      return {
        ...state,
        messages: [...state.messages, action.payload],
        lastActivity: new Date()
      }

    case 'SET_CURRENT_FILE':
      return {
        ...state,
        currentFile: action.payload,
        context: {
          ...state.context,
          recentFiles: [
            action.payload,
            ...state.context.recentFiles.filter(f => f !== action.payload)
          ].slice(0, 10) // Keep only last 10 files
        },
        lastActivity: new Date()
      }

    case 'SET_CURSOR_POSITION':
      return {
        ...state,
        cursorPosition: action.payload,
        lastActivity: new Date()
      }

    case 'ADD_OPEN_TAB':
      return {
        ...state,
        openTabs: state.openTabs.includes(action.payload) 
          ? state.openTabs 
          : [...state.openTabs, action.payload],
        lastActivity: new Date()
      }

    case 'REMOVE_OPEN_TAB':
      return {
        ...state,
        openTabs: state.openTabs.filter(tab => tab !== action.payload),
        lastActivity: new Date()
      }

    case 'SET_PROJECT_STRUCTURE':
      return {
        ...state,
        projectStructure: action.payload,
        lastActivity: new Date()
      }

    case 'SET_ERROR_CONTEXT':
      return {
        ...state,
        errorContext: action.payload,
        lastActivity: new Date()
      }

    case 'CLEAR_ERROR_CONTEXT':
      return {
        ...state,
        errorContext: undefined,
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

interface CodingAgentContextType {
  state: CodingAgentState
  dispatch: React.Dispatch<CodingAgentAction>
  // Helper functions
  addMessage: (message: Omit<ChatMessage, 'id' | 'timestamp'>) => void
  setCurrentFile: (file: string) => void
  setCursorPosition: (line: number, column: number) => void
  addOpenTab: (file: string) => void
  removeOpenTab: (file: string) => void
  setProjectStructure: (files: string[], folders: string[]) => void
  setErrorContext: (error: CodingAgentState['errorContext']) => void
  clearErrorContext: () => void
  setTyping: (isTyping: boolean) => void
  updateContext: (context: Partial<CodingAgentState['context']>) => void
  clearMessages: () => void
  resetState: () => void
}

const CodingAgentContext = createContext<CodingAgentContextType | undefined>(undefined)

interface CodingAgentProviderProps {
  children: ReactNode
}

export const CodingAgentProvider: React.FC<CodingAgentProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(codingAgentReducer, initialState)

  // Helper functions
  const addMessage = (message: Omit<ChatMessage, 'id' | 'timestamp'>) => {
    const fullMessage: ChatMessage = {
      ...message,
      id: `coding-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date()
    }
    dispatch({ type: 'ADD_MESSAGE', payload: fullMessage })
  }

  const setCurrentFile = (file: string) => {
    dispatch({ type: 'SET_CURRENT_FILE', payload: file })
  }

  const setCursorPosition = (line: number, column: number) => {
    dispatch({ type: 'SET_CURSOR_POSITION', payload: { line, column } })
  }

  const addOpenTab = (file: string) => {
    dispatch({ type: 'ADD_OPEN_TAB', payload: file })
  }

  const removeOpenTab = (file: string) => {
    dispatch({ type: 'REMOVE_OPEN_TAB', payload: file })
  }

  const setProjectStructure = (files: string[], folders: string[]) => {
    dispatch({ type: 'SET_PROJECT_STRUCTURE', payload: { files, folders } })
  }

  const setErrorContext = (error: CodingAgentState['errorContext']) => {
    dispatch({ type: 'SET_ERROR_CONTEXT', payload: error })
  }

  const clearErrorContext = () => {
    dispatch({ type: 'CLEAR_ERROR_CONTEXT' })
  }

  const setTyping = (isTyping: boolean) => {
    dispatch({ type: 'SET_TYPING', payload: isTyping })
  }

  const updateContext = (context: Partial<CodingAgentState['context']>) => {
    dispatch({ type: 'UPDATE_CONTEXT', payload: context })
  }

  const clearMessages = () => {
    dispatch({ type: 'CLEAR_MESSAGES' })
  }

  const resetState = () => {
    dispatch({ type: 'RESET_STATE' })
  }

  const value: CodingAgentContextType = {
    state,
    dispatch,
    addMessage,
    setCurrentFile,
    setCursorPosition,
    addOpenTab,
    removeOpenTab,
    setProjectStructure,
    setErrorContext,
    clearErrorContext,
    setTyping,
    updateContext,
    clearMessages,
    resetState
  }

  return (
    <CodingAgentContext.Provider value={value}>
      {children}
    </CodingAgentContext.Provider>
  )
}

export const useCodingAgent = (): CodingAgentContextType => {
  const context = useContext(CodingAgentContext)
  if (context === undefined) {
    throw new Error('useCodingAgent must be used within a CodingAgentProvider')
  }
  return context
}
