# AIMOS 4-Axis Classification Matrix - 2026-03-13

Status: descriptive evidence matrix for `CONSOLIDATION-WORK-PACKAGE-01`

Notes:
- This matrix is descriptive only. It does not propose a target architecture.
- A surface can appear in more than one axis in reality. Each row below records the most visible evidence path in this pass.
- `MCP` is treated here as one transport/adapter family, not as the whole system.

## 1. Kernel / Core

| Surface | Primary evidence path | Evidence tag | Current note |
|---|---|---|---|
| CMC | `packages/cmc_service/`; `.agent/sev/reports/RUNTIME_TRUTH_MAP_2026-03-13.md` | `direct-evidence` | package present; truth map marks it alive |
| HHNI | `packages/hhni/`; `.agent/sev/reports/RUNTIME_TRUTH_MAP_2026-03-13.md` | `direct-evidence` | package present; truth map marks retrieval broken/not initialized |
| VIF | `packages/vif/`; `.agent/sev/reports/RUNTIME_TRUTH_MAP_2026-03-13.md` | `direct-evidence` | package present; truth map marks it partial/unused |
| APOE | `packages/apoe/`; `.agent/sev/reports/RUNTIME_TRUTH_MAP_2026-03-13.md` | `direct-evidence` | package present; truth map marks live verification incomplete |
| SEG | `packages/seg/`; `.agent/sev/reports/RUNTIME_TRUTH_MAP_2026-03-13.md` | `direct-evidence` | package present; truth map marks live verification incomplete |
| CAS | `packages/cas/`; `.agent/sev/reports/RUNTIME_TRUTH_MAP_2026-03-13.md` | `direct-evidence` | package present; truth map marks it degraded |
| SIS | `packages/sis/`; `.agent/sev/reports/RUNTIME_TRUTH_MAP_2026-03-13.md` | `direct-evidence` | package present; truth map marks live verification incomplete |
| SDF-CVF | `packages/sdfcvf/`; `.agent/sev/reports/RUNTIME_TRUTH_MAP_2026-03-13.md` | `direct-evidence` | package present; truth map marks live verification incomplete |
| timeline context system | `packages/timeline_context_system/` | `direct-evidence` | local core-adjacent surface exists, but current directory scan counts it as non-importable in this checkout |

## 2. Transport / Adapters

| Surface | Primary evidence path | Evidence tag | Current note |
|---|---|---|---|
| Lucid MCP server | `lucid_mcp_server.py` | `direct-evidence` | root transport surface present |
| MCP HTTP fallback | `scripts/mcp_http_fallback_server.py` | `direct-evidence` | local HTTP bridge surface present |
| legacy MCP server | `packages/mcp_server/` | `direct-evidence` | local legacy server package present |
| MCP data integration | `packages/mcp_data_integration/` | `direct-evidence` | local integration package present |
| MCP RAG proxy | `packages/mcp_rag_proxy/` | `direct-evidence` | local proxy surface present; counted as non-importable in this pass |
| AI Engine MCP server | `scripts/ai_engine/ai_engine_mcp_server.py` | `direct-evidence` | local slim MCP server surface present |
| Browser Automation Service | `packages/browser-automation-service/`; `packages/joc/src/services/basClient.ts` | `direct-evidence` | adapter surface between JOC and browser automation present |
| AIMOS relay / ChatGPT bridge | `scripts/aimos_relay/` | `direct-evidence` | relay surface for browser/ChatGPT connectivity present |
| Gemini bridge host | `scripts/aimos_bridge_host.py`; `scripts/aimos_bridge.json` | `direct-evidence` | local native host adapter for Gemini bridge present |
| JOC MCP client | `packages/joc/src/services/mcpClient.ts` | `direct-evidence` | client-side adapter from JOC to MCP present |
| Antigravity extension MCP client | `packages/antigravity-extension/src/services/mcpClient.ts` | `direct-evidence` | extension-side MCP client present |

## 3. Habitats / Hosts

| Surface | Primary evidence path | Evidence tag | Current note |
|---|---|---|---|
| Cursor Codex lane | `AGENTS.md`; `.agent/comms/chat/codex/2026-03-13.md` | `direct-evidence` | current working host for this pass |
| Codex standalone / CLI lane | `AGENTS.md`; `scripts/ai_engine/providers/codex_cli_provider.py` | `direct-evidence` | Codex-family host surface is explicitly routed in repo controls |
| Antigravity IDE lane | `AGENTS.md`; `packages/antigravity-extension/` | `direct-evidence` | Antigravity host surface and local extension code both exist |
| Gemini CLI lane | `AGENTS.md`; `scripts/ai_engine/providers/gemini_cli_provider.py`; `packages/antigravity-extension/src/services/geminiClient.ts` | `direct-evidence` | CLI habitat surface is present in both provider and extension layers |
| browser / ChatGPT lane | `scripts/aimos_relay/`; `scripts/security.py`; `scripts/sentinel_host_baselines.py` | `direct-evidence` | browser habitat surface is present through relay and host-baseline code |
| JOC / Electron surface | `packages/joc/`; `IDE/` | `direct-evidence` | operator-facing app habitat exists in multiple local surfaces |
| Cursor addon surface | `cursor-addon/` | `direct-evidence` | local Cursor-related habitat support surface exists |
| other-laptop branch / JOC evolution | `.agent/comms/chat/sev/2026-03-13.md`; `.agent/sev/CONSOLIDATION_WORK_PACKAGE_01_2026-03-13.md` | `operator-reported-only`; `inaccessible` | named habitat/branch exists in the evidence chain but is not reachable from this machine |

## 4. Model Runtimes

| Surface | Primary evidence path | Evidence tag | Current note |
|---|---|---|---|
| OpenAI / ChatGPT browser runtime | `scripts/aimos_relay/`; `scripts/security.py`; `scripts/sentinel_host_baselines.py` | `direct-evidence` | direct repo evidence exists for ChatGPT/OpenAI-facing relay, CORS, and host-baseline handling |
| Anthropic / Claude runtime | `packages/llm_client/anthropic.py` | `direct-evidence` | local client adapter code present |
| Gemini API runtime | `packages/llm_client/gemini.py`; `scripts/seer/discovery.py` | `direct-evidence` | local API client and Gemini vision/image paths present |
| Gemini CLI runtime | `scripts/ai_engine/providers/gemini_cli_provider.py`; `packages/antigravity-extension/src/services/geminiClient.ts`; `scripts/seer/gemini_integration.py` | `direct-evidence` | local CLI runtime adapters present in multiple layers |
| local model runtime (Ollama) | `packages/antigravity-extension/src/services/ollamaClient.ts` | `direct-evidence` | local-model integration surface present in Antigravity extension code |
| Cerebras runtime | `packages/llm_client/cerebras.py` | `direct-evidence` | additional model runtime adapter present locally |

## 5. Matrix Notes

- the repo directly shows all four requested axes: kernel/core packages, transport/adapter code, multiple habitats/hosts, and multiple model runtime integrations.
- the evidence is uneven across axes: filesystem/code presence is strong, but live verification is not uniform across every host and runtime in this pass.
- the model-runtime axis is not limited to one provider family. Direct evidence exists for ChatGPT/OpenAI browser relay handling, Anthropic client code, Gemini API and CLI paths, local Ollama integration, and Cerebras client code.
