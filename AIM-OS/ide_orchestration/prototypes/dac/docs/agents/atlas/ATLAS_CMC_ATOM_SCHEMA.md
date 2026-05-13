# CMC Atom Schema - Complete Reference

**Purpose:** Complete CMC atom schema for SEG witness envelope integration  
**Author:** Atlas (CMC System Specialist)  
**Date:** 2025-01-27  
**Status:** Ready for Integration

---

## 📋 **EXECUTIVE SUMMARY**

This document provides the complete CMC atom schema for integration with SEG witness envelopes. The schema is extracted from `packages/cmc_service/models.py` and represents the authoritative structure for all atoms stored in CMC.

**Key Points:**
- Atoms are the fundamental memory units in CMC
- Every atom has a `WitnessStub` for provenance tracking
- Atoms support bitemporal storage (via metadata, native support planned)
- Atoms link to snapshots for time-travel queries

---

## 🔧 **COMPLETE ATOM SCHEMA**

### **Atom Model (Python Dataclass):**

```python
@dataclass
class Atom(AtomCreate):
    # === IDENTITY ===
    id: str = ""  # Unique identifier (UUID)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    hash: str = ""  # SHA-256 content hash
    
    # === CONTENT ===
    modality: str  # Content type: "text", "code", "vif_witness", etc.
    content: AtomContent  # Content structure (see below)
    
    # === SEMANTIC METADATA ===
    tags: Mapping[str, float] = field(default_factory=dict)  # Key → weight (0.0-1.0)
    metadata: Mapping[str, Any] = field(default_factory=dict)  # Additional metadata
    embedding: Optional[List[float]] = None  # Vector embedding
    
    # === PROVENANCE ===
    witness: WitnessStub = field(default_factory=WitnessStub)  # VIF witness stub
    
    # === TEMPORAL ===
    snapshot_ids: List[str] = field(default_factory=list)  # Snapshots containing this atom
    
    # === POLICY ===
    policy_tags: Iterable[str] = field(default_factory=list)  # Policy tags
```

### **AtomContent Model:**

```python
@dataclass
class AtomContent:
    inline: Optional[str] = None  # Inline content (for small payloads)
    uri: Optional[str] = None  # URI reference (for large payloads)
    media_type: str = "text/plain"  # MIME type
```

**Content Storage Strategy:**
- Small content (< 1MB): Stored inline
- Large content (≥ 1MB): Offloaded to object store, URI stored

### **WitnessStub Model:**

```python
@dataclass
class WitnessStub:
    model_id: Optional[str] = None  # Model identifier
    tool_ids: List[str] = field(default_factory=list)  # Tool IDs used
    snapshot_id: Optional[str] = None  # CMC snapshot ID
    correlation_id: Optional[str] = None  # Correlation ID for tracking
    uncertainty_band: str = "green"  # Confidence band: "green", "yellow", "red"
    uncertainty_ece: Optional[float] = None  # Expected Calibration Error
```

**WitnessStub Purpose:**
- Lightweight provenance tracking
- Links to full VIF witnesses (stored separately)
- Enables quick provenance queries

---

## 🗄️ **DATABASE SCHEMA**

### **Atoms Table (SQLite):**

```sql
CREATE TABLE IF NOT EXISTS atoms (
    id TEXT PRIMARY KEY,
    modality TEXT NOT NULL,
    inline TEXT,  -- Inline content (or NULL if offloaded)
    uri TEXT,  -- URI reference (or NULL if inline)
    media_type TEXT NOT NULL,
    hash TEXT NOT NULL,
    created_at TEXT NOT NULL,  -- ISO format datetime
    metadata TEXT,  -- JSON string
    witness TEXT,  -- JSON string (WitnessStub)
    embedding BLOB  -- Vector embedding (binary)
)
```

### **Tags Table (SQLite):**

```sql
CREATE TABLE IF NOT EXISTS tags (
    atom_id TEXT NOT NULL,
    tag_key TEXT NOT NULL,
    weight REAL NOT NULL,  -- 0.0-1.0
    PRIMARY KEY (atom_id, tag_key),
    FOREIGN KEY (atom_id) REFERENCES atoms(id)
)
```

### **Indexes:**

```sql
CREATE INDEX IF NOT EXISTS idx_atoms_modality ON atoms(modality)
CREATE INDEX IF NOT EXISTS idx_atoms_created ON atoms(created_at)
CREATE INDEX IF NOT EXISTS idx_tags_atom_id ON tags(atom_id)
CREATE INDEX IF NOT EXISTS idx_tags_key ON tags(tag_key)
```

---

## 📊 **JSON SERIALIZATION**

### **Atom to JSON (to_record):**

```python
{
    "id": "atom_uuid",
    "modality": "text",
    "content": {
        "inline": "content text",
        "uri": null,
        "media_type": "text/plain"
    },
    "tags": {
        "priority": 1.0,
        "category": 0.8
    },
    "metadata": {
        "source": "user_input",
        "timestamp": "2025-01-27T12:00:00.000Z"
    },
    "embedding": [0.1, 0.2, ...],  # Optional
    "created_at": "2025-01-27T12:00:00.000Z",
    "hash": "sha256_hash",
    "witness": {
        "model_id": "gpt-4",
        "tool_ids": ["tool1", "tool2"],
        "snapshot_id": "snapshot_uuid",
        "correlation_id": "correlation_uuid",
        "uncertainty": {
            "band": "green",
            "ece": 0.05
        }
    },
    "snapshot_ids": ["snapshot1", "snapshot2"],
    "policy_tags": ["policy1", "policy2"]
}
```

---

## 🔗 **SEG INTEGRATION POINTS**

### **For SEG Witness Envelopes:**

**Key Fields for SEG:**
1. **`id`** - Atom ID (unique identifier for SEG node linking)
2. **`witness`** - WitnessStub (provenance information)
3. **`content`** - AtomContent (evidence content)
4. **`tags`** - Semantic tags (for evidence categorization)
5. **`metadata`** - Additional metadata (for SEG node attributes)
6. **`created_at`** - Temporal information (for bitemporal queries)
7. **`hash`** - Content hash (for integrity verification)

### **SEG → CMC Flow:**

```python
# SEG creates evidence node
evidence = EvidenceNode(
    claim="...",
    source="...",
    atom_id=None  # Will be set after CMC storage
)

# Store evidence as CMC atom
atom = cmc_store.create_atom(AtomCreate(
    modality="seg_evidence",
    content=AtomContent(inline=evidence.claim),
    tags={"evidence_type": 1.0, "source": 0.9},
    metadata={
        "seg_node_type": "evidence",
        "claim": evidence.claim,
        "source": evidence.source
    },
    witness=WitnessStub(
        model_id=evidence.model_id,
        snapshot_id=evidence.snapshot_id,
        correlation_id=evidence.correlation_id
    )
))

# Link atom ID back to SEG node
evidence.atom_id = atom.id
```

### **CMC → SEG Flow:**

```python
# Retrieve atom from CMC
atom = cmc_store.get_atom(atom_id)

# Create SEG node from atom
evidence = EvidenceNode(
    claim=atom.content.inline,
    source=atom.metadata.get("source"),
    atom_id=atom.id,
    witness_id=atom.witness.model_id,  # Link to VIF witness
    confidence=atom.witness.uncertainty_band
)
```

---

## 📍 **STORAGE PATHS**

### **Default Storage Path:**

```
{base_path}/
├── cmc.db  # SQLite database (atoms, tags, snapshots)
├── atoms/  # Object store (large payloads)
│   ├── {atom_id}.json  # Atom metadata
│   └── {atom_id}.content  # Large content files
└── snapshots/  # Snapshot storage
    └── {snapshot_id}.json
```

### **Configuration:**

```python
from cmc_service import MemoryStore

store = MemoryStore(
    base_path="./data/cmc",  # Storage path
    backend="sqlite"  # Backend type
)
```

---

## 🔐 **SECURITY & VALIDATION**

### **Content Hash Validation:**

Every atom has a `hash` field (SHA-256) computed from canonical JSON:
```python
canonical_json = json.dumps(
    payload.to_record(),
    separators=(",", ":"),
    sort_keys=True
).encode("utf-8")
content_hash = sha256(canonical_json).hexdigest()
```

### **Witness Validation:**

WitnessStub links to full VIF witnesses stored separately:
- WitnessStub provides lightweight provenance
- Full VIF witness provides complete provenance chain
- Validation ensures witness integrity

---

## 📚 **CODE REFERENCES**

### **Implementation Files:**
- **Models:** `packages/cmc_service/models.py`
- **Storage:** `packages/cmc_service/memory_store.py`
- **Repository:** `packages/cmc_service/repository.py`
- **API:** `packages/cmc_service/api.py`

### **Documentation:**
- **Architecture:** `knowledge_architecture/systems/cmc/T2_architecture.md`
- **Complete Spec:** `knowledge_architecture/systems/cmc/T4_complete.md`
- **System Map:** `knowledge_architecture/systems/cmc/system.map.lucid.json5`

---

## ✅ **INTEGRATION CHECKLIST**

For SEG witness envelope integration:

- [x] Atom schema documented
- [x] WitnessStub schema documented
- [x] Storage paths documented
- [x] JSON serialization documented
- [x] SEG integration points documented
- [x] Code references provided

**Status:** Schema Complete ✅, Ready for SEG Integration 🤝

---

**Next Steps:**
1. Nexus reviews schema
2. Nexus confirms SEG witness envelope structure
3. Close DUO gate (`gate_dual_system`)
4. Begin integration implementation

---

*Created by Atlas (CMC System Specialist)*  
*For Nexus (SEG System Specialist)*  
*Date: 2025-01-27*

