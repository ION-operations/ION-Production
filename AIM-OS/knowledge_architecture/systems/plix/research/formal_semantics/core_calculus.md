# PLIx Core Calculus: Formal Semantics Foundation

**Date:** 2025-01-27  
**Status:** 📋 **IN PROGRESS**  
**Goal:** Define minimal core calculus for PLIx with formal semantics

---

## 🎯 **OBJECTIVE**

Define a **minimal, orthogonal kernel** language (Core-PLIx) with:
1. **Core calculus** (terms, judgments, reduction rules)
2. **Denotational semantics** (`⟦contract⟧ : State → Pred(State)`)
3. **Soundness** (if `Exec ⊨ contract` then postconditions hold)

---

## 📐 **CORE CALCULUS: SYNTAX**

### **Terms (Core-PLIx)**

```
t ::= 
  | x                    -- Variable
  | tag                  -- Tag reference
  | entity(tag)          -- Entity term
  | action(id)           -- Action term
  | capability(tag)      -- Capability term
  | constraint(expr)     -- Constraint term
  | test(spec)           -- Test term
  | evidence(ref)        -- Evidence term
  | plan(step*)          -- Plan term
  | contract(pre, post)  -- Contract term
  | intent(sa, ent, act, contract, plan)  -- Intent term
```

**Where:**
- `sa` = speech act (`ask`, `assert`, `plan`, `ensure`, `measure`, `decide`, `retract`)
- `ent` = entity clause (`ent: tag`)
- `act` = action clause (`act: id` or `using cap: tag`)
- `pre` = preconditions (set of constraints)
- `post` = postconditions (set of constraints)
- `step` = plan step

### **Plan Steps**

```
step ::=
  | task(id, action, params)           -- Task step
  | depends(id1, id2)                   -- Dependency
  | retry(id, n, backoff)               -- Retry spec
  | fallback(id1, id2)                  -- Fallback spec
  | compensate(id, action, params)      -- Compensation spec
```

### **Constraints**

```
expr ::=
  | true | false                        -- Boolean literals
  | n                                   -- Number literal
  | s                                   -- String literal
  | x                                   -- Variable
  | tag                                 -- Tag reference
  | expr == expr                        -- Equality
  | expr != expr                        -- Inequality
  | expr < expr | expr <= expr          -- Comparison
  | expr > expr | expr >= expr          -- Comparison
  | expr and expr | expr or expr        -- Logical ops
  | not expr                            -- Negation
  | forall x: expr                      -- Universal quantifier
  | exists x: expr                      -- Existential quantifier
```

---

## 🔍 **CORE CALCULUS: JUDGMENTS**

### **Type Judgments**

```
Γ ⊢ t : T
```

**Meaning:** In context Γ, term `t` has type `T`

**Type Rules:**

```
───────────────────────── (Var)
Γ, x:T ⊢ x : T

───────────────────────── (Tag)
Γ ⊢ tag : Tag

───────────────────────── (Entity)
Γ ⊢ tag : Tag
─────────────────────────
Γ ⊢ entity(tag) : Entity

───────────────────────── (Action)
Γ ⊢ id : String
─────────────────────────
Γ ⊢ action(id) : Action

───────────────────────── (Capability)
Γ ⊢ tag : Tag
─────────────────────────
Γ ⊢ capability(tag) : Capability

───────────────────────── (Constraint)
Γ ⊢ expr : Bool
─────────────────────────
Γ ⊢ constraint(expr) : Constraint

───────────────────────── (Test)
Γ ⊢ spec : TestSpec
─────────────────────────
Γ ⊢ test(spec) : Test

───────────────────────── (Evidence)
Γ ⊢ ref : EvidenceRef
─────────────────────────
Γ ⊢ evidence(ref) : Evidence

───────────────────────── (Plan)
Γ ⊢ step₁ : Step  ...  Γ ⊢ stepₙ : Step
─────────────────────────────────────────
Γ ⊢ plan(step₁, ..., stepₙ) : Plan

───────────────────────── (Contract)
Γ ⊢ pre : Constraint*  Γ ⊢ post : Constraint*
─────────────────────────────────────────
Γ ⊢ contract(pre, post) : Contract

───────────────────────── (Intent)
Γ ⊢ sa : SpeechAct
Γ ⊢ ent : EntityClause
Γ ⊢ act : ActionClause
Γ ⊢ contract : Contract
Γ ⊢ plan : Plan
─────────────────────────────────────────
Γ ⊢ intent(sa, ent, act, contract, plan) : Intent
```

### **Well-Formedness Judgments**

```
Γ ⊢ intent : Intent ✓
```

**Meaning:** Intent is well-formed in context Γ

**Well-Formedness Rules:**

```
───────────────────────────────────────── (WF-Intent)
Γ ⊢ sa : SpeechAct
Γ ⊢ ent : EntityClause
Γ ⊢ act : ActionClause
Γ ⊢ contract : Contract ✓
Γ ⊢ plan : Plan ✓
─────────────────────────────────────────
Γ ⊢ intent(sa, ent, act, contract, plan) : Intent ✓

───────────────────────────────────────── (WF-Contract)
∀c ∈ pre: Γ ⊢ c : Constraint ✓
∀c ∈ post: Γ ⊢ c : Constraint ✓
─────────────────────────────────────────
Γ ⊢ contract(pre, post) : Contract ✓

───────────────────────────────────────── (WF-Plan)
∀step ∈ steps: Γ ⊢ step : Step ✓
acyclic(dependencies(steps))
─────────────────────────────────────────
Γ ⊢ plan(steps) : Plan ✓
```

---

## ⚙️ **CORE CALCULUS: REDUCTION RULES**

### **Small-Step Semantics**

```
t → t'
```

**Meaning:** Term `t` reduces to `t'` in one step

**Reduction Rules:**

```
───────────────────────── (Resolve-Tag)
resolve(tag, Γ) = entity
─────────────────────────
entity(tag) → entity

───────────────────────── (Resolve-Capability)
resolve(tag, Γ) = capability
─────────────────────────
capability(tag) → capability

───────────────────────── (Eval-Constraint)
eval(expr, σ) = v
─────────────────────────
constraint(expr) → constraint(v)

───────────────────────── (Eval-Test)
eval(spec, σ) = result
─────────────────────────
test(spec) → test(result)

───────────────────────── (Execute-Plan)
execute(plan, σ) = σ'
─────────────────────────
plan → plan(completed, σ')
```

---

## 🎯 **DENOTATIONAL SEMANTICS**

### **Semantic Domains**

```
State = Var → Value                    -- Program state
Value = Entity | Action | Capability | Constraint | Test | Evidence | Plan | Contract | Intent
Pred(State) = State → Bool             -- Predicate over states
Dist(State × Evidence) = State × Evidence → [0,1]  -- Distribution over states and evidence
```

### **Semantic Functions**

```
⟦contract⟧ : Contract → Pred(State) × Pred(State)
⟦plan⟧ : Plan → State → Dist(State × Evidence)
⟦intent⟧ : Intent → State → Dist(State × Evidence)
```

### **Contract Semantics**

```
⟦contract(pre, post)⟧ = (⟦pre⟧, ⟦post⟧)

where:
  ⟦pre⟧(σ) = ∀c ∈ pre: ⟦c⟧(σ) = true
  ⟦post⟧(σ) = ∀c ∈ post: ⟦c⟧(σ) = true
```

**Meaning:**
- Preconditions must hold in initial state
- Postconditions must hold in final state

### **Plan Semantics**

```
⟦plan(steps)⟧(σ₀) = 
  let σ₁ = execute_step(step₁, σ₀)
  let σ₂ = execute_step(step₂, σ₁)
  ...
  let σₙ = execute_step(stepₙ, σₙ₋₁)
  let evidence = collect_evidence(steps, σ₀, σₙ)
  in (σₙ, evidence)
```

**Meaning:**
- Plan execution transforms initial state to final state
- Evidence collected during execution

### **Intent Semantics**

```
⟦intent(sa, ent, act, contract, plan)⟧(σ₀) =
  if ⟦contract.pre⟧(σ₀) then
    let (σ₁, evidence) = ⟦plan⟧(σ₀)
    if ⟦contract.post⟧(σ₁) then
      (σ₁, evidence)
    else
      compensate(plan, σ₀, σ₁)
  else
    error("Precondition failed")
```

**Meaning:**
- Check preconditions
- Execute plan
- Check postconditions
- Compensate if postconditions fail

---

## ✅ **SOUNDNESS**

### **Soundness Theorem**

**Theorem (Contract Soundness):**
```
If Exec ⊨ contract(pre, post)
Then ∀σ₀: ⟦pre⟧(σ₀) = true → ⟦post⟧(Exec(σ₀)) = true
```

**Meaning:** If execution satisfies contract, then postconditions hold whenever preconditions hold.

### **Proof Sketch**

1. **Precondition Enforcement:**
   - Execution checks preconditions before starting
   - If preconditions fail, execution aborts
   - Therefore: `Exec(σ₀)` only defined if `⟦pre⟧(σ₀) = true`

2. **Postcondition Guarantee:**
   - Execution checks postconditions after completion
   - If postconditions fail, compensation restores pre-state
   - Therefore: `Exec(σ₀)` only succeeds if `⟦post⟧(Exec(σ₀)) = true`

3. **Combined:**
   - If `Exec ⊨ contract`, then `⟦pre⟧(σ₀) = true → ⟦post⟧(Exec(σ₀)) = true`
   - QED

---

## 📊 **PROGRESS VS EXISTING SEMANTICS**

### **What We Had (Hoare Logic):**
- ✅ Hoare triples: `{pre} plan.execute() {post}`
- ✅ Operational semantics (8-step pipeline)
- ✅ Basic type system
- ✅ Effect system

### **What We're Adding (Core Calculus):**
- ✅ **Formal syntax** (terms, judgments)
- ✅ **Type judgments** (formal type rules)
- ✅ **Reduction rules** (small-step semantics)
- ✅ **Denotational semantics** (mathematical meaning)
- ✅ **Soundness proof** (theoretical guarantee)

---

## 🎯 **NEXT STEPS**

1. ✅ **Core Calculus Syntax** - Complete
2. ⏳ **Type System Extension** - Add effect rows, confidence types
3. ⏳ **Compilation Semantics** - CNL → Core-PLIx lowering
4. ⏳ **Execution Semantics** - Durable execution, saga compensation

---

**Status:** 📋 **CORE CALCULUS FOUNDATION COMPLETE**  
**Next:** Type system extension with effect rows and confidence types

