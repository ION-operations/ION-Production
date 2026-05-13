# PLIx→APOE Integration – L2 Architecture

**Document ID:** `plix_integration_l2_architecture`  
**Level:** L2 (Architecture)  
**Word Count Target:** 2,000 words  
**Status:** ✅ **COMPLETE**  
**Confidence:** 0.87

---

## 🏗️ **INTEGRATION ARCHITECTURE OVERVIEW**

This document provides detailed architectural design for integrating PLIx formal specification capabilities into APOE orchestration engine. The integration follows a compilation approach: PLIx intent compiles to ACL plans, which execute on enhanced APOE infrastructure.

### **Design Principles:**
1. **Enhance, Don't Replace** - APOE remains the orchestration engine
2. **Preserve Existing Functionality** - All 30 APOE tests continue passing
3. **Add Value Through Formalization** - Formal verification, provenance, resilience
4. **Maintain Simplicity** - ACL syntax remains straightforward
5. **Systematic Integration** - Follow LDP and L0-L4 protocols rigorously

---

## 📊 **ARCHITECTURAL LAYERS**

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERACTION LAYER                   │
│  PLIx Intent (CNL) - Human-readable contract specification   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    PARSING & VALIDATION LAYER                │
│  PLIx Parser (100% Core-PLIx compliant)                      │
│  - Tokenizer, AST builder, type checker                      │
│  - Produces: PLIx AST with contracts, plans, constraints     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    COMPILATION LAYER (NEW)                   │
│  PLIx→ACL Compiler                                           │
│  - Maps PLIx constructs to ACL constructs                    │
│  - Validates purity, generates compensation                  │
│  - Produces: Enhanced ACL Plan                               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATION LAYER (ENHANCED)            │
│  Enhanced APOE Executor                                      │
│  - Existing: Dependency resolution, gate validation          │
│  - New: Compensation, retry/fallback, purity checking        │
│  - Produces: Execution result + enhanced evidence            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    VERIFICATION LAYER (NEW)                  │
│  Backend Compilers: TLA+, Alloy, OPA, IRPlan                │
│  - Formal verification (TLA+/Alloy)                          │
│  - Policy enforcement (OPA)                                  │
│  - Execution (IRPlan)                                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    PROVENANCE LAYER (ENHANCED)               │
│  Enhanced VIF Integration                                    │
│  - Existing: Execution witnesses                             │
│  - New: Constraint replay, purity proofs, subdistribution    │
│  - Stores: CMC bitemporal atoms                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 **DETAILED COMPONENT DESIGN**

### **1. PLIx→ACL Compiler (NEW COMPONENT)**

**Purpose:** Transform PLIx intent (CNL with formal semantics) into APOE's ACL execution language while preserving formal properties.

**Location:** `packages/apoe/plix_compiler/`

**Architecture:**
```typescript
class PLIxToACLCompiler {
  // Core compilation
  compile(plixIntent: PLIxIntent): ACLPlan
  
  // PLIx construct mapping
  private mapContract(contract: Contract): ACLGates[]
  private mapPlan(plan: Plan): ACLSteps[]
  private mapStep(step: Step): ACLStep
  private mapDependencies(deps: Dependency[]): ACLRequires[]
  
  // Formal semantics preservation
  private validatePurity(constraint: Constraint): PurityCheck
  private generateCompensation(step: Step): ACLCompensation
  private generateRetryPolicy(step: Step): ACLRetry
  
  // Type system mapping
  private mapEffects(effects: EffectRow): ACLEffects
  private mapConfidence(conf: Confidence): ACLGate
}
```

**Mapping Strategy:**

| PLIx Construct | ACL Construct | Preservation |
|----------------|---------------|--------------|
| `pre: constraint` | `GATE precondition: eval(constraint)` | Purity validated |
| `post: constraint` | `GATE postcondition: eval(constraint)` | Purity validated |
| `depends_on: [steps]` | `REQUIRES step1, step2` | Direct mapping |
| `compensate step -> Action` | Custom compensation logic | Saga semantics |
| `retry: policy` | Retry handler with backoff | Subdistribution |
| `fallback: alternative` | Fallback execution path | Resilience |
| `effects: [io, net]` | Effect tracking metadata | Type system |
| `confidence: 0.90` | `GATE confidence >= 0.90` | Lattice ops |

**Purity Validation:**
```typescript
interface PurityChecker {
  // Check if constraint is pure (no side effects)
  isPure(expr: Expression): boolean
  
  // Validate no I/O, network, database, or state mutation
  validateNoSideEffects(expr: Expression): PurityResult
  
  // Safe operations: arithmetic, logic, comparison, pure functions
  allowedOperations: Set<OperationType>
}
```

**Compilation Example:**
```plix
ask ent:room/meeting
  act:reserve
  requires
    con:available == true
  ensures
    con:reserved == true
  plan [
    task check := api.check_room()
    task reserve := api.reserve_room(room: check.ref:room_id)
      depends_on: check
      compensate reserve -> api.cancel(id: reserve.ref:id)
      retry: exponential(max: 3, backoff: 2s)
      confidence: 0.95
  ]
```

**Compiles to ACL:**
```acl
PLAN room_reservation:
  ROLE api: llm(model="gpt-4-turbo")
  
  GATE precondition: available == true
  GATE postcondition: reserved == true
  
  STEP check:
    ASSIGN api: "Check room availability"
    BUDGET tokens=1000, time=5s
  
  STEP reserve:
    ASSIGN api: "Reserve meeting room"
    REQUIRES check
    BUDGET tokens=1000, time=5s
    GATE confidence: output.confidence >= 0.95
    COMPENSATION: api.cancel(id=output.id)
    RETRY: exponential(max=3, backoff=2s)
```

---

### **2. Enhanced APOE Executor (ENHANCED COMPONENT)**

**Purpose:** Execute ACL plans with new capabilities: compensation, retry/fallback, purity checking.

**Location:** `packages/apoe/executor.py` (enhanced)

**New Capabilities:**

**A. Compensation Execution (Saga Pattern)**
```python
class CompensationEngine:
    """
    Execute compensation steps in reverse topological order on failure.
    Implements saga pattern for reversible operations.
    """
    
    def execute_with_compensation(self, plan: ExecutionPlan) -> Result:
        completed_steps = []
        try:
            for step in plan.steps:
                result = self._execute_step(step)
                completed_steps.append((step, result))
        except Exception as e:
            # Failure: compensate in reverse order
            return self._compensate(completed_steps, e)
        return Success(completed_steps)
    
    def _compensate(self, steps: List[Tuple[Step, Result]], error: Exception):
        """Execute compensation in reverse topological order"""
        compensation_results = []
        for step, result in reversed(steps):
            if step.compensation:
                comp_result = self._execute_compensation(step.compensation, result)
                compensation_results.append(comp_result)
        return CompensationFailure(error, compensation_results)
```

**B. Retry/Fallback Logic**
```python
class RetryFallbackEngine:
    """
    Retry steps with exponential backoff, fallback on exhaustion.
    Implements subdistribution monad semantics.
    """
    
    def execute_with_retry(self, step: Step) -> Result:
        policy = step.retry_policy or RetryPolicy(max=3, backoff=ExponentialBackoff(base=2))
        
        for attempt in range(policy.max_attempts):
            try:
                result = self._execute_step(step)
                if self._validate_result(result, step.gates):
                    return Success(result)
            except Exception as e:
                if attempt < policy.max_attempts - 1:
                    time.sleep(policy.backoff.delay(attempt))
                    continue
                else:
                    # Exhausted retries: try fallback
                    if step.fallback:
                        return self._execute_fallback(step.fallback)
                    raise e
```

**C. Purity Checking**
```python
class PurityValidator:
    """
    Validate constraints are pure (no side effects).
    Enforces formal semantics requirement.
    """
    
    def validate_constraint_purity(self, constraint: Constraint) -> PurityResult:
        # Parse constraint expression
        expr = self._parse_expression(constraint.condition)
        
        # Check for forbidden operations
        if self._has_side_effects(expr):
            return PurityViolation(constraint, "Constraint has side effects")
        
        # Validate all operations are pure
        for op in self._get_operations(expr):
            if op not in PURE_OPERATIONS:
                return PurityViolation(constraint, f"Impure operation: {op}")
        
        return PurityValid(constraint)
```

---

### **3. Verification Backends (NEW COMPONENTS)**

**Purpose:** Compile ACL plans to various verification targets for formal checking and policy enforcement.

**A. TLA+ Backend**

**Location:** `packages/apoe/backends/tlaplus_backend.py`

**Purpose:** Compile ACL to TLA+ for model checking safety and liveness properties.

**Example Output:**
```tla
---- MODULE RoomReservation ----
EXTENDS Naturals, Sequences

VARIABLES available, reserved, compensation_executed

Init == available = TRUE /\ reserved = FALSE /\ compensation_executed = FALSE

CheckRoom == available = TRUE

ReserveRoom == 
    /\ available = TRUE
    /\ reserved' = TRUE
    /\ available' = FALSE
    /\ UNCHANGED compensation_executed

Compensate ==
    /\ reserved = TRUE
    /\ reserved' = FALSE
    /\ compensation_executed' = TRUE

Next == CheckRoom \/ ReserveRoom \/ Compensate

Spec == Init /\ [][Next]_<<available, reserved, compensation_executed>>

Safety == reserved => ~available
Liveness == <>reserved
====
```

**B. Alloy Backend**

**Location:** `packages/apoe/backends/alloy_backend.py`

**Purpose:** Compile ACL to Alloy for structural validation.

**Example Output:**
```alloy
sig Room {
  available: lone Bool,
  reserved: lone Bool
}

pred checkRoom[r: Room] {
  r.available = True
}

pred reserveRoom[r, r': Room] {
  r.available = True
  r'.reserved = True
  r'.available = False
}

pred compensate[r, r': Room] {
  r.reserved = True
  r'.reserved = False
}

assert safetyProperty {
  all r: Room | r.reserved = True => r.available = False
}

check safetyProperty for 5
```

**C. OPA Backend**

**Location:** `packages/apoe/backends/opa_backend.py`

**Purpose:** Compile ACL to OPA policies for runtime enforcement.

**Example Output:**
```rego
package room_reservation

default allow = false

allow {
  input.action == "check_room"
  input.room.available == true
}

allow {
  input.action == "reserve_room"
  input.room.available == true
  input.confidence >= 0.95
}

compensate {
  input.action == "cancel_reservation"
  input.room.reserved == true
}
```

---

### **4. Enhanced VIF Integration (ENHANCED COMPONENT)**

**Purpose:** Create enhanced witnesses for PLIx-specific provenance (purity proofs, constraint replay, subdistribution evidence).

**Location:** `packages/apoe/vif_integration.py` (enhanced)

**New Witness Types:**

**A. Constraint Replay Witness**
```python
@dataclass
class ConstraintReplayWitness:
    """
    Witness for deterministic constraint re-evaluation.
    Enables verification without re-execution.
    """
    constraint_id: str
    constraint_text: str
    evaluation_time: datetime
    input_state: Dict[str, Any]  # Variable bindings
    result: bool
    evidence_dag_hash: str  # Hash of supporting evidence
    purity_proof: PurityProof  # Proof constraint is pure
```

**B. Purity Proof Witness**
```python
@dataclass
class PurityProof:
    """
    Cryptographic proof that constraint is pure (no side effects).
    """
    constraint_id: str
    ast_hash: str  # Hash of constraint AST
    allowed_operations: Set[str]  # Whitelist of operations used
    validation_result: bool
    validator_signature: str  # Cryptographic signature
```

**C. Subdistribution Witness**
```python
@dataclass
class SubdistributionWitness:
    """
    Witness for probabilistic execution (retries, fallbacks).
    Tracks all execution attempts and their outcomes.
    """
    step_id: str
    attempts: List[AttemptRecord]  # All retry attempts
    final_result: Optional[Result]  # Success or None
    probability_mass: float  # Total probability consumed
    subdistribution_valid: bool  # Monad laws verified
```

---

## 🔗 **SYSTEM INTEGRATION POINTS**

### **Integration with CMC (Context Memory Core)**

**Purpose:** Store enhanced witnesses bitemporally for complete provenance.

**Integration:**
```python
# Store PLIx execution witness
witness = create_plix_witness(plan, result)
atom = CMCAtom(
    content=witness,
    modality="execution",
    valid_from=now(),
    valid_to=None,  # Open-ended
    metadata={
        "plix_plan_id": plan.id,
        "formal_verification": True,
        "compensation_available": plan.has_compensation,
    }
)
cmc_client.store_atom(atom)
```

**Data Flow:**
```
Enhanced APOE → Execution Result → Enhanced VIF Witness → CMC Atom → Bitemporal Storage
```

### **Integration with HHNI (Hierarchical Hypergraph Neural Index)**

**Purpose:** Index PLIx constructs for semantic retrieval.

**New Index Types:**
```python
# Index PLIx contracts
hhni.index_contract(
    contract_id=contract.id,
    preconditions=contract.preconditions,
    postconditions=contract.postconditions,
    embedding=generate_embedding(contract)
)

# Index formal proofs
hhni.index_proof(
    proof_id=proof.id,
    theorem=proof.theorem,
    verification_backend="TLA+",
    embedding=generate_embedding(proof)
)
```

### **Integration with SEG (Shared Evidence Graph)**

**Purpose:** Synthesize formal proofs from multiple verification backends.

**Synthesis:**
```python
# Combine TLA+ and Alloy results
tla_result = tlaplus_backend.verify(plan)
alloy_result = alloy_backend.verify(plan)

synthesis = seg.synthesize_proofs([tla_result, alloy_result])
# Result: Confidence-weighted consensus on safety properties
```

---

## 📊 **DATA FLOW ARCHITECTURE**

### **End-to-End Flow:**

```
1. User writes PLIx intent (CNL)
   └→ Natural language contract specification

2. PLIx Parser processes intent
   └→ PLIx AST (contracts, plans, steps, constraints)

3. PLIx→ACL Compiler transforms AST
   ├→ Validates purity of constraints
   ├→ Generates compensation steps
   ├→ Maps to ACL constructs
   └→ Produces: Enhanced ACL Plan

4. Enhanced APOE Executor runs plan
   ├→ Resolves dependencies (topological sort)
   ├→ Executes steps with retry/fallback
   ├→ Validates gates (pre/post conditions)
   ├→ Runs compensation on failure
   └→ Produces: Execution Result + Evidence

5. Verification Backends validate
   ├→ TLA+ checks safety/liveness
   ├→ Alloy validates structure
   ├→ OPA enforces policies
   └→ Produces: Verification Results

6. Enhanced VIF creates witnesses
   ├→ Constraint replay witnesses
   ├→ Purity proofs
   ├→ Subdistribution evidence
   └→ Produces: Enhanced VIF Witnesses

7. CMC stores witnesses bitemporally
   └→ Complete provenance chain preserved

8. HHNI indexes for retrieval
   └→ Semantic search over contracts/proofs

9. SEG synthesizes proofs
   └→ Confidence-weighted consensus
```

---

## ⚙️ **COMPONENT INTERFACES**

### **PLIx→ACL Compiler API:**
```typescript
interface PLIxToACLCompiler {
  compile(intent: PLIxIntent): ACLPlan
  validatePurity(constraint: Constraint): PurityResult
  generateCompensation(step: Step): Compensation
}
```

### **Enhanced APOE Executor API:**
```python
class EnhancedAPOEExecutor:
    def execute(self, plan: ACLPlan) -> ExecutionResult
    def execute_with_compensation(self, plan: ACLPlan) -> Result
    def validate_purity(self, plan: ACLPlan) -> PurityValidation
```

### **Backend Compiler APIs:**
```python
class TLAPlusBackend:
    def compile(self, plan: ACLPlan) -> TLASpec
    def verify(self, spec: TLASpec) -> VerificationResult

class AlloyBackend:
    def compile(self, plan: ACLPlan) -> AlloyModel
    def check(self, model: AlloyModel) -> AlloyResult

class OPABackend:
    def compile(self, plan: ACLPlan) -> OPAPolicy
    def evaluate(self, policy: OPAPolicy, input: Dict) -> PolicyResult
```

---

## 🎯 **ARCHITECTURAL DECISIONS**

### **Decision 1: Compilation vs. Direct Execution**
- **Chosen:** Compilation (PLIx → ACL)
- **Rationale:** Leverages existing APOE infrastructure, clear separation of concerns
- **Alternative Rejected:** Direct PLIx execution (redundant engine)

### **Decision 2: Enhance vs. Replace APOE**
- **Chosen:** Enhance APOE
- **Rationale:** APOE is 70% complete, well-tested, integrated
- **Alternative Rejected:** Create separate PLIx executor

### **Decision 3: Backend Architecture**
- **Chosen:** Pluggable backend system (TLA+/Alloy/OPA/IRPlan)
- **Rationale:** Supports multiple verification strategies
- **Alternative Rejected:** Single verification backend

### **Decision 4: Witness Storage**
- **Chosen:** Enhanced VIF + CMC bitemporal storage
- **Rationale:** Preserves existing provenance infrastructure
- **Alternative Rejected:** Separate PLIx witness store

---

## 📊 **PERFORMANCE CONSIDERATIONS**

### **Compilation Performance:**
- **Target:** < 1 second for typical intent (10-20 steps)
- **Strategy:** Single-pass compilation, minimal AST traversals
- **Optimization:** Cache purity validation results

### **Execution Performance:**
- **Target:** No degradation vs. current APOE (< 5% overhead)
- **Strategy:** Compensation/retry only when needed
- **Optimization:** Lazy evaluation of verification backends

### **Verification Performance:**
- **Target:** < 5 seconds for TLA+/Alloy verification
- **Strategy:** Sandboxed, parallel execution
- **Optimization:** Cache verification results per plan hash

---

## 🔒 **SECURITY CONSIDERATIONS**

### **Purity Enforcement:**
- All constraints validated as pure before execution
- Prevents side effects in verification layer
- Cryptographic proof of purity in VIF witnesses

### **Sandboxed Verification:**
- TLA+/Alloy/OPA run in isolated processes
- Resource limits enforced
- Timeout protection

### **Provenance Integrity:**
- All witnesses cryptographically signed
- Tamper-evident evidence chains
- Bitemporal immutability via CMC

---

## 🎯 **SUCCESS METRICS**

**Integration succeeds when:**
1. ✅ PLIx intent compiles to ACL with 100% correctness
2. ✅ All 30 existing APOE tests continue passing
3. ✅ New integration tests pass (target: 50+)
4. ✅ Performance acceptable (< 5% overhead)
5. ✅ Verification backends operational
6. ✅ Enhanced VIF witnesses created correctly
7. ✅ Documentation complete (L0-L4)
8. ✅ System maps updated
9. ✅ SUPER_INDEX updated with PLIx concepts

---

**Word Count:** ~2,000 words ✅  
**Confidence:** 0.87  
**Status:** L2 COMPLETE  
**Next:** L3 Implementation Guide (10,000 words)

