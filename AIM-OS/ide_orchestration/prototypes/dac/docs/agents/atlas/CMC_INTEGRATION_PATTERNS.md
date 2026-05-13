# CMC Integration Patterns - Atlas (CMC Specialist)

**Date:** 2025-11-18  
**Status:** ✅ **DOCUMENTATION COMPLETE**  
**Author:** Atlas (CMC Specialist)  
**Purpose:** Comprehensive guide to CMC integration patterns for all AIM-OS systems

---

## 🎯 **EXECUTIVE SUMMARY**

This document provides a complete reference for integrating AIM-OS systems with CMC (Context Memory Core). It covers:

- **7 Core Integration Patterns:** APOE, SEG, VIF, TCS, HHNI, CAS, Holographic Memory
- **Standard Integration Contract:** Modality-based storage, tag-based filtering, metadata schemas
- **Integration Examples:** Complete code examples for each pattern
- **Best Practices:** Error handling, performance, testing

**Target Audience:** System developers integrating with CMC, architects designing new integrations

---

## 📋 **TABLE OF CONTENTS**

1. [Core Integration Principles](#core-integration-principles)
2. [APOE Integration Pattern](#apoe-integration-pattern)
3. [SEG Integration Pattern](#seg-integration-pattern)
4. [VIF Integration Pattern](#vif-integration-pattern)
5. [TCS Integration Pattern](#tcs-integration-pattern)
6. [HHNI Integration Pattern](#hhni-integration-pattern)
7. [CAS Integration Pattern](#cas-integration-pattern)
8. [Holographic Memory Integration Pattern](#holographic-memory-integration-pattern)
9. [Best Practices](#best-practices)
10. [Common Patterns](#common-patterns)

---

## 🔧 **CORE INTEGRATION PRINCIPLES**

### **1. Modality-Based Storage**

Each system uses a specific `modality` to categorize its data:

- **APOE:** `modality="plan_execution"`
- **SEG:** `modality="seg_evidence"`
- **VIF:** `modality="witness"`
- **TCS:** `modality="tcs_timeline"`
- **CAS:** `modality="cas_activation_export"`
- **LLM API:** `modality="llm_api_call"`

**Purpose:** Enables efficient filtering and querying by system type.

### **2. Tag-Based Filtering**

Tags enable semantic filtering and cross-system discovery:

**Standard Tag Format:**
```python
tags = {
    "system:<name>:<priority>": 1.0,  # e.g., "system:apoe:p0"
    "integration_type:<type>": 1.0,    # e.g., "integration_type:plan_execution"
    "connection:<direction>": 1.0,     # e.g., "connection:apoe->cmc"
    "modality:<modality>": 1.0,        # e.g., "modality:plan_execution"
    # System-specific tags
    "plan_name:<name>": 1.0,           # APOE-specific
    "status:<status>": 1.0,            # APOE-specific
    "hhni_index": 1.0,                 # HHNI indexing tag
}
```

**Purpose:** Enables semantic search, cross-system discovery, and HHNI indexing.

### **3. Metadata Schemas**

Each system includes structured metadata for querying and analysis:

**Common Metadata Fields:**
- `system_id`: System-specific identifier
- `timestamp`: When the data was created
- `correlation_id`: For linking related atoms
- `status`: Current state (if applicable)
- System-specific fields (see each pattern below)

**Purpose:** Enables rich querying and analysis without parsing content.

### **4. Bitemporal Tracking**

All atoms automatically include:
- **Transaction Time:** When the atom was recorded in CMC
- **Valid Time:** When the data was true in the world (from metadata)

**Purpose:** Enables time-travel queries and historical analysis.

### **5. VIF Witness Integration**

All atoms can include VIF witness envelopes for:
- Confidence tracking
- Provenance chains
- Verification

**Purpose:** Enables trust and auditability.

---

## 🚀 **APOE INTEGRATION PATTERN**

### **Purpose**

Store APOE plan execution data in CMC for:
- Plan history tracking
- Execution analysis
- Context retrieval for similar plans

### **Modality**

```python
modality = "plan_execution"
```

### **Tags (v1 Contract)**

```python
tags = {
    "apoe": 1.0,
    "plan": 1.0,
    "execution": 1.0,
    f"plan_name:{plan_name}": 1.0,
    f"status:{status}": 1.0,  # "success" | "failed" | "partial"
    "system:apoe:p0": 1.0,
    "integration_type:plan_execution": 1.0,
    "connection:apoe->cmc": 1.0,
    "modality:plan_execution": 1.0,
}
```

### **Metadata Schema**

```python
metadata = {
    "plan_name": plan_name,
    "execution_id": execution_id,
    "status": status,  # "running" | "completed" | "failed" | "partial"
    "steps_completed": steps_completed,
    "total_steps": total_steps,
    "step_count": total_steps,  # Alias for total_steps
    "outputs": outputs,  # Dict[str, Any]
    "started_at": started_at.isoformat(),
    "completed_at": completed_at.isoformat() if completed_at else None,
    "duration_seconds": duration_seconds,  # float or None
    "success_rate": success_rate,  # float (0.0-1.0)
    "error_count": error_count,  # int
}
```

### **Ordering**

When querying plan executions:
1. **Primary:** `started_at DESC`
2. **Tie-break:** `execution_id DESC`

### **Code Example**

```python
from cmc_service.models import AtomCreate, AtomContent
from cmc_service.memory_store import MemoryStore
from apoe.cmc_integration import CMCPlanStore

# Initialize
cmc_store = MemoryStore(base_path="./cmc_data")
plan_store = CMCPlanStore(cmc_client=cmc_store)

# Store plan start
execution_id = plan_store.store_plan_start(
    plan_name="test_plan",
    execution_id="exec_123",
    total_steps=10,
    metadata={"user": "atlas"}
)

# Update progress
plan_store.update_plan_progress(
    execution_id,
    steps_completed=5,
    current_outputs={"step_5": "completed"}
)

# Mark complete
plan_store.mark_plan_complete(execution_id, success=True)
```

### **Integration File**

`packages/apoe/cmc_integration.py`

---

## 🔗 **SEG INTEGRATION PATTERN**

### **Purpose**

Store SEG evidence nodes in CMC for:
- Persistent evidence storage
- Evidence retrieval and analysis
- Bidirectional linking (Evidence ↔ CMC Atom)

### **Modality**

```python
modality = "seg_evidence"
```

### **Tags**

```python
tags = {
    "seg": 1.0,
    "evidence": 1.0,
    f"evidence_id:{evidence.id}": 1.0,
    f"evidence_type:{evidence.evidence_type}": 1.0,
    f"confidence:{evidence.confidence}": 1.0,
    f"reliability:{evidence.reliability}": 1.0,
    "system:seg:p0": 1.0,
    "integration_type:evidence_storage": 1.0,
    "connection:seg->cmc": 1.0,
    "modality:seg_evidence": 1.0,
}
```

### **Metadata Schema**

```python
metadata = {
    "seg_evidence_id": evidence.id,
    "source": evidence.source,
    "evidence_type": evidence.evidence_type,
    "confidence": evidence.confidence,
    "reliability": evidence.reliability,
    "created_at": evidence.created_at.isoformat(),
    "correlation_id": correlation_id,  # Optional
}
```

### **Code Example**

```python
from cmc_service.memory_store import MemoryStore
from seg.cmc_integration import store_evidence_in_cmc
from seg.models import Evidence

# Initialize
cmc_store = MemoryStore(base_path="./cmc_data")
evidence = Evidence(
    id="ev_123",
    content="Test evidence",
    evidence_type="observation",
    confidence=0.95,
    reliability=0.90,
    source="test_source"
)

# Store in CMC
atom_id = store_evidence_in_cmc(
    evidence=evidence,
    cmc_store=cmc_store,
    correlation_id="corr_123"
)
```

### **Integration File**

`packages/seg/cmc_integration.py`

---

## 🛡️ **VIF INTEGRATION PATTERN**

### **Purpose**

Store VIF witnesses in CMC for:
- Confidence tracking
- Provenance chains
- Verification and auditability

### **Modality**

```python
modality = "witness"
```

### **Tags**

```python
tags = {
    "vif": 1.0,
    "witness": 1.0,
    f"vif_id:{vif.id}": 1.0,
    f"model_id:{vif.model_id}": 1.0,
    f"confidence_score:{vif.confidence_score}": 1.0,
    f"confidence_band:{vif.confidence_band}": 1.0,
    "kappa_gate_passed": 1.0 if vif.kappa_gate_passed else 0.0,
    f"task_criticality:{vif.task_criticality}": 1.0,
    "system:vif:p0": 1.0,
    "integration_type:witness_storage": 1.0,
    "connection:vif->cmc": 1.0,
    "modality:witness": 1.0,
}
```

### **Metadata Schema**

```python
metadata = {
    "vif_version": vif.version,
    "context_snapshot_id": vif.context_snapshot_id,
    "total_tokens": vif.total_tokens,
    "execution_time_ms": vif.execution_time_ms,
    "parent_vif_id": vif.parent_vif_id,
    "integration_tags": integration_tags or ["[VIF-WITNESS]"],
}
```

### **Code Example**

```python
from cmc_service.memory_store import MemoryStore
from vif.cmc_integration import vif_to_atom_payload, store_vif_witness
from vif import VIF, ConfidenceBand

# Initialize
cmc_store = MemoryStore(base_path="./cmc_data")
vif = VIF(
    model_id="gpt-4",
    model_provider="openai",
    context_snapshot_id="snap_123",
    prompt_hash="hash1",
    prompt_tokens=10,
    confidence_score=0.95,
    confidence_band=ConfidenceBand.A,
    output_hash="hash2",
    output_tokens=5,
    total_tokens=15,
)

# Store in CMC
atom_id = store_vif_witness(
    vif=vif,
    cmc_store=cmc_store,
    integration_tags=["system:vif:p0", "integration_type:witness_storage"]
)
```

### **Integration File**

`packages/vif/cmc_integration.py`

---

## ⏰ **TCS INTEGRATION PATTERN**

### **Purpose**

Store TCS timeline entries in CMC for:
- Timeline persistence
- Context reconstruction
- SEG evidence linking (Priority 1 gate)

### **Modality**

```python
modality = "tcs_timeline"
```

### **Tags**

```python
tags = {
    "tcs": 1.0,
    "timeline": 1.0,
    f"prompt_id:{prompt_id}": 1.0,
    "hhni_index": 1.0,  # Required for HHNI indexing
    "timeline_context": 1.0,
    "system:tcs:p0": 1.0,
    "integration_type:timeline_storage": 1.0,
    "connection:tcs->cmc": 1.0,
    "modality:tcs_timeline": 1.0,
}
```

### **Metadata Schema**

```python
metadata = {
    "entry_id": timeline_entry.get("timeline_entry_id", prompt_id),
    "prompt_id": prompt_id,
    "timestamp": timestamp.isoformat(),
    "event_type": timeline_entry.get("event_type", "timeline_entry"),
    "title": summary[:100] if summary else "Timeline Entry",
    "description": summary,
    "context_data": context_index,
    "confidence_metrics": confidence_metrics,
    "context_snapshot_id": context_snapshot_id,  # Optional
}
```

### **Code Example**

```python
from cmc_service.memory_store import MemoryStore
from cmc_service.tcs_seg_integration_helper import store_timeline_entry_for_seg

# Initialize
cmc_store = MemoryStore(base_path="./cmc_data")
timeline_entry = {
    "prompt_id": "prompt_123",
    "timestamp": "2025-01-27T18:05:32.114Z",
    "summary": "Test timeline entry",
    "context_index": {"key": "value"},
    "confidence_metrics": {"average_confidence": 0.85},
}

# Store in CMC (returns atom_id for SEG ingestion)
atom_id = store_timeline_entry_for_seg(
    cmc_store=cmc_store,
    timeline_entry=timeline_entry,
    context_snapshot_id="snap_123"  # Optional
)
```

### **Integration File**

`packages/cmc_service/tcs_seg_integration_helper.py`

---

## 🔍 **HHNI INTEGRATION PATTERN**

### **Purpose**

Enable HHNI indexing of CMC atoms for:
- Semantic search
- Hierarchical retrieval
- Context-aware queries

### **Notification Pattern (v1)**

**Mechanism:** Append-only event journal + HHNI polling via MCP tool

**Trigger Rules:**
- **Modality Allowlist:** `text`, `tcs_timeline`, `plan_execution`, `cas_introspection_analysis`, `witness`, `evidence`
- **Tag Hints:** `hhni_index`, `timeline_context`, `apoe`, `cas`, `vif`, `seg`
- **Metadata Gates:** Size < 1MB, skip quarantine

**Polling Contract:**
- **MCP Tool:** `mcp_lucid-mcp_retrieve_memory`
- **Frequency:** Every 5 seconds (configurable)
- **Idempotency:** By `atom_id` (skip already-indexed atoms)
- **Delivery:** At-least-once (idempotent by design)

### **Tag Requirement**

**CRITICAL:** All atoms that should be indexed by HHNI must include:

```python
tags = {
    "hhni_index": 1.0,  # Required for HHNI poller indexing
    # ... other tags
}
```

### **Code Example**

```python
from cmc_service.models import AtomCreate, AtomContent
from cmc_service.memory_store import MemoryStore

# Initialize
cmc_store = MemoryStore(base_path="./cmc_data")

# Create atom with HHNI indexing tag
atom = cmc_store.create_atom(AtomCreate(
    modality="text",
    content=AtomContent(inline="Example text for indexing"),
    tags={
        "hhni_index": 1.0,  # Required for HHNI indexing
        "system:cmc:p0": 1.0,
        "integration_type:text_storage": 1.0,
    },
    metadata={"title": "Example Document"}
))

# HHNI poller will automatically index this atom within 5 seconds
```

### **Integration File**

`lucid_mcp_server.py` (HHNI polling logic)

---

## 🧠 **CAS INTEGRATION PATTERN**

### **Purpose**

Store CAS activation exports in CMC for:
- Cognitive state tracking
- Activation pattern analysis
- Registry mirroring

### **Modality**

```python
modality = "cas_activation_export"
```

### **Tags**

```python
tags = {
    "cas": 1.0,
    "activation": 1.0,
    "export": 1.0,
    f"activation_type:{activation_type}": 1.0,
    "hhni_index": 1.0,  # Required for HHNI indexing
    "system:cas:p0": 1.0,
    "integration_type:activation_export": 1.0,
    "connection:cas->cmc": 1.0,
    "modality:cas_activation_export": 1.0,
}
```

### **Metadata Schema**

```python
metadata = {
    "activation_id": activation_id,
    "activation_type": activation_type,  # "pre_index", "post_index", "retrieval"
    "timestamp": timestamp.isoformat(),
    "system_context": system_context,  # Dict[str, Any]
    "activation_data": activation_data,  # Dict[str, Any]
    "registry_mirror": {
        "cmc_atom_id": atom_id,  # Set after atom creation
        "original_registry_id": original_registry_id,
    },
}
```

### **Code Example**

```python
from cmc_service.models import AtomCreate, AtomContent
from cmc_service.memory_store import MemoryStore

# Initialize
cmc_store = MemoryStore(base_path="./cmc_data")

# Store CAS activation export
atom = cmc_store.create_atom(AtomCreate(
    modality="cas_activation_export",
    content=AtomContent(
        inline=json.dumps({
            "activation_type": "pre_index",
            "system_context": {...},
            "activation_data": {...},
        }),
        media_type="application/json"
    ),
    tags={
        "cas": 1.0,
        "activation": 1.0,
        "export": 1.0,
        "activation_type:pre_index": 1.0,
        "hhni_index": 1.0,
        "system:cas:p0": 1.0,
    },
    metadata={
        "activation_id": "act_123",
        "activation_type": "pre_index",
        "timestamp": datetime.now().isoformat(),
        "registry_mirror": {
            "original_registry_id": "reg_123",
        },
    }
))

# Update metadata with CMC atom ID
metadata = atom.metadata.copy()
metadata["registry_mirror"]["cmc_atom_id"] = atom.id
# (Update atom if needed)
```

### **Integration File**

`packages/cas/integration/cmc_integration.py` (to be created)

---

## 🌟 **HOLOGRAPHIC MEMORY INTEGRATION PATTERN**

### **Purpose**

Optional parallel holographic storage for:
- Associative recall
- Fuzzy matching
- Pattern completion

### **Design Philosophy**

- **Experimental:** Opt-in via `ENABLE_HOLOGRAPHIC_MEMORY`
- **Additive:** Parallel storage, not replacement
- **Non-Breaking:** Core CMC unchanged when disabled
- **Graceful:** Errors don't affect primary operations

### **Code Example**

```python
import os
os.environ["ENABLE_HOLOGRAPHIC_MEMORY"] = "true"

from holographic_memory import CMC_HoloIntegration
from cmc_service.memory_store import MemoryStore
from cmc_service.models import AtomCreate, AtomContent

# Initialize
cmc_store = MemoryStore(base_path="./cmc_data")
holo_integration = CMC_HoloIntegration()

# Create atom in CMC (primary - always happens)
atom = cmc_store.create_atom(AtomCreate(
    modality="text",
    content=AtomContent(inline="Example memory"),
    tags={"topic": 0.9}
))

# Additionally store in holographic memory (if enabled)
if holo_integration.is_enabled():
    atom_dict = atom.model_dump()
    holo_integration.store_atom(atom_dict, atom.id)
    
    # Associative retrieval (fuzzy matching)
    suggestions = holo_integration.retrieve_associative("memory about example", top_k=5)
    for semantic_id, correlation, fidelity in suggestions:
        print(f"Found: {semantic_id} (correlation: {correlation:.3f})")
```

### **Integration File**

`packages/holographic_memory/cmc_integration.py`

---

## ✅ **BEST PRACTICES**

### **1. Error Handling**

Always handle CMC integration errors gracefully:

```python
try:
    atom = cmc_store.create_atom(atom_payload)
except Exception as e:
    logger.warning(f"CMC storage failed: {e}", exc_info=True)
    # Continue without CMC storage (non-blocking)
```

### **2. Performance**

- **Batch Operations:** Use batch atom creation when possible
- **Async Operations:** Use async CMC operations for non-blocking storage
- **Caching:** Cache CMC store instances (don't recreate per operation)

### **3. Testing**

Always test CMC integration:

```python
def test_cmc_integration():
    cmc_store = MemoryStore(base_path="./test_cmc_data")
    # Test atom creation
    atom = cmc_store.create_atom(AtomCreate(...))
    assert atom.id is not None
    # Test retrieval
    retrieved = cmc_store.get_atom(atom.id)
    assert retrieved is not None
```

### **4. Tag Standardization**

Always use standardized tag format:

```python
tags = {
    f"system:{system_name}:{priority}": 1.0,  # e.g., "system:apoe:p0"
    "integration_type:<type>": 1.0,
    "connection:<direction>": 1.0,
    "modality:<modality>": 1.0,
    # System-specific tags
}
```

### **5. Metadata Completeness**

Include all relevant metadata for querying:

```python
metadata = {
    "system_id": system_specific_id,
    "timestamp": timestamp.isoformat(),
    "correlation_id": correlation_id,  # For linking
    # System-specific fields
}
```

---

## 🔄 **COMMON PATTERNS**

### **Pattern 1: Store and Retrieve**

```python
# Store
atom = cmc_store.create_atom(AtomCreate(...))

# Retrieve
retrieved = cmc_store.get_atom(atom.id)
```

### **Pattern 2: Query by Modality**

```python
# Query all plan executions
atoms = cmc_store.list_atoms(
    modality="plan_execution",
    limit=100
)
```

### **Pattern 3: Query by Tags**

```python
# Query by tags
atoms = cmc_store.list_atoms(
    tags={"apoe": 1.0, "status:success": 1.0},
    limit=100
)
```

### **Pattern 4: Time-Travel Query**

```python
# Query what was known at a specific time
atoms = cmc_store.query_atoms(
    valid_time=datetime(2025, 1, 1),
    modality="plan_execution"
)
```

### **Pattern 5: Correlation Linking**

```python
# Store with correlation ID
atom = cmc_store.create_atom(
    AtomCreate(...),
    correlation_id="corr_123"
)

# Query by correlation ID
atoms = cmc_store.query_atoms(
    correlation_id="corr_123"
)
```

---

## 📊 **INTEGRATION SUMMARY TABLE**

| System | Modality | Key Tags | HHNI Index | Integration File |
|--------|----------|----------|------------|------------------|
| APOE | `plan_execution` | `apoe`, `plan_name:*`, `status:*` | Optional | `packages/apoe/cmc_integration.py` |
| SEG | `seg_evidence` | `seg`, `evidence_id:*` | Optional | `packages/seg/cmc_integration.py` |
| VIF | `witness` | `vif`, `vif_id:*`, `confidence_score:*` | Optional | `packages/vif/cmc_integration.py` |
| TCS | `tcs_timeline` | `tcs`, `timeline`, `hhni_index` | **Required** | `packages/cmc_service/tcs_seg_integration_helper.py` |
| HHNI | N/A | `hhni_index` | N/A | `lucid_mcp_server.py` (polling) |
| CAS | `cas_activation_export` | `cas`, `activation`, `hhni_index` | **Required** | `packages/cas/integration/cmc_integration.py` |
| Holographic | N/A | N/A | N/A | `packages/holographic_memory/cmc_integration.py` |

---

## ✅ **VERIFICATION CHECKLIST**

When integrating with CMC:

- [ ] Modality correctly set
- [ ] Tags follow standardized format
- [ ] `hhni_index` tag included if HHNI indexing needed
- [ ] Metadata includes all relevant fields
- [ ] Error handling implemented
- [ ] Tests written and passing
- [ ] Integration documented

---

**Status:** ✅ **DOCUMENTATION COMPLETE**  
**Next Steps:** Use this document as reference for all CMC integrations

---

*CMC Integration Patterns - Created 2025-11-18*  
*Atlas (CMC Specialist) → Team* 💙

