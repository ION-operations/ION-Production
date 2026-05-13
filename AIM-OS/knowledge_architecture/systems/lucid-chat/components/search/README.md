# Search Services Component

**Component of:** Lucid Chat System  
**Purpose:** Multi-provider search with aggregation and synthesis  
**Status:** Framework 90%, Implementation varies (40-90%)

---

## 🎯 **Quick Context (50 words)**

Search services integrate 5 providers: DEEPSEARCH (sovereign 9-layer intelligence), ICIP (3-tier code search), Perplexity (AI web search), Tavily (research), Web (fallback). SearchOrchestrator executes parallel searches, aggregates results, deduplicates, ranks by relevance, and synthesizes via SEG. Auto-configured by thinking modes.

---

## 📦 **Files & Structure**

```
search/
├── DeepSearchService.ts      # DEEPSEARCH wrapper (90%)
├── ICIPSearchService.ts      # Code search wrapper (90%)
└── SearchOrchestrator.ts     # Multi-provider orchestration (90%)
```

**Backend:**
```
packages/deepsearch/
└── __init__.py               # DEEPSEARCH engine (40% - needs algorithms)

packages/icip_search/         # NEEDED
├── semantic_engine.py        # Embeddings + FAISS
├── code_embedder.py          # Code → vectors
└── ast_parser.py             # Structural search
```

**Total:** 3 frontend files (done), 4 backend files (2 needed)

---

## 🔧 **Key Classes**

### **DeepSearchService**
```typescript
class DeepSearchService {
  async search(request: DeepSearchRequest): Promise<APIResponse<DeepSearchResult>>
  async quickWebSearch(query: string): Promise<...>
  async deepResearch(topic: string, depth: number): Promise<...>
}
```

**Status:** Wrapper 90%, backend 40%

### **ICIPSearchService**
```typescript
class ICIPSearchService {
  async semanticSearch(query: string): Promise<...>
  async literalSearch(query: string): Promise<...>
  async findFunction(name: string): Promise<...>
  async findClass(name: string): Promise<...>
}
```

**Status:** Wrapper 90%, semantic tier 30% (NOT SEMANTIC!)

### **SearchOrchestrator**
```typescript
class SearchOrchestrator {
  async search(request: UnifiedSearchRequest): Promise<UnifiedSearchResult>
  private aggregateResults(results): any[]
  private synthesizeResults(results): any
}
```

**Status:** 90% (depends on providers)

---

## 📊 **Usage Example**

```typescript
// Multi-provider search
const orchestrator = getSearchOrchestrator()

const result = await orchestrator.search({
  query: 'React performance optimization',
  providers: ['deepsearch', 'icip', 'perplexity'],
  depth: 'comprehensive',
  synthesize: true,
})

// Returns:
// - results.deepsearch: Web + filesystem results
// - results.icip: Code search results
// - results.perplexity: AI search results
// - aggregated: Deduplicated, ranked
// - synthesis: SEG knowledge summary
```

---

## ⚠️ **Critical Issues**

**Issue 1: ICIP NOT Semantic** 🚨
- Claims "semantic search" but uses `query.lower() in line.lower()`
- No embeddings, no vectors, no FAISS
- **FALSE CAPABILITY CLAIM**
- **Fix:** Implement sentence-transformers + FAISS (3 days)

**Issue 2: DEEPSEARCH Backend Placeholder** 🚨
- Trust scoring algorithm missing
- Shannon entropy not implemented
- No web crawler
- No master index
- **Fix:** Implement 4 modules (5 days)

**Tests:** 0 / ~35 needed

---

## 🎯 **Integration Points**

**Upstream:**
- CMC - Store search results
- HHNI - Use for semantic search (ICIP)
- SEG - Synthesize results
- MCP Tools - Call via Command Server

**Downstream:**
- AdvancedLLMService - Deep search feature
- ARDService - Multi-source gathering
- Thinking modes - Auto-configure providers/depth

---

## 🚀 **Next Steps**

1. **ICIP:** Implement real semantic search (3 days)
   - sentence-transformers for embeddings
   - FAISS for vector search
   - Code chunking and embedding
   
2. **DEEPSEARCH:** Complete backend (5 days)
   - Trust scoring algorithm
   - Shannon entropy calculation
   - Web crawler with robots.txt respect
   - SQLite master index
   
3. **Tests:** Comprehensive suite (2 days)

**Effort to Production:** ~10 days

---

**Parent:** [../../L2_architecture.md](../../L2_architecture.md)  
**Implementation:** `ide_orchestration/prototypes/dac/src/services/lucid-chat/search/`

