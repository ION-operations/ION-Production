"""
AIM-OS AI Engine — Execution Traces

Wave 3: Structured execution traces for CMC storage.

Replaces text-blob memory with structured, searchable records
of every task the AI Engine executes. Each trace contains:
    - Task description and type
    - Agent used and model selected
    - Execution plan steps and outcomes
    - Files modified/created
    - Confidence scores and VIF gate results
    - Error details and recovery actions
    - Timing and performance metrics

Traces are stored in CMC via MCP and can be retrieved
for learning, auditing, and self-improvement analysis.
"""

import time
import json
import uuid
import logging
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field, asdict
from enum import Enum

logger = logging.getLogger('ai_engine.execution_trace')


class TraceType(str, Enum):
    TASK = 'task'
    SWARM = 'swarm'
    WORKER = 'worker'
    AUDIT = 'audit'
    SELF_IMPROVE = 'self_improve'


class TraceOutcome(str, Enum):
    SUCCESS = 'success'
    PARTIAL = 'partial'
    FAILURE = 'failure'
    TIMEOUT = 'timeout'
    ESCALATED = 'escalated'


@dataclass
class StepTrace:
    """Trace of a single execution step."""
    step_index: int
    step_type: str
    description: str
    status: str = 'pending'
    target: str = ''          # file path, command, etc.
    duration_ms: float = 0.0
    error: str = ''


@dataclass
class ExecutionTrace:
    """
    Structured execution trace for CMC storage.
    
    Every AI Engine task produces one of these.
    They are searchable by task_type, agent, model, outcome.
    """
    # Identity
    trace_id: str = field(default_factory=lambda: f'trace_{uuid.uuid4().hex[:12]}')
    trace_type: str = TraceType.TASK
    parent_trace_id: str = ''     # For sub-tasks/workers

    # Task
    task_description: str = ''
    task_type: str = ''
    complexity: str = ''

    # Agent & Model
    agent_name: str = ''
    agent_role: str = ''
    model_used: str = ''
    model_preference: str = ''

    # Outcome
    outcome: str = TraceOutcome.SUCCESS
    confidence: float = 0.0
    vif_gate_passed: bool = True
    verification_passed: bool = False

    # Steps
    steps: List[StepTrace] = field(default_factory=list)
    steps_completed: int = 0
    steps_failed: int = 0

    # Artifacts
    files_modified: List[str] = field(default_factory=list)
    files_created: List[str] = field(default_factory=list)
    files_deleted: List[str] = field(default_factory=list)

    # Errors & Recovery
    errors: List[str] = field(default_factory=list)
    recovery_actions: List[str] = field(default_factory=list)

    # Performance
    total_time_ms: float = 0.0
    context_tokens: int = 0
    response_tokens: int = 0

    # Learnings
    learnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    # Metadata
    created_at: float = field(default_factory=time.time)
    workspace: str = ''
    tags: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = asdict(self)
        d['steps'] = [asdict(s) for s in self.steps]
        return d

    def to_cmc_content(self) -> str:
        """Format for CMC storage (structured but readable)."""
        lines = [
            f"[ExecutionTrace] {self.trace_id}",
            f"Type: {self.trace_type} | Outcome: {self.outcome}",
            f"Task: {self.task_description[:200]}",
            f"Agent: {self.agent_name} ({self.agent_role})",
            f"Model: {self.model_used}",
            f"Confidence: {self.confidence:.2f} | VIF: {'PASS' if self.vif_gate_passed else 'FAIL'}",
            f"Steps: {self.steps_completed} OK / {self.steps_failed} FAIL",
            f"Time: {self.total_time_ms:.0f}ms",
        ]

        if self.files_modified:
            lines.append(f"Modified: {', '.join(self.files_modified[:5])}")
        if self.files_created:
            lines.append(f"Created: {', '.join(self.files_created[:5])}")
        if self.errors:
            lines.append(f"Errors: {'; '.join(self.errors[:3])}")
        if self.learnings:
            lines.append(f"Learnings: {'; '.join(self.learnings[:3])}")

        return '\n'.join(lines)

    def to_cmc_tags(self) -> dict:
        """Tags for CMC storage (enables structured search)."""
        return {
            'type': 'execution_trace',
            'trace_type': self.trace_type,
            'task_type': self.task_type,
            'agent': self.agent_name,
            'model': self.model_used,
            'outcome': self.outcome,
            'confidence': str(round(self.confidence, 2)),
            **self.tags,
        }


class TraceStore:
    """
    Store and retrieve execution traces via CMC (MCP).
    
    Usage:
        store = TraceStore()
        trace = ExecutionTrace(task_description="...", ...)
        store.save(trace)
        
        similar = store.find_similar("Fix auth bug", limit=3)
    """

    def __init__(self):
        self._mcp = None
        self._local_traces: List[ExecutionTrace] = []

    def _get_mcp(self):
        if self._mcp is None:
            from ai_engine.self_improve import MCPBridge
            self._mcp = MCPBridge()
        return self._mcp

    def save(self, trace: ExecutionTrace) -> dict:
        """Save a trace to CMC."""
        self._local_traces.append(trace)

        # Keep last 100 locally
        if len(self._local_traces) > 100:
            self._local_traces = self._local_traces[-100:]

        try:
            mcp = self._get_mcp()
            return mcp.store_memory(
                content=trace.to_cmc_content(),
                tags=trace.to_cmc_tags(),
            )
        except Exception as e:
            logger.debug(f'Failed to save trace to CMC: {e}')
            return {'stored': True, 'local': True}

    def find_similar(self, task: str, limit: int = 3) -> List[ExecutionTrace]:
        """Find similar traces from CMC."""
        try:
            mcp = self._get_mcp()
            result = mcp.retrieve_memory(query=f'execution_trace {task}', limit=limit)
            # Returns raw memories — in future, parse back into ExecutionTrace
            return []
        except Exception:
            return []

    def recent(self, limit: int = 10) -> List[ExecutionTrace]:
        """Get recent traces from local cache."""
        return self._local_traces[-limit:]

    def stats(self) -> dict:
        """Trace statistics."""
        total = len(self._local_traces)
        if total == 0:
            return {'total': 0}

        successes = sum(1 for t in self._local_traces if t.outcome == TraceOutcome.SUCCESS)
        avg_confidence = sum(t.confidence for t in self._local_traces) / total
        avg_time = sum(t.total_time_ms for t in self._local_traces) / total

        models = {}
        for t in self._local_traces:
            models.setdefault(t.model_used, []).append(t.outcome)

        return {
            'total': total,
            'success_rate': successes / total,
            'avg_confidence': round(avg_confidence, 3),
            'avg_time_ms': round(avg_time, 1),
            'models': {m: len(v) for m, v in models.items()},
        }
