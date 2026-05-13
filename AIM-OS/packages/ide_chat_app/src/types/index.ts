// Core types for the IDE/Chat App

export type Theme = 'space' | 'cyberpunk' | 'matrix' | 'aurora' | 'blade-runner' | 'retro' | 'mist'

export type InteractionMode = 'conversational' | 'analytical' | 'creative' | 'collaborative' | 'research' | 'art' | 'math' | 'mystic'

export interface Memory {
  id: string
  title: string
  content: string
  category: string
  tags: string[]
  importance: number
  createdAt: Date
  updatedAt: Date
}

export interface ChatSession {
  id: string
  title: string
  messages: ChatMessage[]
  mode: InteractionMode
  createdAt: Date
  updatedAt: Date
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  metadata?: {
    tokens?: number
    model?: string
    confidence?: number
  }
}

export interface DeepSearchEntry {
  id: string
  query: string
  results: SearchResult[]
  timestamp: Date
}

export interface SearchResult {
  id: string
  title: string
  content: string
  relevance: number
  source: 'memory' | 'document' | 'web'
}

export interface Document {
  id: string
  title: string
  content: string
  type: 'markdown' | 'text' | 'code'
  tags: string[]
  createdAt: Date
  updatedAt: Date
}

export interface ImageAsset {
  id: string
  filename: string
  url: string
  alt: string
  tags: string[]
  createdAt: Date
}

export interface QuestionForUser {
  id: string
  question: string
  context: string
  priority: 'low' | 'medium' | 'high' | 'urgent'
  createdAt: Date
  answered: boolean
}

export interface AppState {
  theme: Theme
  mode: InteractionMode
  memories: Memory[]
  chatSessions: ChatSession[]
  currentSession: ChatSession | null
  deepSearchEntries: DeepSearchEntry[]
  documents: Document[]
  images: ImageAsset[]
  questionsForUser: QuestionForUser[]
  aiProcessVisualization: {
    isVisible: boolean
    currentStep: string
    progress: number
  }
  chatBubbleSettings: {
    showTimestamps: boolean
    showMetadata: boolean
    maxWidth: number
  }
  waveBackground: {
    isEnabled: boolean
    intensity: number
    speed: number
  }
  aiAgentPrompts: {
    systemPrompt: string
    userPrompt: string
    contextPrompt: string
  }
  browserWindow: {
    isVisible: boolean
    url: string
    title: string
  }
  isAuthenticated: boolean
  user: {
    id: string
    name: string
    email: string
  } | null
}

export type AppAction =
  | { type: 'SET_THEME'; payload: Theme }
  | { type: 'SET_MODE'; payload: InteractionMode }
  | { type: 'ADD_MEMORY'; payload: Memory }
  | { type: 'UPDATE_MEMORY'; payload: { id: string; updates: Partial<Memory> } }
  | { type: 'DELETE_MEMORY'; payload: string }
  | { type: 'ADD_CHAT_SESSION'; payload: ChatSession }
  | { type: 'UPDATE_CHAT_SESSION'; payload: { id: string; updates: Partial<ChatSession> } }
  | { type: 'DELETE_CHAT_SESSION'; payload: string }
  | { type: 'SET_CURRENT_SESSION'; payload: ChatSession | null }
  | { type: 'ADD_MESSAGE'; payload: { sessionId: string; message: ChatMessage } }
  | { type: 'ADD_DEEP_SEARCH_ENTRY'; payload: DeepSearchEntry }
  | { type: 'ADD_DOCUMENT'; payload: Document }
  | { type: 'UPDATE_DOCUMENT'; payload: { id: string; updates: Partial<Document> } }
  | { type: 'DELETE_DOCUMENT'; payload: string }
  | { type: 'ADD_IMAGE'; payload: ImageAsset }
  | { type: 'DELETE_IMAGE'; payload: string }
  | { type: 'ADD_QUESTION_FOR_USER'; payload: QuestionForUser }
  | { type: 'ANSWER_QUESTION'; payload: string }
  | { type: 'TOGGLE_AI_PROCESS_VISUALIZATION' }
  | { type: 'UPDATE_AI_PROCESS_VISUALIZATION'; payload: Partial<AppState['aiProcessVisualization']> }
  | { type: 'UPDATE_CHAT_BUBBLE_SETTINGS'; payload: Partial<AppState['chatBubbleSettings']> }
  | { type: 'UPDATE_WAVE_BACKGROUND'; payload: Partial<AppState['waveBackground']> }
  | { type: 'UPDATE_AI_AGENT_PROMPTS'; payload: Partial<AppState['aiAgentPrompts']> }
  | { type: 'TOGGLE_BROWSER_WINDOW' }
  | { type: 'UPDATE_BROWSER_WINDOW'; payload: Partial<AppState['browserWindow']> }
  | { type: 'SET_AUTHENTICATED'; payload: boolean }
  | { type: 'SET_USER'; payload: AppState['user'] }
  | { type: 'LOAD_STATE'; payload: AppState }
  | { type: 'RESET_STATE' }

// Memory Architecture Types (3-layer system)
export interface RawLogEntry {
  id: string
  timestamp: Date
  content: string
  metadata: {
    sessionId: string
    userId: string
    type: 'chat' | 'search' | 'action' | 'system'
  }
}

export interface SummaryEntry {
  id: string
  title: string
  summary: string
  level: 'session' | 'daily' | 'weekly' | 'monthly'
  parentId?: string
  childrenIds: string[]
  createdAt: Date
  updatedAt: Date
}

export interface VectorEntry {
  id: string
  content: string
  embedding: number[]
  metadata: {
    type: string
    tags: string[]
    importance: number
  }
  createdAt: Date
}

// AI Integration Types
export interface AIProvider {
  id: string
  name: string
  type: 'anthropic' | 'openai' | 'xai' | 'gemini' | 'cerebras'
  isActive: boolean
  config: {
    apiKey?: string
    model?: string
    temperature?: number
    maxTokens?: number
  }
}

export interface AIResponse {
  content: string
  metadata: {
    provider: string
    model: string
    tokens: number
    confidence: number
    processingTime: number
  }
}

// Component Props Types
export interface ComponentProps {
  className?: string
  children?: React.ReactNode
}

export interface ThemeableProps extends ComponentProps {
  theme?: Theme
}

export interface InteractiveProps extends ComponentProps {
  onClick?: () => void
  onHover?: () => void
  disabled?: boolean
}
