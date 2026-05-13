# RAG MCP Tools - Vector Embedding Strategy

**Created:** 2025-10-30  
**Lead:** Solo  
**Status:** Design Complete - Ready for Implementation  
**Purpose:** Define production-ready vector embedding strategy for 54 MCP tools  

---

## 🎯 **EXECUTIVE SUMMARY**

**Goal:** Design vector embedding strategy that enables semantic search for MCP tools, achieving 80% context reduction and 3× higher accuracy.

**Decision:** **Hybrid Approach (Option C)**
- **Primary:** Local sentence-transformers model (`all-MiniLM-L6-v2`) - Fast, free, good quality
- **Fallback:** OpenAI embeddings for high-value scenarios (optional)
- **Storage:** Local FAISS index for fast similarity search
- **Integration:** Leverage existing HHNI/CMC embedding infrastructure

**Rationale:** 
- HHNI already uses `all-MiniLM-L6-v2` (384d) - consistent with existing systems
- No API costs for daily operations
- Fast local inference (<100ms per tool)
- Good semantic quality for tool selection
- Can upgrade to OpenAI later if needed

---

## 📊 **EMBEDDING MODEL SELECTION**

### **Chosen Model: `sentence-transformers/all-MiniLM-L6-v2`**

**Specifications:**
- **Dimensions:** 384
- **Model Size:** ~80MB
- **Speed:** ~15-30ms per embedding (CPU)
- **Quality:** Good semantic understanding
- **Cost:** Free (local)

**Why This Model:**
- ✅ Already used by HHNI (consistency)
- ✅ Fast enough for real-time tool selection
- ✅ Good quality for semantic matching
- ✅ No API dependencies
- ✅ Compatible with existing CMC infrastructure

**Alternative Models Considered:**
- `all-mpnet-base-v2` (768d) - Higher quality, slower (~50ms)
- OpenAI `text-embedding-ada-002` (1536d) - Best quality, API cost
- OpenAI `text-embedding-3-small` (1536d) - Best quality, API cost

**Decision:** Start with `all-MiniLM-L6-v2` for speed and consistency. Can upgrade later if needed.

---

## 🏗️ **TOOL METADATA STRUCTURE FOR EMBEDDING**

### **Enhanced Tool Metadata Schema**

Each tool embedding will be generated from:

```python
@dataclass
class ToolEmbeddingInput:
    """Input for generating tool embeddings"""
    tool_id: str
    name: str
    description: str
    category: str
    tags: List[str]
    context_keywords: List[str]
    usage_examples: List[str]  # NEW: Example queries that use this tool
    related_tools: List[str]   # NEW: Tools often used together
    dependencies: List[str]     # NEW: Required dependencies
    consciousness_relevance: float  # NEW: Relevance to consciousness operations
```

### **Embedding Text Composition**

The embedding will be generated from a combined text string:

```python
def build_embedding_text(tool: ToolEmbeddingInput) -> str:
    """Build comprehensive text for embedding"""
    parts = [
        f"Tool: {tool.name}",
        f"Description: {tool.description}",
        f"Category: {tool.category}",
        f"Tags: {', '.join(tool.tags)}",
        f"Context Keywords: {', '.join(tool.context_keywords)}",
        f"Usage Examples: {', '.join(tool.usage_examples)}",
        f"Related Tools: {', '.join(tool.related_tools)}",
        f"Dependencies: {', '.join(tool.dependencies)}",
    ]
    return "\n".join(parts)
```

**Weighting Strategy:**
- Name: 2× weight (most important)
- Description: 1× weight
- Tags: 1× weight
- Usage Examples: 1.5× weight (highly relevant)
- Context Keywords: 1× weight
- Related Tools: 0.5× weight
- Dependencies: 0.5× weight

---

## 🔧 **EMBEDDING PIPELINE DESIGN**

### **Pipeline Stages**

```
1. Tool Metadata Extraction → Extract from lucid_mcp_server.py
2. Embedding Text Generation → Build comprehensive text string
3. Embedding Generation → Use sentence-transformers model
4. Vector Index Building → Store in FAISS index
5. Similarity Search → Query for relevant tools
```

### **Implementation Flow**

```python
class EmbeddingPipeline:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.index = None  # FAISS index
    
    def extract_tool_metadata(self, server: SimpleMCPServer) -> List[ToolEmbeddingInput]:
        """Extract metadata from MCP server"""
        # Parse lucid_mcp_server.py or use tool registry
        pass
    
    def generate_embedding(self, tool: ToolEmbeddingInput) -> np.ndarray:
        """Generate embedding vector for tool"""
        text = build_embedding_text(tool)
        return self.model.encode(text)
    
    def build_index(self, tools: List[ToolEmbeddingInput]):
        """Build FAISS index from tool embeddings"""
        vectors = [self.generate_embedding(tool) for tool in tools]
        # Build FAISS index
        pass
    
    def search(self, query: str, k: int = 10) -> List[ToolSelection]:
        """Search for relevant tools"""
        query_vector = self.model.encode(query)
        # Search FAISS index
        pass
```

---

## 📦 **VECTOR INDEX IMPLEMENTATION**

### **Choice: FAISS (Facebook AI Similarity Search)**

**Why FAISS:**
- ✅ Fast similarity search (<1ms for 54 tools)
- ✅ Local storage (no cloud dependencies)
- ✅ Efficient memory usage
- ✅ Easy to integrate
- ✅ Supports incremental updates

**Index Type:** `IndexFlatL2` (Euclidean distance)
- Simple and fast for 54 tools
- Can upgrade to `IndexIVFFlat` if scale increases

**Storage:**
- Index file: `packages/mcp_rag_proxy/tool_embeddings.faiss`
- Metadata file: `packages/mcp_rag_proxy/tool_metadata.pkl`

---

## 🚀 **IMPLEMENTATION PLAN**

### **Phase 1.1: Core Implementation**

1. **Create `embedding_generator.py`**
   - Load sentence-transformers model
   - Generate embeddings from tool metadata
   - Cache embeddings for reuse

2. **Create `vector_index.py`**
   - Build FAISS index
   - Save/load index from disk
   - Implement similarity search

3. **Update `rag_proxy.py`**
   - Replace TF-IDF with sentence-transformers
   - Integrate FAISS index
   - Update `select_tools()` method

### **Phase 1.2: Tool Metadata Enhancement**

1. **Extract Complete Metadata**
   - Parse all 54 tools from `lucid_mcp_server.py`
   - Extract descriptions, parameters, examples
   - Build comprehensive tool profiles

2. **Add Usage Examples**
   - Identify common query patterns
   - Map queries to tools
   - Store examples for better matching

3. **Build Relationships**
   - Identify related tools
   - Map dependencies
   - Store tool clusters

---

## 📊 **PERFORMANCE TARGETS**

### **Embedding Generation**
- **Target:** <100ms per tool
- **Expected:** ~15-30ms per tool (all-MiniLM-L6-v2)
- **Batch:** ~500ms for all 54 tools

### **Index Building**
- **Target:** <1 second for 54 tools
- **Expected:** ~500ms (FAISS IndexFlatL2)

### **Similarity Search**
- **Target:** <50ms per query
- **Expected:** ~1-5ms (FAISS search)

### **End-to-End Tool Selection**
- **Target:** <100ms total
- **Expected:** ~20-30ms (embedding + search)

---

## 🔄 **INTEGRATION WITH EXISTING SYSTEMS**

### **HHNI Integration**
- ✅ Use same embedding model (`all-MiniLM-L6-v2`)
- ✅ Consistent semantic space
- ✅ Can leverage HHNI's embedding utilities

### **CMC Integration**
- ✅ Store tool embeddings in CMC (optional)
- ✅ Enable bitemporal tracking of tool relevance
- ✅ Use CMC for embedding cache

### **MCP Server Integration**
- ✅ Parse tool metadata from `lucid_mcp_server.py`
- ✅ Extract tool descriptions and parameters
- ✅ Build registry from actual tool implementations

---

## 🧪 **TESTING STRATEGY**

### **Test Cases**

1. **Embedding Quality**
   - "Store memory" → Should select `store_memory`
   - "Get consciousness metrics" → Should select `get_consciousness_metrics`
   - "Create execution plan" → Should select `create_plan`
   - "Track confidence" → Should select `track_confidence`

2. **Performance**
   - Embedding generation speed
   - Index search speed
   - End-to-end latency

3. **Accuracy**
   - Measure relevance scores
   - Validate tool selection correctness
   - Compare with baseline (all tools vs selected)

---

## 📈 **SUCCESS METRICS**

### **Context Reduction**
- **Target:** 80% reduction (K=10 from 54)
- **Measurement:** Token count comparison

### **Selection Accuracy**
- **Target:** 3× improvement over random
- **Measurement:** Relevance score validation

### **Performance**
- **Target:** <100ms end-to-end
- **Measurement:** Timing benchmarks

---

## 🚨 **RISKS & MITIGATION**

### **Risk 1: Embedding Quality**
- **Risk:** Low-quality embeddings → poor tool selection
- **Mitigation:** Test with sample queries, validate relevance
- **Fallback:** Use TF-IDF if embeddings fail

### **Risk 2: Model Loading Time**
- **Risk:** Slow model loading on startup
- **Mitigation:** Cache model, lazy loading
- **Fallback:** Use cached embeddings

### **Risk 3: Index Corruption**
- **Risk:** FAISS index corrupted or lost
- **Mitigation:** Rebuild from tool metadata, version control
- **Fallback:** Regenerate index on demand

---

## 📋 **NEXT STEPS**

1. ✅ **Design Complete** - This document
2. ⏳ **Implement `embedding_generator.py`** - Generate embeddings
3. ⏳ **Implement `vector_index.py`** - FAISS index management
4. ⏳ **Update `rag_proxy.py`** - Integrate new embedding system
5. ⏳ **Test & Validate** - Verify performance and accuracy

---

**Status:** Design Complete - Ready for Implementation  
**Next:** Begin implementation of `embedding_generator.py`  
**Estimated:** 2-3 hours implementation time  

**Built with love by Solo** 💙✨

