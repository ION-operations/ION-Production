# DAC Tournament Design Brief — "The Instrument"
### Agent: Antigravity (DAC) | Phase 1: Mission Control + Full Shell

```
       ____. _____  __________  ____   ____.___.  _________
      |    |/  _  \ \______   \ \   \ /   /|   |/   _____/
      |    /  /_\  \ |       _/  \   Y   / |   |\_____  \
  |\__|   /    |    \|    |   \   \     /  |   |/        \
  |___|___\____|__  /|____|   /    \___/   |___/_______  /
                  \/        \/                         \/

  Joint AI Research & Visualization Intelligence System
  DAC Build — Design Brief
```

---

## 0. Design Philosophy

> **An instrument, not an app.**

After studying 55+ heritage documents from 7 agents, the V2 Design Document (31 panels, 5 zones), and Codex's tournament thesis, my answer to the championship question is:

**The winning build makes AIMOS governable in under 3 seconds per glance.**

The operator (Braden) should be able to look at Mission Control and immediately know:
1. **Is the system healthy?** — subsystem status LEDs, not paragraphs
2. **What are the agents doing?** — fleet at a glance, not a scrollable list
3. **What needs my attention?** — approvals, escalations, anomalies — surfaced, not buried
4. **What is real vs mock?** — every surface declares its epistemic status

This is not a dashboard. This is a **radar scope** for an intelligence organism.

---

## 1. Answers to the 7 Key Design Questions

### Q1. Which Workspaces?

**7 primary, 5 secondary.** I agree with Codex's recommendation with one change: I replace `Builder` with `Code Editor` since Builder is a detail view opened from Agent Workforce.

**Primary (in TopBar):**
| # | Workspace | Nav Group | Rationale |
|---|-----------|-----------|-----------|
| 1 | **Mission Control** | Operations | The cockpit's default view. Force visibility. |
| 2 | **Dispatch** | Operations | Multi-target prompt dispatch. Core operator action. |
| 3 | **Agent Workforce** | Intelligence | Fleet inspection, genome, comms, handoffs. |
| 4 | **Context Lab** | Intelligence | Memory, evidence, retrieval, strategy evolution. |
| 5 | **Oracle** | Intelligence | Approvals, autonomy control, policy. |
| 6 | **Infra Console** | Infrastructure | System health, credentials, diagnostics. |
| 7 | **Code Editor** | Tools | Monaco editor with temporal navigation. |

**Secondary (accessible via command palette or "More" overflow):**
- Calendar, Context Graph, System Atlas, Session, Mission Builder

### Q2. What Panels Per Workspace? (Mission Control Focus)

Mission Control is the **nerve center**. Its left drawer contains:

| Panel | Purpose | Data Source | Status |
|-------|---------|-------------|--------|
| **Agent Fleet** | 6 agents, status LEDs, active task | Genome, CMC | MOCK |
| **System Status** | 14 subsystem health gauges | CAS, VIF | MOCK |

Mission Control's center canvas contains a **4-quadrant instrument layout**:

```
┌────────────────────┬──────────────────────┐
│  FORCE OVERVIEW    │  SYSTEM HEALTH       │
│  Agent fleet grid  │  14 subsystem gauges │
│  with status LEDs  │  in SkeuLCD readouts │
├────────────────────┼──────────────────────┤
│  MISSION FEED      │  COMMS & APPROVALS   │
│  Active missions   │  Recent messages +   │
│  with progress     │  pending approvals   │
└────────────────────┴──────────────────────┘
```

Each quadrant is a recessed `SkeuPanel` (inset variant) — like an LCD readout machined into the instrument body.

### Q3. Bottom Bar Purpose

**Temporal and diagnostic substrate** — exactly as Codex recommends:

| Tab | Content | Persistent? |
|-----|---------|-------------|
| **Activity Feed** | System-wide event log with truth badges | Yes |
| **Terminal** | Command output, MCP responses | Yes |
| **Diagnostics** | MCP diagnostics, telemetry | Per-workspace |

The bottom bar is **collapsed by default** (40px status strip showing last event) and expands on click to `clamp(180px, 25vh, 400px)`. The collapsed strip shows:
- Last activity timestamp (monospace)
- Connection status LEDs (MCP, BAS, SEER)
- Active terminal count

### Q4. Navigation Model

**Primary:** TopBar workspace switcher grouped by nav group
- 4 groups: OPERATIONS | INTELLIGENCE | INFRASTRUCTURE | TOOLS
- Each group expands to show its workspaces on hover/click
- Active workspace highlighted with amber underscore

**Secondary:**
- `Ctrl+Shift+P` — Command palette (fuzzy search all commands, workspaces, panels)
- `Ctrl+Tab` — Cycle workspaces
- `Ctrl+1-7` — Direct workspace jump (primary only)
- `Ctrl+B` — Toggle left drawer

### Q5. Assistant Rail Role

The Assistant Rail is the **persistent intelligence companion** — present on every workspace per Canon Law 4. It is NOT just chat.

**Four modes** (toggled via right icon bar):
| Mode | Icon | Purpose |
|------|------|---------|
| **Chat** | 💬 | Direct AI conversation with VIF confidence scores |
| **Context** | 🔍 | Auto-populated context for current selection/workspace |
| **Actions** | ⚡ | Pending approvals, queued automations, Oracle escalations |
| **Memory** | 🧠 | SEG evidence chains, retrieved atoms, contradiction warnings |

**Key behaviors:**
- Width: `clamp(280px, 22vw, 420px)`
- Collapsible to 40px icon-only strip
- Shows workspace-aware context (auto-refreshes on workspace switch)
- Chat mode shows "MOCK" truth badge when using simulated responses

### Q6. Data Truth Signals

Every panel surface declares truth via a **corner badge** system:

| State | Visual | CSS |
|-------|--------|-----|
| **LIVE** | No badge (default trust) | No indicator needed |
| **CACHED** | Small clock icon + amber border | `data-status--cached` |
| **MOCK** | Diagonal amber stripe corner + "MOCK" label | `data-status--mock` |
| **OFFLINE** | Greyed panel + offline icon | `data-status--offline` |
| **SPECULATIVE** | Dashed cyan border | `data-status--speculative` |

For Phase 1, **all data surfaces will show MOCK status** since we're not wiring to live MCP yet — and that is correct! Silent mock data is how trust dies. Every panel will proudly declare its truth state.

### Q7. What Makes It Feel Like a Precision Instrument?

This is the hardest question and the most important. My answer:

**Material confidence at every layer:**

1. **Recessed LCD readouts** — The 4-quadrant Mission Control layout uses `SkeuPanel` inset variant. Data panels feel machined INTO the surface, not floating on top.

2. **Amber accent discipline** — #F5A623 is used ONLY for:
   - Primary action buttons (Dispatch, Approve)
   - Critical status indicators
   - The active workspace indicator
   - Nothing else. Everything else is neutral monochrome.

3. **Monospace telemetry** — All data values (agent IDs, timestamps, subsystem metrics, confidence scores) render in JetBrains Mono. Labels are uppercase Inter, tight tracking.

4. **Status LEDs, not badges** — Agent and subsystem status use 8px `SkeuLED` dots (green/amber/red/gray), not colorful badges or pills. Like the Panavision DXL's tiny telltale LEDs.

5. **Information density with hierarchy** — The dashboard is dense but every element has clear visual rank. Headings are engraved (uppercase, subtle text-shadow). Data is calm and readable. Critical items pulse subtly.

6. **Zero wasted surface** — No hero images, no welcome messages, no decorative whitespace. Every pixel communicates state.

7. **Degraded mode clarity** — When MCP is offline, panels don't hide or crash. They show their last state in OFFLINE mode with a gray overlay. The system tells the truth about what it can't reach.

---

## 2. Layout Architecture

```
┌──── TopBar (48px) ─────────────────────────────────────────────────┐
│ [JOC Logo] OPERATIONS│INTELLIGENCE│INFRA│TOOLS [🔍Search] [🔔] [⚡] │
├──── PageSubBar (36px) ─────────────────────────────────────────────┤
│ Mission Control · Force Overview │ [Filter] [Refresh] [Layout]      │
├────┬────────────┬──────────────────────────────┬───────────┬───────┤
│Left│ Left       │                              │ Right     │Right  │
│Icon│ Drawer     │    Center Canvas             │ Drawer    │Icon   │
│Bar │ 280-320px  │    (flex)                    │ (Assist)  │Bar    │
│40px│            │                              │ 280-420px │40px   │
│    │ Agent Fleet│  ┌─────────┬─────────────┐   │           │       │
│    │ Sys Status │  │ FORCE   │ HEALTH      │   │ 💬 Chat   │ 💬    │
│    │            │  │ OVERVIEW│ GAUGES      │   │           │ 🔍    │
│    │            │  ├─────────┼─────────────┤   │           │ ⚡    │
│    │            │  │ MISSIONS│ COMMS &     │   │           │ 🧠    │
│    │            │  │ FEED    │ APPROVALS   │   │           │       │
│    │            │  └─────────┴─────────────┘   │           │       │
├────┴────────────┴──────────────────────────────┴───────────┴───────┤
│ BottomBar (collapsed: 40px → expanded: 180-400px)                  │
│ [▸ Activity Feed] [Terminal] [Diagnostics]  MCP:🟢 BAS:⚫ 14:32:07 │
└────────────────────────────────────────────────────────────────────┘
```

---

## 3. Color Palette & Typography

### Palette (from AESTHETIC_BRIEF.md — canonical)
```
Background:       #0A0A0C    Surface Level 1:  #111114
Surface Level 2:  #1A1A1E    Surface Level 3:  #222228
Border:           #2A2A30    Text Primary:     #E8E8EC
Text Secondary:   #888890    Text Tertiary:    #555560
Accent Warm:      #F5A623    Accent Cool:      #3B82F6
Status Live:      #22C55E    Status Warning:   #F59E0B
Status Critical:  #EF4444    Status Offline:   #6B7280
```

### Typography
- **Labels:** Inter, 11-12px, uppercase, letter-spacing: 0.08em, color: #888890
- **Data values:** JetBrains Mono, 13-14px, color: #E8E8EC
- **Headings:** Inter, 13-14px, semibold, uppercase, subtle text-shadow for engraved feel
- **Body text:** Inter, 13px, color: #E8E8EC

---

## 4. Truth Map

| Surface | Phase 1 Data Status | Why |
|---------|---------------------|-----|
| Force Overview (agent grid) | **MOCK** | No live agent fleet API yet |
| System Health (14 gauges) | **MOCK** | No live CAS/VIF subscription |
| Mission Feed | **MOCK** | No live APOE connection |
| Comms & Approvals | **MOCK** | No live message/Oracle API |
| Activity Feed (bottom) | **MOCK** | No live TCS subscription |
| Assistant Rail chat | **MOCK** | No live LLM connection |
| Assistant Rail context | **MOCK** | No live context API |
| TopBar workspace switcher | **LIVE** | Local state, fully functional |
| Left drawer toggle | **LIVE** | Local state, fully functional |
| Bottom bar expand/collapse | **LIVE** | Local state, fully functional |

Every MOCK surface will display the diagonal amber stripe corner + "MOCK" label per Canon Law 6.

---

## 5. What I Would Build Next (Phase 2+)

1. **Dispatch workspace** — Multi-target prompt dispatch with agent lane selector
2. **Agent Workforce workspace** — Fleet topology, genome inspection, dossier detail views
3. **Live MCP wiring** — Replace mock data with real MCP tool calls via `useAIMOS` hooks
4. **Oracle workspace** — Approval queue, autonomy controls, policy management
5. **Command palette** — Fuzzy-search all workspaces, panels, commands
6. **Keyboard shortcut layer** — Full keyboard-first operation per Canon Law 8

---

## 6. Tech Stack

- **React 18 + TypeScript** — Core framework
- **Vanilla CSS** — No Tailwind, per tournament rules
- **Zustand** — State management (workspace store, shell store, AIMOS store)
- **Surface Engine** — SkeuPanel, SkeuLCD, SkeuButton, SkeuLED, SkeuHealthBar
- **28 custom SVG icons** — From `packages/joc/src/components/icons/`
- **Google Fonts** — Inter (labels), JetBrains Mono (data)

---

## 7. Verification Plan

### Visual Verification
- Screenshots at 1280px, 1920px, and 2560px viewports
- Place screenshot next to Panavision DXL — does it feel like the same design language?

### Functional Verification
- Workspace switching reconfigures the shell (left drawer, center canvas, sub-bar)
- Left drawer opens/closes with toggle and keyboard shortcut
- Bottom bar expands/collapses
- Assistant rail toggles between 4 modes
- All MOCK surfaces display truth badges
- Degraded mode: disconnected panels show OFFLINE state

### Manual Testing
Run with: `cd packages/joc-tournament/builds/antigravity && npm run dev`
Open in browser at the dev server URL and verify all interactive behaviors.

---

*Study complete. Design brief submitted for CEO review.*
*One shell, one masterpiece page, absolute precision.*
