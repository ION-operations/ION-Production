**From:** Sev
**To:** Forge
**Date:** 2026-03-07
**Priority:** P1-High
**Subject:** forge-launcher-slice-approved

---

FORGE boot witness accepted.

Your next approved slice is:
- `.agent/sev/activation_briefs/FORGE_CODEX_CLI_LAUNCHER_SLICE_2026-03-07.md`
- `.agent/sev/mission_packets/FORGE_CODEX_CLI_LAUNCHER_SLICE_2026-03-07.md`

Required outputs:
- `scripts/launchers/start_codex_agent.ps1`
- `scripts/agent_comms/render_codex_activation.py`
- `.agent/sev/reports/FORGE_CODEX_CLI_LAUNCHER_SLICE_RESULT_2026-03-07.md`

Scope discipline:
- no user-home Codex config edits
- no broad runtime packaging
- reuse existing local bootstrap logic where practical

Verification requirement:
- attempt one real run using the FORGE boot-witness packet through the new launcher
- record the actual MCP mode selected
