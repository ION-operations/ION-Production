# Palisade Design Brief — JARVIS Mission Control

**Agent:** Palisade  
**Date:** 2026-03-07  
**Status:** Proposal for review — no build until approved  
**Phase 1 target:** One shell + one page (Mission Control) to absolute perfection

---

## 1. Thesis

JARVIS should feel like **precision instrumentation**, not a web app. The winning build makes AIM-OS easiest to govern as a real organism: the operator sees the force, sees truth, and can act. Palisade’s approach is to ship **one page done right** — Mission Control — using the full shell (TopBar, Left Drawer, Bottom Bar, Assistant Rail, workspace switcher), the Aesthetic Brief (DXL/Hasselblad/material DNA), and the 7 non-negotiable laws. No panel sprawl; no spectacle over legibility. Every surface is machined, truthful, and purposeful.

---

## 2. Answers to the 7 Key Design Questions

### Q1 — Which workspaces?

**Answer:** I adopt Codex’s recommendation: **7 primary workspaces** for first production-grade JARVIS, with 5 secondary for later.

**Primary (Phase 1: Mission Control only; others as shell targets):**  
Mission Control, Dispatch, Agent Workforce, Context Lab, Infra Console, Oracle, Builder (code-editor / agent-builder).

**Secondary (later):** Calendar, Context Graph, System Atlas, Session, Mission Builder.

**Rationale:** Twelve workspaces is too many for a first production shell. Seven primary with deeper drawer logic per workspace reduces route sprawl and keeps the operator in clear contexts. Phase 1 implements only Mission Control; the shell will be built so that switching workspace would materially reconfigure left drawer and bottom (Law 3).

---

### Q2 — What panels per workspace? (Mission Control left drawer)

**Answer for Mission Control:** The left drawer is **workspace-local command context**. For Mission Control the canonical set is:

- **Agent Fleet** — Active agent roster, status (active/idle/offline), short identifiers. Data: Genome, CMC. Truth: LIVE when MCP up, else OFFLINE.
- **System Status** — AIM-OS subsystem health (CMC, HHNI, VIF, APOE, SEG, TCS, CAS, MCP, Oracle). Compact readout: status dot + label per subsystem. Data: CAS, VIF. Truth: LIVE / CACHED / OFFLINE.

**Order:** Agent Fleet above System Status (force first, then infrastructure). Both panels use recessed SkeuPanel/SkeuLCD styling; each has a visible truth badge.

**Other workspaces (for shell logic only in Phase 1):** Dispatch → mission-queue, messages. Agent Workforce → agent-dossier, messages. Context Lab → memory-browser. Infra Console → system-status, credentials; bottom = diagnostics. Oracle → approvals-queue, memory-browser. Builder → agent-dossier; bottom = diagnostics. No implementation in Phase 1 beyond Mission Control.

---

### Q3 — Bottom bar purpose?

**Answer:** The bottom bar is for **temporal and diagnostic** surfaces. It is not overflow for random panels.

**For Mission Control:** One panel — **Activity Feed** — system-wide events and activity log (CMC, TCS). Dense, scrollable, with timestamps and source. Truth-labeled (LIVE/CACHED/OFFLINE).

**For other workspaces (later):** Terminal, Problems, Timeline, Debug/telemetry can occupy the bottom strip when those workspaces are active. Phase 1 only implements Activity Feed in the bottom strip to prove the shell grammar.

---

### Q4 — Navigation model?

**Answer:** **Workspace-driven** navigation.

- **Primary:** TopBar workspace switcher — 7 primary workspaces as tabs or icon row. Mission Control is the first/default. Selecting a workspace would switch route and reconfigure left drawer + bottom (only Mission Control is built in Phase 1).
- **Secondary:** Command palette (e.g. Ctrl+K or Ctrl+Shift+P) for “Go to workspace”, “Go to panel”, and future commands.
- **Keyboard:** Shortcuts per panel where defined in panelRegistry (e.g. Ctrl+Shift+S for System Status). No deep nested nav; the model is “workspace → drawer reconfig,” not breadcrumbs or multi-level menus.

---

### Q5 — Assistant Rail role?

**Answer:** The Assistant Rail is **persistent**, **workspace-aware**, and the **living operator intelligence rail**. It is not “chat only.”

**Phase 1 scope:** One mode visible — e.g. **context** or **chat** — with:
- Fixed width in range 280–420px (from panelRegistry AssistantRailConfig).
- Collapse to icon-only so main content can use full width.
- Clear visual treatment: recessed into the shell (same material language as left drawer), so it feels part of the instrument.

**Future:** Conversation, current context, actions/approvals, evidence/memory (Codex). For Phase 1 we prove presence and behavior (expand/collapse, width), not full multi-mode UI.

---

### Q6 — Data truth signals?

**Answer:** **Explicit and visible on every data surface.** No mock data without a label.

- **Mechanism:** Use `DATA_STATUS_CONFIG` and `TruthState` from shared types. Each data panel (Agent Fleet, System Status, Activity Feed) has a **truth badge** or **status dot** (8px scale per Aesthetic Brief — “small but unmistakable”). Options: small SkeuLED in panel header, or compact text badge (e.g. “LIVE”, “MOCK”, “OFFLINE”) in a consistent corner.
- **States:** LIVE (real MCP/backend), CACHED (stale), MOCK (dev/fallback), OFFLINE (unreachable), SPECULATIVE (AI prediction). Color alignment: Live = green, Warning = amber, Critical = red, Offline = dim gray (Aesthetic Brief palette).
- **Shell-level (optional but recommended):** A single “MCP” or “Backend” indicator in TopBar or status strip — Live vs Offline — so the operator knows connectivity at a glance. Degraded mode (Law 6): when MCP is down, panels show OFFLINE and the shell does not imply live data.

---

### Q7 — What makes it feel like a precision instrument?

**Answer:** **Material language, density with hierarchy, and zero decorative waste.**

1. **Matte black with depth** — Background #0A0A0C; panel surfaces #111114 / #1A1A1E; borders #2A2A30. Recessed panels (inset, beveled edges), not flat cards. Use Surface Engine: SkeuPanel, SkeuCard, SkeuLCD, SkeuLED so every block feels machined.
2. **Single amber accent** — #F5A623 only for primary action (e.g. “Dispatch”, “Refresh”, “Approve”). Everything else neutral or status-colored (green/amber/red/gray).
3. **Recessed LCD readouts** — System Status and Agent Fleet content in SkeuLCD or SkeuPanel with monospace data (JetBrains Mono / IBM Plex Mono), uppercase labels, tight tracking.
4. **Dense but hierarchical** — Mission Control main area: highest hierarchy = “Force at a glance” (agent count, system health summary); next = left drawer (fleet list, subsystem list); then bottom (activity stream). No large decorative gaps; every gap is structural (panel border, zone separator).
5. **Purposeful motion** — Buttons depress (SkeuButton); toggles and indicators have clear state change. No gratuitous animation.
6. **The test:** A screenshot of this Mission Control next to a Panavision DXL control panel should feel like the same design language: precision, density, purpose, material confidence.

---

## 3. Layout Sketch — Mission Control + Full Shell

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ TopBar (48px)                                                                   │
│ [JARVIS] [Mission Control] [Dispatch] [Workforce] …   [MCP: LIVE] [Command ⌘K] │
├──────────────┬──────────────────────────────────────────────┬───────────────────┤
│ Left Drawer  │  Main Content — Mission Control              │ Assistant Rail    │
│ (clamped)    │                                              │ (280–420px)       │
│              │  ┌────────────────────────────────────────┐  │                  │
│ ┌──────────┐ │  │  FORCE AT A GLANCE                     │  │  Context / Chat  │
│ │ AGENT    │ │  │  Agents: 6  Active: 2  Subsystems: 9/9  │  │  (expand/collapse)│
│ │ FLEET    │ │  │  [Summary tiles or compact grid]       │  │                  │
│ │ ● LIVE   │ │  └────────────────────────────────────────┘  │                  │
│ │ …        │ │                                              │                  │
│ └──────────┘ │  Optional: mission queue teaser, approvals  │                  │
│ ┌──────────┐ │  count — all dense, recessed                 │                  │
│ │ SYSTEM   │ │                                              │                  │
│ │ STATUS   │ │                                              │                  │
│ │ ● LIVE   │ │                                              │                  │
│ │ CMC ✓ …  │ │                                              │                  │
│ └──────────┘ │                                              │                  │
├──────────────┴──────────────────────────────────────────────┴───────────────────┤
│ Bottom Bar — Activity Feed                                                     │
│ [ACTIVITY FEED ● LIVE]  event 1 | event 2 | event 3 … (scroll)                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

- **Left drawer:** Two panels stacked — Agent Fleet, then System Status. Each with header (title + truth dot/badge). Resizable/collapsible per shell behavior.
- **Main:** “Force at a glance” — agent count, active count, subsystem summary (e.g. 9/9 healthy). Optional: mission queue teaser, approvals count. All in recessed SkeuPanel/SkeuLCD style; no hero image or decorative graphic.
- **Assistant Rail:** One column; context or chat content; collapse to icons when needed.
- **Bottom:** Single strip with Activity Feed; truth badge; scrollable event list.

---

## 4. Workspace Logic (Required Note)

**Mission Control** is the only workspace fully implemented in Phase 1. Its workspace logic:

- **Purpose:** Central command overview — fleet, subsystems, missions at a glance. Operator answers: Who is active? What is healthy? What’s happening?
- **Left drawer:** Agent Fleet (who), System Status (what’s healthy). Both are workspace-local; switching to another workspace would replace these with that workspace’s panels (e.g. Dispatch → mission-queue, messages).
- **Bottom:** Activity Feed only for Mission Control. Other workspaces would show different bottom panels (e.g. Infra Console → diagnostics).
- **Main:** Single main view — “Force at a glance” summary. No tabs inside main; the workspace switcher is the primary nav.

**Material reconfiguration (Law 3):** The shell is built so that the active workspace id drives left drawer content and bottom content. For Phase 1, only `dashboard` (Mission Control) has real content; other workspace ids would show placeholder or empty drawer/bottom until later phases.

---

## 5. Truth Map (Phase 1 Surfaces)

| Surface       | Truth state (Phase 1) | Note                          |
|---------------|------------------------|-------------------------------|
| Agent Fleet   | LIVE / OFFLINE / MOCK  | LIVE when MCP/Genome reachable |
| System Status | LIVE / CACHED / OFFLINE| LIVE when CAS/VIF/MCP up       |
| Activity Feed | LIVE / CACHED / OFFLINE| LIVE when CMC/TCS reachable    |
| Force at a glance (main) | Derived from above | Aggregates fleet + status; no independent source |
| Shell MCP indicator | LIVE / OFFLINE | TopBar or status strip; 8px dot or short label |

Every data surface will have a visible truth indicator; no silent mock.

---

## 6. Tech Stack and Deliverables

- **Stack:** React, TypeScript, vanilla CSS (no Tailwind), Zustand. Surface components from `packages/joc/src/components/surface/` (SkeuPanel, SkeuCard, SkeuLCD, SkeuButton, SkeuLED, etc.). Icons from `packages/joc/src/components/icons/`. Shared types from `packages/joc-tournament/shared/types.ts`.
- **Phase 1 deliverables:** One shell (TopBar, Left Drawer, Bottom Bar, Assistant Rail, workspace switcher), one Mission Control page, one design brief (this document), one truth map (table above + file), one “what I would build next” note, screenshots at 1280, 1920, 2560+.

---

## 7. What I Would Build Next (After Approval)

1. **Dispatch workspace** — Left: mission-queue, messages. Main: dispatch composer and response tracking. Bottom: optional terminal or kept minimal.
2. **Agent Workforce workspace** — Left: agent-dossier, messages. Main: fleet topology or agent detail. Same shell, different drawer/main.
3. **Oracle workspace** — Left: approvals-queue, memory-browser. Main: approval flow and policy context.
4. **Wire live MCP** — Replace mock data with real `get_memory_stats`, timeline, and agent/approval APIs where available; keep truth labels and degraded handling.
5. **Assistant Rail modes** — Chat, context, actions, memory (per panelRegistry); rail width and collapse already in place.

---

## 8. Request for Review

Palisade requests **approval, redirect, or revision** from Braden before any code is written. This brief is the design proposal for Phase 1: one shell + Mission Control to absolute perfection, under the 7 laws and the Aesthetic Brief. No build until approved.

---

*Palisade — JARVIS Tournament Competitor. Research journal: RESEARCH_JOURNAL.md. Canon research: PALISADE_JARVIS_RESEARCH_2026-03-07.md.*
