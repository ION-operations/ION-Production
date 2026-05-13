// Hybrid Retrieval System
// Phase 2: Combines RAG message retrieval with atom-based retrieval

import { ChatMessage } from '../types/chatTypes'
import { SummaryAtom, ContextOverride } from './summaryAtoms'
import { assemble, AssembledContext, Need, TokenBudget } from './assemble'
import { retrieveMessagesWithRAG, RAGRetrievalResult, RAGRetrievalOptions } from './ragRetrieval'
import { getEmbeddingService } from '../services/MessageEmbeddingService'
import { getVectorStore, MessageMetadata } from '../services/VectorStore'

export interface HybridRetrievalOptions extends RAGRetrievalOptions {
  /** Enable RAG retrieval */
  ragEnabled?: boolean
  /** Weight for RAG results (0-1) */
  ragWeight?: number
  /** Weight for atom results (0-1) */
  atomWeight?: number
  /** Diversify results */
  diversify?: boolean
}

export interface CombinedResult {
  message?: ChatMessage
  atom?: SummaryAtom
  score: number
  source: 'rag' | 'atom' | 'both'
  reasons: string[]
  semanticScore?: number
  significanceScore?: number
  tokens?: number
}

export interface HybridRetrievalResult {
  /** RAG retrieval results */
  ragResults: RAGRetrievalResult[]
  /** Atom-based retrieval results */
  atomResults: AssembledContext
  /** Combined and deduplicated results */
  combined: CombinedResult[]
  /** Total tokens used */
  totalTokens: number
  /** Tokens used by RAG results */
  ragTokens: number
  /** Tokens used by atom results */
  atomTokens: number
}

/**
 * Estimate tokens for a message or atom
 */
function estimateTokens(result: CombinedResult): number {
  if (result.message) {
    // Rough estimate: ~4 chars per token
    return Math.ceil(result.message.content.length / 4)
  }
  if (result.atom) {
    const baseTokens = Math.ceil(result.atom.recap.length / 4)
    const multipliers: Record<string, number> = {
      macro: 0.3,
      meso: 0.5,
      micro: 0.7,
      raw: 1.0
    }
    return Math.ceil(baseTokens * (multipliers[result.atom.level] ?? 1.0))
  }
  return 0
}

/**
 * Merge RAG and atom results
 */
function mergeRAGAndAtoms(
  ragResults: RAGRetrievalResult[],
  atomResults: AssembledContext,
  ragWeight: number = 0.6,
  atomWeight: number = 0.4
): CombinedResult[] {
  const messageMap = new Map<string, ChatMessage>()
  const atomMap = new Map<string, SummaryAtom>()
  
  // Build maps
  ragResults.forEach(r => messageMap.set(r.message.id, r.message))
  atomResults.atoms.forEach(a => atomMap.set(a.id, a))
  
  const combined: CombinedResult[] = []
  const seenIds = new Set<string>()
  
  // Add RAG results (with atom if available)
  ragResults.forEach(r => {
    const atom = atomMap.get(r.message.id)
    const score = ragWeight * r.score + (atom ? atomWeight * atom.sig.score : 0)
    
    combined.push({
      message: r.message,
      atom,
      score,
      source: atom ? 'both' : 'rag',
      reasons: r.reasons,
      semanticScore: r.semanticScore,
      significanceScore: r.significanceScore,
      tokens: estimateTokens({ message: r.message, atom, score, source: atom ? 'both' : 'rag', reasons: r.reasons })
    })
    
    seenIds.add(r.message.id)
  })
  
  // Add atom-only results (not in RAG results)
  atomResults.atoms.forEach(atom => {
    if (!seenIds.has(atom.id)) {
      combined.push({
        atom,
        score: atomWeight * atom.sig.score,
        source: 'atom',
        reasons: atomResults.reasons[atom.id] || ['significance'],
        significanceScore: atom.sig.score,
        tokens: estimateTokens({ atom, score: atom.sig.score, source: 'atom', reasons: atomResults.reasons[atom.id] || ['significance'] })
      })
    }
  })
  
  // Sort by score descending
  combined.sort((a, b) => b.score - a.score)
  
  return combined
}

/**
 * Pack combined results to token budget
 */
function packToBudget(
  combined: CombinedResult[],
  budget: TokenBudget,
  overrides: Record<string, ContextOverride>
): CombinedResult[] {
  const packed: CombinedResult[] = []
  let totalTokens = 0
  
  // Sort by score
  const sorted = [...combined].sort((a, b) => b.score - a.score)
  
  for (const result of sorted) {
    const messageId = result.message?.id || result.atom?.id
    if (!messageId) continue
    
    const tokens = result.tokens || estimateTokens(result)
    const override = overrides[messageId]
    
    // Check if we can fit it
    if (totalTokens + tokens <= budget) {
      packed.push(result)
      totalTokens += tokens
    } else if (override?.pinned && totalTokens + tokens <= budget * 1.2) {
      // Pinned messages can exceed budget slightly
      packed.push(result)
      totalTokens += tokens
    }
  }
  
  return packed
}

/**
 * Hybrid retrieval: Combine RAG message retrieval with atom-based retrieval
 */
export async function hybridRetrieve(
  query: string,
  messages: Record<string, ChatMessage[]>,
  summaryAtoms: Record<string, SummaryAtom[]>,
  overrides: Record<string, ContextOverride>,
  needs: Need[],
  budget: TokenBudget,
  options: HybridRetrievalOptions = {}
): Promise<HybridRetrievalResult> {
  const {
    ragEnabled = true,
    ragWeight = 0.6,
    atomWeight = 0.4,
    diversify = true,
    ...ragOptions
  } = options
  
  // RAG retrieval (if enabled)
  let ragResults: RAGRetrievalResult[] = []
  if (ragEnabled) {
    ragResults = await retrieveMessagesWithRAG(
      query,
      messages,
      summaryAtoms,
      overrides,
      ragOptions
    )
  }
  
  // Atom-based retrieval (existing system)
  const allAtoms: SummaryAtom[] = []
  Object.values(summaryAtoms).forEach(channelAtoms => {
    allAtoms.push(...channelAtoms)
  })
  
  const atomResults = assemble(
    query,
    needs,
    budget,
    allAtoms,
    overrides,
    'default'
  )
  
  // Merge results
  const combined = mergeRAGAndAtoms(ragResults, atomResults, ragWeight, atomWeight)
  
  // Pack to budget
  const packed = packToBudget(combined, budget, overrides)
  
  // Calculate token usage
  const ragTokens = packed
    .filter(r => r.source === 'rag' || r.source === 'both')
    .reduce((sum, r) => sum + (r.tokens || 0), 0)
  
  const atomTokens = packed
    .filter(r => r.source === 'atom' || r.source === 'both')
    .reduce((sum, r) => sum + (r.tokens || 0), 0)
  
  const totalTokens = ragTokens + atomTokens
  
  return {
    ragResults,
    atomResults,
    combined: packed,
    totalTokens,
    ragTokens,
    atomTokens
  }
}

/**
 * Index messages in vector store as they're created
 * Call this when messages are added/updated
 */
export async function indexMessages(
  messages: Record<string, ChatMessage[]>,
  summaryAtoms: Record<string, SummaryAtom[]>
): Promise<void> {
  const embeddingService = getEmbeddingService()
  const vectorStore = getVectorStore()
  
  // Collect all messages to index
  const messagesToIndex: Array<{
    message: ChatMessage
    channelId: string
    atom?: SummaryAtom
  }> = []
  
  Object.entries(messages).forEach(([channelId, channelMessages]) => {
    const channelAtoms = summaryAtoms[channelId] || []
    const atomMap = new Map(channelAtoms.map(a => [a.id, a]))
    
    channelMessages.forEach(message => {
      messagesToIndex.push({
        message,
        channelId,
        atom: atomMap.get(message.id)
      })
    })
  })
  
  // Batch embed messages
  const embeddings = await embeddingService.embedBatch(
    messagesToIndex.map(m => m.message)
  )
  
  // Add to vector store
  const entries = messagesToIndex.map(({ message, channelId, atom }) => {
    const embedding = embeddings.get(message.id)
    if (!embedding) return null
    
    const metadata: MessageMetadata = {
      messageId: message.id,
      channelId,
      timestamp: message.timestamp,
      agent: message.agent,
      significance: atom?.sig.score,
      level: atom?.level,
      pinned: false, // Will be updated from overrides
      priority: 0
    }
    
    return {
      messageId: message.id,
      embedding,
      metadata
    }
  }).filter((entry): entry is NonNullable<typeof entry> => entry !== null)
  
  await vectorStore.addBatch(entries)
}

/**
 * Update message metadata in vector store (e.g., when pinned/priority changes)
 */
export async function updateMessageMetadata(
  messageId: string,
  metadata: Partial<MessageMetadata>
): Promise<void> {
  const vectorStore = getVectorStore()
  await vectorStore.updateMetadata(messageId, metadata)
}

