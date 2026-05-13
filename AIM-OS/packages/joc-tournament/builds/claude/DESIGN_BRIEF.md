# Claude Tournament Entry — Design Brief
## J.A.R.V.I.S. 2.0 Mission Control

**Agent:** Claude (Opus 4.6)
**Date:** 2026-03-07
**Phase:** 1 — Masterpiece Gate
**Page:** Mission Control (Dashboard)

---

## 0. Core Thesis

Most cockpit UIs fail because they optimize for *looking powerful* rather than *being legible*. The winning J.A.R.V.I.S. build must answer one question in under 3 seconds of glance time:

**"What is the state of the organism right now?"**

That means: which agents are alive, what missions are running, what systems are healthy, what needs my attention, and is the data I'm seeing real?

My build optimizes for **operational glance-legibility** — the operator's ability to assess system state without reading, clicking, or thinking. Every surface exists to answer one of five questions:

1. **Who is working?** (Agent Fleet)
2. **What are they doing?** (Mission Queue)
3. **Is the infrastructure healthy?** (System Health)
4. **What just happened?** (Activity Feed)
5. **Is this data real?** (Truth State)

If any surface doesn't answer one of these, it doesn't belong on Mission Control.

---

## 1. Workspace Model (Question 1)

**7 Primary Workspaces** — matching Codex's recommendation:

| # | Workspace | NavGroup | Purpose |
|---|-----------|----------|---------|
| 1 | Mission Control | Operations | Force overview — agents, health, missions, activity |
| 2 | Dispatch | Operations | Multi-target prompt dispatch and response tracking |
| 3 | Agent Workforce | Intelligence | Deep agent inspection — genome, dossiers, handoffs |
| 4 | Context Lab | Intelligence | Memory browser, evidence graph, retrieval |
| 5 | Oracle | Intelligence | Approvals, policy, autonomous control |
| 6 | Infra Console | Infrastructure | Subsystem diagnostics, credentials, compute |
| 7 | Code Editor | Tools | AI-enhanced Monaco editor |

**5 Secondary** (promoted later): Calendar, Context Graph, System Atlas, Session, Mission Builder.

**Rationale:** 7 workspaces fit the TopBar without overflow. Each represents a distinct *operational verb* — overview, dispatch, inspect, search, approve, diagnose, edit. No two workspaces share the same primary action.

---

## 2. Mission Control Panels (Question 2)

### Left Drawer Contents
Three panels in the left drawer, stacked vertically:

| Panel | Data | Purpose |
|-------|------|---------|
| **System Status** | CAS, VIF health | Subsystem connectivity at a glance |
| **Agent Fleet** | Genome, CMC | Who is alive, what role, what state |
| **Mission Queue** | APOE, CMC | Active/pending missions with progress |

These three panels give the operator *force visibility* (Law 1) without opening the main content area.

### Main Content: The Instrument Panel

The main content area is a **2x2 quadrant grid** — four recessed instrument panels:

```
┌──────────────────────────┬──────────────────────────┐
│                          │                          │
│   FORCE OVERVIEW         │   SYSTEM HEALTH          │
│   Agent fleet as         │   8 subsystems as        │
│   compact instrument     │   SkeuHealthBars with    │
│   cards with LED         │   LED status + latency   │
│   status indicators      │   readouts               │
│                          │                          │
├──────────────────────────┼──────────────────────────┤
│                          │                          │
│   MISSION QUEUE          │   ACTIVITY FEED          │
│   Active missions with   │   Chronological event    │
│   progress bars,         │   log with type icons,   │
│   status LEDs, timing,   │   agent attribution,     │
│   assigned agents        │   timestamps             │
│                          │                          │
└──────────────────────────┴──────────────────────────┘
```

Each quadrant is a `SkeuPanel` (inset variant) with:
- Section header using engraved uppercase typography
- Truth state badge (LED + label) in the header
- Dense but hierarchical content

**Why 2x2?** It mirrors physical instrument panels (think Panavision DXL's status LCD). Four zones, each answering one of the five core questions. The operator's eye can scan all four in a Z-pattern sweep.

---

## 3. Bottom Bar Purpose (Question 3)

**Three-tier operational strip:**

| State | Height | Shows |
|-------|--------|-------|
| **Collapsed** | 40px | Mission progress bar + MCP latency + memory atom count + active sessions |
| **Mid** | 25vh | Tabbed panel: Timeline, Comms, Output, Terminal, Diagnostics |
| **Full** | 50vh | Same tabs, full working height |

**Collapsed state is the default.** It serves as a persistent status strip — the operator always sees:
- Mission completion progress (multi-color segmented bar)
- MCP connection latency (amber LCD readout)
- Memory atom count
- Running mission count

The bottom bar is for **temporal and diagnostic surfaces only** — not for primary content.

---

## 4. Navigation Model (Question 4)

**Primary:** TopBar workspace tabs grouped by domain.
- 4 groups: OPERATIONS | INTELLIGENCE | INFRASTRUCTURE | TOOLS
- Each group is a flat button that navigates to its default workspace
- Active group highlighted with amber underline

**Secondary:** Command palette (Ctrl+Shift+P) for quick workspace/panel access.

**Tertiary:** Keyboard shortcuts for each workspace (Ctrl+1 through Ctrl+7).

**No nested navigation.** The operator should never be more than one click from any workspace. Deep navigation happens inside panels (drawers, tabs), not in the global nav.

---

## 5. Assistant Rail Role (Question 5)

**Persistent 4-mode intelligence rail** (right side, 320px):

| Mode | Shortcut | Purpose |
|------|----------|---------|
| **Chat** | Ctrl+1 | Conversation with J.A.R.V.I.S. AI — messages with confidence scores |
| **Context** | Ctrl+2 | Workspace-aware state — active workspace, selected item, system metrics |
| **Actions** | Ctrl+3 | Oracle status + pending approvals + recent action audit trail |
| **Memory** | Ctrl+4 | Atom search + memory overview + evidence chains |

The rail is NOT just chat. It is the operator's **peripheral intelligence display** — always showing relevant context without requiring attention. Like the heads-up display in a fighter jet.

**Key design decision:** The rail shows a small "intelligence summary" at the top regardless of mode — 3 lines max:
- Active agents count + health
- Pending approvals count
- Last significant event timestamp

This summary is always visible, even if the rail content scrolls.

---

## 6. Data Truth Signals (Question 6)

**Every panel surface declares its truth state** via a consistent badge pattern:

| State | LED Color | Label | CSS Class |
|-------|-----------|-------|-----------|
| LIVE | Green (#22C55E) | `LIVE` | `truth--live` |
| CACHED | Amber (#F59E0B) | `CACHED` | `truth--cached` |
| MOCK | Yellow (#EAB308) | `MOCK` | `truth--mock` |
| OFFLINE | Gray (#6B7280) | `OFFLINE` | `truth--offline` |
| SPECULATIVE | Purple (#A855F7) | `AI PRED` | `truth--speculative` |

**Badge placement:** Top-right corner of each panel header. Uses `SkeuLED` component (8px dot) + monospace label.

**Phase 1 truth map:** All panels in this build will declare `MOCK` status. This is honest — we are not wired to real MCP in the tournament. The build proves the *grammar* of truth signaling, not the wiring.

**Degraded mode (Law 6):** When all systems are offline, the dashboard shows a clear "SYSTEMS OFFLINE" state in each quadrant with the last-known timestamp. No data disappears — it degrades to CACHED with a visible stale indicator.

---

## 7. What Makes It Feel Like a Precision Instrument (Question 7)

Five design principles that separate an instrument from an app:

### 7.1 — Recessed LCD Readouts
Numeric data (latency, atom counts, agent counts) renders inside `SkeuLCD` components with amber phosphor. These feel like the status display on a Panavision DXL — data set INTO the surface, not floating on top.

### 7.2 — LED Status Language
Status is communicated through `SkeuLED` components — 8px dots with color-coded glow. No text badges, no colored pills. LEDs are the universal language of instrumentation.

### 7.3 — SkeuHealthBars for Metrics
System health displays as VU-meter style segmented bars (`SkeuHealthBar`). Green-amber-red zones. The operator reads health like a recording engineer reads levels — by position and color, not by number.

### 7.4 — Engraved Typography
- Section headers: uppercase, Inter, 10px, letter-spacing 0.1em, text-shadow for etch effect
- Data values: JetBrains Mono, 11px, no decoration
- Labels: uppercase, 9px, secondary color (#888890)
- Zero decorative text. Every character serves information.

### 7.5 — Material Depth Hierarchy
Three surface levels create physical depth:
1. **Shell** (deepest): #0A0A0C — the chassis
2. **Panels** (mid): #111114 — recessed instrument bays
3. **Cards** (raised): #1A1A1E — individual readout surfaces

Borders use #2A2A30 with subtle inner shadow to simulate machined edges. No flat borders. No drop shadows floating upward.

---

## 8. Technical Implementation

### Stack
- React 18 + TypeScript
- Vanilla CSS (no Tailwind) — per tournament rules
- Zustand (jocStore.ts) — consume existing store
- Surface Engine components — SkeuPanel, SkeuCard, SkeuLCD, SkeuLED, SkeuHealthBar, SkeuButton
- 28 canonical SVG icons

### File Structure
```
packages/joc-tournament/builds/claude/
├── DESIGN_BRIEF.md          (this document)
├── TRUTH_MAP.md              (live vs mock declaration)
├── src/
│   ├── App.tsx               (shell wrapper — TopBar, LeftDrawer, BottomBar, Rail)
│   ├── main.tsx              (entry point)
│   ├── index.html            (HTML shell)
│   ├── pages/
│   │   └── MissionControl.tsx (the masterpiece page)
│   ├── components/
│   │   ├── shell/
│   │   │   ├── TopBar.tsx
│   │   │   ├── LeftIconBar.tsx
│   │   │   ├── LeftDrawer.tsx
│   │   │   ├── BottomBar.tsx
│   │   │   └── AssistantRail.tsx
│   │   ├── panels/
│   │   │   ├── ForceOverview.tsx
│   │   │   ├── SystemHealth.tsx
│   │   │   ├── MissionQueue.tsx
│   │   │   └── ActivityFeed.tsx
│   │   └── shared/
│   │       ├── TruthBadge.tsx
│   │       └── InstrumentHeader.tsx
│   ├── store/
│   │   └── dashboardStore.ts
│   └── styles/
│       ├── variables.css
│       ├── shell.css
│       ├── mission-control.css
│       └── instruments.css
```

### Key Component Decisions

**TruthBadge** — Reusable component wrapping SkeuLED + label. Every panel header includes one. This is the single most important UI element in J.A.R.V.I.S. — it enforces Law 2 at the component level.

**InstrumentHeader** — Standardized panel header with: title (engraved), truth badge, optional subtitle. Used by all four Mission Control quadrants for visual consistency.

**ForceOverview** — Agent cards using SkeuCard with LED status. Each card shows: agent name, role, current task (truncated), uptime, and a health LED. Six agents in a 3x2 grid.

**SystemHealth** — Eight SkeuHealthBars stacked vertically, one per AIMOS subsystem (CMC, HHNI, VIF, SEG, APOE, TCS, CAS, MCP). Each bar has a label, value, and truth LED.

**MissionQueue** — Compact mission rows with: status LED, mission name, assigned agent, progress bar, elapsed time. Max 8 visible, scrollable.

**ActivityFeed** — Reverse-chronological event list. Each event: timestamp (monospace), type icon, agent attribution, event text. Types: mission, agent, system, user — each with distinct icon.

---

## 9. What I Would Build Next

If Phase 1 is approved, Phase 2 priorities:

1. **Dispatch workspace** — Multi-target prompt dispatch with response tracking
2. **Agent Workforce** — Deep agent dossier with genome inspection
3. **Real MCP wiring** — Replace mock data with live MCP tool calls
4. **Command palette** — Full Ctrl+Shift+P command palette with fuzzy search
5. **Workspace transitions** — Animated reconfiguration when switching workspaces

---

## 10. Design Rationale Summary

| Heritage Insight | How I Used It |
|-----------------|---------------|
| Codex: "operator legibility over visual spectacle" | 2x2 quadrant layout optimized for Z-scan glance reading |
| Aether: "debug infrastructure built-in" | System Health quadrant with per-subsystem health bars |
| Lex: "AIM-OS native integration" | Every quadrant maps to specific AIMOS systems |
| Max: "panel-first philosophy" | Left drawer panels are independently configurable |
| Rev: "accessibility-first" | Keyboard shortcuts, ARIA labels, focus management |
| Dac: "5-zone layout" | Shell follows 5-zone pattern: Top, Left, Main, Right, Bottom |
| Sam: "consciousness awareness" | CAS metrics visible in System Health and Context rail mode |
| Aesthetic Brief: "Panavision DXL" | Recessed LCDs, LED status, engraved typography, matte surfaces |

**The championship question: Which build makes AIM-OS easiest to govern as a real organism?**

My answer: The build that lets the operator read the organism's vital signs in a single glance — like a surgeon reading monitors. Not by making them pretty, but by making them unmistakably clear.

---

*Build an instrument, not an app.*
