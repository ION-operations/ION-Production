// Hook for managing SummaryAtoms in AI Chat
// Computes significance scores and relationships for messages

import { useState, useEffect, useMemo } from 'react'
import { ChatMessage } from '../types/chatTypes'
import {
  SummaryAtom,
  MessageContextInfo,
  ContextOverride
} from './summaryAtoms'
import {
  messagesToSummaryAtoms,
  trackMessageView,
  trackMessageReference
} from '../utils/messageToAtom'

export function useSummaryAtoms(messages: Record<string, ChatMessage[]>) {
  const [summaryAtoms, setSummaryAtoms] = useState<Record<string, SummaryAtom[]>>({})
  const [contextInfo, setContextInfo] = useState<Record<string, MessageContextInfo[]>>({})
  const [overrides, setOverrides] = useState<Record<string, ContextOverride>>({})
  
  // Compute summary atoms for all messages
  useEffect(() => {
    const newAtoms: Record<string, SummaryAtom[]> = {}
    const newContextInfo: Record<string, MessageContextInfo[]> = {}
    let turnCounter = 0
    
    Object.entries(messages).forEach(([channelId, channelMessages]) => {
      const { atoms, priorSymbols } = messagesToSummaryAtoms(channelMessages, turnCounter)
      newAtoms[channelId] = atoms
      
      // Create context info for each atom
      newContextInfo[channelId] = atoms.map(atom => ({
        id: atom.id,
        turn: atom.turn[0],
        included: false,  // Will be set by retrieval system
        totalTokensInPack: 0,  // Will be computed by retrieval system
        significance: atom.sig.score,
        relations: atom.rel.map(r => ({
          to: r.to,
          type: r.type,
          strength: r.strength
        })),
        uses: []  // Will be populated by retrieval system
      }))
      
      turnCounter += channelMessages.length
    })
    
    setSummaryAtoms(newAtoms)
    setContextInfo(newContextInfo)
  }, [messages])
  
  // Track message view when user views a message
  const handleMessageView = (messageId: string) => {
    trackMessageView(messageId)
    // Recompute significance for this message's channel
    // (In a real implementation, this would trigger a recomputation)
  }
  
  // Track message reference when agent references a message
  const handleMessageReference = (messageId: string) => {
    trackMessageReference(messageId)
  }
  
  // Get summary atom for a message
  const getSummaryAtom = (channelId: string, messageId: string): SummaryAtom | undefined => {
    return summaryAtoms[channelId]?.find(atom => atom.id === messageId)
  }
  
  // Get context info for a message
  const getContextInfo = (channelId: string, messageId: string): MessageContextInfo | undefined => {
    return contextInfo[channelId]?.find(info => info.id === messageId)
  }
  
  // Get override for a message
  const getOverride = (messageId: string): ContextOverride | undefined => {
    return overrides[messageId]
  }
  
  // Set override for a message
  const setOverride = (messageId: string, override: Partial<ContextOverride>) => {
    setOverrides(prev => ({
      ...prev,
      [messageId]: {
        id: messageId,
        ...prev[messageId],
        ...override
      }
    }))
  }
  
  // Pin/unpin a message
  const togglePin = (messageId: string) => {
    const current = overrides[messageId]
    setOverride(messageId, { pinned: !current?.pinned })
  }
  
  // Set priority for a message
  const setPriority = (messageId: string, priority: number) => {
    setOverride(messageId, { priority: clampPriority(priority) })
  }
  
  // Force level for a message
  const setForcedLevel = (messageId: string, level: SummaryAtom['level'] | 'raw' | null) => {
    if (level === null) {
      // Remove forced level
      const current = overrides[messageId]
      if (current) {
        const { forcedLevel, ...rest } = current
        setOverride(messageId, rest)
      }
    } else {
      setOverride(messageId, { forcedLevel: level })
    }
  }
  
  return {
    summaryAtoms,
    contextInfo,
    overrides,
    getSummaryAtom,
    getContextInfo,
    getOverride,
    setOverride,
    togglePin,
    setPriority,
    setForcedLevel,
    handleMessageView,
    handleMessageReference
  }
}

function clampPriority(priority: number): number {
  return Math.max(-1, Math.min(1, priority))
}

