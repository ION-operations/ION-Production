---
id: "temporal_consciousness_viz_T5_quick_reference"
system: "temporal_consciousness_visualization"
component: null
level: "T5"
type: "quick_reference"
title: "Temporal Consciousness Visualization Quick Reference"
description: "Quick reference guide"
audience: "developers, quick lookup"
confidence_threshold: 0.80
token_cost: 500
word_count: 500
created: "2025-11-05T20:15:00Z"
updated: "2025-11-05T20:15:00Z"
author: "aether"
status: "complete"
tags: ["temporal-consciousness", "quick-reference", "react-flow", "t0-t6"]
dependencies: ["timeline_goals_integration", "prompt_chains"]
related_docs: ["T0_executive.md", "T3_detailed.md", "T4_complete.md"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# Temporal Consciousness Visualization – T5 Quick Reference

## Quick Start

```typescript
import { TemporalConsciousnessVisualization } from '@/components/TemporalConsciousnessVisualization';

// Render visualization
<TemporalConsciousnessVisualization
    enableRealTime={true}
    refreshIntervalSeconds={5}
    initialLayout="temporal"
    enableQueryInterface={true}
/>
```

---

## Node Types

**Timeline (Blue):** Past events, sequence-ordered, links via `executed_via_chain_id`  
**Goal (Green):** Current objectives, progress tracking, links via `related_chain_ids`  
**Chain (Orange):** Future plans, execution workflows, links via `goal_id`

---

## Edge Types

**Temporal (Gray):** Timeline → Timeline (chronological)  
**Execution (Red Dashed):** Timeline → Chain (which chain executed this)  
**Production (Purple):** Chain → Timeline (what chain produced)  
**Planning (Teal):** Goal ↔ Chain (bidirectional working relationship)

---

## Query Interface

**Why?** → Trace backwards: Timeline → Chain → Goal (understand causation)  
**What?** → See connected goals (current focus)  
**How?** → Explore forward: Goal → Chains → Timeline (see plans and results)

---

## Layout Options

**Temporal:** Vertical timeline (top to bottom = past to future)  
**Force-Directed:** Organic (connected nodes attract)  
**Hierarchical:** Tree structure (North Star → Systems → Components)

---

## API Endpoints

```
GET /api/timeline/entries?limit=100
GET /api/goals/timeline?status=all
GET /api/chains?tier=1
```

---

## Common Patterns

### Pattern 1: Load and Display
```typescript
const { nodes, edges } = await GraphBuilder.buildGraph(data);
<ReactFlow nodes={nodes} edges={edges} />
```

### Pattern 2: Query Execution
```typescript
const result = await QueryExecutor.executeWhyQuery(nodeId, graph);
// Highlight result nodes
```

---

**Full Documentation:** [T0](T0_executive.md) | [T1](T1_overview.md) | [T2](T2_architecture.md) | [T3](T3_detailed.md) | [T4](T4_complete.md)

**Status:** Design Complete, Partial Implementation

