# AIMOS Surface Specialization And Inactivity Register - 2026-03-14

Work package: `CONSOLIDATION_WORK_PACKAGE_06_2026-03-13`
Correction packet: `.agent/sev/CONSOLIDATION_CORRECTION_PACKET_2026-03-14.md`
Status: comparative candidates only; not a removal list

Pattern labels in this register are comparative only:
- `duplicated`
- `narrow-purpose`
- `auxiliary`
- `dormant`
- `unknown`

## 1. JOC and operator-surface cluster

| Path | Pattern observed | Direct evidence | Best-known current role or value | Uncertainty note |
| --- | --- | --- | --- | --- |
| `packages/joc/` | `duplicated` | `package.json` describes a "Joint Operations Center" browser-based command surface; `src/` has `122` files; package uses React, Vite, Electron, Monaco, and Zustand | Most substantial local browser JOC shell and dispatch/session UI surface in this checkout | Off-branch JOC work could change how this surface compares to other operator shells. |
| `IDE/` | `auxiliary` | `package.json` has only Tauri scripts; `IDE/src/main.js` points at JOC `5011`, MCP `5001`, and BAS `5002`; `src/` has `3` files total | Lightweight desktop wrapper and service monitor around the existing JOC runtime ports | The local shell is small; external host usage could make it more important than the local source size suggests. |
| `packages/ide_chat_app/` | `duplicated` | `package.json` names `ide-chat-app`; `src/` has `222` files; `README_STANDALONE.md` frames it as a standalone dashboard launcher with Lucid Orchestrator telemetry | Separate Electron/chat/dashboard lane with a larger app body than `IDE/` | Relationship to newer off-branch UI work remains outside this machine. |
| `packages/joc-tournament/` | `narrow-purpose` | `README.md` frames a JARVIS UI tournament; tree contains `builds/`, `references/`, and `shared/`; surface has `10314` files across heritage and build corpora | Research, comparison, and heritage surface around the JOC design lane | Tournament outputs on other machines or branches may broaden the comparative picture. |

## 2. Echo Forge cluster

| Path | Pattern observed | Direct evidence | Best-known current role or value | Uncertainty note |
| --- | --- | --- | --- | --- |
| `echo-forge-loop/` | `duplicated` | root `package.json` names `echo-forge-loop`; `src/` has `155` files; `README.md` frames a 9-phase cognition pipeline with mission-control UI and chat | Full-stack product surface that visualizes AIM-OS cognition and run traces | Off-branch Echo Forge work may change how complete this local slice is. |
| `echo-forge-loop/server/` | `narrow-purpose` | `README.md` defines this subtree as the FastAPI SSE backend; subtree has `46` files; `requirements.txt` lists `fastapi` and `uvicorn` | Backend execution and event-stream surface for the Echo Forge loop | Deployed or alternate server variants are not inspectable from this machine. |
| `echo-forge-loop/supabase/` | `auxiliary` | subtree contains `21` files; `README.md` explicitly includes Supabase as the cloud mode / persistence path | Cloud and hosted persistence adjunct to the local Echo Forge app | Actual remote Supabase state is outside local verification scope. |

## 3. Host-adapter and console cluster

| Path | Pattern observed | Direct evidence | Best-known current role or value | Uncertainty note |
| --- | --- | --- | --- | --- |
| `packages/antigravity-extension/` | `duplicated` | `package.json` describes live MCP metrics, ghost bridge status, agent comms, and system health; `src/` has `13` TypeScript files; multiple `.vsix` builds are stored locally | Antigravity-specific host dashboard and messaging surface for AIM-OS agents | Live host behavior and off-branch Antigravity work are not fully visible here. |
| `cursor-addon/` | `duplicated` | `package.json` describes AIM-OS MCP integration; `src/` has `40` files including `commandServer.ts`, `mcp/mcpClient.ts`, and dashboard providers | Cursor-specific extension and local HTTP automation bridge into the AIM-OS MCP tool plane | Archived variants and packaged builds show a longer history than this one source pass can fully compare. |
| `packages/lucid_core_console/` | `auxiliary` | `package.json` describes voice I/O, phone remote control, and hard gates on file mutations; `src/` has `9` TypeScript files | Separate console/control surface with emphasis on approval, voice, and daemon-mediated mutation control | Relative live use in the current workflow is not verified from this pass alone. |

## 4. Transport and bridge cluster

| Path | Pattern observed | Direct evidence | Best-known current role or value | Uncertainty note |
| --- | --- | --- | --- | --- |
| `packages/mcp_server/` | `auxiliary` | importable package exists locally; local import graph shows dependencies on `agent`, `cmc_service`, `hhni`, `llm_client`, `seg`, and `vif` | Package-based MCP surface that sits on the same core dependency spine as the repo-root daemon | Exact runtime selection between this surface and the repo-root daemon can vary by host or branch. |
| `scripts/mcp_http_fallback_server.py` | `narrow-purpose` | runtime dependency truth map and runbook both point to this bridge for non-stdio hosts | HTTP bridge surface for Codex-family hosts that do not spawn MCP over stdio directly | Health, host, and readiness settings vary by session. |
| `packages/mcp_rag_proxy/` | `narrow-purpose` | `requirements.txt` lists `numpy`, `scikit-learn`, and `nltk`; local import graph shows a single dependency on `hhni` | Retrieval/RAG adjunct rather than a general control plane | Runtime activation was not separately verified in this pass. |
| `packages/router_api_server/` | `auxiliary` | importable package exists; local import graph shows dependencies on `router` and `log_sentinels`; requirements artifact mixes dependency lines and setup notes | API exposure layer around routing and logging surfaces | Install or deployment shape may differ after packaging cleanup or on other branches. |

## 5. Packaging-only or currently unclear surfaces

| Path | Pattern observed | Direct evidence | Best-known current role or value | Uncertainty note |
| --- | --- | --- | --- | --- |
| `packages/cmc_service.egg-info/` | `dormant` | directory exists under `packages/` with none of the normal top-level package markers used in this pass | Packaging metadata attached to `cmc_service`, not a standalone runtime module | Low uncertainty in this checkout. |
| `packages/shared/` | `unknown` | directory exists locally without `__init__.py`, `package.json`, `requirements.txt`, or `pyproject.toml` | Shared-material surface is present on disk but not classifiable as an importable Python package under the current simple rule | Other branches or non-Python tooling may give this surface a clearer role. |
| `packages/timeline_context_system/` | `unknown` | directory exists locally without `__init__.py`; AST scan still found one local dependency on `cmc_service` in contained Python files | Timeline-related code surface with partial local structure but incomplete top-level packaging marker | Off-branch context may clarify whether this is intentionally un-packaged or only partially carried here. |

## 6. Net reading

1. The strongest comparative overlap is in operator shells and host adapters, not in the core kernel packages.
2. Echo Forge is internally differentiated into app, backend, and hosted-persistence sub-surfaces rather than one monolithic lane.
3. Several auxiliary or narrow-purpose surfaces still preserve useful specialization even when they are not the central local runtime path.
4. `dormant` and `unknown` labels here are descriptive only. They are not disposal recommendations.
