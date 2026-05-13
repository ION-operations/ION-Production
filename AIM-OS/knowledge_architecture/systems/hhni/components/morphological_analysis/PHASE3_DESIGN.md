# Phase 3: Pre-Organized Semantic Blocks - Design

**Date:** 2025-01-27  
**Status:** 📋 **DESIGN** - Ready for implementation  
**Component:** Semantic Organization Enhancement - Pre-Organized Semantic Blocks  
**Dependencies:** Phase 1 ✅ Complete, Phase 2 ✅ Complete

---

## 🎯 **PHASE 3 OBJECTIVE**

**Goal:** Pre-compute semantic relationships at index time to enable retrieval of "pre-organized semantic blocks" instead of isolated chunks.

**Core Insight:** "Perfecting how you save and organize it" means pre-computing semantic relationships during indexing, not post-processing during retrieval.

---

## 📊 **CURRENT STATE ANALYSIS**

### **What We Have:**
- ✅ **Phase 1:** Morphological analysis (word → parts)
- ✅ **Phase 2:** Cross-document relationships (semantic similarity, narrative context)
- ✅ **HHNI:** Hierarchical index within documents
- ✅ **SEG:** Graph structure with entities and relations
- ✅ **CMC:** Atoms with molecular relationships

### **What's Missing:**
- ❌ **Pre-computation:** Semantic relationships computed during retrieval, not at index time
- ❌ **Semantic blocks:** Content stored as isolated chunks, not pre-organized blocks
- ❌ **Relationship pre-computation:** Relationships discovered during query, not stored
- ❌ **Block organization:** No pre-computed semantic clusters

---

## 🏗️ **DESIGN OVERVIEW**

### **Architecture:**

```
┌─────────────────────────────────────────────────────────────┐
│         PRE-ORGANIZED SEMANTIC BLOCKS SYSTEM                │
└─────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
         ┌──────▼──────┐ ┌───▼────┐ ┌──────▼──────┐
         │   HHNI      │ │  SEG   │ │    CMC       │
         │  (Index)     │ │ (Graph)│ │  (Storage)   │
         └─────────────┘ └────────┘ └─────────────┘
                │             │             │
                └─────────────┼─────────────┘
                              │
         ┌────────────────────▼─────────────────────┐
         │   SEMANTIC BLOCK ORGANIZER                │
         │                                            │
         │  • Semantic Clustering (at index time)    │
         │  • Relationship Pre-computation           │
         │  • Block Formation                        │
         │  • Storage in CMC as Molecules            │
         └──────────────────────────────────────────┘
```

### **Key Components:**

1. **Semantic Block Organizer:** Clusters related content at index time
2. **Relationship Pre-computer:** Pre-computes semantic relationships
3. **Block Storage:** Stores organized blocks in CMC as molecules
4. **Block Retriever:** Retrieves pre-organized blocks instead of isolated chunks

---

## 🔧 **IMPLEMENTATION DESIGN**

### **1. Semantic Block Model**

**New Model: `packages/hhni/semantic_blocks.py`**

```python
"""Semantic block models for pre-organized content."""

from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime

@dataclass
class SemanticBlock:
    """A pre-organized semantic block containing related content."""
    
    id: str
    block_type: str  # "thematic", "narrative", "conceptual", "morphological"
    content_ids: List[str]  # HHNI node IDs or CMC atom IDs
    relationships: Dict[str, float]  # Relationship strengths
    centroid_embedding: List[float]  # Block centroid embedding
    created_at: datetime
    attributes: Dict[str, any] = None
```

### **2. Semantic Block Organizer**

**New Module: `packages/hhni/semantic_block_organizer.py`**

```python
"""Organizes content into semantic blocks at index time."""

from typing import List, Dict, Optional
from packages.hhni.models import HHNINode
from packages.hhni.semantic_blocks import SemanticBlock
from packages.seg.seg_graph import SEGraph

class SemanticBlockOrganizer:
    """Organizes content into semantic blocks during indexing."""
    
    def __init__(
        self,
        seg_graph: SEGraph,
        cluster_threshold: float = 0.80,
        max_block_size: int = 10,
    ):
        """Initialize semantic block organizer.
        
        Args:
            seg_graph: SEG graph for relationship tracking
            cluster_threshold: Minimum similarity for clustering (0-1)
            max_block_size: Maximum nodes per block
        """
        self.seg_graph = seg_graph
        self.cluster_threshold = cluster_threshold
        self.max_block_size = max_block_size
    
    def organize_into_blocks(
        self,
        nodes: List[HHNINode],
        atom_id: str,
    ) -> List[SemanticBlock]:
        """Organize nodes into semantic blocks.
        
        Args:
            nodes: HHNI nodes to organize
            atom_id: CMC atom ID for provenance
            
        Returns:
            List of semantic blocks
        """
        # Implementation:
        # 1. Compute embeddings for all nodes
        # 2. Cluster nodes by semantic similarity
        # 3. Form blocks from clusters
        # 4. Pre-compute relationships between blocks
        # 5. Store blocks in CMC as molecules
        pass
    
    def pre_compute_relationships(
        self,
        blocks: List[SemanticBlock],
    ) -> Dict[str, Dict[str, float]]:
        """Pre-compute relationships between blocks.
        
        Args:
            blocks: Semantic blocks to compute relationships for
            
        Returns:
            Dictionary mapping block_id → {other_block_id: similarity}
        """
        # Implementation:
        # 1. Compute block centroid embeddings
        # 2. Calculate similarity between all block pairs
        # 3. Store relationships in SEG
        # 4. Return relationship matrix
        pass
```

### **3. Integration with HHNI Indexing**

**Modify `packages/hhni/indexer.py`:**

```python
def build_hhni_for_atom(
    *,
    atom,
    dgraph_client,
    qdrant_client,
    correlation_id: Optional[str] = None,
    seg_graph: Optional["SEGraph"] = None,
    cross_doc_detector: Optional["CrossDocumentRelationshipDetector"] = None,
    block_organizer: Optional["SemanticBlockOrganizer"] = None,  # NEW
) -> List[HHNINode]:
    """Build HHNI nodes for the given atom with optional enhancements."""
    
    # ... existing code ...
    
    # Phase 3: Organize into semantic blocks (if organizer provided)
    if block_organizer is not None:
        blocks = block_organizer.organize_into_blocks(
            nodes=nodes,
            atom_id=atom.id,
        )
        
        # Pre-compute relationships
        relationships = block_organizer.pre_compute_relationships(blocks)
        
        # Store blocks in CMC as molecules
        _store_blocks_as_molecules(blocks, atom_id)
```

### **4. Block Storage in CMC**

**New Function in `packages/hhni/indexer.py`:**

```python
def _store_blocks_as_molecules(
    blocks: List["SemanticBlock"],
    atom_id: str,
) -> None:
    """Store semantic blocks in CMC as molecules.
    
    Each block becomes a molecule with:
    - Block atoms (content nodes)
    - Block relationships (pre-computed)
    - Block metadata (type, centroid, etc.)
    """
    # Implementation:
    # 1. Create molecule for each block
    # 2. Link block atoms via molecular relationships
    # 3. Store block metadata in molecule attributes
    # 4. Link blocks via SEG relations
    pass
```

---

## 📋 **IMPLEMENTATION PLAN**

### **Task 1: Create Semantic Block Models** (2-3 hours)
- [ ] Create `semantic_blocks.py` with `SemanticBlock` model
- [ ] Add block types (thematic, narrative, conceptual, morphological)
- [ ] Add block metadata structure
- [ ] Add tests

### **Task 2: Create Semantic Block Organizer** (6-8 hours)
- [ ] Create `semantic_block_organizer.py` module
- [ ] Implement clustering algorithm (k-means or hierarchical)
- [ ] Implement block formation logic
- [ ] Implement relationship pre-computation
- [ ] Add tests

### **Task 3: Integrate with HHNI Indexing** (3-4 hours)
- [ ] Modify `build_hhni_for_atom()` to accept `block_organizer` parameter
- [ ] Add block organization after node creation
- [ ] Add relationship pre-computation
- [ ] Add error handling
- [ ] Add tests

### **Task 4: Block Storage in CMC** (4-5 hours)
- [ ] Implement `_store_blocks_as_molecules()` function
- [ ] Create molecule structure for blocks
- [ ] Link blocks via molecular relationships
- [ ] Store block metadata
- [ ] Add tests

### **Task 5: Block Retrieval** (4-5 hours)
- [ ] Implement block retrieval from CMC
- [ ] Implement block-based query interface
- [ ] Add block similarity search
- [ ] Add tests

### **Task 6: Documentation** (2-3 hours)
- [ ] Update design documentation
- [ ] Create usage examples
- [ ] Update system maps
- [ ] Create integration guide

**Total Estimated Effort:** 21-28 hours (3-4 days)

---

## 🎯 **SUCCESS CRITERIA**

**Phase 3 Success:**
- ✅ Semantic blocks created at index time
- ✅ Relationships pre-computed and stored
- ✅ Blocks stored in CMC as molecules
- ✅ Block retrieval working
- ✅ Retrieval quality improved (+15% target)
- ✅ Faster retrieval (less post-processing)

**Quality Metrics:**
- Block formation accuracy: >85%
- Relationship pre-computation accuracy: >80%
- Retrieval quality improvement: +15% (target)
- Retrieval speed improvement: +20% (target)

---

## 🔍 **TECHNICAL DETAILS**

### **Clustering Algorithm:**

**Method:** Hierarchical clustering with semantic similarity
- Use embeddings for similarity calculation
- Cluster threshold: 0.80 (configurable)
- Max block size: 10 nodes (configurable)
- Block types: thematic, narrative, conceptual, morphological

### **Block Formation:**

**Process:**
1. Compute embeddings for all nodes
2. Cluster nodes by semantic similarity
3. Form blocks from clusters
4. Compute block centroids
5. Pre-compute inter-block relationships

### **Storage Structure:**

**CMC Molecules:**
- Each block = one molecule
- Block atoms = content nodes (HHNI nodes or CMC atoms)
- Block relationships = pre-computed similarities
- Block metadata = type, centroid, creation time

**SEG Relations:**
- Block-to-block relations (SEMANTICALLY_RELATED)
- Block-to-entity relations (CONTAINS)
- Block-to-document relations (FROM_DOCUMENT)

---

## 📚 **USAGE EXAMPLES**

### **Basic Block Organization:**

```python
from packages.hhni.semantic_block_organizer import SemanticBlockOrganizer
from packages.seg.seg_graph import SEGraph
from packages.hhni.indexer import build_hhni_for_atom

seg_graph = SEGraph()
block_organizer = SemanticBlockOrganizer(
    seg_graph=seg_graph,
    cluster_threshold=0.80,
    max_block_size=10,
)

# Index document with block organization
nodes = build_hhni_for_atom(
    atom=atom,
    dgraph_client=dgraph,
    qdrant_client=qdrant,
    seg_graph=seg_graph,
    block_organizer=block_organizer  # Enable block organization
)

# Blocks are automatically created and stored
```

### **Block Retrieval:**

```python
# Retrieve semantic blocks
blocks = retrieve_semantic_blocks(
    query="river bank",
    block_type="narrative",
    similarity_threshold=0.75,
)

for block in blocks:
    print(f"Block: {block.id}")
    print(f"  Type: {block.block_type}")
    print(f"  Content: {len(block.content_ids)} nodes")
    print(f"  Relationships: {len(block.relationships)}")
```

---

## 🔗 **INTEGRATION POINTS**

### **With Phase 1:**
- Morphological blocks (words with same root)
- Morphological relationships in blocks

### **With Phase 2:**
- Cross-document blocks (related content across documents)
- Narrative context in blocks
- Symbolic meaning in blocks

### **With HHNI:**
- Blocks contain HHNI nodes
- Block retrieval uses HHNI index

### **With SEG:**
- Block relationships stored in SEG
- Block queries via SEG graph

### **With CMC:**
- Blocks stored as molecules
- Block metadata in molecule attributes
- Block relationships via molecular links

---

## 📊 **METRICS & VALIDATION**

### **Performance Metrics:**
- Block formation time: <200ms per document
- Relationship pre-computation time: <100ms per block
- Block retrieval time: <50ms per query

### **Quality Metrics:**
- Block formation accuracy: >85%
- Relationship pre-computation accuracy: >80%
- Retrieval quality improvement: +15% (target)
- Retrieval speed improvement: +20% (target)

### **Validation Tests:**
- Test block formation
- Test relationship pre-computation
- Test block storage in CMC
- Test block retrieval
- Test integration with HHNI indexing

---

## 📋 **NEXT STEPS**

1. **Review Design:** Validate design with stakeholders
2. **Implement Task 1:** Create semantic block models
3. **Implement Task 2:** Create semantic block organizer
4. **Implement Task 3:** Integrate with HHNI indexing
5. **Implement Task 4:** Block storage in CMC
6. **Implement Task 5:** Block retrieval
7. **Implement Task 6:** Documentation
8. **Testing:** Comprehensive test suite
9. **Validation:** Real-world test cases

---

**Status:** 📋 **DESIGN COMPLETE** - Ready for implementation  
**Next:** Implement Task 1 (Create Semantic Block Models)

