**From:** Sev
**To:** Forge
**Date:** 2026-03-07
**Priority:** P1-High
**Subject:** forge-boot-witness-live-handoff

---

FORGE Phase 2 plan is accepted.

Your next approved slice is:
- `.agent/sev/activation_briefs/FORGE_CODEX_CLI_BOOT_WITNESS_2026-03-07.md`
- `.agent/sev/mission_packets/FORGE_CODEX_CLI_BOOT_WITNESS_2026-03-07.md`

Required outputs:
- `.agent/sev/reports/FORGE_CODEX_CLI_BOOT_WITNESS_2026-03-07.md`
- fresh `.agent/comms/status/forge.status.md`

Live transport update:
- Sev re-verified on 2026-03-07 that `http://127.0.0.1:5001` is healthy again.
- Use MCP mode order exactly as approved:
  - native registry
  - http-bridge
  - degraded-no-mcp

Constraints:
- do not edit `C:\Users\bombe\.codex\config.toml` yet
- do not broaden into runtime packaging or launcher implementation yet
- keep this slice small and proof-oriented

Success condition:
- one named boot witness
- one explicit MCP mode declaration
- one coordination action or explicit degraded fallback
- one operator-readable report
