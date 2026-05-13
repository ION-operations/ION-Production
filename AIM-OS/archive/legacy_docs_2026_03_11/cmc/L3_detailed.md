---
id: cmc_T3_detailed
level: L3
system: CMC
status: complete
updated: 2025-10-30
---

> TRANSITIONAL T-LEVEL DOCUMENT – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# CMC – T3 Detailed Implementation Guide

## Setup & Interfaces

### Public API Methods

```python
from packages.cmc_service import MemoryStore, Atom, Snapshot, QueryFilter

# Initialize CMC
store = MemoryStore(
    metadata_db="sqlite:///cmc.db",
    vector_store="faiss",
    object_store="s3://cmc-objects/"
)

# Create atom
atom = store.create_atom(
    modality="text",
    content="This is important context",
    tags=[Tag(key="topic", value="authentication")],
    vif=VIF(model_id="gpt-4", writer="system", confidence_band="A")
)

# Query atoms
atoms = store.query_atoms(
    filter=QueryFilter(
        modality=["text"],
        tags=[("topic", "authentication")],
        time_range=(datetime(2025, 10, 1), datetime(2025, 10, 30))
    ),
    budget_tokens=8000
)

# As-of query (time-travel)
historical_atoms = store.query_as_of(
    query="authentication",
    as_of_time=datetime(2025, 10, 15)
)

# Get atom history
history = store.get_history(atom_id="atom_123...")

# Create snapshot
snapshot = store.create_snapshot(
    notes="Pre-deployment checkpoint",
    atom_ids=[a.id for a in current_atoms]
)

# Restore snapshot
store.restore_snapshot(snapshot_id="snap_abc...")
```

### Type Definitions

```python
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class Modality(str, Enum):
    TEXT = "text"
    CODE = "code"
    EVENT = "event"
    TOOL_CALL = "tool:call"
    TOOL_RESULT = "tool:result"

class ContentRef(BaseModel):
    inline: Optional[str] = None  # <1KB stored inline
    uri: Optional[str] = None  # Larger content → object store
    media_type: str = "text/plain"
    size_bytes: Optional[int] = None
    hash_sha256: Optional[str] = None

class Tag(BaseModel):
    key: str
    value: str
    weight: float = 1.0  # 0.0-1.0
    confidence: Optional[float] = None  # 0.0-1.0

class VIF(BaseModel):
    model_id: str
    writer: str
    confidence_band: Optional[str] = None  # "A", "B", "C"
    entropy: Optional[float] = None

class Atom(BaseModel):
    id: str  # Format: "atom_{uuid}"
    modality: Modality
    content_ref: ContentRef
    embedding: Optional[Embedding] = None
    tags: List[Tag] = []
    hhni: Optional[HHNIPath] = None
    tpv: Optional[TPV] = None
    created_at: datetime  # Transaction time
    valid_from: Optional[datetime] = None  # Valid time start
    valid_to: Optional[datetime] = None  # Valid time end (None = current)
    snapshot_id: str
    vif: VIF
```

## Write Path Implementation

### Step 1: Validation

```python
def validate_atom_input(modality: Modality, content: str, vif: VIF) -> None:
    """Validate input before atom creation"""
    # Check modality is valid
    if modality not in Modality:
        raise ValueError(f"Invalid modality: {modality}")
    
    # Check content not empty
    if not content or len(content.strip()) == 0:
        raise ValueError("Content cannot be empty")
    
    # Check VIF required fields
    if not vif.model_id or not vif.writer:
        raise ValueError("VIF must include model_id and writer")
    
    # Check content size limits
    content_bytes = len(content.encode('utf-8'))
    if content_bytes > 10 * 1024 * 1024:  # 10MB limit
        raise ValueError(f"Content too large: {content_bytes} bytes")
```

### Step 2: Timestamp Assignment

```python
def assign_timestamps(
    atom: Atom,
    valid_from: Optional[datetime] = None,
    valid_to: Optional[datetime] = None
) -> Atom:
    """Assign bitemporal timestamps"""
    # Transaction time: when recorded (monotonic, never decreases)
    atom.created_at = get_monotonic_time()
    
    # Valid time: when true in the world
    atom.valid_from = valid_from or atom.created_at
    atom.valid_to = valid_to  # None = current/valid
    
    # Enforce constraints
    if atom.valid_to and atom.valid_from >= atom.valid_to:
        raise ValueError("valid_from must be < valid_to")
    
    return atom
```

### Step 3: Storage & Indexing Hooks

```python
def persist_atom(atom: Atom, store: MemoryStore) -> None:
    """Persist atom to all storage layers"""
    # Single-writer lock (C-1 constraint)
    with store.single_writer_lock():
        # 1. Metadata store (SQLite)
        store.metadata_db.insert_atom(atom)
        
        # 2. Vector store (if embedding exists)
        if atom.embedding:
            store.vector_store.add(
                ids=[atom.id],
                embeddings=[atom.embedding.vector],
                metadata={"modality": atom.modality.value}
            )
        
        # 3. Object store (if content externalized)
        if atom.content_ref.uri:
            # Already stored during ContentRef creation
            pass
        
        # 4. HHNI indexing hook
        if atom.hhni:
            store.hhni_client.index_atom(atom.id, atom.hhni)
        
        # 5. SEG graph hook (if evidence node)
        if "evidence" in [t.key for t in atom.tags]:
            store.seg_client.add_evidence_node(atom.id, atom)
```

## Read Path Implementation

### Query Planner

```python
def query_atoms(
    store: MemoryStore,
    filter: QueryFilter,
    budget_tokens: int = 8000
) -> List[Atom]:
    """Query atoms with filters and budget constraints"""
    # 1. Build query plan
    plan = QueryPlan(
        modality_filter=filter.modality,
        tag_filter=filter.tags,
        time_range=filter.time_range,
        semantic_query=filter.query
    )
    
    # 2. HHNI lookup (hierarchical retrieval)
    candidate_ids = store.hhni_client.retrieve(
        query=filter.query,
        path_hints=filter.hhni_paths,
        k=100  # Initial candidates
    )
    
    # 3. Load atoms from metadata store
    candidates = [store.metadata_db.get_atom(id) for id in candidate_ids]
    
    # 4. Apply filters
    filtered = apply_filters(candidates, plan)
    
    # 5. DVNS optimization (physics-guided layout)
    optimized = store.dvns_optimizer.optimize(filtered, query_embedding)
    
    # 6. Deduplication
    deduped = deduplication.remove_duplicates(optimized)
    
    # 7. Budget fit
    final = budget_fitter.fit_to_budget(deduped, budget_tokens)
    
    return final
```

### As-Of Query (Time-Travel)

```python
def query_as_of(
    store: MemoryStore,
    query: str,
    as_of_time: datetime
) -> List[Atom]:
    """Query atoms valid at specific time"""
    # 1. Semantic search for candidates
    candidate_ids = store.vector_store.search(query_embedding, k=100)
    
    # 2. Load atoms
    candidates = [store.metadata_db.get_atom(id) for id in candidate_ids]
    
    # 3. Filter by valid time
    valid_at_time = [
        atom for atom in candidates
        if atom.valid_from <= as_of_time and
           (atom.valid_to is None or atom.valid_to > as_of_time)
    ]
    
    # 4. Sort by transaction time (for deterministic ordering)
    valid_at_time.sort(key=lambda a: a.created_at)
    
    return valid_at_time
```

### Pagination & Performance

```python
def query_atoms_paginated(
    store: MemoryStore,
    filter: QueryFilter,
    page_size: int = 100,
    cursor: Optional[str] = None
) -> PaginatedResult[Atom]:
    """Paginated query with cursor-based pagination"""
    # Build query
    query = build_query(filter)
    
    # Apply cursor (if provided)
    if cursor:
        query = query.where(Atom.created_at > parse_cursor(cursor))
    
    # Execute with limit
    atoms = store.metadata_db.execute(query.limit(page_size))
    
    # Generate next cursor
    next_cursor = atoms[-1].created_at.isoformat() if atoms else None
    
    return PaginatedResult(
        items=atoms,
        next_cursor=next_cursor,
        has_more=len(atoms) == page_size
    )
```

## Snapshots & Versioning

### Create Snapshot

```python
def create_snapshot(
    store: MemoryStore,
    notes: str,
    atom_ids: Optional[List[str]] = None
) -> Snapshot:
    """Create immutable snapshot"""
    # Single-writer lock
    with store.single_writer_lock():
        # 1. Collect atoms (current if not specified)
        if atom_ids is None:
            atoms = store.metadata_db.get_current_atoms()
        else:
            atoms = [store.metadata_db.get_atom(id) for id in atom_ids]
        
        # 2. Canonicalize (sort for deterministic hash)
        sorted_atom_ids = sorted([a.id for a in atoms])
        sorted_content_hashes = sorted([
            a.content_ref.hash_sha256 for a in atoms
            if a.content_ref.hash_sha256
        ])
        
        # 3. Compute hash
        canonical = json.dumps({
            "atoms": sorted_atom_ids,
            "content_hashes": sorted_content_hashes
        }, sort_keys=True)
        snap_hash = hashlib.sha256(canonical.encode()).hexdigest()
        
        # 4. Create snapshot
        snapshot = Snapshot(
            id=f"snap_{snap_hash[:16]}",
            atoms=sorted_atom_ids,
            created_at=datetime.utcnow(),
            notes=notes,
            hash=snap_hash
        )
        
        # 5. Persist (immutable - never modified)
        store.metadata_db.insert_snapshot(snapshot)
        
        return snapshot
```

### Restore Snapshot

```python
def restore_snapshot(
    store: MemoryStore,
    snapshot_id: str
) -> None:
    """Restore state to snapshot moment"""
    # Single-writer lock
    with store.single_writer_lock():
        # 1. Load snapshot
        snapshot = store.metadata_db.get_snapshot(snapshot_id)
        if not snapshot:
            raise ValueError(f"Snapshot not found: {snapshot_id}")
        
        # 2. Invalidate current atoms (not in snapshot)
        current_atoms = store.metadata_db.get_current_atoms()
        snapshot_atom_set = set(snapshot.atoms)
        
        for atom in current_atoms:
            if atom.id not in snapshot_atom_set:
                atom.valid_to = datetime.utcnow()
                store.metadata_db.update_atom(atom)
        
        # 3. Restore snapshot atoms (set valid_to = None)
        for atom_id in snapshot.atoms:
            atom = store.metadata_db.get_atom(atom_id)
            atom.valid_to = None  # Mark as current
            store.metadata_db.update_atom(atom)
        
        # 4. Log restoration
        store.audit_log.log(
            event="snapshot_restored",
            snapshot_id=snapshot_id,
            timestamp=datetime.utcnow()
        )
```

## Witness Integration

### Accept VIF Envelope

```python
def attach_witness(atom: Atom, vif: VIF) -> Atom:
    """Attach VIF witness envelope to atom"""
    # Validate VIF
    if not vif.model_id or not vif.writer:
        raise ValueError("VIF must include model_id and writer")
    
    # Attach to atom
    atom.vif = vif
    
    # Store in provenance store
    store.provenance_store.record_witness(atom.id, vif)
    
    return atom
```

### Confidence & Provenance Policies

```python
def verify_atom(atom: Atom) -> VerificationResult:
    """Verify atom using provenance policies"""
    # Check VIF confidence band
    confidence = {
        "A": 1.0,
        "B": 0.7,
        "C": 0.4
    }.get(atom.vif.confidence_band, 0.0)
    
    # Check witness chain
    witnesses = store.provenance_store.get_witness_chain(atom.id)
    
    # Apply policy
    if confidence < 0.7:
        return VerificationResult(
            verified=False,
            reason="Low confidence band",
            witnesses=witnesses
        )
    
    return VerificationResult(
        verified=True,
        confidence=confidence,
        witnesses=witnesses
    )
```

## Error Handling

### Input Validation Errors

```python
class AtomValidationError(Exception):
    """Raised when atom input is invalid"""
    pass

def create_atom_safe(...) -> Atom:
    """Create atom with validation"""
    try:
        validate_atom_input(...)
        return create_atom(...)
    except ValueError as e:
        raise AtomValidationError(f"Invalid atom input: {e}")
```

### Storage/Index Failures

```python
class StorageError(Exception):
    """Raised when storage operation fails"""
    pass

def persist_atom_with_retry(atom: Atom, max_retries: int = 3) -> None:
    """Persist atom with retry logic"""
    for attempt in range(max_retries):
        try:
            persist_atom(atom)
            return
        except StorageError as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
```

## Examples

### Example: Write Path

```python
# Create atom with full metadata
atom = store.create_atom(
    modality="text",
    content="Authentication requires JWT tokens",
    tags=[
        Tag(key="topic", value="authentication", weight=1.0),
        Tag(key="priority", value="high", weight=0.9)
    ],
    vif=VIF(
        model_id="gpt-4-turbo",
        writer="system",
        confidence_band="A",
        entropy=0.1
    ),
    valid_from=datetime(2025, 10, 1),
    valid_to=None  # Current
)

# Create snapshot
snapshot = store.create_snapshot(
    notes="Pre-deployment checkpoint",
    atom_ids=[atom.id]
)
```

### Example: Read Path

```python
# Query with filters
atoms = store.query_atoms(
    filter=QueryFilter(
        modality=["text"],
        tags=[("topic", "authentication")],
        time_range=(datetime(2025, 10, 1), datetime(2025, 10, 30))
    ),
    budget_tokens=8000
)

# Time-travel query
historical = store.query_as_of(
    query="authentication",
    as_of_time=datetime(2025, 10, 15)
)
```

### Example: Snapshot/Restore

```python
# Create checkpoint
snapshot = store.create_snapshot(notes="Before major refactor")

# ... make changes ...

# Restore if needed
store.restore_snapshot(snapshot.id)
```

## Tests

### Unit Test Example

```python
def test_create_atom():
    """Test atom creation"""
    store = MemoryStore(memory_db=":memory:")
    
    atom = store.create_atom(
        modality="text",
        content="Test content",
        vif=VIF(model_id="test", writer="test")
    )
    
    assert atom.id.startswith("atom_")
    assert atom.modality == Modality.TEXT
    assert atom.content_ref.inline == "Test content"
    assert atom.created_at is not None
```

### Integration Test Example

```python
def test_snapshot_deterministic():
    """Test snapshot determinism"""
    store = MemoryStore(memory_db=":memory:")
    
    # Create atoms
    atom1 = store.create_atom(...)
    atom2 = store.create_atom(...)
    
    # Create snapshot twice
    snap1 = store.create_snapshot(notes="Test")
    snap2 = store.create_snapshot(notes="Test")
    
    # Should have same hash
    assert snap1.hash == snap2.hash
```

## Migration & Cutover Notes

### T→L Rename Strategy

After review and acceptance:
1. Run validation gate: `knowledge_architecture/validation/T0_T6_DOCUMENTATION.validation.md`
2. Get reviewer sign-off (Braden)
3. Backup L-level files: `mv L*.md L*.md.backup`
4. Rename T-level files: `mv T0_executive.md L0_executive.md` (repeat for T1-T6)
5. Update references in indices/maps
6. Run post-cutover validation
7. Archive old L-level files

### Post-Cutover Validation Checklist

- [ ] All T-level files renamed to L-level
- [ ] Indices updated to reference new L-level paths
- [ ] System maps updated
- [ ] Validation gates pass
- [ ] No broken links
- [ ] Old L-level files archived

## References

- System map: `systems/cmc/system.map.lucid.json5`
- Validation gates: `knowledge_architecture/validation/T0_T6_DOCUMENTATION.validation.md`
- Templates: `knowledge_architecture/PERFECT_TEMPLATES_LIBRARY.md`
- L-level docs: `systems/cmc/L0_executive.md` through `L4_complete.md`
- Implementation: `packages/cmc_service/`
