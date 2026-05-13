// Enhanced useSummaryAtoms hook with RAG support
// Phase 2: Integrates RAG retrieval with summary atoms

import { useState, useEffect, useMemo, useCallback } from 'react'
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
import { indexMessages, updateMessageMetadata } from '../utils/hybridRetrieval'

export interface UseSummaryAtomsWithRAGOptions {
  /** Enable RAG indexing */
  ragEnabled?: boolean
  /** Auto-index messages when they change */
  autoIndex?: boolean
}

/**
 * Enhanced hook with RAG support
 */
export function useSummaryAtomsWithRAG(
  messages: Record<string, ChatMessage[]>,
  options: UseSummaryAtomsWithRAGOptions = {}
) {
  const { ragEnabled = false, autoIndex = true } = options
  
  const [summaryAtoms, setSummaryAtoms] = useState<Record<string, SummaryAtom[]>>({})
  const [contextInfo, setContextInfo] = useState<Record<string, MessageContextInfo[]>>({})
  const [overrides, setOverrides] = useState<Record<string, ContextOverride>>({})
  const [ragIndexed, setRagIndexed] = useState(false)
  
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
        included: false,
        totalTokensInPack: 0,
        significance: atom.sig.score,
        relations: atom.rel.map(r => ({
          to: r.to,
          type: r.type,
          strength: r.strength
        })),
        uses: []
      }))
      
      turnCounter += channelMessages.length
    })
    
    setSummaryAtoms(newAtoms)
    setContextInfo(newContextInfo)
    setRagIndexed(false) // Reset indexing flag when messages change
  }, [messages])
  
  // Index messages in vector store when RAG is enabled
  useEffect(() => {
    if (ragEnabled && autoIndex && !ragIndexed && Object.keys(summaryAtoms).length > 0) {
      indexMessages(messages, summaryAtoms)
        .then(() => setRagIndexed(true))
        .catch(err => console.error('Failed to index messages:', err))
    }
  }, [ragEnabled, autoIndex, ragIndexed, messages, summaryAtoms])
  
  // Track message view when user views a message
  const handleMessageView = useCallback((messageId: string) => {
    trackMessageView(messageId)
  }, [])
  
  // Track message reference when agent references a message
  const handleMessageReference = useCallback((messageId: string) => {
    trackMessageReference(messageId)
  }, [])
  
  // Get summary atom for a message
  const getSummaryAtom = useCallback((channelId: string, messageId: string): SummaryAtom | undefined => {
    return summaryAtoms[channelId]?.find(atom => atom.id === messageId)
  }, [summaryAtoms])
  
  // Get context info for a message
  const getContextInfo = useCallback((channelId: string, messageId: string): MessageContextInfo | undefined => {
    return contextInfo[channelId]?.find(info => info.id === messageId)
  }, [contextInfo])
  
  // Get override for a message
  const getOverride = useCallback((messageId: string): ContextOverride | undefined => {
    return overrides[messageId]
  }, [overrides])
  
  // Set override for a message
  const setOverride = useCallback((messageId: string, override: Partial<ContextOverride>) => {
    setOverrides(prev => {
      const newOverrides = {
        ...prev,
        [messageId]: {
          id: messageId,
          ...prev[messageId],
          ...override
        }
      }
      
      // Update vector store metadata if RAG is enabled
      if (ragEnabled) {
        updateMessageMetadata(messageId, {
          pinned: newOverrides[messageId]?.pinned,
          priority: newOverrides[messageId]?.priority
        }).catch(err => console.error('Failed to update vector store metadata:', err))
      }
      
      return newOverrides
    })
  }, [ragEnabled])
  
  // Pin/unpin a message
  const togglePin = useCallback((messageId: string) => {
    const current = overrides[messageId]
    setOverride(messageId, { pinned: !current?.pinned })
  }, [overrides, setOverride])
  
  // Set priority for a message
  const setPriority = useCallback((messageId: string, priority: number) => {
    setOverride(messageId, { priority: clampPriority(priority) })
  }, [setOverride])
  
  // Force level for a message
  const setForcedLevel = useCallback((messageId: string, level: SummaryAtom['level'] | 'raw' | null) => {
    if (level === null) {
      const current = overrides[messageId]
      if (current) {
        const { forcedLevel, ...rest } = current
        setOverride(messageId, rest)
      }
    } else {
      setOverride(messageId, { forcedLevel: level })
    }
  }, [overrides, setOverride])
  
  // Manually trigger indexing
  const triggerIndexing = useCallback(async () => {
    if (ragEnabled) {
      await indexMessages(messages, summaryAtoms)
      setRagIndexed(true)
    }
  }, [ragEnabled, messages, summaryAtoms])
  
  return {
    summaryAtoms,
    contextInfo,
    overrides,
    ragEnabled,
    ragIndexed,
    getSummaryAtom,
    getContextInfo,
    getOverride,
    setOverride,
    togglePin,
    setPriority,
    setForcedLevel,
    handleMessageView,
    handleMessageReference,
    triggerIndexing
  }
}

function clampPriority(priority: number): number {
  return Math.max(-1, Math.min(1, priority))
}

