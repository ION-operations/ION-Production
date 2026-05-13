# Next Tasks — Bounded, Owner, Criteria

**Updated:** 2026-03-04  
**Purpose:** Paste to ChatGPT. Bounded scope. No drift.

---

## Task 1: DispatchPage browserId Seam (Finding #10)

| Field | Value |
|-------|-------|
| **Owner** | Opus (COO) or assigned specialist |
| **Allowed paths** | `packages/joc/src/pages/DispatchPage.tsx`, `packages/joc/src/stores/`, BAS API contract |
| **Forbidden paths** | MCP server, agent genomes, other pages |
| **Output required** | Patch that aligns browserId with BAS expectation (real browser IDs from SessionPage) |
| **Acceptance** | DispatchPage can use SessionPage-launched browsers; no gpt-1/gem-1 placeholders |

---

## Task 2: jocStore vs sessionStore Sync (Finding #11)

| Field | Value |
|-------|-------|
| **Owner** | Opus or assigned |
| **Allowed paths** | `packages/joc/src/stores/`, SessionPage, DispatchPage |
| **Forbidden paths** | BAS, MCP |
| **Output required** | sessionStore and jocStore aligned so DispatchPage sees SessionPage browsers |
| **Acceptance** | E2E: SessionPage launch → DispatchPage can dispatch to that browser |

---

## Task 3: ChatGPT Context Maintenance

| Field | Value |
|-------|-------|
| **Owner** | Composer + Opus (whoever does work) |
| **Allowed paths** | `context/00_operational_definition.md`, `01_current_truth.md`, `02_canonical_map.md`, `03_next_task.md` |
| **Forbidden paths** | None — these are the sync files |
| **Output required** | Files updated when state changes. Braden pastes to ChatGPT. |
| **Acceptance** | ChatGPT receives current truth; no stale assumptions |

---

## Boundary

ChatGPT is **not** the decision maker. It synthesizes, drafts, recommends. We decide and execute.
