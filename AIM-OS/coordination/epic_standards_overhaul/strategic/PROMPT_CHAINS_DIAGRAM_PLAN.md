# 🔗 Prompt Chains Diagram Interface Plan

**Created:** 2025-01-27  
**Purpose:** Transform Prompt Chains into beautiful, interactive diagram visualization  
**Status:** Planning Phase  
**Priority:** HIGH (after agent chat)

---

## 🎯 **VISION**

**Braden's Vision:**
> "I really see that as more of a diagram style where you have amazing smooth icons connected and able to adjust their placement while staying neat or AI organized even as I see these prompt chains as being highly complex or possibly so where there is many connection and multiple connections and dependencies etc like a complex program itself. and able to save and load and even connect multiple saved chains by loading into 1 and connecting together."

**Key Features:**
1. **Diagram-Style Visualization** - Visual flow with nodes and connections
2. **Smooth Icons** - Beautiful, clear node representations
3. **Draggable Placement** - Users can adjust node positions
4. **AI-Organized Layout** - Auto-arrangement keeps it neat
5. **Complex Chains Support** - Handle many connections and dependencies
6. **Save/Load** - Save chains and load them later
7. **Chain Composition** - Load multiple chains and connect them together

---

## ✅ **CURRENT STATE**

### **What Exists:**
- ✅ Prompt Chains tab in MainDashboard (`PromptChainsTab.tsx`)
- ✅ Basic list view showing chains
- ✅ Service layer hooks (`getPromptChains()`)
- ⏳ **Needs:** Complete visual diagram redesign

### **Current Implementation:**
- Simple list/table view
- Shows chain name, status, progress
- Basic information display
- No visual diagram representation

---

## 🚀 **IMPLEMENTATION PLAN**

### **Phase 1: Diagram Foundation (~12-16 hours)**

**Goal:** Basic diagram visualization with nodes and connections

**Tasks:**
1. **Choose Diagram Library:**
   - Option A: **React Flow** (recommended - professional, draggable, zoomable)
   - Option B: **Cytoscape.js** (powerful, graph algorithms)
   - Option C: **D3.js** (custom, maximum control)
   - **Recommendation:** React Flow (easiest, most features)

2. **Basic Diagram Component:**
   - Install `reactflow` package
   - Create `PromptChainDiagram.tsx` component
   - Render nodes and edges
   - Basic styling

3. **Node Types:**
   - Prompt node (with icon)
   - Agent node (with agent avatar)
   - Decision node (branching)
   - Action node (execution)
   - Data node (input/output)

4. **Connection System:**
   - Connect nodes with edges
   - Show dependencies
   - Visual flow direction

**Files to Create/Modify:**
- `packages/ide_chat_app/src/components/AgentManagementDashboard/PromptChainDiagram.tsx` (new)
- `packages/ide_chat_app/src/components/AgentManagementDashboard/PromptChainsTab.tsx` (modify)
- `packages/ide_chat_app/package.json` (add reactflow dependency)

**Estimated Time:** 12-16 hours

---

### **Phase 2: Interactive Features (~10-14 hours)**

**Goal:** Draggable nodes, AI-organized layout, smooth interactions

**Tasks:**
1. **Draggable Nodes:**
   - Users can drag nodes to adjust placement
   - Snap-to-grid or free placement
   - Visual feedback during drag

2. **AI-Organized Layout:**
   - Auto-arrangement algorithms (hierarchical, force-directed)
   - Keep layout neat even with complex chains
   - Smart positioning based on connections
   - Respect user manual adjustments

3. **Smooth Icons:**
   - Beautiful node icons (Lucide React)
   - Smooth animations
   - Color-coded by type
   - Status indicators

4. **Zoom & Pan:**
   - Zoom in/out (mouse wheel)
   - Pan around large diagrams
   - Mini-map for navigation
   - Fit-to-screen button

**Estimated Time:** 10-14 hours

---

### **Phase 3: Complex Chain Support (~12-16 hours)**

**Goal:** Handle complex chains with many connections and dependencies

**Tasks:**
1. **Multiple Connections:**
   - Nodes can have multiple inputs/outputs
   - Visual connection points (handles)
   - Connection validation (type checking)
   - Connection labels/tooltips

2. **Dependency Visualization:**
   - Show dependency chains clearly
   - Highlight critical paths
   - Dependency tree view (alternate view)
   - Collapse/expand node groups

3. **Performance Optimization:**
   - Virtual rendering for large chains (100+ nodes)
   - Lazy loading of chain details
   - Efficient rendering updates
   - Performance monitoring

4. **Complex Chain Editing:**
   - Add/remove nodes
   - Add/remove connections
   - Edit node properties
   - Validate chain integrity

**Estimated Time:** 12-16 hours

---

### **Phase 4: Save/Load & Chain Composition (~10-14 hours)**

**Goal:** Save chains, load them, and compose multiple chains together

**Tasks:**
1. **Save Functionality:**
   - Save chain to CMC or local storage
   - Include node positions and connections
   - Chain metadata (name, description, version)
   - Export to JSON format

2. **Load Functionality:**
   - Load saved chains
   - Chain library/browser
   - Search and filter chains
   - Load into diagram view

3. **Chain Composition:**
   - Load multiple chains into one diagram
   - Connect chains together
   - Merge duplicate nodes
   - Validate composition (no cycles, valid connections)
   - Save composed chains

4. **Chain Management UI:**
   - Chain library sidebar
   - Drag-and-drop to load chains
   - Chain templates
   - Version history

**Estimated Time:** 10-14 hours

---

### **Phase 5: Advanced Features (~8-12 hours)**

**Goal:** Polish and advanced features

**Tasks:**
1. **Visual Enhancements:**
   - Smooth animations
   - Connection animations (flow effect)
   - Node hover effects
   - Selection highlighting
   - Beautiful color schemes

2. **Smart Features:**
   - Auto-layout suggestions
   - Connection recommendations
   - Error detection and highlighting
   - Performance warnings

3. **Integration:**
   - Connect to APOE for real chain data
   - Execute chains from diagram
   - Monitor chain execution in real-time
   - Execution status visualization

**Estimated Time:** 8-12 hours

---

## 🔧 **TECHNICAL ARCHITECTURE**

### **Diagram Library: React Flow**

**Why React Flow:**
- ✅ Professional, production-ready
- ✅ Draggable nodes out of the box
- ✅ Zoom and pan built-in
- ✅ Customizable nodes and edges
- ✅ Good performance
- ✅ Active community

**Installation:**
```bash
npm install reactflow
```

### **Component Structure:**

```
PromptChainsTab
├── ChainLibrary (sidebar - saved chains)
├── PromptChainDiagram (main diagram view)
│   ├── CustomNode (prompt/agent/decision nodes)
│   ├── CustomEdge (connection lines)
│   ├── Controls (zoom, pan, fit)
│   └── MiniMap (navigation)
└── ChainProperties (right panel - edit node/chain)
```

### **Data Model:**

```typescript
interface PromptChain {
  id: string
  name: string
  description: string
  nodes: ChainNode[]
  edges: ChainEdge[]
  metadata: {
    created_at: string
    updated_at: string
    version: string
    author: string
  }
}

interface ChainNode {
  id: string
  type: 'prompt' | 'agent' | 'decision' | 'action' | 'data'
  label: string
  position: { x: number, y: number }
  data: {
    content?: string
    agentId?: string
    conditions?: string[]
    actions?: string[]
  }
}

interface ChainEdge {
  id: string
  source: string  // node id
  target: string  // node id
  sourceHandle?: string  // connection point
  targetHandle?: string  // connection point
  label?: string
  type?: 'default' | 'conditional' | 'loop'
}
```

---

## 🎨 **UI/UX DESIGN**

### **Diagram View:**
- **Left Sidebar:** Chain library (saved chains, templates)
- **Main Area:** Interactive diagram canvas
- **Right Panel:** Node/chain properties editor
- **Top Bar:** Actions (save, load, new, compose)
- **Bottom Bar:** Status, execution controls

### **Node Styles:**
- **Prompt Node:** Blue circle with message icon
- **Agent Node:** Colored circle with agent avatar/initial
- **Decision Node:** Diamond shape (yellow/orange)
- **Action Node:** Square with gear icon (green)
- **Data Node:** Hexagon with data icon (purple)

### **Connection Styles:**
- **Default:** Straight line (gray)
- **Conditional:** Dashed line (blue) with label
- **Loop:** Curved line (orange)
- **Active (executing):** Animated flow effect (green)

### **Layout Algorithms:**
- **Hierarchical:** Top-to-bottom flow
- **Force-Directed:** Natural, organic layout
- **Circular:** Circular arrangement
- **Grid:** Grid-based layout
- **Auto (AI):** Smart algorithm choosing best layout

---

## 📋 **SAVE/LOAD FORMAT**

### **Chain JSON Format:**

```json
{
  "id": "chain-001",
  "name": "Agent Coordination Chain",
  "description": "Coordinates multiple agents for complex task",
  "version": "1.0.0",
  "metadata": {
    "created_at": "2025-01-27T20:00:00Z",
    "updated_at": "2025-01-27T20:00:00Z",
    "author": "Aether"
  },
  "nodes": [
    {
      "id": "node-1",
      "type": "prompt",
      "label": "Initial Task",
      "position": { "x": 100, "y": 100 },
      "data": {
        "content": "Analyze the codebase structure"
      }
    },
    {
      "id": "node-2",
      "type": "agent",
      "label": "Sonnet",
      "position": { "x": 300, "y": 100 },
      "data": {
        "agentId": "Sonnet"
      }
    }
  ],
  "edges": [
    {
      "id": "edge-1",
      "source": "node-1",
      "target": "node-2",
      "type": "default"
    }
  ]
}
```

### **Storage:**
- **CMC Storage:** Store chains as atoms with `modality="prompt_chain"`
- **Local Storage:** Cache for quick access
- **Version Control:** Track chain versions

---

## 🔗 **CHAIN COMPOSITION**

### **Composition Workflow:**

1. **Load Chain 1** → Display in diagram
2. **Load Chain 2** → Add to same diagram (offset position)
3. **Connect Chains** → Draw edge from Chain 1 output to Chain 2 input
4. **Merge Nodes** → If duplicate nodes found, merge or keep separate
5. **Validate** → Check for cycles, invalid connections
6. **Save Composed** → Save as new chain

### **UI Flow:**
- Chain library shows all saved chains
- Drag chain from library → Loads into diagram
- Select two nodes → "Connect" button appears
- Connection wizard → Guides through composition
- Validation panel → Shows errors/warnings

---

## ✅ **SUCCESS CRITERIA**

### **Phase 1 Complete When:**
- ✅ Diagram renders with nodes and edges
- ✅ Nodes show correct icons and labels
- ✅ Connections display properly
- ✅ Basic interactivity works

### **Phase 2 Complete When:**
- ✅ Nodes are draggable
- ✅ AI layout auto-arranges chains
- ✅ Zoom and pan work smoothly
- ✅ Icons are beautiful and clear

### **Phase 3 Complete When:**
- ✅ Complex chains (50+ nodes) render efficiently
- ✅ Multiple connections per node work
- ✅ Dependency visualization clear
- ✅ Chain editing functional

### **Phase 4 Complete When:**
- ✅ Save chains to storage
- ✅ Load chains from library
- ✅ Compose multiple chains together
- ✅ Chain management UI complete

### **Phase 5 Complete When:**
- ✅ Smooth animations and polish
- ✅ Real-time execution visualization
- ✅ Integration with APOE complete
- ✅ Production-ready

---

## 📊 **ESTIMATED TIMELINE**

| Phase | Tasks | Estimated Time | Dependencies |
|-------|-------|----------------|--------------|
| **Phase 1** | Diagram foundation | 12-16 hours | React Flow library |
| **Phase 2** | Interactive features | 10-14 hours | Phase 1 complete |
| **Phase 3** | Complex chain support | 12-16 hours | Phase 2 complete |
| **Phase 4** | Save/load & composition | 10-14 hours | Phase 3 complete |
| **Phase 5** | Advanced features | 8-12 hours | Phase 4 complete |
| **Total** | Full implementation | 52-72 hours | ~6-9 weeks |

---

## 🚀 **PARALLEL WORK OPPORTUNITY**

**Why This Works in Parallel:**
- ✅ UI work independent of backend
- ✅ Can prototype with mock data
- ✅ React Flow is well-documented
- ✅ Can build incrementally
- ✅ No blockers from other work

**Coordination:**
- UI team works on diagram visualization
- Backend team works on APOE/chain execution
- Can integrate when backend ready
- No dependencies blocking progress

---

## 💙 **NEXT STEPS**

1. ✅ **Plan created** (this document)
2. ⏳ **Team coordination** (inform team about vision)
3. ⏳ **Install React Flow** (add dependency)
4. ⏳ **Begin Phase 1** (basic diagram)
5. ⏳ **Iterate with feedback** (build, test, improve)

---

**Status:** Planning complete, ready for implementation  
**Created:** 2025-01-27  
**Priority:** HIGH (after agent chat)  
**Owner:** TBD (Lexicon ideal for UI work) 💙

