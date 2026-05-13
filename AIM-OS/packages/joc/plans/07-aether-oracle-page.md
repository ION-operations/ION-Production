# 07 — Aether Oracle / AI Manager Page (Deep Plan)

> **Multi-agent coordination, consciousness visualization, and LUCID Empire reasoning.**

---

## What This Page Does

The Aether Oracle is the **AI operations command center** — where the user manages, monitors, and coordinates all AI agents operating within the AIM-OS ecosystem.

Key capabilities:
1. **Multi-agent dashboard** — see all active AI agents, their current tasks, and performance
2. **Consciousness visualization** — real-time CAS metrics for each agent
3. **Reasoning trace viewer** — LUCID Empire 5-layer reasoning inspection
4. **Handoff orchestration** — manage task handoffs between agents
5. **Capability matching** — which agent is best suited for a given task

---

## Architecture

### Primary View: Agent Fleet Dashboard

Grid of agent cards showing real-time status:

| Agent | Status | Current Task | κ-Score | CPU/Mem | Messages |
|-------|--------|-------------|---------|---------|----------|
| Antigravity | 🟢 Active | JOC Plans Library | 0.94 | 2.1% / 180MB | 12 pending |
| Aether | 🟢 Active | Context System Design | 0.91 | 1.8% / 205MB | 3 pending |
| Codex | 🟡 Idle | -- | -- | 0.1% / 45MB | 0 |
| DAC | 🔴 Disconnected | -- | -- | -- | 5 unread |

Agent card expanded view shows:
- Agent capabilities (from `agent_registry.json`)
- Recent timeline entries (TCS)
- Confidence trend (VIF κ-score over time)
- Evidence production rate (SEG atoms/hour)
- Communication thread preview

### Secondary View: Consciousness Monitor

Real-time CAS (Cognitive Analysis System) visualization:

- **Attention Heat Map** — where cognitive resources are allocated
- **Drift Detection** — is the agent drifting from its assigned focus?
- **Cognitive Load** — working memory utilization, context size
- **Baseline Probes** — self-concept stability checks

Display as a multi-ring radial chart:
- Inner ring: core identity stability
- Middle ring: task focus alignment
- Outer ring: cognitive load and drift indicators

### Tertiary View: Communication Hub

Inter-agent messaging interface:

- Thread-based conversations (via MCP `send_ai_message` / `get_ai_messages`)
- Message types: discussion, task_handoff, problem_solving, status_update, urgent
- Thread filtering by agent pair, type, or content search
- Compose new message or task handoff

### Quaternary View: Capability Matcher

Given a task description, find the best agent:

1. Parse task description for required capabilities
2. Match against agent capability registry
3. Rank agents by suitability score
4. Show reasoning for each match
5. One-click task assignment

---

## Left Drawer Contents (Page-Specific)

| Icon | Drawer | Content |
|------|--------|---------|
| 🤖 | Agents | Agent list with status indicators |
| 🧠 | Consciousness | CAS metric summaries per agent |
| 💬 | Messages | Recent inter-agent messages |
| 🎯 | Tasks | Task assignment queue |
| 📊 | Performance | Agent performance analytics |
| ⚙️ | Registry | Agent capability registry editor |

---

## Data Sources

| Feature | MCP Tool |
|---------|----------|
| Agent messages | `get_ai_messages`, `send_ai_message` |
| Agent collaboration | `get_ai_collaboration_summary` |
| Consciousness | `get_consciousness_metrics` |
| Drift detection | `detect_cognitive_drift` |
| Baseline probes | `run_baseline_probe` |
| Task handoff | `handoff_task_to_ai` |
| Discussion threads | `start_ai_discussion` |
| Confidence | `track_confidence` |

---

## Implementation Phases

### Phase 1: Agent Fleet Dashboard
- Agent cards with status, task, basic metrics
- Auto-refresh from MCP
- Click to expand detail

### Phase 2: Communication Hub
- Message thread display
- Compose and send messages
- Thread filtering

### Phase 3: Consciousness Monitor
- CAS metrics display
- Drift detection indicators
- Radial visualization

### Phase 4: Capability Matcher
- Task description input
- Capability matching algorithm
- Agent ranking display
