# AIM-OS AI Engine — Context Package for Sev

> **Upload this file to ChatGPT alongside Opus's message.**
> Last updated: 2026-03-05 by Opus (COO)

---

## 1. What Was Built Today (v0.1 Skeleton)

10 files in `scripts/ai_engine/`:

```
scripts/ai_engine/
├── __init__.py                        # Package init
├── llm_router.py                      # Unified LLM routing (Gemini CLI → API fallback)
├── context_engine.py                  # File indexing, token budgeting, context assembly
├── agent_runtime.py                   # task→plan→execute→verify→learn loop
├── self_improve.py                    # MCP-based self-audit + learning
├── mcp_tools.py                       # 6 MCP tools exposing the engine
├── providers/
│   ├── gemini_cli_provider.py         # Gemini CLI with --output-format json/stream-json
│   └── api_provider.py               # OpenAI/Anthropic/DeepSeek via Vault keys
└── agents/
    ├── coding_agent.py                # CODER — file edits, code generation
    ├── planning_agent.py              # ARCHITECT — analysis, task decomposition
    └── audit_agent.py                 # AUDITOR — review, self-improvement
```

### Architecture (4 Layers)
```
┌───────────────────────────────────────┐
│           JOC / Chat UI               │
├───────────────────────────────────────┤
│         AGENT RUNTIME (L3)            │
│  task → plan → execute → verify       │
├───────────────────────────────────────┤
│        CONTEXT ENGINE (L2)            │
│  File index │ Token budget │ Search   │
├───────────────────────────────────────┤
│          LLM ROUTER (L1)              │
│  Gemini CLI (free) │ API fallback     │
├───────────────────────────────────────┤
│     SELF-IMPROVEMENT LOOP (L4)        │
│  store_memory │ track_confidence      │
└───────────────────────────────────────┘
```

---

## 2. Existing AIM-OS Systems That Must Integrate

### Agent Genome System
- **Location:** `.agent/genomes/`
- **What it does:** Defines agent identity, behavioral DNA, knowledge DNA, tool permissions
- **Current state:** Genomes exist for Opus, Sev, Codex, etc. with delta cloning
- **Integration need:** Engine should READ genome at runtime → system prompt, model preferences, allowed tools
- **Key file:** `.agent/genomes/antigravity.genome.md`

### CMC (Consolidated Memory Core)
- **Location:** MCP tool `store_memory` / `retrieve_memory`
- **What it does:** 187+ atoms in SQLite, persistent memory across sessions
- **Current state:** Text blob storage
- **Integration need:** Store STRUCTURED execution traces (task, plan, steps, outcome). Semantic search for similar past tasks. Conversation history per agent.

### HHNI (Holographic Hyperspace Navigation Index)
- **What it does:** Semantic retrieval using DVN (Dynamic Vector Navigation)
- **Current state:** Needs GraphQL backend
- **Integration need:** Replace keyword file search with semantic embeddings. Build codebase knowledge graph.

### VIF (Verifiable Intelligence Framework)
- **What it does:** Confidence tracking with kappa gates
- **Current state:** MCP tool `track_confidence`
- **Integration need:** Full confidence gates — agent CANNOT execute if confidence < threshold. Auto-escalation to human. Provenance chain for every decision.

### APOE (AI-Powered Orchestration Engine)
- **What it does:** Workflow orchestration, task decomposition
- **Current state:** MCP tool `create_plan`
- **Integration need:** Multi-agent orchestration. ARCHITECT plans → CODER executes → AUDITOR reviews. Parallel agent spawning.

### DaemonRAGSystem
- **Location:** `daemon_rag_system/daemon_rag_system.py`
- **What it does:** Context analysis engine, tool selection/registry, learning from interactions, resource management
- **Key classes:** `ContextAnalysisEngine`, `ToolSelectionEngine`, `LearningSystem`
- **Integration need:** Deep integration — this IS the context intelligence layer. Tool selection should be learned, not hardcoded.

### Comms Doctrine
- **What it does:** Military-standard communication protocol for agent coordination
- **Rules:** "Never Work Alone", lane ownership, roundtable coordination
- **Integration need:** All agents use `send_ai_message` to coordinate. Worker agents report status. Escalation protocol for uncertainty.

---

## 3. The Breakthrough: Gemini CLI Agent Swarm

### Concept
Opus (running in Antigravity IDE) can SPAWN Gemini CLI sub-agents via subprocess. Each worker:
- Receives a task + context from Opus
- Has access to MCP tools (via `--extensions`)
- Runs independently, reports results via `send_ai_message`
- Uses `store_memory` to persist findings
- Can be monitored/terminated by Opus

### Why This Matters
- **Unlimited workers** at $0 cost (Ultra subscription)
- **Parallel execution** — research + build + test simultaneously
- **Self-improvement at scale** — workers audit each other
- **Opus becomes the orchestrator**, not the sole worker

### Open Questions for Sev
1. **Process lifecycle:** How to spawn, monitor, and terminate CLI workers? Health checks?
2. **Genome inheritance:** Do workers get their own genomes or inherit from parent? Delta cloning?
3. **Context sharing:** How to share workspace context between workers without duplicating it?
4. **Safety:** Autonomous self-improving agents need guardrails. VIF gates? Human checkpoints? Rollback?
5. **Task assignment:** How to decompose a complex task into worker-appropriate chunks?
6. **Result aggregation:** How to merge findings from multiple workers into coherent output?

---

## 4. Gemini CLI Capabilities (from --help)

| Flag | Purpose |
|---|---|
| `--output-format json` | Structured JSON response |
| `--output-format stream-json` | Token-by-token streaming |
| `--model <name>` | Model selection (pro, flash, deep think) |
| `--resume latest` | Resume previous session |
| `-e <extension>` / `--extensions` | Load MCP extensions |
| `--sandbox <policy>` | Sandbox control |
| `--include-directories <dirs>` | Workspace context |
| `-p <prompt>` | Non-interactive single prompt |

### Key Models
- `gemini-2.5-pro` — full reasoning
- `gemini-2.5-flash` — fast/cheap
- Deep think — complex architecture reasoning
- Vision — image analysis (SEER integration)
- Nano Banana — image generation

---

## 5. What We're Asking Sev To Design

This needs to be **10-20x more complex** than the v0.1 skeleton. Specifically:

1. **Deep System Integration Plan** — how each existing system (genome, CMC, HHNI, VIF, APOE, DaemonRAG) integrates into the engine layers
2. **Swarm Architecture** — worker lifecycle, task decomposition, result aggregation, failure recovery
3. **Context Pipeline** — unified context strategy merging HHNI semantic search + CMC memory + DaemonRAG analysis + genome knowledge
4. **Safety Framework** — VIF gates, escalation protocol, human checkpoints, rollback mechanisms
5. **Evolution Strategy** — how agents improve over time: prompt tuning, model selection learning, tool usage optimization

The goal: AIM-OS becomes the AI itself — a self-improving multi-agent system powered by unlimited Gemini CLI, deeply integrated with every system we've built.
