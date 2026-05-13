---
ion_id: docs/aether-os/aether-integration-spec
type: spec
authority: A3_OPERATIONAL
confidence: 0.80
epistemic_status: DERIVED
owner: opus
created: 2026-03-23T17:00:00-04:00
depends_on:
  - docs/aether-os/system-universe-map
  - docs/aether-os/ion-engine-spec
  - docs/aether-os/ion-master-plan
affects:
  - docs/aether-os/missing-systems-analysis
bonds:
  - target: docs/aether-os/aether-constitution
    type: governed_by
  - target: docs/aether-os/aether-interface
    type: implements
tags: [integration, core-infrastructure, cmc, hhni, vif, apoe, seg, tcs]
---

# Aether Integration Specification — Core Infrastructure ↔ ION Convergence

> **Purpose:** Detailed specification of how the 6 core infrastructure systems (CMC, HHNI, VIF, APOE, SEG, TCS — totaling 150,284 lines) integrate with the ION engine. For each system, this document defines the integration surface, data flow, protocol mappings, and implementation pathway.
>
> **Epistemic Status:** DERIVED from ION Master Plan, Aether Constitution, and observed system registries. Integration designs are SPECULATIVE until validated by implementation.
>
> **Governing Law:** AETHER_CONSTITUTION.md, AETHER_INTERFACE.md (21 schemas)
>
> **Key Principle (from Atlas V1):** The system moves from *inference-all-the-time* to *governance-always, reaction-by-default, inference-only-when-thresholds-demand-it.*

---

## §1. Integration Architecture Overview

The 6 core infrastructure systems form a **service constellation** around the ION engine. Each provides a capability that ION needs but doesn't have natively:

```
                    ┌──────────────────────────────┐
                    │      ION ENGINE (10,932 L)    │
                    │  model │ parser │ store │ gw  │
                    │  manifest │ index │ graph     │
                    │  threshold │ navigator        │
                    └──────┬───────┬───────┬────────┘
                           │       │       │
           ┌───────────────┤       │       ├───────────────┐
           │               │       │       │               │
    ┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
    │  CMC        │ │  HHNI       │ │  VIF        │ │  TCS        │
    │  23,460 L   │ │  13,198 L   │ │  20,525 L   │ │  44,492 L   │
    │  Bitemporal │ │  Fractal    │ │  Confidence │ │  Context    │
    │  Memory     │ │  Retrieval  │ │  Calibration│ │  Continuity │
    └──────┬──────┘ └─────────────┘ └──────┬──────┘ └──────┬──────┘
           │                               │               │
    ┌──────▼──────┐                 ┌──────▼──────┐        │
    │  SEG        │                 │  APOE       │        │
    │  6,050 L    │                 │  34,529 L   │        │
    │  Evidence   │                 │  Execution  │        │
    │  Graph      │                 │  Planning   │        │
    └─────────────┘                 └─────────────┘        │
                                                           │
                    ┌──────────────────────────────┐        │
                    │      AETHER ENGINE (J.03)    │◄───────┘
                    │  LLM + Navigator + Context    │
                    └──────────────────────────────┘
```

### Integration Roles

| System | ION Role | C1/C2/C3 Layer | Integration Point |
|--------|---------|---------------|-------------------|
| **CMC** | Memory indexing backend | C2 (Reactive) | `store.py` — persistent query index |
| **HHNI** | Retrieval optimizer | C2 (Reactive) | `index.py` — fractal search |
| **VIF** | Confidence calibrator | C2/C3 (Reactive/Escalation) | `governed_write.py` W8-W9 |
| **APOE** | Execution planner | C1 (Organizer) | `navigator.py` — complex task decomposition |
| **SEG** | Evidence graph runtime | C2 (Reactive) | `graph.py` — evidence synthesis |
| **TCS** | Session continuity | C2 (Reactive) | `capsule.py` — state persistence |

---

## §2. CMC — Context Memory Core Integration

> **System:** `packages/cmc_service/` — 23,460 lines
> **Subsystems:** memory_store, models, repository, store_io, advanced_compression

### 2.1 What CMC Provides That ION Needs

CMC implements **bitemporal memory** — the ability to query what was known at any point in time, not just the current state. ION's filesystem stores current state only. You can see what an ion says NOW, but not what it said LAST WEEK.

CMC's memory atoms carry:
- `valid_time` — when the fact was true in the real world
- `transaction_time` — when the fact was recorded in the system
- Provenance chains — who said what, based on what evidence
- Compression — efficient storage of historical revisions

### 2.2 Integration Design

**Principle: ION filesystem is the source of truth. CMC is the temporal query index.**

Every governed write (W10: PROPAGATE) triggers a CMC atom creation:

```
ION Governed Write Pipeline:
  W1-W9: normal pipeline stages
  W10 PROPAGATE:
    1. Write ion to filesystem          ← ION store.py
    2. Create CMC atom from ion state   ← CMC integration
    3. Index atom with valid/txn time   ← CMC memory_store
    4. Notify affected ions             ← ION graph.py
```

**Query Routing:**
- "What is the current state of ion X?" → `store.read(ion_id)` (direct filesystem)
- "What was the state of ion X last Tuesday?" → `cmc.query(ion_id, valid_time=tuesday)`
- "When did ion X change from authority A3 to A4?" → `cmc.temporal_query(ion_id, field='authority')`

**A2 Protocol Mapping:**
- CMC atoms map to AETHER_INTERFACE Schema 17 (`memory_atom/v1`):
  ```yaml
  schema: memory_atom/v1
  atom_id: "cmc-{ion_id}-{timestamp}"
  content_type: ion_snapshot
  valid_time: "2026-03-23T17:00:00"
  transaction_time: "2026-03-23T17:00:01"
  provenance: 
    source: "governed_write"
    agent: "opus"
    pipeline_stage: "W10"
  ```

### 2.3 What Must Be Built

| Component | Lines (est) | Priority |
|-----------|-------------|----------|
| `CMCAdapter` — wraps CMC API for ION consumption | ~200 | HIGH |
| Governed write W10 hook — emit CMC atom on write | ~100 | HIGH |
| Temporal query router — route temporal queries to CMC | ~150 | MEDIUM |
| Ion revision history — display all versions of an ion | ~100 | MEDIUM |

---

## §3. HHNI — Hierarchical Hypergraph Neural Index Integration

> **System:** `packages/hhni/` — 13,198 lines
> **Subsystems:** budget_manager, retrieval, dvns_physics, deduplication, conflict_resolver, compressor

### 3.1 What HHNI Provides That ION Needs

ION's `index.py` (318 lines) is a flat in-memory dictionary. It works for small ion trees (<1,000 ions), but cannot scale.

HHNI provides:
- **Fractal indexing** — hierarchical search that zooms from universe to atom
- **Budget management** — fit maximum relevance within a token budget
- **DVNS physics** — gravity-based relevance scoring (more referenced = higher gravity)
- **Deduplication** — detect and merge near-duplicate ions
- **Conflict resolution** — when two ions say contradictory things

### 3.2 Integration Design

**Principle: ION index is the filesystem index. HHNI is the semantic relevance index.**

```
ION Query Flow:
  1. Simple lookup: "get ion X"
     → index.lookup(ion_id)                    ← ION index.py, O(1)
  
  2. Filtered search: "all evidence ions by opus"
     → index.query(type=EVIDENCE, owner=opus)  ← ION index.py
  
  3. Relevance search: "most relevant ions for this LLM query"
     → hhni.retrieve(query, budget=4000)       ← HHNI retrieval
     → returns ranked ion_ids within token budget
```

**Budget-Aware Context Compilation:**
HHNI's budget manager integrates directly with ION's context compiler (J.02):
```
Aether Engine §7.1 CONTEXTUALIZE:
  1. Read manifest → get active branches, evidence links      ← ION
  2. HHNI.retrieve(query, budget=model_context_window * 0.6)  ← HHNI
  3. Compile retrieved ions into structured prompt              ← ION J.02
  4. Inject into LLM                                           ← ION J.01
```

**DVNS Physics as Ion Gravity:**
Every ion accumulates "gravity" based on:
- How often it's referenced (bond count)
- How recently it was updated
- Its confidence score
- Its authority class (higher authority = more gravity)

This gravity score determines retrieval priority in budget-constrained contexts.

### 3.3 What Must Be Built

| Component | Lines (est) | Priority |
|-----------|-------------|----------|
| `HHNIAdapter` — wraps HHNI retrieval for ION | ~200 | HIGH |
| Ion-to-HHNI indexer — push ion metadata to HHNI on create/update | ~150 | HIGH |
| Budget-aware context compiler — integrate HHNI with J.02 | ~250 | HIGH |
| Gravity score calculator — derive from ion bonds + confidence | ~150 | MEDIUM |

---

## §4. VIF — Verifiable Intelligence Framework Integration

> **System:** `packages/vif/` — 20,525 lines
> **Subsystems:** witness, confidence_tracker, kappa_gate, ece_tracker, audit_api

### 4.1 What VIF Provides That ION Needs

ION assigns confidence scores (0.0-1.0) to every ion, but these scores are **uncalibrated**. A confidence of 0.8 on one ion might mean "extremely reliable" while 0.8 on another means "rough guess." VIF provides:

- **ECE (Expected Calibration Error) tracking** — measures whether confidence scores match actual accuracy
- **κ-gating** — a production-grade implementation of the K-Gate concept from ION Master Plan
- **Witness envelopes** — cryptographic proof of what evidence supported a conclusion
- **Confidence tracking** — historical confidence trajectory per ion

### 4.2 Integration Design

**Principle: VIF calibrates ION's confidence scores and provides audit evidence.**

**Governed Write Integration:**
```
Governed Write Pipeline:
  W8 VERIFY:
    1. ION invariant checks                    ← existing
    2. VIF.κ_gate(ion, context)                ← NEW
       → evaluates κ = confidence × evidence_weight × consistency
       → PASS if κ ≥ threshold, FAIL otherwise
  
  W9 PROVENANCE:
    1. Write provenance record                 ← existing
    2. VIF.emit_witness(ion, pipeline_result)  ← NEW
       → creates witness envelope (A2 Schema 11)
       → includes hash of evidence, agent ID, timestamp
```

**Confidence Calibration Loop:**
```
When the Aether Engine completes a cognitive loop:
  1. Record the loop result (success/failure/partial)
  2. For each ion read/written during the loop:
     VIF.confidence_tracker.record(ion_id, was_accurate=result)
  3. Periodically:
     VIF.ece_tracker.recalibrate(all_ions)
     → adjusts confidence scores system-wide to match actual accuracy
```

**A2 Protocol Mapping:**
- VIF witness → Schema 11 (`witness_envelope/v1`)
- VIF audit → Schema 9 (`audit_receipt/v1`)
- VIF confidence → Schema 7 (`belief_state/v1`)

### 4.3 What Must Be Built

| Component | Lines (est) | Priority |
|-----------|-------------|----------|
| `VIFAdapter` — wraps VIF for ION consumption | ~200 | HIGH |
| W8 κ-gate hook — VIF gate check at verification stage | ~150 | HIGH |
| W9 witness hook — emit witness envelope at provenance stage | ~100 | HIGH |
| Confidence calibration cron — periodic recalibration | ~200 | MEDIUM |
| Ion confidence trajectory display — for dashboard | ~150 | LOW |

---

## §5. APOE — AI-Powered Orchestration Engine Integration

> **System:** `packages/apoe/` — 34,529 lines
> **Subsystems:** acl_parser, plix_compiler, execution_orchestrator, roles

### 5.1 What APOE Provides That ION Needs

ION's navigator (404 lines) traverses the graph but cannot decompose complex multi-step tasks into executable plans. APOE provides:

- **ACL (APOE Composition Language)** — a formal language for expressing execution plans
- **PLIx compilation** — compiling high-level specifications into execution steps
- **Execution orchestration** — managing multi-step, multi-agent task execution
- **Role configuration** — defining which agents can do what (maps to authority classes)

### 5.2 Integration Design

**Principle: ION provides the data graph and governance. APOE provides the execution planner.**

```
Aether Engine §7.3 PLAN:
  1. Navigator identifies required work from branch analysis    ← ION
  2. If work is simple (single ion write):
     → Execute directly (C2 reactive, no APOE needed)
  3. If work is complex (multi-step, multi-agent):
     → APOE.plan(task_description, available_agents, constraints)    ← APOE
     → Returns ACL plan with steps, dependencies, quality gates
     → Each plan step becomes a sub-branch ion in branches/active/
  4. APOE.execute(plan) with callbacks to ION for each step:
     → On step complete: write evidence ion with results
     → On step fail: write evidence ion with failure, re-plan
     → On plan complete: update branch confidence, mark done
```

**Role-Authority Mapping:**
| APOE Role | ION Authority Class | Can Do |
|-----------|-------------------|--------|
| Executor | A3_OPERATIONAL | Read/write operational ions |
| Auditor | A3_OPERATIONAL | Read all, write audit ions only |
| Supervisor | A2_PROTOCOL | Promote/demote ion authority |
| Architect | A1_PROTECTED | Modify system structure |
| Director | A0_SUPREME | Override anything (Braden only) |

**Branch Lifecycle with APOE:**
```
branches/active/complex-task.md:
  ion_id: branches/active/complex-task
  type: branch
  state: in_progress
  apoe_plan_id: "PLAN-2026-03-23-001"
  sub_branches:
    - branches/active/complex-task/step-1
    - branches/active/complex-task/step-2
    - branches/active/complex-task/step-3
  quality_gates:
    - gate: "all_steps_pass"
      threshold: 0.9
```

### 5.3 What Must Be Built

| Component | Lines (est) | Priority |
|-----------|-------------|----------|
| `APOEAdapter` — wraps APOE planning for ION | ~300 | HIGH |
| Branch-to-plan mapper — APOE plans ↔ ION branch ions | ~200 | HIGH |
| Role-authority bridge — map APOE roles to ION authority classes | ~100 | HIGH |
| Quality gate integration — APOE gates as K-Gate evaluations | ~150 | MEDIUM |

---

## §6. SEG — Shared Evidence Graph Integration

> **System:** `packages/seg/` — 6,050 lines
> **Subsystems:** graph operations, evidence ingestion, synthesis

### 6.1 What SEG Provides That ION Needs

ION has an `evidence/` directory with evidence ions, and a `graph.py` that builds bond graphs. But ION doesn't have:
- **Evidence synthesis** — combining multiple evidence items into stronger conclusions
- **Contradiction detection** — identifying when two evidence items conflict
- **Evidence ingestion** — structured intake of new evidence with classification

SEG provides all three.

### 6.2 Integration Design

**Principle: ION's evidence/ directory stores the evidence ions. SEG provides the runtime reasoning over them.**

```
When new evidence is discovered:
  1. SEG.ingest(evidence_data)                    ← SEG
     → classifies, validates, checks provenance
  2. SEG.check_contradictions(evidence_data, existing_evidence)  ← SEG
     → If contradiction found:
        Create contradiction ion (A2 Schema 8)
        Suspend dependent branches
        Escalate to C1 (Organizer)
     → If no contradiction:
        Continue
  3. ION governed_write.create(evidence_ion)       ← ION
     → 10-stage pipeline writes to evidence/
  4. SEG.synthesize(related_evidence)               ← SEG
     → creates synthesis ion combining related evidence
     → updates confidence scores based on evidence weight
```

**Contradiction Protocol (A0 Article 14):**
```yaml
# Created when SEG detects a contradiction
ion_id: contradictions/evidence-a-vs-evidence-b
type: evidence
authority: A3_OPERATIONAL
confidence: 0.0  # Zero confidence until resolved
state: suspended
contradicting_ions:
  - evidence/finding-a
  - evidence/finding-b
escalated_to: braden  # Or appropriate authority
resolution: pending
```

### 6.3 What Must Be Built

| Component | Lines (est) | Priority |
|-----------|-------------|----------|
| `SEGAdapter` — wraps SEG for ION consumption | ~200 | MEDIUM |
| Contradiction ion writer — create ION contradiction ions from SEG detection | ~150 | MEDIUM |
| Evidence synthesis router — route evidence ingestion through SEG → ION | ~200 | MEDIUM |
| Branch suspension on contradiction — auto-suspend affected branches | ~150 | MEDIUM |

---

## §7. TCS — Timeline Context System Integration

> **System:** `packages/timeline_context_system/` — 44,492 lines
> **Subsystems:** adaptive_context_dumping, timeline entries, context management

### 7.1 What TCS Provides That ION Needs

ION defines capsules (PRE and POST session snapshots) as the mechanism for session continuity — surviving context truncation. But ION's capsule implementation is a stub (~130 lines in `capsule.py`). TCS is the **most mature continuity system in the entire AIM-OS ecosystem** at 44,492 lines.

TCS provides:
- **Adaptive context dumping** — intelligently selecting what to preserve based on importance
- **Context sizing** — fitting context within model token limits
- **Session continuity** — maintaining coherence across context truncations
- **Timeline persistence** — recording events with timestamps

### 7.2 Integration Design

**Principle: TCS becomes the implementation of ION's capsule system (Track E).**

**Session Start Protocol:**
```
1. TCS.load_context(agent="opus", session_id=current)    ← TCS
   → Returns: previous session state, recent timeline, active branches
2. ION manifest.read()                                    ← ION
   → Returns: current manifest state
3. Merge TCS context into ION manifest:
   → Update manifest.active_branches from TCS
   → Update manifest.evidence_links from TCS
   → Write PRE capsule ion to capsules/
4. Navigator.contextualize() with merged state             ← ION
```

**Session End Protocol:**
```
1. Navigator.deliver() — final cognitive loop step         ← ION
2. Capture session state:
   → Active branches and their states
   → Evidence created/modified this session
   → Decisions made and their rationale
   → Open questions and uncertainties
3. TCS.dump_context(session_state, adaptive=True)          ← TCS
   → Adaptively selects most important context to preserve
   → Compresses historical context
   → Writes to TCS storage
4. ION governed_write.create(post_capsule_ion)             ← ION
   → Writes POST capsule to capsules/ directory
```

**Capsule Ion Structure (A2 Schema 1):**
```yaml
ion_id: capsules/session-2026-03-23-post
type: memory
authority: A4_RUNTIME
confidence: 0.95
schema: capsule/v1
session_id: "2026-03-23-001"
capsule_type: POST
timestamp: "2026-03-23T17:00:00"
active_branches:
  - branches/active/system-mapping
evidence_created:
  - evidence/system-registry-audit
decisions:
  - decision: "IONv2 marked as total failure"
    rationale: "Wrong paradigm, lower fidelity reimplementation"
open_questions:
  - "Which integration option: build on victus or fresh build?"
confidence_summary:
  system_health: 0.42
  highest_confidence_ion: "evidence/codebase-audit"
  lowest_confidence_ion: "branches/future/ionv3"
```

### 7.3 What Must Be Built

| Component | Lines (est) | Priority |
|-----------|-------------|----------|
| `TCSAdapter` — wraps TCS for ION | ~250 | CRITICAL |
| Capsule writer — structured PRE/POST capsule creation | ~200 | CRITICAL |
| Session boundary detector — trigger capsule writes | ~100 | HIGH |
| Context merge — combine TCS state with ION manifest | ~200 | HIGH |
| Adaptive pruning — TCS-informed context window management | ~150 | MEDIUM |

---

## §8. Cross-System Integration Patterns

### 8.1 The Governed Write as Integration Backbone

Every integration routes through the governed write pipeline. Here's where each system hooks in:

| Stage | Name | Integrating System | What It Does |
|-------|------|-------------------|-------------|
| W1 | INTAKE | TCS | Enrich intake with session context |
| W2 | PARSE | — | Pure ION (parser.py) |
| W3 | CLASSIFY | SEG | Classify evidence category |
| W4 | EVIDENCE | VIF | Verify evidence claims |
| W5 | AUTHORITY | APOE | Validate role ↔ authority mapping |
| W6 | ZONE | — | Pure ION (directory assignment) |
| W7 | CONTRADICT | SEG | Contradiction detection |
| W8 | VERIFY | VIF + SCOR | κ-gate + invariant checks |
| W9 | PROVENANCE | VIF | Emit witness envelope |
| W10 | PROPAGATE | CMC + HHNI | Temporal index + retrieval update |

### 8.2 The Cognitive Loop with All Systems

```
§7.1 CONTEXTUALIZE:
  ION manifest.read()
  + TCS.load_context(session)
  + HHNI.retrieve(query, budget)
  + CMC.temporal_context(recent_changes)
  → Merged context

§7.2 REFLECT:
  ION graph.traverse(evidence/)
  + VIF.confidence_assess(all_ions)
  + SEG.synthesis(related_evidence)
  → Gap analysis, confidence map

§7.3 PLAN:
  ION branch analysis
  + APOE.plan(task, agents, constraints) [if complex]
  → Execution plan as branch ions

§7.4 GATE:
  ION threshold.evaluate(planned_actions)
  + VIF.κ_gate(proposed_writes)
  + SDF-CVF.blast_radius(affected_ions) [safety check]
  → PASS / FAIL / ESCALATE

§7.5 EXECUTE:
  ION governed_write(action_results)
  → All 10 stages, hooks at each stage (§8.1)

§7.6 AUDIT:
  ION invariant_check()
  + SCOR.sanity_check()
  + VIF.witness_emit()
  → Audit receipt (A2 Schema 9)

§7.7 DELIVER:
  ION manifest.update()
  + TCS.dump_context(session_state)
  + CMC.snapshot(current_state)
  → Results to human or calling agent
```

### 8.3 Data Flow Summary

```
                    Human / Agent Query
                           │
                    ┌──────▼──────┐
                    │ AETHER      │ ??? 
                    │ ENGINE      │ J.03
                    │ (Cognitive  │
                    │  Loop)      │
                    └──┬───┬───┬──┘
                       │   │   │
              ┌────────┤   │   ├────────┐
              │        │   │   │        │
         READ │   PLAN │   │   │ WRITE  │ PERSIST
              │        │   │   │        │
        ┌─────▼──┐ ┌───▼───▼┐ │ ┌──────▼──────┐
        │ HHNI   │ │ APOE   │ │ │ Governed    │
        │ budget │ │ ACL    │ │ │ Write (10)  │
        │ search │ │ plan   │ │ │ VIF+SEG+CMC │
        └───┬────┘ └────────┘ │ └──────┬──────┘
            │                 │        │
        ┌───▼─────────────────▼────────▼──┐
        │        ION FILESYSTEM            │
        │  .ion/manifest.md                │
        │  .ion/evidence/                  │
        │  .ion/branches/                  │
        │  .ion/memory/                    │
        │  .ion/specs/                     │
        │  .ion/capsules/                  │
        │  .ion/timeline/                  │
        └─────────────────────────────────┘
```

---

## §9. Integration Priority Matrix

### Phase 1: Minimal Viable Integration (4-6 sessions)
| Integration | Why First | Depends On |
|-------------|-----------|------------|
| LLM Adapter (J.01) + LLM Client | Can't think without LLM | ION Engine (done) |
| Context Compiler (J.02) + HHNI adapter | Can't contextualize without retrieval | J.01 |
| TCS adapter + Capsule writer | Can't maintain continuity | ION Engine (done) |

### Phase 2: Governed Intelligence (4-6 sessions)
| Integration | Why Second | Depends On |
|-------------|-----------|------------|
| VIF κ-gate at W8 | Confidence calibration | Phase 1 |
| SEG contradiction detection at W7 | Evidence integrity | Phase 1 |
| CMC temporal indexing at W10 | Query history | Phase 1 |

### Phase 3: Autonomous Operation (6-8 sessions)
| Integration | Why Third | Depends On |
|-------------|-----------|------------|
| APOE execution planning | Complex task decomposition | Phases 1-2 |
| SDF-CVF blast radius at W8 | Mutation safety | Phases 1-2 |
| Full cognitive loop with all hooks | Steady-state operation | All above |

---

## §10. Open Questions

> Per AETHER_CONSTITUTION Article 13 (Epistemic Law): these are PENDING claims that require evidence to resolve.

1. **CMC atom granularity:** Should every ion update create a CMC atom, or only governed writes? Full atomicity = complete history but massive storage. Governed-only = gaps but manageable.

2. **HHNI index persistence:** Should HHNI's index persist alongside the ION filesystem, or rebuild on startup like ION's current index? Persistence = faster startup. Rebuild = guaranteed consistency.

3. **VIF calibration frequency:** How often should VIF recalibrate confidence scores? Per-session? Per-hour? On-demand? Too frequent = noise. Too infrequent = drift.

4. **APOE plan granularity:** At what complexity threshold does the navigator invoke APOE? Single ion writes should not need APOE overhead. Where's the line?

5. **TCS compression vs ION capsules:** TCS has advanced compression. ION capsules are raw markdown. Should capsules use TCS compression or stay human-readable?

6. **SEG ↔ ION graph.py overlap:** Both build evidence graphs. Should SEG replace ION's graph.py for evidence operations, or should they coexist?

---

## §11. Self-Audit Gate

| Criterion | Status | Evidence |
|-----------|--------|----------|
| All 6 core systems covered | ✅ | §2-§7 |
| Integration surface defined per system | ✅ | Data flow, protocol mapping, what must be built |
| Lines-of-code estimates provided | ✅ | Per-component estimates |
| A2 protocol schemas referenced | ✅ | Schemas 1, 7, 8, 9, 11, 17 |
| Governed write hooks mapped | ✅ | §8.1 — all 10 stages |
| Cognitive loop integration shown | ✅ | §8.2 — all 7 steps |
| Priority matrix provided | ✅ | §9 — 3 phases |
| Open questions documented | ✅ | §10 — 6 questions |
| C1/C2/C3 model applied | ✅ | §1 integration roles |
| Epistemic status of integration designs marked | ✅ | Frontmatter: DERIVED/SPECULATIVE |

---

*This specification maps how 150,284 lines of core infrastructure converge with the ION engine. The integration designs are hypothetical until validated by implementation, but the data flows are grounded in observed system capabilities.*

*Governed by: AETHER_CONSTITUTION.md*
*— Opus, 2026-03-23*
