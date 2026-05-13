# SEG Integration for Morphological Analysis

**Date:** 2025-01-27  
**Status:** ✅ **COMPLETE**  
**Component:** SEG Graph Linking of Morphological Parts

---

## 🎯 **INTEGRATION COMPLETE**

Morphological parts (prefix, root, suffix) are now linked in the SEG graph when SEG is provided during HHNI indexing. This enables semantic relationships between words and their morphological components.

---

## 📊 **HOW IT WORKS**

### **Flow:**
```
HHNI Indexing (build_hhni_for_atom)
    ↓
Morphological Analysis (tokenize_with_morphology)
    ↓
SUBWORD Nodes Created (Level 6)
    ↓
SEG Integration (if seg_graph provided):
    - Create word entity in SEG
    - Create part entities (prefix, root, suffix)
    - Create relations: word → parts (DERIVES_FROM)
```

### **Entity Creation:**

**Word Entity:**
```python
Entity(
    id="morph_word:unhappiness",
    type="morphological_word",
    name="unhappiness",
    attributes={
        "hhni_node_id": "tok:atom_id#p0#s0#t0",
        "atom_id": "atom_123",
        "pos_tag": "NN",
        "operations": ["negation", "noun_formation"]
    },
    tags=["morphology", "word"]
)
```

**Part Entities:**
```python
# Prefix entity
Entity(
    id="morph_part:prefix:un-",
    type="morphological_part",
    name="prefix:un-",
    attributes={"part_type": "prefix", "operation": "negation"},
    tags=["morphology", "prefix"]
)

# Root entity
Entity(
    id="morph_part:root:happy",
    type="morphological_part",
    name="root:happy",
    attributes={"part_type": "root"},
    tags=["morphology", "root"]
)

# Suffix entity
Entity(
    id="morph_part:suffix:-ness",
    type="morphological_part",
    name="suffix:-ness",
    attributes={"part_type": "suffix", "operation": "noun_formation"},
    tags=["morphology", "suffix"]
)
```

### **Relations:**

**Word → Parts:**
```python
Relation(
    source_id="morph_word:unhappiness",
    target_id="morph_part:prefix:un-",
    relation_type=RelationType.DERIVES_FROM,
    confidence=1.0,
    tags=["morphology", "prefix_relation"]
)
```

---

## 🔧 **IMPLEMENTATION DETAILS**

### **Modified Files:**

1. **`packages/hhni/indexer.py`:**
   - Added optional `seg_graph` parameter to `build_hhni_for_atom()`
   - Added `_link_morphological_parts_in_seg()` function
   - Integrated SEG linking after SUBWORD node creation

### **Code Changes:**

**Function Signature:**
```python
def build_hhni_for_atom(
    *,
    atom,
    dgraph_client,
    qdrant_client,
    correlation_id: Optional[str] = None,
    seg_graph: Optional["SEGraph"] = None,  # NEW: Optional SEG integration
) -> List[HHNINode]:
```

**Integration Point:**
```python
# After creating SUBWORD node with morphology
if seg_graph is not None and morphology.root:
    _link_morphological_parts_in_seg(
        seg_graph=seg_graph,
        word=token,
        morphology=morphology,
        hhni_node_id=token_id,
        atom_id=atom.id,
        correlation_id=correlation_id,
    )
```

### **Key Features:**

1. **Optional Integration:** SEG is optional - doesn't break existing code
2. **Deduplication:** Entity IDs use consistent naming (e.g., `morph_word:unhappiness`)
3. **Error Handling:** SEG failures don't break HHNI indexing (logged as warnings)
4. **Provenance:** Entities include `hhni_node_id` and `atom_id` for cross-reference
5. **Relations:** Word → parts linked with `DERIVES_FROM` relations

---

## 📋 **USAGE**

### **Basic Usage (Without SEG):**
```python
# Existing code continues to work
nodes = build_hhni_for_atom(
    atom=atom,
    dgraph_client=dgraph,
    qdrant_client=qdrant,
    correlation_id="123"
)
```

### **With SEG Integration:**
```python
from packages.seg.seg_graph import SEGraph

seg_graph = SEGraph()

nodes = build_hhni_for_atom(
    atom=atom,
    dgraph_client=dgraph,
    qdrant_client=qdrant,
    correlation_id="123",
    seg_graph=seg_graph  # Enable SEG integration
)

# Morphological parts are now linked in SEG
# Query SEG for morphological relationships
entities = seg_graph.list_entities(entity_type="morphological_word")
for entity in entities:
    print(f"Word: {entity.name}")
    # Get relations to parts
    relations = seg_graph.get_relations(source_id=entity.id)
    for rel in relations:
        part_entity = seg_graph.get_entity(rel.target_id)
        print(f"  → {part_entity.name}")
```

### **Querying Morphological Relationships:**
```python
# Find all words with a specific prefix
prefix_entity = seg_graph.get_entity("morph_part:prefix:un-")
if prefix_entity:
    # Get all words that derive from this prefix
    relations = seg_graph.get_relations(target_id=prefix_entity.id)
    for rel in relations:
        word_entity = seg_graph.get_entity(rel.source_id)
        print(f"Word with 'un-' prefix: {word_entity.name}")

# Find all words with a specific root
root_entity = seg_graph.get_entity("morph_part:root:happy")
if root_entity:
    relations = seg_graph.get_relations(target_id=root_entity.id)
    for rel in relations:
        word_entity = seg_graph.get_entity(rel.source_id)
        print(f"Word with 'happy' root: {word_entity.name}")
```

---

## ✅ **SUCCESS CRITERIA MET**

- ✅ SEG entities created for words and morphological parts
- ✅ Relations linking word → parts (DERIVES_FROM)
- ✅ Optional integration (doesn't break existing code)
- ✅ Entity deduplication (consistent IDs)
- ✅ Error handling (SEG failures don't break HHNI)
- ✅ Provenance tracking (hhni_node_id, atom_id in attributes)

---

## 📚 **REFERENCES**

- **Morphological Analysis:** `packages/hhni/morphology.py`
- **HHNI Indexer:** `packages/hhni/indexer.py`
- **SEG Graph:** `packages/seg/seg_graph.py`
- **SEG Models:** `packages/seg/models.py`
- **Design Document:** `knowledge_architecture/systems/hhni/components/morphological_analysis/DESIGN.md`
- **CMC Integration:** `knowledge_architecture/systems/hhni/components/morphological_analysis/CMC_INTEGRATION.md`

---

**Status:** ✅ **SEG INTEGRATION COMPLETE**  
**Next:** Testing & validation, then Phase 2 (cross-document relationships)

