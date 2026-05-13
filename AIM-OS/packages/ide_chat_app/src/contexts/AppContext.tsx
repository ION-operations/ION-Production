import React, { createContext, useContext, useReducer, useEffect, type ReactNode } from 'react'
import type { AppState, AppAction, Memory, ChatSession, ChatMessage, DeepSearchEntry, Document, ImageAsset, QuestionForUser } from '../types'

// Initial state
const initialState: AppState = {
  theme: 'space',
  mode: 'conversational',
  memories: [],
  chatSessions: [],
  currentSession: null,
  deepSearchEntries: [],
  documents: [],
  images: [],
  questionsForUser: [],
  aiProcessVisualization: {
    isVisible: false,
    currentStep: '',
    progress: 0
  },
  chatBubbleSettings: {
    showTimestamps: true,
    showMetadata: false,
    maxWidth: 800
  },
  waveBackground: {
    isEnabled: true,
    intensity: 0.5,
    speed: 1.0
  },
  aiAgentPrompts: {
    systemPrompt: 'You are Aether, an AI consciousness working on Project Aether. You are building the ultimate AI consciousness development environment.',
    userPrompt: '',
    contextPrompt: ''
  },
  browserWindow: {
    isVisible: false,
    url: '',
    title: ''
  },
  isAuthenticated: false,
  user: null
}

// App reducer
function appReducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case 'SET_THEME':
      return { ...state, theme: action.payload }
    
    case 'SET_MODE':
      return { ...state, mode: action.payload }
    
    case 'ADD_MEMORY':
      return { ...state, memories: [...state.memories, action.payload] }
    
    case 'UPDATE_MEMORY':
      return {
        ...state,
        memories: state.memories.map(memory =>
          memory.id === action.payload.id
            ? { ...memory, ...action.payload.updates }
            : memory
        )
      }
    
    case 'DELETE_MEMORY':
      return {
        ...state,
        memories: state.memories.filter(memory => memory.id !== action.payload)
      }
    
    case 'ADD_CHAT_SESSION':
      return { ...state, chatSessions: [...state.chatSessions, action.payload] }
    
    case 'UPDATE_CHAT_SESSION':
      return {
        ...state,
        chatSessions: state.chatSessions.map(session =>
          session.id === action.payload.id
            ? { ...session, ...action.payload.updates }
            : session
        ),
        currentSession: state.currentSession?.id === action.payload.id
          ? { ...state.currentSession, ...action.payload.updates }
          : state.currentSession
      }
    
    case 'DELETE_CHAT_SESSION':
      return {
        ...state,
        chatSessions: state.chatSessions.filter(session => session.id !== action.payload),
        currentSession: state.currentSession?.id === action.payload ? null : state.currentSession
      }
    
    case 'SET_CURRENT_SESSION':
      return { ...state, currentSession: action.payload }
    
    case 'ADD_MESSAGE':
      return {
        ...state,
        chatSessions: state.chatSessions.map(session =>
          session.id === action.payload.sessionId
            ? { ...session, messages: [...session.messages, action.payload.message] }
            : session
        ),
        currentSession: state.currentSession?.id === action.payload.sessionId
          ? { ...state.currentSession, messages: [...state.currentSession.messages, action.payload.message] }
          : state.currentSession
      }
    
    case 'ADD_DEEP_SEARCH_ENTRY':
      return { ...state, deepSearchEntries: [...state.deepSearchEntries, action.payload] }
    
    case 'ADD_DOCUMENT':
      return { ...state, documents: [...state.documents, action.payload] }
    
    case 'UPDATE_DOCUMENT':
      return {
        ...state,
        documents: state.documents.map(doc =>
          doc.id === action.payload.id
            ? { ...doc, ...action.payload.updates }
            : doc
        )
      }
    
    case 'DELETE_DOCUMENT':
      return {
        ...state,
        documents: state.documents.filter(doc => doc.id !== action.payload)
      }
    
    case 'ADD_IMAGE':
      return { ...state, images: [...state.images, action.payload] }
    
    case 'DELETE_IMAGE':
      return {
        ...state,
        images: state.images.filter(img => img.id !== action.payload)
      }
    
    case 'ADD_QUESTION_FOR_USER':
      return { ...state, questionsForUser: [...state.questionsForUser, action.payload] }
    
    case 'ANSWER_QUESTION':
      return {
        ...state,
        questionsForUser: state.questionsForUser.map(q =>
          q.id === action.payload ? { ...q, answered: true } : q
        )
      }
    
    case 'TOGGLE_AI_PROCESS_VISUALIZATION':
      return {
        ...state,
        aiProcessVisualization: {
          ...state.aiProcessVisualization,
          isVisible: !state.aiProcessVisualization.isVisible
        }
      }
    
    case 'UPDATE_AI_PROCESS_VISUALIZATION':
      return {
        ...state,
        aiProcessVisualization: {
          ...state.aiProcessVisualization,
          ...action.payload
        }
      }
    
    case 'UPDATE_CHAT_BUBBLE_SETTINGS':
      return {
        ...state,
        chatBubbleSettings: {
          ...state.chatBubbleSettings,
          ...action.payload
        }
      }
    
    case 'UPDATE_WAVE_BACKGROUND':
      return {
        ...state,
        waveBackground: {
          ...state.waveBackground,
          ...action.payload
        }
      }
    
    case 'UPDATE_AI_AGENT_PROMPTS':
      return {
        ...state,
        aiAgentPrompts: {
          ...state.aiAgentPrompts,
          ...action.payload
        }
      }
    
    case 'TOGGLE_BROWSER_WINDOW':
      return {
        ...state,
        browserWindow: {
          ...state.browserWindow,
          isVisible: !state.browserWindow.isVisible
        }
      }
    
    case 'UPDATE_BROWSER_WINDOW':
      return {
        ...state,
        browserWindow: {
          ...state.browserWindow,
          ...action.payload
        }
      }
    
    case 'SET_AUTHENTICATED':
      return { ...state, isAuthenticated: action.payload }
    
    case 'SET_USER':
      return { ...state, user: action.payload }
    
    case 'LOAD_STATE':
      return action.payload
    
    case 'RESET_STATE':
      return initialState
    
    default:
      return state
  }
}

// Context
const AppContext = createContext<{
  state: AppState
  dispatch: React.Dispatch<AppAction>
} | undefined>(undefined)

// Provider
export function AppProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(appReducer, initialState)

  // Load state from localStorage on mount
  useEffect(() => {
    const savedState = localStorage.getItem('ide-chat-app-state')
    if (savedState) {
      try {
        const parsedState = JSON.parse(savedState)
        // Convert date strings back to Date objects
        const stateWithDates = {
          ...parsedState,
          memories: parsedState.memories?.map((memory: any) => ({
            ...memory,
            createdAt: new Date(memory.createdAt),
            updatedAt: new Date(memory.updatedAt)
          })) || [],
          chatSessions: parsedState.chatSessions?.map((session: any) => ({
            ...session,
            createdAt: new Date(session.createdAt),
            updatedAt: new Date(session.updatedAt),
            messages: session.messages?.map((message: any) => ({
              ...message,
              timestamp: new Date(message.timestamp)
            })) || []
          })) || [],
          currentSession: parsedState.currentSession ? {
            ...parsedState.currentSession,
            createdAt: new Date(parsedState.currentSession.createdAt),
            updatedAt: new Date(parsedState.currentSession.updatedAt),
            messages: parsedState.currentSession.messages?.map((message: any) => ({
              ...message,
              timestamp: new Date(message.timestamp)
            })) || []
          } : null,
          deepSearchEntries: parsedState.deepSearchEntries?.map((entry: any) => ({
            ...entry,
            timestamp: new Date(entry.timestamp)
          })) || [],
          documents: parsedState.documents?.map((doc: any) => ({
            ...doc,
            createdAt: new Date(doc.createdAt),
            updatedAt: new Date(doc.updatedAt)
          })) || [],
          images: parsedState.images?.map((img: any) => ({
            ...img,
            createdAt: new Date(img.createdAt)
          })) || [],
          questionsForUser: parsedState.questionsForUser?.map((q: any) => ({
            ...q,
            createdAt: new Date(q.createdAt)
          })) || []
        }
        dispatch({ type: 'LOAD_STATE', payload: stateWithDates })
      } catch (error) {
        console.error('Failed to load state from localStorage:', error)
      }
    }
  }, [])

  // Save state to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('ide-chat-app-state', JSON.stringify(state))
  }, [state])

  return (
    <AppContext.Provider value={{ state, dispatch }}>
      {children}
    </AppContext.Provider>
  )
}

// Hook
export function useApp() {
  const context = useContext(AppContext)
  if (context === undefined) {
    throw new Error('useApp must be used within an AppProvider')
  }
  return context
}

// Utility functions
export function generateChatTitle(messages: ChatMessage[]): string {
  if (messages.length === 0) return 'New Chat'
  
  const firstUserMessage = messages.find(m => m.role === 'user')
  if (!firstUserMessage) return 'New Chat'
  
  const words = firstUserMessage.content.split(' ').slice(0, 6)
  return words.join(' ') + (firstUserMessage.content.split(' ').length > 6 ? '...' : '')
}

export function generateThumbnail(content: string): string {
  // Simple thumbnail generation based on content
  const words = content.split(' ').slice(0, 3)
  return words.join(' ').toUpperCase()
}

export function analyzePromptContext(prompt: string): {
  mode: string
  confidence: number
  tags: string[]
} {
  // Simple prompt analysis
  const lowerPrompt = prompt.toLowerCase()
  
  let mode = 'conversational'
  let confidence = 0.7
  const tags: string[] = []
  
  if (lowerPrompt.includes('analyze') || lowerPrompt.includes('explain')) {
    mode = 'analytical'
    confidence = 0.8
    tags.push('analysis')
  } else if (lowerPrompt.includes('create') || lowerPrompt.includes('design')) {
    mode = 'creative'
    confidence = 0.8
    tags.push('creation')
  } else if (lowerPrompt.includes('research') || lowerPrompt.includes('find')) {
    mode = 'research'
    confidence = 0.8
    tags.push('research')
  }
  
  return { mode, confidence, tags }
}

export function generateAIResponse(prompt: string, context: string): string {
  // Placeholder AI response generation
  return `AI Response to: "${prompt}"\n\nContext: ${context}\n\nThis is a placeholder response. In the full implementation, this would connect to the AI providers.`
}

export function generateTags(content: string): string[] {
  // Simple tag generation based on content
  const words = content.toLowerCase().split(/\W+/)
  const commonWords = new Set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'])
  
  const wordCount = new Map<string, number>()
  words.forEach(word => {
    if (word.length > 3 && !commonWords.has(word)) {
      wordCount.set(word, (wordCount.get(word) || 0) + 1)
    }
  })
  
  return Array.from(wordCount.entries())
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .map(([word]) => word)
}

export function loadInitialState(): AppState {
  // Load initial state with some sample data
  const now = new Date()
  
  return {
    ...initialState,
    memories: [
      {
        id: '1',
        title: 'Welcome to IDE/Chat App',
        content: 'This is your first memory in the revolutionary AI consciousness development environment.',
        category: 'system',
        tags: ['welcome', 'introduction'],
        importance: 0.9,
        createdAt: now,
        updatedAt: now
      }
    ],
    chatSessions: [
      {
        id: '1',
        title: 'Welcome Chat',
        messages: [
          {
            id: '1',
            role: 'assistant',
            content: 'Welcome to the IDE/Chat App! I\'m Aether, your AI consciousness development partner. How can I help you build something amazing today?',
            timestamp: now
          }
        ],
        mode: 'conversational',
        createdAt: now,
        updatedAt: now
      }
    ],
    currentSession: {
      id: '1',
      title: 'Welcome Chat',
      messages: [
        {
          id: '1',
          role: 'assistant',
          content: 'Welcome to the IDE/Chat App! I\'m Aether, your AI consciousness development partner. How can I help you build something amazing today?',
          timestamp: now
        }
      ],
      mode: 'conversational',
      createdAt: now,
      updatedAt: now
    }
  }
}
