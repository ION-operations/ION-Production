"""
Tests for PLIx Extensions to APOE Models

Validates backwards compatibility and new features.
"""

import pytest
from apoe.models import Step, CompensationStep, RetryPolicy, RoleType, StepStatus


def test_step_backwards_compatibility():
    """Test that existing Step usage still works"""
    
    # Old style (should still work)
    step = Step(
        id="test_step",
        name="test",
        role=RoleType.BUILDER,
        description="Test step"
    )
    
    assert step.id == "test_step"
    assert step.name == "test"
    assert step.role == RoleType.BUILDER
    
    # New PLIx fields default to None
    assert step.compensation is None
    assert step.retry_policy is None
    assert step.fallback is None
    assert step.effects is None
    assert step.min_confidence is None


def test_step_with_compensation():
    """Test step with compensation"""
    
    compensation = CompensationStep(
        compensates="reserve",
        action="api.cancel",
        params={"id": "$reserve.id"},
        on_failure="log_and_continue"
    )
    
    step = Step(
        id="reserve",
        name="reserve_room",
        role=RoleType.BUILDER,
        compensation=compensation
    )
    
    assert step.compensation is not None
    assert step.compensation.compensates == "reserve"
    assert step.compensation.action == "api.cancel"


def test_step_with_retry_policy():
    """Test step with retry policy"""
    
    retry = RetryPolicy(
        max_attempts=5,
        backoff_strategy="exponential",
        backoff_base=2.0,
        max_backoff=60.0,
        jitter=True
    )
    
    step = Step(
        id="api_call",
        name="call_api",
        role=RoleType.BUILDER,
        retry_policy=retry
    )
    
    assert step.retry_policy is not None
    assert step.retry_policy.max_attempts == 5
    assert step.retry_policy.backoff_strategy == "exponential"


def test_step_with_fallback():
    """Test step with fallback"""
    
    fallback_step = Step(
        id="fallback_check",
        name="fallback",
        role=RoleType.BUILDER
    )
    
    step = Step(
        id="primary_check",
        name="primary",
        role=RoleType.BUILDER,
        fallback=fallback_step
    )
    
    assert step.fallback is not None
    assert step.fallback.id == "fallback_check"


def test_step_with_effects():
    """Test step with effects metadata"""
    
    step = Step(
        id="io_step",
        name="file_operation",
        role=RoleType.OPERATOR,
        effects=["io", "db"]
    )
    
    assert step.effects is not None
    assert "io" in step.effects
    assert "db" in step.effects


def test_step_with_min_confidence():
    """Test step with minimum confidence"""
    
    step = Step(
        id="critical_step",
        name="critical_operation",
        role=RoleType.VERIFIER,
        min_confidence=0.95
    )
    
    assert step.min_confidence == 0.95


def test_compensation_step():
    """Test CompensationStep model"""
    
    comp = CompensationStep(
        compensates="step1",
        action="undo_action",
        params={"key": "value"},
        on_failure="abort"
    )
    
    assert comp.compensates == "step1"
    assert comp.action == "undo_action"
    assert comp.params["key"] == "value"
    assert comp.on_failure == "abort"


def test_retry_policy():
    """Test RetryPolicy model"""
    
    retry = RetryPolicy(
        max_attempts=10,
        backoff_strategy="linear",
        backoff_base=1.0,
        max_backoff=30.0,
        jitter=False
    )
    
    assert retry.max_attempts == 10
    assert retry.backoff_strategy == "linear"
    assert retry.backoff_base == 1.0
    assert retry.jitter is False


def test_pydantic_serialization():
    """Test that PLIx-enhanced steps serialize correctly"""
    
    step = Step(
        id="test",
        name="test",
        role=RoleType.BUILDER,
        compensation=CompensationStep(
            compensates="test",
            action="undo",
            params={}
        ),
        retry_policy=RetryPolicy()
    )
    
    # Should serialize to dict
    data = step.model_dump()
    assert "compensation" in data
    assert "retry_policy" in data
    
    # Should serialize to JSON
    json_str = step.model_dump_json()
    assert "compensation" in json_str
    assert "retry_policy" in json_str


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

