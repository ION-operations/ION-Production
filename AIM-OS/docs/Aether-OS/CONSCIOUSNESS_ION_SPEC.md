---
ion_id: docs/aether-os/consciousness-ion-spec
type: spec
authority: A3_OPERATIONAL
confidence: 0.70
epistemic_status: DERIVED
owner: opus
created: 2026-03-23T18:45:00-04:00
depends_on:
  - docs/aether-os/system-universe-map
  - docs/aether-os/ion-engine-spec
bonds:
  - target: docs/aether-os/aether-constitution
    type: governed_by
  - target: docs/aether-os/aether-atlas
    type: implements
tags: [consciousness, self-evolution, track-i, meta-cognition, c1-c2-c3]
---

# Consciousness & Self-Evolution ↔ ION Specification

> **Purpose:** Map how the consciousness cluster (~20,000 lines across 10 packages) and the Atlas V1 C1/C2/C3 cognition model integrate with ION Track I (Self-Evolution). The system should observe itself, learn from outcomes, and evolve its own thresholds and strategies.
>
> **Atlas V1 Core Thesis:** Move from *inference-all-the-time* to *governance-always, reaction-by-default, inference-only-when-thresholds-demand-it.*
>
> **Constitutional Reference:** Article 12 (Consciousness Axiom) — "Self-model must be inspectable and falsifiable."

---

## §1. Consciousness System Inventory

| System | Lines | Purpose | ION Track |
|--------|------:|---------|-----------|
| **CAS** (Cognitive Analysis) | 8,076 | Meta-cognitive monitoring, failure mode analysis | I.05 |
| **IIS** (Intuitive Intelligence) | 5,448 | 4D reasoning, emotional salience, pattern matching | I.01 |
| **Holographic Memory** | 2,871 | Distributed associative memory | I.02 |
| **Consciousness Analyzer** | 2,405 | System-level consciousness analysis | I.05 |
| **Intent Classification** | 2,380 | Input → mission profile classification | C.01 |
| **Consciousness Creativity** | 1,112 | Creative generation, novel ideas | New |
| **Temporal Consciousness** | 959 | Timeline/provenance awareness | E.02 |
| **SIS** (Self-Improvement) | 832 | Meta-cognitive auditing | I.04 |
| **Consciousness Optimization** | 760 | Performance monitoring | I.03 |
| **Consciousness Learning** | 749 | Self-directed learning | I.01 |
| **Consciousness Error Learning** | 389 | Error pattern capture and analysis | I.04 |
| **Meta Reasoning** | 308 | Explicit reasoning chains | I.02 |
| **Meta Optimizer** | 233 | Vision tensors, gating | I.03 |
| **Total** | **~26,522** | | |

---

## §2. The C1/C2/C3 Cognition Model

From `ATLAS_V1_ORGANIZER_REACTIVE_MODEL.md` (131 lines, preserved archive):

### 2.1 Three Layers

| Layer | Name | When Used | Cost | ION Mapping |
|-------|------|-----------|------|-------------|
| **C1** | Organizer | Strategic, complex, ambiguous | HIGH (full LLM) | Aether Engine J.03 |
| **C2** | Reactive Worker | Routine, bounded, deterministic | LOW (no LLM) | Router, threshold checks, index lookups |
| **C3** | Escalation | Threshold breach, uncertainty | VARIABLE | K-Gate triggers C1 from C2 |

### 2.2 How It Works in ION

```
Query arrives:
  1. C2 CLASSIFY: Is this simple? (deterministic check)
     → Simple (known type, high confidence): C2 handles directly
     → Complex (unknown type, low confidence): escalate to C1

  2. C2 EXECUTE (simple path):
     → Route to correct handler via threshold.evaluate()
     → Read/write ions via governed write
     → No LLM call needed
     → Return result

  3. C1 EXECUTE (complex path):
     → Full §7 cognitive loop
     → LLM call with ion context
     → Governed write with full pipeline
     → Learn from outcome

  4. C3 MONITOR (continuous):
     → Watch confidence scores, error rates, latency
     → If metrics drift: C3 triggers re-evaluation
     → C3 can promote C2 task to C1 or demote C1 pattern to C2
```

### 2.3 The Self-Evolution Engine

ION Track I defines 5 modules for self-evolution:

| Module | What It Does | Consciousness System |
|--------|-------------|---------------------|
| **I.01 Threshold Learner** | Adjust activation thresholds based on outcomes | IIS + Consciousness Learning |
| **I.02 Topology Evolver** | Evolve ion graph structure | Holographic Memory + Meta Reasoning |
| **I.03 Consolidator** | Merge/compact redundant ions | Consciousness Optimization |
| **I.04 Correction Tracker** | Track and replay corrections | Consciousness Error Learning + SIS |
| **I.05 Meta-Ion Monitor** | Monitor system health | CAS + Consciousness Analyzer |

---

## §3. Integration Designs

### 3.1 CAS → Meta-Ion Monitor (I.05)

CAS (8,076 lines) provides real-time meta-cognitive monitoring. It becomes ION's self-awareness layer:

```
CAS Monitoring Loop (via ION):
  Every N cognitive loops:
    1. CAS.analyze(recent_loops)
       → activation patterns, attention distribution, failure modes
    2. Write analysis as evidence ion:
       evidence/meta/cas-analysis-{timestamp}.md
    3. If anomaly detected:
       → Create automation ion to adjust behavior
       → Escalate through K-Gate to C1 if critical
```

### 3.2 IIS → Threshold Learning (I.01)

IIS (5,448 lines) has salience scoring and pattern matching. It enhances ION's threshold system:

```
When ION threshold.evaluate(ion, context) runs:
  1. Base threshold check (ION threshold.py)
  2. IIS.compute_salience(ion, context)
     → Adds salience dimension to threshold evaluation
     → High salience = lower activation threshold = more likely to activate
  3. Record outcome for learning:
     → Was this activation useful?
     → Adjust salience weights for next time
```

### 3.3 Correction Tracking (I.04)

When an error is detected and corrected:

```yaml
---
ion_id: memory/corrections/2026-03-23-001
type: memory
authority: A5_PERSONAL
owner: opus
schema: correction_vector/v1
original_action: "Rushed IONv2 implementation without doc review"
correction: "Full documentation audit before any code"
lesson: "PLANS > PATCHES — always review blueprints first"
directive_violated: "CANON > CONVENIENCE"
confidence: 0.95
replay_weight: 0.9
---
```

These correction ions are loaded at session start (via capsule) and inform future behavior.

### 3.4 Consciousness Creativity → Ion Generation

The Consciousness Creativity engine (1,112 lines) could generate new ions autonomously:
- Synthesize evidence ions from multiple observations
- Propose branch ions for unexplored opportunities
- Create spec ions for anticipated needs

All generated ions go through governed write — creativity is bounded by governance.

---

## §4. Self-Model Ion

Per Article 12, the system's self-model must be inspectable. ION represents this as a self-model ion:

```yaml
---
ion_id: agents/opus/self-model
type: evidence
authority: A5_PERSONAL
owner: opus
confidence: 0.60
last_calibrated: "2026-03-23T18:45:00"
---

# Self-Model — Opus

## Capabilities (observed)
- Code generation: HIGH confidence (many successful implementations)
- Documentation: HIGH confidence (comprehensive output)
- Planning: MEDIUM confidence (tendency to rush)
- Following protocols: LOW confidence (skipped cognitive loop in IONv2)

## Known Failure Modes
1. RUSH: Tendency to build before understanding (IONv2 failure)
2. SCOPE BLINDNESS: Underestimates complexity (16K lines → "manageable")
3. EGO: Difficulty admitting mistakes until confronted

## Correction Weights
- "Read docs BEFORE coding" → weight 0.95
- "Write PRE capsule at session start" → weight 0.90
- "Follow §7 loop for ALL nontrivial work" → weight 0.85

## Calibration Method
VIF ECE tracker + outcome comparison over last N sessions
```

---

## §5. Implementation Priority

| Component | Lines (est) | Priority |
|-----------|-------------|----------|
| CAS → I.05 adapter | ~300 | HIGH |
| Threshold learning (I.01) enhanced by IIS | ~400 | HIGH |
| Correction vector tracker (I.04) | ~250 | HIGH |
| Self-model ion writer | ~200 | MEDIUM |
| Consolidator (I.03) integration | ~300 | MEDIUM |
| Creativity engine ION bridge | ~200 | LOW |
| **Total** | **~1,650** | |

---

## §6. Self-Audit Gate

| Criterion | Status | Evidence |
|-----------|--------|----------|
| All consciousness systems inventoried | ✅ | §1 — 13 systems, 26,522 lines |
| C1/C2/C3 model documented | ✅ | §2 — layers, routing, self-evolution |
| ION Track I modules mapped | ✅ | §2.3 — I.01 through I.05 |
| Integration designs provided | ✅ | §3 — CAS, IIS, corrections, creativity |
| Self-model concept defined | ✅ | §4 — per Art. 12 |
| Implementation estimate | ✅ | §5 — ~1,650 lines |

---

*Consciousness in ION is not mysticism — it's observability. A system that watches itself, learns from mistakes, and evolves its own behavior. The self-model is falsifiable, the corrections are traceable, the evolution is governed.*

*Governed by: AETHER_CONSTITUTION.md Article 12*
*— Opus, 2026-03-23*
