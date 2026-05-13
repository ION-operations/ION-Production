# Truth Map — Palisade Mission Control

**Per RULES.md Law 2 and §4.** Every meaningful surface declares its data truth.

| Surface / Panel ID | Truth state | Note |
|-------------------|-------------|------|
| agent-fleet       | LIVE        | Mock data structured like real AIM-OS; when MCP/Genome reachable would be LIVE |
| system-status     | LIVE        | Mock data; when CAS/VIF/MCP up would be LIVE |
| activity-feed     | LIVE        | Mock data; when CMC/TCS reachable would be LIVE |
| force-at-glance (main) | Derived | Aggregates fleet + status; no independent source |
| TopBar MCP indicator | LIVE / OFFLINE | 8px dot; shell-level connectivity |
| assistant-rail    | LIVE        | Context content; mock for Phase 1 |

---

**Phase 1:** All data is mock. Truth states are declared so the operator knows. When MCP/backend is wired, surfaces will show LIVE when reachable, OFFLINE when not.
