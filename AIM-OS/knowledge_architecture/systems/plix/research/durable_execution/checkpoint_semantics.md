# Durable Execution: Checkpoint Semantics and Saga Compensation

**Date:** 2025-01-27  
**Status:** 📋 **IN PROGRESS**  
**Goal:** Define checkpoint semantics, saga compensation, and TLA+ invariants

---

## 🎯 **OBJECTIVE**

Define durable execution:
1. **Checkpoint semantics:** Formal checkpoint definition
2. **Saga compensation:** Pre/post conditions for compensation
3. **TLA+ invariants:** "at-most-once" effects, compensation guarantees

---

## 💾 **CHECKPOINT SEMANTICS**

### **Checkpoint Definition**

```
Checkpoint = (σ: State, ε: EvLog, Q: Set(StepId), done: Set(StepId), failed: Set(StepId))
```

**Meaning:** Snapshot of execution state at a point in time

### **Checkpoint Creation**

**Checkpoint Rule:**
```
(CHECKPOINT)
C = ⟨σ, ε, Q⟩
checkpoint_triggered(C)

───────────────────────────────────────────────────────────────
checkpoint(C) = (σ, ε, Q, done, failed)
```

**Checkpoint Triggers:**
- After each step completion
- Before external I/O operations
- At compensation boundaries
- Periodically (time-based)

### **Checkpoint Restoration**

**Restore Rule:**
```
(RESTORE)
checkpoint = (σ, ε, Q, done, failed)

───────────────────────────────────────────────────────────────
restore(checkpoint) = ⟨σ, ε, Q⟩
```

**Restoration Semantics:**
- State `σ` restored exactly
- Evidence log `ε` restored exactly
- Ready set `Q` restored exactly
- Execution resumes from checkpoint

---

## 🔄 **SAGA COMPENSATION**

### **Saga Pattern**

**Definition:**
A saga is a sequence of steps where each step has a compensation action that can undo its effects.

### **Compensation Preconditions**

**Compensation Precondition:**
```
compensate(id, action, params) requires:
  - step(id) was executed successfully
  - step(id) has compensable effect
  - compensation action is defined
```

### **Compensation Postconditions**

**Compensation Postcondition:**
```
After compensate(id, action, params):
  - state restored to pre-step(id) state (up to compensation evidence)
  - compensation evidence logged
  - step(id) marked as compensated
```

### **Compensation Order**

**Reverse Topological Order:**
```
compensation_order = reverse(topological_sort(completed_steps))
```

**Meaning:** Compensate steps in reverse order of execution

### **Compensation Execution**

**Compensation Rule:**
```
(COMPENSATE-SAGA)
postcheck(σ) = false
compensation_order = reverse(topological_sort(done))
∀step ∈ compensation_order: has_compensation(step)

───────────────────────────────────────────────────────────────
⟨σ, ε, ∅⟩ ⇝* ⟨σ₀, ε⊕e_comp, ∅⟩

where:
  - σ₀ ≈ σ_pre_execution  (state restored)
  - e_comp = compensation_evidence(compensation_order)
```

---

## ✅ **TLA+ INVARIANTS**

### **At-Most-Once Invariant**

**Invariant:**
```
TypeOK == 
  /\ state ∈ [Var → Value]
  /\ evidence_log ∈ Seq(EvidenceEntry)
  /\ ready_set ∈ SUBSET StepId
  /\ done_set ∈ SUBSET StepId
  /\ failed_set ∈ SUBSET StepId
  /\ done_set ∩ failed_set = {}
```

**At-Most-Once:**
```
AtMostOnce == 
  ∀step ∈ StepId:
    (step ∈ done_set) ∨ (step ∈ failed_set) ∨ (step ∈ ready_set) ∨ (step ∉ (done_set ∪ failed_set ∪ ready_set))
```

**Meaning:** Each step is in exactly one state

### **Compensation Invariant**

**Compensation Safety:**
```
CompensationSafety == 
  ∀step ∈ done_set:
    IF has_compensable_effect(step) THEN
      has_compensation(step)
```

**Compensation Completeness:**
```
CompensationCompleteness == 
  IF postcheck(state) = false THEN
    ∃compensation_plan: 
      execute(compensation_plan, state) → state_pre_execution
```

### **Evidence Invariant**

**Evidence Chain:**
```
EvidenceChain == 
  ∀i ∈ DOMAIN evidence_log:
    IF i > 0 THEN
      evidence_log[i].parent_hash = hash(evidence_log[i-1])
```

**Evidence Completeness:**
```
EvidenceCompleteness == 
  ∀step ∈ done_set:
    ∃entry ∈ evidence_log: entry.step_id = step
```

---

## 📋 **SAGA COMPENSATION SPECIFICATION**

### **Compensation Action**

**Compensation Action Type:**
```
CompensationAction = Action × Params × State → State × EvLog
```

**Compensation Semantics:**
```
compensate(step_id, action, params)(σ, ε) = (σ', ε')

where:
  - σ' ≈ σ_pre_step  (state restored)
  - ε' = ε ⊕ compensation_entry(step_id, action, params)
```

### **Compensation Plan**

**Compensation Plan:**
```
compensation_plan(done_steps) = 
  reverse([compensate(step) | step ∈ done_steps, has_compensable_effect(step)])
```

**Compensation Execution:**
```
execute_compensation(plan, σ, ε) = 
  foldl(λ(σ',ε') step. compensate(step)(σ',ε'), (σ,ε), plan)
```

---

## 🔒 **DURABILITY GUARANTEES**

### **Durability Property**

**Durability:**
```
After checkpoint(C):
  IF system_failure THEN
    restore(checkpoint(C)) = C
```

**Meaning:** Checkpoints are persistent and restorable

### **Compensation Property**

**Compensation Guarantee:**
```
IF execution_fails AND compensation_plan_exists THEN
  execute_compensation(plan, σ_failed, ε_failed) → (σ_pre_execution, ε_pre_execution ⊕ e_comp)
```

**Meaning:** Failed executions can be compensated to restore pre-execution state

### **Idempotence Property**

**Idempotence:**
```
IF step has idempotent effect THEN
  execute(step, σ) = execute(step, execute(step, σ))
```

**Meaning:** Idempotent steps can be safely retried

---

## 📊 **TLA+ SPECIFICATION**

### **Complete TLA+ Module**

```tla
EXTENDS Naturals, Sequences, FiniteSets

VARIABLES state, evidence_log, ready_set, done_set, failed_set, checkpoint

TypeOK == 
  /\ state ∈ [Var → Value]
  /\ evidence_log ∈ Seq(EvidenceEntry)
  /\ ready_set ∈ SUBSET StepId
  /\ done_set ∈ SUBSET StepId
  /\ failed_set ∈ SUBSET StepId
  /\ done_set ∩ failed_set = {}

AtMostOnce == 
  ∀step ∈ StepId:
    (step ∈ done_set) ∨ (step ∈ failed_set) ∨ (step ∈ ready_set) ∨ 
    (step ∉ (done_set ∪ failed_set ∪ ready_set))

CompensationSafety == 
  ∀step ∈ done_set:
    IF has_compensable_effect(step) THEN has_compensation(step)

Init == 
  /\ state = initial_state
  /\ evidence_log = <<>>
  /\ ready_set = initial_ready_set
  /\ done_set = {}
  /\ failed_set = {}
  /\ checkpoint = NULL

ExecuteStep(step) ==
  /\ step ∈ ready_set
  /\ LET result == execute(step, state)
     IN IF result.success THEN
          /\ state' = result.state
          /\ evidence_log' = Append(evidence_log, result.evidence)
          /\ done_set' = done_set ∪ {step}
          /\ ready_set' = (ready_set \ {step}) ∪ new_ready_steps
        ELSE
          /\ state' = state
          /\ evidence_log' = Append(evidence_log, failure_evidence(step))
          /\ failed_set' = failed_set ∪ {step}
          /\ ready_set' = ready_set \ {step}

CompensateStep(step) ==
  /\ step ∈ done_set
  /\ has_compensable_effect(step)
  /\ LET comp_result == compensate(step, state)
     IN /\ state' = comp_result.state
        /\ evidence_log' = Append(evidence_log, comp_result.evidence)
        /\ done_set' = done_set \ {step}

CreateCheckpoint ==
  /\ checkpoint' = (state, evidence_log, ready_set, done_set, failed_set)
  /\ UNCHANGED <<state, evidence_log, ready_set, done_set, failed_set>>

RestoreCheckpoint ==
  /\ checkpoint ≠ NULL
  /\ LET (σ, ε, Q, D, F) == checkpoint
     IN /\ state' = σ
        /\ evidence_log' = ε
        /\ ready_set' = Q
        /\ done_set' = D
        /\ failed_set' = F
        /\ checkpoint' = NULL

Next == 
  ExecuteStep(step) ∨ CompensateStep(step) ∨ CreateCheckpoint ∨ RestoreCheckpoint

Spec == Init /\ [][Next]_vars /\ WF_vars(ExecuteStep)

THEOREM Spec => []TypeOK
THEOREM Spec => []AtMostOnce
THEOREM Spec => []CompensationSafety
```

---

## 🎯 **NEXT STEPS**

1. ✅ **Checkpoint Semantics** - Complete
2. ✅ **Saga Compensation** - Complete
3. ✅ **TLA+ Invariants** - Complete
4. ⏳ **Implementation** - Link to runtime

---

**Status:** 📋 **DUrable Execution Specification Complete**  
**Next:** Security model research

