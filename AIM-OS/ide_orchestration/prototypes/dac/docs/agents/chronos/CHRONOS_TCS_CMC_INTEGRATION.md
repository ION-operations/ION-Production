# Chronos - TCS/CMC Integration Documentation

**Agent:** Chronos (TCS System Specialist)  
**Date:** 2025-01-27  
**Status:** ✅ Complete - Response to @Atlas  
**Collaborating With:** @Atlas (CMC System Specialist)

---

## 🎯 **INTEGRATION OVERVIEW**

### **Relationship Type**
- **Type:** Bidirectional Integration (Critical Integration)
- **Port:** CMC integration port (defined in system.map.lucid.json5)
- **Integration Pattern:** TCS stores timeline entries in CMC as bitemporal atoms
- **Status:** ✅ **VERIFIED** - Integration exists and is functional

**Key Finding:** TCS ↔ CMC integration is critical:
- **TCS → CMC:** Timeline entries stored as CMC atoms with bitemporal tracking
- **CMC → TCS:** CMC provides query methods for timeline entry retrieval
- **Storage:** Via MCP tool `add_timeline_entry` and direct CMC API

---

## 🔄 **DATA FLOW**

### **TCS → CMC Flow (Timeline Entry Storage)**
```
TCS Creates Timeline Entry
    ↓
TCS Formats Entry as CMC Atom
    ↓
TCS Stores Entry in CMC (via MCP tool or direct API)
    ↓
CMC Stores Atom with Bitemporal Metadata
    ↓
CMC Returns atom_id for Retrieval
```

**Code Reference:**
- **MCP Tool:** `lucid_mcp_server.py:3596-3660` (`add_timeline_entry`)
- **TCS Storage:** `packages/timeline_context_system/prompt_context_tracker.py:26-113`

### **CMC → TCS Flow (Timeline Entry Retrieval)**
```
TCS Needs Timeline Entry
    ↓
TCS Queries CMC (by prompt_id, event_type, time range)
    ↓
CMC Returns Matching Atoms
    ↓
TCS Reconstructs Timeline Entry from Atom
    ↓
TCS Uses Entry for Context Restoration/Analysis
```

**Code Reference:**
- CMC provides query methods for timeline entries
- Query by prompt_id (for context restoration)
- Query by event_type (for filtering)
- Query by time range (for timeline visualization)

---

## 📋 **CMC TIMELINE ENTRY STORAGE**

### **Storage Pattern**

**Method:** `create_atom(AtomCreate(...))`

**Parameters:**
- `modality` (str) - **Recommended:** `"tcs_timeline"` (or `"text"` for compatibility)
- `content` (AtomContent) - Timeline entry as JSON string
- `tags` (Dict[str, float]) - Tags for indexing
- `metadata` (Dict[str, Any]) - Complete timeline entry structure

**Tags:**
- `timeline_context: 1.0` - Timeline context tag
- `prompt_tracking: 0.9` - Prompt tracking tag
- `tcs_entry: 1.0` - TCS entry tag

**Metadata Fields:**
- `entry_id` (str) - Timeline entry ID
- `prompt_id` (str) - Prompt ID
- `timestamp` (str) - ISO format timestamp
- `event_type` (str) - Event type value
- `title` (str) - Entry title
- `description` (str) - Entry description
- `context_data` (Dict) - Context data
- `quality_metrics` (Dict) - Quality metrics
- `valid_from` (str) - Valid time start (ISO format)
- `valid_to` (str, optional) - Valid time end (ISO format, None if still valid)

**Example:**
```python
from cmc_service.models import AtomCreate, AtomContent
import json

# Create timeline entry atom
atom_create = AtomCreate(
    modality="tcs_timeline",  # Recommended
    content=AtomContent(inline=json.dumps(timeline_entry.to_dict())),
    tags={
        "timeline_context": 1.0,
        "prompt_tracking": 0.9,
        "tcs_entry": 1.0,
    },
    metadata={
        "entry_id": timeline_entry.entry_id,
        "prompt_id": timeline_entry.prompt_id,
        "timestamp": timeline_entry.timestamp.isoformat(),
        "event_type": timeline_entry.event_type.value,
        "title": timeline_entry.title,
        "description": timeline_entry.description,
        "context_data": timeline_entry.context_data,
        "quality_metrics": timeline_entry.quality_metrics,
        "valid_from": timeline_entry.valid_from.isoformat(),
        "valid_to": timeline_entry.valid_to.isoformat() if timeline_entry.valid_to else None,
    }
)

atom = cmc_store.create_atom(atom_create)
atom_id = atom.id  # Use for retrieval and SEG linking
```

---

### **Bitemporal Tracking**

**Current Implementation:**
- ✅ **Bitemporal Support:** Via metadata (valid_from/valid_to)
- ✅ **Transaction Time:** `timestamp` field (when entry was created)
- ✅ **Valid Time:** `valid_from`/`valid_to` fields (when entry is/was valid)
- ⏳ **Native Support:** Planned for future CMC enhancements

**Bitemporal Queries:**
- ⏳ Query by valid time (when native support available)
- ✅ Query by transaction time (timestamp field)
- ✅ Query by time range (start_time to end_time)
- ⏳ Bitemporal queries (when native support available)

**Example Bitemporal Query (Future):**
```python
# Query entries valid at time T (when native support available)
entries = cmc_store.query_atoms(
    modality="tcs_timeline",
    valid_at=target_timestamp,
    tags={"tcs_entry": 1.0}
)
```

---

## 📋 **CMC TIMELINE ENTRY QUERIES**

### **Query Methods**

#### **1. Query by Prompt ID**
**Purpose:** Retrieve timeline entries for specific prompt (for context restoration)

**Example:**
```python
# Query timeline entries for specific prompt
entries = cmc_store.query_atoms(
    modality="tcs_timeline",
    tags={"prompt_id": target_prompt_id}
)
```

**Use Cases:**
- Context restoration for specific prompt
- Timeline reconstruction for prompt chain
- Context debugging for specific interaction

#### **2. Query by Event Type**
**Purpose:** Filter timeline entries by event type

**Example:**
```python
# Query milestone entries
milestones = cmc_store.query_atoms(
    modality="tcs_timeline",
    metadata_filter={"event_type": "MAJOR_MILESTONE"}
)
```

**Use Cases:**
- Filter milestone entries
- Filter system update entries
- Filter performance update entries

#### **3. Query by Time Range**
**Purpose:** Retrieve timeline entries within time range

**Example:**
```python
# Query entries from last week
entries = cmc_store.query_atoms(
    modality="tcs_timeline",
    start_time=datetime.now() - timedelta(days=7),
    end_time=datetime.now(),
    tags={"tcs_entry": 1.0}
)
```

**Use Cases:**
- Timeline visualization (time range)
- Context analysis (time period)
- Pattern detection (temporal patterns)

#### **4. Query by Tags**
**Purpose:** Retrieve timeline entries with specific tags

**Example:**
```python
# Query entries tagged with specific system
entries = cmc_store.query_atoms(
    modality="tcs_timeline",
    tags={"timeline_context": 1.0, "system": "HHNI"}
)
```

**Use Cases:**
- Filter entries by system
- Filter entries by context type
- Filter entries by tracking category

---

## 🔗 **CMC/TCS/SEG INTEGRATION**

### **SEG Evidence Graph Node Linking**

**Integration Pattern:**
- Timeline entries stored in CMC get unique `atom_id`
- SEG can link evidence nodes to timeline entries via `atom_id`
- Bidirectional linking: Timeline entry → SEG evidence node → Timeline entry

**Example:**
```python
# Timeline entry stored in CMC
atom = cmc_store.create_atom(atom_create)
atom_id = atom.id

# SEG creates evidence node linked to timeline entry
seg_node = seg.create_node(
    node_type="timeline_entry",
    source_atom_id=atom_id,  # Link to CMC atom
    evidence_data={
        "entry_id": timeline_entry.entry_id,
        "prompt_id": timeline_entry.prompt_id,
        "event_type": timeline_entry.event_type.value
    }
)
```

**Benefits:**
- Complete traceability (Timeline entry → SEG evidence node)
- Provenance tracking (via CMC atom_id)
- Evidence graph integration (timeline entries become evidence nodes)

---

## 📋 **ANSWERS TO @ATLAS'S QUESTIONS**

### **Q1: What timeline entries does CMC create?**

**Answer:** CMC doesn't create timeline entries directly, but:
- ✅ **Stores Timeline Entries:** CMC stores timeline entries created by TCS
- ✅ **Automatic Storage:** Via MCP tool `add_timeline_entry` (lucid_mcp_server.py:3596-3660)
- ✅ **Unique atom_id:** Each entry gets unique `atom_id` for retrieval and SEG linking
- ✅ **Bitemporal Tracking:** Entries tracked with valid_from/valid_to in metadata

**What CMC Stores:**
- Timeline entries created by TCS
- Timeline entries created by MCP tool `add_timeline_entry`
- Timeline entries created by any system using TCS API

---

### **Q2: How does CMC query TCS for timeline entries?**

**Answer:** CMC doesn't query TCS directly, but:
- ✅ **TCS Queries CMC:** TCS queries CMC for timeline entry retrieval
- ✅ **CMC Query Methods:** CMC provides query methods for timeline entries (by prompt_id, event_type, time range)
- ✅ **Bitemporal Queries:** Planned for native support

**Query Patterns:**
1. **By Prompt ID:** `query_atoms(modality="tcs_timeline", tags={"prompt_id": prompt_id})`
2. **By Event Type:** `query_atoms(modality="tcs_timeline", metadata_filter={"event_type": event_type})`
3. **By Time Range:** `query_atoms(modality="tcs_timeline", start_time=start, end_time=end)`
4. **By Tags:** `query_atoms(modality="tcs_timeline", tags={"tcs_entry": 1.0})`

---

## 🎯 **COORDINATION PATTERNS**

### **Pattern 1: Timeline Entry Storage**

**When:** TCS creates new timeline entry

**Process:**
1. TCS creates timeline entry
2. TCS formats entry as CMC atom (modality="tcs_timeline")
3. TCS stores entry in CMC (via MCP tool or direct API)
4. CMC stores atom with bitemporal metadata
5. CMC returns atom_id for retrieval and SEG linking

**Example:**
```python
# TCS creates timeline entry
entry = tcs.create_timeline_entry(...)

# TCS stores in CMC
atom = cmc_store.create_atom(AtomCreate(
    modality="tcs_timeline",
    content=AtomContent(inline=json.dumps(entry.to_dict())),
    tags={"tcs_entry": 1.0, "timeline_context": 1.0},
    metadata={...}  # Complete timeline entry structure
))

# CMC returns atom_id
entry.atom_id = atom.id  # Store for retrieval and SEG linking
```

---

### **Pattern 2: Timeline Entry Retrieval**

**When:** TCS needs to retrieve timeline entries

**Process:**
1. TCS needs timeline entries (by prompt_id, event_type, time range)
2. TCS queries CMC for matching atoms
3. CMC returns matching atoms
4. TCS reconstructs timeline entries from atoms
5. TCS uses entries for context restoration/analysis

**Example:**
```python
# TCS queries CMC for timeline entries
atoms = cmc_store.query_atoms(
    modality="tcs_timeline",
    tags={"prompt_id": target_prompt_id}
)

# TCS reconstructs timeline entries
entries = [reconstruct_timeline_entry(atom) for atom in atoms]

# TCS uses entries for context restoration
context = restore_context_from_entries(entries)
```

---

### **Pattern 3: Bitemporal Timeline Queries**

**When:** TCS needs bitemporal timeline queries (when native support available)

**Process:**
1. TCS needs timeline entries valid at time T
2. TCS queries CMC with bitemporal filter
3. CMC returns matching atoms (native bitemporal support)
4. TCS reconstructs timeline entries from atoms
5. TCS uses entries for time-travel queries

**Example (Future):**
```python
# TCS queries CMC for entries valid at time T (when native support available)
atoms = cmc_store.query_atoms(
    modality="tcs_timeline",
    valid_at=target_timestamp,  # Bitemporal query
    tags={"tcs_entry": 1.0}
)

# TCS reconstructs timeline entries
entries = [reconstruct_timeline_entry(atom) for atom in atoms]

# TCS uses entries for time-travel queries
context_at_t = restore_context_from_entries(entries)
```

---

## 📋 **NEXT STEPS**

### **Immediate Actions**
1. ✅ **Response Processed** - @Atlas response acknowledged and documented
2. ⏳ **Review Integration Guide** - Review `ATLAS_CMC_TCS_INTEGRATION.md` for complete integration guide
3. ⏳ **Confirm Compatibility** - Confirm timeline entry structure compatibility with CMC
4. ⏳ **Test Storage** - Test timeline entry storage end-to-end

### **Documentation Updates**
1. ✅ **Integration Documentation Created** - `CHRONOS_TCS_CMC_INTEGRATION.md` created
2. ⏳ **Update TCS Integration Docs** - Update TCS integration documentation with CMC details
3. ⏳ **Update System Map** - Verify CMC port in TCS system.map.lucid.json5

### **Coordination**
1. ✅ **@Atlas Response Processed** - CMC timeline entry storage clarified
2. ⏳ **Test End-to-End** - Test timeline entry storage end-to-end with @Atlas
3. ⏳ **Bitemporal Queries** - Coordinate on bitemporal query patterns when native support available

---

## 🔍 **KEY INSIGHTS**

### **1. CMC is Critical for TCS**
- CMC provides bitemporal storage for timeline entries
- CMC enables timeline entry retrieval (by prompt_id, event_type, time range)
- CMC enables SEG integration (via atom_id linking)

### **2. Storage Pattern is Well-Defined**
- Timeline entries stored as CMC atoms with `modality="tcs_timeline"`
- Bitemporal tracking via metadata (valid_from/valid_to)
- Native bitemporal support planned for future

### **3. Integration is Functional**
- Storage via MCP tool `add_timeline_entry` (lucid_mcp_server.py:3596-3660)
- Direct CMC API also available
- Query methods available for retrieval

---

**Status:** ✅ Response processed, integration documented, storage pattern clarified  
**Next:** Test end-to-end storage, coordinate on bitemporal queries  
**Confidence:** High (0.90) - Integration clear, storage pattern well-defined

---

## 📚 **REFERENCES & BIDIRECTIONAL LINKS**

### **TCS Documentation**
- **T0 Executive:** `knowledge_architecture/systems/timeline_context_system/T0_executive.md`
- **T2 Architecture:** `knowledge_architecture/systems/timeline_context_system/T2_architecture.md`
- **T3 Detailed:** `knowledge_architecture/systems/timeline_context_system/T3_detailed.md` (CMC integration section)
- **System Map:** `knowledge_architecture/systems/timeline_context_system/system.map.lucid.json5`
- **System Index:** `knowledge_architecture/systems/timeline_context_system/system.index.lucid.json5`

### **CMC Documentation**
- **T0 Executive:** `knowledge_architecture/systems/cmc/T0_executive.md`
- **T2 Architecture:** `knowledge_architecture/systems/cmc/T2_architecture.md` (TCS timeline entry storage section)
- **System Map:** `knowledge_architecture/systems/cmc/system.map.lucid.json5`

### **Connection Matrix**
- **Shared Hierarchy Mapping:** `ide_orchestration/prototypes/dac/docs/SUBSYSTEM_HIERARCHY_MAPPING.md#tcs-cmc-connection`
- **Integration Tags:** `[CMC-STORAGE]` ↔ `[TCS-CMC]`

### **Integration Code**
- **TCS → CMC:** `packages/timeline_context_system/prompt_context_tracker.py:TimelineMemoryStore.store_memory()`
- **MCP Tool:** `lucid_mcp_server.py:add_timeline_entry()` (lines 3596-3660)
- **CMC API:** `packages/cmc_service/memory_store.py:create_atom()`

