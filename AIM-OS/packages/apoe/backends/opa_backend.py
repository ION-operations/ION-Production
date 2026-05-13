"""
OPA Backend

Compiles ACL plans to Open Policy Agent (OPA) policies.
Enforces runtime policies and authorization.
"""

import subprocess
import tempfile
import json
import os
from typing import Dict, Any, List
from dataclasses import dataclass
import time

from ..models import ExecutionPlan, Step, Gate


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
    """Compiles ACL plans to OPA policies for runtime enforcement"""
    
    def __init__(self, opa_path: str = "opa"):
        self.opa_path = opa_path
    
    def compile(self, plan: ExecutionPlan) -> OPAPolicy:
        """Compile ACL plan to OPA policy"""
        package_name = self._sanitize_name(plan.name)
        policy = self._generate_policy(plan, package_name)
        rules = self._extract_rules(plan)
        
        return OPAPolicy(
            package_name=package_name,
            policy_text=policy,
            rules=rules
        )
    
    def evaluate(self, policy: OPAPolicy, input_data: Dict[str, Any]) -> PolicyResult:
        """Evaluate policy against input"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.rego', delete=False) as f:
            f.write(policy.policy_text)
            policy_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(input_data, f)
            input_file = f.name
        
        try:
            result = subprocess.run(
                [self.opa_path, "eval", "--data", policy_file, "--input", input_file, "--format", "json", f"data.{policy.package_name}.allow"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            output = json.loads(result.stdout)
            allowed = output.get('result', [{}])[0].get('expressions', [{}])[0].get('value', False)
            
            return PolicyResult(
                allowed=allowed,
                reasons=[],
                violations=[] if allowed else ["Policy denied"]
            )
        except:
            return PolicyResult(allowed=True, reasons=["OPA unavailable"], violations=[])
        finally:
            os.unlink(policy_file)
            os.unlink(input_file)
    
    def _generate_policy(self, plan: ExecutionPlan, package_name: str) -> str:
        """Generate OPA policy"""
        policy = f"""package {package_name}

default allow = false

"""
        for step in plan.steps:
            policy += f"""allow {{
  input.step == "{step.name}"
  input.context.ready
}}

"""
        return policy
    
    def _extract_rules(self, plan: ExecutionPlan) -> List[str]:
        return ["allow"]
    
    def _sanitize_name(self, name: str) -> str:
        return name.replace("-", "_").replace(":", "_").replace("/", "_")

