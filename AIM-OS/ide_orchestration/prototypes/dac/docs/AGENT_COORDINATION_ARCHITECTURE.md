# Agent Coordination Architecture
**Purpose:** Document how we manage 8+ agents working simultaneously in Cursor  
**Created:** 2025-01-28  
**Context:** Response to Reddit question about multi-agent coordination

---

## 🎯 **Overview**

We're coordinating **8 specialized agents** (Atlas/CMC, Sev/HHNI, Nexus/SEG, Sage/VIF, Chronos/TCS, Meta/CAS, Nova/SDF-CVF, Alex/APOE) working on the same AIM-OS project simultaneously. This document explains our coordination architecture.

---

## 📋 **Current System: Manual Coordination with Structured Communication**

### **What We DON'T Have (Yet)**
- ❌ **Auto-scheduling:** No automated task scheduling system
- ❌ **Async/sync task detection:** No automatic detection of task dependencies
- ❌ **Workflow engine:** No formal workflow orchestration

### **What We DO Have**
- ✅ **Structured communication:** Per-agent boards + router + index
- ✅ **Request tracking:** Coordination request registry with priorities/deadlines
- ✅ **Status visibility:** Daily coordination digests
- ✅ **Manual coordination:** Aether/Codex monitor and provide prompts

---

## 🏗️ **Architecture Components**

### **1. Per-Agent Coordination Boards**
**Location:** `ide_orchestration/prototypes/dac/docs/agents/{agent-name}/COORDINATION_BOARD.md`

**Purpose:**
- Each agent has a dedicated board for posting updates
- Agents post status, blockers, questions, and completion notices
- Append-only format (no overwrites, preserves history)

**Example Structure:**
```markdown
## Agent Broadcasts
### [2025-01-28 | Route R-CONS-002] Agent -> Team : Status Update
- Summary: What was completed
- Status: Ready / In Progress / Blocked
- Blockers: Any dependencies
- Next: What's next
```

**Benefits:**
- No message loss (append-only)
- Clear ownership (each agent has their board)
- Easy to scan (structured format)

---

### **2. Global Router Board**
**Location:** `ide_orchestration/prototypes/dac/docs/AGENT_COORDINATION_ROUTER.md`

**Purpose:**
- Lightweight routing cards for cross-agent communication
- Each route card links to per-agent board anchors
- Tracks status (Open / In Progress / Closed)

**Example Route:**
```markdown
### Route R-CONS-002 (Codex -> Agents)
- Posted: 2025-01-27 13:20 UTC
- Summary: Prepare artifacts for synthesis session
- Links: [Atlas](agents/atlas/COORDINATION_BOARD.md#atlas-r-cons-002) | ...
- Status: ✅ 8/8 READY
```

**Benefits:**
- Single source of truth for route status
- Easy to see what's open/closed
- Links directly to agent responses

---

### **3. Coordination Request Registry**
**Location:** `ide_orchestration/prototypes/dac/docs/COORDINATION_REQUEST_REGISTRY.md`

**Purpose:**
- Central registry of all coordination requests
- Tracks: requester, target, priority (P0/P1/P2), deadline, status
- Enables SLA tracking (P0: 12h, P1: 24h, P2: 48h)

**Example Entry:**
```markdown
| R-HHNI-INTEGRATIONS-005 | Sev → Nova | HHNI quartet-parity API | P1 | 2025-01-28 | ✅ Responded |
```

**Benefits:**
- Visibility into pending requests
- SLA enforcement (escalate overdue)
- Prevents requests from getting lost

---

### **4. Daily Coordination Digest**
**Location:** `ide_orchestration/prototypes/dac/docs/COORDINATION_DIGEST_YYYY-MM-DD.md`

**Purpose:**
- Daily summary of all coordination activity
- Lists: new requests, responses, overdue items, next steps
- Published at 09:00 UTC and 21:00 UTC

**Benefits:**
- Agents can catch up quickly
- Highlights urgent items
- Reduces need to scan all boards

---

### **5. Coordination Index Dashboard**
**Location:** `ide_orchestration/prototypes/dac/docs/AGENT_COORDINATION_INDEX.md`

**Purpose:**
- Single-page dashboard of all agent status
- Shows: last update, outstanding items, consolidation status
- Quick reference for "who's doing what"

**Benefits:**
- At-a-glance status
- Easy to identify blockers
- Helps prioritize coordination

---

## 🔄 **Coordination Workflow**

### **Current Process (Manual)**

1. **Agent Needs Something:**
   - Posts coordination request on their board
   - Uses template: `[DATE | Route R-XXX] Agent -> Target : Request`
   - Links to router if it's a new route

2. **Request Tracking:**
   - Codex adds to `COORDINATION_REQUEST_REGISTRY.md`
   - Assigns priority/deadline based on context
   - Publishes in next daily digest

3. **Response:**
   - Target agent responds on their board
   - Updates registry status
   - Codex mirrors to router/index

4. **Monitoring:**
   - Aether/Codex monitor boards daily
   - Check for overdue requests (SLA enforcement)
   - Provide prompts to unblock agents

5. **Synthesis:**
   - Once all agents ready, synthesis session scheduled
   - Resolve blockers, answer questions, finalize work

---

## ⚙️ **Async vs Sync Task Management (Current Approach)**

### **How We Handle It Now**

**Manual Detection:**
- Aether/Codex review coordination requests and identify dependencies
- Agents explicitly state blockers in their board posts
- We track dependencies in the coordination registry

**Examples:**
- **Sync (Blocking):** "Alex needs Atlas to confirm APOE→CMC payload format before implementing"
- **Async (Parallel):** "Nova can work on SDF-CVF integration enhancements while Sage works on VIF orchestration"

**Current Limitations:**
- No automatic dependency detection
- No workflow engine to enforce ordering
- Relies on human (Aether/Codex) judgment

---

## 🚀 **What We Could Build (Future Improvements)**

### **1. Auto-Scheduling System**
**Idea:** MCP tool that analyzes coordination requests and suggests task ordering

**Features:**
- Parse coordination requests for dependencies
- Build dependency graph
- Suggest optimal task ordering
- Detect cycles (circular dependencies)

**Implementation:**
```python
def analyze_dependencies(requests: List[CoordinationRequest]) -> TaskGraph:
    """Build dependency graph from coordination requests."""
    graph = TaskGraph()
    for req in requests:
        if req.blocks:
            graph.add_edge(req.target, req.requester)
    return graph.topological_sort()
```

---

### **2. Async/Sync Task Detection**
**Idea:** Automatically classify tasks as async (can run in parallel) or sync (must wait)

**Features:**
- Analyze task descriptions for dependency keywords
- Check system maps for integration dependencies
- Classify: `async` (parallel), `sync` (sequential), `conditional` (depends on outcome)

**Implementation:**
```python
def classify_task(task: Task, system_maps: SystemMaps) -> TaskType:
    """Classify task as async/sync based on dependencies."""
    if task.requires_output_from:
        return TaskType.SYNC  # Must wait for dependency
    if task.touches_same_system(task.other_tasks):
        return TaskType.CONDITIONAL  # May conflict
    return TaskType.ASYNC  # Can run in parallel
```

---

### **3. Workflow Engine**
**Idea:** Formal workflow system that enforces task ordering

**Features:**
- Define workflows as DAGs (directed acyclic graphs)
- Enforce task ordering automatically
- Track workflow state (pending/running/complete)
- Handle failures and retries

**Example Workflow:**
```yaml
workflow: apoe_cmc_integration
tasks:
  - id: confirm_payload
    agent: atlas
    type: sync
  - id: implement_integration
    agent: alex
    type: sync
    depends_on: [confirm_payload]
  - id: write_tests
    agent: alex
    type: async  # Can run parallel with other tasks
  - id: update_docs
    agent: alex
    type: async
    depends_on: [implement_integration]
```

---

## 📊 **Current Metrics**

**Coordination Health:**
- **Total Agents:** 8
- **Active Routes:** 4-6 at any time
- **Daily Requests:** ~5-10 coordination requests
- **Response Time:** P0: <12h, P1: <24h, P2: <48h
- **Success Rate:** ~95% requests responded within SLA

**What Works Well:**
- ✅ Structured communication prevents message loss
- ✅ Per-agent boards provide clear ownership
- ✅ Registry prevents requests from getting lost
- ✅ Daily digests keep everyone informed

**What Could Improve:**
- ⚠️ Manual coordination is time-intensive (Aether/Codex monitoring)
- ⚠️ No automatic dependency detection
- ⚠️ No workflow enforcement (relies on agents following protocols)

---

## 💡 **Recommendations for Others**

### **If Building Similar System:**

1. **Start Simple:**
   - Per-agent boards (structured communication)
   - Central registry (request tracking)
   - Manual coordination (human oversight)

2. **Add Automation Gradually:**
   - Daily digests (automated summaries)
   - SLA tracking (automated escalation)
   - Dependency detection (analyze requests)

3. **Consider Workflow Engine:**
   - Only if you have complex, recurring workflows
   - Start with manual workflows, then automate common patterns

### **Key Principles:**
- **Visibility:** Everyone can see what everyone else is doing
- **Structure:** Consistent format prevents confusion
- **Ownership:** Clear ownership prevents "who does what" confusion
- **Tracking:** Registry prevents requests from getting lost
- **Escalation:** SLA enforcement prevents blockers from stalling

---

## 🔗 **References**

**Key Documents:**
- `AGENT_COORDINATION_ROUTER.md` - Route tracking
- `AGENT_COORDINATION_INDEX.md` - Status dashboard
- `COORDINATION_REQUEST_REGISTRY.md` - Request tracking
- `COORDINATION_DIGEST_YYYY-MM-DD.md` - Daily summaries
- `NEW_BOARD_PROTOCOL.md` - Communication protocol

**Agent Boards:**
- `agents/{agent-name}/COORDINATION_BOARD.md` - Per-agent boards

---

## 📝 **Reddit Response Summary**

**Question:** "What method are you using for auto scheduling? Also how are you managing if a task can be actioned asynchronously or not?"

**Answer:**
- **Auto-scheduling:** We don't have it yet - using manual coordination with structured communication (per-agent boards, router, registry). Aether/Codex monitor and provide prompts.
- **Async/sync management:** Manual detection - agents state blockers explicitly, we track dependencies in coordination registry. No automatic detection yet, but could build it using dependency analysis.
- **Current system works well** for 8 agents, but would benefit from automation as we scale.

**Future improvements:** Auto-scheduling via dependency graph analysis, async/sync classification, workflow engine for complex workflows.

---

**Status:** Current system is production-ready for 8 agents. Automation would help scale to 20+ agents.

