# AIMOS Activation-Wiring Surface Comparison - 2026-03-14

Work package: `CONSOLIDATION_WORK_PACKAGE_22_2026-03-14`

This comparison stays inside evidence only.
It does not choose an activation canon or turn bridge health into proof that all dependent capabilities are equally healthy.

| Surface family | Startup guidance clarity | Actual launch or recovery power | Transport-surface specificity | Host-connection specificity | Freshness of readiness proof | Failure visibility | Operator readability | Drift or wiring-gap tendency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Startup or runbook surfaces | Highest; they explain the intended order and fallback law most clearly | Low by themselves; they instruct but do not start anything | Medium; they name `:5001`, `/health`, and `/mcp/execute`, but only descriptively | Medium; they distinguish Codex, Cursor, JOC, and ChatGPT paths at a prose level | Low; they are not per-run evidence | Medium; they mention degraded mode and recovery steps, but do not expose live failures directly | Highest; they are built for human startup and recovery | Medium to high; prose can drift from the actual active route, caller identity, or transport behavior |
| Bootstrap or control-script surfaces | Medium to high; less explanatory than runbooks but still legible | Highest; these are the only surfaces that can directly ensure, restart, test, or bootstrap the active bridge | High; `mcp_control.ps1` explicitly checks `/health`, `/mcp/list`, and `/mcp/execute` on `:5001` | Medium; they operate at bridge level rather than per-host client semantics | Medium to high; they actively probe readiness during execution | High; `ensure`, `test`, and status output make readiness failure explicit | Medium; concise but more tool-operator oriented than prose docs | Medium; they can prove bridge readiness even when deeper host or subsystem wiring remains uneven |
| Bridge or server surfaces | Low to medium; code reveals behavior, but not in a startup-order form | High; they are the actual transport and endpoint implementations | Highest; this family defines endpoint shapes, ports, and protocol boundaries | Medium; clients depend on them, but host-specific semantics live elsewhere | Medium; code is current implementation, not current host state | Medium to high; endpoint shape mismatches and unsupported tools are visible in code | Medium to low; exact but slower to scan | High; this family visibly contains multiple server shapes and protocol assumptions at once |
| Host-adapter or client surfaces | Medium; each host shows its own connection assumptions | Medium; they can connect or fail, but they do not recover the bridge globally | Medium; they expose the endpoints they expect, but only from the client side | Highest; this family shows how JOC, ide chat, and antigravity actually try to consume MCP | Medium; code is current host-adapter intent, not a live session result | Medium; some errors are surfaced, but some mismatches are hidden behind retries or cached assumptions | Medium; clearer than server internals, denser than runbooks | Highest; host clients are visibly non-uniform in ports, protocols, and even whether they use HTTP at all |
| Live readiness probe surfaces | Low; they show outcomes, not onboarding sequence | Medium; they do not launch or rewire, but they confirm whether launch succeeded | High; they prove the active endpoint behavior right now | High; they show what the current host can actually reach and what dependent calls return | Highest; each probe is current-run evidence | Highest; failures and partial readiness show immediately | Medium; direct but terse | Lowest for present readiness truth, but narrow if mistaken for total-system wiring proof |

## Direct Comparative Reading

- Startup and runbook surfaces are strongest at telling operators and agents how activation is supposed to work, but they are not proof that the host is actually wired that way right now.
- Bootstrap and control scripts are strongest at causing or checking bridge recovery, because they directly call health, list, and execute endpoints and can restart the fallback bridge.
- Bridge and server surfaces are strongest at defining what transport surfaces exist at all, but the family is visibly plural rather than singular.
- Host-adapter clients are strongest at revealing how concrete hosts really attempt to connect, and the visible sample set shows those hosts do not all consume MCP through the same path.
- Live readiness probes are strongest at proving the current host state, but they only prove the slices they exercise.

## Visible Activation and Wiring Contradictions

1. `docs/MCP_RUNBOOK.md` declares Codex should use HTTP fallback and gives bootstrap examples for `sev`, while the active workspace route for this session is `codex`.
2. `scripts\mcp.cmd status` reported a ready bridge with `tools=103` and `total_atoms=701`, but the same status output could not confirm the fallback process via Win32 process inspection and reported `Fallback server process: NOT FOUND`.
3. `scripts/mcp_http_fallback_server.py` exposes `/health`, `/mcp/list`, and `/mcp/execute`, while `packages/mcp_server/server.py` exposes `/mcp/tools/list` and `/mcp/tools/call` with only four listed tools, so the visible server family is not one unified transport shape.
4. `packages/joc/src/services/mcpClient.ts` rotates across `:5001` and `:5003`, `packages/ide_chat_app/src/services/mcpApi.ts` assumes `:5001` and an "extension command server", while `packages/antigravity-extension/src/services/mcpClient.ts` reads SQLite and JSON directly for reads and hardcodes `toolCount: 93`.
5. Live bridge readiness did not imply subsystem readiness: `/health` was healthy and `get_ai_messages(...)` succeeded, but `get_hhni_status(...)` returned `hhni_index_initialized=false`, `retriever_available=false`, and `cmc_error="tuple index out of range"`.

## Evidence Boundaries

- Startup and runbook prose were treated as activation guidance only.
- Control scripts were treated as launch and recovery machinery, not as proof that every dependent subsystem is healthy after launch.
- Bridge and server code were treated as transport implementation evidence, not as proof of the currently active server choice.
- Host-adapter clients were treated as host-consumption intent and wiring evidence, not as proof they all use the same path successfully right now.
- Live probes were treated as the freshest readiness evidence, but only for the slices they actually touched.
