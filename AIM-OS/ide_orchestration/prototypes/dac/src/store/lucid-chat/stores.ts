/**
 * Zustand stores for Lucid Chat API services
 */

import { create } from 'zustand'

// ============================================================================
// Meshy Store (3D Generation)
// ============================================================================

export interface MeshyTask {
  taskId: string
  type:
    | 'text-to-3d'
    | 'image-to-3d'
    | 'multi-image-to-3d'
    | 'remesh'
    | 'retexture'
    | 'rig'
    | 'balance'
  prompt?: string
  /**
   * UI convenience field for image inputs. Historically this was base64; now we store Data URI when available.
   */
  imageData?: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: number
  modelUrl?: string
  previewUrl?: string
  error?: string
  createdAt: Date
}

interface MeshyState {
  currentTask: MeshyTask | null
  taskQueue: MeshyTask[]
  history: MeshyTask[]
  settings: {
    defaultMode: 'preview' | 'refine'
    defaultArtStyle: string
    autoDownload: boolean
    pollingInterval: number
  }
  
  setCurrentTask: (task: MeshyTask | null) => void
  addTask: (task: MeshyTask) => void
  updateTask: (taskId: string, updates: Partial<MeshyTask>) => void
  addToHistory: (task: MeshyTask) => void
  updateSettings: (settings: Partial<MeshyState['settings']>) => void
}

export const useMeshyStore = create<MeshyState>((set) => ({
  currentTask: null,
  taskQueue: [],
  history: [],
  settings: {
    defaultMode: 'preview',
    defaultArtStyle: '',
    autoDownload: false,
    pollingInterval: 2000,
  },
  
  setCurrentTask: (task) => set({ currentTask: task }),
  
  addTask: (task) => set((state) => ({
    taskQueue: [...state.taskQueue, task],
  })),
  
  updateTask: (taskId, updates) => set((state) => ({
    taskQueue: state.taskQueue.map((task) =>
      task.taskId === taskId ? { ...task, ...updates } : task
    ),
    currentTask: state.currentTask?.taskId === taskId
      ? { ...state.currentTask, ...updates }
      : state.currentTask,
  })),
  
  addToHistory: (task) => set((state) => ({
    history: [task, ...state.history].slice(0, 50), // Keep last 50
  })),
  
  updateSettings: (newSettings) => set((state) => ({
    settings: { ...state.settings, ...newSettings },
  })),
}))

// ============================================================================
// ElevenLabs Store (TTS)
// ============================================================================

export interface ElevenLabsVoice {
  voice_id: string
  name: string
  category: string
  description?: string
  preview_url?: string
}

interface ElevenLabsState {
  voices: ElevenLabsVoice[]
  selectedVoiceId: string | null
  favoriteVoiceIds: string[]
  text: string
  voiceSettings: {
    stability: number
    similarity_boost: number
    style?: number
    use_speaker_boost: boolean
  }
  modelId: string
  outputFormat: string
  
  setModelId: (modelId: string) => void
  setOutputFormat: (format: string) => void
  isGenerating: boolean
  audioUrl: string | null
  audioBlob: Blob | null
  error: string | null
  history: Array<{
    text: string
    voiceId: string
    audioUrl: string
    createdAt: Date
  }>
  
  setVoices: (voices: ElevenLabsVoice[]) => void
  setSelectedVoice: (voiceId: string | null) => void
  toggleFavorite: (voiceId: string) => void
  setText: (text: string) => void
  updateVoiceSettings: (settings: Partial<ElevenLabsState['voiceSettings']>) => void
  setGenerating: (isGenerating: boolean) => void
  setAudio: (audioUrl: string | null, audioBlob: Blob | null) => void
  setError: (error: string | null) => void
  addToHistory: (text: string, voiceId: string, audioUrl: string) => void
}

export const useElevenLabsStore = create<ElevenLabsState>((set) => ({
  voices: [],
  selectedVoiceId: null,
  favoriteVoiceIds: [],
  text: '',
  voiceSettings: {
    stability: 0.5,
    similarity_boost: 0.75,
    style: 0.0,
    use_speaker_boost: true,
  },
  modelId: 'eleven_multilingual_v2',
  outputFormat: 'mp3_44100_128',
  isGenerating: false,
  audioUrl: null,
  audioBlob: null,
  error: null,
  history: [],
  
  setVoices: (voices) => set({ voices }),
  
  setSelectedVoice: (voiceId) => set({ selectedVoiceId: voiceId }),
  
  toggleFavorite: (voiceId) => set((state) => ({
    favoriteVoiceIds: state.favoriteVoiceIds.includes(voiceId)
      ? state.favoriteVoiceIds.filter(id => id !== voiceId)
      : [...state.favoriteVoiceIds, voiceId],
  })),
  
  setText: (text) => set({ text }),
  
  updateVoiceSettings: (settings) => set((state) => ({
    voiceSettings: { ...state.voiceSettings, ...settings },
  })),
  
  setModelId: (modelId) => set({ modelId }),
  
  setOutputFormat: (outputFormat) => set({ outputFormat }),
  
  setGenerating: (isGenerating) => set({ isGenerating }),
  
  setAudio: (audioUrl, audioBlob) => set({ audioUrl, audioBlob }),
  
  setError: (error) => set({ error }),
  
  addToHistory: (text, voiceId, audioUrl) => set((state) => ({
    history: [
      { text, voiceId, audioUrl, createdAt: new Date() },
      ...state.history,
    ].slice(0, 50), // Keep last 50
  })),
}))

// ============================================================================
// Minimax Store (LLM)
// ============================================================================

export interface MinimaxMessage {
  role: 'system' | 'user' | 'assistant'
  content: string
  timestamp: Date
}

interface MinimaxState {
  messages: MinimaxMessage[]
  input: string
  isStreaming: boolean
  streamingMessage: string
  selectedModel: string
  temperature: number
  maxTokens: number
  topP: number
  frequencyPenalty: number
  presencePenalty: number
  usage: {
    promptTokens: number
    completionTokens: number
    totalTokens: number
  }
  history: Array<{
    messages: MinimaxMessage[]
    model: string
    timestamp: Date
  }>
  
  addMessage: (message: MinimaxMessage) => void
  setInput: (input: string) => void
  setStreaming: (isStreaming: boolean) => void
  setStreamingMessage: (message: string) => void
  setModel: (model: string) => void
  setTemperature: (temperature: number) => void
  setMaxTokens: (maxTokens: number) => void
  setTopP: (topP: number) => void
  setFrequencyPenalty: (penalty: number) => void
  setPresencePenalty: (penalty: number) => void
  updateUsage: (usage: Partial<MinimaxState['usage']>) => void
  addToHistory: () => void
  clearMessages: () => void
}

export const useMinimaxStore = create<MinimaxState>((set) => ({
  messages: [],
  input: '',
  isStreaming: false,
  streamingMessage: '',
  selectedModel: 'abab5.5-chat', // Default model
  temperature: 0.7,
  maxTokens: 2000,
  topP: 1.0,
  frequencyPenalty: 0.0,
  presencePenalty: 0.0,
  usage: {
    promptTokens: 0,
    completionTokens: 0,
    totalTokens: 0,
  },
  history: [],
  
  addMessage: (message) => set((state) => ({
    messages: [...state.messages, message],
  })),
  
  setInput: (input) => set({ input }),
  
  setStreaming: (isStreaming) => set({ isStreaming }),
  
  setStreamingMessage: (message) => set({ streamingMessage: message }),
  
  setModel: (selectedModel) => set({ selectedModel }),
  
  setTemperature: (temperature) => set({ temperature }),
  
  setMaxTokens: (maxTokens) => set({ maxTokens }),
  
  setTopP: (topP) => set({ topP }),
  
  setFrequencyPenalty: (frequencyPenalty) => set({ frequencyPenalty }),
  
  setPresencePenalty: (presencePenalty) => set({ presencePenalty }),
  
  updateUsage: (newUsage) => set((state) => ({
    usage: { ...state.usage, ...newUsage },
  })),
  
  addToHistory: () => set((state) => {
    if (state.messages.length === 0) return state
    return {
      history: [
        {
          messages: [...state.messages],
          model: state.selectedModel,
          timestamp: new Date(),
        },
        ...state.history,
      ].slice(0, 20), // Keep last 20 conversations
    }
  }),
  
  clearMessages: () => set({ messages: [], input: '' }),
}))

// ============================================================================
// Export Advanced LLM Store
// ============================================================================

export { useAdvancedLLMStore } from './advancedLLMStore'
export type { AdvancedChatMessage } from './advancedLLMStore'

