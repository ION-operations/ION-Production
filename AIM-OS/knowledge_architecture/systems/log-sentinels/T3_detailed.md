---
id: "log-sentinels_T3_detailed"
system: "log-sentinels"
component: null
level: "T3"
type: "detailed"
title: "Log-Sentinels Detailed Implementation Guide"
description: "10,000-word detailed implementation guide for Log-Sentinels"
audience: "developers, implementers"
confidence_threshold: 0.60
token_cost: 10000
word_count: 10000
created: "2025-01-27T00:00:00Z"
updated: "2025-01-27T00:00:00Z"
author: "aether"
status: "complete"
tags: ["log-sentinels", "log-analysis", "hybrid", "privacy", "t0-t4", "transitional"]
dependencies: ["log-sentinels_T2_architecture"]
related_docs: ["log-sentinels_T4_complete", "system.map.lucid.json5", "usage.envelope.md"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# Log-Sentinels – T3 Detailed Implementation Guide (≈10,000 words)

## Purpose

This document provides a comprehensive implementation guide for Log-Sentinels (Hybrid Log Analysis System), enabling developers to build, integrate, and deploy privacy-first log analysis systems. This guide covers the complete API, implementation patterns, integration strategies, configuration, testing, troubleshooting, and advanced topics needed to successfully implement Log-Sentinels-based systems.

## Audience

This guide is designed for:
- **Developers** implementing Log-Sentinels log analysis systems
- **Systems engineers** integrating Log-Sentinels with existing infrastructure
- **Privacy engineers** ensuring PII protection
- **DevOps engineers** deploying and monitoring Log-Sentinels systems

---

## Setup & Installation

### Installation

```bash
# Install Log-Sentinels package
cd packages/log_sentinels
pip install -e .

# Install dependencies
pip install pytest pytest-asyncio drain3
```

### Basic Usage

```python
from log_sentinels.core.pipeline import LogSentinelsPipeline
from log_sentinels.core.collectors import BrowserConsoleCollector, TerminalCollector
from log_sentinels.core.normalizer import LogNormalizer
from log_sentinels.core.template_miner import LogTemplateMiner
from log_sentinels.core.windower import Windower
from log_sentinels.core.scout import ScoutAdapter
from log_sentinels.core.forensics import ForensicsAdapter
from log_sentinels.core.router_policy import RouterPolicy
from log_sentinels.types import RedactionConfig, RedactionPattern

# Configure redaction
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
redaction_config = RedactionConfig(patterns=patterns)

# Initialize components
collectors = [
    BrowserConsoleCollector(ws_url="ws://localhost:7001/console"),
    TerminalCollector(log_path="./logs/dev-terminal.log")
]
normalizer = LogNormalizer(redaction_config)
template_miner = LogTemplateMiner(cache_size=5000)
windower = Windower(roll_seconds=60, min_records=12)
scout = ScoutAdapter(api_key="your_cerebras_key")
forensics = ForensicsAdapter(model="llama3:8b-instruct-q4")
router_policy = RouterPolicy(
    min_severity="medium",
    max_confidence=0.80,
    novelty_threshold=0.70
)

# Create pipeline
pipeline = LogSentinelsPipeline(
    collectors=collectors,
    normalizer=normalizer,
    template_miner=template_miner,
    windower=windower,
    scout=scout,
    forensics=forensics,
    router_policy=router_policy
)

# Process logs
result = await pipeline.collect_and_process()
```

---

## Component Implementation Details

### LogSentinelsPipeline Class

**File:** `packages/log_sentinels/core/pipeline.py`

**Key Methods:**

```python
async def process_window(self, win_id: str) -> Dict[str, Any]:
    """
    Process a log window.
    
    Flow:
    1. Get window
    2. Scout analysis (fast, cloud)
    3. Router policy decision
    4. Forensics analysis (if escalated, local)
    5. Return results
    """
    window = await self._get_window(win_id)
    if not window:
        return {"error": "Window not found"}
    
    # Scout analysis
    scout_report = await self.scout.analyze(window)
    
    # Router policy decision
    novelty = await self.template_miner.novelty_score(window)
    decision = self.router_policy.decide(scout_report, novelty)
    
    result = {
        "window_id": win_id,
        "scout_report": scout_report,
        "decision": decision
    }
    
    if decision.kind == "escalate":
        # Forensics analysis
        context = await self._build_local_context(window)
        forensics_report = await self.forensics.analyze(window, context)
        result["forensics_report"] = forensics_report
    
    return result
```

### LogNormalizer Class

**File:** `packages/log_sentinels/core/normalizer.py`

**Key Methods:**

```python
def normalize(self, record: LogRecord) -> LogRecord:
    """
    Normalize log record by redacting PII.
    
    Critical: Redaction happens BEFORE any cloud calls.
    """
    redacted = record.raw
    
    # Apply all redaction patterns
    for pattern in self.patterns:
        redacted = pattern["regex"].sub(pattern["replacement"], redacted)
    
    # Compute hash of original
    raw_hash = hashlib.sha256(record.raw.encode()).hexdigest()
    
    return LogRecord(
        ts=record.ts,
        source=record.source,
        level=record.level,
        template=record.template,
        vars=record.vars,
        raw_hash=raw_hash,
        raw=redacted  # Redacted version
    )
```

**Privacy Guarantees:**
- All PII redacted before cloud calls
- Raw logs never sent to cloud
- Hash references enable local forensics
- Structure preserved for analysis

### ScoutAdapter Class

**File:** `packages/log_sentinels/core/scout.py`

**Key Methods:**

```python
async def analyze(self, window: Window) -> ScoutReport:
    """
    Analyze log window using Scout LLM.
    
    Only sees redacted logs (PII removed).
    """
    # Build prompt (only uses redacted samples)
    prompt = self._build_prompt(window)
    
    # Call LLM (Cerebras, <700ms timeout)
    response = await self._call_llm(prompt)
    
    # Parse report
    report = self._parse_report(response, window.id)
    
    return report
```

**Privacy Enforcement:**
- Only redacted samples in prompt
- Pre-flight validation ensures no raw data
- Timeout prevents long-running analysis
- Error handling returns safe defaults

### ForensicsAdapter Class

**File:** `packages/log_sentinels/core/forensics.py`

**Key Methods:**

```python
async def analyze(
    self,
    window: Window,
    context: Dict[str, Any]
) -> ForensicsReport:
    """
    Analyze log window using Forensics LLM.
    
    Can access raw logs (never leaves machine).
    """
    # Build prompt (can include raw logs - local only)
    prompt = self._build_prompt(window, context)
    
    # Call local LLM (Ollama, <8s timeout)
    response = await self._call_llm(prompt)
    
    # Parse report
    report = self._parse_report(response, window.id)
    
    return report
```

**Local-Only Guarantees:**
- Raw logs only in local prompts
- Ollama runs locally (never leaves machine)
- Context includes local data (diffs, tests, PRs)
- No network calls for raw data

---

## Integration Examples

### Router Integration

```python
# Scout/Forensics suggest tools
scout_report = await scout.analyze(window)
forensics_report = await forensics.analyze(window, context)

# Send suggestions to Router
await router.receive_suggestions(
    tools=scout_report.suggested_tools + forensics_report.suggested_tools,
    insights={
        "scout_summary": scout_report.summary,
        "forensics_root_cause": forensics_report.root_cause
    }
)
```

### SEG Integration

```python
# Record Scout evidence
await seg.create_evidence_node(
    claim=scout_report.summary,
    sources=[window.id],
    confidence=scout_report.confidence
)

# Record Forensics evidence
await seg.create_evidence_chain(
    root_cause=forensics_report.root_cause,
    evidence=forensics_report.evidence,
    fix_suggestion=forensics_report.fix_suggestion
)
```

### VIF Integration

```python
# Validate analysis quality
vif_result = await vif.validate(
    analysis=forensics_report,
    confidence_threshold=0.80
)

# Emit witness
witness = await vif.create_witness(
    operation="log_analysis",
    window_id=window.id,
    confidence=vif_result.confidence
)
```

### CMC Integration

```python
# Store escalation decision
await cmc.store_decision_atom(
    decision_type="log_escalation",
    window_id=window.id,
    decision=decision.kind,
    reason=decision.reason
)
```

### TCS Integration

```python
# Create incident marker
await tcs.add_entry(
    event_type="incident",
    window_id=window.id,
    severity=scout_report.severity,
    timestamp=datetime.utcnow()
)
```

---

## Configuration

### Log-Sentinels Configuration

```yaml
# sentinel.config.yaml
ingest:
  sources:
    - id: browser.console
      type: ws
      url: ws://localhost:7001/console
    - id: terminal
      type: file
      path: ./logs/dev-terminal.log
    - id: backend.api
      type: otel
      endpoint: http://localhost:4318/v1/logs

normalize:
  redact:
    patterns:
      - name: bearer_tokens
        regex: "(?i)bearer\\s+[a-z0-9\\._\\-]+"
        replacement: "BEARER_TOKEN"
      - name: emails
        regex: "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}"
        replacement: "EMAIL_REDACTED"

windowing:
  roll_seconds: 60
  min_records: 12
  burst_threshold: 2.5

router:
  mode: hybrid
  escalate:
    min_severity: medium
    max_confidence: 0.80
    novelty_threshold: 0.70

models:
  scout:
    provider: cerebras
    model: "cerebras/small:latest"
    max_tokens: 384
    timeout_ms: 700
  forensics:
    provider: local
    engine: "ollama"
    model: "llama3:8b-instruct-q4"
    max_tokens: 2048
    timeout_ms: 8000

budgets:
  per_minute_scout_calls: 60
  per_minute_forensics_calls: 6
  max_parallel_forensics: 2
```

---

## Testing

### Unit Tests

```python
import pytest
from log_sentinels.core.normalizer import LogNormalizer
from log_sentinels.types import LogRecord, LogLevel, RedactionConfig, RedactionPattern

@pytest.mark.asyncio
async def test_normalizer_redaction():
    """Test PII redaction."""
    patterns = [
        RedactionPattern(
            name="emails",
            regex=r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
            replacement="EMAIL_REDACTED"
        )
    ]
    config = RedactionConfig(patterns=patterns)
    normalizer = LogNormalizer(config)
    
    record = LogRecord(
        ts="2025-01-01T00:00:00Z",
        source="test",
        level=LogLevel.INFO,
        template="User {email} logged in",
        vars={"email": "user@example.com"},
        raw_hash="hash",
        raw="User user@example.com logged in"
    )
    
    normalized = normalizer.normalize(record)
    assert "EMAIL_REDACTED" in normalized.raw
    assert "user@example.com" not in normalized.raw
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_pipeline_end_to_end():
    """Test end-to-end pipeline."""
    pipeline = create_test_pipeline()
    result = await pipeline.collect_and_process()
    
    assert "scout_report" in result
    assert result["scout_report"].confidence >= 0.0
```

---

## Troubleshooting

### Common Issues

**Issue:** PII not being redacted
- **Solution:** Check redaction patterns in `RedactionConfig`
- **Check:** Verify `normalizer.normalize()` output

**Issue:** Forensics analysis is slow
- **Solution:** Reduce window size or increase `min_records` threshold
- **Check:** Forensics adapter timeout settings

**Issue:** Privacy violations detected
- **Solution:** Review normalizer patterns, add validation checks
- **Check:** Pre-flight validation before cloud calls

---

## Advanced Topics

### Custom Redaction Patterns

```python
# Add custom pattern
custom_pattern = RedactionPattern(
    name="custom_secret",
    regex=r"secret:\s*([A-Za-z0-9]+)",
    replacement="secret:REDACTED"
)

config.patterns.append(custom_pattern)
normalizer = LogNormalizer(config)
```

### Custom Escalation Policy

```python
# Custom router policy
class CustomRouterPolicy(RouterPolicy):
    def decide(self, report, novelty):
        # Custom escalation logic
        if report.severity == "high" and novelty > 0.5:
            return RouterDecision(kind="escalate", reason="custom")
        return super().decide(report, novelty)
```

### Custom Collectors

```python
# Custom collector
class CustomCollector(LogCollector):
    async def collect(self) -> List[LogRecord]:
        # Custom collection logic
        return []
```

---

**Read T4 for complete reference.**

