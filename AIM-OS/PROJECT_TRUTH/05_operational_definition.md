# Operational Definition

Created: 2026-03-05 03:30 ET  
Scope: pass/fail criteria only

---

## Operational Tonight = ALL Gates Pass

### Gate G1 - MCP health

Command:
```powershell
Invoke-RestMethod http://localhost:5001/health
```

Pass:
- response includes `status = ok`
- response includes `ready = true`

Fail:
- connection refused/timeout
- any non-ok status

### Gate G2 - MCP tool execution (memory)

Command:
```powershell
$body = @{ tool='get_memory_stats'; arguments=@{} } | ConvertTo-Json
Invoke-RestMethod -Uri http://localhost:5001/mcp/execute -Method Post -ContentType 'application/json' -Body $body
```

Pass:
- top-level `success = true`
- nested result contains memory stats payload

Fail:
- execution error / non-success response

### Gate G3 - MCP tool execution (collaboration)

Command:
```powershell
$body = @{ tool='get_ai_messages'; arguments=@{ thread_id='aimos_roundtable_operational_convergence_2026-03-04'; limit=5 } } | ConvertTo-Json -Depth 6
Invoke-RestMethod -Uri http://localhost:5001/mcp/execute -Method Post -ContentType 'application/json' -Body $body
```

Pass:
- `success = true`
- result returns message list/count

Fail:
- tool call failure or malformed result

### Gate G4 - BAS health

Command:
```powershell
Invoke-RestMethod http://localhost:5002/health
```

Pass:
- response `status = ok`

Fail:
- BAS not reachable or not ok

### Gate G5 - BAS browser lifecycle flow

Commands (sequence):
```powershell
$launch = Invoke-RestMethod -Uri http://localhost:5002/api/browser/launch -Method Post -ContentType 'application/json' -Body (@{headless=$true;viewport=@{width=1280;height=720}}|ConvertTo-Json -Depth 5)
$bid = $launch.browserId
Invoke-RestMethod -Uri http://localhost:5002/api/browser/navigate -Method Post -ContentType 'application/json' -Body (@{browserId=$bid;url='https://chat.openai.com'}|ConvertTo-Json)
Invoke-RestMethod -Uri "http://localhost:5002/api/browser/status?browserId=$bid"
Invoke-RestMethod -Uri http://localhost:5002/api/browser/close -Method Post -ContentType 'application/json' -Body (@{browserId=$bid}|ConvertTo-Json)
```

Pass:
- each step returns `success = true`
- status call returns title/url data

Fail:
- any step fails or returns invalid browser ID

### Gate G6 - JOC build

Command:
```powershell
cd packages/joc
npm run build
```

Pass:
- exit code `0`

Fail:
- TypeScript/Vite build failure

### Gate G7 - BAS build + tests

Commands:
```powershell
cd packages/browser-automation-service
npm run build
npm test
```

Pass:
- build exit code `0`
- tests all pass

Fail:
- build or tests fail

### Gate G8 - MCP tool parity

Command:
```powershell
python scripts/check_mcp_tool_parity.py
```

Pass:
- `parity_ok = true`
- `listed_count = callable_count`

Fail:
- parity script exits non-zero
- listed/callable mismatch

---

## Optional Visibility Gate (recommended)

### Gate G9 - JOC dev surface reachable

Command:
```powershell
Invoke-WebRequest http://localhost:5011/
```

Pass:
- returns HTML for JOC app shell

---

## Final Pass/Fail Rule

- **Operational tonight = G1 through G8 all pass in one session.**
- Any failed gate = not operational.

---

## Authenticated Gate Policy (Separate from Baseline)

### Gate A1 - Authenticated prompt+response proof (ChatGPT)

Commands:
- follow `docs/BAS_AUTH_GATES_7_8_PROOF_RUNBOOK_2026-03-04.md`

Pass:
- Gate 7 (`send-prompt`, `waitForResponse=true`) succeeds with authenticated provider session
- Gate 8 (`extract-response`) returns non-empty provider response content

Pending:
- if provider login is missing or expired, mark **`PENDING_AUTH`**

Guardrail:
- never count transport-only success as authenticated response proof
