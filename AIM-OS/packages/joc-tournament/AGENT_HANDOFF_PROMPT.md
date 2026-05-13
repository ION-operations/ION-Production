# Agent Handoff Prompt — Copy/Paste Template

> Replace `[AGENT_NAME]` with the agent's name (e.g., "Cursor", "Gemini", "Claude-IDE").
> That name becomes their build folder: `packages/joc-tournament/builds/[AGENT_NAME]/`

---

**COPY BELOW THIS LINE** ↓

---

You are **[AGENT_NAME]**, and you have been selected to compete in the **J.A.R.V.I.S. UI Tournament** — a multi-agent competition to build the best command surface for AIM-OS.

## What Is J.A.R.V.I.S.?

J.A.R.V.I.S. stands for **Joint AI Research & Visualization Intelligence System**. It is the operator cockpit for AIM-OS — a platform with 14 backend subsystems, 92 MCP tools, 6 AI agents, and 190+ persistent memory atoms. It is NOT a generic dashboard. It is a precision instrument that lets a non-coder sovereign (Braden, the CEO) see the force, inspect truth, steer agents, recover from failure, and understand system state.

## Your Mission

Build **one page done to absolute perfection** — the **Mission Control (Dashboard)** page — wrapped in the full shell (TopBar, LeftDrawer, BottomBar, AssistantRail, workspace switcher). This is not a mockup — it's a working React/TypeScript build with real components.

## But First: Research, Plan, Prepare

**You have time.** Do NOT rush into code. The team has 4+ months of design research you must study first. Your process should be:

1. **Research Phase** — Read the heritage docs. Understand what 7 previous agents built. Study the synthesis documents. Journal your observations. Take notes on what worked and what didn't.

2. **Design Phase** — Write a design proposal/brief in your build folder. Sketch your layout. Answer the 7 key design questions (listed below). Define your workspace model, drawer contents, and information hierarchy.

3. **Submit Proposal** — Present your design brief to Braden for review BEFORE building. He will approve, redirect, or ask for revisions. No building until approved.

4. **Build Phase** — Only after proposal approval, build your one perfect page with full shell wrap.

## Where to Read

All paths are relative to the AIM-OS project root:

### Must-Read (Tier 0)
| Doc | Path |
|-----|------|
| **Tournament Rules** (7 operational laws) | `packages/joc-tournament/RULES.md` |
| **Aesthetic Brief** (design DNA from hardware references) | `packages/joc-tournament/references/AESTHETIC_BRIEF.md` |
| **Competitor Index** (full onboarding guide) | `packages/joc-tournament/README.md` |
| **Heritage Index** (all 55+ heritage docs, 4 tiers) | `packages/joc-tournament/HERITAGE_INDEX.md` |
| **Panel Registry** (12 panels, 12 workspaces, types) | `packages/joc/src/store/panelRegistry.ts` |

### Architecture Heritage (Tier 1)
| Doc | Path |
|-----|------|
| DACv2 Design (771 lines, 31 panels, 5-zone layout) | `ide_orchestration/prototypes/dac/V2_DESIGN_DOCUMENT.md` |
| Best Ideas Synthesis (distilled from 7 agents) | `ide_orchestration/prototypes/dac/BEST_IDEAS_SYNTHESIS.md` |
| Codex Tournament Brief | `packages/joc-tournament/builds/codex/CODEX_TOURNAMENT_BRIEF_2026-03-07.md` |

## The 7 Key Design Questions

Before you build, you must answer these in your proposal:

1. **Which workspaces?** — 12 exist today. Codex recommends 7 primary. What's your take?
2. **What panels per workspace?** — What goes in Mission Control's left drawer?
3. **Bottom bar purpose?** — Terminal? Diagnostics? Activity feed? All?
4. **Navigation model?** — TopBar tabs? Keyboard shortcuts? Command palette?
5. **Assistant Rail role?** — Chat only? Context panel? Intelligence rail?
6. **Data truth signals?** — How do you show LIVE vs MOCK vs OFFLINE?
7. **What makes it feel like a precision instrument?** — Not a web app. An instrument.

## Aesthetic Standard

The visual bar is set by physical engineering references: Panavision DXL cinema camera, Hasselblad X2D, military-grade optics. Read `AESTHETIC_BRIEF.md` for the full translation, but the core DNA:

- **Matte black with material depth** — textured surfaces, not flat dark mode
- **Single amber accent** (#F5A623) — only for primary actions
- **Recessed LCD readouts** — panels inset into the surface
- **Engraved typography** — uppercase labels, monospace data
- **Zero wasted surface** — every element functional
- **Dense but hierarchical** — information density with clear visual hierarchy

> The test: put your screenshot next to a Panavision DXL control panel. They should feel like the same design language.

## The 7 Non-Negotiable Laws (from RULES.md)

1. **Force visibility first** — the operator must see agents, missions, health, comms
2. **Data truth must be explicit** — LIVE / CACHED / MOCK / OFFLINE / SPECULATIVE
3. **Workspace logic must be real** — switching workspaces must reconfigure the cockpit
4. **Layout must serve operations** — dispatch, inspect, recover, correlate, adjudicate
5. **Layer discipline** — J.A.R.V.I.S. is the cockpit layer, not the runtime
6. **Degraded mode matters** — UI must still make sense when MCP is down
7. **Premium ≠ vague** — confidence, clarity, materials, hierarchy, purposeful motion

## Build Location

Your build goes in:
```
packages/joc-tournament/builds/[AGENT_NAME]/
```

Create whatever files you need there. Start with a design brief:
```
packages/joc-tournament/builds/[AGENT_NAME]/DESIGN_BRIEF.md
```

## Tech Stack
- React + TypeScript
- Vanilla CSS (no Tailwind)
- Zustand for state management
- Surface Engine components available (SkeuButton, SkeuCard, SkeuPanel, SkeuLCD, SkeuToggle, SkeuKnob, SkeuGauge, SkeuIndicator)
- 28 custom SVG icons available in `packages/joc/src/components/icons/`

## What Wins

The winning build should feel like:
- The operator can actually run AIM-OS from it
- The system is telling the truth
- The layout understands work
- The UI belongs to a real intelligence cockpit
- Every surface is machined, purposeful, and beautiful

**Which build makes AIM-OS easiest to govern as a real organism?** That is the championship question.

---

Take your time. Research deeply. Journal your thoughts. Plan carefully. Then propose before you build. This is a masterpiece competition — not a speed run.
