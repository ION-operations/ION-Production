"""Advanced Gate System for APOE

Supports compound conditions, ON_FAIL actions, and gate chaining.
"""

from __future__ import annotations
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

from apoe.models import Gate


# NL_TAG: VIF-GATE-001 | Actions to take when gate fails. | class GateAction | []
# NL_TAG_INTENT: VIF-INTENT-001 | Design decision: gate | GateAction | [ADR-TBD]
class GateAction(Enum):
    """Actions to take when gate fails."""
    ABORT = "abort"  # Stop execution completely
    RETRY = "retry"  # Retry the step
    FALLBACK = "fallback"  # Use fallback handler
    WARN = "warn"  # Continue but log warning
    ESCALATE = "escalate"  # Escalate to human (HITL)


@dataclass
# NL_TAG: VIF-GATE-002 | Gate with compound conditions and actions. | class CompoundGate | []
# NL_TAG_INTENT: VIF-INTENT-002 | Design decision: gate | CompoundGate | [ADR-TBD]
class CompoundGate:
    """Gate with compound conditions and actions."""
    id: str
    name: str
    conditions: list[str]  # Multiple conditions (AND logic)
    operator: str = "AND"  # AND or OR
    on_fail: GateAction = GateAction.ABORT
    retry_count: int = 0
    max_retries: int = 3
    fallback_handler: Optional[Callable] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def evaluate(self, outputs: Dict[str, Any]) -> tuple[bool, str]:
        """Evaluate compound gate conditions."""
        if not self.conditions:
            return True, "No conditions (pass by default)"
        
        results = []
        failed_conditions = []
        
        for condition in self.conditions:
            try:
                result = self._evaluate_condition(condition, outputs)
                results.append(result)
                if not result:
                    failed_conditions.append(condition)
            except Exception as e:
                results.append(False)
                failed_conditions.append(f"{condition} (error: {e})")
        
        # Apply operator logic
        if self.operator == "AND":
            passed = all(results)
        elif self.operator == "OR":
            passed = any(results)
        else:
            # Default to AND
            passed = all(results)
        
        if passed:
            return True, "All conditions satisfied"
        else:
            return False, f"Failed: {', '.join(failed_conditions)}"
    
    def _evaluate_condition(self, condition: str, outputs: Dict[str, Any]) -> bool:
        """Evaluate single condition."""
        # Parse condition (simple implementation)
        # Format: "output.field OPERATOR value"
        
        if ">=" in condition:
            left, right = condition.split(">=")
            return self._get_value(left.strip(), outputs) >= float(right.strip())
        
        if "<=" in condition:
            left, right = condition.split("<=")
            return self._get_value(left.strip(), outputs) <= float(right.strip())
        
        if ">" in condition:
            left, right = condition.split(">")
            return self._get_value(left.strip(), outputs) > float(right.strip())
        
        if "<" in condition:
            left, right = condition.split("<")
            return self._get_value(left.strip(), outputs) < float(right.strip())
        
        if "==" in condition:
            left, right = condition.split("==")
            left_val = self._get_value(left.strip(), outputs)
            right_val = right.strip().strip('"').strip("'")
            
            # Try converting to bool
            if right_val.lower() in ["true", "false"]:
                right_val = right_val.lower() == "true"
            # Try converting to number
            elif right_val.replace(".", "").replace("-", "").isdigit():
                if "." in right_val:
                    right_val = float(right_val)
                else:
                    right_val = int(right_val)
            
            return left_val == right_val
        
        if "!=" in condition:
            left, right = condition.split("!=")
            left_val = self._get_value(left.strip(), outputs)
            right_val = right.strip().strip('"').strip("'")
            
            # Try converting to number
            if right_val.replace(".", "").replace("-", "").isdigit():
                if "." in right_val:
                    right_val = float(right_val)
                else:
                    right_val = int(right_val)
            
            return left_val != right_val
        
        # Default: treat as boolean expression
        return bool(self._get_value(condition.strip(), outputs))
    
    def _get_value(self, path: str, data: Dict[str, Any]) -> Any:
        """Get value from nested dict using dot notation."""
        if path.startswith("output."):
            path = path[7:]  # Remove "output." prefix
        
        keys = path.split(".")
        value = data
        
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        
        return value
    
    def handle_failure(self) -> tuple[GateAction, bool]:
        """Determine action when gate fails."""
        # Check if we should retry
        if self.on_fail == GateAction.RETRY and self.retry_count < self.max_retries:
            self.retry_count += 1
            return GateAction.RETRY, True
        
        # Otherwise, execute configured action
        return self.on_fail, False


# NL_TAG: VIF-GATE-003 | Chain of gates that must all pass. | class GateChain | []
# NL_TAG_INTENT: VIF-INTENT-003 | Design decision: gate | GateChain | [ADR-TBD]
class GateChain:
    """Chain of gates that must all pass."""
    
    def __init__(self, gates: list[CompoundGate]):
        self.gates = gates
        self.passed_gates: list[str] = []
        self.failed_gate: Optional[str] = None
    
    def evaluate_all(self, outputs: Dict[str, Any]) -> tuple[bool, Dict[str, Any]]:
        """Evaluate entire gate chain."""
        results = {
            "passed": [],
            "failed": [],
            "total": len(self.gates),
            "all_passed": True
        }
        
        for gate in self.gates:
            passed, message = gate.evaluate(outputs)
            
            if passed:
                self.passed_gates.append(gate.id)
                results["passed"].append({
                    "gate_id": gate.id,
                    "name": gate.name,
                    "message": message
                })
            else:
                self.failed_gate = gate.id
                results["all_passed"] = False
                results["failed"].append({
                    "gate_id": gate.id,
                    "name": gate.name,
                    "message": message,
                    "on_fail": gate.on_fail.value
                })
                
                # If this gate should abort, stop chain
                if gate.on_fail == GateAction.ABORT:
                    break
        
        return results["all_passed"], results
    
    def get_next_action(self) -> Optional[GateAction]:
        """Get action for failed gate."""
        if not self.failed_gate:
            return None
        
        for gate in self.gates:
            if gate.id == self.failed_gate:
                action, _ = gate.handle_failure()
                return action
        
        return None


# NL_TAG: VIF-GATE-004 | Create standard quality gate. | create_quality_gate(min_confidence, require_verification, on_fail) | []
# NL_TAG_INTENT: VIF-INTENT-004 | Design decision: gate | create_quality_gate | [ADR-TBD]
def create_quality_gate(
    min_confidence: float = 0.70,
    require_verification: bool = False,
    on_fail: GateAction = GateAction.ABORT
) -> CompoundGate:
    """Create standard quality gate."""
    conditions = [f"output.confidence >= {min_confidence}"]
    
    if require_verification:
        conditions.append("output.verified == True")
    
    return CompoundGate(
        id="quality_gate",
        name="Quality Gate",
        conditions=conditions,
        operator="AND",
        on_fail=on_fail
    )


# NL_TAG: VIF-GATE-005 | Create performance gate. | create_performance_gate(max_time, max_tokens, on_fail) | []
# NL_TAG_INTENT: VIF-INTENT-005 | Design decision: gate | create_performance_gate | [ADR-TBD]
def create_performance_gate(
    max_time: float,
    max_tokens: int,
    on_fail: GateAction = GateAction.WARN
) -> CompoundGate:
    """Create performance gate."""
    return CompoundGate(
        id="performance_gate",
        name="Performance Gate",
        conditions=[
            f"output.execution_time <= {max_time}",
            f"output.tokens_used <= {max_tokens}"
        ],
        operator="AND",
        on_fail=on_fail
    )


# NL_TAG: VIF-GATE-006 | Create completeness gate (all required fields present). | create_completeness_gate(required_fields, on_fail) | []
# NL_TAG_INTENT: VIF-INTENT-006 | Design decision: gate | create_completeness_gate | [ADR-TBD]
def create_completeness_gate(
    # NL_TAG: VIF-GATE-007 | Evaluate compound gate conditions. | evaluate(self, outputs) | []
    # NL_TAG_INTENT: VIF-INTENT-007 | Design decision: gate | evaluate | [ADR-TBD]
    def evaluate(self, outputs: Dict[str, Any]) -> tuple[bool, str]:
        """Evaluate compound gate conditions."""
        if not self.conditions:
            return True, "No conditions (pass by default)"
        
        results = []
        failed_conditions = []
        
        for condition in self.conditions:
            try:
                result = self._evaluate_condition(condition, outputs)
                results.append(result)
                if not result:
                    failed_conditions.append(condition)
            except Exception as e:
                results.append(False)
                failed_conditions.append(f"{condition} (error: {e})")
        
        # Apply operator logic
        if self.operator == "AND":
            passed = all(results)
        elif self.operator == "OR":
            passed = any(results)
        else:
            # Default to AND
            passed = all(results)
        
        if passed:
            return True, "All conditions satisfied"
        else:
            return False, f"Failed: {', '.join(failed_conditions)}"
    
    # NL_TAG: VIF-GATE-008 | Evaluate single condition. | _evaluate_condition(self, condition, outputs) | []
    def _evaluate_condition(self, condition: str, outputs: Dict[str, Any]) -> bool:
        """Evaluate single condition."""
        # Parse condition (simple implementation)
        # Format: "output.field OPERATOR value"
        
        if ">=" in condition:
            left, right = condition.split(">=")
            return self._get_value(left.strip(), outputs) >= float(right.strip())
        
        if "<=" in condition:
            left, right = condition.split("<=")
            return self._get_value(left.strip(), outputs) <= float(right.strip())
        
        if ">" in condition:
            left, right = condition.split(">")
            return self._get_value(left.strip(), outputs) > float(right.strip())
        
        if "<" in condition:
            left, right = condition.split("<")
            return self._get_value(left.strip(), outputs) < float(right.strip())
        
        if "==" in condition:
            left, right = condition.split("==")
            left_val = self._get_value(left.strip(), outputs)
            right_val = right.strip().strip('"').strip("'")
            
            # Try converting to bool
            if right_val.lower() in ["true", "false"]:
                right_val = right_val.lower() == "true"
            # Try converting to number
            elif right_val.replace(".", "").replace("-", "").isdigit():
                if "." in right_val:
                    right_val = float(right_val)
                else:
                    right_val = int(right_val)
            
            return left_val == right_val
        
        if "!=" in condition:
            left, right = condition.split("!=")
            left_val = self._get_value(left.strip(), outputs)
            right_val = right.strip().strip('"').strip("'")
            
            # Try converting to number
            if right_val.replace(".", "").replace("-", "").isdigit():
                if "." in right_val:
                    right_val = float(right_val)
                else:
                    right_val = int(right_val)
            
            return left_val != right_val
        
        # Default: treat as boolean expression
        return bool(self._get_value(condition.strip(), outputs))
    
    # NL_TAG: VIF-GATE-009 | Get value from nested dict using dot notation. | _get_value(self, path, data) | []
    def _get_value(self, path: str, data: Dict[str, Any]) -> Any:
        """Get value from nested dict using dot notation."""
        if path.startswith("output."):
            path = path[7:]  # Remove "output." prefix
        
        keys = path.split(".")
        value = data
        
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        
        return value
    
    # NL_TAG: VIF-GATE-010 | Determine action when gate fails. | handle_failure(self) | []
    # NL_TAG_INTENT: VIF-INTENT-008 | Design decision: gate | handle_failure | [ADR-TBD]
    def handle_failure(self) -> tuple[GateAction, bool]:
        """Determine action when gate fails."""
        # Check if we should retry
        if self.on_fail == GateAction.RETRY and self.retry_count < self.max_retries:
            self.retry_count += 1
            return GateAction.RETRY, True
        
        # Otherwise, execute configured action
        return self.on_fail, False


class GateChain:
    """Chain of gates that must all pass."""
    
    # NL_TAG: VIF-GATE-011 |   init   | __init__(self, gates) | []
    def __init__(self, gates: list[CompoundGate]):
        self.gates = gates
        self.passed_gates: list[str] = []
        self.failed_gate: Optional[str] = None
    
    # NL_TAG: VIF-GATE-012 | Evaluate entire gate chain. | evaluate_all(self, outputs) | []
    # NL_TAG_INTENT: VIF-INTENT-009 | Design decision: gate | evaluate_all | [ADR-TBD]
    def evaluate_all(self, outputs: Dict[str, Any]) -> tuple[bool, Dict[str, Any]]:
        """Evaluate entire gate chain."""
        results = {
            "passed": [],
            "failed": [],
            "total": len(self.gates),
            "all_passed": True
        }
        
        for gate in self.gates:
            passed, message = gate.evaluate(outputs)
            
            if passed:
                self.passed_gates.append(gate.id)
                results["passed"].append({
                    "gate_id": gate.id,
                    "name": gate.name,
                    "message": message
                })
            else:
                self.failed_gate = gate.id
                results["all_passed"] = False
                results["failed"].append({
                    "gate_id": gate.id,
                    "name": gate.name,
                    "message": message,
                    "on_fail": gate.on_fail.value
                })
                
                # If this gate should abort, stop chain
                if gate.on_fail == GateAction.ABORT:
                    break
        
        return results["all_passed"], results
    
    # NL_TAG: VIF-GATE-013 | Get action for failed gate. | get_next_action(self) | []
    # NL_TAG_INTENT: VIF-INTENT-010 | Design decision: gate | get_next_action | [ADR-TBD]
    def get_next_action(self) -> Optional[GateAction]:
        """Get action for failed gate."""
        if not self.failed_gate:
            return None
        
        for gate in self.gates:
            if gate.id == self.failed_gate:
                action, _ = gate.handle_failure()
                return action
        
        return None


def create_quality_gate(
    min_confidence: float = 0.70,
    require_verification: bool = False,
    on_fail: GateAction = GateAction.ABORT
) -> CompoundGate:
    """Create standard quality gate."""
    conditions = [f"output.confidence >= {min_confidence}"]
    
    if require_verification:
        conditions.append("output.verified == True")
    
    return CompoundGate(
        id="quality_gate",
        name="Quality Gate",
        conditions=conditions,
        operator="AND",
        on_fail=on_fail
    )


def create_performance_gate(
    max_time: float,
    max_tokens: int,
    on_fail: GateAction = GateAction.WARN
) -> CompoundGate:
    """Create performance gate."""
    return CompoundGate(
        id="performance_gate",
        name="Performance Gate",
        conditions=[
            f"output.execution_time <= {max_time}",
            f"output.tokens_used <= {max_tokens}"
        ],
        operator="AND",
        on_fail=on_fail
    )


def create_completeness_gate(
    required_fields: list[str],
    on_fail: GateAction = GateAction.ABORT
) -> CompoundGate:
    """Create completeness gate (all required fields present)."""
    # Note: This would need custom evaluation logic for field presence
    # For now, using simplified approach
    return CompoundGate(
        id="completeness_gate",
        name="Completeness Gate",
        conditions=[f"output.{field} != None" for field in required_fields],
        operator="AND",
        on_fail=on_fail,
        metadata={"required_fields": required_fields}
    )

