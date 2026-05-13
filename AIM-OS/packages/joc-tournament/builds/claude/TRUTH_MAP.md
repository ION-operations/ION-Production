# Truth Map — Claude Tournament Entry
## Phase 1: Mission Control

**Agent:** Claude (Opus 4.6)
**Date:** 2026-03-07
**Law:** Data truth must be explicit (Law 2)

---

## Surface Truth Declaration

Every surface in this build declares its data source honestly.

### Mission Control — Main Content

| Surface | Truth State | Data Source | Notes |
|---------|-------------|-------------|-------|
| Force Overview (Agent Fleet) | `MOCK` | Hardcoded 6 agents | Structured to match Genome/CMC schema |
| System Health (8 subsystems) | `MOCK` | Hardcoded health values | Would wire to CAS/VIF via MCP |
| Mission Queue | `MOCK` | Hardcoded 4 missions | Structured to match APOE schema |
| Activity Feed | `MOCK` | Hardcoded 8 events | Structured to match TCS/CMC schema |

### Shell Components

| Surface | Truth State | Data Source | Notes |
|---------|-------------|-------------|-------|
| TopBar workspace list | `LIVE` | panelRegistry.ts | Static canonical data, always true |
| Oracle status badge | `MOCK` | Hardcoded SUPERVISED | Would wire to Oracle system |
| Left drawer panels | `MOCK` | Hardcoded summaries | Match canonical panel registry |
| Bottom bar status strip | `MOCK` | Hardcoded metrics | MCP latency, atom count, session count |
| Bottom bar tabs content | `MOCK` | Hardcoded log entries | Timeline, comms, diagnostics |
| Assistant Rail — Chat | `MOCK` | Hardcoded messages | Would wire to AI conversation API |
| Assistant Rail — Context | `MOCK` | Hardcoded state | Would wire to workspace state |
| Assistant Rail — Actions | `MOCK` | Hardcoded approvals | Would wire to Oracle |
| Assistant Rail — Memory | `MOCK` | Hardcoded atoms | Would wire to CMC/HHNI |

### Degraded Mode Behavior

| Scenario | Display | User Signal |
|----------|---------|-------------|
| MCP offline | All panels show `OFFLINE` badge | Gray LEDs, "NO CONNECTION" in LCD readouts |
| Data stale (>30s) | Panels switch to `CACHED` badge | Amber LEDs, timestamp of last refresh |
| No data available | Panels show empty state | "AWAITING DATA" in LCD, dim health bars |

---

## What Would Be LIVE in Production

| Surface | Required MCP Connection | Estimated Latency |
|---------|------------------------|-------------------|
| Agent Fleet | Genome + CMC | <100ms |
| System Health | CAS + VIF + per-subsystem ping | <200ms |
| Mission Queue | APOE + CMC | <100ms |
| Activity Feed | TCS + CMC | <150ms (polling) |
| Oracle Status | Oracle system | <50ms |
| Memory Browser | CMC + HHNI | <300ms (search) |

---

*No mock data masquerades as runtime truth.*
