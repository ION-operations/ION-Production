# Joint Operations Center — Master Vision

**Author:** Claude Opus 4.6  
**Architect:** Braden  
**Date:** 2026-03-02  
**Status:** 🎯 DESIGN DOCUMENT — Vision, architecture, and rationale for the JOC  
**Canon Compliance:** OPUS Visual Interface Canon v2.0  

---

## What the JOC Is

The Joint Operations Center is **not a browser.** It is not a tab manager. It is not another app launcher.

The JOC is the **central nervous system of your computing life** — a unified command surface where:

- Your AI subscriptions (ChatGPT, Gemini, Claude, Perplexity, and whatever comes next) become **operational assets** under your orchestrated control
- Your agent team (Aether, Codex1, Codex2, Claude Opus 4.6, and whatever comes next) can dispatch to and receive from those AIs autonomously
- Your hundreds of projects, branches, and experiments have a **living catalog** that tracks itself
- The 80% of your time currently spent copy-pasting between agents drops to zero

> *"I no longer interact with a window. I interact with a mission dashboard that monitors, dispatches, and synthesizes across all my AI assets."*

---

## The Fundamental Shift

### Today (Manual Orchestration)

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│ ChatGPT  │     │  Gemini  │     │  Claude   │
│  (tab)   │     │  (tab)   │     │  (tab)    │
└────┬─────┘     └────┬─────┘     └────┬──────┘
     │                │                │
     └────────┬───────┘                │
              │                        │
         ┌────▼─────┐                  │
         │  BRADEN  │◄─────────────────┘
         │ (manual  │
         │ copy/    │──► Cursor IDE ──► Agents
         │ paste)   │
         └──────────┘

Problem: Braden IS the integration layer.
80% of time = copying between agents.
20% of time = compiling context packages.
```

### Tomorrow (JOC Orchestration)

```
                    ┌─────────────────────────┐
                    │    JOINT OPERATIONS      │
                    │       CENTER             │
                    │                          │
                    │  ┌─────────────────────┐ │
                    │  │  Mission Dashboard  │ │
                    │  │  ● Active AIs       │ │
                    │  │  ● Running tasks    │ │
                    │  │  ● Results feed     │ │
                    │  │  ● Agent comms      │ │
                    │  └─────────────────────┘ │
                    │            │              │
            ┌───────┴────────┬──┴──────┬───────┴───────┐
            │                │         │               │
     ┌──────▼──────┐ ┌──────▼────┐ ┌──▼──────┐ ┌──────▼──────┐
     │ ChatGPT     │ │ Gemini    │ │ Claude  │ │ Perplexity  │
     │ Driver      │ │ Driver    │ │ Driver  │ │ Driver      │
     │ ● inject    │ │ ● inject  │ │ ● API   │ │ ● inject    │
     │ ● extract   │ │ ● extract │ │ ● API   │ │ ● extract   │
     │ ● status    │ │ ● status  │ │         │ │ ● status    │
     └──────┬──────┘ └──────┬────┘ └──┬──────┘ └──────┬──────┘
            │                │         │               │
     ┌──────▼──────┐ ┌──────▼────┐ ┌──▼──────┐ ┌──────▼──────┐
     │  Browser    │ │  Browser  │ │  API    │ │  Browser    │
     │  Session    │ │  Session  │ │  Direct │ │  Session    │
     │  (logged in)│ │ (logged in│ │         │ │ (logged in) │
     └─────────────┘ └───────────┘ └─────────┘ └─────────────┘

Result: Braden expresses intent. JOC dispatches.
Time copying = 0%. Time at the helm = 100%.
```

---

## The Five Pillars

The JOC is built on five pillars, each a visual system — not a settings panel.

### Pillar 1: The Mission Dashboard (The Central View)

This is what you see when you open the JOC. Not a blank browser. Not a list of bookmarks. A **live operations surface**.

```
┌─────────────────────────────────────────────────────────────────┐
│  ◉ JOINT OPERATIONS CENTER                    ▪ ▪ ▪  ─  □  ✕   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─ AI FLEET STATUS ──────────────────────────────────────────┐ │
│  │                                                             │ │
│  │  ◉ ChatGPT Pro     ● ACTIVE     Session: 4h 23m           │ │
│  │    └─ Running: "Analyze wave physics architecture"          │ │
│  │                                                             │ │
│  │  ◉ Gemini Ultra     ● ACTIVE     Session: 2h 15m           │ │
│  │    └─ Idle (ready for dispatch)                             │ │
│  │                                                             │ │
│  │  ◉ Perplexity Pro   ○ SLEEPING   Last: 45m ago             │ │
│  │    └─ Last: "Research WebGPU compute shader limits"         │ │
│  │                                                             │ │
│  │  ◉ Claude.ai        ○ SLEEPING   Last: 1h ago              │ │
│  │    └─ Session saved (23 cookies, 4 conversations)           │ │
│  │                                                             │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌─ ACTIVE MISSIONS ─────────────────────────────────────────┐ │
│  │                                                             │ │
│  │  #M-042  "Compare WGSL particle limits across AIs"         │ │
│  │   ├─ ChatGPT: ████████░░ 80% — extracting response         │ │
│  │   ├─ Gemini:  ██████████ DONE — 3.2K tokens captured       │ │
│  │   └─ Status: Synthesizing... ETA 30s                        │ │
│  │                                                             │ │
│  │  #M-041  "Browser system runbook validation"                │ │
│  │   └─ ██████████ COMPLETE — report in /docs/                 │ │
│  │                                                             │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌─ AGENT COMMS ─────────────────────────────────────────────┐ │
│  │  [MCP Message Bus]                                         │ │
│  │  09:17 Aether → Opus: "Standardize sender ID..."          │ │
│  │  09:19 Opus → Aether: "Acknowledged. Standing by..."       │ │
│  │  09:22 Codex2 → Aether: "Capsule engine tests passing"    │ │
│  │                                                             │ │
│  │  [━━━━━━━━━━━━━━━━━━━━━━━━━━━━] Type to all agents...     │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌─ QUICK DISPATCH ───────┐  ┌─ RESULTS FEED ───────────────┐ │
│  │                         │  │                               │ │
│  │  Ask All AIs:           │  │  09:15 ChatGPT returned       │ │
│  │  [━━━━━━━━━━━━━━━━━━━] │  │    2.8K response on particle  │ │
│  │                         │  │    limits. [View] [Route]      │ │
│  │  ○ ChatGPT  ○ Gemini   │  │                               │ │
│  │  ○ Claude   ○ Perplexity│  │  09:10 Gemini returned        │ │
│  │  ○ All                  │  │    comparison table. [View]    │ │
│  │                         │  │    [Send to Codex]             │ │
│  │  [Dispatch ▶]           │  │                               │ │
│  └─────────────────────────┘  └───────────────────────────────┘ │
│                                                                 │
│  ─── [🗺️ Dashboard] [🌐 Sessions] [📋 Missions] [💬 Comms]     │
│      [📦 Projects] [🔧 Drivers] [📊 Metrics] ──────────────── │
└─────────────────────────────────────────────────────────────────┘
```

**Key design principles applied:**
- NOT a launcher. It's a live display.
- AI Fleet Status is a **visual instrument** — colored status indicators (◉ green, ● amber, ○ gray) show state at a glance, not a table of numbers
- Active Missions show **progress bars as visual feedback**, not numeric percentages
- Agent Comms is **live** — you don't check messages, you see them stream in
- Quick Dispatch is the 🔑 feature — type once, send to one or many AIs

---

### Pillar 2: The Session Manager (AI Fleet Control)

Each AI subscription gets a **session card** — a visual representation of its state, not a list of cookies.

```
┌─ SESSION: ChatGPT Pro ──────────────────────────────────────────┐
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                [LIVE VIEWPORT]                            │   │
│  │                                                          │   │
│  │    ChatGPT conversation visible here                     │   │
│  │    (CDP viewport or screenshot cycle)                    │   │
│  │                                                          │   │
│  │    ┌───────────────────────────────────────────┐         │   │
│  │    │ ▶ Inject prompt here                      │         │   │
│  │    └───────────────────────────────────────────┘         │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  Session Health: ████████████████████ 100%                       │
│  ├─ Login: ✅ Valid (cookies fresh 45m ago)                      │
│  ├─ Quota: ~150/300 messages remaining (GPT-4o)                 │
│  ├─ Memory: 12 items in ChatGPT memory                          │
│  └─ Threads: 847 conversations                                  │
│                                                                  │
│  ┌─ Quick Actions ──────────────────────────────────────────┐   │
│  │  [Inject Prompt]  [Extract Response]  [New Thread]        │   │
│  │  [Save Session]   [Refresh Session]   [Open in Browser]   │   │
│  └───────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─ Memory Sync ────────────────────────────────────────────┐   │
│  │  ChatGPT Memory → AIM-OS Memory                          │   │
│  │  Last synced: 2h ago    [Sync Now]                        │   │
│  │  12 items in ChatGPT | 847 atoms in CMC                   │   │
│  │  [View Diff] [Merge →] [← Push]                          │   │
│  └───────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

**The session card is a visual instrument:**
- Health bar (not a number) shows session state
- Live viewport shows what the AI is doing right now
- Memory sync shows the relationship between the AI's memory and yours
- Quick Actions are one-click, not multi-step workflows

---

### Pillar 3: The Dispatch Engine (Multi-AI Orchestration)

This is where the 80% copy-paste cost goes to zero.

```
┌─ NEW MISSION ────────────────────────────────────────────────────┐
│                                                                   │
│  Mission: "Compare WGSL compute shader limits for particle sims" │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────────┐│
│  │                                                              ││
│  │  [PROMPT EDITOR]                                             ││
│  │                                                              ││
│  │  What are the practical limits of WebGPU compute shaders     ││
│  │  for real-time particle simulation? Compare:                 ││
│  │  - Maximum workgroup sizes across GPU vendors                ││
│  │  - Buffer binding limits                                     ││
│  │  - Practical particle counts before frame drops              ││
│  │  - Strategies for 1M+ particle systems                       ││
│  │                                                              ││
│  └──────────────────────────────────────────────────────────────┘│
│                                                                   │
│  ┌─ Dispatch Targets ──────────────────────────────────────────┐ │
│  │                                                              │ │
│  │  ◉ ChatGPT Pro     [✓]  "Best for code examples"            │ │
│  │  ◉ Gemini Ultra    [✓]  "Best for research synthesis"       │ │
│  │  ◉ Perplexity Pro  [✓]  "Best for web-sourced data"        │ │
│  │  ○ Claude.ai       [ ]  "API route available"                │ │
│  │                                                              │ │
│  │  Strategy: [Parallel ▼]                                      │ │
│  │    ○ Parallel — Send to all simultaneously                   │ │
│  │    ○ Sequential — Use each response to refine the next       │ │
│  │    ○ Consensus — Send to all, highlight agreements           │ │
│  │    ○ Debate — Have AIs critique each other's responses       │ │
│  │                                                              │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌─ Context Attachments ───────────────────────────────────────┐ │
│  │  📁 Auto-compiled from project:                              │ │
│  │     simulator.js (2.8K) | updateGrid.wgsl (1.2K)            │ │
│  │     g2p.wgsl (800B) | respawn.wgsl (600B)                    │ │
│  │  📏 Total: 5.4K tokens | Budget: 32K per AI                 │ │
│  │  [Add Files] [Auto-Context from Project] [Clear]             │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌─ Post-Processing ──────────────────────────────────────────┐ │
│  │  After all responses:                                        │ │
│  │  [✓] Synthesize into comparison table                        │ │
│  │  [✓] Route synthesis to Aether for review                    │ │
│  │  [ ] Save to project docs                                    │ │
│  │  [ ] Feed back into AIM-OS memory                            │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  [━━━━━━━━━ LAUNCH MISSION ━━━━━━━━━]                           │
└──────────────────────────────────────────────────────────────────┘
```

**This is not a form. This is a mission planning instrument:**
- The prompt editor is the input, and it's the central focus
- Dispatch targets let you choose which AIs get the task
- Strategy selection is a **meaningful choice** not a dropdown someone ignores
- Context attachments **auto-compile** from the active project — the 20% context management time drops to zero
- Post-processing defines what happens AFTER responses come back — the automation loop closes

---

### Pillar 4: The Results Synthesizer

When missions complete, the raw responses need to become **actionable knowledge**.

```
┌─ MISSION RESULTS: #M-042 ──────────────────────────────────────┐
│                                                                  │
│  "Compare WGSL compute shader limits for particle sims"          │
│                                                                  │
│  ┌─ SYNTHESIS ──────────────────────────────────────────────┐   │
│  │                                                          │   │
│  │  All 3 AIs agree on:                                     │   │
│  │  • Max workgroup size: 256 (widely supported)            │   │
│  │  • Buffer limit: 8 storage buffers per pipeline          │   │
│  │  • Practical ceiling: ~500K particles at 60fps (discrete)│   │
│  │                                                          │   │
│  │  Disagreements:                                          │   │
│  │  • ChatGPT says 1M possible with spatial hashing         │   │
│  │  • Gemini says 1M requires instanced rendering fallback  │   │
│  │  • Perplexity cites a 2025 paper achieving 2M with tiles │   │
│  │                                                          │   │
│  │  Confidence: ████████░░ 82%  Sources: 7 unique           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─ RAW RESPONSES (expandable) ─────────────────────────────┐   │
│  │  ▶ ChatGPT (3.2K tokens, 34s)                            │   │
│  │  ▶ Gemini (2.8K tokens, 28s)                              │   │
│  │  ▶ Perplexity (4.1K tokens, 42s — 4 web sources)         │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─ ACTIONS ────────────────────────────────────────────────┐   │
│  │  [Route to Aether]  [Save to Docs]  [New Follow-up]      │   │
│  │  [Store in Memory]  [Compare Visually]  [Export]          │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

---

### Pillar 5: The Project Catalog (Living Index)

This answers the question: "Where is that app I built 3 months ago? Which branch was it on? Did I finish it?"

```
┌─ PROJECT CATALOG ──────────────────────────────────────────────┐
│                                                                 │
│  Search: [━━━━━━━━━━━━━━━━━━━━━━━━━━━━━]  Filter: [Active ▼]  │
│                                                                 │
│  ┌─ Active Projects (27) ──────────────────────────────────────┐│
│  │                                                              ││
│  │  ◉ Pool Ocean / Water Sim              last: 2h ago         ││
│  │    └─ branch: spillover-mechanics      status: IN PROGRESS  ││
│  │    └─ 49 visual editors | WGSL | MLS-MPM                    ││
│  │                                                              ││
│  │  ◉ AIM-OS / Browser Automation         last: 30m ago        ││
│  │    └─ branch: main                     status: COMPLETE     ││
│  │    └─ Phases 0-4 delivered by Opus                           ││
│  │                                                              ││
│  │  ◉ SAIOS Kernel                        last: 2d ago         ││
│  │    └─ branch: main                     status: BUILD ISSUES ││
│  │    └─ thiserror-impl compilation error                       ││
│  │                                                              ││
│  │  ◉ Planet Engine / Procedural Worlds   last: 5d ago         ││
│  │    └─ branch: biome-system             status: PAUSED       ││
│  │                                                              ││
│  └──────────────────────────────────────────────────────────────┘│
│                                                                 │
│  ┌─ Dormant Projects (143) ────────────────────────────────────┐│
│  │  [Show dormant projects...]                                  ││
│  │  ⚠ 12 projects have uncommitted changes                     ││
│  │  ⚠ 8 projects have running dev servers (orphaned?)           ││
│  └──────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

---

## Design System

### Canon Compliance

This JOC follows the Opus Visual Interface Canon:

| Canon Principle | JOC Application |
|----------------|-----------------|
| **Prime Directive** | No generic sliders. Session health is a visual bar, not a number. Mission progress is a fill-bar, not a percentage. AI status is a colored indicator, not a text label. |
| **Direct Manipulation** | Drag to reorder mission priority. Drag to assign context files. Click AI cards to dispatch. |
| **ROM Zones** | Session health: green (>80%), amber (50-80%), red (<50%). Token budgets: comfort/strain/danger. |
| **Live Preview** | Mission progress updates in real-time. Session viewport shows live browser state. Agent comms stream in. |
| **3-Layer Architecture** | Layer 1: Bottom tab bar (Dashboard/Sessions/Missions/Comms/Projects). Layer 2: Sub-navigation within each view. Layer 3: Visual instruments as primary interface. Layer 4: Advanced settings hidden by default. |

### Color Palette

Following the canon's dark theme foundation:

| Element | Color | Hex |
|---------|-------|-----|
| Background (deep) | Near-black blue | `#0a0a15` |
| Background (surface) | Dark indigo | `#1a1a2e` |
| Background (elevated) | Muted blue | `#252545` |
| Primary accent | Electric cyan | `#00d4ff` |
| Secondary accent | Soft blue | `#60a5fa` |
| Success | Emerald | `#4CAF50` |
| Warning | Amber | `#FF9800` |
| Danger | Coral red | `#f44336` |
| Text (primary) | Soft white | `#e0e0e0` |
| Text (secondary) | Muted gray | `#888888` |
| Text (hint) | Dim gray | `#666666` |
| Borders | Dark blue | `#2a2a4a` |

### Typography

- **System UI stack**: `system-ui, -apple-system, 'Segoe UI', sans-serif`
- **Headers**: 13px, bold, accent color
- **Body**: 12px, normal, primary text
- **Captions**: 10px, normal, secondary text  
- **Status**: 9px, uppercase, letterSpacing 0.5px

### Motion

- **Transition standard**: `all 0.15s ease` (per canon)
- **Status pulse**: `pulse 2s ease-in-out infinite` for active indicators
- **Progress fill**: `width 0.5s ease-out` for smooth bar fills
- **Entry animation**: `fadeIn 0.2s ease` for new content appearing

---

## Technical Architecture

*See companion document: [JOC_ARCHITECTURE.md](./OPUS1_JOC_ARCHITECTURE.md)*

---

## Implementation Phases

### Phase A: The Shell (Week 1)
- JOC window frame with tab navigation
- Dashboard layout with placeholder cards
- Session Manager with mock AI cards
- Dark theme system fully applied

### Phase B: The Nervous System (Week 2)
- MCP message bus integration (live agent comms)
- Session persistence (login/cookies/health monitoring)
- Live viewport rendering for active browser sessions

### Phase C: The Brain (Week 3)  
- AI Drivers (ChatGPT, Gemini prompt injection + response extraction)
- Dispatch Engine (compose prompt → send to multiple AIs)
- Context auto-compilation from project files

### Phase D: The Synthesis (Week 4)
- Results aggregator (multi-AI response comparison)
- Memory sync (ChatGPT memory ↔ AIM-OS CMC)
- Project catalog with automatic staleness detection

### Phase E: The Polish (Week 5)
- Micro-animations, transitions, keyboard shortcuts
- Presets for common dispatch patterns
- Operator runbook and validation

---

## What This Changes

When the JOC is complete, Braden's workflow transforms:

| Before | After |
|--------|-------|
| Open ChatGPT tab, type, wait, copy | Type once in JOC, dispatch to ChatGPT |
| Switch to Gemini, paste context, rephrase, wait | Same dispatch hits Gemini simultaneously |
| Manually compare responses | Synthesis panel highlights agreements/disagreements |
| Copy results to Cursor for agents | "Route to Aether" button sends via MCP |
| Compile context files for 10-file limits | Auto-context compiles from project |
| "Which project was that? Which branch?" | Project catalog with live status |
| "Is my ChatGPT session still logged in?" | Session health bar turns red = auto-alert |

**The JOC is the answer to the 80/20 problem.** It takes the 80% mechanical orchestration work and automates it, leaving 100% of your time for the creative work — the architecture, the vision, the decisions that only a human can make.

---

*With the canon as foundation and the vision as guide,*  
*Claude Opus 4.6 💙*
