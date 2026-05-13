/**
 * Zustand store for Advanced LLM Service
 * Manages state for Lucid Chat with full AIM-OS integration
 */

import { create } from 'zustand'
import type { ThinkingMode, OutputFormat, OutputStyle, OutputTone } from '../../services/lucid-chat/llm/AdvancedLLMService'
import type { DeepSearchConfig } from '../../services/lucid-chat/llm/AdvancedLLMService'

export interface AdvancedChatMessage {
  role: 'system' | 'user' | 'assistant'
  content: string
  timestamp: Date
  outputProtocol?: {
    format?: OutputFormat
    sections?: string[]
    citations?: Array<{ id: string; source: string; url?: string }>
    diagrams?: Array<{ type: string; content: string }>
    charts?: Array<{ type: string; data: any; config?: any }>
    images?: Array<{ url: string; alt?: string; caption?: string }>
    video?: Array<{ url: string; type?: string; caption?: string }>
  }
  aimos?: {
    apoe?: {
      planId?: string
      rolesUsed?: string[]
      executionTime?: number
    }
    seg?: {
      knowledgeSynthesized?: boolean
      contradictionsDetected?: number
      evidenceCount?: number
    }
    vif?: {
      witnessId?: string
      confidence?: number
      provenance?: any
    }
    cas?: {
      qualityScore?: number
      cognitiveLoad?: number
      driftDetected?: boolean
    }
  }
  reasoning?: {
    steps?: Array<{ step: number; thought: string; confidence: number }>
    finalAnswer?: string
  }
  sources?: Array<{ title: string; url: string; relevance: number }>
  tokensUsed?: number
  latencyMs?: number
}

interface AdvancedLLMState {
  // Messages
  messages: AdvancedChatMessage[]
  input: string
  isStreaming: boolean
  streamingMessage: string
  streamingProtocol?: AdvancedChatMessage['outputProtocol']
  
  // Thinking Mode
  thinkingMode: ThinkingMode
  setThinkingMode: (mode: ThinkingMode) => void
  
  // Deep Search
  deepSearchEnabled: boolean
  deepSearchConfig: DeepSearchConfig
  setDeepSearchEnabled: (enabled: boolean) => void
  updateDeepSearchConfig: (config: Partial<DeepSearchConfig>) => void
  
  // Branch Reasoning
  branchReasoningEnabled: boolean
  setBranchReasoningEnabled: (enabled: boolean) => void
  
  // APOE
  apoeEnabled: boolean
  setAPOEEnabled: (enabled: boolean) => void
  
  // Output Format
  outputFormat: OutputFormat
  outputStyle: OutputStyle
  outputTone: OutputTone
  setOutputFormat: (format: OutputFormat) => void
  setOutputStyle: (style: OutputStyle) => void
  setOutputTone: (tone: OutputTone) => void
  
  // Model Selection
  provider: 'gemini' | 'anthropic' | 'cerebras' | 'minimax' | 'openai'
  model: string
  setProvider: (provider: AdvancedLLMState['provider']) => void
  setModel: (model: string) => void
  
  // Budget Tracking
  budget: {
    tokens: number
    time: number
    cost: number
  }
  budgetLimit: {
    tokens?: number
    time?: number
    cost?: number
  }
  updateBudget: (usage: Partial<AdvancedLLMState['budget']>) => void
  setBudgetLimit: (limit: Partial<AdvancedLLMState['budgetLimit']>) => void
  
  // Quality Gates
  qualityGates: {
    confidence: number
    quality: number
    consistency: number
  }
  setQualityGates: (gates: Partial<AdvancedLLMState['qualityGates']>) => void
  
  // Message Management
  addMessage: (message: AdvancedChatMessage) => void
  setInput: (input: string) => void
  setStreaming: (isStreaming: boolean) => void
  setStreamingMessage: (message: string) => void
  setStreamingProtocol: (protocol?: AdvancedChatMessage['outputProtocol']) => void
  clearMessages: () => void
  
  // History
  history: Array<{
    messages: AdvancedChatMessage[]
    thinkingMode: ThinkingMode
    timestamp: Date
  }>
  addToHistory: () => void
  loadFromHistory: (index: number) => void
}

export const useAdvancedLLMStore = create<AdvancedLLMState>((set, get) => ({
  // Messages
  messages: [],
  input: '',
  isStreaming: false,
  streamingMessage: '',
  streamingProtocol: undefined,
  
  // Thinking Mode
  thinkingMode: 'balanced',
  setThinkingMode: (mode) => set({ thinkingMode: mode }),
  
  // Deep Search
  deepSearchEnabled: false,
  deepSearchConfig: {
    providers: ['deepsearch', 'perplexity'],
    depth: 'basic',
    enableCrawling: false,
    synthesizeResults: true,
  },
  setDeepSearchEnabled: (enabled) => set({ deepSearchEnabled: enabled }),
  updateDeepSearchConfig: (config) => set((state) => ({
    deepSearchConfig: { ...state.deepSearchConfig, ...config },
  })),
  
  // Branch Reasoning
  branchReasoningEnabled: false,
  setBranchReasoningEnabled: (enabled) => set({ branchReasoningEnabled: enabled }),
  
  // APOE
  apoeEnabled: false,
  setAPOEEnabled: (enabled) => set({ apoeEnabled: enabled }),
  
  // Output Format
  outputFormat: 'mixed',
  outputStyle: 'detailed',
  outputTone: 'professional',
  setOutputFormat: (format) => set({ outputFormat: format }),
  setOutputStyle: (style) => set({ outputStyle: style }),
  setOutputTone: (tone) => set({ outputTone: tone }),
  
  // Model Selection
  provider: 'gemini',
  model: 'gemini-pro',
  setProvider: (provider) => set({ provider }),
  setModel: (model) => set({ model }),
  
  // Budget Tracking
  budget: {
    tokens: 0,
    time: 0,
    cost: 0,
  },
  budgetLimit: {
    tokens: 100000,
    time: 300000, // 5 minutes
    cost: 10.0, // $10
  },
  updateBudget: (usage) => set((state) => ({
    budget: { ...state.budget, ...usage },
  })),
  setBudgetLimit: (limit) => set((state) => ({
    budgetLimit: { ...state.budgetLimit, ...limit },
  })),
  
  // Quality Gates
  qualityGates: {
    confidence: 0.70,
    quality: 0.75,
    consistency: 0.80,
  },
  setQualityGates: (gates) => set((state) => ({
    qualityGates: { ...state.qualityGates, ...gates },
  })),
  
  // Message Management
  addMessage: (message) => set((state) => ({
    messages: [...state.messages, message],
  })),
  
  setInput: (input) => set({ input }),
  
  setStreaming: (isStreaming) => set({ isStreaming }),
  
  setStreamingMessage: (message) => set({ streamingMessage: message }),
  
  setStreamingProtocol: (protocol) => set({ streamingProtocol: protocol }),
  
  clearMessages: () => set({ messages: [], input: '' }),
  
  // History
  history: [],
  
  addToHistory: () => {
    const state = get()
    if (state.messages.length === 0) return
    set((currentState) => ({
      history: [
        {
          messages: [...currentState.messages],
          thinkingMode: currentState.thinkingMode,
          timestamp: new Date(),
        },
        ...currentState.history,
      ].slice(0, 20), // Keep last 20 conversations
    }))
  },
  
  loadFromHistory: (index) => {
    const state = get()
    if (index < 0 || index >= state.history.length) return
    const historyItem = state.history[index]
    set({
      messages: [...historyItem.messages],
      thinkingMode: historyItem.thinkingMode,
    })
  },
}))

