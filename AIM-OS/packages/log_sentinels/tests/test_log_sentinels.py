"""
Log-Sentinels system test suite - comprehensive unit and integration tests.
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from log_sentinels.core.pipeline import LogSentinelsPipeline
from log_sentinels.core.collectors import LogCollector
from log_sentinels.core.normalizer import LogNormalizer
from log_sentinels.core.template_miner import LogTemplateMiner
from log_sentinels.core.windower import Windower
from log_sentinels.core.scout import ScoutAdapter
from log_sentinels.core.forensics import ForensicsAdapter
from log_sentinels.core.router_policy import RouterPolicy
from log_sentinels.types import (
    LogRecord,
    LogLevel,
    Window,
    ScoutReport,
    ForensicsReport,
    Severity,
    RedactionPattern,
    RedactionConfig
)


@pytest.fixture
def sample_log_record():
    """Create a sample log record."""
    return LogRecord(
        ts="2025-01-01T00:00:00Z",
        source="browser.console",
        level=LogLevel.ERROR,
        template="Error in {component}: {message}",
        vars={"component": "router", "message": "Connection failed"},
        raw_hash="abc123",
        raw="Error in router: Connection failed"
    )


@pytest.fixture
def redaction_config():
    """Create redaction configuration."""
    patterns = [
        RedactionPattern(
            name="bearer_tokens",
            regex=r"(?i)bearer\s+[a-z0-9\._\-]+",
            replacement="BEARER_TOKEN"
        ),
        RedactionPattern(
            name="emails",
            regex=r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
            replacement="EMAIL_REDACTED"
        )
    ]
    return RedactionConfig(patterns=patterns)


class TestLogNormalizer:
    """Test log normalization and PII redaction."""
    
    def test_normalize_with_redaction(self, sample_log_record, redaction_config):
        """Test log normalization with PII redaction."""
        normalizer = LogNormalizer(redaction_config)
        
        # Create record with PII
        record_with_pii = LogRecord(
            ts="2025-01-01T00:00:00Z",
            source="browser.console",
            level=LogLevel.INFO,
            template="User {email} logged in",
            vars={"email": "user@example.com"},
            raw_hash="def456",
            raw="User user@example.com logged in"
        )
        
        normalized = normalizer.normalize(record_with_pii)
        
        # Email should be redacted
        assert "EMAIL_REDACTED" in normalized.raw or "user@example.com" not in normalized.raw
        assert normalized.raw_hash == "def456"  # Hash should remain
    
    def test_normalize_preserves_structure(self, sample_log_record, redaction_config):
        """Test that normalization preserves log structure."""
        normalizer = LogNormalizer(redaction_config)
        normalized = normalizer.normalize(sample_log_record)
        
        assert normalized.ts == sample_log_record.ts
        assert normalized.source == sample_log_record.source
        assert normalized.level == sample_log_record.level
        assert normalized.template == sample_log_record.template


class TestWindower:
    """Test windowing system."""
    
    @pytest.mark.asyncio
    async def test_create_window(self):
        """Test creating a log window."""
        windower = Windower(roll_seconds=60, min_records=5)
        
        records = [
            LogRecord(
                ts=f"2025-01-01T00:00:{i:02d}Z",
                source="browser.console",
                level=LogLevel.INFO,
                template="Log {id}",
                vars={"id": i},
                raw_hash=f"hash{i}",
                raw=f"Log {i}"
            )
            for i in range(10)
        ]
        
        window = await windower.create_window(records)
        
        if window:
            assert window.size >= windower.min_records
            assert window.source == records[0].source
    
    @pytest.mark.asyncio
    async def test_window_insufficient_records(self):
        """Test windowing with insufficient records."""
        windower = Windower(roll_seconds=60, min_records=10)
        
        records = [
            LogRecord(
                ts="2025-01-01T00:00:00Z",
                source="browser.console",
                level=LogLevel.INFO,
                template="Log",
                vars={},
                raw_hash="hash",
                raw="Log"
            )
            for _ in range(5)  # Less than min_records
        ]
        
        window = await windower.create_window(records)
        assert window is None


class TestRouterPolicy:
    """Test Router policy for escalation decisions."""
    
    def test_decide_keep(self):
        """Test decision to keep (not escalate)."""
        policy = RouterPolicy()
        
        report = ScoutReport(
            window_id="win1",
            summary="Low severity issue",
            confidence=0.9,
            severity=Severity.LOW,
            tags=[],
            suggested_tools=[]
        )
        
        decision = policy.decide(report, novelty=0.3)
        assert decision.kind == "keep"
    
    def test_decide_escalate_high_severity(self):
        """Test escalation for high severity."""
        policy = RouterPolicy()
        
        report = ScoutReport(
            window_id="win1",
            summary="High severity issue",
            confidence=0.7,
            severity=Severity.HIGH,
            tags=[],
            suggested_tools=[]
        )
        
        decision = policy.decide(report, novelty=0.5)
        assert decision.kind == "escalate"
    
    def test_decide_escalate_low_confidence(self):
        """Test escalation for low confidence."""
        policy = RouterPolicy()
        
        report = ScoutReport(
            window_id="win1",
            summary="Uncertain issue",
            confidence=0.6,  # Below threshold
            severity=Severity.MEDIUM,
            tags=[],
            suggested_tools=[]
        )
        
        decision = policy.decide(report, novelty=0.8)  # High novelty
        assert decision.kind == "escalate"


class TestScoutAdapter:
    """Test Scout adapter (cloud LLM)."""
    
    @pytest.mark.asyncio
    async def test_analyze_window(self):
        """Test analyzing a log window."""
        scout = ScoutAdapter(api_key="test_key")
        
        window = Window(
            id="win1",
            source="browser.console",
            from_time=1000,
            to_time=2000,
            size=10,
            templates={"error": 5, "info": 5},
            sample=["Error log 1", "Error log 2"]
        )
        
        # Mock LLM call
        with patch.object(scout, '_call_llm', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = '{"summary": "Test summary", "confidence": 0.8, "severity": "medium", "tags": ["error"], "suggested_tools": ["test_tool"]}'
            
            report = await scout.analyze(window)
            
            assert isinstance(report, ScoutReport)
            assert report.window_id == window.id


class TestForensicsAdapter:
    """Test Forensics adapter (local LLM)."""
    
    @pytest.mark.asyncio
    async def test_analyze_with_context(self):
        """Test forensics analysis with context."""
        forensics = ForensicsAdapter(model="llama3:8b-instruct-q4")
        
        window = Window(
            id="win1",
            source="browser.console",
            from_time=1000,
            to_time=2000,
            size=10,
            templates={"error": 10},
            sample=["Error log"]
        )
        
        context = {
            "window": window,
            "recent_diffs": [],
            "failing_tests": []
        }
        
        # Mock LLM call
        with patch.object(forensics, '_call_llm', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = '{"summary": "Root cause found", "confidence": 0.9, "severity": "high", "tags": ["error"], "suggested_tools": ["fix_tool"], "root_cause": "Memory leak", "fix_suggestion": {"steps": ["Fix leak"]}, "evidence": ["ev1"]}'
            
            report = await forensics.analyze(window, context)
            
            assert isinstance(report, ForensicsReport)
            assert report.root_cause is not None
            assert report.fix_suggestion is not None


class TestLogSentinelsPipeline:
    """Test Log-Sentinels pipeline."""
    
    @pytest.fixture
    def mock_collector(self):
        """Create mock log collector."""
        collector = Mock(spec=LogCollector)
        collector.collect = AsyncMock(return_value=[
            LogRecord(
                ts="2025-01-01T00:00:00Z",
                source="browser.console",
                level=LogLevel.ERROR,
                template="Error",
                vars={},
                raw_hash="hash",
                raw="Error message"
            )
        ])
        return collector
    
    @pytest.fixture
    def pipeline(self, mock_collector, redaction_config):
        """Create Log-Sentinels pipeline."""
        normalizer = LogNormalizer(redaction_config)
        template_miner = LogTemplateMiner()
        windower = Windower(roll_seconds=60, min_records=1)
        scout = ScoutAdapter(api_key="test")
        forensics = ForensicsAdapter()
        router_policy = RouterPolicy()
        
        return LogSentinelsPipeline(
            collectors=[mock_collector],
            normalizer=normalizer,
            template_miner=template_miner,
            windower=windower,
            scout=scout,
            forensics=forensics,
            router_policy=router_policy
        )
    
    @pytest.mark.asyncio
    async def test_collect_and_process(self, pipeline):
        """Test collecting and processing logs."""
        # Mock Scout and Forensics
        with patch.object(pipeline.scout, 'analyze', new_callable=AsyncMock) as mock_scout:
            mock_scout.return_value = ScoutReport(
                window_id="win1",
                summary="Test summary",
                confidence=0.8,
                severity=Severity.MEDIUM,
                tags=[],
                suggested_tools=[]
            )
            
            result = await pipeline.collect_and_process()
            
            assert "status" in result or "scout_report" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

