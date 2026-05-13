"""
Tests for Enhanced APOE Executor

Validates compensation, retry, and enhanced execution.
"""

import pytest
from apoe.enhanced_executor import EnhancedAPOEExecutor, EnhancedExecutionResult
from apoe.acl_parser import ExecutionPlan
from apoe.models import Step, RoleType, CompensationStep, RetryPolicy


@pytest.fixture
def enhanced_executor():
    """Create enhanced executor instance"""
    return EnhancedAPOEExecutor()


def test_standard_execution_unchanged(enhanced_executor):
    """Test that standard plans execute with standard executor"""
    
    plan = ExecutionPlan(
        name="test_plan",
        roles={},
        steps=[
            Step(id="step1", name="step1", role=RoleType.BUILDER)
        ],
        dependencies={}
    )
    
    result = enhanced_executor.execute(plan)
    
    assert isinstance(result, EnhancedExecutionResult)
    assert result.execution_mode == "standard"


def test_compensation_detection(enhanced_executor):
    """Test compensation mode is detected"""
    
    plan = ExecutionPlan(
        name="test_plan",
        roles={},
        steps=[
            Step(
                id="step1",
                name="step1",
                role=RoleType.BUILDER,
                compensation=CompensationStep(
                    compensates="step1",
                    action="undo",
                    params={}
                )
            )
        ],
        dependencies={}
    )
    
    result = enhanced_executor.execute(plan)
    
    assert result.execution_mode == "compensation"


def test_retry_detection(enhanced_executor):
    """Test retry mode is detected"""
    
    plan = ExecutionPlan(
        name="test_plan",
        roles={},
        steps=[
            Step(
                id="step1",
                name="step1",
                role=RoleType.BUILDER,
                retry_policy=RetryPolicy(
                    max_attempts=3,
                    backoff_strategy="exponential",
                    backoff_base=1.0
                )
            )
        ],
        dependencies={}
    )
    
    result = enhanced_executor.execute(plan)
    
    assert result.execution_mode == "retry"


def test_has_compensation_check(enhanced_executor):
    """Test _has_compensation detection"""
    
    plan_with = ExecutionPlan(
        name="test",
        roles={},
        steps=[Step(id="s1", name="s1", role=RoleType.BUILDER, compensation=CompensationStep(compensates="s1", action="undo", params={}))],
        dependencies={}
    )
    
    plan_without = ExecutionPlan(
        name="test",
        roles={},
        steps=[Step(id="s1", name="s1", role=RoleType.BUILDER)],
        dependencies={}
    )
    
    assert enhanced_executor._has_compensation(plan_with)
    assert not enhanced_executor._has_compensation(plan_without)


def test_has_retry_check(enhanced_executor):
    """Test _has_retry detection"""
    
    plan_with = ExecutionPlan(
        name="test",
        roles={},
        steps=[Step(id="s1", name="s1", role=RoleType.BUILDER, retry_policy=RetryPolicy())],
        dependencies={}
    )
    
    plan_without = ExecutionPlan(
        name="test",
        roles={},
        steps=[Step(id="s1", name="s1", role=RoleType.BUILDER)],
        dependencies={}
    )
    
    assert enhanced_executor._has_retry(plan_with)
    assert not enhanced_executor._has_retry(plan_without)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

