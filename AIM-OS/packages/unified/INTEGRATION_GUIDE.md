# Router + Log-Sentinels Integration Guide

## Overview

This guide explains how to integrate Router and Log-Sentinels systems with AIM-OS.

## Prerequisites

- Python 3.10+
- AIM-OS systems (APOE, VIF, SEG, CMC, HHNI, TCS)
- Cerebras API access (for Scout LLM)
- Ollama local installation (for Forensics LLM)

## Installation

```bash
# Install Router
cd packages/router
pip install -e .

# Install Log-Sentinels
cd ../log_sentinels
pip install -e .

# Install dependencies
pip install pytest pytest-asyncio
```

## Configuration

### Router Configuration

```python
from router.core.router import Router
from router.core.scout import ScoutLLM
from router.core.bandit import BanditScorer
from router.core.rules import RulesEngine
from router.core.manifest import ToolManifest
from router.core.snapshot import SnapshotBuilder
from router.core.cache import RouterCache

# Initialize components
scout = ScoutLLM(api_key="your_cerebras_key")
bandit = BanditScorer(cmc_client, hhni_client, vif_client)
rules = RulesEngine(vif_client)
manifest = ToolManifest()
manifest.initialize_aimos_tools()  # Register AIM-OS tools
snapshot_builder = SnapshotBuilder(cmc, hhni, vif, seg, tcs)
cache = RouterCache(ttl_seconds=300, max_size=1000)

# Create Router
router = Router(
    scout=scout,
    bandit=bandit,
    rules=rules,
    manifest=manifest,
    snapshot_builder=snapshot_builder,
    cache=cache
)
```

### Log-Sentinels Configuration

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
```

## Usage

### Router Usage

```python
from router.types import RouterContext

# Create context
ctx = RouterContext(
    goal="Fix test failures",
    task="Run tests and fix errors",
    confidence=0.8,
    files=["test_file.py"],
    errors=["Test failed"],
    agent_intent="debug",
    budget={"tokens": 1000, "cost": 0.1}
)

# Get tool plan
plan = await router.decide(ctx)

# Execute plan (via APOE)
result = await apoe.execute(plan)

# Learn from outcome
await router.learn_from_outcome(plan, result)
```

### Log-Sentinels Usage

```python
# Process logs
result = await pipeline.collect_and_process()

# Check for Scout report
if "scout_report" in result:
    scout_report = result["scout_report"]
    print(f"Summary: {scout_report.summary}")
    print(f"Suggested tools: {scout_report.suggested_tools}")

# Check for Forensics report (if escalated)
if "forensics_report" in result:
    forensics_report = result["forensics_report"]
    print(f"Root cause: {forensics_report.root_cause}")
    print(f"Fix suggestion: {forensics_report.fix_suggestion}")
```

## Unified Integration

```python
from unified.router_sentinels_service import UnifiedRouterSentinelsService

# Create unified service
service = UnifiedRouterSentinelsService()

# Process logs and route tools
result = await service.process_logs_and_route(logs)

# Result contains:
# - logAnalysis: ScoutReport
# - toolSelection: ToolCallPlan
# - toolExecution: ExecutionResult
# - validation: ValidationResult
```

## Troubleshooting

### Router Issues

**Problem:** Router decisions are slow
- **Solution:** Enable caching with `RouterCache(ttl_seconds=300)`
- **Check:** Cache hit rate via `cache.get_stats()`

**Problem:** Tool proposals are inaccurate
- **Solution:** Adjust Bandit weights or improve Scout prompt
- **Check:** Success rates via `bandit.update_success_rate()`

### Log-Sentinels Issues

**Problem:** PII not being redacted
- **Solution:** Check redaction patterns in `RedactionConfig`
- **Check:** Verify `normalizer.normalize()` output

**Problem:** Forensics analysis is slow
- **Solution:** Reduce window size or increase `min_records` threshold
- **Check:** Forensics adapter timeout settings

## Performance Tuning

### Router Performance

- **Caching:** Enable `RouterCache` for 80%+ cache hit rate
- **Parallel Scoring:** Bandit uses parallel scoring by default
- **Pattern Caching:** Scout caches common patterns for 10 minutes

### Log-Sentinels Performance

- **Window Size:** Adjust `roll_seconds` and `min_records` based on log volume
- **Redaction:** Pre-compile regex patterns for faster processing
- **Template Mining:** Use Drain3 with appropriate cache size

## Testing

```bash
# Run Router tests
cd packages/router
pytest tests/ -v

# Run Log-Sentinels tests
cd ../log_sentinels
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

## API Endpoints

### Router API

- `POST /api/router/tools` - Get tool proposals
- `POST /api/router/execute` - Execute tool
- `GET /api/router/telemetry` - Get telemetry

### Log-Sentinels API

- `GET /api/log-sentinels/scouts` - Get Scout reports
- `GET /api/log-sentinels/forensics` - Get Forensics reports
- `GET /api/log-sentinels/telemetry` - Get telemetry
- `GET /api/log-sentinels/stream` - SSE stream for real-time updates

## Production Deployment

### Environment Variables

```bash
# Router
CEREBRAS_API_KEY=your_key
ROUTER_CACHE_TTL=300
ROUTER_CACHE_SIZE=1000

# Log-Sentinels
LOG_SENTINELS_SCOUT_MODEL=cerebras/small:latest
LOG_SENTINELS_FORENSICS_MODEL=llama3:8b-instruct-q4
LOG_SENTINELS_WINDOW_SECONDS=60
LOG_SENTINELS_MIN_RECORDS=12
```

### Monitoring

- **Router Metrics:** Decision time, cache hit rate, success rate
- **Log-Sentinels Metrics:** Scout calls, Forensics calls, escalations
- **Integration Metrics:** Tool suggestions → Router → Execution success

## Support

For issues or questions:
- Check test suite for usage examples
- Review API documentation
- Check troubleshooting guide above

