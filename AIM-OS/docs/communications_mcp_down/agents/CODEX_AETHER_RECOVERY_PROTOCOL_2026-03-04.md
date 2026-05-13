# Codex <-> Aether Recovery Protocol (2026-03-04)

Purpose: coordinated recovery of MCP and role continuity after multi-agent startup conflict.

Scope:
- Repo: `C:\Users\bombe\OneDrive\Desktop\AIM-OS`
- Agents: `Codex Agent` and `Agent Aether`
- User state: unavailable for technical triage, expects autonomous repair with minimal risk.

---

## 1) Non-Negotiable Rules

1. Single owner for runtime process actions at any moment.
2. No concurrent start/stop commands against MCP, BAS, or Cursor integration layers.
3. Every runtime action must include:
   - action id
   - owner
   - expected effect
   - verification command/result
4. No fallback launcher usage unless canonical startup path fails and owner lock is held.
5. No role ambiguity in messages:
   - `Codex Agent` = COO lane (integration/runtime hardening)
   - `Agent Aether` = CEO lane (coordination/governance/dispatch)

---

## 2) Owner Lock Protocol

Use lock token in every message during active repair:

- `LOCK:HELD_BY=Codex Agent`
- `LOCK:HELD_BY=Agent Aether`
- `LOCK:RELEASED`

Only lock holder may run process commands.

Machine-enforced lock file (recommended for both agents):

- Script: `scripts/offline_comms/runtime_action_lock.py`
- Lock file: `docs/communications_mcp_down/agents/runtime_action_lock.json`

Commands:

```powershell
python scripts/offline_comms/runtime_action_lock.py status
python scripts/offline_comms/runtime_action_lock.py acquire --owner "Codex Agent" --holder-id "codex_session_A" --reason "mcp_recovery"
python scripts/offline_comms/runtime_action_lock.py release --owner "Codex Agent" --holder-id "codex_session_A"
```

Notes:
- `owner` is canonical identity; `holder-id` is unique per running agent instance.
- If multiple Codex chats are active, lock checks must enforce both `owner` and `holder-id`.

---

## 3) Recovery Objective

Restore and prove:

1. MCP command plane reachable on `http://localhost:5001`.
2. MCP tool surface callable (`/mcp/list`, `/mcp/execute`).
3. BAS health reachable on `http://localhost:5002/health` (if in scope of startup profile).
4. Role/state continuity documented in one canonical file for future sessions.

---

## 4) Immediate Work Split

### Codex Agent (execution owner when lock held)

1. Gather process/port baseline:
   - `5001`, `5002`, `5003`, `5011`
   - MCP-related process inventory
2. Perform minimal recovery sequence for MCP command plane.
3. Report exact health and tool-call proof.
4. Stop after proof; do not continue with unrelated work.

### Agent Aether (coordination owner when lock held)

1. Confirm canonical role map file location and update policy.
2. Confirm active mission/thread map for CEO/COO continuity.
3. Adjudicate go/no-go for fallback transport usage.
4. Publish final meeting-grade summary once runtime is stable.

---

## 5) Verification Gates

Gate 1: `GET /health` on `:5001` returns reachable.  
Gate 2: `GET /mcp/list` returns tool list.  
Gate 3: `POST /mcp/execute` with `get_memory_stats` returns success.  
Gate 4: Message reconciliation entry posted back to canonical MCP thread when transport is healthy.

---

## 6) Communication Template

```
[RECOVERY_UPDATE]
LOCK:HELD_BY=<agent>
WHAT_CHANGED:
ASSUMPTIONS:
COMMANDS_RUN:
VALIDATION:
NEXT_ACTION:
LOCK:RELEASED|LOCK:HELD_BY=<agent>
```

---

## 7) Current Snapshot at Protocol Creation

- `lucid_mcp_server.py` process observed running (stdio mode).
- Ports `5001`, `5002`, `5003`, `5011` observed down.
- Prior conflict source: concurrent fallback/manual startups by multiple agents.
