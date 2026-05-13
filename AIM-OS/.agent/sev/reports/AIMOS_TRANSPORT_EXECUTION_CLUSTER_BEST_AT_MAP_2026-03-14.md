# AIMOS Transport Execution Cluster Best-At Map - 2026-03-14

Work package: `CONSOLIDATION_WORK_PACKAGE_12_2026-03-14`
Status: evidence-only comparative answer map

## Best-At Answers

| Surface | What it appears best at locally | Where it seems narrower than siblings | Unique value preserved locally | Direct evidence |
| --- | --- | --- | --- | --- |
| `packages/agent/` | Best at embodying AIM-OS capabilities as conscious, memory-native, orchestrating agents rather than as raw infrastructure pieces | Narrower than `mcp_server` in external transport exposure, narrower than `router` in explicit tool-routing policy, and narrower than `prompt_chain_executor` in dedicated chain-definition execution | Preserves the clearest persona-bearing layer in this cluster through AetherAgent, OrchestrationAgent, and ConsciousAgent | `README.md` frames three layers of consciousness; `__init__.py` exports the agent types; dependency graph records `agent` as a heaviest core consumer |
| `packages/mcp_server/` | Best at exposing conscious-agent and memory-backed capabilities outward through a package-local MCP/API server surface | Narrower than `agent` in embodied cognition logic, narrower than `router` in route-selection intelligence, and narrower than `prompt_chain_executor` in chain-specific execution semantics | Preserves the clearest package-local MCP tool surface in this cluster, including ask, remember, retrieve, and knowledge bootstrap flows | `README.md` describes the MCP-compliant tool surface; `server.py` wires LLMs, memory, HHNI, SEG, VIF, and agent logic into callable request handlers |
| `packages/router/` | Best at deciding which tools should be called and how a tool-call plan should be assembled and validated | Narrower than `mcp_server` in endpoint transport, narrower than `llm_client` in direct provider access, and narrower than `prompt_chain_executor` in executing a chain once chosen | Preserves the strongest explicit observe-propose-score-plan-validate loop in the cluster, including scout, bandit, rules, snapshot, manifest, and cache logic | `README.md` documents Router, ScoutLLM, BanditScorer, and RouterCache; `core/router.py` shows the routing control loop and learning hooks |
| `packages/llm_client/` | Best at abstracting multiple model providers behind one consistent contract | Narrower than `agent` in embodiment, narrower than `mcp_server` in MCP transport, narrower than `router` in routing logic, and narrower than `prompt_chain_executor` in execution flow | Preserves the shared provider contract that lets higher layers swap Gemini, Anthropic, or Cerebras without changing their own response handling model | `README.md` frames unified provider access; `__init__.py` exports standardized provider clients; `base.py` defines the common response and error model |
| `packages/prompt_chain_executor/` | Best at running defined prompt chains with branching, gates, state persistence, and MCP-triggered execution | Narrower than `router` in open-ended tool selection, narrower than `mcp_server` in broad transport exposure, and narrower than `agent` in full embodied consciousness behavior | Preserves the clearest chain-runner surface in the cluster, including stateful step execution, quality gates, confidence routing, and CMC-backed chain retrieval | `__init__.py` exports `ChainExecutor` plus MCP helper; `executor.py` implements branching, gates, and persisted state; `mcp_integration.py` retrieves chain definitions from CMC and executes them |

## Net Comparative Answer

1. `packages/agent/` appears best at conscious agent embodiment.
2. `packages/mcp_server/` appears best at MCP-facing transport and exposure.
3. `packages/router/` appears best at intelligent tool routing and plan assembly.
4. `packages/llm_client/` appears best at multi-provider model access.
5. `packages/prompt_chain_executor/` appears best at dynamic chain execution.

The map stays comparative. It does not declare a single operational center.
