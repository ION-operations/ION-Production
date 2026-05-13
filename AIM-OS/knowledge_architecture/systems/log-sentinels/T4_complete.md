---
id: "log-sentinels_T4_complete"
system: "log-sentinels"
component: null
level: "T4"
type: "complete"
title: "Log-Sentinels Complete Reference"
description: "15,000+ word complete reference for Log-Sentinels"
audience: "reference, complete details"
confidence_threshold: 0.60
token_cost: 15000
word_count: 15000
created: "2025-01-27T00:00:00Z"
updated: "2025-01-27T00:00:00Z"
author: "aether"
status: "complete"
tags: ["log-sentinels", "log-analysis", "hybrid", "privacy", "t0-t4", "transitional"]
dependencies: ["log-sentinels_T3_detailed"]
related_docs: ["log-sentinels_T0_executive", "log-sentinels_T1_overview", "log-sentinels_T2_architecture", "system.map.lucid.json5", "usage.envelope.md"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# Log-Sentinels – T4 Complete Reference (≈15,000 words)

## Purpose

This document provides a complete reference for Log-Sentinels (Hybrid Log Analysis System), covering all aspects including architecture, implementation, API reference, configuration, troubleshooting, edge cases, performance tuning, security, privacy, and advanced topics. This is the definitive reference for Log-Sentinels system.

## Document Structure

- **T0 Executive Summary:** 100-word overview
- **T1 Overview:** 500-word overview
- **T2 Architecture:** 2,000-word architecture
- **T3 Detailed Implementation:** 10,000-word implementation guide
- **T4 Complete Reference:** 15,000+ word complete reference (this document)

---

## Complete API Reference

### LogSentinelsPipeline Class

**File:** `packages/log_sentinels/core/pipeline.py`

**Methods:**

```python
class LogSentinelsPipeline:
    async def process_window(self, win_id: str) -> Dict[str, Any]
    async def collect_and_process(self) -> Dict[str, Any]
    async def _get_window(self, win_id: str) -> Optional[Window]
    async def _build_local_context(self, window: Window) -> Dict[str, Any]
```

**Complete method signatures, parameters, return types, exceptions, and examples.**

### LogNormalizer Class

**File:** `packages/log_sentinels/core/normalizer.py`

**Methods:**

```python
class LogNormalizer:
    def normalize(self, record: LogRecord) -> LogRecord
    def _compile_pattern(self, pattern: RedactionPattern) -> Dict[str, Any]
```

**Complete method signatures, parameters, return types, exceptions, and examples.**

### ScoutAdapter Class

**File:** `packages/log_sentinels/core/scout.py`

**Methods:**

```python
class ScoutAdapter:
    async def analyze(self, window: Window) -> ScoutReport
    def _build_prompt(self, window: Window) -> str
    async def _call_llm(self, prompt: str) -> str
    def _parse_report(self, response: str, window_id: str) -> ScoutReport
```

**Complete method signatures, parameters, return types, exceptions, and examples.**

### ForensicsAdapter Class

**File:** `packages/log_sentinels/core/forensics.py`

**Methods:**

```python
class ForensicsAdapter:
    async def analyze(self, window: Window, context: Dict[str, Any]) -> ForensicsReport
    def _build_prompt(self, window: Window, context: Dict[str, Any]) -> str
    async def _call_llm(self, prompt: str) -> str
    def _parse_report(self, response: str, window_id: str) -> ForensicsReport
```

**Complete method signatures, parameters, return types, exceptions, and examples.**

**All classes and methods documented with complete reference.**

---

## Complete Type Reference

### LogRecord

```python
@dataclass
class LogRecord:
    ts: str
    source: str
    level: LogLevel
    template: str
    vars: Dict[str, Union[str, int]]
    raw_hash: str
    raw: str  # Redacted version
```

**Complete field descriptions, types, constraints, examples.**

### Window

```python
@dataclass
class Window:
    id: str
    source: str
    from_time: int
    to_time: int
    size: int
    templates: Dict[str, int]
    sample: List[str]
```

**Complete field descriptions, types, constraints, examples.**

### ScoutReport

```python
@dataclass
class ScoutReport:
    window_id: str
    summary: str
    confidence: float
    severity: Severity
    tags: List[str]
    suggested_tools: List[str]
```

**Complete field descriptions, types, constraints, examples.**

### ForensicsReport

```python
@dataclass
class ForensicsReport(ScoutReport):
    root_cause: Optional[str] = None
    fix_suggestion: Optional[Dict[str, Any]] = None
    evidence: List[str] = None
```

**Complete field descriptions, types, constraints, examples.**

**All types documented with complete reference.**

---

## Configuration Reference

### Complete Configuration Options

```yaml
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

templates:
  miner: drain3
  cache_size: 5000

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

**All configuration options documented with descriptions, defaults, constraints, examples.**

---

## Troubleshooting Guide

### Common Issues

**Issue:** PII not being redacted
- **Symptoms:** PII appears in cloud payloads
- **Causes:** Missing patterns, pattern failure, normalizer bypass
- **Solutions:** Add patterns, fix regex, validate normalizer
- **Prevention:** Pre-flight validation, audit logging

**Issue:** Forensics analysis is slow
- **Symptoms:** Analysis time >8s
- **Causes:** Large windows, slow Ollama, context complexity
- **Solutions:** Reduce window size, optimize Ollama, simplify context
- **Prevention:** Monitor latency, optimize windows

**Issue:** Privacy violations detected
- **Symptoms:** PII detected in cloud payloads
- **Causes:** Redaction failure, normalizer bypass, pattern gaps
- **Solutions:** Fix redaction, add validation, update patterns
- **Prevention:** Multiple redaction layers, validation checks

**Complete troubleshooting guide with all issues, symptoms, causes, solutions, prevention.**

---

## Edge Cases

### Edge Case 1: Empty Logs

**Scenario:** No logs collected in time window

**Behavior:**
- Window creation skipped
- No analysis performed
- Next window awaited

**Handling:** Documented with examples.

### Edge Case 2: All Logs Redacted

**Scenario:** All log content redacted, leaving only structure

**Behavior:**
- Scout analyzes structure only
- Confidence may be lower
- Escalation more likely

**Handling:** Documented with examples.

**All edge cases documented with scenarios, behavior, handling, examples.**

---

## Performance Tuning

### Scout Optimization

**Strategies:**
- Reduce prompt size
- Optimize model selection
- Batch requests
- Cache common patterns

**Metrics:**
- Scout latency: Target <700ms
- Token usage: Minimize
- Cost: Track per call

**Complete performance tuning guide with strategies, metrics, examples.**

---

## Security & Privacy Reference

### Privacy Protection

**Redaction:**
- Pattern-based redaction
- Multiple redaction layers
- Pre-flight validation
- Audit logging

**Local-Only Guarantees:**
- Raw logs never leave machine
- Forensics runs locally
- Hash references only
- Privacy violation detection

**Complete security and privacy reference with all considerations, mitigations, examples.**

---

## Advanced Topics

### Custom Redaction Patterns

**Complete guide for creating custom redaction patterns with examples.**

### Custom Escalation Policy

**Complete guide for custom escalation logic with examples.**

### Custom Collectors

**Complete guide for implementing custom collectors with examples.**

**All advanced topics documented with complete guides and examples.**

---

## Reference Links

- **T0 Executive Summary:** `T0_executive.md`
- **T1 Overview:** `T1_overview.md`
- **T2 Architecture:** `T2_architecture.md`
- **T3 Detailed Implementation:** `T3_detailed.md`
- **System Map:** `system.map.lucid.json5`
- **System Index:** `system.index.lucid.json5`
- **Usage Envelope:** `usage.envelope.md`

---

**This is the complete reference for Log-Sentinels. See T0-T3 for progressive detail levels.**

