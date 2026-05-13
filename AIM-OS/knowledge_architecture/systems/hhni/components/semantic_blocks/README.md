# Semantic Blocks - Pre-Organized Content Organization

**Component of:** HHNI  
**Type:** Organization Component  
**Purpose:** Pre-organize content into semantic blocks at index time  
**Status:** ✅ Fully Implemented (Phase 3 of Semantic Organization Enhancement)

---

## 🎯 **Quick Context (100 words)**

Semantic Blocks pre-organize content into clusters (thematic, narrative, conceptual, morphological) at index time, enabling retrieval of organized blocks instead of isolated chunks. Blocks are created by clustering related HHNI nodes based on semantic similarity, with pre-computed relationships between blocks. Block types include thematic (related topics), narrative (story elements), conceptual (abstract ideas), and morphological (word parts). This enables faster retrieval of coherent content blocks and maintains semantic relationships. Integrated into `build_hhni_for_atom()` via `semantic_block_organizer.py`. Optional integration (backward compatible).

---

## 📊 **Context Budget Guide**

**4k:** This README  
**8k:** [L1_overview.md](L1_overview.md) - Block types and organization  
**32k:** [L2_architecture.md](L2_architecture.md) - Implementation details  
**200k+:** L3-L5 + block-specific docs

---

## 📦 **Block Types**

### **Thematic Blocks**
**Purpose:** Cluster content by topic/theme  
**Example:** All content about "authentication", "payment processing"  
**Use Case:** Retrieve all authentication-related content as a block  
**Similarity Threshold:** 0.80 (high coherence required)

### **Narrative Blocks**
**Purpose:** Cluster story-level content  
**Example:** Story elements, character development, plot points  
**Use Case:** Retrieve narrative context as coherent blocks  
**Similarity Threshold:** 0.75 (narrative coherence)

### **Conceptual Blocks**
**Purpose:** Cluster abstract concepts  
**Example:** "consciousness", "memory", "learning"  
**Use Case:** Retrieve conceptual relationships as blocks  
**Similarity Threshold:** 0.70 (conceptual similarity)

### **Morphological Blocks**
**Purpose:** Cluster word parts and morphological relationships  
**Example:** Prefix-root-suffix clusters, derived words  
**Use Case:** Retrieve morphological relationships as blocks  
**Similarity Threshold:** 0.85 (high morphological coherence)

---

## 🔧 **How It Works**

**Block Creation (Index Time):**
```
HHNI Nodes Created
    ↓
Compute Embeddings
    ↓
Cluster by Similarity
    ↓
Create Semantic Blocks
    ↓
Compute Block Relationships
    ↓
Store Block Metadata
```

**Block Retrieval (Query Time):**
```
Query Arrives
    ↓
Match Block Centroids
    ↓
Retrieve Block Content
    ↓
Return Organized Blocks
```

---

## 📊 **Block Structure**

**SemanticBlock Model:**
```python
class SemanticBlock:
    id: str                      # Unique block identifier
    block_type: str             # thematic, narrative, conceptual, morphological
    content_ids: List[str]      # HHNI node IDs in this block
    relationships: Dict[str, float]  # Block relationships (block_id -> similarity)
    centroid_embedding: List[float]  # Block centroid for similarity
    created_at: datetime
    attributes: Dict[str, Any]  # Additional metadata
    node_count: int             # Number of nodes in block
    avg_similarity: float       # Average similarity within block
```

---

## 🔗 **Relationships**

**Semantic Blocks use:**
- HHNI nodes (content to organize)
- Embeddings (semantic similarity)
- SEG graph (relationship tracking, optional)

**Semantic Blocks enable:**
- Pre-organized retrieval
- Block-level relationships
- Coherent content blocks
- Faster retrieval of related content

---

## 📈 **Metrics**

**Block Quality:**
- Average similarity within block (higher = more coherent)
- Block size (optimal: 2-10 nodes)
- Relationship strength to other blocks

**Retrieval Performance:**
- Block retrieval vs. individual node retrieval
- Coherence improvement
- Relationship pre-computation savings

---

## 🔧 **Implementation**

**File:** `packages/hhni/semantic_block_organizer.py` (~350 lines)  
**Models:** `packages/hhni/semantic_blocks.py` (~150 lines)  
**Tests:** `packages/hhni/tests/test_semantic_blocks.py` (8 test cases)  
**Status:** ✅ Complete, production-ready

**Key Functions:**
- `organize_blocks()` - Cluster content into semantic blocks
- `compute_block_relationships()` - Pre-compute block similarities
- `create_block_centroid()` - Calculate block embedding centroids
- `retrieve_blocks()` - Retrieve pre-organized blocks

**Integration:**
- Integrated into `build_hhni_for_atom()` (optional parameter)
- Works with SEG for relationship tracking
- Backward compatible (works without SEG)

---

## 📚 **Detail Levels**

**L0:** This README  
**L1-L5:** Architecture docs (to create)

**Sub-components:**
- [block_types/thematic/](block_types/thematic/) - Thematic block organization
- [block_types/narrative/](block_types/narrative/) - Narrative block organization
- [block_types/conceptual/](block_types/conceptual/) - Conceptual block organization
- [block_types/morphological/](block_types/morphological/) - Morphological block organization

---

## 🎯 **Key Concepts**

**Pre-Organization:** Blocks created at index time, not query time  
**Semantic Clustering:** Content grouped by semantic similarity  
**Block Relationships:** Pre-computed relationships between blocks  
**Coherent Retrieval:** Retrieve organized blocks instead of isolated chunks

---

**Parent:** [../../README.md](../../README.md)  
**Siblings:** [../morphological_analysis/](../morphological_analysis/), [../cross_document_relationships/](../cross_document_relationships/)  
**Implementation:** `packages/hhni/semantic_block_organizer.py`  
**Status:** ✅ Production-ready, tested

