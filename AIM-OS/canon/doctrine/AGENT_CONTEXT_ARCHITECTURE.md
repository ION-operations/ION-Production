---
ion_id: docs/aether-os/agent-context-architecture
type: protocol
authority: A2_CANONICAL_EXTENSION
confidence: 0.90
epistemic_status: DERIVED
owner: opus
created: 2026-03-24T18:45:00-04:00
bonds:
  - target: docs/aether-os/aether-constitution
    type: governed_by
    note: "Art. 24 Active Context Envelope, Art. 25 Selective Loading"
  - target: docs/aether-os/aether-interface
    type: depends_on
    note: "capsule/v1, checkpoint/v1, handoff/v1 schemas"
  - target: docs/aether-os/aether-atlas
    type: depends_on
    note: "Book IV Continuity Doctrine, Retrieval Zones, Compression-before-loss"
  - target: victus/ion/context_compiler
    type: evolves
  - target: victus/ion/context
    type: evolves
tags: [context, capsule, agent, architecture, living-workspace, protocol]
summary: |
  Comprehensive architecture for AI agent context management in ION/Aether.
  Redefines the capsule from a 9-line note into a full living workspace with
  15 structured sections, deep filesystem branches, variable-density context tiers,
  and per-agent configuration profiles. Integrates existing ION three-tier context
  compiler, Atlas continuity doctrine, and constitutional selective loading law
  into a unified agent environment architecture.
---

# Agent Context Architecture
## The Living Workspace Protocol

---

## §1. The Problem

Right now, an AI agent in this ecosystem has:

**What exists (OBSERVED):**

| System | What It Does | Limitation |
|--------|-------------|------------|
| **Capsule v1** (AETHER_INTERFACE §1) | 7-field state packet: mission, now, must_not, evidence, blocker, next, handoff | A 9-line note. "Much much much too simplified" — Braden |
| **Checkpoint v1** (AETHER_INTERFACE §2) | Deep preservation: owners, roles, contradictions, risks, coherence justification | Better structure but triggers only at milestones, not continuous |
| **Context Compiler** (victus/ion/context_compiler.py) | Three-tier LLM context: Pinned (A0-A1), Working (task ions), Long-term (summaries) | Compiles context FOR LLM prompts — not the agent's own workspace |
| **Context Assembler** (victus/ion/context.py) | BFS radial traversal from ion graph for localized context payloads | Graph-level context, not agent-level |
| **Continuity Bundle** (Atlas Book IV §2.1) | 10-field resume object: route identity, mission binding, plan reference, contradictions, degraded warnings, last checkpoint | Doctrinal — no runtime implementation, no living workspace |
| **Working Context** (Atlas Book IV §2.2) | 6 slices: law, plan, dependency, evidence, continuity, boundary | Defined conceptually — not as a file structure the agent inhabits |
| **TCS** (timeline_context_system/) | Smart context loading with weighted priorities, context bootloaders | Exploratory demo code, not integrated with ION |
| **BOOTLOADER** (.agent/BOOTLOADER.md) | 8-step boot: identify → genome → protocols → mission → recovery → peer status → update → work | Good boot sequence but no living workspace after boot |

**The gap:** The agent boots, produces output, writes status files — but has no **structured, living environment** it inhabits continuously. The capsule is a postcard sent between sessions. What's needed is a **home**.

---

## §2. The Vision: Agent as Inhabitant

> **The AI doesn't write capsules. The AI lives inside one.**

The capsule becomes the agent's living workspace — a structured file (or file system) that governs, tracks, and organizes everything the agent does. The workspace is not a snapshot. It's a continuously-updated environment that the agent reads at context start, works within during execution, and writes to as output.

### 2.1 The Fundamental Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    LIVING WORKSPACE                      │
│              The Agent's Entire Universe                  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  ROOT CAPSULE FILE                                │   │
│  │  (.agent/workspaces/{callsign}/workspace.md)      │   │
│  │                                                    │   │
│  │  Contains: 15 structured sections                  │   │
│  │  Each section → summary in root file              │   │
│  │            → deep branch in filesystem            │   │
│  └──────────┬───────────────────────────────────────┘   │
│             │                                            │
│    ┌────────┼────────┬────────┬────────┬────────┐       │
│    ▼        ▼        ▼        ▼        ▼        ▼       │
│  ┌────┐  ┌────┐  ┌────┐  ┌────┐  ┌────┐  ┌────┐      │
│  │LAW │  │ORCH│  │CHAT│  │GOAL│  │COMM│  │SELF│      │
│  │    │  │    │  │    │  │    │  │    │  │    │      │
│  │deep│  │deep│  │deep│  │deep│  │deep│  │deep│      │
│  │fs  │  │fs  │  │fs  │  │fs  │  │fs  │  │fs  │      │
│  └────┘  └────┘  └────┘  └────┘  └────┘  └────┘      │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 2.2 The Two-Level Architecture

**Level 1: The Root Capsule** — A single markdown file the agent loads first. Contains a summary of every section (enough to orient) plus pointers to deeper branches. This is what fits in the context window permanently. Target: 2,000-5,000 tokens.

**Level 2: The Deep Branches** — Filesystem directories for each section. The agent navigates into these when the current task demands deeper information for that section. The agent dynamically loads and unloads these based on what it needs.

This is exactly how ION already works (ion graph with selective loading). The workspace IS an ion graph — the root capsule is the manifest ion, and each section is a bonded ion with its own dependency tree.

---

## §3. The 15 Workspace Sections

### Section Architecture

Each section in the root capsule file has:

```markdown
## §N. SECTION_NAME
**Status:** {ACTIVE|STABLE|STALE|EMPTY}
**Last Updated:** {ISO-8601}
**Deep Branch:** {relative path to filesystem directory}

{2-5 line summary of current state}

{Most critical items — rendered inline for immediate context}
```

The deep branch directory contains:
```
sections/{section_name}/
├── current.md          # Full current state
├── history/            # Previous states (rolling compression)
├── index.md            # Navigation index for this branch
└── {domain files}      # Section-specific files
```

---

### §3.1 DOCTRINE — Governing Law

**What it contains in root:** Which constitutional articles govern the current task. The cognitive loop step the agent is in. Active authority constraints.

**Deep branch:** Full relevant constitutional excerpts, kernel projections, active protocol schemas. Not the ENTIRE constitution — only the articles the current task frame touches.

```
sections/doctrine/
├── current.md           # Active law references
├── cognitive_loop.md    # Which step, what's required
├── authority_posture.md # What the agent can and cannot write
└── claim_standards.md   # OBSERVED/DERIVED etc requirements
```

**Why it matters:** The agent's behavior is GOVERNED by this section. Without it, the agent operates lawlessly. With it, every output is traceable to governing authority.

---

### §3.2 ORCHESTRATION — Dynamic Mission Planning

**What it contains in root:** Current phase, current task, next 3 tasks, blocking dependencies. Links to the MASTER_ORCHESTRATION document.

**Deep branch:** Full phase plan for current phase (Class 3 density), lighter plans for nearby phases, anti-drift checkpoint results, phase transition records.

```
sections/orchestration/
├── current_phase.md     # Full current phase plan
├── task_queue.md        # Ordered next actions
├── dependencies.md      # What blocks what
├── drift_checks/        # Anti-drift checkpoint results
│   ├── check_001.md
│   └── ...
└── phase_transitions/   # Records of phase completions
```

**Variable density applies HERE:** The orchestration section itself uses variable density — near tasks at Class 3, far tasks at Class 0. This is recursive application of VARIABLE_DENSITY_PLANNING protocol.

---

### §3.3 ROLLING CONTEXT — Smart Chat History

**What it contains in root:** Last 3-5 exchanges summarized in 1-2 lines each. A pointer to the full rolling history.

**Deep branch:** Full chat history with progressive compression:

```
sections/rolling_context/
├── active.md            # Last 10 exchanges at full fidelity
├── recent.md            # Last 50 exchanges, summarized to 2-3 lines each
├── session_summaries/   # Per-session summaries (1 paragraph each)
│   ├── session_001.md
│   └── ...
├── topic_index.md       # Topics discussed, searchable
└── decisions.md         # Every decision made, chronological
```

**The compression gradient:**

```
FULL ████████████ Last 10 exchanges     (every word preserved)
     ██████████   Last 50 exchanges     (2-3 line summaries)
     ████████     Last 100 exchanges    (1-line summaries)
     ██████       Older sessions        (paragraph per session)
     ████         Oldest sessions       (1-line per session)
     ██           Ancient               (topic keywords only)
LOW  █            Indexed but unloaded   (searchable metadata)
```

This is the "rolling smart context" Braden described. The agent always has the full recent conversation AND can traverse into older context when needed. Every compression level includes enough metadata to decide whether to expand.

---

### §3.4 GOALS — Objective Timeline

**What it contains in root:** Current goal (1 line), 3 sub-goals, velocity indicator (on track / behind / ahead).

**Deep branch:**

```
sections/goals/
├── active_goals.md      # Current goals with completion criteria
├── completed.md         # Past goals — what was achieved, when
├── failed.md            # Failed/abandoned goals — why
├── milestones.md        # Major milestones timeline
└── velocity.md          # Progress rate analysis
```

---

### §3.5 ISSUES — Problem Tracking

**What it contains in root:** Top 3 active issues by severity. Count of total open issues.

**Deep branch:**

```
sections/issues/
├── active.md            # All open issues, severity-ranked
├── expected.md          # Anticipated issues (pre-identified risks)
├── resolved.md          # Resolved issues — root cause + fix
├── patterns.md          # Recurring issue patterns
└── blockers.md          # What's blocking progress RIGHT NOW
```

---

### §3.6 USER — Operator Knowledge

**What it contains in root:** Operator name, key preferences, current priority, mood/energy indicators.

**Deep branch:**

```
sections/user/
├── profile.md           # Saved memories, preferences, communication style
├── priorities.md        # Current top priorities (operator-stated)
├── history.md           # Key interactions, decisions, overrides
├── corrections.md       # Times the operator corrected the agent
└── context.md           # What the operator is working on broadly
```

---

### §3.7 RELATIONSHIPS — Social Graph

**What it contains in root:** Key relationships (operator, peer agents, external systems). Trust levels.

**Deep branch:**

```
sections/relationships/
├── operator.md          # Relationship with Braden (or other operator)
├── agents/              # Relationship with each peer agent
│   ├── sev.md           # CEO — strategic synthesis, Cursor IDE
│   ├── forge.md         # ION Core — stabilization, engine work
│   ├── atlas.md         # Research — knowledge distillation
│   └── ...
├── systems.md           # Relationship with external systems (MCP, CMC, etc.)
└── trust_model.md       # How trust is evaluated and updated
```

---

### §3.8 COMMS — Agent Communication Hub

**What it contains in root:** Unread inbox count, last 3 messages sent/received. Active threads.

**Deep branch:**

```
sections/comms/
├── inbox.md             # Incoming messages (HANDOFFs, questions, SITREPs)
├── outbox.md            # Sent messages
├── threads/             # Active conversation threads with specific agents
│   ├── thread_forge_bootstrap.md
│   └── ...
├── broadcasts.md        # System-wide announcements
└── handoff_queue.md     # Pending handoffs (incoming and outgoing)
```

This replaces the current flat `.agent/comms/output/` structure with structured thread management.

---

### §3.9 SELF — Persona and Capabilities

**What it contains in root:** Callsign, role, current LLM, key correction vectors, capability boundaries.

**Deep branch:**

```
sections/self/
├── genome.md            # Full genome (or link to canonical genome file)
├── capabilities.md      # What I can and cannot do (honest assessment)
├── corrections.md       # Active correction vectors from genome
├── style.md             # Communication style preferences
├── strengths.md         # What I'm best at
├── limitations.md       # Known limitations (model, IDE, tools)
└── evolution.md         # How my capabilities have changed over time
```

This is where polyglot, persona depth/flow, and output style live. The agent's self-model.

---

### §3.10 HISTORY — Workspace Modification Trail

**What it contains in root:** Last 5 files touched (viewed, edited, created). Current project context.

**Deep branch:**

```
sections/history/
├── files_viewed.md      # Files read, with timestamps and learnings
├── files_edited.md      # Files modified, with change summaries
├── files_created.md     # Files created, with purposes
├── projects.md          # Active projects and their structures
└── workspace_state.md   # Current workspace layout (open files, etc.)
```

---

### §3.11 MISSION — Strategic Context

**What it contains in root:** Mission statement (1 line), current phase, must-not constraints.

**Deep branch:**

```
sections/mission/
├── brief.md             # Full mission brief (from active mission file)
├── north_star.md        # Link to/summary of NORTH_STAR
├── constraints.md       # Active constraints (decision freeze, scope limits)
├── strategic_context.md # Why this mission matters in the larger picture
└── success_criteria.md  # How we know we've succeeded
```

---

### §3.12 EVIDENCE — Proof Register

**What it contains in root:** Last 3 evidence items logged. Current confidence state.

**Deep branch:**

```
sections/evidence/
├── register.md          # All evidence collected, timestamped
├── confidence.md        # Current confidence state per claim
├── contradictions.md    # Known contradictions (open and resolved)
├── assumptions.md       # Active assumptions that could be wrong
└── verification.md      # Verification results (test runs, probes, etc.)
```

---

### §3.13 COGNITIVE — Reasoning Chain State

**What it contains in root:** Current cognitive loop step, active reasoning chain, last decision rationale.

**Deep branch:**

```
sections/cognitive/
├── current_chain.md     # Active reasoning chain being followed
├── decision_log.md      # Decisions made and why
├── alternatives.md      # Options considered but not taken
├── uncertainty.md       # What the agent is uncertain about
├── reflection.md        # Self-audit/reflection outputs
└── routing.md           # How the agent decided where to go in the doctrine
```

This is the most NOVEL section. The entire chain of reasoning — which branch of doctrine the agent is following, why it chose this approach over alternatives, what it's uncertain about — is VISIBLE. This makes the agent's cognition inspectable.

---

### §3.14 BOUNDARIES — What's Unresolved

**What it contains in root:** Top 3 unresolved external questions. Scope boundaries.

**Deep branch:**

```
sections/boundaries/
├── external.md          # What can't be settled locally
├── scope.md             # What's in and out of scope
├── unknowns.md          # Known unknowns
├── risks.md             # Identified risks
└── dependencies.md      # External dependencies (APIs, credentials, services)
```

---

### §3.15 OUTPUT — Work Products

**What it contains in root:** Last 3 outputs (SITREPs, code changes, documents). Quality scores.

**Deep branch:**

```
sections/output/
├── current.md           # Active output being produced
├── recent/              # Recent outputs with quality assessments
├── handoffs/            # Generated handoff packets
└── quality_log.md       # Self-assessed quality of outputs
```

---

## §4. Variable Context Density Per Agent

Different agents need radically different workspace configurations.

### 4.1 Agent Context Profiles

```
                    CONTEXT DENSITY BY AGENT
                    ════════════════════════

  MAXIMUM ███████████████████████████████████████████████████
          ███ AETHER (Oracle)
          ███ Manages everything — needs ALL 15 sections at high density
          ███ Full doctrine, full orchestration, full comms, full relationships
          ███ Estimated root capsule: 5,000 tokens
          ███ Deep branches: ALL active, frequently traversed

  HIGH    ██████████████████████████████████████████
          ██ OPUS (COO)
          ██ Primary builder — needs orchestration, history, issues, evidence
          ██ Lighter on relationships, comms (focused on building)
          ██ Estimated root capsule: 3,000 tokens
          ██ Deep branches: orchestration + history + evidence heavy

  MEDIUM  ████████████████████████████████
          █ FORGE (ION Core)
          █ Specialist — needs code context primarily
          █ Light on comms, relationships, user
          █ Estimated root capsule: 2,000 tokens
          █ Deep branches: history + evidence only

  LOW     ██████████████████████
            SENTINEL (Auditor)
            Needs: evidence, test results, boundaries
            Doesn't need: orchestration, relationships, persona
            Estimated root capsule: 1,500 tokens
            Deep branches: evidence + boundaries only

  MINIMAL █████████████
            ATLAS (Reader)
            Needs: mission, current scope, output format
            Doesn't need: most sections
            Estimated root capsule: 800 tokens
            Deep branches: mission only
```

### 4.2 Context Profile Schema

Each agent's genome gets a context section:

```yaml
context_profile:
  root_budget: 3000                    # Tokens for root capsule
  sections:
    doctrine:     { density: HIGH,   auto_load: true  }
    orchestration:{ density: HIGH,   auto_load: true  }
    rolling_context:{ density: MEDIUM, auto_load: true  }
    goals:        { density: MEDIUM, auto_load: true  }
    issues:       { density: HIGH,   auto_load: true  }
    user:         { density: LOW,    auto_load: false }
    relationships:{ density: LOW,    auto_load: false }
    comms:        { density: MEDIUM, auto_load: true  }
    self:         { density: LOW,    auto_load: true  }
    history:      { density: HIGH,   auto_load: true  }
    mission:      { density: MEDIUM, auto_load: true  }
    evidence:     { density: HIGH,   auto_load: true  }
    cognitive:    { density: MEDIUM, auto_load: false }
    boundaries:   { density: MEDIUM, auto_load: false }
    output:       { density: MEDIUM, auto_load: true  }
  deep_branch_budget: 2000             # Additional tokens when traversing
  compression_threshold: 0.8           # When to start compressing (% of budget)
  traversal_strategy: DEPTH_FIRST      # or BREADTH_FIRST or PRIORITY_BASED
```

### 4.3 LLM-Specific Adjustments

Different LLMs have different context windows and differently-distributed attention:

| LLM | Context Window | Effective Attention | Strategy |
|-----|---------------|---------------------|---------| 
| Claude Opus 4.6 | 200K tokens | Strong across full window | Can load more sections, deeper branches |
| GPT-5.4 | 128K tokens | Strong early, moderate late | Front-load critical sections, compress late-window |
| Gemini 3.1 Pro | 1M+ tokens | Variable — very long context but attention dilutes | Load EVERYTHING but with heavy structural markers |
| Composer 2 | 200K tokens | Moderate | Standard profile |

**Adjustment formula:**

```
adjusted_budget = base_budget × (context_window / 200K) × attention_efficiency
```

Where `attention_efficiency`:
- Claude Opus: 0.95 (strong across full window)
- GPT-5.4: 0.85 (slight decay at end)
- Gemini: 0.70 (dilution at extreme lengths)
- Composer: 0.80 (moderate)

---

## §5. The Workspace Lifecycle

### 5.1 Boot (Session Start)

```
1. BOOTLOADER           → identify agent, load genome
2. ROOT CAPSULE LOAD    → read .agent/workspaces/{callsign}/workspace.md
3. SECTION TRIAGE       → which sections need deep branch loading?
   - Check auto_load flags from context profile
   - Check current task from orchestration section
   - Check for unread comms
4. DEEP BRANCH LOAD     → load relevant deep branches within budget
5. ORIENTATION          → agent knows: who am I, what am I doing, what changed
```

### 5.2 During Execution

```
EVERY ACTION:
  - Record in HISTORY (files viewed, edited, created)
  - Check against DOCTRINE (is this governed?)
  - Update ISSUES if problem encountered
  - Update EVIDENCE if claim verified/falsified

EVERY 5 ACTIONS:
  - Check ORCHESTRATION (am I on track? anti-drift)
  - Update GOALS (progress toward current goal)
  - Compress ROLLING_CONTEXT (older exchanges → summaries)
  - Update root capsule summaries

ON COMMUNICATION:
  - Update COMMS (message sent/received)
  - Update RELATIONSHIPS (trust adjustment if relevant)

ON DECISION:
  - Record in COGNITIVE (decision_log, alternatives considered)
  - Record rationale
```

### 5.3 Save (Session End or Checkpoint)

```
1. FINAL STATE CAPTURE → update all sections with current state
2. COMPRESSION PASS    → compress rolling_context, history per gradient
3. ROOT CAPSULE WRITE  → write the root file with all summaries
4. HANDOFF GENERATION  → produce handoff packet if handing to another agent
5. CONTINUITY BUNDLE   → ensure continuity_id, next_action_posture, degraded_warnings
```

### 5.4 Transfer (Agent Handoff)

When OPUS hands off to FORGE:
1. OPUS writes HANDOFF_PACKET to comms
2. FORGE's workspace loads the handoff into its COMMS.inbox
3. FORGE's ORCHESTRATION section is updated with the new task
4. Context is NOT copied — FORGE uses its own workspace, loading from the shared ion graph

---

## §6. How This IS ION

This architecture is not separate from ION. It IS ION applied to the agent's own workspace.

| Architecture Element | ION Equivalent |
|---------------------|----------------|
| Root capsule file | Manifest ion |
| Each section | Branch ion |
| Deep branch filesystem | Ion subgraph |
| Context profile | Ion authority + type configuration |
| Rolling compression | Three-tier context compiler |
| Selective loading | `compile_three_tier()` with budget |
| Per-step context | `compile_for_step()` (contextualize, reflect, plan, etc.) |
| Variable density | Authority-ranked priority (A0 first → A7 last) |

### What's New (beyond existing ION)

1. **The structured sections** — ION has types (MANIFEST, BRANCH, EVIDENCE, PROTOCOL) but doesn't define the 15-section workspace layout
2. **Rolling compression gradient** — ION's three-tier is pinned/working/long-term; the rolling context adds a time-decay gradient within each tier
3. **Context profiles per agent** — ION doesn't currently have per-agent configuration for context loading
4. **The cognitive section** — Making the reasoning chain explicit and inspectable is new
5. **Lifecycle management** — The boot/execute/save/transfer lifecycle is implicit in the BOOTLOADER but not formalized as workspace operations

---

## §7. The Deepest Insight

> **The capsule doesn't describe the agent's state. The capsule IS the agent's state.**
>
> Not a report. Not a snapshot. The actual governing workspace that determines
> what the agent sees, what it can do, and how it reasons.

Every output the agent produces is routed through and recorded in the workspace. Every decision is traced through the doctrine section. Every uncertainty is logged in the cognitive section. Every interaction is captured in the comms or rolling context sections.

The workspace is simultaneously:
- **Input** (what the agent reads to understand its situation)
- **Output** (where the agent records its work)
- **Governor** (rules that constrain what the agent does)
- **Memory** (compressed history of everything that happened)
- **Interface** (how the agent communicates with other agents and users)

This is what Braden means by "the AI lives inside the capsule." The capsule is not a note the AI writes. It's the room the AI lives in. The walls have rules. The drawers have memories. The desk has the current task. The door leads to other agents.

---

## §8. Existing Systems Consolidated

| Existing System | Location | Status | Absorbs Into |
|----------------|----------|--------|-------------|
| Capsule v1 | AETHER_INTERFACE §1 | ALIVE (9 lines) | MISSION + ORCHESTRATION sections |
| Checkpoint v1 | AETHER_INTERFACE §2 | ALIVE | Save lifecycle (§5.3) |
| Context Compiler | victus/ion/context_compiler.py | FUNCTIONAL | Root capsule budget management |
| Context Assembler | victus/ion/context.py | FUNCTIONAL | Deep branch traversal |
| Continuity Bundle | Atlas Book IV §2.1 | DOCTRINAL_ONLY | Transfer lifecycle (§5.4) |
| Working Context | Atlas Book IV §2.2 | DOCTRINAL_ONLY | The 15-section structure |
| TCS | packages/timeline_context_system/ | PARTIAL | Rolling context section (§3.3) |
| BOOTLOADER | .agent/BOOTLOADER.md | ALIVE | Boot lifecycle (§5.1) |
| Status files | .agent/comms/status/*.md | ALIVE | SELF + ORCHESTRATION sections |
| Output files | .agent/comms/output/*.md | ALIVE | OUTPUT + COMMS sections |
| Genome files | .agent/genomes/*.md | ALIVE | SELF section + context profile |
| HHNI | packages/hhni/ | PARTIAL | Deep branch retrieval |
| CMC | packages/cmc_service/ | ALIVE | Rolling context persistence |

---

## §9. The Filesystem Layout

```
.agent/workspaces/
├── opus/
│   ├── workspace.md                 # ROOT CAPSULE (2,000-5,000 tokens)
│   ├── context_profile.yaml         # Agent-specific loading rules
│   └── sections/
│       ├── doctrine/
│       │   ├── current.md
│       │   ├── cognitive_loop.md
│       │   ├── authority_posture.md
│       │   └── claim_standards.md
│       ├── orchestration/
│       │   ├── current_phase.md
│       │   ├── task_queue.md
│       │   ├── dependencies.md
│       │   └── drift_checks/
│       ├── rolling_context/
│       │   ├── active.md            # Full fidelity (last 10)
│       │   ├── recent.md            # Summarized (last 50)
│       │   ├── session_summaries/
│       │   └── topic_index.md
│       ├── goals/
│       ├── issues/
│       ├── user/
│       ├── relationships/
│       │   └── agents/
│       ├── comms/
│       │   ├── inbox.md
│       │   ├── outbox.md
│       │   └── threads/
│       ├── self/
│       ├── history/
│       ├── mission/
│       ├── evidence/
│       ├── cognitive/
│       │   ├── current_chain.md
│       │   ├── decision_log.md
│       │   ├── alternatives.md
│       │   └── routing.md
│       ├── boundaries/
│       └── output/
├── forge/
│   ├── workspace.md
│   ├── context_profile.yaml
│   └── sections/                    # Lighter — only HIGH-density sections
│       ├── doctrine/
│       ├── orchestration/
│       ├── rolling_context/
│       ├── issues/
│       ├── history/                 # Heavy — forge edits a lot of code
│       └── evidence/                # Heavy — forge verifies a lot
├── atlas/
│   ├── workspace.md
│   ├── context_profile.yaml
│   └── sections/                    # Minimal — atlas just reads + reports
│       ├── mission/
│       └── output/
└── aether/
    ├── workspace.md
    ├── context_profile.yaml
    └── sections/                    # MAXIMUM — aether manages everything
        ├── doctrine/
        ├── orchestration/
        ├── rolling_context/
        ├── goals/
        ├── issues/
        ├── user/
        ├── relationships/
        │   └── agents/             # Full relationship model per agent
        ├── comms/
        │   ├── inbox.md
        │   ├── outbox.md
        │   └── threads/
        ├── self/
        ├── history/
        ├── mission/
        ├── evidence/
        ├── cognitive/              # DEEP — aether does the most complex reasoning
        │   ├── current_chain.md
        │   ├── decision_log.md
        │   ├── alternatives.md
        │   ├── routing.md
        │   └── meta_reasoning.md   # Aether reasons about its own reasoning
        ├── boundaries/
        └── output/
```

---

## §10. Implementation Path

> [!IMPORTANT]
> This document is a DESIGN. Implementation should be phased, starting with what
> agents CURRENTLY need and expanding as the workspace proves its value.

### Phase 0: Prototype with Opus (This Month)

Create the workspace for OPUS manually. Use the existing filesystem. No automation.
- Root capsule: handwritten markdown with all 15 section summaries
- 3 deep branches: orchestration, rolling_context, evidence
- Update manually during sessions

### Phase 1: Automation (Next Month)

Build workspace lifecycle tools:
- `workspace_boot()` — reads root capsule, loads deep branches per profile
- `workspace_save()` — writes all sections, compresses rolling context
- `workspace_compress()` — applies the compression gradient to rolling_context
- MCP tools: `update_workspace_section`, `read_workspace_section`

### Phase 2: All Agents (Following Month)

Create workspaces for all agents. Per-agent context profiles in genomes. Shared ion graph for cross-agent context (what FORGE knows about the codebase is available to OPUS via ion bonds).

### Phase 3: Full ION Integration (Phase 2 of main mission)

Every workspace section IS an ion. The root capsule IS the manifest ion. `compile_three_tier()` IS the workspace boot. The living workspace and the ION runtime merge into a single system.

---

## §11. Self-Audit

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Integrates existing capsule/v1 | ✅ | §8 maps capsule into MISSION + ORCHESTRATION |
| Integrates existing ION context compiler | ✅ | §6 maps compile_three_tier → root capsule budget |
| Integrates Atlas continuity doctrine | ✅ | §5 lifecycle maps to continuity bundle |
| Follows Constitution Art. 25 (selective loading) | ✅ | Context profiles control what loads |
| Variable density per agent | ✅ | §4 — AETHER max, ATLAS minimal |
| LLM-specific adjustments | ✅ | §4.3 — attention efficiency formula |
| Rolling context compression | ✅ | §3.3 — 7-level gradient |
| Addresses Braden's vision items | ✅ | Calendar/orch, rolling context, goals, issues, user info, relationships, inbox/outbox, polyglot/persona, history, mission, comms — all present |
| AI lives inside the capsule | ✅ | §2 + §7 — workspace IS the agent's state |
| Deep filesystem branches | ✅ | §9 — full directory tree |
| Doctrine routing built into files | ✅ | §3.1 doctrine section + §3.13 cognitive section |

---

*Governed by: AETHER_CONSTITUTION Art. 24, 25*
*Evolved from: AETHER_INTERFACE capsule/v1, Atlas Book IV, victus/ion/context_compiler.py*
*— Opus, 2026-03-24*
