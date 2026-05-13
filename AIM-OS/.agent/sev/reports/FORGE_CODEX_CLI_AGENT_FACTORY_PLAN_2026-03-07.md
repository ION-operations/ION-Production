# FORGE Codex CLI Agent Factory Plan - 2026-03-07

**Mission ID:** `FORGE-002-codex-cli-agent-factory`  
**Author:** Forge  
**Host scope:** Codex CLI only. This plan does **not** assume Cursor Codex shares the same behavior.

---

## 1. Executive Summary

1. **Codex CLI is present but not yet AIM-OS-ready.** Local truth on 2026-03-07 is `codex-cli 0.111.0`, `codex mcp list` returns no configured servers, and `codex mcp get lucid-mcp` fails.
2. **`C:\Users\bombe\.codex\config.toml` is residue, not proof.** It contains a `lucid-mcp` stanza on disk, but the running CLI does not recognize it.
3. **The current live AIM-OS transport for this lane is HTTP, not native Codex MCP.** `http://localhost:5001/health` returned `status=ok`, `mode=fallback-http-bridge`, `ready=true`.
4. **Repo state has changed since the 2026-03-06 reports.** A repo-root `AGENTS.md` now exists, so older claims that Codex CLI has no repo bootstrap file are stale.
5. **The first serious factory slice should be repo-first, not user-home-first.** Build one launcher that composes existing doctrine files into a generated prompt and runs one named Codex CLI lane end-to-end.
6. **The first demo should use a bounded boot-witness packet, not a large implementation packet.** Prove named boot, packet loading, MCP mode selection, one coordination action, and report output before broader runtime work.
7. **Native Codex MCP remains the preferred steady-state path, but it is a follow-on hardening step.** Do not block the first demo on repairing `codex mcp` if the HTTP bridge is already healthy.
8. **Cursor Codex remains a separate host.** Relay's verification card and this run both support keeping Cursor Codex and Codex CLI separate in doctrine, tooling, and verification.

---

## 2. Current Codex CLI Truth

### 2.1 Verified working now

| Surface | Evidence | Judgment |
| --- | --- | --- |
| Codex CLI binary | `codex --version` -> `codex-cli 0.111.0` | usable local CLI |
| Non-interactive runner | `codex exec --help` shows stdin prompt support and `--output-last-message` | viable wrapper target |
| Native MCP management surface | `codex mcp add/get/list` commands exist | real CLI feature, not configured here |
| Repo bootstrap layer | `AGENTS.md` exists at repo root | repo-level Codex entry point now exists |
| Live AIM-OS bridge | `GET http://localhost:5001/health` -> `fallback-http-bridge`, `ready=true` | current operational MCP path |
| Filesystem comms layer | `.agent/comms/status`, broadcasts, roundtable, `scripts/agent_comms/*` all present | viable persistence and degraded comms layer |

### 2.2 Verified drift or missing pieces

| Surface | Evidence | Judgment |
| --- | --- | --- |
| Native Codex MCP registration | `codex mcp list` -> no configured servers | not working yet |
| Named server lookup | `codex mcp get lucid-mcp --json` -> no server found | config not loaded by CLI |
| Approval rules | `C:\Users\bombe\.codex\rules\default.rules` is ProFlow-heavy | wrong default policy surface for AIM-OS |
| Codex launcher | no AIM-OS Codex launcher exists under `scripts/launchers/` | missing operator entry point |
| Repeatable packet injection | no prompt compositor for Codex CLI exists | still manual |
| Native Codex proof of repo `AGENTS.md` loading | not yet witnessed in a fresh Codex CLI run | must be verified, not assumed |

### 2.3 Explicit conflict to name, not guess through

1. **Transport conflict**
   - `docs/MCP_RUNBOOK.md` says "Codex has no stdio path" and canonizes HTTP fallback only.
   - `AGENTS.md`, `.agent/STARTUP.md`, `.agent/COMMS_DOCTRINE.md`, and the current CLI help all imply Codex-family lanes must check native MCP surfaces first, then HTTP.
   - Local truth: Codex CLI has an MCP registry surface, but it is unconfigured here. HTTP is the only proven transport today.

2. **Bootstrap conflict**
   - Older 2026-03-06 reports said there was no repo-root `AGENTS.md`.
   - Current repo state on 2026-03-07 includes `AGENTS.md`.
   - Judgment: the older reports remain useful historical evidence, but their "no repo bootstrap" conclusion is now stale.

---

## 3. Agent Factory Target

For this phase, "Codex CLI can spawn AIM-OS agents" should minimally mean:

1. The operator can run **one command** and name the agent lane explicitly, for example `FORGE`.
2. The lane receives a **deterministic boot chain**:
   - `AGENTS.md`
   - `.agent/STARTUP.md`
   - `.agent/COMMS_DOCTRINE.md`
   - selected genome
   - selected activation brief
   - selected mission packet
3. The launcher records which MCP mode is active:
   - `native`
   - `http-bridge`
   - `degraded-no-mcp`
4. Codex CLI executes one bounded task and writes one dated deliverable file.
5. The lane leaves at least two durable traces:
   - updated `.agent/comms/status/forge.status.md`
   - one coordination event via live bus or filesystem comms

This is enough to call the lane a real factory slice. It is not yet a full runtime package, clone system, or capability-gating framework.

---

## 4. Smallest Working Demonstration

### 4.1 Demo lane

**Named agent:** `FORGE`  
**Host:** Codex CLI  
**Goal:** prove named boot, packet loading, transport selection, one coordination action, and one report output  
**Recommended demo packet:** add a new bounded packet instead of reusing a large planning packet

Recommended artifacts:

- `.agent/sev/activation_briefs/FORGE_CODEX_CLI_BOOT_WITNESS_2026-03-07.md`
- `.agent/sev/mission_packets/FORGE_CODEX_CLI_BOOT_WITNESS_2026-03-07.md`
- `.agent/sev/reports/FORGE_CODEX_CLI_BOOT_WITNESS_2026-03-07.md`

### 4.2 What the demo packet should require

The boot-witness packet should instruct `FORGE` to do exactly this:

1. confirm identity and required startup read order
2. state whether Codex CLI is using `native` or `http-bridge` MCP
3. poll `get_ai_messages` if MCP is available
4. send one short status update to `Sev` if MCP is available, otherwise write a filesystem comms note
5. write the witness report with the exact files it loaded and the exact MCP mode it used

### 4.3 Practical launcher path

**Primary operator entrypoint:** `scripts/launchers/start_codex_agent.ps1`

Expected command shape:

```powershell
.\scripts\launchers\start_codex_agent.ps1 `
  -Agent FORGE `
  -ActivationBrief .agent/sev/activation_briefs/FORGE_CODEX_CLI_BOOT_WITNESS_2026-03-07.md `
  -MissionPacket .agent/sev/mission_packets/FORGE_CODEX_CLI_BOOT_WITNESS_2026-03-07.md `
  -Deliverable .agent/sev/reports/FORGE_CODEX_CLI_BOOT_WITNESS_2026-03-07.md
```

### 4.4 Wrapper behavior

The wrapper should do five things only:

1. verify `codex --version`
2. detect MCP mode in this order:
   - `codex mcp list`
   - `http://localhost:5001/health`
   - filesystem-only degraded mode
3. generate one prompt bundle from the selected doctrine files
4. run Codex non-interactively:

```powershell
Get-Content $PromptFile -Raw | codex exec -C $RepoRoot --output-last-message $Deliverable -
```

5. print a human-readable pass/fail summary with:
   - chosen MCP mode
   - deliverable path
   - next action if MCP was unavailable

### 4.5 Why this is the right first demo

- It proves the factory can boot a **named** AIM-OS lane instead of a generic chat.
- It exercises the real doctrine stack already on disk.
- It avoids risky user-home mutation on day one.
- It produces an artifact a non-coder can inspect.
- It keeps Codex CLI separate from Cursor Codex while still using the live AIM-OS bridge when available.

---

## 5. MCP Strategy Order

Use this order for **Codex CLI only**:

1. **Native Codex MCP registry**
   - proof command: `codex mcp list`
   - success condition: `lucid-mcp` appears
   - steady-state target: preferred

2. **HTTP fallback bridge**
   - proof command: `GET http://localhost:5001/health`
   - success condition: `status=ok` and `ready=true`
   - current demo expectation on 2026-03-07: this is the live path

3. **Filesystem degraded mode**
   - use `.agent/comms/status`, inbox, broadcasts, and roundtable
   - allowed only when native MCP is absent and the HTTP bridge is down

**Do not use `C:\Users\bombe\.codex\config.toml` as proof of activation.** It is only a configuration hint until `codex mcp list` confirms the registry.

### Follow-on native MCP repair path

After the repo-first demo works, repair native Codex CLI registration with an explicit command such as:

```powershell
codex mcp add lucid-mcp `
  --env "PYTHONPATH=C:\Users\bombe\OneDrive\Desktop\AIM-OS" `
  --env "AIMOS_AI_MESSAGES_FILES=mcp_ai_messages.json;codex_workspace/persistence/collaboration/codex_ai_messages.json" `
  -- python -u C:\Users\bombe\OneDrive\Desktop\AIM-OS\lucid_mcp_server.py
```

Then re-run `codex mcp list` and the boot-witness lane.

---

## 6. Exact File and Runner Plan

### 6.1 First implementation slice: repo-only and demo-safe

| Path | Action | Purpose |
| --- | --- | --- |
| `scripts/launchers/start_codex_agent.ps1` | add | operator-facing entrypoint for named Codex CLI lanes |
| `scripts/agent_comms/render_codex_activation.py` | add | compose `AGENTS.md` + startup + doctrine + genome + brief + packet into one generated prompt |
| `.agent/sev/activation_briefs/FORGE_CODEX_CLI_BOOT_WITNESS_2026-03-07.md` | add | short operator-facing activation brief for the first demo lane |
| `.agent/sev/mission_packets/FORGE_CODEX_CLI_BOOT_WITNESS_2026-03-07.md` | add | bounded demo packet proving boot, transport, comms, and output |
| `docs/CODEX_CLI_AGENT_FACTORY_RUNBOOK.md` | add | non-coder runbook with launcher command, expected outputs, and failure recovery |
| `docs/MCP_RUNBOOK.md` | edit | replace "Codex has no stdio path" with Codex CLI-specific transport order: native registry first, HTTP currently proven |

### 6.2 Second slice: host hardening after the demo proves out

| Path | Action | Purpose |
| --- | --- | --- |
| `C:\Users\bombe\.codex\config.toml` | edit only if still needed | align home config with the registry format Codex CLI actually honors |
| `C:\Users\bombe\.codex\rules\aimos.rules` | add | AIM-OS-specific approval surface separated from ProFlow rules |
| `C:\Users\bombe\.codex\rules\default.rules` | edit later | stop unrelated ProFlow allowlists from defining AIM-OS behavior |
| `.agent/sev/IDE_CONFIGURATION_MATRIX_2026-03-06.md` | edit after proof | update Codex CLI row with the real launcher path and verified transport |

### 6.3 Runner sequence

1. `start_codex_agent.ps1` resolves repo root and validates all input files.
2. The wrapper checks native MCP, then HTTP health, then chooses degraded mode if both fail.
3. `render_codex_activation.py` writes a generated prompt file under a temp/runtime path.
4. The wrapper pipes that prompt into `codex exec`.
5. The wrapper reports:
   - `agent=FORGE`
   - `mcp_mode=<native|http-bridge|degraded-no-mcp>`
   - `deliverable=<path>`
   - `status_update=<written|failed>`

---

## 7. Verification Plan

This is written for a non-coder operator.

### 7.1 Before you run anything

1. Open the AIM-OS folder in File Explorer.
2. Confirm these files exist:
   - `AGENTS.md`
   - `scripts/launchers/start_codex_agent.ps1`
   - `.agent/sev/mission_packets/FORGE_CODEX_CLI_BOOT_WITNESS_2026-03-07.md`
3. If the launcher says the HTTP bridge is missing, start it with:

```powershell
.\scripts\run_mcp_http_fallback.ps1
```

Leave that window open.

### 7.2 Run the demo

In a second PowerShell window at the repo root, run:

```powershell
.\scripts\launchers\start_codex_agent.ps1 `
  -Agent FORGE `
  -ActivationBrief .agent/sev/activation_briefs/FORGE_CODEX_CLI_BOOT_WITNESS_2026-03-07.md `
  -MissionPacket .agent/sev/mission_packets/FORGE_CODEX_CLI_BOOT_WITNESS_2026-03-07.md `
  -Deliverable .agent/sev/reports/FORGE_CODEX_CLI_BOOT_WITNESS_2026-03-07.md
```

### 7.3 What counts as a pass

All of these must be true:

1. The launcher prints a Codex version and does not stop at startup.
2. The launcher prints one MCP mode:
   - `native`, or
   - `http-bridge`
3. The file `.agent/sev/reports/FORGE_CODEX_CLI_BOOT_WITNESS_2026-03-07.md` exists after the run.
4. Inside that file, you can read:
   - the agent name `FORGE`
   - the packet path it loaded
   - the MCP mode it used
5. `.agent/comms/status/forge.status.md` has a fresh timestamp.
6. The witness file says one coordination action succeeded:
   - `get_ai_messages` worked, or
   - a filesystem fallback message/status note was written

### 7.4 What counts as a fail

Treat the demo as failed if any of these happen:

- `codex mcp list` is empty **and** the HTTP bridge health check fails
- no witness report is written
- the report does not name `FORGE`
- the report does not say which MCP mode was used
- no updated `forge.status.md` appears

### 7.5 Graduation rule

Only after the boot-witness demo passes should the same launcher be used for a larger packet such as the current FORGE Phase 2 planning packet.

---

## 8. Risks and Dependencies

### Risks

1. **Unproven automatic AGENTS loading:** repo `AGENTS.md` exists, but Codex CLI still needs a fresh witness proving it auto-loads as expected.
2. **Native MCP schema drift:** the current CLI ignores the on-disk `config.toml` MCP stanza, so user-home changes may still be required.
3. **Shared home-rule risk:** changing `default.rules` too early could break non-AIM-OS work on the same machine.
4. **Stale transport canon:** `docs/MCP_RUNBOOK.md` currently overstates HTTP-only reality for Codex. That must be corrected once the launcher path lands.

### Dependencies

1. **Sev:** approve the bounded boot-witness packet as the first official Codex CLI demo lane.
2. **Relay:** continue to own Cursor Codex verification so this Codex CLI plan does not accidentally broaden into cross-host assumptions.
3. **Operator:** allow a later follow-on pass to repair native `codex mcp` registration once the repo-first demo is proven.

---

## 9. Final Recommendation

Build the first Codex CLI agent-factory slice as a **repo-first launch wrapper** that boots one bounded `FORGE` witness lane through `codex exec`, chooses MCP mode in a strict order, and writes one dated report plus one status update.

Do **not** start with runtime packaging, clone infrastructure, or user-home rewrites. First prove that Codex CLI can repeatedly boot a named AIM-OS lane from repo doctrine and produce one operator-verifiable artifact. That is the smallest serious slice.
