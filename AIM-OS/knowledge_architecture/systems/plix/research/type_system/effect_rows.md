# Type System: Effect Rows and Confidence Types

**Date:** 2025-01-27  
**Status:** 📋 **IN PROGRESS**  
**Goal:** Extend type system with effect rows and confidence types

---

## 🎯 **OBJECTIVE**

Extend PLIx type system with:
1. **Effect rows** (idempotent, compensable, external-io, data-mutation)
2. **Confidence types** (`Conf p ∈ [0,1]` with lattice joins)
3. **Policy types** (first-class policy types)

---

## 📐 **EFFECT ROWS**

### **Effect Types**

```
Effect = Idempotent | Compensable | ExternalIO | DataMutation | Read | Write | Execute | Witness
```

**Effect Definitions:**
- **Idempotent:** Can be safely retried (no side effects on retry)
- **Compensable:** Has compensation action (can be rolled back)
- **ExternalIO:** Performs external I/O (network, file system)
- **DataMutation:** Mutates data (database writes, state changes)
- **Read:** Read-only access (no mutations)
- **Write:** Write access (mutations)
- **Execute:** Execution capability (runs actions)
- **Witness:** Evidence generation (creates witnesses)

### **Effect Rows**

```
EffectRow = {Effect*}
```

**Example:**
```
{Idempotent, Compensable, ExternalIO}
```

### **Effect Subtyping**

```
Effect₁ <: Effect₂  if  Effect₁ is more restrictive than Effect₂
```

**Subtyping Rules:**
```
Read <: Idempotent
Write <: DataMutation
Compensable <: DataMutation
ExternalIO <: DataMutation
```

### **Effect Row Subtyping**

```
Row₁ <: Row₂  if  ∀e ∈ Row₂: ∃e' ∈ Row₁ such that e' <: e
```

**Example:**
```
{Read} <: {Idempotent}
{Write, Compensable} <: {DataMutation}
```

---

## 🎯 **CONFIDENCE TYPES**

### **Confidence Type**

```
Conf p ∈ [0,1]
```

**Meaning:** Confidence value `p` in range [0,1]

### **Confidence Lattice**

**Join (Maximum):**
```
p₁ ⊔ p₂ = max(p₁, p₂)
```

**Meet (Minimum):**
```
p₁ ⊓ p₂ = min(p₁, p₂)
```

**Top Element:**
```
⊤ = 1.0
```

**Bottom Element:**
```
⊥ = 0.0
```

### **Confidence Propagation**

**Through Supports:**
```
conf(claim) = max({conf(source) | source supports claim})
```

**Through Derives:**
```
conf(derived) = min(conf(input), conf(derivation_method))
```

**Through And:**
```
conf(c₁ and c₂) = min(conf(c₁), conf(c₂))
```

**Through Or:**
```
conf(c₁ or c₂) = max(conf(c₁), conf(c₂))
```

### **Confidence Type Rules**

**Confidence Annotation:**
```
───────────────────────── (Conf-Annot)
Γ ⊢ e : T
─────────────────────────
Γ ⊢ e : T @ Conf p
```

**Confidence Requirement:**
```
───────────────────────── (Conf-Req)
Γ ⊢ e : T @ Conf p
p >= threshold
─────────────────────────
Γ ⊢ e : T @ Conf p ✓
```

---

## 📋 **POLICY TYPES**

### **Policy Type**

```
Policy = Constraint → Bool
```

**Meaning:** Policy is a function from constraints to boolean (allows/denies)

### **Policy Composition**

**And Policy:**
```
policy₁ and policy₂ = λc. policy₁(c) ∧ policy₂(c)
```

**Or Policy:**
```
policy₁ or policy₂ = λc. policy₁(c) ∨ policy₂(c)
```

**Not Policy:**
```
not policy = λc. ¬policy(c)
```

### **Policy Type Rules**

**Policy Annotation:**
```
───────────────────────── (Policy-Annot)
Γ ⊢ e : T
─────────────────────────
Γ ⊢ e : T @ Policy p
```

**Policy Check:**
```
───────────────────────── (Policy-Check)
Γ ⊢ e : T @ Policy p
p(constraint) = true
─────────────────────────
Γ ⊢ e : T @ Policy p ✓
```

---

## 🔍 **EXTENDED TYPE SYSTEM**

### **Type Judgments (Extended)**

```
Γ ⊢ t : T @ Effects @ Conf @ Policy
```

**Meaning:** In context Γ, term `t` has type `T` with effects `Effects`, confidence `Conf`, and policy `Policy`

### **Type Rules (Extended)**

**Task with Effects:**
```
───────────────────────────────────────── (Task-Effects)
Γ ⊢ action : Action
Γ ⊢ params : Params
effects(action) = {e₁, ..., eₙ}
─────────────────────────────────────────
Γ ⊢ task(id, action, params) : Task @ {e₁, ..., eₙ}
```

**Task with Confidence:**
```
───────────────────────────────────────── (Task-Conf)
Γ ⊢ task : Task
conf(action) = p
─────────────────────────────────────────
Γ ⊢ task : Task @ Conf p
```

**Task with Policy:**
```
───────────────────────────────────────── (Task-Policy)
Γ ⊢ task : Task
policy(action) = p
─────────────────────────────────────────
Γ ⊢ task : Task @ Policy p
```

**Complete Task:**
```
───────────────────────────────────────── (Task-Complete)
Γ ⊢ task : Task @ {Idempotent, Compensable} @ Conf 0.95 @ Policy allow_read
─────────────────────────────────────────
Γ ⊢ task : Task @ {Idempotent, Compensable} @ Conf 0.95 @ Policy allow_read ✓
```

---

## 📊 **EFFECT INFERENCE**

### **Effect Inference Rules**

**From Action:**
```
effects(action) = infer_effects(action_signature)
```

**From Plan:**
```
effects(plan) = ∪{effects(step) | step ∈ plan}
```

**From Intent:**
```
effects(intent) = effects(intent.plan)
```

### **Effect Checking**

**Idempotent Check:**
```
is_idempotent(action) = 
  action.has_retry_spec ∧
  action.has_fallback_spec
```

**Compensable Check:**
```
is_compensable(action) = 
  action.has_compensation_spec
```

**ExternalIO Check:**
```
is_external_io(action) = 
  action.calls_external_api ∨
  action.reads_file ∨
  action.writes_file
```

**DataMutation Check:**
```
is_data_mutation(action) = 
  action.writes_database ∨
  action.modifies_state
```

---

## 🎯 **CONFIDENCE INFERENCE**

### **Confidence Inference Rules**

**From Source:**
```
conf(source) = source.authority_tier.confidence
```

**From Derivation:**
```
conf(derived) = min(conf(input), conf(method))
```

**From Plan:**
```
conf(plan) = min({conf(step) | step ∈ plan})
```

**From Intent:**
```
conf(intent) = min(conf(contract), conf(plan))
```

### **Confidence Propagation**

**Through Supports:**
```
conf(claim) = max({conf(source) | source supports claim})
```

**Through Derives:**
```
conf(derived) = conf(derivation) × conf(input)
```

**Through And:**
```
conf(c₁ and c₂) = min(conf(c₁), conf(c₂))
```

**Through Or:**
```
conf(c₁ or c₂) = max(conf(c₁), conf(c₂))
```

---

## 📋 **POLICY INFERENCE**

### **Policy Inference Rules**

**From Action:**
```
policy(action) = infer_policy(action_signature)
```

**From Plan:**
```
policy(plan) = ∩{policy(step) | step ∈ plan}
```

**From Intent:**
```
policy(intent) = policy(intent.contract) ∩ policy(intent.plan)
```

### **Policy Checking**

**Allow Check:**
```
allow(action, constraint) = policy(action)(constraint)
```

**Deny Check:**
```
deny(action, constraint) = ¬policy(action)(constraint)
```

---

## 🎯 **NEXT STEPS**

1. ✅ **Effect Rows** - Complete
2. ✅ **Confidence Types** - Complete
3. ✅ **Policy Types** - Complete
4. ⏳ **Integration** - Link to type checker implementation

---

**Status:** 📋 **TYPE SYSTEM EXTENSION COMPLETE**  
**Next:** Integration with type checker

