"""
Router core types and data structures.
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum


class Severity(str, Enum):
    """Severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskLevel(str, Enum):
    """Risk levels for tools."""
    LOW = "low"
    MEDIUM = "med"
    HIGH = "high"


@dataclass
class RouterContext:
    """Context for router decision-making."""
    goal: str
    task: str
    confidence: float
    files: List[str]
    errors: List[str]
    agent_intent: str
    budget: Dict[str, float]
    suggested_tools: Optional[List[str]] = None
    log_insights: Optional[Dict[str, Any]] = None


@dataclass
class Snapshot:
    """Snapshot of current system state."""
    cmc_decisions: List[Dict[str, Any]]
    hhni_context: List[Dict[str, Any]]
    vif_status: Dict[str, Any]
    seg_evidence: List[Dict[str, Any]]
    tcs_cursor: Dict[str, Any]
    goal: str
    summary: str
    timestamp: datetime
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


@dataclass
class ToolProposal:
    """Tool proposal from Scout LLM."""
    tool_name: str
    rationale: str
    draft_arguments: Dict[str, Any]
    confidence: float
    context_fit: float = 0.0


@dataclass
class RankedTool:
    """Ranked tool with score."""
    proposal: ToolProposal
    score: float
    context_fit: float = 0.0
    success_rate: float = 0.0
    precondition_satisfied: bool = False
    expected_info_gain: float = 0.0
    parallelizable: bool = False


@dataclass
class ToolCallStep:
    """Single step in a tool call plan."""
    id: str
    tool: str
    args: Dict[str, Any]
    parallel_group: Optional[str] = None
    preflight: Optional[List[str]] = None
    timeout_ms: Optional[int] = None
    on_fail: Optional[List[Dict[str, Any]]] = None


@dataclass
class ToolCallPlan:
    """Complete tool call plan (DAG)."""
    plan_id: str
    goal: str
    steps: List[ToolCallStep]
    context: RouterContext
    max_depth: int = 3
    budget: Dict[str, float] = None
    
    def __post_init__(self):
        if self.budget is None:
            self.budget = {}


@dataclass
class ValidationResult:
    """Result of plan validation."""
    passed: bool
    reasons: List[str]
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


@dataclass
class VIFGate:
    """VIF gate result."""
    passed: bool
    reasons: Optional[List[str]] = None
    confidence: float = 0.0
    
    def __post_init__(self):
        if self.reasons is None:
            self.reasons = []


@dataclass
class ExecutionResult:
    """Result of tool execution."""
    success: bool
    result: Any
    logs: List[str]
    error: Optional[str] = None
    execution_time_ms: float = 0.0

