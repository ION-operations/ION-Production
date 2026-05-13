# AIMOS Transport Execution Cluster Capability Comparison - 2026-03-14

Work package: `CONSOLIDATION_WORK_PACKAGE_12_2026-03-14`
Status: evidence-only comparative capability analysis

## Comparative Table

| Comparison axis | `packages/agent/` | `packages/mcp_server/` | `packages/router/` | `packages/llm_client/` | `packages/prompt_chain_executor/` |
| --- | --- | --- | --- | --- | --- |
| Agent embodiment or coordination role | Strongest embodiment layer: packages memory, retrieval, provenance, graph, and quality primitives into agent personas and orchestration behaviors | Exposes embodied agent capabilities outward, but does not itself define the consciousness layers | Coordinates tool choice and tool-call planning rather than embodying an agent persona | No embodiment role; supplies models to embodied or orchestrating layers | Coordinates execution of chain definitions, but not broad embodied agent behavior |
| MCP or transport role | Indirect transport role through surfaces that call it | Strongest MCP and API transport role in the cluster | Uses routing logic that may feed transport, but is not itself the main MCP exposure layer | Provider transport to external model APIs, not MCP transport to AIM-OS tools | Has MCP-triggered execution helper, but is not the primary MCP server surface |
| Routing role | Can orchestrate steps, but not the main tool router | Exposes tools and requests, but does not rank or route tool choices deeply | Strongest routing role: snapshot, scout, bandit, rules, plan compilation, and learning from outcomes | No routing role beyond provider selection by callers | Routes within a chain definition through branching and quality gates, not across the broader tool ecosystem |
| Model-provider role | Consumes model clients as part of agent behavior | Selects default model client and surfaces it through server operations | May rely on models for ScoutLLM logic, but does not define provider abstractions itself | Strongest model-provider role: normalized multi-provider interface and response contract | Uses provider-backed execution indirectly through surrounding systems rather than being the provider layer itself |
| Execution-chain role | Strong on multi-step agent orchestration, but broader and less chain-definition-specific than prompt-chain execution | Invokes agent actions and bootstrap flows, but not the main chain engine | Builds tool-call plans, but does not execute prompt chains as its primary identity | No direct execution-chain role | Strongest execution-chain role: dynamic branching, state tracking, quality gates, and CMC-backed chain retrieval and execution |
| Dependency position relative to the core spine | Heaviest consumer above the spine with `7` direct dependencies into core systems | Directly on top of the spine through `agent`, `cmc_service`, `hhni`, `seg`, `vif`, and `llm_client` | Mid-level operational layer sitting on top of APOE and core trust/memory/retrieval systems | Shared provider surface adjacent to the spine, consumed by multiple higher operational layers | Another heaviest consumer above the spine with `7` direct dependencies into planning, memory, retrieval, trust, and validation |

## Direct Comparative Reading

### `packages/agent/` vs `packages/mcp_server/`

- `packages/agent/` embodies the conscious operational persona.
- `packages/mcp_server/` transports that capability outward as callable tools and server endpoints.

### `packages/router/` vs `packages/prompt_chain_executor/`

- `packages/router/` is strongest at deciding which tools should be called.
- `packages/prompt_chain_executor/` is strongest at executing a defined chain once that execution structure exists.

### `packages/llm_client/` vs the rest of the cluster

- `packages/llm_client/` is the shared provider substrate.
- The other four surfaces sit above it as embodiment, transport, routing, or execution layers.

## Net Comparative Answer

1. `agent` anchors embodiment.
2. `mcp_server` anchors MCP-facing transport.
3. `router` anchors tool routing and plan selection.
4. `llm_client` anchors model-provider access.
5. `prompt_chain_executor` anchors dynamic chain execution.

These are comparative role answers only. They do not declare one operational center or flatten the cluster into one layer.
