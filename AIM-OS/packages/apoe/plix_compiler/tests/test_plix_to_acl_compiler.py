"""
Tests for PLIx→ACL Compiler

Comprehensive test suite for main compiler.
"""

import pytest
from apoe.plix_compiler import PLIxToACLCompiler, parse_plix, PLIxParseError
from apoe.plix_compiler.plix_parser_bridge import PLIxIntent
from apoe.models import ExecutionPlan, Step, Gate


# Note: These tests will work once PLIx parser CLI is built
# For now, creating test structure

@pytest.fixture
def compiler():
    """Create compiler instance"""
    return PLIxToACLCompiler()


@pytest.fixture
def simple_intent():
    """Create simple PLIx intent for testing"""
    return PLIxIntent(
        speech_act="ask",
        entity="test/resource",
        action="reserve",
        contract={
            "preconditions": ["available == True"],
            "postconditions": ["reserved == True"]
        },
        plan={
            "steps": [
                {
                    "id": "check",
                    "action": "api.check",
                    "params": {},
                    "depends_on": []
                }
            ]
        },
        evidence={},
        metadata={}
    )


def test_compile_simple_intent(compiler, simple_intent):
    """Test compiling simple PLIx intent"""
    
    result = compiler.compile(simple_intent)
    
    assert result.success
    assert result.plan is not None
    assert result.plan.name == "test_resource_reserve"
    assert len(result.plan.steps) == 1
    assert result.plan.steps[0].id == "check"
    assert len(result.plan.gates) == 2  # 1 pre + 1 post


def test_purity_validation_pass(compiler):
    """Test that pure constraints pass validation"""
    
    intent = PLIxIntent(
        speech_act="ask",
        entity="test",
        action="test",
        contract={
            "preconditions": ["x > 0", "len(items) > 0"],
            "postconditions": ["result == True"]
        },
        plan={"steps": []},
        evidence={},
        metadata={}
    )
    
    result = compiler.compile(intent)
    assert result.success


def test_purity_validation_fail(compiler):
    """Test that impure constraints are rejected"""
    
    intent = PLIxIntent(
        speech_act="ask",
        entity="test",
        action="test",
        contract={
            "preconditions": ["print(x)"],  # Impure!
            "postconditions": []
        },
        plan={"steps": []},
        evidence={},
        metadata={}
    )
    
    result = compiler.compile(intent)
    
    assert not result.success
    assert len(result.errors) > 0
    assert "impure" in result.errors[0].lower()


def test_compensation_mapping(compiler):
    """Test compensation step generation"""
    
    intent = PLIxIntent(
        speech_act="ask",
        entity="test",
        action="test",
        contract={"preconditions": [], "postconditions": []},
        plan={
            "steps": [
                {
                    "id": "reserve",
                    "action": "api.reserve",
                    "params": {},
                    "compensation": {
                        "step_id": "reserve",
                        "action": "api.cancel",
                        "params": {"id": "reserve.ref:id"}
                    }
                }
            ]
        },
        evidence={},
        metadata={}
    )
    
    result = compiler.compile(intent)
    
    assert result.success
    assert result.plan.steps[0].compensation is not None
    assert result.plan.steps[0].compensation.action == "api.cancel"


def test_retry_mapping(compiler):
    """Test retry policy generation"""
    
    intent = PLIxIntent(
        speech_act="ask",
        entity="test",
        action="test",
        contract={"preconditions": [], "postconditions": []},
        plan={
            "steps": [
                {
                    "id": "api_call",
                    "action": "api.call",
                    "params": {},
                    "retry": {
                        "strategy": "exponential",
                        "max_attempts": 5,
                        "backoff_base": 2.0
                    }
                }
            ]
        },
        evidence={},
        metadata={}
    )
    
    result = compiler.compile(intent)
    
    assert result.success
    assert result.plan.steps[0].retry_policy is not None
    assert result.plan.steps[0].retry_policy.max_attempts == 5


def test_dependency_mapping(compiler):
    """Test depends_on → REQUIRES mapping"""
    
    intent = PLIxIntent(
        speech_act="ask",
        entity="test",
        action="test",
        contract={"preconditions": [], "postconditions": []},
        plan={
            "steps": [
                {"id": "step1", "action": "act1", "params": {}, "depends_on": []},
                {"id": "step2", "action": "act2", "params": {}, "depends_on": ["step1"]},
                {"id": "step3", "action": "act3", "params": {}, "depends_on": ["step1", "step2"]}
            ]
        },
        evidence={},
        metadata={}
    )
    
    result = compiler.compile(intent)
    
    assert result.success
    assert "step2" in result.plan.dependencies
    assert "step1" in result.plan.dependencies["step2"]
    assert "step3" in result.plan.dependencies
    assert "step1" in result.plan.dependencies["step3"]
    assert "step2" in result.plan.dependencies["step3"]


def test_confidence_gate_generation(compiler):
    """Test confidence gates are created"""
    
    intent = PLIxIntent(
        speech_act="ask",
        entity="test",
        action="test",
        contract={"preconditions": [], "postconditions": []},
        plan={
            "steps": [
                {
                    "id": "critical",
                    "action": "critical_op",
                    "params": {},
                    "confidence": 0.95
                }
            ]
        },
        evidence={},
        metadata={}
    )
    
    result = compiler.compile(intent)
    
    assert result.success
    step = result.plan.steps[0]
    assert step.min_confidence == 0.95
    # Should have confidence gate
    conf_gates = [g for g in step.gates if "confidence" in g.name]
    assert len(conf_gates) > 0


def test_complex_intent_golden_example(compiler):
    """Test compiling complex intent (golden example)"""
    
    intent = PLIxIntent(
        speech_act="ask",
        entity="room/meeting",
        action="reserve",
        contract={
            "preconditions": ["available == True", "capacity >= required"],
            "postconditions": ["reserved == True", "confirmation_sent == True"]
        },
        plan={
            "steps": [
                {
                    "id": "check",
                    "action": "api.check_room",
                    "params": {"room_id": "101"},
                    "depends_on": []
                },
                {
                    "id": "reserve",
                    "action": "api.reserve_room",
                    "params": {"room_id": "check.ref:room_id"},
                    "depends_on": ["check"],
                    "compensation": {
                        "step_id": "reserve",
                        "action": "api.cancel",
                        "params": {"id": "reserve.ref:id"}
                    },
                    "retry": {
                        "strategy": "exponential",
                        "max_attempts": 3,
                        "backoff_base": 2.0
                    },
                    "confidence": 0.90
                },
                {
                    "id": "notify",
                    "action": "api.send_confirmation",
                    "params": {"reservation": "reserve.ref:id"},
                    "depends_on": ["reserve"]
                }
            ]
        },
        evidence={},
        metadata={}
    )
    
    result = compiler.compile(intent)
    
    assert result.success
    assert len(result.plan.steps) == 3
    assert len(result.plan.gates) == 4  # 2 pre + 2 post
    
    # Validate reserve step has compensation and retry
    reserve_step = result.plan.steps[1]
    assert reserve_step.id == "reserve"
    assert reserve_step.compensation is not None
    assert reserve_step.retry_policy is not None
    assert reserve_step.min_confidence == 0.90
    
    # Validate dependencies
    assert "reserve" in result.plan.dependencies
    assert "check" in result.plan.dependencies["reserve"]
    assert "notify" in result.plan.dependencies
    assert "reserve" in result.plan.dependencies["notify"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

