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

## 📋 NL Tag Coverage

Comprehensive NL tag coverage for semantic search, cross-system tracing, and quintet parity validation:

**Tag Metrics:**
- **Total tags:** 370 across 19 APOE files
- **Coverage:** 90% public API, 74% internal
- **Quintet parity:** P = 0.88 (very good)

**Key Categories:**
- **APOE-PLAN:** Plan creation, orchestration (primary)
- **APOE-GATE:** Execution gates, confidence routing
- **APOE-EXEC:** Task processing, parallelization
- **APOE-ACL:** Access control, role-based security
- **APOE-BUDGET:** Cost pooling, optimization
- **APOE-ERROR:** Recovery, retry strategies

**Integration Points:**
- **APOE↔VIF:** Execution witnessing, confidence gating
- **APOE↔CMC:** Plan storage, context retrieval
- **APOE↔HHNI:** Context assembly for execution

See [NL_TAG_CATALOG.md](NL_TAG_CATALOG.md) for complete index.

---

## System Overview

APOE (AI-Powered Orchestration Engine) transforms AI execution from improvisation (one-shot generation) to compilation (planned, budgeted, gated execution). The core insight: reasoning should be compiled into typed plans BEFORE execution, not improvised during execution. This enables verification, budgeting, replay, and quality gates—making AI operations predictable, auditable, and trustworthy.

APOE provides:
1. **Plan Compilation:** ACL text → Typed DAG with budgets and gates
2. **Role-Based Execution:** Eight specialized roles execute steps with enforced contracts
3. **Quality Enforcement:** Gates verify quality, safety, and policy before proceeding

## Subsystem Architecture

APOE organizes into a 3-layer hierarchy: **Layer 1** (Main System), **Layer 2** (Subsystems), **Layer 3** (Components).

### Layer 1: Main System
**apoe.aiPoweredOrchestration** - The orchestration engine that coordinates all subsystems.

### Layer 2: Subsystems (5 subsystems)

#### 1. ACL Subsystem (`acl`)
**Purpose:** Compiles ACL text into typed, executable DAG plans with budgets, gates, and contracts.

**Components (Layer 3):**
- **parser:** Parses ACL grammar (pipelines, steps, gates, budgets, roles)
- **typeChecker:** Validates contracts, inputs/outputs (integrates with SDF-CVF for quartet parity)
- **budgetAnalyzer:** Computes total budgets from step budgets
- **dependencyResolver:** Resolves step dependencies, builds DAG structure

**Integration Points:**
- SDF-CVF: ACL plans validated for quartet parity (`[SDFCVF-TYPECHECKER]`)

#### 2. Gates Subsystem (`gates`)
**Purpose:** Enforces quality, safety, and policy standards with PASS/FAIL/WARN/ABSTAIN routing.

**Components (Layer 3):**
- **qualityGates:** Quality gates (confidence, completeness, correctness) - integrates with VIF, SDF-CVF, TCS
- **safetyGates:** Safety gates (policy enforcement, risk assessment) - integrates with VIF, CAS, TCS
- **policyGates:** Policy gates (compliance, authorization) - integrates with CAS, TCS
- **budgetGates:** Budget gates (resource limits, cost controls) - integrates with TCS, CMC

**Integration Points:**
- VIF: Gates use VIF confidence scores (`[VIF-GATE]`)
- SDF-CVF: Gates enforce SDF-CVF quality standards (`[SDFCVF-GATE]`)
- CAS: Gate decisions analyzed by CAS introspection (`[CAS-INTROSPECTION]`)
- TCS: Gate evaluations tracked in TCS timeline (`[TCS-TIMELINE]`)

#### 3. Roles Subsystem (`roles`)
**Purpose:** Dispatches steps to appropriate role agents (8 roles: Planner, Retriever, Reasoner, Verifier, Builder, Critic, Operator, Witness).

**Components (Layer 3):**
- **plannerRole:** Plans execution strategy, step sequencing - integrates with CMC, CAS, TCS
- **retrieverRole:** Retrieves context for execution - integrates with HHNI (`[HHNI-RETRIEVER]`), CMC, TCS
- **reasonerRole:** Performs reasoning tasks - integrates with VIF, CMC, TCS
- **verifierRole:** Verifies execution results - integrates with VIF, SDF-CVF, TCS
- **builderRole:** Builds artifacts (code, docs, tests) - integrates with SDF-CVF, CMC, TCS
- **criticRole:** Critiques and improves outputs - integrates with VIF, CAS, TCS
- **operatorRole:** Performs operational tasks - integrates with CMC, CAS, TCS
- **witnessRole:** Generates VIF witnesses for provenance - integrates with VIF (`[VIF-WITNESS]`), CMC, TCS

**Integration Points:**
- HHNI: Retriever role uses HHNI for context retrieval (`[HHNI-RETRIEVER]`)
- VIF: Witness role generates VIF witnesses (`[VIF-WITNESS]`)
- CMC: All roles store execution traces in CMC (`[CMC-STORAGE]`)
- CAS: All roles analyzed by CAS for decision events (`[CAS-INTROSPECTION]`)
- TCS: All roles tracked in TCS timeline (`[TCS-TIMELINE]`)

#### 4. Budget Subsystem (`budget`)
**Purpose:** Tracks and enforces resource budgets (tokens, time, tools) for plan execution.

**Components (Layer 3):**
- **tokenTracker:** Tracks token consumption - integrates with TCS, CMC
- **timeTracker:** Tracks time consumption - integrates with TCS, CMC
- **toolTracker:** Tracks tool usage - integrates with TCS, CMC
- **budgetPooler:** Pools and allocates budgets across steps - integrates with CAS, CMC

**Integration Points:**
- TCS: Budget milestones tracked in TCS timeline (`[TCS-TIMELINE]`)
- CMC: Budget state stored in CMC for persistence (`[CMC-STORAGE]`)
- CAS: Budget decisions analyzed by CAS for resource patterns (`[CAS-INTROSPECTION]`)

#### 5. DEPP Subsystem (`depp`)
**Purpose:** Self-rewriting plans using SEG evidence for continuous improvement.

**Components (Layer 3):**
- **evidenceAnalyzer:** Analyzes SEG evidence for plan improvements - integrates with SEG, VIF
- **planRewriter:** Rewrites plans based on evidence - integrates with SEG, VIF, CMC
- **effectivenessCalculator:** Calculates plan effectiveness from execution traces - integrates with SEG, TCS, CAS

**Integration Points:**
- SEG: DEPP uses SEG evidence for plan rewriting (`[SEG-TRACE]`)
- VIF: DEPP rewrites validated by VIF confidence scores (`[VIF-GATE]`)
- CMC: DEPP modifications stored in CMC for audit (`[CMC-STORAGE]`)
- CAS: DEPP modifications analyzed by CAS for learning (`[CAS-INTROSPECTION]`)
- TCS: DEPP modifications tracked in TCS timeline (`[TCS-TIMELINE]`)

### Connection Pattern Tags

All integration points use connection pattern tags for semantic search and validation:
- `[HHNI-RETRIEVER]` - HHNI context retrieval
- `[VIF-GATE]` - VIF confidence gating
- `[VIF-WITNESS]` - VIF witness generation
- `[CMC-STORAGE]` - CMC state storage
- `[SEG-TRACE]` - SEG execution traces
- `[SDFCVF-GATE]` - SDF-CVF quality gates
- `[SDFCVF-TYPECHECKER]` - SDF-CVF type checking
- `[TCS-TIMELINE]` - TCS timeline tracking
- `[CAS-INTROSPECTION]` - CAS decision analysis

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

## Integration Architecture

APOE integrates with 7 core AIM-OS systems through bidirectional connections:

### HHNI Integration (`[HHNI-RETRIEVER]`)
**Purpose:** Context retrieval for Retriever role steps  
**Direction:** Bidirectional  
**Data Flow:** queries → optimized_context  
**Port:** `hhniIntegration`  
**Integration Module:** `retriever_role.py`  
**Handler:** `RetrieverRole.execute(inputs, budget)` (standard APOE role handler)

**Response Schema (passthrough of HHNI RetrievalResult):**
```json
{
  "context": [ {"id": "...", "content": "...", "level": "paragraph|section|system|sentence", "relevance": 0.0-1.0, "metadata": {...}} ],
  "total_tokens": <int>,
  "relevance_scores": [<float>],
  "modality": "code|docs|data|text",
  "k": <int>,
  "dvns_enabled": true|false,
  "metrics": {
    "coarse_time_ms": <int>,
    "dvns_time_ms": <int>,
    "relevance_score": <float>,
    "efficiency": <float>,
    "budget_utilization": <float>
  }
}
```

**Multi‑Resolution Support:**
- Use `inputs.resolution_levels: ["system"|"section"|"paragraph"|"sentence", ...]` to trigger adaptive coarse→refined retrieval.
- Handler method: `RetrieverRole._execute_multi_resolution(inputs, budget)` returns `{ multi_resolution: {<level>: {items[], tokens, scores, count}}, total_tokens, resolution_levels, modality }`.

### VIF Integration (`[VIF-GATE]`, `[VIF-WITNESS]`)
**Purpose:** Witness generation, κ-gating, confidence tracking  
**Direction:** Bidirectional  
**Data Flow:** execution_data → provenance_traces  
**Port:** `vifIntegration`  
**Integration Module:** `vif_integration.py`  
**Usage:** All steps generate VIF witnesses. Gates use VIF confidence for abstention decisions. Full provenance enables replay and auditing.

### CMC Integration (`[CMC-STORAGE]`)
**Purpose:** Execution state storage, plan artifacts  
**Direction:** Bidirectional  
**Data Flow:** execution_data → persistent_storage  
**Port:** `cmcIntegration`  
**Integration Module:** `cmc_integration.py`  
**Usage:** Plans, steps, and results persisted as atoms. State snapshots enable resumption and recovery.

### SEG Integration (`[SEG-TRACE]`)
**Purpose:** Execution traces, plan effectiveness  
**Direction:** Bidirectional  
**Data Flow:** execution_data → evidence_nodes  
**Port:** `segIntegration`  
**Integration Module:** `seg_integration.py`  
**Usage:** Execution traces become evidence nodes in SEG. DEPP uses SEG evidence to improve plans over time.

### SDF-CVF Integration (`[SDFCVF-GATE]`, `[SDFCVF-TYPECHECKER]`)
**Purpose:** Quality gates, quartet parity enforcement  
**Direction:** Bidirectional  
**Data Flow:** execution_data → quality_validation  
**Port:** `sdfcvfIntegration`  
**Integration Module:** `sdfcvf_integration.py`  
**Usage:** ACL plans validated for quartet parity. Quality gates enforce SDF-CVF standards. Builder role enforces quartet parity for artifacts.

### TCS Integration (`[TCS-TIMELINE]`)
**Purpose:** Timeline tracking, session continuity  
**Direction:** Bidirectional  
**Data Flow:** execution_events → timeline_entries  
**Port:** `tcsIntegration`  
**Integration Module:** `tcs_integration.py`  
**Usage:** Timeline entries capture plan/step/gate/budget events. Enables session continuity and performance analysis.

### CAS Integration (`[CAS-INTROSPECTION]`)
**Purpose:** Decision analysis, failure mode context  
**Direction:** Bidirectional  
**Data Flow:** execution_events → introspection_data  
**Port:** `casIntegration`  
**Integration Module:** `cas_integration.py`  
**Usage:** Safety/policy gate decisions introspected. Planning/operational decisions analyzed. Resource patterns tracked for optimization.

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


---

## 🔗 RELATED SYSTEMS

### **Systems We Depend On**

#### **CMC**
**Relationship:** bidirectional
**Integration Point:** cmcIntegration
**Data Exchanged:** execution_state, plan_artifacts, step_results (+ 1 more)
**Security Level:** high
**Docs:** `knowledge_architecture/systems/cmc/T0_executive.md`

#### **HHNI**
**Relationship:** bidirectional
**Integration Point:** hhniIntegration
**Data Exchanged:** context_retrieval_requests, optimized_context, budget_aware_queries (+ 1 more)
**Security Level:** high
**Docs:** `knowledge_architecture/systems/hhni/T0_executive.md`

#### **SDFCVF**
**Relationship:** bidirectional
**Integration Point:** sdfcvfIntegration
**Data Exchanged:** quality_gate_status, parity_checks, evolution_artifacts (+ 1 more)
**Security Level:** high
**Docs:** `knowledge_architecture/systems/sdfcvf/T0_executive.md`

#### **SEG**
**Relationship:** bidirectional
**Integration Point:** segIntegration
**Data Exchanged:** execution_traces, evidence_nodes, synthesis_requests (+ 1 more)
**Security Level:** high
**Docs:** `knowledge_architecture/systems/seg/T0_executive.md`

#### **VIF**
**Relationship:** bidirectional
**Integration Point:** vifIntegration
**Data Exchanged:** execution_witnesses, confidence_scores, provenance_traces (+ 1 more)
**Security Level:** critical
**Docs:** `knowledge_architecture/systems/vif/T0_executive.md`


### **Systems That Depend On Us**

**Other Systems:** ai_collaboration_system, autonomous_research_dream, branch_reasoning_system, capability_awareness, ccs, confidence_gated_controls, context_fidelity_inspector, context_frames_system, context_mesh_maps, cross_model_consciousness, deep_expansion_layer, dual_prompt_architecture, dynamic_cursor_rules_system, dynamic_onboarding, global_user_rules, intent_classification_system, knowledge_bootstrap_system, memory_pyramid_system, mutation_modes_system, scor

**Layer 1:** cmc, seg

**Layer 2:** hhni, sdfcvf, vif

**Layer 4:** cognitive_analysis, timeline_context_system

**Layer 5 (Infrastructure):** consciousness_enhancement, daemon_rag_system, llm_client_integration, lucid_mcp_integration, mcp_integration, mcp_tools, performance_monitoring, self_improvement_protocol, spec_coverage_index

**Layer 6 (Application):** advanced_monaco_editor, agent_system, icip_data_ingestion_layer, icip_platform, icip_streaming_processing_layer, lucid_core_console

**Total Dependent Systems:** 42

### **External Systems**

**External Dependencies:** llm

**Integration Details:** See system map (`system.map.lucid.json5`) for complete integration topology.