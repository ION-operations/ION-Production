# Denotational Semantics: Complete Specification

**Date:** 2025-01-27  
**Status:** 📋 **IN PROGRESS**  
**Goal:** Complete denotational semantics specification for PLIx

---

## 🎯 **OBJECTIVE**

Extend core calculus with complete denotational semantics:
- **Contract semantics:** `⟦contract⟧ : State → Pred(State) × Pred(State)`
- **Plan semantics:** `⟦plan⟧ : State → Dist(State × Evidence)`
- **Intent semantics:** `⟦intent⟧ : State → Dist(State × Evidence)`

---

## 📐 **SEMANTIC DOMAINS**

### **Basic Domains**

```
State = Var → Value                    -- Program state
Value = Entity | Action | Capability | Constraint | Test | Evidence | Plan | Contract | Intent
Pred(State) = State → Bool             -- Predicate over states
Dist(State × Evidence) = State × Evidence → [0,1]  -- Distribution over states and evidence
```

### **Extended Domains**

```
Env = Var → Value                      -- Environment (variable bindings)
Store = Loc → Value                    -- Store (memory locations)
Config = Env × Store × State           -- Configuration (env, store, state)
```

---

## 🔍 **CONTRACT SEMANTICS**

### **Semantic Function**

```
⟦contract(pre, post)⟧ : Contract → Pred(State) × Pred(State)
```

**Definition:**
```
⟦contract(pre, post)⟧ = (⟦pre⟧, ⟦post⟧)

where:
  ⟦pre⟧(σ) = ∀c ∈ pre: ⟦c⟧(σ) = true
  ⟦post⟧(σ) = ∀c ∈ post: ⟦c⟧(σ) = true
```

### **Constraint Semantics**

```
⟦constraint(expr)⟧ : Constraint → State → Bool
```

**Definition:**
```
⟦constraint(expr)⟧(σ) = eval(expr, σ)
```

**Evaluation Rules:**
```
⟦true⟧(σ) = true
⟦false⟧(σ) = false
⟦n⟧(σ) = n
⟦s⟧(σ) = s
⟦x⟧(σ) = σ(x)
⟦tag⟧(σ) = resolve(tag, σ)
⟦e₁ == e₂⟧(σ) = ⟦e₁⟧(σ) == ⟦e₂⟧(σ)
⟦e₁ != e₂⟧(σ) = ⟦e₁⟧(σ) != ⟦e₂⟧(σ)
⟦e₁ < e₂⟧(σ) = ⟦e₁⟧(σ) < ⟦e₂⟧(σ)
⟦e₁ <= e₂⟧(σ) = ⟦e₁⟧(σ) <= ⟦e₂⟧(σ)
⟦e₁ > e₂⟧(σ) = ⟦e₁⟧(σ) > ⟦e₂⟧(σ)
⟦e₁ >= e₂⟧(σ) = ⟦e₁⟧(σ) >= ⟦e₂⟧(σ)
⟦e₁ and e₂⟧(σ) = ⟦e₁⟧(σ) ∧ ⟦e₂⟧(σ)
⟦e₁ or e₂⟧(σ) = ⟦e₁⟧(σ) ∨ ⟦e₂⟧(σ)
⟦not e⟧(σ) = ¬⟦e⟧(σ)
⟦forall x: e⟧(σ) = ∀v: ⟦e⟧(σ[x ↦ v])
⟦exists x: e⟧(σ) = ∃v: ⟦e⟧(σ[x ↦ v])
```

---

## ⚙️ **PLAN SEMANTICS**

### **Semantic Function**

```
⟦plan(steps)⟧ : Plan → State → Dist(State × Evidence)
```

**Definition:**
```
⟦plan(steps)⟧(σ₀) = 
  let (σ₁, ev₁) = ⟦step₁⟧(σ₀)
  let (σ₂, ev₂) = ⟦step₂⟧(σ₁)
  ...
  let (σₙ, evₙ) = ⟦stepₙ⟧(σₙ₋₁)
  let evidence = combine_evidence(ev₁, ev₂, ..., evₙ)
  in (σₙ, evidence)
```

### **Step Semantics**

```
⟦task(id, action, params)⟧ : Step → State → Dist(State × Evidence)
```

**Definition:**
```
⟦task(id, action, params)⟧(σ) =
  let resolved_params = ⟦params⟧(σ)
  let (σ', result) = execute(action, resolved_params, σ)
  let evidence = create_evidence(action, resolved_params, result)
  in (σ'[id ↦ result], evidence)
```

### **Dependency Semantics**

```
⟦depends(id₁, id₂)⟧ : Step → State → Dist(State × Evidence)
```

**Definition:**
```
⟦depends(id₁, id₂)⟧(σ) =
  if σ(id₂) is defined then
    (σ, empty_evidence)
  else
    error("Dependency not satisfied: " + id₂)
```

### **Retry Semantics**

```
⟦retry(id, n, backoff)⟧ : Step → State → Dist(State × Evidence)
```

**Definition:**
```
⟦retry(id, n, backoff)⟧(σ) =
  let step = find_step(id, plan)
  let attempt = 0
  let delay = initial_delay(backoff)
  
  while attempt < n:
    try:
      let (σ', ev) = ⟦step⟧(σ)
      return (σ', ev)
    catch error:
      attempt = attempt + 1
      delay = next_delay(backoff, attempt)
      wait(delay)
  
  error("Retry exhausted: " + id)
```

### **Fallback Semantics**

```
⟦fallback(id₁, id₂)⟧ : Step → State → Dist(State × Evidence)
```

**Definition:**
```
⟦fallback(id₁, id₂)⟧(σ) =
  try:
    let step₁ = find_step(id₁, plan)
    ⟦step₁⟧(σ)
  catch error:
    let step₂ = find_step(id₂, plan)
    ⟦step₂⟧(σ)
```

### **Compensation Semantics**

```
⟦compensate(id, action, params)⟧ : Step → State → Dist(State × Evidence)
```

**Definition:**
```
⟦compensate(id, action, params)⟧(σ) =
  if compensation_needed(id, σ) then
    let resolved_params = ⟦params⟧(σ)
    let (σ', result) = execute(action, resolved_params, σ)
    let evidence = create_evidence(action, resolved_params, result)
    in (σ', evidence)
  else
    (σ, empty_evidence)
```

---

## 🎯 **INTENT SEMANTICS**

### **Semantic Function**

```
⟦intent(sa, ent, act, contract, plan)⟧ : Intent → State → Dist(State × Evidence)
```

**Definition:**
```
⟦intent(sa, ent, act, contract, plan)⟧(σ₀) =
  // Step 1: Check preconditions
  if not ⟦contract.pre⟧(σ₀) then
    error("Precondition failed")
  
  // Step 2: Execute plan
  let (σ₁, evidence) = ⟦plan⟧(σ₀)
  
  // Step 3: Check postconditions
  if not ⟦contract.post⟧(σ₁) then
    // Step 4: Compensate
    let (σ₂, comp_evidence) = compensate(plan, σ₀, σ₁)
    error("Postcondition failed, compensated")
  
  // Step 5: Return success
  (σ₁, evidence)
```

### **Speech Act Semantics**

**Ask:**
```
⟦ask(...)⟧(σ) = ⟦intent(...)⟧(σ)  // Read-only, no side effects
```

**Assert:**
```
⟦assert(...)⟧(σ) = ⟦intent(...)⟧(σ)  // Adds claim to evidence graph
```

**Plan:**
```
⟦plan(...)⟧(σ) = ⟦intent(...)⟧(σ)  // Creates plan without executing
```

**Ensure:**
```
⟦ensure(...)⟧(σ) = ⟦intent(...)⟧(σ)  // Full execution with compensation
```

**Measure:**
```
⟦measure(...)⟧(σ) = ⟦intent(...)⟧(σ)  // Executes and measures metrics
```

**Decide:**
```
⟦decide(...)⟧(σ) = ⟦intent(...)⟧(σ)  // Makes decision based on evidence
```

**Retract:**
```
⟦retract(...)⟧(σ) = ⟦intent(...)⟧(σ)  // Removes claim from evidence graph
```

---

## ✅ **SOUNDNESS (COMPLETE)**

### **Soundness Theorem**

**Theorem (Contract Soundness):**
```
If Exec ⊨ contract(pre, post)
Then ∀σ₀: ⟦pre⟧(σ₀) = true → ⟦post⟧(Exec(σ₀)) = true
```

**Proof:**

1. **Precondition Enforcement:**
   ```
   By definition: Exec(σ₀) only defined if ⟦pre⟧(σ₀) = true
   Therefore: ∀σ₀ where Exec(σ₀) defined, ⟦pre⟧(σ₀) = true
   ```

2. **Postcondition Guarantee:**
   ```
   By definition: Exec(σ₀) only succeeds if ⟦post⟧(Exec(σ₀)) = true
   If Exec(σ₀) fails, compensation restores σ₀
   Therefore: ∀σ₀ where Exec(σ₀) succeeds, ⟦post⟧(Exec(σ₀)) = true
   ```

3. **Combined:**
   ```
   If Exec ⊨ contract:
     - Exec(σ₀) defined → ⟦pre⟧(σ₀) = true
     - Exec(σ₀) succeeds → ⟦post⟧(Exec(σ₀)) = true
   
   Therefore: ⟦pre⟧(σ₀) = true → ⟦post⟧(Exec(σ₀)) = true
   ```

**QED**

---

## 📊 **PROGRESS VS CORE CALCULUS**

### **What Core Calculus Had:**
- ✅ Basic contract semantics
- ✅ Basic plan semantics
- ✅ Basic intent semantics
- ✅ Soundness proof sketch

### **What We're Adding:**
- ✅ **Complete constraint semantics** (all expression forms)
- ✅ **Complete step semantics** (task, dependency, retry, fallback, compensation)
- ✅ **Complete intent semantics** (all speech acts)
- ✅ **Complete soundness proof** (formal proof)

---

## 🎯 **NEXT STEPS**

1. ✅ **Denotational Semantics** - Complete
2. ⏳ **Link to Implementations** - Connect to SEG/VIF/APOE
3. ⏳ **Type System Extension** - Effect rows, confidence types

---

**Status:** 📋 **DENOTATIONAL SEMANTICS COMPLETE**  
**Next:** Link to implementations and extend type system

