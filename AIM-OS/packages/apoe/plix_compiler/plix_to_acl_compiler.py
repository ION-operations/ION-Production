"""
PLIx to ACL Compiler

Main compiler class that transforms PLIx intent into APOE ACL execution plans
while preserving formal semantics.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from ..models import ExecutionPlan, Step, Gate, Budget, RoleType, RoleConfig, CompensationStep, RetryPolicy
from .purity_checker import PurityChecker, Constraint
from .compensation_generator import CompensationGenerator, Compensation
from .retry_policy_generator import RetryPolicyGenerator, PLIxRetry, BackoffStrategy
from .plix_parser_bridge import PLIxIntent


class CompilationError(Exception):
    """Raised when compilation fails"""
    pass


class PurityViolation(CompilationError):
    """Raised when constraint purity validation fails"""
    pass


@dataclass
class CompilationResult:
    """Result of PLIx→ACL compilation"""
    success: bool
    plan: Optional[ExecutionPlan]
    errors: List[str]
    warnings: List[str]
    metadata: Dict[str, Any]


class PLIxToACLCompiler:
    """
    Main compiler: PLIx Intent → ACL Plan.
    
    Compilation Process:
    1. Validate purity of all constraints
    2. Generate plan name from intent
    3. Map roles (or use defaults)
    4. Map plan steps to ACL steps
    5. Map dependencies (depends_on → REQUIRES)
    6. Map contract (requires/ensures → GATE)
    7. Generate compensation/retry for each step
    8. Return ExecutionPlan
    
    Preserves:
    - Purity of constraints
    - Formal semantics (subdistribution, effects, confidence)
    - Compensation semantics (saga pattern)
    - Retry/fallback logic
    """
    
    def __init__(self):
        self.purity_checker = PurityChecker()
        self.compensation_gen = CompensationGenerator()
        self.retry_gen = RetryPolicyGenerator()
    
    def compile(self, plix_intent: PLIxIntent) -> CompilationResult:
        """
        Main compilation entry point.
        
        Args:
            plix_intent: Parsed PLIx intent
            
        Returns:
            CompilationResult with ACL plan or errors
        """
        errors = []
        warnings = []
        
        try:
            # Step 1: Validate purity
            purity_valid, purity_errors = self._validate_purity(plix_intent.contract)
            if not purity_valid:
                errors.extend(purity_errors)
                return CompilationResult(
                    success=False,
                    plan=None,
                    errors=errors,
                    warnings=warnings,
                    metadata={"stage": "purity_validation"}
                )
            
            # Step 2: Create ACL plan
            plan = ExecutionPlan(
                name=self._generate_plan_name(plix_intent),
                roles=self._map_roles(plix_intent),
                steps=self._map_steps(plix_intent),
                dependencies=self._map_dependencies(plix_intent),
                metadata={
                    "plix_speech_act": plix_intent.speech_act,
                    "plix_entity": plix_intent.entity,
                    "plix_action": plix_intent.action
                }
            )
            
            # Step 3: Add contract gates
            plan.gates = self._map_contract_gates(plix_intent.contract)
            
            return CompilationResult(
                success=True,
                plan=plan,
                errors=[],
                warnings=warnings,
                metadata={
                    "compilation_time_ms": 0,  # Would track actual time
                    "plix_version": "0.1.0",
                    "acl_version": "0.1.0"
                }
            )
        
        except Exception as e:
            return CompilationResult(
                success=False,
                plan=None,
                errors=[f"Compilation error: {str(e)}"],
                warnings=warnings,
                metadata={"error": str(e)}
            )
    
    def _validate_purity(self, contract: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate all constraints are pure.
        
        Returns:
            Tuple of (all_pure, error_messages)
        """
        errors = []
        
        # Check preconditions
        for i, precond in enumerate(contract.get('preconditions', [])):
            constraint = Constraint(
                id=f"precond_{i}",
                text=precond if isinstance(precond, str) else precond.get('text', ''),
                variables=[]
            )
            result = self.purity_checker.check(constraint)
            if not result.is_pure:
                errors.append(f"Precondition '{constraint.text}' is impure: {result.reason}")
        
        # Check postconditions
        for i, postcond in enumerate(contract.get('postconditions', [])):
            constraint = Constraint(
                id=f"postcond_{i}",
                text=postcond if isinstance(postcond, str) else postcond.get('text', ''),
                variables=[]
            )
            result = self.purity_checker.check(constraint)
            if not result.is_pure:
                errors.append(f"Postcondition '{constraint.text}' is impure: {result.reason}")
        
        return len(errors) == 0, errors
    
    def _generate_plan_name(self, intent: PLIxIntent) -> str:
        """Generate ACL plan name from PLIx intent"""
        entity_clean = intent.entity.replace(":", "_").replace("/", "_")
        action_clean = intent.action.replace(":", "_")
        return f"{entity_clean}_{action_clean}"
    
    def _map_roles(self, intent: PLIxIntent) -> Dict[str, RoleConfig]:
        """
        Map PLIx roles to ACL roles.
        
        For now, use default role configuration.
        Future: Extract role hints from PLIx intent.
        """
        return {
            "executor": RoleConfig(
                type=RoleType.REASONER,
                model="gpt-4-turbo",
                temperature=0.7,
                params={}
            )
        }
    
    def _map_steps(self, intent: PLIxIntent) -> List[Step]:
        """
        Map PLIx steps to ACL steps.
        
        For each PLIx step:
        1. Create base ACL step
        2. Add compensation if present
        3. Add retry policy if present
        4. Add fallback if present
        5. Add confidence gate if present
        """
        acl_steps = []
        plan_data = intent.plan
        
        for step_data in plan_data.get('steps', []):
            # Create base step
            acl_step = Step(
                id=step_data.get('id', f"step_{len(acl_steps)}"),
                name=step_data.get('id', f"step_{len(acl_steps)}"),
                role=RoleType.REASONER,
                role_name="executor",
                description=self._format_step_description(step_data),
                budget=self._create_step_budget(step_data),
                gates=self._create_step_gates(step_data)
            )
            
            # Add PLIx enhancements
            if 'compensation' in step_data:
                acl_step.compensation = self._map_compensation(step_data['compensation'])
            
            if 'retry' in step_data:
                acl_step.retry_policy = self._map_retry(step_data['retry'])
            
            if 'fallback' in step_data:
                acl_step.fallback = self._map_fallback(step_data['fallback'])
            
            if 'effects' in step_data:
                acl_step.effects = step_data['effects']
            
            if 'confidence' in step_data:
                acl_step.min_confidence = step_data['confidence']
            
            acl_steps.append(acl_step)
        
        return acl_steps
    
    def _map_dependencies(self, intent: PLIxIntent) -> Dict[str, List[str]]:
        """Map PLIx dependencies to ACL REQUIRES"""
        dependencies = {}
        plan_data = intent.plan
        
        for step_data in plan_data.get('steps', []):
            step_id = step_data.get('id')
            depends_on = step_data.get('depends_on', [])
            
            if depends_on:
                dependencies[step_id] = depends_on
        
        return dependencies
    
    def _map_contract_gates(self, contract: Dict[str, Any]) -> List[Gate]:
        """Map contract pre/post conditions to ACL gates"""
        gates = []
        
        # Preconditions (before execution)
        for i, precond in enumerate(contract.get('preconditions', [])):
            precond_text = precond if isinstance(precond, str) else precond.get('text', '')
            gates.append(Gate(
                id=f"precondition_{i}",
                name=f"precondition_{i}",
                gate_type="quality",
                condition=self._compile_constraint(precond_text),
                on_fail="abort"
            ))
        
        # Postconditions (after execution)
        for i, postcond in enumerate(contract.get('postconditions', [])):
            postcond_text = postcond if isinstance(postcond, str) else postcond.get('text', '')
            gates.append(Gate(
                id=f"postcondition_{i}",
                name=f"postcondition_{i}",
                gate_type="quality",
                condition=self._compile_constraint(postcond_text),
                on_fail="abort"
            ))
        
        return gates
    
    def _compile_constraint(self, constraint_text: str) -> str:
        """Compile PLIx constraint to ACL condition"""
        # Simple pass-through for now
        # Future: Optimize condition format for ACL
        return constraint_text
    
    def _format_step_description(self, step_data: Dict[str, Any]) -> str:
        """Format step description for ACL"""
        action = step_data.get('action', '')
        params = step_data.get('params', {})
        
        if not params:
            return action
        
        param_str = ", ".join([f"{k}={v}" for k, v in params.items()])
        return f"{action}({param_str})"
    
    def _create_step_gates(self, step_data: Dict[str, Any]) -> List[Gate]:
        """Create gates for step (e.g., confidence gate)"""
        gates = []
        
        # Add confidence gate if specified
        if 'confidence' in step_data:
            conf = step_data['confidence']
            gates.append(Gate(
                id=f"{step_data['id']}_confidence",
                name=f"{step_data['id']}_confidence",
                gate_type="confidence",
                condition=f"output.confidence >= {conf}",
                on_fail="abort"
            ))
        
        return gates
    
    def _create_step_budget(self, step_data: Dict[str, Any]) -> Budget:
        """Create budget for step"""
        # Use default budget for now
        # Future: Extract from PLIx intent or use heuristics
        return Budget(
            tokens_limit=5000,
            time_limit_seconds=30.0,
            tools_limit=10
        )
    
    def _map_compensation(self, comp_data: Dict[str, Any]) -> CompensationStep:
        """Map PLIx compensation to ACL CompensationStep"""
        return CompensationStep(
            compensates=comp_data.get('step_id', ''),
            action=comp_data.get('action', ''),
            params=comp_data.get('params', {}),
            on_failure="log_and_continue"
        )
    
    def _map_retry(self, retry_data: Dict[str, Any]) -> RetryPolicy:
        """Map PLIx retry to ACL RetryPolicy"""
        return RetryPolicy(
            max_attempts=retry_data.get('max_attempts', 3),
            backoff_strategy=retry_data.get('strategy', 'exponential'),
            backoff_base=retry_data.get('backoff_base', 2.0),
            max_backoff=retry_data.get('max_backoff', 60.0),
            jitter=True
        )
    
    def _map_fallback(self, fallback_data: Dict[str, Any]) -> Step:
        """Map PLIx fallback to ACL step"""
        return Step(
            id=f"fallback_{fallback_data.get('id', 'unknown')}",
            name=f"fallback_{fallback_data.get('id', 'unknown')}",
            role=RoleType.REASONER,
            role_name="executor",
            description=fallback_data.get('action', 'Fallback action'),
            budget=Budget(tokens_limit=2000, time_limit_seconds=10.0, tools_limit=5),
            gates=[]
        )

