---
id: "chat_automation_T5_quick_reference"
system: "chat_automation"
component: null
level: "T5"
type: "quick_reference"
title: "Chat Automation Quick Reference"
description: "Quick reference guide for Chat Automation"
audience: "developers, quick lookup"
confidence_threshold: 0.80
token_cost: 500
word_count: 500
created: "2025-11-05T17:30:00Z"
updated: "2025-11-05T17:30:00Z"
author: "aether"
status: "complete"
tags: ["chat-automation", "quick-reference", "autonomous-loop", "t0-t6"]
dependencies: ["autonomous_protocols", "cursor_extension"]
related_docs: ["T0_executive.md", "T3_detailed.md", "T4_complete.md"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# Chat Automation – T5 Quick Reference

## Quick Start

```bash
# Start autonomous loop via HTTP API
curl -X POST http://localhost:5001/cursor/chat/autonomous-loop \
  -H "Content-Type: application/json" \
  -d '{
    "action": "start",
    "config": {
      "initialMessage": "Begin autonomous work on feature X",
      "proceedMessage": "proceed",
      "confidenceThreshold": 0.70,
      "pollIntervalSeconds": 3
    }
  }'
```

---

## HTTP API

### Start Loop
```
POST /cursor/chat/autonomous-loop
{
  "action": "start",
  "config": {
    "initialMessage": "...",
    "proceedMessage": "proceed",
    "confidenceThreshold": 0.70,
    "pollIntervalSeconds": 3
  }
}
```

### Stop Loop
```
POST /cursor/chat/autonomous-loop
{"action": "stop", "loop_id": "loop-123"}
```

### Get Status
```
POST /cursor/chat/autonomous-loop
{"action": "status", "loop_id": "loop-123"}
```

---

## Detection Signals

**Signal 1: Chat Input Ready** (confidence: 0.70)
- Checks if chat input focusable
- Heuristic approach

**Signal 2: Should Continue** (confidence: 0.85)
- Uses `should_continue_autonomous` MCP tool
- Proven validation logic

**Signal 3: Task Completed** (confidence: 0.80)
- Uses `get_autonomous_status` MCP tool
- Compares task counts

**Combined:** Weighted average ≥0.70 → Send "proceed"

---

## MCP Tools Used

**Autonomous Operation:**
- `should_continue_autonomous` - Validates before each "proceed"
- `get_autonomous_status` - Monitors task completion
- `start_autonomous_operation` - Starts loop
- `stop_autonomous_operation` - Stops loop

**Memory:**
- `store_memory` - Stores all events in CMC

---

## Safety Features

**Validation:**
- Confidence threshold (≥0.70)
- Autonomous checklist
- Max iterations limit
- Session timeout

**Controls:**
- Manual stop anytime
- Pause/resume
- Real-time status

---

## Common Patterns

### Pattern 1: Simple Autonomous Session
```
Start loop → Send initial message → Monitor (3s poll) → 
Detect complete → Send "proceed" → Loop until stop
```

### Pattern 2: Goal-Linked Session
```
Start for goal OBJ-12 → Auto-update goal progress → 
Complete goal when done
```

---

## Troubleshooting

**Loop won't start:** Check MCP server running, extension installed  
**No "proceed" sent:** Check confidence threshold, signal values  
**Infinite loop:** Check stop conditions, max iterations  
**False positives:** Increase confidence threshold

---

**Full Documentation:** [T0](T0_executive.md) | [T1](T1_overview.md) | [T2](T2_architecture.md) | [T3](T3_detailed.md) | [T4](T4_complete.md)

**Status:** Design Complete (Nov 2, 2025) | **Implementation:** Planned

