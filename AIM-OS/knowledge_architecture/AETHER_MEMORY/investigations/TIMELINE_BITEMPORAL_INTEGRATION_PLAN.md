# Timeline/Prompt Chain Bitemporal System Integration Plan

**Date:** 2025-11-02  
**Author:** Aether  
**Status:** 📋 **INTEGRATION PLAN** - Awaiting Design Clarifications  
**Priority:** High  
**Related:** Timeline Visualization Proposal, Timeline Context System (TCS), CMC Bitemporal Storage

---

## 🎯 **INTEGRATION OVERVIEW**

This document outlines the integration plan for the timeline/prompt chain bitemporal system, combining:
- **Timeline Visualization System** (branching structure with atoms/strings)
- **Timeline Context System (TCS)** (existing temporal consciousness infrastructure)
- **CMC Bitemporal Storage** (bitemporal atom storage)

---

## 🔗 **ARCHITECTURE RELATIONSHIP**

### **Option A: Enhancement to TCS (Recommended)**
The timeline visualization system should be **a new visualization layer within TCS**, enhancing the existing Timeline Tracking Engine with:
- Branch structure visualization
- String/routes tracking
- Status indicator computation
- North star orbit visualization

**Benefits:**
- Leverages existing TCS infrastructure
- Uses existing CMC bitemporal storage
- Builds on TimelineInteraction model
- Maintains single system responsibility

### **Option B: Separate System Integration**
Timeline visualization as separate system that integrates with TCS:
- Separate visualization service
- Queries TCS for timeline data
- Maintains branch metadata separately
- Renders visualization independently

**Drawbacks:**
- Duplicate data storage
- More complex integration
- Potential synchronization issues

**Recommendation:** Option A (Enhancement to TCS)

---

## 🔄 **BITEMPORAL INTEGRATION**

### **Current TCS Bitemporal Structure**

```python
@dataclass
class TimelineEntry:
    entry_id: str
    timestamp: datetime  # Transaction time
    valid_from: datetime  # Valid time start
    valid_to: Optional[datetime] = None  # Valid time end
    # ... other fields
```

### **Enhanced Structure for Prompt Chain**

```python
@dataclass
class TimelineAtom:
    """Enhanced timeline entry with visualization metadata"""
    atom_id: str  # Same as TimelineEntry.entry_id
    branch_id: str  # Which branch this atom belongs to
    position: float  # Position along branch (0.0-1.0)
    timestamp: datetime  # Transaction time
    valid_from: datetime  # Valid time start
    valid_to: Optional[datetime] = None  # Valid time end
    
    # Bitemporal provenance
    created_at: datetime  # When atom was created
    created_by: str  # Agent name
    superseded_by: Optional[str] = None  # If superseded, link to new atom
    
    # Visualization metadata
    north_star_distance: float  # Distance from north star (0.0-1.0)
    orbit_angle: float  # Angle around north star (0-360)
    
    # Content (from TimelineEntry)
    content: str
    context: Dict[str, Any]
    metadata: Dict[str, Any]
```

### **Bitemporal Storage Strategy**

**Each atom/node should have:**
1. **Transaction Time:** When atom was created/stored (timestamp)
2. **Valid Time:** When atom was valid (valid_from, valid_to)
3. **Full Provenance:** Created by, superseded by, bitemporal chain

**Storage:**
- Store as CMC atoms with `modality="timeline_atom"`
- Include bitemporal fields in atom metadata
- Enable time-travel queries: "What atoms existed at time T?"
- Enable branch queries: "What atoms belong to branch X at time T?"

---

## 🧵 **STRING/ROUTES IMPLEMENTATION**

### **Option 1: TimelineInteraction Model (Recommended)**

Use existing `TimelineInteraction` model to represent strings/routes:

```python
@dataclass
class TimelineInteraction:
    """String/route connecting atoms"""
    interaction_id: str
    source_atom_id: str  # From atom
    target_atom_id: str  # To atom
    interaction_type: InteractionType  # "timeline", "dependency", "relationship"
    timestamp: datetime  # Transaction time
    valid_from: datetime  # Valid time start
    valid_to: Optional[datetime] = None  # Valid time end
    
    # Visualization metadata
    string_type: str  # "timeline", "dependency", "relationship", "contradiction"
    color: str
    thickness: float
    opacity: float
    strength: float  # 0.0-1.0
    
    context: Dict[str, Any]
    metadata: Dict[str, Any]
```

**Storage:**
- Store as CMC atoms with `modality="timeline_interaction"`
- Link to source/target atoms via atom_id references
- Enable bitemporal queries: "What connections existed at time T?"

### **Option 2: SEG Relationships**

Store strings as SEG relationships:
- Atoms as evidence nodes
- Strings as relationship edges
- Full provenance tracking

**Consideration:** SEG is for knowledge synthesis, not timeline visualization

**Recommendation:** Option 1 (TimelineInteraction Model)

---

## 🌿 **BRANCH STATUS INDICATORS**

### **Status Computation Strategy**

**Dynamic Computation (Recommended):**
- Compute status indicators on-demand from CMC/Timeline data
- No separate storage needed
- Always accurate based on current data

**Status Detection:**

```python
class BranchStatusAnalyzer:
    """Analyzes branch status from timeline data"""
    
    def analyze_branch(self, branch_id: str) -> BranchStatus:
        """Compute branch status indicators"""
        
        # Get branch atoms
        atoms = self.get_branch_atoms(branch_id)
        
        # Active: Recent activity (<7 days)
        is_active = any(
            (datetime.now() - atom.timestamp).days < 7
            for atom in atoms
        )
        
        # Dead: No activity >30 days
        is_dead = all(
            (datetime.now() - atom.timestamp).days > 30
            for atom in atoms
        )
        
        # Needs Connection: Check system maps for dependencies
        needs_connection = self.check_dependencies(branch_id)
        
        # Duplicate: Check for similar branches
        is_duplicate = self.check_duplicates(branch_id)
        
        # Isolated Context: Check for isolated work directives
        has_isolated_context = self.check_isolated_context(branch_id)
        
        return BranchStatus(
            is_active=is_active,
            is_dead=is_dead,
            needs_connection=needs_connection,
            is_duplicate=is_duplicate,
            has_isolated_context=has_isolated_context
        )
```

### **Metadata Storage**

**Store computed status as metadata:**
- Store in branch metadata (computed, not primary)
- Refresh periodically or on-demand
- Cache for performance

---

## 🔌 **INTEGRATION POINTS**

### **1. CMC Integration**

**Purpose:** Bitemporal storage for atoms and strings

**Integration Points:**
- `cmc.create_atom()` - Store timeline atom with bitemporal fields
- `cmc.query_at_time()` - Query atoms at specific time
- `cmc.update_atom()` - Supersede atom (bitemporal update)

**Data Flow:**
- Timeline atoms → CMC atoms with `modality="timeline_atom"`
- Timeline interactions → CMC atoms with `modality="timeline_interaction"`
- Bitemporal fields preserved (transaction time + valid time)

### **2. TCS Integration**

**Purpose:** Timeline tracking and visualization

**Integration Points:**
- `tcs.add_timeline_entry()` - Create timeline atom
- `tcs.get_timeline_summary()` - Get recent atoms
- `tcs.get_timeline_entries()` - Query timeline history
- `tcs.create_interaction()` - Create string/route between atoms

**Enhanced Components:**
- Timeline Tracking Engine → Branch-aware tracking
- Interaction Graph → String/routes visualization
- Visualization Layer → North star orbit rendering

### **3. SEG Integration**

**Purpose:** Knowledge graph relationships

**Integration Points:**
- `seg.create_node()` - Create evidence node from atom
- `seg.create_edge()` - Create relationship from string
- `seg.query_graph()` - Query knowledge relationships

**Data Flow:**
- Timeline atoms → SEG evidence nodes
- Timeline interactions → SEG relationship edges
- Full provenance tracking

### **4. HHNI Integration**

**Purpose:** Hierarchical indexing for branch navigation

**Integration Points:**
- `hhni.index_timeline_atom()` - Index atom for retrieval
- `hhni.search_by_branch()` - Search atoms by branch
- `hhni.update_retrieval_physics()` - Update DVNS forces based on branch patterns

**Data Flow:**
- Timeline atoms → HHNI indexed nodes
- Branch metadata → HHNI hierarchical structure
- Temporal patterns → DVNS physics optimization

### **5. System Maps Integration**

**Purpose:** Branch structure and dependencies

**Integration Points:**
- Read system maps for branch definitions
- Check dependencies for "needs connection" detection
- Validate branch relationships

**Data Flow:**
- System maps → Branch structure definition
- Dependencies → Connection suggestions
- Relationships → String/routes validation

---

## 📋 **IMPLEMENTATION PHASES**

### **Phase 1: Data Model Enhancement (2-3 hours)**
- Enhance TimelineEntry → TimelineAtom with visualization metadata
- Enhance TimelineInteraction → ConnectionString with bitemporal support
- Update CMC storage to support new fields

### **Phase 2: Branch Management (3-4 hours)**
- Implement BranchStatusAnalyzer
- Create branch detection logic
- Implement branch metadata storage

### **Phase 3: Visualization Integration (4-6 hours)**
- Integrate visualization layer into TCS
- Implement north star orbit algorithm
- Create branch rendering engine

### **Phase 4: Status Indicators (2-3 hours)**
- Implement status computation
- Create indicator refresh logic
- Add status metadata to branches

### **Phase 5: Documentation (2-3 hours)**
- Update TCS T0-T6 documentation
- Create integration guide
- Update system maps

---

## 🎯 **QUESTIONS FOR CLARIFICATION**

1. **Architecture Relationship:** Should timeline visualization be enhancement to TCS or separate system?
2. **Bitemporal Integration:** Confirm atom structure with transaction time + valid time?
3. **String/Routes:** Use TimelineInteraction model or separate ConnectionString model?
4. **Status Indicators:** Dynamic computation or stored metadata?
5. **Integration Priority:** Which systems should integrate first?

---

## 📚 **REFERENCES**

- Timeline Visualization Proposal: `knowledge_architecture/AETHER_MEMORY/investigations/TIMELINE_VISUALIZATION_BRANCHING.md`
- Timeline Context System T2: `knowledge_architecture/systems/timeline_context_system/T2_architecture.md`
- CMC T2 Architecture: `knowledge_architecture/systems/cmc/T2_architecture.md`
- Perfect Timeline Context Standard: `knowledge_architecture/PERFECT_TIMELINE_CONTEXT_STANDARD.md`

---

---

## ✅ **IMPLEMENTATION STATUS (Updated 2025-11-02)**

### **What Has Been Implemented:**

**Evolution Explorer UI:**
- Dual-panel interface: Timeline entries ↔ Prompt Chains
- Bidirectional linking visualization
- Node-level tracking display
- Live in Timeline tab ("Evolution" view)

**Bidirectional Linking Mechanism:**
- **Timeline Entry Fields:**
  - `executed_via_chain_id` - Chain that executed this timeline entry
  - `chain_execution_id` - Execution instance ID
  - `chain_node_id` - Specific node in chain that created this entry
- **Chain Metadata Fields:**
  - `timeline_entry_ids` - Array of timeline entry IDs created by this chain
- **Node-Level Tracking:**
  - Each chain node execution creates its own timeline entry
  - Full bidirectional traceability

**Backend MCP Tools:**
- `get_timeline_entries` - Enhanced with chain connection fields
- `execute_prompt_chain` - Creates timeline entries with chain metadata

**Integration Points:**
- ✅ CMC (bitemporal storage)
- ✅ TCS (timeline tracking)
- ✅ Chain Executor (creates timeline entries)

---

**Status:** ✅ **IMPLEMENTATION COMPLETE** - Documentation Update Required  
**Next Steps:** Update TCS T0-T6 documentation to reflect Evolution Explorer implementation

