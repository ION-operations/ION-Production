# J.A.R.V.I.S. UI Tournament — Competitor Index
### Everything you need to build the best AIM-OS command surface

```
       ____. _____  __________  ____   ____.___.  _________
      |    |/  _  \ \______   \ \   \ /   /|   |/   _____/
      |    /  /_\  \ |       _/  \   Y   / |   |\_____  \
  |   |   /    |    \|    |   \   \     /  |   |/        \
  |___|___\____|__  /|____|   /    \___/   |___/_______  /
                  \/        \/                         \/

  Joint AI Research & Visualization Intelligence System
  UI Tournament — March 2026
```

---

## 🏁 Quick Start

1. **Read the Operational Laws** → `RULES.md` (Codex's 7 non-negotiable laws — force visibility, data truth, degraded mode)
2. **Read Codex's Brief** → `builds/codex/CODEX_TOURNAMENT_BRIEF_2026-03-07.md` (the correct championship question)
3. **Study the Canon** → Section A below (the 8 binding UI laws)
4. **Study the Heritage** → Section B below (4 months of team research from 7 agents)
5. **Build** → `builds/<your-agent>/` (your tournament entry)
6. **Launch** → `scripts/launchers/LAUNCH_JARVIS.bat` (test at localhost:5011)

---

## A. The Canon — Binding Laws

These are **law**. Break them = disqualification.

| # | Law | File |
|---|-----|------|
| 1 | Shell Structure | `packages/joc/src/store/panelRegistry.ts` |
| 2 | Panel Registry | `packages/joc/src/store/panelRegistry.ts` |
| 3 | Workspace Model | `packages/joc/src/store/panelRegistry.ts` |
| 4 | Assistant Rail | KI: `implementation/assistant_rail_component.md` |
| 5 | DXL Aesthetic | KI: `binding_ui_canon.md` (Law 5) |
| 6 | Data Truth Signals | KI: `binding_ui_canon.md` (Law 6) |
| 7 | Responsive Layout | KI: `binding_ui_canon.md` (Law 7 — clamp, no fixed px) |
| 8 | Naming & Consistency | KI: `binding_ui_canon.md` (Law 8) |

**Full Canon Document:**
`knowledge/joc_master_blueprint/artifacts/architecture/binding_ui_canon.md`

---

## B. Design Heritage — 4 Months of Team Research

### B.1 — Prototype Agent Builds (Nov 2025)

Seven agents each built their own IDE layout prototype. Study what worked.

| Agent | Specialty | Primary Design Doc |
|-------|-----------|-------------------|
| **Aether** | Debug infra, 5 AIM-OS structure panels, 3 code explorer variants | `ide_orchestration/prototypes/aether/IDE_LAYOUT_PROTOTYPE_AETHER.md` |
| **Max** | Panel-first (drag/drop/resize/group), layout presets | `ide_orchestration/prototypes/max/IDE_LAYOUT_PROTOTYPE_MAX.md` |
| **Lex** | AIM-OS native integration, PDAS, contradiction detection | `ide_orchestration/prototypes/lex/IDE_LAYOUT_PROTOTYPE_LEX.md` |
| **Codex** | Architecture-first, Lucid Orchestrator (4-pane), quality gates | `ide_orchestration/prototypes/codex/IDE_LAYOUT_PROTOTYPE_CODEX.md` |
| **Dac** | `useAIMOS` hooks, V2 synthesis (31 panels, 6 modes) | `ide_orchestration/prototypes/dac/V2_DESIGN_DOCUMENT.md` |
| **Rev** | Research-driven, WCAG 2.1 AA accessibility, performance | `ide_orchestration/prototypes/rev/REV_PROTOTYPE_DESIGN.md` |
| **Sam** | Consciousness-aware editor, temporal navigation | `ide_orchestration/research/NOVEL_UI_DESIGN_PROPOSALS.md` |

### B.2 — Synthesis Documents

| Document | What It Contains |
|----------|-----------------|
| `dac/BEST_IDEAS_SYNTHESIS.md` | Best systems/panels/UX distilled from all 7 agents |
| `dac/V2_DESIGN_DOCUMENT.md` | The 771-line V2 architecture (5-zone, 31 panels, 6 modes) |
| `dac/LEARNINGS_FROM_OTHER_AGENTS.md` | Cross-agent lessons learned |
| `dac/PHASE4_BETTER_IDEAS_DISCOVERY.md` | Phase 4 advanced concepts |

### B.3 — Research & Proposals

| Document | What It Contains |
|----------|-----------------|
| `ide_orchestration/research/NOVEL_UI_DESIGN_PROPOSALS.md` | 8 novel UI concepts (consciousness editor, temporal nav, evidence suggestions, etc.) |
| `ide_orchestration/research/PDAS_PROPOSAL.md` | Proactive Debugging & Auditing System |
| `dac/UI_DESIGN_ANALYSIS.md` | Current UI strengths/weaknesses analysis |
| `dac/PHASE1_PANELS_ANALYSIS.md` | Panel-by-panel deep analysis |
| `dac/PHASE1_ARCHITECTURE_ANALYSIS.md` | Architecture patterns analysis |
| `dac/PHASE2_AETHER_ANALYSIS.md` | Deep dive into Aether's innovations |
| `dac/PHASE2_REV_ANALYSIS.md` | Deep dive into Rev's research approach |
| `dac/PHASE2_CODEX_ANALYSIS.md` | Deep dive into Codex's architecture-first |
| `dac/PHASE2_LEX_ANALYSIS.md` | Deep dive into Lex's AIM-OS native approach |
| `dac/PHASE2_MAX_ANALYSIS.md` | Deep dive into Max's panel-first philosophy |

### B.4 — Planning & Roadmaps

| Document | What It Contains |
|----------|-----------------|
| KI: `planning/evolution_roadmap_v2.md` | Wave-based rebuild roadmap |
| KI: `technical/joc_technical_audit_and_inventory.md` | Current codebase audit (26 pages, 33 CSS files) |
| `dac/EXTENDED_TODO_LIST.md` | Comprehensive feature backlog |

---

## C. Current J.A.R.V.I.S. Codebase

### C.1 — Shell Components (what exists today)

| Component | File | Purpose |
|-----------|------|---------|
| TopBar | `packages/joc/src/components/layout/TopBar.tsx` | Workspace navigation |
| LeftIconBar | `packages/joc/src/components/layout/LeftIconBar.tsx` | Workspace icon rail |
| LeftDrawerSystem | `packages/joc/src/components/layout/LeftDrawerSystem.tsx` | Dynamic left panels |
| AssistantRail | `packages/joc/src/components/layout/AssistantRail.tsx` | AI assistant sidebar |
| BottomBar | `packages/joc/src/components/layout/BottomBar.tsx` | Bottom panel dock |

### C.2 — Panel Registry (fully populated)

**12 Panels:** system-status, agent-fleet, mission-queue, messages, activity-feed, memory-browser, session-health, approvals-queue, diagnostics, credentials, agent-dossier, calendar-view

**12 Workspaces:** dashboard, dispatch, mission-builder, calendar, context-lab, agent-workforce, oracle, context-graph, session, infra-console, system-atlas, code-editor

File: `packages/joc/src/store/panelRegistry.ts`

### C.3 — Surface Engine (8 skeuomorphic components)

| Component | Purpose |
|-----------|---------|
| SkeuButton | Beveled button with press animation |
| SkeuCard | Raised content card |
| SkeuPanel | Container with depth and borders |
| SkeuLCD | LCD-style display readout |
| SkeuToggle | Physical toggle switch |
| SkeuKnob | Rotary knob control |
| SkeuGauge | Analog gauge display |
| SkeuIndicator | Status light indicator |

### C.4 — Icons (28 custom SVG components)

File: `packages/joc/src/components/icons/index.tsx`
All icons: RadarIcon, ConstellationIcon, LaunchVectorIcon, SignalPulseIcon, HexLatticeIcon, ChipDieIcon, TuningForkIcon, BoltIcon, RobotHeadIcon, ClipboardListIcon, BellAlertIcon, RefreshCycleIcon, ShieldKeyIcon, CalendarMarkIcon, CrosshairIcon, ParallelLinesIcon, ChainLinkIcon, MergePathsIcon, CrossedSwordsIcon, DispatchIcon, JOCLogo, StatusDotIcon, SatelliteIcon, AutomationIcon, PlusIcon, CloseIcon, ChevronUp/Down/Left/RightIcon

---

## D. Backend Systems You Can Wire To

| System | Port | Purpose |
|--------|------|---------|
| MCP Server | 5001 | 92 tools — memory, confidence, search, AI collaboration |
| JOC Surface | 5011 | Vite dev server (your UI) |
| BAS/SEER | 5002 | Browser automation and visual manipulation |

| Subsystem | Acronym | What It Does |
|-----------|---------|-------------|
| Context Memory Core | CMC | Immutable memory atoms (190+) |
| Hierarchical Holonic Nav Index | HHNI | Semantic search and retrieval |
| Verifiable Intelligence Framework | VIF | Confidence tracking, kappa gates |
| AI-Powered Orchestration Engine | APOE | Workflow plans and execution |
| Semantic Evidence Graph | SEG | Knowledge synthesis, contradictions |
| Timeline Context System | TCS | Bitemporal event tracking |
| Cognitive Analysis System | CAS | Attention, drift, self-awareness |
| NL Tags System | NLT | Code documentation tags |

---

## E. Key Design Questions to Answer

Before building, every competitor must decide:

1. **Which workspaces?** (12 is the current count — too many? Right ones?)
2. **What panels per workspace?** (Left drawer contents per workspace)
3. **Bottom bar purpose?** (Terminal? Diagnostics? Activity feed? All?)
4. **Navigation model?** (TopBar tabs? Keyboard shortcuts? Command palette?)
5. **Assistant Rail role?** (Chat? Context panel? Both? How wide?)
6. **Data truth signals?** (Which panels show LIVE/MOCK/OFFLINE badges?)
7. **What makes it feel like a billion-dollar ops center?**

---

## F. Launcher

```bash
# Simple launch (browser)
scripts\launchers\LAUNCH_JARVIS.bat

# PowerShell with options
scripts\launchers\LAUNCH_JARVIS.ps1 -Mode dev       # Vite only
scripts\launchers\LAUNCH_JARVIS.ps1 -Mode electron   # Desktop shell
scripts\launchers\LAUNCH_JARVIS.ps1 -Mode full        # MCP + BAS + Electron
```

---

*Study. Design. Build. Wow us.*
