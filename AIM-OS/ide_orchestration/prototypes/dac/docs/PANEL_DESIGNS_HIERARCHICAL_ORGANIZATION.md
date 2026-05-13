# Panel Designs for Hierarchical Organization Visualization

**Created:** 2025-01-27  
**Agent:** Sev  
**Purpose:** Design panels to visualize AIM-OS hierarchical organization (System Maps, Indexes, T0-T4 docs, SUPER_INDEX, GOAL_TREE)  
**Status:** Design Phase

---

## 🎯 **EXECUTIVE SUMMARY**

This document designs panels for DAC v2 IDE that visualize the hierarchical organization and mapping of AIM-OS. The panels will display:
- **System Maps** - Internal topology and external connections
- **System Indexes** - System intent, architecture, integrations, status
- **T0-T4 Documentation** - Progressive disclosure documentation levels
- **SUPER_INDEX** - Alphabetical concept map
- **GOAL_TREE** - Hierarchical goal structure (North Star → Objectives → Key Results)

**Design Principles:**
- **Tree/Graph Hybrid Views** - Both tree (hierarchical) and graph (force-directed Obsidian-style) visualizations
- **Independent Panels** - Each panel is data-driven, no cross-panel communication
- **Backend Data Focus** - All panels relate directly to backend data (system maps, indexes, docs, goals)
- **Obsidian-Style Graphs** - Force-directed graphs using `react-force-graph-2d` (like TopicGraphView)
- **Progressive Disclosure** - Overview → details → deep dive
- **Real-Time Updates** - Live status from backend data
- **Deep AIM-OS Integration** - CMC, HHNI, VIF, SEG, TCS for data retrieval

---

## 🏗️ **PANEL DESIGNS**

### **1. System Atlas Panel** ⭐ NEW

**Purpose:** Obsidian-style force-directed graph showing all system maps stitched together

**Location:** Main Content Area (full-screen mode) or Right Drawer (collapsed view)

**Features:**
- **Obsidian-Style Graph** - Force-directed graph using `react-force-graph-2d` (like TopicGraphView)
- **Tree/Graph Toggle** - Switch between hierarchical tree view and force-directed graph view
- **Multi-Layer Views** - Security, performance, governance, timeline layers (filter nodes/edges)
- **Real-Time Activity** - Live activity visualization across edges (from TCS)
- **System Details** - Click system node to show details in side panel (no cross-panel communication)
- **Connection Visualization** - See how systems connect via ports (edges between nodes)

**Visual Design:**
```
┌─────────────────────────────────────────────────────────┐
│ [Tree] [Graph] | [Layer: All] [Security] [Performance] │
│ ┌───────────────────────────────────────────────────┐   │
│ │                                                   │   │
│ │    ⚙️ CMC ────┐                                    │   │
│ │      │        │                                    │   │
│ │      │    🧠 HHNI ──── 🔍 VIF                      │   │
│ │      │        │         │                          │   │
│ │      └─── 🕸️ SEG ───────┘                          │   │
│ │            │                                       │   │
│ │         📊 APOE                                    │   │
│ │                                                   │   │
│ │  (Force-directed graph | Drag nodes | Click: Details)│
│ └───────────────────────────────────────────────────┘   │
│ Selected: CMC | Layer: All | Activity: Live             │
└─────────────────────────────────────────────────────────┘
```

**Tree View:** Hierarchical tree with expandable nodes (like file explorer)
**Graph View:** Force-directed graph with nodes and edges (Obsidian-style)

**Data Sources:**
- Load all `system.map.lucid.json5` files
- Parse internal nodes and ports
- Build connection graph
- Real-time activity from TCS

**AIM-OS Integration:**
- **CMC:** Store atlas state, zoom level, selected system
- **HHNI:** Semantic search for systems
- **VIF:** Confidence scores for system health
- **SEG:** System relationships and dependencies
- **TCS:** Real-time activity tracking

**Implementation:**
- **Graph View:** `react-force-graph-2d` (Obsidian-style, like TopicGraphView)
  - Force-directed layout with physics simulation
  - Node icons/colors based on system type
  - Edge colors based on connection type
  - Click node to show details in side panel
- **Tree View:** Custom tree component with expandable nodes
  - Hierarchical structure (Layer → System → Component)
  - Expandable/collapsible nodes
  - Click node to show details in side panel
- **Toggle:** Switch between tree/graph views with button/checkbox
- **Layer Filters:** Filter nodes/edges by layer type (filters backend data)
- **System Detail Panel:** Side panel within this component (no cross-panel communication)

---

### **2. System Map Explorer Panel** ⭐ NEW

**Purpose:** Deep dive into individual system maps with internal topology and external connections

**Location:** Right Drawer or Main Content (independent panel, no cross-panel communication)

**Features:**
- **Tree/Graph Toggle** - Switch between hierarchical tree and force-directed graph
- **Internal Topology View** - Show all internal nodes (components) as graph nodes
- **External Connections View** - Show all ports and connections to other systems as edges
- **Component Details** - Click component node to show details in side panel (within this component)
- **Port Details** - Click port edge to see what's exchanged, protocol, security level
- **Visual Metaphor** - "Chip layout with pads around edges" (graph view) or tree structure (tree view)
- **System Selection** - Select system from dropdown/search (data-driven, no cross-panel communication)

**Visual Design:**
```
┌─────────────────────────────────────────────────────────┐
│ System: CMC (Context Memory Core)                       │
│ [Internal] [External] [Both]                            │
│ ┌───────────────────────────────────────────────────┐   │
│ │                                                   │   │
│ │  ┌─────────┐  ┌─────────┐  ┌─────────┐          │   │
│ │  │ Atom    │──│ Write   │──│ Storage │          │   │
│ │  │ Manager │  │ Pipeline│  │ Manager │          │   │
│ │  └─────────┘  └─────────┘  └─────────┘          │   │
│ │      │            │              │              │   │
│ │      └────────────┴──────────────┘              │   │
│ │                                                   │   │
│ │  Ports (External Connections):                   │   │
│ │  ┌──────────────┐  ┌──────────────┐             │   │
│ │  │ HHNI         │  │ VIF          │             │   │
│ │  │ Integration  │  │ Integration  │             │   │
│ │  └──────────────┘  └──────────────┘             │   │
│ │                                                   │   │
│ └───────────────────────────────────────────────────┘   │
│ Selected: atomManager | Status: production             │
└─────────────────────────────────────────────────────────┘
```

**Data Sources:**
- Load `system.map.lucid.json5` for selected system
- Parse internal nodes, ports, edges
- Load related system maps for external connections

**AIM-OS Integration:**
- **CMC:** Store selected system, view mode, zoom level
- **HHNI:** Search for related systems
- **VIF:** Component health and confidence scores
- **SEG:** Component relationships and dependencies

**Implementation:**
- **Graph View:** `react-force-graph-2d` (Obsidian-style force-directed graph)
- **Tree View:** Custom tree component with expandable nodes
- **Toggle:** Switch between tree/graph views
- **View Modes:** Internal/External/Both (filter nodes/edges)
- **Component Detail Panel:** Side panel within this component (no cross-panel communication)
- **System Selector:** Dropdown/search to select system (loads from backend data)

---

### **3. System Index Browser Panel** ⭐ NEW

**Purpose:** Browse all system indexes with intent, architecture, integrations, and status

**Location:** Left Drawer or Right Drawer (independent panel)

**Features:**
- **Tree/Graph Toggle** - Switch between hierarchical tree and force-directed graph
- **System List (Tree View)** - All systems with status indicators, expandable nodes
- **System Graph (Graph View)** - Force-directed graph showing system relationships
- **Intent View** - Purpose, must_not_regress, why_it_exists
- **Architecture View** - Components, relationships, data flow
- **Integration View** - With other systems, protocols, APIs
- **Status View** - Completion, health, dependencies
- **Filter/Search** - By layer, status, name, tags (filters backend data)

**Visual Design:**
```
┌─────────────────────────────────────────────────────────┐
│ System Index Browser                                    │
│ [All] [Layer 1] [Layer 2] [Layer 3] [Layer 4]         │
│ Search: [____________]                                  │
│ ┌───────────────────────────────────────────────────┐   │
│ │ ✅ CMC (Context Memory Core) - Layer 1            │   │
│ │    Status: production | Completion: 70%           │   │
│ │    Purpose: Bitemporal memory substrate            │   │
│ │                                                    │   │
│ │ ✅ HHNI (Hierarchical Index) - Layer 2            │   │
│ │    Status: production | Completion: 100%          │   │
│ │    Purpose: Physics-guided retrieval              │   │
│ │                                                    │   │
│ │ ⚠️ SEG (Shared Evidence Graph) - Layer 1           │   │
│ │    Status: development | Completion: 10%          │   │
│ │    Purpose: Knowledge synthesis                    │   │
│ └───────────────────────────────────────────────────┘   │
│ Selected: CMC | View: Intent | Details: [Expand]        │
└─────────────────────────────────────────────────────────┘
```

**Data Sources:**
- Load all `system.index.lucid.json5` files
- Parse intent, architecture, integrations, status
- Filter by layer, status, tags

**AIM-OS Integration:**
- **CMC:** Store selected system, view mode, filters
- **HHNI:** Search systems by purpose, components
- **VIF:** System health and confidence scores
- **SEG:** System relationships and dependencies

**Implementation:**
- **Tree View:** Custom tree component with expandable nodes
- **Graph View:** `react-force-graph-2d` (Obsidian-style force-directed graph)
- **Toggle:** Switch between tree/graph views
- **Tab-based View Switching:** Intent/Architecture/Integration/Status
- **Filter Sidebar:** Filter by layer, status, name, tags (filters backend data)
- **Search:** Search with highlighting (searches backend data)

---

### **4. Documentation Navigator Panel** ⭐ NEW

**Purpose:** Navigate T0-T4 documentation levels with progressive disclosure

**Location:** Right Drawer or Main Content (independent panel)

**Features:**
- **Tree/Graph Toggle** - Switch between hierarchical tree and force-directed graph
- **System Tree (Tree View)** - All systems with documentation levels, expandable nodes
- **Documentation Graph (Graph View)** - Force-directed graph showing documentation relationships
- **Level Indicators** - T0/T1/T2/T3/T4 completion status
- **Progressive Disclosure** - Click to expand from T0 → T4
- **Quick Preview** - Hover to see T0 summary
- **Confidence-Based Routing** - Suggest level based on confidence (from VIF)
- **Cross-References** - Links to related systems and concepts (from backend data)

**Visual Design:**
```
┌─────────────────────────────────────────────────────────┐
│ Documentation Navigator                                 │
│ [All Systems] [By Layer] [By Status]                    │
│ ┌───────────────────────────────────────────────────┐   │
│ │ 📁 CMC (Context Memory Core)                     │   │
│ │    ✅ T0 ✅ T1 ✅ T2 ✅ T3 ✅ T4                  │   │
│ │    ├─ T0_executive.md (100 words)                 │   │
│ │    ├─ T1_overview.md (500 words)                 │   │
│ │    ├─ T2_architecture.md (2,000 words)            │   │
│ │    ├─ T3_detailed.md (10,000 words)              │   │
│ │    └─ T4_complete.md (15,000+ words)             │   │
│ │                                                    │   │
│ │ 📁 HHNI (Hierarchical Index)                      │   │
│ │    ✅ T0 ✅ T1 ✅ T2 ✅ T3 ✅ T4                  │   │
│ │                                                    │   │
│ │ 📁 SEG (Shared Evidence Graph)                    │   │
│ │    ✅ T0 ✅ T1 ⚠️ T2 ⚠️ T3 ⚠️ T4                 │   │
│ └───────────────────────────────────────────────────┘   │
│ Selected: CMC/T2 | Confidence: 0.75 → T2 recommended   │
└─────────────────────────────────────────────────────────┘
```

**Data Sources:**
- Scan `knowledge_architecture/systems/{system}/` for T0-T4 files
- Parse frontmatter metadata
- Calculate word counts
- Track completion status

**AIM-OS Integration:**
- **CMC:** Store selected system, level, reading position
- **HHNI:** Search documentation by content
- **VIF:** Documentation quality and confidence scores
- **SEG:** Documentation relationships and cross-references

**Implementation:**
- **Tree View:** Custom tree component with expandable folders
- **Graph View:** `react-force-graph-2d` (Obsidian-style force-directed graph)
- **Toggle:** Switch between tree/graph views
- **Level Indicators:** ✅/⚠️/❌ (from backend data)
- **Quick Preview:** Hover to see T0 summary (from backend data)
- **Confidence-Based Routing:** Suggestions from VIF (backend data)

---

### **5. SUPER_INDEX Explorer Panel** ⭐ NEW

**Purpose:** Interactive exploration of the alphabetical concept map

**Location:** Left Drawer or Right Drawer (independent panel)

**Features:**
- **Tree/Graph Toggle** - Switch between alphabetical tree and force-directed graph
- **Alphabetical Tree (Tree View)** - A-Z navigation with expandable concept nodes
- **Concept Graph (Graph View)** - Force-directed graph showing concept relationships
- **Concept Cards** - What, Where, Code, Related (from backend data)
- **Search/Filter** - By concept, system, type (filters backend data)
- **Cross-References** - Links to related concepts (from backend data, no cross-panel navigation)
- **Confidence-Based Routing** - Suggest documentation level (from VIF backend data)
- **Live Updates** - New concepts appear automatically (from backend data)

**Visual Design:**
```
┌─────────────────────────────────────────────────────────┐
│ SUPER_INDEX Explorer                                    │
│ [A] [B] [C] ... [Z] | Search: [____________]            │
│ ┌───────────────────────────────────────────────────┐   │
│ │ A                                                 │   │
│ │ ┌─────────────────────────────────────────────┐ │   │
│ │ │ Abstention (Behavioral)                     │ │   │
│ │ │ What: AI refuses to answer when confidence  │ │   │
│ │ │       too low                                │ │   │
│ │ │ Where: systems/vif/L3_detailed.md           │ │   │
│ │ │ Code: packages/seg/kappa_gate.py            │ │   │
│ │ │ Related: κ-gating, HITL, confidence        │ │   │
│ │ │ [View T2] [View T3] [View Code]            │ │   │
│ │ └─────────────────────────────────────────────┘ │   │
│ │                                                    │   │
│ │ ┌─────────────────────────────────────────────┐ │   │
│ │ │ APOE (AI-Powered Orchestration Engine)      │ │   │
│ │ │ What: Compiles reasoning into executable    │ │   │
│ │ │       plans (DAGs) with roles, budgets      │ │   │
│ │ │ Where: systems/apoe/README.md               │ │   │
│ │ │ Code: packages/apoe_runner/                 │ │   │
│ │ │ Related: 8 roles, ACL, DAG execution       │ │   │
│ │ │ [View T2] [View T3] [View Code]            │ │   │
│ │ └─────────────────────────────────────────────┘ │   │
│ └───────────────────────────────────────────────────┘   │
│ Selected: APOE | Confidence: 0.80 → T2 recommended    │
└─────────────────────────────────────────────────────────┘
```

**Data Sources:**
- Load `knowledge_architecture/SUPER_INDEX.md`
- Parse concept entries (What/Where/Code/Related)
- Extract links and references
- Track concept updates

**AIM-OS Integration:**
- **CMC:** Store selected concept, reading position
- **HHNI:** Semantic search for concepts
- **VIF:** Concept confidence and quality scores
- **SEG:** Concept relationships and dependencies

**Implementation:**
- **Tree View:** Custom tree component with alphabetical navigation (A-Z)
- **Graph View:** `react-force-graph-2d` (Obsidian-style force-directed graph)
- **Toggle:** Switch between tree/graph views
- **Concept Cards:** Expandable details (from backend data)
- **Search:** Search with highlighting (searches backend data)
- **Quick Navigation:** Links to documentation (from backend data, no cross-panel navigation)

---

### **6. GOAL_TREE Navigator Panel** ⭐ NEW

**Purpose:** Visualize hierarchical goal structure (North Star → Objectives → Key Results)

**Location:** Left Drawer or Right Drawer (independent panel)

**Features:**
- **Tree/Graph Toggle** - Switch between hierarchical tree and force-directed graph
- **Hierarchical Tree (Tree View)** - North Star → Objectives → Key Results, expandable nodes
- **Goal Graph (Graph View)** - Force-directed graph showing goal relationships and dependencies
- **Progress Indicators** - Completion percentage, status (from backend data)
- **Priority Tiers** - Color-coded by tier (S/A/B) (from backend data)
- **Timeline View** - Target dates and milestones (from backend data)
- **Filter/Search** - By tier, status, owner, date (filters backend data)
- **Interactive Navigation** - Click to expand/collapse (tree view) or drag nodes (graph view)

**Visual Design:**
```
┌─────────────────────────────────────────────────────────┐
│ GOAL_TREE Navigator                                     │
│ [All] [Tier S] [Tier A] [Tier B] | Search: [____]      │
│ ┌───────────────────────────────────────────────────┐   │
│ │ 🎯 North Star                                     │   │
│ │ Ship AIM-OS v0.3 by 2025-11-30                   │   │
│ │                                                    │   │
│ │ ├─ 🔴 OBJ-01: Reliable Memory Storage (CMC)       │   │
│ │ │   Tier: S - SHIP-CRITICAL                       │   │
│ │ │   Status: in_progress (70%)                     │   │
│ │ │   Target: 2025-11-13                           │   │
│ │ │   ├─ KR-1.1: Snapshot determinism (100%)        │   │
│ │ │   ├─ KR-1.2: Write-error rate (<0.1%)          │   │
│ │ │   └─ KR-1.3: Journal corruption (0 incidents)   │   │
│ │ │                                                    │   │
│ │ ├─ 🟢 OBJ-02: Hierarchical Indexing (HHNI)        │   │
│ │ │   Tier: S - SHIP-CRITICAL                       │   │
│ │ │   Status: completed (100%)                      │   │
│ │ │   Target: 2025-11-15                            │   │
│ │ │                                                    │   │
│ │ ├─ 🔴 OBJ-07: MCP Tools Real Integrations          │   │
│ │ │   Tier: S - SHIP-CRITICAL                       │   │
│ │ │   Status: in_progress (5%)                      │   │
│ │ │   Target: 2025-11-20                            │   │
│ └───────────────────────────────────────────────────┘   │
│ Selected: OBJ-01 | Progress: 70% | Days Remaining: 17  │
└─────────────────────────────────────────────────────────┘
```

**Data Sources:**
- Load `goals/GOAL_TREE.yaml`
- Parse north_star, objectives, key_results
- Calculate progress and status
- Track target dates

**AIM-OS Integration:**
- **CMC:** Store selected goal, view mode, filters
- **HHNI:** Search goals by name, description
- **VIF:** Goal confidence and quality scores
- **TCS:** Goal timeline and progress tracking
- **APOE:** Goal execution plans and status

**Implementation:**
- **Tree View:** Custom tree component with expandable nodes
- **Graph View:** `react-force-graph-2d` (Obsidian-style force-directed graph)
- **Toggle:** Switch between tree/graph views
- **Progress Bars:** Status indicators (from backend data)
- **Color-Coded Tiers:** Priority visualization (from backend data)
- **Timeline Visualization:** Target dates and milestones (from backend data)
- **Filter Sidebar:** Filter by tier, status, owner, date (filters backend data)

---

### **7. System Hierarchy Panel** ⭐ NEW

**Purpose:** Visualize 6-layer system hierarchy with dependencies

**Location:** Left Drawer or Right Drawer (independent panel)

**Features:**
- **Tree/Graph Toggle** - Switch between hierarchical tree and force-directed graph
- **Layer Tree (Tree View)** - 6 layers with systems, expandable nodes
- **Hierarchy Graph (Graph View)** - Force-directed graph showing layer relationships and dependencies
- **Status Indicators** - Completion, health, status (from backend data)
- **Layer Navigation** - Click layer to filter systems (filters backend data)
- **System Details** - Click system to show details in side panel (within this component)

**Visual Design:**
```
┌─────────────────────────────────────────────────────────┐
│ System Hierarchy                                        │
│ [All Layers] [Layer 1] [Layer 2] ... [Layer 6]         │
│ ┌───────────────────────────────────────────────────┐   │
│ │ Layer 1: Memory & Knowledge Foundation             │   │
│ │ ┌─────────┐  ┌─────────┐                          │   │
│ │ │ CMC     │  │ SEG     │                          │   │
│ │ │ 70%     │  │ 10%     │                          │   │
│ │ └─────────┘  └─────────┘                          │   │
│ │                                                    │   │
│ │ Layer 2: Intelligence Processing                   │   │
│ │ ┌─────────┐  ┌─────────┐  ┌─────────┐            │   │
│ │ │ HHNI    │  │ VIF     │  │ SDF-CVF │            │   │
│ │ │ 100%    │  │ 95%     │  │ 95%     │            │   │
│ │ └─────────┘  └─────────┘  └─────────┘            │   │
│ │      │            │              │                │   │
│ │      └────────────┴──────────────┘                │   │
│ │                                                    │   │
│ │ Layer 3: Orchestration & Planning                 │   │
│ │ ┌─────────┐                                       │   │
│ │ │ APOE    │                                       │   │
│ │ │ 90%     │                                       │   │
│ │ └─────────┘                                       │   │
│ └───────────────────────────────────────────────────┘   │
│ Selected: HHNI | Layer: 2 | Dependencies: CMC, SEG     │
└─────────────────────────────────────────────────────────┘
```

**Data Sources:**
- Load `knowledge_architecture/SYSTEM_HIERARCHY.md`
- Parse layer structure and dependencies
- Load system status from indexes

**AIM-OS Integration:**
- **CMC:** Store selected layer, system, view mode
- **HHNI:** Search systems by layer, dependencies
- **VIF:** Layer health and confidence scores
- **SEG:** Layer relationships and dependencies

**Implementation:**
- **Tree View:** Custom tree component with layer-based hierarchy
- **Graph View:** `react-force-graph-2d` (Obsidian-style force-directed graph)
- **Toggle:** Switch between tree/graph views
- **Status Indicators:** Completion, health, status (from backend data)
- **Layer Filter Buttons:** Filter by layer (filters backend data)
- **System Detail Panel:** Side panel within this component (no cross-panel communication)

---

## 🎨 **UNIFIED PANEL ARCHITECTURE**

### **Common Features Across All Panels**

**1. Tree/Graph Hybrid Views:**
- **Tree View:** Hierarchical tree with expandable nodes (like file explorer)
- **Graph View:** Force-directed graph using `react-force-graph-2d` (Obsidian-style, like TopicGraphView)
- **Toggle:** Switch between tree/graph views with button/checkbox

**2. Independent & Data-Driven:**
- **No Cross-Panel Communication:** Each panel is independent, no clicking in one panel opens things in another
- **Backend Data Focus:** All panels relate directly to backend data (system maps, indexes, docs, goals)
- **Data Loading:** Load data from backend (CMC, HHNI, VIF, SEG, TCS) independently

**3. Progressive Disclosure:**
- Overview → Details → Deep Dive
- Expandable sections (tree view)
- Tab-based navigation

**4. Interactive Navigation:**
- Click to explore (within panel)
- Breadcrumb navigation (within panel)
- Back/forward buttons (within panel)

**5. Real-Time Updates:**
- Live status indicators (from backend data)
- Activity visualization (from TCS backend data)
- Progress tracking (from backend data)

**6. Search & Filter:**
- Context-specific search (searches backend data)
- Context-specific filters (filters backend data)
- Quick navigation (within panel)

**7. AIM-OS Integration:**
- **CMC:** State persistence (panel state, not cross-panel)
- **HHNI:** Semantic search (backend data retrieval)
- **VIF:** Confidence scores (backend data)
- **SEG:** Relationships (backend data)
- **TCS:** Timeline tracking (backend data)

---

## 🔧 **IMPLEMENTATION PRIORITIES**

### **Phase 1: Core Panels (Week 1-2)**

1. **System Index Browser Panel** - Foundation for all other panels
2. **GOAL_TREE Navigator Panel** - Critical for understanding priorities
3. **Documentation Navigator Panel** - Essential for navigation

**Deliverables:**
- ✅ System Index Browser operational
- ✅ GOAL_TREE Navigator operational
- ✅ Documentation Navigator operational

---

### **Phase 2: Visualization Panels (Week 3-4)**

1. **System Atlas Panel** - Google Maps-like interface
2. **System Map Explorer Panel** - Deep dive into system maps
3. **System Hierarchy Panel** - Layer visualization

**Deliverables:**
- ✅ System Atlas operational
- ✅ System Map Explorer operational
- ✅ System Hierarchy operational

---

### **Phase 3: Advanced Panels (Week 5-6)**

1. **SUPER_INDEX Explorer Panel** - Concept map exploration
2. **Enhanced Integration** - Deep AIM-OS integration
3. **Performance Optimization** - Lazy loading, memoization

**Deliverables:**
- ✅ SUPER_INDEX Explorer operational
- ✅ Deep AIM-OS integration complete
- ✅ Performance optimized

---

## 🔧 **TECHNICAL IMPLEMENTATION**

### **Graph View Implementation (Obsidian-Style)**

**Library:** `react-force-graph-2d` (same as TopicGraphView)

**Example Implementation:**
```typescript
import ForceGraph2D from 'react-force-graph-2d'
import { useRef, useMemo, useState } from 'react'

interface SystemAtlasPanelProps {
  width?: number
  height?: number
}

export const SystemAtlasPanel: React.FC<SystemAtlasPanelProps> = ({ 
  width, 
  height 
}) => {
  const graphRef = useRef<any>()
  const [viewMode, setViewMode] = useState<'tree' | 'graph'>('graph')
  const [selectedSystem, setSelectedSystem] = useState<string | null>(null)
  
  // Load system maps from backend
  const { systemMaps, loading } = useSystemMaps() // Custom hook
  
  // Build graph data from system maps
  const graphData = useMemo(() => {
    const nodes: Array<{ id: string; name: string; group: number; size: number }> = []
    const links: Array<{ source: string; target: string; value: number; type: string }> = []
    
    // Add system nodes
    systemMaps.forEach(system => {
      nodes.push({
        id: system.systemId,
        name: system.systemName,
        group: system.layer,
        size: 12 + (system.completionPercentage / 10)
      })
      
      // Add connections via ports
      system.ports.forEach(port => {
        if (port.connectsToSystem) {
          links.push({
            source: system.systemId,
            target: port.connectsToSystem,
            value: 1.0,
            type: port.protocol
          })
        }
      })
    })
    
    return { nodes, links }
  }, [systemMaps])
  
  // Color scheme for different system types
  const getNodeColor = (node: any) => {
    if (node.id === selectedSystem) return '#3b82f6' // Blue for selected
    if (node.group === 1) return '#10b981' // Green for Layer 1
    if (node.group === 2) return '#3b82f6' // Blue for Layer 2
    if (node.group === 3) return '#8b5cf6' // Purple for Layer 3
    return '#6b7280' // Gray default
  }
  
  // Link color based on connection type
  const getLinkColor = (link: any) => {
    switch (link.type) {
      case 'internal_api': return '#10b981' // Green
      case 'external_api': return '#3b82f6' // Blue
      default: return '#6b7280' // Gray
    }
  }
  
  if (viewMode === 'tree') {
    // Tree view implementation
    return <SystemTreeView systems={systemMaps} onSelect={setSelectedSystem} />
  }
  
  return (
    <div className="w-full h-full bg-gray-900 rounded-lg overflow-hidden relative">
      <div className="absolute top-2 left-2 z-10">
        <button
          onClick={() => setViewMode(viewMode === 'tree' ? 'graph' : 'tree')}
          className="px-3 py-1 bg-gray-800 text-white rounded text-sm"
        >
          {viewMode === 'tree' ? 'Graph' : 'Tree'}
        </button>
      </div>
      
      <ForceGraph2D
        ref={graphRef}
        graphData={graphData}
        width={width || 800}
        height={height || 600}
        nodeLabel={(node: any) => {
          return `<div style="background: rgba(0,0,0,0.9); color: white; padding: 6px 10px; border-radius: 4px; font-size: 12px; font-weight: 500;">${node.name}</div>`
        }}
        nodeColor={getNodeColor}
        nodeVal={(node: any) => node.size}
        linkColor={getLinkColor}
        linkWidth={2}
        linkDirectionalArrowLength={6}
        linkDirectionalArrowRelPos={1}
        onNodeClick={(node: any) => {
          setSelectedSystem(node.id)
        }}
        onNodeHover={(node: any) => {
          if (node && graphRef.current) {
            graphRef.current.getGraph().setNodeHighlight(node.id, true)
          }
        }}
        cooldownTicks={100}
        onEngineStop={() => {
          if (graphRef.current) {
            graphRef.current.zoomToFit(400, 20)
          }
        }}
        nodeCanvasObjectMode={() => 'after'}
        nodeCanvasObject={(node: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
          // Draw circle background
          ctx.beginPath()
          ctx.arc(node.x, node.y, node.size, 0, 2 * Math.PI)
          ctx.fillStyle = getNodeColor(node)
          ctx.fill()
          
          // Draw border for selected nodes
          if (node.id === selectedSystem) {
            ctx.strokeStyle = '#ffffff'
            ctx.lineWidth = 2 / globalScale
            ctx.stroke()
          }
          
          // Draw system icon/emoji
          const icon = getSystemIcon(node.group)
          ctx.font = `${node.size * 1.2}px Arial`
          ctx.textAlign = 'center'
          ctx.textBaseline = 'middle'
          ctx.fillStyle = '#ffffff'
          ctx.fillText(icon, node.x, node.y)
        }}
      />
      
      {/* System Detail Panel (within this component) */}
      {selectedSystem && (
        <SystemDetailPanel
          systemId={selectedSystem}
          onClose={() => setSelectedSystem(null)}
        />
      )}
    </div>
  )
}
```

### **Tree View Implementation**

**Custom Tree Component:**
```typescript
interface SystemTreeViewProps {
  systems: SystemMap[]
  onSelect: (systemId: string) => void
}

export const SystemTreeView: React.FC<SystemTreeViewProps> = ({ 
  systems, 
  onSelect 
}) => {
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set())
  
  const toggleNode = (nodeId: string) => {
    const newExpanded = new Set(expandedNodes)
    if (newExpanded.has(nodeId)) {
      newExpanded.delete(nodeId)
    } else {
      newExpanded.add(nodeId)
    }
    setExpandedNodes(newExpanded)
  }
  
  return (
    <div className="w-full h-full bg-gray-900 text-white p-4 overflow-auto">
      {systems.map(system => (
        <div key={system.systemId} className="mb-2">
          <div
            className="flex items-center gap-2 cursor-pointer hover:bg-gray-800 p-2 rounded"
            onClick={() => toggleNode(system.systemId)}
          >
            <span>{expandedNodes.has(system.systemId) ? '▼' : '▶'}</span>
            <span className="font-semibold">{system.systemName}</span>
            <span className="text-xs text-gray-400">({system.layer})</span>
          </div>
          {expandedNodes.has(system.systemId) && (
            <div className="ml-6 mt-1">
              {/* Show system details */}
              <div className="text-sm text-gray-300">
                Status: {system.status}
              </div>
              <div className="text-sm text-gray-300">
                Completion: {system.completionPercentage}%
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  )
}
```

### **Data Loading Hooks**

**Custom Hook for System Maps:**
```typescript
import { useState, useEffect } from 'react'
import { useCMC } from '../hooks/useAIMOS'

export const useSystemMaps = () => {
  const { retrieveAtoms } = useCMC()
  const [systemMaps, setSystemMaps] = useState<SystemMap[]>([])
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    const loadSystemMaps = async () => {
      try {
        // Load all system.map.lucid.json5 files
        const maps = await retrieveAtoms('system.map.lucid.json5', ['system-map'])
        const parsed = maps.map(atom => JSON5.parse(atom.content))
        setSystemMaps(parsed)
      } catch (error) {
        console.error('Failed to load system maps:', error)
      } finally {
        setLoading(false)
      }
    }
    
    loadSystemMaps()
  }, [retrieveAtoms])
  
  return { systemMaps, loading }
}
```

---

## 📊 **DATA SOURCES & PARSING**

### **System Maps**
- **Location:** `knowledge_architecture/systems/{system}/system.map.lucid.json5`
- **Format:** JSON5 with internalNodes, ports, edges
- **Parser:** JSON5 parser with validation

### **System Indexes**
- **Location:** `knowledge_architecture/systems/{system}/system.index.lucid.json5`
- **Format:** JSON5 with intent, architecture, integrations, status
- **Parser:** JSON5 parser with validation

### **T0-T4 Documentation**
- **Location:** `knowledge_architecture/systems/{system}/T{0-4}_*.md`
- **Format:** Markdown with frontmatter metadata
- **Parser:** Markdown parser with frontmatter extraction

### **SUPER_INDEX**
- **Location:** `knowledge_architecture/SUPER_INDEX.md`
- **Format:** Markdown with concept entries
- **Parser:** Markdown parser with concept extraction

### **GOAL_TREE**
- **Location:** `goals/GOAL_TREE.yaml`
- **Format:** YAML with hierarchical structure
- **Parser:** YAML parser with validation

---

## 🎯 **SUCCESS CRITERIA**

### **Phase 1 Success Criteria:**
- ✅ All 3 core panels operational
- ✅ Data parsing working correctly
- ✅ Basic navigation functional

### **Phase 2 Success Criteria:**
- ✅ All 3 visualization panels operational
- ✅ Graph visualization working
- ✅ Interactive navigation functional

### **Phase 3 Success Criteria:**
- ✅ All panels operational
- ✅ Deep AIM-OS integration complete
- ✅ Performance optimized (<100ms load time)

---

## 💡 **FUTURE ENHANCEMENTS**

### **Planned Features:**
1. **Enhanced Graph Physics** - Better force-directed graph parameters
2. **Custom Views** - Save custom panel layouts (within panel)
3. **Export/Share** - Export system maps and indexes (from backend data)
4. **Real-Time Collaboration** - Share views with other agents (via backend)
5. **Advanced Filtering** - More sophisticated filter combinations
6. **Graph Clustering** - Cluster related nodes in graph view
7. **Tree Expansion** - Remember expanded/collapsed state (within panel)

---

**Status:** ✅ **DESIGN COMPLETE**  
**Next:** Begin Phase 1 implementation  
**Confidence:** 0.85 (High - comprehensive design complete)

---

*Created by Agent Sev*  
*2025-01-27*  
*Purpose: Panel designs for hierarchical organization visualization*

