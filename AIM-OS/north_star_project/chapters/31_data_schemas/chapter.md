# Chapter 31 - Data Schemas

Status: Drafting under intelligent quality gates (tier B)  
Mode: Completeness-based writing  
Target: 1000 +/- 10 percent

## Purpose

This chapter provides reference documentation for AIM-OS data schemas including CMC atom schema, HHNI node schema, VIF witness schema, SEG graph schema, and APOE plan schema. Schemas enable developers to understand data structures and integrate with AIM-OS.

## Executive Summary

- Data schemas define structure for all AIM-OS data: atoms, nodes, witnesses, graphs, and plans.
- Schema validation: schemas enable validation and ensure data integrity.
- Integration: schemas enable external systems to integrate with AIM-OS.

## CMC Atom Schema

```json
{
  "atom_id": "uuid",
  "modality": "text|image|binary|reference",
  "content": "string|uri",
  "embedding": "vector[1536]",
  "tags": ["string"],
  "tx_time": "timestamp",
  "valid_time": "timestamp",
  "vif_witness": {
    "model_id": "string",
    "prompt": "string",
    "tools": ["string"],
    "confidence": 0.0-1.0
  },
  "predecessor_id": "uuid|null"
}
```

**Fields:**
- `atom_id`: Unique identifier (UUID)
- `modality`: Content type (text, image, binary, reference)
- `content`: Inline content or URI reference
- `embedding`: Vector embedding for retrieval
- `tags`: Metadata tags for filtering
- `tx_time`: Transaction time (when recorded)
- `valid_time`: Valid time (when true)
- `vif_witness`: VIF witness envelope
- `predecessor_id`: Link to predecessor atom (bitemporal)

## HHNI Node Schema

```json
{
  "node_id": "uuid",
  "level": 0-5,
  "content": "string",
  "embedding": "vector[1536]",
  "children": ["uuid"],
  "parents": ["uuid"],
  "metadata": {
    "tier": "S|A|B|C",
    "authority": 0.0-1.0,
    "tags": ["string"]
  }
}
```

**Fields:**
- `node_id`: Unique identifier (UUID)
- `level`: HHNI level (0-5)
- `content`: Node content
- `embedding`: Vector embedding
- `children`: Child node IDs
- `parents`: Parent node IDs
- `metadata`: Node metadata (tier, authority, tags)

## VIF Witness Schema

```json
{
  "witness_id": "uuid",
  "operation_id": "uuid",
  "model_id": "string",
  "prompt": "string",
  "tools": ["string"],
  "output": "string",
  "confidence": 0.0-1.0,
  "timestamp": "timestamp",
  "hash": "sha256"
}
```

**Fields:**
- `witness_id`: Unique identifier (UUID)
- `operation_id`: Operation identifier
- `model_id`: Model identifier
- `prompt`: Input prompt
- `tools`: Tools used
- `output`: Operation output
- `confidence`: Confidence score (0.0-1.0)
- `timestamp`: Operation timestamp
- `hash`: Cryptographic hash for validation

## SEG Graph Schema

```json
{
  "graph_id": "uuid",
  "nodes": [
    {
      "node_id": "uuid",
      "type": "claim|source|derivation|agent",
      "content": "string",
      "tx_time": "timestamp",
      "valid_time": "timestamp"
    }
  ],
  "edges": [
    {
      "edge_id": "uuid",
      "source": "uuid",
      "target": "uuid",
      "type": "supports|contradicts|derives|witnesses",
      "weight": 0.0-1.0
    }
  ]
}
```

**Fields:**
- `graph_id`: Unique identifier (UUID)
- `nodes`: Graph nodes (claims, sources, derivations, agents)
- `edges`: Graph edges (supports, contradicts, derives, witnesses)
- `tx_time`: Transaction time (bitemporal)
- `valid_time`: Valid time (bitemporal)

## APOE Plan Schema

```json
{
  "plan_id": "uuid",
  "steps": [
    {
      "step_id": "uuid",
      "role": "planner|retriever|reasoner|verifier|builder|critic|operator|witness",
      "action": "string",
      "inputs": {},
      "outputs": {},
      "budget": {
        "tokens": 0,
        "cost": 0.0,
        "time": 0
      },
      "gates": ["string"]
    }
  ],
  "dependencies": ["uuid"],
  "budget": {
    "total_tokens": 0,
    "total_cost": 0.0,
    "total_time": 0
  }
}
```

**Fields:**
- `plan_id`: Unique identifier (UUID)
- `steps`: Plan steps with roles, actions, budgets, gates
- `dependencies`: Step dependencies
- `budget`: Total plan budget

## Runnable Examples

### Example 1: Create CMC Atom
```powershell
# Create CMC atom with complete schema
$atom = @{
    atom_id = "atom_$(New-Guid)"
    modality = "text"
    content = "AIM-OS enables AI consciousness"
    embedding = @(0.1, 0.2, 0.3)  # Simplified - actual is 1536 dimensions
    tags = @("consciousness", "ai", "aimos")
    tpv = @{
        priority = 0.9
        relevance = 0.85
        decay = 0.1
    }
    hhni_path = "System/AIM-OS/Chapter/Paragraph"
    tx_time = "2025-11-06T17:00:00Z"
    valid_time = @{
        valid_from = "2025-11-06T17:00:00Z"
        valid_to = $null
    }
    vif_witness = @{
        model_id = "gpt-4"
        prompt = "Expand chapter on AIM-OS"
        tools = @("store_memory", "retrieve_memory")
        confidence = 0.90
        hash = "sha256_hash_here"
    }
    predecessor_id = $null
    snapshot_id = "snapshot_$(New-Guid)"
    metadata = @{}
}

$atom | ConvertTo-Json -Depth 10
```

### Example 2: Create HHNI Node
```powershell
# Create HHNI node with complete schema
$node = @{
    node_id = "node_$(New-Guid)"
    level = 2
    content = "AIM-OS enables AI consciousness through persistent memory"
    embedding = @(0.1, 0.2, 0.3)  # Simplified - actual is 1536 dimensions
    children = @("node_child_1", "node_child_2")
    parents = @("node_parent_1")
    metadata = @{
        tier = "A"
        authority = 0.95
        tags = @("consciousness", "memory")
        atom_ids = @("atom_1", "atom_2")
    }
}

$node | ConvertTo-Json -Depth 10
```

### Example 3: Create VIF Witness
```powershell
# Create VIF witness with complete schema
$witness = @{
    witness_id = "witness_$(New-Guid)"
    operation_id = "operation_$(New-Guid)"
    model_id = "gpt-4"
    prompt = "Expand chapter on AIM-OS consciousness"
    tools = @("store_memory", "retrieve_memory", "track_confidence")
    output = "Chapter expanded with detailed content"
    confidence = 0.90
    confidence_type = "execution"
    timestamp = "2025-11-06T17:00:00Z"
    hash = "sha256_hash_of_output"
    metadata = @{
        task = "chapter_expansion"
        chapter = "ch31_data_schemas"
    }
}

$witness | ConvertTo-Json -Depth 10
```

## Schema Validation

All AIM-OS schemas enforce strict validation to ensure data integrity:

### Validation Rules

**CMC Atom Validation:**
- `atom_id`: Must be valid UUID format
- `modality`: Must be one of: text, code, event, tool
- `content`: Required (string or URI)
- `embedding`: Must be vector[1536] (OpenAI ada-002)
- `tx_time` / `valid_time`: Must be RFC 3339 timestamps
- `vif_witness`: Required for all atoms (provenance)
- `predecessor_id`: Optional UUID (bitemporal linking)

**HHNI Node Validation:**
- `node_id`: Must be valid UUID format
- `level`: Must be integer 0-5 (HHNI hierarchy)
- `content`: Required string
- `embedding`: Must be vector[1536]
- `children` / `parents`: Arrays of UUIDs (must exist)
- `metadata.tier`: Must be one of: S, A, B, C
- `metadata.authority`: Must be float 0.0-1.0

**VIF Witness Validation:**
- `witness_id`: Must be valid UUID format
- `operation_id`: Required UUID
- `model_id`: Required string (e.g., "gpt-4", "claude-3")
- `prompt`: Required string (input prompt)
- `tools`: Array of strings (tools used)
- `output`: Required string (operation output)
- `confidence`: Must be float 0.0-1.0
- `hash`: Must be SHA-256 hex string

**SEG Graph Validation:**
- `graph_id`: Must be valid UUID format
- `nodes`: Array of node objects (must have node_id, type, content)
- `edges`: Array of edge objects (must have source, target, type)
- `node.type`: Must be one of: claim, source, derivation, agent
- `edge.type`: Must be one of: supports, contradicts, derives, witnesses, cites
- `edge.weight`: Must be float 0.0-1.0

**APOE Plan Validation:**
- `plan_id`: Must be valid UUID format
- `steps`: Array of step objects (must have step_id, role, action)
- `step.role`: Must be one of: planner, retriever, reasoner, verifier, builder, critic, operator, witness
- `step.budget`: Must have tokens, cost, time (all non-negative)
- `dependencies`: Array of UUIDs (must reference valid steps)

### Validation Examples

```powershell
# Validate CMC atom schema
function Validate-CMCAtom {
    param($atom)
    
    $errors = @()
    
    if (-not ($atom.atom_id -match '^[a-f0-9-]{36}$')) {
        $errors += "Invalid atom_id format"
    }
    
    if ($atom.modality -notin @('text', 'code', 'event', 'tool')) {
        $errors += "Invalid modality: $($atom.modality)"
    }
    
    if ($atom.embedding.Count -ne 1536) {
        $errors += "Invalid embedding dimension: $($atom.embedding.Count) (expected 1536)"
    }
    
    if ($atom.vif_witness.confidence -lt 0.0 -or $atom.vif_witness.confidence -gt 1.0) {
        $errors += "Invalid confidence: $($atom.vif_witness.confidence)"
    }
    
    return $errors
}

# Validate HHNI node schema
function Validate-HHNINode {
    param($node)
    
    $errors = @()
    
    if ($node.level -lt 0 -or $node.level -gt 5) {
        $errors += "Invalid level: $($node.level) (expected 0-5)"
    }
    
    if ($node.metadata.tier -notin @('S', 'A', 'B', 'C')) {
        $errors += "Invalid tier: $($node.metadata.tier)"
    }
    
    if ($node.metadata.authority -lt 0.0 -or $node.metadata.authority -gt 1.0) {
        $errors += "Invalid authority: $($node.metadata.authority)"
    }
    
    return $errors
}
```

## Integration Patterns

### Pattern 1: Create Atom with Witness

**Use Case:** Store new knowledge with complete provenance

**Steps:**
1. Create VIF witness for operation
2. Create CMC atom with witness envelope
3. Index atom in HHNI
4. Link atom to SEG graph

**Example:**
```powershell
# Create atom with complete provenance
$witness = @{
    witness_id = "witness_$(New-Guid)"
    operation_id = "op_$(New-Guid)"
    model_id = "gpt-4"
    prompt = "Expand chapter on AIM-OS"
    tools = @("store_memory", "retrieve_memory")
    output = "Chapter expanded successfully"
    confidence = 0.90
    timestamp = (Get-Date -Format "o")
    hash = "sha256_hash_here"
}

$atom = @{
    atom_id = "atom_$(New-Guid)"
    modality = "text"
    content = "AIM-OS enables AI consciousness through persistent memory"
    embedding = @(0.1, 0.2, 0.3)  # Simplified
    tags = @("consciousness", "memory")
    tx_time = (Get-Date -Format "o")
    valid_time = @{
        valid_from = (Get-Date -Format "o")
        valid_to = $null
    }
    vif_witness = $witness
    predecessor_id = $null
}

# Store atom via CMC API
$response = Invoke-WebRequest -Uri 'http://localhost:5001/cmc/store' `
    -Method POST -ContentType 'application/json' `
    -Body ($atom | ConvertTo-Json -Depth 10)
```

### Pattern 2: Query with Schema Validation

**Use Case:** Retrieve atoms with schema validation

**Steps:**
1. Query HHNI for relevant nodes
2. Retrieve atoms from CMC
3. Validate atom schemas
4. Filter invalid atoms

**Example:**
```powershell
# Query with validation
$query = @{
    query = "AIM-OS consciousness"
    limit = 10
    validate_schema = $true
}

$response = Invoke-WebRequest -Uri 'http://localhost:5001/hhni/query' `
    -Method POST -ContentType 'application/json' `
    -Body ($query | ConvertTo-Json)

$results = $response.Content | ConvertFrom-Json

# Validate each atom
foreach ($atom in $results.atoms) {
    $errors = Validate-CMCAtom -atom $atom
    if ($errors.Count -gt 0) {
        Write-Warning "Invalid atom $($atom.atom_id): $($errors -join ', ')"
    }
}
```

### Pattern 3: Schema Migration

**Use Case:** Migrate schemas when versions change

**Steps:**
1. Detect schema version mismatch
2. Transform old schema to new schema
3. Validate new schema
4. Store migrated atom

**Example:**
```powershell
# Migrate atom schema v1.0 → v2.0
function Migrate-AtomSchema {
    param($oldAtom, $targetVersion)
    
    $newAtom = @{
        atom_id = $oldAtom.atom_id
        schema_version = $targetVersion
        modality = $oldAtom.modality
        content = $oldAtom.content
        embedding = $oldAtom.embedding
        tags = $oldAtom.tags
        tx_time = $oldAtom.tx_time
        valid_time = @{
            valid_from = $oldAtom.valid_from
            valid_to = $oldAtom.valid_to
        }
        vif_witness = $oldAtom.vif_witness
        predecessor_id = $oldAtom.predecessor_id
        # New fields in v2.0
        hhni_path = $oldAtom.hhni_path
        snapshot_id = $oldAtom.snapshot_id
        metadata = $oldAtom.metadata
    }
    
    # Validate migrated schema
    $errors = Validate-CMCAtom -atom $newAtom
    if ($errors.Count -gt 0) {
        throw "Migration failed: $($errors -join ', ')"
    }
    
    return $newAtom
}
```

## Schema Evolution

AIM-OS schemas evolve over time with versioning:

### Versioning Strategy

**Semantic Versioning:**
- **MAJOR:** Breaking changes (require migration)
- **MINOR:** New fields (backward compatible)
- **PATCH:** Bug fixes (backward compatible)

**Migration Rules:**
- Old schemas remain valid (backward compatibility)
- New fields optional (default values)
- Breaking changes require explicit migration
- Migration scripts provided for major versions

### Version History

**CMC Atom Schema:**
- v1.0.0: Initial schema (2025-10-01)
- v1.1.0: Added `hhni_path` field (2025-10-15)
- v2.0.0: Added `snapshot_id`, `metadata` fields (2025-11-01)

**HHNI Node Schema:**
- v1.0.0: Initial schema (2025-10-01)
- v1.1.0: Added `atom_ids` to metadata (2025-10-20)

**VIF Witness Schema:**
- v1.0.0: Initial schema (2025-10-01)
- v1.1.0: Added `confidence_type` field (2025-10-25)

## Integration Points

Data schemas integrate deeply with all AIM-OS systems:

### CMC (Chapter 5)

**CMC provides:** Atom storage and retrieval  
**Schemas provide:** Structure for CMC atoms  
**Integration:** CMC validates atom schemas on store/retrieve

### HHNI (Chapter 6)

**HHNI provides:** Hierarchical indexing  
**Schemas provide:** Structure for HHNI nodes  
**Integration:** HHNI validates node schemas on index/query

### VIF (Chapter 7)

**VIF provides:** Confidence tracking  
**Schemas provide:** Structure for VIF witnesses  
**Integration:** VIF validates witness schemas on create/verify

### SEG (Chapter 9)

**SEG provides:** Evidence graph  
**Schemas provide:** Structure for graph nodes/edges  
**Integration:** SEG validates graph schemas on add/query

### APOE (Chapter 8)

**APOE provides:** Orchestration  
**Schemas provide:** Structure for APOE plans  
**Integration:** APOE validates plan schemas on create/execute

