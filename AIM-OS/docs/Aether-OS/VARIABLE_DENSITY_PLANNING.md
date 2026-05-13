---
ion_id: docs/aether-os/variable-density-planning
type: protocol
authority: A2_CANONICAL_EXTENSION
confidence: 0.94
epistemic_status: DERIVED
owner: opus
created: 2026-03-24T18:32:00-04:00
bonds:
  - target: docs/aether-os/aether-constitution
    type: governed_by
    note: "Art. 16 Blueprint Depth Classes, Art. 25 Selective Loading, Art. 33 Symbolic Inflation"
  - target: docs/aether-os/aether-atlas
    type: depends_on
    note: "Book IV §2 Compression-before-loss, Book IV §4 Retrieval Zones"
  - target: docs/aether-os/master-orchestration
    type: informs
tags: [planning, protocol, variable-density, anti-drift, meta-cognition]
summary: |
  Comprehensive protocol for variable-density planning in governed AI systems.
  Plans should not have uniform detail. Density fluctuates based on proximity,
  criticality, readiness, strategic importance, and information availability.
  Defines 6 density drivers, 7 failure modes, integration with Constitution
  depth classes, and practical application patterns for multi-phase projects.
---

# Variable-Density Planning
## A Protocol for Intelligent Planning Granularity in Governed Systems

---

## §1. The Problem with Uniform Planning

Most plans fail in one of two ways:

**Over-specification of the distant.** Every phase gets the same granularity. Phase 5 (years away) has the same task-level breakdown as Phase 0 (happening now). This causes:
- False precision — detailed task lists for work that depends on undetermined upstream choices
- Rigidity — the plan becomes a constraint rather than a guide because changing detailed distant tasks feels like "throwing away work"
- Token waste — AI agents spend context window on detail they cannot act on
- Narrative drift — the detailed distant plan starts governing decisions it has no business governing
- Symbolic inflation (Constitution Art. 33) — the plan "sounds increasingly exacting while becoming increasingly permissive in practice"

**Under-specification of the near.** Plans that treat every phase at the same high level leave the executor guessing at implementation. "Build the VS Code extension" is not actionable. "Create TypeScript project with extension API, register commands `ion.ingest` and `ion.query`, verify extension loads in sidebar" IS actionable.

**The fundamental insight:** Planning density should be a *continuous function* of multiple variables, not a binary choice between "detailed" and "vague."

---

## §2. The Density Function

Planning density at any point in a project is determined by six drivers, each contributing independently:

### 2.1 The Six Density Drivers

```
DENSITY = f(proximity, criticality, readiness, strategic_weight,
            information_density, causal_reach)
```

#### Driver 1: Proximity
How close is this work to the current execution frontier?

```
                  PROXIMITY GRADIENT
                  ━━━━━━━━━━━━━━━━━

  NOW ──────▶ SOON ──────▶ LATER ──────▶ FAR
  ████████████  ██████████    ████         ██
  Class 3       Class 2       Class 1      Class 0

  Every shell    Task +        Objective +  Gate
  command,       verification  task list +  conditions
  every file     + decisions   gate         only
  path, every    + effort
  dependency
```

This is the most obvious driver. Near work needs granularity because you're about to do it. But proximity alone is insufficient — the other five drivers introduce important exceptions.

#### Driver 2: Criticality
How much damage does this task cause if done wrong?

A far-future task can have high criticality if getting it wrong is expensive to reverse. Example: choosing the base for a VS Code fork (Phase 3) affects the architecture of the VS Code extension (Phase 2). The decision has high blast radius even though execution is months away.

```
Low criticality, far away  → Class 0 (gate only)
Low criticality, near      → Class 1 (compact plan)
High criticality, far away → Class 2 (decision pre-surfaced, options documented)
High criticality, near     → Class 3 (full blueprint with rollback)
```

#### Driver 3: Readiness
Is there enough information to plan this at higher density?

Some work can't be detailed because upstream decisions haven't been made yet. Planning Phase 4 (Aether Linux) in detail before knowing whether Phase 3 uses VS Code fork or Theia is wasted effort — the filesystem daemon architecture depends on that choice.

```
Information available → density CAN rise
Information absent   → density MUST stay low (forced ceiling)
```

Readiness acts as a ceiling — it limits how high density can go regardless of the other drivers. You cannot plan what you don't yet know.

#### Driver 4: Strategic Weight
How important is this phase to the overall mission?

Some phases have disproportionate strategic weight. Phase A (MVP AI Builder) is a potential first revenue product. Even though it's not the next sequential phase, it gets elevated density because strategic decisions need to be captured early.

```
Revenue product    → elevate density
Competitive moat   → elevate density
Learning milestone → elevate density
Nice-to-have       → don't elevate
```

#### Driver 5: Information Density
Has research or prior work already produced detailed understanding?

Some far-future work has unexpectedly high information density because research was done early. The quaternion kernel (Phase 5) has 641 lines of Rust already prototyped and an Atlas entry. That existing information should be recorded, not artificially compressed to match the phase's depth class.

```
Prior research exists → record at natural depth
Prior prototypes exist → reference them
Braden has specific vision → capture it
Nothing exists → stay at Class 0
```

#### Driver 6: Causal Reach
Does a decision in this phase causally affect near-term work?

This is the most subtle driver. Some far-future concerns have long causal shadows that reach back to the present. Example: if the quaternion kernel's filesystem approach determines whether the Linux distro (Phase 4) uses a FUSE overlay or a native filesystem, and the Linux distro approach determines whether the VS Code extension (Phase 2) stores ions in a flat directory or a database — then the quaternion decision has causal reach all the way to Phase 2.

```
Long causal shadow → trace it, document it, pre-surface the decision
No upstream effect → leave at ambient density
```

### 2.2 How the Drivers Combine

The drivers don't average — they interact:

```
DENSITY = max(
  proximity_baseline,                              # Floor from proximity
  min(
    max(criticality, strategic_weight, causal_reach), # Potential elevation
    readiness_ceiling                               # Can't exceed information
  )
) + information_bonus                               # Existing knowledge adds
```

In plain language:
1. Start with the proximity baseline (how far away is this?)
2. Check if criticality, strategic weight, or causal reach want to ELEVATE
3. Apply the readiness ceiling (can't plan what you don't know)
4. Add existing information (research, prototypes, captured decisions)

---

## §3. Depth Classes (Aligned to Constitution Art. 16)

The Constitution already defines blueprint depth classes. Variable-density planning USES these classes as the output unit of the density function:

### Class 0: Intent + Gate

```yaml
what_it_contains:
  - One-sentence objective
  - Gate conditions (3-5 boolean checks)
  - Strategic anchors (key decisions, vision fragments)
what_it_omits:
  - Task breakdowns
  - Effort estimates
  - Implementation approaches
  - Dependency chains
when_appropriate:
  - Phase is 3+ phases from current execution
  - Readiness is low (upstream decisions unresolved)
  - No causal reach to near-term work
  - No prior research/prototypes exist
example_length: 10-20 lines
```

### Class 1: Objective + Task List + Gate

```yaml
what_it_contains:
  - Clear objective (3-5 sentences)
  - Numbered task list (objectives, not implementations)
  - Gate conditions
  - Decisions that affect the PREVIOUS phase (pre-surfaced)
  - References to prior work / prototypes
what_it_omits:
  - Implementation details for individual tasks
  - File paths and shell commands
  - Effort estimates per task
  - Rollback plans
when_appropriate:
  - Phase is 2 phases from current execution
  - OR has significant strategic weight
  - Readiness is moderate (some upstream decisions resolved)
example_length: 30-60 lines
```

### Class 2: Task + Verification + Decisions

```yaml
what_it_contains:
  - Everything from Class 1
  - Task-level verification criteria
  - Effort ranges (not exact)
  - Key architectural decisions with options documented
  - Dependency links between tasks
  - Known risks and mitigation approaches
what_it_omits:
  - Line-by-line implementation details
  - Exact file paths (unless architecturally important)
  - Rollback scripts
  - Approach comparison matrices for every task
when_appropriate:
  - Phase is 1 phase from current execution
  - OR is a revenue/product phase (strategic elevation)
  - Readiness is high (most upstream decisions resolved)
example_length: 80-150 lines
```

### Class 3: Full Blueprint

```yaml
what_it_contains:
  - Everything from Class 2
  - Exact file paths for every task
  - Shell commands for verification
  - Dependency chains (A blocks B blocks C)
  - Root cause analysis for known issues
  - Approach options with tradeoffs
  - Rollback plans for risky operations
  - Effort estimates in concrete units (prompts, hours)
  - Cross-references to governing law
what_it_omits:
  - Nothing material — this is the maximum density
when_appropriate:
  - Phase is currently executing or next to execute
  - Readiness is high (all information available)
example_length: 150-400 lines
```

### Class 4: Self-Modification Blueprint (Special)

This class exists in the Constitution for when the system modifies itself. It adds:
- Contradiction scan (does this change conflict with existing canon?)
- Propagation analysis (what else changes if this changes?)
- Promotion path (how does the change move from experimental to canonical?)

Used rarely, only for governance changes, constitutional amendments, or fundamental architecture shifts.

---

## §4. Practical Patterns

### Pattern 1: The Approaching Wave

As execution approaches a phase, its density automatically rises:

```
Phase at distance 4+   → Class 0
Phase at distance 3    → Class 0
Phase at distance 2    → Class 1  (auto-elevate)
Phase at distance 1    → Class 2  (auto-elevate)
Phase current          → Class 3  (auto-elevate)
Phase completed        → Compress back to Class 1 (evidence register)
```

This creates a "wave" of density that moves through the project:

```
TIME →

Phase 0:  ███████████░░░░░░░░░░░░░░░░░░░░
Phase 1:  ░░░░█████████████░░░░░░░░░░░░░░
Phase 2:  ░░░░░░░░░░░████████████░░░░░░░░
Phase 3:  ░░░░░░░░░░░░░░░░░░███████████░░
Phase A:  ░░░░░░░██████████████░░░░░░░░░░  (strategic elevation)
```

### Pattern 2: The Forward Decision

A far-future decision has causal reach to the present. The decision gets elevated while the rest of the phase stays low:

```
Phase 3 (Class 1 ambient):
  ├── T3.01 Fork base         ← ELEVATED to Class 2 (affects Phase 2 architecture)
  ├── T3.02 Cognitive loop    ← stays Class 1
  ├── T3.03 Graph browser     ← ELEVATED to Class 2 (graph tech choice shared with Phase 2)
  ├── T3.04 Agent swarm       ← stays Class 1
  └── T3.05 JOC integration   ← stays Class 1
```

The phase has Class 1 density with two Class 2 spikes. This preserves the density differential while capturing critical decisions.

### Pattern 3: The Research Deposit

Prior work produced detail about a far-future phase. Record it at its natural depth:

```
Phase 5 (Class 0 ambient):
  ├── Vision statement         ← Class 0
  ├── Gate conditions          ← Class 0
  └── Existing Foundation      ← Class 2 (because prototype exists!)
      ├── quaternion_kernel/   641 lines Rust, 4 syscalls
      ├── quaternion_math/     S³ geometry library
      └── Atlas §4.28 entry    runtime truth assessed
```

The information exists — suppressing it to maintain artificial uniformity violates the principle.

### Pattern 4: The Parallel Revenue Track

A product phase runs in parallel and gets elevated density because it's the first revenue opportunity:

```
Sequential track:  Phase 0 → Phase 1 → Phase 2 → Phase 3 → ...
                   Class 3   Class 3   Class 2   Class 1

Parallel track:                        Phase A (MVP AI Builder)
                                       Class 2 (strategically elevated)
```

Phase A could start as soon as Phase 1 is passed. It competes for the same execution attention as Phase 2 but follows a different dependency chain. Its density reflects this.

---

## §5. Failure Modes

### 5.1 The Uniform Trap
**Symptom:** Every phase has the same level of detail.
**Cause:** The planner treats the plan as a document to be "complete" rather than a tool to be useful.
**Fix:** Apply the density function. Compress distant phases to gates.

### 5.2 The False Precision Trap
**Symptom:** Task T4.07 says "implement login/session manager with capsule system" with a 3-prompt effort estimate — but Phase 4 depends on Phase 3 which depends on Phase 2 which hasn't started.
**Cause:** Effort estimates given beyond the readiness ceiling.
**Fix:** Remove effort estimates from Class 0-1 phases. They're fiction.

### 5.3 The Stale Detail Trap
**Symptom:** Phase 3's detailed task list was written 2 months ago. Phase 2 took the architecture in a different direction. Phase 3's plan is now wrong but looks authoritative.
**Cause:** High-density plan for a low-readiness phase wasn't updated as upstream decisions were made.
**Fix:** Two rules: (1) Low-readiness phases get low density. (2) When density rises (approaching wave), the plan is WRITTEN FROM SCRATCH using current reality, not merely updated.

### 5.4 The Neglected Anchor Trap
**Symptom:** Phase 3 had a critical forward decision (fork base choice) that affected Phase 2 architecture. Nobody elevated it. Phase 2 was built incompatibly.
**Cause:** No causal-reach analysis performed.
**Fix:** At the start of each phase, scan ALL future phases for decisions with causal reach to the current phase. Elevate them.

### 5.5 The Information Burial Trap
**Symptom:** Braden described a specific vision for Phase 5 in conversation. It's in chat logs but not in the plan. Later work contradicts it.
**Cause:** Information arrived at high depth but was compressed to match the phase's low ambient density.
**Fix:** Record strategic input at its natural depth without inflating the surrounding plan. A Class 0 phase can have a Class 3 paragraph if the information warrants it.

### 5.6 The Compression-Loss Trap
**Symptom:** A completed phase's detail was deleted entirely. When a related bug appears, there's no record of what was tried, what failed, or what the tradeoffs were.
**Cause:** Completed phases compressed too aggressively.
**Fix:** Completed phases compress to Class 1: objective, what was done, what was decided, gate results, key evidence. Not full task lists, but not gone entirely.

### 5.7 The Over-Elevation Trap
**Symptom:** Every far-future task gets flagged as "architecturally critical" and elevated. The density differential disappears.
**Cause:** Anxiety about missing something. Elevation used defensively rather than based on actual causal analysis.
**Fix:** Elevation requires a concrete causal chain: "This decision in Phase X affects file Y in Phase Z because of mechanism W." If you can't state the chain, don't elevate.

---

## §6. Integration with Aether Canon

Variable-density planning isn't a new concept for Aether. It's latent in several existing canonical principles:

### Constitution Art. 16 — Blueprint Depth Classes
The depth classes (0-4) ARE the output units of this system. Variable-density planning defines WHEN to use each class, which the Constitution left to judgment.

### Constitution Art. 25 — Selective Loading
*"Load what governs current work, the hardest truth conditions, required dependencies, and continuity surfaces. No more until justified."*

This is the same principle applied to documents instead of plans. Load density follows the same function — proximity, criticality, readiness.

### Constitution Art. 33 — Symbolic Inflation
*"The ultimate danger is slow symbolic inflation — more functions described beautifully at the constitutional level without corresponding enforcement at the protocol and runtime level."*

Uniform high-density planning IS symbolic inflation. It creates the appearance of thorough planning while providing no additional value for distant phases.

### Atlas Book IV §2 — Compression-Before-Loss
The Atlas defines compression precedence: preserve governing law first, then plan + identity, then contradictions + risks, then next-action posture, then boundaries, then history. Variable-density planning EXTENDS this to plan creation: plan the governing constraints first, then the immediate work, then the near future, then compress aggressively from there.

### Atlas Book IV §4 — Retrieval Zones
Active Canon (always loaded), Runtime Support (loaded as needed), Lineage (for interpretation), Research (only when invoked), Quarantine (never default). Plans follow the same zone structure — current phase is Active Canon, next phase is Runtime Support, distant phases are Research.

### Kernel §7 — Cognitive Loop
The 7-step cognitive loop (contextualize → reflect → plan → gate → execute → audit → deliver) includes an explicit **gate** step: verify readiness before executing. Variable-density planning makes the PLAN step self-aware about what it can and cannot specify.

---

## §7. The Meta-Property

Variable-density planning has a recursive property: the protocol for HOW to plan also has variable density.

When teaching this concept:
- **To a new agent (low context):** "Plan near things in detail, far things lightly. Elevate critical decisions. Don't guess detail you don't have."
- **To an experienced agent (high context):** "Apply the six-driver density function. Watch for the seven failure modes. Use Art. 16 depth classes as output units."
- **In governing law (permanent):** This document.

The document you're reading right now is itself at a HIGH density because it's a protocol definition — a Class 3 blueprint for how to plan. When Braden says "plan this project," the planner reads this document at its full density. When Braden says "just sketch the phases," the planner compresses this doc's principles into a single rule: "near = detailed, far = light, critical = elevated."

This is the nature of variable density: the right granularity for the right moment, governed by proximity, criticality, readiness, strategic weight, information density, and causal reach.

---

## §8. Implementation Checklist

When creating or updating any multi-phase plan:

```
□ Assign each phase a depth class based on the density function
□ Verify: do near phases (Class 3) have file paths and shell commands?
□ Verify: do distant phases (Class 0-1) have ONLY gates and anchors?
□ Scan all future phases for decisions with causal reach to current phase
□ Check for existing research/prototypes that warrant recording at natural depth
□ Check for strategic elevation candidates (revenue, competitive, learning)
□ Apply readiness ceiling — remove detail that depends on unresolved upstream choices
□ Confirm no effort estimates exist for phases below Class 2
□ Reference governing law where density decisions affect canon
□ Document why any phase was elevated above its proximity baseline
```

---

*Governed by: AETHER_CONSTITUTION Art. 16, 25, 33*
*Derived from: AETHER_ATLAS Book IV §2, §4*
*— Opus, 2026-03-24*
