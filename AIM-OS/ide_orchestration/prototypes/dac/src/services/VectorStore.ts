// Vector Store for Message Embeddings
// Phase 1: Foundation - In-memory implementation
// Future: Replace with CMC Vector Store integration

import { ChatMessage } from '../types/chatTypes'
import { SummaryAtom } from '../utils/summaryAtoms'
import { cosineSimilarity } from '../utils/mathUtils'

export interface MessageMetadata {
  messageId: string
  channelId: string
  timestamp: Date
  agent?: string
  significance?: number
  level?: 'micro' | 'meso' | 'macro'
  pinned?: boolean
  priority?: number
}

export interface VectorSearchResult {
  messageId: string
  score: number  // Cosine similarity [0, 1]
  metadata: MessageMetadata
}

export interface VectorSearchOptions {
  k?: number
  minScore?: number
  channelIds?: string[]
  agent?: string
  pinned?: boolean
  includeMetadata?: boolean
}

interface VectorStoreEntry {
  messageId: string
  embedding: number[]
  metadata: MessageMetadata
}

/**
 * In-memory vector store for message embeddings
 * Phase 1: Simple implementation with linear search
 * Future: Replace with Faiss/Chroma integration via CMC
 */
export class InMemoryVectorStore {
  private vectors: Map<string, VectorStoreEntry>
  
  constructor() {
    this.vectors = new Map()
  }
  
  /**
   * Add a message embedding to the store
   */
  async add(messageId: string, embedding: number[], metadata: MessageMetadata): Promise<void> {
    this.vectors.set(messageId, {
      messageId,
      embedding,
      metadata
    })
  }
  
  /**
   * Search for similar messages using cosine similarity
   * Uses linear search (O(n)) - fine for prototype, upgrade to Faiss for production
   */
  async search(queryEmbedding: number[], options: VectorSearchOptions = {}): Promise<VectorSearchResult[]> {
    const {
      k = 20,
      minScore = 0.1,
      channelIds,
      agent,
      pinned,
      includeMetadata = true
    } = options
    
    const results: VectorSearchResult[] = []
    
    // Linear search through all vectors
    for (const entry of this.vectors.values()) {
      // Apply filters
      if (channelIds && !channelIds.includes(entry.metadata.channelId)) continue
      if (agent && entry.metadata.agent !== agent) continue
      if (pinned !== undefined && entry.metadata.pinned !== pinned) continue
      
      // Compute similarity
      const score = cosineSimilarity(queryEmbedding, entry.embedding)
      
      if (score >= minScore) {
        results.push({
          messageId: entry.messageId,
          score,
          metadata: includeMetadata ? entry.metadata : {
            messageId: entry.messageId,
            channelId: entry.metadata.channelId,
            timestamp: entry.metadata.timestamp
          }
        })
      }
    }
    
    // Sort by score descending
    results.sort((a, b) => b.score - a.score)
    
    // Return top K
    return results.slice(0, k)
  }
  
  /**
   * Update message metadata
   */
  async updateMetadata(messageId: string, metadata: Partial<MessageMetadata>): Promise<void> {
    const entry = this.vectors.get(messageId)
    if (entry) {
      entry.metadata = { ...entry.metadata, ...metadata }
    }
  }
  
  /**
   * Remove a message from the store
   */
  async remove(messageId: string): Promise<void> {
    this.vectors.delete(messageId)
  }
  
  /**
   * Get embedding for a message
   */
  async getEmbedding(messageId: string): Promise<number[] | null> {
    const entry = this.vectors.get(messageId)
    return entry ? entry.embedding : null
  }
  
  /**
   * Get metadata for a message
   */
  async getMetadata(messageId: string): Promise<MessageMetadata | null> {
    const entry = this.vectors.get(messageId)
    return entry ? entry.metadata : null
  }
  
  /**
   * Get total number of indexed messages
   */
  async size(): Promise<number> {
    return this.vectors.size
  }
  
  /**
   * Clear all embeddings
   */
  async clear(): Promise<void> {
    this.vectors.clear()
  }
  
  /**
   * Batch add embeddings
   */
  async addBatch(
    entries: Array<{ messageId: string; embedding: number[]; metadata: MessageMetadata }>
  ): Promise<void> {
    for (const entry of entries) {
      await this.add(entry.messageId, entry.embedding, entry.metadata)
    }
  }
  
  /**
   * Get all message IDs
   */
  async getAllMessageIds(): Promise<string[]> {
    return Array.from(this.vectors.keys())
  }
}

// Singleton instance
let vectorStoreInstance: InMemoryVectorStore | null = null

/**
 * Get singleton vector store instance
 */
export function getVectorStore(): InMemoryVectorStore {
  if (!vectorStoreInstance) {
    vectorStoreInstance = new InMemoryVectorStore()
  }
  return vectorStoreInstance
}

