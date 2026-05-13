# RAG-Enhanced Message Selection for AI Chat

## Overview
Enhance the AI chat context selection system with RAG (Retrieval-Augmented Generation) to intelligently choose which chat messages to include in context, combining semantic relevance with user selections and temporal signals.

## Current System Analysis

### Existing Retrieval (`assemble()`)
- **Input**: SummaryAtoms (structured data from messages)
- **Scoring**: 
  - 45% significance score
  - 25% semantic similarity (simple word matching)
  - 15% relationship boost
  - 10% recency boost
  - 5% pin boost
- **Limitations**:
  - Simple token-based similarity (word matching, not semantic)
  - Works on summary atoms, not raw messages
  - No embedding-based semantic search
  - Limited cross-channel context

## RAG Enhancement Design

### 1. **Message-Level RAG Retrieval**

**Goal**: Use semantic embeddings to find relevant messages based on current conversation context.

**Implementation**:
```typescript
interface RAGMessageRetrieval {
  // Embed messages as they're created
  embedMessage(message: ChatMessage): Promise<Embedding>
  
  // Query for relevant messages
  retrieveRelevantMessages(
    query: string,  // Current user input or conversation context
    channelIds: string[],  // Channels to search
    options: {
      limit: number
      minScore: number
      includePinned: boolean
      timeDecay: boolean
    }
  ): Promise<Array<{
    message: ChatMessage
    score: number
    reasons: string[]
  }>>
}
```

**Scoring Formula**:
```
finalScore = 
  0.40 * semanticRelevance (RAG embedding similarity)
  + 0.25 * significance (existing atom score)
  + 0.15 * userSelection (pins, forced, priority)
  + 0.10 * recency (time decay)
  + 0.10 * relationshipBoost (typed relationships)
```

### 2. **Hybrid Retrieval Strategy**

**Combine RAG with existing system**:
- **RAG Layer**: Find semantically relevant messages using embeddings
- **Atom Layer**: Use existing summary atom system for structured data
- **Merge**: Combine both results, deduplicate, diversify

**Flow**:
```
User Input → RAG Query
  ↓
1. Embed user input
2. Search message embeddings (semantic similarity)
3. Search summary atoms (structured data)
4. Merge & score combined results
5. Apply user selections (pins, priority)
6. Apply time decay
7. Pack to token budget
```

### 3. **User Selection Integration**

**Enhance user selections with RAG**:
- **Pinned Messages**: Always included, but RAG can find related unpinned messages
- **Priority Boost**: RAG can find messages related to high-priority ones
- **Forced Level**: User can force message inclusion, RAG finds related context
- **Selection History**: Track which messages user expands/views, boost their relevance

**Example**:
```typescript
// User pins message about "authentication"
// RAG finds related messages about:
// - "login flow"
// - "session management" 
// - "password reset"
// All get boosted relevance
```

### 4. **Temporal Context with RAG**

**Time-aware RAG**:
- **Recent Messages**: Higher weight in RAG search
- **Conversation Threads**: RAG identifies related message threads
- **Context Windows**: Use RAG to find relevant context from different time periods

**Time Decay Formula**:
```typescript
timeDecay = Math.exp(-ageInHours / halfLife)
ragScore = semanticScore * (0.7 + 0.3 * timeDecay)
```

### 5. **Cross-Channel RAG**

**Find relevant messages across channels**:
- When user asks in "ui-building", RAG can find relevant messages from:
  - "ui-research" (related research)
  - "backend-building" (related backend work)
  - "ui-debugging" (related issues)

**Multi-Channel Query**:
```typescript
// User in "ui-building" asks: "How do we handle errors?"
// RAG searches across:
// - ui-building (current channel)
// - ui-debugging (error handling)
// - backend-building (API error responses)
// Returns most relevant from all channels
```

### 6. **Query Expansion**

**Enhance RAG queries**:
- **Current Input**: User's current message
- **Conversation Context**: Last N messages for context
- **Channel Context**: Channel description, recent topics
- **User Intent**: Extract intent from conversation flow

**Query Building**:
```typescript
function buildRAGQuery(
  currentInput: string,
  recentMessages: ChatMessage[],
  channelContext: Channel
): string {
  // Extract key concepts from recent messages
  const recentTopics = extractTopics(recentMessages.slice(-5))
  
  // Combine with current input
  return `${currentInput} ${recentTopics.join(' ')} ${channelContext.description}`
}
```

## Implementation Plan

### Phase 1: Basic RAG Integration
1. Add embedding generation for messages
2. Create vector store for message embeddings
3. Implement semantic search
4. Integrate with existing `assemble()` function

### Phase 2: User Selection Enhancement
1. Boost RAG scores based on user selections
2. Find related messages for pinned/priority messages
3. Track selection history

### Phase 3: Temporal & Cross-Channel
1. Add time decay to RAG scores
2. Implement cross-channel RAG search
3. Thread detection and grouping

### Phase 4: Advanced Features
1. Query expansion
2. Intent extraction
3. Conversation flow analysis
4. Adaptive retrieval (learn from user behavior)

## Technical Considerations

### Embedding Model
- **Option 1**: Use existing LLM API (OpenAI, Anthropic) for embeddings
- **Option 2**: Local embedding model (sentence-transformers)
- **Option 3**: Hybrid (local for speed, API for quality)

### Vector Store
- **Option 1**: In-memory (simple, fast, limited scale)
- **Option 2**: CMC integration (persistent, scalable)
- **Option 3**: External vector DB (Pinecone, Weaviate, Qdrant)

### Performance
- **Lazy Embedding**: Generate embeddings on-demand, cache results
- **Batch Processing**: Embed messages in batches
- **Incremental Updates**: Only re-embed new/changed messages

### Cost Optimization
- **Caching**: Cache embeddings and search results
- **Selective Embedding**: Only embed messages above significance threshold
- **Compression**: Use smaller embedding dimensions for older messages

## Benefits

1. **Better Context Selection**: Semantic understanding vs. simple word matching
2. **User Intent Awareness**: Understand what user is asking about
3. **Cross-Channel Intelligence**: Find relevant context across channels
4. **Adaptive**: Learns from user selections and behavior
5. **Scalable**: Works with large message histories

## Example Use Cases

### Use Case 1: Related Context Discovery
**User**: "How did we fix the authentication bug?"
**RAG**: Finds messages about:
- Original bug report
- Debugging steps
- Fix implementation
- Related authentication changes
**Result**: Complete context chain, not just recent messages

### Use Case 2: Cross-Channel Relevance
**User in "ui-building"**: "What's the API endpoint for user data?"
**RAG**: Finds relevant messages from:
- "backend-building" (API implementation)
- "ui-research" (API research)
- "backend-debugging" (API issues)
**Result**: Cross-channel context without manual channel switching

### Use Case 3: User Selection Amplification
**User**: Pins message about "error handling"
**RAG**: Automatically finds and suggests related messages:
- Error logging implementation
- Error recovery strategies
- Related error cases
**Result**: User selection amplifies to find related context

## Next Steps

1. **Prototype**: Start with simple embedding-based search
2. **Integrate**: Combine with existing `assemble()` function
3. **Test**: Validate with real conversation data
4. **Iterate**: Refine scoring and retrieval based on results

