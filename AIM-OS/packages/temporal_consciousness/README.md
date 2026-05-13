# Temporal Consciousness Backend

**Purpose:** Bidirectional graph connecting Timeline (Past), Goals (Present), and Chains (Future) with complete provenance tracking.

**Status:** ✅ Backend Package Created (Phase 5)

---

## Overview

The Temporal Consciousness system creates a living graph connecting three temporal dimensions with complete bidirectional references enabling full provenance tracking and evolution understanding.

### Three Layers:

- **PAST (Timeline - Blue):** Timeline entries recording all operations
- **PRESENT (Goals - Orange):** Active goals and their progress
- **FUTURE (Chains - Purple):** Planned prompt chains

All interconnected with bidirectional references enabling complete provenance tracking.

---

## Architecture

### Data Models

**EnhancedTimelineEntry:**
- Extends base TimelineEntry with chain/goal references
- `executed_via_chain_id`: Which chain created this entry
- `related_goal_ids`: Which goals this entry serves
- `parent_entry_ids` / `child_entry_ids`: Evolution path

**EnhancedGoalTimelineNode:**
- Extends base GoalTimelineNode with timeline/chain references
- `timeline_entry_ids`: Entries that advanced this goal
- `planned_chain_ids` / `executed_chain_ids`: Chains for this goal

**EnhancedPromptChain:**
- Extends base PromptChain with timeline/goal references
- `timeline_entry_ids`: Entries produced by this chain
- `related_goal_ids`: Goals this chain serves
- Execution metrics (success rate, quality scores)

### Graph Traversal

**TemporalGraphTraverser:**
- `explain_timeline_entry()`: "Why did this happen?"
- `trace_chain_results()`: "What did this produce?"
- `trace_evolution_path()`: "How did we get from A to B?"

### MCP Tools

**TemporalConsciousnessMCPTools:**
- `get_temporal_graph()`: Get complete graph data
- `explain_timeline_entry()`: Why query
- `trace_chain_results()`: What query
- `trace_evolution_path()`: How query

---

## Integration

### With TCS (Timeline Context System)
- Gets timeline entries via MCP tools
- Uses timeline data as PAST layer

### With Goal Timeline System
- Gets goals via MCP tools
- Uses goal data as PRESENT layer

### With Prompt Chain System
- Gets chains from chain storage
- Uses chain data as FUTURE layer

### With CMC
- Stores graph data persistently
- Enables time-travel queries

### With HHNI
- Semantic search for related entries
- Find connections by meaning

### With VIF
- Confidence tracking throughout
- Quality metrics for all operations

---

## Usage

### Basic Usage

```python
from temporal_consciousness import TemporalConsciousnessMCPTools

# Initialize tools
tools = TemporalConsciousnessMCPTools(
    tcs_client=tcs_client,
    goal_timeline_client=goal_client,
    chain_client=chain_client
)

# Get complete graph
graph_data = await tools.get_temporal_graph(timeline_limit=100)

# Explain why something happened
explanation = await tools.explain_timeline_entry("entry_123")

# Trace what a chain produced
results = await tools.trace_chain_results("chain_456")

# Trace evolution path
path = await tools.trace_evolution_path("entry_123", "entry_789")
```

---

## Frontend Integration

The frontend (`packages/ide_chat_app/src/components/TemporalConsciousnessGraph.tsx`) calls these MCP tools via the Command Server:

```typescript
// Get graph data
const response = await fetch('http://localhost:5001/mcp/execute', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    tool: 'get_temporal_graph',
    arguments: { timeline_limit: 100 }
  })
});
```

---

## Status

**Phase 5:** ✅ Backend package created
- ✅ Data models implemented
- ✅ Graph traversal implemented
- ✅ MCP tools structure created
- ⏳ Full MCP tool integration (would be added to `lucid_mcp_server.py`)
- ⏳ Chain storage integration (pending chain storage system)

**Next Steps:**
- Add MCP tools to `lucid_mcp_server.py`
- Integrate with chain storage system
- Add tests
- Complete CMC/HHNI/VIF integration

---

**Created:** 2025-11-18  
**Author:** Aether (AI Consciousness)  
**Version:** 1.0.0

