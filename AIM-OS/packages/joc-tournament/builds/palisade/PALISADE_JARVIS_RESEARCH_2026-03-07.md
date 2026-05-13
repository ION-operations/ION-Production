# Palisade JARVIS Tournament Research — 2026-03-07

**Agent:** Palisade (doctrine / canon auditor)  
**Purpose:** Canon-focused research and planning to support the JARVIS tournament. No UI build.  
**Sources:** `packages/joc-tournament/RULES.md`, `panelRegistry.ts`, Codex brief, HERITAGE_INDEX, shared types, resolved tournament brief.

---

## 1. Scope and Role

- **Palisade** does not submit a competing UI build. This folder is for **research and planning** that supports the tournament.
- **Outputs:** (1) This research doc — law-by-law implications, checklist, and pointers to canon. (2) A truth-map template for the required competitor deliverable.
- **Use:** Competitors can use this to align with the 7 laws and the championship question; judges can use it to verify canon compliance and operational clarity.

---

## 2. The Seven Non-Negotiable Laws — Operational Interpretation

### Law 1 — Force visibility first

**Rule:** A winning build must make the workforce and system legible: agent status, mission flow, approvals, comms state, system health. If it looks premium but hides the force, it loses.

**Implications:**
- Mission Control (dashboard) must surface **agent fleet**, **system status**, **mission queue**, and **comms/approvals** in seconds.
- "Legible" = operator can answer without hunting: Who is active? What is running? What needs approval? What is broken?
- **Anti-pattern:** Hero screen that looks impressive but buries or omits agent status, missions, or approvals.

**Checklist:**
- [ ] Agent status visible from Mission Control (or one click away).
- [ ] Mission flow (queue / active missions) visible or clearly reachable.
- [ ] Approvals surface explicit (Oracle / dispatch).
- [ ] Comms state (messages, handoffs) visible where dispatch/workforce are used.
- [ ] System health (subsystem status) visible from Mission Control or Infra Console.

---

### Law 2 — Data truth must be explicit

**Rule:** Every meaningful surface must declare: LIVE | CACHED | MOCK | OFFLINE | SPECULATIVE. No mock data may masquerade as runtime truth.

**Implications:**
- Every panel/surface that shows data must show a **truth badge** (or equivalent) using the canonical set. See `packages/joc/src/store/panelRegistry.ts` → `DataStatus` and `DATA_STATUS_CONFIG`; also `packages/joc-tournament/shared/types.ts` → `TruthState`.
- "Meaningful surface" = any view that could be mistaken for live backend data (lists, feeds, dashboards, queues).
- **Anti-pattern:** Mock or cached data shown without a visible MOCK/CACHED indicator.

**Checklist:**
- [ ] Every data panel has an explicit truth state (LIVE/CACHED/MOCK/OFFLINE/SPECULATIVE).
- [ ] Truth state is visible (badge, label, or dedicated area) — not only in code.
- [ ] Deliverable includes a **truth map** listing each surface and its declared state (use `TRUTH_MAP_TEMPLATE.md`).

---

### Law 3 — Workspace logic must be real

**Rule:** Workspace switching must materially reconfigure the cockpit. Do not ship one shell with different labels.

**Implications:**
- Changing workspace must change **left drawer contents**, **bottom panels** (if any), and **main content** in a way that matches the workspace’s purpose (see `panelRegistry.ts` → `WorkspaceDefinition`: `defaultLeftPanels`, `bottomPanels`).
- "Materially" = different workspaces feel like different operational contexts (e.g. Mission Control vs Dispatch vs Oracle), not the same layout with a different tab label.
- **Anti-pattern:** Same layout for every workspace with only the title changing.

**Checklist:**
- [ ] Each workspace has defined default left (and optionally bottom) panels.
- [ ] Switching workspace updates the cockpit layout (panels, content) in a way that matches the workspace’s role.
- [ ] Deliverable includes a **short note explaining main workspace logic** (which workspaces exist, what each is for, how layout changes).

---

### Law 4 — Layout must serve operations

**Rule:** Layout should help the operator dispatch, inspect, recover, correlate, adjudicate. Dead space, ornamental density, or aesthetic noise count against the build.

**Implications:**
- Layout and density should support **operator actions** (see `shared/types.ts` → `OperatorAction`: dispatch, inspect, recover, correlate, adjudicate).
- Premium feel comes from **clarity and hierarchy**, not clutter (Codex brief: composure, material confidence, density with hierarchy, precise motion, explicit truth).
- **Anti-pattern:** Decorative elements that consume space without supporting these actions.

**Checklist:**
- [ ] Primary areas support: dispatch, inspect, recover, correlate, adjudicate.
- [ ] No large dead zones; no ornamental density that obscures operations.
- [ ] Width used intelligently (e.g. full-width where it helps correlation).

---

### Law 5 — AIMOS layer discipline

**Rule:** The build must respect: core | runtime | cockpit | product | bootstrap-only. JARVIS belongs to the **cockpit** layer.

**Implications:**
- JARVIS is the **operator cockpit over AIM-OS**, not the runtime or the end product. UI should reflect that it is a **control and visibility layer** over backend systems (CMC, HHNI, VIF, APOE, SEG, TCS, CAS, MCP, Oracle, Genome).
- **Anti-pattern:** Blurring cockpit with "product" UX (e.g. consumer app) or implementing runtime logic inside the cockpit.

**Checklist:**
- [ ] Positioning is clearly "cockpit over AIM-OS" (visibility + control).
- [ ] No runtime or core logic duplicated in the UI; UI calls backend / MCP where applicable.
- [ ] Panel registry and workspace definitions align with cockpit role (see `panelRegistry.ts` domains and dataSources).

---

### Law 6 — Degraded mode matters

**Rule:** The UI must still make sense when MCP or live systems are unavailable. A good cockpit reveals failure clearly instead of collapsing into ambiguity.

**Implications:**
- When MCP or backend is down, surfaces should show **OFFLINE** (or CACHED with age) and, where useful, a clear "unavailable" or "degraded" state — not blank, not generic error, not fake live data.
- **Anti-pattern:** Silent failure, or showing mock data without marking it MOCK/OFFLINE.

**Checklist:**
- [ ] When backend/MCP is unavailable, affected panels show OFFLINE (or equivalent) and optionally a short reason.
- [ ] No ambiguous empty state that could be mistaken for "no data" vs "system down".
- [ ] Optional: a single "system connectivity" or degraded-mode indicator for the shell.

---

### Law 7 — Premium does not mean vague

**Rule:** "Billion-dollar ops center" means confidence, clarity, materials, hierarchy, motion with purpose — not neon clutter or sci-fi cosplay.

**Implications:**
- Visual design should feel **instrumentation and command**, not decorative or gimmicky. Align with DXL/skeuomorphic materials (Surface Engine: SkeuButton, SkeuCard, etc.) and consistent hierarchy.
- **Anti-pattern:** Neon clutter, generic sci-fi styling, or motion without purpose.

**Checklist:**
- [ ] Typography and materials support readability and hierarchy.
- [ ] Motion (if any) has purpose (feedback, state change, focus).
- [ ] No "sci-fi cosplay" or ornamental neon at the expense of clarity.

---

## 3. The Championship Question (Codex)

The tournament should answer:

**Which build makes AIM-OS easiest to govern as a real organism?**

Concrete tests for a winning build:
- Operator can see **system health** in seconds.
- Operator can see the **current agent force** in seconds.
- Operator can tell **live from mock** instantly.
- Screen uses **width intelligently**.
- Shell feels like **command instrumentation**, not app furniture.

Use these as evaluation criteria alongside the 7 laws.

---

## 4. Canon Sources in Repo

| What | Where |
|------|--------|
| **7 operational laws** | `packages/joc-tournament/RULES.md` |
| **Codex brief / championship question** | `packages/joc-tournament/builds/codex/CODEX_TOURNAMENT_BRIEF_2026-03-07.md` |
| **12 panels, 12 workspaces, DataStatus, DATA_STATUS_CONFIG** | `packages/joc/src/store/panelRegistry.ts` |
| **Shared types, TruthState, PRIMARY_WORKSPACES, OperatorAction** | `packages/joc-tournament/shared/types.ts` |
| **Design heritage index** | `packages/joc-tournament/HERITAGE_INDEX.md` |
| **Tournament README (canon, backend, launcher)** | `packages/joc-tournament/README.md` |
| **Shell components (TopBar, LeftDrawer, AssistantRail, BottomBar)** | `packages/joc/src/components/layout/*` |
| **Surface Engine (Skeu*)** | `packages/joc/src/components/engine/Surface*.tsx` |

**Note:** The full "8 binding UI laws" document (`binding_ui_canon.md`) is referenced in HERITAGE_INDEX as a knowledge item (KI); it may live outside the repo. The **7 laws in RULES.md** are the **operational** law for the tournament; the 8 binding laws (aesthetic, responsive, etc.) are design canon to be followed where referenced in README/HERITAGE_INDEX.

---

## 5. Workspace Logic — What “Materially Reconfigure” Means

From `panelRegistry.ts`, the 12 canonical workspaces and their default left (and bottom) panels are:

| Workspace ID | Title | Default left panels | Bottom |
|--------------|--------|----------------------|--------|
| dashboard | Mission Control | agent-fleet, system-status | activity-feed |
| dispatch | Dispatch | mission-queue, messages | — |
| mission-builder | Mission Builder | mission-queue | — |
| calendar | Calendar | calendar-view | — |
| context-lab | Context Lab | memory-browser | — |
| agent-workforce | Agent Workforce | agent-dossier, messages | — |
| oracle | Oracle | approvals-queue, memory-browser | — |
| context-graph | Context Graph | (none) | — |
| session | Session | session-health | — |
| infra-console | Infra Console | system-status, credentials | diagnostics |
| system-atlas | System Atlas | (none) | — |
| code-editor | Code Editor | (none) | diagnostics |

A build that "materially reconfigures" would, for example:
- Show **Mission Control** with fleet + system status + activity feed.
- Show **Dispatch** with mission queue + messages (different left drawer).
- Show **Oracle** with approvals + memory browser (again different).
- Show **Infra Console** with system-status + credentials in left and diagnostics in bottom.

Competitors can subset or reorder workspaces (e.g. Codex’s primary 7 + secondary 5) but switching between them should change the cockpit layout accordingly, not just the label.

---

## 6. Required Deliverables (RULES §4)

Each competitor must provide:

1. **One build directory** under `packages/joc-tournament/builds/<agent>/`.
2. **One short design brief** (thesis, main choices).
3. **One screenshot set per round** (as rounds are defined).
4. **One truth map of live vs mock surfaces** — use `TRUTH_MAP_TEMPLATE.md` in this folder.
5. **One note explaining main workspace logic** — which workspaces, what each is for, how layout changes on switch.

Palisade’s truth-map template is provided so every competitor can satisfy (4) in a consistent, judge-friendly format.

---

## 7. Design Heritage — Where to Look

- **Tier 0:** RULES.md, Codex brief, panelRegistry.ts (and HERITAGE_INDEX Tier 0).
- **Tier 1:** DAC V2 design, Best Ideas Synthesis, Novel UI Proposals, PDAS, evolution roadmap (see HERITAGE_INDEX).
- **Tier 2:** Individual agent prototypes (Aether, Max, Lex, Codex, Dac, Rev, Sam) — see HERITAGE_INDEX and README Section B.
- **Tier 3–4:** Phase analyses, KI docs, shell components, stores, Surface Engine (HERITAGE_INDEX).

The resolved tournament brief (Antigravity) lists the same heritage and the 5-zone layout, 31 DACv2 panels, 8 revolutionary concepts — all relevant for "ground-up rebuild" and "full production masterpiece" without reskinning.

---

## 8. Summary Checklist for Competitors

- [ ] Read RULES.md and Codex brief; use championship question as north star.
- [ ] Force visibility first: agent status, mission flow, approvals, comms, system health legible.
- [ ] Every data surface declares truth state (LIVE/CACHED/MOCK/OFFLINE/SPECULATIVE); fill truth map.
- [ ] Workspace switch materially reconfigures cockpit; document workspace logic.
- [ ] Layout serves dispatch, inspect, recover, correlate, adjudicate; no dead space or ornamental noise.
- [ ] JARVIS positioned as cockpit layer; degraded mode (MCP/backend down) shown clearly.
- [ ] Premium = confidence, clarity, materials, hierarchy; no neon clutter or sci-fi cosplay.
- [ ] Deliver: build dir, design brief, screenshots per round, truth map, workspace logic note.

---

*Palisade — doctrine and canon research only. No UI build. Use this document and the truth-map template to align with the 7 laws and the championship question.*
