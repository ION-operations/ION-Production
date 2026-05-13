# Already-Built Registry

Created: 2026-03-05 03:26 ET  
Purpose: prevent reinvention; force integration-first execution  
Rule: if listed here, default posture is **DO NOT REBUILD**

---

## Registry

| System | Canonical Path(s) | Current State | Integration Needed | DO NOT REBUILD |
|---|---|---|---|---|
| MCP monolith server | `lucid_mcp_server.py` | Implemented; callable through bridge (`/mcp/execute`) | Stabilize ownership/routing discipline only | YES |
| MCP HTTP fallback bridge | `scripts/mcp_http_fallback_server.py` | Running on `:5001` and healthy | Keep transport canonical; avoid duplicate startup races | YES |
| MCP/BAS launch-control scripts | `scripts/mcp_control.ps1`, `scripts/run_mcp_http_fallback.ps1`, `scripts/launchers/START_BAS_DETERMINISTIC.ps1` | Implemented with health-gated lifecycle behavior | Deconflict old launcher usage and document canonical startup path | YES |
| MCP tool registry and parity guards | `lucid_mcp_server.py`, `scripts/check_mcp_tool_parity.py` | Implemented; parity currently `103/103` | Keep docs in sync with actual tool count and parity checks | YES |
| MCP collaboration/message persistence | `mcp_ai_messages.json`, `codex_workspace/persistence/collaboration/codex_ai_messages.json` | Live message flow working; prior corruption incident documented | Maintain lock/write discipline | YES |
| Browser Automation Service (BAS) | `packages/browser-automation-service/` | Health/build/tests pass; browser lifecycle verified | JOC seam hardening and reliability iteration | YES |
| JOC app shell | `packages/joc/` | Build passes; app serves on `:5011` | Resolve dispatch/session seam and BAS-target wiring | YES |
| JOC/BAS bridge endpoints | `packages/browser-automation-service/src/api/mcpBridge.ts` | Implemented endpoint surface exists | Align with JOC dispatch/store flow | YES |
| Rust context mapper live seam | `IDE/src-tauri/src/context_mapper/*`, `IDE/src-tauri/src/context_service.rs` | Substantial implementation present | Controlled integration/validation, not rebuild | YES |
| Shadow sync prototype | `context_capsule_wire_and_mapper_v1/shadow_sync/*` | Standalone prototype with tests/artifacts | Keep additive; promote slices intentionally | YES |
| Context canon registry | `docs/CONTEXT_SYSTEM_CANON_REGISTRY_2026-03-05.md` | Canon tier map recorded (A/B/S/D/E) | Enforce lane-tier assignment before context work | YES |
| Timeline context system (deferred canon) | `packages/timeline_context_system/*` | Broad implementation with duplicate variants | Dedupe + promotion-gate proof before canon promotion | YES |
| CMC memory service | `packages/cmc_service/*` | Implemented package + MCP memory stats operational | Keep runtime contracts aligned; avoid parallel memory stack | YES |
| HHNI retrieval stack | `packages/hhni/*` | Implemented package/test surfaces | Re-enable/runtime-wire where currently unavailable | YES |
| APOE orchestration stack | `packages/apoe/*`, `packages/apoe_runner/*` | Implemented packages and tests exist | Integrate with current live path intentionally | YES |
| Specialist/agent activation system | `packages/specialist_system/*` | Implemented package/tests and registry model present | Wire into runtime decisions instead of role-chaos | YES |
| Agent genome operational identity layer | `.agent/genomes/*`, `.agent/genomes/GENOME_PROTOCOL.md` | Live identity packets and loading protocol present | Align with evolving V3 cloning design without rebuilding base identity layer | YES |
| Roundtable/offline comms protocol | `scripts/offline_comms/*`, `docs/communications_mcp_down/*`, `docs/roundtable/*` | In active use during MCP instability | Keep single write policy and lock protocol | YES |
| ChatGPT context packaging workflow | `context/*`, `scripts/package_chatgpt_context.ps1` | Implemented and producing zip artifacts | Keep ownership cadence through Composer | YES |

---

## Systems Often Rebuilt by Mistake

1. MCP transport/coordination layer
- Already exists in at least two runnable forms (monolith + fallback bridge).
- Failure mode: agents start "new MCP" recovery variants instead of using canonical path.

2. JOC shell/UI
- Core shell exists and builds.
- Failure mode: redesign/re-scaffold instead of fixing specific seams.

3. Agent framework
- Specialist system + genome specs + comms doctrine already exist.
- Failure mode: creating new role schemas without integrating existing runtime pieces.

---

## Enforcement Note

Before any new system proposal, compare against this file first.  
If overlap exists, treat task as integration/hardening unless explicitly authorized otherwise.
