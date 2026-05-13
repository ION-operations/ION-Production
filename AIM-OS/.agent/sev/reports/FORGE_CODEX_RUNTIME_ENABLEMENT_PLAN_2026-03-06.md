# FORGE Codex Runtime Enablement Plan - 2026-03-06

**Mission ID:** FORGE-001-codex-runtime-enablement  
**Author:** Forge (candidate, Codex CLI host)  
**Output:** Evidence-backed Codex runtime enablement plan  
**Scope:** Codex CLI project layer, home transport/rules surfaces, first implementation slice

---

## 1. Executive Summary

1. **Codex CLI currently has no AIM-OS project instruction layer:** there is no repo-root `AGENTS.md`, no repo `.codex/` layer, and no `C:\Users\bombe\.codex\AGENTS.md` or `AGENTS.override.md`.

2. **Current Codex docs use `AGENTS.md`, not `codex.md`:** the local platform doc's Codex section is still marked preliminary. The smallest reliable project injection point is a tracked `AGENTS.md` bootstrap file at repo root.

3. **Home MCP config exists but is not proven active in the current CLI:** `C:\Users\bombe\.codex\config.toml` declares `lucid-mcp` under `[mcp.servers.lucid-mcp]`, but `codex mcp list` on `codex-cli 0.111.0` reports `No MCP servers configured yet.` Treat the current config shape as drifted until migrated or regenerated.

4. **The AIM-OS MCP backend itself is live:** `POST http://localhost:5001/mcp/execute` with `get_memory_stats` returned success in this run. That proves the repo MCP stack is reachable locally, but it does not prove Codex CLI is consuming it natively.

5. **`default.rules` is active but wrong for AIM-OS governance:** `codex execpolicy check` matched `C:\Users\bombe\.codex\rules\default.rules` allow rules, but the file is dominated by ProFlow-specific command prefixes. Keep rules as approval policy, not identity/runtime doctrine.

6. **The smallest viable enablement slice is bootstrap plus transport proof, not `packages/agent_genome/` first:** add a repo-tracked `AGENTS.md`, add a Codex layer/verification doc, then repair home MCP registration. Defer runtime packaging until the host layer is proven stable.

7. **Cursor Codex must remain separate until Relay closes the host question:** do not assume repo `AGENTS.md`, home rules, or MCP behavior carry from Codex CLI into Cursor Codex.

8. **Forge should package doctrine, not rewrite it:** Sev/Opus own the identity and governance text. Forge's job is to bind that text to Codex entry points and verification steps.

---

## 2. Enablement Target

A minimally governed Codex lane should include all of the following:

- A repo-root `AGENTS.md` that acts as the Codex bootstrap layer.
  - It should require identity assignment before work.
  - It should route the agent through `.agent/STARTUP.md`, `.agent/COMMS_DOCTRINE.md`, `.agent/workflows/startup.md`, and the matching genome/packet.
  - It should explicitly state that candidate identities like `FORGE`, `RELAY`, and `PALISADE` are task-local unless Sev promotes them.

- A repo-tracked Codex reference doc that explains:
  - the supported instruction surfaces (`AGENTS.md`, `~/.codex/config.toml`, `~/.codex/rules/*.rules`)
  - which surfaces are project-scoped versus user-home scoped
  - the last verified transport path
  - the manual operator steps to re-establish the lane on a fresh machine

- A live MCP path that Codex CLI itself can enumerate and use.
  - Minimum proof: `codex mcp list` shows `lucid-mcp`.
  - Minimum proof: a fresh Codex session can successfully call one lightweight tool such as `get_memory_stats`.

- A bounded approval surface in `~/.codex/rules/*.rules`.
  - Approval rules should allow safe AIM-OS work.
  - They should not carry ProFlow-specific drift into every Codex repo.

- A verification witness doc with a dated proof of zero-context boot plus MCP reachability.

---

## 3. Smallest Viable Implementation Slice

### Step 1 - Add the repo bootstrap layer first

Add a root `AGENTS.md` for Codex. Keep it narrow:

- identify the assigned callsign
- read `.agent/STARTUP.md`
- load the right genome or packet based on operator assignment
- follow `.agent/COMMS_DOCTRINE.md` header and status rules
- prohibit silent canon rewrites and unverified cross-host claims

Why first:

- it is repo-tracked
- it does not touch user-home config
- it gives Codex a deterministic project entry point immediately

### Step 2 - Add the Codex reference and verification docs

Add a short Codex project layer doc and a verification runbook/witness. The AGENTS file should stay compact; the reference doc can hold the longer explanations, transport notes, and operator steps.

Why second:

- it creates a durable source of truth for future edits
- it gives Relay and Opus somewhere concrete to point when comparing hosts

### Step 3 - Repair native Codex MCP registration

Do not treat the current `config.toml` as trusted until Codex itself sees the server. Re-register `lucid-mcp` with the current CLI (`codex mcp add ...`) or migrate `config.toml` to the schema recognized by `codex-cli 0.111.0`, then verify with `codex mcp list`.

Why third:

- current HTTP success proves the repo MCP server is live
- current Codex CLI evidence says its native MCP registry is still empty
- this is the smallest host-layer change that turns "MCP-ready on paper" into "MCP working in Codex"

### Step 4 - Clean up command approval drift

Once MCP is confirmed, split AIM-OS-safe command rules from ProFlow-specific rules. The goal is not broad lock-down; the goal is preventing unrelated rule baggage from defining AIM-OS Codex behavior.

Why fourth:

- rules are active today
- rules cleanup is useful, but not a blocker for the first governed lane if the AGENTS layer and MCP are already working

### Defer until after the host layer is proven

Defer the following from slice 1:

- `packages/agent_genome/` runtime scaffolding
- capability/loadout gating beyond basic AGENTS boot plus MCP reachability
- any claim that Cursor Codex inherits the same layer as Codex CLI
- broad doctrine rewrites outside the Codex surfaces

---

## 4. Exact File Plan

| Phase | Path | Action | Purpose |
|------|------|--------|---------|
| Slice 1 | `AGENTS.md` | add | Codex project bootstrap: identity selection, startup sequence, comms header, packet loading, and scope guardrails |
| Slice 1 | `docs/CODEX_PROJECT_RULE_LAYER.md` | add | Human-readable explanation of Codex instruction surfaces, manual setup, and ownership boundaries |
| Slice 1 | `docs/CODEX_RUNTIME_VERIFICATION_2026-03-07.md` | add | Dated witness log for zero-context boot, `codex mcp list`, tool-call proof, and regression checks |
| Slice 1 | `docs/GENOME_INJECTION_PROTOCOLS_BY_PLATFORM.md` | edit | Replace preliminary Codex `codex.md` language with verified `AGENTS.md` plus home config/rules surfaces |
| Slice 1 | `.agent/sev/IDE_CONFIGURATION_MATRIX_2026-03-06.md` | edit | Update Codex CLI row after implementation so the matrix reflects the new project layer and real MCP status |
| Slice 1 | `C:\Users\bombe\.codex\config.toml` | edit | Migrate or regenerate Codex-native MCP registration so `codex mcp list` shows `lucid-mcp` |
| Slice 1 | `C:\Users\bombe\.codex\rules\aimos.rules` | add | AIM-OS-specific approval rules, separated from unrelated ProFlow rules |
| Slice 1 or later | `C:\Users\bombe\.codex\rules\default.rules` | edit | Reduce or archive ProFlow-biased allow rules once the new AIM-OS rule file is proven safe |
| Deferred | `packages/agent_genome/__init__.py` | add | Package entry point for a future runtime slice |
| Deferred | `packages/agent_genome/registry.py` | add | Agent registry primitives |
| Deferred | `packages/agent_genome/genome_manager.py` | add | Genome loading and snapshot management |
| Deferred | `packages/agent_genome/clone_api.py` | add | Clone lifecycle API |
| Deferred | `packages/agent_genome/promotion_gate.py` | add | Promotion gate API |
| Deferred | `packages/agent_genome/tests/test_registry.py` | add | Registry validation coverage |
| Deferred | `packages/agent_genome/tests/test_clone_api.py` | add | Clone isolation coverage |

---

## 5. Verification Plan

1. **Bootstrap proof**
   - Start a brand-new `codex` session from the repo root after `AGENTS.md` exists.
   - Give only the task-local assignment prompt, for example `You are agent FORGE`.
   - Pass criteria:
     - the agent follows the startup read order instead of acting immediately
     - it loads the named packet/genome
     - it adopts the required response header
     - it does not invent a different identity

2. **AGENTS precedence proof**
   - Place the repo under a parent directory with no conflicting `AGENTS.md`, or note any parent/global file if present.
   - Pass criteria:
     - repo `AGENTS.md` is sufficient by itself
     - no hidden `~/.codex/AGENTS.md` or override is required

3. **Native MCP proof**
   - Run `codex mcp list`.
   - Pass criteria:
     - `lucid-mcp` appears in the list
   - Then start a fresh Codex session and ask for one MCP-backed action such as `get_memory_stats`.
   - Pass criteria:
     - tool succeeds from inside Codex, not only from shell HTTP

4. **Approval rules proof**
   - Run `codex execpolicy check` for one allowed AIM-OS command and one command that should not auto-allow.
   - Pass criteria:
     - AIM-OS safe command matches `aimos.rules`
     - unrelated ProFlow rules are no longer the only active allow surface

5. **Regression proof**
   - Restart Codex CLI and rerun steps 1-4.
   - Record the results, exact version, and timestamp in `docs/CODEX_RUNTIME_VERIFICATION_2026-03-07.md`.

6. **Baseline evidence already available from this packet**
   - `codex-cli 0.111.0`
   - `codex mcp list` returned no configured servers
   - `codex execpolicy check` confirmed `default.rules` is still active
   - `http://localhost:5001/mcp/execute` returned successful `get_memory_stats`

---

## 6. Risks and Dependencies

- **Risk: MCP config schema drift.** The on-disk `config.toml` does not currently produce any registered servers in `codex mcp list`. Back up the file before any migration.

- **Risk: repo-root `AGENTS.md` affects every Codex session in this repo.** Keep it as a bootstrap layer, not an agent-specific persona or a global canon rewrite.

- **Risk: home rules are shared across projects.** Editing `default.rules` carelessly could break non-AIM-OS workflows. Prefer adding `aimos.rules` first, then trimming `default.rules`.

- **Dependency: Relay.** Relay must verify whether Cursor Codex reads the same project layer, the same home config, or a different host-injected surface. Until then, this plan applies to Codex CLI only.

- **Dependency: Sev and Opus.** The bootstrap text should reference existing doctrine, not rewrite it. If the AGENTS layer needs new identity language, that language should be approved upstream.

- **Dependency: operator tolerance for home-directory changes.** Slice 1 can add repo files immediately, but native Codex MCP enablement still requires a user-home change or `codex mcp add` action.

---

## 7. Evidence Notes

**Read in this run:**  
`.agent/STARTUP.md`, `.agent/COMMS_DOCTRINE.md`, `.agent/sev/ACTIVE_COMMAND_WAVE_01_2026-03-06.md`, `.agent/sev/IDE_CONFIGURATION_MATRIX_2026-03-06.md`, `.agent/sev/candidate_genomes/forge.genome.md`, `.agent/sev/mission_packets/FORGE_MISSION_PACKET_2026-03-06.md`, `.agent/genomes/GENOME_PROTOCOL.md`, `docs/GENOME_INJECTION_PROTOCOLS_BY_PLATFORM.md`, `docs/AGENT_BUILDING_AND_CLONING_SYSTEM_SPEC_V3.md`, `docs/AGENT_BUILDING_AND_CLONING_SYSTEM_SPEC_V2.md`, `docs/CODEX_IDE_MCP_ONBOARDING_V1.md`, `docs/GENOME_INJECTION_VERIFICATION_AND_REGRESSION_2026-03-05.md`, `docs/AUDIT_01_SYSTEM_MAP.md`, `.agent/workflows/startup.md`, `C:\Users\bombe\.codex\config.toml`, `C:\Users\bombe\.codex\rules\default.rules`, `packages/specialist_system/*`, `.agent/sev/reports/PALISADE_DOCTRINE_DRIFT_MAP_2026-03-06.md`.

**Verified commands in this run:**  
`codex --version`, `codex mcp list`, `codex execpolicy check`, and `POST http://localhost:5001/mcp/execute` for `get_memory_stats`.

**External host reference checked in this run:**  
Current OpenAI Codex documentation for `AGENTS.md` and advanced config/rules behavior, checked 2026-03-07.

**Not claimed in this report:**  
- that Cursor Codex is governed by the same layer as Codex CLI  
- that the current `config.toml` MCP stanza is active inside Codex CLI  
- that `packages/agent_genome/` should be built before the host layer is proven

*FORGE | DELIVERABLE | Codex runtime enablement plan complete. No host config mutated.*
