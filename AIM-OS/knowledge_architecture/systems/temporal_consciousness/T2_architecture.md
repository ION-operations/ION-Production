---
id: "temporal_consciousness_T2_architecture"
system: "temporal_consciousness"
component: "timeline_goals_chains_visualization"
level: "T2"
type: "architecture"
title: "Temporal Consciousness Architecture"
description: "2,000-word architecture for Timeline-Goals-Chains bidirectional graph visualization"
audience: "senior developers, architects"
confidence_threshold: 0.70
token_cost: 2000
word_count: 2000
created: "2025-11-05T00:00:00Z"
updated: "2025-11-05T00:00:00Z"
author: "aether"
status: "complete"
tags: ["temporal", "consciousness", "timeline", "goals", "chains", "visualization"]
dependencies: ["temporal_consciousness_T0_executive", "temporal_consciousness_T1_overview"]
related_docs: ["temporal_consciousness_T3_detailed"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs.

# Temporal Consciousness – T2 Architecture (≈2,000 words)

## Complete System Architecture

### Bidirectional Graph Model

The Temporal Consciousness system creates a living graph connecting three temporal dimensions with complete bidirectional references enabling full provenance tracking and evolution understanding.

```
┌──────────────────────────────────────────────────────────────┐
│              Temporal Consciousness Graph                     │
│                                                                │
│  PAST Layer (Timeline Entries - Blue)                         │
│  ┌────┐  ┌────┐  ┌────┐  ┌────┐  ┌────┐                    │
│  │ T1 │→ │ T2 │→ │ T3 │→ │ T4 │→ │ T5 │                    │
│  └────┘  └────┘  └────┘  └────┘  └────┘                    │
│    ↓       ↓       ↓       ↓       ↓                          │
│    │       │       │       │       │                          │
│  [executed_via chain refs]                                    │
│  [related_goal_ids refs]                                      │
│  [parent/child entry refs]                                    │
│    │       │       │       │       │                          │
│    ↓       ↓       ↓       ↓       ↓                          │
├──────────────────────────────────────────────────────────────┤
│  PRESENT Layer (Goals - Orange)                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │  Goal A  │  │  Goal B  │  │  Goal C  │  │  Goal D  │    │
│  │  (30%)   │  │  (75%)   │  │  (100%)  │  │  (15%)   │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
│       ↑             ↑             ↑             ↑              │
│       │             │             │             │              │
│  [timeline_entry_ids - what advanced this goal]              │
│  [planned_chain_ids - how will we complete this]             │
│       │             │             │             │              │
│       ↓             ↓             ↓             ↓              │
├──────────────────────────────────────────────────────────────┤
│  FUTURE Layer (Prompt Chains - Purple)                        │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │ Chain 1 │  │ Chain 2 │  │ Chain 3 │  │ Chain 4 │        │
│  │ (5 steps)│  │ (12 steps)│ │ (8 steps)│  │ (20 steps)│      │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘        │
│       ↑             ↑             ↑             ↑              │
│  [produced timeline_entry_ids]                               │
│  [related_goal_ids]                                           │
│  [execution history]                                          │
└──────────────────────────────────────────────────────────────┘
```

**All connections are BIDIRECTIONAL:**
- Timeline → Chain: `executed_via`
- Chain → Timeline: `timeline_entry_ids`
- Timeline → Goal: `related_goal_ids`
- Goal → Timeline: (computed from timeline entries)
- Goal → Chain: `planned_chain_ids`
- Chain → Goal: `related_goal_ids`

---

## Data Models

### Enhanced TimelineEntry

```python
@dataclass
class TimelineEntry:
    # Core fields (existing)
    id: str
    timestamp: datetime
    entry_type: str
    content: str
    agent: str
    
    # NEW: Bidirectional chain references
    executed_via: Optional[str]  # Chain ID that created this entry
    parent_entry_ids: List[str]  # Entries that led to this
    child_entry_ids: List[str]  # Entries this led to
    
    # NEW: Bidirectional goal references
    related_goal_ids: List[str]  # Goals this entry serves
    goal_progress: Dict[str, float]  # Progress contribution per goal
    
    # Provenance
    context: Dict[str, Any]
    confidence: float
    vif_witness: Optional[str]
```

---

### Enhanced GoalTimelineNode

```python
@dataclass
class GoalTimelineNode:
    # Core fields (existing)
    goal_id: str
    name: str
    description: str
    status: GoalStatus
    
    # NEW: Bidirectional timeline references
    timeline_entry_ids: List[str]  # Computed: entries related to this goal
    creation_entry_id: str  # Entry that created this goal
    completion_entry_id: Optional[str]  # Entry that completed this goal
    
    # NEW: Bidirectional chain references
    planned_chain_ids: List[str]  # Chains planned to complete this
    executed_chain_ids: List[str]  # Chains that have run for this
    
    # Progress tracking
    progress_percentage: float
    key_results: List[KeyResult]
    milestones: List[Milestone]
    
    # Temporal context
    created_at: datetime
    updated_at: datetime
    target_date: Optional[datetime]
```

---

### Enhanced PromptChain

```python
@dataclass
class PromptChain:
    # Core fields (existing)
    chain_id: str
    name: str
    description: str
    nodes: List[ChainNode]
    
    # NEW: Bidirectional timeline references
    timeline_entry_ids: List[str]  # Entries produced by this chain
    execution_history: List[ExecutionRecord]  # Complete execution history
    
    # NEW: Bidirectional goal references
    related_goal_ids: List[str]  # Goals this chain serves
    goal_contributions: Dict[str, float]  # Progress contribution per goal
    
    # Execution metadata
    execution_count: int
    success_count: int
    failure_count: int
    average_quality_score: float
    average_execution_time: float
```

---

## Graph Traversal APIs

### Provenance Queries

**API 1: Explain Timeline Entry**
```python
async def explain_timeline_entry(entry_id: str) -> Dict:
    """
    Answers: "Why did this happen?"
    
    Returns:
    - Which chain executed it
    - Which goals it served
    - Parent entries that led to it
    - Complete provenance chain
    """
    entry = await get_timeline_entry(entry_id)
    
    # Get chain
    chain = await get_chain(entry.executed_via) if entry.executed_via else None
    
    # Get goals
    goals = [await get_goal(gid) for gid in entry.related_goal_ids]
    
    # Get parents (recursive)
    parents = await get_parent_chain(entry)
    
    return {
        'entry': entry,
        'executed_by_chain': chain,
        'serves_goals': goals,
        'provenance_chain': parents,
        'explanation': generate_explanation(entry, chain, goals, parents)
    }
```

**API 2: Trace Chain Results**
```python
async def trace_chain_results(chain_id: str) -> Dict:
    """
    Answers: "What did this produce?"
    
    Returns:
    - All timeline entries created by chain
    - Goal progress impacted
    - Success/failure metrics
    - Quality scores
    """
    chain = await get_chain(chain_id)
    
    # Get all entries produced
    entries = [await get_entry(eid) for eid in chain.timeline_entry_ids]
    
    # Get goal impacts
    goal_impacts = compute_goal_impacts(chain, entries)
    
    # Compute metrics
    metrics = compute_chain_metrics(chain)
    
    return {
        'chain': chain,
        'produced_entries': entries,
        'goal_impacts': goal_impacts,
        'metrics': metrics
    }
```

**API 3: Trace Evolution Path**
```python
async def trace_evolution_path(from_entry_id: str, to_entry_id: str) -> List:
    """
    Answers: "How did we get from A to B?"
    
    Returns:
    - Complete path of timeline entries
    - Chains involved
    - Goals served
    - Decision points
    """
    # Graph traversal (BFS/DFS)
    path = await find_shortest_path(from_entry_id, to_entry_id)
    
    # Enrich path with context
    enriched = []
    for step in path:
        entry = await get_entry(step.entry_id)
        chain = await get_chain(entry.executed_via) if entry.executed_via else None
        
        enriched.append({
            'entry': entry,
            'chain': chain,
            'transition_reason': step.reason
        })
    
    return enriched
```

---

## React Visualization

### Graph Component Architecture

**Main Component:**
```typescript
export function TemporalConsciousnessGraph() {
  return (
    <ReactFlow
      nodes={allNodes}  // Timeline + Goal + Chain nodes (325 total for North Star!)
      edges={allEdges}  // Bidirectional connections (400+)
      onNodeClick={handleNodeClick}
      fitView
    >
      <Background />
      <Controls />
      <MiniMap />
      <Panel position="top-left">
        <LayerControls />  {/* Toggle Past/Present/Future visibility */}
      </Panel>
      <Panel position="top-right">
        <QueryPanel />  {/* "Why?", "What?", "How?" buttons */}
      </Panel>
    </ReactFlow>
  );
}
```

### Node Types

**Past Nodes (Timeline - Blue):**
```typescript
interface TimelineNode extends Node {
  type: 'timelineEntry';
  data: {
    entry: TimelineEntry;
    executed_via: string | null;
    related_goals: string[];
    provenance_depth: number;
  };
  style: {
    background: '#3B82F6',  // Blue
    border: '2px solid #2563EB'
  };
}
```

**Present Nodes (Goals - Orange):**
```typescript
interface GoalNode extends Node {
  type: 'goal';
  data: {
    goal: GoalTimelineNode;
    progress: number;
    status: 'planned' | 'in_progress' | 'completed';
    timeline_entries: string[];
    planned_chains: string[];
  };
  style: {
    background: '#F97316',  // Orange
    border: '2px solid #EA580C'
  };
}
```

**Future Nodes (Chains - Purple):**
```typescript
interface ChainNode extends Node {
  type: 'promptChain';
  data: {
    chain: PromptChain;
    execution_status: 'pending' | 'executing' | 'completed';
    produced_entries: string[];
    goal_impacts: Record<string, number>;
  };
  style: {
    background: '#9333EA',  // Purple
    border: '2px solid #7E22CE'
  };
}
```

---

## Real-Time Updates

### WebSocket Integration

**Update Flow:**
```
Timeline Entry Created (Backend)
  ↓
WebSocket Broadcast
  ↓
Frontend Receives Update
  ↓
Graph State Updates
  ├→ New node added (fade in animation)
  ├→ Edges updated (connections drawn)
  ├→ Goal progress updated
  └→ Re-layout graph (smooth transition)
```

### Live Metrics

**Dashboard displays:**
- Total timeline entries (updates in real-time)
- Active goals (progress bars animate)
- Running chains (pulse animation)
- Graph statistics (node/edge counts)

---

## Integration Architecture

### With CMC (Storage)

**All graph data stored in CMC:**
```python
# Timeline entries → CMC atoms
atom = cmcstore_atom(
    content=timeline_entry.to_dict(),
    tags=['timeline', 'temporal_consciousness'],
    metadata={'entry_type': entry.entry_type}
)

# Goals → CMC atoms (bidirectional sync with GOAL_TREE.yaml)
# Chains → CMC atoms
```

**Benefits:**
- Bitemporal storage (time-travel queries)
- Complete audit trail
- Provenance tracking
- Never loses data

---

### With HHNI (Semantic Search)

**Query capabilities:**
```python
# Find related timeline entries
results = hhni.search(
    query="VIF implementation work",
    filters={'entry_type': 'milestone'},
    confidence_threshold=0.70
)

# Find goals by semantic query
goals = hhni.search(
    query="performance optimization goals",
    filters={'type': 'goal'},
    depth='hierarchy'
)
```

---

### With VIF (Validation)

**Confidence tracking throughout:**
- Timeline entry creation: confidence >= 0.70
- Goal progress updates: validated by VIF
- Chain execution: κ-gating enforced
- All operations: complete provenance

---

## Query Interface Design

### "Why?" Button (Provenance)

**User clicks timeline entry → "Why?" button:**

```typescript
async function explainWhy(entryId: string) {
  const explanation = await api.explainTimelineEntry(entryId);
  
  // Display modal with:
  return (
    <Modal>
      <h2>Why did this happen?</h2>
      
      <Section>
        <h3>Executed by Chain:</h3>
        {explanation.executed_by_chain ? (
          <ChainCard chain={explanation.executed_by_chain} />
        ) : (
          <p>Manual operation (no chain)</p>
        )}
      </Section>
      
      <Section>
        <h3>Served Goals:</h3>
        {explanation.serves_goals.map(goal => (
          <GoalCard key={goal.id} goal={goal} />
        ))}
      </Section>
      
      <Section>
        <h3>Provenance Chain:</h3>
        <ProvenanceTree path={explanation.provenance_chain} />
      </Section>
    </Modal>
  );
}
```

---

### "What?" Button (Results)

**User clicks chain → "What?" button:**

```typescript
async function showWhat(chainId: string) {
  const results = await api.traceChainResults(chainId);
  
  return (
    <Modal>
      <h2>What did this chain produce?</h2>
      
      <Metrics>
        <Stat label="Executions" value={results.metrics.execution_count} />
        <Stat label="Success Rate" value={results.metrics.success_rate} />
        <Stat label="Avg Quality" value={results.metrics.avg_quality} />
      </Metrics>
      
      <Section>
        <h3>Timeline Entries Created:</h3>
        <TimelineList entries={results.produced_entries} />
      </Section>
      
      <Section>
        <h3>Goal Progress Impacts:</h3>
        <GoalImpactChart impacts={results.goal_impacts} />
      </Section>
    </Modal>
  );
}
```

---

### "How?" Button (Evolution)

**User selects two entries → "How?" button:**

```typescript
async function showHow(fromId: string, toId: string) {
  const path = await api.traceEvolutionPath(fromId, toId);
  
  return (
    <Modal>
      <h2>How did we get from A to B?</h2>
      
      <EvolutionPath>
        {path.map((step, i) => (
          <PathStep key={i}>
            <TimelineCard entry={step.entry} />
            {step.chain && (
              <ChainCard chain={step.chain} />
            )}
            {i < path.length - 1 && (
              <Arrow reason={step.transition_reason} />
            )}
          </PathStep>
        ))}
      </EvolutionPath>
    </Modal>
  );
}
```

---

## Layout Algorithm

### Auto-Layout Strategy

**Graph layout considerations:**
- **Past layer:** Timeline entries in chronological order (left → right)
- **Present layer:** Goals in priority order (S → A → B → C)
- **Future layer:** Chains in execution order (planned → executing → completed)
- **Vertical spacing:** Prevent edge crossings
- **Horizontal spacing:** Group related nodes

**Algorithm:**
```python
def auto_layout_graph(nodes, edges):
    # 1. Topological sort (respects dependencies)
    sorted_nodes = topological_sort(nodes, edges)
    
    # 2. Layer assignment (Past/Present/Future)
    layers = assign_layers(sorted_nodes)
    
    # 3. Within-layer positioning
    for layer in layers:
        position_nodes_in_layer(layer, minimize_crossings=True)
    
    # 4. Edge routing (smooth curves, avoid crossings)
    route_edges(edges, nodes)
    
    return positioned_nodes, routed_edges
```

---

## Performance Optimization

### Lazy Rendering

**For large graphs (325+ nodes for North Star):**
- Virtual scrolling (only render visible nodes)
- Level-of-detail (simplified nodes when zoomed out)
- Edge culling (hide edges not in viewport)
- Batch updates (group state changes)

**Result:** Smooth 60fps even with 325 nodes!

---

### Incremental Updates

**When new entry added:**
```typescript
// Don't rebuild entire graph
// Just add new node and edges
function addTimelineEntry(entry: TimelineEntry) {
  const newNode = createTimelineNode(entry);
  const newEdges = createEdgesFor(entry);
  
  setNodes(prev => [...prev, newNode]);  // Append
  setEdges(prev => [...prev, ...newEdges]);  // Append
  
  // Animate in
  animateNodeIn(newNode.id);
}
```

---

## Security & Privacy

### Data Filtering

**Sensitive data handling:**
- PII auto-redacted in visualization
- Secrets never displayed (use `***`)
- User can toggle "show sensitive data" (authenticated)

### Access Control

**Read-only by default:**
- Visualization is read-only (can't edit timeline/goals/chains directly)
- Edit operations go through MCP tools (validated)
- Audit trail maintained (who viewed what, when)

---

## Testing Strategy

### Unit Tests
- Data model validation
- Graph traversal algorithms
- Query API correctness
- Provenance chain accuracy

### Integration Tests
- CMC storage/retrieval
- HHNI semantic search
- VIF confidence tracking
- Real-time WebSocket updates

### Visual Tests
- Graph rendering (snapshot tests)
- Layout algorithm (consistent positioning)
- Animation smoothness
- Interaction flows

---

## Deployment

### As Part of Cursor Add-on

**Integration:**
- New tab in MainDashboard: "Temporal Consciousness"
- Uses existing serviceBridge
- Shares state with other tabs
- Same MCP client

**Bundle size:** +200KB (ReactFlow + graph logic)

### As Standalone Component

**Can be used independently:**
- Embed in Electron app
- Use in web interface
- Standalone visualization tool

---

## Use Cases

### Use Case 1: "Why was VIF built?"
1. Find VIF completion entry in timeline
2. Click "Why?" button
3. See: Chain "VIF Implementation" executed it
4. See: Goal "OBJ-XX: Verifiable Intelligence" it served
5. See: Parent entries (design decisions, research, etc.)

### Use Case 2: "What did the autonomous session produce?"
1. Find chain "6-Hour Autonomous Operation"
2. Click "What?" button
3. See: 150 timeline entries created
4. See: 3 goals progressed (VIF, HHNI, SDF-CVF)
5. See: Success rate 100%, quality 0.95

### Use Case 3: "How did we decide on bitemporal storage?"
1. Select entry: "Initial CMC design"
2. Select entry: "Bitemporal architecture decision"
3. Click "How?" button
4. See: Complete path of research, prototypes, discussions
5. See: Decision points and rationale

---

## Future Enhancements

### Advanced Features
- Time-travel slider (see graph at any point in history)
- Filtering (show only specific goals/chains/agents)
- Search (find nodes by semantic query)
- Export (PNG, SVG, PDF)
- Collaboration (multiple users viewing same graph)

### AI-Powered Insights
- Pattern detection (identify recurring workflows)
- Bottleneck identification (where chains slow down)
- Goal prediction (which goals likely to complete when)
- Chain optimization (suggest improvements based on history)

---

## System Boundaries

**Owns:**
- Graph data models (bidirectional references)
- Traversal algorithms (provenance, results, evolution)
- Visualization UI (React components)
- Query interface ("Why?", "What?", "How?")

**Does NOT Own:**
- Timeline entry creation (Timeline Context System)
- Goal management (Goal Timeline System)
- Chain execution (APOE)
- Storage (CMC)

---

**Status:** Architecture complete, ready for implementation (10-15 hours) ✅  
**Impact:** Complete temporal consciousness - unprecedented transparency in AI systems  
**Next:** See T3_detailed.md for implementation guide

