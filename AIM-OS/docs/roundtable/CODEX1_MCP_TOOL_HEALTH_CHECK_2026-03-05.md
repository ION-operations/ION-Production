# Codex1 MCP Tool Health Check (2026-03-05)

Timestamp: 2026-03-05 03:38 ET  
Operator: Codex1 (Codex Agent runtime identity lock)

## Objective
Verify MCP tool plane is live and callable before any further runtime work.

## Evidence Checks

1. `GET http://localhost:5001/health`
- Result: `status=ok`, `ready=true`, `mode=fallback-http-bridge`

2. `GET http://localhost:5002/health`
- Result: `status=ok`

3. `GET http://localhost:5001/mcp/list`
- Result: `success=true`, `count=103`

4. `POST http://localhost:5001/mcp/execute` (`get_memory_stats`)
- Result: `success=true`
- Memory backend reports operational stats from CMC/SQLite path

5. `POST http://localhost:5001/mcp/execute` (`get_ai_messages`, thread scope)
- Result: `success=true`, recent messages returned

6. `python scripts/check_mcp_tool_parity.py`
- Result: `listed_count=103`, `callable_count=103`, `parity_ok=true`

## Identity Lock Note
`send_ai_message` requires matching `holder_id` when sender lock exists.  
Current lock file: `.agent/comms/identity_session_locks.json`  
Working sender tuple: `from_ai="Codex Agent"`, `holder_id="codex_primary_20260304T1300"`

## Conclusion
MCP tools are currently operational and callable.  
Canonical status for MCP layer at this checkpoint: **HEALTHY**.
