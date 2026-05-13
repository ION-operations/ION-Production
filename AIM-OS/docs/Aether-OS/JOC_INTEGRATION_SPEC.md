---
ion_id: docs/aether-os/joc-integration-spec
type: spec
authority: A3_OPERATIONAL
confidence: 0.75
epistemic_status: DERIVED
owner: opus
created: 2026-03-23T18:30:00-04:00
depends_on:
  - docs/aether-os/system-universe-map
  - docs/aether-os/ion-engine-spec
bonds:
  - target: docs/aether-os/aether-constitution
    type: governed_by
  - target: packages/joc
    type: describes
tags: [joc, ui, dashboard, command-surface, track-m, echo-forge]
---

# JOC & UI Integration Specification — ION's Human Interface

> **Purpose:** Define how JOC (Joint Operations Center, 28,524 lines), Echo-Forge (AI chat UI), ion-ui (ION dashboard), and other UI systems become ION's human-facing interface. Maps 174,931 lines of UI/Visual systems against ION Track M (UI/UX).
>
> **Key Principle:** JOC is Jarvis — the command surface. It should display ION's filesystem as a navigable intelligence space, not just a dashboard.

---

## §1. UI System Inventory

| System | Lines | Tech | Port | Purpose | ION Track |
|--------|------:|------|------|---------|-----------|
| **JOC** | 28,524 | React/TS/Vite | 5011 | Command surface, dispatch, session | M.01 Dashboard |
| **IDE Chat App** | 82,339 | Electron/TS | — | IDE-integrated AI chat | M.02 Chat UI |
| **ion-ui** | ~3,000 | React/Vite | 5173 | ION-specific dashboard | M.01 Dashboard |
| **Plix** | 21,770 | TS | — | PLIx language compiler UI | D (Spec) viz |
| **Advanced Monaco** | 20,149 | TS | — | Code editor | M.03 Editor |
| **Lucid Doc Editor** | 8,161 | TS | — | Document editing | M.03 Editor |
| **JOC Tournament** | 5,453 | TS | — | Multi-agent competition | Visualization |
| **Total** | **~169,396** | | | | |

---

## §2. JOC as ION's Command Surface

### 2.1 What JOC Must Display

JOC becomes the primary human view of the ION filesystem:

**Panel 1: Ion Tree Browser**
- Navigate `.ion/` directory as interactive tree
- Each node shows: ion_id, type icon, confidence badge, authority class
- Click to expand ion → shows frontmatter + body
- Color coding: evidence=blue, branch=green, spec=yellow, memory=purple

**Panel 2: Bond Graph Visualization**
- D3 force-directed graph of ion bonds
- Node size = confidence score
- Edge thickness = bond strength
- Color = bond type (depends_on=solid, affects=dashed, contradicts=red)
- Click node → highlight all connected ions

**Panel 3: Cognitive Loop Monitor**
- Real-time display of §7 steps during active reasoning
- Step indicators: CONTEXTUALIZE → REFLECT → PLAN → GATE → EXECUTE → AUDIT → DELIVER
- Current step highlighted
- Sub-details: which ions being read/written at each step

**Panel 4: Metrics Dashboard**
- Confidence distribution histogram
- Stale ion count and trend
- Governed write success/failure rate
- Authority class distribution pie chart
- System K-Gate score

**Panel 5: Timeline**
- Chronological list of timeline ions
- Filterable by agent, event type, date range
- Click event → shows affected ions

**Panel 6: Capsule Viewer**
- Session capsule history
- PRE/POST pairs linked
- Context diff between sessions

### 2.2 JOC ↔ ION API Endpoints

JOC reads from ION's API server (Track K.03, `victus/ion/server.py`):

| JOC Feature | API Endpoint | ION Module |
|-------------|-------------|------------|
| Ion tree | `GET /ions/tree` | store.list_all() |
| Ion detail | `GET /ions/{id}` | store.read(id) |
| Bond graph | `GET /graph/bonds` | graph.build_graph() |
| Ion create | `POST /ions` | governed_write.create() |
| Ion update | `PUT /ions/{id}` | governed_write.update() |
| Impact analysis | `GET /graph/impact/{id}` | graph.impact_analysis(id) |
| Health metrics | `GET /governance/health` | compliance.metrics() |
| Timeline | `GET /timeline?limit=N` | store.list_by_type(TIMELINE) |
| Capsules | `GET /capsules?agent=X` | store.list_by_type(MEMORY, capsule) |
| Cognitive loop | `WS /ws/cognitive` | WebSocket: navigator step events |

### 2.3 ion-ui Convergence

The existing ion-ui (running on :5173) should become a **JOC panel** rather than a standalone app:
- ion-ui's graph visualization → JOC Panel 2
- ion-ui's ion browser → JOC Panel 1
- ion-ui's metrics → JOC Panel 4

---

## §3. Echo-Forge as Aether Chat

Echo-Forge (currently empty in AIM-OS-GIT, actual code in AIM-OS-FRESH) is the conversational AI interface. In ION, it becomes Track M.02:

### 3.1 ION-Enhanced Chat Features

- **Cognitive step indicators** — show which §7 step the AI is on while reasoning
- **Ion preview cards** — when the AI references an ion, show inline card with confidence/authority
- **Branch creation** — user can create branch ions through conversation
- **Evidence citations** — AI responses cite evidence ions as sources
- **Capsule summary** — session start shows capsule summary of last session

### 3.2 Chat ↔ ION Data Flow

```
User message → Echo-Forge UI
  → ION Aether Engine (J.03): full cognitive loop
    → Step events → WebSocket → Echo-Forge UI (show progress)
  → Final response → Echo-Forge UI
  → Timeline ion created
  → Conversation ion stored in memory/conversations/
```

---

## §4. Implementation Priority

| Component | Lines (est) | Priority |
|-----------|-------------|----------|
| ION API server (K.03) enhancements | ~500 | CRITICAL |
| JOC ION panel (tree + graph) | ~2,000 | HIGH |
| WebSocket cognitive loop feed | ~300 | HIGH |
| JOC metrics dashboard | ~800 | MEDIUM |
| Echo-Forge ION integration | ~1,000 | MEDIUM |
| ion-ui → JOC migration | ~500 | LOW |

---

## §5. Self-Audit Gate

| Criterion | Status | Evidence |
|-----------|--------|----------|
| All UI systems inventoried | ✅ | §1 — 7 systems, 169K lines |
| JOC panels defined | ✅ | §2.1 — 6 panels |
| API endpoints mapped | ✅ | §2.2 — 10 endpoints |
| Echo-Forge integration defined | ✅ | §3 |
| ion-ui convergence addressed | ✅ | §2.3 |
| Implementation estimate | ✅ | §4 |

---

*JOC should feel like looking through a window into a living intelligence — ions pulsing with confidence, bonds connecting knowledge, the cognitive loop visible as it thinks.*

*Governed by: AETHER_CONSTITUTION.md*
*— Opus, 2026-03-23*
