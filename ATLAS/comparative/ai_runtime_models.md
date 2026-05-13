# Comparative: AI Runtime Models

**Atlas scope:** Where inference runs, how tools attach, trust boundaries for agent loops.  
**Constraint:** No asserted internal topology for closed cloud runtimes; compare **public surfaces** only unless package ledger upgrades tier.

## Systems referenced

| Slug | Package status | Comparable on |
|------|----------------|---------------|
| `openai-agents-chatgpt-public-runtime` | seeded | Public APIs, product docs, SDK docs |
| `anthropic-claude-code-agent-sdk` | seeded | Public SDK, MCP usage, CLI surfaces |
| `model-context-protocol` | seeded | JSON-RPC protocol, stdio/transports |
| `gemini-api` | seeded | Google AI Gemini API docs |
| `deepseek-api` | seeded | DeepSeek API docs |
| `microsoft-agent-framework` | seeded | Microsoft Learn agent/workflow docs |
| `openhands` | seeded | OSS repo + docs (split OSS vs Cloud claims per package) |
| `aim-os` | seeded | AIM-OS repo: Aether law quartet + `AIMOS_MAJOR_SYSTEMS.md`; MCP host (LUCID-MCP); **not** vendor cloud API |

## Public-surface dimensions (selected)

| Dimension | openai-agents-chatgpt-public-runtime | anthropic-claude-code-agent-sdk | gemini-api | deepseek-api |
|-----------|--------------------------------------|----------------------------------|------------|---------------|
| **Primary contract** | HTTP APIs + SDKs (`DOCUMENTED`) | HTTP APIs + SDK + Claude Code (`DOCUMENTED`) | HTTP/gRPC-class Gemini API (`DOCUMENTED`) | HTTP API (`DOCUMENTED`) |
| **Tool attachment** | API tools/functions (`DOCUMENTED`) | MCP + local tools (`DOCUMENTED`) | API tool/function patterns where documented (`DOCUMENTED`) | Tool patterns if documented (`DOCUMENTED`) |
| **Trust boundary** | Cloud + client device (`INFERRED` class) | Local workspace risk for agents (`DOCUMENTED` warnings) | Google account / GCP boundary varies by product (`DOCUMENTED` per surface) | API key + client (`DOCUMENTED`) |

| Dimension | microsoft-agent-framework | openhands | model-context-protocol |
|-----------|---------------------------|-----------|-------------------------|
| **Primary contract** | In-process SDK + workflows (`DOCUMENTED` Learn) | OSS runtime + optional cloud SKU (`DOCUMENTED` split) | Host↔server JSON-RPC (`DOCUMENTED` spec) |
| **Tool attachment** | Tools + MCP servers (`DOCUMENTED`) | Sandboxed shell/tools + integrations (`DOCUMENTED`) | Tool listing + invocation (`DOCUMENTED` spec) |
| **Trust boundary** | Host app + configured providers (`DOCUMENTED` / deployer) | Workspace + sandbox container (`DOCUMENTED` pattern) | Host process ↔ MCP server (`DOCUMENTED`) |

| Dimension | aim-os |
|-----------|--------|
| **Primary contract** | Governed **multi-subsystem** stack (memory, evidence, orchestration) + **MCP server** (LUCID-MCP) — `DOCUMENTED` in AIM-OS docs, not a single HTTP API |
| **Tool attachment** | **103** tools in `lucid_mcp_server.py` `handle_tools_list` (`OBSERVED` 2026-04-03, package `aim-028`); overview doc may still say 93 |
| **Trust boundary** | VIF/SCOR/CAS/constitutional law **as documented**; host IDE + local AIM-OS processes (`DOCUMENTED` overview) |

## Agent control-loop pattern (structural, not vendor-specific)

1. **Observe** context window + tool outputs.  
2. **Plan** (implicit in model; not a stable OS-like interface across vendors — tier per vendor claim).  
3. **Act** via tool calls.  
4. **Settle** with final message to user.

Mark each vendor’s guarantees about steps 2–4 per **DOCUMENTED** product doc or keep **UNKNOWN**.

## Forbidden merges

- Treating “Claude Code” or “ChatGPT” as interchangeable runtimes.  
- Diagramming datacenter GPU placement without primary operator engineering publications in ledger.
