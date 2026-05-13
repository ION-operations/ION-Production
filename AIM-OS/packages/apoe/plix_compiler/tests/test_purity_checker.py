"""
Tests for Purity Checker
"""

import pytest
from apoe.plix_compiler.purity_checker import PurityChecker, Constraint, PurityResult


def test_pure_arithmetic():
    """Test pure arithmetic constraints"""
    checker = PurityChecker()
    
    assert checker.check(Constraint("c1", "x + y == z", ["x", "y", "z"])).is_pure
    assert checker.check(Constraint("c2", "a * b > 10", ["a", "b"])).is_pure
    assert checker.check(Constraint("c3", "n ** 2 <= 100", ["n"])).is_pure


def test_pure_comparison():
    """Test pure comparison constraints"""
    checker = PurityChecker()
    
    assert checker.check(Constraint("c1", "x > 10", ["x"])).is_pure
    assert checker.check(Constraint("c2", "a == b", ["a", "b"])).is_pure
    assert checker.check(Constraint("c3", "item in items", ["item", "items"])).is_pure


def test_pure_logical():
    """Test pure logical constraints"""
    checker = PurityChecker()
    
    assert checker.check(Constraint("c1", "x and y", ["x", "y"])).is_pure
    assert checker.check(Constraint("c2", "not invalid", ["invalid"])).is_pure
    assert checker.check(Constraint("c3", "a or b or c", ["a", "b", "c"])).is_pure


def test_pure_functions():
    """Test pure function calls"""
    checker = PurityChecker()
    
    assert checker.check(Constraint("c1", "len(items) > 0", ["items"])).is_pure
    assert checker.check(Constraint("c2", "max(values) < 100", ["values"])).is_pure
    assert checker.check(Constraint("c3", "abs(x) == 10", ["x"])).is_pure
    assert checker.check(Constraint("c4", "all(checks)", ["checks"])).is_pure


def test_impure_io():
    """Test that I/O operations are rejected"""
    checker = PurityChecker()
    
    result = checker.check(Constraint("c1", "print(x)", ["x"]))
    assert not result.is_pure
    assert "print" in result.reason.lower() or any("print" in v.lower() for v in result.violations)
    
    result = checker.check(Constraint("c2", "input()", []))
    assert not result.is_pure
    
    result = checker.check(Constraint("c3", "open('file.txt')", []))
    assert not result.is_pure


def test_impure_system():
    """Test that system calls are rejected"""
    checker = PurityChecker()
    
    result = checker.check(Constraint("c1", "exec('code')", []))
    assert not result.is_pure
    
    result = checker.check(Constraint("c2", "eval('expression')", []))
    assert not result.is_pure


def test_impure_assignment():
    """Test that assignments are rejected"""
    checker = PurityChecker()
    
    result = checker.check(Constraint("c1", "x = 10", []))
    assert not result.is_pure
    assert "assignment" in result.reason.lower() or any("assignment" in v.lower() for v in result.violations)


def test_impure_unknown_function():
    """Test that unknown functions are rejected (whitelist approach)"""
    checker = PurityChecker()
    
    result = checker.check(Constraint("c1", "unknown_function(x)", ["x"]))
    assert not result.is_pure
    assert "unknown" in result.reason.lower() or any("unknown" in v.lower() for v in result.violations)


def test_operations_used_tracking():
    """Test that operations are tracked"""
    checker = PurityChecker()
    
    result = checker.check(Constraint("c1", "max(x, y) == abs(z)", ["x", "y", "z"]))
    
    assert result.is_pure
    assert "max" in result.operations_used
    assert "abs" in result.operations_used


def test_syntax_error_handling():
    """Test syntax error handling"""
    checker = PurityChecker()
    
    result = checker.check(Constraint("c1", "invalid {{ syntax", []))
    
    assert not result.is_pure
    assert "syntax error" in result.reason.lower()


def test_get_effects():
    """Test effect extraction from impure constraints"""
    checker = PurityChecker()
    
    # Pure constraint: no effects
    pure = Constraint("c1", "x > 0", ["x"])
    assert len(checker.get_effects(pure)) == 0
    
    # Impure with I/O: io effect
    impure_io = Constraint("c2", "print(x)", ["x"])
    effects = checker.get_effects(impure_io)
    assert "io" in effects


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

