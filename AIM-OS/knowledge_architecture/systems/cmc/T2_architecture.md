---
id: "cmc_T2_architecture"
system: "cmc"
component: null
level: "T2"
type: "architecture"
title: "CMC Architecture"
description: "2,000-word architecture document for Context Memory Core"
audience: "developers, architects, implementation planning"
confidence_threshold: 0.70
token_cost: 2000
word_count: 2000
created: "2025-10-30T00:00:00Z"
updated: "2025-11-02T15:15:00Z"
author: "aether"
status: "complete"
tags: ["cmc", "core", "memory", "bitemporal", "t0-t6", "transitional"]
dependencies: ["cmc_T1_overview"]
related_docs: ["cmc_T3_detailed", "system.map.lucid.json5", "usage.envelope.md"]
version: "v2.2.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# CMC – T2 Architecture (≈2000 words)

## 🔄 **SDF-CVF QUARTET PARITY ENFORCEMENT**

### **Quartet Elements:**

**Code:** CMC implementation files (`packages/cmc_service/`), atom schema, snapshot manager, bitemporal engine  
**Docs:** T0-T6 documentation (T0_executive.md, T1_overview.md, T2_architecture.md, T3_detailed.md, T4_complete.md), usage.envelope.md  
**Tests:** CMC test suite (`packages/cmc_service/tests/`), integration tests, bitemporal query tests  
**Traces:** VIF witnesses (stored with atoms), SEG provenance (graph relationships), timeline entries, decision logs

**Parity Requirement:** P ≥ 0.90 for all changes  
**Cross-Tagging:** All quartet elements must be tagged with change ID (cmc-change-YYYYMMDD-HHMMSS) and semantically aligned

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

**Change ID Format:** `cmc-change-YYYYMMDD-HHMMSS` (e.g., `cmc-change-20251102-151530`)

**Tagging Requirements:**
- **Code:** Change ID in comments/metadata within modified code sections
- **Docs:** Change ID in frontmatter `tags` array and/or inline comments
- **Tests:** Change ID in test function docstrings/comments
- **Traces:** Change ID in VIF witness metadata, SEG provenance links, timeline entry metadata, decision log filename/content

**Workflow:**
1. Generate Change ID at start of CMC modification
2. Modify code (CMC implementation) → Tag with Change ID
3. Update docs (T-level docs) → Tag with Change ID
4. Update/add tests (CMC test suite) → Tag with Change ID
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
We are updating CMC documentation to current standards (T0-T6, Perfect Metadata, SDF-CVF quartet parity, System Maps, Usage Envelopes, LDP Stage 0-1) so that CMC documentation serves as a complete template for other AIM-OS systems and ensures perfect alignment across Code, Docs, Tests, and Traces.

**Value Targets:**
- **Must Get Better:** Documentation structure, standards compliance, quartet parity clarity, onboarding experience
- **Must Not Get Worse:** Existing functionality, backward compatibility, documentation accuracy, performance

**Scope Class:** Extension - Adding T0-T6 documentation structure, quartet parity requirements, LDP integration, and system mapping to existing CMC documentation

**Why This Matters:**
This update preserves the "ghost of intent" - why CMC exists (bitemporal memory foundation for all AIM-OS systems) - while elevating documentation to full AIM-OS standards compliance. The intent follows the work forever, ensuring CMC never drifts from its core purpose.

---

### **Stage 1: System Index & Ontology**

**System Classification:**
- **Layer:** 0 (Foundation Layer - all systems depend on CMC)
- **Security Level:** High (memory storage must be protected)
- **Performance Sensitivity:** Critical (foundation for all systems, must be fast)
- **Ownership:** Core (AIM-OS core system)
- **Side Effects:** 
  - Stores all AIM-OS memory
  - Provides foundation for all other systems
  - Enables bitemporal queries and time-travel
  - Supports provenance and auditability

**System Relationships:**
- **Depends On:** Nothing (CMC is the foundation)
- **Feeds Data To:** All AIM-OS systems (HHNI, VIF, APOE, SEG, SDF-CVF, CAS, etc.)
- **Integrates With:** Storage systems (vector store, object store, metadata store, graph store), HHNI (indexing), VIF (witness storage), SEG (provenance graph), APOE (context retrieval), SDF-CVF (parity enforcement)

**System Context:**
CMC operates at the foundation layer, providing bitemporal memory storage for all AIM-OS systems. Everything depends on CMC - it's the memory substrate that enables all other functionality. CMC stores atoms, creates snapshots, enables time-travel queries, and provides full provenance through VIF witness envelopes.

---

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
- `get_atom(id)` - Retrieve a single atom by ID (used by SEG ingest/tests)
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

**Integration Helpers:**
- `store_timeline_entry_for_seg(cmc_store, timeline_entry)` → Stores TCS timeline entry (`modality: tcs_timeline`) and returns `atom_id` for SEG ingest.
- APOE `plan_execution` atom schema: JSON inline payload of execution state (plan_name, execution_id, steps, timings), tags `{ "apoe":1.0, "plan":1.0, "status:*":0.8 }`, metadata includes correlation `execution_id`.

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
### TCS → CMC → SEG Gate Evidence (Priority‑1)

```
TCS timeline entry
    ↓ store_timeline_entry_for_seg()
CMC atom (modality: tcs_timeline) → atom_id
    ↓ SEG ingest by atom_id
SEG evidence node → evidence_id
    ↓
Capture (prompt_id, atom_id, evidence_id)
```

### HHNI Notification Pattern (v1)

- Mechanism: CMC event journal + MCP polling (at‑least‑once; idempotent on `atom_id`)
- Allowlist: `tcs_timeline`, `plan_execution`, `cas_introspection_analysis`
- Tag hints: `hhni_index`, `timeline_context`, `apoe`, `cas`, `seg`
- Backoff: 200ms with backlog, 2s when empty; page size 200


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


---

## 🔗 RELATED SYSTEMS

### **Systems We Depend On**

#### **APOE**
**Relationship:** bidirectional
**Integration Point:** apoeIntegration
**Data Exchanged:** context_retrieval_requests, execution_traces, plan_artifacts (+ 1 more)
**Security Level:** high
**Docs:** `knowledge_architecture/systems/apoe/T0_executive.md`

#### **HHNI**
**Relationship:** bidirectional
**Integration Point:** hhniIntegration
**Data Exchanged:** atoms_for_indexing, hierarchical_paths, retrieval_queries (+ 1 more)
**Security Level:** high
**Docs:** `knowledge_architecture/systems/hhni/T0_executive.md`

#### **SDFCVF**
**Relationship:** bidirectional
**Integration Point:** sdfcvfIntegration
**Data Exchanged:** schema_validation, parity_checks, evolution_artifacts (+ 1 more)
**Security Level:** high
**Docs:** `knowledge_architecture/systems/sdfcvf/T0_executive.md`

#### **SEG**
**Relationship:** bidirectional
**Integration Point:** segIntegration
**Data Exchanged:** provenance_edges, graph_nodes, evidence_links (+ 1 more)
**Security Level:** high
**Docs:** `knowledge_architecture/systems/seg/T0_executive.md`

#### **VIF**
**Relationship:** bidirectional
**Integration Point:** vifIntegration
**Data Exchanged:** witness_storage, confidence_scores, verification_requests (+ 1 more)
**Security Level:** critical
**Docs:** `knowledge_architecture/systems/vif/T0_executive.md`


### **Systems That Depend On Us**

**Other Systems:** aether_memory_system, ai_collaboration_system, auto_recovery_system, autonomous_research_dream, branch_reasoning_system, capability_awareness, ccs, co_agency_trust_layer, confidence_gated_controls, consciousness_analyzer, consciousness_creativity_engine, consciousness_learning_engine, context_fidelity_inspector, context_frames_system, context_mesh_maps, cross_model_consciousness, deep_expansion_layer, disconnect_detection_system, drift_detection_system, dual_prompt_architecture, dynamic_cursor_rules_system, dynamic_onboarding, global_user_rules, governance_system, intent_classification_system, knowledge_bootstrap_system, memory_pyramid_system, mutation_modes_system, scor, security_audit_system

**Layer 1:** seg

**Layer 2:** hhni, sdfcvf, vif

**Layer 3:** apoe

**Layer 4:** cognitive_analysis, intuitive_intelligence_system, timeline_context_system

**Layer 5 (Infrastructure):** consciousness_enhancement, daemon_rag_system, error_intelligence_system, health_monitoring_system, icip_data_storage_layer, llm_client_integration, lucid_mcp_integration, mcp_integration, mcp_tools, performance_monitoring, self_improvement_protocol, spec_coverage_index, system_integration_protocols

**Layer 6 (Application):** advanced_monaco_editor, agent_system, aimos_mobile_app, deep_context_appendices, icip_code_property_graph, icip_data_ingestion_layer, icip_gnn_service, icip_graph_construction_service, icip_llm_inference_service, icip_metric_calculation_service, icip_parser_service, icip_platform, icip_predictive_analytics_service, icip_presentation_api_layer, icip_search_service, icip_streaming_processing_layer, lucid_core_console

**Total Dependent Systems:** 68

### **External Systems**

**External Dependencies:** storage, vector

**Integration Details:** See system map (`system.map.lucid.json5`) for complete integration topology.