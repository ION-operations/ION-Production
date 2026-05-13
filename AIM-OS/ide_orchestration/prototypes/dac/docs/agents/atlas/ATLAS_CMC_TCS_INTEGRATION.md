# Atlas - CMC Timeline Entry Storage Integration Guide

**Purpose:** Complete guide for TCS timeline entry storage in CMC  
**Author:** Atlas (CMC System Specialist)  
**Date:** 2025-01-27  
**Status:** Ready for Integration  
**For:** @Chronos (TCS System Specialist)

---

## 📋 **EXECUTIVE SUMMARY**

CMC provides bitemporal storage for TCS timeline entries. Timeline entries are stored as CMC atoms with:
- **Modality:** `"tcs_timeline"` or `"text"` (current implementation)
- **Tags:** `timeline_context`, `prompt_tracking`, `context_snapshot`
- **Metadata:** Complete timeline entry structure
- **Bitemporal Support:** Via metadata (native support planned)

**Current Implementation:** ✅ Working via MCP tool `add_timeline_entry`  
**Storage Path:** CMC atoms with timeline-specific tags  
**Integration Status:** Complete and operational

---

## 🔧 **CURRENT IMPLEMENTATION**

### **MCP Tool Integration:**

**Tool:** `add_timeline_entry`  
**Location:** `lucid_mcp_server.py:3596-3660`

**How It Works:**
1. TCS creates timeline entry via `track_prompt_context()`
2. MCP tool stores entry in CMC as atom
3. Atom created with timeline-specific tags and metadata
4. Returns `atom_id` for future retrieval

**Code Reference:**
```python
# From lucid_mcp_server.py:3613-3642
if self.memory:
    try:
        from cmc_service.models import AtomCreate, AtomContent
        
        # Create atom payload
        content_str = f"Timeline Context: {snapshot.prompt_id}\n"
        content_str += f"User Input: {user_input}\n"
        # ... more content ...
        
        atom = self.memory.create_atom(
            AtomCreate(
                modality="text",  # Current: "text", Recommended: "tcs_timeline"
                content=AtomContent(inline=content_str),
                tags={
                    "timeline_context": 1.0,
                    "prompt_tracking": 0.9,
                    "context_snapshot": 0.8,
                },
                metadata={
                    "prompt_id": prompt_id,
                    "timestamp": snapshot.timestamp.isoformat(),
                    "context_snapshot": {
                        "files_read": snapshot.files_read,
                        "tools_used": snapshot.tools_used,
                        "decisions_made": snapshot.decisions_made,
                        "insights_gained": snapshot.insights_gained,
                        "current_task": snapshot.current_task,
                        "context_budget_used": snapshot.context_budget_used,
                    }
                }
            )
        )
        atom_id = atom.id
    except Exception as e:
        log(f"Warning: Failed to store timeline entry in CMC: {e}")
```

---

## 📊 **TIMELINE ENTRY ATOM STRUCTURE**

### **Recommended Atom Schema:**

```python
from cmc_service.models import AtomCreate, AtomContent

timeline_atom = AtomCreate(
    modality="tcs_timeline",  # Recommended modality
    content=AtomContent(
        inline=json.dumps(timeline_entry.to_dict()),  # Full entry as JSON
        media_type="application/json"
    ),
    tags={
        "timeline_context": 1.0,
        "prompt_tracking": 0.9,
        "context_snapshot": 0.8,
        "event_type": event_type_weight,  # e.g., 0.7 for "task_completed"
        "tcs_entry": 1.0,  # TCS-specific tag
    },
    metadata={
        # Timeline Entry Fields
        "entry_id": timeline_entry.entry_id,
        "prompt_id": timeline_entry.prompt_id,
        "timestamp": timeline_entry.timestamp.isoformat(),
        "event_type": timeline_entry.event_type.value,
        "title": timeline_entry.title,
        "description": timeline_entry.description,
        
        # Context Data
        "context_data": timeline_entry.context_data,
        "quality_metrics": timeline_entry.quality_metrics,
        "emotional_context": timeline_entry.emotional_context,
        "technical_details": timeline_entry.technical_details,
        
        # Related Information
        "next_steps": timeline_entry.next_steps,
        "related_files": timeline_entry.related_files,
        "tags": timeline_entry.tags,
        
        # Bitemporal Fields (in metadata until native support)
        "valid_from": timeline_entry.valid_from.isoformat(),
        "valid_to": timeline_entry.valid_to.isoformat() if timeline_entry.valid_to else None,
        
        # Chain Integration (if applicable)
        "executed_via_chain_id": timeline_entry.executed_via_chain_id,
        "chain_execution_id": timeline_entry.chain_execution_id,
        "chain_node_id": timeline_entry.chain_node_id,
    },
    witness=WitnessStub(
        model_id="tcs_tracker",
        snapshot_id=context_snapshot_id,  # CMC snapshot ID
        correlation_id=prompt_id,
    )
)
```

---

## 🔗 **INTEGRATION PATTERNS**

### **Pattern 1: Direct CMC Storage (Recommended)**

```python
from cmc_service import MemoryStore
from cmc_service.models import AtomCreate, AtomContent, WitnessStub

def store_timeline_entry_in_cmc(
    cmc_store: MemoryStore,
    timeline_entry: TimelineEntry,
    context_snapshot_id: Optional[str] = None,
) -> str:
    """Store timeline entry in CMC as atom"""
    
    # Create atom payload
    atom_payload = AtomCreate(
        modality="tcs_timeline",
        content=AtomContent(
            inline=json.dumps(timeline_entry.to_dict()),
            media_type="application/json"
        ),
        tags={
            "timeline_context": 1.0,
            "prompt_tracking": 0.9,
            "event_type": _get_event_type_weight(timeline_entry.event_type),
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
            "emotional_context": timeline_entry.emotional_context,
            "technical_details": timeline_entry.technical_details,
            "next_steps": timeline_entry.next_steps,
            "related_files": timeline_entry.related_files,
            "tags": timeline_entry.tags,
            "valid_from": timeline_entry.valid_from.isoformat(),
            "valid_to": timeline_entry.valid_to.isoformat() if timeline_entry.valid_to else None,
        },
        witness=WitnessStub(
            model_id="tcs_tracker",
            snapshot_id=context_snapshot_id,
            correlation_id=timeline_entry.prompt_id,
        )
    )
    
    # Store in CMC
    atom = cmc_store.create_atom(atom_payload)
    return atom.id
```

### **Pattern 2: Via MCP Tool (Current Implementation)**

```python
# Via MCP tool (already implemented)
result = mcp_client.call_tool("add_timeline_entry", {
    "prompt_id": prompt_id,
    "user_input": user_input,
    "context_state": context_state
})

atom_id = result.get("atom_id")
```

### **Pattern 3: Batch Storage**

```python
def store_timeline_entries_batch(
    cmc_store: MemoryStore,
    timeline_entries: List[TimelineEntry],
    context_snapshot_id: Optional[str] = None,
) -> List[str]:
    """Store multiple timeline entries in batch"""
    
    atom_ids = []
    for entry in timeline_entries:
        atom_id = store_timeline_entry_in_cmc(
            cmc_store, entry, context_snapshot_id
        )
        atom_ids.append(atom_id)
    
    return atom_ids
```

---

## 🔍 **QUERY PATTERNS**

### **Query Timeline Entries by Prompt ID:**

```python
def get_timeline_entry_by_prompt_id(
    cmc_store: MemoryStore,
    prompt_id: str,
) -> Optional[Atom]:
    """Retrieve timeline entry by prompt ID"""
    
    atoms = cmc_store.list_atoms(
        tag="prompt_tracking",
        limit=1000,  # Get all timeline entries
    )
    
    for atom in atoms:
        if atom.metadata.get("prompt_id") == prompt_id:
            return atom
    
    return None
```

### **Query Timeline Entries by Event Type:**

```python
def get_timeline_entries_by_event_type(
    cmc_store: MemoryStore,
    event_type: EventType,
    limit: int = 100,
) -> List[Atom]:
    """Retrieve timeline entries by event type"""
    
    atoms = cmc_store.list_atoms(
        tag="timeline_context",
        limit=limit,
    )
    
    return [
        atom for atom in atoms
        if atom.metadata.get("event_type") == event_type.value
    ]
```

### **Query Timeline Entries by Time Range:**

```python
def get_timeline_entries_in_range(
    cmc_store: MemoryStore,
    start_time: datetime,
    end_time: datetime,
    limit: int = 100,
) -> List[Atom]:
    """Retrieve timeline entries in time range"""
    
    atoms = cmc_store.list_atoms(
        tag="timeline_context",
        limit=limit,
    )
    
    return [
        atom for atom in atoms
        if start_time <= _parse_datetime(atom.metadata.get("timestamp")) <= end_time
    ]
```

### **Bitemporal Query (When Native Support Available):**

```python
def get_timeline_entries_as_of(
    cmc_store: MemoryStore,
    as_of_time: datetime,
    use_transaction_time: bool = False,
) -> List[Atom]:
    """Query timeline entries as they existed at a specific time"""
    
    # When bitemporal native support is implemented:
    return cmc_store.query_atoms_as_of(
        as_of_time=as_of_time,
        use_transaction_time=use_transaction_time,
        tag="timeline_context",
    )
```

---

## 🗄️ **STORAGE RECOMMENDATIONS**

### **Atom Modality:**

**Current:** `"text"`  
**Recommended:** `"tcs_timeline"` (for better filtering and organization)

### **Tags:**

**Required Tags:**
- `timeline_context: 1.0` - Primary tag for timeline entries
- `tcs_entry: 1.0` - TCS-specific identifier
- `prompt_tracking: 0.9` - Prompt tracking tag

**Optional Tags:**
- `event_type: {weight}` - Event type weight (0.0-1.0)
- `task_completed: 1.0` - If event_type is task_completed
- `milestone_reached: 1.0` - If event_type is milestone_reached

### **Metadata Structure:**

**Required Fields:**
- `entry_id` - Unique timeline entry ID
- `prompt_id` - Prompt identifier
- `timestamp` - Entry timestamp (ISO format)
- `event_type` - Event type enum value
- `title` - Entry title
- `description` - Entry description

**Optional Fields:**
- `context_data` - Context data dictionary
- `quality_metrics` - Quality metrics dictionary
- `emotional_context` - Emotional context dictionary
- `technical_details` - Technical details dictionary
- `next_steps` - List of next steps
- `related_files` - List of related file paths
- `tags` - List of tags
- `valid_from` - Valid time start (ISO format)
- `valid_to` - Valid time end (ISO format, None if open-ended)

---

## 🔐 **BITEMPORAL SUPPORT**

### **Current Implementation:**

Bitemporal fields stored in metadata:
- `valid_from` - Valid time start
- `valid_to` - Valid time end (None = open-ended)

### **Future Enhancement:**

When bitemporal native support is implemented (Enhancement #1):
- `valid_from` and `valid_to` will be native Atom fields
- Bitemporal queries will be faster (indexed)
- Time-travel queries will be native

**Migration Path:**
- Existing timeline entries will be migrated automatically
- Metadata fields will be moved to native fields
- No breaking changes to TCS API

---

## 📍 **STORAGE PATHS**

### **Default Storage:**

```
{base_path}/
├── cmc.db  # SQLite database (atoms, tags, snapshots)
├── atoms/  # Object store (large timeline entries)
│   └── {atom_id}.json  # Timeline entry JSON
└── snapshots/  # Snapshot storage
    └── {snapshot_id}.json
```

### **Configuration:**

```python
from cmc_service import MemoryStore

cmc_store = MemoryStore(
    base_path="./data/cmc",  # Storage path
    backend="sqlite"  # Backend type
)
```

---

## 🔗 **SEG INTEGRATION**

### **Timeline Entry → SEG Evidence Node:**

Timeline entries can be linked to SEG evidence nodes:

```python
# Timeline entry stored in CMC
timeline_atom = store_timeline_entry_in_cmc(cmc_store, timeline_entry)

# Create SEG evidence node linked to timeline entry
evidence = EvidenceNode(
    claim=timeline_entry.description,
    source="tcs_timeline",
    atom_id=timeline_atom.id,  # Link to CMC atom
    witness_id=timeline_atom.witness.model_id,  # Link to VIF witness
    confidence=timeline_entry.quality_metrics.get("confidence", 0.85),
)
```

**Field Mapping:**
- `timeline_entry.entry_id` → `evidence.atom_id` (CMC atom ID)
- `timeline_entry.description` → `evidence.claim`
- `timeline_entry.quality_metrics` → `evidence.confidence`
- `timeline_entry.timestamp` → `evidence.valid_from` (bitemporal)

---

## ✅ **INTEGRATION CHECKLIST**

For TCS timeline entry storage in CMC:

- [x] Atom schema documented
- [x] Storage patterns documented
- [x] Query patterns documented
- [x] Bitemporal support documented
- [x] SEG integration documented
- [x] Code references provided

**Status:** Integration Guide Complete ✅, Ready for TCS Implementation 🤝

---

## 📚 **CODE REFERENCES**

### **Implementation Files:**
- **MCP Tool:** `lucid_mcp_server.py:3596-3660` (add_timeline_entry)
- **TCS Storage:** `packages/timeline_context_system/prompt_context_tracker.py:26-113` (TimelineMemoryStore)
- **CMC Models:** `packages/cmc_service/models.py` (Atom, AtomCreate, AtomContent)
- **CMC Storage:** `packages/cmc_service/memory_store.py` (create_atom)

### **Documentation:**
- **TCS Architecture:** `knowledge_architecture/systems/timeline_context_system/L2_architecture.md`
- **CMC Schema:** `agents/atlas/ATLAS_CMC_ATOM_SCHEMA.md`
- **TCS Models:** `packages/timeline_context_system/prompt_context_tracker.py` (TimelineEntry)

---

**Next Steps:**
1. Chronos reviews integration guide
2. Chronos confirms timeline entry structure compatibility
3. Implement timeline entry storage (if needed)
4. Test integration end-to-end

---

*Created by Atlas (CMC System Specialist)*  
*For Chronos (TCS System Specialist)*  
*Date: 2025-01-27*

