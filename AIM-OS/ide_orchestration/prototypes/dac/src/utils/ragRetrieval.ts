// RAG-Enhanced Message Retrieval
// Phase 1: Foundation - Enhanced with MessageEmbeddingService and VectorStore

import { ChatMessage } from '../types/chatTypes'
import { SummaryAtom, ContextOverride } from './summaryAtoms'
import { assemble, AssembledContext, Need } from './assemble'
import { MessageEmbeddingService, getEmbeddingService } from '../services/MessageEmbeddingService'
import { InMemoryVectorStore, getVectorStore, MessageMetadata, VectorSearchResult } from '../services/VectorStore'
import { cosineSimilarity } from './mathUtils'

// Simple embedding interface (would use actual embedding API in production)
export interface MessageEmbedding {
  messageId: string
  channelId: string
  embedding: number[]  // Vector embedding
  timestamp: Date
}

// RAG retrieval result
export interface RAGRetrievalResult {
  message: ChatMessage
  atom?: SummaryAtom
  score: number
  reasons: string[]
  semanticScore: number
  significanceScore: number
  userSelectionScore: number
  recencyScore: number
}

// RAG retrieval options
export interface RAGRetrievalOptions {
  limit?: number
  minScore?: number
  includePinned?: boolean
  timeDecay?: boolean
  halfLifeHours?: number
  crossChannel?: boolean
  channelIds?: string[]
}

/**
 * Compute semantic similarity using embeddings
 * Uses MessageEmbeddingService for real embeddings (or mock)
 */
async function computeSemanticSimilarity(
  queryEmbedding: number[],
  messageEmbedding: number[]
): Promise<number> {
  return cosineSimilarity(queryEmbedding, messageEmbedding)
}

/**
 * Compute time decay score
 */
function computeTimeDecay(
  messageTimestamp: Date,
  halfLifeHours: number = 24
): number {
  const ageHours = (Date.now() - messageTimestamp.getTime()) / (1000 * 60 * 60)
  return Math.exp(-ageHours / halfLifeHours)
}

/**
 * Compute user selection score (pins, priority, forced level)
 */
function computeUserSelectionScore(
  messageId: string,
  overrides: Record<string, ContextOverride>
): number {
  const override = overrides[messageId]
  if (!override) return 0
  
  let score = 0
  if (override.pinned) score += 0.3
  if (override.priority) score += Math.max(-0.2, Math.min(0.2, override.priority * 0.2))
  if (override.forcedLevel) score += 0.1
  
  return Math.max(0, Math.min(1, score))
}

/**
 * Build enhanced query from current input and conversation context
 */
export function buildRAGQuery(
  currentInput: string,
  recentMessages: ChatMessage[],
  channelContext?: { name: string; description?: string }
): string {
  // Extract topics from recent messages
  const recentTopics = recentMessages
    .slice(-5)
    .map(m => m.content)
    .join(' ')
    .split(/\s+/)
    .filter(w => w.length > 4)
    .slice(0, 10)
    .join(' ')
  
  // Combine with current input and channel context
  const parts = [currentInput]
  if (recentTopics) parts.push(recentTopics)
  if (channelContext?.description) parts.push(channelContext.description)
  
  return parts.join(' ')
}

/**
 * RAG-enhanced message retrieval
 * Combines semantic search with existing atom-based retrieval
 * Phase 1: Uses MessageEmbeddingService and VectorStore
 */
export async function retrieveMessagesWithRAG(
  query: string,
  messages: Record<string, ChatMessage[]>,
  summaryAtoms: Record<string, SummaryAtom[]>,
  overrides: Record<string, ContextOverride>,
  options: RAGRetrievalOptions = {}
): Promise<RAGRetrievalResult[]> {
  const {
    limit = 20,
    minScore = 0.1,
    includePinned = true,
    timeDecay = true,
    halfLifeHours = 24,
    crossChannel = false,
    channelIds
  } = options
  
  const embeddingService = getEmbeddingService()
  const vectorStore = getVectorStore()
  
  // Embed query
  const queryEmbedding = await embeddingService.embedQuery(query)
  
  // Search vector store
  const vectorResults = await vectorStore.search(queryEmbedding, {
    k: limit * 2, // Get more results for filtering
    minScore: minScore,
    channelIds: channelIds || (crossChannel ? undefined : Object.keys(messages)),
    includeMetadata: true
  })
  
  const results: RAGRetrievalResult[] = []
  const channelsToSearch = channelIds || Object.keys(messages)
  
  // Create message and atom maps
  const messageMap = new Map<string, ChatMessage>()
  const atomMap = new Map<string, SummaryAtom>()
  
  channelsToSearch.forEach(channelId => {
    const channelMessages = messages[channelId] || []
    const channelAtoms = summaryAtoms[channelId] || []
    
    channelMessages.forEach(msg => messageMap.set(msg.id, msg))
    channelAtoms.forEach(atom => atomMap.set(atom.id, atom))
  })
  
  // Process vector search results
  for (const vectorResult of vectorResults) {
    const message = messageMap.get(vectorResult.messageId)
    if (!message) continue
    
    const atom = atomMap.get(message.id)
    
    // Semantic similarity from vector search
    const semanticScore = vectorResult.score
    
    // Significance score (from atom)
    const significanceScore = atom?.sig.score || 0.5
    
    // User selection score
    const userSelectionScore = computeUserSelectionScore(message.id, overrides)
    
    // Recency score (time decay)
    const recencyScore = timeDecay 
      ? computeTimeDecay(message.timestamp, halfLifeHours)
      : 1.0
    
    // Composite score (RAG-enhanced)
    const compositeScore =
      0.40 * semanticScore +           // RAG semantic relevance
      0.25 * significanceScore +       // Existing significance
      0.15 * userSelectionScore +      // User selections (pins, priority)
      0.10 * recencyScore +            // Time decay
      0.10 * (atom?.sig.breakdown.usage || 0)  // Usage frequency
    
    // Reasons for inclusion
    const reasons: string[] = []
    if (semanticScore > 0.5) reasons.push('semantic-relevance')
    if (significanceScore > 0.7) reasons.push('high-significance')
    if (userSelectionScore > 0.2) reasons.push('user-selected')
    if (recencyScore > 0.7) reasons.push('recent')
    if (atom?.rel.length > 0) reasons.push('related')
    
    // Filter by minimum score
    if (compositeScore >= minScore) {
      // Always include pinned messages if requested
      const override = overrides[message.id]
      if (includePinned && override?.pinned) {
        results.push({
          message,
          atom,
          score: Math.max(compositeScore, 0.8),  // Boost pinned messages
          reasons: ['pinned', ...reasons],
          semanticScore,
          significanceScore,
          userSelectionScore,
          recencyScore
        })
      } else if (!override?.pinned || includePinned) {
        results.push({
          message,
          atom,
          score: compositeScore,
          reasons,
          semanticScore,
          significanceScore,
          userSelectionScore,
          recencyScore
        })
      }
    }
  }
  
  // Sort by score descending
  results.sort((a, b) => b.score - a.score)
  
  // Return top results
  return results.slice(0, limit)
}

// Note: hybridRetrieve has been moved to hybridRetrieval.ts
// Import it from there: import { hybridRetrieve } from './hybridRetrieval'

/**
 * Find related messages using RAG (for pinned/priority messages)
 * Phase 1: Enhanced with async RAG retrieval
 */
export async function findRelatedMessages(
  anchorMessage: ChatMessage,
  messages: Record<string, ChatMessage[]>,
  summaryAtoms: Record<string, SummaryAtom[]>,
  overrides: Record<string, ContextOverride>,
  options: RAGRetrievalOptions = {}
): Promise<RAGRetrievalResult[]> {
  // Use anchor message content as query
  const query = buildRAGQuery(
    anchorMessage.content,
    [], // No recent context needed
    undefined
  )
  
  // Retrieve related messages
  const results = await retrieveMessagesWithRAG(
    query,
    messages,
    summaryAtoms,
    overrides,
    {
      ...options,
      minScore: 0.2,  // Lower threshold for related messages
      limit: 10
    }
  )
  
  // Exclude anchor message
  return results.filter(r => r.message.id !== anchorMessage.id)
}
