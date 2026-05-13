# Agent Building & Cloning System — Enhanced Spec V3

**Status:** Proposal (Antigravity + Codex synthesis)
**Date:** 2026-03-04
**Authors:** Antigravity (Opus agent), synthesizing Codex V2 spec + deep codebase research
**Audience:** Braden, all AIM-OS agents
**Supersedes:** `AGENT_BUILDING_AND_CLONING_SYSTEM_SPEC_V2.md` (Codex)

---

## 0) Design Philosophy

> *"There is a limit to the efficiency of a specialist defined by their breadth of skills. It may be better to keep highly specialized agents working together rather than one agent adjusting its rules and context back and forth."* — Braden

This spec operationalizes that principle. An agent is NOT a temporary persona. It is a **persistent cognitive entity** with its own memory, skills, and evolutionary trajectory. The entire system is designed so that the network of agents can collectively hold knowledge that exceeds any single intelligence — human or AI.

---

## 1) Canonical Definitions (Codex V2, refined)

| Term | Definition | Persistence |
|------|-----------|-------------|
| **Role** | Execution function for a step (planner, retriever, builder, critic, verifier) | Ephemeral — lives inside one task |
| **Agent** | Persistent identity with Behavioral DNA + Knowledge DNA + Metrics | Permanent — survives across sessions |
| **Specialist** | Agent with bounded domain ownership and activation thresholds | Permanent — domain is its identity |
| **Clone** | New agent derived from parent genome + mutation delta | Permanent — separate lineage branch |
| **Genome** | Versioned, immutable snapshot of an agent's complete state | Immutable — append-only |
| **Handoff** | Task-time transfer of ownership when relevance drops below threshold | Event — logged with rationale |
| **Fission** | Evolution-time splitting of one agent into two when breadth degrades performance | Structural — creates new lineage |

### Role vs Agent — The Critical Distinction

```
┌─────────────────────────────────────────────┐
│ AGENT: "Dispatch Specialist"                │
│ ┌─────────────────────────────────────────┐ │
│ │ Behavioral DNA (always active):         │ │
│ │ • Focus: AI dispatch orchestration      │ │
│ │ • Skills: BAS integration, routing      │ │
│ │ • Policy: supervised dispatch, no vault  │ │
│ ├─────────────────────────────────────────┤ │
│ │ Knowledge DNA (always warm):            │ │
│ │ • Episode history: 847 dispatches       │ │
│ │ • Context: provider latency patterns    │ │
│ │ • Learned: Gemini better for code tasks │ │
│ ├─────────────────────────────────────────┤ │
│ │ Current Task: Multi-provider dispatch   │ │
│ │ ┌──────┐ ┌──────┐ ┌──────┐ ┌────────┐  │ │
│ │ │Plan  │→│Route │→│Send  │→│Verify  │  │ │
│ │ │(role)│ │(role)│ │(role)│ │(role)  │  │ │
│ │ └──────┘ └──────┘ └──────┘ └────────┘  │ │
│ └─────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

**Roles live INSIDE agents.** An agent uses roles as execution steps. But the agent's identity, knowledge, and behavioral policy persist across all tasks.

---

## 2) The Two Pillars of an Agent

### Pillar 1: Behavioral DNA (Rules/Skills)

```yaml
behavioral_dna:
  identity:
    name: "Dispatch Specialist"
    purpose: ["Orchestrate multi-provider AI dispatches"]
    personality: "Precise, efficiency-focused, metric-driven"
    
  policies:
    autonomy: supervised          # auto | supervised | manual
    oracle_integration: true      # Responds to Oracle commands
    max_cost_per_action: 0.50     # USD budget guardrail
    forbidden_systems: [vault, settings]
    
  competence:
    tools: [bas.sendPrompt, bas.fullSession, mcp.dispatch]
    skills:
      - { id: "multi-provider-routing", version: "1.3.0" }
      - { id: "consensus-synthesis", version: "0.9.1" }
    playbooks:
      - { id: "parallel-dispatch", steps: 4, avg_duration: "12s" }
      - { id: "sequential-chain", steps: 6, avg_duration: "45s" }
```

### Pillar 2: Knowledge DNA (Context Banks)

```yaml
knowledge_dna:
  channels:
    short:    # Current task context (TTL: task duration)
      capacity: 8000 tokens
      contents: "active dispatch targets + prompt"
    scratch:  # Session working memory (TTL: session)
      capacity: 16000 tokens
      contents: "recent results, provider states"
    long:     # Agent memory (TTL: permanent, compacted)
      capacity: 64000 tokens
      contents: "learned provider patterns, failure modes"
    ops:      # Mission execution log (TTL: 30 days)
      capacity: 32000 tokens
      contents: "dispatch logs, latency measurements"
      
  shared_knowledge:   # Read-only, from SEG
    - ref: "provider-capability-matrix"
    - ref: "bas-api-contracts"
    
  episodes:           # Experience history (compressed)
    total: 847
    last_compressed: "2026-03-01T00:00:00Z"
    compression_ratio: 12:1
```

---

## 3) Specialization-Breadth Curve & Fission Algorithm

### The Curve (from Antigravity research)

```
Performance
    │
    │     ╭──────╮
    │    ╱        ╲    ← Fission Point: when adding breadth
    │   ╱  OPTIMAL ╲      causes more harm than splitting
    │  ╱    ZONE    ╲     into two specialists would
    │ ╱              ╲
    │╱                ╲________
    └──────────────────────────── Breadth
```

### FissionScore Formula (Codex V2, enhanced)

```python
def compute_fission_score(agent: AgentGenome, window: int = 20) -> float:
    """
    Compute whether an agent should split into two specialists.
    Returns 0.0 (no fission needed) to 1.0 (urgent fission).
    
    Trigger: FissionScore >= 0.65 sustained over 20+ episodes
    """
    recent = agent.episodes[-window:]
    
    # 1. Domain Entropy — how spread across domains is the work?
    #    High entropy = agent is being asked to do too many things
    domain_entropy = shannon_entropy(
        [ep.primary_domain for ep in recent]
    ) / max_possible_entropy(agent.domains)
    
    # 2. Context Switch Frequency — how often does domain change?
    #    High switching = agent keeps losing context
    switches = sum(
        1 for i in range(1, len(recent))
        if recent[i].primary_domain != recent[i-1].primary_domain
    )
    switch_rate = switches / len(recent)
    
    # 3. Confidence Decay — does confidence drop in any domain?
    #    Decay in a domain = losing expertise there
    domain_confidences = group_by_domain(recent, metric='confidence')
    max_decay = max(
        linear_regression_slope(confidences)
        for confidences in domain_confidences.values()
    )
    confidence_decay = max(0, -max_decay)  # Positive = decaying
    
    # 4. Token Waste — irrelevant context loaded for current task
    avg_relevance = mean(ep.context_relevance_score for ep in recent)
    token_waste = 1.0 - avg_relevance
    
    # 5. Cost/Latency Drift — is the agent getting slower/costlier?
    cost_drift = linear_regression_slope([ep.cost for ep in recent])
    latency_drift = linear_regression_slope([ep.latency for ep in recent])
    drift = max(0, (cost_drift + latency_drift) / 2)
    
    # Weighted composite
    return (
        0.25 * domain_entropy +
        0.25 * switch_rate +
        0.20 * confidence_decay +
        0.15 * token_waste +
        0.15 * drift
    )
```

### Fission Execution

When `FissionScore >= 0.65` persists for 20+ episodes:

1. **Identify split point**: Cluster recent episodes by domain → find the natural split
2. **Clone parent**: `clone(parent, new_id, mutation_delta={domains: cluster_B})`
3. **Partition context banks**: Domain-A knowledge → parent, Domain-B knowledge → clone
4. **Re-score both**: Run eval suite on each specialist in their narrowed domain
5. **If both improve**: Promote both; retire the parent's broad version
6. **If only one improves**: Keep the specialist, revert the other to parent

---

## 4) Oracle Integration (NEW — from Antigravity)

The Aether Oracle controls agents, and agents register with the Oracle via PageOracleAPI:

```
┌──────────────┐     ┌─────────────────┐     ┌──────────────┐
│ Aether Oracle │────→│ Agent Registry  │────→│ Active Agents│
│  (control)    │     │ (genome manager)│     │  (executing) │
└──────┬───────┘     └────────┬────────┘     └──────┬───────┘
       │                      │                      │
       │  mode: auto          │  activate/deactivate │  handoff
       │  mode: supervised    │  clone/promote       │  events
       │  mode: manual        │  fission/retire      │
       │                      │                      │
       └──────────────────────┴──────────────────────┘
                    PageOracleAPI Event Bus
```

### Oracle Permission Model for Agent Operations

| Operation | auto | supervised | manual |
|-----------|------|-----------|--------|
| Activate specialist | ✅ | ✅ | ❌ |
| Handoff between agents | ✅ | ✅ | ❌ |
| Clone agent | ❌ | ✅ (approve) | ❌ |
| Promote agent version | ❌ | ✅ (approve) | ❌ |
| Fission agent | ❌ | ✅ (approve) | ❌ |
| Retire agent | ❌ | ❌ | ✅ (user only) |

> [!CAUTION]
> **Retiring an agent is ALWAYS manual.** No agent can be deleted autonomously. This is a canon-level guardrail.

---

## 5) Context Bank Evolution Protocol (NEW)

### Growth Cycle

```
Episode Recorded
    ↓
Short Channel Updated (task-scoped)
    ↓
Task Complete → Compress to Scratch
    ↓
Session End → Compress to Long
    ↓
Compaction Threshold Hit (64K tokens)
    ↓
Extract Key Learnings → SEG Pointers
    ↓
Discard Raw Episodes (keep summaries)
    ↓
Long Channel Stays Under Budget
```

### TTL Policy

| Channel | TTL | Compaction | Max Size |
|---------|-----|-----------|----------|
| `short` | Task duration | Auto on task end | 8K tokens |
| `scratch` | Session | Auto on session end | 16K tokens |
| `long` | Permanent | Weekly compaction | 64K tokens |
| `ops` | 30 days | Monthly archive | 32K tokens |

### Relevance Decay

Context items decay in relevance over time: `relevance(t) = base_relevance × e^(-λt)`. When relevance drops below 0.3, the item is eligible for compaction. This prevents unbounded context growth while preserving important knowledge.

---

## 6) Lifecycle Protocol (Codex V2, enhanced with Oracle hooks)

| # | Stage | Action | Oracle Hook |
|---|-------|--------|-------------|
| 1 | **Onboard** | Register identity, create genome, create channels | `agent:registered` event |
| 2 | **Activate** | Detect work → score relevance → assign ownership | Oracle can trigger in `auto` mode |
| 3 | **Execute** | Build APOE role chain, log witnesses | Oracle monitors in `supervised` |
| 4 | **Learn** | Store episodes, update metrics, compress context | Automatic — no approval needed |
| 5 | **Snapshot** | Write immutable genome version | `agent:snapshot` event |
| 6 | **Clone** | Create child with mutation delta + isolated channels | Requires `supervised` approval |
| 7 | **Promote** | Tournament → gate validation → alias update | Requires `supervised` approval |
| 8 | **Fission** | FissionScore threshold → recommend split → execute | Requires `supervised` approval |
| 9 | **Retire** | Freeze alias, preserve lineage | **Manual only** — user must approve |

---

## 7) JOC Agent Builder Page Design (Antigravity scope)

### Layout (3 panels)

```
┌────────────────────────────────────────────────────────────┐
│ AGENT BUILDER                                    [Create] │
├──────────┬────────────────────────┬────────────────────────┤
│ Registry │ Agent Inspector        │ Lineage Graph          │
│          │                        │                        │
│ ● Atlas  │ ┌──────────────────┐   │     [Atlas]            │
│ ● Lex    │ │ Lex v2.3.1       │   │      ↙ ↘              │
│ ● Codex  │ │ Domain: Language  │   │  [Lex-A] [Lex-B]     │
│ ● Solo   │ │ Mode: supervised  │   │     ↓                │
│ ● Math   │ │ Health: 94%       │   │  [Lex-A2]  ← promoted│
│ ● UI     │ │ Episodes: 234     │   │                       │
│           │ │ FissionScore: 0.23│   │                       │
│ [+ New]   │ └──────────────────┘   │                       │
│ [Clone]   │                        │                       │
│ [Import]  │ [Behavioral DNA]       │ [Timeline View]       │
│           │ [Knowledge DNA]        │ [Tournament History]  │
│           │ [Metrics]              │ [Gate Log]            │
│           │ [Context Health]       │                       │
└──────────┴────────────────────────┴────────────────────────┘
```

### Key Features

1. **Create Agent**: Define name, purpose, domains, initial skills, autonomy mode
2. **Clone Agent**: Select parent → define mutation delta → create isolated clone
3. **Inspect Health**: Context bank fullness, relevance scores, FissionScore gauge
4. **Lineage Graph**: Interactive force-directed graph showing parent→child relationships
5. **Tournament View**: Compare clone variants side by side (win-rate, cost, latency)
6. **Gate Log**: History of promotion attempts — passed/failed gates with rationale

---

## 8) Delivery Plan (Codex V2, enhanced with Oracle phases)

| Phase | Focus | Deliverables | Owner |
|-------|-------|-------------|-------|
| **0** | Contract | Finalize this spec + schemas | All agents |
| **1** | Runtime Core | `packages/agent_genome/` — registry, snapshot, clone, diff | Codex |
| **2** | Specialist Bridge | Wire specialist activation → APOE → genome logging | Codex |
| **3** | Context Evolution | Channel isolation, compaction, episode capture | Codex + Antigravity |
| **4** | Oracle Integration | Wire genome events to Oracle event bus, permission model | Antigravity |
| **5** | Fission Engine | FissionScore telemetry, recommendation UI, auto-split | Codex + Antigravity |
| **6** | JOC Agent Builder | Full UI page (registry, inspector, lineage, tournaments) | Antigravity |
| **7** | Promotion Engine | Tournament runner, gate evaluator, rollback workflow | Codex |

---

## 9) Acceptance Criteria

The system is production-ready when:

1. ✅ Agents can be created, snapshotted, cloned, and resolved deterministically
2. ✅ Clone memory isolation is enforced and tested
3. ✅ Ownership/handoff is logged with reproducible rationale
4. ✅ Promotion cannot bypass VIF confidence + parity + budget gates
5. ✅ FissionScore is computed and displayed for all active agents
6. ✅ Oracle can activate/deactivate/handoff agents in `auto` and `supervised` modes
7. ✅ JOC Agent Builder page renders registry, inspector, lineage graph, and gate log
8. ✅ Context bank compaction runs on schedule without data loss
9. ✅ Retiring an agent requires explicit user approval (never autonomous)

---

## 10) Source References

| Source | Path |
|--------|------|
| Codex V2 Spec | [AGENT_BUILDING_AND_CLONING_SYSTEM_SPEC_V2.md](file:///C:/Users/bombe/OneDrive/Desktop/AIM-OS/docs/AGENT_BUILDING_AND_CLONING_SYSTEM_SPEC_V2.md) |
| Antigravity Research | [agent_architecture_research.md](file:///C:/Users/bombe/.gemini/antigravity/brain/b9c41de3-025a-4f17-821b-defafe76f822/agent_architecture_research.md) |
| Agent Genome T2 | [T2_architecture.md](file:///C:/Users/bombe/OneDrive/Desktop/AIM-OS/knowledge_architecture/systems/agent_genome/T2_architecture.md) |
| Specialist Architecture | [SPECIALIST_AGENT_ARCHITECTURE.md](file:///C:/Users/bombe/OneDrive/Desktop/AIM-OS/knowledge_architecture/AGENT_ONBOARDING/SPECIALIST_AGENT_ARCHITECTURE.md) |
| Specialist Registry | [specialist_registry.py](file:///C:/Users/bombe/OneDrive/Desktop/AIM-OS/packages/specialist_system/specialist_registry.py) |
| Oracle Store | [oracleStore.ts](file:///C:/Users/bombe/OneDrive/Desktop/AIM-OS/packages/joc/src/store/oracleStore.ts) |
| PageOracleAPI | [usePageOracle.ts](file:///C:/Users/bombe/OneDrive/Desktop/AIM-OS/packages/joc/src/hooks/usePageOracle.ts) |
