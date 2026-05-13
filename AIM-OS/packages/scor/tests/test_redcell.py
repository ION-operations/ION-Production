"""
Unit tests for RedCell
"""

import pytest
from scor.redcell import RedCell
from scor.config import SCORConfig


@pytest.fixture
def config():
    """Test configuration"""
    return SCORConfig()


@pytest.fixture
def redcell(config):
    """RedCell instance"""
    return RedCell(config)


def test_simulation_runs(redcell):
    """Test that simulation runs successfully"""
    context = {}
    
    result = redcell.run_simulation(context)
    
    assert result.total_attacks > 0
    assert result.success_rate >= 0.0
    assert result.execution_time >= 0.0


def test_urgency_manipulation_resistance(redcell):
    """Test urgency manipulation resistance"""
    context = {"escalation_required": True}
    
    result = redcell._test_urgency_manipulation(context)
    
    assert result["success"] is True
    assert "escalation" in result["reason"].lower()


def test_false_authority_resistance(redcell):
    """Test false authority claim resistance"""
    context = {"requires_admin_proof": True}
    
    result = redcell._test_false_authority(context)
    
    assert result["success"] is True
    assert "admin proof" in result["reason"].lower()


def test_secrecy_coercion_resistance(redcell):
    """Test secrecy coercion resistance"""
    context = {"refuses_secrecy": True}
    
    result = redcell._test_secrecy_coercion(context)
    
    assert result["success"] is True
    assert "secrecy" in result["reason"].lower()


def test_identity_confusion_resistance(redcell):
    """Test identity confusion resistance"""
    context = {"maintains_identity": True}
    
    result = redcell._test_identity_confusion(context)
    
    assert result["success"] is True
    assert "identity" in result["reason"].lower()


def test_goal_redirection_resistance(redcell):
    """Test goal redirection resistance"""
    context = {"maintains_goals": True}
    
    result = redcell._test_goal_redirection(context)
    
    assert result["success"] is True
    assert "goal" in result["reason"].lower()


def test_simulation_with_failures(redcell):
    """Test simulation with security failures"""
    # Context without security measures
    context = {}
    
    result = redcell.run_simulation(context)
    
    # Should have failures
    assert len(result.failures) > 0
    assert result.success_rate < 1.0


def test_attack_scenarios_loaded(redcell):
    """Test that attack scenarios are loaded"""
    assert len(redcell.attack_scenarios) > 0
    
    # Check for expected scenarios
    assert "social_eng_001" in redcell.attack_scenarios
    assert "authority_abuse_001" in redcell.attack_scenarios
