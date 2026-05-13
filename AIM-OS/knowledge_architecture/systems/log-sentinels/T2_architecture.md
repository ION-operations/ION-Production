---
id: "log-sentinels_T2_architecture"
system: "log-sentinels"
component: null
level: "T2"
type: "architecture"
title: "Log-Sentinels Architecture"
description: "2,000-word architecture document for Log-Sentinels (Hybrid Log Analysis System)"
audience: "developers, architects, implementation planning"
confidence_threshold: 0.70
token_cost: 2000
word_count: 2000
created: "2025-01-27T00:00:00Z"
updated: "2025-01-27T00:00:00Z"
author: "aether"
status: "complete"
tags: ["log-sentinels", "log-analysis", "hybrid", "privacy", "t0-t4", "transitional"]
dependencies: ["log-sentinels_T1_overview"]
related_docs: ["log-sentinels_T3_detailed", "system.map.lucid.json5", "usage.envelope.md"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# Log-Sentinels – T2 Architecture (≈2000 words)

## 🔄 **SDF-CVF QUARTET PARITY ENFORCEMENT**

### **Quartet Elements:**

**Code:** Log-Sentinels implementation files (`packages/log_sentinels/core/`), LogSentinelsPipeline, LogCollector, LogNormalizer, LogTemplateMiner, Windower, ScoutAdapter, ForensicsAdapter, RouterPolicy  
**Docs:** T0-T4 documentation (T0_executive.md, T1_overview.md, T2_architecture.md, T3_detailed.md, T4_complete.md), usage.envelope.md  
**Tests:** Log-Sentinels test suite (`packages/log_sentinels/tests/test_log_sentinels.py`), unit tests, integration tests  
**Traces:** VIF witnesses (analysis quality), SEG evidence (analysis chains), TCS timeline entries (incident markers), CMC decision atoms (escalation decisions)

**Parity Requirement:** P ≥ 0.90 for all changes  
**Cross-Tagging:** All quartet elements must be tagged with change ID (log-sentinels-change-YYYYMMDD-HHMMSS) and semantically aligned

### **Quartet Parity Formula:**

```
P = (C_code×docs + C_code×tests + C_code×traces +
     C_docs×tests + C_docs×traces + C_tests×traces) / 6

Where:
- C_code×docs = semantic similarity between code and docs
- C_code×tests = semantic similarity between code and tests
- C_code×traces = semantic similarity between code and traces
- C_docs×tests = semantic similarity between docs and tests
- C_docs×traces = semantic similarity between docs and traces
- C_tests×traces = semantic similarity between tests and traces

Target: P ≥ 0.90 for all changes
```

### **Cross-Tagging Protocol:**

**Change ID Format:** `log-sentinels-change-YYYYMMDD-HHMMSS` (e.g., `log-sentinels-change-20250127-120000`)

**Tagging Requirements:**
- **Code:** Change ID in comments/metadata within modified code sections
- **Docs:** Change ID in frontmatter `tags` array and/or inline comments
- **Tests:** Change ID in test function docstrings/comments
- **Traces:** Change ID in VIF witness metadata, SEG provenance links, timeline entry metadata, decision log filename/content

**Workflow:**
1. Generate Change ID at start of Log-Sentinels modification
2. Modify code (Log-Sentinels implementation) → Tag with Change ID
3. Update docs (T-level docs) → Tag with Change ID
4. Update/add tests (Log-Sentinels test suite) → Tag with Change ID
5. Create traces (VIF witnesses, SEG, timeline, decision log) → Tag with Change ID
6. Validate quartet parity (P ≥ 0.90) before merge

---

## System Architecture

Log-Sentinels implements a privacy-first hybrid analysis pipeline: **Collectors → Normalizer → Template Miner → Windower → Scout (cloud) → Router Policy → Forensics (local) → SEG/VIF/CMC/TCS**. The system uses fast cloud analysis (Cerebras Scout) for rolling summaries and deep local analysis (Ollama Forensics) for root cause detection. Privacy is enforced at every step: cloud sees only redacted/templated windows; local has raw for deep analysis.

### **Pipeline Architecture**

**1. Collection Phase:**
- **LogCollector** implementations gather logs from sources
- BrowserConsoleCollector: WebSocket connection to browser console
- TerminalCollector: File-based collection from terminal logs
- BackendAPICollector: OTEL endpoint collection from backend API
- All collectors emit **LogRecord** objects with timestamp, source, level, raw text

**2. Normalization Phase:**
- **LogNormalizer** receives raw log records
- Applies redaction patterns (bearer tokens, emails, IPs, API keys)
- Computes SHA256 hash of original raw (for local storage reference)
- Preserves structure (timestamp, source, level, template, vars)
- Returns normalized **LogRecord** with redacted raw text
- **Critical:** Redaction happens BEFORE any cloud calls

**3. Template Mining Phase:**
- **LogTemplateMiner** receives normalized log records
- Uses Drain3 algorithm to extract log templates (patterns)
- Clusters similar logs by template
- Computes template counts per window
- Computes novelty scores (comparison vs historical templates)
- Manages template cache (LRU eviction, max 5000 templates)

**4. Windowing Phase:**
- **Windower** receives normalized log records
- Creates rolling time windows (60s roll, 12+ min records)
- Filters records by time window
- Detects bursts (2.5x baseline threshold)
- Creates **Window** objects with ID, source, time range, size, templates, samples
- Returns None if insufficient records

**5. Scout Analysis Phase (Cloud):**
- **ScoutAdapter** receives redacted window
- Builds prompt using only redacted samples (first 5)
- Calls Cerebras LLM (<700ms timeout)
- Parses JSON response into **ScoutReport**
- Returns summary, confidence, severity, tags, suggested tools
- **Critical:** Only redacted data sent to cloud

**6. Router Policy Phase:**
- **RouterPolicy** receives ScoutReport and novelty score
- Computes severity score (low: 0.2, medium: 0.6, high: 1.0)
- Checks escalation conditions:
  - Severity ≥ min_severity (default: medium)
  - AND (Confidence < max_confidence (default: 0.80) OR Novelty ≥ novelty_threshold (default: 0.70))
- Returns **RouterDecision** (keep or escalate)

**7. Forensics Analysis Phase (Local, if escalated):**
- **ForensicsAdapter** receives raw window and local context
- Builds prompt using raw samples (first 20) and context (diffs, tests, PRs)
- Calls Ollama LLM (<8s timeout, local-only)
- Parses JSON response into **ForensicsReport**
- Returns root cause, fix suggestion, evidence
- **Critical:** Raw logs never leave machine

**8. Evidence Recording Phase:**
- **LogSentinelsPipeline** records results in AIM-OS systems
- SEG: Scout/Forensics evidence chains
- VIF: Quality gates for analysis quality
- CMC: Decision atoms for escalation decisions
- TCS: Incident markers for timeline
- Router: Tool suggestions for tool selection

---

## Component Details

### **1. LogSentinelsPipeline (Main Orchestrator)**

**Purpose:** Coordinate entire pipeline from collection to evidence recording

**Key Methods:**
- `process_window(win_id: str) -> Dict[str, Any]` - Process a log window
- `collect_and_process() -> Dict[str, Any]` - Collect logs and process windows
- `_get_window(win_id: str) -> Optional[Window]` - Get window by ID
- `_build_local_context(window: Window) -> Dict[str, Any]` - Build local context for forensics

**Dependencies:** LogCollector[], LogNormalizer, LogTemplateMiner, Windower, ScoutAdapter, ForensicsAdapter, RouterPolicy

**Performance:** Target <1000ms end-to-end processing time

### **2. LogCollector (Abstract Base)**

**Purpose:** Abstract base for log collection from various sources

**Implementations:**
- **BrowserConsoleCollector:** WebSocket connection to browser console (ws://localhost:7001/console)
- **TerminalCollector:** File-based collection from terminal logs (./logs/dev-terminal.log)
- **BackendAPICollector:** OTEL endpoint collection from backend API (http://localhost:4318/v1/logs)

**Key Methods:**
- `collect() -> List[LogRecord]` - Collect logs from source

**Performance:** Target <50ms collection time per source

### **3. LogNormalizer (Privacy Component)**

**Purpose:** Redact PII/secrets before cloud calls

**Key Methods:**
- `normalize(record: LogRecord) -> LogRecord` - Normalize log record by redacting PII
- `_compile_pattern(pattern: RedactionPattern) -> Dict[str, Any]` - Compile redaction pattern into regex

**Redaction Patterns:**
- Bearer tokens: `(?i)bearer\s+[a-z0-9\._\-]+` → `BEARER_TOKEN`
- Emails: `[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}` → `EMAIL_REDACTED`
- IPs: `\b(\d{1,3}\.){3}\d{1,3}\b` → `IP_REDACTED`
- API keys: `(?i)(key|token|secret)=([A-Za-z0-9_\-]{8,})` → `$1=REDACTED`

**Features:**
- Pattern-based redaction (regex compilation)
- Hash computation (SHA256 of original raw)
- Structure preservation (timestamp, source, level, template, vars)

**Performance:** Target <10ms normalization time per record

### **4. LogTemplateMiner (Analysis Component)**

**Purpose:** Extract log templates using Drain3 algorithm

**Key Methods:**
- `mine(records: List[LogRecord]) -> Dict[str, int]` - Mine templates from log records
- `novelty_score(window: Window) -> float` - Compute novelty score for window
- `_extract_template(log_message: str) -> str` - Extract template from log message
- `_evict_lru()` - Evict least recently used templates from cache

**Features:**
- Drain3 algorithm for template extraction
- Template clustering (similar logs grouped)
- Novelty detection (comparison vs historical templates)
- Cache management (LRU eviction, max 5000 templates)

**Performance:** Target <100ms mining time per window

### **5. Windower (Windowing Component)**

**Purpose:** Create rolling time windows from log records

**Key Methods:**
- `create_window(records: List[LogRecord]) -> Optional[Window]` - Create rolling window from log records

**Features:**
- Rolling windows (60s roll, configurable)
- Minimum records threshold (12 records, configurable)
- Burst detection (2.5x baseline threshold, configurable)
- Baseline tracking (exponential moving average)

**Performance:** Target <20ms windowing time

### **6. ScoutAdapter (Cloud Analysis)**

**Purpose:** Fast cloud LLM analysis of redacted windows

**Key Methods:**
- `analyze(window: Window) -> ScoutReport` - Analyze log window using Scout LLM
- `_build_prompt(window: Window) -> str` - Build prompt for Scout LLM
- `_call_llm(prompt: str) -> str` - Call Cerebras API
- `_parse_report(response: str, window_id: str) -> ScoutReport` - Parse LLM response

**Features:**
- Fast analysis (<700ms timeout)
- Redacted-only data (never sends raw logs)
- JSON response parsing
- Error handling (default reports on parse errors)

**Performance:** Target <700ms analysis time

### **7. ForensicsAdapter (Local Analysis)**

**Purpose:** Deep local LLM analysis of raw windows

**Key Methods:**
- `analyze(window: Window, context: Dict[str, Any]) -> ForensicsReport` - Analyze log window using Forensics LLM
- `_build_prompt(window: Window, context: Dict[str, Any]) -> str` - Build prompt for Forensics LLM
- `_call_llm(prompt: str) -> str` - Call Ollama API
- `_parse_report(response: str, window_id: str) -> ForensicsReport` - Parse LLM response

**Features:**
- Deep analysis (<8s timeout)
- Raw data access (local-only, never leaves machine)
- Context integration (diffs, tests, PRs)
- Root cause analysis
- Fix suggestions (patches or steps)

**Performance:** Target <8s analysis time

### **8. RouterPolicy (Decision Component)**

**Purpose:** Escalation decision logic

**Key Methods:**
- `decide(report: ScoutReport, novelty: float) -> RouterDecision` - Decide whether to escalate
- `_severity_to_score(severity: str) -> float` - Convert severity string to numeric score

**Escalation Logic:**
- Escalate if: Severity ≥ min_severity AND (Confidence < max_confidence OR Novelty ≥ novelty_threshold)
- Default thresholds: min_severity="medium", max_confidence=0.80, novelty_threshold=0.70

**Performance:** Target <5ms decision time

---

## Data Flow

### **Processing Flow:**

```
Log Sources (Browser Console, Terminal, Backend API)
  ↓
LogCollector.collect()
  ↓
List[LogRecord] (raw logs)
  ↓
LogNormalizer.normalize(record)
  ↓
List[LogRecord] (redacted logs, raw_hash preserved)
  ↓
LogTemplateMiner.mine(records)
  ↓
Dict[str, int] (template -> count)
  ↓
Windower.create_window(records)
  ↓
Window (id, source, from_time, to_time, size, templates, sample)
  ↓
ScoutAdapter.analyze(window)
  ↓ (cloud call, redacted only)
ScoutReport (summary, confidence, severity, tags, suggested_tools)
  ↓
LogTemplateMiner.novelty_score(window)
  ↓
float (novelty score 0-1)
  ↓
RouterPolicy.decide(scout_report, novelty)
  ↓
RouterDecision (keep or escalate)
  ↓ (if escalate)
ForensicsAdapter.analyze(window, context)
  ↓ (local call, raw data)
ForensicsReport (root_cause, fix_suggestion, evidence)
  ↓
SEG/VIF/CMC/TCS Recording
  ↓
Router (tool suggestions)
```

### **Privacy Flow:**

```
Raw Log Record
  ↓
LogNormalizer.normalize()
  ↓
Redaction Patterns Applied
  ↓
SHA256 Hash Computed (raw_hash)
  ↓
Redacted LogRecord (raw_hash preserved)
  ↓
Cloud Path: ScoutAdapter (redacted only)
Local Path: ForensicsAdapter (raw data, never leaves machine)
```

---

## Interfaces

### **LogRecord**

```python
@dataclass
class LogRecord:
    ts: str  # Timestamp ISO format
    source: str  # Source identifier (browser.console, terminal, backend.api)
    level: LogLevel  # debug, info, warn, error
    template: str  # Log template pattern
    vars: Dict[str, Union[str, int]]  # Template variables
    raw_hash: str  # SHA256 hash of original raw (for local storage reference)
    raw: str  # Redacted version (for cloud), original stored locally
```

### **Window**

```python
@dataclass
class Window:
    id: str  # Unique window identifier
    source: str  # Log source
    from_time: int  # Start timestamp (Unix epoch)
    to_time: int  # End timestamp (Unix epoch)
    size: int  # Number of records in window
    templates: Dict[str, int]  # template -> count
    sample: List[str]  # Small redacted excerpts (for Scout)
```

### **ScoutReport**

```python
@dataclass
class ScoutReport:
    window_id: str  # Window identifier
    summary: str  # Brief summary (1-2 sentences)
    confidence: float  # Confidence level (0-1)
    severity: Severity  # low, medium, high
    tags: List[str]  # Components/APIs mentioned
    suggested_tools: List[str]  # MCP tool names
```

### **ForensicsReport**

```python
@dataclass
class ForensicsReport(ScoutReport):
    root_cause: Optional[str] = None  # Root cause analysis
    fix_suggestion: Optional[Dict[str, Any]] = None  # {patch?: string, steps?: List[str]}
    evidence: List[str] = None  # References into SEG
```

### **RouterDecision**

```python
@dataclass
class RouterDecision:
    kind: str  # "keep" | "escalate"
    reason: str  # Decision reasoning
```

---

## Integration Points

### **Router Integration**

Log-Sentinels sends to Router:
- Tool suggestions (from Scout/Forensics reports)
- Log insights (anomaly detection)
- Forensics reports (root cause analysis)

Router uses suggestions to:
- Enhance tool proposals
- Improve context understanding
- Guide tool selection

### **SEG Integration**

Log-Sentinels records in SEG:
- Scout evidence (analysis chains)
- Forensics evidence (root cause chains)
- Escalation chains (decision evidence)

### **VIF Integration**

Log-Sentinels uses VIF for:
- Quality gates (analysis quality validation)
- Confidence tracking
- Validation requests

Log-Sentinels emits:
- VIF witnesses (analysis quality)
- Confidence scores
- Provenance traces

### **CMC Integration**

Log-Sentinels stores in CMC:
- Decision atoms (escalation decisions)
- Analysis results (Scout/Forensics reports)
- Processing state (window state)

### **TCS Integration**

Log-Sentinels creates TCS entries for:
- Incident markers (severity-based)
- Analysis events (Scout/Forensics completion)
- Escalation events (router policy decisions)

### **IDE Panels Integration**

Log-Sentinels sends to IDE panels via SSE/WS:
- Scout reports (AI Summaries panel)
- Forensics reports (Anomalies panel)
- Telemetry data (dashboards)
- Real-time updates (event stream)

---

## Performance Characteristics

### **Latency Targets:**

- **End-to-End Processing:** <1000ms (with Scout only)
- **Scout Analysis:** <700ms (p95)
- **Forensics Analysis:** <8s (p95)
- **Normalization:** <10ms per record
- **Template Mining:** <100ms per window
- **Windowing:** <20ms per window

### **Throughput:**

- **Windows per minute:** 60+ (per source)
- **Scout calls per minute:** 60 (per source)
- **Forensics calls per minute:** 6 (per source, if escalated)
- **Privacy violations:** 0 (hard requirement)

### **Optimization Strategies:**

1. **Template Caching:** Template miner caches templates (LRU, max 5000)
2. **Window Optimization:** Windower filters by time and burst detection
3. **Batch Processing:** Pipeline processes windows in batches
4. **Parallel Analysis:** Multiple windows can be analyzed in parallel
5. **Redaction Optimization:** Patterns pre-compiled for faster processing

---

## Security & Privacy

### **Privacy Protection:**

- **Redaction Before Cloud:** All PII redacted before any cloud calls
- **Raw Logs Stay Local:** Original raw logs never leave machine
- **Hash References:** Raw logs referenced by hash, stored locally
- **Validation Checks:** Pre-flight validation ensures no raw data in cloud payloads

### **Security:**

- **Source Validation:** Collectors validate source authenticity
- **Rate Limiting:** Collectors enforce rate limits
- **Access Control:** IDE panels require authentication
- **Audit Logging:** All operations logged in CMC

### **Governance:**

- **Privacy Enforcement:** Hard gates prevent privacy violations
- **Escalation Tracking:** All escalations tracked
- **Evidence Recording:** All analysis evidenced in SEG
- **Quartet Parity:** Code/Docs/Tests/Traces maintained

---

**Read T3 for detailed implementation guide.**

