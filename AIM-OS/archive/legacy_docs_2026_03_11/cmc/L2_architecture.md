---
id: cmc_T2_architecture
level: L2
system: CMC
status: complete
updated: 2025-10-30
---

> TRANSITIONAL T-LEVEL DOCUMENT – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# CMC – T2 Architecture (≈2000 words)

## System Overview

CMC (Context Memory Core) implements the Memory Invariant from AIM-OS's formal axioms: ∀ context c, ∃ reversible mapping c ↔ atom a. This ensures every piece of context can be stored, retrieved, and replayed deterministically.

CMC provides three core guarantees:
1. **Bitemporal Storage:** Every atom has transaction time (when recorded) and valid time (when true in the world)
2. **Deterministic Snapshots:** Content-addressed, immutable bundles enabling time-travel and rollback
3. **Full Provenance:** VIF witness envelopes link every atom to confidence, sources, and verification

## Components

### 1. Memory Store
**Purpose:** Core atom lifecycle management (create, read, update metadata, tombstone)

**Responsibilities:**
- Atom CRUD operations with bitemporal tracking
- Transaction time management (monotonic, never decreases)
- Valid time range management (valid_from, valid_to)
- Atom metadata updates (tags, TPV, embeddings)

**Key Operations:**
- `create_atom()` - Create new atom with dual timestamps
- `update_atom()` - Update metadata (never modifies immutable content)
- `tombstone_atom()` - Mark atom as deleted (valid_to = now)
- `query_atoms()` - Retrieve atoms with filters (modality, time, tags)

### 2. Bitemporal Engine
**Purpose:** Temporal query processing and time-travel operations

**Responsibilities:**
- As-of queries ("what did we know on Oct 15?")
- Temporal range queries (valid_from ≤ t ≤ valid_to)
- Transaction time queries (when was this recorded?)
- Time-travel state restoration

**Key Operations:**
- `query_as_of()` - Get atoms valid at specific time
- `get_history()` - Retrieve temporal history of atom
- `rollback_to_time()` - Restore state to specific transaction time

### 3. Provenance/Witness Store
**Purpose:** VIF witness envelope management and audit trail

**Responsibilities:**
- Store VIF witness envelopes with atoms
- Link atoms to confidence scores, sources, verification
- Provide audit trail for contradiction detection
- Enable provenance queries

**Key Operations:**
- `attach_witness()` - Link VIF envelope to atom
- `get_provenance()` - Retrieve full provenance chain
- `verify_atom()` - Check witness validity

### 4. Snapshot Manager
**Purpose:** Immutable snapshot creation and restoration

**Responsibilities:**
- Content-addressed snapshot creation (SHA-256 hash)
- Deterministic snapshot computation (same atoms → same hash)
- Snapshot lineage tracking (parent-child relationships)
- Rollback and restore operations

**Key Operations:**
- `create_snapshot()` - Bundle atoms into immutable snapshot
- `restore_snapshot()` - Rollback to specific snapshot state
- `list_snapshots()` - Enumerate snapshots with metadata

### 5. API/Schema Layer
**Purpose:** Public interface and data model definitions

**Responsibilities:**
- REST/gRPC API endpoints
- Pydantic schema definitions
- Request/response validation
- Error handling and status codes

**Key Endpoints:**
- `POST /atoms` - Create atom
- `GET /atoms/:id` - Retrieve atom
- `GET /atoms` - Query atoms with filters
- `POST /snapshots` - Create snapshot
- `GET /snapshots/:id` - Retrieve snapshot
- `POST /snapshots/:id/restore` - Restore snapshot

## Data Models

### Atom Schema

```python
class Atom(BaseModel):
    # Identity
    id: str  # Format: "atom_{uuid}"
    
    # Content
    modality: str  # "text", "code", "event", "tool:call", "tool:result"
    content_ref: ContentRef  # Inline or URI reference
    
    # Semantic Layer
    embedding: Optional[Embedding]  # Vector representation
    tags: List[Tag]  # Semantic categorization
    hhni: Optional[HHNIPath]  # Position in fractal index
    
    # Quality & Priority
    tpv: Optional[TPV]  # Tag Priority Vector
    
    # Temporal (Bitemporal)
    created_at: datetime  # Transaction time (when recorded)
    valid_from: Optional[datetime]  # Valid time start (when true)
    valid_to: Optional[datetime]  # Valid time end (None = current)
    
    # Provenance
    snapshot_id: str  # Which snapshot contains this
    vif: VIF  # Witness envelope
```

### ContentRef (Payload Abstraction)

```python
class ContentRef(BaseModel):
    inline: Optional[str]  # Small content embedded (<1KB)
    uri: Optional[str]  # Large content referenced (s3://...)
    media_type: str  # MIME type
    size_bytes: Optional[int]
    hash_sha256: Optional[str]  # Content integrity
```

**Design:** Payloads under 1KB stored inline, larger content externalized to object store.

### Embedding Specification

```python
class Embedding(BaseModel):
    model_id: str  # "text-embedding-3-small", "embed-004"
    dim: int  # 768, 1536, etc.
    vector: List[float]  # The actual embedding
    generated_at: datetime
```

**Strategy:** Primary model Sentence Transformers (`all-MiniLM-L6-v2`) - local, fast. Fallback OpenAI/Anthropic - cloud, higher quality. Cache embeddings to avoid regeneration.

### Tag System & TPV

```python
class Tag(BaseModel):
    key: str  # "topic", "priority", "author"
    value: str  # "authentication", "high", "alice"
    weight: float = 1.0  # Importance (0.0-1.0)
    confidence: Optional[float]  # How certain (0.0-1.0)

class TPV(BaseModel):
    priority: float  # Overall importance (0.0-1.0)
    relevance: float  # How relevant to current task (0.0-1.0)
    decay_tau: Optional[int]  # Decay time constant (seconds)
    last_accessed: Optional[datetime]
```

**Decay Formula:** `relevance(t) = relevance₀ * exp(-(t - t₀) / τ)`

### VIF Witness Envelope

```python
class VIF(BaseModel):
    model_id: str  # Which LLM created this
    weights_hash: Optional[str]  # Model version
    prompt_template_id: Optional[str]  # Which prompt
    tool_ids: List[str]  # Tools used
    writer: str  # System identifier
    confidence_band: Optional[str]  # "A", "B", "C"
    entropy: Optional[float]  # Uncertainty measure
```

Every atom records HOW it was created for full auditability.

### Snapshot Schema

```python
class Snapshot(BaseModel):
    id: str  # Content-addressed: "snap_{sha256}"
    atoms: List[str]  # Atom IDs in this snapshot
    parent_snapshot: Optional[str]  # Git-like lineage
    created_at: datetime
    metadata: Dict[str, Any]  # Freeform annotations
    notes: Optional[str]  # Human description
    hash: str  # SHA-256 of canonical repr
```

**Immutable Property:** Once created, snapshot never modified (C-2 constraint).

## Key Flows

### Write Path (Create Atom)

```
Input Context
    ↓
┌──────────────────┐
│ 1. Ingest        │ Parse input, determine modality
└──────────────────┘
    ↓
┌──────────────────┐
│ 2. Atomize       │ Break into atomic units
└──────────────────┘
    ↓
┌──────────────────┐
│ 3. Enrich        │ Generate embeddings, calculate QS, TPV
└──────────────────┘
    ↓
┌──────────────────┐
│ 4. Index (HHNI)  │ Assign hierarchical path
└──────────────────┘
    ↓
┌──────────────────┐
│ 5. Gate          │ Quality checks, policy validation
└──────────────────┘
    ↓
┌──────────────────┐
│ 6. Persist       │ Write to all stores
└──────────────────┘
    ↓
┌──────────────────┐
│ 7. Snapshot      │ Bundle atoms, compute hash
└──────────────────┘
    ↓
Snapshot ID returned
```

### Read Path (Query Context)

```
Query
    ↓
┌──────────────────┐
│ 1. HHNI Lookup   │ Hierarchical retrieval
└──────────────────┘
    ↓
┌──────────────────┐
│ 2. DVNS Optimize │ Physics-guided layout
└──────────────────┘
    ↓
┌──────────────────┐
│ 3. Deduplicate   │ Remove redundant atoms
└──────────────────┘
    ↓
┌──────────────────┐
│ 4. Resolve       │ Handle contradictions
└──────────────────┘
    ↓
┌──────────────────┐
│ 5. Compress      │ Age-based strategic compression
└──────────────────┘
    ↓
┌──────────────────┐
│ 6. Budget Fit    │ Respect token limits
└──────────────────┘
    ↓
Optimal Context
```

### As-Of Query (Time-Travel)

```
Query: "What did we know about authentication on Oct 15?"
    ↓
┌──────────────────┐
│ 1. Filter        │ valid_from ≤ Oct 15 ≤ valid_to
└──────────────────┘
    ↓
┌──────────────────┐
│ 2. Sort         │ By transaction time (created_at)
└──────────────────┘
    ↓
┌──────────────────┐
│ 3. Resolve       │ Handle temporal conflicts
└──────────────────┘
    ↓
Historical state at Oct 15
```

### Snapshot/Restore

```
Create Snapshot:
    ↓
┌──────────────────┐
│ 1. Collect       │ Gather all current atoms (valid_to = None)
└──────────────────┘
    ↓
┌──────────────────┐
│ 2. Canonicalize  │ Sort atom IDs, compute content hashes
└──────────────────┘
    ↓
┌──────────────────┐
│ 3. Hash          │ SHA-256 of canonical representation
└──────────────────┘
    ↓
┌──────────────────┐
│ 4. Persist       │ Store snapshot metadata
└──────────────────┘
    ↓
Snapshot ID returned

Restore Snapshot:
    ↓
┌──────────────────┐
│ 1. Load          │ Retrieve snapshot by ID
└──────────────────┘
    ↓
┌──────────────────┐
│ 2. Invalidate    │ Mark current atoms as valid_to = now
└──────────────────┘
    ↓
┌──────────────────┐
│ 3. Restore       │ Set snapshot atoms to valid_to = None
└──────────────────┘
    ↓
State restored to snapshot moment
```

## Integrations

**HHNI (Hierarchical Hypergraph Neural Index):**
- CMC provides atoms, HHNI indexes them hierarchically (System → Subword)
- HHNI uses CMC for retrieval context and dependency tracking
- Integration hooks: `index_atom()`, `retrieve_by_path()`, `dvns_optimize()`

**VIF (Verifiable Intelligence Framework):**
- All VIF witnesses stored as atoms in CMC
- CMC provides confidence envelopes and provenance chains
- Integration hooks: `attach_witness()`, `verify_atom()`, `get_provenance()`

**SEG (Shared Evidence Graph):**
- Provenance graph nodes/edges stored in CMC's graph layer
- CMC enables contradiction detection and evidence synthesis
- Integration hooks: `link_evidence()`, `detect_contradictions()`, `synthesize()`

**APOE (AI-Powered Orchestration Engine):**
- APOE retrieves context from CMC, stores execution traces back to CMC
- CMC provides plan state and checkpoint restoration
- Integration hooks: `store_trace()`, `restore_checkpoint()`, `query_context()`

**SDF-CVF (Atomic Evolution Framework):**
- Parity gates enforce CMC schema consistency across code/docs/tests
- CMC stores trace emissions for quartet parity
- Integration hooks: `emit_trace()`, `validate_parity()`, `check_schema()`

## Storage Layers

### Architecture

```
┌─────────────────────────────────────────┐
│         CMC Storage Layers              │
├─────────────────────────────────────────┤
│  Vector Store (Embeddings)              │
│  - Faiss / Chroma / LanceDB            │
│  - Fast KNN search                      │
│  - Embedding → Atom ID mapping         │
├─────────────────────────────────────────┤
│  Object Store (Large Payloads)          │
│  - S3 / MinIO / Local filesystem       │
│  - Content-addressed storage            │
│  - Lazy loading                         │
├─────────────────────────────────────────┤
│  Metadata Store (Atoms, Snapshots)      │
│  - SQLite (local) / PostgreSQL (prod)  │
│  - Indexed by ID, tags, time            │
│  - JSONL fallback for simplicity        │
├─────────────────────────────────────────┤
│  Graph Store (SEG Edges)                │
│  - RDF triples (future)                 │
│  - Neo4j / TypeDB (future)              │
│  - Currently: JSONL with atom refs      │
└─────────────────────────────────────────┘
```

### Metadata Store Schema

```sql
CREATE TABLE atoms (
    id TEXT PRIMARY KEY,
    modality TEXT NOT NULL,
    content_inline TEXT,
    content_uri TEXT,
    created_at TIMESTAMP,
    valid_from TIMESTAMP,
    valid_to TIMESTAMP,
    snapshot_id TEXT,
    metadata_json TEXT,  -- Full atom as JSON
    INDEX idx_modality (modality),
    INDEX idx_snapshot (snapshot_id),
    INDEX idx_created (created_at),
    INDEX idx_valid (valid_from, valid_to)
);

CREATE TABLE snapshots (
    id TEXT PRIMARY KEY,
    hash TEXT UNIQUE,
    created_at TIMESTAMP,
    notes TEXT,
    metadata_json TEXT
);

CREATE TABLE tags (
    atom_id TEXT,
    key TEXT,
    value TEXT,
    weight REAL,
    FOREIGN KEY (atom_id) REFERENCES atoms(id),
    INDEX idx_tag (key, value)
);
```

## Non‑Functional Requirements

### Performance Targets

**SLOs (from thesis):**
- p50 write latency: < 50ms
- p95 write latency: < 200ms
- p99 write latency: < 500ms
- Throughput: 1000 atoms/sec (single writer)

**Current Performance:**
- p95: ~150ms (meeting target)
- Bottleneck: Embedding generation (30-50ms)
- Optimization: Batch embeddings, async processing

### Storage & Retention

- **Retention Policy:** Configurable per atom (TTL, snapshot-based)
- **Compression:** Age-based strategic compression for old atoms
- **Archival:** Move to cold storage after retention period
- **Deduplication:** Content-addressed storage prevents duplicates

### Security & Access

- **Authentication:** API key or OAuth2 for write operations
- **Authorization:** Role-based access control (RBAC)
- **Encryption:** At-rest encryption for sensitive content
- **Audit Logging:** All operations logged with VIF witness envelopes

### Design Constraints

**C-1: Single Writer**
- Enforcement: Lock file, database transaction serialization
- Only one process writes to CMC at a time
- Ensures deterministic ordering and reproducibility

**C-2: Snapshot Immutability**
- Enforcement: Database constraint, immutable data structures
- Snapshots never modified after creation
- Enables rollback, replay, audit

**C-7: Time Ordering**
- Enforcement: Monotonic transaction time
- Transaction time never decreases
- Enables deterministic replay

## Diagrams

**Component Diagram:**
```
┌─────────────┐
│   API Layer │
└──────┬──────┘
       │
┌──────▼──────────────────┐
│    Memory Store         │
├──────────────────────────┤
│  • Atom CRUD            │
│  • Bitemporal Engine    │
│  • Provenance Store     │
│  • Snapshot Manager     │
└──────┬──────────────────┘
       │
┌──────▼──────────────────┐
│   Storage Layers         │
├──────────────────────────┤
│  • Vector Store         │
│  • Object Store         │
│  • Metadata Store       │
│  • Graph Store          │
└──────────────────────────┘
```

**Sequence Diagram (Write Path):**
```
Client → API → Memory Store → HHNI → VIF → Storage → Snapshot
  │       │         │         │      │        │         │
  └───────┴─────────┴─────────┴──────┴────────┴─────────┘
```

## References

- System map: `systems/cmc/system.map.lucid.json5`
- Validation gates: `knowledge_architecture/validation/T0_T6_DOCUMENTATION.validation.md`
- Templates: `knowledge_architecture/PERFECT_TEMPLATES_LIBRARY.md`
- L-level docs: `systems/cmc/L0_executive.md` through `L4_complete.md`
- Implementation: `packages/cmc_service/`
