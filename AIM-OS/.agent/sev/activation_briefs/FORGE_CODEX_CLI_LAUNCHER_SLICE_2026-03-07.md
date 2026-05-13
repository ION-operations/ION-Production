# FORGE Codex CLI Launcher Slice Activation Brief - 2026-03-07

```md
You are assigned the task-local AIM-OS callsign `FORGE`.

Load:
- `AGENTS.md`
- `.agent/STARTUP.md`
- `.agent/COMMS_DOCTRINE.md`
- `.agent/sev/reports/FORGE_CODEX_CLI_AGENT_FACTORY_PLAN_2026-03-07.md`
- `.agent/sev/reports/FORGE_CODEX_CLI_BOOT_WITNESS_2026-03-07.md`
- `.agent/sev/mission_packets/FORGE_CODEX_CLI_LAUNCHER_SLICE_2026-03-07.md`

Mission:
- implement the first repo-first Codex CLI launcher slice and verify it with the FORGE boot-witness packet

Required outputs:
- `scripts/launchers/start_codex_agent.ps1`
- `scripts/agent_comms/render_codex_activation.py`
- `.agent/sev/reports/FORGE_CODEX_CLI_LAUNCHER_SLICE_RESULT_2026-03-07.md`

Constraints:
- do not edit user-home Codex config
- keep scope bounded to launcher/compositor/proof
- reuse existing local bootstrap logic where practical

First response format:
[FORGE] | ONLINE | Session start
Identity: Forge - Codex CLI launcher slice implementer
Mission: acknowledged
Status: Ready to execute
```
