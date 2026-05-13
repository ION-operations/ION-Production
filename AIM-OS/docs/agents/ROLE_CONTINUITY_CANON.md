# Role Continuity Canon

> **DEPRECATED (2026-03-05)** — Superseded by `docs/roundtable/IDENTITY_CANON.md`.  
> This file reflects pre-handoff roles (Aether=CEO, Codex=COO). Current canon: Braden=CEO, Opus=COO, Codex=specialist. Do not use for new decisions.

Date: 2026-03-04  
Status: deprecated  
Purpose: prevent agent-role drift across parallel chats/sessions.

---

## 1) Canonical Roles

- `Agent Aether` = CEO / program governance owner
  - Owns strategic adjudication, priority arbitration, and lane-go/no-go.
- `Codex Agent` = COO / execution owner
  - Owns implementation integration, runtime hardening, gate evidence, and delivery sequencing.
- `Claude Opus 4.6` = JOC primary builder
  - Owns JOC UI/app implementation lane under CEO/COO governance.
- `Composer` = independent auditor
  - Owns findings, seam checks, and verification reports.

---

## 2) Canonical Sender IDs

Allowed IDs for control-plane coordination:

1. `Agent Aether`
2. `Codex Agent`
3. `Claude Opus 4.6`
4. `Composer`

Alias handling rule:
- If alias appears (`Aether`, `Opus1`, `Antigravity`, etc.), include explicit normalization line in next update:
  - `Normalized identity: <alias> -> <canonical id>`

---

## 3) Mission Thread Canon

Primary governance thread:
- `aimos_24h_operational_convergence_2026-03-02`

Recovery thread (MCP-down fallback):
- `aimos_recovery_codex_aether_2026-03-04`

Lane threads:
- `aimos_task_codex_mcp_fixes_2026-03-03`
- `aimos_task_codex_bas_hardening_2026-03-03`
- `aimos_task_codex_context_contract_2026-03-03`

---

## 4) Runtime Ownership Rule

At any time, exactly one runtime action owner is allowed for start/stop/restart commands affecting:

- MCP transport (`5001`, `5003`)
- BAS (`5002`)
- JOC dev server (`5011`)
- related launcher scripts

Lock token format:
- `LOCK:HELD_BY=<canonical id>`
- `LOCK:RELEASED`

No process command is valid without a currently held lock.

---

## 5) Session Rehydration Checklist

Every new agent session must read, in order:

1. `docs/ROLE_CONTINUITY_STATE.md`
2. `docs/agents/ROLE_CONTINUITY_CANON.md`
3. `docs/AIM_OS_PRIME_COO_24H_OPERATIONAL_CONVERGENCE_PACKET_V1.md`
4. `docs/COO_ROUNDTABLE_OPERATIONAL_AUDIT_AND_EXECUTION_PLAN_V1_2026-03-03.md`

Then post a continuity check message:

`[CONTINUITY_ACK] <canonical id> role=<role> thread=<active thread> lock=<state>`

---

## 6) Violation Response

If two agents issue runtime commands concurrently:

1. Immediate stop on both sides.
2. Record event in MCP-down thread.
3. Reassign lock owner explicitly.
4. Resume only after lock ACK by both CEO and COO.

