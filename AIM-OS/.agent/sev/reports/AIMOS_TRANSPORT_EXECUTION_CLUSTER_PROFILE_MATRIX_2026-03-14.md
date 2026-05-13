# AIMOS Transport Execution Cluster Profile Matrix - 2026-03-14

Work package: `CONSOLIDATION_WORK_PACKAGE_12_2026-03-14`
Status: evidence-only transport and execution cluster profile matrix

## Surface Matrix

| Surface | Primary technical role | Main files or subsystems visible locally | Strongest visible integrations | Local scale signals | Best-known intended role from docs, code, or tests | Direct evidence |
| --- | --- | --- | --- | --- | --- | --- |
| `packages/agent/` | Agent embodiment and consciousness-layer composition over the core spine | `aether_agent.py`, `orchestration_agent.py`, `conscious_agent.py`, `knowledge_bootstrap.py`, `models.py`, tests | Direct dependency read shows consumption of `apoe`, `cmc_service`, `hhni`, `llm_client`, `sdfcvf`, `seg`, and `vif` | `32` files across `3` subdirectories | Conscious-agent framework that turns model clients plus AIM-OS subsystems into memory-native, orchestrating, and self-aware agents | `README.md` frames AetherAgent, OrchestrationAgent, and ConsciousAgent as three consciousness layers; `__init__.py` exports the agent types and response models; dependency graph marks `agent` as a heaviest consumer |
| `packages/mcp_server/` | Package-based MCP and API transport surface exposing conscious-agent capabilities | `server.py`, `models.py`, tests | `server.py` wires `agent`, `llm_client`, `cmc_service`, `hhni`, `seg`, and `vif`; dependency graph marks `mcp_server` as directly on the same core cluster | `6` files across `2` subdirectories | MCP-compliant server that exposes asking, remembering, retrieval, and knowledge bootstrapping to external clients | `README.md` describes the server as the MCP interface to conscious AI; `server.py` exposes `ask_agent`, `remember`, `retrieve_context`, `build_knowledge`, and health flows |
| `packages/router/` | Tool-selection and routing intelligence layer for planning which tools to call | `core/router.py`, `core/scout.py`, `core/bandit.py`, `core/rules.py`, `core/manifest.py`, `core/snapshot.py`, integrations, types, tests | `README.md` and code tie it to `APOE`, `VIF`, `SEG`, `CMC`, `HHNI`, and `TCS` | `30` files across `8` subdirectories | Intelligent router that builds snapshots, proposes tools, scores them, compiles plans, validates them, and learns from outcomes | `README.md` documents Router, ScoutLLM, BanditScorer, and RouterCache; `__init__.py` exports `Router`, `ScoutLLM`, `BanditScorer`, `RulesEngine`, and `ToolManifest`; `core/router.py` shows the observe-propose-score-plan-validate loop |
| `packages/llm_client/` | Unified model-provider access layer | `base.py`, provider clients `gemini.py`, `anthropic.py`, `cerebras.py`, tests | Dependency graph shows direct consumption by `agent`, `api_service_registry`, `mcp_server`, and `prompt_chain_executor` | `21` files across `3` subdirectories | Standardized multi-provider interface for generation, response normalization, error handling, and provider swapping | `README.md` frames it as a unified multi-provider interface; `__init__.py` exports base types plus Gemini, Cerebras, and Anthropic clients; `base.py` defines `LLMClient`, `LLMResponse`, and provider metadata |
| `packages/prompt_chain_executor/` | Execution-chain engine with branching, gates, state persistence, and MCP-triggered chain runs | `executor.py`, `mcp_integration.py`, tests | Dependency graph marks it as a heaviest consumer of `apoe`, `cmc_service`, `hhni`, `llm_client`, `sdfcvf`, `seg`, and `vif` | `9` files across `3` subdirectories | Chain execution surface that runs prompt-chain definitions with quality gates, confidence routing, state persistence, and optional MCP invocation | `__init__.py` exports `ChainExecutor` and MCP execution helper; `executor.py` implements branching, gates, state, and persistence; `mcp_integration.py` retrieves chain definitions from CMC and runs them through the executor |

## Net Local Reading

1. `agent` is the clearest embodiment layer in this cluster.
2. `mcp_server` is the clearest transport surface in this cluster.
3. `router` is the clearest decision-and-tool-routing surface in this cluster.
4. `llm_client` is the clearest provider-abstraction surface in this cluster.
5. `prompt_chain_executor` is the clearest chain-execution surface in this cluster.
