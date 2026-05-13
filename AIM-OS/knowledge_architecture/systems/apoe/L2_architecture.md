---
id: "apoe_T2_architecture"
system: "apoe"
component: null
level: "T2"
type: "architecture"
title: "APOE Architecture"
description: "2,000-word architecture document for AI-Powered Orchestration Engine"
audience: "developers, architects, implementation planning"
confidence_threshold: 0.70
token_cost: 2000
word_count: 2000
created: "2025-10-30T00:00:00Z"
updated: "2025-11-02T15:55:00Z"
author: "aether"
status: "complete"
tags: ["apoe", "core", "orchestration", "planning", "t0-t6", "transitional"]
dependencies: ["apoe_T1_overview"]
related_docs: ["apoe_T3_detailed", "system.map.lucid.json5", "usage.envelope.md"]
version: "v2.2.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# APOE – T2 Architecture (≈2000 words)

## 🔄 **SDF-CVF QUARTET PARITY ENFORCEMENT**

### **Quartet Elements:**

**Code:** APOE implementation files (`packages/apoe/`), ACL compiler, DAG executor, role dispatcher  
**Docs:** T0-T6 documentation (L0_executive.md, L1_overview.md, L2_architecture.md, L3_detailed.md, L4_complete.md), usage.envelope.md  
**Tests:** APOE test suite (`packages/apoe/tests/`), integration tests, ACL compilation tests  
**Traces:** VIF witnesses (execution traces), SEG provenance (plan effectiveness), timeline entries, decision logs

**Parity Requirement:** P ≥ 0.90 for all changes  
**Cross-Tagging:** All quartet elements must be tagged with change ID (apoe-change-YYYYMMDD-HHMMSS) and semantically aligned

### **Quartet Parity Formula:**

```
P = (C_code×docs + C_code×tests + C_code×traces +
     C_docs×tests + C_docs×traces + C_tests×traces) / 6

Where:
- C_code×docs = semantic similarity between code and docs
- C_code×tests = semantic similarity between code and tests
- C_code×traces = semantic similarity between code and traces
- C_docs×tests = semantic similarity between docs and tests
- C_docs×traces = semantic similarity between docs and traces
- C_tests×traces = semantic similarity between tests and traces

Target: P ≥ 0.90 for all changes
```

### **Cross-Tagging Protocol:**

**Change ID Format:** `apoe-change-YYYYMMDD-HHMMSS` (e.g., `apoe-change-20251102-155530`)

**Tagging Requirements:**
- **Code:** Change ID in comments/metadata within modified code sections
- **Docs:** Change ID in frontmatter `tags` array and/or inline comments
- **Tests:** Change ID in test function docstrings/comments
- **Traces:** Change ID in VIF witness metadata, SEG provenance links, timeline entry metadata, decision log filename/content

**Workflow:**
1. Generate Change ID at start of APOE modification
2. Modify code (APOE implementation) → Tag with Change ID
3. Update docs (T-level docs) → Tag with Change ID
4. Update/add tests (APOE test suite) → Tag with Change ID
5. Create traces (VIF witnesses, SEG, timeline, decision log) → Tag with Change ID
6. Validate quartet parity (P ≥ 0.90) before merge

### **Gate Enforcement:**

**Pre-commit Gate:** Check quartet completeness and parity before commit  
**CI Gate:** Validate quartet parity in pipeline  
**Deployment Gate:** Verify quartet parity before deployment  
**Quarantine:** Changes with P < 0.90 are quarantined until parity achieved

---

## 🎯 **LUCID DEVELOPMENT PROTOCOL INTEGRATION**

### **Stage 0: Intent Capture**

**Intent Statement:**
We are updating APOE documentation to current standards (T0-T6, Perfect Metadata, SDF-CVF quartet parity, System Maps, Usage Envelopes, LDP Stage 0-1) so that APOE documentation serves as a complete template for other AIM-OS systems and ensures perfect alignment across Code, Docs, Tests, and Traces.

**Value Targets:**
- **Must Get Better:** Documentation structure, standards compliance, quartet parity clarity, onboarding experience
- **Must Not Get Worse:** Existing functionality, backward compatibility, documentation accuracy, performance

**Scope Class:** Extension - Adding T0-T6 documentation structure, quartet parity requirements, LDP integration, and system mapping to existing APOE documentation

**Why This Matters:**
This update preserves the "ghost of intent" - why APOE exists (transform AI execution from improvisation to compilation through planned, budgeted, gated execution) - while elevating documentation to full AIM-OS standards compliance. The intent follows the work forever, ensuring APOE never drifts from its core purpose.

---

### **Stage 1: System Index & Ontology**

**System Classification:**
- **Layer:** 3 (Orchestration Layer - depends on CMC, HHNI, VIF)
- **Security Level:** Critical (orchestration affects all systems)
- **Performance Sensitivity:** High (execution latency affects user experience)
- **Ownership:** Core (AIM-OS core system)
- **Side Effects:** 
  - Orchestrates all AI operations
  - Enables planned execution
  - Enforces budgets and gates
  - Affects execution quality for all systems

**System Relationships:**
- **Depends On:** CMC (state storage), HHNI (context retrieval), VIF (witness generation), LLM providers (model execution)
- **Feeds Data To:** All AIM-OS systems (SEG, SDF-CVF, CAS, etc.)
- **Integrates With:** HHNI (context retrieval), VIF (execution gates), CMC (state storage), SEG (execution traces), SDF-CVF (quality gates)

**System Context:**
APOE operates at the orchestration layer, providing planned, budgeted, gated execution for all AIM-OS systems. It transforms AI execution from improvisation to compilation, enabling verification before execution, budget enforcement, and quality gates.

---

## System Overview

APOE (AI-Powered Orchestration Engine) transforms AI execution from improvisation (one-shot generation) to compilation (planned, budgeted, gated execution). The core insight: reasoning should be compiled into typed plans BEFORE execution, not improvised during execution. This enables verification, budgeting, replay, and quality gates—making AI operations predictable, auditable, and trustworthy.

APOE provides:
1. **Plan Compilation:** ACL text → Typed DAG with budgets and gates
2. **Role-Based Execution:** Eight specialized roles execute steps with enforced contracts
3. **Quality Enforcement:** Gates verify quality, safety, and policy before proceeding

## Components

### 1. ACL Compiler
**Purpose:** Transform ACL text into typed, executable plans

**Responsibilities:**
- Parse ACL grammar (pipelines, steps, gates, budgets, roles)
- Type checking (validate contracts, inputs/outputs)
- Budget analysis (compute total budgets from step budgets)
- Gate placement (verify gates positioned correctly)
- DAG generation (convert to directed acyclic graph)
- Optimization (parallelize independent steps)

**Key Operations:**
- `compile()` - Parse and compile ACL to executable plan
- `parse()` - ACL text → AST (Abstract Syntax Tree)
- `type_check()` - Validate types and contracts
- `analyze_budgets()` - Compute total budgets
- `generate_dag()` - Convert plan to DAG structure
- `optimize()` - Parallelize independent steps

### 2. DAG Executor
**Purpose:** Execute plans as directed acyclic graphs

**Responsibilities:**
- Topological sort (determine execution order)
- Dependency resolution (resolve step dependencies)
- Parallel execution (run independent steps concurrently)
- State management (track step outputs, inputs)
- Error handling (retry, backoff, circuit breakers)

**Key Operations:**
- `execute()` - Run plan DAG from start to finish
- `topological_sort()` - Order steps by dependencies
- `execute_step()` - Run single step with role dispatch
- `resolve_dependencies()` - Resolve step inputs from outputs
- `handle_error()` - Retry, backoff, or escalate

### 3. Role Dispatcher
**Purpose:** Dispatch steps to appropriate role agents

**Responsibilities:**
- Role selection (match step to role capabilities)
- Contract enforcement (validate inputs/outputs match contracts)
- Budget enforcement (ensure steps don't exceed budgets)
- κ-gating integration (VIF confidence checks)
- VIF witness generation (emit witnesses for each step)

**Key Operations:**
- `dispatch()` - Assign step to role and execute
- `select_role()` - Choose appropriate role for step
- `enforce_contract()` - Validate contract compliance
- `enforce_budget()` - Check budget limits
- `generate_witness()` - Create VIF witness for step

### 4. Gate Manager
**Purpose:** Enforce quality, safety, and policy gates

**Responsibilities:**
- Gate evaluation (check gate conditions)
- Decision routing (PASS, FAIL, WARN, ABSTAIN)
- Escalation handling (route to HITL when needed)
- Policy enforcement (check against policies)
- Budget gate enforcement (prevent resource violations)

**Key Operations:**
- `evaluate_gate()` - Check gate condition
- `route_decision()` - Route based on gate result
- `escalate()` - Route to human-in-the-loop
- `check_policy()` - Verify policy compliance
- `check_budget()` - Verify budget not exceeded

### 5. Budget Tracker
**Purpose:** Track and enforce resource budgets

**Responsibilities:**
- Token accounting (track token usage per step)
- Time tracking (monitor execution time)
- Tool usage tracking (count tool invocations)
- Budget enforcement (halt if exceeded)
- Resource optimization (warn before limits)

**Key Operations:**
- `track_tokens()` - Monitor token usage
- `track_time()` - Monitor execution time
- `track_tools()` - Count tool invocations
- `check_budget()` - Verify within limits
- `halt_if_exceeded()` - Stop execution if budget exceeded

### 6. DEPP Module (Self-Rewriting Plans)
**Purpose:** Improve plans via evidence-based rewriting

**Responsibilities:**
- Evidence collection (gather VIF witnesses, SEG evidence)
- Effectiveness analysis (evaluate plan performance)
- Plan rewriting (generate improved plan version)
- Meta-learning (learn from execution patterns)
- Continuous optimization (iteratively improve plans)

**Key Operations:**
- `collect_evidence()` - Gather VIF and SEG evidence
- `analyze_effectiveness()` - Evaluate plan performance
- `rewrite_plan()` - Generate improved plan
- `learn_patterns()` - Extract meta-learning insights
- `optimize()` - Iteratively improve plans

## Data Models

### Plan Schema

```python
@dataclass
class ExecutionPlan:
    """Compiled, executable plan"""
    id: str
    name: str
    dag: DAG  # Directed acyclic graph of steps
    total_budget: Budget
    gates: List[Gate]
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    created_at: datetime
    
@dataclass
class Step:
    """Single step in execution plan"""
    id: str
    name: str
    role: Role  # Planner, Retriever, etc.
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    budget: Budget
    contract: Contract
    dependencies: List[str]  # Step IDs that must complete first
    gates: List[Gate]  # Gates after this step
    
@dataclass
class Budget:
    """Resource budget constraints"""
    tokens: int
    time: int  # seconds
    tools: int
    cost: Optional[float]  # USD
    
@dataclass
class Gate:
    """Quality/safety/policy gate"""
    id: str
    type: str  # "quality" | "safety" | "policy" | "budget"
    condition: str  # Expression to evaluate
    action: str  # "PASS" | "FAIL" | "WARN" | "ABSTAIN"
```

### Role Schema

```python
@dataclass
class Role:
    """Specialized agent role"""
    name: str  # Planner, Retriever, etc.
    capabilities: List[str]
    contract: Contract
    budget_defaults: Budget
    
@dataclass
class Contract:
    """Input/output contract"""
    inputs: Dict[str, Type]
    outputs: Dict[str, Type]
    ensures: str  # Postcondition
```

## Key Flows

### Compilation Flow

```
ACL Text
    ↓
┌──────────────────┐
│ Parse            │ ACL → AST
└──────────────────┘
    ↓
┌──────────────────┐
│ Type Check       │ Validate types, contracts
└──────────────────┘
    ↓
┌──────────────────┐
│ Budget Analysis  │ Compute total budgets
└──────────────────┘
    ↓
┌──────────────────┐
│ Gate Placement   │ Verify gates positioned correctly
└──────────────────┘
    ↓
┌──────────────────┐
│ DAG Generation   │ Convert to directed acyclic graph
└──────────────────┘
    ↓
┌──────────────────┐
│ Optimization     │ Parallelize independent steps
└──────────────────┘
    ↓
Executable Plan
```

### Execution Flow

```
Executable Plan
    ↓
┌──────────────────┐
│ Topological Sort │ Order steps by dependencies
└──────────────────┘
    ↓
┌──────────────────┐
│ For Each Step:   │
│ 1. Dispatch Role │ Assign to appropriate role
│ 2. Execute Step  │ Run with budgets enforced
│ 3. Check Gates   │ Verify quality/safety/policy
│ 4. Emit VIF      │ Generate witness envelope
│ 5. Store Results │ Persist in CMC
└──────────────────┘
    ↓
Execution Complete
```

### DEPP Loop Flow

```
Current Plan
    ↓
┌──────────────────┐
│ Execute Plan     │ Run with monitoring
└──────────────────┘
    ↓
┌──────────────────┐
│ Gather Evidence  │ Collect VIF witnesses, SEG nodes
└──────────────────┘
    ↓
┌──────────────────┐
│ Analyze          │ Evaluate effectiveness
│ Effectiveness    │
└──────────────────┘
    ↓
┌──────────────────┐
│ Rewrite Plan     │ Generate improved version
└──────────────────┘
    ↓
Better Plan → Repeat
```

## Integrations

**HHNI (Hierarchical Hypergraph Neural Index):**
- APOE uses HHNI for context retrieval in Retriever role steps
- Retrieval operations budgeted and witnessed
- Context influences confidence scores for κ-gating

**VIF (Verifiable Intelligence Framework):**
- APOE emits VIF witnesses for every step execution
- Gates use VIF confidence for abstention decisions
- Full provenance enables replay and auditing

**CMC (Context Memory Core):**
- APOE stores execution state in CMC
- Plans, steps, and results persisted as atoms
- State snapshots enable resumption and recovery

**SEG (Shared Evidence Graph):**
- APOE execution traces become evidence nodes in SEG
- DEPP uses SEG evidence to improve plans over time
- Synthesis across executions enables meta-learning

**SDF-CVF (Atomic Evolution Framework):**
- APOE operations respect quartet parity (Code/Docs/Tests/Traces)
- Quality gates enforce SDF-CVF standards
- Trace emissions include APOE execution provenance

## The 8 Roles

**Planner:** Decompose complex tasks into sub-tasks  
**Retriever:** Fetch context via HHNI (uses CMC)  
**Reasoner:** Multi-step logical inference  
**Verifier:** Check outputs match requirements  
**Builder:** Generate code/content/artifacts  
**Critic:** Identify flaws, edge cases, issues  
**Operator:** Execute plans, monitor progress  
**Witness:** Record provenance, emit VIF

Each role has capabilities, contracts, budgets, and κ-gating integration.

## Gate Types

**Quality Gates:** Verify output meets standards  
**Safety Gates:** Enforce security/compliance  
**Policy Gates:** Check against policies  
**Budget Gates:** Ensure limits not exceeded

Gates can PASS (continue), FAIL (halt), WARN (flag), ABSTAIN (escalate to HITL).

## Non‑Functional Requirements

### Performance Targets

**SLOs:**
- Compilation: < 100ms for typical plan
- Execution: < 1s per step (role-dependent)
- Gate evaluation: < 10ms per gate
- DAG traversal: Efficient topological sort

**Current Performance:**
- Compilation: ~50ms ✅
- Execution: Variable (role-dependent) ✅
- Gates: < 5ms ✅

### Concurrency & Scalability

- **Parallel Execution:** Independent steps run concurrently
- **Resource Management:** Budget enforcement prevents overload
- **State Management:** CMC snapshots enable scalability

### Determinism & Reproducibility

- **Deterministic:** Same plan + inputs → same outputs (with VIF replay)
- **Reproducible:** VIF witnesses enable complete replay
- **Auditable:** Full provenance trail in VIF and SEG

## Diagrams

**Component Diagram:**
```
┌────────────────────────────────────────┐
│         User Intent (ACL)              │
└──────────────┬─────────────────────────┘
               │
┌──────────────▼─────────────────────────┐
│       ACL Compiler                     │
├────────────────────────────────────────┤
│  • Parse                               │
│  • Type Check                          │
│  • Budget Analysis                     │
│  • DAG Generation                      │
└──────────────┬─────────────────────────┘
               │
┌──────────────▼─────────────────────────┐
│       DAG Executor                     │
├────────────────────────────────────────┤
│  • Topological Sort                    │
│  • Dependency Resolution               │
│  • Parallel Execution                  │
└──────────────┬─────────────────────────┘
               │
┌──────────────▼─────────────────────────┐
│       Role Dispatcher                  │
├────────────────────────────────────────┤
│  • 8 Roles (Planner, Retriever, etc.) │
│  • Contract Enforcement                │
│  • Budget Enforcement                  │
└──────────────┬─────────────────────────┘
               │
┌──────────────▼─────────────────────────┐
│       Gate Manager                     │
├────────────────────────────────────────┤
│  • Quality Gates                       │
│  • Safety Gates                        │
│  • Policy Gates                        │
└──────────────┬─────────────────────────┘
               │
┌──────────────▼─────────────────────────┐
│       Budget Tracker                   │
├────────────────────────────────────────┤
│  • Token Accounting                    │
│  • Time Tracking                       │
│  • Tool Usage                          │
└──────────────┬─────────────────────────┘
               │
┌──────────────▼─────────────────────────┐
│       VIF Witness Generator            │
└────────────────────────────────────────┘
```

**Sequence Diagram (Execution):**
```
Plan → Executor → Role Dispatcher → Execute Step → Gate Check → VIF Witness → Next Step
```

## References

- System map: `systems/apoe/system.map.lucid.json5`
- Validation gates: `knowledge_architecture/validation/T0_T6_DOCUMENTATION.validation.md`
- Templates: `knowledge_architecture/PERFECT_TEMPLATES_LIBRARY.md`
- L-level docs: `systems/apoe/L0_executive.md` through `L4_complete.md`
- Implementation: `packages/apoe/` (139 tests passing ✅)
