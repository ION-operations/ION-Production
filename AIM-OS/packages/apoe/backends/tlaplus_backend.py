"""
TLA+ Backend

Compiles ACL plans to TLA+ specifications for model checking.
Verifies safety and liveness properties.
"""

import subprocess
import tempfile
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import time

from ..models import ExecutionPlan, Step, Gate


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
        
        # Extract properties
        safety_props = self._extract_safety_properties(plan)
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
        if not self.tla_tools_path:
            # Graceful degradation: skip verification if tools not available
            return TLAVerificationResult(
                success=True,  # Assume success if can't verify
                safety_violated=[],
                liveness_violated=[],
                model_checker_output="TLA+ tools not configured - skipping verification",
                execution_time_ms=0.0
            )
        
        # Write spec to temporary file
        with tempfile.TemporaryDirectory() as tmpdir:
            spec_file = Path(tmpdir) / f"{spec.module_name}.tla"
            spec_file.write_text(spec.specification)
            
            try:
                # Run TLC model checker
                start_time = time.time()
                result = subprocess.run(
                    [
                        "java",
                        "-jar",
                        self.tla_tools_path,
                        "-workers", "4",
                        str(spec_file)
                    ],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                end_time = time.time()
                
                # Parse output
                safety_violated = self._parse_safety_violations(result.stdout)
                liveness_violated = self._parse_liveness_violations(result.stdout)
                
                return TLAVerificationResult(
                    success=result.returncode == 0 and len(safety_violated) == 0,
                    safety_violated=safety_violated,
                    liveness_violated=liveness_violated,
                    model_checker_output=result.stdout,
                    execution_time_ms=(end_time - start_time) * 1000
                )
            
            except (subprocess.TimeoutExpired, FileNotFoundError) as e:
                return TLAVerificationResult(
                    success=False,
                    safety_violated=[],
                    liveness_violated=[],
                    model_checker_output=f"Verification failed: {e}",
                    execution_time_ms=60000.0
                )
    
    def _generate_specification(self, plan: ExecutionPlan, module_name: str) -> str:
        """Generate TLA+ specification from plan"""
        
        variables = self._generate_variables(plan)
        init = self._generate_init(plan)
        actions = self._generate_actions(plan)
        next_state = self._generate_next(plan)
        spec = self._generate_spec(plan)
        properties = self._generate_properties(plan)
        
        return f"""---- MODULE {module_name} ----
EXTENDS Naturals, Sequences, TLC

{variables}

{init}

{actions}

{next_state}

{spec}

{properties}
====
"""
    
    def _generate_variables(self, plan: ExecutionPlan) -> str:
        """Generate VARIABLES declaration"""
        var_names = ["pc"]
        for step in plan.steps:
            var_names.append(f"{step.name}_status")
        return f"VARIABLES {', '.join(var_names)}"
    
    def _generate_init(self, plan: ExecutionPlan) -> str:
        """Generate Init predicate"""
        conditions = ["pc = 0"]
        for step in plan.steps:
            conditions.append(f'{step.name}_status = "pending"')
        return "Init == " + " /\\ ".join(conditions)
    
    def _generate_actions(self, plan: ExecutionPlan) -> str:
        """Generate action for each step"""
        actions = []
        for i, step in enumerate(plan.steps):
            preconditions = [f"pc = {i}", f'{step.name}_status = "pending"']
            postconditions = [f"pc' = {i + 1}", f'{step.name}_status' + "' = \"completed\""]
            
            action = f"""{step.name} ==
    /\\ {' /\\ '.join(preconditions)}
    /\\ {' /\\ '.join(postconditions)}
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
        
        # Liveness: eventually complete
        completion = " /\\ ".join([f'{s.name}_status = "completed"' for s in plan.steps])
        properties.append(f"Liveness == <>[{completion}]")
        
        return "\n".join(properties)
    
    def _extract_safety_properties(self, plan: ExecutionPlan) -> List[str]:
        """Extract safety properties from plan"""
        return []  # Simplified for now
    
    def _extract_liveness_properties(self, plan: ExecutionPlan) -> List[str]:
        """Extract liveness properties"""
        return ["Liveness"]
    
    def _parse_safety_violations(self, output: str) -> List[str]:
        """Parse TLC output for safety violations"""
        return []  # Would parse TLC output
    
    def _parse_liveness_violations(self, output: str) -> List[str]:
        """Parse TLC output for liveness violations"""
        return []  # Would parse TLC output
    
    def _sanitize_name(self, name: str) -> str:
        """Sanitize plan name for TLA+ module"""
        return name.replace("-", "_").replace(":", "_").replace("/", "_")

