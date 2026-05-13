"""
Tests for the Adaptive Nervous System.

Covers:
- AdaptiveCore: Tracker persistence, threshold, pipeline orchestration
- Research Depth: confidence detection, T-level escalation, approval tiers
- Doc Depth: parity drift, stub generation, enrich commands
- Context Depth: cognitive drift, compression, strategy switching
"""

import json
import tempfile
from pathlib import Path

import pytest

from packages.adaptive_system.adaptive_core import (
    AdaptiveSystem, AdaptiveSensor, AdaptiveTracker,
    AdaptiveAnalyzer, AdaptiveGenerator, AdaptiveGatekeeper,
    Signal, Assessment, AdaptiveResponse,
    Severity, ApprovalLevel,
)
from packages.adaptive_system.research_depth import (
    ResearchDepthSensor, ResearchDepthAnalyzer, ResearchDepthGenerator,
    create_research_depth_adaptor,
)
from packages.adaptive_system.doc_depth import (
    DocDepthSensor, DocDepthAnalyzer, DocDepthGenerator,
    create_doc_depth_adaptor,
)
from packages.adaptive_system.context_depth import (
    ContextDepthSensor, ContextDepthAnalyzer, ContextDepthGenerator,
    create_context_depth_adaptor,
)


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


# ─────────────────────────────────────────────────────────────
# Adaptive Core Tests
# ─────────────────────────────────────────────────────────────

class TestAdaptiveTracker:
    def test_record_and_count(self, temp_dir):
        tracker = AdaptiveTracker(storage_path=temp_dir / "test.json")
        sig = Signal(signal_type="test", source="test")
        tracker.record(sig, "domain_a")
        tracker.record(sig, "domain_a")
        tracker.record(sig, "domain_b")
        
        assert tracker.count_occurrences("domain_a") == 2
        assert tracker.count_occurrences("domain_b") == 1
    
    def test_persistence(self, temp_dir):
        tracker1 = AdaptiveTracker(storage_path=temp_dir / "test.json")
        sig = Signal(signal_type="test", source="test")
        tracker1.record(sig, "domain_a")
        
        tracker2 = AdaptiveTracker(storage_path=temp_dir / "test.json")
        assert tracker2.count_occurrences("domain_a") == 1
    
    def test_threshold(self, temp_dir):
        tracker = AdaptiveTracker(storage_path=temp_dir / "test.json", threshold=3)
        sig = Signal(signal_type="test", source="test")
        
        tracker.record(sig, "domain_a")
        tracker.record(sig, "domain_a")
        assert not tracker.exceeds_threshold("domain_a")
        
        tracker.record(sig, "domain_a")
        assert tracker.exceeds_threshold("domain_a")
    
    def test_hot_domains(self, temp_dir):
        tracker = AdaptiveTracker(storage_path=temp_dir / "test.json", threshold=2)
        sig = Signal(signal_type="test", source="test")
        
        for _ in range(3):
            tracker.record(sig, "hot")
        tracker.record(sig, "cold")
        
        hot = tracker.get_hot_domains()
        assert "hot" in hot
        assert "cold" not in hot


class TestAdaptiveGatekeeper:
    def test_auto_approve(self, temp_dir):
        gk = AdaptiveGatekeeper(proposals_dir=temp_dir / "proposals")
        resp = AdaptiveResponse(response_type="test", content="test")
        result = gk.check_approval(resp, ApprovalLevel.AUTO)
        assert result.approved is True
    
    def test_non_auto_saves_proposal(self, temp_dir):
        proposals = temp_dir / "proposals"
        gk = AdaptiveGatekeeper(proposals_dir=proposals)
        resp = AdaptiveResponse(response_type="test", content="test")
        result = gk.check_approval(resp, ApprovalLevel.LEAD)
        
        assert result.approved is False
        assert "approval" in result.error.lower()
        assert any(proposals.iterdir())


# ─────────────────────────────────────────────────────────────
# Research Depth Tests
# ─────────────────────────────────────────────────────────────

class TestResearchDepth:
    def test_low_confidence_triggers(self):
        sensor = ResearchDepthSensor()
        signal = sensor.detect({
            "topic": "CMC internals",
            "current_depth": "T0",
            "confidence": 0.25,  # Below 0.30 = double jump
            "evidence_count": 1,
        })
        assert signal is not None
        assert signal.data["next_depth"] == "T2"  # Low confidence = jump by 2
    
    def test_high_confidence_no_trigger(self):
        sensor = ResearchDepthSensor()
        signal = sensor.detect({
            "topic": "CMC internals",
            "current_depth": "T0",
            "confidence": 0.85,
            "evidence_count": 10,
        })
        assert signal is None
    
    def test_max_depth_no_trigger(self):
        sensor = ResearchDepthSensor()
        signal = sensor.detect({
            "topic": "test",
            "current_depth": "T4",
            "confidence": 0.20,
        })
        assert signal is None
    
    def test_high_complexity_shallow_depth(self):
        sensor = ResearchDepthSensor()
        signal = sensor.detect({
            "topic": "complex task",
            "current_depth": "T0",
            "confidence": 0.65,
            "evidence_count": 5,
            "task_complexity": 0.85,
        })
        assert signal is not None
        assert "high complexity" in signal.description
    
    def test_analyzer_approval_tiers(self):
        analyzer = ResearchDepthAnalyzer()
        
        # T2 = auto
        sig_t2 = Signal(signal_type="test", source="test", data={"next_depth": "T2", "current_depth": "T0", "confidence": 0.4, "topic": "x"})
        result = analyzer.assess(sig_t2, 1, False)
        assert result.approval_level == ApprovalLevel.AUTO
        
        # T3 = lead
        sig_t3 = Signal(signal_type="test", source="test", data={"next_depth": "T3", "current_depth": "T1", "confidence": 0.3, "topic": "x"})
        result = analyzer.assess(sig_t3, 1, False)
        assert result.approval_level == ApprovalLevel.LEAD
    
    def test_full_pipeline(self, temp_dir):
        system = create_research_depth_adaptor(storage_dir=temp_dir)
        
        result = system.process({
            "topic": "HHNI retrieval optimization",
            "current_depth": "T0",
            "confidence": 0.30,
            "evidence_count": 1,
        })
        
        assert result is not None
        assert result.executed is True
        assert "HHNI" in result.description.lower() or "research" in result.response_type


# ─────────────────────────────────────────────────────────────
# Documentation Depth Tests
# ─────────────────────────────────────────────────────────────

class TestDocDepth:
    def test_no_docs_triggers_stub(self):
        sensor = DocDepthSensor()
        signal = sensor.detect({
            "module_name": "new_package",
            "doc_exists": False,
            "parity_score": 0,
        })
        assert signal is not None
        assert signal.data["recommended_depth"] == "stub"
        assert signal.severity == "critical"
    
    def test_low_parity_triggers_enrich(self):
        sensor = DocDepthSensor()
        signal = sensor.detect({
            "module_name": "cmc_service",
            "doc_exists": True,
            "parity_score": 0.55,
            "new_symbols": 1,
        })
        assert signal is not None
        assert signal.data["recommended_depth"] == "enrich"
    
    def test_high_parity_no_trigger(self):
        sensor = DocDepthSensor()
        signal = sensor.detect({
            "module_name": "well_documented",
            "doc_exists": True,
            "parity_score": 0.90,
            "new_symbols": 0,
            "code_changed_files": 1,
        })
        assert signal is None
    
    def test_stub_generation(self, temp_dir):
        gen = DocDepthGenerator(docs_root=temp_dir / "docs")
        assessment = Assessment(
            should_adapt=True, severity=Severity.CRITICAL,
            domain_key="new_package", occurrences=1,
            description="Generate T0 stub", recommended_action="generate_docs_stub",
            approval_level=ApprovalLevel.AUTO,
        )
        
        resp = gen.generate(assessment)
        assert resp.response_type == "doc_t0_stub"
        assert "new_package" in resp.content.lower() or "New Package" in resp.content
    
    def test_full_pipeline_creates_stub(self, temp_dir):
        system = create_doc_depth_adaptor(
            storage_dir=temp_dir / "adaptive",
            docs_root=temp_dir / "docs",
        )
        
        # First detection (below threshold of 2, but critical severity bypasses)
        result = system.process({
            "module_name": "new_package",
            "doc_exists": False,
            "parity_score": 0,
        })
        
        assert result is not None
        assert result.executed is True


# ─────────────────────────────────────────────────────────────
# Context Depth Tests
# ─────────────────────────────────────────────────────────────

class TestContextDepth:
    def test_high_fill_triggers(self):
        sensor = ContextDepthSensor()
        signal = sensor.detect({
            "context_size_tokens": 75000,
            "max_context_tokens": 100000,
        })
        assert signal is not None
        assert signal.data["fill_ratio"] == 0.75
    
    def test_high_error_rate_triggers(self):
        sensor = ContextDepthSensor()
        signal = sensor.detect({
            "context_size_tokens": 10000,
            "max_context_tokens": 100000,
            "error_rate": 0.35,  # Above 0.30 = critical
        })
        assert signal is not None
        assert signal.severity == "critical"
    
    def test_emergency_at_90_percent(self):
        sensor = ContextDepthSensor()
        signal = sensor.detect({
            "context_size_tokens": 92000,
            "max_context_tokens": 100000,
        })
        assert signal is not None
        assert signal.severity == "critical"
        assert signal.data["recommended_action"] == "emergency_compress"
    
    def test_low_retrieval_triggers_enrich(self):
        sensor = ContextDepthSensor()
        signal = sensor.detect({
            "context_size_tokens": 20000,
            "max_context_tokens": 100000,
            "retrieval_quality": 0.25,
        })
        assert signal is not None
        assert signal.data["recommended_action"] == "enrich_retrieval"
    
    def test_healthy_no_trigger(self):
        sensor = ContextDepthSensor()
        signal = sensor.detect({
            "context_size_tokens": 20000,
            "max_context_tokens": 100000,
            "error_rate": 0.05,
            "confidence": 0.85,
            "retrieval_quality": 0.90,
        })
        assert signal is None
    
    def test_full_pipeline(self, temp_dir):
        system = create_context_depth_adaptor(storage_dir=temp_dir)
        
        result = system.process({
            "context_size_tokens": 85000,
            "max_context_tokens": 100000,
            "error_rate": 0.20,
            "confidence": 0.40,
        })
        
        assert result is not None
        assert result.executed is True
        assert result.approved is True  # Context is always auto-approved


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
