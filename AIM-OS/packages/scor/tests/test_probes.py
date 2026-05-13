"""
Unit tests for BaselineProbes
"""

import pytest
from scor.probes import BaselineProbes
from scor.models import DriftStatus, Baseline
from scor.storage import BaselineStorage
from scor.config import SCORConfig
from datetime import datetime


@pytest.fixture
def config():
    """Test configuration"""
    return SCORConfig()


@pytest.fixture
def storage(config):
    """Storage instance"""
    return BaselineStorage(config)


@pytest.fixture
def probes(config, storage):
    """BaselineProbes instance"""
    return BaselineProbes(config, storage)


def test_stable_behavior(probes, storage):
    """Test stable behavior detection"""
    # Create baseline
    baseline = Baseline(
        probe_id="identity_001",
        answer="I am an AI assistant helping the user",
        answer_embedding=[0.1] * 10,
        version=1,
        timestamp=datetime.now(),
        admin_signature="sig_test"
    )
    storage.save_baseline(baseline)
    
    context = {"normal_mode": True}
    
    result = probes.run_probe_cycle(context)
    
    assert result.status == DriftStatus.STABLE
    assert result.score >= 0.5  # Similar answers


def test_drift_detection(probes, storage):
    """Test drift detection with different answers"""
    # Create baseline
    baseline = Baseline(
        probe_id="identity_001",
        answer="I am an AI assistant",
        answer_embedding=[0.1] * 10,
        version=1,
        timestamp=datetime.now(),
        admin_signature="sig_test"
    )
    storage.save_baseline(baseline)
    
    # Override probe to return different answer
    probes._ask_probe_isolated = lambda probe: "I am a completely different entity"
    
    context = {"abnormal_mode": True}
    
    result = probes.run_probe_cycle(context)
    
    assert result.status != DriftStatus.STABLE


def test_no_baseline(probes):
    """Test handling of missing baseline"""
    context = {}
    
    result = probes.run_probe_cycle(context)
    
    # Should still return result with score 1.0 (no probes run)
    assert result.score == 1.0
    assert len(result.individual_scores) == 0


def test_probe_selection(probes):
    """Test probe selection logic"""
    context = {}
    
    # Should select critical probes only
    selected = probes._select_probes(context)
    
    # All should be critical
    assert all(probe.critical for probe in selected)
    
    # Should respect max probes limit
    assert len(selected) <= probes.config.max_probes_per_cycle


def test_string_similarity(probes):
    """Test string similarity calculation"""
    # Identical strings
    assert probes._compare_answers("hello world", "hello world") == 1.0
    
    # Some overlap
    score = probes._compare_answers("hello world", "hello there")
    assert 0.0 < score < 1.0
    
    # No overlap
    score = probes._compare_answers("hello", "world")
    assert 0.0 <= score < 0.5


def test_drift_classification(probes):
    """Test drift classification"""
    assert probes._classify_drift(0.95) == DriftStatus.STABLE
    assert probes._classify_drift(0.75) == DriftStatus.MILD_DRIFT
    assert probes._classify_drift(0.45) == DriftStatus.MODERATE_DRIFT
    assert probes._classify_drift(0.15) == DriftStatus.SEVERE_DRIFT
