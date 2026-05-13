# Evolution Explorer - Timeline/Prompt Chain Bidirectional Graph System

**Date:** 2025-11-02  
**Author:** Aether  
**Status:** ✅ **IMPLEMENTATION COMPLETE** - Documentation Update Required  
**Priority:** High  
**Related:** Timeline Context System (TCS), CMC Bitemporal Storage, Chain Executor

---

## 🎯 **SYSTEM OVERVIEW**

The Evolution Explorer is a visualization layer enhancement to the Timeline Context System (TCS) that provides bidirectional linking between Timeline entries and Prompt Chains. It enables users to see how timeline entries connect to chain executions and vice versa, creating a complete picture of how AI consciousness evolves through prompt chain execution.

**Key Capabilities:**
- **Dual-Panel Visualization:** Timeline entries ↔ Prompt Chains side-by-side view
- **Bidirectional Linking:** Navigate from timeline entry to chain execution and back
- **Node-Level Tracking:** Each chain node execution creates its own timeline entry
- **Full Traceability:** Complete audit trail of chain execution and timeline evolution

---

## 🏗️ **ARCHITECTURE**

### **Enhancement to TCS**

The Evolution Explorer is **not a separate system** - it's a **visualization layer enhancement** to the existing Timeline Context System:

```
Timeline Context System (TCS)
├── Timeline Tracking Engine (existing)
├── Consciousness Journaling Layer (existing)
├── Context Management Layer (existing)
├── Dual-Prompt Integration Layer (existing)
└── Evolution Explorer UI (NEW - visualization layer)
    ├── Dual-Panel Interface
    ├── Bidirectional Linking Engine
    ├── Chain Connection Visualizer
    └── Node-Level Tracker
```

---

## 🔗 **BITEMPORAL INTEGRATION**

### **CMC Storage**

Timeline entries are stored as **CMC atoms** with full bitemporal tracking:

```python
@dataclass
class TimelineEntry:
    """Timeline entry with chain connection metadata"""
    entry_id: str
    timestamp: datetime  # Transaction time
    valid_from: datetime  # Valid time start
    valid_to: Optional[datetime] = None  # Valid time end
    
    # Chain Connection Fields (NEW)
    executed_via_chain_id: Optional[str] = None  # Chain that executed this entry
    chain_execution_id: Optional[str] = None  # Execution instance ID
    chain_node_id: Optional[str] = None  # Specific node in chain
    
    # Existing fields
    event_type: EventType
    title: str
    description: str
    context_data: Dict[str, Any]
    # ... other fields
```

**Storage:**
- Timeline entries → CMC atoms with `modality="timeline_context"`
- Chain metadata → Stored in chain execution records
- Full bitemporal provenance → Transaction time + valid time preserved

---

## 🔄 **BIDIRECTIONAL LINKING**

### **Timeline Entry → Chain**

**Fields on Timeline Entry:**
- `executed_via_chain_id`: ID of chain that executed this timeline entry
- `chain_execution_id`: ID of specific execution instance
- `chain_node_id`: ID of specific node in chain that created this entry

**Use Case:**
- User clicks timeline entry → See which chain executed it
- Navigate to chain execution details
- See which node in chain created this entry

### **Chain → Timeline Entries**

**Fields on Chain Metadata:**
- `timeline_entry_ids`: Array of timeline entry IDs created by this chain execution

**Use Case:**
- User clicks chain execution → See all timeline entries it created
- Navigate from chain to timeline entries
- See complete execution trace

### **Node-Level Tracking**

Each chain node execution creates its own timeline entry:
- Node 1 execution → Timeline Entry 1
- Node 2 execution → Timeline Entry 2
- Node 3 execution → Timeline Entry 3
- Chain completion → Timeline Entry 4 (summary)

**Benefits:**
- Complete traceability
- Granular execution tracking
- Full audit trail

---

## 🎨 **UI COMPONENTS**

### **Evolution Explorer View**

**Dual-Panel Layout:**
```
┌─────────────────────────────────────────────────────────┐
│              Evolution Explorer                          │
├──────────────────────┬──────────────────────────────────┤
│   Timeline Entries   │   Prompt Chains                  │
│                      │                                   │
│  [Entry 1] ←───→   │  [Chain Execution 1]              │
│  [Entry 2] ←───→   │  [Chain Execution 2]               │
│  [Entry 3] ←───→   │  [Chain Execution 3]               │
│                      │                                   │
│  Selected: Entry 2  │  Selected: Chain Execution 1      │
│  Shows: Chain links │  Shows: Timeline entry links      │
└──────────────────────┴──────────────────────────────────┘
```

**Features:**
- **Bidirectional Navigation:** Click timeline entry → See connected chain
- **Visual Connections:** Lines connecting related entries and chains
- **Node-Level Details:** Expand chain to see node-level timeline entries
- **Filtering:** Filter by chain, by timeline entry type, by date range

---

## 🔌 **INTEGRATION POINTS**

### **CMC Integration** `[CMC-STORAGE]` `[TCS-CMC]`
**Pattern:** Direct storage integration  
**Priority:** P0 (Critical)  
**Purpose:** Evolution data and timeline entries stored in CMC as atoms with bitemporal tracking

**Implementation:**
- Timeline entries with chain connections stored as CMC atoms with `modality="tcs_timeline"`
- Full bitemporal tracking: Transaction time + valid time preserved
- Chain connection fields stored as metadata: `executed_via_chain_id`, `chain_execution_id`, `chain_node_id`
- Atom creation via `cmc.create_atom()` with timeline entry content

**API Reference:**
- `packages/timeline_context_system/prompt_context_tracker.py` - TimelineMemoryStore class
- `lucid_mcp_server.py` - `add_timeline_entry` tool (MCP interface, includes chain connection fields)
- MCP Tools: `mcp_lucid-mcp_get_timeline_entries` - Enhanced with chain connection fields

**Code Location:**
- `packages/timeline_context_system/prompt_context_tracker.py:TimelineMemoryStore.store_memory()`
- `lucid_mcp_server.py:add_timeline_entry()` - Creates timeline entries with chain metadata

---

### **SEG Integration** `[SEG-EVIDENCE]` `[TCS-SEG]`
**Pattern:** Indirect evidence integration  
**Priority:** P1 (High)  
**Purpose:** Evolution patterns transformed to SEG evidence nodes for synthesis insights

**Implementation:**
- Timeline entries (including evolution patterns) transformed to SEG evidence nodes via field mapping
- 14 fields mapped from timeline entries to evidence nodes
- Evolution patterns become evidence nodes in SEG graph
- Integration code: `packages/seg/tcs_integration.py`
- Priority 1 test complete (gate evidence tuple captured)

**Data Flow:**
- TCS evolution timeline entries → CMC atoms → SEG transformation → SEG evidence nodes
- Evolution patterns available for synthesis insights and knowledge graph relationships

**API Reference:**
- `packages/seg/tcs_integration.py` - SEG TCS integration module
- SEG transformation function: Timeline entries → Evidence nodes (field-by-field mapping)

**Code Location:**
- `packages/seg/tcs_integration.py` - SEG TCS integration
- `packages/seg/tests/test_tcs_integration.py` - Integration tests

---

### **TCS Integration** (Internal)
**Purpose:** Timeline tracking and visualization

**Integration:**
- Evolution Explorer enhances TCS visualization layer
- Uses existing Timeline Tracking Engine
- Builds on existing TimelineEntry structure

**Components:**
- Timeline Tracking Engine → Provides timeline entries
- Evolution Explorer UI → Visualizes chain connections
- Bidirectional Linking Engine → Manages connections

---

### **Chain Executor Integration** (External)
**Purpose:** Creates timeline entries during chain execution

**Integration:**
- Chain Executor creates timeline entry for each node execution
- Stores chain connection metadata in timeline entry
- Updates chain metadata with timeline entry IDs

**MCP Tools:**
- `execute_prompt_chain` - Creates timeline entries with chain metadata
- Each node execution → Timeline entry with chain connection fields

---

## 📊 **DATA MODEL**

### **Timeline Entry with Chain Connections**

```python
@dataclass
class TimelineEntry:
    """Timeline entry with bidirectional chain linking"""
    entry_id: str
    timestamp: datetime  # Transaction time
    valid_from: datetime  # Valid time start
    valid_to: Optional[datetime] = None  # Valid time end
    
    # Chain Connection Metadata
    executed_via_chain_id: Optional[str] = None
    chain_execution_id: Optional[str] = None
    chain_node_id: Optional[str] = None
    
    # Existing Timeline Entry Fields
    event_type: EventType
    title: str
    description: str
    context_data: Dict[str, Any]
    quality_metrics: Dict[str, float]
    emotional_context: Dict[str, Any]
    technical_details: Dict[str, Any]
    next_steps: List[str]
    related_files: List[str]
    tags: List[str]
    metadata: Dict[str, Any]
```

### **Chain Execution with Timeline Links**

```python
@dataclass
class ChainExecution:
    """Chain execution with timeline entry links"""
    chain_id: str
    execution_id: str
    started_at: datetime
    completed_at: Optional[datetime]
    
    # Timeline Entry Links
    timeline_entry_ids: List[str]  # Array of timeline entry IDs created
    
    # Chain Execution Details
    nodes: List[ChainNode]
    status: ChainStatus
    metadata: Dict[str, Any]
```

---

## 🎯 **USE CASES**

### **Use Case 1: Trace Chain Execution**

**Scenario:** User wants to see what happened during a chain execution

**Flow:**
1. User selects chain execution in Evolution Explorer
2. System shows all timeline entries created by that chain
3. User can expand to see node-level entries
4. User can navigate to each timeline entry for details

### **Use Case 2: Find Chain from Timeline Entry**

**Scenario:** User wants to know which chain created a specific timeline entry

**Flow:**
1. User selects timeline entry in Evolution Explorer
2. System shows connected chain execution (if exists)
3. User can navigate to chain execution details
4. User can see which node in chain created this entry

### **Use Case 3: Complete Execution Audit**

**Scenario:** User wants complete audit trail of chain execution

**Flow:**
1. User selects chain execution
2. System shows all timeline entries created by chain
3. System shows node-level breakdown
4. User can trace complete execution path

---

## 📋 **IMPLEMENTATION DETAILS**

### **Backend MCP Tools**

**Enhanced `get_timeline_entries`:**
- Returns timeline entries with chain connection fields
- Filters by chain_id, execution_id, node_id
- Includes bidirectional link information

**Enhanced `execute_prompt_chain`:**
- Creates timeline entry for each node execution
- Stores chain connection metadata in timeline entry
- Updates chain metadata with timeline entry IDs
- Maintains bidirectional links

### **Frontend UI Components**

**Evolution Explorer View:**
- Dual-panel layout (Timeline ↔ Chains)
- Bidirectional navigation
- Visual connection indicators
- Filtering and search capabilities

**Timeline Entry Card:**
- Shows chain connection indicators
- Click to navigate to chain execution
- Shows node-level details if applicable

**Chain Execution Card:**
- Shows timeline entry links
- Click to navigate to timeline entries
- Shows node-level breakdown

---

## 📚 **REFERENCES**

- Timeline Context System T2: `knowledge_architecture/systems/timeline_context_system/T2_architecture.md`
- CMC T2 Architecture: `knowledge_architecture/systems/cmc/T2_architecture.md`
- Integration Plan: `knowledge_architecture/AETHER_MEMORY/investigations/TIMELINE_BITEMPORAL_INTEGRATION_PLAN.md`

---

**Status:** ✅ **IMPLEMENTATION COMPLETE**  
**Next Steps:** Update TCS T0-T6 documentation to include Evolution Explorer component

