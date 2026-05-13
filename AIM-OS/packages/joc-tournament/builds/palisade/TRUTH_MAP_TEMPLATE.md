# Truth Map — Live vs Mock Surfaces

**Purpose:** RULES.md Law 2 requires every meaningful surface to declare its data truth. Each competitor must submit "one truth map of live vs mock surfaces" (RULES §4).

**How to use:** Copy this template into your build folder (e.g. `builds/<agent>/TRUTH_MAP.md`). For every panel or data surface in your build, list it and set **Truth state** to one of: `LIVE` | `CACHED` | `MOCK` | `OFFLINE` | `SPECULATIVE`. Add a short note when useful (e.g. "MCP :5001" for live, "seed data" for mock).

---

## Template

| Surface / Panel ID | Truth state | Note (optional) |
|-------------------|-------------|-----------------|
| system-status     |             | e.g. LIVE when MCP up, else OFFLINE |
| agent-fleet       |             | |
| mission-queue     |             | |
| messages          |             | |
| activity-feed     |             | |
| memory-browser    |             | |
| session-health    |             | |
| approvals-queue  |             | |
| diagnostics      |             | |
| credentials      |             | |
| agent-dossier     |             | |
| calendar-view     |             | |
| *(add any other surfaces your build shows)* | | |

---

## Truth state definitions (canonical)

| State | Meaning |
|-------|--------|
| **LIVE** | Real data from AIM-OS / MCP (e.g. :5001). |
| **CACHED** | Was live; now stale (e.g. >30s old). |
| **MOCK** | Development or fallback data; not from production backend. |
| **OFFLINE** | Cannot reach data source (e.g. MCP down). |
| **SPECULATIVE** | AI prediction or unconfirmed. |

Source: `packages/joc/src/store/panelRegistry.ts` (`DataStatus`), `packages/joc-tournament/shared/types.ts` (`TruthState`).

---

*Fill this map for every data surface in your build. Judges will use it to verify Law 2 compliance.*
