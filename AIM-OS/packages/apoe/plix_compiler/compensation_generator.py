"""
Compensation Generator

Generates compensation steps for saga pattern.
Maps PLIx compensation syntax to ACL compensation logic.
"""

from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class Compensation:
    """PLIx compensation definition"""
    step_id: str  # Step to compensate
    action: str  # Compensation action
    params: Dict[str, Any]  # Parameters


class CompensationGenerator:
    """
    Generates ACL compensation logic from PLIx compensation syntax.
    
    PLIx Syntax:
        compensate step_id -> Action(params)
    
    ACL Output:
        {
            "compensates": "step_id",
            "action": "action_name",
            "params": {...},
            "on_failure": "log_and_continue"
        }
    
    Example:
        PLIx: compensate reserve -> api.cancel(id: reserve.ref:id)
        
        ACL: {
            "compensates": "reserve",
            "action": "api.cancel",
            "params": {"id": {"$ref": "reserve.id"}},
            "on_failure": "log_and_continue"
        }
    """
    
    def generate(self, plix_compensation: Compensation) -> Dict[str, Any]:
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
            "params": self._resolve_params(plix_compensation.params),
            "on_failure": "log_and_continue"  # Best-effort compensation
        }
    
    def _resolve_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve parameter references.
        
        Handles references like:
        - step.ref:field → {"$ref": "step.field"}
        - $variable → {"$var": "variable"}
        - literal values → unchanged
        
        Args:
            params: Raw parameter dictionary
            
        Returns:
            Resolved parameters with references converted
        """
        resolved = {}
        
        for key, value in params.items():
            if isinstance(value, str):
                if ".ref:" in value:
                    # Step output reference: "step.ref:field"
                    step_id, field = value.split(".ref:")
                    resolved[key] = {"$ref": f"{step_id}.{field}"}
                elif value.startswith("$"):
                    # Variable reference: "$variable"
                    resolved[key] = {"$var": value[1:]}
                else:
                    # Literal string
                    resolved[key] = value
            else:
                # Non-string literal (number, bool, etc.)
                resolved[key] = value
        
        return resolved
    
    def validate_compensation(self, compensation: Compensation, plan_steps: list) -> bool:
        """
        Validate compensation references exist.
        
        Args:
            compensation: Compensation to validate
            plan_steps: List of step IDs in plan
            
        Returns:
            True if compensation is valid
        """
        # Check step to compensate exists
        if compensation.step_id not in plan_steps:
            return False
        
        # Check parameter references are resolvable
        for param_value in compensation.params.values():
            if isinstance(param_value, str) and ".ref:" in param_value:
                step_id = param_value.split(".ref:")[0]
                if step_id not in plan_steps:
                    return False
        
        return True

