# 04 — Task Manager Page (Deep Plan)

> **"Task manager on steroids"** — the user's words.  
> Grounded in EPIC Orchestration System Design and ChainSpec architecture.

---

## What This Page Actually Represents

Not a Kanban board with sticky notes. A **multi-level orchestration visualization** that mirrors the actual AIM-OS task execution architecture:

- **Epic** → entire IDE orchestration mission
- **Phase** → cohesive outcome block (Research, Architecture, Build, QA, Launch)
- **Workstream** → track-specific flow (API Mediation, IDE UX, Knowledge Ops)
- **Task** → smallest executable unit, bound to capabilities and quality gates

Each level has:
- **Entry gates** — conditions that must be met before starting
- **Exit gates** — validation that must pass before completion
- **Dependencies** — what blocks what
- **Agent assignments** — which AI/human is responsible
- **Evidence targets** — what artifacts must be produced

---

## Source Documents

| Document | Lines | Key Content |
|----------|-------|-------------|
| EPIC_ORCHESTRATION_SYSTEM_DESIGN.md | 472 | ChainSpec schema, quality gates, agent coordination |
| IDE_PROTOTYPES_CONSOLIDATION.md | 536 | Panel production status tracking |
| NORTH_STAR_DIRECTIVE.md | 210 | Vision of what's being built |

---

## Page Architecture

### Primary View: Hierarchy Navigator

```
Epic: IDE Chat + Orchestration
├── Phase: Research (100% ■■■■■■■■■■)
│   ├── Workstream: External Systems Analysis
│   │   ├── Task: Cursor Research ✅ (agent: Rev, κ: 0.92)
│   │   ├── Task: Codex Research ✅ (agent: Codex, κ: 0.88)
│   │   └── Task: Market Analysis ✅ (agent: Sam, κ: 0.91)
│   └── Workstream: Internal Systems Audit
│       ├── Task: AIM-OS Capabilities ✅
│       └── Task: Existing Code Audit ✅
├── Phase: Architecture (75% ■■■■■■■□□□)
│   ├── Workstream: API Mediation Layer
│   │   ├── Task: LLM Adapter Design 🟡 (in-progress)
│   │   └── Task: Quality Enhancement Pipeline ⬜ (blocked)
│   └── ...
└── Phase: Build (0% □□□□□□□□□□)
    └── ...
```

### Secondary View: Dependency Graph

Interactive directed graph (force-directed or hierarchical) showing:
- **Nodes** = Tasks/Phases
- **Edges** = dependency relationships (blocks, requires, supports)
- **Colors** = status (green=done, yellow=active, red=blocked, gray=pending)
- **Click** → task detail panel with agent, κ-score, evidence, gate results

### Tertiary View: Quality Gates Dashboard

From EPIC Orchestration System Design:
- **Task-level gates**: research_artifact_quality (SEG validate), coding_example_density (threshold: 0.9)
- **Phase-level gates**: phase_completeness (coverage check), integration_consistency (HHNI glossary diff)
- **Epic-level gates**: system_integration (AIM-OS system audit), operability (SDF-CVF suite)

Visual: gate cards showing pass/fail status, confidence scores, remediation actions

### Quaternary View: Agent Assignment Matrix

| Agent | Capability | Current Task | Queue Depth | Quality Floor |
|-------|-----------|-------------|-------------|---------------|
| Codex | architecture, implementation | API Design | 3 | 0.88 |
| Aether | system architecture, consciousness | Memory System | 1 | 0.92 |
| Rev | research, documentation | UX Patterns | 2 | 0.90 |

---

## Left Drawer Contents (Page-Specific)

| Icon | Drawer | Content |
|------|--------|---------|
| 📋 | Task Browser | Hierarchical task tree with filters |
| 🚧 | Blockers | Currently blocked tasks with dependency chains |
| ✅ | Gate Status | Quality gate pass/fail overview |
| 👥 | Agents | Agent capability registry and assignment |
| 📊 | Burn Chart | Burndown/burnup progress visualization |
| 🔔 | Alerts | Gate failures, blocked tasks, agent timeouts |

---

## Data Sources (MCP Integration)

| Feature | MCP Tool | Fallback |
|---------|----------|----------|
| Plans | `create_plan`, `get_autonomous_status` | Mock ChainSpec YAML |
| Goals | `query_goal_timeline`, `update_goal_progress` | Mock goal hierarchy |
| Timeline | `get_timeline_summary` | Mock timeline |
| Agent comms | `get_ai_messages`, `send_ai_message` | Mock agent messages |
| Confidence | `track_confidence` | Static scores |

---

## Implementation Phases

### Phase 1: Hierarchy Navigator
- Tree-based collapsible view of Epic → Phase → Workstream → Task
- Status indicators per node (done/active/blocked/pending)
- Progress bars per Phase
- Click → detail panel

### Phase 2: Dependency Graph
- Force-directed or hierarchical graph of task dependencies
- Color-coded by status
- Interactive (drag, zoom, click-to-inspect)
- Critical path highlighting

### Phase 3: Quality Gates Dashboard
- Card-based gate display (task/phase/epic levels)
- Pass/fail indicators with confidence scores
- Remediation action buttons
- Gate history timeline

### Phase 4: Agent Assignment
- Agent registry table
- Capability matching visualization
- Task queue management
- Performance metrics (tasks completed, avg κ-score)
