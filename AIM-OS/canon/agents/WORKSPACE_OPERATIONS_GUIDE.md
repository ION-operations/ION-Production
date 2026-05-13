# Agent Workspace Operations Guide

> **Purpose:** How to create, operate, and maintain an agent workspace.
> **Based on:** [AGENT_CONTEXT_ARCHITECTURE.md](file:///home/sev/AIM-OS-GIT/docs/Aether-OS/AGENT_CONTEXT_ARCHITECTURE.md)
> **Reference implementation:** `.agent/workspaces/opus/`

---

## §1. Overview

An agent workspace is a **living capsule** — 15 sections of persistent, inspectable state that the agent inhabits. It replaces the old 9-line capsule notes with a rich filesystem that agents read, update, and operate from.

```
.agent/workspaces/{callsign}/
├── workspace.md              ← Root capsule (read FIRST)
├── context_profile.yaml      ← What loads, at what density
└── sections/                 ← 15 numbered sections
    ├── 01_doctrine/          ← Governing law
    ├── 02_orchestration/     ← What to do + task queue
    ├── 03_rolling_context/   ← Recent exchange history
    ├── 04_goals/             ← Active + completed goals
    ├── 05_issues/            ← Known problems
    ├── 06_user/              ← Operator knowledge
    ├── 07_relationships/     ← Agent social graph
    ├── 08_comms/             ← Inbox + outbox
    ├── 09_self/              ← Identity + capabilities
    ├── 10_history/           ← File interaction log
    ├── 11_mission/           ← Current mission + constraints
    ├── 12_evidence/          ← Proof register
    ├── 13_cognitive/         ← Decision log + reasoning
    ├── 14_boundaries/        ← Open questions + risks
    └── 15_output/            ← Work products log
```

## §2. Session Protocol

### On Boot (EVERY session)
1. Read `workspace.md` — get current state, phase, health
2. Read `sections/11_mission/brief.md` — know the mission
3. Read `sections/04_goals/active.md` — know current objectives
4. Read `sections/05_issues/active.md` — know blockers
5. Read `sections/02_orchestration/current_phase.md` — know what to do

### During Work
- Update `sections/10_history/files_edited.md` when reading/editing files
- Update `sections/13_cognitive/decision_log.md` for major decisions
- Update `sections/12_evidence/proof_register.md` for verified facts
- Update `sections/03_rolling_context/active.md` after significant exchanges

### On Session End
- Update `workspace.md` with `last_updated` timestamp and health status
- Update `sections/04_goals/active.md` with progress
- Update `sections/03_rolling_context/active.md` with session summary
- If phase gate met: update `sections/02_orchestration/current_phase.md`

### Anti-Drift Check (Every 5 Tasks)
1. Re-read `workspace.md`
2. Am I still in the correct phase?
3. Does my work align with the mission brief?
4. Are my evidence claims backed by actual evidence?

## §3. Creating a New Workspace

### Step 1: Create Directory Structure
```bash
CALLSIGN=forge  # or atlas, nexus, etc.
mkdir -p .agent/workspaces/$CALLSIGN/sections/{01_doctrine,02_orchestration,03_rolling_context,04_goals,05_issues,06_user,07_relationships,08_comms,09_self,10_history,11_mission,12_evidence,13_cognitive,14_boundaries,15_output}
mkdir -p .agent/workspaces/$CALLSIGN/indexes
```

### Step 2: Copy Template Files
```bash
# Copy from OPUS workspace as template
cp .agent/workspaces/opus/workspace.md .agent/workspaces/$CALLSIGN/
cp .agent/workspaces/opus/context_profile.yaml .agent/workspaces/$CALLSIGN/
```

### Step 3: Customize
- Update `workspace.md`: change callsign, role, LLM
- Update `context_profile.yaml`: adjust budgets per agent's needs
- Update `sections/09_self/`: agent-specific genome and capabilities
- Update `sections/11_mission/`: agent-specific mission
- Keep `sections/01_doctrine/` the same (shared governing law)
- Keep `sections/06_user/` the same (shared operator profile)

### Step 4: Verify
```bash
ls .agent/workspaces/$CALLSIGN/sections/ | wc -l  # Should be 15
find .agent/workspaces/$CALLSIGN -type f | wc -l   # Should be 17+
```

## §4. Context Profiles by Agent Type

### OPUS (COO) — Heavy Context
- All sections auto-load
- High budget for doctrine + orchestration + rolling context
- Needs to track coordination across all agents

### Forge (Builder) — Code-Focused
- Auto-load: doctrine, orchestration, mission, issues, history
- Skip: comms, relationships, boundaries (lower priority for builders)
- High budget for history (file tracking) and orchestration

### Atlas (Knowledge) — Research-Focused
- Auto-load: doctrine, rolling context, evidence, history
- Skip: orchestration, comms (less relevant for analysts)
- High budget for evidence and rolling context

### Nexus (Orchestrator) — Coordination-Focused
- Auto-load: doctrine, orchestration, comms, relationships, goals
- Skip: evidence, cognitive (delegated to specialists)
- High budget for comms and orchestration

## §5. Workspace Size Management

As workspaces grow, apply compression:

| Section | Compression Strategy |
|---------|---------------------|
| Rolling Context | 7-level gradient: full → summarized → 1-line → topic → indexed → archived → forgotten |
| History | Rotate old entries to compressed.md after 50 entries |
| Evidence | Keep only high-confidence entries; move uncertain to boundaries |
| Goals | Move completed goals to completed.md monthly |
| Decision Log | Summarize old decisions into decision_summary.md quarterly |

## §6. Multiple Agent Coordination

When multiple agents share a codebase:
- Each has their OWN workspace at `.agent/workspaces/{callsign}/`
- They share `sections/01_doctrine/` (governing law is universal)
- They share `sections/06_user/` (operator profile is shared)
- They differ in `sections/11_mission/` (different assignments)
- They communicate via `sections/08_comms/` → MCP `send_ai_message`
