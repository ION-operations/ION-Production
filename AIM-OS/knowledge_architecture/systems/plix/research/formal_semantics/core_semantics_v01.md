# Core-PLIx Semantics v0.1: Refined with ChatGPT Feedback

**Date:** 2025-01-27  
**Status:** 📋 **REFINED**  
**Version:** 0.1.0  
**Based on:** ChatGPT feedback on mathematical rigor and completeness

---

## 🎯 **OBJECTIVE**

Refined core calculus incorporating ChatGPT's feedback:
- Tighter mathematical objects (States, Evidence log as monoid, Process configuration)
- Fixed distribution definition (subdistribution monad)
- Annotated typing judgment (`Γ ⊢ t : T ! ε ▷ φ`)
- Complete operational semantics with configurations
- Two soundness theorems (partial correctness + saga safety)
- Normative Evidence schema

---

## 📐 **MATHEMATICAL OBJECTS (TIGHTENED)**

### **State**

```
State = Var ⇀ Value  (partial map)
```

**Meaning:** Partial function from variables to values

### **Evidence Log (Monoid)**

```
EvLog = List(EvidenceEntry)

EvidenceEntry = (time: Timestamp, tool: ToolId, input_hash: Hash, output_hash: Hash, parent_hash: Hash)

(EvLog, ⊕, ϵ) where:
  - ⊕ : EvLog × EvLog → EvLog  (append, hash-chaining)
  - ϵ : EvLog  (empty log)
```

**Monoid Laws:**
```
ϵ ⊕ ε = ε
ε ⊕ ϵ = ε
(ε₁ ⊕ ε₂) ⊕ ε₃ = ε₁ ⊕ (ε₂ ⊕ ε₃)
```

**Hash-Chaining:**
```
parent_hash(eᵢ) = hash(eᵢ₋₁)  for i > 0
parent_hash(e₀) = null
```

### **Process Configuration**

```
C ::= ⟨σ, ε, Q⟩

where:
  - σ : State  (current state)
  - ε : EvLog  (evidence log)
  - Q : Set(StepId)  (ready set of runnable steps)
```

**Meaning:** Configuration tracks state, evidence, and ready steps

---

## 📊 **DISTRIBUTION (FIXED)**

### **Subdistribution Monad**

```
Dist(X) = { μ : X → [0,1] | μ is finitely supported, ∑_{x∈X} μ(x) ≤ 1 }
```

**Unit (Dirac):**
```
η(x) = λy. if y = x then 1 else 0
```

**Bind:**
```
bind(μ, f)(y) = ∑_{x} μ(x) · f(x)(y)
```

**Monad Laws:**
```
bind(η(x), f) = f(x)
bind(μ, η) = μ
bind(bind(μ, f), g) = bind(μ, λx. bind(f(x), g))
```

---

## 🔍 **KINDS, TYPES, AND EFFECTS**

### **Kinds**

```
Kind ::= ★ | Eff | Conf
```

**Meaning:**
- `★` = Type kind
- `Eff` = Effect kind
- `Conf` = Confidence kind

### **Types (Minimal, Orthogonal)**

```
T ::= Bool | Num | Str | Tag | Entity | Action | Capability
    | Constraint | Test | Evidence | Step | Plan | Contract | Intent
    | State | Unit
```

### **Effect Rows**

```
ε ::= { io?, net?, db?, compensable?, idempotent? }
```

**Effect Subtyping:**
```
ε₁ <: ε₂  if  ε₁ ⊆ ε₂
```

### **Confidence Types**

```
Conf = ([0,1], ⊔, ⊓, 0, 1)

where:
  - ⊔ = max (join)
  - ⊓ = min (meet)
  - 0 = bottom
  - 1 = top
```

### **Annotated Typing Judgment**

```
Γ ⊢ t : T ! ε ▷ φ
```

**Meaning:** In context Γ, term `t` has type `T`, may incur effects `ε`, and ensures minimum confidence `φ`

---

## 📋 **CORE JUDGMENT FORMS**

### **PLAN Rule**

```
(PLAN)
Γ ⊢ step₁ : Step ! ε₁ ▷ φ₁  ...  Γ ⊢ stepₙ : Step ! εₙ ▷ φₙ
acyclic(deps)

───────────────────────────────────────────────────────────────
Γ ⊢ plan(step₁,…,stepₙ) : Plan ! (⋃ᵢ εᵢ) ▷ (infᵢ φᵢ)
```

### **CONTRACT Rule**

```
(CONTRACT)
∀c∈pre. Γ ⊢ c : Constraint ! {} ▷ 1   ∧   ∀c∈post. Γ ⊢ c : Constraint ! {} ▷ 1

───────────────────────────────────────────────────────────────────────────
Γ ⊢ contract(pre,post) : Contract ! {} ▷ 1
```

### **INTENT Rule**

```
(INTENT)
Γ ⊢ sa : SpeechAct
Γ ⊢ ent : EntityClause
Γ ⊢ act : ActionClause
Γ ⊢ contract : Contract ! {} ▷ 1
Γ ⊢ plan : Plan ! ε ▷ φ

───────────────────────────────────────────────────────────────────────────
Γ ⊢ intent(sa, ent, act, contract, plan) : Intent ! ε ▷ φ
```

### **TASK Rule**

```
(TASK)
Γ ⊢ action(id) : Action
Γ ⊢ params : ParamEnv
cap_ok(action, params)

───────────────────────────────────────────────────────────────
Γ ⊢ task(id, action, params) : Step ! {io?} ▷ φ_task
```

### **DEPENDS Rule**

```
(DEPENDS)
Γ ⊢ id1,id2 : StepId

────────────────────────
Γ ⊢ depends(id1,id2) : Step ! {} ▷ 1
```

### **RETRY Rule**

```
(RETRY)
Γ ⊢ id : StepId
n ≥ 0
Γ ⊢ backoff : BackoffSpec

───────────────────────────────────────────────
Γ ⊢ retry(id,n,backoff) : Step ! {} ▷ 1
```

### **COMPENSATE Rule**

```
(COMPENSATE)
Γ ⊢ action : Action
Γ ⊢ params : ParamEnv

───────────────────────────────────────────────────────────────
Γ ⊢ compensate(id,action,params) : Step ! {compensable?} ▷ 1
```

---

## ⚙️ **SMALL-STEP OPERATIONAL SEMANTICS**

### **Configurations**

```
C ::= ⟨σ, ε, Q⟩

where:
  - σ : State
  - ε : EvLog
  - Q : Set(StepId)  (ready set)
```

### **Ready Set Formation**

```
ready(G, S_done) = { v ∈ V | ∀(u→v)∈E. u ∈ S_done } \ S_done
```

**READY Rule:**
```
(READY)
Q = ready(G, done)

───────────────────────────────────────────────
⟨σ, ε, ∅⟩ ⇝ ⟨σ, ε, Q⟩
```

### **Execute Task**

```
(EXEC-TASK)
eval_params(p, σ) = p'
step = task(i, a, p')
run(a, p', σ) ↠ μ over pairs (σ', e, ok)

───────────────────────────────────────────────────────────────────────────
⟨σ, ε, {step}∪Q⟩ → ⟨σ', ε⊕e, Q⟩   with prob μ(σ', e, ok=true)
```

**FAIL-TASK Rule:**
```
(FAIL-TASK)
eval_params(p, σ) = p'
step = task(i, a, p')
run(a, p', σ) ↠ μ over pairs (σ', e, ok)

───────────────────────────────────────────────────────────────────────────
⟨σ, ε, {step}∪Q⟩ → ⟨σ', ε⊕e, Q⟩   with prob μ(σ', e, ok=false)
```

### **Retry & Backoff**

```
(RETRY-FAIL)
remaining(step) = k > 0
failure(step)

───────────────────────────────────────────────────────────────
⟨σ, ε, Q⟩ → ⟨σ, ε, Q ∪ {backoff(step, k-1)}⟩
```

### **Fallback**

```
(FALLBACK)
failure(id1)
fallback(id1, id2)
deps(id2) ⊆ done

───────────────────────────────────────────────────────────────
⟨σ, ε, Q⟩ → ⟨σ, ε, Q ∪ {id2}⟩
```

### **Compensation**

```
(COMPENSATE)
postcheck(σ) = false

───────────────────────────────────────────────────────────────
⟨σ, ε, ∅⟩ ⇝* ⟨σ₀, ε⊕e_comp, ∅⟩
```

**Meaning:** `⇝*` executes compensation plan in reverse topological order

---

## 🎯 **DENOTATIONAL SEMANTICS (CLEAN, COMPOSITIONAL)**

### **Contracts**

```
⟦pre⟧, ⟦post⟧ : State → Bool

⟦contract(pre,post)⟧ = (λσ. ∀c∈pre. ⟦c⟧σ,  λσ. ∀c∈post. ⟦c⟧σ)
```

### **Plans (Subdistributions)**

```
ExecPlan : Plan → State×EvLog → Dist(State×EvLog×Bool)

⟦plan⟧ : Plan → State×EvLog → Dist(State×EvLog)

⟦plan⟧ p (σ,ε) = bind(ExecPlan p (σ,ε), λ(σ',ε',ok).
                      if ok then η(σ',ε') else 0)
```

### **Intents**

```
⟦intent(sa, ent, act, contract, plan)⟧(σ,ε) =
  if fst⟦contract⟧(σ) then
     bind(⟦plan⟧ plan (σ,ε), λ(σ',ε').
        if snd⟦contract⟧(σ') then η(σ',ε') else η(σ, ε ⊕ mark_compensation))
  else 0
```

### **Confidence Aggregation**

- Each primitive action `a` supplies `conf(a,p,σ) ∈ [0,1]`
- For plan DAG: `φ_plan = inf_{steps s} conf(s)`
- Type system ensures `φ_plan ≥ φ_required`

---

## ✅ **SOUNDNESS (TWO FLAVORS)**

### **A. Partial Correctness (Classic)**

**Theorem (Partial Correctness):**

If `Γ ⊢ intent : Intent ! ε ▷ φ` and `⟦intent⟧(σ,ε₀)` yields `(σ',ε₁)`, then:

```
fst⟦contract⟧(σ) = true  ⇒  snd⟦contract⟧(σ') = true
```

**Proof Sketch:** By definition of `⟦intent⟧`, success branch only returns `(σ',ε₁)` when post holds.

### **B. Failure Safety with Compensation (Saga Safety)**

**Execution Relation:**
```
Exec ⊢ (σ,ε₀) ⇓ (σ',ε₁, r)

where r ∈ {success, compensated, aborted}
```

**Theorem (Saga Safety):**

Assume each compensable step has a left-inverse compensator and compensations run in reverse topological order. Then for any run with `r = compensated`:

```
fst⟦contract⟧(σ) = true  ⇒  σ' = σ   ∧   ε₁ = ε₀ ⊕ e_comp
```

**Meaning:** Failed runs restore pre-state (up to logged compensation evidence)

### **C. Type Soundness (Progress/Preservation)**

**Preservation:**
```
If Γ ⊢ C : ok and C → C' then Γ ⊢ C' : ok
```

**Progress:**
```
If Γ ⊢ C : ok then C is either terminal (no ready steps and post holds or compensation complete) or ∃C'. C → C'
```

---

## 📋 **EVIDENCE SCHEMA (NORMATIVE)**

### **Node Format**

```
EvidenceNode = {
  id: NodeId,
  time: Timestamp,
  tool: ToolId,
  input_hash: Hash,
  output_hash: Hash,
  parents: [NodeId],
  signer: SignerId,
  sig: Signature
}
```

### **Invariant**

Hash-chain forms a DAG: `parents ⊆ prior ids`

### **Verifier Algorithm**

1. Re-executes pure constraints
2. Checks hash equality
3. Checks signatures
4. Returns PASS iff every postcondition node is supported by reachable evidence nodes

---

## 📐 **MINIMAL EBNF (CORE-PLIX SURFACE)**

```
Plan      ::= "plan" "{" Step* "}"
Step      ::= Task | Depends | Retry | Fallback | Comp

Task      ::= "task" ident ":" Action "(" Params? ")"
Depends   ::= "depends" ident "<-" ident
Retry     ::= "retry" ident "," Nat "," Backoff
Fallback  ::= "fallback" ident "->" ident
Comp      ::= "compensate" ident "->" Action "(" Params? ")"

Contract  ::= "contract" "{" "requires" Constr*  "ensures" Constr* "}"
Intent    ::= "intent" ident "{" SA Ent Act Contract Plan "}"
```

---

## 🎯 **NEXT STEPS**

1. ✅ **Mathematical Objects** - Tightened ✅
2. ✅ **Distribution** - Fixed (subdistribution monad) ✅
3. ✅ **Annotated Typing** - Added ✅
4. ✅ **Operational Semantics** - Complete ✅
5. ✅ **Denotational Semantics** - Clean, compositional ✅
6. ✅ **Soundness** - Two flavors ✅
7. ✅ **Evidence Schema** - Normative ✅
8. ✅ **EBNF** - Minimal surface syntax ✅
9. ⏳ **Implementation** - Reference interpreter, verifier, examples

---

**Status:** 📋 **CORE SEMANTICS v0.1 COMPLETE**  
**Next:** Create reference interpreter and verifier

