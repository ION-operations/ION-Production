"""
Test Coverage Adaptor — Auto-detects untested code and spawns QA agents.

Detects modules with low/dropping test coverage and responds by:
- Generating test stub files for uncovered modules
- Spawning AGENT-UNIT-TEST for deep test generation
- Spawning AGENT-INTEGRATION-TEST for cross-module scenarios
- Spawning AGENT-PERF for performance regression detection

NL_TAG: ADAPTIVE-TEST-001 | Auto-detect and fill test coverage gaps | TestCoverageAdaptor | [ADAPTIVE-CORE-001]
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from .adaptive_core import (
    AdaptiveSensor, AdaptiveTracker, AdaptiveAnalyzer,
    AdaptiveGenerator, AdaptiveGatekeeper, AdaptiveSystem,
    Signal, Assessment, AdaptiveResponse,
    Severity, ApprovalLevel,
)

logger = logging.getLogger("adaptive_system.test_coverage")


# ─────────────────────────────────────────────────────────────
# Test Action Levels
# ─────────────────────────────────────────────────────────────

TEST_ACTIONS = {
    "stub":        {"name": "Test Stub", "action": "Create test file skeleton", "agents": 0},
    "unit":        {"name": "Unit Tests", "action": "Spawn AGENT-UNIT-TEST", "agents": 1},
    "integration": {"name": "Integration Tests", "action": "Spawn AGENT-INTEGRATION-TEST", "agents": 1},
    "perf":        {"name": "Performance Tests", "action": "Spawn AGENT-PERF", "agents": 1},
    "full_suite":  {"name": "Full QA Suite", "action": "Spawn QA division", "agents": 3},
}


# ─────────────────────────────────────────────────────────────
# Sensor
# ─────────────────────────────────────────────────────────────

class TestCoverageSensor(AdaptiveSensor):
    """
    Detects modules with insufficient test coverage.
    
    Context expected:
        module_name: str — package or module being assessed
        coverage_percent: float — current line coverage (0-100)
        previous_coverage: float — coverage at last check (0-100)
        total_lines: int — total lines in module
        uncovered_lines: int — lines not covered by tests
        has_test_file: bool — whether a test file exists
        changed_since_last_test: int — files changed since last test update
        critical_module: bool — whether this is a core/critical module
    """
    
    COVERAGE_FLOOR = 60.0       # Below this = needs tests
    COVERAGE_DROP_ALERT = 10.0  # Drop of 10%+ = regression
    CRITICAL_FLOOR = 80.0       # Critical modules need higher coverage
    
    def detect(self, context: Dict[str, Any]) -> Optional[Signal]:
        module_name = context.get("module_name", "")
        if not module_name:
            return None
        
        coverage = context.get("coverage_percent", 100.0)
        previous = context.get("previous_coverage", coverage)
        has_test = context.get("has_test_file", True)
        critical = context.get("critical_module", False)
        changed = context.get("changed_since_last_test", 0)
        uncovered = context.get("uncovered_lines", 0)
        
        floor = self.CRITICAL_FLOOR if critical else self.COVERAGE_FLOOR
        drop = previous - coverage
        
        problems = []
        _RANK = {"low": 0, "medium": 1, "high": 2, "critical": 3}
        sev_rank = 0
        
        # No test file at all
        if not has_test:
            problems.append("no test file exists")
            sev_rank = max(sev_rank, 2 if not critical else 3)
            action = "stub"
        # Coverage below floor
        elif coverage < floor:
            problems.append(f"coverage {coverage:.0f}% < {floor:.0f}% floor")
            sev_rank = max(sev_rank, 2 if coverage > 30 else 3)
            action = "unit"
        # Coverage dropped significantly
        elif drop >= self.COVERAGE_DROP_ALERT:
            problems.append(f"coverage dropped {drop:.0f}% ({previous:.0f}% → {coverage:.0f}%)")
            sev_rank = max(sev_rank, 2)
            action = "unit"
        # Many changes without test update
        elif changed >= 5:
            problems.append(f"{changed} files changed without test update")
            sev_rank = max(sev_rank, 1)
            action = "unit"
        else:
            return None
        
        # Escalate for critical modules
        if critical and coverage < 40:
            action = "full_suite"
            sev_rank = 3
        
        _NAME = {0: "low", 1: "medium", 2: "high", 3: "critical"}
        
        return Signal(
            signal_type="low_test_coverage",
            source="pytest_cov",
            severity=_NAME[sev_rank],
            description=f"Test coverage issue for '{module_name}': {', '.join(problems)}",
            data={
                "module_name": module_name,
                "coverage_percent": coverage,
                "previous_coverage": previous,
                "coverage_drop": drop,
                "has_test_file": has_test,
                "critical_module": critical,
                "uncovered_lines": uncovered,
                "recommended_action": action,
            },
        )
    
    def get_domain_key(self, signal: Signal) -> str:
        return signal.data.get("module_name", "unknown").lower().strip()


# ─────────────────────────────────────────────────────────────
# Analyzer
# ─────────────────────────────────────────────────────────────

class TestCoverageAnalyzer(AdaptiveAnalyzer):
    """Assesses test coverage gaps and determines response."""
    
    def assess(self, signal: Signal, occurrences: int, exceeds_threshold: bool) -> Assessment:
        action = signal.data.get("recommended_action", "stub")
        critical = signal.data.get("critical_module", False)
        
        # Stubs auto-approved, unit tests need review, full suite needs lead
        if action == "stub":
            approval = ApprovalLevel.AUTO
        elif action in ("unit", "integration"):
            approval = ApprovalLevel.AUTO  # Test generation is safe
        elif action == "perf":
            approval = ApprovalLevel.LEAD
        else:  # full_suite
            approval = ApprovalLevel.LEAD
        
        severity_map = {"low": Severity.LOW, "medium": Severity.MEDIUM, "high": Severity.HIGH, "critical": Severity.CRITICAL}
        severity = severity_map.get(signal.severity, Severity.MEDIUM)
        
        # Respond after 2 detections (not just noise)
        should_adapt = exceeds_threshold or severity in (Severity.HIGH, Severity.CRITICAL)
        
        return Assessment(
            should_adapt=should_adapt,
            severity=severity,
            domain_key=signal.data.get("module_name", "unknown"),
            occurrences=occurrences,
            description=f"Generate {TEST_ACTIONS[action]['name']} for {signal.data.get('module_name')}",
            recommended_action=action,
            approval_level=approval,
            confidence=max(0, 1.0 - signal.data.get("coverage_percent", 0) / 100),
            metadata={"action_info": TEST_ACTIONS[action]},
        )


# ─────────────────────────────────────────────────────────────
# Generator
# ─────────────────────────────────────────────────────────────

class TestCoverageGenerator(AdaptiveGenerator):
    """Generates test stubs or spawn commands for QA agents."""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()
    
    def generate(self, assessment: Assessment) -> AdaptiveResponse:
        action = assessment.recommended_action
        module = assessment.domain_key
        
        if action == "stub":
            content = self._generate_test_stub(module)
            target = str(self.project_root / "packages" / module / "tests" / f"test_{module}.py")
            return AdaptiveResponse(
                response_type="test_stub",
                content=content,
                target_path=target,
                description=f"Test stub for {module}",
            )
        elif action in ("unit", "integration", "perf"):
            agent_map = {
                "unit": "agent-unit-test",
                "integration": "agent-integration-test",
                "perf": "agent-perf",
            }
            agent = agent_map[action]
            command = (
                f"python scripts/ai_engine/genome_assembler.py spawn {agent} "
                f"--task 'Generate {action} tests for {module}'"
            )
            return AdaptiveResponse(
                response_type=f"test_{action}",
                content={"command": command, "agent": agent, "module": module},
                description=f"Spawn {agent} for {module} {action} tests",
            )
        else:  # full_suite
            command = (
                f"python scripts/ai_engine/genome_assembler.py spawn-division qa "
                f"--task 'Full QA suite for {module}'"
            )
            return AdaptiveResponse(
                response_type="test_full_suite",
                content={"command": command, "module": module},
                description=f"Spawn QA division for {module}",
            )
    
    def _generate_test_stub(self, module: str) -> str:
        """Generate a minimal test file skeleton."""
        class_name = module.replace("_", " ").title().replace(" ", "")
        return f'''"""
Tests for {module}

Auto-generated by Test Coverage Adaptor.
Needs human implementation of test logic.
"""

import pytest


class Test{class_name}:
    """Test suite for {module}."""
    
    def test_import(self):
        """Verify module can be imported."""
        import packages.{module}
    
    def test_placeholder(self):
        """Placeholder — implement real tests."""
        # TODO: Replace with actual test assertions
        assert True
'''
    
    def execute(self, response: AdaptiveResponse) -> AdaptiveResponse:
        """Write test stub or log spawn command."""
        if response.response_type == "test_stub" and response.target_path:
            target = Path(response.target_path)
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                target.write_text(response.content, encoding="utf-8")
                logger.info(f"Test stub written: {target}")
            else:
                logger.info(f"Test file already exists, skipping: {target}")
        else:
            logger.info(f"Test command ready: {response.content}")
        
        response.executed = True
        return response


# ─────────────────────────────────────────────────────────────
# Factory
# ─────────────────────────────────────────────────────────────

def create_test_coverage_adaptor(
    storage_dir: Optional[Path] = None,
    project_root: Optional[Path] = None,
) -> AdaptiveSystem:
    """Create a fully wired Test Coverage Adaptor."""
    storage = storage_dir or (Path.cwd() / ".agent" / "adaptive")
    
    return AdaptiveSystem(
        name="Test Coverage",
        sensor=TestCoverageSensor(),
        tracker=AdaptiveTracker(
            storage_path=storage / "test_coverage.json",
            threshold=2,  # Flag after 2nd detection
            window_days=14,
        ),
        analyzer=TestCoverageAnalyzer(),
        generator=TestCoverageGenerator(project_root),
        gatekeeper=AdaptiveGatekeeper(proposals_dir=storage / "proposals"),
    )
