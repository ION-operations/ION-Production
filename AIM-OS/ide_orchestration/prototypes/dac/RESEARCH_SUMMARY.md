# Deep AIM-OS Research Summary
**Date:** 2025-11-07  
**Purpose:** Comprehensive research findings for perfecting IDE prototype panels  
**Author:** Dac

---

## 🎯 **RESEARCH OBJECTIVE**

Deep exploration of AIM-OS systems (CMC, HHNI, SEG, TCS) to ensure prototype panels match real system implementations exactly.

---

## 📦 **1. CMC (Context Memory Core) - Complete Structure**

### **Atom Structure (from `packages/cmc_service/models.py`):**

```python
@dataclass
class Atom:
    # Identity
    id: str  # Format: "atom_{uuid}" (32 hex chars)
    
    # Content
    modality: str  # "text" | "code" | "event" | "tool" | "cross_model"
    content: AtomContent  # {inline?: string, uri?: string, media_type: string}
    
    # Semantic
    embedding: Optional[List[float]]  # Vector representation
    tags: Dict[str, float]  # Weighted tags (0.0-1.0)
    
    # Temporal
    created_at: datetime  # Transaction time
    valid_from: datetime  # Valid time start (bitemporal)
    valid_to: Optional[datetime]  # Valid time end (bitemporal)
    
    # Provenance
    witness: WitnessStub  # {
    #   model_id?: string,
    #   tool_ids: List[str],
    #   snapshot_id?: string,
    #   correlation_id?: string,
    #   uncertainty_band: "green" | "yellow" | "red",
    #   uncertainty_ece?: float
    # }
    snapshot_ids: List[str]
    hash: str  # SHA-256 hash
    
    # Extensible
    metadata: Dict[str, Any]
```

### **Key Findings:**
- **Modality:** Can be "text", "code", "event", "tool", or "cross_model"
- **Content:** Either `inline` (<1KB) or `uri` (≥1KB), never both
- **Tags:** Weighted dictionary (0.0-1.0), not just strings
- **Witness:** Contains `uncertainty_band` ("green"/"yellow"/"red"), not `confidence_band`
- **Bitemporal:** `valid_from`/`valid_to` for time-travel queries
- **Hash:** SHA-256 hash of content

---

## 🔍 **2. HHNI (Hierarchical Hypergraph Neural Index) - Complete Structure**

### **IndexNode Structure (from `packages/hhni/hierarchical_index.py`):**

```python
@dataclass
class IndexNode:
    id: str  # e.g., "doc:atom_123", "para:atom_123#p0"
    level: IndexLevel  # SYSTEM(1), SECTION(2), PARAGRAPH(3), SENTENCE(4), SUBWORD(5)
    content: str  # Full content text
    summary: str  # Summary/abstract
    parent_id: Optional[str]  # Parent node ID
    children_ids: List[str]  # Child node IDs
    embeddings: Optional[List[float]]  # Embedding vector
    metadata: Dict[str, Any]  # Additional metadata
```

### **HHNINode (Complete with persistence metadata):**

```python
@dataclass
class HHNINode:
    id: str  # "doc:atom_123", "para:atom_123#p0"
    level: int  # 1-5
    path: str  # "/sys:aimos/doc:atom_123/para:0"
    content_hash: str  # SHA-256 hash
    text: Optional[str]
    parent_id: Optional[str]
    children_ids: List[str]
    depends_on: List[str]
    depended_by: List[str]
    vector_id: Optional[str]  # Qdrant vector ID
    tags: Dict[str, float]  # Tag weights
    tpv: TagPriorityVector  # Priority vector
    atom_refs: List[str]  # CMC atom references
    created_at: datetime
    snapshot_id: str
    impact_score: Optional[float]
    staleness_days: Optional[int]
```

### **Key Findings:**
- **5-Level Hierarchy:** SYSTEM → SECTION → PARAGRAPH → SENTENCE → SUBWORD
- **Path Format:** "/sys:aimos/doc:atom_123/para:0"
- **Dependencies:** `depends_on` and `depended_by` for graph relationships
- **TPV:** Tag Priority Vector for temporal decay and relevance
- **Atom References:** Links back to CMC atoms

---

## 🕸️ **3. SEG (Shared Evidence Graph) - Complete Structure**

### **Entity Structure (from `packages/seg/models.py`):**

```python
class Entity(BaseModel):
    id: str  # "entity_{uuid}"
    type: str  # Entity type (person, concept, event, etc.)
    name: str  # Human-readable name
    attributes: Dict[str, Any]
    
    # Bitemporal
    tt_start: datetime  # Transaction time start
    tt_end: Optional[datetime]  # Transaction time end
    vt_start: datetime  # Valid time start
    vt_end: Optional[datetime]  # Valid time end
    
    # Metadata
    source: Optional[str]
    confidence: float  # 0-1
    tags: List[str]
    witness_id: Optional[str]  # VIF witness
```

### **Relation Structure:**

```python
class Relation(BaseModel):
    id: str  # "relation_{uuid}"
    source_id: str  # Source entity ID
    target_id: str  # Target entity ID
    relation_type: RelationType  # SUPPORTS, CONTRADICTS, REFERENCES, DERIVES_FROM, RELATES_TO
    evidence_ids: List[str]  # Evidence supporting this relation
    confidence: float  # 0-1
    
    # Bitemporal
    tt_start: datetime
    tt_end: Optional[datetime]
    vt_start: datetime
    vt_end: Optional[datetime]
    
    # Metadata
    source: Optional[str]
    tags: List[str]
    witness_id: Optional[str]
```

### **Contradiction Structure:**

```python
class Contradiction(BaseModel):
    id: str  # "contradiction_{uuid}"
    entity1_id: str  # First conflicting entity
    entity2_id: str  # Second conflicting entity
    contradiction_type: str
    similarity: float  # 0-1
    confidence: float  # 0-1
    explanation: str
    resolved: bool
    resolution: Optional[str]
    resolved_at: Optional[datetime]
    detected_at: datetime
    tags: List[str]
```

### **Key Findings:**
- **Bitemporal:** Both `tt_start/tt_end` (transaction time) AND `vt_start/vt_end` (valid time)
- **Relation Types:** SUPPORTS, CONTRADICTS, REFERENCES, DERIVES_FROM, RELATES_TO
- **Evidence IDs:** Relations have `evidence_ids` array
- **Contradictions:** Separate model with `entity1_id`/`entity2_id`, not `claim_a_id`/`claim_b_id`

---

## ⏱️ **4. TCS (Timeline Context System) - Complete Structure**

### **TimelineEntry Structure (from `packages/timeline_context_system/prompt_context_tracker.py`):**

```python
@dataclass
class TimelineEntry:
    timestamp: datetime
    prompt_id: str
    context_index: Dict[str, Any]
    summary: str
    context_evolution: Dict[str, Any]
    confidence_metrics: Dict[str, float]
    relevance_score: float
    
    # Chain Connection Fields (NEW - Evolution Explorer)
    executed_via_chain_id: Optional[str]  # Which chain executed this
    chain_execution_id: Optional[str]  # Execution instance ID
    chain_node_id: Optional[str]  # Which chain node produced this
    
    # Chain Evolution Tracking
    parent_chain_ids: List[str]  # Chains that led here
    child_chain_ids: List[str]  # Chains spawned from here
    evolution_path: List[str]  # Path through evolution graph
```

### **Extended TimelineEntry (from T2_architecture.md):**

```python
@dataclass
class TimelineEntry:
    entry_id: str
    timestamp: datetime
    event_type: EventType  # BREAKTHROUGH, MAJOR_MILESTONE, etc.
    title: str
    description: str
    context_data: Dict[str, Any]
    quality_metrics: Dict[str, float]
    emotional_context: Dict[str, Any]
    technical_details: Dict[str, Any]
    next_steps: List[str]
    related_files: List[str]
    tags: List[str]
    metadata: Dict[str, Any]
    
    # Bitemporal
    valid_from: datetime
    valid_to: Optional[datetime]
    
    # Chain Connections
    executed_via_chain_id: Optional[str]
    chain_execution_id: Optional[str]
    chain_node_id: Optional[str]
    parent_chain_ids: List[str]
    child_chain_ids: List[str]
    evolution_path: List[str]
```

### **Key Findings:**
- **Two Structures:** Basic (`prompt_context_tracker.py`) and Extended (T2_architecture.md)
- **Chain Connections:** `executed_via_chain_id`, `chain_execution_id`, `chain_node_id`
- **Evolution Tracking:** `parent_chain_ids`, `child_chain_ids`, `evolution_path`
- **Bitemporal:** `valid_from`/`valid_to` in extended structure
- **Rich Metadata:** `quality_metrics`, `emotional_context`, `technical_details`, `next_steps`, `related_files`

---

## 🎯 **PANEL PERFECTION PLAN**

### **1. MemoryBrowser Panel**
- ✅ Use exact CMC Atom structure
- ✅ Display `witness.uncertainty_band` (not `confidence_band`)
- ✅ Show `valid_from`/`valid_to` for bitemporal
- ✅ Filter by modality (text, code, event, tool, cross_model)
- ✅ Display tags as weighted dictionary
- ✅ Show hash for verification

### **2. ContextWeb Panel**
- ✅ Use exact SEG Entity/Relation structure
- ✅ Display bitemporal fields (`tt_start/tt_end`, `vt_start/vt_end`)
- ✅ Show relation types (SUPPORTS, CONTRADICTS, etc.)
- ✅ Display evidence_ids for relations
- ✅ Show contradictions with `entity1_id`/`entity2_id`
- ✅ Visualize confidence scores

### **3. TimelineView Panel**
- ✅ Use extended TimelineEntry structure
- ✅ Display chain connections (`executed_via_chain_id`, etc.)
- ✅ Show evolution paths
- ✅ Display bitemporal fields (`valid_from`/`valid_to`)
- ✅ Show quality metrics, emotional context, technical details
- ✅ Playback controls for bitemporal timeline

### **4. EvolutionExplorer View**
- ✅ Connect Timeline ↔ Chain ↔ Goals
- ✅ Use `executed_via_chain_id` for Timeline → Chain
- ✅ Use `parent_chain_ids`/`child_chain_ids` for Chain relationships
- ✅ Use `evolution_path` for path visualization
- ✅ Display goal connections via `context_data.goal_id`
- ✅ Bidirectional graph visualization

---

**Status:** Research Complete ✅  
**Next:** Perfect each panel systematically

