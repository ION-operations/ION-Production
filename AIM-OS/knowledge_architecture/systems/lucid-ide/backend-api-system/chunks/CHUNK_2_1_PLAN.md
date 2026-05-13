# Chunk 2.1: Implement ICIP Semantic Search

**Phase:** 2 (Core Algorithms)  
**Chunk:** 2.1  
**Duration:** 3 days (24 hours)  
**Priority:** P0-1 (CRITICAL - Biggest False Claim)  
**Status:** READY TO START ⏳

---

## 🎯 **GOAL**

Replace case-insensitive grep with REAL semantic search using sentence-transformers embeddings and FAISS vector search.

**Why This Is Critical:**
- Currently claiming "semantic search" but it's just grep
- This is a FALSE CAPABILITY CLAIM
- ICIP is supposed to be flagship code search feature
- Need embeddings for actual semantic understanding

**Success Criteria:**
- Code embedded using sentence-transformers
- FAISS index for fast vector search
- Semantic queries return relevant results (not just literal matches)
- "login" query finds "authenticate" code
- Comprehensive tests (90%+ coverage for this feature)

---

## 🎭 **APOE WORKFLOW**

### **Role 1: RETRIEVER (Research) - 3 hours**
**Task:** Research implementation approaches

**Activities:**
1. Study HHNI embedding implementation (`packages/hhni/semantic_search.py`)
2. Review sentence-transformers documentation
3. Research FAISS index types and usage
4. Find code chunking strategies
5. Review existing embedding patterns in project

**Outputs:**
- Understanding of HHNI's approach
- sentence-transformers usage patterns
- FAISS index selection
- Code chunking strategy

**Validation:**
- [ ] Understand HHNI's embedding approach
- [ ] Know how to use sentence-transformers
- [ ] FAISS index type selected
- [ ] Chunking strategy defined

---

### **Role 2: REASONER (Design) - 3 hours**
**Task:** Design semantic search architecture

**Activities:**
1. Design code chunking algorithm (function-level? class-level?)
2. Design embedding generation pipeline
3. Design FAISS index structure
4. Design search algorithm
5. Design caching strategy
6. Plan incremental index updates

**Outputs:**
- Complete design document
- Architecture diagram
- API contracts
- Performance estimates

**Validation:**
- [ ] Chunking algorithm clear
- [ ] Embedding pipeline designed
- [ ] Index structure defined
- [ ] Search algorithm specified

---

### **Role 3: BUILDER (Implementation) - 12 hours**
**Task:** Implement semantic search

**Day 1 (6 hours):**
1. Create `packages/icip_search/` package structure
2. Implement code embedder (sentence-transformers integration)
3. Implement code chunker (extract functions/classes)
4. Write unit tests for embedder and chunker

**Day 2 (6 hours):**
5. Implement FAISS index wrapper
6. Implement semantic search engine
7. Integrate with MCP tool in `lucid_mcp_server.py`
8. Update TypeScript service if needed
9. Write unit tests for search engine

**Outputs:**
- `packages/icip_search/semantic_engine.py` (~300 lines)
- `packages/icip_search/code_embedder.py` (~200 lines)
- `packages/icip_search/code_chunker.py` (~150 lines)
- `packages/icip_search/faiss_index.py` (~150 lines)
- Updated MCP tool integration
- Unit tests (~200 lines)

**Validation:**
- [ ] All files created
- [ ] Code compiles/runs
- [ ] Basic search works
- [ ] Tests written

---

### **Role 4: OPERATOR (Execution) - 2 hours**
**Task:** Run tests and verify

**Activities:**
1. Install dependencies (sentence-transformers, faiss-cpu)
2. Run unit tests
3. Run integration test
4. Generate coverage report
5. Fix any failures

**Outputs:**
- All tests passing
- Coverage report (target: 90%+)

**Validation:**
- [ ] Tests run successfully
- [ ] All tests passing
- [ ] 90%+ coverage
- [ ] Performance acceptable (<500ms)

---

### **Role 5: VERIFIER (Validation) - 3 hours**
**Task:** Validate semantic search works correctly

**Activities:**
1. Test with real queries
   - "authentication functions" → finds auth-related code
   - "login" → finds "authenticate" (synonym matching!)
   - "React hooks for API" → finds relevant hooks
   
2. Compare results: semantic vs literal
   - Verify semantic finds relevant code literal misses
   - Verify relevance ranking makes sense
   
3. Performance validation
   - Measure search time
   - Verify <500ms target
   
4. Edge case testing
   - Empty query
   - Very long query
   - No results
   - Large codebase

**Outputs:**
- Validation report
- Performance benchmarks
- Edge case results

**Validation:**
- [ ] Semantic actually works (not grep!)
- [ ] Synonym matching demonstrated
- [ ] Performance acceptable
- [ ] Edge cases handled

---

### **Role 6: WITNESS** (Documentation) - 1 hour
**Task:** Document implementation

**Activities:**
1. Update L3 with implementation details
2. Create implementation notes
3. Document design decisions
4. Update placeholder registry (P0-1 complete)
5. Create chunk completion report

**Outputs:**
- Updated L3_detailed.md
- `CHUNK_2_1_COMPLETE.md`
- Updated `MASTER_PROGRESS_TRACKER.md`
- Updated `PLACEHOLDER_REGISTRY.md`

---

## 📦 **DELIVERABLES**

### **Python Implementation:**
```
packages/icip_search/
├── __init__.py              # Package init
├── semantic_engine.py       # Main search engine (300 lines)
├── code_embedder.py         # sentence-transformers wrapper (200 lines)
├── code_chunker.py          # Extract functions/classes (150 lines)
├── faiss_index.py           # FAISS wrapper (150 lines)
└── config.py                # Configuration

tests/
└── unit/
    └── icip_search/
        ├── test_code_embedder.py
        ├── test_code_chunker.py
        ├── test_semantic_engine.py
        └── test_faiss_index.py
```

### **Integration:**
- Updated `lucid_mcp_server.py` `icip_search` method
- Uses new semantic engine instead of grep

### **TypeScript:**
- `ICIPSearchService.ts` unchanged (wrapper already good)

### **Documentation:**
- Updated L3 Section 4.2 with implementation
- CHUNK_2_1_COMPLETE.md
- Updated trackers

**Total:** ~1,200 lines code + ~400 lines tests + docs

---

## ✅ **VALIDATION CRITERIA**

### **Must Pass:**
1. **Semantic Search Works:**
   - [ ] "login" finds "authenticate" code
   - [ ] Synonym matching demonstrated
   - [ ] Relevance ranking sensible
   - [ ] NOT using grep/literal matching

2. **Performance:**
   - [ ] Search time <500ms for typical codebase
   - [ ] Index generation acceptable
   - [ ] Memory usage reasonable

3. **Quality:**
   - [ ] 90%+ test coverage
   - [ ] All tests passing
   - [ ] Edge cases handled
   - [ ] Error messages clear

4. **Integration:**
   - [ ] MCP tool returns semantic results
   - [ ] TypeScript service works unchanged
   - [ ] CMC integration functional
   - [ ] End-to-end flow validated

5. **Documentation:**
   - [ ] L3 updated with implementation
   - [ ] Design decisions documented
   - [ ] Performance benchmarks recorded
   - [ ] Known limitations documented

---

## ⏱️ **TIME ALLOCATION**

| Role | Activity | Hours |
|------|----------|-------|
| Retriever | Research | 3h |
| Reasoner | Design | 3h |
| Builder | Implement | 12h |
| Operator | Run tests | 2h |
| Verifier | Validate | 3h |
| Witness | Document | 1h |
| **TOTAL** | | **24h** |

**Estimated:** 3 working days (8h each)  
**Realistic:** 3 days

---

## 🎯 **TECHNICAL APPROACH**

### **Embedding Model:**
Use `sentence-transformers/all-MiniLM-L6-v2` (384d)
- Same as HHNI (consistency!)
- Fast (~30ms per embedding)
- Good quality for code
- Free (local inference)

### **Code Chunking:**
Extract at function/class level:
```python
def chunk_code(file_path: str) -> List[CodeChunk]:
    # Parse with tree-sitter or ast module
    # Extract: functions, classes, methods
    # Return: {name, code, start_line, end_line}
```

### **Indexing:**
```python
# 1. Chunk all code
chunks = chunk_codebase(codebase_path)

# 2. Generate embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode([chunk.code for chunk in chunks])

# 3. Store in FAISS
index = faiss.IndexFlatL2(384)
index.add(embeddings)

# 4. Persist index
faiss.write_index(index, "icip_index.faiss")
```

### **Searching:**
```python
# 1. Embed query
query_embedding = model.encode(query)

# 2. Search FAISS
distances, indices = index.search(query_embedding, k=20)

# 3. Return results with relevance scores
results = [
    {
        'chunk': chunks[i],
        'relevance': 1.0 / (1.0 + distances[j])
    }
    for j, i in enumerate(indices[0])
]
```

---

## 🚀 **SUCCESS DEFINITION**

**Chunk Complete When:**
- Real semantic search implemented (not grep!)
- Can demonstrate synonym matching
- Tests passing (90%+ coverage)
- Performance validated (<500ms)
- Documentation updated
- P0-1 placeholder removed from registry

**This fixes the biggest false claim in the system!** ✅

---

**Status:** ⏳ READY TO START  
**Prerequisites:** Phase 1 complete ✅  
**Confidence:** 0.88 (Complex but clear path)  
**Impact:** HIGH (fixes major false claim)

Let's build real semantic search! 🚀


