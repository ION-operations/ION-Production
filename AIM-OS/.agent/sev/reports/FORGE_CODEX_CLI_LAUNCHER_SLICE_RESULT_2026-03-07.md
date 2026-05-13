# FORGE Codex CLI Launcher Slice Result - 2026-03-07

**Mission ID:** `FORGE-004-codex-cli-launcher-slice`  
**Result:** functional PASS with host-timeout caveat  
**Host scope:** Codex CLI only. No Cursor Codex claims are made here.

---

## 1. What Was Implemented

This slice implemented the first repo-first Codex CLI launcher path for AIM-OS:

1. `scripts/launchers/start_codex_agent.ps1`
2. `scripts/agent_comms/render_codex_activation.py`
3. `docs/CODEX_CLI_AGENT_FACTORY_RUNBOOK.md`

The launcher now:

- accepts `-Agent`, `-ActivationBrief`, `-MissionPacket`, and `-Deliverable`
- validates the selected doctrine files
- detects MCP mode in the approved order
- reuses `scripts/agent_comms/bootstrap_agent_session.py`
- renders a generated prompt file
- runs `codex exec`
- writes the last agent message to the requested deliverable path

---

## 2. Files Added or Changed

### Added

- `scripts/launchers/start_codex_agent.ps1`
- `scripts/agent_comms/render_codex_activation.py`
- `docs/CODEX_CLI_AGENT_FACTORY_RUNBOOK.md`
- `.agent/sev/reports/FORGE_CODEX_CLI_LAUNCHER_SLICE_RESULT_2026-03-07.md`

### Changed during implementation

- `scripts/launchers/start_codex_agent.ps1`

Two real defects were fixed during the slice:

1. the first launcher version tried to compute `$RepoRoot` from `$PSScriptRoot` inside the parameter default, which fails before the script body executes
2. the second launcher version hit `codex.ps1`, whose PowerShell wrapper surfaced native stderr warnings as terminating noise; the launcher was switched to `codex.cmd`

---

## 3. How the Launcher Works

1. Resolve repo root and required file paths.
2. Check `codex.cmd --version`.
3. Detect MCP mode in this order:
   - `codex.cmd mcp list`
   - `http://localhost:5001/health`
   - fallback to `degraded-no-mcp`
4. Run `python scripts/agent_comms/bootstrap_agent_session.py` and save a bootstrap snapshot under `.agent/runtime/codex_cli/<agent>/`.
5. Run `python scripts/agent_comms/render_codex_activation.py` to build a deterministic prompt from:
   - `AGENTS.md`
   - `.agent/STARTUP.md`
   - `.agent/COMMS_DOCTRINE.md`
   - selected activation brief
   - selected mission packet
   - bootstrap snapshot
6. Pipe the generated prompt into:

```powershell
codex.cmd exec -C <repo-root> -s danger-full-access --output-last-message <deliverable> -
```

7. Print a short launcher summary with MCP mode, deliverable path, prompt path, and pass/fail.

---

## 4. Verification Run

### Exact command used

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/launchers/start_codex_agent.ps1 `
  -Agent FORGE `
  -ActivationBrief .agent/sev/activation_briefs/FORGE_CODEX_CLI_BOOT_WITNESS_2026-03-07.md `
  -MissionPacket .agent/sev/mission_packets/FORGE_CODEX_CLI_BOOT_WITNESS_2026-03-07.md `
  -Deliverable .agent/sev/reports/FORGE_CODEX_CLI_BOOT_WITNESS_2026-03-07.md
```

### Actual MCP mode chosen

- `http-bridge`

### Actual result

Observed preflight:

- `codex-cli 0.111.0`
- `codex.cmd mcp list` remained empty
- `http://localhost:5001/health` returned `ready=true`
- launcher printed `mode: http-bridge`

Generated runtime artifacts from the real launcher run:

- `.agent/runtime/codex_cli/forge/bootstrap_20260307_115237.txt`
- `.agent/runtime/codex_cli/forge/prompt_20260307_115237.md`

Observed outputs produced by the launcher-driven Codex CLI lane:

- `.agent/sev/reports/FORGE_CODEX_CLI_BOOT_WITNESS_2026-03-07.md` was rewritten at `2026-03-07 11:57:58 AM`
- `.agent/comms/status/forge.status.md` was refreshed to `2026-03-07 16:55 UTC`
- the launcher-driven lane reported a live bridge send:
  - `message_id=ai_msg_0_20260307_115457`
  - `thread_id=FORGE-003-codex-cli-boot-witness-2026-03-07`

### Result judgment

**Functional pass.** The launcher, compositor, and Codex CLI lane completed the packet work and produced the requested deliverable path.

### Caveat

The outer automation host timed out after roughly 300 seconds before the PowerShell launcher returned its final summary line. In other words:

- the repo artifacts prove the launcher-run Codex lane finished the mission
- the surrounding automation wrapper did not stay attached long enough to observe the final script exit cleanly

That is an automation-timeout limitation in this verification environment, not evidence that the repo-first launcher failed to produce the requested artifacts.

---

## 5. Operator Instructions

Use the runbook:

- `docs/CODEX_CLI_AGENT_FACTORY_RUNBOOK.md`

Minimal operator command:

```powershell
.\scripts\launchers\start_codex_agent.ps1 `
  -Agent FORGE `
  -ActivationBrief .agent/sev/activation_briefs/FORGE_CODEX_CLI_BOOT_WITNESS_2026-03-07.md `
  -MissionPacket .agent/sev/mission_packets/FORGE_CODEX_CLI_BOOT_WITNESS_2026-03-07.md `
  -Deliverable .agent/sev/reports/FORGE_CODEX_CLI_BOOT_WITNESS_2026-03-07.md
```

Expected current machine reality on 2026-03-07:

- native registry still empty
- launcher should select `http-bridge`
- boot-witness deliverable should be rewritten

---

## 6. Known Limitations

1. Native Codex MCP is still not configured on this machine, so the launcher currently lands on `http-bridge`, not `native`.
2. The verification environment used for this slice has a 300-second outer timeout; long `codex exec` runs may complete their artifacts after that wrapper stops waiting.
3. The launcher depends on `codex.cmd` being on `PATH`.
4. User-home Codex config edits remain out of scope for this slice.

---

## 7. Bottom Line

The first repo-first Codex CLI launcher slice now exists and successfully drove one real boot-witness packet through:

- a repo-tracked PowerShell launcher
- a repo-tracked prompt compositor
- a real `codex exec` run
- a real deliverable write

The remaining gap is not launcher design. It is the known host reality: Codex CLI on this machine still uses `http-bridge` instead of native MCP, and long automation wrappers should allow more than 300 seconds for full return-path observation.
