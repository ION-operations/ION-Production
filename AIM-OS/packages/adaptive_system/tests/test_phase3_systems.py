"""
Tests for Phase 3 Adaptive Systems: Security Posture + Architectural Drift.
"""

import tempfile
from pathlib import Path

import pytest

from packages.adaptive_system.security_posture import (
    SecurityPostureSensor, SecurityPostureAnalyzer,
    create_security_posture_adaptor,
)
from packages.adaptive_system.arch_drift import (
    ArchDriftSensor, ArchDriftAnalyzer,
    create_arch_drift_detector,
)
from packages.adaptive_system.adaptive_core import Severity, ApprovalLevel


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


# ─────────────────────────────────────────────────────────────
# Security Posture Tests
# ─────────────────────────────────────────────────────────────

class TestSecurityPosture:
    def test_new_dependency_triggers(self):
        sensor = SecurityPostureSensor()
        signal = sensor.detect({
            "change_type": "new_dependency",
            "module_name": "api_gateway",
            "new_dependencies": ["lodash@4.17.21", "express@5.0.0"],
        })
        assert signal is not None
        assert signal.data["recommended_action"] == "dep_audit"
    
    def test_new_endpoint_triggers(self):
        sensor = SecurityPostureSensor()
        signal = sensor.detect({
            "change_type": "new_endpoint",
            "module_name": "user_service",
            "new_endpoints": ["/api/users/delete", "/api/admin/reset"],
        })
        assert signal is not None
        assert signal.data["recommended_action"] == "endpoint_scan"
    
    def test_secret_env_var_critical(self):
        sensor = SecurityPostureSensor()
        signal = sensor.detect({
            "change_type": "new_env_var",
            "module_name": "config",
            "new_env_vars": ["DATABASE_URL", "API_SECRET_KEY"],
        })
        assert signal is not None
        assert signal.severity == "critical"  # SECRET_KEY matches
    
    def test_safe_env_var_low(self):
        sensor = SecurityPostureSensor()
        signal = sensor.detect({
            "change_type": "new_env_var",
            "module_name": "config",
            "new_env_vars": ["LOG_LEVEL", "NODE_ENV"],
        })
        assert signal is not None
        assert signal.severity == "medium"  # No keyword match
    
    def test_permission_change_critical(self):
        sensor = SecurityPostureSensor()
        signal = sensor.detect({
            "change_type": "permission_change",
            "module_name": "auth_service",
            "details": "Changed admin role to allow file deletion",
        })
        assert signal is not None
        assert signal.severity == "critical"
        assert signal.data["recommended_action"] == "full_audit"
    
    def test_no_change_type_no_trigger(self):
        sensor = SecurityPostureSensor()
        signal = sensor.detect({"module_name": "safe_module"})
        assert signal is None
    
    def test_dep_audit_auto_approved(self):
        analyzer = SecurityPostureAnalyzer()
        from packages.adaptive_system.adaptive_core import Signal
        sig = Signal(signal_type="test", source="test", severity="high",
                    data={"recommended_action": "dep_audit", "module_name": "x"})
        result = analyzer.assess(sig, 1, True)
        assert result.approval_level == ApprovalLevel.AUTO
    
    def test_full_audit_needs_executive(self):
        analyzer = SecurityPostureAnalyzer()
        from packages.adaptive_system.adaptive_core import Signal
        sig = Signal(signal_type="test", source="test", severity="critical",
                    data={"recommended_action": "full_audit", "module_name": "x"})
        result = analyzer.assess(sig, 1, True)
        assert result.approval_level == ApprovalLevel.EXECUTIVE
    
    def test_full_pipeline_auto(self, temp_dir):
        system = create_security_posture_adaptor(storage_dir=temp_dir)
        result = system.process({
            "change_type": "new_dependency",
            "module_name": "api",
            "new_dependencies": ["axios@1.0.0"],
        })
        assert result is not None
        assert result.approved is True  # dep_audit = auto
        assert result.executed is True
    
    def test_full_pipeline_gated(self, temp_dir):
        system = create_security_posture_adaptor(storage_dir=temp_dir)
        result = system.process({
            "change_type": "permission_change",
            "module_name": "auth",
            "details": "Added admin bypass",
        })
        assert result is not None
        assert result.approved is False  # full_audit = executive
        assert "executive" in result.error.lower()


# ─────────────────────────────────────────────────────────────
# Architectural Drift Tests
# ─────────────────────────────────────────────────────────────

class TestArchDrift:
    def test_layer_bypass_triggers(self):
        sensor = ArchDriftSensor()
        signal = sensor.detect({
            "rule_id": "layer_bypass",
            "module_name": "api_handler",
            "file_path": "packages/api/handler.py",
            "description": "Direct SQL query in API handler",
        })
        assert signal is not None
        assert signal.severity == "high"
        assert signal.data["recommended_action"] == "refactor"
    
    def test_naming_violation_low(self):
        sensor = ArchDriftSensor()
        signal = sensor.detect({
            "rule_id": "naming_violation",
            "module_name": "utils",
            "description": "Function uses camelCase instead of snake_case",
        })
        assert signal is not None
        assert signal.severity == "low"
        assert signal.data["recommended_action"] == "warning"
    
    def test_god_module_auto_detected(self):
        sensor = ArchDriftSensor()
        signal = sensor.detect({
            "module_name": "monolith",
            "module_complexity": 75,  # Above 50 threshold
        })
        assert signal is not None
        assert signal.data["rule_id"] == "god_module"
    
    def test_below_complexity_no_trigger(self):
        sensor = ArchDriftSensor()
        signal = sensor.detect({
            "module_name": "small_module",
            "module_complexity": 20,
        })
        assert signal is None
    
    def test_repeated_violations_escalate(self):
        sensor = ArchDriftSensor()
        signal = sensor.detect({
            "rule_id": "naming_violation",
            "module_name": "messy_module",
            "violation_count": 8,  # >= 5 -> escalates severity
        })
        assert signal is not None
        # naming_violation is "low" but 8 violations escalates to "medium"
        assert signal.severity == "medium"
    
    def test_unknown_rule_no_trigger(self):
        sensor = ArchDriftSensor()
        signal = sensor.detect({
            "rule_id": "nonexistent_rule",
            "module_name": "test",
        })
        assert signal is None
    
    def test_warning_auto_approved(self):
        analyzer = ArchDriftAnalyzer()
        from packages.adaptive_system.adaptive_core import Signal
        sig = Signal(signal_type="test", source="test", severity="low",
                    data={"recommended_action": "warning", "rule_id": "x", "module_name": "x", "violation_count": 1})
        result = analyzer.assess(sig, 1, False)
        assert result.approval_level == ApprovalLevel.AUTO
    
    def test_refactor_needs_lead(self):
        analyzer = ArchDriftAnalyzer()
        from packages.adaptive_system.adaptive_core import Signal
        sig = Signal(signal_type="test", source="test", severity="high",
                    data={"recommended_action": "refactor", "rule_id": "x", "module_name": "x", "violation_count": 3})
        result = analyzer.assess(sig, 3, True)
        assert result.approval_level == ApprovalLevel.LEAD
    
    def test_full_pipeline_high_severity(self, temp_dir):
        system = create_arch_drift_detector(
            storage_dir=temp_dir / "adaptive",
            audit_log_dir=temp_dir / "reports",
        )
        # High severity = bypasses threshold
        result = system.process({
            "rule_id": "layer_bypass",
            "module_name": "api_handler",
            "file_path": "handler.py",
            "description": "Direct DB access",
        })
        assert result is not None
        # refactor needs lead approval
        assert result.approved is False
        assert "lead" in result.error.lower()
    
    def test_full_pipeline_accumulation(self, temp_dir):
        system = create_arch_drift_detector(
            storage_dir=temp_dir / "adaptive",
            audit_log_dir=temp_dir / "reports",
        )
        # Low severity — needs 3 occurrences
        r1 = system.process({"rule_id": "naming_violation", "module_name": "utils"})
        assert r1 is None  # 1/3
        
        r2 = system.process({"rule_id": "naming_violation", "module_name": "utils"})
        assert r2 is None  # 2/3
        
        r3 = system.process({"rule_id": "naming_violation", "module_name": "utils"})
        assert r3 is not None  # 3/3 = threshold!
        assert r3.approved is True  # warning = auto


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
