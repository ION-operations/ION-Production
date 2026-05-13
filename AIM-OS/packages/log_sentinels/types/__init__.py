"""
Log-Sentinels core types and data structures.
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from enum import Enum


class LogLevel(str, Enum):
    """Log levels."""
    DEBUG = "debug"
    INFO = "info"
    WARN = "warn"
    ERROR = "error"


class Severity(str, Enum):
    """Severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class LogRecord:
    """Single log record."""
    ts: str
    source: str
    level: LogLevel
    template: str
    vars: Dict[str, Union[str, int]]
    raw_hash: str
    raw: str  # Redacted version (for cloud), original stored locally


@dataclass
class Window:
    """Rolling time window of log records."""
    id: str
    source: str
    from_time: int
    to_time: int
    size: int
    templates: Dict[str, int]  # template -> count
    sample: List[str]  # Small redacted excerpts


@dataclass
class ScoutReport:
    """Scout LLM analysis report."""
    window_id: str
    summary: str
    confidence: float  # 0..1
    severity: Severity
    tags: List[str]  # components/APIs
    suggested_tools: List[str]  # MCP tool names


@dataclass
class ForensicsReport(ScoutReport):
    """Forensics LLM analysis report (extends ScoutReport)."""
    root_cause: Optional[str] = None
    fix_suggestion: Optional[Dict[str, Any]] = None  # {patch?: string, steps?: List[str]}
    evidence: List[str] = None  # refs into SEG
    
    def __post_init__(self):
        if self.evidence is None:
            self.evidence = []


@dataclass
class RedactionPattern:
    """PII redaction pattern."""
    name: str
    regex: str
    replacement: str


@dataclass
class RedactionConfig:
    """Redaction configuration."""
    patterns: List[RedactionPattern]


@dataclass
class RouterDecision:
    """Router policy decision."""
    kind: str  # "keep" | "escalate"
    reason: str

