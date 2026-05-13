---
id: "timeline_goals_integration_T5_quick_reference"
system: "timeline_goals_integration"
component: null
level: "T5"
type: "quick_reference"
title: "Timeline-Goals Integration Quick Reference"
description: "Quick reference guide for Timeline-Goals Integration"
audience: "developers, quick lookup"
confidence_threshold: 0.80
token_cost: 500
word_count: 500
created: "2025-11-05T11:00:00Z"
updated: "2025-11-05T11:00:00Z"
author: "aether"
status: "complete"
tags: ["timeline-goals", "quick-reference", "api", "t0-t6", "transitional"]
dependencies: ["timeline_context_system", "goal_tree"]
related_docs: ["T0_executive.md", "T3_detailed.md", "T4_complete.md"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# Timeline-Goals Integration – T5 Quick Reference

## Quick Start

```python
from packages.timeline_context_system.goal_timeline_manager import GoalTimelineManager

# Initialize
manager = GoalTimelineManager()

# Create goal
goal = manager.create_goal(
    goal_id="OBJ-12",
    name="My Goal",
    description="Goal description",
    priority=GoalPriority.HIGH
)

# Update progress
manager.update_progress("OBJ-12", 0.65, "Milestone achieved")

# Query goals
in_progress = manager.query_goals(status=GoalStatus.IN_PROGRESS)
```

---

## MCP Tools API

### create_goal_timeline_node
```python
create_goal_timeline_node(
    goal_id="OBJ-12",
    name="Goal Name",
    description="Description",
    priority="high",  # critical|high|medium|low
    key_results=[{"name": "KR", "metric": "Metric", "target": "100%"}],
    emotional_context={"primary": "excitement", "intensity": 0.9}
)
```

### update_goal_progress
```python
update_goal_progress(
    goal_id="OBJ-12",
    progress=0.65,  # 0.0 to 1.0
    milestone="Milestone description",
    status="in_progress"  # optional
)
```

### query_goal_timeline
```python
query_goal_timeline(
    status="in_progress",     # optional
    priority="high",          # optional
    sequence_from=1,          # optional
    sequence_to=50            # optional
)
```

---

## Common Patterns

### Pattern 1: Create → Track → Complete
```python
# Create
create_goal_timeline_node(goal_id="NEW", name="New Goal", description="...")

# Track progress
update_goal_progress("NEW", 0.25, "25% done")
update_goal_progress("NEW", 0.50, "Halfway")
update_goal_progress("NEW", 0.75, "Almost there")

# Complete
update_goal_progress("NEW", 1.0, status="completed")
```

### Pattern 2: Query Active Work
```python
# Get all in-progress high-priority goals
active = query_goal_timeline(status="in_progress", priority="high")
```

### Pattern 3: Sync from YAML
```python
# If GOAL_TREE.yaml modified externally
manager = GoalTimelineManager()
manager.sync_from_goal_tree()
```

---

## Data Model Quick Ref

**GoalTimelineNode Fields:**
- `goal_id`: Goal identifier (e.g., "OBJ-01")
- `name`: Goal name
- `status`: planned | in_progress | completed | blocked | cancelled
- `progress`: 0.0 to 1.0
- `created_sequence`: When created (PAST)
- `current_sequence`: Current position (PRESENT)
- `target_sequence`: Target completion (FUTURE)
- `key_results`: List of KeyResult
- `emotional_context`: EmotionalContext
- `artifacts`: List[str] (code/docs references)
- `evidence`: List[str] (validation references)

---

## Status Transitions

```
PLANNED → IN_PROGRESS: Sets started_at
IN_PROGRESS → COMPLETED: Sets actual_completion, progress = 1.0
IN_PROGRESS → BLOCKED: Preserves progress
BLOCKED → IN_PROGRESS: Resumes from saved progress
* → CANCELLED: Sets actual_completion (failed)
```

---

## Sequential Ordering

**Global sequence counter tracks temporal order:**
```
Goal A: sequence 1  → 15 → 30 (created → now → target)
Goal B: sequence 5  → 20 → 25 (created → now → target)
```

**Query by sequence:**
```python
early_goals = query_goal_timeline(sequence_from=1, sequence_to=10)
```

---

## Integration Quick Reference

**CMC:** `cmc.store_atom(mpd_id=goal_id, data=goal.to_dict())`  
**HHNI:** `hhni.index_node(node_id=goal.node_id, content=...)`  
**VIF:** `vif.track_confidence(operation_id=goal_id, confidence_score=...)`  
**YAML:** Automatic bidirectional sync

---

## File Locations

**Code:**
- `packages/timeline_context_system/goal_timeline_node.py` (264 lines)
- `packages/timeline_context_system/goal_timeline_manager.py` (346 lines)
- `packages/timeline_context_system/goal_tree_sync.py` (287 lines)

**Storage:**
- `timeline_goals/goal_{goal_id}.json` (one per goal)
- `goals/GOAL_TREE.yaml` (synced bidirectionally)

**Tests:**
- `packages/timeline_context_system/tests/test_goal_timeline_node.py`

**Docs:**
- `knowledge_architecture/systems/timeline_goals_integration/`

---

## Troubleshooting Quick Fixes

**Sync fails:** `manager.sync_from_goal_tree()` (force re-sync)  
**Goal not found:** Check `manager.goals.keys()` or sync from YAML  
**Sequence drift:** `manager._recalculate_sequences()` (reset counter)  
**YAML conflicts:** `sync.resolve_conflicts(strategy="timeline_wins")`

---

**Full Documentation:** [T0](T0_executive.md) | [T1](T1_overview.md) | [T2](T2_architecture.md) | [T3](T3_detailed.md) | [T4](T4_complete.md)

**Status:** ✅ Production Ready | **Phase:** 2 Complete (Oct 25, 2025) | **Lines:** 610

