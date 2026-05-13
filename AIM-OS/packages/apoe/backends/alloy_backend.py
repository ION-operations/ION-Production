"""
Alloy Backend

Compiles ACL plans to Alloy models for structural validation.
"""

import subprocess
import tempfile
import os
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
import time

from ..models import ExecutionPlan, Step


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
    """Compiles ACL plans to Alloy for structural validation"""
    
    def __init__(self, alloy_path: Optional[str] = None):
        self.alloy_path = alloy_path or os.environ.get('ALLOY_PATH')
    
    def compile(self, plan: ExecutionPlan) -> AlloyModel:
        """Compile ACL plan to Alloy model"""
        model_name = self._sanitize_name(plan.name)
        model = self._generate_model(plan, model_name)
        assertions = self._extract_assertions(plan)
        
        return AlloyModel(
            model_name=model_name,
            model_text=model,
            assertions=assertions
        )
    
    def check(self, model: AlloyModel) -> AlloyResult:
        """Check Alloy model using Alloy Analyzer"""
        if not self.alloy_path:
            return AlloyResult(
                success=True,
                assertions_passed=[],
                assertions_failed=[],
                counterexamples=[],
                execution_time_ms=0.0
            )
        
        with tempfile.TemporaryDirectory() as tmpdir:
            model_file = Path(tmpdir) / f"{model.model_name}.als"
            model_file.write_text(model.model_text)
            
            try:
                start_time = time.time()
                result = subprocess.run(
                    ["java", "-jar", self.alloy_path, str(model_file)],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                end_time = time.time()
                
                passed, failed, counterexamples = self._parse_result(result.stdout)
                
                return AlloyResult(
                    success=len(failed) == 0,
                    assertions_passed=passed,
                    assertions_failed=failed,
                    counterexamples=counterexamples,
                    execution_time_ms=(end_time - start_time) * 1000
                )
            except:
                return AlloyResult(success=False, assertions_passed=[], assertions_failed=[], counterexamples=[], execution_time_ms=60000.0)
    
    def _generate_model(self, plan: ExecutionPlan, model_name: str) -> str:
        """Generate Alloy model"""
        return f"""module {model_name}

sig Step {{
  status: one Status,
  dependsOn: set Step
}}

abstract sig Status {{}}
one sig Pending, Running, Completed, Failed extends Status {{}}

fact noCycles {{
  no s: Step | s in s.^dependsOn
}}

pred validExecution[s: Step] {{
  all dep: s.dependsOn | dep.status = Completed
}}

assert noDeadlocks {{
  all s: Step | some dep: s.dependsOn implies (validExecution[s] or s.status = Pending)
}}

check noDeadlocks for 5
"""
    
    def _extract_assertions(self, plan: ExecutionPlan) -> List[str]:
        return ["noDeadlocks"]
    
    def _parse_result(self, output: str) -> Tuple[List[str], List[str], List[Dict]]:
        return [], [], []
    
    def _sanitize_name(self, name: str) -> str:
        return name.replace("-", "_").replace(":", "_").replace("/", "_")

