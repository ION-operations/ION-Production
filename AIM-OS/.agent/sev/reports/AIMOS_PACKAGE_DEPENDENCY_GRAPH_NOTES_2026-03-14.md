# AIMOS Package Dependency Graph Notes - 2026-03-14

Work package: `CONSOLIDATION_WORK_PACKAGE_06_2026-03-13`
Correction packet: `.agent/sev/CONSOLIDATION_CORRECTION_PACKET_2026-03-14.md`
Status: evidence-only comparative dependency notes

## 1. Method used in this pass

This note combines four local evidence sources:

1. direct directory scan of `packages/`
2. AST-based scan of Python imports between top-level `packages/*` directories
3. package-manifest reads for `package.json`, `requirements.txt`, and `pyproject.toml`
4. direct reads of repo-root and host-adapter surfaces that wire MCP or JOC runtime paths

The Python import graph in this note is limited to top-level imports that match a visible `packages/*` directory name. It is a useful local dependency slice, not a full semantic build graph.

## 2. Strongest local dependency hubs

### Highest in-degree surfaces in the local Python graph

| Surface | Local dependent count | Direct dependent surfaces observed locally | Reading |
| --- | --- | --- | --- |
| `cmc_service` | `13` | `agent`, `apoe`, `capability_awareness`, `hhni`, `holographic_memory`, `integration_tests`, `intuitive_intelligence_system`, `mcp_server`, `prompt_chain_executor`, `sdfcvf`, `seg`, `timeline_context_system`, `vif` | Strongest local hub across memory, retrieval, orchestration, verification, and server layers. |
| `hhni` | `11` | `agent`, `cmc_service`, `integration_tests`, `intuitive_intelligence_system`, `mcp_rag_proxy`, `mcp_server`, `nl_tags`, `prompt_chain_executor`, `router`, `seg`, `vif` | Retrieval and indexing remain broadly depended on even while runtime health is uneven. |
| `seg` | `10` | `agent`, `cmc_service`, `hhni`, `holographic_memory`, `integration_tests`, `log_sentinels`, `mcp_server`, `prompt_chain_executor`, `router`, `vif` | Knowledge-graph and synthesis logic sits close to the middle of the local graph. |
| `vif` | `9` | `agent`, `capability_awareness`, `integration_tests`, `intuitive_intelligence_system`, `log_sentinels`, `mcp_server`, `prompt_chain_executor`, `router`, `seg` | Confidence and gate logic are wired into several orchestration and routing surfaces. |
| `apoe` | `5` | `agent`, `capability_awareness`, `integration_tests`, `prompt_chain_executor`, `router` | Orchestration is a mid-level hub rather than the single strongest center. |
| `llm_client` | `4` | `agent`, `api_service_registry`, `mcp_server`, `prompt_chain_executor` | Shared model-client surface for agents, API registry, and MCP transport. |
| `sdfcvf` | `4` | `agent`, `integration_tests`, `prompt_chain_executor`, `vif` | Verification math is reused by agent, execution, and confidence paths. |

### Heaviest local consumers in the same graph

| Surface | Local dependency count | Direct dependencies observed locally | Reading |
| --- | --- | --- | --- |
| `agent` | `7` | `apoe`, `cmc_service`, `hhni`, `llm_client`, `sdfcvf`, `seg`, `vif` | Aggregator surface pulling from the main AIM-OS kernel cluster. |
| `integration_tests` | `7` | `apoe`, `cmc_service`, `hhni`, `schemas`, `sdfcvf`, `seg`, `vif` | Broad test coverage layer over the same core cluster. |
| `prompt_chain_executor` | `7` | `apoe`, `cmc_service`, `hhni`, `llm_client`, `sdfcvf`, `seg`, `vif` | Execution surface that depends on both planning and verification primitives. |
| `mcp_server` | `6` | `agent`, `cmc_service`, `hhni`, `llm_client`, `seg`, `vif` | Package-based MCP surface sits directly on the same core runtime cluster. |
| `vif` | `5` | `cas`, `cmc_service`, `hhni`, `sdfcvf`, `seg` | Confidence system depends on both memory/search and verification math. |

## 3. Major dependency families visible from manifests

| Family | Direct evidence | Reading |
| --- | --- | --- |
| React/Vite/Monaco UI stack | `packages/joc/package.json`, `packages/ide_chat_app/package.json`, `echo-forge-loop/package.json`, `packages/lucid_document_editor/package.json` | JOC, IDE chat, Echo Forge, and document-editing surfaces share a modern browser-app dependency family. |
| VS Code extension stack | `packages/antigravity-extension/package.json`, `cursor-addon/package.json`, `packages/lucid_core_console/package.json` | Antigravity, Cursor, and Lucid Core Console are host-adapter or console-style extension surfaces rather than plain Python packages. |
| FastAPI service stack | `echo-forge-loop/server/requirements.txt`, `packages/router_api_server/requirements.txt` | Echo Forge backend and router API surfaces are server-oriented and FastAPI-flavored. |
| Retrieval / science stack | `packages/mcp_rag_proxy/requirements.txt`, `packages/consciousness_analyzer/requirements.txt`, `packages/holographic_memory/requirements.txt`, `packages/scor/requirements.txt` | Retrieval, analysis, and scoring surfaces pull in numerical, ML, and scientific Python dependencies. |

## 4. Cross-surface chokepoints outside the pure Python graph

| Chokepoint surface | Direct evidence | Why it matters |
| --- | --- | --- |
| `lucid_mcp_server.py` | inserts `packages/` into `sys.path`; defaults `SimpleMCPServer(memory_directory="./mcp_memory")` | Repo-root runtime entry point and local mutable-state anchor for the live MCP tool plane. |
| `cursor-addon/src/mcp/mcpClient.ts` and `cursor-addon/src/commandServer.ts` | default server path is workspace-root `lucid_mcp_server.py`; command server listens on `http://localhost:5001` and instantiates `MCPClient` | Cursor host path depends on the repo-root MCP server and a long-lived local bridge. |
| `packages/antigravity-extension/src/services/mcpClient.ts` | joins workspace root with `lucid_mcp_server.py` and `mcp_memory` | Antigravity host path also depends on the same repo-root MCP and local state assumptions. |
| `IDE/src/main.js` | hard-coded service map for JOC `5011`, MCP `5001`, and BAS `5002` | The standalone IDE shell is wired as a service monitor and wrapper around the existing runtime ports. |

## 5. Obvious breakpoints or graph-reading constraints

| Path | Direct evidence | Effect on the dependency reading |
| --- | --- | --- |
| `packages/sis/__init__.py` and `packages/sis/sis_core.py` | import `system_usage_auditor`, `performance_monitor`, `gap_identifier`, `improvement_implementer`, and `continuous_learner`, but those modules are not present on disk | `sis` is present as a package surface but unavailable as a complete local runtime package. |
| `packages/router_api_server/requirements.txt` | file is a triple-quoted setup note containing dependency lines, install instructions, and env examples in one block | The router API dependency surface exists, but the requirements artifact is not a plain install list. |
| `packages/shared/` and `packages/timeline_context_system/` | both directories exist locally without `__init__.py` | These surfaces are present but do not classify as importable Python packages under the simple rule used in this pass. |
| mixed JS/app surfaces under `packages/` | `joc`, `ide_chat_app`, `antigravity-extension`, `advanced_monaco_editor`, `plix`, `lucid_document_editor`, and others carry `package.json` or app-only layouts | Non-importable under the Python rule does not mean absent; it often means the surface is an app or extension rather than a Python module. |

## 6. Net local reading

1. The core runtime graph is concentrated in a small repeat-appearing cluster: `cmc_service`, `hhni`, `seg`, `vif`, `apoe`, `llm_client`, `sdfcvf`, plus transport surfaces that sit on top of them.
2. The host-adapter layer is coupled less by imports than by shared assumptions about repo-root entry points, ports, and local mutable stores.
3. The package tree mixes runtime packages and product habitats in one namespace, so dependency interpretation requires both import scanning and manifest reading.
4. The clearest breakpoints are incomplete `sis` submodules and the non-uniform packaging/install surfaces around router/API and mixed app directories.
