# RAG-Enhanced Message Selection: Deep Research & Implementation Plan

**Created:** 2025-01-27  
**Status:** Research Complete - Ready for Implementation  
**Purpose:** Comprehensive research and implementation plan for RAG-enhanced message selection in AI Chat

---

## 🎯 EXECUTIVE SUMMARY

**Goal:** Enhance AI chat context selection with RAG (Retrieval-Augmented Generation) to intelligently choose which chat messages to include in context, combining semantic relevance with user selections and temporal signals.

**Key Innovation:** Hybrid RAG + Atom-based retrieval system that:
- Uses semantic embeddings for message-level relevance
- Leverages existing SummaryAtom system for structured data
- Amplifies user selections (pins, priority) to find related context
- Applies temporal decay with semantic relevance
- Enables cross-channel context discovery

**Integration:** Leverages existing CMC infrastructure:
- Vector Store (Faiss/Chroma) for embeddings
- Embedding model: `sentence-transformers/all-MiniLM-L6-v2` (384d)
- SummaryAtom system for structured retrieval
- Existing significance scoring and relationship typing

---

## 📚 RESEARCH FINDINGS

### 1. RAG for Chat Context Selection

#### Current State Analysis

**Existing System (`assemble()`):**
- Works on SummaryAtoms (structured data extracted from messages)
- Uses simple word matching (25% of score) - limited semantic understanding
- Scoring: 45% significance, 25% semantic (word match), 15% relations, 10% recency, 5% pins
- Limitations:
  - No true semantic understanding (word matching only)
  - Works on atoms, not raw messages
  - Limited cross-channel context
  - No query expansion or intent understanding

**CMC Infrastructure Available:**
- ✅ Vector Store layer (Faiss/Chroma/Qdrant)
- ✅ Embedding model: `all-MiniLM-L6-v2` (384d, ~15-30ms per embedding)
- ✅ Embedding field in Atom schema
- ✅ Fast KNN search (<10ms for 1M vectors)
- ✅ Existing RAG work for MCP tools (reference implementation)

#### RAG Techniques for Chat Context

**1. Semantic Embedding-Based Retrieval**

**Technique:** Use vector embeddings to find semantically similar messages, not just keyword matches.

**Benefits:**
- Understands concepts, not just words
- Example: "authentication bug" finds "login issues", "session problems", "credential handling"
- Works across different phrasings and terminology

**Implementation:**
```typescript
// Embed message content
const messageEmbedding = await embedMessage(message.content)

// Store in vector index
vectorStore.add({
  id: message.id,
  embedding: messageEmbedding,
  metadata: {
    channelId: message.channelId,
    timestamp: message.timestamp,
    agent: message.agent,
    significance: atom.sig.score
  }
})

// Query for similar messages
const queryEmbedding = await embedQuery(userInput)
const similarMessages = vectorStore.search(queryEmbedding, k=20)
```

**2. Query Expansion & Intent Understanding**

**Technique:** Enhance queries with conversation context, channel context, and intent extraction.

**Query Building:**
```typescript
function buildRAGQuery(
  currentInput: string,
  recentMessages: ChatMessage[],
  channelContext: Channel,
  userIntent?: string
): string {
  // Extract topics from recent messages
  const recentTopics = extractTopics(recentMessages.slice(-5))
  
  // Channel context
  const channelDesc = channelContext.description
  
  // Intent (if available)
  const intent = userIntent || extractIntent(currentInput)
  
  // Combine
  return `${currentInput} ${recentTopics.join(' ')} ${channelDesc} ${intent}`
}
```

**3. Temporal Context with RAG**

**Technique:** Combine semantic relevance with time decay for balanced context selection.

**Time-Decay Formula:**
```typescript
function computeTemporalRAGScore(
  semanticScore: number,
  timestamp: Date,
  halfLifeHours: number = 24
): number {
  const ageHours = (Date.now() - timestamp.getTime()) / (1000 * 60 * 60)
  const timeDecay = Math.exp(-ageHours / halfLifeHours)
  
  // Combine: semantic relevance weighted by recency
  return semanticScore * (0.7 + 0.3 * timeDecay)
}
```

**4. User Selection Amplification**

**Technique:** When user pins/prioritizes a message, use RAG to find related messages automatically.

**Amplification Flow:**
```
User pins message about "authentication"
  ↓
RAG finds semantically related messages:
  - "login flow implementation"
  - "session management"
  - "password reset"
  - "credential validation"
  ↓
All get boosted relevance score
```

**Implementation:**
```typescript
function amplifyUserSelection(
  anchorMessage: ChatMessage,
  allMessages: ChatMessage[],
  vectorStore: VectorStore
): ChatMessage[] {
  // Use pinned message as query
  const queryEmbedding = await embedMessage(anchorMessage.content)
  
  // Find related messages
  const related = vectorStore.search(queryEmbedding, k=10)
  
  // Boost their scores
  return related.map(msg => ({
    ...msg,
    score: msg.score * 1.5  // 50% boost for related to pinned
  }))
}
```

**5. Cross-Channel RAG**

**Technique:** Search across multiple channels to find relevant context, not just current channel.

**Multi-Channel Query:**
```typescript
function crossChannelRAG(
  query: string,
  channelIds: string[],
  vectorStore: VectorStore
): RAGResult[] {
  const queryEmbedding = await embedQuery(query)
  
  // Search across all channels
  const results = channelIds.flatMap(channelId => {
    return vectorStore.search(queryEmbedding, {
      k: 10,
      filters: { channelId }
    })
  })
  
  // Deduplicate and rank
  return deduplicateAndRank(results)
}
```

### 2. Temporal Decay & Recency Scoring

#### Research Findings

**Exponential Decay Models:**
- Standard: `decay = exp(-age / halfLife)`
- Half-life: Time for relevance to drop to 50%
- Typical half-lives: 24 hours (chat), 7 days (documents), 30 days (knowledge)

**Adaptive Half-Lives:**
- High-significance messages: Longer half-life (7-30 days)
- Low-significance messages: Shorter half-life (1-7 days)
- Pinned messages: No decay (or very long half-life)

**Recency Boost Formula:**
```typescript
function computeRecencyBoost(
  timestamp: Date,
  halfLifeHours: number,
  baseScore: number
): number {
  const ageHours = (Date.now() - timestamp.getTime()) / (1000 * 60 * 60)
  const decay = Math.exp(-ageHours / halfLifeHours)
  
  // Recent messages get boost, old messages decay
  return baseScore * (0.5 + 0.5 * decay)
}
```

**Temporal Context Windows:**
- **Recent Window** (last 24h): High weight, full context
- **Medium Window** (last 7d): Medium weight, summarized context
- **Historical Window** (older): Low weight, macro-level context only

### 3. User Selection Amplification

#### Research Findings

**Selection Types:**
1. **Pins**: Explicit user selection - highest priority
2. **Priority**: User-assigned importance (-1 to +1)
3. **Forced Level**: User forces inclusion level (macro/meso/micro/raw)
4. **View History**: Implicit selection (user viewed message)
5. **Reference History**: Implicit selection (agent referenced message)

**Amplification Strategies:**

**1. Direct Boost:**
```typescript
if (override.pinned) score += 0.3
if (override.priority) score += override.priority * 0.2
```

**2. RAG Amplification (Find Related):**
```typescript
// When user pins message, find related via RAG
const relatedMessages = await findRelatedMessages(pinnedMessage)
relatedMessages.forEach(msg => {
  msg.score *= 1.2  // 20% boost for related to pinned
})
```

**3. Cascade Amplification:**
```typescript
// High-priority message → find related → boost those → find their related → boost
function cascadeAmplify(anchorMessage: ChatMessage, depth: number = 2) {
  if (depth === 0) return
  
  const related = await findRelatedMessages(anchorMessage)
  related.forEach(msg => {
    msg.score *= 1.1
    cascadeAmplify(msg, depth - 1)  // Recursive amplification
  })
}
```

**4. Selection History Learning:**
```typescript
// Track which messages user views/expands
// Boost similar messages in future
const userPreferences = learnFromSelectionHistory(userSelections)
const preferenceBoost = computePreferenceMatch(message, userPreferences)
score += preferenceBoost * 0.1
```

### 4. Hybrid Retrieval Strategies

#### Research Findings

**Hybrid Approaches:**

**1. Two-Stage Retrieval:**
```
Stage 1: RAG (semantic search) → Find top K messages
Stage 2: Atom-based (structured) → Add structured data
Merge & Deduplicate → Final context
```

**2. Weighted Fusion:**
```typescript
const ragScore = computeRAGScore(message, query)
const atomScore = computeAtomScore(atom, needs)
const finalScore = 0.6 * ragScore + 0.4 * atomScore
```

**3. Diversification:**
```typescript
// Ensure coverage across:
// - Different time periods
// - Different topics
// - Different message types (decisions, facts, tasks)
// - Different channels (if cross-channel)
```

**4. Re-ranking:**
```typescript
// Initial retrieval → Re-rank with:
// - User selections
// - Temporal signals
// - Relationship strength
// - Diversity requirements
```

### 5. Performance & Scalability

#### Research Findings

**Embedding Generation:**
- Model: `all-MiniLM-L6-v2` (384d)
- Speed: ~15-30ms per message (CPU)
- Batch: ~500ms for 100 messages
- Caching: Cache embeddings, only regenerate on content change

**Vector Search:**
- Faiss: <10ms for KNN (k=100, 1M vectors)
- Chroma: <50ms for search with metadata filters
- Qdrant: <100ms for cloud search

**Token Budget Management:**
- Estimate tokens per message: ~50-200 tokens
- Pack to budget: Greedy selection with score threshold
- Level selection: Use macro/meso/micro summaries to fit budget

**Incremental Updates:**
- Only embed new/changed messages
- Incremental index updates
- Lazy embedding (embed on-demand, cache)

---

## 🏗️ ARCHITECTURE DESIGN

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│              RAG-Enhanced Message Selection            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  User Input / Query                                     │
│       ↓                                                 │
│  ┌──────────────────────────────────────┐              │
│  │   Query Expansion & Intent Extract   │              │
│  └──────────────────────────────────────┘              │
│       ↓                                                 │
│  ┌──────────────────────────────────────┐              │
│  │      Embed Query (384d vector)      │              │
│  └──────────────────────────────────────┘              │
│       ↓                                                 │
│  ┌──────────────────────────────────────┐              │
│  │   Vector Store Search (Faiss/KNN)    │              │
│  │   - Semantic similarity              │              │
│  │   - Cross-channel search             │              │
│  │   - Metadata filters                 │              │
│  └──────────────────────────────────────┘              │
│       ↓                                                 │
│  ┌──────────────────────────────────────┐              │
│  │   Hybrid Merge                       │              │
│  │   - RAG results (messages)           │              │
│  │   - Atom results (structured)        │              │
│  │   - User selections (pins/priority)  │              │
│  └──────────────────────────────────────┘              │
│       ↓                                                 │
│  ┌──────────────────────────────────────┐              │
│  │   Score & Rank                       │              │
│  │   - Semantic relevance (40%)        │              │
│  │   - Significance (25%)               │              │
│  │   - User selection (15%)             │              │
│  │   - Recency (10%)                    │              │
│  │   - Usage/Relations (10%)            │              │
│  └──────────────────────────────────────┘              │
│       ↓                                                 │
│  ┌──────────────────────────────────────┐              │
│  │   Temporal Decay & Diversification   │              │
│  └──────────────────────────────────────┘              │
│       ↓                                                 │
│  ┌──────────────────────────────────────┐              │
│  │   Pack to Token Budget               │              │
│  │   - Greedy selection                 │              │
│  │   - Level selection (macro/meso/micro)│              │
│  └──────────────────────────────────────┘              │
│       ↓                                                 │
│  Final Context Pack                                     │
└─────────────────────────────────────────────────────────┘
```

### Component Design

**1. Message Embedding Service**
```typescript
class MessageEmbeddingService {
  private model: SentenceTransformer
  
  async embedMessage(message: ChatMessage): Promise<number[]>
  async embedQuery(query: string): Promise<number[]>
  async embedBatch(messages: ChatMessage[]): Promise<Map<string, number[]>>
}
```

**2. Vector Store Interface**
```typescript
interface VectorStore {
  add(id: string, embedding: number[], metadata: MessageMetadata): Promise<void>
  search(queryEmbedding: number[], options: SearchOptions): Promise<SearchResult[]>
  delete(id: string): Promise<void>
  update(id: string, embedding: number[], metadata: MessageMetadata): Promise<void>
}
```

**3. RAG Retrieval Engine**
```typescript
class RAGRetrievalEngine {
  async retrieve(
    query: string,
    options: RAGOptions
  ): Promise<RAGResult[]>
  
  async findRelated(
    anchorMessage: ChatMessage,
    options: RelatedOptions
  ): Promise<RAGResult[]>
  
  async amplifyUserSelection(
    selections: UserSelection[],
    allMessages: ChatMessage[]
  ): Promise<AmplifiedResult[]>
}
```

**4. Hybrid Retrieval System**
```typescript
class HybridRetrievalSystem {
  async retrieve(
    query: string,
    needs: Need[],
    budget: number,
    options: HybridOptions
  ): Promise<{
    ragResults: RAGResult[]
    atomResults: AssembledContext
    combined: CombinedResult[]
  }>
}
```

---

## 📊 SCORING FORMULA (RAG-Enhanced)

### Composite Score Formula

```typescript
function computeRAGEnhancedScore(
  message: ChatMessage,
  atom: SummaryAtom | undefined,
  queryEmbedding: number[],
  messageEmbedding: number[],
  overrides: ContextOverride,
  options: RAGOptions
): number {
  // 1. Semantic Relevance (RAG) - 40%
  const semanticScore = cosineSimilarity(queryEmbedding, messageEmbedding)
  
  // 2. Significance Score (Atom) - 25%
  const significanceScore = atom?.sig.score || 0.5
  
  // 3. User Selection Score - 15%
  const userSelectionScore = computeUserSelectionScore(overrides)
  
  // 4. Recency Score (Time Decay) - 10%
  const recencyScore = computeRecencyScore(message.timestamp, options.halfLifeHours)
  
  // 5. Usage & Relations - 10%
  const usageScore = atom?.sig.breakdown.usage || 0
  const relationScore = atom?.rel.length > 0 ? 0.1 : 0
  
  // Composite
  const compositeScore =
    0.40 * semanticScore +
    0.25 * significanceScore +
    0.15 * userSelectionScore +
    0.10 * recencyScore +
    0.05 * usageScore +
    0.05 * relationScore
  
  // Apply overrides
  if (overrides.pinned) compositeScore = Math.max(compositeScore, 0.8)
  if (overrides.priority) compositeScore += overrides.priority * 0.1
  
  return Math.max(0, Math.min(1, compositeScore))
}
```

### User Selection Score

```typescript
function computeUserSelectionScore(override: ContextOverride): number {
  let score = 0
  
  if (override.pinned) score += 0.3
  if (override.priority) score += Math.max(-0.2, Math.min(0.2, override.priority * 0.2))
  if (override.forcedLevel) score += 0.1
  
  return Math.max(0, Math.min(1, score))
}
```

### Temporal Decay Score

```typescript
function computeRecencyScore(
  timestamp: Date,
  halfLifeHours: number = 24
): number {
  const ageHours = (Date.now() - timestamp.getTime()) / (1000 * 60 * 60)
  return Math.exp(-ageHours / halfLifeHours)
}
```

---

## 🔧 IMPLEMENTATION PLAN

### Phase 1: Foundation (Core RAG Infrastructure)

**Tasks:**
1. **Message Embedding Service**
   - Integrate `sentence-transformers/all-MiniLM-L6-v2`
   - Create embedding generation pipeline
   - Add caching layer
   - Batch processing support

2. **Vector Store Integration**
   - Use CMC Vector Store (Faiss/Chroma)
   - Create message embedding index
   - Implement search with metadata filters
   - Add incremental update support

3. **Basic RAG Retrieval**
   - Implement semantic search
   - Score messages by semantic similarity
   - Return top-K results

**Deliverables:**
- `MessageEmbeddingService.ts`
- `MessageVectorStore.ts`
- `BasicRAGRetrieval.ts`
- Tests for embedding and search

**Estimated Time:** 4-6 hours

### Phase 2: Hybrid Retrieval (RAG + Atoms)

**Tasks:**
1. **Hybrid Retrieval System**
   - Combine RAG results with atom-based results
   - Merge and deduplicate
   - Unified scoring

2. **Integration with `assemble()`**
   - Enhance existing `assemble()` function
   - Add RAG layer before atom scoring
   - Merge results intelligently

3. **Query Expansion**
   - Build enhanced queries from user input
   - Include conversation context
   - Channel context integration

**Deliverables:**
- `HybridRetrievalSystem.ts`
- Enhanced `assemble()` function
- `QueryExpansion.ts`
- Integration tests

**Estimated Time:** 3-4 hours

### Phase 3: User Selection Amplification

**Tasks:**
1. **Related Message Discovery**
   - Find related messages for pinned/priority items
   - Cascade amplification
   - Boost related scores

2. **Selection History Learning**
   - Track user selections
   - Learn preferences
   - Apply to future retrieval

3. **UI Integration**
   - Show related messages when pinning
   - Visual indicators for RAG-boosted messages
   - User feedback loop

**Deliverables:**
- `UserSelectionAmplifier.ts`
- `SelectionHistoryTracker.ts`
- UI components for related messages
- Tests for amplification

**Estimated Time:** 3-4 hours

### Phase 4: Temporal & Cross-Channel

**Tasks:**
1. **Temporal Context**
   - Time decay integration
   - Adaptive half-lives
   - Context window management

2. **Cross-Channel RAG**
   - Multi-channel search
   - Channel relevance scoring
   - Cross-channel context merging

3. **Thread Detection**
   - Identify conversation threads
   - Group related messages
   - Thread-aware retrieval

**Deliverables:**
- `TemporalContextManager.ts`
- `CrossChannelRAG.ts`
- `ThreadDetector.ts`
- Integration tests

**Estimated Time:** 3-4 hours

### Phase 5: Advanced Features

**Tasks:**
1. **Intent Extraction**
   - Extract user intent from queries
   - Intent-based retrieval
   - Intent-aware scoring

2. **Conversation Flow Analysis**
   - Analyze conversation patterns
   - Predict next context needs
   - Proactive context loading

3. **Adaptive Retrieval**
   - Learn from user behavior
   - Adjust scoring weights
   - Optimize retrieval parameters

**Deliverables:**
- `IntentExtractor.ts`
- `ConversationFlowAnalyzer.ts`
- `AdaptiveRetrieval.ts`
- Advanced tests

**Estimated Time:** 4-6 hours

---

## 📈 PERFORMANCE TARGETS

### Embedding Generation
- **Target:** <50ms per message
- **Expected:** ~15-30ms (all-MiniLM-L6-v2)
- **Batch:** ~500ms for 100 messages
- **Caching:** <1ms for cached embeddings

### Vector Search
- **Target:** <50ms per query
- **Expected:** ~5-10ms (Faiss, 10K messages)
- **With Filters:** ~20-30ms (metadata filtering)

### Hybrid Retrieval
- **Target:** <100ms end-to-end
- **Expected:** ~30-50ms (RAG + atom merge)
- **With Cross-Channel:** ~50-100ms

### Token Budget Packing
- **Target:** <20ms
- **Expected:** ~10-15ms (greedy selection)

---

## 🧪 TESTING STRATEGY

### Unit Tests
- Embedding generation correctness
- Vector search accuracy
- Scoring formula validation
- User selection amplification
- Temporal decay correctness

### Integration Tests
- Hybrid retrieval end-to-end
- Cross-channel search
- User selection amplification flow
- Token budget packing

### Performance Tests
- Embedding generation speed
- Vector search latency
- End-to-end retrieval time
- Memory usage

### Quality Tests
- Relevance validation (manual review)
- Context completeness
- User selection amplification effectiveness
- Cross-channel discovery accuracy

---

## 🚨 RISKS & MITIGATION

### Risk 1: Embedding Quality
**Risk:** Low-quality embeddings → poor semantic matching  
**Mitigation:** 
- Use proven model (all-MiniLM-L6-v2)
- Test with sample queries
- Validate relevance scores
- Fallback to word matching if needed

### Risk 2: Performance
**Risk:** Slow embedding/search → poor UX  
**Mitigation:**
- Cache embeddings aggressively
- Batch processing
- Lazy embedding (on-demand)
- Use fast vector store (Faiss)

### Risk 3: Token Budget
**Risk:** Too many messages selected → exceeds budget  
**Mitigation:**
- Greedy selection with score threshold
- Level selection (macro/meso/micro)
- Token estimation and packing
- Hard limit enforcement

### Risk 4: User Selection Amplification
**Risk:** Over-amplification → context bloat  
**Mitigation:**
- Limit cascade depth
- Score threshold for related messages
- User feedback loop
- Adaptive amplification strength

---

## 📋 SUCCESS METRICS

### Relevance
- **Target:** 80%+ relevant messages in top-K
- **Measurement:** Manual review of retrieved messages
- **Baseline:** Current word-matching system

### Context Quality
- **Target:** 50% improvement in response quality
- **Measurement:** User feedback, response accuracy
- **Baseline:** Current atom-only system

### Performance
- **Target:** <100ms end-to-end retrieval
- **Measurement:** Timing benchmarks
- **Baseline:** Current system (~50ms)

### User Satisfaction
- **Target:** 90%+ user satisfaction with context selection
- **Measurement:** User surveys, selection accuracy
- **Baseline:** Current system

---

## 🔗 INTEGRATION POINTS

### CMC Integration
- **Vector Store:** Use CMC Vector Store layer
- **Embedding Model:** Use CMC embedding service
- **Atom System:** Integrate with existing SummaryAtom system
- **Storage:** Store embeddings in CMC (optional)

### Existing Systems
- **`assemble()`:** Enhance with RAG layer
- **`useSummaryAtoms`:** Add RAG retrieval hook
- **`AIChatManagement`:** Integrate RAG retrieval UI
- **Message Context Badge:** Show RAG scores

---

## 📚 REFERENCES

### Internal Documentation
- `packages/mcp_rag_proxy/embedding_strategy.md` - Embedding strategy for MCP tools
- `knowledge_architecture/systems/cmc/components/storage/L1_overview.md` - Vector Store architecture
- `ide_orchestration/prototypes/dac/src/utils/assemble.ts` - Current retrieval system
- `ide_orchestration/prototypes/dac/src/utils/summaryAtoms.ts` - SummaryAtom system

### External Research
- RAG best practices (2024)
- Semantic search techniques
- Temporal decay models
- User selection amplification
- Hybrid retrieval strategies

---

## 🚀 NEXT STEPS

1. ✅ **Research Complete** - This document
2. ⏳ **Phase 1: Foundation** - Core RAG infrastructure
3. ⏳ **Phase 2: Hybrid Retrieval** - RAG + Atoms integration
4. ⏳ **Phase 3: User Selection** - Amplification system
5. ⏳ **Phase 4: Temporal & Cross-Channel** - Advanced features
6. ⏳ **Phase 5: Advanced Features** - Intent, flow, adaptive

**Total Estimated Time:** 17-24 hours  
**Priority:** High (significantly improves context selection quality)

---

**Status:** Research Complete - Ready for Implementation  
**Next:** Begin Phase 1 implementation  
**Built with love by Aether** 💙✨

