# Reference Interpreter: Implementation Plan

**Date:** 2025-01-27  
**Status:** 📋 **PLANNING**  
**Goal:** Create small interpreter over core semantics rules with confidence aggregation

---

## 🎯 **OBJECTIVE**

Implement reference interpreter with:
1. **DAG scheduler** (ready set formation, topological execution)
2. **Retry/fallback precedence** (idempotent vs non-idempotent retries)
3. **Compensation engine** (reverse topological order, left-inverse assumption)
4. **Effect & confidence checker** (rejects plans violating required φ or effects)

---

## 📐 **ARCHITECTURE**

### **Core Components**

```
ref-interpreter/
├── src/
│   ├── lib.rs                    # Main library
│   ├── types.rs                  # Core types (State, EvLog, Config, etc.)
│   ├── resolver.rs               # Namespace resolution (Σ)
│   ├── dag_scheduler.rs          # DAG scheduler
│   ├── retry_fallback.rs         # Retry/fallback logic
│   ├── compensation.rs           # Compensation engine
│   ├── effect_checker.rs         # Effect & confidence checking
│   ├── executor.rs               # Step execution
│   └── interpreter.rs           # Main interpreter loop
├── tests/
│   ├── test_dag_scheduler.rs
│   ├── test_retry_fallback.rs
│   ├── test_compensation.rs
│   └── test_effect_checker.rs
└── examples/
    └── room.rs                   # Meeting-room example
```

---

## 🔧 **IMPLEMENTATION SPECIFICATIONS**

### **1. Types Module**

**Core Types:**
```rust
pub type State = HashMap<String, Value>;
pub type EvLog = Vec<EvidenceEntry>;
pub type StepId = String;
pub type Config = (State, EvLog, HashSet<StepId>, HashSet<StepId>, HashSet<StepId>);

pub struct EvidenceEntry {
    pub id: String,
    pub step_id: Option<StepId>,
    pub contract_id: Option<String>,
    pub time: DateTime<Utc>,
    pub tool: String,
    pub input_hash: String,
    pub output_hash: String,
    pub parents: Vec<String>,
    pub signer: String,
    pub sig: String,
}
```

### **2. Resolver Module**

**Resolver:**
```rust
pub struct Resolver {
    pub tags: HashMap<Tag, Value>,
    pub actions: HashMap<String, PrimAction>,
}

impl Resolver {
    pub fn resolve_tag(&self, tag: &Tag) -> Option<Value>;
    pub fn resolve_action(&self, id: &str) -> Option<PrimAction>;
}
```

### **3. DAG Scheduler Module**

**Ready Set Formation:**
```rust
pub fn ready_set(
    graph: &PlanDAG,
    done: &HashSet<StepId>
) -> HashSet<StepId> {
    graph.vertices()
        .filter(|v| {
            graph.incoming(*v)
                .all(|u| done.contains(u))
        })
        .filter(|v| !done.contains(v))
        .collect()
}
```

**Topological Execution:**
```rust
pub fn execute_topological(
    plan: &Plan,
    config: &mut Config,
    resolver: &Resolver
) -> Result<Config, Error> {
    let mut done = HashSet::new();
    let mut failed = HashSet::new();
    
    loop {
        let ready = ready_set(&plan.dag, &done);
        if ready.is_empty() {
            break;
        }
        
        for step_id in ready {
            match execute_step(&step_id, config, resolver) {
                Ok(_) => done.insert(step_id),
                Err(_) => failed.insert(step_id),
            };
        }
    }
    
    Ok(config)
}
```

### **4. Retry/Fallback Module**

**Retry Logic:**
```rust
pub fn handle_retry(
    step: &Step,
    config: &mut Config,
    remaining: usize
) -> Result<(), Error> {
    if remaining > 0 {
        if step.is_idempotent() {
            // Re-enqueue without compensation
            config.ready_set.insert(step.id.clone());
        } else {
            // Must compensate before retry
            compensate_step(step, config)?;
            config.ready_set.insert(step.id.clone());
        }
    }
    Ok(())
}
```

**Fallback Logic:**
```rust
pub fn handle_fallback(
    failed_step: &StepId,
    fallback_step: &StepId,
    config: &mut Config
) -> Result<(), Error> {
    if config.failed.contains(failed_step) {
        if deps_satisfied(fallback_step, &config.done) {
            config.ready_set.insert(fallback_step.clone());
        }
    }
    Ok(())
}
```

### **5. Compensation Module**

**Compensation Engine:**
```rust
pub fn compensate_plan(
    plan: &Plan,
    config: &mut Config,
    resolver: &Resolver
) -> Result<Config, Error> {
    let compensable_steps: Vec<StepId> = plan.steps
        .iter()
        .filter(|s| s.has_compensable_effect())
        .filter(|s| config.done.contains(&s.id))
        .map(|s| s.id.clone())
        .rev()  // Reverse topological order
        .collect();
    
    for step_id in compensable_steps {
        let step = plan.get_step(&step_id)?;
        compensate_step(step, config, resolver)?;
    }
    
    Ok(config.clone())
}
```

**Compensation Step:**
```rust
pub fn compensate_step(
    step: &Step,
    config: &mut Config,
    resolver: &Resolver
) -> Result<(), Error> {
    let comp_action = step.compensation_action()?;
    let comp_params = step.compensation_params()?;
    
    let (new_state, evidence) = execute_action(
        comp_action,
        comp_params,
        &config.state,
        resolver
    )?;
    
    config.state = new_state;
    config.evidence_log.push(evidence);
    
    Ok(())
}
```

### **6. Effect & Confidence Checker Module**

**Effect Checker:**
```rust
pub fn check_effects(
    plan: &Plan,
    allowed_effects: &HashSet<Effect>,
    context: &Context
) -> Result<(), Error> {
    for step in &plan.steps {
        let step_effects = step.effects();
        if !allowed_effects.is_superset(&step_effects) {
            return Err(Error::EffectViolation {
                step: step.id.clone(),
                required: step_effects,
                allowed: allowed_effects.clone(),
            });
        }
    }
    Ok(())
}
```

**Confidence Checker:**
```rust
pub fn check_confidence(
    plan: &Plan,
    required_confidence: f64,
    resolver: &Resolver
) -> Result<(), Error> {
    let plan_confidence = plan.min_confidence(resolver)?;
    
    if plan_confidence < required_confidence {
        return Err(Error::ConfidenceViolation {
            required: required_confidence,
            actual: plan_confidence,
        });
    }
    
    Ok(())
}
```

### **7. Executor Module**

**Step Execution:**
```rust
pub fn execute_step(
    step: &Step,
    config: &mut Config,
    resolver: &Resolver
) -> Result<(State, EvidenceEntry), Error> {
    let params = eval_params(&step.params, &config.state, resolver)?;
    let action = resolver.resolve_action(&step.action_id)?;
    
    let (new_state, result) = run_action(action, params, &config.state)?;
    
    let evidence = create_evidence(
        &step.id,
        &step.contract_id,
        action,
        params,
        result,
        &config.evidence_log
    )?;
    
    Ok((new_state, evidence))
}
```

### **8. Interpreter Module**

**Main Interpreter Loop:**
```rust
pub fn interpret(
    intent: &Intent,
    initial_state: State,
    resolver: &Resolver
) -> Result<(State, EvLog), Error> {
    // Step 1: Check preconditions
    if !check_preconditions(&intent.contract.pre, &initial_state)? {
        return Err(Error::PreconditionFailed);
    }
    
    // Step 2: Check effects and confidence
    check_effects(&intent.plan, &intent.safety.allowed_effects, resolver)?;
    check_confidence(&intent.plan, intent.safety.min_confidence, resolver)?;
    
    // Step 3: Execute plan
    let mut config = (
        initial_state,
        Vec::new(),
        HashSet::new(),
        HashSet::new(),
        HashSet::new(),
    );
    
    config.2 = ready_set(&intent.plan.dag, &config.3);
    
    loop {
        if config.2.is_empty() {
            break;
        }
        
        for step_id in config.2.clone() {
            match execute_step_with_retry(&step_id, &mut config, resolver) {
                Ok(_) => {
                    config.3.insert(step_id.clone());
                    config.2.remove(&step_id);
                }
                Err(e) => {
                    config.4.insert(step_id.clone());
                    config.2.remove(&step_id);
                    
                    // Handle retry/fallback
                    handle_retry_fallback(&step_id, &mut config, resolver)?;
                }
            }
        }
        
        config.2 = ready_set(&intent.plan.dag, &config.3);
    }
    
    // Step 4: Check postconditions
    if !check_postconditions(&intent.contract.post, &config.0)? {
        // Step 5: Compensate
        compensate_plan(&intent.plan, &mut config, resolver)?;
        return Err(Error::PostconditionFailed);
    }
    
    Ok((config.0, config.1))
}
```

---

## 🎯 **NEXT STEPS**

1. ✅ **Implementation Plan** - Complete
2. ⏳ **Rust Implementation** - Create reference interpreter
3. ⏳ **Tests** - Create test suite
4. ⏳ **Examples** - Implement meeting-room example

---

**Status:** 📋 **IMPLEMENTATION PLAN COMPLETE**  
**Next:** Create Rust implementation

