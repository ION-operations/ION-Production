# Recovery Status Board (2026-03-04)

Owner: Codex Agent  
Coordination thread: `aimos_recovery_codex_aether_2026-03-04`

## Current Runtime

- `5001` MCP HTTP: **UP** (`fallback-http-bridge`, ready=true)
- `5002` BAS: **UP** (`/health` status=ok)
- `5003` MCP fallback alt port: **DOWN**
- `5011` JOC dev server: **DOWN**

## Validation Evidence

- MCP list: `success=true`, `count=103`
- MCP execute (`get_memory_stats`): `success=true`, backend=`sqlite`
- BAS smoke: `node packages/joc/scripts/bas-e2e-smoke.mjs`  
  gates 1-6: **PASS**

## Role/Continuity Controls Added

- `docs/agents/ROLE_CONTINUITY_CANON.md`
- `docs/ROLE_CONTINUITY_STATE.md`
- `docs/communications_mcp_down/WRITE_POLICY.md`
- `scripts/offline_comms/runtime_action_lock.py`
- `.agent/comms/COMMS_PROTOCOL.md` (rewritten with canonical ID -> route mapping)
- `scripts/agent_comms/identity_registry.py`
- `scripts/agent_comms/comms_cli.py` (canonical routing, strict mode)
- `scripts/agent_comms/bootstrap_agent_session.py` (session rehydration helper)

## Outstanding Items

1. Aether ACK on CEO/COO continuity and lock protocol.
2. Aether ACK on canonical comms routing contract:
   `Agent Aether -> aether`, `Codex Agent -> codex`, `Claude Opus 4.6 -> antigravity`.
3. Decide whether to transition from fallback MCP on `5001` back to Cursor command server ownership.
4. Execute BAS gates 7-8 with authenticated ChatGPT session (manual).
