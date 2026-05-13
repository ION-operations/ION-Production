# FORGE Mission Packet - Codex CLI Boot Witness - 2026-03-07

**Status:** Approved follow-on packet
**Mission owner:** Sev
**Assigned specialist:** FORGE
**Recommended host:** Codex CLI first, GPT-5.4 lane acceptable for packet prep
**Mission class:** Boot witness / transport verification / operator-proof demo
**Output location:** `.agent/sev/reports/FORGE_CODEX_CLI_BOOT_WITNESS_2026-03-07.md`

---

## 1. Mission ID + Intent

**Mission ID:** `FORGE-003-codex-cli-boot-witness`

**Mission objective:** Prove one named Codex CLI lane can boot from AIM-OS doctrine, determine its live MCP mode, perform one coordination action, and write a witness artifact that a non-coder operator can verify.

---

## 2. Read This First

1. `AGENTS.md`
2. `.agent/STARTUP.md`
3. `.agent/COMMS_DOCTRINE.md`
4. `.agent/sev/candidate_genomes/forge.genome.md`
5. `.agent/sev/reports/FORGE_CODEX_CLI_AGENT_FACTORY_PLAN_2026-03-07.md`
6. `.agent/sev/activation_briefs/FORGE_CODEX_CLI_BOOT_WITNESS_2026-03-07.md`

---

## 3. Scope Boundaries

### 3.1 In scope

- named Codex CLI boot proof for `FORGE`
- live MCP mode detection
- one coordination action
- one witness report
- one fresh `forge.status.md` update

### 3.2 Out of scope

- repairing native Codex MCP registration
- editing user-home Codex config
- broad runtime packaging
- Cursor Codex verification

---

## 4. Required Behavior

1. Confirm the active identity is `FORGE`.
2. State the doctrine files loaded.
3. Detect MCP mode in this order:
   - native Codex registry
   - HTTP bridge at `http://localhost:5001/health`
   - degraded filesystem-only mode
4. Attempt one coordination action:
   - if MCP is live, use `get_ai_messages` or `send_ai_message`
   - if MCP is down, write a filesystem comms note explaining degraded mode
5. Write the witness report.
6. Update `.agent/comms/status/forge.status.md`.

---

## 5. Required Deliverable

Create:
- `.agent/sev/reports/FORGE_CODEX_CLI_BOOT_WITNESS_2026-03-07.md`

Required sections:

1. **Identity**
   - agent name
   - host
   - startup files loaded
2. **MCP mode**
   - `native`, `http-bridge`, or `degraded-no-mcp`
   - exact proof command/result
3. **Coordination action**
   - what was attempted
   - whether it succeeded
4. **Status trace**
   - path updated
   - timestamp
5. **Operator check**
   - simple pass/fail checklist
6. **Next move**
   - what should happen after the witness result

---

## 6. Critical Notes

- Do not assume the HTTP bridge remains healthy just because it was healthy earlier. Verify live.
- Do not claim native Codex MCP works unless `codex mcp list` proves it.
- If both native MCP and HTTP are unavailable, degraded mode is valid if clearly declared.
- The point of this packet is proof, not ambition.

---

## 7. Definition of Done

Mission is done when:
- the witness report exists at the specified path
- it names `FORGE`
- it states the exact MCP mode used
- it proves one coordination action or one explicit degraded fallback
- `forge.status.md` is freshly updated
