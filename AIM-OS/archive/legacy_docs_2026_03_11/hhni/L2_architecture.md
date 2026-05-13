---
id: hhni_T2_architecture
level: L2
system: HHNI
status: complete
updated: 2025-10-30
---

> TRANSITIONAL T-LEVEL DOCUMENT – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# HHNI – T2 Architecture (≈2000 words)

## System Overview

HHNI (Hierarchical Hypergraph Neural Index) combines fractal multi-resolution indexing with physics-guided retrieval to solve the "lost in the middle" problem—delivering +15% improvement in retrieval quality while respecting token budgets and maintaining context coherence.

HHNI provides two breakthrough innovations:
1. **6-Level Fractal Hierarchical Index:** Every piece of content indexed at multiple resolutions simultaneously
2. **DVNS Physics Optimization:** Treats context items as particles, applies physics forces to optimize spatial layout

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

### 5. IO/Adapters (CMC, SEG)
**Purpose:** Integration with external systems

**Responsibilities:**
- Read atoms from CMC
- Sync with SEG for evidence indexing
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
│ Build 6-Level    │ Construct indices at all levels
│ Index            │
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

**CMC (Context Memory Core):**
- HHNI reads atoms from CMC, indexes them hierarchically
- Assigns HHNI paths to atoms for dependency tracking
- Retrieves atoms by query, returns optimized context

**APOE (AI-Powered Orchestration Engine):**
- HHNI provides optimized context for reasoning
- Supports multi-step retrieval with plan awareness
- Budget-aware orchestration hooks

**VIF (Verifiable Intelligence Framework):**
- HHNI retrieval operations witnessed (VIF envelopes)
- RS-lift metrics tracked (+15% improvement validated)
- Replay enabled via snapshots

**SEG (Shared Evidence Graph):**
- HHNI syncs with SEG for evidence indexing
- Supports contradiction detection via hierarchical relationships
- Evidence nodes linked to index entries

**SDF-CVF (Atomic Evolution Framework):**
- HHNI tracks dependency changes via dependency_hash
- Supports quartet parity via index consistency
- SDF-CVF monitors HHNI index quality

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
