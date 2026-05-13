# Phase 2: Cross-Document Relationship Tracking - Design

**Date:** 2025-01-27  
**Status:** 📋 **DESIGN** - Ready for implementation  
**Component:** Semantic Organization Enhancement - Cross-Document Relationships  
**Dependencies:** Phase 1 (Morphological Analysis) ✅ Complete

---

## 🎯 **PHASE 2 OBJECTIVE**

**Goal:** Track semantic relationships across documents to enable narrative context and symbolic meaning accumulation.

**Core Insight:** "River bank" on page 200 should be linked to "love" on page 5 and "wept" on page 30, creating a narrative context where "river bank" accumulates symbolic meaning over time.

---

## 📊 **CURRENT STATE ANALYSIS**

### **What We Have:**
- ✅ **HHNI:** Hierarchical index within documents (System → Section → Paragraph → Sentence → Word → Subword)
- ✅ **SEG:** Graph structure with entities and relations (supports, contradicts, derives, witnesses, cites)
- ✅ **CMC:** Atoms with molecular relationships (parent-child-sibling, supports, contradicts)
- ✅ **Phase 1:** Morphological analysis integrated (words → parts, parts → SEG entities)

### **What's Missing:**
- ❌ **Cross-document relationships:** No explicit tracking of semantic connections across documents
- ❌ **Narrative context:** No preservation of story-level relationships ("river bank" → "love")
- ❌ **Symbolic accumulation:** No tracking of how meaning accumulates over time
- ❌ **Cross-document retrieval:** Can't query "find all references to 'river bank' with accumulated meaning"

---

## 🏗️ **DESIGN OVERVIEW**

### **Architecture:**

```
┌─────────────────────────────────────────────────────────────┐
│              CROSS-DOCUMENT RELATIONSHIP TRACKING            │
└─────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
         ┌──────▼──────┐ ┌───▼────┐ ┌──────▼──────┐
         │   HHNI      │ │  SEG   │ │    CMC      │
         │  (Index)     │ │ (Graph)│ │  (Storage)  │
         └─────────────┘ └────────┘ └─────────────┘
                │             │             │
                └─────────────┼─────────────┘
                              │
         ┌────────────────────▼─────────────────────┐
         │   CROSS-DOCUMENT RELATIONSHIP LAYER       │
         │                                            │
         │  • Semantic Similarity Detection          │
         │  • Narrative Context Tracking              │
         │  • Symbolic Meaning Accumulation          │
         │  • Cross-Document Link Creation            │
         └──────────────────────────────────────────┘
```

### **Key Components:**

1. **Semantic Relationship Detector:** Identifies semantically related concepts across documents
2. **Narrative Context Tracker:** Tracks story-level relationships (symbols, themes, motifs)
3. **Symbolic Accumulator:** Accumulates meaning over time (first mention → later references)
4. **Cross-Document Linker:** Creates SEG relations between entities across documents

---

## 🔧 **IMPLEMENTATION DESIGN**

### **1. New SEG Relation Types**

**Extend `packages/seg/models.py` `RelationType` enum:**

```python
class RelationType(str, Enum):
    # Existing types
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    DERIVES_FROM = "derives_from"
    WITNESSES = "witnesses"
    CITES = "cites"
    
    # NEW: Cross-document semantic relationships
    SEMANTICALLY_RELATED = "semantically_related"  # General semantic similarity
    NARRATIVE_CONTEXT = "narrative_context"         # Story-level relationship
    SYMBOLIC_LINK = "symbolic_link"                 # Symbolic meaning connection
    CO_OCCURS_WITH = "co_occurs_with"              # Co-occurrence in context
    ACCUMULATES_MEANING = "accumulates_meaning"     # Meaning accumulation over time
```

### **2. Cross-Document Relationship Detector**

**New Module: `packages/hhni/cross_document_relationships.py`**

```python
"""Cross-document relationship detection and tracking."""

from typing import List, Dict, Optional, Tuple
from packages.seg.seg_graph import SEGraph
from packages.seg.models import Entity, Relation, RelationType
from packages.hhni.models import HHNINode

class CrossDocumentRelationshipDetector:
    """Detects and tracks semantic relationships across documents."""
    
    def __init__(self, seg_graph: SEGraph, similarity_threshold: float = 0.75):
        self.seg_graph = seg_graph
        self.similarity_threshold = similarity_threshold
    
    def detect_semantic_relationships(
        self,
        source_entity: Entity,
        target_entities: List[Entity],
        source_doc_id: str,
        target_doc_ids: List[str]
    ) -> List[Relation]:
        """Detect semantic relationships between entities across documents.
        
        Args:
            source_entity: Source entity (from document A)
            target_entities: Candidate target entities (from document B, C, etc.)
            source_doc_id: Source document ID
            target_doc_ids: Target document IDs (one per target entity)
            
        Returns:
            List of detected relations
        """
        # Implementation:
        # 1. Compute semantic similarity (embedding-based)
        # 2. Check narrative context (co-occurrence patterns)
        # 3. Detect symbolic links (repeated references)
        # 4. Create SEG relations
        pass
    
    def track_narrative_context(
        self,
        entity: Entity,
        context_entities: List[Entity],
        document_ids: List[str]
    ) -> List[Relation]:
        """Track narrative context relationships.
        
        Example: "river bank" → "love" (narrative context from story)
        """
        # Implementation:
        # 1. Identify narrative patterns (symbols, themes, motifs)
        # 2. Link entities with NARRATIVE_CONTEXT relations
        # 3. Store document context in relation attributes
        pass
    
    def accumulate_symbolic_meaning(
        self,
        entity: Entity,
        references: List[Tuple[Entity, str, float]]  # (entity, doc_id, timestamp)
    ) -> Entity:
        """Accumulate symbolic meaning over time.
        
        Example: "river bank" first mentioned → later references accumulate meaning
        """
        # Implementation:
        # 1. Track first mention vs. later references
        # 2. Update entity attributes with accumulated meaning
        # 3. Create ACCUMULATES_MEANING relations
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
    cross_doc_detector: Optional["CrossDocumentRelationshipDetector"] = None,  # NEW
) -> List[HHNINode]:
    """Build HHNI index for atom with optional SEG and cross-document integration."""
    
    # ... existing code ...
    
    # After creating entities in SEG, detect cross-document relationships
    if seg_graph is not None and cross_doc_detector is not None:
        _detect_cross_document_relationships(
            seg_graph=seg_graph,
            detector=cross_doc_detector,
            new_entities=new_entities,  # Entities created for this atom
            atom_id=atom.id,
            correlation_id=correlation_id,
        )
```

### **4. Cross-Document Relationship Detection Function**

**New Function in `packages/hhni/indexer.py`:**

```python
def _detect_cross_document_relationships(
    *,
    seg_graph: "SEGraph",
    detector: "CrossDocumentRelationshipDetector",
    new_entities: List["Entity"],
    atom_id: str,
    correlation_id: Optional[str] = None,
) -> None:
    """Detect and create cross-document relationships.
    
    For each new entity:
    1. Find similar entities in other documents
    2. Detect narrative context relationships
    3. Track symbolic meaning accumulation
    4. Create SEG relations
    """
    try:
        # Get all existing entities (from other documents)
        existing_entities = seg_graph.list_entities()
        
        for new_entity in new_entities:
            # Filter to entities from other documents
            other_doc_entities = [
                e for e in existing_entities
                if e.attributes.get("atom_id") != atom_id
            ]
            
            if not other_doc_entities:
                continue
            
            # Detect semantic relationships
            relations = detector.detect_semantic_relationships(
                source_entity=new_entity,
                target_entities=other_doc_entities,
                source_doc_id=atom_id,
                target_doc_ids=[e.attributes.get("atom_id") for e in other_doc_entities],
            )
            
            # Add relations to SEG
            for relation in relations:
                seg_graph.add_relation(relation)
                
    except Exception as exc:
        logger.warning(
            "hhni.cross_doc.detection.failed",
            extra={
                "atom_id": atom_id,
                "error": str(exc),
                "correlation_id": correlation_id,
            },
        )
```

---

## 📋 **IMPLEMENTATION PLAN**

### **Task 1: Extend SEG Relation Types** (1-2 hours)
- [ ] Add new relation types to `RelationType` enum
- [ ] Update SEG documentation
- [ ] Add tests for new relation types

### **Task 2: Create Cross-Document Detector** (4-6 hours)
- [ ] Create `cross_document_relationships.py` module
- [ ] Implement `CrossDocumentRelationshipDetector` class
- [ ] Implement semantic similarity detection (embedding-based)
- [ ] Implement narrative context tracking
- [ ] Implement symbolic meaning accumulation
- [ ] Add tests

### **Task 3: Integrate with HHNI Indexing** (2-3 hours)
- [ ] Modify `build_hhni_for_atom()` to accept `cross_doc_detector` parameter
- [ ] Add `_detect_cross_document_relationships()` function
- [ ] Integrate detection after entity creation
- [ ] Add error handling
- [ ] Add tests

### **Task 4: Cross-Document Query Support** (3-4 hours)
- [ ] Add query methods to SEG for cross-document relationships
- [ ] Implement "find all references with accumulated meaning" query
- [ ] Add narrative context queries
- [ ] Add tests

### **Task 5: Documentation** (2-3 hours)
- [ ] Update design documentation
- [ ] Create usage examples
- [ ] Update system maps
- [ ] Create integration guide

**Total Estimated Effort:** 12-18 hours (1.5-2.5 days)

---

## 🎯 **SUCCESS CRITERIA**

**Phase 2 Success:**
- ✅ Cross-document relationships tracked in SEG
- ✅ "River bank" → "love" relationship preserved (narrative context)
- ✅ Symbolic meaning accumulation working (first mention → later references)
- ✅ Can query cross-document relationships
- ✅ Integration with HHNI indexing complete
- ✅ Tests passing

**Quality Metrics:**
- Semantic similarity detection accuracy: >80%
- Cross-document relationship recall: >70%
- Narrative context preservation: >85%
- Symbolic accumulation tracking: >90%

---

## 🔍 **TECHNICAL DETAILS**

### **Semantic Similarity Detection:**

**Method:** Embedding-based cosine similarity
- Use sentence-transformers (same as HHNI)
- Compute similarity between entity embeddings
- Threshold: 0.75 (configurable)

**Example:**
```python
# "river bank" (doc A) vs. "river" (doc B)
similarity = cosine_similarity(
    embed("river bank"),
    embed("river")
)  # ~0.85 → Create SEMANTICALLY_RELATED relation
```

### **Narrative Context Detection:**

**Method:** Pattern-based + LLM-assisted
- Identify repeated patterns (symbols, themes, motifs)
- Use LLM to detect narrative connections
- Store as NARRATIVE_CONTEXT relations

**Example:**
```python
# "river bank" (page 200) → "love" (page 5)
# Detected via narrative pattern analysis
relation = Relation(
    source_id="entity:river_bank",
    target_id="entity:love",
    relation_type=RelationType.NARRATIVE_CONTEXT,
    confidence=0.90,
    attributes={
        "context_type": "symbolic",
        "source_doc": "doc_a",
        "target_doc": "doc_b",
        "narrative_pattern": "symbol_accumulation",
    }
)
```

### **Symbolic Meaning Accumulation:**

**Method:** Temporal tracking + attribute updates
- Track first mention timestamp
- Track subsequent references
- Update entity attributes with accumulated meaning
- Create ACCUMULATES_MEANING relations

**Example:**
```python
# First mention: "river bank" (page 50, timestamp: T1)
# Later reference: "river bank" (page 200, timestamp: T2)
# → Accumulate meaning: "river bank" now has symbolic weight

entity.attributes.update({
    "first_mention": T1,
    "reference_count": 2,
    "symbolic_weight": 0.75,  # Accumulated over time
    "accumulated_meaning": "Symbol of love and loss",
})
```

---

## 📚 **USAGE EXAMPLES**

### **Basic Cross-Document Relationship Detection:**

```python
from packages.hhni.cross_document_relationships import CrossDocumentRelationshipDetector
from packages.seg.seg_graph import SEGraph

seg_graph = SEGraph()
detector = CrossDocumentRelationshipDetector(
    seg_graph=seg_graph,
    similarity_threshold=0.75
)

# Index document A
nodes_a = build_hhni_for_atom(
    atom=atom_a,
    dgraph_client=dgraph,
    qdrant_client=qdrant,
    seg_graph=seg_graph,
    cross_doc_detector=detector  # Enable cross-document detection
)

# Index document B (will detect relationships to document A)
nodes_b = build_hhni_for_atom(
    atom=atom_b,
    dgraph_client=dgraph,
    qdrant_client=qdrant,
    seg_graph=seg_graph,
    cross_doc_detector=detector
)

# Query cross-document relationships
relations = seg_graph.get_relations(
    relation_type=RelationType.SEMANTICALLY_RELATED
)
print(f"Found {len(relations)} cross-document relationships")
```

### **Narrative Context Query:**

```python
# Find all entities with narrative context to "river bank"
river_bank_entity = seg_graph.get_entity("entity:river_bank")
narrative_relations = seg_graph.get_relations(
    source_id=river_bank_entity.id,
    relation_type=RelationType.NARRATIVE_CONTEXT
)

for rel in narrative_relations:
    target_entity = seg_graph.get_entity(rel.target_id)
    print(f"River bank → {target_entity.name} (narrative context)")
    print(f"  Confidence: {rel.confidence}")
    print(f"  Pattern: {rel.attributes.get('narrative_pattern')}")
```

### **Symbolic Meaning Accumulation Query:**

```python
# Find entities with accumulated symbolic meaning
entities_with_meaning = [
    e for e in seg_graph.list_entities()
    if e.attributes.get("symbolic_weight", 0) > 0.5
]

for entity in entities_with_meaning:
    print(f"{entity.name}:")
    print(f"  Symbolic weight: {entity.attributes.get('symbolic_weight')}")
    print(f"  References: {entity.attributes.get('reference_count')}")
    print(f"  Meaning: {entity.attributes.get('accumulated_meaning')}")
```

---

## 🔗 **INTEGRATION POINTS**

### **With Phase 1 (Morphological Analysis):**
- Morphological parts can be linked across documents
- "unhappy" in doc A → "happy" in doc B (via root relationship)
- Cross-document morphological relationships

### **With HHNI:**
- Cross-document relationships stored in SEG
- HHNI index entries linked via SEG relations
- Enable cross-document retrieval through HHNI

### **With CMC:**
- Cross-document relationships reference CMC atoms
- Molecular relationships extended across documents
- Bitemporal tracking of cross-document links

### **With SEG:**
- New relation types added to SEG
- Cross-document queries via SEG graph
- Narrative context and symbolic meaning in graph

---

## 📊 **METRICS & VALIDATION**

### **Performance Metrics:**
- Cross-document detection time: <100ms per document
- Relationship creation time: <10ms per relation
- Query time: <50ms for cross-document queries

### **Quality Metrics:**
- Semantic similarity accuracy: >80%
- Narrative context precision: >75%
- Symbolic accumulation recall: >90%

### **Validation Tests:**
- Test semantic similarity detection
- Test narrative context tracking
- Test symbolic meaning accumulation
- Test cross-document queries
- Test integration with HHNI indexing

---

## 📋 **NEXT STEPS**

1. **Review Design:** Validate design with stakeholders
2. **Implement Task 1:** Extend SEG relation types
3. **Implement Task 2:** Create cross-document detector
4. **Implement Task 3:** Integrate with HHNI indexing
5. **Implement Task 4:** Add query support
6. **Implement Task 5:** Documentation
7. **Testing:** Comprehensive test suite
8. **Validation:** Real-world test cases

---

**Status:** 📋 **DESIGN COMPLETE** - Ready for implementation  
**Next:** Implement Task 1 (Extend SEG Relation Types)

