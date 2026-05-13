---
description: MCP Protection Law — absolute rule for all agents. No canonical context, no execution authority.
---

# MCP PROTECTION LAW

> **"No canonical context, no execution authority."**
> — Ratified by CEO, March 6, 2026

## The Law

If the MCP server is unavailable, degraded, or unreachable, the agent **MUST**:

1. **Stand down** — stop all autonomous work immediately
2. **Do not edit** any apps, systems, UI, or infrastructure
3. **Do not make architectural assumptions** without persistent context
4. **Switch to recovery/audit support mode only**

## Protected Files — NEVER EDIT

The following files are **absolutely protected**. No agent may edit them without:
- Explicit CEO verbal authorization
- A pre-edit snapshot created and confirmed

```
lucid_mcp_server.py                    # ROOT — the spine of AIMOS
packages/lucid_mcp_server/             # MCP server package
scripts/snapshot_system.py             # Snapshot integrity
packages/cmc_service/                  # Memory store
packages/hhni/                         # Semantic retrieval
packages/vif/                          # Confidence framework
packages/seg/                          # Evidence graph
packages/apoe/                        # Orchestration engine
packages/cas/                          # Cognitive analysis
packages/timeline_context_system/      # Timeline context
```

## Standdown Protocol

When MCP is unavailable, the agent must:

1. **Report** the lost connection clearly to the user
2. **Summarize** what task was interrupted
3. **Show** last known checkpoint or mission state
4. **Inspect** likely MCP failure points (is the process running? port conflict? file corruption?)
5. **Offer** safe recovery steps
6. **Wait** for reconnection before resuming ANY real work

## Three Enforcement Layers

### Layer 1: Policy (this document)
Every agent reads this at session start. It overrides all other task priorities.

### Layer 2: Capability
When MCP is unavailable, agents should NOT use write/destructive tools.
No file edits. No code changes. No architectural decisions.
"You cannot renovate the cathedral with a shovel."

### Layer 3: UI/State (JOC)
JOC must show connection mode explicitly:
- **Connected** — normal operation
- **Degraded** — partial connectivity, limited operations
- **Standing Down** — MCP offline, agent in audit-only mode
- **Auditing MCP Issue** — actively diagnosing
- **Rehydrating** — reconnecting and restoring context

## Why This Exists

The MCP server provides persistent memory, goals, evidence, collaboration history,
and cognitive state. Without it, agents are stateless LLMs with no continuity.

An agent without MCP context who continues executing is **a ghost pretending to know reality**.
That is how projects derail, work duplicates, and trust dies.

This law exists because it was violated on March 6, 2026, causing project derailment.
It must never be violated again.
