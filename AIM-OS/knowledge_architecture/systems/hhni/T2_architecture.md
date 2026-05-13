---
id: "hhni_T2_architecture"
system: "hhni"
component: null
level: "T2"
type: "architecture"
title: "HHNI Architecture"
description: "2,000-word architecture document for Hierarchical Hypergraph Neural Index"
audience: "developers, architects, implementation planning"
confidence_threshold: 0.70
token_cost: 2000
word_count: 2000
created: "2025-10-30T00:00:00Z"
updated: "2025-11-16T00:00:00Z"
author: "aether"
status: "complete"
tags: ["hhni", "core", "indexing", "retrieval", "t0-t6", "transitional"]
dependencies: ["hhni_T1_overview"]
related_docs: ["hhni_T3_detailed", "system.map.lucid.json5", "usage.envelope.md"]
version: "v2.2.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# HHNI – T2 Architecture (≈2000 words)

## 🔄 **SDF-CVF QUARTET PARITY ENFORCEMENT**

### **Quartet Elements:**

**Code:** HHNI implementation files (`packages/hhni/`), index engine, DVNS physics module, retrieval planner  
**Docs:** T0-T6 documentation (L0_executive.md, L1_overview.md, L2_architecture.md, L3_detailed.md, L4_complete.md), usage.envelope.md  
**Tests:** HHNI test suite (`packages/hhni/tests/`), integration tests, physics simulation tests  
**Traces:** VIF witnesses (RS-lift metrics), SEG provenance (evidence indexing), timeline entries, decision logs

**Parity Requirement:** P ≥ 0.90 for all changes  
**Cross-Tagging:** All quartet elements must be tagged with change ID (hhni-change-YYYYMMDD-HHMMSS) and semantically aligned

### **Quartet Parity Formula:**

```
P = (C_code×docs + C_code×tests + C_code×traces +
     C_docs×tests + C_docs×traces + C_tests×traces) / 6

Where:
- C_code×docs = semantic similarity between code and docs
- C_code×tests = semantic similarity between code and tests
- C_code×traces = semantic similarity between code and traces
- C_docs×tests = semantic similarity between docs and tests
- C_docs×traces = semantic similarity between docs and traces
- C_tests×traces = semantic similarity between tests and traces

Target: P ≥ 0.90 for all changes
```

### **Cross-Tagging Protocol:**

**Change ID Format:** `hhni-change-YYYYMMDD-HHMMSS` (e.g., `hhni-change-20251102-154530`)

**Tagging Requirements:**
- **Code:** Change ID in comments/metadata within modified code sections
- **Docs:** Change ID in frontmatter `tags` array and/or inline comments
- **Tests:** Change ID in test function docstrings/comments
- **Traces:** Change ID in VIF witness metadata, SEG provenance links, timeline entry metadata, decision log filename/content

**Workflow:**
1. Generate Change ID at start of HHNI modification
2. Modify code (HHNI implementation) → Tag with Change ID
3. Update docs (T-level docs) → Tag with Change ID
4. Update/add tests (HHNI test suite) → Tag with Change ID
5. Create traces (VIF, SEG, timeline, decision log) → Tag with Change ID
6. Validate quartet parity (P ≥ 0.90) before merge

### **Gate Enforcement:**

**Pre-commit Gate:** Check quartet completeness and parity before commit  
**CI Gate:** Validate quartet parity in pipeline  
**Deployment Gate:** Verify quartet parity before deployment  
**Quarantine:** Changes with P < 0.90 are quarantined until parity achieved

---

## 🎯 **LUCID DEVELOPMENT PROTOCOL INTEGRATION**

### **Stage 0: Intent Capture**

**Intent Statement:**
We are updating HHNI documentation to current standards (T0-T6, Perfect Metadata, SDF-CVF quartet parity, System Maps, Usage Envelopes, LDP Stage 0-1) so that HHNI documentation serves as a complete template for other AIM-OS systems and ensures perfect alignment across Code, Docs, Tests, and Traces.

**Value Targets:**
- **Must Get Better:** Documentation structure, standards compliance, quartet parity clarity, onboarding experience
- **Must Not Get Worse:** Existing functionality, backward compatibility, documentation accuracy, performance

**Scope Class:** Extension - Adding T0-T6 documentation structure, quartet parity requirements, LDP integration, and system mapping to existing HHNI documentation

**Why This Matters:**
This update preserves the "ghost of intent" - why HHNI exists (solve "lost in the middle" problem with physics-guided retrieval) - while elevating documentation to full AIM-OS standards compliance. The intent follows the work forever, ensuring HHNI never drifts from its core purpose.

---

### **Stage 1: System Index & Ontology**

**System Classification:**
- **Layer:** 1 (Indexing Layer - depends on CMC)
- **Security Level:** High (indexing operations must be protected)
- **Performance Sensitivity:** Critical (retrieval latency affects all systems, must be fast)
- **Ownership:** Core (AIM-OS core system)
- **Side Effects:** 
  - Provides retrieval for all AIM-OS systems
  - Enables physics-guided optimization
  - Supports multi-resolution queries
  - Affects context quality for all systems

**System Relationships:**
- **Depends On:** CMC (bitemporal memory storage), Vector Store (similarity search)
- **Feeds Data To:** All AIM-OS systems (APOE, VIF, SEG, SDF-CVF, CAS, etc.)
- **Integrates With:** CMC (atom indexing), APOE (context retrieval), VIF (witness storage), SEG (evidence indexing), SDF-CVF (index consistency)

**System Context:**
HHNI operates at the indexing layer, providing physics-guided retrieval for all AIM-OS systems. It solves the "lost in the middle" problem by combining fractal hierarchical indexing with DVNS physics optimization, delivering +15% improvement in retrieval quality while respecting token budgets.

---

## System Overview

HHNI (Hierarchical Hypergraph Neural Index) combines fractal multi-resolution indexing with physics-guided retrieval to solve the "lost in the middle" problem—delivering +15% improvement in retrieval quality while respecting token budgets and maintaining context coherence.

HHNI provides two breakthrough innovations:
1. **6-Level Fractal Hierarchical Index:** Every piece of content indexed at multiple resolutions simultaneously
2. **DVNS Physics Optimization:** Treats context items as particles, applies physics forces to optimize spatial layout

## Subsystem Hierarchy

HHNI is organized into a 3-layer hierarchy:

**Layer 1 (Main System):** `hhni.hierarchicalHypergraph` - The complete HHNI system

**Layer 2 (Subsystems):** Four subsystems that meet complexity, independence, relationship, and evolution criteria:

1. **Hierarchical Index Subsystem** - Manages 6-level fractal indexing (System → Section → Paragraph → Sentence → Word → Subword). Integrates with CMC (atom indexing), SEG (hierarchical paths), SDF-CVF (index consistency), CAS (activation hooks), TCS (temporal context).

2. **DVNS Physics Subsystem** - Applies 4 forces (gravity, repulsion, elastic, damping) to optimize context layout. Integrates with VIF (RS-lift metrics) and SDF-CVF (physics quartet parity).

3. **Retrieval Subsystem** - Two-stage intelligent retrieval pipeline. **Main pipeline** uses 3 Layer 3 components: coarseRetrieval (semantic search), physicsRefinement (DVNS optimization), budgetFitter (token budget management). **Additional components** available: deduplicationEngine (available but not integrated), conflictResolver (used in baseline comparison), strategicCompressor (used in baseline comparison). Integrates with CMC (atom retrieval), APOE (context provision), VIF (witnessing), SEG (semantic search), CAS (activation tracking), TCS (context management), SDF-CVF (quartet parity).

4. **Morphological Analysis Subsystem** - Decomposes words into parts (prefix, root, suffix) for enhanced subword indexing. Integrates with CMC (morphological data storage) and SEG (morphological entities).

**Layer 3 (Components):** Components within the Retrieval Subsystem (see Components section below).

## Components

### 1. Index Engine
**Purpose:** Build and maintain 6-level hierarchical index structure

**Responsibilities:**
- Extract hierarchical structure from CMC atoms (System → Section → Paragraph → Sentence → Word → Subword)
- Build parent-child relationships across levels
- Maintain index entries with embeddings, metadata, hierarchical paths
- Update indices when atoms change (dependency tracking)

**Key Operations:**
- `build_index()` - Construct all 6 levels from atoms
- `update_index()` - Refresh index when dependencies change
- `get_entry()` - Retrieve index entry by ID or path
- `get_children()` / `get_parent()` - Navigate hierarchy

### 2. DVNS Physics Module
**Purpose:** Physics-guided optimization of context layout

**Responsibilities:**
- Create particles from retrieval candidates
- Apply four physics forces (gravity, elastic, repulse, damping)
- Run Velocity-Verlet simulation (50-100 iterations)
- Detect convergence and optimize spatial arrangement

**Key Operations:**
- `create_particles()` - Convert items to particles with positions/velocities
- `simulate_physics()` - Run physics simulation to convergence
- `compute_forces()` - Calculate all four forces for each particle
- `has_converged()` - Check if simulation reached stable state

### 3. Retrieval Planner
**Purpose:** Orchestrate two-stage retrieval pipeline

**Responsibilities:**
- Stage 1: Coarse retrieval (KNN semantic search)
- Stage 2: Physics refinement (DVNS optimization)
- Quality pipeline orchestration (deduplication, conflict resolution, compression, budget fitting)

**Key Operations:**
- `retrieve()` - Complete two-stage retrieval
- `coarse_retrieval()` - Fast KNN search (top-100 candidates)
- `physics_refinement()` - Apply DVNS to optimize candidates
- `apply_quality_pipeline()` - Deduplication, conflict resolution, compression, budget fitting

### 4. Compression/Deduplication Module
**Purpose:** Quality filters for optimal context

**Responsibilities:**
- Semantic deduplication (cluster similar items, keep best)
- Conflict detection and resolution (identify contradictions, select best stance)
- Strategic compression (age-based compression levels)
- Budget management (fit to token limits)

**Key Operations:**
- `remove_duplicates()` - Cluster and deduplicate semantically similar items
- `detect_conflicts()` - Find contradictory information
- `resolve_conflicts()` - Select best stance globally
- `compress_content()` - Age-based strategic compression
- `fit_to_budget()` - Select items within token budget

### 5. Morphological Analysis Component
**Purpose:** Enhanced SUBWORD level indexing through morphological decomposition

**Responsibilities:**
- Decompose words into morphological parts (prefix, root, suffix)
- Store morphological data in HHNI nodes
- Link parts in SEG graph (DERIVES_FROM relations)
- Enhance SUBWORD level with part-of-speech and lemma information

**Key Operations:**
- `tokenize_with_morphology()` - Decompose words into parts
- `analyze_morphology()` - Extract prefix, root, suffix, stem, lemma
- `link_morphological_parts()` - Create SEG relations for parts
- `enhance_subword_indexing()` - Add morphological data to SUBWORD level

**Integration:**
- Integrated into `build_hhni_for_atom()` via `morphology.py`
- Optional SEG integration for part linking
- Backward compatible (works with or without SEG)

### 6. Semantic Block Organizer Component
**Purpose:** Pre-organize content into semantic blocks at index time

**Responsibilities:**
- Cluster related content into semantic blocks (thematic, narrative, conceptual, morphological)
- Pre-compute relationships between blocks
- Enable retrieval of pre-organized blocks instead of isolated chunks
- Maintain block coherence and semantic relationships

**Key Operations:**
- `organize_blocks()` - Cluster content into semantic blocks
- `compute_block_relationships()` - Pre-compute block similarities
- `create_block_centroid()` - Calculate block embedding centroids
- `retrieve_blocks()` - Retrieve pre-organized blocks

**Integration:**
- Integrated into `build_hhni_for_atom()` via `semantic_block_organizer.py`
- Optional integration (backward compatible)
- Works with SEG for relationship tracking

### 7. Cross-Document Relationship Detector Component
**Purpose:** Detect semantic relationships across documents

**Responsibilities:**
- Detect semantic similarity across documents (embedding-based)
- Track narrative context (story-level relationships)
- Accumulate symbolic meaning (meaning over time)
- Create cross-document relations in SEG graph

**Key Operations:**
- `detect_semantic_relationships()` - Find semantic similarities
- `track_narrative_context()` - Identify story-level relationships
- `accumulate_symbolic_meaning()` - Track meaning over time
- `add_cross_doc_relations()` - Create SEG relations

**Integration:**
- Integrated into `build_hhni_for_atom()` via `cross_document_relationships.py`
- Requires SEG graph for relation storage
- Optional integration (backward compatible)

**New SEG Relation Types:**
- `SEMANTICALLY_RELATED` - General semantic similarity
- `NARRATIVE_CONTEXT` - Story-level relationship
- `SYMBOLIC_LINK` - Symbolic meaning connection
- `CO_OCCURS_WITH` - Co-occurrence in context
- `ACCUMULATES_MEANING` - Meaning accumulation over time

### 8. IO/Adapters (CMC, SEG)
**Purpose:** Integration with external systems

**Responsibilities:**
- Read atoms from CMC
- Sync with SEG for evidence indexing and cross-document relationships
- Provide orchestration hooks for APOE
- Emit metrics to VIF

**Key Operations:**
- `index_cmc_atoms()` - Read atoms from CMC, build index
- `sync_seg_evidence()` - Sync evidence nodes with SEG
- `provide_context()` - Serve APOE retrieval requests
- `emit_metrics()` - Send RS-lift metrics to VIF

## Data Models

### Index Entry Schema

```python
@dataclass
class IndexEntry:
    """Entry at any hierarchical level"""
    id: str                          # "sys:auth" or "sent:1234"
    level: int                       # 1-6
    content_summary: str             # Brief description
    embedding: List[float]           # Vector at this abstraction
    
    # Hierarchy
    parent_id: Optional[str]         # Parent entry (e.g., sent→para)
    child_ids: List[str]             # Child entries
    
    # Content
    atom_refs: List[str]             # Atoms at this level
    full_content: Optional[str]      # Full text (if small)
    
    # Metrics
    depth_score: float              # IDS component
    dependency_hash: str            # Change tracking
    
    # Metadata
    created_at: datetime
    last_updated: datetime
```

### Retrieval Request Schema

```python
@dataclass
class RetrievalRequest:
    """Query with constraints"""
    query: str
    query_embedding: Optional[List[float]] = None
    modality_filter: Optional[List[str]] = None
    tag_filters: Optional[List[Tuple[str, str]]] = None
    time_range: Optional[Tuple[datetime, datetime]] = None
    token_budget: int = 8000
    enable_dvns: bool = True
    enable_dedup: bool = True
    enable_conflict_resolution: bool = True
    enable_compression: bool = True
```

### Retrieval Result Schema

```python
@dataclass
class RetrievalResult:
    """Optimized context with metrics"""
    items: List[BudgetItem]
    total_tokens: int
    items_count: int
    rs_lift: float                  # Improvement over baseline
    dvns_applied: bool
    iterations: int                 # Physics iterations
    duplicates_removed: int
    conflicts_resolved: int
    compression_applied: bool
    metrics: Dict[str, Any]
```

### Particle Schema (DVNS)

```python
@dataclass
class Particle:
    """Physics particle for DVNS"""
    item_id: str
    position: NDArray               # Position in embedding space
    velocity: NDArray              # Velocity vector
    acceleration: NDArray          # Acceleration vector
    mass: float                    # Relevance to query
    embedding: NDArray             # Semantic vector
    content: str
```

## Key Flows

### Indexing Pipeline

```
CMC Atoms
    ↓
┌──────────────────┐
│ Extract Structure│ Parse hierarchy (System → Section → ...)
└──────────────────┘
    ↓
┌──────────────────┐
│ Morphological    │ Decompose words into parts (optional)
│ Analysis        │ Enhance SUBWORD level
└──────────────────┘
    ↓
┌──────────────────┐
│ Build 6-Level    │ Construct indices at all levels
│ Index            │
└──────────────────┘
    ↓
┌──────────────────┐
│ Cross-Document   │ Detect relationships across documents (optional)
│ Relationships    │ Add to SEG graph
└──────────────────┘
    ↓
┌──────────────────┐
│ Semantic Blocks  │ Organize into pre-computed blocks (optional)
│ Organization     │ Cluster related content
└──────────────────┘
    ↓
┌──────────────────┐
│ Assign Paths     │ Set hierarchical paths (HHNIPath)
└──────────────────┘
    ↓
┌──────────────────┐
│ Store Entries    │ Persist index entries
└──────────────────┘
    ↓
┌──────────────────┐
│ Link Relationships│ Establish parent-child links
└──────────────────┘
    ↓
Index Complete
```

### Retrieval Pipeline (Two-Stage)

```
Query
    ↓
┌──────────────────┐
│ Stage 1: Coarse │ KNN semantic search (top-100)
│ Retrieval        │ Latency: ~10ms
└──────────────────┘
    ↓
┌──────────────────┐
│ Stage 2: DVNS    │ Physics optimization (50-100 iterations)
│ Physics          │ Latency: ~30-50ms
└──────────────────┘
    ↓
┌──────────────────┐
│ Deduplication    │ Remove semantically similar items
└──────────────────┘
    ↓
┌──────────────────┐
│ Conflict         │ Detect contradictions, select best stance
│ Resolution       │
└──────────────────┘
    ↓
┌──────────────────┐
│ Strategic        │ Age-based compression
│ Compression      │
└──────────────────┘
    ↓
┌──────────────────┐
│ Budget Fitting   │ Respect token limits
└──────────────────┘
    ↓
Optimal Context (p95 < 80ms)
```

### DVNS Physics Flow

```
Create Particles
    ↓
┌──────────────────┐
│ Initialize       │ Set positions, velocities, masses
│ Particles        │
└──────────────────┘
    ↓
┌──────────────────┐
│ Iteration Loop   │ For 50-100 iterations:
│ (Velocity-Verlet)│ 1. Compute forces (gravity, elastic, repulse, damping)
│                  │ 2. Update positions
│                  │ 3. Update velocities
│                  │ 4. Check convergence
└──────────────────┘
    ↓
┌──────────────────┐
│ Reorder by       │ Sort by optimized positions
│ Physics Score    │
└──────────────────┘
    ↓
Optimized Layout
```

## Integrations

**CMC (Context Memory Core):** ✅ **Implemented** (+ Notification Poller v1)
- HHNI reads atoms from CMC, indexes them hierarchically
- Assigns HHNI paths to atoms for dependency tracking
- Retrieves atoms by query, returns optimized context
- Automatic indexing via CMC→HHNI poller (at‑least‑once, idempotent) per `ide_orchestration/prototypes/dac/docs/agents/atlas/ATLAS_CMC_HHNI_NOTIFICATION_PATTERN.md`
- **Code Status:** Implemented – `build_hhni_for_atom()`; poller in `packages/hhni/cmc_poller.py`; tests pass (`packages/hhni/tests/test_cmc_poller.py`)
- **Integration Points:** hierarchical_index (indexing), retrieval (atom retrieval), morphological_analysis (data storage), hhni.cmc_poller (automatic indexing)

**APOE (AI-Powered Orchestration Engine):** ⚠️ **Pattern Only**
- HHNI provides optimized context for reasoning
- Supports multi-step retrieval with plan awareness
- Budget-aware orchestration hooks
- **Code Status:** Pattern documented in `packages/apoe/integration_examples.py`, direct HHNI code pending (likely via MCP)
- **Integration Points:** retrieval (context provision)

**VIF (Verifiable Intelligence Framework):** ⚠️ **Partial**
- HHNI retrieval operations witnessed (VIF envelopes) - **Pending**
- RS-lift metrics tracked (+15% improvement validated) - **✅ Implemented**
- Replay enabled via snapshots - **Pending**
- **Code Status:** RS-lift metrics exist in `RetrievalResult`, witness creation code missing
- **Integration Points:** dvns (RS-lift metrics), retrieval (witnessing)

**SEG (Shared Evidence Graph):** ✅ **Implemented**
- HHNI syncs with SEG for evidence indexing
- Supports contradiction detection via hierarchical relationships
- Evidence nodes linked to index entries
- **Code Status:** Implemented - `seg_graph` parameter exists, `test_seg_integration.py` tests exist
- **Integration Points:** hierarchical_index (hierarchical paths), retrieval (semantic search), morphological_analysis (morphological entities)

**SDF-CVF (Atomic Evolution Framework):** ❌ **Pending**
- HHNI tracks dependency changes via dependency_hash
- Supports quartet parity via index consistency
- SDF-CVF monitors HHNI index quality
- Validates quartet parity across all subsystems (hierarchical_index, dvns, retrieval)
- **Code Status:** Not implemented - Documentation claims integration, but no code found in `packages/hhni/`
- **Integration Points:** hierarchical_index (index consistency), dvns (physics quartet parity), retrieval (retrieval quartet parity)

**CAS (Cognitive Analysis System):** ✅ **Phase 1 Implemented** (env‑gated hooks) / 🔜 Phase 2-3
- Pre‑index + post‑index hooks in `packages/hhni/indexer.py` call `packages.cas.client.ActivationTracker` (`capture_state`, `record_document_read`, `record_concept_use`)
- Retrieval hook in `packages/hhni/retrieval.py` calls `record_principle_use` + `capture_state` (includes `selected_ids`, `dvns_iterations`, `efficiency`, `relevance_score`)
- Env gate: `CAS_ENABLED=true` (fail‑soft import); tests validate calls/payloads (`packages/hhni/tests/test_cas_hooks.py`)
- **Integration Points:** hierarchical_index (activation hooks), retrieval (activation tracking)

**TCS (Timeline Context System):** ❌ **Pending**
- TCS context retrieval for temporal context during indexing (hierarchical_index subsystem)
- TCS context management for retrieval operations (retrieval subsystem)
- Enables temporal correlation of HHNI operations
- **Code Status:** Not implemented - Documentation claims integration, but no code found in `packages/hhni/`
- **Integration Points:** hierarchical_index (temporal context), retrieval (context management)

## The Four Physics Forces

### Force 1: Gravity

Attracts semantically related items toward query:
```python
F_gravity = G · (mass_i · mass_j) / distance² · similarity(i, j)
```
- Mass: Relevance to query (cosine similarity)
- Modulated by: Semantic similarity between items
- Result: Related items cluster together near query

### Force 2: Elastic

Maintains hierarchical structure from HHNI:
```python
F_elastic = k · (current_distance - ideal_distance)
```
- Ideal distance: Based on hierarchical level relationships
- Spring constant: k = 0.5
- Result: Hierarchical structure preserved

### Force 3: Repulse

Separates contradictory information:
```python
F_repulse = δ · contradiction_score / distance²
```
- Contradiction score: From conflict detector
- Repulse strength: δ = 0.3
- Result: Opposing stances kept apart

### Force 4: Damping

Stabilizes system, prevents oscillation:
```python
F_damping = -c · velocity
```
- Damping coefficient: c = 0.1
- Result: Smooth convergence without oscillation

**Integration:** Velocity-Verlet algorithm (2nd-order, energy-conserving), converges in 50-100 iterations.

## Retrieval Score Formula

### RS = QS · IDS · (1 - DD)

**QS (Quality Score):**
```python
QS = (Confidence + Recency + Authority) / 3.0
```
- Confidence: From VIF band (A=1.0, B=0.7, C=0.4)
- Recency: 7-day half-life decay
- Authority: Verified tag boost

**IDS (Index Depth Score):**
```python
IDS = sum(level_weights[i] for i in depth) / sum(weights)
```
- Weights: [0.5, 0.7, 0.9, 1.0, 0.8, 0.6] (Level 4=sentence most important)
- Depth: How many hierarchical levels indexed

**DD (Dependency Drift):**
```python
DD = 1.0 if dependency_hash changed else 0.0
```
- Tracks: Whether dependencies have changed since indexing
- Stale: Needs reindexing if DD = 1.0

**Range:** 0.0-1.0 (higher = better)  
**Used for:** Ranking retrieval results  
**Validated:** +15% improvement at precision-at-rank-5 ✅

## Non‑Functional Requirements

### Performance Targets

**SLOs:**
- Stage 1 (Coarse): < 10ms latency
- Stage 2 (Physics): < 50ms latency
- Total: p95 < 80ms (target: <100ms) ✅
- Throughput: 100 queries/sec

**Current Performance:**
- p95: ~75ms (meeting target) ✅
- Convergence: 50-100 iterations (target: <100) ✅
- Cache hit rate: >80% for repeated queries

### Storage & Scalability

- **Index Size:** ~100MB for 1M atoms (compressed)
- **Update Frequency:** Real-time (on atom change)
- **Scalability:** Horizontal scaling via sharding

### Determinism & Reproducibility

- **Deterministic:** Same query → same results (within epsilon)
- **Reproducible:** Physics simulation converges reliably
- **Auditable:** Full retrieval trace with metrics

## Diagrams

**Component Diagram:**
```
┌─────────────┐
│   Query API │
└──────┬──────┘
       │
┌──────▼──────────────────┐
│   Retrieval Planner     │
├──────────────────────────┤
│  • Coarse Retrieval     │
│  • Physics Refinement   │
│  • Quality Pipeline     │
└──────┬──────────────────┘
       │
┌──────▼──────────────────┐
│   Index Engine          │
├──────────────────────────┤
│  • 6-Level Index        │
│  • Hierarchy Builder    │
└──────┬──────────────────┘
       │
┌──────▼──────────────────┐
│   DVNS Physics Module   │
├──────────────────────────┤
│  • Force Computation    │
│  • Velocity-Verlet      │
│  • Convergence Check    │
└──────┬──────────────────┘
       │
┌──────▼──────────────────┐
│   Quality Filters       │
├──────────────────────────┤
│  • Deduplication        │
│  • Conflict Resolution  │
│  • Compression          │
│  • Budget Fitting       │
└──────────────────────────┘
```

**Sequence Diagram (Retrieval):**
```
Query → Retrieval Planner → Index Engine → DVNS → Quality Filters → Result
  │          │                 │           │           │             │
  └──────────┴─────────────────┴───────────┴───────────┴─────────────┘
```

## References

- System map: `systems/hhni/system.map.lucid.json5`
- Validation gates: `knowledge_architecture/validation/T0_T6_DOCUMENTATION.validation.md`
- Templates: `knowledge_architecture/PERFECT_TEMPLATES_LIBRARY.md`
- L-level docs: `systems/hhni/L0_executive.md` through `L4_complete.md`
- Implementation: `packages/hhni/` (~1,850 lines, 77 tests)


---

## 🔗 RELATED SYSTEMS

### **Systems We Depend On**

#### **APOE**
**Relationship:** bidirectional
**Integration Point:** apoeIntegration
**Data Exchanged:** context_retrieval_requests, optimized_context, multi_step_queries (+ 1 more)
**Security Level:** high
**Docs:** `knowledge_architecture/systems/apoe/T0_executive.md`

#### **CMC**
**Relationship:** bidirectional
**Integration Point:** cmcIntegration
**Data Exchanged:** atoms_for_indexing, hierarchical_paths, retrieval_queries (+ 1 more)
**Security Level:** high
**Docs:** `knowledge_architecture/systems/cmc/T0_executive.md`

#### **VIF**
**Relationship:** bidirectional
**Integration Point:** vifIntegration
**Data Exchanged:** retrieval_operations, rs_lift_metrics, witness_data (+ 1 more)
**Security Level:** high
**Docs:** `knowledge_architecture/systems/vif/T0_executive.md`


### **Systems That Depend On Us**

**Other Systems:** aether_memory_system, ai_collaboration_system, auto_recovery_system, autonomous_research_dream, branch_reasoning_system, ccs, co_agency_trust_layer, consciousness_analyzer, consciousness_creativity_engine, consciousness_learning_engine, context_fidelity_inspector, context_frames_system, context_mesh_maps, cross_model_consciousness, deep_expansion_layer, disconnect_detection_system, drift_detection_system, dynamic_cursor_rules_system, dynamic_onboarding, global_user_rules, intent_classification_system, knowledge_bootstrap_system, memory_pyramid_system, mutation_modes_system

**Layer 1:** cmc, seg

**Layer 2:** sdfcvf, vif

**Layer 3:** apoe

**Layer 4:** cognitive_analysis, intuitive_intelligence_system, timeline_context_system

**Layer 5 (Infrastructure):** consciousness_enhancement, daemon_rag_system, health_monitoring_system, icip_data_storage_layer, llm_client_integration, lucid_mcp_integration, mcp_integration, mcp_tools, self_improvement_protocol, spec_coverage_index, system_integration_protocols

**Layer 6 (Application):** advanced_monaco_editor, agent_system, aimos_mobile_app, deep_context_appendices, icip_code_property_graph, icip_gnn_service, icip_graph_construction_service, icip_llm_inference_service, icip_metric_calculation_service, icip_parser_service, icip_platform, icip_predictive_analytics_service, icip_presentation_api_layer, icip_search_service, lucid_core_console

**Total Dependent Systems:** 58

### **External Systems**

**External Dependencies:** embedding, vector

**Integration Details:** See system map (`system.map.lucid.json5`) for complete integration topology.