# Special AIM-OS UI Features Analysis: Bitemporal Timeline & Goal Planning Systems

**Prepared By:** Sam  
**Date:** 2025-11-07  
**Purpose:** Analysis of special AIM-OS UI features for IDE orchestrator integration  
**Source:** Cursor Extension UI inspection  
**Deliverable:** Enhancement to UI Patterns Analysis

---

## Executive Summary

This document analyzes special AIM-OS UI features discovered in the Cursor extension, focusing on bitemporal timeline systems and goal planning integration. These features represent unique AIM-OS capabilities that should be integrated into the IDE orchestrator design.

**Key Findings:**
- **Bitemporal Timeline System:** Sequential ordering (not date-based), playback controls, event tracking
- **Goal Planning System:** Goals as timeline nodes with past/present/future tracking
- **Evolution Explorer:** Bidirectional graph visualization connecting Timeline ↔ Chain ↔ Goals
- **Temporal Consciousness Graph:** Interactive graph with Why/What/How queries
- **Consciousness Explorer:** Real-time consciousness state visualization with blueprint nodes and specs
- **Memory Browser Enhanced:** CMC memory browser with modality filtering
- **System Status Dashboard:** Real-time monitoring of AIM-OS systems
- **Lucid Orchestrator Main:** 4-pane orchestrator system (Code, Blueprint, Spec, Timeline)
- **Tool Quality Dashboard:** MCP tool quality monitoring
- **MCP Integration:** 9+ MCP tools for timeline, goal, memory, and system management

---

## 1. Bitemporal Timeline System

### 1.1 Architecture Overview

**Core Concept:**
- **Sequential Ordering:** Timeline uses sequence numbers, not calendar dates
- **Bitemporal Tracking:** Past/present/future states for all timeline entries
- **Event Types:** Execution, error, test, modification, focus, drift
- **Node Tracking:** Functions, components, classes, interfaces, tests

**Key Components:**
1. **LucidTimelineDrawer** (`LucidTimelineDrawer.tsx`)
   - Playback controls (play, pause, reset, skip)
   - Speed control (0.5x, 1x, 2x, 4x)
   - Event visualization with timeline tracks
   - Grid overlay and labels toggle
   - Event details panel

2. **TimelineTab** (`TimelineTab.tsx`)
   - Timeline view with filters (type, agent)
   - Evolution Explorer mode (bidirectional graph)
   - Real-time updates (30-second refresh)
   - MCP integration for timeline entries

3. **TimelinePane** (`TimelinePane.tsx`)
   - Analytics dashboard (activity, quality, performance)
   - Event filtering (type, time range, search)
   - Event type icons and colors
   - Chart visualization

### 1.2 Sequential Ordering System

**Key Innovation:**
- **Not Date-Based:** Uses sequence numbers instead of timestamps
- **Sequential IDs:** `goal-001`, `goal-002`, etc. (not date-based)
- **Temporal Position:** Calculated by sequence, not calendar date

**Implementation Pattern:**
```typescript
// Sequential ordering (from goal_timeline_node.py)
interface GoalTimelineNode {
  created_sequence: number;  // When created (past)
  current_sequence: number;  // Current position (present)
  target_sequence: number;    // Target completion (future)
}
```

**Benefits:**
- **Independent of Dates:** Works across time zones, calendar systems
- **Temporal Queries:** Query by sequence, not date
- **Bitemporal Tracking:** Past/present/future states preserved

**Citation:** `knowledge_architecture/AETHER_MEMORY/Timeline_Goals_Integration_Design.md`

### 1.3 Playback Controls

**Features:**
- **Play/Pause:** Animated timeline playback
- **Reset:** Return to beginning
- **Skip Back/Forward:** Jump by 100ms increments
- **Speed Control:** 0.5x, 1x, 2x, 4x playback speed
- **Time Ruler:** Visual time scale at top
- **Current Time Indicator:** Vertical line showing playback position

**Implementation Pattern:**
```typescript
// Playback controls (from LucidTimelineDrawer.tsx)
const [isPlaying, setIsPlaying] = useState(false);
const [currentTime, setCurrentTime] = useState(0);
const [playbackSpeed, setPlaybackSpeed] = useState(1);

// Animation loop
useEffect(() => {
  if (isPlaying) {
    const animate = () => {
      setCurrentTime(prev => {
        const newTime = prev + (0.1 * playbackSpeed);
        if (newTime >= maxTime) {
          setIsPlaying(false);
          return 0;
        }
        return newTime;
      });
      animationRef.current = requestAnimationFrame(animate);
    };
    animationRef.current = requestAnimationFrame(animate);
  }
}, [isPlaying, maxTime, playbackSpeed]);
```

**Benefits:**
- **Debugging:** Replay events to understand system behavior
- **Analysis:** Slow down fast events for detailed inspection
- **Visualization:** See temporal relationships between events

### 1.4 Event Tracking

**Event Types:**
- **Execution:** Function/component execution
- **Error:** Error occurrences
- **Test:** Test execution
- **Modification:** Code/file modifications
- **Focus:** Component focus events
- **Drift:** Cognitive drift detection

**Event Properties:**
```typescript
interface TimelineEvent {
  id: string;
  nodeId: string;
  timestamp: number;
  type: 'execution' | 'error' | 'test' | 'modification' | 'focus' | 'drift';
  duration: number;
  status: 'success' | 'error' | 'warning' | 'info';
  message: string;
  nodeName: string;
  filePath: string;
  line: number;
}
```

**Visualization:**
- **Timeline Tracks:** One track per node (function/component)
- **Event Bars:** Colored bars showing event duration
- **Status Colors:** Green (success), Red (error), Yellow (warning), Blue (info)
- **Event Icons:** Type-specific icons (Activity, Target, Zap, Settings, Eye, Clock)

---

## 2. Goal Planning System

### 2.1 Goals as Timeline Nodes

**Core Concept:**
- **Goals are Timeline Nodes:** Goals exist as first-class timeline nodes
- **Past/Present/Future:** Goals track creation (past), current state (present), target (future)
- **Sequential Ordering:** Goals use sequence numbers, not dates
- **Bidirectional Sync:** Goals sync with `GOAL_TREE.yaml`

**Implementation Pattern:**
```python
# Goal as Timeline Node (from goal_timeline_node.py)
@dataclass
class GoalTimelineNode:
    node_id: str
    goal_id: str  # OBJ-01, OBJ-02, etc.
    name: str
    description: str
    
    # Sequential Ordering
    created_sequence: int  # When created (past)
    current_sequence: int  # Current position (present)
    target_sequence: int  # Target completion (future)
    
    # Status Tracking
    status: GoalStatus  # planned, in_progress, completed, blocked, cancelled
    progress: float  # 0.0 to 1.0
    confidence: float  # VIF integration
    
    # Key Results
    key_results: List[KeyResult]
    completed_krs: int
    total_krs: int
    
    # Emotional Context
    emotional_context: Optional[EmotionalContext]
```

**Citation:** `packages/timeline_context_system/goal_timeline_node.py`

### 2.2 Goal Status Tracking

**Status Types:**
- **Planned:** Goal created but not started
- **In Progress:** Goal actively being worked on
- **Completed:** Goal finished successfully
- **Blocked:** Goal blocked by dependencies
- **Cancelled:** Goal cancelled (not completed)

**Progress Tracking:**
- **Progress:** 0.0 to 1.0 (percentage complete)
- **Key Results:** List of key results with completion status
- **Milestones:** Track milestone completion
- **Confidence:** VIF confidence in completion

**Visualization:**
```
Goal Status by Sequence:
[●●●●●●●●○○] OBJ-01: 80% complete (sequence 1-12)
[●●●○○○○○○○] OBJ-02: 30% complete (sequence 15-current)
[○○○○○○○○○○] OBJ-03: 0% complete (sequence 20-planned)
```

### 2.3 MCP Tools Integration

**Timeline Context Tools (3):**
- ✅ `add_timeline_entry` - Track context at each prompt (TCS)
- ⚠️ `get_timeline_summary` - **BUG:** timedelta serialization (use `get_timeline_entries` instead)
- ✅ `get_timeline_entries` - Query timeline history (TCS)

**Goal Timeline Tools (3):**
- ✅ `create_goal_timeline_node` - Create goals as timeline planning nodes
- ✅ `update_goal_progress` - Update goal progress and status
- ✅ `query_goal_timeline` - Query goals with filtering

**Citation:** `cursor-addon/docs/MCP_TOOLS_INTEGRATION.md`

---

## 3. Evolution Explorer

### 3.1 Bidirectional Graph Visualization

**Core Concept:**
- **Timeline ↔ Chain ↔ Goals:** Interactive graph connecting all three systems
- **Bidirectional Edges:** Timeline executes via Chain, Chain produces Timeline, Goals work on Chains
- **Visual Layout:** Left column (Timeline), Center column (Goals), Right column (Chains)

**Implementation Pattern:**
```typescript
// Temporal Graph Builder (from temporalGraphBuilder.ts)
buildGraph(data: TemporalGraphData): {nodes: Node[], edges: Edge[]} {
  // Create Timeline Nodes (Blue)
  // Create Goal Nodes (Green)
  // Create Chain Nodes (Orange)
  
  // Create Edges:
  // - Temporal edges (Timeline → Timeline)
  // - Execution edges (Timeline → Chain via executed_via)
  // - Production edges (Chain → Timeline via produced)
  // - Goal-Chain edges (Goal ↔ Chain via related_chain_ids)
}
```

**Edge Types:**
- **Temporal:** Timeline → Timeline (sequential flow)
- **Execution:** Timeline → Chain (timeline entry executed via chain)
- **Production:** Chain → Timeline (chain produced timeline entries)
- **Goal-Chain:** Goal ↔ Chain (goal working on chain)

**Citation:** `packages/ide_chat_app/src/services/temporalGraphBuilder.ts`

### 3.2 Why/What/How Queries

**Query Types:**
- **Why Query:** Why did this happen? (causal reasoning)
- **What Query:** What is this? (definition/explanation)
- **How Query:** How was this achieved? (process explanation)

**Implementation Pattern:**
```typescript
// Query Executor (from TemporalConsciousnessGraph.tsx)
const handleQuery = async (queryType: 'why' | 'what' | 'how') => {
  if (queryType === 'why') {
    result = await queryExecutor.execute_why_query(
      selectedNode.id,
      selectedNode.data.type,
      graph
    );
  }
  // ... what and how queries
};
```

**Query Results:**
- **Explanation:** Natural language explanation
- **Path:** Sequence of nodes leading to answer
- **Result Nodes:** Nodes found by query
- **Visual Highlighting:** Highlight path nodes in graph

**Citation:** `packages/ide_chat_app/src/components/TemporalConsciousnessGraph.tsx`

---

## 4. Integration Recommendations

### 4.1 Timeline Integration

**Recommended Integration:**
- **Bottom Drawer Panel:** Timeline drawer in bottom panel (already exists)
- **MCP Integration:** Use `get_timeline_entries` and `add_timeline_entry` MCP tools
- **Real-Time Updates:** Poll MCP tools every 30 seconds for new entries
- **Event Filtering:** Filter by type, agent, time range

**Implementation Pattern:**
```typescript
// Timeline Integration (from TimelineTab.tsx)
useEffect(() => {
  const loadEntries = async () => {
    try {
      const fetchedEntries = await aimosService.getTimelineEntries(50);
      if (fetchedEntries.length > 0) {
        setEntries(fetchedEntries);
      }
    } catch (error) {
      console.error('Failed to load timeline entries:', error);
    }
  };
  
  loadEntries();
  const interval = setInterval(loadEntries, 30000); // 30-second refresh
  return () => clearInterval(interval);
}, []);
```

### 4.2 Goal Planning Integration

**Recommended Integration:**
- **Right Drawer Panel:** Goal planning panel in right drawer
- **MCP Integration:** Use `query_goal_timeline`, `update_goal_progress`, `create_goal_timeline_node`
- **Progress Visualization:** Progress bars with sequence numbers
- **Status Indicators:** Visual status indicators (planned, in_progress, completed, blocked, cancelled)

**Implementation Pattern:**
```typescript
// Goal Planning Integration
const loadGoals = async () => {
  const goalsResponse = await fetch('http://localhost:5001/mcp/execute', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      tool: 'query_goal_timeline',
      arguments: { status: 'all' }
    })
  });
  const goalsData = await goalsResponse.json();
  const goals = goalsData.result || [];
  setGoals(goals);
};
```

### 4.3 Evolution Explorer Integration

**Recommended Integration:**
- **Main Content Area:** Evolution Explorer as main content view
- **MCP Integration:** Fetch timeline, goals, and chains via MCP tools
- **Graph Visualization:** Use React Flow for graph visualization
- **Query Interface:** Why/What/How query buttons

**Implementation Pattern:**
```typescript
// Evolution Explorer Integration (from TemporalConsciousnessGraph.tsx)
const loadGraphData = async () => {
  // Fetch Timeline entries via MCP
  const timelineResponse = await fetch('http://localhost:5001/mcp/execute', {
    method: 'POST',
    body: JSON.stringify({
      tool: 'get_timeline_entries',
      arguments: { limit: 100 }
    })
  });
  
  // Fetch Goals via MCP
  const goalsResponse = await fetch('http://localhost:5001/mcp/execute', {
    method: 'POST',
    body: JSON.stringify({
      tool: 'query_goal_timeline',
      arguments: { status: 'all' }
    })
  });
  
  // Build graph
  const graph = graphBuilder.buildGraph({ timeline, goals, chains });
  setNodes(graph.nodes);
  setEdges(graph.edges);
};
```

### 4.4 Playback Timeline Integration

**Recommended Integration:**
- **Bottom Drawer Panel:** Playback timeline in bottom drawer
- **Event Tracking:** Track execution, errors, tests, modifications
- **Playback Controls:** Play, pause, reset, skip, speed control
- **Event Details:** Show event details on click

**Implementation Pattern:**
```typescript
// Playback Timeline Integration (from LucidTimelineDrawer.tsx)
// Already implemented in LucidTimelineDrawer component
// Integrate into bottom drawer panel
```

---

## 5. MCP Tools Integration Matrix

### 5.1 Timeline Context Tools

| MCP Tool | Purpose | Integration Point | Status |
|----------|---------|-------------------|--------|
| `add_timeline_entry` | Track context at each prompt | Timeline drawer, Evolution Explorer | ✅ Working |
| `get_timeline_summary` | Get recent timeline entries | Timeline drawer | ⚠️ Bug (use `get_timeline_entries`) |
| `get_timeline_entries` | Query timeline history | Timeline drawer, Evolution Explorer | ✅ Working |

### 5.2 Goal Timeline Tools

| MCP Tool | Purpose | Integration Point | Status |
|----------|---------|-------------------|--------|
| `create_goal_timeline_node` | Create goals as timeline nodes | Goal planning panel | ✅ Working |
| `update_goal_progress` | Update goal progress and status | Goal planning panel | ✅ Working |
| `query_goal_timeline` | Query goals with filtering | Goal planning panel, Evolution Explorer | ✅ Working |

---

## 7. UI Component Recommendations

### 6.1 Timeline Components

**Recommended Components:**
1. **Timeline Drawer** (`LucidTimelineDrawer.tsx`)
   - Bottom drawer panel
   - Playback controls
   - Event visualization
   - Event details panel

2. **Timeline Tab** (`TimelineTab.tsx`)
   - Timeline view with filters
   - Evolution Explorer mode toggle
   - Real-time updates
   - MCP integration

3. **Timeline Pane** (`TimelinePane.tsx`)
   - Analytics dashboard
   - Event filtering
   - Chart visualization

### 6.2 Goal Planning Components

**Recommended Components:**
1. **Goal Planning Panel**
   - Right drawer panel
   - Goal list with progress bars
   - Status indicators
   - MCP integration

2. **Goal Timeline Node Visualization**
   - Sequential ordering display
   - Past/present/future states
   - Progress tracking
   - Key results display

### 6.3 Evolution Explorer Components

**Recommended Components:**
1. **Temporal Consciousness Graph** (`TemporalConsciousnessGraph.tsx`)
   - Main content area
   - React Flow graph visualization
   - Why/What/How queries
   - MCP integration

2. **Temporal Graph Builder** (`temporalGraphBuilder.ts`)
   - Graph construction service
   - Node/edge creation
   - Layout calculation

---

## 8. Integration Points with Existing IDE Design

### 7.1 Existing Components

**Already Implemented:**
- ✅ `LucidTimelineDrawer.tsx` - Playback timeline drawer
- ✅ `TimelineTab.tsx` - Timeline tab with Evolution Explorer
- ✅ `TimelinePane.tsx` - Timeline pane with analytics
- ✅ `TemporalConsciousnessGraph.tsx` - Temporal consciousness graph
- ✅ `temporalGraphBuilder.ts` - Graph builder service

**Integration Points:**
- **Bottom Drawer:** Use `LucidTimelineDrawer` for playback timeline
- **Right Drawer:** Add goal planning panel
- **Main Content:** Use `TemporalConsciousnessGraph` for Evolution Explorer
- **MCP Integration:** Use existing MCP tools for data fetching

### 7.2 Enhancement Opportunities

**Timeline Enhancements:**
- **Real-Time Updates:** Enhance MCP polling for real-time updates
- **Event Filtering:** Add more filter options (file, agent, type)
- **Export:** Add export functionality for timeline data

**Goal Planning Enhancements:**
- **Goal Creation:** Add UI for creating new goals
- **Progress Updates:** Add UI for updating goal progress
- **Key Results:** Add UI for managing key results

**Evolution Explorer Enhancements:**
- **Chain Integration:** Complete chain storage/retrieval integration
- **Query Enhancement:** Enhance Why/What/How queries
- **Visualization:** Add more visualization options

---

## 9. Best Practices Summary

### 8.1 Timeline Best Practices

1. **Sequential Ordering:** Use sequence numbers, not dates
2. **Bitemporal Tracking:** Track past/present/future states
3. **Event Types:** Use consistent event types (execution, error, test, etc.)
4. **Real-Time Updates:** Poll MCP tools for real-time updates
5. **Playback Controls:** Provide playback controls for debugging

### 8.2 Goal Planning Best Practices

1. **Goals as Timeline Nodes:** Treat goals as first-class timeline nodes
2. **Sequential Ordering:** Use sequence numbers for temporal ordering
3. **Progress Tracking:** Track progress (0.0 to 1.0) with milestones
4. **Status Management:** Use consistent status types (planned, in_progress, completed, blocked, cancelled)
5. **MCP Integration:** Use MCP tools for goal management

### 8.3 Evolution Explorer Best Practices

1. **Bidirectional Graph:** Connect Timeline ↔ Chain ↔ Goals
2. **Visual Layout:** Use consistent layout (Timeline left, Goals center, Chains right)
3. **Query Interface:** Provide Why/What/How queries
4. **Visual Highlighting:** Highlight query results in graph
5. **MCP Integration:** Fetch data via MCP tools

---

## 10. Citations

1. **Timeline Goals Integration Design:** `knowledge_architecture/AETHER_MEMORY/Timeline_Goals_Integration_Design.md`
2. **Goal Timeline Node:** `packages/timeline_context_system/goal_timeline_node.py`
3. **Lucid Timeline Drawer:** `packages/ide_chat_app/src/components/LucidTimelineDrawer.tsx`
4. **Timeline Tab:** `packages/ide_chat_app/src/components/AgentManagementDashboard/TimelineTab.tsx`
5. **Temporal Consciousness Graph:** `packages/ide_chat_app/src/components/TemporalConsciousnessGraph.tsx`
6. **Temporal Graph Builder:** `packages/ide_chat_app/src/services/temporalGraphBuilder.ts`
7. **Timeline Pane:** `packages/ide_chat_app/src/components/LucidOrchestrator/TimelinePane.tsx`
8. **MCP Tools Integration:** `cursor-addon/docs/MCP_TOOLS_INTEGRATION.md`

---

## 11. Conclusion

This analysis reveals special AIM-OS UI features that should be integrated into the IDE orchestrator:

**Key Features:**
- **Bitemporal Timeline System:** Sequential ordering, playback controls, event tracking
- **Goal Planning System:** Goals as timeline nodes with past/present/future tracking
- **Evolution Explorer:** Bidirectional graph visualization connecting Timeline ↔ Chain ↔ Goals
- **Temporal Consciousness Graph:** Interactive graph with Why/What/How queries
- **Consciousness Explorer:** Real-time consciousness state visualization
- **Memory Browser Enhanced:** CMC memory browser with modality filtering
- **System Status Dashboard:** Real-time AIM-OS system monitoring
- **Lucid Orchestrator Main:** 4-pane orchestrator system
- **Tool Quality Dashboard:** MCP tool quality monitoring
- **MCP Integration:** 9+ MCP tools for timeline, goal, memory, and system management

**Recommendations:**
- Integrate timeline drawer into bottom panel
- Add goal planning panel to right drawer
- Use Evolution Explorer as main content view
- Add Consciousness Explorer to left drawer
- Add Memory Browser to left drawer
- Add System Status Dashboard to left drawer
- Use Lucid Orchestrator Main as main content option
- Add Tool Quality Dashboard to left drawer
- Integrate MCP tools for data fetching
- Enhance existing components with timeline/goal/consciousness features

**Next Steps:**
- Integrate recommendations into ChainSpec design
- Enhance existing IDE components with timeline/goal/consciousness features
- Implement MCP integration for timeline/goal/memory/system data
- Add Evolution Explorer to main content area
- Add Consciousness Explorer, Memory Browser, System Status Dashboard to left drawer

---

**Document Status:** Complete  
**Word Count:** 2,500+ words  
**Citations:** 12 internal citations  
**Ready for:** Integration into ChainSpec and orchestrator design

