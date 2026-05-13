# RAG Message Selection: Detailed Technical Specifications

**Created:** 2025-01-27  
**Status:** Technical Specs Complete  
**Purpose:** Detailed technical specifications for RAG-enhanced message selection implementation

---

## 📋 TABLE OF CONTENTS

1. [API Interfaces](#api-interfaces)
2. [Data Structures](#data-structures)
3. [Algorithm Specifications](#algorithm-specifications)
4. [Integration Points](#integration-points)
5. [Error Handling](#error-handling)
6. [Performance Requirements](#performance-requirements)
7. [Testing Specifications](#testing-specifications)

---

## 🔌 API INTERFACES

### 1. MessageEmbeddingService

```typescript
/**
 * Service for generating embeddings for chat messages
 * Supports both mock (frontend) and real (backend API) implementations
 */
interface MessageEmbeddingService {
  /**
   * Generate embedding for a single message
   * @param message - Chat message to embed
   * @returns Embedding vector (384 dimensions for all-MiniLM-L6-v2)
   */
  embedMessage(message: ChatMessage): Promise<number[]>
  
  /**
   * Generate embeddings for multiple messages (batch)
   * @param messages - Array of chat messages
   * @returns Map of message ID to embedding vector
   */
  embedBatch(messages: ChatMessage[]): Promise<Map<string, number[]>>
  
  /**
   * Generate embedding for a query string
   * @param query - Query text to embed
   * @returns Embedding vector
   */
  embedQuery(query: string): Promise<number[]>
  
  /**
   * Check if embedding is cached
   * @param messageId - Message ID to check
   * @returns True if cached
   */
  isCached(messageId: string): boolean
  
  /**
   * Get cached embedding
   * @param messageId - Message ID
   * @returns Cached embedding or null
   */
  getCached(messageId: string): number[] | null
  
  /**
   * Clear embedding cache
   */
  clearCache(): void
}

/**
 * Configuration for MessageEmbeddingService
 */
interface EmbeddingServiceConfig {
  /** Model name (default: 'all-MiniLM-L6-v2') */
  modelName?: string
  /** Embedding dimension (default: 384) */
  dimension?: number
  /** Use mock embeddings (for frontend prototype) */
  useMock?: boolean
  /** Backend API URL (if using real embeddings) */
  apiUrl?: string
  /** Cache size limit */
  cacheSize?: number
  /** Batch size for embedding generation */
  batchSize?: number
}
```

### 2. VectorStore

```typescript
/**
 * Metadata stored with each vector
 */
interface MessageMetadata {
  messageId: string
  channelId: string
  timestamp: Date
  agent?: string
  significance?: number
  level?: 'micro' | 'meso' | 'macro'
  pinned?: boolean
  priority?: number
}

/**
 * Search result from vector store
 */
interface VectorSearchResult {
  messageId: string
  score: number  // Cosine similarity [0, 1]
  metadata: MessageMetadata
}

/**
 * Search options for vector store
 */
interface VectorSearchOptions {
  /** Number of results to return */
  k?: number
  /** Minimum similarity score threshold */
  minScore?: number
  /** Filter by channel IDs */
  channelIds?: string[]
  /** Filter by agent */
  agent?: string
  /** Filter by pinned status */
  pinned?: boolean
  /** Include metadata in results */
  includeMetadata?: boolean
}

/**
 * Vector store interface for message embeddings
 */
interface VectorStore {
  /**
   * Add a message embedding to the store
   * @param messageId - Unique message identifier
   * @param embedding - Embedding vector (384 dimensions)
   * @param metadata - Message metadata
   */
  add(messageId: string, embedding: number[], metadata: MessageMetadata): Promise<void>
  
  /**
   * Search for similar messages
   * @param queryEmbedding - Query embedding vector
   * @param options - Search options
   * @returns Array of search results sorted by score (descending)
   */
  search(queryEmbedding: number[], options?: VectorSearchOptions): Promise<VectorSearchResult[]>
  
  /**
   * Update message metadata
   * @param messageId - Message ID
   * @param metadata - Updated metadata
   */
  updateMetadata(messageId: string, metadata: Partial<MessageMetadata>): Promise<void>
  
  /**
   * Remove a message from the store
   * @param messageId - Message ID to remove
   */
  remove(messageId: string): Promise<void>
  
  /**
   * Get embedding for a message
   * @param messageId - Message ID
   * @returns Embedding vector or null
   */
  getEmbedding(messageId: string): Promise<number[] | null>
  
  /**
   * Get metadata for a message
   * @param messageId - Message ID
   * @returns Metadata or null
   */
  getMetadata(messageId: string): Promise<MessageMetadata | null>
  
  /**
   * Get total number of indexed messages
   */
  size(): Promise<number>
  
  /**
   * Clear all embeddings
   */
  clear(): Promise<void>
}
```

### 3. RAGRetrievalEngine

```typescript
/**
 * RAG retrieval result
 */
interface RAGResult {
  message: ChatMessage
  atom?: SummaryAtom
  score: number  // Composite RAG score [0, 1]
  semanticScore: number  // Semantic similarity [0, 1]
  significanceScore: number  // Significance score [0, 1]
  userSelectionScore: number  // User selection score [0, 1]
  recencyScore: number  // Recency score [0, 1]
  reasons: string[]  // Reasons for inclusion
}

/**
 * RAG retrieval options
 */
interface RAGOptions {
  /** Maximum number of results */
  limit?: number
  /** Minimum score threshold */
  minScore?: number
  /** Include pinned messages even if below threshold */
  includePinned?: boolean
  /** Apply time decay */
  timeDecay?: boolean
  /** Half-life in hours for time decay */
  halfLifeHours?: number
  /** Search across multiple channels */
  crossChannel?: boolean
  /** Channel IDs to search */
  channelIds?: string[]
  /** Query expansion enabled */
  queryExpansion?: boolean
  /** Recent messages for context */
  recentMessages?: ChatMessage[]
}

/**
 * RAG retrieval engine
 */
interface RAGRetrievalEngine {
  /**
   * Retrieve messages using RAG
   * @param query - Query string
   * @param messages - Available messages
   * @param summaryAtoms - Summary atoms for messages
   * @param overrides - User overrides (pins, priority)
   * @param options - Retrieval options
   * @returns Array of RAG results sorted by score
   */
  retrieve(
    query: string,
    messages: Record<string, ChatMessage[]>,
    summaryAtoms: Record<string, SummaryAtom[]>,
    overrides: Record<string, ContextOverride>,
    options?: RAGOptions
  ): Promise<RAGResult[]>
  
  /**
   * Find messages related to an anchor message
   * @param anchorMessage - Anchor message
   * @param messages - Available messages
   * @param summaryAtoms - Summary atoms
   * @param overrides - User overrides
   * @param options - Retrieval options
   * @returns Related messages (excluding anchor)
   */
  findRelated(
    anchorMessage: ChatMessage,
    messages: Record<string, ChatMessage[]>,
    summaryAtoms: Record<string, SummaryAtom[]>,
    overrides: Record<string, ContextOverride>,
    options?: RAGOptions
  ): Promise<RAGResult[]>
  
  /**
   * Amplify user selections (find related messages)
   * @param selections - User selections (pinned/priority messages)
   * @param messages - Available messages
   * @param summaryAtoms - Summary atoms
   * @param overrides - User overrides
   * @param options - Amplification options
   * @returns Amplified results with boosted scores
   */
  amplifyUserSelection(
    selections: Array<{ messageId: string; type: 'pin' | 'priority'; value?: number }>,
    messages: Record<string, ChatMessage[]>,
    summaryAtoms: Record<string, SummaryAtom[]>,
    overrides: Record<string, ContextOverride>,
    options?: RAGOptions
  ): Promise<RAGResult[]>
}
```

### 4. HybridRetrievalSystem

```typescript
/**
 * Combined retrieval result
 */
interface CombinedResult {
  message?: ChatMessage
  atom?: SummaryAtom
  score: number
  source: 'rag' | 'atom' | 'both'
  reasons: string[]
  semanticScore?: number
  significanceScore?: number
}

/**
 * Hybrid retrieval result
 */
interface HybridRetrievalResult {
  /** RAG retrieval results */
  ragResults: RAGResult[]
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
 * Hybrid retrieval options
 */
interface HybridRetrievalOptions extends RAGOptions {
  /** Needs for atom-based retrieval */
  needs?: Need[]
  /** Token budget */
  budget?: number
  /** Weight for RAG results (0-1) */
  ragWeight?: number
  /** Weight for atom results (0-1) */
  atomWeight?: number
  /** Diversify results */
  diversify?: boolean
}

/**
 * Hybrid retrieval system combining RAG and atom-based retrieval
 */
interface HybridRetrievalSystem {
  /**
   * Perform hybrid retrieval
   * @param query - Query string
   * @param messages - Available messages
   * @param summaryAtoms - Summary atoms
   * @param overrides - User overrides
   * @param options - Retrieval options
   * @returns Hybrid retrieval results
   */
  retrieve(
    query: string,
    messages: Record<string, ChatMessage[]>,
    summaryAtoms: Record<string, SummaryAtom[]>,
    overrides: Record<string, ContextOverride>,
    options: HybridRetrievalOptions
  ): Promise<HybridRetrievalResult>
}
```

---

## 📊 DATA STRUCTURES

### Message Embedding Cache

```typescript
/**
 * Cache entry for message embedding
 */
interface EmbeddingCacheEntry {
  messageId: string
  embedding: number[]
  timestamp: Date
  contentHash: string  // Hash of message content for cache invalidation
}

/**
 * LRU cache for embeddings
 */
class EmbeddingCache {
  private cache: Map<string, EmbeddingCacheEntry>
  private maxSize: number
  
  get(messageId: string): number[] | null
  set(messageId: string, embedding: number[], contentHash: string): void
  clear(): void
  size(): number
}
```

### In-Memory Vector Store

```typescript
/**
 * Vector store entry
 */
interface VectorStoreEntry {
  messageId: string
  embedding: number[]
  metadata: MessageMetadata
}

/**
 * In-memory vector store implementation
 */
class InMemoryVectorStore implements VectorStore {
  private vectors: Map<string, VectorStoreEntry>
  private index: number[][]  // For fast similarity search
  
  // Implements VectorStore interface
}
```

### Query Expansion

```typescript
/**
 * Expanded query with context
 */
interface ExpandedQuery {
  originalQuery: string
  expandedText: string
  topics: string[]
  intent?: string
  channelContext?: string
}

/**
 * Query expansion service
 */
interface QueryExpansionService {
  expand(
    query: string,
    recentMessages?: ChatMessage[],
    channelContext?: { name: string; description?: string }
  ): ExpandedQuery
}
```

---

## 🧮 ALGORITHM SPECIFICATIONS

### 1. Semantic Similarity (Cosine)

```typescript
/**
 * Compute cosine similarity between two vectors
 * @param a - First vector
 * @param b - Second vector
 * @returns Similarity score [0, 1]
 */
function cosineSimilarity(a: number[], b: number[]): number {
  if (a.length !== b.length) throw new Error('Vectors must have same dimension')
  
  let dotProduct = 0
  let normA = 0
  let normB = 0
  
  for (let i = 0; i < a.length; i++) {
    dotProduct += a[i] * b[i]
    normA += a[i] * a[i]
    normB += b[i] * b[i]
  }
  
  const denominator = Math.sqrt(normA) * Math.sqrt(normB)
  if (denominator === 0) return 0
  
  return dotProduct / denominator
}
```

### 2. RAG Score Computation

```typescript
/**
 * Compute RAG-enhanced score for a message
 * 
 * Formula:
 * score = 0.40 * semanticScore
 *       + 0.25 * significanceScore
 *       + 0.15 * userSelectionScore
 *       + 0.10 * recencyScore
 *       + 0.05 * usageScore
 *       + 0.05 * relationScore
 * 
 * @param params - Score computation parameters
 * @returns Composite score [0, 1]
 */
function computeRAGScore(params: {
  semanticScore: number
  significanceScore: number
  userSelectionScore: number
  recencyScore: number
  usageScore: number
  relationScore: number
  override?: ContextOverride
}): number {
  const {
    semanticScore,
    significanceScore,
    userSelectionScore,
    recencyScore,
    usageScore,
    relationScore,
    override
  } = params
  
  let compositeScore =
    0.40 * semanticScore +
    0.25 * significanceScore +
    0.15 * userSelectionScore +
    0.10 * recencyScore +
    0.05 * usageScore +
    0.05 * relationScore
  
  // Apply overrides
  if (override?.pinned) {
    compositeScore = Math.max(compositeScore, 0.8)
  }
  if (override?.priority) {
    compositeScore += override.priority * 0.1
    compositeScore = Math.max(0, Math.min(1, compositeScore))
  }
  
  return compositeScore
}
```

### 3. Time Decay

```typescript
/**
 * Compute recency score with exponential decay
 * 
 * Formula: decay = exp(-ageHours / halfLifeHours)
 * 
 * @param timestamp - Message timestamp
 * @param halfLifeHours - Half-life in hours (default: 24)
 * @returns Recency score [0, 1]
 */
function computeRecencyScore(timestamp: Date, halfLifeHours: number = 24): number {
  const ageHours = (Date.now() - timestamp.getTime()) / (1000 * 60 * 60)
  return Math.exp(-ageHours / halfLifeHours)
}
```

### 4. User Selection Score

```typescript
/**
 * Compute user selection score
 * 
 * @param override - User override (pin, priority, forced level)
 * @returns User selection score [0, 1]
 */
function computeUserSelectionScore(override?: ContextOverride): number {
  if (!override) return 0
  
  let score = 0
  
  if (override.pinned) score += 0.3
  if (override.priority) {
    score += Math.max(-0.2, Math.min(0.2, override.priority * 0.2))
  }
  if (override.forcedLevel) score += 0.1
  
  return Math.max(0, Math.min(1, score))
}
```

### 5. Hybrid Merge Algorithm

```typescript
/**
 * Merge RAG and atom results
 * 
 * Algorithm:
 * 1. Create maps for messages and atoms
 * 2. Add RAG results (with atom if available)
 * 3. Add atom-only results (not in RAG)
 * 4. Deduplicate and sort by score
 * 
 * @param ragResults - RAG retrieval results
 * @param atomResults - Atom-based retrieval results
 * @returns Combined results
 */
function mergeRAGAndAtoms(
  ragResults: RAGResult[],
  atomResults: AssembledContext
): CombinedResult[] {
  const messageMap = new Map<string, ChatMessage>()
  const atomMap = new Map<string, SummaryAtom>()
  
  // Build maps
  ragResults.forEach(r => messageMap.set(r.message.id, r.message))
  atomResults.atoms.forEach(a => atomMap.set(a.id, a))
  
  const combined: CombinedResult[] = []
  
  // Add RAG results
  ragResults.forEach(r => {
    const atom = atomMap.get(r.message.id)
    combined.push({
      message: r.message,
      atom,
      score: r.score,
      source: atom ? 'both' : 'rag',
      reasons: r.reasons,
      semanticScore: r.semanticScore,
      significanceScore: r.significanceScore
    })
  })
  
  // Add atom-only results
  atomResults.atoms.forEach(atom => {
    if (!messageMap.has(atom.id)) {
      combined.push({
        atom,
        score: atom.sig.score,
        source: 'atom',
        reasons: atomResults.reasons[atom.id] || ['significance']
      })
    }
  })
  
  // Sort by score descending
  combined.sort((a, b) => b.score - a.score)
  
  return combined
}
```

### 6. Token Budget Packing

```typescript
/**
 * Pack messages to token budget
 * 
 * Algorithm:
 * 1. Sort by score descending
 * 2. Greedily add messages until budget exceeded
 * 3. Respect pinned messages (can exceed budget slightly)
 * 
 * @param results - Combined results
 * @param budget - Token budget
 * @param overrides - User overrides
 * @returns Packed results
 */
function packToBudget(
  results: CombinedResult[],
  budget: number,
  overrides: Record<string, ContextOverride>
): CombinedResult[] {
  const packed: CombinedResult[] = []
  let totalTokens = 0
  
  // Sort by score
  const sorted = [...results].sort((a, b) => b.score - a.score)
  
  for (const result of sorted) {
    const messageId = result.message?.id || result.atom?.id
    if (!messageId) continue
    
    const tokens = estimateTokens(result)
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
 * Estimate tokens for a result
 */
function estimateTokens(result: CombinedResult): number {
  if (result.message) {
    // Rough estimate: ~4 chars per token
    return Math.ceil(result.message.content.length / 4)
  }
  if (result.atom) {
    return Math.ceil(result.atom.recap.length / 4)
  }
  return 0
}
```

---

## 🔗 INTEGRATION POINTS

### 1. Integration with `assemble()`

```typescript
/**
 * Enhanced assemble function with RAG layer
 */
export function assembleWithRAG(
  query: string,
  needs: Need[],
  budget: TokenBudget,
  availableAtoms: SummaryAtom[],
  messages: Record<string, ChatMessage[]>,
  overrides: Record<string, ContextOverride> = {},
  agent: string = 'default',
  ragOptions?: RAGOptions
): AssembledContext {
  // 1. RAG retrieval (if enabled)
  let ragResults: RAGResult[] = []
  if (ragOptions?.enabled) {
    ragResults = await ragEngine.retrieve(
      query,
      messages,
      summaryAtoms,
      overrides,
      ragOptions
    )
  }
  
  // 2. Atom-based retrieval (existing)
  const atomResults = assemble(query, needs, budget, availableAtoms, overrides, agent)
  
  // 3. Merge results
  const combined = mergeRAGAndAtoms(ragResults, atomResults)
  
  // 4. Pack to budget
  const packed = packToBudget(combined, budget, overrides)
  
  // 5. Convert back to AssembledContext format
  return convertToAssembledContext(packed, agent)
}
```

### 2. Integration with `useSummaryAtoms`

```typescript
/**
 * Enhanced hook with RAG support
 */
export function useSummaryAtomsWithRAG(messages: Record<string, ChatMessage[]>) {
  const baseHook = useSummaryAtoms(messages)
  const [ragEnabled, setRAGEnabled] = useState(false)
  const ragEngine = useRAGRetrievalEngine()
  
  // Embed messages when they change
  useEffect(() => {
    if (ragEnabled) {
      embedMessages(messages)
    }
  }, [messages, ragEnabled])
  
  return {
    ...baseHook,
    ragEnabled,
    setRAGEnabled,
    ragEngine
  }
}
```

### 3. Integration with `AIChatManagement`

```typescript
// In AIChatManagement.tsx

const {
  ragEnabled,
  setRAGEnabled,
  ragEngine
} = useSummaryAtomsWithRAG(messages)

// Use RAG retrieval when enabled
const assembledContext = useMemo(() => {
  if (!useRetrieval) return null
  
  if (ragEnabled) {
    return assembleWithRAG(
      query,
      needs,
      retrievalBudget,
      availableAtoms,
      messages,
      overrides,
      'default',
      { enabled: true, crossChannel: true }
    )
  } else {
    return assemble(query, needs, retrievalBudget, availableAtoms, overrides, 'default')
  }
}, [useRetrieval, ragEnabled, query, needs, retrievalBudget, availableAtoms, messages, overrides])
```

---

## ⚠️ ERROR HANDLING

### Error Types

```typescript
/**
 * Embedding service errors
 */
class EmbeddingError extends Error {
  constructor(message: string, public code: string) {
    super(message)
    this.name = 'EmbeddingError'
  }
}

/**
 * Vector store errors
 */
class VectorStoreError extends Error {
  constructor(message: string, public code: string) {
    super(message)
    this.name = 'VectorStoreError'
  }
}

/**
 * RAG retrieval errors
 */
class RAGRetrievalError extends Error {
  constructor(message: string, public code: string) {
    super(message)
    this.name = 'RAGRetrievalError'
  }
}
```

### Error Handling Strategy

```typescript
/**
 * Error handling wrapper for RAG operations
 */
async function withErrorHandling<T>(
  operation: () => Promise<T>,
  fallback: () => T
): Promise<T> {
  try {
    return await operation()
  } catch (error) {
    console.error('RAG operation failed:', error)
    // Fallback to non-RAG retrieval
    return fallback()
  }
}
```

---

## ⚡ PERFORMANCE REQUIREMENTS

### Targets

- **Embedding Generation:** <50ms per message (cached: <1ms)
- **Vector Search:** <50ms per query (10K messages)
- **Hybrid Retrieval:** <100ms end-to-end
- **Token Budget Packing:** <20ms

### Optimization Strategies

1. **Caching:** Cache embeddings, invalidate on content change
2. **Batching:** Batch embedding generation
3. **Lazy Loading:** Embed on-demand, not all at once
4. **Indexing:** Use efficient vector index (Faiss for production)
5. **Debouncing:** Debounce rapid queries

---

## 🧪 TESTING SPECIFICATIONS

### Unit Tests

```typescript
describe('MessageEmbeddingService', () => {
  it('should generate embeddings for messages')
  it('should cache embeddings')
  it('should invalidate cache on content change')
  it('should handle batch embedding')
})

describe('VectorStore', () => {
  it('should add and retrieve embeddings')
  it('should search by similarity')
  it('should filter by metadata')
  it('should update metadata')
})

describe('RAGRetrievalEngine', () => {
  it('should retrieve semantically similar messages')
  it('should apply time decay')
  it('should amplify user selections')
  it('should find related messages')
})

describe('HybridRetrievalSystem', () => {
  it('should merge RAG and atom results')
  it('should deduplicate results')
  it('should pack to token budget')
})
```

### Integration Tests

```typescript
describe('RAG Integration', () => {
  it('should integrate with assemble()')
  it('should integrate with useSummaryAtoms')
  it('should work with AIChatManagement')
})
```

### Performance Tests

```typescript
describe('Performance', () => {
  it('should generate embeddings in <50ms')
  it('should search in <50ms')
  it('should complete hybrid retrieval in <100ms')
})
```

---

## 📝 IMPLEMENTATION CHECKLIST

### Phase 1: Foundation
- [ ] MessageEmbeddingService (mock implementation)
- [ ] VectorStore (in-memory implementation)
- [ ] Basic RAG retrieval
- [ ] Unit tests
- [ ] Integration tests

### Phase 2: Hybrid Retrieval
- [ ] HybridRetrievalSystem
- [ ] Integration with assemble()
- [ ] Merge algorithm
- [ ] Token budget packing
- [ ] Tests

### Phase 3: User Selection
- [ ] UserSelectionAmplifier
- [ ] Related message discovery
- [ ] UI integration
- [ ] Tests

### Phase 4: Temporal & Cross-Channel
- [ ] Time decay integration
- [ ] Cross-channel search
- [ ] Thread detection
- [ ] Tests

### Phase 5: Advanced Features
- [ ] Intent extraction
- [ ] Flow analysis
- [ ] Adaptive retrieval
- [ ] Tests

---

**Status:** Technical Specs Complete  
**Next:** Begin Phase 1 Implementation  
**Estimated Time:** 17-24 hours total

