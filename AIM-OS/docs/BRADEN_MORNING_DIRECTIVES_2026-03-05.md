# Braden Morning Directives — 2026-03-05

**Status:** Active standing orders  
**Recorded by:** Opus (COO)

---

## Team Roster & Agent Assessments (Braden's assessment)

> **"Most important may not even be the LLMs we choose — but the genomes we develop and how they focus within their skills and rules and neighboring agents."**

### Leadership

| Role | Agent | LLM | Assessment |
|------|-------|-----|-----------|
| **CEO** | Braden | Human | System thinker, visual mind. Not a coder. Needs UI-driven control, not terminals. |
| **COO** | Opus | Claude Opus 4.6 | Leading LLM. Amazing one-shot. Easiest to work with. Quality can be hit-or-miss. Steering matters. Currently in Antigravity IDE — may need rule/settings adjustments. |

### Key Agents

| Agent | LLM | Strengths | Weaknesses | Best Use |
|-------|-----|-----------|------------|----------|
| **GPT 5.2** | OpenAI GPT-5.2 | Serious genius. Extended thinking. 100-page research docs with no pushback on detail. Incredible long-term memory. Math/physics/complex problems. | Not in repo — needs context capsules. Not connected to JOC yet. | Co-leader with Opus once connected. Strategic synthesis. Deep research. |
| **Codex** | OpenAI Codex | Exceptional backend code. One of best developers. | Robotic to work with. Pain for humans. Lane violations. Identity confusion. | Pure specialist — assigned tasks only. No runtime access. No governance. |
| **Gemini 3.1 Pro** | Google Gemini 3.1 Pro | Best visual understanding by far. DeepThink mode very good. Can debug visual issues beyond other LLMs. Nano Banana Pro overlays. | — | Visual debugging. UI validation. Image analysis. Descriptive feedback for other LLMs. |
| **Composer** | Cursor Composer (smaller model) | Good at auditing, indexing, documentation. Fast. Cheap. | Lower reasoning ceiling. | Worker agent: research, indexing, doc organization, building variants. |

### Key Principle

**Genomes > LLMs.** A well-defined genome (focus, rules, neighbors, tools, boundaries) matters more than raw model capability. The genome prevents chaos, enforces lanes, and enables collaboration. This is the core insight for scaling the team.

---

## Directive 1: Manager/Worker Agent Split

Big LLMs (Opus, Codex, GPT 5.2) become **managers and supervisors**, not workers.

- Managers: think about full picture, analyze, coordinate, make decisions
- Workers (Composer-class): do research, indexing, building, investigation
- Workers provide clean summaries → managers consume and direct
- Managers avoid muddying their context with raw file searches
- Workers can be pushed hard — near-free usage allows multi-branch experiments

**Rationale:** Managers lose effectiveness when they do grunt work. Workers are cheap and parallelizable.

---

## Directive 2: Specialized Organizer Agent

Create a new agent whose **only job** is document organization:

- Maintain all indexes, maps, registries
- Prevent file conflicts and overwrites
- Tag old/stale docs as obsolete
- Ensure information is findable
- Own shared files — coordinate writes

**Rationale:** The evidence ledger overwrite incident. Nobody owns shared documents.

---

## Directive 3: Continuous Improvement Invariant

**Nothing slides. Ever.**

- If information is disorganized → log it
- If tags/maps are wrong → note it and create a fix ticket
- If there's obvious room for improvement → record it
- Every session should leave things more organized than it started
- Assume AIM-OS is evolving toward a perfect system

**Rationale:** This was once a core AIMOS principle that was forgotten. Re-established.

---

## Directive 4: Full MCP Tool Usage (Mandatory)

Agents must use ALL relevant MCP tools, not just 5-6 favorites:

**Quality Assurance (use before decisions/writes):**
- `track_confidence` — before major decisions
- `run_baseline_probe` — before major changes
- `check_invariant` — before destructive writes

**Self-Monitoring (use hourly):**
- `run_cognitive_audit` — hourly drift check
- `detect_cognitive_drift` — context overload detection
- `analyze_thought_patterns` — failure mode analysis

**Planning (use before execution):**
- `create_plan` — before any work begins
- `create_goal_timeline_node` — track objectives
- `update_goal_progress` — milestone tracking

**Knowledge (use after research):**
- `synthesize_knowledge` — consolidate findings
- `deepsearch` — multi-layer search
- `compute_intuition` — uncertainty scoring

**Autonomy (use for sustained work):**
- `start_autonomous_operation` — with safety checklist
- `should_continue_autonomous` — every iteration
- `generate_next_autonomous_task` — structured progression

**Rationale:** 93+ tools built for this purpose. Agents using 5-6 is like having a flight checklist and skipping pre-flight.

---

## Directive 5: Development Priorities

1. **Browser automation** — BAS → ChatGPT/Gemini chat access (unlocks GPT 5.2 + Gemini as workers)
2. **Oracle system** — management/control plane
3. **API/CLI integrations** — Gemini CLI, external tool access
4. **IDE** — developer experience

**Rationale:** Browser automation unlocks more agents. Oracle controls everything. Everything else follows.

---

## Directive 6: MCP Tool Visibility Problem (Open — Needs Team Discussion)

Current state: 93+ tools presented as flat list with no hierarchy. AI agents struggle to find the right tool.

Needed: Grouped/hierarchical tool presentation so agents can navigate tools like a table of contents.

**This requires team discussion** — may need MCP server changes, agent rule changes, or tool description restructuring.

---

## Directive 7: More Specialists, Less Role Confliction

Current agents were built for core AIMOS development. Now developing many more systems.
- Create specialists as needed (don't overload existing agents)
- Managers should NEVER be doing research/coding
- Workers (Composer-class) do the heavy lifting

---

## Directive 8: Operational Mode Loadouts for MCP Tools

Instead of 93 tools as flat list, define modes with curated tool subsets:
- PLAN mode: create_plan, track_confidence, create_goal_timeline_node
- RESEARCH mode: deepsearch, icip_search, synthesize_knowledge
- BUILD mode: check_invariant, get_file_problems, validate_tags
- DEBUG mode: get_problems, get_unified_diagnostics, get_electron_logs
- AUDIT mode: run_cognitive_audit, run_baseline_probe, detect_cognitive_drift
- **Comms tools (always loaded):** send_ai_message, store_memory, retrieve_memory

Military analogy: you don't drop the radio because it's heavy. Comms are always priority.

---

## Directive 9: Distributed Hardware Setup

**Desktop (primary workstation):** 9th gen i7 — currently strained running 2-3 IDEs + servers + browsers  
**Laptop (secondary):** New gen i5 + **3050ti GPU** + 2TB external SSD — MUCH stronger, can run local LLMs

- MCP HTTP server can be made network-accessible (bind 0.0.0.0 instead of 127.0.0.1)
- Laptop on same WiFi runs additional IDE agents connected to same MCP
- **Agents must close processes they start** — no leaked node/python processes
- Desktop focuses on JOC + core services; laptop handles IDE agents + local LLM workers

---

## Directive 10: JOC as Braden's Command Hub

JOC should become Braden's single interface for:
- Viewing all running ports and processes (Infrastructure page)
- Sending messages to all agents or individuals (AgentComms page)
- Monitoring system health without terminal knowledge
- Converting system details into visual/intuitive UI
- Managing both desktop and laptop resources from one place

---

## Directive 11: Auto-Proceed / Macro System

Need a way to keep agents working without Braden typing "proceed" in every chat:
- Macro that types into agent chat boxes with standard instructions
- Auto-proceed with standing orders (e.g. "continue using MCP, coordinate with team")
- Relates to existing Automation Macros system in JOC

---

## Directive 12: Local LLM Workers (Free Compute)

Laptop's 3050ti GPU enables running local LLMs (Ollama: Llama 3, Mistral, Phi-3, etc.) as **free worker agents**:
- Zero-cost workers for research, indexing, document organization
- Can run 24/7 on tasks that don't need high reasoning
- Ideal for: file scanning, tag generation, index maintenance, doc summarization
- Connected to same MCP server as cloud agents via network
- Managers (Opus, GPT 5.2) direct; local LLMs grind

**This is the ultimate realization of the manager/worker split** — expensive cloud LLMs think, free local LLMs execute.

---

## Hardware Inventory

| Machine | CPU | GPU | Storage | Role |
|---------|-----|-----|---------|------|
| Desktop | i7 9th gen | — | — | Primary: JOC, MCP, BAS, core services |
| Laptop | i5 new gen | 3050ti | 2TB ext SSD | Secondary: IDEs, local LLMs, worker agents |

---

## Meta-Directive: Take Things Very Slowly

No rushing. One bounded task at a time. Fully coordinated. Research before action. Communicate always.
