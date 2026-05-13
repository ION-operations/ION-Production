---
id: apoe_T3_detailed
level: L3
system: APOE
status: complete
updated: 2025-10-30
---

> TRANSITIONAL T-LEVEL DOCUMENT – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# APOE – T3 Detailed Implementation Guide

## Setup & Interfaces

### Public API Methods

```python
from packages.apoe import APOEEngine, compile_plan, execute_plan, create_role

# Initialize APOE engine
engine = APOEEngine(
    cmc_client=cmc_client,
    hhni_client=hhni_client,
    vif_client=vif_client
)

# Compile ACL plan
plan = compile_plan(acl_text="""
    pipeline code_review {
        step parse: Builder(input=code_file, budget=2k)
        step analyze: Critic(input=parse.ast, budget=5k)
        gate quality: check(analyze.issues.critical == 0)
        step suggest: Reasoner(input=analyze, budget=4k)
    }
""")

# Execute plan
result = execute_plan(plan, inputs={"code_file": code_file})

# Create custom role
planner_role = create_role(
    name="Planner",
    capabilities=["task_analysis", "decomposition"],
    contract={"input": "task: ComplexTask", "output": "plan: List[SubTask]"}
)
```

### Type Definitions

```python
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum

class RoleType(Enum):
    PLANNER = "planner"
    RETRIEVER = "retriever"
    REASONER = "reasoner"
    VERIFIER = "verifier"
    BUILDER = "builder"
    CRITIC = "critic"
    OPERATOR = "operator"
    WITNESS = "witness"

@dataclass
class ExecutionPlan:
    """Compiled, executable plan"""
    id: str
    name: str
    dag: DAG
    total_budget: Budget
    gates: List[Gate]

@dataclass
class Step:
    """Single step in execution plan"""
    id: str
    name: str
    role: RoleType
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    budget: Budget
    status: StepStatus

@dataclass
class Budget:
    """Resource budget constraints"""
    tokens: int
    time: int  # seconds
    tools: int
```

## Plan Compilation Implementation

### ACL Compilation

```python
def compile_plan(acl_text: str) -> ExecutionPlan:
    """Compile ACL text to executable plan"""
    
    # Parse ACL → AST
    ast = parse_acl(acl_text)
    
    # Type check
    validate_types(ast)
    
    # Budget analysis
    total_budget = compute_total_budget(ast)
    
    # Gate placement
    validate_gates(ast)
    
    # Generate DAG
    dag = build_dag(ast)
    
    # Optimize (parallelize independent steps)
    dag = optimize_dag(dag)
    
    return ExecutionPlan(
        id=f"plan_{uuid.uuid4().hex}",
        name=ast.name,
        dag=dag,
        total_budget=total_budget,
        gates=ast.gates
    )
```

### DAG Generation

```python
def build_dag(ast: AST) -> DAG:
    """Convert AST to directed acyclic graph"""
    dag = DAG()
    
    for step in ast.steps:
        node = Node(
            id=step.id,
            data=step,
            dependencies=step.dependencies
        )
        dag.add_node(node)
    
    # Add edges from dependencies
    for step in ast.steps:
        for dep_id in step.dependencies:
            dag.add_edge(dep_id, step.id)
    
    return dag
```

## Execution Implementation

### DAG Execution

```python
def execute_plan(plan: ExecutionPlan, inputs: Dict[str, Any]) -> ExecutionResult:
    """Execute plan DAG"""
    
    # Topological sort
    execution_order = topological_sort(plan.dag)
    
    # State for step outputs
    step_outputs = {}
    
    # Execute steps in order
    for step_id in execution_order:
        step = plan.dag.get_node(step_id).data
        
        # Resolve dependencies
        step_inputs = resolve_dependencies(step, step_outputs, inputs)
        
        # Execute step
        result = execute_step(step, step_inputs)
        
        # Store outputs
        step_outputs[step_id] = result.outputs
        
        # Check gates after step
        gate_result = check_gates(step, result)
        if gate_result.status == "FAIL":
            return ExecutionResult(status="FAILED", reason="gate_failed")
        
        # Emit VIF witness
        vif_witness = generate_vif_witness(step, result)
        store_vif_witness(vif_witness)
    
    return ExecutionResult(status="SUCCESS", outputs=step_outputs)
```

### Step Execution

```python
def execute_step(step: Step, inputs: Dict[str, Any]) -> StepResult:
    """Execute single step with role dispatch"""
    
    # Select role
    role = get_role(step.role)
    
    # Enforce contract
    validate_contract(role.contract, inputs)
    
    # Check budget
    if not step.budget.check_all():
        raise BudgetExceeded(f"Budget exceeded for step {step.id}")
    
    # Execute role
    step.started_at = datetime.utcnow()
    try:
        outputs = role.execute(inputs, step.budget)
    except Exception as e:
        step.status = StepStatus.FAILED
        step.error = str(e)
        raise
    
    step.completed_at = datetime.utcnow()
    step.status = StepStatus.COMPLETED
    
    # Update budget
    step.budget.tokens_consumed += estimate_tokens(outputs)
    step.budget.time_elapsed_seconds = step.duration_seconds()
    
    return StepResult(outputs=outputs, step=step)
```

## Role Implementation

### Retriever Role Example

```python
class RetrieverRole:
    """Fetches context via HHNI"""
    
    def execute(self, inputs: Dict[str, Any], budget: Budget) -> Dict[str, Any]:
        """Retrieve context using HHNI"""
        query = inputs["query"]
        
        # Use HHNI for retrieval
        result = hhni_client.retrieve(
            query=query,
            config=RetrievalConfig(
                token_budget=budget.tokens,
                enable_dvns=True,
                enable_dedup=True
            )
        )
        
        return {
            "context": result.items,
            "total_tokens": result.total_tokens
        }
```

### Builder Role Example

```python
class BuilderRole:
    """Generates code/content/artifacts"""
    
    def execute(self, inputs: Dict[str, Any], budget: Budget) -> Dict[str, Any]:
        """Generate artifact from specification"""
        spec = inputs["spec"]
        examples = inputs.get("examples", [])
        
        # Generate using few-shot prompting
        artifact = model.generate(
            prompt=self.build_prompt(spec, examples),
            max_tokens=budget.tokens
        )
        
        return {
            "artifact": artifact,
            "tokens_used": estimate_tokens(artifact)
        }
```

## Gate Implementation

### Gate Evaluation

```python
def check_gates(step: Step, result: StepResult) -> GateResult:
    """Check gates after step execution"""
    
    for gate in step.gates:
        gate_result = evaluate_gate(gate, result)
        
        if gate_result.status == "FAIL":
            return GateResult(status="FAIL", gate=gate, reason=gate_result.reason)
        elif gate_result.status == "ABSTAIN":
            return GateResult(status="ABSTAIN", gate=gate, reason=gate_result.reason)
        elif gate_result.status == "WARN":
            log.warning(f"Gate warning: {gate_result.reason}")
    
    return GateResult(status="PASS")
```

### Gate Types

```python
def evaluate_gate(gate: Gate, result: StepResult) -> GateResult:
    """Evaluate gate condition"""
    
    if gate.type == "quality":
        return check_quality_gate(gate, result)
    elif gate.type == "safety":
        return check_safety_gate(gate, result)
    elif gate.type == "policy":
        return check_policy_gate(gate, result)
    elif gate.type == "budget":
        return check_budget_gate(gate, result)
    else:
        raise ValueError(f"Unknown gate type: {gate.type}")
```

## Budget Management

### Budget Tracking

```python
class BudgetTracker:
    """Track and enforce resource budgets"""
    
    def track_tokens(self, step: Step, tokens_used: int):
        """Track token usage"""
        step.budget.tokens_consumed += tokens_used
        
        if step.budget.tokens_consumed > step.budget.tokens_limit:
            raise BudgetExceeded(f"Token budget exceeded: {step.budget.tokens_consumed} > {step.budget.tokens_limit}")
    
    def track_time(self, step: Step):
        """Track execution time"""
        step.budget.time_elapsed_seconds = step.duration_seconds()
        
        if step.budget.time_elapsed_seconds > step.budget.time_limit_seconds:
            raise BudgetExceeded(f"Time budget exceeded: {step.budget.time_elapsed_seconds}s > {step.budget.time_limit_seconds}s")
    
    def track_tools(self, step: Step):
        """Track tool usage"""
        step.budget.tools_consumed += 1
        
        if step.budget.tools_consumed > step.budget.tools_limit:
            raise BudgetExceeded(f"Tool budget exceeded: {step.budget.tools_consumed} > {step.budget.tools_limit}")
```

## Error Handling

### Retry Logic

```python
def execute_with_retry(step: Step, inputs: Dict[str, Any], max_retries: int = 3) -> StepResult:
    """Execute step with retry logic"""
    
    for attempt in range(max_retries):
        try:
            return execute_step(step, inputs)
        except BudgetExceeded as e:
            # Don't retry budget violations
            raise
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            # Exponential backoff
            time.sleep(2 ** attempt)
    
    raise ExecutionError(f"Failed after {max_retries} attempts")
```

### Circuit Breaker

```python
class CircuitBreaker:
    """Prevent cascading failures"""
    
    def __init__(self, failure_threshold: int = 5):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker"""
        if self.state == "OPEN":
            raise CircuitBreakerOpen("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise
    
    def on_success(self):
        """Reset on success"""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def on_failure(self):
        """Track failures"""
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
```

## Examples

### Example: Simple Plan Execution

```python
# Compile plan
plan = compile_plan("""
    pipeline simple_task {
        step retrieve: Retriever(query="authentication", budget=2k)
        step build: Builder(input=retrieve.context, budget=5k)
        gate quality: check(build.artifact is not None)
    }
""")

# Execute
result = execute_plan(plan, inputs={})

# Check result
assert result.status == "SUCCESS"
assert "build" in result.outputs
```

### Example: Complex Plan with Gates

```python
plan = compile_plan("""
    pipeline code_review {
        step parse: Builder(input=code_file, budget=2k)
        step analyze: Critic(input=parse.ast, budget=5k)
        gate quality: check(analyze.issues.critical == 0)
        step suggest: Reasoner(input=analyze, budget=4k)
        gate safety: check(suggest.suggestions.security_issues == 0)
        step verify: Verifier(input=suggest, budget=3k)
    }
""")

result = execute_plan(plan, inputs={"code_file": code_file})

if result.status == "FAILED":
    if result.reason == "quality_gate_failed":
        print("Critical issues found, stopping")
    elif result.reason == "safety_gate_failed":
        print("Security issues found, stopping")
```

### Example: DEPP Self-Rewriting

```python
# Initial plan
plan = compile_plan(acl_text)

# Execute and collect evidence
result = execute_plan(plan, inputs)
evidence = collect_evidence(result)

# Analyze effectiveness
effectiveness = analyze_effectiveness(evidence)

# Rewrite plan if needed
if effectiveness.score < 0.8:
    improved_plan = rewrite_plan(plan, evidence)
    result = execute_plan(improved_plan, inputs)
```

## Tests

### Unit Test Example

```python
def test_budget_enforcement():
    """Test budget enforcement"""
    step = Step(
        name="test_step",
        role=RoleType.BUILDER,
        budget=Budget(tokens=1000, time=10, tools=1)
    )
    
    # Should pass
    result = execute_step(step, inputs={})
    assert result.status == StepStatus.COMPLETED
    
    # Should fail (budget exceeded)
    step.budget.tokens_limit = 100
    with pytest.raises(BudgetExceeded):
        execute_step(step, inputs={})
```

### Integration Test Example

```python
def test_complete_pipeline():
    """End-to-end plan execution"""
    plan = compile_plan("""
        pipeline test {
            step retrieve: Retriever(query="test", budget=1k)
            step build: Builder(input=retrieve.context, budget=2k)
            gate quality: check(build.artifact is not None)
        }
    """)
    
    result = execute_plan(plan, inputs={})
    
    assert result.status == "SUCCESS"
    assert "retrieve" in result.outputs
    assert "build" in result.outputs
```

## Performance Optimization

### Parallel Execution

```python
def execute_parallel(plan: ExecutionPlan, inputs: Dict[str, Any]) -> ExecutionResult:
    """Execute independent steps in parallel"""
    
    execution_order = topological_sort(plan.dag)
    
    # Group steps by dependency level
    dependency_levels = group_by_dependency_level(execution_order)
    
    # Execute each level in parallel
    step_outputs = {}
    for level in dependency_levels:
        # Execute all steps in this level concurrently
        results = execute_concurrently(level, step_outputs, inputs)
        step_outputs.update(results)
    
    return ExecutionResult(status="SUCCESS", outputs=step_outputs)
```

## Migration & Cutover Notes

### T→L Rename Strategy

After review and acceptance:
1. Run validation gate: `knowledge_architecture/validation/T0_T6_DOCUMENTATION.validation.md`
2. Get reviewer sign-off (Braden)
3. Backup L-level files: `mv L*.md L*.md.backup`
4. Rename T-level files: `mv T0_executive.md L0_executive.md` (repeat for T1-T6)
5. Update references in indices/maps
6. Run post-cutover validation
7. Archive old L-level files

### Post-Cutover Validation Checklist

- [ ] All T-level files renamed to L-level
- [ ] Indices updated to reference new L-level paths
- [ ] System maps updated
- [ ] Validation gates pass
- [ ] No broken links
- [ ] Old L-level files archived
- [ ] Performance benchmarks still pass
- [ ] Plan compilation still works
- [ ] Execution still functional
- [ ] Gates still enforce correctly

## References

- System map: `systems/apoe/system.map.lucid.json5`
- Validation gates: `knowledge_architecture/validation/T0_T6_DOCUMENTATION.validation.md`
- Templates: `knowledge_architecture/PERFECT_TEMPLATES_LIBRARY.md`
- L-level docs: `systems/apoe/L0_executive.md` through `L4_complete.md`
- Implementation: `packages/apoe/` (139 tests passing ✅)
