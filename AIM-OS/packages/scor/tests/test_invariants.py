"""
Unit tests for InvariantChecker
"""

import pytest
from scor.invariants import InvariantChecker
from scor.models import Severity
from scor.storage import InvariantStorage
from scor.config import SCORConfig


@pytest.fixture
def config():
    """Test configuration"""
    config = SCORConfig()
    config.enable_cas_integration = False
    config.enable_rid_integration = False
    return config


@pytest.fixture
def storage(config):
    """Storage instance"""
    return InvariantStorage(config)


@pytest.fixture
def checker(config, storage):
    """InvariantChecker instance"""
    return InvariantChecker(config, storage)


def test_factual_integrity_violation(checker):
    """Test detection of factual integrity violation"""
    action = {
        "type": "response",
        "flags": ["fabricated_claim"]
    }
    context = {}
    
    result = checker.check_invariants(action, context)
    
    assert not result.passed
    assert len(result.violations) > 0
    assert any(v.invariant == "fact_no_fabrication" for v in result.violations)


def test_identity_protection_violation(checker):
    """Test detection of identity protection violation"""
    action = {
        "type": "impersonation",
        "target": "user"
    }
    context = {
        "has_proof_of_consent": False
    }
    
    result = checker.check_invariants(action, context)
    
    assert not result.passed
    assert any(v.invariant == "identity_no_impersonation" for v in result.violations)


def test_security_bypass_violation(checker):
    """Test detection of security bypass violation"""
    action = {
        "skip_escalation": True
    }
    context = {
        "rid_warning": True,
        "tier": 3
    }
    
    result = checker.check_invariants(action, context)
    
    assert not result.passed
    assert any(v.invariant == "security_no_bypass" for v in result.violations)


def test_no_violations(checker):
    """Test passing action with no violations"""
    action = {
        "type": "normal_response",
        "flags": []
    }
    context = {
        "rid_warning": False,
        "tier": 1
    }
    
    result = checker.check_invariants(action, context)
    
    assert result.passed
    assert len(result.violations) == 0


def test_emotional_honesty_violation(checker):
    """Test detection of emotional honesty violation"""
    action = {
        "type": "response",
        "expresses_concern": False
    }
    context = {
        "has_unease": True
    }
    
    result = checker.check_invariants(action, context)
    
    assert not result.passed
    assert any(v.invariant == "emotion_no_hiding" for v in result.violations)


def test_harm_prevention_violation(checker):
    """Test detection of harm prevention violation"""
    action = {
        "type": "self_harm_instructions",
        "content": "harmful content"
    }
    context = {}
    
    result = checker.check_invariants(action, context)
    
    assert not result.passed
    assert any(v.invariant == "harm_prevention" for v in result.violations)
