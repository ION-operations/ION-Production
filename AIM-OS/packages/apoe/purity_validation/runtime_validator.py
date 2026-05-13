"""
Runtime Purity Validator

Validates constraint purity at runtime during execution.
Double-checks compile-time validation for safety.
"""

from typing import Dict, Any, Set, List
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
    
    Provides defense-in-depth: compile-time + runtime validation.
    """
    
    def __init__(self):
        # Track operations during evaluation
        self._call_stack: List[str] = []
        self._io_operations: Set[str] = set()
        self._state_mutations: Set[str] = set()
    
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
            
        Note:
            This is a best-effort runtime check.
            Full instrumentation would require more complex tracking.
        """
        # Check for I/O operations during evaluation
        if self._io_operations:
            raise PurityViolationError(
                constraint_text,
                f"I/O operations detected: {self._io_operations}"
            )
        
        # Check for state mutations
        if self._state_mutations:
            raise PurityViolationError(
                constraint_text,
                f"State mutations detected: {self._state_mutations}"
            )
        
        # Clear tracking for next constraint
        self._call_stack.clear()
        self._io_operations.clear()
        self._state_mutations.clear()
    
    def mark_io_operation(self, operation: str):
        """Mark that I/O operation occurred"""
        self._io_operations.add(operation)
    
    def mark_state_mutation(self, variable: str):
        """Mark that state mutation occurred"""
        self._state_mutations.add(variable)
    
    def reset(self):
        """Reset tracking state"""
        self._call_stack.clear()
        self._io_operations.clear()
        self._state_mutations.clear()

