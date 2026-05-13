# Chapter 46: APOE Integration: Intent-Aware Orchestration

**Part IV: Integration**  
**Unified Textbook Chapter Number:** 46

---

> **Cross-References:**
> - **AIM-OS Foundations:** See Chapter 8 (Orchestration Engine - APOE) for APOE architecture
> - **PLIx Architecture:** See Chapter 40 (The Four Pillars) for how APOE integrates with the Execution Layer
> - **PLIx Integration:** See Chapter 44 (CMC Integration) for intent storage with tags
> - **PLIx Integration:** See Chapter 45 (VIF Integration) for intent verification with tags
> - **PLIx Integration:** See Chapter 47 (SEG Integration) for evidence collection with tags
> - **Tag System:** See Chapter 5 (Tag System) for how entity tags enable canonical identity in APOE

---

**Target Word Count:** 2,500-3,000 words  
**Status:** ✅ **COMPLETE** (Unified Textbook Edition)

---

## Section 46.1: Before PLIx: Plan Execution

Before PLIx, APOE (Atomic Provenance Orchestration Engine) executes plans—running steps in order, managing budgets and gates, but lacking intent awareness.

**APOE's Original Purpose**

APOE was designed to:

- **Execute Plans:** Run ExecutionPlans with role-based orchestration
- **Manage Budgets:** Track execution budgets (cost, time, tokens)
- **Enforce Gates:** Validate gates before execution (confidence, policy)
- **Track Provenance:** Record execution provenance for auditability

APOE's strength lies in its ability to orchestrate multi-agent plans with budget management and gate enforcement, enabling reliable plan execution.

**Plan Execution Example**

Before PLIx, APOE executes plans:

```python
# Execute plan
plan = ExecutionPlan(
    steps=[
        ExecutionStep(id="check_room", role="api_executor", description="Check room availability"),
        ExecutionStep(id="reserve_room", role="api_executor", description="Reserve room", dependencies=["check_room"])
    ],
    roles={
        "api_executor": RoleDefinition(description="Execute API calls", capabilities=["api"])
    },
    budget=Budget(max_cost=1000, max_time=300000),
    gates=[ConfidenceGate(threshold=0.70)]
)

result = apoe.execute(plan)
# Verification: "Did steps complete?"
```

APOE executes plans (runs steps in order) but doesn't verify intent achievement (did we achieve what we wanted?). This limits APOE's ability to orchestrate for purpose and measure intent-outcome alignment.

**Limitations of Plan Execution**

Plan execution has limitations:

- **No Intent Awareness:** APOE doesn't know what was intended, only what steps to execute
- **No Intent Verification:** Can't verify "did this plan achieve the intent?"
- **No Intent-Driven Execution:** Execution isn't driven by intent contracts
- **No Intent Evidence:** Doesn't collect evidence of intent achievement

These limitations prevent APOE from supporting intent-driven orchestration, verification, and learning.

**Role-Based Execution**

APOE executes plans using roles:

```python
# Role-based execution
executor = PlanExecutor()
executor.register_role_handler("api_executor", async (description, inputs) => {
    # Execute API call
    return await execute_api_call(inputs)
})

result = executor.execute(plan)
```

Role-based execution enables flexible orchestration, but without intent awareness, roles don't understand purpose.

**Budget and Gate Management**

APOE manages budgets and gates:

```python
# Budget management
budget = Budget(max_cost=1000, max_time=300000)
if budget.exceeded():
    raise BudgetExceededError()

# Gate enforcement
gate = ConfidenceGate(threshold=0.70)
if not gate.check(step):
    raise GateFailedError()
```

Budget and gate management enables controlled execution, but without intent awareness, gates don't verify intent achievement.

**Before PLIx Summary**

Before PLIx, APOE is execution-focused:
- Executes plans (runs steps in order)
- Manages budgets and gates
- Tracks execution provenance
- Lacks intent awareness (no intent verification or evidence collection)

This execution focus limits APOE's ability to orchestrate for purpose and measure intent achievement.

---

## Section 46.2: After PLIx: Intent Achievement

After PLIx, APOE achieves intent—orchestrating execution to achieve intent contracts, verifying intent achievement, and collecting intent evidence.

**Intent-Aware Orchestration**

With PLIx, APOE achieves intent:

```python
# Achieve intent with entity tag
contract = PLIxContract(
    intent="Book a meeting room",
    entity="plix://room/meeting_room",  # Entity tag
    contract={"post": ["room_reserved == true"]}
)

# Compile contract to plan (includes tag resolution)
plan = compile_contract_to_plan(contract)

# Execute to achieve intent
result = apoe.execute(plan)

# Verify intent achievement (uses tag-based entity references)
intent_achieved = verify_contract(contract, result.outcome)
```

APOE now orchestrates to achieve intent (what we want) **with tag-based entity references**, enabling intent-driven orchestration with canonical identity. Tags enable unambiguous entity references (`plix://room/meeting_room`), while resolved entities enable efficient execution.

**Intent Verification**

With PLIx, APOE verifies intent achievement:

```python
# Verify intent after execution (uses tag-based entity references)
def verify_intent_achievement(contract: PLIxContract, result: ExecutionResult) -> bool:
    # Get entity tag from contract
    entity_tag = contract.entity or contract.entityTag
    
    # Check postconditions for the entity identified by tag
    for postcondition in contract.contract["post"]:
        # Verify postcondition for entity plix://room/meeting_room
        if not evaluate_postcondition(postcondition, result.outcome, entity_tag):
            return False
    return True

# Execute and verify
result = apoe.execute(plan)
intent_achieved = verify_intent_achievement(contract, result)

if not intent_achieved:
    # Intent not achieved: trigger compensation or retry
    handle_intent_failure(contract, result)
```

Intent verification enables APOE to verify that execution achieved the intended goals **for specific entities via tags**, not just that steps completed. Tags enable entity-based intent verification.

**Intent Evidence Collection**

With PLIx, APOE collects intent evidence:

```python
# Collect intent evidence (includes tag-based entity references)
def collect_intent_evidence(contract: PLIxContract, result: ExecutionResult) -> Evidence:
    entity_tag = contract.entity or contract.entityTag
    
    evidence = Evidence(
        contract=contract,
        entity_tag=entity_tag,  # Entity tag
        outcome=result.outcome,
        execution_provenance=result.provenance,
        postconditions_satisfied=verify_intent_achievement(contract, result),
        timestamp=datetime.now()
    )
    
    # Store evidence in SEG with entity tag
    seg.add_evidence(evidence, entity_tag=entity_tag)
    
    return evidence
```

Intent evidence collection enables APOE to record proof of intent achievement **with tag-based entity references**, supporting verification and learning. Tags enable entity-based evidence queries.

**Contract-Driven Execution**

With PLIx, APOE execution is driven by contracts:

```python
# Contract-driven execution
def execute_contract(contract: PLIxContract) -> ExecutionResult:
    # Compile contract to plan
    plan = compile_contract_to_plan(contract)
    
    # Execute plan
    result = apoe.execute(plan)
    
    # Verify intent achievement
    intent_achieved = verify_intent_achievement(contract, result)
    
    # Collect evidence
    evidence = collect_intent_evidence(contract, result)
    
    return ExecutionResult(
        outcome=result.outcome,
        intent_achieved=intent_achieved,
        evidence=evidence
    )
```

Contract-driven execution ensures that APOE orchestrates to achieve intent contracts, not just execute step sequences.

**After PLIx Summary**

After PLIx, APOE is intent-aware:
- Achieves intent (orchestrates to achieve intent contracts)
- Verifies intent achievement (checks postconditions)
- Collects intent evidence (records proof of intent achievement)
- Executes contract-driven (execution driven by intent contracts)

This intent awareness transforms APOE from execution-focused orchestration to intent-aware orchestration, enabling intent-driven systems.

---

## Section 46.3: Transformation Details

The transformation from plan execution to intent achievement involves compiling PLIx IR to APOE ExecutionPlans, mapping intent to roles, budgets, and gates, and enabling intent verification and evidence collection.

**PLIx IR → APOE ExecutionPlan**

IR to APOE compilation **uses resolved entities/capabilities from tag resolution**:

```python
def compile_to_apoe(ir: IRPlan) -> ExecutionPlan:
    """Compile PLIx IR to APOE ExecutionPlan with tag resolution"""
    
    # Map IR nodes to APOE steps (uses resolved entities/capabilities)
    steps = []
    for node in ir.nodes:
        # Use resolved entity/capability from tag resolution
        entity = node.resolvedEntity or {}
        capability = node.resolvedCapability or {}
        
        step = ExecutionStep(
            id=node.id,
            role=extract_role(node.action, capability),  # Extract role from action/capability
            description=f"{node.action}: {ir.intent}",
            inputs={
                ...node.params,
                "entity_tag": node.entityTag,  # Include entity tag
                "entity": entity,  # Include resolved entity
                "capability": capability  # Include resolved capability
            },
            outputs={},
            dependencies=[
                Dependency(step_id=dep_id, output_field="result")
                for dep_id in node.deps
            ]
        )
        steps.append(step)
    
    # Map roles (uses capability tag resolution)
    roles = {}
    for step in steps:
        if step.role not in roles:
            roles[step.role] = RoleDefinition(
                description=f"Execute {step.role} actions",
                capabilities=[step.role]
            )
    
    # Map budgets and gates from contract
    budget, gates = map_budgets_and_gates(ir)
    
    return ExecutionPlan(
        steps=steps,
        roles=roles,
        budget=budget,
        gates=gates
    )
```

This compilation transforms PLIx IR into APOE ExecutionPlans **with tag-based entity references**, preserving intent semantics while enabling APOE orchestration. Tags enable canonical identity for entities and capabilities, while resolved entities/capabilities enable efficient execution.

**Intent → Role Mapping**

Intent to role mapping **uses capability tag resolution**:

```python
def extract_role(action: str, capability: any = None) -> str:
    """Extract role from action/capability"""
    # Use capability tag resolution if available
    if capability and capability.get("role"):
        return capability["role"]
    
    # Extract role from action: "api.reserve_room" → "api_executor"
    namespace = action.split('.')[0]
    role_mapping = {
        "api": "api_executor",
        "db": "database_executor",
        "ai": "ai_agent",
        "router": "router_agent"
    }
    return role_mapping.get(namespace, "default_executor")
```

Role mapping enables APOE to route tasks to appropriate executors **based on capability tag resolution**, enabling tag-based role discovery. Tags enable canonical identity for capabilities, while resolved capabilities enable efficient role mapping.

**Intent → Budget Mapping**

Intent to budget mapping:

```python
def map_budgets_and_gates(ir: IRPlan) -> Tuple[Budget, List[Gate]]:
    """Map intent to budgets and gates"""
    
    # Calculate budget from contract metadata
    budget = Budget(
        max_cost=ir.metadata.get("max_cost", 1000),
        max_time=ir.metadata.get("max_time", 300000),
        max_tokens=ir.metadata.get("max_tokens", 10000)
    )
    
    # Map constraints to gates
    gates = []
    
    # Confidence gate
    gates.append(ConfidenceGate(
        threshold=PLIX_DEFAULTS.confidence.global_minimum,
        check=async (step) => {
            confidence = await vif.get_confidence(step.role, step.inputs)
            return confidence >= PLIX_DEFAULTS.confidence.global_minimum
        }
    ))
    
    # Policy gate (from constraints)
    gates.append(PolicyGate(
        constraints=ir.constraints,
        check=async (step) => {
            policy = compile_constraints_to_policy(ir.constraints)
            return await evaluate_policy(policy, step.inputs)
        }
    ))
    
    return budget, gates
```

Budget and gate mapping enables APOE to enforce PLIx constraints (confidence thresholds, policy rules) during execution.

**Intent Verification Integration**

Intent verification integration **uses tag-based entity references**:

```python
def execute_with_intent_verification(
    contract: PLIxContract,
    plan: ExecutionPlan
) -> ExecutionResult:
    """Execute plan with intent verification"""
    
    # Execute plan
    result = apoe.execute(plan)
    
    # Verify intent achievement (uses tag-based entity references)
    entity_tag = contract.entity or contract.entityTag
    intent_achieved = verify_contract(contract, result.outcome, entity_tag)
    
    # Collect evidence (includes entity tag)
    evidence = collect_intent_evidence(contract, result)
    
    # Update result
    result.intent_achieved = intent_achieved
    result.evidence = evidence
    result.entity_tag = entity_tag  # Include entity tag
    
    return result
```

Intent verification integration enables APOE to verify intent achievement **for specific entities via tags** after execution, ensuring that execution achieved intended goals. Tags enable entity-based intent verification.

**Transformation Benefits**

The transformation provides:

- **Intent-Driven Orchestration:** APOE orchestrates to achieve intent contracts
- **Intent Verification:** APOE verifies intent achievement through postcondition checking
- **Intent Evidence:** APOE collects evidence of intent achievement
- **Contract-Driven Execution:** Execution driven by intent contracts, not just step sequences

These benefits transform APOE from execution-focused orchestration to intent-aware orchestration, enabling intent-driven systems.

---

## Section 46.4: Implementation Examples

Implementation examples demonstrate PLIx → APOE compilation, intent execution, intent verification, and intent evidence collection.

**Example 1: PLIx → APOE Compilation**

```python
# PLIx IR with entity tags
ir = IRPlan(
    intent="Book a meeting room",
    nodes=[
        IRNode(
            id="check_availability", 
            action="api.check_room_availability", 
            deps=[],
            entityTag="plix://room/meeting_room"  # Entity tag
        ),
        IRNode(
            id="reserve_room", 
            action="api.reserve_room", 
            deps=["check_availability"],
            entityTag="plix://room/meeting_room"  # Same entity tag
        )
    ],
    constraints=["duration <= 4h"],
    tagResolutions: new Map([  # Tag resolution cache
        ["plix://room/meeting_room", {
            type: "database_table",
            location: "postgresql://db/rooms"
        }]
    ])
)

# Compile to APOE (uses resolved entities)
apoe_plan = compile_to_apoe(ir)

print(f"APOE Plan Steps: {len(apoe_plan.steps)}")  # 2
print(f"APOE Plan Roles: {list(apoe_plan.roles.keys())}")  # ["api_executor"]
print(f"APOE Plan Gates: {len(apoe_plan.gates)}")  # 2 (confidence + policy)
print(f"Entity Tag: {ir.nodes[0].entityTag}")  # plix://room/meeting_room
```

This example demonstrates compiling PLIx IR to APOE ExecutionPlans, preserving intent semantics.

**Example 2: Intent Execution**

```python
# Execute intent contract with entity tag
contract = PLIxContract(
    intent="Book a meeting room",
    entity="plix://room/meeting_room",  # Entity tag
    contract={"post": ["room_reserved == true"]}
)

# Compile and execute
plan = compile_contract_to_plan(contract)
result = apoe.execute(plan)

print(f"Execution completed: {result.success}")
print(f"Outcome: {result.outcome}")
print(f"Entity Tag: {contract.entity}")  # plix://room/meeting_room
print(f"Intent Achieved: {result.intent_achieved}")
```

This example demonstrates executing intent contracts through APOE, achieving intent through orchestration.

**Example 3: Intent Verification**

```python
# Verify intent achievement (uses tag-based entity references)
entity_tag = contract.entity or contract.entityTag
intent_achieved = verify_intent_achievement(contract, result)

if intent_achieved:
    print(f"Intent achieved for {entity_tag}: Room reserved")
else:
    print(f"Intent not achieved for {entity_tag}: Postconditions not satisfied")
    # Trigger compensation or retry
    handle_intent_failure(contract, result)
```

This example demonstrates verifying intent achievement through postcondition checking.

**Example 4: Intent Evidence Collection**

```python
# Collect intent evidence (includes entity tag)
evidence = collect_intent_evidence(contract, result)

print(f"Evidence ID: {evidence.id}")
print(f"Entity Tag: {evidence.entity_tag}")  # plix://room/meeting_room
print(f"Postconditions satisfied: {evidence.postconditions_satisfied}")
print(f"Evidence stored in SEG: {evidence.seg_id}")

# Query evidence by entity tag
evidence_chain = seg.query_evidence_chain(evidence.id, entity_tag=evidence.entity_tag)
print(f"Evidence chain length for {evidence.entity_tag}: {len(evidence_chain)}")
```

This example demonstrates collecting intent evidence and storing it in SEG for verification and learning.

**Implementation Benefits**

Implementation examples demonstrate:

- **PLIx → APOE Compilation:** Transforming intent contracts to execution plans
- **Intent Execution:** Achieving intent through orchestration
- **Intent Verification:** Verifying intent achievement through postcondition checking
- **Intent Evidence:** Collecting proof of intent achievement

These examples show how APOE transforms from execution-focused orchestration to intent-aware orchestration, enabling intent-driven systems.

---

## Chapter 46 Summary

APOE transforms from plan execution to intent achievement through PLIx integration. Before PLIx, APOE executes plans but lacks intent awareness. After PLIx, APOE achieves intent contracts **with tag-based entity references**, verifies intent achievement **for specific entities via tags**, collects intent evidence **with tag-based entity tracking**, and executes contract-driven **using resolved entities/capabilities from tag resolution**.

**Tags enable canonical identity** throughout APOE integration: intent contracts reference entities via tags (`plix://room/meeting_room`), role mapping uses capability tag resolution, intent verification checks postconditions for specific entities via tags, and evidence collection includes entity tags for entity-based queries. Tags enable unambiguous entity references that survive technology changes, enabling intent-aware orchestration with canonical identity.

This transformation enables intent-driven orchestration, verification, and learning, making APOE a foundation for intent-aware systems. Tags provide the identity foundation that makes this transformation possible.

**Next:** Chapter 47 explores SEG integration—how SEG transforms from evidence chains to intent lineage, showing how tags enable intent lineage tracking.

---

**Word Count:** ~2,800 words  
**Status:** ✅ **COMPLETE** (Unified Textbook Edition)  
**Cross-References:**
> - **AIM-OS Foundations:** Chapter 8 (Orchestration Engine - APOE)
> - **PLIx Architecture:** Chapter 40 (The Four Pillars)
> - **PLIx Architecture:** Chapter 43 (Compiler Architecture)
> - **PLIx Integration:** Chapter 44 (CMC Integration)
> - **PLIx Integration:** Chapter 45 (VIF Integration)
> - **PLIx Integration:** Chapter 47 (SEG Integration)
> - **Tag System:** Chapter 5 (Tag System)

