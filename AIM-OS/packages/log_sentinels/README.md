"""
Log-Sentinels API Documentation

# Log-Sentinels API Reference

## Overview

Log-Sentinels provides comprehensive log analysis with hybrid cloud/local processing. It uses fast Cerebras scouts for rolling summaries and local Ollama analyzers for deep forensics.

## Core Classes

### LogSentinelsPipeline

Main pipeline for log processing.

**Methods:**

- `process_window(win_id: str) -> Dict[str, Any]`
  - Process a log window
  - Returns: Processing result with Scout/Forensics reports

- `collect_and_process() -> Dict[str, Any]`
  - Collect logs and process windows
  - Returns: Processing results

**Example:**

```python
from log_sentinels.core.pipeline import LogSentinelsPipeline

pipeline = LogSentinelsPipeline(
    collectors=[collector],
    normalizer=normalizer,
    template_miner=template_miner,
    windower=windower,
    scout=scout,
    forensics=forensics,
    router_policy=router_policy
)

result = await pipeline.collect_and_process()
```

### LogNormalizer

PII redaction normalizer.

**Methods:**

- `normalize(record: LogRecord) -> LogRecord`
  - Normalize log record by redacting PII
  - Critical: Redaction happens BEFORE cloud calls
  - Returns: Normalized log record with redacted raw text

**Example:**

```python
from log_sentinels.core.normalizer import LogNormalizer
from log_sentinels.types import RedactionConfig, RedactionPattern

patterns = [
    RedactionPattern(
        name="emails",
        regex=r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        replacement="EMAIL_REDACTED"
    )
]
config = RedactionConfig(patterns=patterns)
normalizer = LogNormalizer(config)

normalized = normalizer.normalize(log_record)
```

### ScoutAdapter

Fast cloud LLM for log analysis.

**Methods:**

- `analyze(window: Window) -> ScoutReport`
  - Analyze log window using Scout LLM
  - Only sees redacted logs (PII removed)
  - Returns: ScoutReport with summary, confidence, severity, tags, suggested tools

**Example:**

```python
from log_sentinels.core.scout import ScoutAdapter

scout = ScoutAdapter(api_key="your_key")
report = await scout.analyze(window)
```

### ForensicsAdapter

Deep local LLM for log analysis.

**Methods:**

- `analyze(window: Window, context: Dict[str, Any]) -> ForensicsReport`
  - Analyze log window using Forensics LLM
  - Can access raw logs (never leaves machine)
  - Returns: ForensicsReport with root cause, fix suggestion, evidence

**Example:**

```python
from log_sentinels.core.forensics import ForensicsAdapter

forensics = ForensicsAdapter(model="llama3:8b-instruct-q4")
report = await forensics.analyze(window, context)
```

### RouterPolicy

Hybrid decision logic for escalation.

**Methods:**

- `decide(report: ScoutReport, novelty: float) -> RouterDecision`
  - Decide whether to escalate based on Scout report and novelty
  - Returns: RouterDecision with kind ("keep" | "escalate") and reason

**Example:**

```python
from log_sentinels.core.router_policy import RouterPolicy

policy = RouterPolicy(
    min_severity="medium",
    max_confidence=0.80,
    novelty_threshold=0.70
)

decision = policy.decide(scout_report, novelty_score)
```

## Types

### LogRecord

Single log record.

```python
@dataclass
class LogRecord:
    ts: str
    source: str
    level: LogLevel  # debug, info, warn, error
    template: str
    vars: Dict[str, Union[str, int]]
    raw_hash: str
    raw: str  # Redacted version (for cloud), original stored locally
```

### ScoutReport

Scout LLM analysis report.

```python
@dataclass
class ScoutReport:
    window_id: str
    summary: str
    confidence: float  # 0..1
    severity: Severity  # low, medium, high
    tags: List[str]  # components/APIs
    suggested_tools: List[str]  # MCP tool names
```

### ForensicsReport

Forensics LLM analysis report (extends ScoutReport).

```python
@dataclass
class ForensicsReport(ScoutReport):
    root_cause: Optional[str] = None
    fix_suggestion: Optional[Dict[str, Any]] = None
    evidence: List[str] = None
```

## Performance

- **Scout Analysis Time:** <700ms average
- **Forensics Analysis Time:** <8s average
- **Privacy:** PII redaction before cloud, raw logs stay local

## Integration

Log-Sentinels integrates with:
- **SEG:** Evidence chains
- **VIF:** Quality gates
- **CMC:** Decision storage
- **TCS:** Timeline tracking
- **Router:** Tool suggestions

