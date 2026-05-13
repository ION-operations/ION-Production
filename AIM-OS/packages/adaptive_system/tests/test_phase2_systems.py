"""
Tests for Phase 2 Adaptive Systems: Test Coverage + Knowledge Decay.
"""

import tempfile
from pathlib import Path

import pytest

from packages.adaptive_system.test_coverage import (
    TestCoverageSensor, TestCoverageAnalyzer, TestCoverageGenerator,
    create_test_coverage_adaptor,
)
from packages.adaptive_system.knowledge_decay import (
    KnowledgeDecaySensor, KnowledgeDecayAnalyzer, KnowledgeDecayGenerator,
    create_knowledge_decay_detector,
)
from packages.adaptive_system.adaptive_core import Severity, ApprovalLevel


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


# ─────────────────────────────────────────────────────────────
# Test Coverage Adaptor Tests
# ─────────────────────────────────────────────────────────────

class TestTestCoverage:
    def test_no_test_file_triggers(self):
        sensor = TestCoverageSensor()
        signal = sensor.detect({
            "module_name": "new_module",
            "coverage_percent": 0,
            "has_test_file": False,
        })
        assert signal is not None
        assert signal.data["recommended_action"] == "stub"
    
    def test_low_coverage_triggers(self):
        sensor = TestCoverageSensor()
        signal = sensor.detect({
            "module_name": "poorly_tested",
            "coverage_percent": 35.0,
            "has_test_file": True,
        })
        assert signal is not None
        assert signal.data["recommended_action"] == "unit"
    
    def test_coverage_drop_triggers(self):
        sensor = TestCoverageSensor()
        signal = sensor.detect({
            "module_name": "regressed",
            "coverage_percent": 70.0,
            "previous_coverage": 85.0,
            "has_test_file": True,
        })
        assert signal is not None
        assert "dropped" in signal.description
    
    def test_good_coverage_no_trigger(self):
        sensor = TestCoverageSensor()
        signal = sensor.detect({
            "module_name": "well_tested",
            "coverage_percent": 85.0,
            "has_test_file": True,
        })
        assert signal is None
    
    def test_critical_module_higher_floor(self):
        sensor = TestCoverageSensor()
        signal = sensor.detect({
            "module_name": "critical_auth",
            "coverage_percent": 65.0,
            "has_test_file": True,
            "critical_module": True,
        })
        assert signal is not None  # 65% < 80% critical floor
    
    def test_critical_very_low_triggers_full_suite(self):
        sensor = TestCoverageSensor()
        signal = sensor.detect({
            "module_name": "critical_auth",
            "coverage_percent": 20.0,
            "has_test_file": True,
            "critical_module": True,
        })
        assert signal is not None
        assert signal.data["recommended_action"] == "full_suite"
    
    def test_stub_generation(self, temp_dir):
        gen = TestCoverageGenerator(project_root=temp_dir)
        from packages.adaptive_system.adaptive_core import Assessment
        assessment = Assessment(
            should_adapt=True, severity=Severity.HIGH,
            domain_key="my_module", occurrences=2,
            description="Test stub", recommended_action="stub",
            approval_level=ApprovalLevel.AUTO,
        )
        resp = gen.generate(assessment)
        assert resp.response_type == "test_stub"
        assert "test_my_module.py" in resp.target_path
        assert "class TestMyModule" in resp.content
    
    def test_full_pipeline_auto_approved(self, temp_dir):
        system = create_test_coverage_adaptor(
            storage_dir=temp_dir / "adaptive",
            project_root=temp_dir,
        )
        # Non-critical with no tests = HIGH severity, stub action = AUTO approved
        result = system.process({
            "module_name": "simple_module",
            "coverage_percent": 0,
            "has_test_file": False,
            "critical_module": False,
        })
        assert result is not None
        assert result.executed is True
    
    def test_full_pipeline_gated(self, temp_dir):
        system = create_test_coverage_adaptor(
            storage_dir=temp_dir / "adaptive",
            project_root=temp_dir,
        )
        # Critical with very low coverage = full_suite = LEAD approval required
        result = system.process({
            "module_name": "critical_auth",
            "coverage_percent": 15,
            "has_test_file": True,
            "critical_module": True,
        })
        assert result is not None
        assert result.approved is False  # Gated
        assert "lead" in result.error.lower()


# ─────────────────────────────────────────────────────────────
# Knowledge Decay Detector Tests
# ─────────────────────────────────────────────────────────────

class TestKnowledgeDecay:
    def test_fresh_ki_no_trigger(self):
        sensor = KnowledgeDecaySensor()
        signal = sensor.detect({
            "ki_id": "fresh_ki",
            "ki_title": "Fresh Knowledge",
            "days_since_update": 5,
            "referenced_files": 10,
            "changed_files": 1,
        })
        # Decay score = 5 * (1/10 + 0) * 1.5 = 0.75 — below threshold
        assert signal is None
    
    def test_stale_ki_triggers_flag(self):
        sensor = KnowledgeDecaySensor()
        signal = sensor.detect({
            "ki_id": "stale_ki",
            "ki_title": "Stale Knowledge",
            "days_since_update": 30,
            "referenced_files": 10,
            "changed_files": 5,
            "ki_type": "reference",
        })
        assert signal is not None
        # Decay = 30 * (0.5 + 0) * 1.5 = 22.5 → flag
        assert signal.data["recommended_action"] == "flag"
    
    def test_very_stale_implementation_triggers_refresh(self):
        sensor = KnowledgeDecaySensor()
        signal = sensor.detect({
            "ki_id": "old_impl",
            "ki_title": "Old Implementation Docs",
            "days_since_update": 60,
            "referenced_files": 10,
            "changed_files": 8,
            "changed_functions": 6,
            "ki_type": "implementation",
        })
        assert signal is not None
        # Decay = 60 * (0.8 + 0.5) * 2.0 = 156 → rebuild
        assert signal.data["recommended_action"] == "rebuild"
        assert signal.severity == "critical"
    
    def test_no_referenced_files_no_trigger(self):
        sensor = KnowledgeDecaySensor()
        signal = sensor.detect({
            "ki_id": "abstract_ki",
            "days_since_update": 365,
            "referenced_files": 0,
            "changed_files": 0,
        })
        assert signal is None  # Can't decay without referenced files
    
    def test_process_ki_decays_slowly(self):
        sensor = KnowledgeDecaySensor()
        signal = sensor.detect({
            "ki_id": "process_ki",
            "ki_title": "Process Doc",
            "days_since_update": 30,
            "referenced_files": 10,
            "changed_files": 3,
            "ki_type": "process",
        })
        # Decay = 30 * (0.3 + 0) * 0.5 = 4.5 → below threshold
        assert signal is None
    
    def test_analyzer_approval_tiers(self):
        analyzer = KnowledgeDecayAnalyzer()
        from packages.adaptive_system.adaptive_core import Signal
        
        # Flag = auto
        sig = Signal(signal_type="test", source="test", severity="low",
                    data={"recommended_action": "flag", "decay_score": 20, "ki_title": "x", "ki_id": "x"})
        result = analyzer.assess(sig, 1, True)
        assert result.approval_level == ApprovalLevel.AUTO
        
        # Rebuild = executive
        sig2 = Signal(signal_type="test", source="test", severity="critical",
                     data={"recommended_action": "rebuild", "decay_score": 150, "ki_title": "x", "ki_id": "x"})
        result2 = analyzer.assess(sig2, 1, True)
        assert result2.approval_level == ApprovalLevel.EXECUTIVE
    
    def test_full_pipeline_auto_flag(self, temp_dir):
        system = create_knowledge_decay_detector(storage_dir=temp_dir)
        
        # Moderate decay = flag action = AUTO approved
        result = system.process({
            "ki_id": "aging_ki",
            "ki_title": "Aging KI",
            "days_since_update": 30,
            "referenced_files": 10,
            "changed_files": 5,
            "ki_type": "reference",
        })
        
        assert result is not None
        assert result.approved is True
        assert result.executed is True
    
    def test_full_pipeline_gated_rebuild(self, temp_dir):
        system = create_knowledge_decay_detector(storage_dir=temp_dir)
        
        # Heavy decay = rebuild = EXECUTIVE approval required
        result = system.process({
            "ki_id": "old_architecture",
            "ki_title": "Old Architecture KI",
            "days_since_update": 90,
            "referenced_files": 10,
            "changed_files": 7,
            "changed_functions": 5,
            "ki_type": "implementation",
        })
        
        assert result is not None
        assert result.approved is False  # Gated
        assert "executive" in result.error.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
