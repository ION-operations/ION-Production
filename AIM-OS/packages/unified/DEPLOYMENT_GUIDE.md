# Router + Log-Sentinels Production Deployment Guide

## Overview

This guide covers production deployment configuration, monitoring, error handling, and rollback procedures for Router and Log-Sentinels systems.

## Configuration Management

### Environment-Based Configuration

Create configuration files for different environments:

**config/development.yaml:**
```yaml
router:
  cache:
    ttl_seconds: 300
    max_size: 1000
  scout:
    api_key: ${CEREBRAS_API_KEY}
    model: "cerebras/small:latest"
    timeout_ms: 700
  bandit:
    learning_rate: 0.01
    weights:
      context_fit: 0.3
      success_rate: 0.25
      precondition: 0.2
      info_gain: 0.15
      parallelizability: 0.1

log_sentinels:
  collectors:
    - type: browser_console
      ws_url: "ws://localhost:7001/console"
    - type: terminal
      log_path: "./logs/dev-terminal.log"
  normalizer:
    patterns:
      - name: bearer_tokens
        regex: "(?i)bearer\\s+[a-z0-9\\._\\-]+"
        replacement: "BEARER_TOKEN"
      - name: emails
        regex: "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}"
        replacement: "EMAIL_REDACTED"
  windower:
    roll_seconds: 60
    min_records: 12
  scout:
    api_key: ${CEREBRAS_API_KEY}
    model: "cerebras/small:latest"
    timeout_ms: 700
  forensics:
    model: "llama3:8b-instruct-q4"
    timeout_ms: 8000
  router_policy:
    min_severity: "medium"
    max_confidence: 0.80
    novelty_threshold: 0.70
```

**config/production.yaml:**
```yaml
router:
  cache:
    ttl_seconds: 600  # Longer TTL for production
    max_size: 5000    # Larger cache
  scout:
    api_key: ${CEREBRAS_API_KEY}
    model: "cerebras/small:latest"
    timeout_ms: 500   # Stricter timeout
  bandit:
    learning_rate: 0.005  # Slower learning in production

log_sentinels:
  windower:
    roll_seconds: 30  # More frequent windows
    min_records: 20   # Higher threshold
  router_policy:
    min_severity: "high"  # Stricter escalation
    max_confidence: 0.85
```

### Configuration Loading

```python
import yaml
import os
from pathlib import Path

def load_config(env: str = None):
    """Load configuration for environment."""
    env = env or os.getenv("ENVIRONMENT", "development")
    config_path = Path(f"config/{env}.yaml")
    
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    # Expand environment variables
    config_str = yaml.dump(config)
    config_str = os.path.expandvars(config_str)
    config = yaml.safe_load(config_str)
    
    return config
```

## Monitoring Setup

### Metrics Collection

```python
from prometheus_client import Counter, Histogram, Gauge

# Router metrics
router_decisions_total = Counter(
    'router_decisions_total',
    'Total router decisions',
    ['status']
)

router_decision_duration = Histogram(
    'router_decision_duration_seconds',
    'Router decision duration',
    buckets=[0.1, 0.2, 0.5, 1.0, 2.0]
)

router_cache_hits = Gauge(
    'router_cache_hits',
    'Router cache hit rate'
)

# Log-Sentinels metrics
sentinels_scout_calls = Counter(
    'sentinels_scout_calls_total',
    'Total Scout calls',
    ['status']
)

sentinels_forensics_calls = Counter(
    'sentinels_forensics_calls_total',
    'Total Forensics calls',
    ['status']
)

sentinels_escalations = Counter(
    'sentinels_escalations_total',
    'Total escalations'
)
```

### Health Checks

```python
from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    checks = {
        "router": check_router_health(),
        "log_sentinels": check_log_sentinels_health(),
        "cache": check_cache_health(),
        "scout": check_scout_health(),
        "forensics": check_forensics_health()
    }
    
    all_healthy = all(checks.values())
    status_code = 200 if all_healthy else 503
    
    return JSONResponse(
        content={"status": "healthy" if all_healthy else "unhealthy", "checks": checks},
        status_code=status_code
    )

def check_router_health():
    """Check Router health."""
    try:
        # Check if Router can make decisions
        return True
    except Exception:
        return False

def check_log_sentinels_health():
    """Check Log-Sentinels health."""
    try:
        # Check if pipeline can process logs
        return True
    except Exception:
        return False
```

## Error Handling

### Retry Logic

```python
import asyncio
from typing import Callable, Any
from functools import wraps

def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0
):
    """Retry decorator with exponential backoff."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        await asyncio.sleep(delay)
                        delay *= backoff_factor
                    else:
                        raise
            
            raise last_exception
        return wrapper
    return decorator

# Usage
@retry_with_backoff(max_retries=3)
async def scout_analyze(window):
    return await scout.analyze(window)
```

### Circuit Breaker

```python
from enum import Enum
from datetime import datetime, timedelta

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    """Circuit breaker for fault tolerance."""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: float = 60.0,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    def call(self, func, *args, **kwargs):
        """Call function with circuit breaker protection."""
        if self.state == CircuitState.OPEN:
            if datetime.utcnow() - self.last_failure_time > timedelta(seconds=self.timeout):
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
            return result
        except self.expected_exception as e:
            self.failure_count += 1
            self.last_failure_time = datetime.utcnow()
            
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
            
            raise
```

## Rollback Procedures

### Version Management

```python
import git
from pathlib import Path

class VersionManager:
    """Manage versions and rollbacks."""
    
    def __init__(self, repo_path: Path):
        self.repo = git.Repo(repo_path)
    
    def get_current_version(self) -> str:
        """Get current version."""
        return self.repo.head.commit.hexsha[:8]
    
    def rollback_to_version(self, version: str):
        """Rollback to specific version."""
        self.repo.git.checkout(version)
        # Restart services
        restart_services()
    
    def create_rollback_point(self, tag: str):
        """Create rollback point."""
        self.repo.create_tag(tag, message=f"Rollback point: {tag}")
```

### Database Migrations

```python
from alembic import config, script
from alembic.runtime import migration

def check_migration_status():
    """Check if migrations are needed."""
    alembic_cfg = config.Config("alembic.ini")
    script_dir = script.ScriptDirectory.from_config(alembic_cfg)
    
    with engine.connect() as connection:
        context = migration.MigrationContext.configure(connection)
        current_rev = context.get_current_revision()
        head_rev = script_dir.get_current_head()
        
        return current_rev == head_rev

def rollback_migration(revision: str):
    """Rollback database migration."""
    from alembic import command
    
    alembic_cfg = config.Config("alembic.ini")
    command.downgrade(alembic_cfg, revision)
```

## Deployment Checklist

### Pre-Deployment

- [ ] Run full test suite
- [ ] Check code coverage (>90%)
- [ ] Review configuration files
- [ ] Verify environment variables
- [ ] Check database migrations
- [ ] Review monitoring setup
- [ ] Test rollback procedure

### Deployment

- [ ] Backup current version
- [ ] Deploy new version
- [ ] Run health checks
- [ ] Monitor metrics for 5 minutes
- [ ] Verify cache is working
- [ ] Check error rates
- [ ] Verify integrations (APOE, VIF, SEG, etc.)

### Post-Deployment

- [ ] Monitor for 1 hour
- [ ] Check performance metrics
- [ ] Verify cache hit rates
- [ ] Check error logs
- [ ] Verify tool selection accuracy
- [ ] Document any issues

## Rollback Procedure

1. **Identify Issue:**
   - Check health endpoint
   - Review error logs
   - Check metrics dashboard

2. **Stop New Requests:**
   - Set health check to unhealthy
   - Drain connections

3. **Rollback:**
   ```bash
   # Rollback code
   git checkout <previous_version>
   
   # Rollback database (if needed)
   alembic downgrade <previous_revision>
   
   # Restart services
   systemctl restart router
   systemctl restart log-sentinels
   ```

4. **Verify:**
   - Check health endpoint
   - Monitor metrics
   - Verify functionality

5. **Document:**
   - Record issue
   - Document rollback
   - Create follow-up task

## Monitoring Dashboard

Key metrics to monitor:

- **Router:**
  - Decision time (p50, p95, p99)
  - Cache hit rate
  - Tool selection accuracy
  - Success rate per tool

- **Log-Sentinels:**
  - Scout call latency
  - Forensics call latency
  - Escalation rate
  - Tool suggestion accuracy

- **Integration:**
  - End-to-end latency
  - Error rates
  - Evidence chain completeness

## Alerting

Set up alerts for:

- Router decision time > 400ms (p95)
- Cache hit rate < 50%
- Scout call failure rate > 5%
- Forensics call failure rate > 10%
- Escalation rate > 30%
- Health check failures

