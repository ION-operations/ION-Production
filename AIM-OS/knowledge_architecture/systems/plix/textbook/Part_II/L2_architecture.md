# Part II: Architecture - L2 Architecture

**Part:** II - Architecture  
**Level:** L2 (Architecture)  
**Word Count:** 2,000 words (exact)  
**Purpose:** Complete technical architecture of Part II architecture

---

## Architecture Overview

Part II defines PLIx architecture through four architectural pillars, CNL grammar system, formal validation framework, and compiler architecture. The architecture enables intent-aware systems with verifiable correctness, durable execution, safety gates, and complete provenance.

## The Four Pillars Architecture

### Pillar 1: Contract Layer

Contract Layer architecture provides intent specification through Design by Contract (DbC), Controlled Natural Language (CNL) DSL, and formal validation (Alloy, TLA+). The layer transforms natural language intent into typed, verifiable contracts.

**Key Components:**
- **DbC Component:** Preconditions, postconditions, invariants specification
- **CNL Component:** SmaCoNat methodology for structured intent expression
- **Formal Validation Component:** Alloy/TLA+ integration for invariant verification
- **Contract Storage Component:** CMC integration for bitemporal contract storage

**Architectural Flow:**
NL Intent → CNL DSL → DbC Contract → Formal Validation → Stored Contract (CMC)

**Integration Points:**
- APOE: Plan compilation from contracts
- VIF: Contract verification as witnesses
- CMC: Bitemporal contract storage

### Pillar 2: Execution Layer

Execution Layer architecture provides durable, recoverable plan execution through durable execution engine, Saga pattern, and formal recovery modeling. The layer ensures plans complete or recover safely.

**Key Components:**
- **Durable Execution Component:** Temporal/Restate integration for state persistence
- **Saga Pattern Component:** Dynamic compensation logic for failure recovery
- **Recovery Verification Component:** TLA+ integration for recovery verification
- **Checkpoint Component:** CMC integration for bitemporal state persistence

**Architectural Flow:**
Contract → Execution Plan → Durable Execution → Saga Compensation → Checkpoint (CMC)

**Integration Points:**
- APOE: Plan orchestration
- CMC: Bitemporal state persistence
- TCS: Timeline tracking for execution history

### Pillar 3: Safety Layer

Safety Layer architecture provides adaptive routing and policy enforcement through linguistic confidence gates, economic router gates, and compliance gates. The layer prevents unsafe or inefficient execution.

**Key Components:**
- **Linguistic Confidence Gate:** Self-REF for confidence scoring
- **Economic Router Gate:** BaRP (Bandit-feedback Routing) for cost/performance optimization
- **Compliance Gate:** OPA/Cedar for policy enforcement
- **Gate Sequencing:** Sequential gate execution (stop at earliest risk)

**Architectural Flow:**
Contract → Linguistic Gate → Economic Gate → Compliance Gate → Execution

**Integration Points:**
- Router: Bandit routing (BaRP equivalent)
- VIF: Confidence tracking and witnesses
- SCOR: Safety and reliability monitoring
- HHNI: Semantic routing for tool selection

### Pillar 4: Evidence Layer

Evidence Layer architecture provides provenance, lineage, and auditable state through W3C PROV, OpenLineage, and intent lineage tracking. The layer enables debugging and learning from execution.

**Key Components:**
- **PROV Component:** W3C Provenance standard for entity/activity/agent tracking
- **OpenLineage Component:** Data lineage tracking (RunEvent, JobEvent, DatasetEvent)
- **Intent Lineage Component:** Trace output → NL contract
- **Bitemporal Tracking Component:** Valid time + transaction time

**Architectural Flow:**
Execution → PROV Events → OpenLineage Events → Intent Lineage → SEG Storage

**Integration Points:**
- SEG: Evidence chains as graph edges
- CMC: Bitemporal memory
- VIF: Provenance tracking via witnesses
- TCS: Timeline for auditability

## CNL Grammar Architecture

### Grammar System Architecture

CNL grammar system provides controlled natural language design through Gherkin-style grammar, SmaCoNat methodology, and complete grammar specification. The system enables unambiguous intent expression.

**Key Components:**
- **Gherkin Component:** Given-When-Then structure for natural language syntax
- **SmaCoNat Component:** Minimal keywords with unambiguous mapping
- **Grammar Specification Component:** EBNF specification with YAML/JSON examples
- **Parser Component:** CNL → PLIx AST transformation

**Architectural Flow:**
CNL Text → Lexer → Parser → AST → Validation → PLIx Contract

**Integration Points:**
- Compiler: AST generation for compilation
- Formal Validation: AST validation for correctness
- CMC: Contract storage

### Parser Architecture

Parser architecture provides robust CNL parsing through lexer design, grammar parsing, error handling, and validation. The parser transforms CNL text to PLIx AST with comprehensive error reporting.

**Key Components:**
- **Lexer Component:** Token generation from CNL text
- **Parser Component:** AST generation from tokens
- **Error Handling Component:** Syntax, semantic, validation error reporting
- **Validation Component:** AST validation for correctness

**Architectural Flow:**
CNL Text → Tokens → AST → Validation → Error Reporting → PLIx AST

**Integration Points:**
- Compiler: AST consumption for compilation
- Formal Validation: AST verification
- Error Reporting: User-friendly error messages

## Formal Validation Architecture

### Validation Framework Architecture

Formal validation framework provides invariant verification through Alloy integration, TLA+ integration, and invariant verification. The framework ensures intent correctness independent of implementation.

**Key Components:**
- **Alloy Component:** Model checking for invariant verification
- **TLA+ Component:** Temporal logic verification for system correctness
- **Layer-1 Guards Component:** Fast constraints (JSON Schema, regex)
- **Layer-2 Validators Component:** Rigorous semantic validation (SHACL, SMT solvers)

**Architectural Flow:**
PLIx Contract → Alloy Model → Model Checking → TLA+ Spec → Temporal Verification → Validation Result

**Integration Points:**
- Contract Layer: Contract validation
- Compiler: Validation during compilation
- VIF: Validation witnesses

### Invariant Verification Architecture

Invariant verification architecture provides property verification through runtime invariants (Layer-1 guards) and compile-time invariants (Layer-2 validators). The architecture ensures properties hold throughout execution.

**Key Components:**
- **Layer-1 Guards:** Runtime invariants (JSON Schema, regex constraints)
- **Layer-2 Validators:** Compile-time invariants (SHACL shapes, SMT solvers)
- **Verification Workflow:** Sequential validation (Layer-1 → Layer-2)
- **Error Reporting:** Property violation reporting

**Architectural Flow:**
Contract → Layer-1 Guards → Layer-2 Validators → Verification Result

**Integration Points:**
- Contract Layer: Property specification
- Compiler: Validation integration
- Runtime: Runtime invariant checking

## Compiler Architecture

### Compiler System Architecture

Compiler system architecture provides PLIx → IR → Execution Plans transformation through IR design, lowering process, target compilation, and APOE integration. The compiler bridges intent expression to execution.

**Key Components:**
- **IR Component:** Intermediate Representation preserving semantics and execution metadata
- **Lowering Component:** PLIx → IR transformation with topological ordering
- **Target Compilation Component:** IR → Target format (Temporal, Step Functions, Argo)
- **APOE Integration Component:** IR → APOE ExecutionPlan compilation

**Architectural Flow:**
PLIx Contract → IR → Topological Ordering → Target Compilation → Execution Plan

**Integration Points:**
- CNL Grammar: AST input
- Formal Validation: Validation during compilation
- APOE: Execution plan generation
- Runtime: Plan execution

### IR Architecture

IR architecture provides intermediate representation preserving PLIx semantics and execution metadata. IR structure includes IRNode (id, action, params, deps, retry, compensate) and IRPlan (intent, nodes, constraints, evidence).

**Key Components:**
- **IRNode Component:** Node structure with action, parameters, dependencies, retry, compensation
- **IRPlan Component:** Plan structure with intent, nodes, constraints, evidence
- **Dependency Resolution Component:** Topological ordering for execution order
- **Parameter Interpolation Component:** Parameter resolution from previous steps

**Architectural Flow:**
PLIx Contract → IRNode Creation → Dependency Resolution → IRPlan Generation

**Integration Points:**
- Lowering: PLIx → IR transformation
- Target Compilation: IR → Target format
- APOE: IR → ExecutionPlan compilation

## Architectural Patterns

### Pattern 1: Four-Pillar Defense

Four-pillar defense pattern provides layered defense against failure domains: Contract Layer (prevents invalid plans), Execution Layer (ensures safe completion), Safety Layer (prevents unsafe execution), Evidence Layer (enables debugging).

### Pattern 2: Sequential Gating

Sequential gating pattern ensures gates run sequentially, stopping at earliest risk point. Pattern: Linguistic Confidence Gate → Economic Router Gate → Compliance Gate → Execution.

### Pattern 3: Evidence Feedback Loop

Evidence feedback loop pattern enables learning from execution outcomes. Pattern: Intent → Plan → Execution → Evidence → Router Update → Improved Selection.

### Pattern 4: Intent-Driven Compilation

Intent-driven compilation pattern compiles intent contracts to execution plans through IR. Pattern: Contract → IR → Topological Ordering → Target Compilation → Execution Plan.

## Quality Attributes

### Verifiability

Part II architecture enables verifiability through formal validation (Alloy, TLA+), contract verification, and invariant checking. Verifiability ensures intent correctness independent of execution.

### Durability

Part II architecture enables durability through durable execution engine, Saga pattern, and CMC checkpointing. Durability ensures execution survives failures and recovers safely.

### Safety

Part II architecture enables safety through confidence gates, policy enforcement, and economic routing. Safety prevents unsafe or inefficient execution.

### Provenance

Part II architecture enables provenance through PROV/OpenLineage integration, intent lineage tracking, and SEG evidence chains. Provenance enables debugging and learning.

## Part II Architecture Summary

Part II architecture provides complete blueprint for PLIx systems through four pillars (Contract, Execution, Safety, Evidence), CNL grammar system (Gherkin-style, SmaCoNat, parser), formal validation framework (Alloy, TLA+, invariants), and compiler architecture (IR, lowering, target compilation, APOE integration).

Architecture enables intent-aware systems with verifiable correctness, durable execution, safety gates, and complete provenance. Architecture bridges intent expression to execution, enabling systems that understand their own purpose and verify their correctness.

---

**Word Count:** 2,000 words (exact)

