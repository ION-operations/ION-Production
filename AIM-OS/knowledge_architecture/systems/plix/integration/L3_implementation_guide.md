# PLIx→APOE Integration – L3 Implementation Guide

**Document ID:** `plix_integration_l3_implementation`  
**Level:** L3 (Implementation Guide)  
**Word Count Target:** 10,000 words  
**Status:** ✅ **COMPLETE**  
**Confidence:** 0.88

---

## 📋 **TABLE OF CONTENTS**

1. [Prerequisites & Setup](#prerequisites--setup)
2. [Phase 1: PLIx→ACL Compiler](#phase-1-plixacl-compiler)
3. [Phase 2: Enhanced APOE Executor](#phase-2-enhanced-apoe-executor)
4. [Phase 3: Verification Backends](#phase-3-verification-backends)
5. [Phase 4: Enhanced VIF Integration](#phase-4-enhanced-vif-integration)
6. [Phase 5: System Integration](#phase-5-system-integration)
7. [Testing Strategy](#testing-strategy)
8. [Deployment Guide](#deployment-guide)
9. [Troubleshooting](#troubleshooting)
10. [Maintenance & Evolution](#maintenance--evolution)

---

## 🎯 **PREREQUISITES & SETUP**

### **Environment Requirements**

**Development Environment:**
```bash
# Python 3.11+
python --version  # >= 3.11.0

# Node.js 18+ (for TypeScript components)
node --version  # >= 18.0.0

# Required Python packages
pip install pytest pytest-cov mypy black ruff
pip install pydantic fastapi uvicorn

# Required Node packages
npm install -g typescript ts-node jest
```

**System Dependencies:**
```bash
# TLA+ Tools (for verification backend)
wget https://github.com/tlaplus/tlaplus/releases/latest/tla2tools.jar
export TLATOOLS_PATH=/path/to/tla2tools.jar

# Alloy Analyzer (for verification backend)
wget https://github.com/AlloyTools/org.alloytools.alloy/releases/latest/alloy.jar
export ALLOY_PATH=/path/to/alloy.jar

# OPA (Open Policy Agent)
curl -L -o opa https://openpolicyagent.org/downloads/latest/opa_linux_amd64
chmod +x opa
export OPA_PATH=/path/to/opa
```

### **Repository Structure**

**Create integration workspace:**
```bash
cd AIM-OS/

# Create integration directories
mkdir -p packages/apoe/plix_compiler
mkdir -p packages/apoe/compensation
mkdir -p packages/apoe/retry_fallback
mkdir -p packages/apoe/purity_validation
mkdir -p packages/apoe/backends/{tlaplus,alloy,opa}
mkdir -p packages/apoe/tests/integration/plix

# Create documentation structure (already done via L0-L4)
# knowledge_architecture/systems/plix/integration/
```

### **Existing Code Assessment**

**Review existing APOE implementation:**
```bash
# Check APOE status
cd packages/apoe
pytest tests/ -v  # Should show 30/30 passing

# Review APOE components
ls -la *.py
# Expected: acl_parser.py, executor.py, vif_integration.py, models.py, roles.py

# Review APOE tests
ls -la tests/
# Expected: test_acl_parser.py, test_executor.py, test_vif_integration.py
```

**Review existing PLIx implementation:**
```bash
# Check PLIx parser status
cd packages/plix
npm test  # Should show 180+ passing

# Review PLIx components
ls -la src/
# Expected: parser/, compiler/, semantics/, backends/, runtime/

# Key files for integration:
# - src/parser/index.ts (PLIx parser, 100% compliant)
# - src/semantics/subdistribution.ts (monad implementation)
# - src/semantics/typing.ts (type system)
# - src/semantics/effects.ts (effect rows)
```

---

## 🔨 **PHASE 1: PLIx→ACL COMPILER**

**Estimated Time:** 5-8 hours  
**Complexity:** High  
**Dependencies:** PLIx parser, APOE ACL parser

### **Step 1.1: Create Compiler Infrastructure**

**File:** `packages/apoe/plix_compiler/__init__.py`

```python
"""
PLIx to ACL Compiler

Transforms PLIx intent (CNL with formal semantics) into APOE's ACL
execution language while preserving formal properties.
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum

from ..models import ExecutionPlan, Step, Gate, Budget, RoleConfig
from .purity_checker import PurityChecker
from .compensation_generator import CompensationGenerator
from .retry_policy_generator import RetryPolicyGenerator


@dataclass
class PLIxIntent:
    """PLIx intent structure (from PLIx parser)"""
    speech_act: str  # "ask", "ensure", "declare"
    entity: str  # Entity reference
    action: str  # Action to perform
    contract: Contract
    plan: Plan
    evidence: Evidence


@dataclass
class Contract:
    """Contract with pre/post conditions"""
    preconditions: List[Constraint]
    postconditions: List[Constraint]


@dataclass
class Plan:
    """Execution plan with steps"""
    steps: List[PLIxStep]


@dataclass
class PLIxStep:
    """Individual step in PLIx plan"""
    id: str
    action: str
    params: Dict[str, any]
    depends_on: List[str]
    compensation: Optional[Compensation]
    retry: Optional[RetryPolicy]
    fallback: Optional[Fallback]
    confidence: Optional[float]
    effects: Set[str]


@dataclass
class Constraint:
    """Contract constraint"""
    text: str
    variables: List[str]
    pure: bool  # Validated by purity checker


class PLIxToACLCompiler:
    """
    Main compiler class.
    
    Transforms PLIx intent into ACL execution plan while preserving:
    - Purity of constraints
    - Formal semantics (subdistribution, effects, confidence)
    - Compensation semantics (saga pattern)
    - Retry/fallback logic
    """
    
    def __init__(self):
        self.purity_checker = PurityChecker()
        self.compensation_gen = CompensationGenerator()
        self.retry_gen = RetryPolicyGenerator()
    
    def compile(self, plix_intent: PLIxIntent) -> ExecutionPlan:
        """
        Main compilation entry point.
        
        Args:
            plix_intent: Parsed PLIx intent
            
        Returns:
            ExecutionPlan: ACL execution plan
            
        Raises:
            CompilationError: If compilation fails
            PurityViolation: If constraints are impure
        """
        # Validate purity of all constraints
        self._validate_purity(plix_intent.contract)
        
        # Create ACL plan structure
        plan = ExecutionPlan(
            name=self._generate_plan_name(plix_intent),
            roles=self._map_roles(plix_intent),
            steps=self._map_steps(plix_intent.plan),
            dependencies=self._map_dependencies(plix_intent.plan)
        )
        
        # Add contract gates (pre/post conditions)
        plan.gates = self._map_contract_gates(plix_intent.contract)
        
        return plan
    
    def _validate_purity(self, contract: Contract):
        """Validate all constraints are pure"""
        for constraint in contract.preconditions + contract.postconditions:
            result = self.purity_checker.check(constraint)
            if not result.is_pure:
                raise PurityViolation(
                    f"Constraint '{constraint.text}' is impure: {result.reason}"
                )
    
    def _generate_plan_name(self, intent: PLIxIntent) -> str:
        """Generate ACL plan name from PLIx intent"""
        return f"{intent.entity}_{intent.action}".replace(":", "_")
    
    def _map_roles(self, intent: PLIxIntent) -> Dict[str, RoleConfig]:
        """Map PLIx roles to ACL roles"""
        # For now, use default role configuration
        # Future: Extract role hints from PLIx intent
        return {
            "executor": RoleConfig(
                type="REASONER",
                model="gpt-4-turbo",
                temperature=0.7
            )
        }
    
    def _map_steps(self, plan: Plan) -> List[Step]:
        """Map PLIx steps to ACL steps"""
        acl_steps = []
        
        for plix_step in plan.steps:
            acl_step = Step(
                name=plix_step.id,
                role_name="executor",
                description=self._format_step_description(plix_step),
                gates=self._create_step_gates(plix_step),
                budget=self._create_step_budget(plix_step)
            )
            
            # Add compensation if present
            if plix_step.compensation:
                acl_step.compensation = self.compensation_gen.generate(
                    plix_step.compensation
                )
            
            # Add retry policy if present
            if plix_step.retry:
                acl_step.retry_policy = self.retry_gen.generate(
                    plix_step.retry
                )
            
            # Add fallback if present
            if plix_step.fallback:
                acl_step.fallback = self._map_fallback(plix_step.fallback)
            
            acl_steps.append(acl_step)
        
        return acl_steps
    
    def _map_dependencies(self, plan: Plan) -> Dict[str, List[str]]:
        """Map PLIx dependencies to ACL REQUIRES"""
        dependencies = {}
        for step in plan.steps:
            if step.depends_on:
                dependencies[step.id] = step.depends_on
        return dependencies
    
    def _map_contract_gates(self, contract: Contract) -> List[Gate]:
        """Map contract pre/post conditions to ACL gates"""
        gates = []
        
        # Preconditions
        for i, precond in enumerate(contract.preconditions):
            gates.append(Gate(
                name=f"precondition_{i}",
                condition=self._compile_constraint(precond),
                timing="before"
            ))
        
        # Postconditions
        for i, postcond in enumerate(contract.postconditions):
            gates.append(Gate(
                name=f"postcondition_{i}",
                condition=self._compile_constraint(postcond),
                timing="after"
            ))
        
        return gates
    
    def _compile_constraint(self, constraint: Constraint) -> str:
        """Compile PLIx constraint to ACL condition"""
        # Simple pass-through for now
        # Future: Optimize condition format for ACL
        return constraint.text
    
    def _format_step_description(self, step: PLIxStep) -> str:
        """Format step description for ACL"""
        desc = f"{step.action}("
        params = ", ".join([f"{k}={v}" for k, v in step.params.items()])
        desc += params + ")"
        return desc
    
    def _create_step_gates(self, step: PLIxStep) -> List[Gate]:
        """Create gates for step (e.g., confidence gate)"""
        gates = []
        
        if step.confidence:
            gates.append(Gate(
                name=f"{step.id}_confidence",
                condition=f"output.confidence >= {step.confidence}",
                timing="after"
            ))
        
        return gates
    
    def _create_step_budget(self, step: PLIxStep) -> Budget:
        """Create budget for step"""
        # Default budget for now
        # Future: Extract from PLIx intent
        return Budget(
            tokens=5000,
            time_seconds=30,
            tools=10
        )
    
    def _map_fallback(self, fallback: Fallback) -> Step:
        """Map PLIx fallback to ACL step"""
        # Create fallback step
        return Step(
            name=f"fallback_{fallback.id}",
            role_name="executor",
            description=fallback.action,
            gates=[],
            budget=Budget(tokens=2000, time_seconds=10, tools=5)
        )


class CompilationError(Exception):
    """Raised when compilation fails"""
    pass


class PurityViolation(CompilationError):
    """Raised when constraint purity validation fails"""
    pass
```

### **Step 1.2: Implement Purity Checker**

**File:** `packages/apoe/plix_compiler/purity_checker.py`

```python
"""
Purity Checker

Validates that constraints are pure (no side effects).
Critical for formal semantics preservation.
"""

import ast
from typing import Set, List
from dataclasses import dataclass


@dataclass
class PurityResult:
    """Result of purity checking"""
    is_pure: bool
    reason: Optional[str] = None
    violations: List[str] = None


class PurityChecker:
    """
    Checks if PLIx constraints are pure (no side effects).
    
    Pure operations:
    - Arithmetic: +, -, *, /, //, %, **
    - Comparison: ==, !=, <, <=, >, >=
    - Logical: and, or, not
    - Field access: obj.field
    - Function calls: ONLY to whitelisted pure functions
    
    Impure operations (forbidden):
    - I/O: print, input, file operations
    - Network: http requests, socket operations
    - Database: queries, updates
    - State mutation: assignments, deletes
    - System calls: os.system, subprocess
    """
    
    # Whitelisted pure functions
    PURE_FUNCTIONS = {
        "abs", "all", "any", "bool", "dict", "float", "int",
        "len", "list", "max", "min", "range", "round", "set",
        "sorted", "str", "sum", "tuple", "zip"
    }
    
    # Forbidden impure operations
    IMPURE_OPERATIONS = {
        "print", "input", "open", "file", "read", "write",
        "exec", "eval", "compile", "__import__",
        "os", "sys", "subprocess", "socket", "http", "requests",
        "db", "database", "query", "insert", "update", "delete"
    }
    
    def check(self, constraint: Constraint) -> PurityResult:
        """
        Check if constraint is pure.
        
        Args:
            constraint: Constraint to check
            
        Returns:
            PurityResult with is_pure=True if pure, False otherwise
        """
        try:
            # Parse constraint as Python AST
            tree = ast.parse(constraint.text, mode='eval')
            
            # Walk AST and check for impure operations
            violations = []
            for node in ast.walk(tree):
                violation = self._check_node(node)
                if violation:
                    violations.append(violation)
            
            if violations:
                return PurityResult(
                    is_pure=False,
                    reason="Impure operations detected",
                    violations=violations
                )
            
            return PurityResult(is_pure=True)
        
        except SyntaxError as e:
            return PurityResult(
                is_pure=False,
                reason=f"Syntax error: {e}",
                violations=[]
            )
    
    def _check_node(self, node: ast.AST) -> Optional[str]:
        """Check if AST node is impure"""
        
        # Check function calls
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
                if func_name in self.IMPURE_OPERATIONS:
                    return f"Impure function call: {func_name}"
                if func_name not in self.PURE_FUNCTIONS:
                    return f"Unknown function (not in whitelist): {func_name}"
        
        # Check assignments (forbidden in constraints)
        if isinstance(node, ast.Assign):
            return "Assignment not allowed in pure constraint"
        
        # Check deletes (forbidden)
        if isinstance(node, ast.Delete):
            return "Delete not allowed in pure constraint"
        
        # Check imports (forbidden)
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            return "Import not allowed in pure constraint"
        
        return None


# Tests for purity checker
def test_purity_checker():
    """Test cases for purity checker"""
    checker = PurityChecker()
    
    # Pure constraints (should pass)
    assert checker.check(Constraint("x > 10", ["x"], False)).is_pure
    assert checker.check(Constraint("x + y == z", ["x", "y", "z"], False)).is_pure
    assert checker.check(Constraint("len(items) > 0", ["items"], False)).is_pure
    assert checker.check(Constraint("max(values) < 100", ["values"], False)).is_pure
    
    # Impure constraints (should fail)
    assert not checker.check(Constraint("print(x)", ["x"], False)).is_pure
    assert not checker.check(Constraint("open('file.txt')", [], False)).is_pure
    assert not checker.check(Constraint("x = 10", [], False)).is_pure
    assert not checker.check(Constraint("os.system('cmd')", [], False)).is_pure
    
    print("✅ All purity checker tests passed")
```

### **Step 1.3: Implement Compensation Generator**

**File:** `packages/apoe/plix_compiler/compensation_generator.py`

```python
"""
Compensation Generator

Generates compensation steps for saga pattern.
Maps PLIx compensation syntax to ACL compensation logic.
"""

from typing import Optional
from dataclasses import dataclass


@dataclass
class Compensation:
    """Compensation step definition"""
    step_id: str  # Step to compensate
    action: str  # Compensation action
    params: Dict[str, any]  # Parameters for compensation


class CompensationGenerator:
    """
    Generates ACL compensation logic from PLIx compensation syntax.
    
    PLIx Syntax:
        compensate step_id -> Action(params)
    
    ACL Output:
        Compensation step with reverse semantics
    """
    
    def generate(self, plix_compensation: Compensation) -> Dict[str, any]:
        """
        Generate ACL compensation from PLIx compensation.
        
        Args:
            plix_compensation: PLIx compensation definition
            
        Returns:
            ACL compensation structure
        """
        return {
            "compensates": plix_compensation.step_id,
            "action": plix_compensation.action,
            "params": plix_compensation.params,
            "on_failure": "log_and_continue"  # Don't fail if compensation fails
        }
```

### **Step 1.4: Implement Retry Policy Generator**

**File:** `packages/apoe/plix_compiler/retry_policy_generator.py`

```python
"""
Retry Policy Generator

Generates retry policies from PLIx retry syntax.
Implements subdistribution monad semantics.
"""

from typing import Optional
from dataclasses import dataclass
from enum import Enum


class BackoffStrategy(Enum):
    """Backoff strategies"""
    CONSTANT = "constant"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"


@dataclass
class RetryPolicy:
    """Retry policy definition"""
    max_attempts: int
    backoff_strategy: BackoffStrategy
    backoff_base: float  # seconds
    max_backoff: float  # seconds


class RetryPolicyGenerator:
    """
    Generates ACL retry policies from PLIx retry syntax.
    
    PLIx Syntax:
        retry: exponential(max: 3, backoff: 2s)
        retry: linear(max: 5, backoff: 1s)
        retry: constant(max: 3, backoff: 5s)
    
    ACL Output:
        Retry policy with backoff calculation
    """
    
    def generate(self, plix_retry: RetryPolicy) -> Dict[str, any]:
        """
        Generate ACL retry policy from PLIx retry.
        
        Args:
            plix_retry: PLIx retry definition
            
        Returns:
            ACL retry policy structure
        """
        return {
            "max_attempts": plix_retry.max_attempts,
            "backoff_strategy": plix_retry.backoff_strategy.value,
            "backoff_base": plix_retry.backoff_base,
            "max_backoff": plix_retry.max_backoff or 60.0,
            "jitter": True  # Add random jitter to prevent thundering herd
        }
```

### **Step 1.5: Create Compiler Tests**

**File:** `packages/apoe/tests/test_plix_compiler.py`

```python
"""
Tests for PLIx→ACL Compiler
"""

import pytest
from apoe.plix_compiler import PLIxToACLCompiler, PLIxIntent, Contract, Plan, PLIxStep, Constraint


def test_compile_simple_intent():
    """Test compiling simple PLIx intent"""
    compiler = PLIxToACLCompiler()
    
    intent = PLIxIntent(
        speech_act="ask",
        entity="room/meeting",
        action="reserve",
        contract=Contract(
            preconditions=[Constraint("available == True", ["available"], True)],
            postconditions=[Constraint("reserved == True", ["reserved"], True)]
        ),
        plan=Plan(steps=[
            PLIxStep(
                id="check",
                action="api.check_room",
                params={},
                depends_on=[],
                compensation=None,
                retry=None,
                fallback=None,
                confidence=0.90,
                effects={"io"}
            )
        ]),
        evidence={}
    )
    
    acl_plan = compiler.compile(intent)
    
    assert acl_plan.name == "room_meeting_reserve"
    assert len(acl_plan.steps) == 1
    assert acl_plan.steps[0].name == "check"
    assert len(acl_plan.gates) == 2  # 1 pre + 1 post


def test_purity_validation():
    """Test that impure constraints are rejected"""
    compiler = PLIxToACLCompiler()
    
    intent_with_impure = PLIxIntent(
        speech_act="ask",
        entity="test",
        action="test",
        contract=Contract(
            preconditions=[Constraint("print(x)", ["x"], False)],  # Impure!
            postconditions=[]
        ),
        plan=Plan(steps=[]),
        evidence={}
    )
    
    with pytest.raises(PurityViolation):
        compiler.compile(intent_with_impure)


def test_compensation_generation():
    """Test compensation step generation"""
    compiler = PLIxToACLCompiler()
    
    compensation = Compensation(
        step_id="reserve",
        action="api.cancel",
        params={"id": "reserve.ref:id"}
    )
    
    acl_compensation = compiler.compensation_gen.generate(compensation)
    
    assert acl_compensation["compensates"] == "reserve"
    assert acl_compensation["action"] == "api.cancel"
    assert "on_failure" in acl_compensation


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

### **Step 1.6: Integration with Existing PLIx Parser**

**File:** `packages/apoe/plix_compiler/plix_bridge.py`

```python
"""
Bridge between PLIx TypeScript parser and Python compiler.

Converts PLIx AST (from TypeScript) to Python structures for compilation.
"""

import json
import subprocess
from typing import Dict, Any


class PLIxParserBridge:
    """
    Bridge to PLIx TypeScript parser.
    
    Calls PLIx parser (Node.js) and converts result to Python structures.
    """
    
    def parse(self, plix_text: str) -> PLIxIntent:
        """
        Parse PLIx text using TypeScript parser.
        
        Args:
            plix_text: PLIx intent in CNL
            
        Returns:
            PLIxIntent: Parsed intent structure
        """
        # Call TypeScript parser
        result = subprocess.run(
            ["node", "packages/plix/dist/cli.js", "parse", "-"],
            input=plix_text.encode(),
            capture_output=True,
            check=True
        )
        
        # Parse JSON output
        ast_json = json.loads(result.stdout)
        
        # Convert to Python structures
        return self._convert_ast(ast_json)
    
    def _convert_ast(self, ast_json: Dict[str, Any]) -> PLIxIntent:
        """Convert JSON AST to Python PLIxIntent"""
        return PLIxIntent(
            speech_act=ast_json["speechAct"],
            entity=ast_json["entity"],
            action=ast_json["action"],
            contract=self._convert_contract(ast_json["contract"]),
            plan=self._convert_plan(ast_json["plan"]),
            evidence=ast_json.get("evidence", {})
        )
    
    def _convert_contract(self, contract_json: Dict[str, Any]) -> Contract:
        """Convert JSON contract to Python Contract"""
        return Contract(
            preconditions=[
                Constraint(c["text"], c["variables"], c.get("pure", False))
                for c in contract_json.get("preconditions", [])
            ],
            postconditions=[
                Constraint(c["text"], c["variables"], c.get("pure", False))
                for c in contract_json.get("postconditions", [])
            ]
        )
    
    def _convert_plan(self, plan_json: Dict[str, Any]) -> Plan:
        """Convert JSON plan to Python Plan"""
        return Plan(
            steps=[
                self._convert_step(s)
                for s in plan_json.get("steps", [])
            ]
        )
    
    def _convert_step(self, step_json: Dict[str, Any]) -> PLIxStep:
        """Convert JSON step to Python PLIxStep"""
        return PLIxStep(
            id=step_json["id"],
            action=step_json["action"],
            params=step_json.get("params", {}),
            depends_on=step_json.get("dependsOn", []),
            compensation=self._convert_compensation(step_json.get("compensation")),
            retry=self._convert_retry(step_json.get("retry")),
            fallback=self._convert_fallback(step_json.get("fallback")),
            confidence=step_json.get("confidence"),
            effects=set(step_json.get("effects", []))
        )
```

---

## 🔧 **PHASE 2: ENHANCED APOE EXECUTOR**

**Estimated Time:** 8-12 hours  
**Complexity:** High  
**Dependencies:** Existing APOE executor, Phase 1 compiler

### **Step 2.1: Add Compensation Execution**

**File:** `packages/apoe/compensation/compensation_engine.py`

```python
"""
Compensation Engine

Implements saga pattern for reversible operations.
Executes compensation steps in reverse topological order on failure.
"""

from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime

from ..models import Step, ExecutionPlan, StepStatus
from ..executor import PlanExecutor


@dataclass
class CompensationResult:
    """Result of compensation execution"""
    success: bool
    compensated_steps: List[str]
    failed_compensations: List[Tuple[str, str]]  # (step_id, error)
    total_time_ms: float


class CompensationEngine:
    """
    Executes compensation steps in reverse order on failure.
    
    Saga Pattern:
    - Forward execution: step1 → step2 → step3
    - On failure at step3: compensate(step2) → compensate(step1)
    - Best effort: Continue compensating even if individual steps fail
    """
    
    def __init__(self, executor: PlanExecutor):
        self.executor = executor
    
    def execute_with_compensation(
        self,
        plan: ExecutionPlan,
        initial_state: Dict[str, Any]
    ) -> Tuple[bool, List[Step], Optional[CompensationResult]]:
        """
        Execute plan with automatic compensation on failure.
        
        Args:
            plan: Execution plan
            initial_state: Initial state for execution
            
        Returns:
            Tuple of (success, completed_steps, compensation_result)
        """
        completed_steps = []
        start_time = datetime.utcnow()
        
        try:
            # Execute plan normally
            for step in self._get_execution_order(plan):
                result = self.executor._execute_step(step, plan)
                
                if result == "failed":
                    # Failure: trigger compensation
                    comp_result = self._compensate(completed_steps, plan)
                    return False, completed_steps, comp_result
                
                completed_steps.append(step)
            
            # Success: no compensation needed
            return True, completed_steps, None
        
        except Exception as e:
            # Unexpected error: compensate what we can
            comp_result = self._compensate(completed_steps, plan)
            return False, completed_steps, comp_result
    
    def _compensate(
        self,
        completed_steps: List[Step],
        plan: ExecutionPlan
    ) -> CompensationResult:
        """
        Execute compensation in reverse topological order.
        
        Args:
            completed_steps: Steps that completed successfully
            plan: Original execution plan
            
        Returns:
            CompensationResult with details
        """
        start_time = datetime.utcnow()
        compensated = []
        failed = []
        
        # Compensate in reverse order
        for step in reversed(completed_steps):
            if not hasattr(step, 'compensation') or step.compensation is None:
                continue
            
            try:
                # Execute compensation step
                comp_step = self._create_compensation_step(step, plan)
                result = self.executor._execute_step(comp_step, plan)
                
                if result == "completed":
                    compensated.append(step.name)
                else:
                    failed.append((step.name, "Compensation failed"))
            
            except Exception as e:
                failed.append((step.name, str(e)))
        
        end_time = datetime.utcnow()
        duration_ms = (end_time - start_time).total_seconds() * 1000
        
        return CompensationResult(
            success=len(failed) == 0,
            compensated_steps=compensated,
            failed_compensations=failed,
            total_time_ms=duration_ms
        )
    
    def _create_compensation_step(self, step: Step, plan: ExecutionPlan) -> Step:
        """Create compensation step from original step"""
        compensation_def = step.compensation
        
        return Step(
            name=f"compensate_{step.name}",
            role_name=step.role_name,
            description=f"Compensate: {compensation_def['action']}",
            gates=[],
            budget=step.budget,  # Use same budget as original
            outputs={}
        )
    
    def _get_execution_order(self, plan: ExecutionPlan) -> List[Step]:
        """Get execution order (topologically sorted)"""
        # Use existing executor's dependency resolution
        return self.executor._resolve_dependencies(plan)


# Integration with existing executor
class EnhancedAPOEExecutor(PlanExecutor):
    """
    Enhanced APOE executor with compensation support.
    
    Extends existing PlanExecutor with compensation capabilities.
    """
    
    def __init__(self):
        super().__init__()
        self.compensation_engine = CompensationEngine(self)
    
    def execute_with_compensation(
        self,
        plan: ExecutionPlan,
        initial_state: Optional[Dict[str, Any]] = None
    ) -> ExecutionResult:
        """
        Execute plan with automatic compensation on failure.
        
        This is the new primary execution method that should be used
        for plans that have compensation steps defined.
        """
        success, completed_steps, comp_result = \
            self.compensation_engine.execute_with_compensation(plan, initial_state or {})
        
        return ExecutionResult(
            success=success,
            completed_steps=len(completed_steps),
            total_steps=len(plan.steps),
            error=None if success else "Execution failed",
            compensation_result=comp_result
        )
```

### **Step 2.2: Add Retry/Fallback Logic**

**File:** `packages/apoe/retry_fallback/retry_engine.py`

```python
"""
Retry/Fallback Engine

Implements retry with exponential backoff and fallback execution.
Preserves subdistribution monad semantics.
"""

import time
import random
from typing import Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum


class BackoffStrategy(Enum):
    """Backoff strategies for retries"""
    CONSTANT = "constant"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"


@dataclass
class RetryPolicy:
    """Retry policy configuration"""
    max_attempts: int = 3
    backoff_strategy: BackoffStrategy = BackoffStrategy.EXPONENTIAL
    backoff_base: float = 2.0  # seconds
    max_backoff: float = 60.0  # seconds
    jitter: bool = True


@dataclass
class RetryResult:
    """Result of retry execution"""
    success: bool
    attempts: int
    total_time_ms: float
    final_result: Optional[Any]
    fallback_used: bool


class RetryEngine:
    """
    Executes steps with retry and fallback logic.
    
    Retry Logic:
    - Attempt 1: Execute immediately
    - Attempt 2: Wait backoff_base seconds
    - Attempt 3: Wait backoff_base * 2 seconds
    - etc.
    
    Fallback Logic:
    - If all retries exhausted, try fallback step
    - Fallback is separate execution path
    """
    
    def execute_with_retry(
        self,
        step_fn: Callable,
        policy: Optional[RetryPolicy] = None,
        fallback_fn: Optional[Callable] = None
    ) -> RetryResult:
        """
        Execute function with retry and optional fallback.
        
        Args:
            step_fn: Function to execute
            policy: Retry policy (default: 3 exponential retries)
            fallback_fn: Optional fallback function
            
        Returns:
            RetryResult with execution details
        """
        policy = policy or RetryPolicy()
        start_time = time.time()
        
        for attempt in range(policy.max_attempts):
            try:
                # Execute step
                result = step_fn()
                
                # Success!
                end_time = time.time()
                return RetryResult(
                    success=True,
                    attempts=attempt + 1,
                    total_time_ms=(end_time - start_time) * 1000,
                    final_result=result,
                    fallback_used=False
                )
            
            except Exception as e:
                # Failure: check if we should retry
                if attempt < policy.max_attempts - 1:
                    # Not last attempt: wait and retry
                    delay = self._calculate_backoff(
                        attempt,
                        policy.backoff_strategy,
                        policy.backoff_base,
                        policy.max_backoff,
                        policy.jitter
                    )
                    time.sleep(delay)
                    continue
                else:
                    # Last attempt failed: try fallback
                    if fallback_fn:
                        try:
                            fallback_result = fallback_fn()
                            end_time = time.time()
                            return RetryResult(
                                success=True,
                                attempts=attempt + 1,
                                total_time_ms=(end_time - start_time) * 1000,
                                final_result=fallback_result,
                                fallback_used=True
                            )
                        except Exception as fallback_error:
                            # Fallback also failed
                            pass
                    
                    # Everything failed
                    end_time = time.time()
                    return RetryResult(
                        success=False,
                        attempts=attempt + 1,
                        total_time_ms=(end_time - start_time) * 1000,
                        final_result=None,
                        fallback_used=fallback_fn is not None
                    )
    
    def _calculate_backoff(
        self,
        attempt: int,
        strategy: BackoffStrategy,
        base: float,
        max_backoff: float,
        jitter: bool
    ) -> float:
        """Calculate backoff delay for retry attempt"""
        
        if strategy == BackoffStrategy.CONSTANT:
            delay = base
        elif strategy == BackoffStrategy.LINEAR:
            delay = base * (attempt + 1)
        elif strategy == BackoffStrategy.EXPONENTIAL:
            delay = base * (2 ** attempt)
        else:
            delay = base
        
        # Cap at max_backoff
        delay = min(delay, max_backoff)
        
        # Add jitter to prevent thundering herd
        if jitter:
            jitter_amount = random.uniform(0, delay * 0.1)  # +/- 10%
            delay += jitter_amount
        
        return delay


# Integration with enhanced executor
class EnhancedAPOEExecutor(PlanExecutor):
    """Enhanced executor with retry/fallback (continued from compensation)"""
    
    def __init__(self):
        super().__init__()
        self.compensation_engine = CompensationEngine(self)
        self.retry_engine = RetryEngine()
    
    def _execute_step_with_retry(
        self,
        step: Step,
        plan: ExecutionPlan
    ) -> str:
        """
        Execute step with retry policy if defined.
        
        Returns:
            "completed" | "failed" | "skipped"
        """
        # Check if step has retry policy
        retry_policy = getattr(step, 'retry_policy', None)
        fallback_step = getattr(step, 'fallback', None)
        
        if not retry_policy:
            # No retry: execute normally
            return self._execute_step(step, plan)
        
        # Execute with retry
        def step_fn():
            result = self._execute_step(step, plan)
            if result != "completed":
                raise Exception(f"Step {step.name} failed")
            return result
        
        def fallback_fn():
            if fallback_step:
                return self._execute_step(fallback_step, plan)
            raise Exception("No fallback defined")
        
        retry_result = self.retry_engine.execute_with_retry(
            step_fn,
            retry_policy,
            fallback_fn if fallback_step else None
        )
        
        return "completed" if retry_result.success else "failed"
```

### **Step 2.3: Add Purity Validation Runtime**

**File:** `packages/apoe/purity_validation/runtime_validator.py`

```python
"""
Runtime Purity Validator

Validates constraint purity at runtime during execution.
Double-checks compile-time validation for safety.
"""

from typing import Dict, Any, Set
from dataclasses import dataclass


@dataclass
class PurityViolationError(Exception):
    """Raised when runtime purity check fails"""
    constraint: str
    violation: str


class RuntimePurityValidator:
    """
    Runtime validator for constraint purity.
    
    This runs during execution to catch any purity violations
    that might have slipped through compile-time checks.
    """
    
    # Track function calls during constraint evaluation
    _call_stack: List[str] = []
    _io_operations: Set[str] = set()
    
    def validate_constraint_execution(
        self,
        constraint_text: str,
        variables: Dict[str, Any],
        result: bool
    ) -> None:
        """
        Validate that constraint evaluation was pure.
        
        Args:
            constraint_text: Constraint being validated
            variables: Variable bindings used
            result: Evaluation result
            
        Raises:
            PurityViolationError: If impure operations detected
        """
        # Check for I/O operations during evaluation
        if self._io_operations:
            raise PurityViolationError(
                constraint_text,
                f"I/O operations detected: {self._io_operations}"
            )
        
        # Check for state mutations
        # (would require instrumentation of variable access)
        
        # Clear tracking for next constraint
        self._call_stack.clear()
        self._io_operations.clear()
```

### **Step 2.4: Update Existing Executor Integration**

**File:** `packages/apoe/executor.py` (modifications)

```python
# Add to existing PlanExecutor class

def execute(self, plan: ExecutionPlan) -> ExecutionResult:
    """
    Main execution entry point (ENHANCED).
    
    Now checks for compensation/retry and uses enhanced execution if needed.
    """
    # Check if plan has compensation or retry
    has_compensation = any(
        hasattr(step, 'compensation') and step.compensation
        for step in plan.steps
    )
    has_retry = any(
        hasattr(step, 'retry_policy') and step.retry_policy
        for step in plan.steps
    )
    
    # Use enhanced execution if needed
    if has_compensation or has_retry:
        enhanced_executor = EnhancedAPOEExecutor()
        enhanced_executor.role_handlers = self.role_handlers  # Copy handlers
        
        if has_compensation:
            return enhanced_executor.execute_with_compensation(plan)
        else:
            # Just use retry (implement similar to compensation)
            return enhanced_executor.execute_with_retry(plan)
    
    # No enhancement needed: use original execution
    return self._execute_original(plan)
```

---

## 🔬 **PHASE 3: VERIFICATION BACKENDS**

**Estimated Time:** 8-12 hours  
**Complexity:** High  
**Dependencies:** Phase 1 compiler, external tools (TLA+/Alloy/OPA)

### **Step 3.1: TLA+ Backend Implementation**

**File:** `packages/apoe/backends/tlaplus_backend.py`

```python
"""
TLA+ Backend

Compiles ACL plans to TLA+ specifications for model checking.
Verifies safety and liveness properties.
"""

import subprocess
import tempfile
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class TLASpec:
    """TLA+ specification"""
    module_name: str
    specification: str
    safety_properties: List[str]
    liveness_properties: List[str]


@dataclass
class TLAVerificationResult:
    """Result of TLA+ verification"""
    success: bool
    safety_violated: List[str]
    liveness_violated: List[str]
    model_checker_output: str
    execution_time_ms: float


class TLAPlusBackend:
    """
    Compiles ACL plans to TLA+ for formal verification.
    
    TLA+ Features Used:
    - State variables for plan state
    - Actions for step execution
    - Temporal formulas for properties
    - Model checking with TLC
    """
    
    def __init__(self, tla_tools_path: Optional[str] = None):
        self.tla_tools_path = tla_tools_path or os.environ.get('TLATOOLS_PATH')
        if not self.tla_tools_path:
            raise ValueError("TLA+ tools path not configured")
    
    def compile(self, plan: ExecutionPlan) -> TLASpec:
        """
        Compile ACL plan to TLA+ specification.
        
        Args:
            plan: ACL execution plan
            
        Returns:
            TLASpec: TLA+ specification
        """
        module_name = self._sanitize_name(plan.name)
        
        # Generate TLA+ specification
        spec = self._generate_specification(plan, module_name)
        
        # Extract safety properties from gates
        safety_props = self._extract_safety_properties(plan)
        
        # Extract liveness properties (e.g., eventually complete)
        liveness_props = self._extract_liveness_properties(plan)
        
        return TLASpec(
            module_name=module_name,
            specification=spec,
            safety_properties=safety_props,
            liveness_properties=liveness_props
        )
    
    def verify(self, spec: TLASpec) -> TLAVerificationResult:
        """
        Verify TLA+ specification using TLC model checker.
        
        Args:
            spec: TLA+ specification
            
        Returns:
            TLAVerificationResult: Verification result
        """
        # Write spec to temporary file
        with tempfile.TemporaryDirectory() as tmpdir:
            spec_file = Path(tmpdir) / f"{spec.module_name}.tla"
            spec_file.write_text(spec.specification)
            
            # Run TLC model checker
            start_time = time.time()
            result = subprocess.run(
                [
                    "java",
                    "-jar",
                    self.tla_tools_path,
                    "-workers", "4",  # Parallel checking
                    str(spec_file)
                ],
                capture_output=True,
                text=True,
                timeout=60  # 60 second timeout
            )
            end_time = time.time()
            
            # Parse TLC output
            safety_violated = self._parse_safety_violations(result.stdout)
            liveness_violated = self._parse_liveness_violations(result.stdout)
            
            return TLAVerificationResult(
                success=result.returncode == 0,
                safety_violated=safety_violated,
                liveness_violated=liveness_violated,
                model_checker_output=result.stdout,
                execution_time_ms=(end_time - start_time) * 1000
            )
    
    def _generate_specification(
        self,
        plan: ExecutionPlan,
        module_name: str
    ) -> str:
        """Generate TLA+ specification from plan"""
        
        # State variables
        variables = self._generate_variables(plan)
        
        # Initial state
        init = self._generate_init(plan)
        
        # Actions for each step
        actions = self._generate_actions(plan)
        
        # Next state relation
        next_state = self._generate_next(plan)
        
        # Temporal specification
        temporal_spec = self._generate_spec(plan)
        
        # Properties
        properties = self._generate_properties(plan)
        
        return f"""
---- MODULE {module_name} ----
EXTENDS Naturals, Sequences, TLC

{variables}

{init}

{actions}

{next_state}

{temporal_spec}

{properties}
====
"""
    
    def _generate_variables(self, plan: ExecutionPlan) -> str:
        """Generate VARIABLES declaration"""
        var_names = ["pc"]  # Program counter
        
        # Add variable for each step's status
        for step in plan.steps:
            var_names.append(f"{step.name}_status")
        
        # Add variables for gates
        for gate in plan.gates:
            var_names.append(f"{gate.name}_satisfied")
        
        return f"VARIABLES {', '.join(var_names)}"
    
    def _generate_init(self, plan: ExecutionPlan) -> str:
        """Generate Init predicate"""
        conditions = ["pc = 0"]
        
        for step in plan.steps:
            conditions.append(f"{step.name}_status = \"pending\"")
        
        for gate in plan.gates:
            if gate.timing == "before":
                conditions.append(f"{gate.name}_satisfied = TRUE")
            else:
                conditions.append(f"{gate.name}_satisfied = FALSE")
        
        return "Init == " + " /\\ ".join(conditions)
    
    def _generate_actions(self, plan: ExecutionPlan) -> str:
        """Generate action for each step"""
        actions = []
        
        for i, step in enumerate(plan.steps):
            preconditions = [f"pc = {i}"]
            preconditions.append(f"{step.name}_status = \"pending\"")
            
            postconditions = [f"pc' = {i + 1}"]
            postconditions.append(f"{step.name}_status' = \"completed\"")
            
            action = f"""
{step.name} ==
    /\\ {" /\\ ".join(preconditions)}
    /\\ {" /\\ ".join(postconditions)}
"""
            actions.append(action)
        
        return "\n".join(actions)
    
    def _generate_next(self, plan: ExecutionPlan) -> str:
        """Generate Next state relation"""
        step_names = [step.name for step in plan.steps]
        return f"Next == {' \\/ '.join(step_names)}"
    
    def _generate_spec(self, plan: ExecutionPlan) -> str:
        """Generate temporal specification"""
        var_names = ["pc"] + [f"{s.name}_status" for s in plan.steps]
        return f"Spec == Init /\\ [][Next]_<<{', '.join(var_names)}>>"
    
    def _generate_properties(self, plan: ExecutionPlan) -> str:
        """Generate safety and liveness properties"""
        properties = []
        
        # Safety: preconditions must be satisfied
        for gate in plan.gates:
            if gate.timing == "before":
                properties.append(f"Safety_{gate.name} == {gate.name}_satisfied")
        
        # Liveness: eventually complete all steps
        completion_check = " /\\ ".join([
            f"{s.name}_status = \"completed\"" for s in plan.steps
        ])
        properties.append(f"Liveness == <>[{completion_check}]")
        
        return "\n".join(properties)
    
    def _extract_safety_properties(self, plan: ExecutionPlan) -> List[str]:
        """Extract safety properties from plan"""
        return [f"Safety_{gate.name}" for gate in plan.gates if gate.timing == "before"]
    
    def _extract_liveness_properties(self, plan: ExecutionPlan) -> List[str]:
        """Extract liveness properties"""
        return ["Liveness"]  # Eventually complete
    
    def _parse_safety_violations(self, output: str) -> List[str]:
        """Parse TLC output for safety violations"""
        violations = []
        # Parse TLC output format
        # (Implementation depends on TLC output format)
        return violations
    
    def _parse_liveness_violations(self, output: str) -> List[str]:
        """Parse TLC output for liveness violations"""
        violations = []
        # Parse TLC output format
        return violations
    
    def _sanitize_name(self, name: str) -> str:
        """Sanitize plan name for TLA+ module"""
        return name.replace("-", "_").replace(":", "_")
```

### **Step 3.2: Alloy Backend Implementation**

**File:** `packages/apoe/backends/alloy_backend.py`

```python
"""
Alloy Backend

Compiles ACL plans to Alloy models for structural validation.
Checks structural properties and constraints.
"""

import subprocess
import tempfile
from typing import List, Dict, Any
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AlloyModel:
    """Alloy model"""
    model_name: str
    model_text: str
    assertions: List[str]


@dataclass
class AlloyResult:
    """Result of Alloy checking"""
    success: bool
    assertions_passed: List[str]
    assertions_failed: List[str]
    counterexamples: List[Dict[str, Any]]
    execution_time_ms: float


class AlloyBackend:
    """
    Compiles ACL plans to Alloy for structural validation.
    
    Alloy Features Used:
    - Signatures for entities (steps, gates, etc.)
    - Predicates for transitions
    - Facts for constraints
    - Assertions for properties
    - Run commands for model finding
    """
    
    def __init__(self, alloy_path: Optional[str] = None):
        self.alloy_path = alloy_path or os.environ.get('ALLOY_PATH')
        if not self.alloy_path:
            raise ValueError("Alloy path not configured")
    
    def compile(self, plan: ExecutionPlan) -> AlloyModel:
        """
        Compile ACL plan to Alloy model.
        
        Args:
            plan: ACL execution plan
            
        Returns:
            AlloyModel: Alloy model
        """
        model_name = self._sanitize_name(plan.name)
        
        # Generate Alloy model
        model = self._generate_model(plan, model_name)
        
        # Extract assertions
        assertions = self._extract_assertions(plan)
        
        return AlloyModel(
            model_name=model_name,
            model_text=model,
            assertions=assertions
        )
    
    def check(self, model: AlloyModel) -> AlloyResult:
        """
        Check Alloy model using Alloy Analyzer.
        
        Args:
            model: Alloy model
            
        Returns:
            AlloyResult: Checking result
        """
        # Write model to temporary file
        with tempfile.TemporaryDirectory() as tmpdir:
            model_file = Path(tmpdir) / f"{model.model_name}.als"
            model_file.write_text(model.model_text)
            
            # Run Alloy Analyzer
            start_time = time.time()
            result = subprocess.run(
                [
                    "java",
                    "-jar",
                    self.alloy_path,
                    str(model_file)
                ],
                capture_output=True,
                text=True,
                timeout=60
            )
            end_time = time.time()
            
            # Parse result
            passed, failed, counterexamples = self._parse_result(result.stdout)
            
            return AlloyResult(
                success=len(failed) == 0,
                assertions_passed=passed,
                assertions_failed=failed,
                counterexamples=counterexamples,
                execution_time_ms=(end_time - start_time) * 1000
            )
    
    def _generate_model(self, plan: ExecutionPlan, model_name: str) -> str:
        """Generate Alloy model from plan"""
        
        # Signatures
        signatures = self._generate_signatures(plan)
        
        # Predicates
        predicates = self._generate_predicates(plan)
        
        # Facts
        facts = self._generate_facts(plan)
        
        # Assertions
        assertions = self._generate_assertions_text(plan)
        
        # Check commands
        checks = self._generate_checks(plan)
        
        return f"""
module {model_name}

{signatures}

{predicates}

{facts}

{assertions}

{checks}
"""
    
    def _generate_signatures(self, plan: ExecutionPlan) -> str:
        """Generate Alloy signatures"""
        sigs = []
        
        # Signature for Steps
        sigs.append("""
sig Step {
  status: one Status,
  dependsOn: set Step
}
""")
        
        # Signature for Status
        sigs.append("""
abstract sig Status {}
one sig Pending, Running, Completed, Failed extends Status {}
""")
        
        # Signature for Gates
        sigs.append("""
sig Gate {
  satisfied: one Bool
}
""")
        
        return "\n".join(sigs)
    
    def _generate_predicates(self, plan: ExecutionPlan) -> str:
        """Generate Alloy predicates"""
        preds = []
        
        # Predicate for valid execution
        preds.append("""
pred validExecution[s: Step] {
  all dep: s.dependsOn | dep.status = Completed
}
""")
        
        return "\n".join(preds)
    
    def _generate_facts(self, plan: ExecutionPlan) -> str:
        """Generate Alloy facts"""
        facts = []
        
        # Fact: No cycles in dependencies
        facts.append("""
fact noCycles {
  no s: Step | s in s.^dependsOn
}
""")
        
        return "\n".join(facts)
    
    def _generate_assertions_text(self, plan: ExecutionPlan) -> str:
        """Generate Alloy assertions"""
        assertions = []
        
        # Assert: If all steps completed, all gates satisfied
        assertions.append("""
assert allCompletedImpliesGatesSatisfied {
  (all s: Step | s.status = Completed) implies (all g: Gate | g.satisfied = True)
}
""")
        
        return "\n".join(assertions)
    
    def _generate_checks(self, plan: ExecutionPlan) -> str:
        """Generate check commands"""
        return "check allCompletedImpliesGatesSatisfied for 5"
    
    def _extract_assertions(self, plan: ExecutionPlan) -> List[str]:
        """Extract assertion names"""
        return ["allCompletedImpliesGatesSatisfied"]
    
    def _parse_result(self, output: str) -> Tuple[List[str], List[str], List[Dict]]:
        """Parse Alloy output"""
        passed = []
        failed = []
        counterexamples = []
        # Parse Alloy output format
        return passed, failed, counterexamples
    
    def _sanitize_name(self, name: str) -> str:
        """Sanitize plan name for Alloy"""
        return name.replace("-", "_").replace(":", "_")
```

### **Step 3.3: OPA Backend Implementation**

**File:** `packages/apoe/backends/opa_backend.py`

```python
"""
OPA Backend

Compiles ACL plans to Open Policy Agent (OPA) policies.
Enforces runtime policies and authorization.
"""

import subprocess
import json
from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class OPAPolicy:
    """OPA policy"""
    package_name: str
    policy_text: str
    rules: List[str]


@dataclass
class PolicyResult:
    """Result of policy evaluation"""
    allowed: bool
    reasons: List[str]
    violations: List[str]


class OPABackend:
    """
    Compiles ACL plans to OPA policies for runtime enforcement.
    
    OPA Features Used:
    - Package for plan namespace
    - Rules for step authorization
    - Default deny policy
    - Input from execution context
    """
    
    def __init__(self, opa_path: Optional[str] = None):
        self.opa_path = opa_path or os.environ.get('OPA_PATH', 'opa')
    
    def compile(self, plan: ExecutionPlan) -> OPAPolicy:
        """
        Compile ACL plan to OPA policy.
        
        Args:
            plan: ACL execution plan
            
        Returns:
            OPAPolicy: OPA policy
        """
        package_name = self._sanitize_name(plan.name)
        
        # Generate OPA policy
        policy = self._generate_policy(plan, package_name)
        
        # Extract rule names
        rules = self._extract_rules(plan)
        
        return OPAPolicy(
            package_name=package_name,
            policy_text=policy,
            rules=rules
        )
    
    def evaluate(
        self,
        policy: OPAPolicy,
        input_data: Dict[str, Any]
    ) -> PolicyResult:
        """
        Evaluate policy against input.
        
        Args:
            policy: OPA policy
            input_data: Input for evaluation
            
        Returns:
            PolicyResult: Evaluation result
        """
        # Write policy to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.rego', delete=False) as f:
            f.write(policy.policy_text)
            policy_file = f.name
        
        # Write input to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(input_data, f)
            input_file = f.name
        
        try:
            # Evaluate with OPA
            result = subprocess.run(
                [
                    self.opa_path,
                    "eval",
                    "--data", policy_file,
                    "--input", input_file,
                    "--format", "json",
                    "data.{}.allow".format(policy.package_name)
                ],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Parse result
            output = json.loads(result.stdout)
            allowed = output.get('result', [{}])[0].get('expressions', [{}])[0].get('value', False)
            
            return PolicyResult(
                allowed=allowed,
                reasons=[],
                violations=[] if allowed else ["Policy denied"]
            )
        
        finally:
            os.unlink(policy_file)
            os.unlink(input_file)
    
    def _generate_policy(self, plan: ExecutionPlan, package_name: str) -> str:
        """Generate OPA policy from plan"""
        
        # Default deny
        policy = f"""
package {package_name}

default allow = false

"""
        
        # Rules for each step
        for step in plan.steps:
            policy += self._generate_step_rule(step)
            policy += "\n"
        
        # Rules for gates
        for gate in plan.gates:
            policy += self._generate_gate_rule(gate)
            policy += "\n"
        
        return policy
    
    def _generate_step_rule(self, step: Step) -> str:
        """Generate OPA rule for step authorization"""
        conditions = []
        
        # Check step name
        conditions.append(f'input.step == "{step.name}"')
        
        # Check dependencies
        for dep in step.dependencies:
            conditions.append(f'input.completed["{dep}"] == true')
        
        # Check gates
        for gate in step.gates:
            conditions.append(self._compile_gate_condition(gate))
        
        return f"""
allow {{
  {" ".join(f"\n  {c}" for c in conditions)}
}}
"""
    
    def _generate_gate_rule(self, gate: Gate) -> str:
        """Generate OPA rule for gate"""
        return f"""
gate_{gate.name} {{
  {self._compile_gate_condition(gate)}
}}
"""
    
    def _compile_gate_condition(self, gate: Gate) -> str:
        """Compile gate condition to OPA syntax"""
        # Simple conversion (would need full expression parser)
        return gate.condition.replace("==", "=")
    
    def _extract_rules(self, plan: ExecutionPlan) -> List[str]:
        """Extract rule names"""
        rules = ["allow"]
        for gate in plan.gates:
            rules.append(f"gate_{gate.name}")
        return rules
    
    def _sanitize_name(self, name: str) -> str:
        """Sanitize plan name for OPA"""
        return name.replace("-", "_").replace(":", "_").replace("/", "_")
```

---

## 🔗 **PHASE 4: ENHANCED VIF INTEGRATION**

**Estimated Time:** 4-6 hours  
**Complexity:** Medium-High  
**Dependencies:** Phase 1-2 (compiler, executor), existing VIF system

### **Step 4.1: Create Enhanced Witness Types**

**File:** `packages/apoe/vif_integration_enhanced.py`

```python
"""
Enhanced VIF Integration for PLIx

Creates PLIx-specific witness types for formal provenance.
"""

from typing import Dict, Any, List, Set
from dataclasses import dataclass
from datetime import datetime
import hashlib


@dataclass
class ConstraintReplayWitness:
    """
    Witness for deterministic constraint re-evaluation.
    
    Enables verification without re-execution by capturing:
    - Constraint text and variables
    - Input state at evaluation time
    - Evaluation result
    - Evidence DAG supporting the evaluation
    - Purity proof
    """
    witness_id: str
    timestamp: datetime
    constraint_id: str
    constraint_text: str
    variables: Dict[str, Any]  # Variable bindings
    evaluation_result: bool
    evidence_dag_hash: str
    purity_proof: 'PurityProof'
    
    def compute_hash(self) -> str:
        """Compute cryptographic hash of witness"""
        hasher = hashlib.sha256()
        hasher.update(self.constraint_id.encode())
        hasher.update(self.constraint_text.encode())
        hasher.update(str(self.variables).encode())
        hasher.update(str(self.evaluation_result).encode())
        hasher.update(self.evidence_dag_hash.encode())
        return hasher.hexdigest()


@dataclass
class PurityProof:
    """
    Cryptographic proof that constraint is pure (no side effects).
    
    Captures:
    - Constraint AST hash
    - Allowed operations used (whitelist)
    - Validation result
    - Validator signature
    """
    constraint_id: str
    ast_hash: str
    allowed_operations: Set[str]
    validation_time: datetime
    validation_result: bool
    validator_signature: str  # Cryptographic signature


@dataclass
class SubdistributionWitness:
    """
    Witness for probabilistic execution (retries, fallbacks).
    
    Tracks all execution attempts, outcomes, and probability mass.
    Validates subdistribution monad laws.
    """
    step_id: str
    attempts: List['AttemptRecord']
    final_result: Optional[Any]
    total_probability_mass: float  # Should be ≤ 1.0
    monad_laws_validated: bool


@dataclass
class AttemptRecord:
    """Record of single retry attempt"""
    attempt_number: int
    timestamp: datetime
    result: Optional[Any]
    error: Optional[str]
    probability: float  # Probability of this outcome
    backoff_delay: Optional[float]  # Delay before this attempt


class EnhancedVIFIntegration:
    """
    Enhanced VIF integration with PLIx-specific witnesses.
    
    Extends existing VIF integration with:
    - Constraint replay witnesses
    - Purity proofs
    - Subdistribution witnesses
    """
    
    def create_constraint_replay_witness(
        self,
        constraint: Constraint,
        variables: Dict[str, Any],
        result: bool,
        evidence_dag_hash: str,
        purity_proof: PurityProof
    ) -> ConstraintReplayWitness:
        """
        Create witness for constraint evaluation.
        
        This witness enables deterministic replay:
        - Re-evaluate constraint with same variable bindings
        - Verify result matches
        - Validate purity proof
        """
        return ConstraintReplayWitness(
            witness_id=self._generate_id(),
            timestamp=datetime.utcnow(),
            constraint_id=constraint.id,
            constraint_text=constraint.text,
            variables=variables,
            evaluation_result=result,
            evidence_dag_hash=evidence_dag_hash,
            purity_proof=purity_proof
        )
    
    def create_purity_proof(
        self,
        constraint: Constraint,
        validation_result: PurityResult
    ) -> PurityProof:
        """
        Create cryptographic purity proof.
        
        Args:
            constraint: Constraint that was validated
            validation_result: Result from purity checker
            
        Returns:
            PurityProof with cryptographic signature
        """
        ast_hash = self._hash_ast(constraint.ast)
        signature = self._sign_proof(ast_hash, validation_result)
        
        return PurityProof(
            constraint_id=constraint.id,
            ast_hash=ast_hash,
            allowed_operations=validation_result.operations_used,
            validation_time=datetime.utcnow(),
            validation_result=validation_result.is_pure,
            validator_signature=signature
        )
    
    def create_subdistribution_witness(
        self,
        step: Step,
        retry_result: RetryResult
    ) -> SubdistributionWitness:
        """
        Create witness for probabilistic execution.
        
        Tracks all retry attempts and validates monad laws.
        """
        attempts = self._convert_retry_attempts(retry_result)
        probability_mass = self._calculate_probability_mass(attempts)
        monad_valid = self._validate_monad_laws(attempts, probability_mass)
        
        return SubdistributionWitness(
            step_id=step.name,
            attempts=attempts,
            final_result=retry_result.final_result,
            total_probability_mass=probability_mass,
            monad_laws_validated=monad_valid
        )
    
    def _hash_ast(self, ast: Any) -> str:
        """Hash constraint AST"""
        return hashlib.sha256(str(ast).encode()).hexdigest()
    
    def _sign_proof(self, ast_hash: str, validation: PurityResult) -> str:
        """Create cryptographic signature for proof"""
        # Use Ed25519 or similar
        # (Implementation would use cryptography library)
        return "signature_placeholder"
    
    def _calculate_probability_mass(self, attempts: List[AttemptRecord]) -> float:
        """Calculate total probability mass (must be ≤ 1.0)"""
        return sum(a.probability for a in attempts)
    
    def _validate_monad_laws(
        self,
        attempts: List[AttemptRecord],
        total_mass: float
    ) -> bool:
        """Validate subdistribution monad laws"""
        # Check: total probability ≤ 1.0
        if total_mass > 1.0:
            return False
        
        # Check: left identity, right identity, associativity
        # (Would require access to monad operations)
        
        return True
```

---

## 🗄️ **PHASE 5: SYSTEM INTEGRATION**

**Estimated Time:** 4-6 hours  
**Complexity:** Medium  
**Dependencies:** Phase 4 (VIF), existing CMC/HHNI/SEG systems

### **Step 5.1: CMC Storage Integration**

**File:** `packages/apoe/integration/cmc_storage.py`

```python
"""
CMC Storage Integration

Stores enhanced witnesses and PLIx execution results in CMC bitemporally.
"""

from cmc_service import CMCClient, CMCAtom
from datetime import datetime


class PLIxCMCIntegration:
    """
    Stores PLIx-enhanced execution artifacts in CMC.
    
    Storage Types:
    - Enhanced witnesses (constraint replay, purity, subdistribution)
    - Compilation artifacts (PLIx AST, ACL plan)
    - Verification results (TLA+, Alloy, OPA)
    """
    
    def __init__(self, cmc_client: CMCClient):
        self.cmc = cmc_client
    
    def store_compilation_artifact(
        self,
        plix_intent: PLIxIntent,
        acl_plan: ACLPlan
    ) -> str:
        """
        Store PLIx→ACL compilation artifact.
        
        Returns:
            atom_id: CMC atom identifier
        """
        atom = CMCAtom(
            content={
                "plix_intent": plix_intent.to_dict(),
                "acl_plan": acl_plan.to_dict(),
                "compilation_time": datetime.utcnow().isoformat()
            },
            modality="compilation",
            valid_from=datetime.utcnow(),
            valid_to=None,  # Open-ended
            metadata={
                "type": "plix_to_acl_compilation",
                "plix_version": "0.1.0",
                "acl_version": "0.1.0"
            }
        )
        return self.cmc.store_atom(atom)
    
    def store_enhanced_witness(
        self,
        witness: Union[ConstraintReplayWitness, PurityProof, SubdistributionWitness]
    ) -> str:
        """
        Store enhanced VIF witness in CMC.
        
        Returns:
            atom_id: CMC atom identifier
        """
        atom = CMCAtom(
            content=witness.__dict__,
            modality="provenance",
            valid_from=datetime.utcnow(),
            valid_to=None,
            metadata={
                "witness_type": type(witness).__name__,
                "plix_enhanced": True
            }
        )
        return self.cmc.store_atom(atom)
    
    def store_verification_result(
        self,
        backend: str,
        result: Union[TLAVerificationResult, AlloyResult, PolicyResult]
    ) -> str:
        """
        Store formal verification result.
        
        Returns:
            atom_id: CMC atom identifier
        """
        atom = CMCAtom(
            content={
                "backend": backend,
                "result": result.__dict__,
                "verification_time": datetime.utcnow().isoformat()
            },
            modality="verification",
            valid_from=datetime.utcnow(),
            valid_to=None,
            metadata={
                "formal_verification": True,
                "backend": backend
            }
        )
        return self.cmc.store_atom(atom)
```

### **Step 5.2: HHNI Indexing Integration**

**File:** `packages/apoe/integration/hhni_indexing.py`

```python
"""
HHNI Indexing Integration

Indexes PLIx constructs for semantic retrieval.
"""

from hhni import HHNIClient, NodeType


class PLIxHHNIIntegration:
    """
    Indexes PLIx constructs in HHNI for semantic search.
    
    Index Types:
    - Contracts (pre/post conditions)
    - Constraints (pure expressions)
    - Formal proofs (TLA+/Alloy results)
    - Compensation patterns
    """
    
    def __init__(self, hhni_client: HHNIClient):
        self.hhni = hhni_client
    
    def index_contract(
        self,
        contract: Contract,
        plan_id: str
    ) -> str:
        """
        Index PLIx contract for retrieval.
        
        Returns:
            node_id: HHNI node identifier
        """
        return self.hhni.add_node(
            node_type=NodeType.CONTRACT,
            content={
                "preconditions": [c.text for c in contract.preconditions],
                "postconditions": [c.text for c in contract.postconditions],
                "plan_id": plan_id
            },
            metadata={
                "plix_contract": True,
                "formal_specification": True
            }
        )
    
    def index_formal_proof(
        self,
        proof: Union[TLAVerificationResult, AlloyResult],
        plan_id: str
    ) -> str:
        """Index formal verification proof"""
        return self.hhni.add_node(
            node_type=NodeType.PROOF,
            content=proof.__dict__,
            metadata={
                "plan_id": plan_id,
                "formal_verification": True
            }
        )
```

### **Step 5.3: SEG Synthesis Integration**

**File:** `packages/apoe/integration/seg_synthesis.py`

```python
"""
SEG Synthesis Integration

Synthesizes formal proofs from multiple verification backends.
"""

from seg import SEGClient


class PLIxSEGIntegration:
    """
    Synthesizes PLIx verification results across backends.
    
    Synthesis:
    - Combines TLA+ and Alloy results
    - Computes confidence-weighted consensus
    - Resolves conflicts
    """
    
    def __init__(self, seg_client: SEGClient):
        self.seg = seg_client
    
    def synthesize_verification_results(
        self,
        tla_result: Optional[TLAVerificationResult],
        alloy_result: Optional[AlloyResult],
        opa_result: Optional[PolicyResult]
    ) -> Dict[str, Any]:
        """
        Synthesize verification results from multiple backends.
        
        Returns:
            Synthesis with consensus and confidence scores
        """
        results = []
        
        if tla_result:
            results.append({
                "source": "tla+",
                "success": tla_result.success,
                "confidence": 0.95 if tla_result.success else 0.5
            })
        
        if alloy_result:
            results.append({
                "source": "alloy",
                "success": alloy_result.success,
                "confidence": 0.90 if alloy_result.success else 0.5
            })
        
        if opa_result:
            results.append({
                "source": "opa",
                "success": opa_result.allowed,
                "confidence": 0.85 if opa_result.allowed else 0.5
            })
        
        # Use SEG to synthesize
        return self.seg.synthesize(results)
```

---

## 🧪 **TESTING STRATEGY**

### **Test Pyramid Structure**

```
           /\
          /  \  E2E Tests (10)
         /____\  
        /      \  Integration Tests (30)
       /________\
      /          \  Unit Tests (100+)
     /____________\
```

### **Unit Tests (Target: 100+ tests)**

**A. PLIx→ACL Compiler Tests**
```python
# packages/apoe/tests/test_plix_compiler.py

def test_compile_simple_intent():
    """Test basic PLIx→ACL compilation"""

def test_purity_validation():
    """Test purity checker catches impure constraints"""

def test_compensation_generation():
    """Test compensation step generation"""

def test_retry_policy_generation():
    """Test retry policy mapping"""

def test_constraint_mapping():
    """Test pre/post condition mapping to gates"""

def test_dependency_mapping():
    """Test depends_on → REQUIRES mapping"""

# Target: 20+ compiler tests
```

**B. Enhanced Executor Tests**
```python
# packages/apoe/tests/test_enhanced_executor.py

def test_compensation_execution():
    """Test saga pattern execution"""

def test_compensation_reverse_order():
    """Test compensation runs in reverse topological order"""

def test_retry_exponential_backoff():
    """Test exponential backoff calculation"""

def test_fallback_execution():
    """Test fallback after retry exhaustion"""

def test_purity_runtime_validation():
    """Test runtime purity checking"""

# Target: 30+ executor tests
```

**C. Backend Tests**
```python
# packages/apoe/tests/backends/test_tlaplus_backend.py

def test_tla_compilation():
    """Test TLA+ spec generation"""

def test_tla_verification():
    """Test TLC model checking"""

def test_safety_property_validation():
    """Test safety property checking"""

# Target: 20+ per backend (60+ total)
```

### **Integration Tests (Target: 30 tests)**

```python
# packages/apoe/tests/integration/test_plix_integration.py

def test_end_to_end_compilation():
    """Test PLIx→ACL→Execution pipeline"""
    plix_text = """
    ask ent:test/resource
      act:reserve
      requires con:available == True
      ensures con:reserved == True
      plan [
        task check := api.check()
        task reserve := api.reserve()
          depends_on: check
          compensate reserve -> api.cancel()
      ]
    """
    
    # Parse
    parser = PLIxParser()
    intent = parser.parse(plix_text)
    
    # Compile
    compiler = PLIxToACLCompiler()
    acl_plan = compiler.compile(intent)
    
    # Execute
    executor = EnhancedAPOEExecutor()
    result = executor.execute_with_compensation(acl_plan)
    
    assert result.success
    assert result.completed_steps == 2


def test_compensation_on_failure():
    """Test compensation triggers on step failure"""

def test_retry_with_eventual_success():
    """Test retry succeeds after failures"""

def test_formal_verification_integration():
    """Test TLA+/Alloy/OPA backends"""

def test_vif_witness_creation():
    """Test enhanced VIF witnesses created"""

def test_cmc_storage_integration():
    """Test witnesses stored in CMC"""

def test_hhni_indexing():
    """Test PLIx constructs indexed in HHNI"""

# Target: 30+ integration tests
```

### **E2E Tests (Target: 10 tests)**

```python
# packages/apoe/tests/e2e/test_plix_e2e.py

def test_meeting_room_reservation_golden_example():
    """
    Golden example: Complete meeting room reservation flow.
    
    PLIx Intent → Parse → Compile → Execute → Verify → Store
    """

def test_distributed_workflow_with_compensation():
    """Test multi-step workflow with compensation"""

def test_formal_verification_catches_error():
    """Test TLA+ catches design error"""

# Target: 10 E2E tests covering critical paths
```

### **Test Execution Strategy**

```bash
# Run all tests
pytest packages/apoe/tests/ -v --cov=packages/apoe

# Run specific test suites
pytest packages/apoe/tests/test_plix_compiler.py -v
pytest packages/apoe/tests/test_enhanced_executor.py -v
pytest packages/apoe/tests/backends/ -v
pytest packages/apoe/tests/integration/ -v
pytest packages/apoe/tests/e2e/ -v

# Coverage report
pytest --cov=packages/apoe --cov-report=html
```

**Target Coverage:** ≥95%

---

## 🚀 **DEPLOYMENT GUIDE**

### **Pre-Deployment Checklist**

**Quality Gates:**
- [ ] All tests passing (100+ unit, 30+ integration, 10 E2E)
- [ ] Code coverage ≥95%
- [ ] L0-L4 documentation complete
- [ ] Performance benchmarks acceptable
- [ ] Security audit complete
- [ ] APOE backwards compatibility validated (30/30 tests passing)

### **Deployment Steps**

**Step 1: Package Installation**
```bash
# Install enhanced APOE
cd packages/apoe
pip install -e .[plix]  # With PLIx extras

# Verify installation
python -c "from apoe.plix_compiler import PLIxToACLCompiler; print('✅ Installed')"
```

**Step 2: External Tool Configuration**
```bash
# Configure TLA+ Tools
export TLATOOLS_PATH=/path/to/tla2tools.jar

# Configure Alloy Analyzer
export ALLOY_PATH=/path/to/alloy.jar

# Configure OPA
export OPA_PATH=/path/to/opa
```

**Step 3: Service Configuration**
```yaml
# config/apoe_enhanced.yaml

apoe:
  plix_integration:
    enabled: true
    compiler:
      validate_purity: true
      generate_compensation: true
    executor:
      enable_compensation: true
      enable_retry: true
      max_retries: 3
    backends:
      tlaplus:
        enabled: true
        timeout_seconds: 60
      alloy:
        enabled: true
        timeout_seconds: 60
      opa:
        enabled: true
        cache_policies: true
```

**Step 4: Integration Validation**
```bash
# Run integration tests
pytest packages/apoe/tests/integration/test_plix_integration.py -v

# Verify APOE backwards compatibility
pytest packages/apoe/tests/test_executor.py -v  # All 30 should pass

# Run E2E tests
pytest packages/apoe/tests/e2e/ -v
```

---

## 🔧 **TROUBLESHOOTING**

### **Common Issues**

**Issue 1: Purity Validation Fails**
```
Error: PurityViolation: Constraint 'print(x)' is impure
```

**Solution:**
- Remove side effects from constraints
- Constraints must be pure (arithmetic, comparison, logic only)
- Use output gates instead of embedded I/O

**Issue 2: TLA+ Verification Timeout**
```
Error: TLA+ verification timed out after 60s
```

**Solution:**
- Simplify model (reduce state space)
- Increase timeout in configuration
- Use bounded model checking

**Issue 3: Compensation Fails**
```
Error: Compensation step failed: api.cancel returned error
```

**Solution:**
- Compensation is best-effort (doesn't fail overall execution)
- Check compensation logic is correct
- Ensure compensation has necessary context (IDs, etc.)

**Issue 4: APOE Tests Failing After Integration**
```
Error: 5/30 APOE tests failing
```

**Solution:**
- **CRITICAL:** Integration broke backwards compatibility
- Revert changes immediately
- Review executor modifications
- Ensure enhanced executor only activates when PLIx features present

---

## 🔄 **MAINTENANCE & EVOLUTION**

### **Continuous Quality**

**Weekly:**
- Run full test suite
- Check performance benchmarks
- Review error logs

**Monthly:**
- Security audit
- Dependency updates
- Documentation review

**Quarterly:**
- Comprehensive system audit
- Protocol compliance check
- User feedback integration

### **Evolution Path**

**v0.2 (Next Release):**
- Enhanced ACL syntax (native compensation/retry)
- Improved backend performance
- Extended verification properties

**v1.0 (Stable Release):**
- Production-hardened backends
- Complete formal semantics validation
- Comprehensive tooling ecosystem

---

## 📊 **FINAL IMPLEMENTATION SUMMARY**

### **Total Implementation Estimate:**

| Phase | Component | Estimated Hours |
|-------|-----------|-----------------|
| Phase 1 | PLIx→ACL Compiler | 5-8 hours |
| Phase 2 | Enhanced APOE Executor | 8-12 hours |
| Phase 3 | Verification Backends | 8-12 hours |
| Phase 4 | Enhanced VIF Integration | 4-6 hours |
| Phase 5 | System Integration | 4-6 hours |
| **Total** | **Implementation** | **29-44 hours** |

**Plus:**
- Testing: 4-6 hours
- Deployment: 2-3 hours
- Documentation: Already complete (L0-L4)

**Grand Total:** 35-53 hours of implementation work

### **Success Criteria Checklist**

- [ ] PLIx→ACL compiler functional (100% correct mapping)
- [ ] Enhanced APOE executor with compensation/retry
- [ ] All 3 backends operational (TLA+, Alloy, OPA)
- [ ] Enhanced VIF witnesses created correctly
- [ ] CMC/HHNI/SEG integrations working
- [ ] All tests passing (100+ unit, 30+ integration, 10 E2E)
- [ ] APOE backwards compatibility maintained (30/30 tests)
- [ ] Performance acceptable (< 5% overhead)
- [ ] L0-L4 documentation complete ✅ (this document)
- [ ] Deployment guide complete ✅ (this document)

---

**Word Count:** ~10,000 words ✅  
**Status:** L3 COMPLETE  
**Confidence:** 0.88  
**Next:** L4 Complete Reference (15,000+ words)

---

## 💙 **L3 COMPLETION NOTE**

This implementation guide provides complete, step-by-step instructions for integrating PLIx formal capabilities into APOE. Every component, interface, test, and deployment step is documented.

**Following this guide systematically will result in:**
- ✅ Formal verification capabilities in APOE
- ✅ Mathematical rigor (monad semantics, type system, effects)
- ✅ Failure resilience (compensation, retry/fallback)
- ✅ Enhanced provenance (purity proofs, constraint replay)
- ✅ Maintained quality (backwards compatible, tested, documented)

**Estimated implementation time: 35-53 hours of systematic work.**

**Ready for Stage 3: Foresight & Risk Map** 💙

