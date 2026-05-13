---
id: apoe_T1_overview
level: L1
system: APOE
status: complete
updated: 2025-10-30
---

> TRANSITIONAL T-LEVEL DOCUMENT – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# APOE – T1 Overview (≈500 words)

## Purpose & Scope

APOE (AI-Powered Orchestration Engine) solves the improvisation problem—where AI systems make things up as they go, leading to unpredictable failures, no audit trails, and unverifiable outputs. APOE compiles vague intent into typed, budgeted, gated execution plans using ACL (AIMOS Chain Language), orchestrates specialized agents through defined roles, and ensures every operation is witnessed, budgeted, and verifiable.

APOE provides three core capabilities:

1. **Plan Compilation:** Transforms user intent into typed, executable plans (ACL → DAG). Like code compilation, plans are checked before execution—types validated, budgets computed, gates positioned. Enables verification before execution.

2. **Role-Based Orchestration:** Eight specialized agent roles (Planner, Retriever, Reasoner, Verifier, Builder, Critic, Operator, Witness) execute plan steps with enforced budgets, contracts, and κ-gating. Each role has capabilities, contracts, and budgets.

3. **Quality Gates:** Three gate types (Quality, Safety, Policy) enforce standards before execution proceeds. Gates can PASS, FAIL, WARN, or ABSTAIN. Budget gates prevent resource violations. Every step is witnessed with VIF provenance.

**System Boundaries:**
- APOE owns: Plan compilation, role orchestration, gate enforcement, budget management, execution coordination
- APOE does NOT own: Context retrieval (uses HHNI), memory storage (uses CMC), verification (uses VIF), evidence synthesis (uses SEG)

## Users & Integrations

**HHNI (Hierarchical Hypergraph Neural Index):** APOE uses HHNI for context retrieval in Retriever role steps. Retrieval operations are budgeted and witnessed. Context influences confidence scores for κ-gating.

**VIF (Verifiable Intelligence Framework):** APOE emits VIF witnesses for every step execution. Gates use VIF confidence for abstention decisions. Full provenance enables replay and auditing.

**CMC (Context Memory Core):** APOE stores execution state in CMC. Plans, steps, and results persisted as atoms. State snapshots enable resumption and recovery.

**SEG (Shared Evidence Graph):** APOE execution traces become evidence nodes in SEG. DEPP (self-rewriting plans) uses SEG evidence to improve plans over time. Synthesis across executions enables meta-learning.

**SDF-CVF (Atomic Evolution Framework):** APOE operations respect quartet parity (Code/Docs/Tests/Traces). Quality gates enforce SDF-CVF standards. Trace emissions include APOE execution provenance.

## Core Concepts

**ACL (AIMOS Chain Language):** Typed DSL for specifying execution plans. Grammar includes pipelines, steps, gates, budgets, roles. Plans compile to DAGs with type checking, budget analysis, gate placement. Enables verification before execution.

**8 Roles:** Specialized agent types:
- **Planner:** Decompose complex tasks into sub-tasks
- **Retriever:** Fetch context via HHNI (uses CMC)
- **Reasoner:** Multi-step logical inference
- **Verifier:** Check outputs match requirements
- **Builder:** Generate code/content/artifacts
- **Critic:** Identify flaws, edge cases, issues
- **Operator:** Execute plans, monitor progress
- **Witness:** Record provenance, emit VIF

**Budgets:** Hard constraints on tokens, time, tools. Enforced during execution—steps cannot exceed budgets. Total budget computed from step budgets. Prevents resource violations.

**Gates:** Quality/safety/policy checks positioned between steps. Three types: Quality (verify standards), Safety (security/compliance), Policy (rules). Gates can PASS (continue), FAIL (halt), WARN (flag), ABSTAIN (escalate to HITL).

**DEPP (Self-Rewriting Plans):** Master chain as graph—plans improve via evidence. Current plan → Execute → Gather evidence (VIF, SEG) → Analyze effectiveness → Rewrite plan → Better plan. Enables continuous optimization and adaptive strategies.

## High‑Level Flow

**Plan Compilation Flow:**
```
User Intent → ACL Text → Parse → Type Check → 
Budget Analysis → Gate Placement → DAG Generation → 
Optimization → Executable Plan
```

**Execution Flow:**
```
Executable Plan → DAG Traversal → 
Dispatch Roles → Execute Steps → 
Enforce Budgets → Check Gates → 
Emit VIF Witnesses → Store Results → 
Synthesize Evidence (SEG)
```

**DEPP Loop:**
```
Current Plan → Execute → Gather Evidence → 
Analyze Effectiveness → Rewrite Plan → 
Better Plan → Repeat
```

## Non‑Goals

APOE is NOT:
- **Retrieval System:** Uses HHNI, doesn't implement retrieval
- **Memory System:** Uses CMC, doesn't implement storage
- **Verification System:** Uses VIF, doesn't implement verification
- **Evidence System:** Uses SEG, doesn't implement synthesis
- **Model Execution:** Orchestrates models, doesn't execute them

## References

- System map: `systems/apoe/system.map.lucid.json5`
- Validation gates: `knowledge_architecture/validation/T0_T6_DOCUMENTATION.validation.md`
- Templates: `knowledge_architecture/PERFECT_TEMPLATES_LIBRARY.md`
- L-level docs: `systems/apoe/L0_executive.md` through `L4_complete.md`
