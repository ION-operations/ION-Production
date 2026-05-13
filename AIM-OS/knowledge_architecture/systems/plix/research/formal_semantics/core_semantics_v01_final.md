# Core-PLIx Semantics v0.1: Final Refinements

**Date:** 2025-01-27  
**Status:** 📋 **FINAL REFINEMENTS**  
**Version:** 0.1.1  
**Based on:** ChatGPT final refinements (semantic gaps, actionable effects, full specifications)

---

## 🎯 **OBJECTIVE**

Final refinements to make Core-PLIx v0.1 airtight and implementation-ready:
1. Close remaining semantic gaps
2. Make effect rows & confidence actionable
3. Fully specify retries/fallbacks/compensation
4. Evidence normative completeness
5. Denotation & machine alignment
6. Missing derivations (progress, preservation)
7. Surface grammar micro-fixes
8. Minimal runnable bundle structure

---

## 🔧 **1. CLOSE REMAINING SEMANTIC GAPS**

### **A. Namespaces & Resolution**

**Resolver Definition:**
```
Σ = (Tags: Map<Tag, Entity | Capability | Policy | Value>, 
     Actions: Map<Id, PrimAction>)

resolve_tag : Σ × Tag → Value
resolve_action : Σ × Id → PrimAction
```

**Resolution Side Conditions:**
```
(TAG-RESOLVE)
resolve_tag(Σ, tag) = v

───────────────────────────────────────────────────────────────
Γ, Σ ⊢ tag : Value
```

```
(ACTION-RESOLVE)
resolve_action(Σ, id) = action

───────────────────────────────────────────────────────────────
Γ, Σ ⊢ action(id) : Action
```

### **B. ParamEnv & Expression Layer**

**ParamEnv Definition:**
```
ParamEnv = Map<Name, Value>

Γ ⊢ params : ParamEnv ! {} ▷ 1
Γ ⊢ expr : Bool ! {} ▷ 1
```

**Evaluation:**
```
eval(expr, σ, Σ) : Expression × State × Resolver → Value
```

### **C. Purity Boundary for Constraints**

**Purity Rule:**
```
(PURE-CONSTR)
effects(expr) = ∅

───────────────────────────────────────────────────────────────
Γ ⊢ constraint(expr) : Constraint ! {} ▷ 1
```

**Meaning:** Constraints must be pure/side-effect-free for deterministic replay

### **D. Define `postcheck`**

**Postcheck Definition:**
```
postcheck(σ) ≜ snd⟦contract⟧(σ)
```

**Meaning:** Postcheck is the denotation of the contract's postconditions

### **E. Ready-Set & Bookkeeping Sets**

**Extended Configuration:**
```
C ::= ⟨σ, ε, Q, done, failed⟩

where:
  - σ : State
  - ε : EvLog
  - Q : Set(StepId)  (ready set)
  - done : Set(StepId)  (completed steps)
  - failed : Set(StepId)  (failed steps)
```

**Updated READY Rule:**
```
(READY)
Q = ready(G, done)
done' = done
failed' = failed

───────────────────────────────────────────────────────────────
⟨σ, ε, ∅, done, failed⟩ ⇝ ⟨σ, ε, Q, done', failed'⟩
```

**Updated EXEC-TASK Rule:**
```
(EXEC-TASK)
eval_params(p, σ) = p'
step = task(i, a, p')
run(a, p', σ) ↠ μ over pairs (σ', e, ok)
ok = snd⟦contract⟧(σ')

───────────────────────────────────────────────────────────────────────────
⟨σ, ε, {step}∪Q, done, failed⟩ → ⟨σ', ε⊕e, Q, done∪{i}, failed⟩
  with prob μ(σ', e, ok=true)
```

**Updated FAIL-TASK Rule:**
```
(FAIL-TASK)
eval_params(p, σ) = p'
step = task(i, a, p')
run(a, p', σ) ↠ μ over pairs (σ', e, ok)
ok = false

───────────────────────────────────────────────────────────────────────────
⟨σ, ε, {step}∪Q, done, failed⟩ → ⟨σ', ε⊕e, Q, done, failed∪{i}⟩
  with prob μ(σ', e, ok=false)
```

### **F. Success Criterion in `ExecPlan`**

**Success Definition:**
```
ok ≜ snd⟦contract⟧(σ')
```

**Meaning:** Success only when postconditions hold

---

## 🎯 **2. EFFECT ROWS & CONFIDENCE: ACTIONABLE**

### **A. Effect Subtyping & Weakening**

**Weakening Rule:**
```
(WEAK-EFF)
ε₁ ⊆ ε₂
Γ ⊢ t : T ! ε₁ ▷ φ

───────────────────────────────────────────────────────────────
Γ ⊢ t : T ! ε₂ ▷ φ
```

### **B. Confidence Aggregation on DAGs**

**Path-Sensitive Confidence:**
```
φ_plan ≜ min_{π ∈ Paths(G)}  Π_{s∈π} conf(s)
```

**Fast Lower Bound:**
```
φ_plan ≥ inf_{s ∈ steps} conf(s)
```

### **C. Capability Gating by Effects**

**Capability Check:**
```
cap_ok(a, params) ∧ allowed_effects(context) ⊇ eff(a)

───────────────────────────────────────────────────────────────
task(id, a, params) allowed
```

---

## 🔄 **3. RETRIES, FALLBACKS, COMPENSATION: FULLY SPECIFIED**

### **A. Retry Budget & Idempotence**

**Idempotent Retry:**
```
(RETRY-TO-EXEC)
remaining(i) = k > 0
idempotent(i)

───────────────────────────────────────────────────────────────
may re-enqueue i without extra guards
```

**Non-Idempotent Retry:**
```
(NONIDEMP-RETRY)
remaining(i) = k > 0
¬idempotent(i)

───────────────────────────────────────────────────────────────
must call explicit compensator before retry
```

### **B. Fallback Semantics Precedence**

**Precedence Rule:**
```
retry exhausts before fallback fires, unless fallback_on predicate says otherwise
```

**Example:** HTTP 4xx errors trigger fallback immediately, HTTP 5xx errors retry first

### **C. Compensation Left Inverse (Assumption A1)**

**Assumption A1:**
```
A1: ∀i ∈ compensable.  comp_i ∘ exec_i ≈ id  on i's footprint
```

**Meaning:** Compensation is left-inverse of execution (restores pre-state)

---

## 📋 **4. EVIDENCE: NORMATIVE COMPLETENESS**

### **A. Attach Step IDs and Contract IDs**

**Extended Evidence Node:**
```json
{
  "id": "evidence:uuid",
  "step_id": "reserve",
  "contract_id": "book_room@v1",
  "time": "2025-12-01T10:00:05Z",
  "tool": "calendar.api",
  "input_hash": "sha256:...",
  "output_hash": "sha256:...",
  "parents": ["evidence:parent"],
  "signer": "identity:uuid",
  "sig": "signature:..."
}
```

### **B. Pure Proof Nodes**

**Proof Node:**
```json
{
  "id": "proof:uuid",
  "type": "proof",
  "obligation": "constraint(expr)",
  "result": true,
  "proof_hash": "sha256:...",
  "parents": ["evidence:constraint"]
}
```

**Meaning:** Allows verifier to short-circuit recomputation if cached

### **C. Taint Propagation is Monotone**

**Taint Invariant:**
```
once tainted, descendants remain tainted
```

**Redaction Semantics:**
```
redaction introduces a mask node with reason codes, never deletes history
```

---

## 📊 **5. DENOTATION & MACHINE: ALIGNMENT TABLE**

| Operational          | Denotational                                  |
| -------------------- | --------------------------------------------- |
| `READY` frontier `Q` | support of next-step kernel inside `ExecPlan` |
| `ok`                 | `snd⟦contract⟧(σ')`                           |
| `ε ⊕ e`              | evidence monoid append                        |
| `COMPENSATE`         | branch to `η(σ_pre, ε ⊕ e_comp)`              |
| `done`               | completed steps in `ExecPlan`                 |
| `failed`             | failed steps in `ExecPlan`                    |

---

## ✅ **6. MISSING DERIVATIONS**

### **A. Progress (Sketch over DAG Machine)**

**Progress Theorem:**

Assume `acyclic(G)`, `closed params`, and `resolve` succeeds.

```
If Q = ∅ and postcheck(σ) = true ⇒ terminal success.

If Q = ∅ and post = false and all finished steps have compensators ⇒ COMPENSATE applies.

Else ∃ ready v ∈ ready(G, done): EXEC-TASK or FAIL-TASK applies.
```

**Proof Sketch:**
- If `Q = ∅` and postconditions hold → success (terminal)
- If `Q = ∅` and postconditions fail → compensation applies (by COMPENSATE rule)
- Otherwise → ready set non-empty → execution applies (by READY rule)

### **B. Preservation of Typing/Effects**

**Preservation Theorem:**

Prove by cases on the small-step rules that effects witnessed at runtime are subsets of statically declared rows; compensation steps contribute only `{compensable?}`.

**Proof Sketch:**
- **EXEC-TASK:** Runtime effects ⊆ declared effects (by TASK rule)
- **COMPENSATE:** Only `{compensable?}` effect (by COMPENSATE rule)
- **RETRY/FALLBACK:** No new effects (by RETRY/FALLBACK rules)

---

## 📐 **7. SURFACE GRAMMAR: MICRO-FIXES**

### **A. Scoped Policy and Safety Blocks**

**Updated Intent Grammar:**
```
Intent ::= "intent" ident "{"
             SA Ent Act Contract [Policy] [Safety] Plan
           "}"

Policy ::= "policy" "{" PolicyRule* "}"
Safety ::= "safety" "{" SafetyRule* "}"
```

### **B. Where Clause for Computed Params**

**Updated Task Grammar:**
```
Task ::= "task" ident ":" Action "(" Params? ")" ["where" LetBindings]

LetBindings ::= LetBinding ("," LetBinding)*
LetBinding ::= ident "=" Expr
```

**Meaning:** Keeps tasks pure at parse-time

---

## 📁 **8. MINIMAL RUNNABLE BUNDLE STRUCTURE**

### **Bundle Structure**

```
plix-core-v0.1/
├── plix-core.ebnf              # Updated grammar with Policy/Safety/where
├── semantics.md                # Complete semantics (this document)
├── ref-interpreter/
│   ├── dag_scheduler.rs        # DAG scheduler
│   ├── retry_fallback.rs       # Retry/fallback precedence
│   ├── compensation.rs         # Compensation engine
│   └── effect_checker.rs       # Effect & confidence checker
├── verifier/
│   ├── hash_chain.rs           # Hash chain verification
│   ├── signature.rs            # Signature verification
│   └── constraint_replay.rs    # Pure constraint replay
└── examples/
    └── room/
        ├── meeting_room.cnl    # CNL source
        ├── meeting_room.core.plix  # Core-PLIx
        ├── meeting_room.tla     # TLA+ module
        ├── meeting_room.alloy   # Alloy model
        ├── meeting_room.opa     # OPA policy
        ├── meeting_room.irplan.json  # IRPlan JSON
        ├── evidence_dag.json    # Evidence DAG
        ├── passing_run.json     # Passing execution trace
        └── compensated_run.json # Compensated execution trace
```

---

## 🎯 **NEXT STEPS**

1. ✅ **Semantic Gaps** - Closed ✅
2. ✅ **Effect Rows & Confidence** - Actionable ✅
3. ✅ **Retries/Fallbacks/Compensation** - Fully specified ✅
4. ✅ **Evidence Completeness** - Normative ✅
5. ✅ **Alignment Table** - Complete ✅
6. ✅ **Missing Derivations** - Added ✅
7. ✅ **Surface Grammar** - Fixed ✅
8. ✅ **Bundle Structure** - Defined ✅
9. ⏳ **Implementation** - Create reference interpreter and verifier

---

**Status:** 📋 **CORE SEMANTICS v0.1 FINAL REFINEMENTS COMPLETE**  
**Next:** Create reference interpreter and verifier implementation

