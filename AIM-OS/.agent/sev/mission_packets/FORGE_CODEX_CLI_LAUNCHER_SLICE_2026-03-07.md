# FORGE Mission Packet - Codex CLI Launcher Slice - 2026-03-07

**Status:** Approved implementation slice
**Mission owner:** Sev
**Assigned specialist:** FORGE
**Recommended host:** GPT-5.4 or Codex CLI
**Mission class:** Repo-first implementation / launcher / prompt compositor / verification
**Output location:** `.agent/sev/reports/FORGE_CODEX_CLI_LAUNCHER_SLICE_RESULT_2026-03-07.md`

---

## 1. Mission ID + Intent

**Mission ID:** `FORGE-004-codex-cli-launcher-slice`

**Mission objective:** Implement the first repo-first Codex CLI launcher slice that can boot a named AIM-OS lane using existing doctrine files, select MCP mode, and run the bounded FORGE boot-witness packet end to end.

---

## 2. Preconditions Already Proven

- FORGE-002 plan is accepted.
- FORGE-003 boot witness passed.
- Current proven Codex CLI transport on this machine is `http-bridge`, not native Codex MCP.
- User-home Codex config edits are still out of scope.

---

## 3. Read This First

1. `AGENTS.md`
2. `.agent/STARTUP.md`
3. `.agent/COMMS_DOCTRINE.md`
4. `.agent/sev/reports/FORGE_CODEX_CLI_AGENT_FACTORY_PLAN_2026-03-07.md`
5. `.agent/sev/reports/FORGE_CODEX_CLI_BOOT_WITNESS_2026-03-07.md`
6. `.agent/sev/mission_packets/FORGE_CODEX_CLI_BOOT_WITNESS_2026-03-07.md`
7. `scripts/agent_comms/bootstrap_agent_session.py`
8. `scripts/run_mcp_http_fallback.ps1`

---

## 4. Required Implementation Scope

### 4.1 Must implement

- `scripts/launchers/start_codex_agent.ps1`
- `scripts/agent_comms/render_codex_activation.py`
- one short operator runbook for the launcher
- one result report proving the slice worked or naming the exact failure point

### 4.2 May update if needed

- `.agent/comms/status/forge.status.md`
- `.agent/sev/INDEX.md`

### 4.3 Out of scope

- editing `C:\Users\bombe\.codex\config.toml`
- editing `C:\Users\bombe\.codex\rules\default.rules`
- changing MCP server code
- broad agent runtime packaging
- Cursor Codex host work

---

## 5. Exact Target Behavior

The launcher should:

1. accept at minimum:
   - `-Agent`
   - `-ActivationBrief`
   - `-MissionPacket`
   - `-Deliverable`
2. validate that the named files exist
3. detect MCP mode in this order:
   - `codex mcp list`
   - `http://localhost:5001/health`
   - degraded mode
4. call a prompt compositor that combines:
   - `AGENTS.md`
   - `.agent/STARTUP.md`
   - `.agent/COMMS_DOCTRINE.md`
   - selected activation brief
   - selected mission packet
5. run `codex exec` non-interactively
6. write the last agent message to the requested deliverable path
7. print a short summary including:
   - chosen MCP mode
   - deliverable path
   - pass/fail

---

## 6. Reuse Rule

Do not rebuild local comms/bootstrap logic blindly. Reuse or borrow from:
- `scripts/agent_comms/bootstrap_agent_session.py`

Keep the first implementation simple. It does not need to become a general agent framework yet.

---

## 7. Required Deliverable

Create:
- `.agent/sev/reports/FORGE_CODEX_CLI_LAUNCHER_SLICE_RESULT_2026-03-07.md`

Required sections:

1. **What was implemented**
2. **Files added or changed**
3. **How the launcher works**
4. **Verification run**
   - exact command used
   - actual MCP mode chosen
   - actual result
5. **Operator instructions**
6. **Known limitations**

---

## 8. Verification Requirement

You must attempt one real verification run using the FORGE boot-witness packet.

Pass conditions:
- launcher runs
- prompt compositor runs
- deliverable file is written
- launcher prints/records the selected MCP mode

If full pass is not possible, return the exact failing step and why.

---

## 9. Definition of Done

Mission is done when:
- the launcher exists
- the compositor exists
- the result report exists
- one real run was attempted
- the operator has a repeatable repo-first Codex CLI command to use next time
