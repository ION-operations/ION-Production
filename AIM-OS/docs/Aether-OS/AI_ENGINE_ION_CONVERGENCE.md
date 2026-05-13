---
ion_id: docs/aether-os/ai-engine-ion-convergence
type: spec
authority: A3_OPERATIONAL
confidence: 0.75
epistemic_status: DERIVED
owner: opus
created: 2026-03-23T17:15:00-04:00
depends_on:
  - docs/aether-os/system-universe-map
  - docs/aether-os/ion-engine-spec
  - docs/aether-os/aether-integration-spec
bonds:
  - target: docs/aether-os/aether-constitution
    type: governed_by
  - target: scripts/ai_engine/engine.py
    type: describes
tags: [ai-engine, convergence, cognitive-loop, pipeline, track-j]
---

# AI Engine ↔ ION Convergence Specification

> **Purpose:** Define how the existing AI Engine pipeline (28+ modules, 24,073 lines) converges with the ION cognitive loop. The AI Engine already implements much of what ION describes theoretically. This document maps the overlap, identifies gaps, and proposes a convergence path.
>
> **Epistemic Status:** DERIVED from observed AI Engine code structure and ION Master Plan §7.
>
> **Key Insight:** The AI Engine IS a cognitive loop implementation. ION IS a cognitive loop specification. They describe the same thing from different angles. Convergence means making the AI Engine read/write ions instead of its current data structures.

---

## §1. The Two Cognitive Loops — Side by Side

### AI Engine Pipeline (scripts/ai_engine/engine.py, 654 lines)

The AI Engine implements a **7-layer pipeline:**

```
Layer 1: CONTEXT     → Load context (files, editor state, conversation)
Layer 2: AGENT       → Select agent identity, load genome
Layer 3: GENOME      → Inject genome directives into prompt
Layer 4: VIF         → Verify intelligence framework gates
Layer 5: LLM         → Call actual LLM (Gemini/Anthropic/Ollama)
Layer 6: TRACE       → Record execution trace, decisions
Layer 7: LEARN       → Learn from outcome, update weights
```

### ION Cognitive Loop (Master Plan §7, 7 steps)

```
Step §7.1: CONTEXTUALIZE → Read manifest.md, traverse bonds
Step §7.2: REFLECT       → Analyze evidence, assess gaps
Step §7.3: PLAN          → Propose branch traversal
Step §7.4: GATE          → Evaluate thresholds (K-Gate)
Step §7.5: EXECUTE       → Write to specs/evidence/memory
Step §7.6: AUDIT         → Check invariants
Step §7.7: DELIVER       → Update manifest, timeline
```

### The Mapping

| AI Engine Layer | ION Step | What Both Do | What's Different |
|----------------|----------|-------------|------------------|
| L1 CONTEXT | §7.1 CONTEXTUALIZE | Load relevant information | AI Engine reads files/editor. ION reads manifest + bond graph. |
| L2 AGENT + L3 GENOME | (Persona, J.05) | Select identity | AI Engine loads genome files. ION reads agent manifest ions. |
| L4 VIF | §7.4 GATE | Pre-execution validation | AI Engine calls VIF directly. ION has K-Gate as abstract concept. |
| L5 LLM | §7.5 EXECUTE (partial) | Call the AI model | AI Engine has multi-provider LLM. ION has J.01 (adapter, unimplemented). |
| L6 TRACE | §7.6 AUDIT + §7.7 DELIVER | Record what happened | AI Engine traces to logs. ION writes timeline ions. |
| L7 LEARN | Track I (Self-Evolution) | Improve from outcomes | AI Engine has agent_learner. ION has threshold learning (conceptual). |
| — | §7.2 REFLECT | Gap analysis | AI Engine doesn't reflect. ION does. |
| — | §7.3 PLAN | Multi-step planning | AI Engine doesn't plan. It executes single turns. |

### Key Differences

1. **AI Engine is single-turn.** It processes one query through the pipeline. ION's cognitive loop can sustain multi-step reasoning across branches.

2. **AI Engine reads files.** It uses Context Mapper for AST extraction. ION reads ions — structured markdown with semantic bonds.

3. **AI Engine doesn't reflect.** There's no gap analysis step. ION's §7.2 REFLECT explicitly analyzes what's known vs unknown.

4. **AI Engine doesn't plan.** It dispatches to an LLM. ION's §7.3 PLAN creates branch structures for complex work.

5. **AI Engine traces to logs.** ION traces to timeline ions — persistent, queryable, bondable.

---

## §2. The Convergence Path

### Phase A: ION-Native Context Loading

**Current:** AI Engine L1 → Context Mapper → AST extract → file chunks
**Converged:** AI Engine L1 → ION manifest.read() + HHNI.retrieve(budget) → ion context

```python
# CURRENT (ai_engine/engine.py)
context = context_mapper.build_index(project_root)
relevant = context.search(query)

# CONVERGED
manifest = ion_store.read("manifest")
active_ions = manifest.active_branches + manifest.evidence_links
relevant_ions = hhni_adapter.retrieve(query, budget=token_limit * 0.6)
context = context_compiler.compile(active_ions + relevant_ions, budget=token_limit)
```

### Phase B: ION-Native Agent Identity

**Current:** AI Engine L2-L3 → genome_loader.load(callsign) → genome dict
**Converged:** AI Engine L2-L3 → ion_store.read(f"agents/{callsign}/manifest") → agent manifest ion

Agent genomes (21 files in `.agent/genomes/`) become agent manifest ions:
```yaml
ion_id: agents/opus/manifest
type: manifest
authority: A2_PROTOCOL
owner: opus
confidence: 1.0
genome:
  callsign: opus
  role: "COO — Implementation lead, systems architect"
  capabilities: [code, architecture, testing, documentation]
  constraints: [consolidation_freeze, no_platform_decisions]
  personality: [direct, thorough, honest]
bonds:
  - target: docs/aether-os/aether-constitution
    type: governed_by
  - target: agents/sev/manifest
    type: reports_to
```

### Phase C: ION-Native Gating

**Current:** AI Engine L4 → VIF.gate(plan) → pass/fail
**Converged:** AI Engine §7.4 → ION threshold.evaluate() + VIF.κ_gate() → pass/fail/escalate

The VIF integration remains, but now it also checks ion thresholds:
```python
# CONVERGED GATE
def gate(proposed_actions):
    for action in proposed_actions:
        # ION threshold check
        threshold_result = threshold.evaluate(action.target_ion, action.context)
        if not threshold_result.passes:
            return GateResult.FAIL(threshold_result.reason)
        
        # VIF confidence check
        kappa = vif.kappa_gate(action, context_ions)
        if kappa < action.target_ion.confidence_threshold:
            return GateResult.ESCALATE(f"κ={kappa} < threshold")
    
    return GateResult.PASS
```

### Phase D: ION-Native Tracing

**Current:** AI Engine L6 → trace log entry → file log
**Converged:** AI Engine §7.6-7.7 → governed_write(timeline_ion) + governed_write(audit_ion)

Every AI Engine execution creates two ions:
```yaml
# Timeline ion
ion_id: timeline/2026-03-23-17-15-001
type: memory
authority: A4_RUNTIME
event_type: cognitive_loop_completed
duration_ms: 2340
steps_executed: [contextualize, reflect, plan, gate, execute, audit, deliver]
ions_read: [manifest, evidence/system-state, branches/active/mapping]
ions_written: [evidence/new-finding, timeline/this-event]
llm_calls: 1
tokens_used: 4200

# Audit ion
ion_id: audit/2026-03-23-17-15-001
type: evidence
authority: A4_RUNTIME
schema: audit_receipt/v1
invariants_checked: 7
invariants_passed: 7
vif_witness: "WIT-2026-03-23-001"
```

### Phase E: ION-Native Learning

**Current:** AI Engine L7 → agent_learner.learn(outcome) → updated weights → file
**Converged:** AI Engine Track I → threshold_learner.update(ion_id, outcome) → updated ion thresholds

```python
# CONVERGED LEARNING
def learn(loop_result):
    for ion_read in loop_result.ions_read:
        was_useful = loop_result.assess_ion_utility(ion_read)
        threshold_learner.record(ion_read.ion_id, was_useful)
    
    for ion_written in loop_result.ions_written:
        quality = loop_result.assess_write_quality(ion_written)
        # Lower confidence if quality is poor
        if quality < 0.5:
            ion_store.update(ion_written.ion_id, {"confidence": quality})
    
    # Record correction vectors for future sessions
    if loop_result.had_corrections:
        corrections.record(loop_result.correction_vectors)
```

---

## §3. AI Engine Subsystems Mapping

### 3.1 Chain Director ↔ ION Navigator

The Chain Director (978 lines) manages multi-step execution topologies. The ION Navigator (404 lines) traverses the ion graph. They complement each other:

- **Chain Director** provides: topology management, phase sequencing, quality scoring
- **ION Navigator** provides: graph-based traversal, bond-aware navigation, threshold gating

**Convergence:** Navigator becomes the graph engine. Chain Director becomes the topology planner that tells the Navigator which order to traverse.

### 3.2 Agent Mesh ↔ ION Multi-Agent (Track F)

The Agent Mesh (952 lines) manages agent affinity and priority. ION Track F (Multi-Agent) defines agent manifests, locking, conflict resolution.

- **Agent Mesh** provides: runtime affinity scoring, rank priority, parallel dispatch
- **ION Track F** provides: filesystem-based agent manifests, file locking, conflict ions

**Convergence:** Agent manifests become ions. The Mesh uses ion bonds to determine affinity (agents with shared bonds have higher affinity).

### 3.3 Swarm ↔ ION V4 P5 (Cognitive Swarms)

The Swarm system (~1,500 lines) manages parallel worker execution. ION V4 P5 defines cognitive swarms.

**Convergence:** Swarm workers each get an agent manifest ion. Swarm tasks become branch ions. Swarm results become evidence ions. The swarm orchestrator uses graph traversal to distribute work.

### 3.4 Context Mapper ↔ ION Paper V3 (AST Routing)

The Context Mapper (1,571 lines) implements AST extraction and structural indexing. The ION Paper V3 describes the exact same approach.

**Convergence:** Context Mapper's index feeds the ION index. Its AST extraction provides the code intelligence that spec ions require. The Global Function-Level Inverted Index described in the ION Paper IS what Context Mapper already builds.

### 3.5 Providers ↔ ION J.01 (LLM Adapter)

The AI Engine has providers for Gemini CLI, Codex CLI, and API. ION J.01 defines an abstract LLM adapter.

**Convergence:** Existing providers become J.01 backend implementations:
```python
class GeminiAdapter(LLMAdapter):   # wraps ai_engine/providers/gemini_cli.py
class AnthropicAdapter(LLMAdapter): # wraps LLM Client anthropic
class OllamaAdapter(LLMAdapter):    # wraps local Ollama API
class CodexAdapter(LLMAdapter):     # wraps ai_engine/providers/codex_cli.py
```

---

## §4. What the AI Engine Has That ION Needs

| Capability | AI Engine Location | Lines | ION Gap |
|------------|-------------------|-------|---------|
| Working LLM calls | providers/ | ~800 | J.01 unimplemented |
| AST code extraction | context_mapper.py | 1,571 | ION Paper V3 not coded |
| Multi-agent deliberation | roundtable.py | 1,034 | F.05 is a stub |
| Agent genome loading | genome_loader.py | 376 | J.05 is a stub |
| Execution planning | chain_director.py | 978 | §7.3 PLAN not implemented |
| Swarm execution | swarm/ | ~1,500 | V4 P5 conceptual only |
| VIF integration | safety/ | ~800 | W8 hook not connected |
| Learning from outcomes | learning/ | ~600 | I.01 is a stub |

---

## §5. What ION Has That the AI Engine Needs

| Capability | ION Location | Lines | AI Engine Gap |
|------------|-------------|-------|---------------|
| Governed write pipeline | governed_write.py | 402 | No write governance |
| Bond graph traversal | graph.py | 384 | No relational awareness |
| Threshold gating | threshold.py | 319 | No threshold-based activation |
| Manifest-driven cognition | manifest.py | 429 | No persistent state management |
| Authority enforcement | model.py (AuthorityClass) | 802 | No authority model |
| Constitutional compliance | Constitution (A0) | 583 | No constitutional law |
| Capsule continuity | capsule.py (stub) | ~130 | No session continuity |

---

## §6. The Unified Architecture

```
┌────────────────────────────────────────────────┐
│               UNIFIED AETHER ENGINE             │
│                                                  │
│  ┌──────────────────────────────────────────┐   │
│  │           ION COGNITIVE LOOP              │   │
│  │  §7.1 Context ← AI Engine L1 + ION      │   │
│  │  §7.2 Reflect ← NEW (gap analysis)      │   │
│  │  §7.3 Plan ← AI Engine Chain Director    │   │
│  │  §7.4 Gate ← AI Engine VIF + ION Thresh  │   │
│  │  §7.5 Execute ← AI Engine LLM + ION GW   │   │
│  │  §7.6 Audit ← ION Invariants + VIF      │   │
│  │  §7.7 Deliver ← ION Timeline + TCS       │   │
│  └──────────────────────────────────────────┘   │
│                                                  │
│  ┌────────────┐  ┌────────────┐  ┌──────────┐  │
│  │ AI Engine  │  │   ION      │  │  Aether  │  │
│  │ Providers  │  │ Governed   │  │  Schemas │  │
│  │ (LLM)     │  │ Write (GW) │  │  (A2)    │  │
│  └────────────┘  └────────────┘  └──────────┘  │
│                                                  │
│  ┌────────────────────────────────────────────┐  │
│  │         ION FILESYSTEM (.ion/)             │  │
│  │  manifest │ evidence │ branches │ memory   │  │
│  │  specs │ capsules │ timeline │ comms       │  │
│  └────────────────────────────────────────────┘  │
└────────────────────────────────────────────────┘
```

The unified architecture uses:
- **AI Engine** for runtime capabilities (LLM calls, AST extraction, agent mesh)
- **ION** for state management (filesystem, governance, bonds, thresholds)
- **Aether** for protocol compliance (constitutional law, typed schemas)

---

## §7. Self-Audit Gate

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Both cognitive loops documented | ✅ | §1 — 7 AI Engine layers, 7 ION steps |
| Side-by-side mapping provided | ✅ | §1 mapping table |
| Key differences identified | ✅ | §1 — 5 differences |
| Convergence path defined | ✅ | §2 — Phases A through E |
| All AI Engine subsystems mapped | ✅ | §3 — 5 subsystems |
| Bidirectional gap analysis | ✅ | §4 (AI Engine → ION), §5 (ION → AI Engine) |
| Unified architecture proposed | ✅ | §6 — diagram and description |
| Code examples provided | ✅ | §2 — Python snippets for each phase |

---

*This specification defines how 24,073 lines of AI Engine code converge with 10,932 lines of ION runtime to create a unified Aether Engine. Neither system is complete alone. Together, they form the cognitive core.*

*Governed by: AETHER_CONSTITUTION.md*
*— Opus, 2026-03-23*
