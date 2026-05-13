# Evolution Explorer Visualization Implementation Guide

**Purpose:** Step-by-step implementation guide for 8 remaining visualization modes  
**Created:** 2025-11-08  
**Status:** Ready for Implementation  
**MCP Plan ID:** plan_9c2cbc81-fc1a-48a6-901b-74e43c6505d7

---

## 🎯 **IMPLEMENTATION STRATEGY**

### **Phase 1: High Priority (Start Here)**

#### **1. Force-Directed Graph**
**Complexity:** Medium  
**Dependencies:** D3.js (or custom physics)  
**Time Estimate:** 4-6 hours

**Steps:**
1. Install D3.js: `npm install d3 @types/d3`
2. Create `ForceDirectedGraph.tsx` component
3. Implement D3 force simulation:
   - `d3.forceSimulation()` for physics
   - `d3.forceLink()` for connections
   - `d3.forceManyBody()` for repulsion
   - `d3.forceCenter()` for centering
4. Add drag handlers for interaction
5. Render nodes and links with SVG
6. Add zoom/pan controls
7. Integrate with EvolutionExplorerPanel

**Key Code Structure:**
```typescript
interface ForceDirectedGraphProps {
  nodes: EvolutionNode[]
  selectedNode: string | null
  onNodeSelect: (nodeId: string | null) => void
  getNodeColor: (node: EvolutionNode) => string
  getNodeIcon: (node: EvolutionNode) => React.ReactNode
}

const ForceDirectedGraph: React.FC<ForceDirectedGraphProps> = ({ ... }) => {
  const svgRef = useRef<SVGSVGElement>(null)
  const simulationRef = useRef<d3.Simulation<any, any> | null>(null)
  
  useEffect(() => {
    // Initialize D3 force simulation
    // Update on node changes
    // Handle drag interactions
  }, [nodes])
  
  return <svg ref={svgRef}>...</svg>
}
```

---

#### **2. Sankey Flow Diagram**
**Complexity:** High  
**Dependencies:** D3.js Sankey layout  
**Time Estimate:** 6-8 hours

**Steps:**
1. Install D3.js Sankey: `npm install d3-sankey @types/d3-sankey`
2. Create `SankeyFlowDiagram.tsx` component
3. Calculate flow widths from completion percentages
4. Build node-link structure:
   - Source: Seed
   - Targets: Core Systems (Ring 1)
   - Sub-targets: Subsystems (Ring 2)
   - Final targets: Details (Ring 3)
5. Use `d3.sankey()` layout
6. Render nodes and links
7. Add hover tooltips showing flow values
8. Integrate with EvolutionExplorerPanel

**Key Code Structure:**
```typescript
interface SankeyFlowDiagramProps {
  nodes: EvolutionNode[]
  selectedNode: string | null
  onNodeSelect: (nodeId: string | null) => void
}

const SankeyFlowDiagram: React.FC<SankeyFlowDiagramProps> = ({ ... }) => {
  const svgRef = useRef<SVGSVGElement>(null)
  
  const sankeyData = useMemo(() => {
    // Build Sankey data structure from nodes
    // Calculate flow widths
    // Return {nodes: [], links: []}
  }, [nodes])
  
  useEffect(() => {
    // Initialize D3 Sankey layout
    // Render nodes and links
  }, [sankeyData])
  
  return <svg ref={svgRef}>...</svg>
}
```

---

#### **3. Agent Collaboration Network**
**Complexity:** Medium  
**Dependencies:** Custom SVG (or D3.js)  
**Time Estimate:** 4-5 hours

**Steps:**
1. Create `AgentCollaborationNetwork.tsx` component
2. Filter nodes to show only agent-related:
   - Agent nodes (Aether, Max, Lex, Codex, Dac, Rev, Sam)
   - Goals worked on by agents
   - Tool calls from agents
   - Task handoffs between agents
3. Build network structure:
   - Agent → Goal connections
   - Agent → Tool connections
   - Agent → Agent communication
4. Use force-directed layout (simpler than full force-directed)
5. Color-code by agent
6. Show tool call paths
7. Integrate with EvolutionExplorerPanel

**Key Code Structure:**
```typescript
interface AgentCollaborationNetworkProps {
  nodes: EvolutionNode[]
  selectedNode: string | null
  onNodeSelect: (nodeId: string | null) => void
}

const AgentCollaborationNetwork: React.FC<AgentCollaborationNetworkProps> = ({ ... }) => {
  const agentNodes = useMemo(() => {
    // Filter to agent-related nodes
    // Extract agent assignments
    // Build agent → goal → tool structure
  }, [nodes])
  
  // Render agent network with connections
}
```

---

#### **4. Impact Map**
**Complexity:** Low  
**Dependencies:** Custom SVG  
**Time Estimate:** 2-3 hours

**Steps:**
1. Create `ImpactMap.tsx` component
2. Calculate node size from priority tier:
   - S tier = 80px radius
   - A tier = 60px radius
   - B tier = 40px radius
   - Adjust by completion percentage
3. Use bubble chart layout (pack layout or manual)
4. Color by status
5. Show priority tier badge
6. Show completion percentage
7. Integrate with EvolutionExplorerPanel

**Key Code Structure:**
```typescript
interface ImpactMapProps {
  nodes: EvolutionNode[]
  selectedNode: string | null
  onNodeSelect: (nodeId: string | null) => void
}

const ImpactMap: React.FC<ImpactMapProps> = ({ ... }) => {
  const sizedNodes = useMemo(() => {
    return nodes.map(node => ({
      ...node,
      size: calculateSize(node.priority, node.completion)
    }))
  }, [nodes])
  
  // Render bubbles with sizes
}
```

---

### **Phase 2: Medium Priority**

#### **5. Dependency Graph**
**Complexity:** Medium  
**Dependencies:** Custom SVG (or D3.js)  
**Time Estimate:** 4-5 hours

**Steps:**
1. Create `DependencyGraph.tsx` component
2. Build dependency structure:
   - Parent → Child relationships
   - Blocking relationships (if status = blocked)
   - Critical paths (longest dependency chain)
3. Use hierarchical layout (top-down)
4. Highlight blocking relationships in red
5. Show critical path in yellow
6. Add dependency depth indicators
7. Integrate with EvolutionExplorerPanel

---

#### **6. Network Graph**
**Complexity:** High  
**Dependencies:** D3.js (or React Flow)  
**Time Estimate:** 6-8 hours

**Steps:**
1. Create `NetworkGraph.tsx` component
2. Show all bidirectional connections:
   - Parent-child
   - Dependencies
   - Agent connections
   - Tool call paths
3. Use force-directed layout (simpler than full force-directed)
4. Add path highlighting on node click
5. Show relationship types
6. Add search/filter
7. Integrate with EvolutionExplorerPanel

---

#### **7. Error Propagation Map**
**Complexity:** Medium  
**Dependencies:** Custom SVG  
**Time Estimate:** 4-5 hours

**Steps:**
1. Create `ErrorPropagationMap.tsx` component
2. Filter to show errors + affected nodes
3. Build error propagation paths:
   - Error → Affected systems
   - Error → Recovery actions
4. Use hierarchical layout (errors at top)
5. Color-code by error type
6. Show impact radius
7. Highlight recovery paths
8. Integrate with EvolutionExplorerPanel

---

### **Phase 3: Low Priority**

#### **8. Timeline Spiral**
**Complexity:** Medium  
**Dependencies:** Custom SVG  
**Time Estimate:** 3-4 hours

**Steps:**
1. Create `TimelineSpiral.tsx` component
2. Calculate spiral position from timestamp:
   - Radius = time from start
   - Angle = day within period
   - Each revolution = 1 month
3. Render nodes along spiral path
4. Color by status/type
5. Add time period labels
6. Optional: Animated growth
7. Integrate with EvolutionExplorerPanel

---

## 📦 **DEPENDENCIES TO INSTALL**

```bash
# D3.js core (for force-directed, Sankey, layouts)
npm install d3 @types/d3

# D3 Sankey (for Sankey flow diagram)
npm install d3-sankey

# Optional: React Flow (alternative to D3 for network graphs)
npm install reactflow
```

---

## 🔧 **INTEGRATION PATTERN**

All visualizations follow this pattern:

```typescript
// In EvolutionExplorerPanel.tsx
{viewMode === 'force' && (
  <div className="relative w-full h-full overflow-auto">
    <ForceDirectedGraph 
      nodes={filteredTimeline}
      selectedNode={selectedNode}
      onNodeSelect={setSelectedNode}
      getNodeColor={getNodeColor}
      getNodeIcon={getNodeIcon}
    />
  </div>
)}
```

---

## 📊 **DATA STRUCTURE REQUIREMENTS**

Each visualization needs:
- `nodes`: Array of `EvolutionNode`
- `selectedNode`: Currently selected node ID
- `onNodeSelect`: Callback for node selection
- `getNodeColor`: Function to get node color
- `getNodeIcon`: Function to get node icon

**EvolutionNode Interface:**
```typescript
interface EvolutionNode {
  id: string
  type: 'objective' | 'key_result' | 'milestone' | 'error' | 'divergence'
  label: string
  description: string
  timestamp: string
  status: 'completed' | 'in_progress' | 'planned' | 'paused' | 'error' | 'divergence' | 'designed'
  completion?: number
  priority?: string
  parentId?: string
  children?: EvolutionNode[]
  origin?: string
  errorType?: string
  divergenceReason?: string
}
```

---

## ✅ **IMPLEMENTATION CHECKLIST**

### **Phase 1: High Priority**
- [ ] Install D3.js dependencies
- [ ] Implement Force-Directed Graph
- [ ] Implement Sankey Flow Diagram
- [ ] Implement Agent Collaboration Network
- [ ] Implement Impact Map

### **Phase 2: Medium Priority**
- [ ] Implement Dependency Graph
- [ ] Implement Network Graph
- [ ] Implement Error Propagation Map

### **Phase 3: Low Priority**
- [ ] Implement Timeline Spiral

### **Testing & Polish**
- [ ] Test all visualizations with real data
- [ ] Add loading states
- [ ] Add error handling
- [ ] Optimize performance
- [ ] Add tooltips/hover states
- [ ] Add keyboard navigation

---

## 🚀 **NEXT STEPS**

1. **Install Dependencies:** `npm install d3 @types/d3 d3-sankey`
2. **Start with Force-Directed Graph** (most interactive, reveals patterns)
3. **Then Sankey Flow** (shows effort flow clearly)
4. **Then Agent Network** (unique collaboration insight)
5. **Then Impact Map** (quick prioritization)

---

**Status:** Implementation Guide Complete  
**MCP Plan:** Created and stored  
**Ready:** Yes - Begin Phase 1 implementation

