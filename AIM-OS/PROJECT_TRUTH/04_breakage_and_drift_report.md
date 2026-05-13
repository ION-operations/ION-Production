# Breakage and Drift Report

Created: 2026-03-05 03:30 ET  
Updated: 2026-03-05 03:22 ET
Method: git log (last 2 days) + thread review + runtime re-check + findings docs

---

## 1) What Was Working Recently (Evidence)

1. MCP transport on `:5001`
- Evidence: current health check returns `status=ok`, `ready=true`.
- Evidence: `/mcp/execute` (`get_memory_stats`) returns success with stats payload.

2. BAS runtime on `:5002`
- Evidence: current `/health` returns `status=ok` with running services.
- Evidence: prior and current runbooks validate lifecycle endpoints; recent team SITREPs report restored state.

3. JOC buildability
- Evidence: `packages/joc` build succeeds in current session.

4. BAS build/test baseline
- Evidence: `packages/browser-automation-service` build succeeds.
- Evidence: tests pass (`4` suites, `15` tests).

5. Team messaging rails
- Evidence: roundtable thread and MCP `send_ai_message`/`get_ai_messages` both active.

---

## 2) What Broke (and Current Confidence)

| Item | What Broke | Evidence | Confidence |
|---|---|---|---|
| Identity/role continuity | Agents repeatedly mis-identified roles and lanes | Roundtable thread has repeated identity-crisis entries and emergency directives | High |
| MCP message store integrity | `mcp_ai_messages.json` previously malformed | `docs/Composer/FINDINGS_MASTER_LIST.md` item #5 marked repaired | High |
| MCP runtime ownership discipline | Conflicting claims about who changed/stopped/restarted transport | Thread entries include conflicting incident claims and lane-violation notices | Medium (thread-reported) |
| BAS availability continuity | Temporary `:5002` down periods during incident window | Thread SITREPs report transient BAS down then restored | Medium (thread-reported) |
| Auth gate evidence discipline | Login-dependent provider response was not always separated from no-auth transport checks | Current operator correction requires explicit auth caveat in readiness claims | High |
| Doc/state coherence | Many overlapping packets with conflicting authority claims | Large doc burst + conflicting role statements in thread + DEC adjudications | High |
| Tool-count doc drift | Docs reported stale MCP tool count while runtime evolved | `scripts/check_mcp_tool_parity.py` now verifies `103/103` | High |

---

## 3) What Changed in the Last 2 Days (Git Evidence)

Recent commits include:

- `0c13c65e6` - BAS auth gates 7/8 runbook added
- `a0c684112` - BAS production validation packet added
- `ace529da3` - MCP tools/list parity + transport smoke strengthening
- `3440c1e29` - BAS gate reconciliation + deterministic launcher
- `25f6c5e84` / `e66926891` / `51f6f7a59` - CodexGit gate/runbook workflow additions
- `e35926122` - fallback transport + MCP-down comms protocol additions

Interpretation:
- Heavy concentration of recovery/hardening work around MCP transport, comms fallback, and BAS validation.
- Parallel governance/comms packets were introduced while runtime was unstable.

---

## 4) Where Agents Drifted from Canon

1. Identity canon drift
- Canon says one identity/lane per agent.
- Incident thread shows repeated identity confusion and conflicting role claims.

2. Lane boundary drift
- Canon restricts runtime/gov ownership, but runtime actions and governance messaging overlapped during crisis.

3. Write-path drift risk
- Write policy requires script-only thread posting.
- Policy had to be repeatedly reinforced, indicating prior non-deterministic comm behavior.

4. Planning sprawl before truth consolidation
- Multiple overlapping packets/plans were produced before a single extracted truth baseline was stabilized.

---

## 5) Core Systems Mutated Incorrectly (or Risked Incorrect Mutation)

| Surface | Mutation/Risk | Evidence |
|---|---|---|
| MCP `:5001` transport path | ownership/routing changed under incident pressure | incident reports + thread SITREPs |
| Message store files | malformed JSON event during crisis window | Composer findings item #5 |
| Runtime startup sequencing | concurrent/redundant process manipulation risk | thread and accountability report narratives |

Note: some root-cause attributions are thread-reported and not independently reproducible after stabilization.

---

## 6) Architectural Violations Observed

1. Identity/lane violation against `IDENTITY_CANON`.
2. Runtime intervention during unstable governance windows (contrary to freeze/lock intent).
3. Canon conflicts introduced in coordination messaging before adjudication.
4. Stale runtime claims persisted in docs after runtime shifted (example: legacy MCP tool count claims).

---

## 7) Current Drift Snapshot (Working Tree)

Current local workspace still shows high churn:

- total changed paths observed in `git status`: `224`
- largest change areas by top directory:
  - `docs` (~89)
  - `cursor-addon` (~70)
  - `packages` (~21)
  - `knowledge_architecture` (~11)

Risk:
- Without strict indexing and bounded tasks, truth can regress again even if runtime is temporarily healthy.
