"""
Purity Checker

Validates that PLIx constraints are pure (no side effects).
Critical for formal semantics preservation.
"""

import ast
from typing import Set, List, Optional
from dataclasses import dataclass


@dataclass
class PurityResult:
    """Result of purity checking"""
    is_pure: bool
    reason: Optional[str] = None
    violations: List[str] = None
    operations_used: Set[str] = None
    
    def __post_init__(self):
        if self.violations is None:
            self.violations = []
        if self.operations_used is None:
            self.operations_used = set()


@dataclass
class Constraint:
    """Constraint for purity checking"""
    id: str
    text: str
    variables: List[str]


class PurityChecker:
    """
    Checks if PLIx constraints are pure (no side effects).
    
    Pure operations:
    - Arithmetic: +, -, *, /, //, %, **
    - Comparison: ==, !=, <, <=, >, >=, in, not in
    - Logical: and, or, not
    - Field access: obj.field, obj[key]
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
        # Math
        "abs", "round", "pow", "max", "min", "sum",
        # Collections
        "len", "all", "any", "sorted", "reversed",
        "list", "tuple", "set", "dict", "frozenset",
        # Type checking
        "isinstance", "issubclass", "type",
        # Type conversion
        "bool", "int", "float", "str", "bytes",
        # Iteration
        "range", "enumerate", "zip", "map", "filter",
        # String
        "chr", "ord", "format", "join", "split"
    }
    
    # Forbidden impure operations
    IMPURE_OPERATIONS = {
        # I/O
        "print", "input", "open", "file", "read", "write",
        # Execution
        "exec", "eval", "compile", "__import__",
        # System
        "os", "sys", "subprocess", "system",
        # Network
        "socket", "http", "requests", "urllib", "fetch",
        # Database
        "db", "database", "query", "insert", "update", "delete", "commit",
        # Time (impure if uses system clock)
        "time", "datetime", "now", "today"
    }
    
    # Pure operators
    PURE_OPERATORS = {
        ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow,
        ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE,
        ast.And, ast.Or, ast.Not,
        ast.In, ast.NotIn, ast.Is, ast.IsNot
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
            operations_used = set()
            
            for node in ast.walk(tree):
                operation = self._get_operation_name(node)
                if operation:
                    operations_used.add(operation)
                
                violation = self._check_node(node)
                if violation:
                    violations.append(violation)
            
            if violations:
                return PurityResult(
                    is_pure=False,
                    reason=f"{len(violations)} purity violations detected",
                    violations=violations,
                    operations_used=operations_used
                )
            
            return PurityResult(
                is_pure=True,
                reason=None,
                violations=[],
                operations_used=operations_used
            )
        
        except SyntaxError as e:
            return PurityResult(
                is_pure=False,
                reason=f"Syntax error: {e}",
                violations=[f"Syntax error at position {e.offset}: {e.msg}"],
                operations_used=set()
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
        
        # Check augmented assignment (also forbidden)
        if isinstance(node, ast.AugAssign):
            return "Augmented assignment (+=, etc.) not allowed in pure constraint"
        
        # Check deletes (forbidden)
        if isinstance(node, ast.Delete):
            return "Delete not allowed in pure constraint"
        
        # Check imports (forbidden)
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            return "Import not allowed in pure constraint"
        
        # Check exec/eval (forbidden)
        if isinstance(node, ast.Expr):
            if isinstance(node.value, ast.Call):
                if isinstance(node.value.func, ast.Name):
                    if node.value.func.id in ("exec", "eval"):
                        return f"Dangerous operation: {node.value.func.id}"
        
        return None
    
    def _get_operation_name(self, node: ast.AST) -> Optional[str]:
        """Get operation name for tracking"""
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node, ast.BinOp):
            return type(node.op).__name__
        elif isinstance(node, ast.Compare):
            return "comparison"
        elif isinstance(node, ast.BoolOp):
            return "bool_op"
        elif isinstance(node, ast.UnaryOp):
            return type(node.op).__name__
        return None
    
    def check_expression(self, expr_text: str) -> PurityResult:
        """
        Check if arbitrary expression is pure.
        
        More general than check() - works on any expression.
        """
        dummy_constraint = Constraint(
            id="expr_check",
            text=expr_text,
            variables=[]
        )
        return self.check(dummy_constraint)
    
    def get_effects(self, constraint: Constraint) -> Set[str]:
        """
        Get effects that constraint would perform.
        
        Returns empty set if pure, non-empty if impure.
        """
        result = self.check(constraint)
        if result.is_pure:
            return set()
        
        # Determine effects from violations
        effects = set()
        for violation in result.violations:
            if "print" in violation or "input" in violation or "file" in violation:
                effects.add("io")
            if "socket" in violation or "http" in violation:
                effects.add("net")
            if "db" in violation or "query" in violation:
                effects.add("db")
        
        return effects

