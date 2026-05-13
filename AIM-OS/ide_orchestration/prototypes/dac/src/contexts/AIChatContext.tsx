// Context Provider for AI Chat Data Sharing
// Allows ContextLedger and ChatHeatmapPanel to access AIChatManagement data

import React, { createContext, useContext } from 'react'
import { AssembledContext } from '../utils/assemble'
import { MessageContextInfo } from '../utils/summaryAtoms'
import { ChatMessage } from '../types/chatTypes'

interface AIChatContextData {
  messages: Record<string, ChatMessage[]>
  contextInfo: Record<string, MessageContextInfo[]>
  assembledContext: AssembledContext | null
  selectedChannel: string
  budget: number
  useRetrieval: boolean
  setUseRetrieval: (enabled: boolean) => void
}

const AIChatContext = createContext<AIChatContextData | null>(null)

export const useAIChatContext = () => {
  const context = useContext(AIChatContext)
  if (!context) {
    // Return default values if context not available (panels can work standalone)
    return {
      messages: {},
      contextInfo: {},
      assembledContext: null,
      selectedChannel: '',
      budget: 12000,
      useRetrieval: false,
      setUseRetrieval: () => {}
    }
  }
  return context
}

interface AIChatContextProviderProps {
  children: React.ReactNode
  messages: Record<string, ChatMessage[]>
  contextInfo: Record<string, MessageContextInfo[]>
  assembledContext: AssembledContext | null
  selectedChannel: string
  budget: number
  useRetrieval: boolean
  setUseRetrieval: (enabled: boolean) => void
}

export const AIChatContextProvider: React.FC<AIChatContextProviderProps> = ({
  children,
  messages,
  contextInfo,
  assembledContext,
  selectedChannel,
  budget,
  useRetrieval,
  setUseRetrieval
}) => {
  return (
    <AIChatContext.Provider
      value={{
        messages,
        contextInfo,
        assembledContext,
        selectedChannel,
        budget,
        useRetrieval,
        setUseRetrieval
      }}
    >
      {children}
    </AIChatContext.Provider>
  )
}

