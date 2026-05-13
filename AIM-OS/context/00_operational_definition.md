# AIM-OS Operational Definition (Current)

Last updated: 2026-03-05 03:22 ET
Scope: pass/fail operational gates for current MVP

## Core Definition

### Baseline Operational (no-auth)

AIM-OS baseline is operational if all no-auth gates below pass in one session:

1. MCP transport and execution
- `GET http://localhost:5001/health` -> `status=ok`, `ready=true`
- `POST http://localhost:5001/mcp/execute` with `tool=get_memory_stats` -> `success=true`
- `POST http://localhost:5001/mcp/execute` with `tool=get_ai_messages` -> `success=true`

2. BAS runtime and browser lifecycle
- `GET http://localhost:5002/health` -> `status=ok`
- Browser flow passes:
  - `POST /api/browser/launch`
  - `POST /api/browser/navigate` to ChatGPT
  - `GET /api/browser/status`
  - `POST /api/browser/close`

3. Build/test baseline
- `packages/browser-automation-service`: `npm run build` passes
- `packages/browser-automation-service`: `npm test` passes
- `packages/joc`: `npm run build` passes

4. MCP registry parity
- `python scripts/check_mcp_tool_parity.py` -> `parity_ok=true` and listed==callable

### Authenticated ChatGPT Gate (separate)

For full ChatGPT browser-loop validation, an authenticated provider session is required before claiming response extraction success:

- `POST /api/bridge/send-prompt` with `waitForResponse=true` returns `success=true` with a real response payload
- `POST /api/bridge/extract-response` returns non-empty response from provider page

If provider login is missing, this gate is `PENDING_AUTH` (not baseline pass).

## Non-Goals of this Gate

- Full multi-provider optimization
- Repo-wide cleanup of all legacy/prototype surfaces
- Clean git tree

## Failure Condition

- Any failed baseline gate = not operational.
- Authenticated gate may remain `PENDING_AUTH` until operator login is completed.
