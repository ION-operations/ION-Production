# Cross-Document Relationships - Narrative Context & Symbolic Meaning

**Component of:** HHNI  
**Type:** Relationship Component  
**Purpose:** Detect semantic relationships across documents  
**Status:** ✅ Fully Implemented (Phase 2 of Semantic Organization Enhancement)

---

## 🎯 **Quick Context (100 words)**

Cross-Document Relationship Detector identifies semantic relationships across documents, enabling narrative context tracking and symbolic meaning accumulation. Detects semantic similarity (embedding-based), narrative context (story-level relationships), and symbolic links (meaning over time). Creates cross-document relations in SEG graph using 5 new relation types: SEMANTICALLY_RELATED, NARRATIVE_CONTEXT, SYMBOLIC_LINK, CO_OCCURS_WITH, ACCUMULATES_MEANING. Enables understanding of how concepts evolve across documents and how narrative context accumulates. Integrated into `build_hhni_for_atom()` via `cross_document_relationships.py`. Requires SEG graph. Optional integration (backward compatible).

---

## 📊 **Context Budget Guide**

**4k:** This README  
**8k:** [L1_overview.md](L1_overview.md) - Relationship types and detection  
**32k:** [L2_architecture.md](L2_architecture.md) - Implementation details  
**200k+:** L3-L5 + relationship-specific docs

---

## 📦 **Relationship Types**

### **SEMANTICALLY_RELATED**
**Purpose:** General semantic similarity across documents  
**Example:** "river" in doc1 semantically related to "water" in doc2  
**Detection:** Embedding-based similarity (threshold: 0.75)  
**Use Case:** Find semantically similar concepts across documents

### **NARRATIVE_CONTEXT**
**Purpose:** Story-level relationships  
**Example:** "river bank" in doc1 → "love" in doc2 (narrative context)  
**Detection:** Narrative coherence analysis (threshold: 0.80)  
**Use Case:** Track narrative context and story-level relationships

### **SYMBOLIC_LINK**
**Purpose:** Symbolic meaning connections  
**Example:** "river" as symbol for "flow of time" across documents  
**Detection:** Symbolic pattern recognition (threshold: 0.75)  
**Use Case:** Track symbolic meaning and metaphorical connections

### **CO_OCCURS_WITH**
**Purpose:** Co-occurrence in context  
**Example:** "authentication" and "authorization" co-occur in multiple docs  
**Detection:** Co-occurrence frequency analysis  
**Use Case:** Find concepts that frequently appear together

### **ACCUMULATES_MEANING**
**Purpose:** Meaning accumulation over time  
**Example:** "consciousness" meaning deepens across multiple documents  
**Detection:** Temporal meaning evolution analysis  
**Use Case:** Track how concepts gain meaning over time

---

## 🔧 **How It Works**

**Relationship Detection:**
```
Source Entity (Doc 1)
    ↓
Compute Embedding
    ↓
Compare with Target Entities (Doc 2+)
    ↓
Calculate Similarity Scores
    ↓
Apply Thresholds
    ↓
Create SEG Relations
    ↓
Store in SEG Graph
```

**Narrative Context Tracking:**
```
Story Elements Identified
    ↓
Track Narrative Threads
    ↓
Identify Context Shifts
    ↓
Create NARRATIVE_CONTEXT Relations
```

**Symbolic Meaning Accumulation:**
```
Symbolic Patterns Detected
    ↓
Track Meaning Evolution
    ↓
Identify Symbolic Links
    ↓
Create SYMBOLIC_LINK Relations
```

---

## 📊 **Detection Parameters**

**Similarity Thresholds:**
- Semantic similarity: 0.75 (default)
- Narrative context: 0.80 (default)
- Symbolic links: 0.75 (default)

**Configuration:**
```python
CrossDocumentRelationshipDetector(
    seg_graph: SEGraph,
    similarity_threshold: float = 0.75,
    narrative_threshold: float = 0.80,
)
```

---

## 🔗 **Relationships**

**Cross-Document Detector uses:**
- SEG graph (relation storage)
- Embeddings (semantic similarity)
- HHNI nodes (source entities)

**Cross-Document Detector enables:**
- Narrative context tracking
- Symbolic meaning accumulation
- Cross-document semantic relationships
- Meaning evolution over time

---

## 📈 **Metrics**

**Detection Quality:**
- Relationship accuracy (true positives)
- False positive rate
- Narrative coherence score
- Symbolic pattern recognition accuracy

**Performance:**
- Detection latency
- Relationship creation time
- SEG graph update time

---

## 🔧 **Implementation**

**File:** `packages/hhni/cross_document_relationships.py` (~350 lines)  
**Tests:** `packages/hhni/tests/test_cross_document_relationships.py` (7 test cases)  
**Status:** ✅ Complete, production-ready

**Key Functions:**
- `detect_semantic_relationships()` - Find semantic similarities
- `track_narrative_context()` - Identify story-level relationships
- `accumulate_symbolic_meaning()` - Track meaning over time
- `add_cross_doc_relations()` - Create SEG relations

**Integration:**
- Integrated into `build_hhni_for_atom()` (optional parameter)
- Requires SEG graph for relation storage
- Backward compatible (works without SEG, but no relations created)

**SEG Integration:**
- Creates 5 new relation types in SEG graph
- Stores relationship metadata
- Enables cross-document querying

---

## 📚 **Detail Levels**

**L0:** This README  
**L1-L5:** Architecture docs (to create)

**Sub-components:**
- [detection/semantic/](detection/semantic/) - Semantic similarity detection
- [detection/narrative/](detection/narrative/) - Narrative context tracking
- [detection/symbolic/](detection/symbolic/) - Symbolic meaning detection
- [detection/cooccurrence/](detection/cooccurrence/) - Co-occurrence analysis
- [detection/accumulation/](detection/accumulation/) - Meaning accumulation

---

## 🎯 **Key Concepts**

**Cross-Document:** Relationships span multiple documents  
**Narrative Context:** Story-level relationships and context  
**Symbolic Meaning:** Metaphorical and symbolic connections  
**Meaning Accumulation:** Concepts gain meaning over time  
**SEG Integration:** Relations stored in SEG graph

---

**Parent:** [../../README.md](../../README.md)  
**Siblings:** [../morphological_analysis/](../morphological_analysis/), [../semantic_blocks/](../semantic_blocks/)  
**Implementation:** `packages/hhni/cross_document_relationships.py`  
**Status:** ✅ Production-ready, tested

