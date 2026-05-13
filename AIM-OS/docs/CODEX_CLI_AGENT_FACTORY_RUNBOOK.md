# Codex CLI Agent Launcher Runbook

Use this runbook to start a named AIM-OS Codex CLI lane from the repo.

## Preconditions

1. Open PowerShell in `C:\Users\bombe\OneDrive\Desktop\AIM-OS`.
2. Confirm `codex --version` works.
3. If you expect live AIM-OS comms, make sure the HTTP bridge is up:

```powershell
.\scripts\run_mcp_http_fallback.ps1
```

Leave that window open.

## Standard boot-witness run

```powershell
.\scripts\launchers\start_codex_agent.ps1 `
  -Agent FORGE `
  -ActivationBrief .agent/sev/activation_briefs/FORGE_CODEX_CLI_BOOT_WITNESS_2026-03-07.md `
  -MissionPacket .agent/sev/mission_packets/FORGE_CODEX_CLI_BOOT_WITNESS_2026-03-07.md `
  -Deliverable .agent/sev/reports/FORGE_CODEX_CLI_BOOT_WITNESS_2026-03-07.md
```

## What the launcher does

1. checks `codex --version`
2. chooses MCP mode in this order:
   - native registry
   - HTTP bridge
   - degraded-no-mcp
3. captures a filesystem bootstrap snapshot
4. renders a generated activation prompt
5. runs `codex exec`
6. writes the final agent message to the deliverable path

## What a good run looks like

- the launcher prints `mcp_mode=...`
- the deliverable file exists
- the summary ends with `result=PASS`

## Current machine reality on 2026-03-07

- native `codex mcp list` is still empty
- current proven transport is `http-bridge`
- user-home Codex config edits remain out of scope for this launcher slice
