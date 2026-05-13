// Message Embedding Service
// Phase 1: Foundation - Mock implementation for frontend prototype
// Future: Replace with backend API integration

import { ChatMessage } from '../types/chatTypes'

export interface EmbeddingServiceConfig {
  modelName?: string
  dimension?: number
  useMock?: boolean
  apiUrl?: string
  cacheSize?: number
  batchSize?: number
}

/**
 * Mock embedding service for frontend prototype
 * Uses simple text-based similarity (TF-IDF-like) as placeholder
 * Production: Replace with backend API call to CMC embedding service
 */
export class MessageEmbeddingService {
  private config: Required<EmbeddingServiceConfig>
  private cache: Map<string, { embedding: number[]; contentHash: string; timestamp: Date }>
  
  constructor(config: EmbeddingServiceConfig = {}) {
    this.config = {
      modelName: config.modelName || 'all-MiniLM-L6-v2',
      dimension: config.dimension || 384,
      useMock: config.useMock !== false, // Default to mock
      apiUrl: config.apiUrl || '',
      cacheSize: config.cacheSize || 1000,
      batchSize: config.batchSize || 32
    }
    this.cache = new Map()
  }
  
  /**
   * Generate embedding for a single message
   * Mock: Uses simple text-based vector
   * Production: Call backend API
   */
  async embedMessage(message: ChatMessage): Promise<number[]> {
    // Check cache
    const cached = this.getCached(message.id)
    if (cached) {
      const contentHash = this.hashContent(message.content)
      const cachedEntry = this.cache.get(message.id)
      if (cachedEntry?.contentHash === contentHash) {
        return cached
      }
    }
    
    // Generate embedding
    let embedding: number[]
    if (this.config.useMock) {
      embedding = this.mockEmbed(message.content)
    } else {
      embedding = await this.realEmbed(message.content)
    }
    
    // Cache
    this.setCache(message.id, embedding, this.hashContent(message.content))
    
    return embedding
  }
  
  /**
   * Generate embeddings for multiple messages (batch)
   */
  async embedBatch(messages: ChatMessage[]): Promise<Map<string, number[]>> {
    const results = new Map<string, number[]>()
    
    // Process in batches
    for (let i = 0; i < messages.length; i += this.config.batchSize) {
      const batch = messages.slice(i, i + this.config.batchSize)
      const batchResults = await Promise.all(
        batch.map(async msg => {
          const embedding = await this.embedMessage(msg)
          return { id: msg.id, embedding }
        })
      )
      
      batchResults.forEach(({ id, embedding }) => {
        results.set(id, embedding)
      })
    }
    
    return results
  }
  
  /**
   * Generate embedding for a query string
   */
  async embedQuery(query: string): Promise<number[]> {
    if (this.config.useMock) {
      return this.mockEmbed(query)
    } else {
      return await this.realEmbed(query)
    }
  }
  
  /**
   * Check if embedding is cached
   */
  isCached(messageId: string): boolean {
    return this.cache.has(messageId)
  }
  
  /**
   * Get cached embedding
   */
  getCached(messageId: string): number[] | null {
    const cached = this.cache.get(messageId)
    return cached ? cached.embedding : null
  }
  
  /**
   * Clear embedding cache
   */
  clearCache(): void {
    this.cache.clear()
  }
  
  /**
   * Mock embedding: Simple text-based vector
   * Uses word frequency and simple normalization
   */
  private mockEmbed(text: string): number[] {
    // Simple mock: Create a vector from text characteristics
    // This is NOT a real embedding, just a placeholder
    const words = text.toLowerCase().split(/\s+/).filter(w => w.length > 2)
    const wordFreq = new Map<string, number>()
    
    words.forEach(word => {
      wordFreq.set(word, (wordFreq.get(word) || 0) + 1)
    })
    
    // Create a simple vector (not real semantic embedding)
    const vector: number[] = new Array(this.config.dimension).fill(0)
    const uniqueWords = Array.from(wordFreq.keys())
    
    // Distribute word frequencies across dimensions
    uniqueWords.forEach((word, idx) => {
      const dim = idx % this.config.dimension
      vector[dim] += wordFreq.get(word)! / words.length
    })
    
    // Normalize
    const norm = Math.sqrt(vector.reduce((sum, v) => sum + v * v, 0))
    if (norm > 0) {
      return vector.map(v => v / norm)
    }
    
    return vector
  }
  
  /**
   * Real embedding: Call backend API
   * TODO: Implement when backend API is available
   */
  private async realEmbed(text: string): Promise<number[]> {
    if (!this.config.apiUrl) {
      throw new Error('API URL not configured for real embeddings')
    }
    
    // TODO: Call backend API
    // const response = await fetch(`${this.config.apiUrl}/embed`, {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify({ text })
    // })
    // const data = await response.json()
    // return data.embedding
    
    // Fallback to mock for now
    return this.mockEmbed(text)
  }
  
  /**
   * Hash content for cache invalidation
   */
  private hashContent(content: string): string {
    // Simple hash (not cryptographic, just for cache invalidation)
    let hash = 0
    for (let i = 0; i < content.length; i++) {
      const char = content.charCodeAt(i)
      hash = ((hash << 5) - hash) + char
      hash = hash & hash // Convert to 32-bit integer
    }
    return hash.toString(36)
  }
  
  /**
   * Set cache entry
   */
  private setCache(messageId: string, embedding: number[], contentHash: string): void {
    // Evict oldest if cache is full
    if (this.cache.size >= this.config.cacheSize) {
      const oldestKey = this.cache.keys().next().value
      this.cache.delete(oldestKey)
    }
    
    this.cache.set(messageId, {
      embedding,
      contentHash,
      timestamp: new Date()
    })
  }
}

// Singleton instance
let embeddingServiceInstance: MessageEmbeddingService | null = null

/**
 * Get singleton embedding service instance
 */
export function getEmbeddingService(config?: EmbeddingServiceConfig): MessageEmbeddingService {
  if (!embeddingServiceInstance) {
    embeddingServiceInstance = new MessageEmbeddingService(config)
  }
  return embeddingServiceInstance
}

